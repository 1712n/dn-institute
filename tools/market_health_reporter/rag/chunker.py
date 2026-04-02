"""RAG Chunker Module - Splits text into semantic chunks. 🌰

Implements sentence-aware chunking with overlap to preserve context
across chunk boundaries for better retrieval quality.
"""

import re
from typing import List, Dict


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences, preserving boundaries. 🌰"""
    
    # Handle common abbreviations to avoid incorrect splits
    abbreviations = [
        r'\bDr\.', r'\bMr\.', r'\bMs\.', r'\bMrs\.',
        r'\bProf\.', r'\bInc\.', r'\bLtd\.', r'\bCorp\.',
        r'\bU\.S\.', r'\bU\.K\.', r'\bE\.U\.',
        r'\be\.g\.', r'\bi\.e\.', r'\bvs\.',
    ]
    
    # Temporarily replace abbreviations
    protected_text = text
    for abbrev in abbreviations:
        protected_text = re.sub(abbrev, abbrev.replace('.', '<DOT>'), protected_text)
    
    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', protected_text)
    
    # Restore abbreviations
    sentences = [s.replace('<DOT>', '.') for s in sentences]
    
    # Filter empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return sentences


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
    preserve_sentences: bool = True
) -> List[str]:
    """Split text into overlapping chunks. 🌰
    
    Args:
        text: Text to chunk
        chunk_size: Target chunk size in characters
        overlap: Overlap between chunks in characters
        preserve_sentences: Whether to respect sentence boundaries
    
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    
    if preserve_sentences:
        sentences = split_into_sentences(text)
        
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_len = len(sentence)
            
            if current_length + sentence_len > chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append(chunk_text)
                
                # Start new chunk with overlap (last few sentences)
                overlap_sentences = []
                overlap_len = 0
                for s in reversed(current_chunk):
                    if overlap_len + len(s) <= overlap:
                        overlap_sentences.insert(0, s)
                        overlap_len += len(s)
                    else:
                        break
                
                current_chunk = overlap_sentences
                current_length = overlap_len
            
            current_chunk.append(sentence)
            current_length += sentence_len + 1  # +1 for space
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
    
    else:
        # Simple character-based chunking
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
    
    return chunks


def chunk_articles(
    articles: List[Dict],
    chunk_size: int = 500,
    overlap: int = 50
) -> List[Dict]:
    """Chunk multiple articles with metadata preservation. 🌰
    
    Args:
        articles: List of article dicts with 'content' field
        chunk_size: Target chunk size
        overlap: Overlap between chunks
    
    Returns:
        List of chunk dicts with 'text', 'source', 'url', 'title', 'chunk_idx'
    """
    all_chunks = []
    
    for article in articles:
        content = article.get('content', '')
        if not content:
            continue
        
        chunks = chunk_text(content, chunk_size, overlap)
        
        for idx, chunk_text in enumerate(chunks):
            all_chunks.append({
                'text': chunk_text,
                'source': article.get('source', ''),
                'url': article.get('url', ''),
                'title': article.get('title', ''),
                'chunk_idx': idx,
                'total_chunks': len(chunks),
            })
    
    print(f"[RAG] Created {len(all_chunks)} chunks from {len(articles)} articles 🌰")
    
    return all_chunks


def filter_relevant_chunks(
    chunks: List[Dict],
    marketvenueid: str,
    pairid: str,
    min_relevance: float = 0.1
) -> List[Dict]:
    """Filter chunks by relevance to the market context. 🌰
    
    Uses simple keyword matching for relevance scoring.
    More sophisticated semantic similarity would require embeddings.
    
    Args:
        chunks: List of chunk dicts
        marketvenueid: Exchange identifier
        pairid: Trading pair
        min_relevance: Minimum relevance score to include
    
    Returns:
        Filtered list of chunks with 'relevance' score added
    """
    # Build relevance keywords
    exchange_keywords = _get_exchange_keywords(marketvenueid)
    pair_keywords = _get_pair_keywords(pairid)
    manipulation_keywords = [
        'manipulation', 'wash trading', 'fraud', 'scam', 'fake volume',
        'market abuse', 'insider trading', 'pump and dump', 'spoofing',
        'suspicious', 'anomaly', 'investigation', 'regulator', 'sec',
        'commodity futures', 'cftc', 'enforcement', 'illegal',
    ]
    
    scored_chunks = []
    
    for chunk in chunks:
        text_lower = chunk['text'].lower()
        
        # Calculate relevance score
        score = 0.0
        
        # Exchange mentions (high weight)
        for kw in exchange_keywords:
            if kw.lower() in text_lower:
                score += 0.3
        
        # Pair/token mentions (high weight)
        for kw in pair_keywords:
            if kw.lower() in text_lower:
                score += 0.25
        
        # Manipulation keywords (medium weight)
        for kw in manipulation_keywords:
            if kw.lower() in text_lower:
                score += 0.1
        
        # Normalize score (cap at 1.0)
        score = min(score, 1.0)
        
        if score >= min_relevance:
            chunk['relevance'] = score
            scored_chunks.append(chunk)
    
    # Sort by relevance
    scored_chunks.sort(key=lambda c: c['relevance'], reverse=True)
    
    print(f"[RAG] Filtered to {len(scored_chunks)} relevant chunks (from {len(chunks)}) 🌰")
    
    return scored_chunks


def _get_exchange_keywords(exchange: str) -> List[str]:
    """Get keywords for exchange identification. 🌰"""
    aliases = {
        'huobi': ['Huobi', 'HTX', 'Houbi'],
        'htx': ['HTX', 'Huobi'],
        'okex': ['OKEx', 'OKX', 'Okex'],
        'okx': ['OKX', 'OKEx'],
        'gateio': ['Gate.io', 'Gate', 'Gateio'],
        'gate-io': ['Gate.io', 'Gate'],
        'coinbase': ['Coinbase', 'Coinbase Pro', 'GDAX'],
        'binance': ['Binance', 'BNB'],
        'kraken': ['Kraken'],
        'ftx': ['FTX'],
        'kucoin': ['KuCoin', 'Kucoin'],
        'bybit': ['Bybit'],
        'bitfinex': ['Bitfinex'],
    }
    return aliases.get(exchange.lower(), [exchange])


def _get_pair_keywords(pair: str) -> List[str]:
    """Get keywords for trading pair identification. 🌰"""
    pair_upper = pair.upper()
    
    # Extract base token
    common_quotes = ['USDT', 'USD', 'BTC', 'ETH', 'BUSD', 'USDC', 'EUR']
    base_token = pair_upper
    quote_token = ''
    
    for quote in common_quotes:
        if pair_upper.endswith(quote):
            base_token = pair_upper[:-len(quote)]
            quote_token = quote
            break
    
    keywords = [pair_upper, pair, base_token]
    if quote_token:
        keywords.append(quote_token)
    
    # Add common token names
    token_aliases = {
        'BTC': ['Bitcoin', 'BTC'],
        'ETH': ['Ethereum', 'ETH'],
        'DOGE': ['Dogecoin', 'DOGE'],
        'TRX': ['Tron', 'TRX', 'TRON'],
        'HT': ['Huobi Token', 'HT'],
        'SOL': ['Solana', 'SOL'],
        'XRP': ['Ripple', 'XRP'],
        'ADA': ['Cardano', 'ADA'],
        'LINK': ['Chainlink', 'LINK'],
        'DOT': ['Polkadot', 'DOT'],
        'AVAX': ['Avalanche', 'AVAX'],
        'MATIC': ['Polygon', 'MATIC'],
        'SHIB': ['Shiba Inu', 'SHIB'],
        'LTC': ['Litecoin', 'LTC'],
        'BNB': ['Binance Coin', 'BNB'],
        'ATOM': ['Cosmos', 'ATOM'],
        'UNI': ['Uniswap', 'UNI'],
        'XMR': ['Monero', 'XMR'],
        'ZEC': ['Zcash', 'ZEC'],
    }
    
    if base_token in token_aliases:
        keywords.extend(token_aliases[base_token])
    
    return keywords