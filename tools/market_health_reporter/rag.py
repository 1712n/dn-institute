"""
RAG module for the Market Health Reporter.
Retrieves relevant external articles to provide additional context
for market surveillance report generation.
"""

import json
import os
import requests
from typing import Optional


SEARCH_API_URL = "https://api.search.brave.com/res/v1/web/search"
MAX_CONTEXT_CHARS = 4000
MAX_RESULTS = 5


def search_articles(
    exchange: str,
    pair: str,
    api_key: str,
    additional_terms: str = ""
) -> list[dict]:
    """Search for relevant market manipulation articles about the exchange."""
    query = f"{exchange} wash trading market manipulation {pair} {additional_terms}".strip()

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key
    }
    params = {
        "q": query,
        "count": MAX_RESULTS,
        "freshness": "py"  # past year
    }

    try:
        resp = requests.get(SEARCH_API_URL, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("web", {}).get("results", [])
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "description": r.get("description", ""),
            }
            for r in results
        ]
    except Exception as e:
        print(f"[rag] Search failed: {e}")
        return []


def fetch_article_content(url: str, max_chars: int = 2000) -> str:
    """Fetch and extract text content from a URL."""
    try:
        resp = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "MarketHealthReporter/1.0"}
        )
        resp.raise_for_status()
        text = resp.text

        # Basic HTML stripping
        import re
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        return text[:max_chars]
    except Exception as e:
        print(f"[rag] Failed to fetch {url}: {e}")
        return ""


def build_rag_context(
    exchange: str,
    pair: str,
    search_api_key: Optional[str] = None
) -> str:
    """Build RAG context string from external articles.

    Searches for relevant articles about the exchange and pair,
    fetches their content, and returns a formatted context block.
    """
    api_key = search_api_key or os.environ.get("BRAVE_SEARCH_API_KEY", "")
    if not api_key:
        print("[rag] No search API key configured, skipping RAG context")
        return ""

    print(f"[rag] Searching for context: {exchange} {pair}")
    articles = search_articles(exchange, pair, api_key)

    if not articles:
        print("[rag] No articles found")
        return ""

    context_parts = []
    total_chars = 0

    for article in articles:
        if total_chars >= MAX_CONTEXT_CHARS:
            break

        content = fetch_article_content(article["url"])
        if not content:
            content = article.get("description", "")

        if content:
            remaining = MAX_CONTEXT_CHARS - total_chars
            snippet = content[:remaining]
            context_parts.append(
                f"Source: {article['title']}\n"
                f"URL: {article['url']}\n"
                f"Content: {snippet}\n"
            )
            total_chars += len(snippet)

    if not context_parts:
        return ""

    context = "\n---\n".join(context_parts)
    print(f"[rag] Built context from {len(context_parts)} articles ({total_chars} chars)")

    return (
        "\n\n<external_context>\n"
        "The following are excerpts from external articles about this exchange "
        "and its trading practices. Use them as additional context for your analysis, "
        "but only reference them if they directly support findings from the data.\n\n"
        f"{context}\n"
        "</external_context>\n"
    )
