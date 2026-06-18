"""
RAG (Retrieval Augmented Generation) context retriever for Market Health Reporter.

Retrieves relevant context from:
  1. Local knowledge base (existing market-health articles and documentation)
  2. Web search results via DuckDuckGo (already a project dependency)

Uses lightweight TF-IDF vectorization with cosine similarity for local
document retrieval — no external vector database or embedding API required.
"""

import os
import re
import math
import glob
import logging
from collections import Counter
from dataclasses import dataclass, field
from typing import Optional

import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)

# Paths relative to the repository root
MARKET_HEALTH_POSTS_DIR = "content/research/market-health/posts"
MARKET_HEALTH_DOCS_DIR = "content/research/market-health/docs"

# RAG configuration
MAX_LOCAL_RESULTS = 3
MAX_WEB_RESULTS = 5
MAX_CONTEXT_CHARS = 12000
WEB_SEARCH_TIMEOUT = 10
CHUNK_SIZE = 500  # approximate words per chunk
CHUNK_OVERLAP = 50  # word overlap between chunks


@dataclass
class Document:
    """A document chunk with its source metadata."""
    text: str
    source: str
    title: str = ""
    score: float = 0.0


@dataclass
class RAGContext:
    """Container for retrieved context from all sources."""
    local_docs: list = field(default_factory=list)
    web_results: list = field(default_factory=list)

    def format_context(self) -> str:
        """Format retrieved context as a string suitable for LLM prompt injection."""
        parts = []

        if self.local_docs:
            parts.append("=== Relevant articles from the knowledge base ===")
            for doc in self.local_docs:
                header = f"[Source: {doc.source}]"
                if doc.title:
                    header += f" Title: {doc.title}"
                parts.append(f"{header}\n{doc.text}\n")

        if self.web_results:
            parts.append("=== Relevant web search results ===")
            for doc in self.web_results:
                header = f"[Source: {doc.source}]"
                if doc.title:
                    header += f" Title: {doc.title}"
                parts.append(f"{header}\n{doc.text}\n")

        context = "\n".join(parts)

        # Truncate if exceeding max context size
        if len(context) > MAX_CONTEXT_CHARS:
            context = context[:MAX_CONTEXT_CHARS] + "\n[... context truncated ...]"

        return context

    def is_empty(self) -> bool:
        return len(self.local_docs) == 0 and len(self.web_results) == 0


# ---------------------------------------------------------------------------
# Text processing utilities
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list:
    """Simple word-level tokenizer with lowercasing and stopword removal."""
    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "to", "of", "in", "for",
        "on", "with", "at", "by", "from", "as", "into", "through", "during",
        "before", "after", "and", "but", "or", "nor", "not", "so", "yet",
        "both", "either", "neither", "each", "every", "all", "any", "few",
        "more", "most", "other", "some", "such", "no", "only", "own", "same",
        "than", "too", "very", "just", "because", "about", "between", "this",
        "that", "these", "those", "it", "its", "they", "them", "their", "we",
        "our", "you", "your", "he", "she", "his", "her", "which", "what",
        "who", "whom", "how", "when", "where", "why", "if", "then", "else",
    }
    words = re.findall(r'[a-z0-9]+', text.lower())
    return [w for w in words if w not in stopwords and len(w) > 1]


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE,
                overlap: int = CHUNK_OVERLAP) -> list:
    """Split text into overlapping word-level chunks."""
    words = text.split()
    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap
    return chunks


# ---------------------------------------------------------------------------
# TF-IDF based local retrieval
# ---------------------------------------------------------------------------

class TFIDFRetriever:
    """
    Lightweight TF-IDF retriever with cosine similarity.
    No external dependencies beyond the standard library.
    """

    def __init__(self):
        self.documents: list = []
        self.doc_vectors: list = []
        self.idf: dict = {}
        self.vocab: set = set()
        self._built = False

    def add_documents(self, documents: list):
        """Add Document objects to the index."""
        self.documents.extend(documents)
        self._built = False

    def build_index(self):
        """Compute IDF values and TF-IDF vectors for all documents."""
        if not self.documents:
            return

        n = len(self.documents)
        doc_freq = Counter()
        tokenized_docs = []

        for doc in self.documents:
            tokens = _tokenize(doc.text)
            tokenized_docs.append(tokens)
            unique_tokens = set(tokens)
            for token in unique_tokens:
                doc_freq[token] += 1
            self.vocab.update(unique_tokens)

        # IDF: log(N / df) with smoothing
        self.idf = {
            term: math.log((n + 1) / (df + 1)) + 1
            for term, df in doc_freq.items()
        }

        # TF-IDF vectors (stored as sparse dicts)
        self.doc_vectors = []
        for tokens in tokenized_docs:
            tf = Counter(tokens)
            total = len(tokens) if tokens else 1
            vector = {
                term: (count / total) * self.idf.get(term, 0)
                for term, count in tf.items()
            }
            self.doc_vectors.append(vector)

        self._built = True

    def query(self, query_text: str, top_k: int = MAX_LOCAL_RESULTS) -> list:
        """Retrieve the top-k most relevant documents for the query."""
        if not self._built:
            self.build_index()

        if not self.documents:
            return []

        query_tokens = _tokenize(query_text)
        query_tf = Counter(query_tokens)
        total = len(query_tokens) if query_tokens else 1
        query_vector = {
            term: (count / total) * self.idf.get(term, 0)
            for term, count in query_tf.items()
        }

        scores = []
        for i, doc_vec in enumerate(self.doc_vectors):
            score = _cosine_similarity(query_vector, doc_vec)
            scores.append((score, i))

        scores.sort(reverse=True)
        results = []
        for score, idx in scores[:top_k]:
            if score > 0.0:
                doc = self.documents[idx]
                doc.score = score
                results.append(doc)
        return results


def _cosine_similarity(vec_a: dict, vec_b: dict) -> float:
    """Compute cosine similarity between two sparse vectors (dicts)."""
    common_terms = set(vec_a.keys()) & set(vec_b.keys())
    if not common_terms:
        return 0.0

    dot_product = sum(vec_a[t] * vec_b[t] for t in common_terms)
    norm_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    norm_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))

    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


# ---------------------------------------------------------------------------
# Local knowledge base loading
# ---------------------------------------------------------------------------

def _extract_frontmatter_title(content: str) -> str:
    """Extract title from YAML front matter."""
    match = re.search(r'^---\s*\n.*?title:\s*["\']?(.+?)["\']?\s*\n.*?---',
                       content, re.DOTALL)
    return match.group(1).strip() if match else ""


def _strip_frontmatter(content: str) -> str:
    """Remove YAML front matter from markdown content."""
    return re.sub(r'^---\s*\n.*?---\s*\n', '', content, count=1, flags=re.DOTALL)


def _strip_hugo_shortcodes(content: str) -> str:
    """Remove Hugo shortcodes like {{< figure ... >}} from text."""
    return re.sub(r'\{\{<.*?>}\}', '', content)


def load_local_knowledge_base() -> list:
    """
    Load existing market health articles and documentation as Document objects.
    Chunks long documents for better retrieval granularity.
    """
    documents = []

    # Load market health posts (articles about wash trading / manipulation)
    post_pattern = os.path.join(MARKET_HEALTH_POSTS_DIR, "**/index.md")
    for filepath in glob.glob(post_pattern, recursive=True):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            title = _extract_frontmatter_title(content)
            text = _strip_frontmatter(content)
            text = _strip_hugo_shortcodes(text)
            text = text.strip()

            if not text:
                continue

            # Chunk long articles for finer-grained retrieval
            chunks = _chunk_text(text)
            for i, chunk in enumerate(chunks):
                doc = Document(
                    text=chunk,
                    source=filepath,
                    title=f"{title} (chunk {i + 1}/{len(chunks)})" if len(chunks) > 1 else title,
                )
                documents.append(doc)
        except Exception as e:
            logger.warning(f"Failed to load {filepath}: {e}")

    # Load metric documentation pages
    doc_pattern = os.path.join(MARKET_HEALTH_DOCS_DIR, "**/index.md")
    for filepath in glob.glob(doc_pattern, recursive=True):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            title = _extract_frontmatter_title(content)
            text = _strip_frontmatter(content)
            text = _strip_hugo_shortcodes(text)
            text = text.strip()

            if text:
                documents.append(Document(
                    text=text,
                    source=filepath,
                    title=title or "Metric Documentation",
                ))
        except Exception as e:
            logger.warning(f"Failed to load {filepath}: {e}")

    # Also load the top-level metrics documentation
    metrics_file = os.path.join(MARKET_HEALTH_DOCS_DIR, "market-health-metrics.md")
    if os.path.exists(metrics_file):
        try:
            with open(metrics_file, 'r', encoding='utf-8') as f:
                content = f.read()
            text = _strip_frontmatter(content)
            text = _strip_hugo_shortcodes(text)
            documents.append(Document(
                text=text.strip(),
                source=metrics_file,
                title="Market Health Metrics API Documentation",
            ))
        except Exception as e:
            logger.warning(f"Failed to load {metrics_file}: {e}")

    logger.info(f"Loaded {len(documents)} document chunks from local knowledge base")
    return documents


# ---------------------------------------------------------------------------
# Web search retrieval via DuckDuckGo (already a project dependency)
# ---------------------------------------------------------------------------

def _search_web_duckduckgo(query: str, max_results: int = MAX_WEB_RESULTS) -> list:
    """
    Search the web using DuckDuckGo and return results as Document objects.
    Uses the duckduckgo-search package (already in pyproject.toml).
    """
    results = []
    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            search_results = list(ddgs.text(query, max_results=max_results))

        for item in search_results:
            title = item.get("title", "")
            body = item.get("body", "")
            href = item.get("href", "")

            if body:
                results.append(Document(
                    text=body,
                    source=href,
                    title=title,
                ))
    except ImportError:
        logger.warning("duckduckgo-search not installed; skipping web search")
    except Exception as e:
        logger.warning(f"Web search failed: {e}")

    return results


def _fetch_article_content(url: str, max_chars: int = 3000) -> Optional[str]:
    """
    Fetch and extract main text content from a URL.
    Returns truncated plain text or None on failure.
    """
    try:
        resp = requests.get(
            url,
            timeout=WEB_SEARCH_TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0 (compatible; DNI-MarketHealthBot)"}
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove script and style elements
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        # Collapse whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text[:max_chars] if text else None
    except Exception as e:
        logger.debug(f"Failed to fetch {url}: {e}")
        return None


# ---------------------------------------------------------------------------
# Query builder
# ---------------------------------------------------------------------------

def build_search_query(marketvenueid: str, pairid: str,
                       start: str, end: str) -> str:
    """
    Build a search query string from market data parameters.
    Focuses on terms likely to surface relevant manipulation context.
    """
    exchange_name = marketvenueid.replace("-", " ").title()
    pair_name = pairid.upper().replace("-", "/")

    query = (
        f"{exchange_name} {pair_name} wash trading market manipulation "
        f"volume anomaly {start} {end}"
    )
    return query


# ---------------------------------------------------------------------------
# Main retrieval pipeline
# ---------------------------------------------------------------------------

def retrieve_rag_context(marketvenueid: str, pairid: str,
                         start: str, end: str,
                         enable_web_search: bool = True,
                         enable_web_scraping: bool = False) -> RAGContext:
    """
    Retrieve relevant context for the Market Health Reporter using RAG.

    This function:
      1. Loads and indexes the local knowledge base (articles + docs)
      2. Builds a search query from the market data parameters
      3. Retrieves the most relevant local documents via TF-IDF similarity
      4. Optionally searches the web via DuckDuckGo for additional context
      5. Returns a RAGContext object with formatted results

    Args:
        marketvenueid: Exchange identifier (e.g., "huobi")
        pairid:        Trading pair (e.g., "ht-usdt")
        start:         Analysis period start date
        end:           Analysis period end date
        enable_web_search:   Whether to include DuckDuckGo web results
        enable_web_scraping: Whether to fetch full article content from URLs

    Returns:
        RAGContext with local and web retrieval results
    """
    context = RAGContext()
    query = build_search_query(marketvenueid, pairid, start, end)
    logger.info(f"RAG query: {query}")

    # --- Step 1: Local knowledge base retrieval ---
    try:
        local_docs = load_local_knowledge_base()
        if local_docs:
            retriever = TFIDFRetriever()
            retriever.add_documents(local_docs)
            retriever.build_index()
            context.local_docs = retriever.query(query, top_k=MAX_LOCAL_RESULTS)
            logger.info(
                f"Retrieved {len(context.local_docs)} local documents "
                f"(scores: {[f'{d.score:.3f}' for d in context.local_docs]})"
            )
    except Exception as e:
        logger.warning(f"Local retrieval failed: {e}")

    # --- Step 2: Web search retrieval ---
    if enable_web_search:
        try:
            web_docs = _search_web_duckduckgo(query, max_results=MAX_WEB_RESULTS)

            # Optionally fetch full article content for top results
            if enable_web_scraping:
                for doc in web_docs[:3]:
                    full_text = _fetch_article_content(doc.source)
                    if full_text and len(full_text) > len(doc.text):
                        doc.text = full_text

            context.web_results = web_docs
            logger.info(f"Retrieved {len(context.web_results)} web results")
        except Exception as e:
            logger.warning(f"Web retrieval failed: {e}")

    return context
