#!/usr/bin/env python3
"""
Test script for RAG functionality 🌰

Tests the RAG retriever with sample entity queries.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from python_modules.rag_tool import RAGRetriever


def test_rag_retriever():
    """Test RAG retrieval with Huobi example."""
    print("=== Testing RAG Retriever ===\n")
    
    retriever = RAGRetriever(
        max_context_tokens=2000
    )
    
    # Test with Huobi entity
    entities = ["Huobi", "HT", "TRX"]
    start_date = "2023-08-01"
    end_date = "2023-08-14"
    
    print(f"Entities: {entities}")
    print(f"Date range: {start_date} to {end_date}\n")
    
    context = retriever.retrieve_context(
        entities=entities,
        start_date=start_date,
        end_date=end_date
    )
    
    print("=== Retrieved Context ===\n")
    print(context)
    print("\n=== Test Complete ===")
    
    # Check token count - use assert so CI fails if over limit
    import tiktoken
    encoding = tiktoken.encoding_for_model("gpt-4")
    token_count = len(encoding.encode(context))
    print(f"\nContext token count: {token_count}")
    
    assert token_count <= retriever.max_context_tokens, f"Token count {token_count} exceeds limit of {retriever.max_context_tokens}"
    print("✅ Token count within limit")


if __name__ == "__main__":
    test_rag_retriever()
