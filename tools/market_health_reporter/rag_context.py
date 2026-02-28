"""
🌰 RAG Context Retrieval for Market Health Reporter 🌰

Retrieves real-time external context from multiple sources to augment
the Market Health Reporter's LLM prompts with up-to-date information.

Sources:
  1. DuckDuckGo web search — real-time news and analysis 🌰
  2. CryptoPanic public API — aggregated crypto news feed 🌰
  3. Local wiki articles — existing DN Institute research 🌰

Pipeline:
  fetch → extract clean text → chunk → TF-IDF rank → budget-aware select 🌰

No new API keys required. Uses only existing pyproject.toml dependencies. 🌰
"""

from __future__ import annotations

import math
import os
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import bleach
import requests
import yaml
from bs4 import BeautifulSoup

# 🌰 DuckDuckGo search import with graceful fallback
try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None  # type: ignore[assignment, misc]


# ---------------------------------------------------------------------------
# 🌰 Data structures
# ---------------------------------------------------------------------------

@dataclass
class ContextChunk:
    """A single chunk of retrieved context. 🌰"""

    text: str
    source: str  # "duckduckgo" | "cryptopanic" | "wiki"
    title: str = ""
    url: str = ""
    relevance_score: float = 0.0


@dataclass
class RAGResult:
    """Assembled RAG context ready for prompt injection. 🌰"""

    context_text: str
    chunks_used: int
    sources_queried: List[str] = field(default_factory=list)
    total_chars: int = 0


# ---------------------------------------------------------------------------
# 🌰 Text cleaning utilities
# ---------------------------------------------------------------------------

def clean_html(raw_html: str) -> str:
    """Strip HTML tags and normalize whitespace. 🌰

    Uses BeautifulSoup for robust parsing and bleach for sanitization,
    ensuring no raw HTML leaks into LLM prompts (addresses PR #480 feedback).
    """
    if not raw_html:
        return ""
    # First pass: BeautifulSoup extracts text from HTML structure
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    # Second pass: bleach strips any residual tags
    text = bleach.clean(text, tags=[], strip=True)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def strip_markdown_artifacts(text: str) -> str:
    """Remove markdown formatting artifacts from wiki content. 🌰"""
    if not text:
        return ""
    # Remove Hugo shortcodes like {{< figure ... >}}
    text = re.sub(r"\{\{<[^>]*>\}\}", "", text)
    # Remove image references ![alt](url)
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", "", text)
    # Remove link syntax but keep text [text](url) → text
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    # Remove heading markers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ---------------------------------------------------------------------------
# 🌰 TF-IDF relevance scoring
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> List[str]:
    """Simple whitespace + lowercase tokenizer. 🌰"""
    return re.findall(r"[a-z0-9]+", text.lower())


def compute_tfidf_scores(
    query_tokens: List[str],
    documents: List[str],
) -> List[float]:
    """Compute TF-IDF relevance scores for documents against a query. 🌰

    Uses term frequency / inverse document frequency to rank chunks
    by relevance rather than simply concatenating them.

    Args:
        query_tokens: Tokenized search query terms.
        documents: List of document text strings to score.

    Returns:
        List of float scores (one per document), higher = more relevant.
    """
    if not documents or not query_tokens:
        return [0.0] * len(documents)

    num_docs = len(documents)
    # Pre-tokenize all documents
    doc_token_lists = [_tokenize(doc) for doc in documents]

    # Document frequency for each query term
    doc_freq: Counter = Counter()
    for tokens in doc_token_lists:
        token_set = set(tokens)
        for qt in query_tokens:
            if qt in token_set:
                doc_freq[qt] += 1

    scores: List[float] = []
    for tokens in doc_token_lists:
        if not tokens:
            scores.append(0.0)
            continue
        token_counter = Counter(tokens)
        doc_len = len(tokens)
        score = 0.0
        for qt in query_tokens:
            tf = token_counter.get(qt, 0) / doc_len
            df = doc_freq.get(qt, 0)
            idf = math.log((num_docs + 1) / (df + 1)) + 1
            score += tf * idf
        scores.append(score)

    return scores


def rank_chunks(
    chunks: List[ContextChunk],
    exchange: str,
    pair: str,
) -> List[ContextChunk]:
    """Rank context chunks by TF-IDF relevance. 🌰

    Args:
        chunks: Unranked context chunks.
        exchange: Exchange name (e.g. "binance").
        pair: Trading pair (e.g. "btc-usdt").

    Returns:
        Chunks sorted by relevance score (highest first).
    """
    if not chunks:
        return []

    # Build query from exchange + pair + domain terms 🌰
    query_terms = f"{exchange} {pair} cryptocurrency trading volume manipulation wash"
    query_tokens = _tokenize(query_terms)

    documents = [chunk.text for chunk in chunks]
    scores = compute_tfidf_scores(query_tokens, documents)

    for chunk, score in zip(chunks, scores):
        chunk.relevance_score = score

    return sorted(chunks, key=lambda c: c.relevance_score, reverse=True)


# ---------------------------------------------------------------------------
# 🌰 Source: DuckDuckGo web search
# ---------------------------------------------------------------------------

def _build_search_queries(exchange: str, pair: str) -> List[str]:
    """Generate diverse search queries for comprehensive coverage. 🌰"""
    return [
        f"{exchange} cryptocurrency wash trading manipulation",
        f"{exchange} {pair} trading volume anomaly",
        f"{exchange} crypto exchange market surveillance report",
    ]


def search_duckduckgo(
    exchange: str,
    pair: str,
    max_results_per_query: int = 5,
) -> List[ContextChunk]:
    """Search DuckDuckGo for real-time exchange information. 🌰

    Uses the duckduckgo-search package (already in pyproject.toml deps).
    Returns cleaned text chunks with source metadata.
    """
    if DDGS is None:
        return []

    chunks: List[ContextChunk] = []
    seen_urls: set = set()
    queries = _build_search_queries(exchange, pair)

    for query in queries:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results_per_query))
            for result in results:
                url = result.get("href", "")
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                title = clean_html(result.get("title", ""))
                body = clean_html(result.get("body", ""))
                if not body:
                    continue

                chunks.append(ContextChunk(
                    text=body,
                    source="duckduckgo",
                    title=title,
                    url=url,
                ))
        except Exception:
            # 🌰 Graceful degradation: skip failed queries
            continue

    return chunks


# ---------------------------------------------------------------------------
# 🌰 Source: CryptoPanic public API
# ---------------------------------------------------------------------------

CRYPTOPANIC_PUBLIC_URL = "https://cryptopanic.com/api/free/v1/posts/"


def search_cryptopanic(
    exchange: str,
    pair: str,
    max_results: int = 10,
) -> List[ContextChunk]:
    """Fetch news from CryptoPanic public API. 🌰

    CryptoPanic's free/public endpoint requires no API key and returns
    aggregated crypto news. We filter by exchange and pair relevance.
    """
    chunks: List[ContextChunk] = []

    # 🌰 Build search filter from pair base currency
    base_currency = pair.split("-")[0].upper() if "-" in pair else pair.upper()

    params = {
        "auth_token": "free",
        "currencies": base_currency,
        "filter": "important",
        "public": "true",
    }

    try:
        resp = requests.get(
            CRYPTOPANIC_PUBLIC_URL,
            params=params,
            timeout=10,
            headers={"User-Agent": "DN-Institute-MHR/1.0"},
        )
        if resp.status_code != 200:
            return []

        data = resp.json()
        results = data.get("results", [])[:max_results]

        for item in results:
            title = clean_html(item.get("title", ""))
            # CryptoPanic items have title + optional body
            body = clean_html(item.get("body", "") or title)
            url = item.get("url", "")

            if not body:
                continue

            chunks.append(ContextChunk(
                text=f"{title}. {body}" if title != body else body,
                source="cryptopanic",
                title=title,
                url=url,
            ))
    except Exception:
        # 🌰 Graceful degradation: CryptoPanic is a secondary source
        pass

    return chunks


# ---------------------------------------------------------------------------
# 🌰 Source: Local wiki articles
# ---------------------------------------------------------------------------

def _parse_frontmatter(content: str) -> Tuple[dict, str]:
    """Parse YAML frontmatter from markdown content. 🌰

    Args:
        content: Raw markdown string with optional YAML frontmatter.

    Returns:
        Tuple of (frontmatter dict, body text).
    """
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    try:
        metadata = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        metadata = {}

    body = parts[2].strip()
    return metadata, body


def _normalize_name(name: str) -> str:
    """Normalize an exchange/entity name for comparison. 🌰"""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def load_wiki_articles(
    exchange: str,
    repo_root: str,
    max_chars_per_article: int = 2000,
) -> List[ContextChunk]:
    """Load relevant articles from the local DN Institute wiki. 🌰

    Scans content/market-health/posts/ for articles matching the
    exchange being analyzed.

    Args:
        exchange: Exchange name to match against.
        repo_root: Path to the repository root.
        max_chars_per_article: Maximum characters to extract per article.

    Returns:
        List of context chunks from matching wiki articles.
    """
    posts_dir = os.path.join(repo_root, "content", "market-health", "posts")
    if not os.path.isdir(posts_dir):
        # Try alternate path 🌰
        posts_dir = os.path.join(
            repo_root, "content", "research", "market-health", "posts"
        )
    if not os.path.isdir(posts_dir):
        return []

    normalized_exchange = _normalize_name(exchange)
    chunks: List[ContextChunk] = []

    for entry in os.listdir(posts_dir):
        entry_path = os.path.join(posts_dir, entry)
        if not os.path.isdir(entry_path):
            continue

        # Check directory name for exchange match 🌰
        dir_match = _normalize_name(entry).find(normalized_exchange) >= 0

        index_file = os.path.join(entry_path, "index.md")
        if not os.path.isfile(index_file):
            continue

        try:
            with open(index_file, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            continue

        metadata, body = _parse_frontmatter(content)

        # Check entities in frontmatter for exchange match 🌰
        entities_str = str(metadata.get("entities", ""))
        entity_match = _normalize_name(entities_str).find(normalized_exchange) >= 0

        title_str = str(metadata.get("title", ""))
        title_match = _normalize_name(title_str).find(normalized_exchange) >= 0

        if not (dir_match or entity_match or title_match):
            continue

        # Clean and trim the article body 🌰
        cleaned = strip_markdown_artifacts(body)
        if len(cleaned) > max_chars_per_article:
            cleaned = cleaned[:max_chars_per_article] + "..."

        if cleaned:
            chunks.append(ContextChunk(
                text=cleaned,
                source="wiki",
                title=title_str or entry,
                url=f"posts/{entry}/index.md",
            ))

    return chunks


# ---------------------------------------------------------------------------
# 🌰 Token budget management
# ---------------------------------------------------------------------------

def estimate_tokens(text: str) -> int:
    """Estimate token count from character count. 🌰

    Uses the ~4 chars/token heuristic for English text.
    Avoids importing tiktoken for a lightweight estimate.
    """
    return max(1, len(text) // 4)


def select_within_budget(
    chunks: List[ContextChunk],
    max_tokens: int = 4000,
) -> List[ContextChunk]:
    """Select top-ranked chunks that fit within the token budget. 🌰

    Assumes chunks are already sorted by relevance (highest first).
    Greedily selects chunks until budget is exhausted.

    Args:
        chunks: Ranked context chunks.
        max_tokens: Maximum token budget for RAG context.

    Returns:
        Subset of chunks fitting within budget.
    """
    selected: List[ContextChunk] = []
    used_tokens = 0

    for chunk in chunks:
        chunk_tokens = estimate_tokens(chunk.text)
        if used_tokens + chunk_tokens > max_tokens:
            # 🌰 Try truncating the chunk to fit remaining budget
            remaining = max_tokens - used_tokens
            if remaining >= 50:  # Only include if meaningful (50+ tokens)
                truncated_chars = remaining * 4
                truncated = ContextChunk(
                    text=chunk.text[:truncated_chars] + "...",
                    source=chunk.source,
                    title=chunk.title,
                    url=chunk.url,
                    relevance_score=chunk.relevance_score,
                )
                selected.append(truncated)
            break
        selected.append(chunk)
        used_tokens += chunk_tokens

    return selected


# ---------------------------------------------------------------------------
# 🌰 Context assembly
# ---------------------------------------------------------------------------

def format_context(chunks: List[ContextChunk]) -> str:
    """Format selected chunks into an XML-tagged context block. 🌰

    The formatted context is designed to be injected directly into the
    Market Health Reporter prompt.
    """
    if not chunks:
        return ""

    lines: List[str] = [
        "<external_context>",
        "<!-- 🌰 RAG-retrieved context from multiple sources 🌰 -->",
    ]

    for i, chunk in enumerate(chunks, 1):
        source_label = {
            "duckduckgo": "Web Search",
            "cryptopanic": "CryptoPanic News",
            "wiki": "DN Institute Wiki",
        }.get(chunk.source, chunk.source)

        lines.append(f"<source_{i} type=\"{source_label}\" title=\"{chunk.title}\">")
        lines.append(chunk.text)
        lines.append(f"</source_{i}>")

    lines.append("</external_context>")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 🌰 Main pipeline
# ---------------------------------------------------------------------------

def build_rag_context(
    exchange: str,
    pair: str,
    repo_root: Optional[str] = None,
    max_context_tokens: int = 4000,
    disable_web_search: bool = False,
    disable_cryptopanic: bool = False,
) -> RAGResult:
    """Build RAG context for Market Health Reporter prompts. 🌰

    Full pipeline: fetch from sources → clean text → TF-IDF rank →
    budget-aware selection → formatted context string.

    This addresses PR #480 feedback by:
    - Using real-time web search (not static knowledge base) 🌰
    - Clean text extraction with no raw HTML in prompts 🌰
    - Multiple diverse sources for comprehensive coverage 🌰

    Args:
        exchange: Exchange name (e.g. "binance", "huobi").
        pair: Trading pair (e.g. "btc-usdt").
        repo_root: Path to repo root for wiki article loading.
        max_context_tokens: Token budget for the RAG context block.
        disable_web_search: Skip DuckDuckGo search (for testing). 🌰
        disable_cryptopanic: Skip CryptoPanic API (for testing). 🌰

    Returns:
        RAGResult with formatted context and metadata.
    """
    all_chunks: List[ContextChunk] = []
    sources_queried: List[str] = []

    # 🌰 Source 1: DuckDuckGo real-time web search
    if not disable_web_search:
        ddg_chunks = search_duckduckgo(exchange, pair)
        all_chunks.extend(ddg_chunks)
        sources_queried.append("duckduckgo")

    # 🌰 Source 2: CryptoPanic news aggregation
    if not disable_cryptopanic:
        cp_chunks = search_cryptopanic(exchange, pair)
        all_chunks.extend(cp_chunks)
        sources_queried.append("cryptopanic")

    # 🌰 Source 3: Local wiki articles
    if repo_root:
        wiki_chunks = load_wiki_articles(exchange, repo_root)
        all_chunks.extend(wiki_chunks)
        sources_queried.append("wiki")

    if not all_chunks:
        return RAGResult(
            context_text="",
            chunks_used=0,
            sources_queried=sources_queried,
            total_chars=0,
        )

    # 🌰 TF-IDF relevance ranking
    ranked_chunks = rank_chunks(all_chunks, exchange, pair)

    # 🌰 Budget-aware selection
    selected_chunks = select_within_budget(ranked_chunks, max_context_tokens)

    # 🌰 Format into prompt-ready context
    context_text = format_context(selected_chunks)

    return RAGResult(
        context_text=context_text,
        chunks_used=len(selected_chunks),
        sources_queried=sources_queried,
        total_chars=len(context_text),
    )
