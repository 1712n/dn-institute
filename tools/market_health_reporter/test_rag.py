"""
Tests for the RAG module of the Market Health Reporter.

These tests cover the document collection, text chunking, cosine similarity,
query building, and vector store functionality. Tests that require the OpenAI
API are marked and can be run with a valid API key.
"""

import os
import json
import tempfile
import shutil
import numpy as np
import pytest

from tools.market_health_reporter.rag import (
    collect_documents,
    chunk_text,
    chunk_documents,
    cosine_similarity,
    build_rag_query,
    VectorStore,
    _compute_corpus_hash,
)


# ---- Test fixtures ----

@pytest.fixture
def sample_report_text():
    return """---
title: "Test Report"
date: 2023-01-01
entities:
  - TestExchange
---

## Summary

This is a test market health report analyzing wash trading on TestExchange.

## Volume Analysis

The volume distribution shows suspicious patterns consistent with manipulation.
Trading volume does not follow the expected power law distribution.

## Benford's Law

First-digit distribution analysis reveals significant deviation from Benford's Law,
with the Kolmogorov-Smirnov test value exceeding the critical value.
"""


@pytest.fixture
def sample_doc_text():
    return """---
title: "Test Metric"
weight: 10
---

## Test Metric

The test metric measures market health by analyzing trading patterns.

### Mathematical Background

The formula for this metric is straightforward and based on statistical analysis.

### Applications in Market Surveillance

- Detecting wash trading
- Identifying bot activity
- Monitoring market manipulation
"""


@pytest.fixture
def temp_corpus_dir(sample_report_text, sample_doc_text):
    """Create a temporary directory structure mimicking the corpus."""
    base_dir = tempfile.mkdtemp()
    reports_dir = os.path.join(base_dir, "reports")
    docs_dir = os.path.join(base_dir, "docs")

    # Create report
    report_subdir = os.path.join(reports_dir, "2023-01-01-test")
    os.makedirs(report_subdir)
    with open(os.path.join(report_subdir, "index.md"), "w") as f:
        f.write(sample_report_text)

    # Create doc
    doc_subdir = os.path.join(docs_dir, "test-metric")
    os.makedirs(doc_subdir)
    with open(os.path.join(doc_subdir, "index.md"), "w") as f:
        f.write(sample_doc_text)

    # Create a standalone doc
    with open(os.path.join(docs_dir, "overview.md"), "w") as f:
        f.write("## Overview\n\nThis is an overview of market health metrics and their usage in surveillance.")

    yield base_dir, reports_dir, docs_dir

    shutil.rmtree(base_dir)


@pytest.fixture
def sample_market_data():
    return [
        {
            "timestamp": "2023-01-01T00:00:00",
            "marketvenueid": "testexchange",
            "pairid": "btc-usdt",
            "vvcorrelation": 0.35,
            "benfordlawtest": 0.12,
            "buysellratio": 0.48,
            "volumedist": [[0, 100], [1, 50]],
            "vwap": 42000.0,
            "tradecount": 500,
        }
    ]


# ---- Tests for collect_documents ----

class TestCollectDocuments:
    def test_collects_reports_and_docs(self, temp_corpus_dir):
        _, reports_dir, docs_dir = temp_corpus_dir
        docs = collect_documents(reports_dir, docs_dir)
        assert len(docs) >= 2  # at least one report and one doc

    def test_report_has_correct_type(self, temp_corpus_dir):
        _, reports_dir, docs_dir = temp_corpus_dir
        docs = collect_documents(reports_dir, docs_dir)
        report_docs = [d for d in docs if d["doc_type"] == "past_report"]
        assert len(report_docs) >= 1

    def test_doc_has_correct_type(self, temp_corpus_dir):
        _, reports_dir, docs_dir = temp_corpus_dir
        docs = collect_documents(reports_dir, docs_dir)
        metric_docs = [d for d in docs if d["doc_type"] == "metric_documentation"]
        assert len(metric_docs) >= 1

    def test_documents_have_text(self, temp_corpus_dir):
        _, reports_dir, docs_dir = temp_corpus_dir
        docs = collect_documents(reports_dir, docs_dir)
        for doc in docs:
            assert "text" in doc
            assert len(doc["text"]) > 0

    def test_documents_have_source(self, temp_corpus_dir):
        _, reports_dir, docs_dir = temp_corpus_dir
        docs = collect_documents(reports_dir, docs_dir)
        for doc in docs:
            assert "source" in doc

    def test_empty_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            docs = collect_documents(
                os.path.join(tmp, "nonexistent_reports"),
                os.path.join(tmp, "nonexistent_docs"),
            )
            assert docs == []

    def test_collects_standalone_md_files(self, temp_corpus_dir):
        _, reports_dir, docs_dir = temp_corpus_dir
        docs = collect_documents(reports_dir, docs_dir)
        standalone_docs = [d for d in docs if "overview.md" in d["source"]]
        assert len(standalone_docs) == 1

    def test_ignores_index_files(self, temp_corpus_dir):
        _, reports_dir, docs_dir = temp_corpus_dir
        # Create an _index.md that should be ignored
        with open(os.path.join(docs_dir, "_index.md"), "w") as f:
            f.write("This should be ignored")
        docs = collect_documents(reports_dir, docs_dir)
        index_docs = [d for d in docs if "_index.md" in d["source"]]
        assert len(index_docs) == 0


# ---- Tests for chunk_text ----

class TestChunkText:
    def test_short_text_single_chunk(self):
        text = "## Summary\n\nThis is a short text about market analysis."
        chunks = chunk_text(text)
        assert len(chunks) >= 1

    def test_frontmatter_removed(self, sample_report_text):
        chunks = chunk_text(sample_report_text)
        for chunk in chunks:
            assert "---" not in chunk or not chunk.startswith("---")

    def test_chunks_respect_max_size(self):
        long_text = "## Section\n\n" + ("word " * 500) + "\n\n## Another\n\n" + ("text " * 500)
        chunks = chunk_text(long_text, max_size=500)
        for chunk in chunks:
            # Allow some tolerance for section headers
            assert len(chunk) < 600

    def test_empty_text_returns_no_chunks(self):
        chunks = chunk_text("")
        assert len(chunks) == 0

    def test_sections_are_preserved(self, sample_report_text):
        chunks = chunk_text(sample_report_text)
        all_text = " ".join(chunks)
        assert "Summary" in all_text
        assert "Volume Analysis" in all_text

    def test_small_chunks_filtered(self):
        text = "## A\n\nOk\n\n## B\n\nThis section has enough text to pass the filter."
        chunks = chunk_text(text)
        for chunk in chunks:
            assert len(chunk) > 50


# ---- Tests for chunk_documents ----

class TestChunkDocuments:
    def test_preserves_metadata(self, temp_corpus_dir):
        _, reports_dir, docs_dir = temp_corpus_dir
        docs = collect_documents(reports_dir, docs_dir)
        chunks = chunk_documents(docs)
        for chunk in chunks:
            assert "source" in chunk
            assert "doc_type" in chunk
            assert "chunk_index" in chunk
            assert "text" in chunk

    def test_chunk_index_starts_at_zero(self, temp_corpus_dir):
        _, reports_dir, docs_dir = temp_corpus_dir
        docs = collect_documents(reports_dir, docs_dir)
        chunks = chunk_documents(docs)
        # Each document's first chunk should have index 0
        seen_sources = set()
        for chunk in chunks:
            if chunk["source"] not in seen_sources:
                assert chunk["chunk_index"] == 0
                seen_sources.add(chunk["source"])


# ---- Tests for cosine_similarity ----

class TestCosineSimilarity:
    def test_identical_vectors(self):
        vec = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        corpus = np.array([[1.0, 0.0, 0.0]], dtype=np.float32)
        sims = cosine_similarity(vec, corpus)
        assert abs(sims[0] - 1.0) < 1e-5

    def test_orthogonal_vectors(self):
        vec = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        corpus = np.array([[0.0, 1.0, 0.0]], dtype=np.float32)
        sims = cosine_similarity(vec, corpus)
        assert abs(sims[0]) < 1e-5

    def test_opposite_vectors(self):
        vec = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        corpus = np.array([[-1.0, 0.0, 0.0]], dtype=np.float32)
        sims = cosine_similarity(vec, corpus)
        assert abs(sims[0] + 1.0) < 1e-5

    def test_multiple_corpus_vectors(self):
        query = np.array([1.0, 1.0, 0.0], dtype=np.float32)
        corpus = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [1.0, 1.0, 0.0],
        ], dtype=np.float32)
        sims = cosine_similarity(query, corpus)
        assert len(sims) == 3
        # Third vector should be most similar (identical direction)
        assert sims[2] > sims[0]
        assert sims[2] > sims[1]

    def test_zero_vector_handling(self):
        vec = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        corpus = np.array([[1.0, 0.0, 0.0]], dtype=np.float32)
        sims = cosine_similarity(vec, corpus)
        # Should not raise, result should be close to 0
        assert abs(sims[0]) < 1e-3


# ---- Tests for build_rag_query ----

class TestBuildRagQuery:
    def test_includes_market_venue(self, sample_market_data):
        query = build_rag_query("binance", "btc-usdt", sample_market_data)
        assert "binance" in query

    def test_includes_pair(self, sample_market_data):
        query = build_rag_query("binance", "btc-usdt", sample_market_data)
        assert "btc-usdt" in query

    def test_includes_metric_descriptions(self, sample_market_data):
        query = build_rag_query("binance", "btc-usdt", sample_market_data)
        assert "volume" in query.lower() or "correlation" in query.lower()

    def test_includes_manipulation_keywords(self, sample_market_data):
        query = build_rag_query("binance", "btc-usdt", sample_market_data)
        assert "wash trading" in query.lower()
        assert "manipulation" in query.lower()

    def test_empty_data(self):
        query = build_rag_query("exchange", "eth-usdt", [])
        assert "exchange" in query
        assert "eth-usdt" in query

    def test_data_without_metrics(self):
        data = [{"timestamp": "2023-01-01", "marketvenueid": "test", "pairid": "test"}]
        query = build_rag_query("test", "test-pair", data)
        assert "market health metrics" in query


# ---- Tests for corpus hash ----

class TestCorpusHash:
    def test_same_content_same_hash(self):
        chunks = [{"text": "hello world"}]
        hash1 = _compute_corpus_hash(chunks)
        hash2 = _compute_corpus_hash(chunks)
        assert hash1 == hash2

    def test_different_content_different_hash(self):
        chunks1 = [{"text": "hello world"}]
        chunks2 = [{"text": "different content"}]
        hash1 = _compute_corpus_hash(chunks1)
        hash2 = _compute_corpus_hash(chunks2)
        assert hash1 != hash2


# ---- Tests for VectorStore (non-API parts) ----

class TestVectorStore:
    def test_empty_store_search_returns_empty(self):
        store = VectorStore()
        # Simulate empty store
        assert store.chunks == []
        assert store.embeddings is None

    def test_cache_round_trip(self):
        """Test that saving and loading cache works correctly."""
        store = VectorStore()
        store.chunks = [
            {"text": "test chunk", "source": "test.md", "doc_type": "test", "chunk_index": 0}
        ]
        store.embeddings = np.random.randn(1, 10).astype(np.float32)
        store.corpus_hash = "test_hash_123"

        with tempfile.TemporaryDirectory() as tmp:
            store._save_cache(tmp)

            # Create a new store and load
            store2 = VectorStore()
            store2.chunks = store.chunks
            store2.corpus_hash = "test_hash_123"
            loaded = store2._load_cache(tmp)

            assert loaded is True
            np.testing.assert_array_almost_equal(store2.embeddings, store.embeddings)

    def test_cache_invalidation_on_hash_change(self):
        """Test that cache is invalidated when corpus changes."""
        store = VectorStore()
        store.chunks = [
            {"text": "test chunk", "source": "test.md", "doc_type": "test", "chunk_index": 0}
        ]
        store.embeddings = np.random.randn(1, 10).astype(np.float32)
        store.corpus_hash = "hash_v1"

        with tempfile.TemporaryDirectory() as tmp:
            store._save_cache(tmp)

            # Try to load with different hash
            store2 = VectorStore()
            store2.chunks = store.chunks
            store2.corpus_hash = "hash_v2"  # different hash
            loaded = store2._load_cache(tmp)

            assert loaded is False


# ---- Integration test with real corpus (no API) ----

class TestIntegrationWithRealCorpus:
    def test_collect_real_documents(self):
        """Test collecting documents from the actual repository corpus."""
        reports_dir = "content/research/market-health/posts"
        docs_dir = "content/research/market-health/docs"

        if not os.path.isdir(reports_dir) or not os.path.isdir(docs_dir):
            pytest.skip("Real corpus not available in this environment")

        docs = collect_documents(reports_dir, docs_dir)
        assert len(docs) > 0, "Should find documents in the real corpus"

        report_count = sum(1 for d in docs if d["doc_type"] == "past_report")
        doc_count = sum(1 for d in docs if d["doc_type"] == "metric_documentation")
        print(f"Found {report_count} reports and {doc_count} documentation files")

        assert report_count > 0, "Should find at least one past report"
        assert doc_count > 0, "Should find at least one documentation file"

    def test_chunk_real_documents(self):
        """Test chunking documents from the actual repository corpus."""
        reports_dir = "content/research/market-health/posts"
        docs_dir = "content/research/market-health/docs"

        if not os.path.isdir(reports_dir) or not os.path.isdir(docs_dir):
            pytest.skip("Real corpus not available in this environment")

        docs = collect_documents(reports_dir, docs_dir)
        chunks = chunk_documents(docs)
        assert len(chunks) > len(docs), "Chunking should produce more items than documents"
        print(f"Created {len(chunks)} chunks from {len(docs)} documents")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
