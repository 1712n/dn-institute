"""
Tests for the RAG module of the Market Health Reporter.
"""

import unittest
from unittest.mock import patch, MagicMock

from tools.market_health_reporter.rag import (
    build_search_queries,
    search_web,
    extract_article_content,
    deduplicate_results,
    retrieve_context,
    format_rag_context,
    MAX_CONTENT_LENGTH,
    MAX_TOTAL_CONTEXT_LENGTH,
)


class TestBuildSearchQueries(unittest.TestCase):
    """Tests for building search queries from market parameters."""

    def test_basic_query_generation(self):
        queries = build_search_queries("binance", "btc-usdt", "2024-01-01", "2024-01-07")
        self.assertIsInstance(queries, list)
        self.assertTrue(len(queries) > 0)

    def test_queries_contain_exchange_name(self):
        queries = build_search_queries("binance", "btc-usdt", "2024-01-01", "2024-01-07")
        has_exchange = any("Binance" in q for q in queries)
        self.assertTrue(has_exchange, "At least one query should contain the exchange name")

    def test_queries_contain_token(self):
        queries = build_search_queries("binance", "eth-usdt", "2024-01-01", "2024-01-07")
        has_token = any("ETH" in q for q in queries)
        self.assertTrue(has_token, "At least one query should contain the token symbol")

    def test_queries_contain_dates(self):
        queries = build_search_queries("binance", "btc-usdt", "2024-01-01", "2024-01-07")
        has_start = any("2024-01-01" in q for q in queries)
        self.assertTrue(has_start, "At least one query should contain the start date")


class TestSearchWeb(unittest.TestCase):
    """Tests for web search functionality."""

    @patch("tools.market_health_reporter.rag.ddg")
    def test_successful_search(self, mock_ddg):
        mock_ddg.return_value = [
            {"title": "Test", "href": "https://example.com", "body": "snippet"}
        ]
        results = search_web("test query")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Test")

    @patch("tools.market_health_reporter.rag.ddg")
    def test_search_returns_empty_on_none(self, mock_ddg):
        mock_ddg.return_value = None
        results = search_web("test query")
        self.assertEqual(results, [])

    @patch("tools.market_health_reporter.rag.ddg")
    def test_search_handles_exception(self, mock_ddg):
        mock_ddg.side_effect = Exception("Network error")
        results = search_web("test query")
        self.assertEqual(results, [])


class TestExtractArticleContent(unittest.TestCase):
    """Tests for article content extraction."""

    @patch("tools.market_health_reporter.rag.requests.get")
    def test_extracts_article_content(self, mock_get):
        html = """
        <html><body>
        <article><p>Important market analysis content here.</p></article>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        content = extract_article_content("https://example.com/article")
        self.assertIn("Important market analysis content", content)

    @patch("tools.market_health_reporter.rag.requests.get")
    def test_removes_script_and_style(self, mock_get):
        html = """
        <html><body>
        <script>var x = 1;</script>
        <style>.foo { color: red; }</style>
        <article><p>Clean content</p></article>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        content = extract_article_content("https://example.com")
        self.assertNotIn("var x", content)
        self.assertNotIn("color: red", content)
        self.assertIn("Clean content", content)

    @patch("tools.market_health_reporter.rag.requests.get")
    def test_truncates_long_content(self, mock_get):
        long_text = "A" * (MAX_CONTENT_LENGTH + 500)
        html = f"<html><body><article><p>{long_text}</p></article></body></html>"
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        content = extract_article_content("https://example.com")
        self.assertLessEqual(len(content), MAX_CONTENT_LENGTH)

    @patch("tools.market_health_reporter.rag.requests.get")
    def test_handles_request_error(self, mock_get):
        mock_get.side_effect = Exception("Timeout")
        content = extract_article_content("https://example.com")
        self.assertEqual(content, "")


class TestDeduplicateResults(unittest.TestCase):
    """Tests for result deduplication."""

    def test_removes_duplicates(self):
        results = [
            {"href": "https://a.com", "title": "A"},
            {"href": "https://b.com", "title": "B"},
            {"href": "https://a.com", "title": "A duplicate"},
        ]
        unique = deduplicate_results(results)
        self.assertEqual(len(unique), 2)

    def test_preserves_order(self):
        results = [
            {"href": "https://a.com", "title": "First"},
            {"href": "https://b.com", "title": "Second"},
        ]
        unique = deduplicate_results(results)
        self.assertEqual(unique[0]["title"], "First")

    def test_empty_list(self):
        self.assertEqual(deduplicate_results([]), [])


class TestRetrieveContext(unittest.TestCase):
    """Tests for the main RAG retrieval function."""

    @patch("tools.market_health_reporter.rag.extract_article_content")
    @patch("tools.market_health_reporter.rag.search_web")
    def test_retrieves_and_combines_context(self, mock_search, mock_extract):
        mock_search.return_value = [
            {"href": "https://example.com/1", "title": "Article 1", "body": "Snippet 1"},
            {"href": "https://example.com/2", "title": "Article 2", "body": "Snippet 2"},
        ]
        mock_extract.side_effect = ["Full content 1", "Full content 2"]

        context = retrieve_context("binance", "btc-usdt", "2024-01-01", "2024-01-07")
        self.assertIn("Article 1", context)
        self.assertIn("Article 2", context)
        self.assertIn("Full content 1", context)

    @patch("tools.market_health_reporter.rag.extract_article_content")
    @patch("tools.market_health_reporter.rag.search_web")
    def test_falls_back_to_snippet(self, mock_search, mock_extract):
        mock_search.return_value = [
            {"href": "https://example.com/1", "title": "Article 1", "body": "Fallback snippet"},
        ]
        mock_extract.return_value = ""  # Failed to extract

        context = retrieve_context("binance", "btc-usdt", "2024-01-01", "2024-01-07")
        self.assertIn("Fallback snippet", context)

    @patch("tools.market_health_reporter.rag.search_web")
    def test_returns_empty_when_no_results(self, mock_search):
        mock_search.return_value = []

        context = retrieve_context("binance", "btc-usdt", "2024-01-01", "2024-01-07")
        self.assertEqual(context, "")


class TestFormatRagContext(unittest.TestCase):
    """Tests for RAG context formatting."""

    def test_wraps_in_xml_tags(self):
        formatted = format_rag_context("Some context here")
        self.assertIn("<external_context>", formatted)
        self.assertIn("</external_context>", formatted)
        self.assertIn("Some context here", formatted)

    def test_empty_context_returns_empty(self):
        self.assertEqual(format_rag_context(""), "")

    def test_includes_instructions(self):
        formatted = format_rag_context("Content")
        self.assertIn("enrich your analysis", formatted)


class TestCreatePromptWithRAG(unittest.TestCase):
    """Tests for the updated create_prompt function with RAG context."""

    @classmethod
    def setUpClass(cls):
        """Mock heavy dependencies so create_prompt can be imported."""
        import sys
        cls._mock_modules = {}
        for mod in ['openai', 'tiktoken', 'github', 'tools.python_modules.report_graphics_tool']:
            if mod not in sys.modules:
                cls._mock_modules[mod] = sys.modules[mod] = MagicMock()

    @classmethod
    def tearDownClass(cls):
        import sys
        for mod in cls._mock_modules:
            sys.modules.pop(mod, None)

    def test_prompt_includes_rag_context(self):
        from tools.market_health_reporter.market_health_reporter import create_prompt
        prompt = create_prompt("example", {"key": "val"}, "instructions",
                               rag_context="<external_context>Extra info</external_context>")
        self.assertIn("<external_context>", prompt)
        self.assertIn("Extra info", prompt)

    def test_prompt_works_without_rag(self):
        from tools.market_health_reporter.market_health_reporter import create_prompt
        prompt = create_prompt("example", {"key": "val"}, "instructions")
        self.assertIn("example", prompt)
        self.assertIn("instructions", prompt)
        self.assertNotIn("external_context", prompt)


if __name__ == "__main__":
    unittest.main()
