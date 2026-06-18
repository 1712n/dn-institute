import pytest
from unittest.mock import patch, MagicMock
from tools.market_health_reporter.news_retriever import (
    build_search_queries,
    fetch_article_text,
    truncate_to_tokens,
    deduplicate_results,
    format_context,
    retrieve_news_context,
    search_news,
    search_web,
)
from tiktoken import encoding_for_model


class TestBuildSearchQueries:
    def test_basic_exchange_and_pair(self):
        queries = build_search_queries("binance", "BTC/USDT")
        assert len(queries) == 4
        assert any("binance" in q.lower() for q in queries)
        assert any("BTC" in q for q in queries)

    def test_exchange_alias_huobi(self):
        queries = build_search_queries("htx", "HT/USDT")
        assert any("huobi" in q.lower() for q in queries)

    def test_exchange_alias_okex(self):
        queries = build_search_queries("okx", "ETH/USDT")
        assert any("okex" in q.lower() for q in queries)

    def test_pair_without_slash(self):
        queries = build_search_queries("binance", "BTCUSDT")
        assert any("BTCUSDT" in q for q in queries)

    def test_unknown_exchange_uses_original_name(self):
        queries = build_search_queries("kraken", "ETH/USD")
        assert any("kraken" in q.lower() for q in queries)


class TestFetchArticleText:
    @patch("tools.market_health_reporter.news_retriever.requests.get")
    def test_extracts_text_from_html(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.text = """
        <html><body>
            <nav>Menu</nav>
            <article><p>Exchange was fined for wash trading.</p></article>
            <footer>Copyright</footer>
        </body></html>
        """
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        text = fetch_article_text("https://example.com/article")
        assert text is not None
        assert "wash trading" in text
        assert "Menu" not in text
        assert "Copyright" not in text

    @patch("tools.market_health_reporter.news_retriever.requests.get")
    def test_removes_script_and_style(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.text = """
        <html><body>
            <script>alert('xss')</script>
            <style>.hidden{display:none}</style>
            <p>Relevant content here.</p>
        </body></html>
        """
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        text = fetch_article_text("https://example.com")
        assert "alert" not in text
        assert "hidden" not in text
        assert "Relevant content" in text

    @patch("tools.market_health_reporter.news_retriever.requests.get")
    def test_returns_none_on_http_error(self, mock_get):
        mock_get.side_effect = Exception("Connection refused")
        result = fetch_article_text("https://unreachable.example.com")
        assert result is None

    @patch("tools.market_health_reporter.news_retriever.requests.get")
    def test_returns_none_on_timeout(self, mock_get):
        mock_get.side_effect = TimeoutError()
        result = fetch_article_text("https://slow.example.com")
        assert result is None


class TestTruncateToTokens:
    def test_short_text_unchanged(self):
        enc = encoding_for_model("gpt-4")
        text = "Short text."
        result = truncate_to_tokens(text, 100, enc)
        assert result == text

    def test_long_text_truncated(self):
        enc = encoding_for_model("gpt-4")
        text = "word " * 500
        result = truncate_to_tokens(text, 50, enc)
        tokens = enc.encode(result)
        assert len(tokens) <= 50


class TestDeduplicateResults:
    def test_removes_duplicate_urls(self):
        results = [
            {"url": "https://a.com", "title": "First"},
            {"url": "https://a.com", "title": "Duplicate"},
            {"url": "https://b.com", "title": "Second"},
        ]
        unique = deduplicate_results(results)
        assert len(unique) == 2
        assert unique[0]["title"] == "First"
        assert unique[1]["title"] == "Second"

    def test_handles_href_field(self):
        results = [
            {"href": "https://a.com", "title": "Web result"},
            {"href": "https://a.com", "title": "Duplicate web"},
        ]
        unique = deduplicate_results(results)
        assert len(unique) == 1

    def test_skips_results_without_url(self):
        results = [
            {"title": "No URL"},
            {"url": "https://a.com", "title": "Has URL"},
        ]
        unique = deduplicate_results(results)
        assert len(unique) == 1
        assert unique[0]["title"] == "Has URL"

    def test_empty_input(self):
        assert deduplicate_results([]) == []


class TestFormatContext:
    def test_formats_articles_as_xml(self):
        articles = [
            {"title": "Test Article", "date": "2024-01-01", "url": "https://example.com", "content": "Article body."},
        ]
        result = format_context(articles)
        assert "<external_context>" in result
        assert "</external_context>" in result
        assert '<source index="1">' in result
        assert "<title>Test Article</title>" in result
        assert "Article body." in result

    def test_multiple_articles_numbered(self):
        articles = [
            {"title": f"Article {i}", "content": f"Body {i}"} for i in range(3)
        ]
        result = format_context(articles)
        assert '<source index="1">' in result
        assert '<source index="2">' in result
        assert '<source index="3">' in result

    def test_empty_articles_returns_empty_string(self):
        assert format_context([]) == ""

    def test_handles_missing_fields(self):
        articles = [{"content": "Just content"}]
        result = format_context(articles)
        assert "<title></title>" in result
        assert "Just content" in result


class TestSearchNews:
    @patch("tools.market_health_reporter.news_retriever.DDGS")
    def test_returns_results(self, mock_ddgs_class):
        mock_ddgs = MagicMock()
        mock_ddgs.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs.__exit__ = MagicMock(return_value=False)
        mock_ddgs.news.return_value = [
            {"title": "Breaking news", "url": "https://news.com/1", "body": "Content"},
        ]
        mock_ddgs_class.return_value = mock_ddgs

        results = search_news("test query", max_results=5)
        assert len(results) == 1
        assert results[0]["title"] == "Breaking news"

    @patch("tools.market_health_reporter.news_retriever.DDGS")
    def test_returns_empty_on_error(self, mock_ddgs_class):
        mock_ddgs_class.side_effect = Exception("API error")
        results = search_news("failing query")
        assert results == []


class TestSearchWeb:
    @patch("tools.market_health_reporter.news_retriever.DDGS")
    def test_returns_results(self, mock_ddgs_class):
        mock_ddgs = MagicMock()
        mock_ddgs.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs.__exit__ = MagicMock(return_value=False)
        mock_ddgs.text.return_value = [
            {"title": "Web result", "href": "https://web.com/1", "body": "Content"},
        ]
        mock_ddgs_class.return_value = mock_ddgs

        results = search_web("test query", max_results=5)
        assert len(results) == 1
        assert results[0]["title"] == "Web result"

    @patch("tools.market_health_reporter.news_retriever.DDGS")
    def test_returns_empty_on_error(self, mock_ddgs_class):
        mock_ddgs_class.side_effect = Exception("Network error")
        results = search_web("failing query")
        assert results == []


class TestRetrieveNewsContext:
    @patch("tools.market_health_reporter.news_retriever.fetch_article_text")
    @patch("tools.market_health_reporter.news_retriever.search_web")
    @patch("tools.market_health_reporter.news_retriever.search_news")
    def test_full_pipeline(self, mock_news, mock_web, mock_fetch):
        mock_news.return_value = [
            {"title": "News 1", "url": "https://news.com/1", "date": "2024-01-01", "body": "Summary"},
        ]
        mock_web.return_value = [
            {"title": "Web 1", "href": "https://web.com/1", "body": "Web summary"},
        ]
        mock_fetch.return_value = "Full article content about exchange manipulation."

        result = retrieve_news_context("huobi", "HT/USDT")
        assert "<external_context>" in result
        assert "News 1" in result
        assert "Full article content" in result

    @patch("tools.market_health_reporter.news_retriever.fetch_article_text")
    @patch("tools.market_health_reporter.news_retriever.search_web")
    @patch("tools.market_health_reporter.news_retriever.search_news")
    def test_falls_back_to_snippet_when_fetch_fails(self, mock_news, mock_web, mock_fetch):
        mock_news.return_value = [
            {"title": "News", "url": "https://news.com/1", "body": "Snippet only", "date": "2024-01-01"},
        ]
        mock_web.return_value = []
        mock_fetch.return_value = None  # fetch fails

        result = retrieve_news_context("binance", "BTC/USDT")
        assert "Snippet only" in result

    @patch("tools.market_health_reporter.news_retriever.search_web")
    @patch("tools.market_health_reporter.news_retriever.search_news")
    def test_returns_empty_when_no_results(self, mock_news, mock_web):
        mock_news.return_value = []
        mock_web.return_value = []

        result = retrieve_news_context("unknown_exchange", "XYZ/USD")
        assert result == ""

    @patch("tools.market_health_reporter.news_retriever.fetch_article_text")
    @patch("tools.market_health_reporter.news_retriever.search_web")
    @patch("tools.market_health_reporter.news_retriever.search_news")
    def test_deduplicates_across_searches(self, mock_news, mock_web, mock_fetch):
        shared_result = {"title": "Same article", "url": "https://same.com/1", "body": "Content", "date": "2024-01-01"}
        mock_news.return_value = [shared_result]
        mock_web.return_value = [shared_result]
        mock_fetch.return_value = "Full content"

        result = retrieve_news_context("binance", "ETH/USDT")
        assert result.count('<source index="1">') == 1
        assert '<source index="2">' not in result

    @patch("tools.market_health_reporter.news_retriever.fetch_article_text")
    @patch("tools.market_health_reporter.news_retriever.search_web")
    @patch("tools.market_health_reporter.news_retriever.search_news")
    def test_respects_token_budget(self, mock_news, mock_web, mock_fetch):
        # Generate many results
        mock_news.return_value = [
            {"title": f"Article {i}", "url": f"https://news.com/{i}", "body": f"Body {i}", "date": "2024-01-01"}
            for i in range(50)
        ]
        mock_web.return_value = []
        mock_fetch.return_value = "x " * 5000  # large article

        result = retrieve_news_context("exchange", "TOKEN/USD", max_context_tokens=5000)
        enc = encoding_for_model("gpt-4")
        token_count = len(enc.encode(result))
        # Should be within budget (with some overhead for XML tags)
        assert token_count < 8000  # generous buffer for XML formatting


class TestCreatePromptIntegration:
    """Test the create_prompt function's news_context integration.

    These tests import create_prompt which requires openai and other deps.
    We mock them at the module level to avoid ImportError in CI.
    """

    @pytest.fixture(autouse=True)
    def _mock_deps(self):
        """Mock heavy dependencies that may not be installed in test env."""
        import sys
        mocked = {}
        for mod in [
            "openai", "github", "github.Github",
            "matplotlib", "matplotlib.pyplot", "matplotlib.ticker",
            "matplotlib.dates", "pandas",
        ]:
            if mod not in sys.modules:
                mocked[mod] = sys.modules[mod] = MagicMock()
        yield
        for mod in mocked:
            sys.modules.pop(mod, None)

    def test_prompt_includes_news_context(self):
        from tools.market_health_reporter.market_health_reporter import create_prompt

        result = create_prompt(
            article_example="Example article",
            data={"metric": "value"},
            human_prompt_content="Analyze this data",
            news_context="<external_context><source>News</source></external_context>",
        )
        assert "<external_context>" in result
        assert "<example>" in result
        assert "<data>" in result
        assert "corroborate" in result

    def test_prompt_without_news_context(self):
        from tools.market_health_reporter.market_health_reporter import create_prompt

        result = create_prompt(
            article_example="Example",
            data={"metric": "value"},
            human_prompt_content="Analyze",
        )
        assert "<external_context>" not in result
        assert "<example>" in result

    def test_prompt_with_empty_news_context(self):
        from tools.market_health_reporter.market_health_reporter import create_prompt

        result = create_prompt(
            article_example="Example",
            data={"metric": "value"},
            human_prompt_content="Analyze",
            news_context="",
        )
        assert "corroborate" not in result
