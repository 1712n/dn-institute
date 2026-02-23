"""
Tests for the RAG context retrieval module.

Tests cover:
- HTML cleaning and sanitization
- Hugo shortcode stripping
- TF-IDF similarity computation
- Search query building
- Local wiki article loading
- Context formatting and character budget enforcement
- Full retrieval pipeline (with mocked web search)
"""

import os
import tempfile
from unittest.mock import patch, MagicMock

from tools.market_health_reporter.rag_context import (
    clean_html,
    strip_hugo_shortcodes,
    compute_tfidf_similarity,
    build_search_queries,
    load_local_wiki_articles,
    retrieve_rag_context,
    fetch_web_results,
)


class TestCleanHtml:
    """Tests for HTML cleaning and sanitization."""

    def test_strips_html_tags(self):
        html = "<p>Hello <b>world</b></p>"
        result = clean_html(html)
        assert "<p>" not in result
        assert "<b>" not in result
        assert "Hello" in result
        assert "world" in result

    def test_removes_script_and_style(self):
        html = "<html><script>alert('xss')</script><style>.x{}</style><p>Content</p></html>"
        result = clean_html(html)
        assert "alert" not in result
        assert "Content" in result

    def test_removes_nav_footer_header(self):
        html = "<nav>Menu</nav><main>Article body</main><footer>Copyright</footer>"
        result = clean_html(html)
        assert "Menu" not in result
        assert "Copyright" not in result
        assert "Article body" in result

    def test_normalizes_whitespace(self):
        html = "<p>Line 1</p>\n\n\n\n\n<p>Line 2</p>"
        result = clean_html(html)
        assert "\n\n\n" not in result

    def test_empty_input(self):
        assert clean_html("") == ""
        assert clean_html(None) == ""

    def test_sanitizes_html_entities(self):
        html = "<p>&amp; &lt; &gt;</p>"
        result = clean_html(html)
        assert "<" not in result or "&lt;" not in result


class TestStripHugoShortcodes:
    """Tests for Hugo shortcode removal."""

    def test_strips_figure_shortcode(self):
        text = 'Some text {{< figure src="image.png" alt="desc" >}} more text'
        result = strip_hugo_shortcodes(text)
        assert "{{<" not in result
        assert "Some text" in result
        assert "more text" in result

    def test_strips_multiple_shortcodes(self):
        text = '{{< figure src="a.png" >}} between {{< figure src="b.png" >}}'
        result = strip_hugo_shortcodes(text)
        assert "{{<" not in result
        assert "between" in result

    def test_preserves_normal_text(self):
        text = "Normal markdown text with **bold** and [links](url)"
        assert strip_hugo_shortcodes(text) == text


class TestTfidfSimilarity:
    """Tests for TF-IDF relevance scoring."""

    def test_identical_text_high_similarity(self):
        query = "cryptocurrency wash trading manipulation"
        docs = ["cryptocurrency wash trading manipulation"]
        scores = compute_tfidf_similarity(query, docs)
        assert len(scores) == 1
        assert scores[0] > 0.5

    def test_unrelated_text_low_similarity(self):
        query = "cryptocurrency wash trading manipulation"
        docs = ["weather forecast for tomorrow sunny skies"]
        scores = compute_tfidf_similarity(query, docs)
        assert len(scores) == 1
        assert scores[0] < 0.1

    def test_ranking_order(self):
        query = "huobi exchange wash trading volume"
        docs = [
            "football game results season championship",
            "huobi exchange suspected wash trading detected in volume",
            "cryptocurrency trading platform review",
        ]
        scores = compute_tfidf_similarity(query, docs)
        assert scores[1] > scores[0]  # Huobi doc should rank higher than football
        assert scores[1] > scores[2]  # Huobi doc should rank higher than generic crypto

    def test_empty_documents(self):
        scores = compute_tfidf_similarity("query", [])
        assert scores == []

    def test_empty_query(self):
        scores = compute_tfidf_similarity("", ["some document"])
        assert len(scores) == 1


class TestBuildSearchQueries:
    """Tests for search query construction."""

    def test_returns_three_queries(self):
        queries = build_search_queries("huobi", "ht-usdt", "2023-08-01", "2023-08-14")
        assert len(queries) == 3

    def test_queries_contain_exchange_name(self):
        queries = build_search_queries("huobi", "ht-usdt", "2023-08-01", "2023-08-14")
        assert all("Huobi" in q or "huobi" in q.lower() for q in queries)

    def test_queries_contain_relevant_terms(self):
        queries = build_search_queries("binance", "btc-usdt", "2023-01-01", "2023-01-31")
        combined = " ".join(queries).lower()
        assert "manipulation" in combined or "wash trading" in combined
        assert "binance" in combined

    def test_handles_hyphenated_exchange(self):
        queries = build_search_queries("gate-io", "btc-usdt", "2023-01-01", "2023-01-31")
        combined = " ".join(queries)
        assert "Gate Io" in combined or "gate-io" in combined.lower()


class TestLoadLocalWikiArticles:
    """Tests for local wiki article loading."""

    def test_loads_matching_articles(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test article
            article_dir = os.path.join(tmpdir, "2023-08-14-huobi")
            os.makedirs(article_dir)
            with open(os.path.join(article_dir, "index.md"), "w") as f:
                f.write(
                    "---\n"
                    "title: 'Wash Trading on Huobi'\n"
                    "entities:\n"
                    "  - Huobi\n"
                    "  - HT\n"
                    "---\n\n"
                    "## Summary\n\nHuobi shows manipulation.\n"
                )

            with patch("tools.market_health_reporter.rag_context.WIKI_POSTS_DIR", tmpdir):
                articles = load_local_wiki_articles("huobi")

            assert len(articles) == 1
            assert "Huobi" in articles[0]["title"]
            assert "manipulation" in articles[0]["content"]

    def test_skips_non_matching_articles(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            article_dir = os.path.join(tmpdir, "2023-01-01-binance")
            os.makedirs(article_dir)
            with open(os.path.join(article_dir, "index.md"), "w") as f:
                f.write(
                    "---\n"
                    "title: 'Analysis of Binance'\n"
                    "entities:\n"
                    "  - Binance\n"
                    "---\n\n"
                    "Binance report.\n"
                )

            with patch("tools.market_health_reporter.rag_context.WIKI_POSTS_DIR", tmpdir):
                articles = load_local_wiki_articles("huobi")

            assert len(articles) == 0

    def test_handles_missing_directory(self):
        with patch(
            "tools.market_health_reporter.rag_context.WIKI_POSTS_DIR",
            "/nonexistent/path",
        ):
            articles = load_local_wiki_articles("huobi")
        assert articles == []

    def test_strips_hugo_shortcodes_from_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            article_dir = os.path.join(tmpdir, "2023-08-14-huobi")
            os.makedirs(article_dir)
            with open(os.path.join(article_dir, "index.md"), "w") as f:
                f.write(
                    "---\n"
                    "title: 'Huobi Analysis'\n"
                    "entities:\n"
                    "  - Huobi\n"
                    "---\n\n"
                    '{{< figure src="chart.png" >}}\n'
                    "Real content here.\n"
                )

            with patch("tools.market_health_reporter.rag_context.WIKI_POSTS_DIR", tmpdir):
                articles = load_local_wiki_articles("huobi")

            assert len(articles) == 1
            assert "{{<" not in articles[0]["content"]
            assert "Real content here" in articles[0]["content"]


class TestFetchWebResults:
    """Tests for web search result fetching."""

    @patch("tools.market_health_reporter.rag_context.DDGS")
    def test_deduplicates_results(self, mock_ddgs_class):
        mock_instance = MagicMock()
        mock_ddgs_class.return_value = mock_instance
        # Return same URL from different queries
        mock_instance.text.return_value = [
            {"title": "Article", "href": "https://example.com/1", "body": "Content"},
        ]

        results = fetch_web_results(["query1", "query2"])
        # Should be deduplicated to 1 result
        assert len(results) == 1

    @patch("tools.market_health_reporter.rag_context.DDGS")
    def test_handles_search_failure(self, mock_ddgs_class):
        mock_instance = MagicMock()
        mock_ddgs_class.return_value = mock_instance
        mock_instance.text.side_effect = Exception("Rate limited")

        results = fetch_web_results(["query"])
        assert results == []

    @patch("tools.market_health_reporter.rag_context.DDGS")
    def test_cleans_html_in_snippets(self, mock_ddgs_class):
        mock_instance = MagicMock()
        mock_ddgs_class.return_value = mock_instance
        mock_instance.text.return_value = [
            {
                "title": "Test",
                "href": "https://example.com",
                "body": "<b>Bold</b> <script>bad</script> text",
            },
        ]

        results = fetch_web_results(["query"])
        assert len(results) == 1
        assert "<b>" not in results[0]["snippet"]
        assert "<script>" not in results[0]["snippet"]


class TestRetrieveRagContext:
    """Tests for the full RAG retrieval pipeline."""

    @patch("tools.market_health_reporter.rag_context.fetch_url_content")
    @patch("tools.market_health_reporter.rag_context.fetch_web_results")
    @patch("tools.market_health_reporter.rag_context.load_local_wiki_articles")
    def test_returns_formatted_context(self, mock_wiki, mock_web, mock_fetch_url):
        mock_wiki.return_value = []
        mock_web.return_value = [
            {
                "title": "Huobi Wash Trading Report",
                "url": "https://example.com/huobi",
                "snippet": "Huobi exchange detected wash trading patterns.",
            }
        ]
        mock_fetch_url.return_value = "Huobi exchange detected wash trading patterns in multiple pairs."

        context = retrieve_rag_context("huobi", "ht-usdt", "2023-08-01", "2023-08-14")

        assert "Huobi" in context
        assert "wash trading" in context
        assert '<source type="WEB"' in context

    @patch("tools.market_health_reporter.rag_context.fetch_web_results")
    @patch("tools.market_health_reporter.rag_context.load_local_wiki_articles")
    def test_returns_empty_when_no_results(self, mock_wiki, mock_web):
        mock_wiki.return_value = []
        mock_web.return_value = []

        context = retrieve_rag_context("unknown-exchange", "x-y", "2023-01-01", "2023-01-31")
        assert context == ""

    @patch("tools.market_health_reporter.rag_context.fetch_url_content")
    @patch("tools.market_health_reporter.rag_context.fetch_web_results")
    @patch("tools.market_health_reporter.rag_context.load_local_wiki_articles")
    def test_respects_character_budget(self, mock_wiki, mock_web, mock_fetch_url):
        mock_wiki.return_value = []
        # Return many results
        mock_web.return_value = [
            {
                "title": f"Article {i}",
                "url": f"https://example.com/{i}",
                "snippet": "x" * 5000,
            }
            for i in range(20)
        ]
        mock_fetch_url.return_value = "x" * 5000

        max_chars = 3000
        context = retrieve_rag_context(
            "huobi", "ht-usdt", "2023-08-01", "2023-08-14",
            max_context_chars=max_chars,
        )
        assert len(context) <= max_chars + 500  # Allow some overhead for XML tags

    @patch("tools.market_health_reporter.rag_context.fetch_web_results")
    @patch("tools.market_health_reporter.rag_context.load_local_wiki_articles")
    def test_web_search_disabled(self, mock_wiki, mock_web):
        mock_wiki.return_value = [
            {
                "title": "Local Article",
                "content": "Local content about huobi manipulation.",
                "source": "content/research/market-health/posts/huobi/index.md",
            }
        ]

        context = retrieve_rag_context(
            "huobi", "ht-usdt", "2023-08-01", "2023-08-14",
            enable_web_search=False,
        )
        # Web search should not have been called
        mock_web.assert_not_called()
        assert "Local" in context or "huobi" in context.lower()

    @patch("tools.market_health_reporter.rag_context.fetch_url_content")
    @patch("tools.market_health_reporter.rag_context.fetch_web_results")
    @patch("tools.market_health_reporter.rag_context.load_local_wiki_articles")
    def test_ranks_relevant_sources_higher(self, mock_wiki, mock_web, mock_fetch_url):
        mock_wiki.return_value = []
        mock_web.return_value = [
            {
                "title": "Sports News",
                "url": "https://example.com/sports",
                "snippet": "Football championship game results highlights",
            },
            {
                "title": "Huobi Manipulation Evidence",
                "url": "https://example.com/huobi-manipulation",
                "snippet": "Huobi exchange wash trading cryptocurrency volume manipulation detected",
            },
        ]
        mock_fetch_url.side_effect = lambda url, **kw: (
            "Football championship game results highlights"
            if "sports" in url
            else "Huobi exchange wash trading cryptocurrency volume manipulation detected"
        )

        context = retrieve_rag_context("huobi", "ht-usdt", "2023-08-01", "2023-08-14")

        # The Huobi manipulation source should appear before sports
        huobi_pos = context.find("Huobi Manipulation")
        sports_pos = context.find("Sports News")
        if sports_pos != -1:  # Sports may be excluded due to low relevance
            assert huobi_pos < sports_pos
