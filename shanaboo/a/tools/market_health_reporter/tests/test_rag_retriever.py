"""
Tests for RAG Retriever 🌰
"""
import pytest
from unittest.mock import patch, MagicMock
from rag_retriever import RAGRetriever

class TestRAGRetriever:
    
    def setup_method(self):
        self.retriever = RAGRetriever()
    
    @patch('requests.get')
    def test_fetch_coindesk_articles(self, mock_get):
        """Test fetching articles from CoinDesk"""
        mock_response = MagicMock()
        mock_response.content = """
        <html>
            <a href="/markets/bitcoin-price-analysis">Bitcoin Price Analysis</a>
            <a href="/markets/ethereum-news">Ethereum Market Update</a>
        </html>
        """
        mock_get.return_value = mock_response
        
        articles = self.retriever._fetch_coindesk("bitcoin")
        
        assert len(articles) > 0
        assert articles[0]['source'] == 'coindesk'
        assert 'Bitcoin Price Analysis' in articles[0]['title']
    
    def test_retrieve_context(self):
        """Test retrieving context from vector store"""
        # Mock vector store
        self.retriever.vector_store = MagicMock()
        self.retriever.vector_store.similarity_search.return_value = [
            MagicMock(page_content="Test context 1"),
            MagicMock(page_content="Test context 2")
        ]
        
        context = self.retriever.retrieve_context("test query")
        
        assert len(context) == 2
        assert "Test context 1" in context
        assert "Test context 2" in context