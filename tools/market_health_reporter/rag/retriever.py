"""
Semantic retrieval using OpenAI embeddings and cosine similarity.

Embeds text chunks and a query, then ranks chunks by relevance.
Falls back to TF-IDF-based retrieval when no OpenAI API key is available,
ensuring the RAG pipeline works even without an embedding model.
"""

from __future__ import annotations

import logging
import math
from typing import Optional

from tools.market_health_reporter.rag.chunker import TextChunk

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Cosine similarity
# --------------------------------------------------------------------------- #

def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# --------------------------------------------------------------------------- #
# OpenAI embedding
# --------------------------------------------------------------------------- #

def _embed_texts_openai(texts: list[str], api_key: str) -> Optional[list[list[float]]]:
    """
    Generate embeddings via OpenAI's text-embedding-3-small model.

    Returns None on failure so callers can fall back.
    """
    try:
        import openai
        openai.api_key = api_key
        response = openai.Embedding.create(
            model="text-embedding-3-small",
            input=texts,
        )
        return [item["embedding"] for item in response["data"]]
    except Exception as exc:
        logger.warning("OpenAI embedding failed: %s", exc)
        return None


# --------------------------------------------------------------------------- #
# TF-IDF fallback
# --------------------------------------------------------------------------- #

def _tfidf_similarity(query: str, texts: list[str]) -> list[float]:
    """
    Compute simple TF-IDF cosine similarity scores as an embedding-free fallback.
    Uses term frequency with basic IDF weighting.
    """
    import re
    from collections import Counter

    def tokenize(text: str) -> list[str]:
        return re.findall(r"[a-z0-9]+", text.lower())

    query_tokens = tokenize(query)
    doc_tokens_list = [tokenize(t) for t in texts]

    # Build vocabulary and document frequencies
    all_docs = [query_tokens] + doc_tokens_list
    num_docs = len(all_docs)
    df: Counter = Counter()
    for tokens in all_docs:
        df.update(set(tokens))

    def tfidf_vector(tokens: list[str]) -> dict[str, float]:
        tf = Counter(tokens)
        vec = {}
        for term, count in tf.items():
            idf = math.log((num_docs + 1) / (df.get(term, 0) + 1)) + 1
            vec[term] = count * idf
        return vec

    query_vec = tfidf_vector(query_tokens)

    scores: list[float] = []
    for doc_tokens in doc_tokens_list:
        doc_vec = tfidf_vector(doc_tokens)
        # Cosine similarity between sparse vectors
        common_terms = set(query_vec.keys()) & set(doc_vec.keys())
        dot = sum(query_vec[t] * doc_vec[t] for t in common_terms)
        norm_q = math.sqrt(sum(v * v for v in query_vec.values()))
        norm_d = math.sqrt(sum(v * v for v in doc_vec.values()))
        sim = dot / (norm_q * norm_d) if (norm_q > 0 and norm_d > 0) else 0.0
        scores.append(sim)

    return scores


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def retrieve_relevant_chunks(
    query: str,
    chunks: list[TextChunk],
    openai_api_key: str = "",
    top_k: int = 5,
    min_score: float = 0.15,
) -> list[tuple[TextChunk, float]]:
    """
    Rank chunks by semantic relevance to the query and return top-k.

    Uses OpenAI embeddings when an API key is provided, otherwise falls
    back to TF-IDF similarity.

    Args:
        query: The retrieval query (derived from market data context).
        chunks: All text chunks from fetched articles.
        openai_api_key: OpenAI API key (optional).
        top_k: Maximum number of chunks to return.
        min_score: Minimum similarity score to include a chunk.

    Returns:
        List of (chunk, score) tuples sorted by descending relevance.
    """
    if not chunks:
        return []

    texts = [c.text for c in chunks]

    # Try OpenAI embeddings first
    if openai_api_key:
        embeddings = _embed_texts_openai([query] + texts, openai_api_key)
        if embeddings is not None:
            query_emb = embeddings[0]
            chunk_embs = embeddings[1:]
            scores = [_cosine_similarity(query_emb, ce) for ce in chunk_embs]
            ranked = sorted(
                zip(chunks, scores), key=lambda x: x[1], reverse=True
            )
            return [(c, s) for c, s in ranked if s >= min_score][:top_k]

    # Fallback: TF-IDF similarity
    logger.info("Using TF-IDF fallback for chunk retrieval")
    scores = _tfidf_similarity(query, texts)
    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
    return [(c, s) for c, s in ranked if s >= min_score][:top_k]
