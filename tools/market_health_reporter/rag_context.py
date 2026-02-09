"""
Real-time RAG context retrieval for the Market Health Reporter.

Fetches recent news and articles about a given exchange and trading pair
from the web using the Brave Search API. Content is cleaned of HTML artifacts
and formatted for injection into the reporter's LLM prompt, providing
up-to-date context on events that may explain anomalous market data.
"""

import logging
import requests
from bs4 import BeautifulSoup
import bleach
from typing import Optional
from tenacity import retry, wait_exponential, stop_after_attempt

logger = logging.getLogger(__name__)


def clean_text(raw_text: str) -> str:
    """
    Remove HTML tags, entities, and artifacts from text.
    Returns clean, readable plain text.
    """
    # Parse with BeautifulSoup to handle any HTML fragments
    soup = BeautifulSoup(raw_text, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    # Sanitize with bleach to strip any remaining tags/entities
    text = bleach.clean(text, tags=[], attributes={}, strip=True)
    # Normalize whitespace
    text = " ".join(text.split())
    return text


@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def _brave_search(query: str, api_key: str, count: int = 10) -> dict:
    """
    Execute a search query against the Brave Search API.
    """
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": api_key,
    }
    resp = requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        params={"q": query, "count": count},
        headers=headers,
        timeout=30,
    )
    if resp.status_code != 200:
        logger.error(f"Brave search failed ({resp.status_code}): {resp.text}")
        return {}
    return resp.json()


def _extract_news_items(search_response: dict) -> list[dict]:
    """
    Extract and clean news results from a Brave search response.
    Returns a list of dicts with 'title', 'description', 'url', and 'age'.
    """
    items = []
    for news in search_response.get("news", {}).get("results", []):
        description = clean_text(news.get("description", ""))
        if len(description) < 20:
            continue
        items.append({
            "title": clean_text(news.get("title", "")),
            "description": description,
            "url": news.get("url", ""),
            "age": news.get("age", ""),
            "source": news.get("meta_url", {}).get("hostname", ""),
        })
    return items


def _extract_web_items(search_response: dict) -> list[dict]:
    """
    Extract and clean web results from a Brave search response.
    Returns a list of dicts with 'title', 'description', and 'url'.
    """
    items = []
    for web in search_response.get("web", {}).get("results", []):
        description = clean_text(web.get("description", ""))
        if len(description) < 20:
            continue
        items.append({
            "title": clean_text(web.get("title", "")),
            "description": description,
            "url": web.get("url", ""),
        })
    return items


def _build_search_queries(exchange: str, pair: str, start: str, end: str) -> list[str]:
    """
    Build a set of targeted search queries for the given exchange, pair, and period.
    Multiple queries improve recall across different angles.
    """
    base_token = pair.split("-")[0].upper() if "-" in pair else pair.upper()
    queries = [
        f"{exchange} exchange {base_token} news {start} {end}",
        f"{exchange} cryptocurrency wash trading manipulation {start}",
        f"{exchange} exchange regulatory news {start}",
    ]
    return queries


def _format_context(news_items: list[dict], web_items: list[dict], max_items: int = 8) -> str:
    """
    Format retrieved items into a clean text block for prompt injection.
    Prioritizes news items, then fills with web results up to max_items.
    """
    sections = []
    count = 0

    for item in news_items:
        if count >= max_items:
            break
        section = (
            f"- [{item['title']}]({item['url']})\n"
            f"  Source: {item.get('source', 'N/A')} | {item.get('age', 'N/A')}\n"
            f"  {item['description']}"
        )
        sections.append(section)
        count += 1

    for item in web_items:
        if count >= max_items:
            break
        section = (
            f"- [{item['title']}]({item['url']})\n"
            f"  {item['description']}"
        )
        sections.append(section)
        count += 1

    return "\n\n".join(sections)


def fetch_relevant_context(
    exchange: str,
    pair: str,
    start: str,
    end: str,
    brave_api_key: str,
    max_results: int = 8,
) -> Optional[str]:
    """
    Fetch real-time news and web context relevant to a market health report.

    Searches for recent news about the exchange, trading pair, and time period
    using the Brave Search API. Results are cleaned of HTML artifacts and
    formatted as a context block that can be injected into the LLM prompt.

    Args:
        exchange: Exchange name (e.g., 'huobi', 'binance').
        pair: Trading pair (e.g., 'btc-usdt').
        start: Analysis period start date.
        end: Analysis period end date.
        brave_api_key: API key for Brave Search.
        max_results: Maximum number of context items to include.

    Returns:
        Formatted context string, or None if no results found.
    """
    queries = _build_search_queries(exchange, pair, start, end)
    all_news = []
    all_web = []
    seen_urls = set()

    for query in queries:
        logger.info(f"Searching: {query}")
        try:
            response = _brave_search(query, brave_api_key)
        except Exception as e:
            logger.warning(f"Search failed for query '{query}': {e}")
            continue

        for item in _extract_news_items(response):
            if item["url"] not in seen_urls:
                all_news.append(item)
                seen_urls.add(item["url"])

        for item in _extract_web_items(response):
            if item["url"] not in seen_urls:
                all_web.append(item)
                seen_urls.add(item["url"])

    if not all_news and not all_web:
        logger.warning("No relevant context found from web search.")
        return None

    context = _format_context(all_news, all_web, max_items=max_results)
    logger.info(f"Retrieved {len(all_news)} news + {len(all_web)} web results.")
    return context
