"""Tests for the RAG context retrieval module."""

import os
import tempfile
import requests
import pytest
from unittest.mock import patch, MagicMock

from tools.market_health_reporter.rag_context import (
    clean_text,
    chunk_text,
    score_relevance,
    load_wiki_articles,
    search_web,
    fetch_article_text,
    build_rag_context,
    _tokenize,
    _term_freq,
    _idf,
    _parse_frontmatter,
    _strip_hugo,
)


# ---------------------------------------------------------------------------
# clean_text
# ---------------------------------------------------------------------------


class TestCleanText:
    def test_strips_html_tags(self):
        assert clean_text("<b>bold</b> text") == "bold text"

    def test_strips_html_entities(self):
        result = clean_text("hello&amp;world")
        assert "&amp;" not in result

    def test_normalizes_whitespace(self):
        assert clean_text("hello   \n\t  world") == "hello world"

    def test_empty_string(self):
        assert clean_text("") == ""

    def test_nested_html(self):
        result = clean_text("<div><p>nested <b>content</b></p></div>")
        assert result == "nested content"


# ---------------------------------------------------------------------------
# Tokenization and TF-IDF
# ---------------------------------------------------------------------------


class TestTokenize:
    def test_basic(self):
        assert _tokenize("Hello World 123") == ["hello", "world", "123"]

    def test_strips_punctuation(self):
        tokens = _tokenize("wash-trading, manipulation!")
        assert "wash" in tokens
        assert "trading" in tokens
        assert "manipulation" in tokens

    def test_empty(self):
        assert _tokenize("") == []


class TestTermFreq:
    def test_basic(self):
        tf = _term_freq(["a", "b", "a"])
        assert abs(tf["a"] - 2 / 3) < 0.01
        assert abs(tf["b"] - 1 / 3) < 0.01

    def test_empty(self):
        tf = _term_freq([])
        assert tf == {}


class TestIdf:
    def test_basic(self):
        docs = [["a", "b"], ["a", "c"], ["b", "c"]]
        idf_map = _idf(docs)
        # "a" appears in 2/3 docs, "b" in 2/3, "c" in 2/3
        assert idf_map["a"] == idf_map["b"] == idf_map["c"]

    def test_rare_term_higher_idf(self):
        docs = [["a", "b"], ["a", "c"], ["a", "d"]]
        idf_map = _idf(docs)
        # "a" in all 3, "b" in 1 — b should have higher IDF
        assert idf_map["b"] > idf_map["a"]


class TestScoreRelevance:
    def test_relevant_text_scores_higher(self):
        idf_map = {"huobi": 2.0, "wash": 1.5, "trading": 1.0, "weather": 0.5}
        query = ["huobi", "wash", "trading"]
        relevant = "Huobi wash trading volume manipulation detected"
        irrelevant = "The weather today is sunny and warm"
        assert score_relevance(query, relevant, idf_map) > score_relevance(query, irrelevant, idf_map)

    def test_empty_query(self):
        assert score_relevance([], "some text", {"some": 1.0}) == 0.0

    def test_empty_text(self):
        assert score_relevance(["huobi"], "", {"huobi": 1.0}) == 0.0


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------


class TestChunkText:
    def test_short_text_single_chunk(self):
        chunks = chunk_text("Short text.", max_chars=100)
        assert len(chunks) == 1
        assert chunks[0] == "Short text."

    def test_splits_long_text(self):
        text = "First sentence. " * 50 + "Last sentence."
        chunks = chunk_text(text, max_chars=200, overlap=0)
        assert len(chunks) > 1

    def test_overlap(self):
        text = "A. B. C. D. E. F. G. H. I. J. K. L. M. N. O. P. Q. R. S. T."
        chunks = chunk_text(text, max_chars=30, overlap=10)
        assert len(chunks) > 1

    def test_empty_text(self):
        chunks = chunk_text("", max_chars=100)
        assert len(chunks) == 1


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------


class TestParseFrontmatter:
    def test_valid_frontmatter(self):
        content = "---\ntitle: Test\nentities:\n  - Huobi\n---\nBody text"
        fm, body = _parse_frontmatter(content)
        assert fm["title"] == "Test"
        assert "Huobi" in fm["entities"]
        assert body == "Body text"

    def test_no_frontmatter(self):
        content = "Just body text"
        fm, body = _parse_frontmatter(content)
        assert fm is None
        assert body == "Just body text"

    def test_invalid_yaml(self):
        content = "---\n: invalid: yaml: [[\n---\nBody"
        fm, body = _parse_frontmatter(content)
        assert fm is None


# ---------------------------------------------------------------------------
# Hugo stripping
# ---------------------------------------------------------------------------


class TestStripHugo:
    def test_strips_figure_shortcodes(self):
        text = 'Some text {{< figure src="img.png" >}} more text'
        result = _strip_hugo(text)
        assert "{{<" not in result
        assert "Some text" in result
        assert "more text" in result

    def test_strips_image_markdown(self):
        text = "Before ![alt](image.png) after"
        result = _strip_hugo(text)
        assert "![" not in result

    def test_collapses_blank_lines(self):
        text = "Line 1\n\n\n\n\nLine 2"
        result = _strip_hugo(text)
        assert "\n\n\n" not in result


# ---------------------------------------------------------------------------
# Wiki loading
# ---------------------------------------------------------------------------


class TestLoadWikiArticles:
    def test_finds_matching_article(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            posts = os.path.join(tmpdir, "content", "research", "market-health", "posts")
            article_dir = os.path.join(posts, "2023-08-14-huobi")
            os.makedirs(article_dir)
            with open(os.path.join(article_dir, "index.md"), "w") as f:
                f.write("---\ntitle: Huobi Analysis\nentities:\n  - Huobi\n---\nWash trading detected.")

            articles = load_wiki_articles("huobi", repo_root=tmpdir)
            assert len(articles) == 1
            assert "Huobi" in articles[0]["title"]
            assert "Wash trading" in articles[0]["content"]

    def test_no_match(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            posts = os.path.join(tmpdir, "content", "research", "market-health", "posts")
            article_dir = os.path.join(posts, "2023-01-01-binance")
            os.makedirs(article_dir)
            with open(os.path.join(article_dir, "index.md"), "w") as f:
                f.write("---\ntitle: Binance\nentities:\n  - Binance\n---\nContent.")

            articles = load_wiki_articles("huobi", repo_root=tmpdir)
            assert len(articles) == 0

    def test_missing_directory(self):
        articles = load_wiki_articles("huobi", repo_root="/nonexistent/path")
        assert articles == []


# ---------------------------------------------------------------------------
# Web search (mocked)
# ---------------------------------------------------------------------------


class TestSearchWeb:
    @patch("tools.market_health_reporter.rag_context._duckduckgo_search")
    def test_deduplicates_urls(self, mock_search):
        mock_search.return_value = [
            {"title": "Article 1", "snippet": "Content 1", "url": "https://example.com/1"},
            {"title": "Article 2", "snippet": "Content 2", "url": "https://example.com/1"},  # duplicate
        ]
        results = search_web("huobi", "btc-usdt")
        urls = [r["url"] for r in results]
        assert len(urls) == len(set(urls))

    @patch("tools.market_health_reporter.rag_context._duckduckgo_search")
    def test_returns_results(self, mock_search):
        mock_search.return_value = [
            {"title": "News", "snippet": "Huobi wash trading", "url": "https://example.com/news"},
        ]
        results = search_web("huobi", "ht-usdt")
        assert len(results) >= 1


# ---------------------------------------------------------------------------
# Article fetching (mocked)
# ---------------------------------------------------------------------------


class TestFetchArticleText:
    @patch("tools.market_health_reporter.rag_context.requests.get")
    def test_extracts_article_text(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = """
        <html><body>
        <nav>Navigation</nav>
        <article><p>Huobi has been accused of wash trading. Volume anomalies were detected across multiple trading pairs including HT-USDT and BTC-USDT. Investigators found significant deviations from expected market behavior patterns.</p></article>
        <footer>Footer</footer>
        </body></html>
        """
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        text = fetch_article_text("https://example.com/article")
        assert text is not None
        assert "wash trading" in text.lower()
        assert "Navigation" not in text
        assert "Footer" not in text

    @patch("tools.market_health_reporter.rag_context.requests.get")
    def test_returns_none_on_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout()
        assert fetch_article_text("https://example.com/timeout") is None

    @patch("tools.market_health_reporter.rag_context.requests.get")
    def test_returns_none_for_short_content(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<html><body><article>Short</article></body></html>"
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        assert fetch_article_text("https://example.com/short") is None


# ---------------------------------------------------------------------------
# build_rag_context (integration)
# ---------------------------------------------------------------------------


class TestBuildRagContext:
    def test_with_wiki_only(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            posts = os.path.join(tmpdir, "content", "research", "market-health", "posts")
            article_dir = os.path.join(posts, "2023-08-14-huobi")
            os.makedirs(article_dir)
            with open(os.path.join(article_dir, "index.md"), "w") as f:
                f.write(
                    "---\ntitle: Huobi Wash Trading\nentities:\n  - Huobi\n---\n"
                    "## Summary\nWash trading detected on Huobi with volume anomalies."
                )

            context = build_rag_context(
                exchange="huobi",
                pair="ht-usdt",
                repo_root=tmpdir,
                include_web_search=False,
                fetch_full_articles=False,
            )
            assert "<external_context>" in context
            assert "Huobi" in context
            assert "</external_context>" in context

    def test_empty_when_no_sources(self):
        context = build_rag_context(
            exchange="nonexistent_exchange_xyz",
            pair="abc-usdt",
            repo_root="/nonexistent",
            include_web_search=False,
            fetch_full_articles=False,
        )
        assert context == ""

    def test_respects_max_context_chars(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            posts = os.path.join(tmpdir, "content", "research", "market-health", "posts")
            article_dir = os.path.join(posts, "2023-08-14-huobi")
            os.makedirs(article_dir)
            with open(os.path.join(article_dir, "index.md"), "w") as f:
                f.write(
                    "---\ntitle: Huobi\nentities:\n  - Huobi\n---\n"
                    + "Wash trading content. " * 500
                )

            context = build_rag_context(
                exchange="huobi",
                pair="ht-usdt",
                repo_root=tmpdir,
                include_web_search=False,
                fetch_full_articles=False,
                max_context_chars=500,
            )
            # The wrapper tags add some overhead, but inner content should be bounded
            assert len(context) < 1500  # generous upper bound including tags

    @patch("tools.market_health_reporter.rag_context.search_web")
    def test_with_web_search(self, mock_search):
        mock_search.return_value = [
            {"title": "Huobi News", "snippet": "Huobi wash trading volume spike detected", "url": "https://example.com/1"},
        ]
        context = build_rag_context(
            exchange="huobi",
            pair="ht-usdt",
            repo_root="/nonexistent",
            include_web_search=True,
            fetch_full_articles=False,
        )
        assert "<external_context>" in context
        assert "Huobi" in context
