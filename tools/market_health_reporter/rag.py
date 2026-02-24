"""
RAG (Retrieval-Augmented Generation) module for Market Health Reporter.

Fetches recent news articles related to a market venue and trading pair from
CryptoPanic, extracts clean article text, and returns a token-budget-capped
context string that can be injected into the LLM prompt.

Usage::

    from tools.market_health_reporter.rag import build_rag_context

    context = build_rag_context(
        marketvenueid="binance",
        pairid="btc-usdt",
        cryptopanic_token="<your_token>",   # optional – pass "" for public feed
        max_tokens=2000,
    )
    # context is either a non-empty string or None (graceful fallback)
"""

from __future__ import annotations

import logging
import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CRYPTOPANIC_API_URL = "https://cryptopanic.com/api/v1/posts/"

# Approximate average token length in characters (conservative estimate)
_CHARS_PER_TOKEN = 4

# Hard cap on characters fetched per article body
_MAX_ARTICLE_CHARS = 8_000

# Request timeout for external HTTP calls (seconds)
_HTTP_TIMEOUT = 10

# Maximum number of articles to fetch from CryptoPanic
_MAX_ARTICLES = 10

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_currencies(pairid: str) -> list[str]:
    """
    Derive currency symbols from a pairid like 'btc-usdt' → ['BTC', 'USDT'].
    Falls back to the whole pairid as a single symbol if no separator is found.
    """
    for sep in ("-", "/", "_"):
        if sep in pairid:
            return [p.upper() for p in pairid.split(sep) if p]
    return [pairid.upper()]


def _fetch_cryptopanic_posts(
    currencies: list[str],
    auth_token: str,
    kind: str = "news",
    filter_: str = "hot",
) -> list[dict]:
    """
    Fetch posts from CryptoPanic API for the given currency symbols.

    Returns a list of post dicts (may be empty on error).
    """
    params: dict = {
        "currencies": ",".join(currencies),
        "kind": kind,
        "filter": filter_,
        "public": "true",
    }
    if auth_token:
        params["auth_token"] = auth_token

    try:
        resp = requests.get(
            CRYPTOPANIC_API_URL, params=params, timeout=_HTTP_TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", [])
    except Exception as exc:  # noqa: BLE001
        logger.warning("CryptoPanic fetch failed: %s", exc)
        return []


def _fetch_article_text(url: str) -> Optional[str]:
    """
    Fetch a URL and return clean plain-text content (HTML stripped).

    Returns None if the fetch or extraction fails.
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (compatible; MarketHealthReporter/1.0; "
                "+https://github.com/1712n/dn-institute)"
            )
        }
        resp = requests.get(url, headers=headers, timeout=_HTTP_TIMEOUT)
        resp.raise_for_status()

        content_type = resp.headers.get("Content-Type", "")
        if "html" not in content_type.lower():
            # Not HTML – skip
            return None

        soup = BeautifulSoup(resp.text, "lxml")

        # Remove non-content elements
        for tag in soup(["script", "style", "nav", "header", "footer",
                         "aside", "form", "noscript", "iframe", "meta",
                         "link", "figure"]):
            tag.decompose()

        # Prefer <article> or <main> if available
        body_node = soup.find("article") or soup.find("main") or soup.body
        if body_node is None:
            return None

        raw_text = body_node.get_text(separator="\n")

        # Collapse excessive whitespace
        cleaned = re.sub(r"\n{3,}", "\n\n", raw_text)
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = cleaned.strip()

        if len(cleaned) < 100:
            return None

        return cleaned[:_MAX_ARTICLE_CHARS]

    except Exception as exc:  # noqa: BLE001
        logger.debug("Article fetch failed for %s: %s", url, exc)
        return None


def _is_relevant(text: str, keywords: list[str]) -> bool:
    """
    Return True if the text mentions at least one of the keywords
    (case-insensitive).
    """
    lowered = text.lower()
    return any(kw.lower() in lowered for kw in keywords)


def _token_count(text: str) -> int:
    """Rough token count estimate (characters / 4)."""
    return len(text) // _CHARS_PER_TOKEN


def _truncate_to_token_budget(text: str, budget: int) -> str:
    """Truncate *text* so that its estimated token count ≤ *budget*."""
    max_chars = budget * _CHARS_PER_TOKEN
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + " [...]"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def fetch_news_posts(
    marketvenueid: str,
    pairid: str,
    cryptopanic_token: str = "",
    max_articles: int = _MAX_ARTICLES,
) -> list[dict]:
    """
    Retrieve CryptoPanic news posts relevant to *marketvenueid* / *pairid*.

    Parameters
    ----------
    marketvenueid:
        Exchange identifier (e.g. ``"binance"``).
    pairid:
        Trading pair string (e.g. ``"btc-usdt"``).
    cryptopanic_token:
        CryptoPanic API auth token. Pass empty string to use public endpoint
        (rate-limited, but functional).
    max_articles:
        Maximum number of posts to return.

    Returns
    -------
    list[dict]
        List of post dicts from the CryptoPanic API (may be empty).
    """
    currencies = _extract_currencies(pairid)
    posts = _fetch_cryptopanic_posts(currencies, cryptopanic_token)

    # Also try fetching for the venue name if it looks like a known coin ticker
    if marketvenueid.upper() not in currencies:
        venue_posts = _fetch_cryptopanic_posts(
            [marketvenueid.upper()], cryptopanic_token
        )
        # Deduplicate by URL
        seen_urls = {p.get("url") for p in posts}
        for p in venue_posts:
            if p.get("url") not in seen_urls:
                posts.append(p)
                seen_urls.add(p.get("url"))

    return posts[:max_articles]


def build_rag_context(
    marketvenueid: str,
    pairid: str,
    cryptopanic_token: str = "",
    max_tokens: int = 2000,
) -> Optional[str]:
    """
    Build a RAG context string for the given market venue and pair.

    Fetches recent news, scrapes article full text, filters for relevance,
    and returns a clean context block within *max_tokens*.

    Parameters
    ----------
    marketvenueid:
        Exchange identifier (e.g. ``"binance"``).
    pairid:
        Trading pair identifier (e.g. ``"btc-usdt"``).
    cryptopanic_token:
        CryptoPanic API auth token (empty string uses public endpoint).
    max_tokens:
        Approximate maximum token budget for the returned context string.

    Returns
    -------
    str or None
        A formatted context string ready to inject into the LLM prompt, or
        ``None`` if no relevant content could be retrieved (graceful fallback).
    """
    currencies = _extract_currencies(pairid)
    # Build keyword list for relevance filtering
    keywords = currencies + [marketvenueid]

    posts = fetch_news_posts(marketvenueid, pairid, cryptopanic_token)
    if not posts:
        logger.info("No CryptoPanic posts found for %s/%s", marketvenueid, pairid)
        return None

    snippets: list[str] = []
    token_budget = max_tokens

    for post in posts:
        if token_budget <= 0:
            break

        title = post.get("title", "")
        url = post.get("url") or post.get("source", {}).get("url", "")
        published = post.get("published_at", "")

        if not url:
            continue

        # Try to fetch full article text; fall back to title-only snippet
        body = _fetch_article_text(url)

        if body:
            # Filter: article must mention at least one relevant keyword
            combined = f"{title} {body}"
            if not _is_relevant(combined, keywords):
                logger.debug("Skipping unrelated article: %s", title)
                continue
            content = body
        else:
            # Use title only if we couldn't retrieve the body
            if not _is_relevant(title, keywords):
                continue
            content = "(Full text unavailable)"

        # Compose per-article snippet
        snippet = f"### {title}\n_Source: {url}_\n_Published: {published}_\n\n{content}"
        snippet_tokens = _token_count(snippet)

        if snippet_tokens > token_budget:
            # Try to fit a truncated version
            snippet = _truncate_to_token_budget(snippet, token_budget)

        snippets.append(snippet)
        token_budget -= _token_count(snippet)

        # Small delay to be polite to external servers
        time.sleep(0.3)

    if not snippets:
        logger.info(
            "No relevant articles found after filtering for %s/%s",
            marketvenueid,
            pairid,
        )
        return None

    header = (
        f"## Recent News Context for {marketvenueid.upper()} / {pairid.upper()}\n\n"
        "The following articles were retrieved automatically to provide additional "
        "context. Use them to enrich your market analysis where relevant.\n\n"
    )
    return header + "\n\n---\n\n".join(snippets)
