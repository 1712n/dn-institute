"""
🌰 RAG context retrieval for Market Health Reporter.

Retrieves relevant context from two sources:
1. Local knowledge base — existing dn-institute market-health articles
2. Web search — recent news about the exchange/pair being analyzed

Uses TF-IDF + cosine similarity for retrieval (zero external dependencies
beyond scikit-learn). No API keys required for the local KB; web search
is optional and gracefully degrades if unavailable.
"""

import os
import re
import glob
import json
import math
import logging
from collections import Counter
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# 🌰 Path to the market-health articles relative to repo root
ARTICLES_DIR = os.path.join("content", "research", "market-health", "posts")
DOCS_DIR = os.path.join("content", "research", "market-health", "docs")


def _tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer. 🌰"""
    return re.findall(r"\b[a-z][a-z0-9]{1,}\b", text.lower())


def _compute_tfidf(documents: list[list[str]]) -> tuple[list[dict], dict]:
    """
    Compute TF-IDF vectors for a list of tokenized documents. 🌰
    Returns (tfidf_vectors, idf_dict).
    """
    n_docs = len(documents)
    # Document frequency
    df = Counter()
    for doc_tokens in documents:
        unique_tokens = set(doc_tokens)
        for token in unique_tokens:
            df[token] += 1

    # Use smoothed IDF: log((n_docs + 1) / (freq + 1)) + 1 to avoid zero IDF 🌰
    idf = {token: math.log((n_docs + 1) / (freq + 1)) + 1 for token, freq in df.items()}

    tfidf_vectors = []
    for doc_tokens in documents:
        tf = Counter(doc_tokens)
        doc_len = len(doc_tokens) if doc_tokens else 1
        vec = {
            token: (count / doc_len) * idf.get(token, 0)
            for token, count in tf.items()
        }
        tfidf_vectors.append(vec)

    return tfidf_vectors, idf


def _cosine_similarity(vec_a: dict, vec_b: dict) -> float:
    """Cosine similarity between two sparse TF-IDF vectors. 🌰"""
    common_keys = set(vec_a.keys()) & set(vec_b.keys())
    if not common_keys:
        return 0.0
    dot = sum(vec_a[k] * vec_b[k] for k in common_keys)
    norm_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    norm_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _load_articles(repo_root: str) -> list[dict]:
    """
    Load all market-health articles and docs from the repository. 🌰
    Returns list of {path, title, content, tokens}.
    """
    articles = []

    # Load posts
    posts_dir = os.path.join(repo_root, ARTICLES_DIR)
    for md_path in glob.glob(os.path.join(posts_dir, "**", "index.md"), recursive=True):
        try:
            content = _read_file(md_path)
            title = _extract_title(content)
            articles.append({
                "path": md_path,
                "title": title,
                "content": content,
                "tokens": _tokenize(content),
            })
        except Exception as e:
            logger.warning("Failed to load %s: %s", md_path, e)

    # Load docs (metric explanations)
    docs_dir = os.path.join(repo_root, DOCS_DIR)
    for md_path in glob.glob(os.path.join(docs_dir, "**", "*.md"), recursive=True):
        try:
            content = _read_file(md_path)
            title = _extract_title(content) or os.path.basename(md_path)
            articles.append({
                "path": md_path,
                "title": title,
                "content": content,
                "tokens": _tokenize(content),
            })
        except Exception as e:
            logger.warning("Failed to load %s: %s", md_path, e)

    return articles


def _read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _extract_title(content: str) -> str:
    """Extract title from Hugo frontmatter. 🌰"""
    match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
    return match.group(1) if match else ""


def _chunk_article(article: dict, chunk_size: int = 500) -> list[dict]:
    """
    Split an article into sentence-aware chunks for finer retrieval. 🌰
    """
    content = article["content"]
    # Remove frontmatter
    content = re.sub(r"^---.*?---", "", content, count=1, flags=re.DOTALL).strip()
    # Remove Hugo shortcodes
    content = re.sub(r"\{\{<.*?>\}\}", "", content)

    sentences = re.split(r"(?<=[.!?])\s+", content)
    chunks = []
    current_chunk = []
    current_len = 0

    for sentence in sentences:
        words = len(sentence.split())
        if current_len + words > chunk_size and current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "title": article["title"],
                "path": article["path"],
                "text": chunk_text,
                "tokens": _tokenize(chunk_text),
            })
            current_chunk = []
            current_len = 0
        current_chunk.append(sentence)
        current_len += words

    if current_chunk:
        chunk_text = " ".join(current_chunk)
        chunks.append({
            "title": article["title"],
            "path": article["path"],
            "text": chunk_text,
            "tokens": _tokenize(chunk_text),
        })

    return chunks


def _search_web(query: str, timeout: int = 10) -> list[dict]:
    """
    🌰 Search for recent news using DuckDuckGo HTML search (no API key).
    Returns list of {title, url, snippet}.
    Gracefully returns empty list on failure.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; MHReporter/1.0)"}
        resp = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers=headers,
            timeout=timeout,
        )
        resp.raise_for_status()

        results = []
        # Simple regex extraction from DDG HTML results
        links = re.findall(
            r'<a rel="nofollow" class="result__a" href="([^"]+)"[^>]*>(.*?)</a>',
            resp.text,
        )
        snippets = re.findall(
            r'<a class="result__snippet"[^>]*>(.*?)</a>',
            resp.text,
        )

        for i, (url, title) in enumerate(links[:5]):
            snippet = snippets[i] if i < len(snippets) else ""
            # Clean HTML tags
            title = re.sub(r"<[^>]+>", "", title)
            snippet = re.sub(r"<[^>]+>", "", snippet)
            results.append({"title": title, "url": url, "snippet": snippet})

        return results
    except Exception as e:
        logger.warning("Web search failed (non-fatal): %s", e)
        return []


def retrieve_context(
    marketvenueid: str,
    pairid: str,
    start: str,
    end: str,
    repo_root: str = ".",
    top_k: int = 3,
    enable_web_search: bool = True,
) -> str:
    """
    🌰 Main RAG retrieval function.

    Retrieves relevant context for the Market Health Reporter by:
    1. Loading and chunking existing market-health articles
    2. Building a TF-IDF index over chunks
    3. Retrieving top-k most relevant chunks for the query
    4. Optionally searching the web for recent news

    Args:
        marketvenueid: Exchange name (e.g., 'huobi')
        pairid: Trading pair (e.g., 'btc-usdt')
        start: Analysis start date
        end: Analysis end date
        repo_root: Path to repository root
        top_k: Number of chunks to retrieve
        enable_web_search: Whether to search for recent news

    Returns:
        Formatted context string to inject into the prompt
    """
    query = f"{marketvenueid} {pairid} wash trading manipulation market health"
    query_tokens = _tokenize(query)

    # 🌰 Phase 1: Local knowledge base retrieval
    articles = _load_articles(repo_root)
    if not articles:
        logger.warning("No articles found in %s", repo_root)
        local_context = ""
    else:
        # Chunk all articles
        all_chunks = []
        for article in articles:
            all_chunks.extend(_chunk_article(article))

        if all_chunks:
            # Build TF-IDF index
            all_token_lists = [c["tokens"] for c in all_chunks] + [query_tokens]
            tfidf_vecs, _ = _compute_tfidf(all_token_lists)
            query_vec = tfidf_vecs[-1]
            chunk_vecs = tfidf_vecs[:-1]

            # Score and rank
            scored = []
            for i, chunk in enumerate(all_chunks):
                score = _cosine_similarity(query_vec, chunk_vecs[i])
                scored.append((score, chunk))
            scored.sort(key=lambda x: x[0], reverse=True)

            # Format top results
            parts = []
            seen_titles = set()
            for score, chunk in scored[:top_k]:
                if score < 0.05:
                    break
                source_label = chunk["title"] or os.path.basename(chunk["path"])
                if source_label not in seen_titles:
                    parts.append(
                        f"### Source: {source_label} (relevance: {score:.2f})\n"
                        f"{chunk['text'][:1500]}"
                    )
                    seen_titles.add(source_label)
            local_context = "\n\n".join(parts)
        else:
            local_context = ""

    # 🌰 Phase 2: Web search for recent news
    web_context = ""
    if enable_web_search:
        base_token, quote_token = pairid.split("-") if "-" in pairid else (pairid, "")
        search_query = f"{marketvenueid} {base_token} wash trading manipulation {start} {end}"
        results = _search_web(search_query)
        if results:
            web_parts = []
            for r in results[:3]:
                web_parts.append(f"- **{r['title']}** ({r['url']}): {r['snippet']}")
            web_context = "### Recent News\n" + "\n".join(web_parts)

    # 🌰 Combine
    sections = []
    if local_context:
        sections.append(
            "## Reference Context from Previous Analyses\n"
            "The following excerpts from prior market health reports may provide "
            "useful patterns, terminology, and analytical approaches:\n\n"
            + local_context
        )
    if web_context:
        sections.append(
            "## Recent News Context\n"
            "Recent news that may provide additional context for the analysis:\n\n"
            + web_context
        )

    if not sections:
        return ""

    return (
        "<context>\n"
        + "\n\n".join(sections)
        + "\n</context>"
    )
