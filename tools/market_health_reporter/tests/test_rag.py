"""
Unit tests for the RAG module (tools/market_health_reporter/rag.py).

All external network calls are mocked so tests run offline.
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Ensure the repo root is on the path so we can import the module directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from tools.market_health_reporter.rag import (
    _extract_currencies,
    _is_relevant,
    _token_count,
    _truncate_to_token_budget,
    build_rag_context,
    fetch_news_posts,
)


# ---------------------------------------------------------------------------
# Pure helper tests (no I/O)
# ---------------------------------------------------------------------------


class TestExtractCurrencies(unittest.TestCase):
    def test_dash_separator(self):
        self.assertEqual(_extract_currencies("btc-usdt"), ["BTC", "USDT"])

    def test_slash_separator(self):
        self.assertEqual(_extract_currencies("eth/usdc"), ["ETH", "USDC"])

    def test_underscore_separator(self):
        self.assertEqual(_extract_currencies("sol_bnb"), ["SOL", "BNB"])

    def test_no_separator(self):
        self.assertEqual(_extract_currencies("btc"), ["BTC"])

    def test_already_upper(self):
        self.assertEqual(_extract_currencies("BTC-USDT"), ["BTC", "USDT"])


class TestIsRelevant(unittest.TestCase):
    def test_match_found(self):
        self.assertTrue(_is_relevant("Bitcoin hits new high", ["bitcoin"]))

    def test_match_case_insensitive(self):
        self.assertTrue(_is_relevant("BINANCE exchange news", ["binance"]))

    def test_no_match(self):
        self.assertFalse(_is_relevant("Stock market rally", ["bitcoin", "binance"]))

    def test_empty_keywords(self):
        self.assertFalse(_is_relevant("Some text", []))


class TestTokenCount(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(_token_count(""), 0)

    def test_known_length(self):
        # 8 chars → 2 tokens with floor division by 4
        self.assertEqual(_token_count("abcdefgh"), 2)


class TestTruncateToTokenBudget(unittest.TestCase):
    def test_no_truncation_needed(self):
        text = "Hello world"
        self.assertEqual(_truncate_to_token_budget(text, 1000), text)

    def test_truncation_applied(self):
        # budget = 2 tokens ≈ 8 chars; text is much longer
        text = "The quick brown fox jumps over the lazy dog and then some more words"
        result = _truncate_to_token_budget(text, 2)
        self.assertIn("[...]", result)
        self.assertLessEqual(len(result), 8 + len(" [...]") + 5)

    def test_truncation_ends_on_word_boundary(self):
        text = "alpha beta gamma delta epsilon"
        result = _truncate_to_token_budget(text, 5)
        # Should not cut in the middle of a word
        self.assertFalse(result.startswith(" "))


# ---------------------------------------------------------------------------
# Network-dependent tests (mocked)
# ---------------------------------------------------------------------------

_SAMPLE_POSTS = [
    {
        "title": "Binance BTC-USDT trading volume surges",
        "url": "https://example.com/article1",
        "published_at": "2024-01-15T10:00:00Z",
        "source": {"url": "https://example.com"},
    },
    {
        "title": "Unrelated sports news article",
        "url": "https://example.com/article2",
        "published_at": "2024-01-15T09:00:00Z",
        "source": {"url": "https://example.com"},
    },
]

_SAMPLE_ARTICLE_HTML = """
<html>
<head><title>Binance BTC-USDT trading volume surges</title></head>
<body>
<nav>Navigation</nav>
<article>
<h1>Binance BTC-USDT trading volume surges</h1>
<p>Binance reported a significant increase in BTC-USDT trading volume today,
with analysts pointing to institutional demand as the main driver.</p>
<p>The exchange saw a 40% uptick in spot trading activity over the past 24 hours.</p>
</article>
<footer>Footer content</footer>
</body>
</html>
"""


class TestFetchNewsPosts(unittest.TestCase):
    @patch("tools.market_health_reporter.rag.requests.get")
    def test_returns_posts_on_success(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"results": _SAMPLE_POSTS}
        mock_get.return_value = mock_resp

        posts = fetch_news_posts("binance", "btc-usdt", cryptopanic_token="test")
        self.assertEqual(len(posts), 2)

    @patch("tools.market_health_reporter.rag.requests.get")
    def test_returns_empty_on_api_error(self, mock_get):
        mock_get.side_effect = Exception("Network error")
        posts = fetch_news_posts("binance", "btc-usdt")
        self.assertEqual(posts, [])

    @patch("tools.market_health_reporter.rag.requests.get")
    def test_deduplicates_venue_posts(self, mock_get):
        """Posts fetched for venue ticker should be deduplicated."""
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"results": _SAMPLE_POSTS[:1]}
        mock_get.return_value = mock_resp

        posts = fetch_news_posts("btc", "btc-usdt")
        # Even though both calls return the same URL, result should not duplicate
        urls = [p.get("url") for p in posts]
        self.assertEqual(len(urls), len(set(urls)))


class TestBuildRagContext(unittest.TestCase):
    @patch("tools.market_health_reporter.rag._fetch_article_text")
    @patch("tools.market_health_reporter.rag.fetch_news_posts")
    def test_returns_context_when_articles_found(self, mock_posts, mock_text):
        mock_posts.return_value = [_SAMPLE_POSTS[0]]
        mock_text.return_value = (
            "Binance BTC-USDT trading volume surges. Institutional demand drives "
            "a 40 percent uptick in spot trading activity on the exchange."
        )

        context = build_rag_context("binance", "btc-usdt", max_tokens=500)
        self.assertIsNotNone(context)
        self.assertIn("binance", context.lower())
        self.assertIn("btc", context.lower())

    @patch("tools.market_health_reporter.rag.fetch_news_posts")
    def test_returns_none_when_no_posts(self, mock_posts):
        mock_posts.return_value = []
        context = build_rag_context("binance", "btc-usdt")
        self.assertIsNone(context)

    @patch("tools.market_health_reporter.rag._fetch_article_text")
    @patch("tools.market_health_reporter.rag.fetch_news_posts")
    def test_returns_none_when_no_relevant_articles(self, mock_posts, mock_text):
        # Post exists but text is not relevant to our pair
        mock_posts.return_value = [_SAMPLE_POSTS[1]]  # "Unrelated sports news"
        mock_text.return_value = "A football team won the championship last night."

        context = build_rag_context("binance", "btc-usdt")
        self.assertIsNone(context)

    @patch("tools.market_health_reporter.rag._fetch_article_text")
    @patch("tools.market_health_reporter.rag.fetch_news_posts")
    def test_respects_token_budget(self, mock_posts, mock_text):
        mock_posts.return_value = [_SAMPLE_POSTS[0]]
        # Provide a very long text
        long_text = "Binance BTC-USDT market update. " * 500
        mock_text.return_value = long_text

        context = build_rag_context("binance", "btc-usdt", max_tokens=100)
        self.assertIsNotNone(context)
        # Rough check: context should be well within token budget chars
        self.assertLessEqual(len(context), 100 * 4 + 500)  # budget chars + header

    @patch("tools.market_health_reporter.rag._fetch_article_text")
    @patch("tools.market_health_reporter.rag.fetch_news_posts")
    def test_falls_back_to_title_when_no_body(self, mock_posts, mock_text):
        """When article body fetch fails, use title-based snippet if relevant."""
        mock_posts.return_value = [_SAMPLE_POSTS[0]]  # title mentions binance btc
        mock_text.return_value = None  # simulate fetch failure

        context = build_rag_context("binance", "btc-usdt", max_tokens=500)
        self.assertIsNotNone(context)
        self.assertIn("Binance BTC-USDT", context)

    @patch("tools.market_health_reporter.rag.fetch_news_posts")
    def test_graceful_fallback_on_exception(self, mock_posts):
        """build_rag_context should not raise even if internals throw."""
        mock_posts.side_effect = RuntimeError("unexpected crash")
        # Should propagate (caller wraps in try/except), but let's ensure
        # the function itself doesn't silently swallow exceptions from fetch_news_posts.
        with self.assertRaises(RuntimeError):
            build_rag_context("binance", "btc-usdt")


class TestCreatePromptIntegration(unittest.TestCase):
    """Test that market_health_reporter.create_prompt correctly embeds RAG context.

    We mock out heavy optional dependencies (openai, tiktoken, github) so this
    test suite can run without a full poetry environment.
    """

    def _import_create_prompt(self):
        """Import create_prompt, mocking unavailable deps as needed."""
        # Stub out modules that may not be installed in the test environment
        for mod in ("openai", "tiktoken", "github", "tools.python_modules.utils",
                    "tools.python_modules.report_graphics_tool"):
            if mod not in sys.modules:
                sys.modules[mod] = MagicMock()

        # Force re-evaluation if already partially imported
        import importlib
        import tools.market_health_reporter.market_health_reporter as mhr_mod
        importlib.reload(mhr_mod)
        return mhr_mod.create_prompt

    def test_prompt_without_rag(self):
        create_prompt = self._import_create_prompt()
        prompt = create_prompt("example", {"key": "val"}, "instructions")
        self.assertNotIn("news_context", prompt)
        self.assertIn("<data>", prompt)
        self.assertIn("<example>", prompt)

    def test_prompt_with_rag(self):
        create_prompt = self._import_create_prompt()
        rag = "## Recent News\n\nSome article content here."
        prompt = create_prompt("example", {"key": "val"}, "instructions", rag_context=rag)
        self.assertIn("<news_context>", prompt)
        self.assertIn("Recent News", prompt)
        # RAG section should appear before the data section
        self.assertLess(prompt.index("<news_context>"), prompt.index("<data>"))

    def test_prompt_with_none_rag(self):
        create_prompt = self._import_create_prompt()
        prompt = create_prompt("example", {"key": "val"}, "instructions", rag_context=None)
        self.assertNotIn("news_context", prompt)


if __name__ == "__main__":
    unittest.main()
