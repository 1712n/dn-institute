"""
RAG (Retrieval-Augmented Generation) context retrieval for Market Health Reporter.

Fetches relevant external context from web search results and local wiki articles
to augment the LLM prompt with up-to-date information about exchange-specific events,
regulatory actions, and known manipulation patterns.

Architecture:
    1. Build targeted search queries from exchange/pair/date parameters
    2. Retrieve real-time web results via DuckDuckGo (zero-config, no API key)
    3. Retrieve complementary context from local wiki articles
    4. Clean and sanitize all HTML content (bs4 + bleach)
    5. Rank results by TF-IDF relevance to the analysis context
    6. Format ranked context for prompt injection
"""

import logging
import math
import os
import re
from collections import Counter
from typing import Optional

import bleach
import requests
import yaml
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

# Maximum characters of context to inject into the prompt
DEFAULT_MAX_CONTEXT_CHARS = 12000

# Maximum number of web search results to fetch per query
MAX_RESULTS_PER_QUERY = 8

# Maximum characters to keep from a single source
MAX_CHARS_PER_SOURCE = 2000

# Local wiki articles directory (relative to repo root)
WIKI_POSTS_DIR = "content/research/market-health/posts/"


def clean_html(raw_html: str) -> str:
    """
    Extract clean text from HTML content using BeautifulSoup and bleach.

    Follows the same pattern as tools/article_checker/claude_retriever/utils.py
    to ensure consistent text cleaning across the codebase.
    """
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    # Remove script and style elements
    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()
    text = soup.get_text(strip=True, separator="\n")
    # Sanitize with bleach - strip all HTML tags
    sanitized = bleach.clean(text, tags=[], attributes={}, strip=True)
    # Normalize whitespace
    sanitized = re.sub(r"\n{3,}", "\n\n", sanitized)
    sanitized = re.sub(r" {2,}", " ", sanitized)
    return sanitized.strip()


def strip_hugo_shortcodes(text: str) -> str:
    """Remove Hugo shortcodes like {{< figure ... >}} from markdown text."""
    return re.sub(r"\{\{<.*?>}}", "", text)


def _tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer for TF-IDF."""
    return re.findall(r"[a-z0-9]+", text.lower())


def compute_tfidf_similarity(query_text: str, documents: list[str]) -> list[float]:
    """
    Compute TF-IDF cosine similarity between a query and a list of documents.

    Uses a lightweight in-memory implementation with no external dependencies
    beyond the standard library.

    Returns a list of similarity scores (0.0 to 1.0) for each document.
    """
    if not documents:
        return []

    query_tokens = _tokenize(query_text)
    doc_token_lists = [_tokenize(doc) for doc in documents]
    all_docs = [query_tokens] + doc_token_lists
    n_docs = len(all_docs)

    # Document frequency
    df = Counter()
    for tokens in all_docs:
        unique = set(tokens)
        for t in unique:
            df[t] += 1

    def tfidf_vector(tokens: list[str]) -> dict[str, float]:
        tf = Counter(tokens)
        vec = {}
        for term, count in tf.items():
            idf = math.log(n_docs / (df[term] + 1)) + 1
            vec[term] = (count / max(len(tokens), 1)) * idf
        return vec

    def cosine_sim(v1: dict[str, float], v2: dict[str, float]) -> float:
        common = set(v1.keys()) & set(v2.keys())
        if not common:
            return 0.0
        dot = sum(v1[k] * v2[k] for k in common)
        mag1 = math.sqrt(sum(v ** 2 for v in v1.values()))
        mag2 = math.sqrt(sum(v ** 2 for v in v2.values()))
        if mag1 == 0 or mag2 == 0:
            return 0.0
        return dot / (mag1 * mag2)

    query_vec = tfidf_vector(query_tokens)
    scores = []
    for doc_tokens in doc_token_lists:
        doc_vec = tfidf_vector(doc_tokens)
        scores.append(cosine_sim(query_vec, doc_vec))
    return scores


def build_search_queries(
    marketvenueid: str, pairid: str, start: str, end: str
) -> list[str]:
    """
    Build targeted search queries for the exchange and trading pair.

    Generates multiple queries covering different aspects:
    - Recent news about the exchange and token
    - Wash trading and manipulation reports
    - Regulatory actions and investigations
    """
    exchange = marketvenueid.replace("-", " ").title()
    pair = pairid.upper().replace("-", "/")
    base_token = pair.split("/")[0] if "/" in pair else pair

    queries = [
        f"{exchange} {base_token} cryptocurrency news {start} {end}",
        f"{exchange} exchange wash trading manipulation investigation",
        f"{exchange} crypto exchange regulatory action volume anomaly",
    ]
    return queries


def fetch_web_results(queries: list[str]) -> list[dict]:
    """
    Fetch search results from DuckDuckGo for the given queries.

    Uses the duckduckgo-search library which is already a project dependency
    (listed in pyproject.toml). Requires no API key.

    Returns deduplicated results as list of dicts with keys:
        - title: str
        - url: str
        - snippet: str
    """
    seen_urls = set()
    results = []

    for query in queries:
        try:
            raw_results = DDGS().text(query, max_results=MAX_RESULTS_PER_QUERY)
            if not raw_results:
                continue
            for item in raw_results:
                url = item.get("href", "")
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": url,
                        "snippet": clean_html(item.get("body", "")),
                    }
                )
        except Exception as e:
            logger.warning(f"Web search failed for query '{query}': {e}")
            continue

    return results


def fetch_url_content(url: str, timeout: int = 10) -> Optional[str]:
    """
    Fetch and clean the text content of a URL.

    Returns cleaned text content or None if the request fails.
    """
    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0 (compatible; MarketHealthReporter)"},
        )
        response.raise_for_status()
        cleaned = clean_html(response.text)
        return cleaned[:MAX_CHARS_PER_SOURCE] if cleaned else None
    except Exception as e:
        logger.warning(f"Failed to fetch URL {url}: {e}")
        return None


def load_local_wiki_articles(marketvenueid: str) -> list[dict]:
    """
    Search local wiki articles for content related to the given exchange.

    Looks through the repository's content/research/market-health/posts/
    directory for markdown files whose frontmatter entities match the
    exchange being analyzed.

    Returns list of dicts with keys:
        - title: str
        - content: str (cleaned markdown text)
        - source: str (file path)
    """
    articles = []

    if not os.path.isdir(WIKI_POSTS_DIR):
        logger.info(f"Wiki posts directory not found: {WIKI_POSTS_DIR}")
        return articles

    exchange_name = marketvenueid.replace("-", " ").lower()

    for direntry in os.scandir(WIKI_POSTS_DIR):
        if not direntry.is_dir():
            continue
        index_path = os.path.join(direntry.path, "index.md")
        if not os.path.isfile(index_path):
            continue

        try:
            with open(index_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse YAML frontmatter
            frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if not frontmatter_match:
                continue

            frontmatter = yaml.safe_load(frontmatter_match.group(1))
            entities = frontmatter.get("entities", [])
            title = frontmatter.get("title", "")

            # Check if any entity matches the exchange
            entity_match = any(
                exchange_name in str(e).lower() for e in entities
            )
            title_match = exchange_name in title.lower()

            if entity_match or title_match:
                body = content[frontmatter_match.end():]
                body = strip_hugo_shortcodes(body)
                body = re.sub(r"\n{3,}", "\n\n", body)
                # Trim to summary + first few sections
                body = body[:MAX_CHARS_PER_SOURCE]

                articles.append(
                    {
                        "title": title,
                        "content": body.strip(),
                        "source": index_path,
                    }
                )
        except Exception as e:
            logger.warning(f"Error reading wiki article {index_path}: {e}")
            continue

    return articles


def retrieve_rag_context(
    marketvenueid: str,
    pairid: str,
    start: str,
    end: str,
    max_context_chars: int = DEFAULT_MAX_CONTEXT_CHARS,
    enable_web_search: bool = True,
) -> str:
    """
    Retrieve and format RAG context for the Market Health Reporter.

    This is the main entry point for the RAG module. It:
    1. Builds search queries from the analysis parameters
    2. Fetches web search results via DuckDuckGo (if enabled)
    3. Loads matching local wiki articles
    4. Ranks all sources by TF-IDF relevance
    5. Formats the top results into a structured context string

    Args:
        marketvenueid: Exchange identifier (e.g., "huobi")
        pairid: Trading pair (e.g., "ht-usdt")
        start: Analysis start date
        end: Analysis end date
        max_context_chars: Maximum characters of context to return
        enable_web_search: Whether to include web search results

    Returns:
        Formatted context string ready for prompt injection, or empty string
        if no relevant context was found.
    """
    # Build the relevance query for TF-IDF ranking
    exchange = marketvenueid.replace("-", " ")
    pair = pairid.replace("-", "/")
    relevance_query = (
        f"{exchange} {pair} cryptocurrency market manipulation wash trading "
        f"volume anomaly trading activity {start} {end}"
    )

    all_sources = []

    # 1. Fetch web search results
    if enable_web_search:
        queries = build_search_queries(marketvenueid, pairid, start, end)
        web_results = fetch_web_results(queries)

        for result in web_results:
            # Try to get fuller content from the URL
            full_content = fetch_url_content(result["url"])
            text = full_content if full_content else result["snippet"]
            if text:
                all_sources.append(
                    {
                        "type": "web",
                        "title": result["title"],
                        "url": result["url"],
                        "text": text,
                    }
                )

    # 2. Load local wiki articles
    wiki_articles = load_local_wiki_articles(marketvenueid)
    for article in wiki_articles:
        all_sources.append(
            {
                "type": "wiki",
                "title": article["title"],
                "url": article["source"],
                "text": article["content"],
            }
        )

    if not all_sources:
        logger.info("No RAG context sources found")
        return ""

    # 3. Rank by TF-IDF relevance
    documents = [s["text"] for s in all_sources]
    scores = compute_tfidf_similarity(relevance_query, documents)

    # Attach scores and sort by relevance (highest first)
    for source, score in zip(all_sources, scores):
        source["relevance"] = score

    all_sources.sort(key=lambda x: x["relevance"], reverse=True)

    # 4. Format context within the character budget
    context_parts = []
    total_chars = 0

    for source in all_sources:
        source_type = source["type"].upper()
        title = source["title"]
        text = source["text"]

        # Trim individual source text
        remaining_budget = max_context_chars - total_chars
        if remaining_budget <= 200:
            break

        if len(text) > remaining_budget - 100:
            text = text[: remaining_budget - 100] + "..."

        entry = (
            f'<source type="{source_type}" title="{title}">\n'
            f"{text}\n"
            f"</source>"
        )
        context_parts.append(entry)
        total_chars += len(entry)

    if not context_parts:
        return ""

    formatted_context = "\n\n".join(context_parts)
    return formatted_context
