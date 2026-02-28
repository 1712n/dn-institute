"""
🌰 Unit tests for RAG Context Retrieval module 🌰

Tests cover all pipeline stages:
  - Text cleaning (HTML stripping, markdown artifact removal) 🌰
  - TF-IDF relevance scoring and ranking 🌰
  - DuckDuckGo search integration 🌰
  - CryptoPanic API integration 🌰
  - Local wiki article loading 🌰
  - Token budget management 🌰
  - Context formatting 🌰
  - Full pipeline integration 🌰
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from tools.market_health_reporter.rag_context import (
    ContextChunk,
    RAGResult,
    build_rag_context,
    clean_html,
    compute_tfidf_scores,
    estimate_tokens,
    format_context,
    load_wiki_articles,
    rank_chunks,
    search_cryptopanic,
    search_duckduckgo,
    select_within_budget,
    strip_markdown_artifacts,
    _normalize_name,
    _parse_frontmatter,
    _tokenize,
)


# ---------------------------------------------------------------------------
# 🌰 Test: HTML cleaning
# ---------------------------------------------------------------------------

class TestCleanHtml(unittest.TestCase):
    """Tests for clean_html — no raw HTML in prompts (PR #480 feedback). 🌰"""

    def test_strips_html_tags(self) -> None:
        """🌰 Strips HTML tags while preserving text content."""
        raw = "<p>Binance <b>wash trading</b> report</p>"
        result = clean_html(raw)
        self.assertEqual(result, "Binance wash trading report")

    def test_normalizes_whitespace(self) -> None:
        """🌰 Collapses multiple spaces and newlines."""
        raw = "  too   many    spaces  \n\n  here  "
        result = clean_html(raw)
        self.assertEqual(result, "too many spaces here")

    def test_empty_input(self) -> None:
        """🌰 Returns empty string for empty input."""
        self.assertEqual(clean_html(""), "")
        self.assertEqual(clean_html(None), "")  # type: ignore[arg-type]

    def test_nested_html(self) -> None:
        """🌰 Handles deeply nested HTML structures."""
        raw = "<div><ul><li><a href='x'>link <em>text</em></a></li></ul></div>"
        result = clean_html(raw)
        self.assertIn("link", result)
        self.assertIn("text", result)
        self.assertNotIn("<", result)


# ---------------------------------------------------------------------------
# 🌰 Test: Markdown artifact stripping
# ---------------------------------------------------------------------------

class TestStripMarkdownArtifacts(unittest.TestCase):
    """Tests for strip_markdown_artifacts. 🌰"""

    def test_removes_hugo_shortcodes(self) -> None:
        """🌰 Strips Hugo figure shortcodes."""
        text = 'Some text {{< figure src="chart.png" >}} more text'
        result = strip_markdown_artifacts(text)
        self.assertNotIn("{{<", result)
        self.assertIn("Some text", result)
        self.assertIn("more text", result)

    def test_removes_image_references(self) -> None:
        """🌰 Strips markdown image syntax."""
        text = "Analysis: ![volume chart](images/vol.png) shows anomalies"
        result = strip_markdown_artifacts(text)
        self.assertNotIn("![", result)
        self.assertIn("Analysis:", result)
        self.assertIn("shows anomalies", result)

    def test_preserves_link_text(self) -> None:
        """🌰 Keeps link text but strips URL syntax."""
        text = "See [Binance report](https://example.com) for details"
        result = strip_markdown_artifacts(text)
        self.assertIn("Binance report", result)
        self.assertNotIn("https://", result)

    def test_removes_heading_markers(self) -> None:
        """🌰 Strips heading markers."""
        text = "## Volume Analysis\nSome content\n### Sub heading"
        result = strip_markdown_artifacts(text)
        self.assertNotIn("##", result)
        self.assertIn("Volume Analysis", result)

    def test_empty_input(self) -> None:
        """🌰 Handles empty input."""
        self.assertEqual(strip_markdown_artifacts(""), "")
        self.assertEqual(strip_markdown_artifacts(None), "")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 🌰 Test: Tokenizer
# ---------------------------------------------------------------------------

class TestTokenize(unittest.TestCase):
    """Tests for _tokenize helper. 🌰"""

    def test_lowercase_split(self) -> None:
        """🌰 Tokenizes and lowercases."""
        tokens = _tokenize("Binance BTC-USDT Trading")
        self.assertEqual(tokens, ["binance", "btc", "usdt", "trading"])

    def test_empty_string(self) -> None:
        """🌰 Returns empty list for empty string."""
        self.assertEqual(_tokenize(""), [])


# ---------------------------------------------------------------------------
# 🌰 Test: TF-IDF scoring
# ---------------------------------------------------------------------------

class TestTfidfScoring(unittest.TestCase):
    """Tests for compute_tfidf_scores and rank_chunks. 🌰"""

    def test_relevant_doc_scores_higher(self) -> None:
        """🌰 Document mentioning query terms scores higher than unrelated."""
        query = _tokenize("binance wash trading manipulation")
        docs = [
            "binance wash trading detected in market analysis",
            "the weather forecast for today is sunny and warm",
        ]
        scores = compute_tfidf_scores(query, docs)
        self.assertGreater(scores[0], scores[1])

    def test_empty_query(self) -> None:
        """🌰 Empty query returns zero scores."""
        scores = compute_tfidf_scores([], ["some document"])
        self.assertEqual(scores, [0.0])

    def test_empty_documents(self) -> None:
        """🌰 Empty documents list returns empty scores."""
        scores = compute_tfidf_scores(["test"], [])
        self.assertEqual(scores, [])

    def test_multiple_documents_ranking(self) -> None:
        """🌰 Multiple documents ranked correctly by TF-IDF."""
        query = _tokenize("cryptocurrency volume anomaly")
        docs = [
            "stock market report with no crypto mentions",
            "cryptocurrency exchange volume anomaly detection system",
            "slight mention of volume in a cooking recipe",
        ]
        scores = compute_tfidf_scores(query, docs)
        self.assertEqual(scores.index(max(scores)), 1)

    def test_rank_chunks_sorts_descending(self) -> None:
        """🌰 rank_chunks sorts by relevance score descending."""
        chunks = [
            ContextChunk(text="weather report sunny day", source="web"),
            ContextChunk(text="binance btc wash trading manipulation volume", source="web"),
        ]
        ranked = rank_chunks(chunks, "binance", "btc-usdt")
        self.assertGreater(ranked[0].relevance_score, ranked[1].relevance_score)
        self.assertIn("binance", ranked[0].text)


# ---------------------------------------------------------------------------
# 🌰 Test: DuckDuckGo search
# ---------------------------------------------------------------------------

class TestDuckDuckGoSearch(unittest.TestCase):
    """Tests for search_duckduckgo. 🌰"""

    @patch("tools.market_health_reporter.rag_context.DDGS")
    def test_returns_chunks_from_results(self, mock_ddgs_cls: MagicMock) -> None:
        """🌰 Converts DuckDuckGo results to ContextChunks."""
        mock_ddgs = MagicMock()
        mock_ddgs.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs.__exit__ = MagicMock(return_value=False)
        mock_ddgs.text.return_value = [
            {"title": "Test Title", "body": "wash trading on binance", "href": "https://example.com/1"},
        ]
        mock_ddgs_cls.return_value = mock_ddgs

        chunks = search_duckduckgo("binance", "btc-usdt", max_results_per_query=2)
        self.assertGreater(len(chunks), 0)
        self.assertEqual(chunks[0].source, "duckduckgo")
        self.assertIn("wash trading", chunks[0].text)

    @patch("tools.market_health_reporter.rag_context.DDGS")
    def test_deduplicates_urls(self, mock_ddgs_cls: MagicMock) -> None:
        """🌰 Skips duplicate URLs across queries."""
        mock_ddgs = MagicMock()
        mock_ddgs.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs.__exit__ = MagicMock(return_value=False)
        mock_ddgs.text.return_value = [
            {"title": "Same", "body": "content", "href": "https://example.com/same"},
            {"title": "Same2", "body": "content2", "href": "https://example.com/same"},
        ]
        mock_ddgs_cls.return_value = mock_ddgs

        chunks = search_duckduckgo("binance", "btc-usdt")
        urls = [c.url for c in chunks]
        self.assertEqual(len(urls), len(set(urls)))

    @patch("tools.market_health_reporter.rag_context.DDGS", None)
    def test_returns_empty_when_ddgs_unavailable(self) -> None:
        """🌰 Gracefully returns empty when duckduckgo-search not available."""
        chunks = search_duckduckgo("binance", "btc-usdt")
        self.assertEqual(chunks, [])


# ---------------------------------------------------------------------------
# 🌰 Test: CryptoPanic search
# ---------------------------------------------------------------------------

class TestCryptoPanicSearch(unittest.TestCase):
    """Tests for search_cryptopanic. 🌰"""

    @patch("tools.market_health_reporter.rag_context.requests.get")
    def test_returns_chunks_from_api(self, mock_get: MagicMock) -> None:
        """🌰 Converts CryptoPanic results to ContextChunks."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "results": [
                {"title": "BTC surges", "body": "", "url": "https://news.example.com/1"},
                {"title": "Market alert", "body": "Volume spike detected", "url": "https://news.example.com/2"},
            ]
        }
        mock_get.return_value = mock_resp

        chunks = search_cryptopanic("binance", "btc-usdt")
        self.assertGreater(len(chunks), 0)
        self.assertEqual(chunks[0].source, "cryptopanic")

    @patch("tools.market_health_reporter.rag_context.requests.get")
    def test_handles_api_error(self, mock_get: MagicMock) -> None:
        """🌰 Returns empty on API failure."""
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_get.return_value = mock_resp

        chunks = search_cryptopanic("binance", "btc-usdt")
        self.assertEqual(chunks, [])

    @patch("tools.market_health_reporter.rag_context.requests.get")
    def test_handles_network_error(self, mock_get: MagicMock) -> None:
        """🌰 Returns empty on network exception."""
        mock_get.side_effect = ConnectionError("Network down")

        chunks = search_cryptopanic("binance", "btc-usdt")
        self.assertEqual(chunks, [])


# ---------------------------------------------------------------------------
# 🌰 Test: Frontmatter parsing
# ---------------------------------------------------------------------------

class TestParseFrontmatter(unittest.TestCase):
    """Tests for _parse_frontmatter. 🌰"""

    def test_valid_frontmatter(self) -> None:
        """🌰 Parses valid YAML frontmatter."""
        content = "---\ntitle: Test\nentities: Binance, BTC\n---\nBody text"
        metadata, body = _parse_frontmatter(content)
        self.assertEqual(metadata["title"], "Test")
        self.assertEqual(body, "Body text")

    def test_no_frontmatter(self) -> None:
        """🌰 Returns empty dict for content without frontmatter."""
        content = "Just some markdown text"
        metadata, body = _parse_frontmatter(content)
        self.assertEqual(metadata, {})
        self.assertEqual(body, content)

    def test_invalid_yaml(self) -> None:
        """🌰 Handles invalid YAML gracefully."""
        content = "---\n: [invalid\n---\nBody"
        metadata, body = _parse_frontmatter(content)
        self.assertEqual(metadata, {})


# ---------------------------------------------------------------------------
# 🌰 Test: Name normalization
# ---------------------------------------------------------------------------

class TestNormalizeName(unittest.TestCase):
    """Tests for _normalize_name. 🌰"""

    def test_removes_special_chars(self) -> None:
        """🌰 Strips dots, hyphens, spaces."""
        self.assertEqual(_normalize_name("Gate.io"), "gateio")
        self.assertEqual(_normalize_name("Huobi-Global"), "huobiglobal")

    def test_lowercases(self) -> None:
        """🌰 Converts to lowercase."""
        self.assertEqual(_normalize_name("BINANCE"), "binance")


# ---------------------------------------------------------------------------
# 🌰 Test: Wiki article loading
# ---------------------------------------------------------------------------

class TestLoadWikiArticles(unittest.TestCase):
    """Tests for load_wiki_articles. 🌰"""

    def setUp(self) -> None:
        """🌰 Create a temporary wiki structure."""
        self.tmpdir = tempfile.mkdtemp()
        posts_dir = os.path.join(self.tmpdir, "content", "market-health", "posts")
        os.makedirs(posts_dir)

        # Create a Huobi article 🌰
        huobi_dir = os.path.join(posts_dir, "2023-08-14-huobi")
        os.makedirs(huobi_dir)
        with open(os.path.join(huobi_dir, "index.md"), "w") as f:
            f.write("---\ntitle: Huobi Wash Trading Report\nentities: Huobi, HT\n---\n"
                    "## Analysis\nHuobi shows significant wash trading patterns.\n"
                    "{{< figure src=\"chart.png\" >}}\nMore analysis text here.")

        # Create a Gate.io article 🌰
        gate_dir = os.path.join(posts_dir, "2021-01-19-Gate-io")
        os.makedirs(gate_dir)
        with open(os.path.join(gate_dir, "index.md"), "w") as f:
            f.write("---\ntitle: Gate.io Market Analysis\nentities: Gate.io\n---\n"
                    "Gate.io trading volume analysis results.")

    def test_finds_matching_exchange(self) -> None:
        """🌰 Finds articles matching the exchange name."""
        chunks = load_wiki_articles("huobi", self.tmpdir)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].source, "wiki")
        self.assertIn("wash trading", chunks[0].text)

    def test_case_insensitive_match(self) -> None:
        """🌰 Match is case-insensitive."""
        chunks = load_wiki_articles("HUOBI", self.tmpdir)
        self.assertEqual(len(chunks), 1)

    def test_no_match_returns_empty(self) -> None:
        """🌰 Returns empty for non-matching exchange."""
        chunks = load_wiki_articles("kraken", self.tmpdir)
        self.assertEqual(chunks, [])

    def test_strips_hugo_shortcodes(self) -> None:
        """🌰 Wiki content is cleaned of Hugo shortcodes."""
        chunks = load_wiki_articles("huobi", self.tmpdir)
        self.assertNotIn("{{<", chunks[0].text)

    def test_missing_directory(self) -> None:
        """🌰 Returns empty for non-existent repo root."""
        chunks = load_wiki_articles("huobi", "/nonexistent/path")
        self.assertEqual(chunks, [])

    def test_respects_max_chars(self) -> None:
        """🌰 Truncates long articles to max_chars_per_article."""
        chunks = load_wiki_articles("huobi", self.tmpdir, max_chars_per_article=20)
        self.assertTrue(chunks[0].text.endswith("..."))
        self.assertLessEqual(len(chunks[0].text), 24)  # 20 + "..."


# ---------------------------------------------------------------------------
# 🌰 Test: Token budget management
# ---------------------------------------------------------------------------

class TestTokenBudget(unittest.TestCase):
    """Tests for estimate_tokens and select_within_budget. 🌰"""

    def test_estimate_tokens_heuristic(self) -> None:
        """🌰 Token estimate uses ~4 chars/token heuristic."""
        self.assertEqual(estimate_tokens("a" * 400), 100)
        self.assertEqual(estimate_tokens(""), 1)

    def test_select_within_budget_respects_limit(self) -> None:
        """🌰 Selection stays within token budget."""
        chunks = [
            ContextChunk(text="a" * 400, source="web", relevance_score=3.0),
            ContextChunk(text="b" * 400, source="web", relevance_score=2.0),
            ContextChunk(text="c" * 400, source="web", relevance_score=1.0),
        ]
        # Budget for ~200 tokens = 800 chars = 2 chunks
        selected = select_within_budget(chunks, max_tokens=200)
        self.assertEqual(len(selected), 2)

    def test_truncates_last_chunk(self) -> None:
        """🌰 Truncates partial-fit chunk to fill remaining budget."""
        chunks = [
            ContextChunk(text="a" * 400, source="web", relevance_score=2.0),
            ContextChunk(text="b" * 2000, source="web", relevance_score=1.0),
        ]
        # Budget: 200 tokens = 800 chars. First chunk=100 tokens, remaining=100 tokens=400 chars
        selected = select_within_budget(chunks, max_tokens=200)
        self.assertEqual(len(selected), 2)
        self.assertTrue(selected[1].text.endswith("..."))

    def test_empty_chunks(self) -> None:
        """🌰 Returns empty for empty input."""
        self.assertEqual(select_within_budget([], max_tokens=1000), [])


# ---------------------------------------------------------------------------
# 🌰 Test: Context formatting
# ---------------------------------------------------------------------------

class TestFormatContext(unittest.TestCase):
    """Tests for format_context. 🌰"""

    def test_wraps_in_xml_tags(self) -> None:
        """🌰 Context is wrapped in external_context XML tags."""
        chunks = [ContextChunk(text="test content", source="duckduckgo", title="Test")]
        result = format_context(chunks)
        self.assertIn("<external_context>", result)
        self.assertIn("</external_context>", result)
        self.assertIn("test content", result)

    def test_labels_sources(self) -> None:
        """🌰 Each source chunk gets a labeled XML tag."""
        chunks = [
            ContextChunk(text="web result", source="duckduckgo", title="DDG"),
            ContextChunk(text="news item", source="cryptopanic", title="CP"),
            ContextChunk(text="wiki article", source="wiki", title="Wiki"),
        ]
        result = format_context(chunks)
        self.assertIn("Web Search", result)
        self.assertIn("CryptoPanic News", result)
        self.assertIn("DN Institute Wiki", result)

    def test_empty_chunks(self) -> None:
        """🌰 Returns empty string for no chunks."""
        self.assertEqual(format_context([]), "")

    def test_includes_chestnut_comment(self) -> None:
        """🌰 Includes chestnut emoji in the context block."""
        chunks = [ContextChunk(text="data", source="web", title="T")]
        result = format_context(chunks)
        self.assertIn("🌰", result)


# ---------------------------------------------------------------------------
# 🌰 Test: Full pipeline integration
# ---------------------------------------------------------------------------

class TestBuildRagContext(unittest.TestCase):
    """Integration tests for build_rag_context pipeline. 🌰"""

    def test_returns_rag_result(self) -> None:
        """🌰 Pipeline returns a valid RAGResult."""
        result = build_rag_context(
            exchange="testexchange",
            pair="btc-usdt",
            disable_web_search=True,
            disable_cryptopanic=True,
        )
        self.assertIsInstance(result, RAGResult)

    def test_empty_when_all_disabled(self) -> None:
        """🌰 Returns empty context when all sources disabled and no wiki."""
        result = build_rag_context(
            exchange="testexchange",
            pair="btc-usdt",
            disable_web_search=True,
            disable_cryptopanic=True,
            repo_root="/nonexistent",
        )
        self.assertEqual(result.context_text, "")
        self.assertEqual(result.chunks_used, 0)

    @patch("tools.market_health_reporter.rag_context.search_duckduckgo")
    @patch("tools.market_health_reporter.rag_context.search_cryptopanic")
    def test_combines_multiple_sources(
        self, mock_cp: MagicMock, mock_ddg: MagicMock
    ) -> None:
        """🌰 Pipeline combines chunks from all sources."""
        mock_ddg.return_value = [
            ContextChunk(text="web result about binance trading", source="duckduckgo", title="Web"),
        ]
        mock_cp.return_value = [
            ContextChunk(text="crypto news about volume spike", source="cryptopanic", title="News"),
        ]
        result = build_rag_context(
            exchange="binance",
            pair="btc-usdt",
            max_context_tokens=4000,
        )
        self.assertGreater(result.chunks_used, 0)
        self.assertIn("<external_context>", result.context_text)
        self.assertIn("duckduckgo", result.sources_queried)
        self.assertIn("cryptopanic", result.sources_queried)

    @patch("tools.market_health_reporter.rag_context.search_duckduckgo")
    def test_respects_token_budget(self, mock_ddg: MagicMock) -> None:
        """🌰 Pipeline respects max_context_tokens budget."""
        # Create chunks that exceed budget 🌰
        mock_ddg.return_value = [
            ContextChunk(text="x" * 2000, source="duckduckgo", title=f"R{i}")
            for i in range(10)
        ]
        result = build_rag_context(
            exchange="binance",
            pair="btc-usdt",
            max_context_tokens=500,
            disable_cryptopanic=True,
        )
        # Total chars should be bounded
        self.assertLess(result.chunks_used, 10)


if __name__ == "__main__":
    unittest.main()
