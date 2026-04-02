"""RAG Retriever Module - Semantic retrieval with fallback. 🌰

Primary: OpenAI embeddings with cosine similarity
Fallback: TF-IDF with cosine similarity (no API key required)
"""

import math
import re
from typing import List, Dict, Optional, Tuple
from collections import Counter


def compute_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute cosine similarity between two vectors. 🌰"""
    
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


def compute_tfidf_vectors(
    documents: List[str],
    query: str
) -> Tuple[List[List[float]], List[float]]:
    """Compute TF-IDF vectors for documents and query. 🌰
    
    Simple TF-IDF implementation without external dependencies.
    
    Args:
        documents: List of document texts
        query: Query text
    
    Returns:
        Tuple of (document_vectors, query_vector)
    """
    # Tokenize all texts
    def tokenize(text: str) -> List[str]:
        # Lowercase, remove punctuation, split on whitespace
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return text.split()
    
    all_docs = documents + [query]
    all_tokens = [tokenize(doc) for doc in all_docs]
    
    # Build vocabulary
    vocab = set()
    for tokens in all_tokens:
        vocab.update(tokens)
    vocab = sorted(vocab)
    
    # Compute document frequencies
    doc_freq = Counter()
    for tokens in all_tokens:
        unique_tokens = set(tokens)
        for token in unique_tokens:
            doc_freq[token] += 1
    
    n_docs = len(all_docs)
    
    # Compute IDF
    idf = {}
    for token in vocab:
        df = doc_freq[token]
        idf[token] = math.log(n_docs / (df + 1)) + 1  # Smoothed IDF
    
    # Compute TF-IDF for each document
    def compute_tfidf(tokens: List[str]) -> List[float]:
        tf = Counter(tokens)
        max_tf = max(tf.values()) if tf else 1
        
        vector = []
        for token in vocab:
            # Normalized TF
            tf_val = tf.get(token, 0) / max_tf
            tfidf_val = tf_val * idf.get(token, 0)
            vector.append(tfidf_val)
        
        return vector
    
    doc_vectors = [compute_tfidf(tokens) for tokens in all_tokens[:-1]]
    query_vector = compute_tfidf(all_tokens[-1])
    
    return doc_vectors, query_vector


def retrieve_with_tfidf(
    chunks: List[Dict],
    query: str,
    top_k: int = 5,
    min_score: float = 0.1
) -> List[Dict]:
    """Retrieve most relevant chunks using TF-IDF. 🌰
    
    Args:
        chunks: List of chunk dicts with 'text' field
        query: Query string
        top_k: Number of top results to return
        min_score: Minimum similarity score
    
    Returns:
        List of chunk dicts with 'similarity' score, sorted by relevance
    """
    if not chunks or not query:
        return []
    
    documents = [chunk['text'] for chunk in chunks]
    doc_vectors, query_vector = compute_tfidf_vectors(documents, query)
    
    # Compute similarities
    scored_chunks = []
    for i, chunk in enumerate(chunks):
        similarity = compute_cosine_similarity(doc_vectors[i], query_vector)
        
        if similarity >= min_score:
            chunk['similarity'] = similarity
            scored_chunks.append(chunk)
    
    # Sort by similarity
    scored_chunks.sort(key=lambda c: c['similarity'], reverse=True)
    
    return scored_chunks[:top_k]


def retrieve_with_embeddings(
    chunks: List[Dict],
    query: str,
    api_key: Optional[str] = None,
    top_k: int = 5,
    min_score: float = 0.5
) -> List[Dict]:
    """Retrieve most relevant chunks using OpenAI embeddings. 🌰
    
    Args:
        chunks: List of chunk dicts
        query: Query string
        api_key: OpenAI API key
        top_k: Number of results
        min_score: Minimum cosine similarity
    
    Returns:
        List of chunk dicts with 'similarity' score
    """
    if not chunks or not query:
        return []
    
    if not api_key:
        print("[RAG] No OpenAI API key, falling back to TF-IDF 🌰")
        return retrieve_with_tfidf(chunks, query, top_k, min_score)
    
    try:
        import openai
        
        openai.api_key = api_key
        
        # Get query embedding
        query_response = openai.Embedding.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = query_response['data'][0]['embedding']
        
        # Get document embeddings (batch)
        texts = [chunk['text'] for chunk in chunks]
        
        # Batch in groups of 100 (API limit)
        all_embeddings = []
        batch_size = 100
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_response = openai.Embedding.create(
                model="text-embedding-3-small",
                input=batch
            )
            batch_embeddings = [d['embedding'] for d in batch_response['data']]
            all_embeddings.extend(batch_embeddings)
        
        # Compute similarities
        scored_chunks = []
        for i, chunk in enumerate(chunks):
            similarity = compute_cosine_similarity(all_embeddings[i], query_embedding)
            
            if similarity >= min_score:
                chunk['similarity'] = similarity
                scored_chunks.append(chunk)
        
        # Sort by similarity
        scored_chunks.sort(key=lambda c: c['similarity'], reverse=True)
        
        print(f"[RAG] OpenAI embeddings: retrieved {len(scored_chunks)} chunks 🌰")
        
        return scored_chunks[:top_k]
        
    except ImportError:
        print("[RAG] OpenAI library not available, falling back to TF-IDF 🌰")
        return retrieve_with_tfidf(chunks, query, top_k, min_score)
    except Exception as e:
        print(f"[RAG] OpenAI embedding failed: {e}, falling back to TF-IDF 🌰")
        return retrieve_with_tfidf(chunks, query, top_k, min_score)


def build_retrieval_query(
    marketvenueid: str,
    pairid: str,
    start_date: str = '',
    end_date: str = ''
) -> str:
    """Build a retrieval query from market parameters. 🌰"""
    
    # Exchange aliases
    exchange_names = {
        'huobi': 'Huobi HTX',
        'htx': 'HTX Huobi',
        'okex': 'OKEx OKX',
        'okx': 'OKX OKEx',
        'gateio': 'Gate.io',
        'binance': 'Binance',
        'coinbase': 'Coinbase',
        'kraken': 'Kraken',
    }
    
    exchange = exchange_names.get(marketvenueid.lower(), marketvenueid)
    
    # Extract tokens from pair
    pair_upper = pairid.upper()
    base_token = pair_upper[:3] if len(pair_upper) >= 3 else pair_upper
    
    # Build query
    query_parts = [
        f"{exchange} {base_token}",
        "market manipulation wash trading",
        "trading volume anomaly",
        "cryptocurrency exchange fraud",
    ]
    
    if start_date and end_date:
        query_parts.append(f"{start_date} {end_date}")
    
    return ' '.join(query_parts)


def retrieve_top_chunks(
    chunks: List[Dict],
    marketvenueid: str,
    pairid: str,
    openai_key: Optional[str] = None,
    top_k: int = 5,
    min_score: float = 0.1
) -> List[Dict]:
    """Retrieve top chunks for the market context. 🌰
    
    Uses embeddings if available, falls back to TF-IDF.
    
    Args:
        chunks: List of chunk dicts
        marketvenueid: Exchange identifier
        pairid: Trading pair
        openai_key: Optional OpenAI API key
        top_k: Number of top chunks
        min_score: Minimum relevance score
    
    Returns:
        List of top chunks with similarity scores
    """
    query = build_retrieval_query(marketvenueid, pairid)
    
    print(f"[RAG] Retrieval query: '{query[:100]}...' 🌰")
    
    # Try embeddings first, fall back to TF-IDF
    if openai_key:
        return retrieve_with_embeddings(chunks, query, openai_key, top_k, min_score)
    else:
        return retrieve_with_tfidf(chunks, query, top_k, min_score)