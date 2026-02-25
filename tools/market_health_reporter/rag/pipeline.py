"""
RAG pipeline orchestrator.

Ties together source fetching, text extraction, chunking, and semantic
retrieval into a single `build_rag_context` function that returns a
formatted context string ready for prompt injection.
"""

from __future__ import annotations

import logging
from typing import Optional

from tools.market_health_reporter.rag.sources import fetch_all_sources, ArticleRef
from tools.market_health_reporter.rag.extractor import extract_article_text
from tools.market_health_reporter.rag.chunker import chunk_text, TextChunk
from tools.market_health_reporter.rag.retriever import retrieve_relevant_chunks

logger = logging.getLogger(__name__)

# Approximate chars-per-token ratio for budget calculation
_CHARS_PER_TOKEN = 4


def _build_retrieval_query(marketvenueid: str, pairid: str, start: str, end: str) -> str:
    """
    Construct a semantic search query from the market parameters.

    The query is designed to match news articles about market manipulation,
    wash trading, volume anomalies, and regulatory actions related to the
    specific exchange and trading pair.
    """
    pair_parts = []
    for sep in ("-", "/", "_"):
        if sep in pairid:
            pair_parts = [p.upper() for p in pairid.split(sep) if p]
            break
    if not pair_parts:
        pair_parts = [pairid.upper()]

    venue = marketvenueid.capitalize()
    pair_label = "/".join(pair_parts)

    return (
        f"{venue} exchange {pair_label} market manipulation wash trading "
        f"volume anomaly suspicious trading activity investigation "
        f"regulatory action {start} to {end}"
    )


def _format_context(
    retrieved: list[tuple[TextChunk, float]],
    max_chars: int,
) -> Optional[str]:
    """
    Format retrieved chunks into a structured context string.

    Each chunk includes its source attribution.  The total output is
    capped at max_chars to respect the token budget.
    """
    if not retrieved:
        return None

    sections: list[str] = []
    total_chars = 0

    for chunk, score in retrieved:
        header = f"[Source: {chunk.source_title}]({chunk.source_url})"
        section = f"{header}\n{chunk.text}"

        if total_chars + len(section) > max_chars:
            # Truncate final section to fit budget
            remaining = max_chars - total_chars
            if remaining > 200:
                sections.append(section[:remaining] + "...")
            break

        sections.append(section)
        total_chars += len(section) + 2  # account for separator

    return "\n\n---\n\n".join(sections) if sections else None


def build_rag_context(
    marketvenueid: str,
    pairid: str,
    start: str = "",
    end: str = "",
    openai_api_key: str = "",
    brave_api_key: str = "",
    cryptopanic_token: str = "",
    max_tokens: int = 3000,
    top_k: int = 5,
) -> Optional[str]:
    """
    End-to-end RAG pipeline: fetch, extract, chunk, embed, retrieve.

    This is the main entry point for the RAG module.  It fetches articles
    from multiple news sources, extracts and chunks text, performs semantic
    retrieval, and returns a formatted context string.

    The function is designed to degrade gracefully:
    - No API keys → uses whatever sources are available
    - No OpenAI key → falls back to TF-IDF retrieval
    - Network errors → returns None (caller proceeds without RAG)

    Args:
        marketvenueid: Exchange identifier (e.g., "binance").
        pairid: Trading pair (e.g., "btc-usdt").
        start: Analysis period start date (YYYY-MM-DD).
        end: Analysis period end date (YYYY-MM-DD).
        openai_api_key: OpenAI API key for embeddings (optional).
        brave_api_key: Brave Search API key (optional).
        cryptopanic_token: CryptoPanic auth token (optional).
        max_tokens: Maximum token budget for the context string.
        top_k: Number of top chunks to include.

    Returns:
        Formatted context string with source attributions, or None if
        no relevant content was found.
    """
    max_chars = max_tokens * _CHARS_PER_TOKEN

    # Step 1: Fetch article references from all sources
    logger.info("RAG: Fetching article references for %s/%s", marketvenueid, pairid)
    refs = fetch_all_sources(
        marketvenueid=marketvenueid,
        pairid=pairid,
        start=start,
        end=end,
        brave_api_key=brave_api_key,
        cryptopanic_token=cryptopanic_token,
    )

    if not refs:
        logger.info("RAG: No article references found")
        return None

    logger.info("RAG: Found %d article references", len(refs))

    # Step 2: Extract text from articles
    all_chunks: list[TextChunk] = []
    for ref in refs:
        text = extract_article_text(ref.url)
        if text:
            chunks = chunk_text(
                text=text,
                source_url=ref.url,
                source_title=ref.title,
            )
            all_chunks.extend(chunks)

    if not all_chunks:
        # Fall back to using snippets from search results
        logger.info("RAG: No full-text articles extracted, using snippets")
        for ref in refs:
            if ref.snippet:
                all_chunks.append(TextChunk(
                    text=ref.snippet,
                    source_url=ref.url,
                    source_title=ref.title,
                    chunk_index=0,
                ))

    if not all_chunks:
        logger.info("RAG: No content available after extraction")
        return None

    logger.info("RAG: %d chunks from %d articles", len(all_chunks), len(refs))

    # Step 3: Retrieve most relevant chunks
    query = _build_retrieval_query(marketvenueid, pairid, start, end)
    retrieved = retrieve_relevant_chunks(
        query=query,
        chunks=all_chunks,
        openai_api_key=openai_api_key,
        top_k=top_k,
    )

    if not retrieved:
        logger.info("RAG: No chunks met the relevance threshold")
        return None

    logger.info(
        "RAG: Retrieved %d chunks (top score: %.3f)",
        len(retrieved),
        retrieved[0][1],
    )

    # Step 4: Format into context string
    return _format_context(retrieved, max_chars)
