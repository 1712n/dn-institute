"""
News source adapters for fetching articles related to a market venue and pair.

Each source returns a list of ArticleRef namedtuples containing a title,
URL, and optional snippet.  Sources degrade gracefully — a missing API key
or network error returns an empty list rather than raising.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import requests

logger = logging.getLogger(__name__)

_HTTP_TIMEOUT = 12  # seconds


@dataclass(frozen=True)
class ArticleRef:
    """Lightweight reference to a news article before full-text extraction."""
    title: str
    url: str
    snippet: str = ""


def _build_search_queries(marketvenueid: str, pairid: str, start: str, end: str) -> list[str]:
    """
    Generate diverse search queries to maximise recall of relevant articles.
    """
    pair_parts = []
    for sep in ("-", "/", "_"):
        if sep in pairid:
            pair_parts = [p.upper() for p in pairid.split(sep) if p]
            break
    if not pair_parts:
        pair_parts = [pairid.upper()]

    venue = marketvenueid.capitalize()
    pair_label = "/".join(pair_parts)

    return [
        f"{venue} {pair_label} wash trading manipulation {start}",
        f"{venue} exchange anomaly suspicious trading volume",
        f"{pair_parts[0]} market manipulation {venue} {end}",
        f"{venue} crypto exchange investigation regulatory",
    ]


# --------------------------------------------------------------------------- #
# Brave Search
# --------------------------------------------------------------------------- #

def fetch_brave(
    marketvenueid: str,
    pairid: str,
    start: str,
    end: str,
    api_key: str,
    max_results: int = 10,
) -> list[ArticleRef]:
    """Fetch article references via Brave Web Search API."""
    if not api_key:
        return []

    articles: list[ArticleRef] = []
    queries = _build_search_queries(marketvenueid, pairid, start, end)

    seen_urls: set[str] = set()
    for query in queries[:2]:  # limit to 2 queries to stay within rate limits
        try:
            resp = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers={"X-Subscription-Token": api_key, "Accept": "application/json"},
                params={"q": query, "count": min(max_results, 5), "freshness": "pm"},
                timeout=_HTTP_TIMEOUT,
            )
            resp.raise_for_status()
            for result in resp.json().get("web", {}).get("results", []):
                url = result.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    articles.append(ArticleRef(
                        title=result.get("title", ""),
                        url=url,
                        snippet=result.get("description", ""),
                    ))
        except Exception as exc:
            logger.warning("Brave search failed for query %r: %s", query, exc)

    return articles[:max_results]


# --------------------------------------------------------------------------- #
# CryptoPanic
# --------------------------------------------------------------------------- #

CRYPTOPANIC_API_URL = "https://cryptopanic.com/api/v1/posts/"


def fetch_cryptopanic(
    marketvenueid: str,
    pairid: str,
    auth_token: str = "",
    max_results: int = 10,
) -> list[ArticleRef]:
    """Fetch article references from CryptoPanic news aggregator."""
    pair_parts = []
    for sep in ("-", "/", "_"):
        if sep in pairid:
            pair_parts = [p.upper() for p in pairid.split(sep) if p]
            break
    if not pair_parts:
        pair_parts = [pairid.upper()]

    params: dict = {
        "currencies": ",".join(pair_parts),
        "kind": "news",
        "filter": "hot",
        "public": "true",
    }
    if auth_token:
        params["auth_token"] = auth_token

    try:
        resp = requests.get(CRYPTOPANIC_API_URL, params=params, timeout=_HTTP_TIMEOUT)
        resp.raise_for_status()
        results = resp.json().get("results", [])
    except Exception as exc:
        logger.warning("CryptoPanic fetch failed: %s", exc)
        return []

    articles: list[ArticleRef] = []
    for post in results[:max_results]:
        url = post.get("url", "")
        if url:
            articles.append(ArticleRef(
                title=post.get("title", ""),
                url=url,
                snippet="",
            ))
    return articles


# --------------------------------------------------------------------------- #
# Aggregate
# --------------------------------------------------------------------------- #

def fetch_all_sources(
    marketvenueid: str,
    pairid: str,
    start: str,
    end: str,
    brave_api_key: str = "",
    cryptopanic_token: str = "",
    max_total: int = 15,
) -> list[ArticleRef]:
    """
    Aggregate article references from all available sources, deduplicated by URL.
    """
    refs: list[ArticleRef] = []
    refs.extend(fetch_brave(marketvenueid, pairid, start, end, brave_api_key))
    refs.extend(fetch_cryptopanic(marketvenueid, pairid, cryptopanic_token))

    # Deduplicate by URL
    seen: set[str] = set()
    unique: list[ArticleRef] = []
    for ref in refs:
        if ref.url not in seen:
            seen.add(ref.url)
            unique.append(ref)

    return unique[:max_total]
