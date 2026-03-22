"""
🌰 Tests for RAG context retrieval module.
"""

import os
import tempfile
import pytest

from tools.market_health_reporter.rag_context import (
    _tokenize,
    _compute_tfidf,
    _cosine_similarity,
    _extract_title,
    _chunk_article,
    _load_articles,
    retrieve_context,
)


class TestTokenize:
    """🌰 Test tokenization."""

    def test_basic_tokenization(self):
        tokens = _tokenize("Huobi wash trading BTC-USDT")
        assert "huobi" in tokens
        assert "wash" in tokens
        assert "trading" in tokens
        assert "usdt" in tokens

    def test_removes_single_chars(self):
        tokens = _tokenize("a b c hello world")
        assert "hello" in tokens
        assert "world" in tokens
        assert "a" not in tokens

    def test_lowercases(self):
        tokens = _tokenize("BITCOIN Ethereum")
        assert "bitcoin" in tokens
        assert "ethereum" in tokens


class TestTfIdf:
    """🌰 Test TF-IDF computation."""

    def test_basic_tfidf(self):
        docs = [
            ["wash", "trading", "volume"],
            ["bitcoin", "price", "volume"],
            ["wash", "trading", "manipulation"],
        ]
        vecs, idf = _compute_tfidf(docs)
        assert len(vecs) == 3
        # "volume" appears in 2/3 docs, "wash" in 2/3
        assert "volume" in idf
        assert "wash" in idf

    def test_empty_docs(self):
        vecs, idf = _compute_tfidf([[]])
        assert len(vecs) == 1


class TestCosineSimilarity:
    """🌰 Test cosine similarity."""

    def test_identical_vectors(self):
        vec = {"wash": 1.0, "trading": 0.5}
        assert abs(_cosine_similarity(vec, vec) - 1.0) < 0.001

    def test_orthogonal_vectors(self):
        vec_a = {"wash": 1.0}
        vec_b = {"bitcoin": 1.0}
        assert _cosine_similarity(vec_a, vec_b) == 0.0

    def test_empty_vectors(self):
        assert _cosine_similarity({}, {}) == 0.0


class TestExtractTitle:
    """🌰 Test frontmatter title extraction."""

    def test_quoted_title(self):
        content = '---\ntitle: "Uncovering Wash Trading"\ndate: 2023-08-14\n---\n'
        assert _extract_title(content) == "Uncovering Wash Trading"

    def test_unquoted_title(self):
        content = "---\ntitle: Market Health Report\ndate: 2023-01-01\n---\n"
        assert _extract_title(content) == "Market Health Report"

    def test_no_title(self):
        assert _extract_title("No frontmatter here") == ""


class TestChunkArticle:
    """🌰 Test article chunking."""

    def test_single_chunk(self):
        article = {
            "title": "Test",
            "path": "/test.md",
            "content": "---\ntitle: Test\n---\nShort article.",
            "tokens": ["short", "article"],
        }
        chunks = _chunk_article(article, chunk_size=100)
        assert len(chunks) >= 1
        assert chunks[0]["title"] == "Test"

    def test_multiple_chunks(self):
        long_text = "---\ntitle: Test\n---\n" + ". ".join(
            [f"Sentence number {i} with some padding words" for i in range(100)]
        )
        article = {
            "title": "Long",
            "path": "/long.md",
            "content": long_text,
            "tokens": _tokenize(long_text),
        }
        chunks = _chunk_article(article, chunk_size=20)
        assert len(chunks) > 1


class TestLoadArticles:
    """🌰 Test loading articles from filesystem."""

    def test_loads_from_test_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a mock article
            posts_dir = os.path.join(
                tmpdir, "content", "research", "market-health", "posts", "2023-test"
            )
            os.makedirs(posts_dir)
            with open(os.path.join(posts_dir, "index.md"), "w") as f:
                f.write(
                    '---\ntitle: "Test Article"\n---\n'
                    "This is a test article about wash trading on Huobi."
                )

            articles = _load_articles(tmpdir)
            assert len(articles) >= 1
            assert articles[0]["title"] == "Test Article"

    def test_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            articles = _load_articles(tmpdir)
            assert articles == []


class TestRetrieveContext:
    """🌰 Test the full RAG retrieval pipeline."""

    def test_with_local_articles(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            posts_dir = os.path.join(
                tmpdir, "content", "research", "market-health", "posts", "2023-huobi"
            )
            os.makedirs(posts_dir)
            with open(os.path.join(posts_dir, "index.md"), "w") as f:
                f.write(
                    '---\ntitle: "Wash Trading on Huobi"\n---\n'
                    "Analysis of wash trading patterns and manipulation on Huobi exchange. "
                    "Volume distribution showed anomalous patterns consistent with market manipulation. "
                    "The buy-sell ratio was unnaturally stable during periods of high volatility. "
                    "Benford's law test revealed significant deviations from expected distributions. "
                    "The volume-volatility correlation was consistently below the 0.4 threshold. "
                    "Time-of-trade analysis showed suspicious bot-like patterns in trading activity. "
                    "Market health indicators pointed to wash trading across multiple trading pairs. "
                    "The VWAP diverged significantly from actual trading prices on the exchange. "
                    "Overall market health assessment indicates significant manipulation activity."
                )

            context = retrieve_context(
                marketvenueid="huobi",
                pairid="btc-usdt",
                start="2023-08-01",
                end="2023-08-14",
                repo_root=tmpdir,
                enable_web_search=False,  # Don't hit network in tests
            )
            assert "<context>" in context
            assert "Huobi" in context or "huobi" in context.lower()

    def test_empty_repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            context = retrieve_context(
                marketvenueid="binance",
                pairid="eth-usdt",
                start="2024-01-01",
                end="2024-01-07",
                repo_root=tmpdir,
                enable_web_search=False,
            )
            # Should return empty string when no articles found
            assert context == ""

    def test_returns_string(self):
        """🌰 Ensure output is always a string."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = retrieve_context(
                "test", "btc-usdt", "2024-01-01", "2024-01-07",
                repo_root=tmpdir,
                enable_web_search=False,
            )
            assert isinstance(result, str)
