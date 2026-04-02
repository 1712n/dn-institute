"""RAG Pipeline Module - Orchestrates the full RAG workflow. 🌰

Pipeline stages:
1. Source fetching (CryptoPanic, NewsAPI, DuckDuckGo)
2. Content extraction (HTML → clean text)
3. Chunking (sentence-aware with overlap)
4. Retrieval (semantic similarity)
5. Context formatting (token-budget-aware)
"""

import json
from typing import List, Dict, Optional

from .sources import fetch_all_sources
from .extractor import batch_extract_articles
from .chunker import chunk_articles, filter_relevant_chunks
from .retriever import retrieve_top_chunks


def fetch_rag_context(
    marketvenueid: str,
    pairid: str,
    openai_key: Optional[str] = None,
    cryptopanic_token: Optional[str] = None,
    newsapi_key: Optional[str] = None,
    max_articles: int = 5,
    max_chunks: int = 10,
    max_context_chars: int = 3000,
    start_date: str = '',
    end_date: str = ''
) -> Optional[str]:
    """Fetch RAG context for market health report. 🌰
    
    Full pipeline from news fetching to formatted context string.
    
    Args:
        marketvenueid: Exchange identifier (e.g., 'huobi')
        pairid: Trading pair (e.g., 'btcusdt')
        openai_key: Optional OpenAI API key for embeddings
        cryptopanic_token: Optional CryptoPanic API token
        newsapi_key: Optional NewsAPI key
        max_articles: Maximum articles to fetch
        max_chunks: Maximum chunks to retrieve
        max_context_chars: Maximum context length in characters
        start_date: Analysis start date
        end_date: Analysis end date
    
    Returns:
        Formatted context string for LLM prompt, or None on failure
    """
    print(f"[RAG] Starting pipeline for {marketvenueid}/{pairid} 🌰")
    
    try:
        # Stage 1: Fetch news sources
        articles = fetch_all_sources(
            marketvenueid=marketvenueid,
            pairid=pairid,
            cryptopanic_token=cryptopanic_token,
            newsapi_key=newsapi_key,
            max_total=max_articles * 2  # Fetch more, filter later
        )
        
        if not articles:
            print("[RAG] No articles found, returning None 🌰")
            return None
        
        # Stage 2: Extract content from articles
        extracted = batch_extract_articles(
            articles=articles,
            max_chars=2000,
            max_articles=max_articles,
            timeout=10
        )
        
        if not extracted:
            print("[RAG] No content extracted, returning None 🌰")
            return None
        
        # Stage 3: Chunk articles
        chunks = chunk_articles(
            articles=extracted,
            chunk_size=400,
            overlap=40
        )
        
        # Stage 4: Filter by relevance
        relevant_chunks = filter_relevant_chunks(
            chunks=chunks,
            marketvenueid=marketvenueid,
            pairid=pairid,
            min_relevance=0.05
        )
        
        if not relevant_chunks:
            print("[RAG] No relevant chunks found, returning None 🌰")
            return None
        
        # Stage 5: Retrieve top chunks
        top_chunks = retrieve_top_chunks(
            chunks=relevant_chunks,
            marketvenueid=marketvenueid,
            pairid=pairid,
            openai_key=openai_key,
            top_k=max_chunks,
            min_score=0.05
        )
        
        if not top_chunks:
            print("[RAG] No chunks retrieved, returning None 🌰")
            return None
        
        # Stage 6: Format context with token budget
        context = format_context(top_chunks, max_context_chars)
        
        print(f"[RAG] Pipeline complete: {len(context)} chars of context 🌰")
        
        return context
        
    except Exception as e:
        print(f"[RAG] Pipeline failed: {e} 🌰")
        return None


def format_context(
    chunks: List[Dict],
    max_chars: int = 3000
) -> str:
    """Format retrieved chunks into context string. 🌰
    
    Creates a clean, attributed context block for LLM injection.
    
    Args:
        chunks: List of chunk dicts with 'text', 'source', 'url', 'title'
        max_chars: Maximum total characters
    
    Returns:
        Formatted context string
    """
    if not chunks:
        return ''
    
    context_parts = []
    total_chars = 0
    
    for chunk in chunks:
        # Build chunk entry
        source = chunk.get('source', 'Unknown')
        url = chunk.get('url', '')
        title = chunk.get('title', '')
        text = chunk.get('text', '')
        
        # Format: [Source: Title] Text
        entry = f"[{source}] "
        if title and len(title) < 100:
            entry += f"{title}: "
        entry += text
        
        # Check budget
        entry_len = len(entry)
        if total_chars + entry_len > max_chars:
            # Truncate last entry to fit
            remaining = max_chars - total_chars
            if remaining > 100:
                entry = entry[:remaining].rsplit(' ', 1)[0] + '...'
                context_parts.append(entry)
            break
        
        context_parts.append(entry)
        total_chars += entry_len + 1  # +1 for newline
    
    # Build final context
    context = '\n\n'.join(context_parts)
    
    return context


def build_rag_enhanced_prompt(
    original_prompt: str,
    rag_context: Optional[str],
    include_instructions: bool = True
) -> str:
    """Build RAG-enhanced prompt for LLM. 🌰
    
    Injects retrieved context into the original prompt with
    clear XML tags and usage instructions.
    
    Args:
        original_prompt: The original LLM prompt
        rag_context: Retrieved context string (or None)
        include_instructions: Whether to include usage instructions
    
    Returns:
        Enhanced prompt with RAG context
    """
    if not rag_context:
        return original_prompt
    
    # Build context block
    context_block = f"<external_context>\n{rag_context}\n</external_context>"
    
    # Build instructions
    if include_instructions:
        instructions = """
<rag_instructions>
You have access to external news and market context above. Use this information to:
1. Cross-reference anomalies with real-world events (news, regulatory actions, market events)
2. Add specific dates and events that may explain observed patterns
3. Cite sources when referencing external information (use [Source] notation)
4. Do NOT fabricate information not present in the data or external context
5. If external context contradicts the data, acknowledge the discrepancy
</rag_instructions>
"""
    else:
        instructions = ""
    
    # Inject before the data section
    enhanced_prompt = f"{instructions}\n{context_block}\n\n{original_prompt}"
    
    return enhanced_prompt


def get_rag_stats(
    marketvenueid: str,
    pairid: str
) -> Dict:
    """Get statistics about available RAG context. 🌰
    
    Useful for debugging and monitoring.
    
    Returns:
        Dict with stats about fetched articles, chunks, etc.
    """
    stats = {
        'exchange': marketvenueid,
        'pair': pairid,
        'articles_found': 0,
        'articles_extracted': 0,
        'chunks_created': 0,
        'relevant_chunks': 0,
        'context_chars': 0,
    }
    
    try:
        articles = fetch_all_sources(
            marketvenueid=marketvenueid,
            pairid=pairid,
            max_total=10
        )
        stats['articles_found'] = len(articles)
        
        if articles:
            extracted = batch_extract_articles(articles, max_articles=5)
            stats['articles_extracted'] = len(extracted)
            
            if extracted:
                chunks = chunk_articles(extracted)
                stats['chunks_created'] = len(chunks)
                
                relevant = filter_relevant_chunks(chunks, marketvenueid, pairid)
                stats['relevant_chunks'] = len(relevant)
                
                context = format_context(relevant[:5], max_chars=3000)
                stats['context_chars'] = len(context)
    
    except Exception as e:
        stats['error'] = str(e)
    
    return stats