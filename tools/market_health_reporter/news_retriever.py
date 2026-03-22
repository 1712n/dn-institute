"""
Retrieves external news and article context for market health reports.

Searches for recent news about the exchange and trading pair being analyzed,
extracts article content, and formats it as structured context for the LLM.
"""

import logging
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from tiktoken import encoding_for_model

logger = logging.getLogger(__name__)

MAX_ARTICLE_TOKENS = 2000
MAX_CONTEXT_TOKENS = 25000
MAX_SEARCH_RESULTS = 8
FETCH_TIMEOUT = 10

EXCHANGE_ALIASES = {
    "huobi": ["huobi", "htx"],
    "htx": ["huobi", "htx"],
    "okex": ["okex", "okx"],
    "okx": ["okex", "okx"],
    "gateio": ["gate.io", "gateio", "gate"],
    "gate.io": ["gate.io", "gateio", "gate"],
}


def build_search_queries(exchange: str, pair: str) -> List[str]:
    """Generate search queries for the exchange and trading pair."""
    token = pair.split("/")[0] if "/" in pair else pair
    aliases = EXCHANGE_ALIASES.get(exchange.lower(), [exchange])
    primary = aliases[0]

    return [
        f"{primary} exchange wash trading",
        f"{primary} exchange market manipulation",
        f"{primary} {token} trading anomaly",
        f"{primary} exchange regulatory investigation",
    ]


def search_news(query: str, max_results: int = MAX_SEARCH_RESULTS) -> List[Dict]:
    """Search DuckDuckGo for news articles."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(
                keywords=query,
                region="wt-wt",
                safesearch="off",
                timelimit="y",
                max_results=max_results,
            ))
        return results
    except Exception as e:
        logger.warning("News search failed for '%s': %s", query, e)
        return []


def search_web(query: str, max_results: int = MAX_SEARCH_RESULTS) -> List[Dict]:
    """Search DuckDuckGo for web results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(
                keywords=query,
                max_results=max_results,
            ))
        return results
    except Exception as e:
        logger.warning("Web search failed for '%s': %s", query, e)
        return []


def fetch_article_text(url: str) -> Optional[str]:
    """Fetch and extract clean text content from a URL."""
    try:
        resp = requests.get(
            url,
            timeout=FETCH_TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0 (compatible; DNI-MarketHealthReporter/1.0)"},
        )
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "aside", "iframe"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)

        # Remove excessive blank lines
        lines = [line for line in text.splitlines() if line.strip()]
        return "\n".join(lines)
    except Exception as e:
        logger.debug("Failed to fetch %s: %s", url, e)
        return None


def truncate_to_tokens(text: str, max_tokens: int, encoding) -> str:
    """Truncate text to fit within a token budget."""
    tokens = encoding.encode(text)
    if len(tokens) <= max_tokens:
        return text
    return encoding.decode(tokens[:max_tokens])


def deduplicate_results(results: List[Dict]) -> List[Dict]:
    """Remove duplicate results by URL."""
    seen = set()
    unique = []
    for r in results:
        url = r.get("url") or r.get("href", "")
        if url and url not in seen:
            seen.add(url)
            unique.append(r)
    return unique


def format_context(articles: List[Dict]) -> str:
    """Format retrieved articles as XML-structured context for the LLM prompt."""
    if not articles:
        return ""

    items = []
    for i, article in enumerate(articles, 1):
        items.append(
            f'<source index="{i}">\n'
            f'  <title>{article.get("title", "")}</title>\n'
            f'  <date>{article.get("date", "")}</date>\n'
            f'  <url>{article.get("url", "")}</url>\n'
            f'  <content>\n{article.get("content", "")}\n  </content>\n'
            f'</source>'
        )
    return "<external_context>\n" + "\n".join(items) + "\n</external_context>"


def retrieve_news_context(
    exchange: str,
    pair: str,
    max_context_tokens: int = MAX_CONTEXT_TOKENS,
) -> str:
    """
    Full retrieval pipeline: search -> fetch -> deduplicate -> truncate -> format.

    Returns an XML-formatted string of external article context, or an empty
    string if no relevant articles are found.
    """
    encoding = encoding_for_model("gpt-4")
    queries = build_search_queries(exchange, pair)

    # Collect results from news and web searches
    all_results = []
    for query in queries:
        all_results.extend(search_news(query, max_results=5))
        all_results.extend(search_web(query, max_results=5))

    unique_results = deduplicate_results(all_results)
    logger.info("Found %d unique results across %d queries", len(unique_results), len(queries))

    # Fetch and process articles within token budget
    articles = []
    token_count = 0

    for result in unique_results:
        url = result.get("url") or result.get("href", "")

        # Try fetching full content, fall back to snippet
        content = fetch_article_text(url) if url else None
        if not content:
            content = result.get("body", "")
        if not content:
            continue

        content = truncate_to_tokens(content, MAX_ARTICLE_TOKENS, encoding)
        content_tokens = len(encoding.encode(content))

        if token_count + content_tokens > max_context_tokens:
            break

        articles.append({
            "title": result.get("title", ""),
            "date": result.get("date", ""),
            "url": url,
            "content": content,
        })
        token_count += content_tokens

    logger.info("Retrieved %d articles (%d tokens)", len(articles), token_count)
    return format_context(articles)
