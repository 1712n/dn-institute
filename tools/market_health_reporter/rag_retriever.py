"""
RAG (Retrieval Augmented Generation) module for the Market Health Reporter.

Retrieves relevant context from multiple sources to enrich report generation:
1. Local articles from dn.institute market health posts
2. CoinGecko public API for token/exchange metadata
3. DuckDuckGo web search for recent news and context
"""

import os
import re
import json
import glob
import logging
import requests
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Default path to existing market health articles (relative to repo root)
DEFAULT_ARTICLES_DIR = "content/research/market-health/posts"

# CoinGecko free API base URL (no API key required)
COINGECKO_API_BASE = "https://api.coingecko.com/api/v3"

# Maximum snippet length for local article excerpts
MAX_SNIPPET_LENGTH = 800

# Maximum number of web search results to include
MAX_WEB_RESULTS = 5


class RAGRetriever:
    """
    Retrieval-Augmented Generation context builder for market health reports.

    Searches local articles, public crypto APIs, and the web to gather
    background context that is injected into the LLM prompt before
    report generation.
    """

    def __init__(
        self,
        articles_dir: str = DEFAULT_ARTICLES_DIR,
        enable_web_search: bool = True,
        enable_coingecko: bool = True,
    ):
        self.articles_dir = articles_dir
        self.enable_web_search = enable_web_search
        self.enable_coingecko = enable_coingecko

    # ------------------------------------------------------------------
    # 1. Local article search
    # ------------------------------------------------------------------

    def search_local_articles(self, entity: str, limit: int = 3) -> list[dict]:
        """
        Search existing dn.institute market-health articles that mention
        the given entity (exchange name, token symbol, etc.).

        Returns a list of dicts with keys: source, title, date, snippet.
        """
        results = []
        pattern = os.path.join(self.articles_dir, "*/index.md")
        for path in sorted(glob.glob(pattern)):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
            except OSError as exc:
                logger.warning("Could not read %s: %s", path, exc)
                continue

            if entity.lower() not in content.lower():
                continue

            # Extract front-matter metadata
            title = self._extract_front_matter_field(content, "title") or os.path.basename(os.path.dirname(path))
            date = self._extract_front_matter_field(content, "date") or ""

            # Build a contextual snippet: grab paragraphs mentioning the entity
            snippet = self._extract_relevant_snippet(content, entity)

            results.append(
                {
                    "source": path,
                    "title": title,
                    "date": date,
                    "snippet": snippet,
                }
            )

            if len(results) >= limit:
                break

        logger.info("Local article search for '%s': %d result(s)", entity, len(results))
        return results

    # ------------------------------------------------------------------
    # 2. CoinGecko public API
    # ------------------------------------------------------------------

    def fetch_coingecko_info(self, token_symbol: str) -> Optional[dict]:
        """
        Fetch basic information about a token from the CoinGecko free API.
        Returns a dict with name, symbol, description snippet, market_cap_rank,
        and current price — or None on failure.
        """
        if not self.enable_coingecko:
            return None

        try:
            # Step 1: search for the coin id by symbol
            search_url = f"{COINGECKO_API_BASE}/search"
            resp = requests.get(
                search_url,
                params={"query": token_symbol},
                timeout=10,
            )
            resp.raise_for_status()
            coins = resp.json().get("coins", [])

            if not coins:
                logger.info("CoinGecko: no results for symbol '%s'", token_symbol)
                return None

            # Pick the best match (prefer exact symbol match)
            coin = next(
                (c for c in coins if c.get("symbol", "").lower() == token_symbol.lower()),
                coins[0],
            )
            coin_id = coin.get("id")
            if not coin_id:
                return None

            # Step 2: get coin details
            detail_url = f"{COINGECKO_API_BASE}/coins/{coin_id}"
            resp = requests.get(
                detail_url,
                params={
                    "localization": "false",
                    "tickers": "false",
                    "market_data": "true",
                    "community_data": "false",
                    "developer_data": "false",
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

            description_en = (data.get("description", {}).get("en") or "")[:600]
            # Strip HTML tags from CoinGecko descriptions
            description_en = re.sub(r"<[^>]+>", "", description_en)

            market_data = data.get("market_data", {})
            return {
                "name": data.get("name", ""),
                "symbol": data.get("symbol", ""),
                "description": description_en,
                "market_cap_rank": data.get("market_cap_rank"),
                "current_price_usd": (
                    market_data.get("current_price", {}).get("usd")
                ),
                "total_volume_usd": (
                    market_data.get("total_volume", {}).get("usd")
                ),
            }

        except requests.RequestException as exc:
            logger.warning("CoinGecko API error for '%s': %s", token_symbol, exc)
            return None

    # ------------------------------------------------------------------
    # 3. Web search via DuckDuckGo
    # ------------------------------------------------------------------

    def search_web(self, query: str, limit: int = MAX_WEB_RESULTS) -> list[dict]:
        """
        Run a web search using the duckduckgo-search library
        (already a project dependency).

        Returns a list of dicts with keys: title, url, snippet.
        """
        if not self.enable_web_search:
            return []

        try:
            from duckduckgo_search import ddg  # type: ignore
        except ImportError:
            # duckduckgo-search >= 4.0 changed the API
            try:
                from duckduckgo_search import DDGS  # type: ignore

                return self._search_with_ddgs(query, limit)
            except ImportError:
                logger.warning("duckduckgo-search library not available — skipping web search")
                return []

        try:
            raw_results = ddg(query, max_results=limit) or []
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("href", r.get("link", "")),
                    "snippet": r.get("body", r.get("snippet", "")),
                }
                for r in raw_results[:limit]
            ]
        except Exception as exc:
            logger.warning("DuckDuckGo search failed: %s", exc)
            return []

    def _search_with_ddgs(self, query: str, limit: int) -> list[dict]:
        """Fallback for duckduckgo-search >= 4.x which uses the DDGS class."""
        try:
            from duckduckgo_search import DDGS  # type: ignore

            with DDGS() as ddgs:
                raw_results = list(ddgs.text(query, max_results=limit))
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("href", r.get("link", "")),
                    "snippet": r.get("body", r.get("snippet", "")),
                }
                for r in raw_results[:limit]
            ]
        except Exception as exc:
            logger.warning("DDGS search failed: %s", exc)
            return []

    # ------------------------------------------------------------------
    # 4. Context builder  — main entry point
    # ------------------------------------------------------------------

    def get_context(
        self,
        exchange: str,
        tokens: list[str],
        start_date: str = "",
        end_date: str = "",
    ) -> str:
        """
        Build a combined context string for the LLM prompt.

        Parameters
        ----------
        exchange : str
            Name of the exchange being analysed (e.g. "huobi").
        tokens : list[str]
            Token symbols involved in the analysis (e.g. ["HT", "TRX"]).
        start_date / end_date : str
            Analysis period (used to refine web searches).

        Returns
        -------
        str
            Formatted context block ready to be injected into the prompt.
            Returns an empty string if no context was found.
        """
        sections: list[str] = []

        # --- Local articles ---
        local_results = self.search_local_articles(exchange)
        for token in tokens:
            local_results.extend(self.search_local_articles(token))

        # Deduplicate by source path
        seen_sources: set[str] = set()
        unique_local: list[dict] = []
        for item in local_results:
            if item["source"] not in seen_sources:
                seen_sources.add(item["source"])
                unique_local.append(item)

        if unique_local:
            parts = []
            for item in unique_local[:5]:
                parts.append(
                    f"### {item['title']} ({item['date']})\n"
                    f"Source: {item['source']}\n"
                    f"{item['snippet']}"
                )
            sections.append(
                "## Existing dn.institute Articles\n" + "\n\n".join(parts)
            )

        # --- CoinGecko token info ---
        cg_parts = []
        for token in tokens:
            info = self.fetch_coingecko_info(token)
            if info:
                cg_parts.append(
                    f"### {info['name']} ({info['symbol'].upper()})\n"
                    f"Market Cap Rank: {info.get('market_cap_rank', 'N/A')}\n"
                    f"Current Price (USD): {info.get('current_price_usd', 'N/A')}\n"
                    f"24h Volume (USD): {info.get('total_volume_usd', 'N/A')}\n"
                    f"Description: {info.get('description', 'N/A')}"
                )
        if cg_parts:
            sections.append(
                "## Token Information (CoinGecko)\n" + "\n\n".join(cg_parts)
            )

        # --- Web search ---
        date_range = ""
        if start_date and end_date:
            date_range = f" {start_date} to {end_date}"

        web_query = f"{exchange} cryptocurrency wash trading market manipulation{date_range}"
        web_results = self.search_web(web_query, limit=MAX_WEB_RESULTS)

        # Also search for each token
        for token in tokens[:3]:  # limit to avoid too many searches
            token_results = self.search_web(
                f"{token} {exchange} trading anomaly", limit=2
            )
            web_results.extend(token_results)

        if web_results:
            parts = []
            seen_urls: set[str] = set()
            for item in web_results:
                url = item.get("url", "")
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                parts.append(
                    f"- **{item['title']}**\n"
                    f"  URL: {url}\n"
                    f"  {item['snippet']}"
                )
            sections.append(
                "## Recent Web Results\n" + "\n".join(parts[:MAX_WEB_RESULTS])
            )

        if not sections:
            logger.info("RAG retriever: no context found for %s / %s", exchange, tokens)
            return ""

        context = (
            f"# Background Context (auto-retrieved on {datetime.utcnow().strftime('%Y-%m-%d')})\n\n"
            + "\n\n".join(sections)
        )
        logger.info(
            "RAG context built: %d section(s), %d chars",
            len(sections),
            len(context),
        )
        return context

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_front_matter_field(content: str, field: str) -> Optional[str]:
        """Extract a field value from YAML front matter."""
        match = re.search(
            r"^---\s*\n(.*?)\n---", content, re.DOTALL
        )
        if not match:
            return None
        front_matter = match.group(1)
        # Simple single-line field extraction
        field_match = re.search(
            rf'^{field}:\s*["\']?(.+?)["\']?\s*$',
            front_matter,
            re.MULTILINE,
        )
        return field_match.group(1) if field_match else None

    @staticmethod
    def _extract_relevant_snippet(content: str, entity: str, max_length: int = MAX_SNIPPET_LENGTH) -> str:
        """
        Extract the most relevant paragraphs from an article that mention
        the entity, up to max_length characters.
        """
        # Remove front matter
        content = re.sub(r"^---\s*\n.*?\n---\s*\n", "", content, flags=re.DOTALL)

        paragraphs = re.split(r"\n\s*\n", content)
        relevant: list[str] = []
        total = 0

        for para in paragraphs:
            if entity.lower() in para.lower():
                # Skip Hugo shortcodes that are just image references
                if para.strip().startswith("{{<"):
                    continue
                relevant.append(para.strip())
                total += len(para)
                if total >= max_length:
                    break

        if not relevant:
            # Fallback: return the summary section or first paragraphs
            for para in paragraphs[:3]:
                if para.strip() and not para.strip().startswith("{{<"):
                    relevant.append(para.strip())

        snippet = "\n\n".join(relevant)
        return snippet[:max_length]
