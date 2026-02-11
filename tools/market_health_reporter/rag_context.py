"""
RAG context retrieval for Market Health Reporter.

Retrieves relevant context from two sources:
1. Local wiki articles in the repository (no API key required)
2. Web search via DuckDuckGo for real-time news (no API key required)
"""

import os
import re
import yaml
import logging
from typing import Optional

import requests
from bs4 import BeautifulSoup
import bleach

logger = logging.getLogger(__name__)

WIKI_POSTS_DIR = "content/research/market-health/posts"


def load_wiki_articles(exchange: str, repo_root: str = ".") -> list[dict]:
    """
    Search local wiki articles for content relevant to the given exchange.
    Returns a list of dicts with 'title', 'content', and 'source' keys.
    """
    posts_dir = os.path.join(repo_root, WIKI_POSTS_DIR)
    if not os.path.isdir(posts_dir):
        logger.warning(f"Wiki posts directory not found: {posts_dir}")
        return []

    articles = []
    exchange_lower = exchange.lower().replace(".", "").replace("-", "").replace(" ", "")

    for entry in os.listdir(posts_dir):
        entry_path = os.path.join(posts_dir, entry)
        if not os.path.isdir(entry_path):
            continue

        index_file = os.path.join(entry_path, "index.md")
        if not os.path.isfile(index_file):
            continue

        with open(index_file, "r", encoding="utf-8") as f:
            content = f.read()

        frontmatter, body = _parse_frontmatter(content)
        if not frontmatter:
            continue

        entities = frontmatter.get("entities", [])
        title = frontmatter.get("title", "")

        # Check if exchange matches any entity or appears in directory name
        dir_lower = entry.lower().replace(".", "").replace("-", "").replace(" ", "")
        entity_match = any(
            exchange_lower in str(e).lower().replace(".", "").replace("-", "").replace(" ", "")
            or str(e).lower().replace(".", "").replace("-", "").replace(" ", "") in exchange_lower
            for e in entities
        )

        if entity_match or exchange_lower in dir_lower:
            # Truncate to essential sections (Summary + key evidence)
            trimmed = _trim_article(body)
            articles.append({
                "title": title,
                "content": trimmed,
                "source": f"wiki:{entry}",
            })

    logger.info(f"Found {len(articles)} local wiki article(s) for '{exchange}'")
    return articles


def search_web(exchange: str, pair: str, max_results: int = 5) -> list[dict]:
    """
    Search the web for recent news about the exchange using DuckDuckGo.
    Returns a list of dicts with 'title', 'content', and 'source' keys.
    No API key required.
    """
    results = []
    queries = [
        f"{exchange} cryptocurrency wash trading manipulation",
        f"{exchange} {pair} trading volume anomaly",
    ]

    for query in queries:
        try:
            fetched = _duckduckgo_search(query, max_results=3)
            results.extend(fetched)
        except Exception as e:
            logger.warning(f"Web search failed for query '{query}': {e}")

    # Deduplicate by URL
    seen_urls = set()
    unique = []
    for r in results:
        if r["source"] not in seen_urls:
            seen_urls.add(r["source"])
            unique.append(r)

    return unique[:max_results]


def build_rag_context(
    exchange: str,
    pair: str,
    repo_root: str = ".",
    include_web_search: bool = True,
    max_context_chars: int = 8000,
) -> str:
    """
    Build a formatted RAG context string for injection into the LLM prompt.

    Args:
        exchange: Exchange name (e.g., "huobi", "binance")
        pair: Trading pair (e.g., "btc-usdt")
        repo_root: Path to the repository root
        include_web_search: Whether to include web search results
        max_context_chars: Maximum characters for the context block

    Returns:
        Formatted context string ready for prompt injection, or empty string
        if no relevant context found.
    """
    sections = []
    char_count = 0

    # 1. Local wiki articles (highest quality, always available)
    wiki_articles = load_wiki_articles(exchange, repo_root)
    for article in wiki_articles:
        section = f"### {article['title']}\nSource: {article['source']}\n\n{article['content']}"
        if char_count + len(section) > max_context_chars:
            break
        sections.append(section)
        char_count += len(section)

    # 2. Web search results (real-time, if enabled)
    if include_web_search:
        web_results = search_web(exchange, pair)
        for result in web_results:
            section = f"### {result['title']}\nSource: {result['source']}\n\n{result['content']}"
            if char_count + len(section) > max_context_chars:
                break
            sections.append(section)
            char_count += len(section)

    if not sections:
        return ""

    context = "\n\n---\n\n".join(sections)
    return (
        f"<external_context>\n"
        f"The following is additional context about {exchange} from wiki articles and recent news. "
        f"Reference specific events or findings from this context only where they help explain "
        f"anomalies detected in the data. Do not fabricate information beyond what is provided.\n\n"
        f"{context}\n"
        f"</external_context>"
    )


def _parse_frontmatter(content: str) -> tuple[Optional[dict], str]:
    """Parse YAML frontmatter from markdown content."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
    if not match:
        return None, content
    try:
        frontmatter = yaml.safe_load(match.group(1))
        body = match.group(2)
        return frontmatter, body
    except yaml.YAMLError:
        return None, content


def _trim_article(body: str, max_chars: int = 2000) -> str:
    """
    Trim article to essential sections: Summary and first evidence section.
    Strips Hugo shortcodes and image references.
    """
    # Remove Hugo figure shortcodes
    body = re.sub(r"\{\{<.*?>}}", "", body)
    # Remove image markdown
    body = re.sub(r"!\[.*?\]\(.*?\)", "", body)
    # Collapse multiple blank lines
    body = re.sub(r"\n{3,}", "\n\n", body)

    if len(body) <= max_chars:
        return body.strip()

    # Try to capture Summary section at minimum
    summary_match = re.search(r"(## Summary.*?)(?=\n## |\Z)", body, re.DOTALL)
    if summary_match:
        result = summary_match.group(1).strip()
        if len(result) <= max_chars:
            return result

    return body[:max_chars].strip()


def _duckduckgo_search(query: str, max_results: int = 3) -> list[dict]:
    """
    Search DuckDuckGo using the duckduckgo-search package.
    Falls back to a simple HTML scrape if the package API changes.
    """
    results = []

    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                title = _clean_text(r.get("title", ""))
                body = _clean_text(r.get("body", ""))
                url = r.get("href", r.get("link", ""))
                if title and body:
                    results.append({
                        "title": title,
                        "content": body,
                        "source": url,
                    })
    except ImportError:
        logger.warning("duckduckgo-search package not available, skipping web search")
    except Exception as e:
        logger.warning(f"DuckDuckGo search failed: {e}")
        # Fallback: try DuckDuckGo lite HTML
        try:
            results = _ddg_lite_fallback(query, max_results)
        except Exception as e2:
            logger.warning(f"DuckDuckGo lite fallback also failed: {e2}")

    return results


def _ddg_lite_fallback(query: str, max_results: int = 3) -> list[dict]:
    """Fallback: scrape DuckDuckGo lite for search results."""
    resp = requests.get(
        "https://lite.duckduckgo.com/lite/",
        params={"q": query},
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10,
    )
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []

    for link in soup.find_all("a", class_="result-link"):
        title = _clean_text(link.get_text())
        url = link.get("href", "")
        snippet_td = link.find_parent("tr")
        snippet = ""
        if snippet_td:
            next_tr = snippet_td.find_next_sibling("tr")
            if next_tr:
                snippet = _clean_text(next_tr.get_text())
        if title and url:
            results.append({
                "title": title,
                "content": snippet,
                "source": url,
            })
            if len(results) >= max_results:
                break

    return results


def _clean_text(text: str) -> str:
    """Clean text by stripping HTML tags and normalizing whitespace."""
    text = bleach.clean(text, tags=[], strip=True)
    text = BeautifulSoup(text, "html.parser").get_text()
    text = re.sub(r"\s+", " ", text).strip()
    return text
