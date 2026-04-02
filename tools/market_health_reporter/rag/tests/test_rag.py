"""Unit tests for RAG module. 🌰

Tests cover:
- Chunking edge cases
- Relevance filtering
- TF-IDF retrieval
- Context formatting
- Pipeline graceful degradation
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chunker import chunk_text, split_into_sentences, filter_relevant_chunks
from retriever import compute_cosine_similarity, retrieve_with_tfidf
from pipeline import format_context, build_rag_enhanced_prompt


class TestChunker(unittest.TestCase):
    """Test chunking functionality. 🌰"""
    
    def test_empty_text(self):
        """Empty text should return empty chunks."""
        result = chunk_text("")
        self.assertEqual(result, [])
    
    def test_short_text(self):
        """Short text should return single chunk."""
        text = "This is a short text."
        result = chunk_text(text, chunk_size=1000)
        self.assertEqual(result, [text])
    
    def test_sentence_boundaries(self):
        """Chunking should respect sentence boundaries."""
        text = "First sentence here. Second sentence follows. Third one ends."
        chunks = chunk_text(text, chunk_size=50, overlap=10)
        
        # Each chunk should end with a complete sentence
        for chunk in chunks:
            self.assertTrue(
                chunk.endswith('.') or chunk.endswith('...'),
                f"Chunk does not end properly: {chunk}"
            )
    
    def test_overlap(self):
        """Chunks should have overlap."""
        text = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z"
        chunks = chunk_text(text, chunk_size=10, overlap=3, preserve_sentences=False)
        
        # Check overlap between consecutive chunks
        if len(chunks) > 1:
            overlap_found = False
            for i in range(len(chunks) - 1):
                end_first = chunks[i][-3:]
                start_second = chunks[i+1][:3]
                if end_first == start_second:
                    overlap_found = True
            self.assertTrue(overlap_found, "No overlap found between chunks")


class TestRetriever(unittest.TestCase):
    """Test retrieval functionality. 🌰"""
    
    def test_cosine_similarity_identical(self):
        """Identical vectors should have similarity 1.0."""
        vec = [1.0, 2.0, 3.0]
        similarity = compute_cosine_similarity(vec, vec)
        self.assertAlmostEqual(similarity, 1.0, places=5)
    
    def test_cosine_similarity_orthogonal(self):
        """Orthogonal vectors should have similarity 0.0."""
        vec1 = [1.0, 0.0]
        vec2 = [0.0, 1.0]
        similarity = compute_cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(similarity, 0.0, places=5)
    
    def test_cosine_similarity_zero_vector(self):
        """Zero vectors should return 0.0."""
        vec1 = [0.0, 0.0, 0.0]
        vec2 = [1.0, 2.0, 3.0]
        similarity = compute_cosine_similarity(vec1, vec2)
        self.assertEqual(similarity, 0.0)
    
    def test_tfidf_retrieval(self):
        """TF-IDF should retrieve relevant documents."""
        chunks = [
            {'text': 'Huobi exchange wash trading manipulation investigation'},
            {'text': 'Bitcoin price increases market analysis'},
            {'text': 'Cooking recipes for dinner tonight'},
        ]
        
        query = 'Huobi manipulation wash trading'
        results = retrieve_with_tfidf(chunks, query, top_k=2)
        
        # First result should be about Huobi
        self.assertIn('Huobi', results[0]['text'])
        self.assertTrue(results[0]['similarity'] > results[1]['similarity'])


class TestPipeline(unittest.TestCase):
    """Test pipeline functionality. 🌰"""
    
    def test_format_context_empty(self):
        """Empty chunks should return empty context."""
        result = format_context([])
        self.assertEqual(result, '')
    
    def test_format_context_with_chunks(self):
        """Should format chunks with attribution."""
        chunks = [
            {'text': 'Article content here', 'source': 'CoinDesk', 'url': 'https://example.com', 'title': 'News Title'},
            {'text': 'More content', 'source': 'CryptoNews', 'url': 'https://example2.com', 'title': 'Another Title'},
        ]
        
        result = format_context(chunks, max_chars=1000)
        
        # Should include source attribution
        self.assertIn('[CoinDesk]', result)
        self.assertIn('[CryptoNews]', result)
    
    def test_format_context_truncation(self):
        """Should truncate context to max_chars."""
        chunks = [
            {'text': 'Very long content ' * 100, 'source': 'Source', 'url': 'url', 'title': 'Title'},
        ]
        
        result = format_context(chunks, max_chars=100)
        self.assertTrue(len(result) <= 103)  # max_chars + small buffer for ellipsis
    
    def test_build_rag_prompt_no_context(self):
        """Should return original prompt if no context."""
        original = "Original prompt content"
        result = build_rag_enhanced_prompt(original, None)
        self.assertEqual(result, original)
    
    def test_build_rag_prompt_with_context(self):
        """Should inject context into prompt."""
        original = "<data> Market data here </data>"
        context = "External news context"
        
        result = build_rag_enhanced_prompt(original, context)
        
        # Should include context tags
        self.assertIn('<external_context>', result)
        self.assertIn('</external_context>', result)
        self.assertIn(context, result)


class TestRelevanceFilter(unittest.TestCase):
    """Test relevance filtering. 🌰"""
    
    def test_filter_exchange_relevant(self):
        """Should keep chunks mentioning the exchange."""
        chunks = [
            {'text': 'Huobi exchange shows suspicious trading patterns'},
            {'text': 'Binance announces new trading features'},
            {'text': 'Weather forecast for tomorrow'},
        ]
        
        results = filter_relevant_chunks(chunks, 'huobi', 'btcusdt', min_relevance=0.1)
        
        # Should include Huobi chunk
        self.assertTrue(any('Huobi' in c['text'] for c in results))
        # Should not include weather chunk
        self.assertFalse(any('Weather' in c['text'] for c in results))
    
    def test_filter_pair_relevant(self):
        """Should keep chunks mentioning the trading pair."""
        chunks = [
            {'text': 'BTC USDT trading volume analysis'},
            {'text': 'ETH price movements today'},
            {'text': 'Dogecoin meme coin discussion'},
        ]
        
        results = filter_relevant_chunks(chunks, 'binance', 'btcusdt', min_relevance=0.1)
        
        # Should include BTC chunk
        self.assertTrue(any('BTC' in c['text'] for c in results))


class TestSentenceSplit(unittest.TestCase):
    """Test sentence splitting. 🌰"""
    
    def test_basic_sentences(self):
        """Should split on sentence boundaries."""
        text = "First sentence. Second sentence. Third sentence."
        sentences = split_into_sentences(text)
        self.assertEqual(len(sentences), 3)
    
    def test_preserve_abbreviations(self):
        """Should not split on abbreviations."""
        text = "Dr. Smith visited the U.S. last week."
        sentences = split_into_sentences(text)
        # Should be one sentence, not split on Dr. or U.S.
        self.assertEqual(len(sentences), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)