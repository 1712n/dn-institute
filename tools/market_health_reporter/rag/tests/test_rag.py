"""
Tests for the RAG module components.

These tests use mocking to avoid external API calls and verify the
chunking, retrieval, and pipeline logic works correctly.
"""

import pytest
from unittest.mock import patch, MagicMock

from tools.market_health_reporter.rag.chunker import chunk_text, TextChunk
from tools.market_health_reporter.rag.retriever import (
    _cosine_similarity,
    _tfidf_similarity,
    retrieve_relevant_chunks,
)
from tools.market_health_reporter.rag.sources import (
    _build_search_queries,
    _extract_currencies,
    ArticleRef,
)
from tools.market_health_reporter.rag.pipeline import (
    _build_retrieval_query,
    _format_context,
)


# --------------------------------------------------------------------------- #
# chunker tests
# --------------------------------------------------------------------------- #

class TestChunker:
    def test_empty_text_returns_no_chunks(self):
        assert chunk_text("") == []
        assert chunk_text("short") == []

    def test_single_sentence(self):
        text = "A" * 200 + "."
        chunks = chunk_text(text, source_url="http://example.com", source_title="Test")
        assert len(chunks) == 1
        assert chunks[0].source_url == "http://example.com"

    def test_multiple_chunks_with_overlap(self):
        # Create text with many sentences that exceed chunk_size
        sentences = ["This is sentence number %d." % i for i in range(100)]
        text = " ".join(sentences)
        chunks = chunk_text(text, chunk_size=200, chunk_overlap=50)
        assert len(chunks) > 1
        # Verify chunks overlap (some text appears in consecutive chunks)
        for i in range(len(chunks) - 1):
            # Last words of chunk i should appear in chunk i+1 (overlap)
            last_words = chunks[i].text.split()[-3:]
            assert any(w in chunks[i + 1].text for w in last_words)


# --------------------------------------------------------------------------- #
# retriever tests
# --------------------------------------------------------------------------- #

class TestRetriever:
    def test_cosine_similarity_identical(self):
        vec = [1.0, 2.0, 3.0]
        assert abs(_cosine_similarity(vec, vec) - 1.0) < 1e-6

    def test_cosine_similarity_orthogonal(self):
        assert abs(_cosine_similarity([1, 0], [0, 1])) < 1e-6

    def test_cosine_similarity_zero_vector(self):
        assert _cosine_similarity([0, 0], [1, 2]) == 0.0

    def test_tfidf_similarity_basic(self):
        query = "bitcoin wash trading manipulation"
        texts = [
            "bitcoin exchange wash trading detected on binance",
            "weather forecast for tomorrow sunny skies",
            "crypto manipulation and wash trading investigation",
        ]
        scores = _tfidf_similarity(query, texts)
        # First and third should score higher than the weather text
        assert scores[0] > scores[1]
        assert scores[2] > scores[1]

    def test_retrieve_empty_chunks(self):
        result = retrieve_relevant_chunks("query", [])
        assert result == []

    def test_retrieve_with_tfidf_fallback(self):
        chunks = [
            TextChunk("bitcoin wash trading on binance exchange", "http://a.com", "A", 0),
            TextChunk("sunny weather forecast for the weekend", "http://b.com", "B", 0),
        ]
        results = retrieve_relevant_chunks(
            "binance bitcoin wash trading", chunks, openai_api_key="", top_k=2, min_score=0.0
        )
        assert len(results) >= 1
        # The bitcoin/wash-trading chunk should rank first
        assert results[0][0].source_url == "http://a.com"


# --------------------------------------------------------------------------- #
# sources tests
# --------------------------------------------------------------------------- #

class TestSources:
    def test_extract_currencies_dash(self):
        from tools.market_health_reporter.rag.sources import _extract_currencies
        # _extract_currencies is used internally by _build_search_queries
        queries = _build_search_queries("binance", "btc-usdt", "2024-01-01", "2024-01-07")
        assert any("BTC" in q for q in queries)
        assert any("Binance" in q for q in queries)

    def test_build_search_queries_no_separator(self):
        queries = _build_search_queries("kraken", "eth", "2024-01-01", "2024-01-07")
        assert any("ETH" in q for q in queries)


# --------------------------------------------------------------------------- #
# pipeline tests
# --------------------------------------------------------------------------- #

class TestPipeline:
    def test_build_retrieval_query(self):
        query = _build_retrieval_query("binance", "btc-usdt", "2024-01-01", "2024-01-07")
        assert "Binance" in query
        assert "BTC/USDT" in query
        assert "wash trading" in query

    def test_format_context_respects_budget(self):
        chunks = [
            (TextChunk("A" * 500, "http://a.com", "Article A", 0), 0.9),
            (TextChunk("B" * 500, "http://b.com", "Article B", 0), 0.8),
        ]
        result = _format_context(chunks, max_chars=600)
        assert result is not None
        assert len(result) <= 700  # some overhead from headers

    def test_format_context_empty(self):
        assert _format_context([], max_chars=1000) is None

    @patch("tools.market_health_reporter.rag.pipeline.fetch_all_sources")
    def test_build_rag_context_no_refs(self, mock_fetch):
        mock_fetch.return_value = []
        from tools.market_health_reporter.rag.pipeline import build_rag_context
        result = build_rag_context("binance", "btc-usdt")
        assert result is None
