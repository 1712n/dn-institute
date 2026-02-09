"""
Tests for the RAG context retrieval module.
"""

import unittest
from unittest.mock import patch, MagicMock
from tools.market_health_reporter.rag_context import (
    clean_text,
    _extract_news_items,
    _extract_web_items,
    _build_search_queries,
    _format_context,
    fetch_relevant_context,
)


class TestCleanText(unittest.TestCase):
    """Tests for HTML cleaning and text sanitization."""

    def test_strips_html_tags(self):
        raw = "<p>Hello <strong>world</strong></p>"
        result = clean_text(raw)
        self.assertEqual(result, "Hello world")

    def test_strips_html_entities(self):
        raw = "Price &amp; volume &#x27;analysis&#x27;"
        result = clean_text(raw)
        self.assertNotIn("&amp;", result)
        self.assertNotIn("&#x27;", result)

    def test_normalizes_whitespace(self):
        raw = "  too   many    spaces   "
        result = clean_text(raw)
        self.assertEqual(result, "too many spaces")

    def test_handles_nested_html(self):
        raw = "<div><p><span>Nested <b>content</b></span></p></div>"
        result = clean_text(raw)
        self.assertEqual(result, "Nested content")

    def test_empty_string(self):
        self.assertEqual(clean_text(""), "")

    def test_plain_text_unchanged(self):
        text = "This is plain text with no HTML"
        self.assertEqual(clean_text(text), text)


class TestExtractNewsItems(unittest.TestCase):
    """Tests for extracting news items from Brave search responses."""

    def test_extracts_valid_news(self):
        response = {
            "news": {
                "results": [
                    {
                        "title": "Huobi Exchange Under Investigation",
                        "description": "Regulators are looking into Huobi exchange for potential wash trading activities.",
                        "url": "https://example.com/article1",
                        "age": "2 days ago",
                        "meta_url": {"hostname": "example.com"},
                    }
                ]
            }
        }
        items = _extract_news_items(response)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "Huobi Exchange Under Investigation")
        self.assertEqual(items[0]["source"], "example.com")

    def test_skips_short_descriptions(self):
        response = {
            "news": {
                "results": [
                    {
                        "title": "Test",
                        "description": "Too short",
                        "url": "https://example.com/short",
                    }
                ]
            }
        }
        items = _extract_news_items(response)
        self.assertEqual(len(items), 0)

    def test_handles_empty_response(self):
        items = _extract_news_items({})
        self.assertEqual(items, [])

    def test_cleans_html_in_descriptions(self):
        response = {
            "news": {
                "results": [
                    {
                        "title": "<strong>Bold Title</strong>",
                        "description": "A description with <em>HTML tags</em> that should be cleaned properly.",
                        "url": "https://example.com/html",
                        "meta_url": {"hostname": "example.com"},
                    }
                ]
            }
        }
        items = _extract_news_items(response)
        self.assertNotIn("<strong>", items[0]["title"])
        self.assertNotIn("<em>", items[0]["description"])


class TestExtractWebItems(unittest.TestCase):
    """Tests for extracting web results from Brave search responses."""

    def test_extracts_valid_web_items(self):
        response = {
            "web": {
                "results": [
                    {
                        "title": "Crypto Exchange Analysis",
                        "description": "Comprehensive analysis of trading patterns on major exchanges including wash trading detection.",
                        "url": "https://example.com/analysis",
                    }
                ]
            }
        }
        items = _extract_web_items(response)
        self.assertEqual(len(items), 1)
        self.assertIn("Crypto Exchange Analysis", items[0]["title"])

    def test_skips_short_descriptions(self):
        response = {
            "web": {
                "results": [
                    {
                        "title": "Short",
                        "description": "Tiny desc",
                        "url": "https://example.com/s",
                    }
                ]
            }
        }
        items = _extract_web_items(response)
        self.assertEqual(len(items), 0)


class TestBuildSearchQueries(unittest.TestCase):
    """Tests for search query construction."""

    def test_builds_multiple_queries(self):
        queries = _build_search_queries("huobi", "btc-usdt", "2023-07-01", "2023-07-15")
        self.assertEqual(len(queries), 3)

    def test_extracts_base_token(self):
        queries = _build_search_queries("binance", "eth-usdt", "2023-01-01", "2023-01-31")
        # First query should contain the base token
        self.assertIn("ETH", queries[0])

    def test_includes_exchange_name(self):
        queries = _build_search_queries("huobi", "btc-usdt", "2023-07-01", "2023-07-15")
        for q in queries:
            self.assertIn("huobi", q.lower())


class TestFormatContext(unittest.TestCase):
    """Tests for formatting context items into prompt text."""

    def test_formats_news_items(self):
        news = [
            {
                "title": "Test News",
                "url": "https://example.com/news",
                "source": "example.com",
                "age": "1 day ago",
                "description": "This is a test news article about exchange manipulation.",
            }
        ]
        result = _format_context(news, [])
        self.assertIn("Test News", result)
        self.assertIn("example.com", result)

    def test_respects_max_items(self):
        news = [
            {
                "title": f"News {i}",
                "url": f"https://example.com/{i}",
                "source": "example.com",
                "age": "1 day ago",
                "description": f"Description for article {i} with enough length to pass.",
            }
            for i in range(10)
        ]
        result = _format_context(news, [], max_items=3)
        # Should only contain 3 items
        self.assertEqual(result.count("example.com"), 3)

    def test_combines_news_and_web(self):
        news = [
            {
                "title": "News Item",
                "url": "https://news.com/1",
                "source": "news.com",
                "age": "2 days ago",
                "description": "News description with enough content.",
            }
        ]
        web = [
            {
                "title": "Web Item",
                "url": "https://web.com/1",
                "description": "Web description with enough content.",
            }
        ]
        result = _format_context(news, web, max_items=5)
        self.assertIn("News Item", result)
        self.assertIn("Web Item", result)


class TestFetchRelevantContext(unittest.TestCase):
    """Integration tests for the full context retrieval pipeline."""

    @patch("tools.market_health_reporter.rag_context._brave_search")
    def test_returns_context_when_results_found(self, mock_search):
        mock_search.return_value = {
            "news": {
                "results": [
                    {
                        "title": "Huobi Wash Trading Report",
                        "description": "A detailed report on suspicious trading patterns detected on Huobi exchange during July 2023.",
                        "url": "https://example.com/report",
                        "age": "3 days ago",
                        "meta_url": {"hostname": "example.com"},
                    }
                ]
            },
            "web": {"results": []},
        }
        result = fetch_relevant_context(
            exchange="huobi",
            pair="btc-usdt",
            start="2023-07-01",
            end="2023-07-15",
            brave_api_key="test-key",
        )
        self.assertIsNotNone(result)
        self.assertIn("Huobi Wash Trading Report", result)

    @patch("tools.market_health_reporter.rag_context._brave_search")
    def test_returns_none_when_no_results(self, mock_search):
        mock_search.return_value = {"news": {"results": []}, "web": {"results": []}}
        result = fetch_relevant_context(
            exchange="unknown_exchange",
            pair="btc-usdt",
            start="2023-07-01",
            end="2023-07-15",
            brave_api_key="test-key",
        )
        self.assertIsNone(result)

    @patch("tools.market_health_reporter.rag_context._brave_search")
    def test_deduplicates_urls(self, mock_search):
        mock_search.return_value = {
            "news": {
                "results": [
                    {
                        "title": "Same Article",
                        "description": "This article appears in multiple search results with the same URL.",
                        "url": "https://example.com/duplicate",
                        "age": "1 day ago",
                        "meta_url": {"hostname": "example.com"},
                    }
                ]
            },
            "web": {
                "results": [
                    {
                        "title": "Same Article Web",
                        "description": "This article appears in multiple search results with the same URL.",
                        "url": "https://example.com/duplicate",
                    }
                ]
            },
        }
        result = fetch_relevant_context(
            exchange="huobi",
            pair="btc-usdt",
            start="2023-07-01",
            end="2023-07-15",
            brave_api_key="test-key",
        )
        # The duplicate URL should only appear once
        self.assertEqual(result.count("https://example.com/duplicate"), 1)

    @patch("tools.market_health_reporter.rag_context._brave_search")
    def test_handles_search_failure_gracefully(self, mock_search):
        mock_search.side_effect = Exception("API Error")
        result = fetch_relevant_context(
            exchange="huobi",
            pair="btc-usdt",
            start="2023-07-01",
            end="2023-07-15",
            brave_api_key="test-key",
        )
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
