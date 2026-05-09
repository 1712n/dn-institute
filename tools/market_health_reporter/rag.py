"""
RAG (Retrieval Augmented Generation) module for Market Health Reporter.

Fetches external context about exchanges and trading pairs to enrich
the LLM prompt with real-world information such as:
- Regulatory actions and warnings
- Known wash trading allegations
- News articles and research papers
- Exchange-specific incidents

This improves the quality of generated reports by grounding the analysis
in publicly available context beyond the raw metrics data.

🌰🌰🌰
"""

import requests
import html
import json
import re
from typing import Optional


# Default search queries generated from exchange and pair context
SEARCH_TEMPLATES = [
    "{exchange} wash trading allegations",
    "{exchange} market manipulation {pair}",
    "{exchange} regulatory action cryptocurrency",
    "{pair} trading volume suspicious {exchange}",
    "{exchange} fake volume report",
]

# Maximum number of search results to include in context
MAX_CONTEXT_ITEMS = 5

# Maximum characters per search result snippet
MAX_SNIPPET_LENGTH = 500


def build_search_queries(
    exchange: str, pair: str, start_date: str, end_date: str
) -> list[str]:
    """
    Build search queries from the analysis context.
    Uses the exchange name, pair, and date range to create targeted queries.
    """
    # Clean up pair for search (e.g., "btc-usdt" -> "BTC USDT")
    pair_clean = pair.replace("-", " ").upper()
    exchange_clean = exchange.replace("-", " ").title()
    year = start_date[:4]

    queries = []
    for template in SEARCH_TEMPLATES:
        query = template.format(
            exchange=exchange_clean, pair=pair_clean, year=year
        )
        queries.append(query)

    # Add a date-specific query
    queries.append(
        f"{exchange_clean} cryptocurrency {pair_clean} {year} investigation"
    )

    return queries


def search_brave(query: str, api_key: str, count: int = 3) -> list[dict]:
    """
    Search using Brave Search API.
    Returns list of {title, url, description} results.
    """
    if not api_key:
        return []

    try:
        resp = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": query, "count": str(count)},
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": api_key,
            },
            timeout=10,
        )
        if resp.status_code != 200:
            return []

        data = resp.json()
        results = data.get("web", {}).get("results", [])
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "description": r.get("description", "")[:MAX_SNIPPET_LENGTH],
            }
            for r in results[:count]
        ]
    except Exception as e:
        print(f"Brave search error for '{query}': {e}")
        return []


def search_duckduckgo(query: str, count: int = 3) -> list[dict]:
    """
    Fallback search using DuckDuckGo Instant Answer API (no API key required).
    Returns list of {title, url, description} results.
    """
    try:
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_redirect": "1"},
            headers={"User-Agent": "dn-institute-market-health-reporter/1.0"},
            timeout=10,
        )
        if resp.status_code != 200:
            return []

        data = resp.json()
        results = []

        # Extract from RelatedTopics
        for topic in data.get("RelatedTopics", [])[:count]:
            if "Text" in topic and "FirstURL" in topic:
                results.append(
                    {
                        "title": topic.get("Text", "")[:100],
                        "url": topic.get("FirstURL", ""),
                        "description": topic.get("Text", "")[:MAX_SNIPPET_LENGTH],
                    }
                )

        # Extract from Abstract if available
        if data.get("Abstract") and len(results) < count:
            results.insert(
                0,
                {
                    "title": data.get("Heading", query),
                    "url": data.get("AbstractURL", ""),
                    "description": data["Abstract"][:MAX_SNIPPET_LENGTH],
                },
            )

        return results[:count]
    except Exception as e:
        print(f"DuckDuckGo search error for '{query}': {e}")
        return []


def fetch_external_context(
    exchange: str,
    pair: str,
    start_date: str,
    end_date: str,
    brave_api_key: Optional[str] = None,
) -> str:
    """
    Fetch external context about the exchange and pair.

    Uses Brave Search if API key is provided, otherwise falls back to
    DuckDuckGo Instant Answer API (no key required).

    Returns a formatted string of context to include in the LLM prompt.
    """
    queries = build_search_queries(exchange, pair, start_date, end_date)

    all_results = []
    seen_urls = set()

    for query in queries:
        if len(all_results) >= MAX_CONTEXT_ITEMS:
            break
        if brave_api_key:
            results = search_brave(query, brave_api_key, count=2)
        else:
            results = search_duckduckgo(query, count=2)

        for r in results:
            if len(all_results) >= MAX_CONTEXT_ITEMS:
                break
            if not r.get("url") or not r["url"].startswith("http"):
                continue
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                all_results.append(r)

    if not all_results:
        return ""

    # Format context as structured text for the LLM
    context_parts = [
        "<external_context>",
        "The following external sources provide context about the exchange and "
        "trading pair being analyzed. Use this information to enrich your "
        "analysis, cite relevant findings, and cross-reference with the "
        "metrics data.",
        "",
    ]

    for i, result in enumerate(all_results, 1):
        title = html.escape(result.get("title", ""), quote=False)
        desc = html.escape(result.get("description", ""), quote=False)
        context_parts.append(f"[{i}] {title}")
        context_parts.append(f"    URL: {result['url']}")
        if desc:
            context_parts.append(f"    Summary: {desc}")
        context_parts.append("")

    context_parts.append("</external_context>")

    return "\n".join(context_parts)


def fetch_wiki_context(
    exchange: str,
    pair: str,
    github_token: Optional[str] = None,
    repo_name: str = "1712n/dn-institute",
) -> str:
    """
    Fetch context from existing dn.institute wiki articles.
    Searches the market-health and attacks directories for relevant content.
    """
    if not github_token:
        return ""

    try:
        # Search for existing articles about the exchange
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "dn-institute-market-health-reporter",
        }

        # Use GitHub search API to find relevant files
        exchange_clean = exchange.replace("-", " ").lower()
        query = f"repo:{repo_name} path:content/ {exchange_clean}"
        resp = requests.get(
            "https://api.github.com/search/code",
            params={"q": query, "per_page": 5},
            headers=headers,
            timeout=15,
        )

        if resp.status_code != 200:
            return ""

        data = resp.json()
        items = data.get("items", [])

        if not items:
            return ""

        context_parts = [
            "<wiki_context>",
            f"The following existing wiki articles mention {exchange_clean}. "
            "Reference these for consistency in naming, methodology, and style.",
            "",
        ]

        for item in items[:3]:
            path = item.get("path", "")
            context_parts.append(f"- {path}")

        context_parts.append("</wiki_context>")

        return "\n".join(context_parts)
    except Exception as e:
        print(f"Wiki context fetch error: {e}")
        return ""
