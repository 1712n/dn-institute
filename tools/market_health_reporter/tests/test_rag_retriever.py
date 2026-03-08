"""
Unit tests for the RAG retriever module.
"""

import os
import tempfile
import shutil
import pytest
from unittest.mock import patch, MagicMock
from tools.market_health_reporter.rag_retriever import RAGRetriever


@pytest.fixture
def sample_articles_dir():
    """Create a temporary directory with sample article files."""
    tmpdir = tempfile.mkdtemp()

    # Create sample article 1
    article1_dir = os.path.join(tmpdir, "2023-08-14-huobi")
    os.makedirs(article1_dir)
    with open(os.path.join(article1_dir, "index.md"), "w") as f:
        f.write(
            '---\n'
            'title: "Uncovering Wash Trading on Huobi"\n'
            'date: 2023-08-14\n'
            '---\n\n'
            '## Summary\n\n'
            'Recent data reveals a surge in manipulative practices on Huobi.\n\n'
            'HT and TRX tokens were subject to manipulation.\n'
        )

    # Create sample article 2
    article2_dir = os.path.join(tmpdir, "2021-01-19-Gate-io")
    os.makedirs(article2_dir)
    with open(os.path.join(article2_dir, "index.md"), "w") as f:
        f.write(
            '---\n'
            'title: "Gate.io Market Analysis"\n'
            'date: 2021-01-19\n'
            '---\n\n'
            '## Summary\n\n'
            'Analysis of Gate.io trading patterns.\n'
        )

    yield tmpdir
    shutil.rmtree(tmpdir)


class TestSearchLocalArticles:
    """Tests for local article search functionality."""

    def test_finds_matching_articles(self, sample_articles_dir):
        retriever = RAGRetriever(articles_dir=sample_articles_dir)
        results = retriever.search_local_articles("huobi")
        assert len(results) == 1
        assert "Huobi" in results[0]["title"]
        assert "2023-08-14" in results[0]["date"]

    def test_case_insensitive_search(self, sample_articles_dir):
        retriever = RAGRetriever(articles_dir=sample_articles_dir)
        results = retriever.search_local_articles("HUOBI")
        assert len(results) == 1

    def test_no_results_for_unknown_entity(self, sample_articles_dir):
        retriever = RAGRetriever(articles_dir=sample_articles_dir)
        results = retriever.search_local_articles("binance")
        assert len(results) == 0

    def test_limit_results(self, sample_articles_dir):
        retriever = RAGRetriever(articles_dir=sample_articles_dir)
        results = retriever.search_local_articles("trading", limit=1)
        assert len(results) <= 1

    def test_finds_token_mention(self, sample_articles_dir):
        retriever = RAGRetriever(articles_dir=sample_articles_dir)
        results = retriever.search_local_articles("HT")
        assert len(results) == 1


class TestExtractFrontMatter:
    """Tests for YAML front matter extraction."""

    def test_extracts_title(self):
        content = '---\ntitle: "Test Title"\ndate: 2023-01-01\n---\nBody'
        result = RAGRetriever._extract_front_matter_field(content, "title")
        assert result == "Test Title"

    def test_extracts_date(self):
        content = '---\ntitle: "Test"\ndate: 2023-08-14\n---\nBody'
        result = RAGRetriever._extract_front_matter_field(content, "date")
        assert result == "2023-08-14"

    def test_returns_none_for_missing_field(self):
        content = '---\ntitle: "Test"\n---\nBody'
        result = RAGRetriever._extract_front_matter_field(content, "author")
        assert result is None

    def test_returns_none_without_front_matter(self):
        content = "No front matter here"
        result = RAGRetriever._extract_front_matter_field(content, "title")
        assert result is None


class TestExtractRelevantSnippet:
    """Tests for relevant snippet extraction."""

    def test_extracts_relevant_paragraphs(self):
        content = (
            '---\ntitle: "Test"\n---\n\n'
            'First paragraph about Huobi trading.\n\n'
            'Second paragraph about something else.\n\n'
            'Third paragraph mentioning Huobi again.\n'
        )
        snippet = RAGRetriever._extract_relevant_snippet(content, "Huobi")
        assert "Huobi" in snippet

    def test_respects_max_length(self):
        content = '---\ntitle: "T"\n---\n\n' + "Huobi " * 500
        snippet = RAGRetriever._extract_relevant_snippet(content, "Huobi", max_length=100)
        assert len(snippet) <= 100

    def test_skips_hugo_shortcodes(self):
        content = (
            '---\ntitle: "T"\n---\n\n'
            '{{< figure src="test.png" alt="Huobi chart" >}}\n\n'
            'Real paragraph about Huobi.\n'
        )
        snippet = RAGRetriever._extract_relevant_snippet(content, "Huobi")
        assert "figure" not in snippet


class TestFetchCoinGeckoInfo:
    """Tests for CoinGecko API integration."""

    @patch("tools.market_health_reporter.rag_retriever.requests.get")
    def test_successful_fetch(self, mock_get):
        # Mock search response
        search_response = MagicMock()
        search_response.status_code = 200
        search_response.raise_for_status = MagicMock()
        search_response.json.return_value = {
            "coins": [{"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"}]
        }

        # Mock detail response
        detail_response = MagicMock()
        detail_response.status_code = 200
        detail_response.raise_for_status = MagicMock()
        detail_response.json.return_value = {
            "name": "Bitcoin",
            "symbol": "btc",
            "description": {"en": "Bitcoin is a cryptocurrency."},
            "market_cap_rank": 1,
            "market_data": {
                "current_price": {"usd": 50000},
                "total_volume": {"usd": 30000000000},
            },
        }

        mock_get.side_effect = [search_response, detail_response]

        retriever = RAGRetriever(enable_web_search=False)
        info = retriever.fetch_coingecko_info("btc")

        assert info is not None
        assert info["name"] == "Bitcoin"
        assert info["current_price_usd"] == 50000

    @patch("tools.market_health_reporter.rag_retriever.requests.get")
    def test_returns_none_on_api_error(self, mock_get):
        mock_get.side_effect = Exception("API error")
        retriever = RAGRetriever(enable_web_search=False)
        info = retriever.fetch_coingecko_info("btc")
        assert info is None

    def test_disabled_returns_none(self):
        retriever = RAGRetriever(enable_coingecko=False)
        info = retriever.fetch_coingecko_info("btc")
        assert info is None


class TestGetContext:
    """Tests for the main context builder."""

    def test_returns_string(self, sample_articles_dir):
        retriever = RAGRetriever(
            articles_dir=sample_articles_dir,
            enable_web_search=False,
            enable_coingecko=False,
        )
        context = retriever.get_context(exchange="huobi", tokens=["HT"])
        assert isinstance(context, str)
        assert "Background Context" in context

    def test_empty_when_no_matches(self, sample_articles_dir):
        retriever = RAGRetriever(
            articles_dir=sample_articles_dir,
            enable_web_search=False,
            enable_coingecko=False,
        )
        context = retriever.get_context(exchange="nonexistent", tokens=["XYZ"])
        assert context == ""

    def test_includes_local_articles(self, sample_articles_dir):
        retriever = RAGRetriever(
            articles_dir=sample_articles_dir,
            enable_web_search=False,
            enable_coingecko=False,
        )
        context = retriever.get_context(exchange="huobi", tokens=["HT", "TRX"])
        assert "dn.institute Articles" in context
        assert "Huobi" in context
