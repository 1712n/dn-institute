"""
RAG (Retrieval-Augmented Generation) context module for Market Health Reporter.

Retrieves and ranks relevant context from multiple sources:
1. Local wiki articles in the repository (zero-config, highest quality)
2. Web search via DuckDuckGo (real-time news, no API key required)
3. Full article extraction from search result URLs for deeper context

Retrieved content is cleaned, chunked, scored by relevance using TF-IDF,
and formatted for injection into the LLM prompt.
"""

import os
import re
import math
import logging
from collections import Counter
from typing import Optional

import yaml
import requests
import bleach
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

WIKI_POSTS_DIR = "content/research/market-health/posts"

# ---------------------------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------------------------


def clean_text(raw: str) -> str:
    """Strip HTML tags, entities, and normalize whitespace."""
    import html as html_mod
    soup = BeautifulSoup(raw, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    text = bleach.clean(text, tags=[], attributes={}, strip=True)
    text = html_mod.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ---------------------------------------------------------------------------
# TF-IDF relevance scoring
# ---------------------------------------------------------------------------


def _tokenize(text: str) -> list[str]:
    """Lowercase tokenization, letters and digits only."""
    return re.findall(r"[a-z0-9]+", text.lower())


def _term_freq(tokens: list[str]) -> dict[str, float]:
    counts = Counter(tokens)
    total = len(tokens) or 1
    return {t: c / total for t, c in counts.items()}


def _idf(documents: list[list[str]]) -> dict[str, float]:
    n = len(documents) or 1
    df: dict[str, int] = {}
    for doc in documents:
        for term in set(doc):
            df[term] = df.get(term, 0) + 1
    return {t: math.log(n / d) for t, d in df.items()}


def score_relevance(query_tokens: list[str], text: str, idf_map: dict[str, float]) -> float:
    """Score a text block against query tokens using TF-IDF cosine-like scoring."""
    doc_tokens = _tokenize(text)
    if not doc_tokens or not query_tokens:
        return 0.0
    tf = _term_freq(doc_tokens)
    score = 0.0
    for qt in query_tokens:
        score += tf.get(qt, 0.0) * idf_map.get(qt, 1.0)
    return score


# ---------------------------------------------------------------------------
# Text chunking
# ---------------------------------------------------------------------------


def chunk_text(text: str, max_chars: int = 1500, overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks at sentence boundaries."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current = ""
    for sent in sentences:
        if len(current) + len(sent) > max_chars and current:
            chunks.append(current.strip())
            # Keep overlap from end of previous chunk
            current = current[-overlap:] + " " + sent if overlap else sent
        else:
            current = (current + " " + sent).strip()
    if current.strip():
        chunks.append(current.strip())
    return chunks if chunks else [text[:max_chars]]


# ---------------------------------------------------------------------------
# Local wiki retrieval
# ---------------------------------------------------------------------------


def _parse_frontmatter(content: str) -> tuple[Optional[dict], str]:
    """Parse YAML frontmatter from markdown content."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
    if not match:
        return None, content
    try:
        fm = yaml.safe_load(match.group(1))
        return fm, match.group(2)
    except yaml.YAMLError:
        return None, content


def _strip_hugo(body: str) -> str:
    """Remove Hugo shortcodes and image markdown."""
    body = re.sub(r"\{\{<.*?>}}", "", body)
    body = re.sub(r"!\[.*?\]\(.*?\)", "", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip()


def load_wiki_articles(exchange: str, repo_root: str = ".") -> list[dict]:
    """
    Search local wiki articles for content relevant to the given exchange.

    Returns a list of dicts with 'title', 'content', and 'source' keys.
    """
    posts_dir = os.path.join(repo_root, WIKI_POSTS_DIR)
    if not os.path.isdir(posts_dir):
        logger.warning(f"Wiki posts directory not found: {posts_dir}")
        return []

    exchange_norm = exchange.lower().replace(".", "").replace("-", "").replace(" ", "")
    articles = []

    for entry in sorted(os.listdir(posts_dir)):
        entry_path = os.path.join(posts_dir, entry)
        if not os.path.isdir(entry_path):
            continue
        index_file = os.path.join(entry_path, "index.md")
        if not os.path.isfile(index_file):
            continue

        with open(index_file, "r", encoding="utf-8") as f:
            content = f.read()

        fm, body = _parse_frontmatter(content)
        if not fm:
            continue

        entities = fm.get("entities", [])
        dir_norm = entry.lower().replace(".", "").replace("-", "").replace(" ", "")

        entity_match = any(
            exchange_norm in str(e).lower().replace(".", "").replace("-", "").replace(" ", "")
            or str(e).lower().replace(".", "").replace("-", "").replace(" ", "") in exchange_norm
            for e in entities
        )

        if entity_match or exchange_norm in dir_norm:
            cleaned = _strip_hugo(body)
            articles.append({
                "title": fm.get("title", entry),
                "content": cleaned,
                "source": f"wiki:{entry}",
            })

    logger.info(f"Found {len(articles)} local wiki article(s) for '{exchange}'")
    return articles


# ---------------------------------------------------------------------------
# Web search via DuckDuckGo
# ---------------------------------------------------------------------------


def _duckduckgo_search(query: str, max_results: int = 5) -> list[dict]:
    """Search DuckDuckGo. Returns list of dicts with title, snippet, url."""
    results = []
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                title = clean_text(r.get("title", ""))
                snippet = clean_text(r.get("body", ""))
                url = r.get("href", r.get("link", ""))
                if title and snippet:
                    results.append({"title": title, "snippet": snippet, "url": url})
    except ImportError:
        logger.warning("duckduckgo-search not available, skipping web search")
    except Exception as e:
        logger.warning(f"DuckDuckGo search failed: {e}")
    return results


def search_web(exchange: str, pair: str, start: str = "", end: str = "") -> list[dict]:
    """
    Run targeted web searches for the exchange and pair.

    Returns deduplicated list of dicts with 'title', 'snippet', 'url'.
    """
    base_token = pair.split("-")[0].upper() if "-" in pair else pair.upper()
    queries = [
        f"{exchange} {base_token} wash trading manipulation",
        f"{exchange} cryptocurrency trading volume anomaly",
        f"{exchange} exchange regulatory news",
    ]

    seen_urls: set[str] = set()
    results = []
    for q in queries:
        for item in _duckduckgo_search(q, max_results=3):
            if item["url"] not in seen_urls:
                seen_urls.add(item["url"])
                results.append(item)
    return results


# ---------------------------------------------------------------------------
# Full article extraction from URLs
# ---------------------------------------------------------------------------


def fetch_article_text(url: str, timeout: int = 10, max_chars: int = 5000) -> Optional[str]:
    """
    Fetch a URL and extract the main article text.

    Returns cleaned text or None on failure.
    """
    try:
        resp = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0 (compatible; MarketHealthReporter/1.0)"},
        )
        resp.raise_for_status()
    except Exception as e:
        logger.debug(f"Failed to fetch {url}: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove noise elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()

    # Try <article> first, then <main>, then <body>
    main = soup.find("article") or soup.find("main") or soup.find("body")
    if not main:
        return None

    text = main.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) < 100:
        return None

    return text[:max_chars]


# ---------------------------------------------------------------------------
# Build RAG context
# ---------------------------------------------------------------------------


def build_rag_context(
    exchange: str,
    pair: str,
    start: str = "",
    end: str = "",
    repo_root: str = ".",
    include_web_search: bool = True,
    fetch_full_articles: bool = True,
    max_context_chars: int = 8000,
) -> str:
    """
    Build a ranked RAG context string for injection into the LLM prompt.

    Retrieves content from local wiki and web search, scores chunks by
    relevance using TF-IDF, and returns the top-ranked content formatted
    for prompt injection.

    Args:
        exchange: Exchange name (e.g., "huobi").
        pair: Trading pair (e.g., "btc-usdt").
        start: Analysis period start date.
        end: Analysis period end date.
        repo_root: Path to the repository root.
        include_web_search: Whether to include web search results.
        fetch_full_articles: Whether to fetch full article text from URLs.
        max_context_chars: Maximum characters for the context block.

    Returns:
        Formatted context string, or empty string if nothing found.
    """
    base_token = pair.split("-")[0] if "-" in pair else pair
    query_tokens = _tokenize(f"{exchange} {base_token} wash trading manipulation volume anomaly")

    # Collect all text chunks with their sources
    all_chunks: list[dict] = []  # {"text": ..., "source": ..., "title": ...}

    # 1. Local wiki articles (highest quality)
    wiki_articles = load_wiki_articles(exchange, repo_root)
    for article in wiki_articles:
        chunks = chunk_text(article["content"], max_chars=1500)
        for chunk in chunks:
            all_chunks.append({
                "text": chunk,
                "source": article["source"],
                "title": article["title"],
                "origin": "wiki",
            })

    # 2. Web search
    web_results = []
    if include_web_search:
        web_results = search_web(exchange, pair, start, end)
        for item in web_results:
            all_chunks.append({
                "text": item["snippet"],
                "source": item["url"],
                "title": item["title"],
                "origin": "web_snippet",
            })

    # 3. Full article extraction from top web results
    if fetch_full_articles and web_results:
        for item in web_results[:5]:
            article_text = fetch_article_text(item["url"])
            if article_text:
                chunks = chunk_text(article_text, max_chars=1500)
                for chunk in chunks:
                    all_chunks.append({
                        "text": chunk,
                        "source": item["url"],
                        "title": item["title"],
                        "origin": "web_article",
                    })

    if not all_chunks:
        logger.warning("No relevant context found from any source.")
        return ""

    # Score and rank all chunks
    all_doc_tokens = [_tokenize(c["text"]) for c in all_chunks]
    idf_map = _idf(all_doc_tokens)

    for chunk in all_chunks:
        base_score = score_relevance(query_tokens, chunk["text"], idf_map)
        # Boost wiki content (curated, high quality)
        if chunk["origin"] == "wiki":
            base_score *= 1.5
        # Boost full articles over snippets
        elif chunk["origin"] == "web_article":
            base_score *= 1.2
        chunk["score"] = base_score

    # Sort by score descending, deduplicate similar content
    all_chunks.sort(key=lambda c: c["score"], reverse=True)

    # Select top chunks within budget
    selected: list[dict] = []
    char_count = 0
    seen_texts: set[str] = set()

    for chunk in all_chunks:
        # Simple dedup: skip if first 100 chars match something already selected
        sig = chunk["text"][:100]
        if sig in seen_texts:
            continue
        if char_count + len(chunk["text"]) > max_context_chars:
            continue
        seen_texts.add(sig)
        selected.append(chunk)
        char_count += len(chunk["text"])

    if not selected:
        return ""

    # Format output
    sections = []
    for chunk in selected:
        section = f"### {chunk['title']}\nSource: {chunk['source']}\n\n{chunk['text']}"
        sections.append(section)

    context_body = "\n\n---\n\n".join(sections)

    return (
        f"<external_context>\n"
        f"The following is additional context about {exchange} retrieved from wiki articles "
        f"and recent web sources. Reference specific events or findings from this context "
        f"only where they help explain anomalies detected in the market data. "
        f"Do not fabricate information beyond what is provided.\n\n"
        f"{context_body}\n"
        f"</external_context>"
    )
