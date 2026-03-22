"""
Tests for the RAG retriever module used by Market Health Reporter.
"""

import unittest
from unittest.mock import patch, MagicMock

from tools.market_health_reporter.rag_retriever import (
    Document,
    RAGContext,
    TFIDFRetriever,
    _tokenize,
    _chunk_text,
    _cosine_similarity,
    _extract_frontmatter_title,
    _strip_frontmatter,
    _strip_hugo_shortcodes,
    build_search_query,
    retrieve_rag_context,
    load_local_knowledge_base,
)


class TestTokenize(unittest.TestCase):
    """Test the tokenizer utility."""

    def test_basic_tokenization(self):
        tokens = _tokenize("Hello World, this is a test!")
        self.assertIn("hello", tokens)
        self.assertIn("world", tokens)
        self.assertIn("test", tokens)

    def test_stopword_removal(self):
        tokens = _tokenize("the quick brown fox is a very fast animal")
        self.assertNotIn("the", tokens)
        self.assertNotIn("is", tokens)
        self.assertNotIn("a", tokens)
        self.assertIn("quick", tokens)
        self.assertIn("brown", tokens)
        self.assertIn("fox", tokens)

    def test_empty_input(self):
        tokens = _tokenize("")
        self.assertEqual(tokens, [])

    def test_numeric_tokens(self):
        tokens = _tokenize("BTC price is 50000 USD in 2023")
        self.assertIn("btc", tokens)
        self.assertIn("50000", tokens)
        self.assertIn("2023", tokens)


class TestChunkText(unittest.TestCase):
    """Test text chunking."""

    def test_short_text_no_chunking(self):
        text = "This is a short text."
        chunks = _chunk_text(text, chunk_size=100)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], text)

    def test_long_text_chunking(self):
        words = ["word"] * 200
        text = " ".join(words)
        chunks = _chunk_text(text, chunk_size=100, overlap=20)
        self.assertGreater(len(chunks), 1)
        # Each chunk should have at most chunk_size words
        for chunk in chunks[:-1]:
            self.assertLessEqual(len(chunk.split()), 100)

    def test_overlap_works(self):
        words = [f"w{i}" for i in range(150)]
        text = " ".join(words)
        chunks = _chunk_text(text, chunk_size=100, overlap=30)
        # Second chunk should start 70 words into the text
        second_start = chunks[1].split()[0]
        self.assertEqual(second_start, "w70")


class TestCosineSimilarity(unittest.TestCase):
    """Test cosine similarity computation."""

    def test_identical_vectors(self):
        vec = {"a": 1.0, "b": 2.0, "c": 3.0}
        sim = _cosine_similarity(vec, vec)
        self.assertAlmostEqual(sim, 1.0, places=5)

    def test_orthogonal_vectors(self):
        vec_a = {"a": 1.0}
        vec_b = {"b": 1.0}
        sim = _cosine_similarity(vec_a, vec_b)
        self.assertAlmostEqual(sim, 0.0, places=5)

    def test_partial_overlap(self):
        vec_a = {"a": 1.0, "b": 1.0}
        vec_b = {"b": 1.0, "c": 1.0}
        sim = _cosine_similarity(vec_a, vec_b)
        self.assertGreater(sim, 0.0)
        self.assertLess(sim, 1.0)

    def test_empty_vectors(self):
        self.assertAlmostEqual(_cosine_similarity({}, {}), 0.0)
        self.assertAlmostEqual(_cosine_similarity({"a": 1}, {}), 0.0)


class TestTFIDFRetriever(unittest.TestCase):
    """Test the TF-IDF retriever."""

    def setUp(self):
        self.retriever = TFIDFRetriever()
        self.docs = [
            Document(
                text="Bitcoin wash trading detected on Huobi exchange "
                     "with abnormal volume spikes and manipulation",
                source="article1.md",
                title="Huobi Wash Trading",
            ),
            Document(
                text="Ethereum DeFi protocol security audit reveals "
                     "smart contract vulnerabilities in lending pool",
                source="article2.md",
                title="DeFi Security Audit",
            ),
            Document(
                text="Benford law analysis of trading data shows "
                     "first digit distribution anomalies on Gate.io exchange",
                source="article3.md",
                title="Gate.io Benford Analysis",
            ),
        ]
        self.retriever.add_documents(self.docs)
        self.retriever.build_index()

    def test_relevant_query(self):
        results = self.retriever.query("wash trading Huobi volume manipulation")
        self.assertGreater(len(results), 0)
        # The Huobi article should be the top result
        self.assertEqual(results[0].source, "article1.md")

    def test_benford_query(self):
        results = self.retriever.query(
            "Benford law first digit distribution anomaly exchange"
        )
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].source, "article3.md")

    def test_top_k_limit(self):
        results = self.retriever.query("exchange trading", top_k=2)
        self.assertLessEqual(len(results), 2)

    def test_empty_index(self):
        empty_retriever = TFIDFRetriever()
        results = empty_retriever.query("any query")
        self.assertEqual(results, [])

    def test_scores_are_positive(self):
        results = self.retriever.query("trading volume")
        for doc in results:
            self.assertGreater(doc.score, 0.0)


class TestFrontmatterExtraction(unittest.TestCase):
    """Test YAML front matter parsing."""

    def test_extract_title_double_quotes(self):
        content = '---\ntitle: "My Article Title"\ndate: 2023-01-01\n---\nBody text.'
        title = _extract_frontmatter_title(content)
        self.assertEqual(title, "My Article Title")

    def test_extract_title_single_quotes(self):
        content = "---\ntitle: 'Another Title'\n---\nBody."
        title = _extract_frontmatter_title(content)
        self.assertEqual(title, "Another Title")

    def test_extract_title_no_quotes(self):
        content = "---\ntitle: Plain Title\n---\nBody."
        title = _extract_frontmatter_title(content)
        self.assertEqual(title, "Plain Title")

    def test_no_frontmatter(self):
        content = "Just plain text without front matter."
        title = _extract_frontmatter_title(content)
        self.assertEqual(title, "")

    def test_strip_frontmatter(self):
        content = "---\ntitle: Test\ndate: 2023-01-01\n---\nBody text here."
        stripped = _strip_frontmatter(content)
        self.assertEqual(stripped.strip(), "Body text here.")

    def test_strip_hugo_shortcodes(self):
        text = 'Some text {{< figure src="img.png" >}} more text.'
        cleaned = _strip_hugo_shortcodes(text)
        self.assertEqual(cleaned, "Some text  more text.")


class TestRAGContext(unittest.TestCase):
    """Test RAGContext formatting."""

    def test_empty_context(self):
        ctx = RAGContext()
        self.assertTrue(ctx.is_empty())
        self.assertEqual(ctx.format_context(), "")

    def test_format_with_local_docs(self):
        ctx = RAGContext(
            local_docs=[
                Document(text="Some content", source="file.md", title="Title")
            ]
        )
        formatted = ctx.format_context()
        self.assertIn("knowledge base", formatted)
        self.assertIn("Some content", formatted)
        self.assertIn("Title", formatted)

    def test_format_with_web_results(self):
        ctx = RAGContext(
            web_results=[
                Document(
                    text="Web article content",
                    source="https://example.com",
                    title="Web Article",
                )
            ]
        )
        formatted = ctx.format_context()
        self.assertIn("web search", formatted)
        self.assertIn("Web article content", formatted)

    def test_context_truncation(self):
        long_doc = Document(
            text="x" * 15000, source="big.md", title="Long"
        )
        ctx = RAGContext(local_docs=[long_doc])
        formatted = ctx.format_context()
        self.assertIn("truncated", formatted)


class TestBuildSearchQuery(unittest.TestCase):
    """Test search query construction."""

    def test_basic_query(self):
        query = build_search_query("huobi", "ht-usdt", "2023-06-01", "2023-07-01")
        self.assertIn("Huobi", query)
        self.assertIn("HT/USDT", query)
        self.assertIn("wash trading", query)

    def test_hyphenated_exchange(self):
        query = build_search_query("gate-io", "btc-usdt", "2024-01-01", "2024-02-01")
        self.assertIn("Gate Io", query)


class TestRetrieveRAGContext(unittest.TestCase):
    """Test the full retrieval pipeline."""

    @patch("tools.market_health_reporter.rag_retriever.load_local_knowledge_base")
    @patch("tools.market_health_reporter.rag_retriever._search_web_duckduckgo")
    def test_retrieval_pipeline(self, mock_web, mock_local):
        mock_local.return_value = [
            Document(
                text="Huobi wash trading volume anomaly detected",
                source="post.md",
                title="Huobi Analysis",
            )
        ]
        mock_web.return_value = [
            Document(
                text="News about Huobi trading irregularities",
                source="https://example.com/news",
                title="Huobi News",
            )
        ]

        context = retrieve_rag_context(
            "huobi", "ht-usdt", "2023-06-01", "2023-07-01"
        )

        self.assertFalse(context.is_empty())
        self.assertGreater(len(context.local_docs), 0)
        self.assertGreater(len(context.web_results), 0)

    @patch("tools.market_health_reporter.rag_retriever.load_local_knowledge_base")
    @patch("tools.market_health_reporter.rag_retriever._search_web_duckduckgo")
    def test_web_search_disabled(self, mock_web, mock_local):
        mock_local.return_value = [
            Document(text="Local doc", source="local.md", title="Local")
        ]

        context = retrieve_rag_context(
            "huobi", "ht-usdt", "2023-06-01", "2023-07-01",
            enable_web_search=False,
        )

        mock_web.assert_not_called()
        self.assertEqual(len(context.web_results), 0)

    @patch("tools.market_health_reporter.rag_retriever.load_local_knowledge_base")
    def test_graceful_failure(self, mock_local):
        mock_local.side_effect = Exception("Disk error")

        context = retrieve_rag_context(
            "binance", "btc-usdt", "2024-01-01", "2024-02-01",
            enable_web_search=False,
        )

        # Should not raise, just return empty context
        self.assertIsInstance(context, RAGContext)


if __name__ == "__main__":
    unittest.main()
