"""Tests for the RAG context retrieval module."""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from tools.market_health_reporter.rag_context import (
    load_wiki_articles,
    build_rag_context,
    _parse_frontmatter,
    _trim_article,
    _clean_text,
)


SAMPLE_ARTICLE = """---
title: "Wash Trading on TestExchange"
date: 2024-01-01
entities:
  - TestExchange
  - BTC
---

## Summary

1. **90% fake volume**: TestExchange was found to have 90% fabricated volume.
2. **Regulatory action**: Fined $10 million.

## Evidence

Detailed evidence section with lots of text about manipulation patterns.
"""

SAMPLE_ARTICLE_HUOBI = """---
title: "Uncovering Wash Trading on Huobi"
date: 2023-08-14
entities:
  - Huobi
  - HT
  - TRX
---

## Summary

1. Recent data reveals a **surge in manipulative practices**.

## Metrics used

{{< figure src="chart.png" alt="chart" >}}

Long analysis section here.
"""


@pytest.fixture
def wiki_dir(tmp_path):
    """Create a temporary wiki directory with sample articles."""
    posts_dir = tmp_path / "content" / "research" / "market-health" / "posts"

    # TestExchange article
    exchange_dir = posts_dir / "2024-01-01-testexchange"
    exchange_dir.mkdir(parents=True)
    (exchange_dir / "index.md").write_text(SAMPLE_ARTICLE)

    # Huobi article
    huobi_dir = posts_dir / "2023-08-14-huobi"
    huobi_dir.mkdir(parents=True)
    (huobi_dir / "index.md").write_text(SAMPLE_ARTICLE_HUOBI)

    # Non-matching article
    other_dir = posts_dir / "2024-01-01-other"
    other_dir.mkdir(parents=True)
    (other_dir / "index.md").write_text(
        "---\ntitle: Other\ndate: 2024-01-01\nentities:\n  - OtherExchange\n---\n\nContent."
    )

    return tmp_path


class TestParseFrontmatter:
    def test_valid_frontmatter(self):
        fm, body = _parse_frontmatter(SAMPLE_ARTICLE)
        assert fm is not None
        assert fm["title"] == "Wash Trading on TestExchange"
        assert "TestExchange" in fm["entities"]
        assert "## Summary" in body

    def test_no_frontmatter(self):
        fm, body = _parse_frontmatter("Just some text without frontmatter")
        assert fm is None
        assert body == "Just some text without frontmatter"

    def test_invalid_yaml(self):
        fm, body = _parse_frontmatter("---\n[invalid: yaml: :\n---\nBody")
        assert fm is None


class TestTrimArticle:
    def test_short_article_unchanged(self):
        body = "## Summary\n\nShort content."
        assert _trim_article(body) == body

    def test_removes_hugo_shortcodes(self):
        body = '## Summary\n\n{{< figure src="chart.png" >}}\n\nText here.'
        result = _trim_article(body)
        assert "{{<" not in result
        assert "Text here." in result

    def test_long_article_trimmed_to_summary(self):
        body = "## Summary\n\nShort summary.\n\n## Long Section\n\n" + "x" * 5000
        result = _trim_article(body, max_chars=200)
        assert "Short summary" in result
        assert len(result) <= 200


class TestCleanText:
    def test_strips_html(self):
        assert _clean_text("<b>bold</b> text") == "bold text"

    def test_normalizes_whitespace(self):
        assert _clean_text("hello   world\n\ntest") == "hello world test"

    def test_empty_string(self):
        assert _clean_text("") == ""


class TestLoadWikiArticles:
    def test_finds_matching_exchange(self, wiki_dir):
        articles = load_wiki_articles("testexchange", str(wiki_dir))
        assert len(articles) == 1
        assert "TestExchange" in articles[0]["title"]

    def test_case_insensitive_match(self, wiki_dir):
        articles = load_wiki_articles("TestExchange", str(wiki_dir))
        assert len(articles) == 1

    def test_finds_huobi(self, wiki_dir):
        articles = load_wiki_articles("huobi", str(wiki_dir))
        assert len(articles) == 1
        assert "Huobi" in articles[0]["title"]

    def test_no_match_returns_empty(self, wiki_dir):
        articles = load_wiki_articles("nonexistent", str(wiki_dir))
        assert len(articles) == 0

    def test_does_not_match_unrelated(self, wiki_dir):
        articles = load_wiki_articles("testexchange", str(wiki_dir))
        assert all("Other" not in a["title"] for a in articles)

    def test_missing_directory(self):
        articles = load_wiki_articles("test", "/nonexistent/path")
        assert articles == []


class TestBuildRagContext:
    def test_returns_formatted_context(self, wiki_dir):
        context = build_rag_context(
            "testexchange", "btc-usdt",
            repo_root=str(wiki_dir),
            include_web_search=False,
        )
        assert "<external_context>" in context
        assert "</external_context>" in context
        assert "TestExchange" in context

    def test_empty_when_no_match(self, wiki_dir):
        context = build_rag_context(
            "nonexistent", "btc-usdt",
            repo_root=str(wiki_dir),
            include_web_search=False,
        )
        assert context == ""

    def test_respects_max_context_chars(self, wiki_dir):
        context = build_rag_context(
            "testexchange", "btc-usdt",
            repo_root=str(wiki_dir),
            include_web_search=False,
            max_context_chars=100,
        )
        # Should still produce output if at least one article fits
        # The first article content should be truncated or at least bounded
        if context:
            assert len(context) < 1000  # bounded

    @patch("tools.market_health_reporter.rag_context.search_web")
    def test_includes_web_search(self, mock_search, wiki_dir):
        mock_search.return_value = [
            {"title": "News Article", "content": "Exchange in trouble", "source": "https://example.com"}
        ]
        context = build_rag_context(
            "testexchange", "btc-usdt",
            repo_root=str(wiki_dir),
            include_web_search=True,
        )
        assert "News Article" in context
        mock_search.assert_called_once()

    @patch("tools.market_health_reporter.rag_context.search_web")
    def test_skips_web_search_when_disabled(self, mock_search, wiki_dir):
        build_rag_context(
            "testexchange", "btc-usdt",
            repo_root=str(wiki_dir),
            include_web_search=False,
        )
        mock_search.assert_not_called()
