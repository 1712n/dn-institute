"""RAG Sources Module - Fetches news from multiple external APIs. 🌰

Supports:
- CryptoPanic API (crypto-focused news aggregator)
- NewsAPI (general news with crypto filter)
- Web search fallback via DuckDuckGo HTML scraping (no API key required)
"""

import requests
import time
import re
from typing import List, Dict, Optional, Tuple
from urllib.parse import quote_plus


def fetch_cryptopanic_news(
    currencies: str,
    api_token: Optional[str] = None,
    max_articles: int = 5
) -> List[Dict]:
    """Fetch news from CryptoPanic API. 🌰
    
    CryptoPanic is a crypto-focused news aggregator with free API access.
    
    Args:
        currencies: Comma-separated currency symbols (e.g., 'BTC,ETH')
        api_token: Optional CryptoPanic API token for higher limits
        max_articles: Maximum number of articles to fetch
    
    Returns:
        List of article dicts with title, url, source, published_at
    """
    articles = []
    
    # CryptoPanic free endpoint (works without token, limited results)
    base_url = "https://cryptopanic.com/api/v1/posts/"
    
    params = {
        'currencies': currencies.upper(),
        'filter': 'rising',  # Focus on trending/important news
    }
    
    if api_token:
        params['api_token'] = api_token
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        for post in data.get('results', [])[:max_articles]:
            articles.append({
                'title': post.get('title', ''),
                'url': post.get('url', ''),
                'source': post.get('source', {}).get('title', 'CryptoPanic'),
                'published_at': post.get('created_at', ''),
                'kind': post.get('kind', 'news'),
                'currencies': [c.get('code', '') for c in post.get('currencies', [])],
            })
        
        print(f"[RAG] CryptoPanic: fetched {len(articles)} articles for {currencies} 🌰")
        
    except requests.RequestException as e:
        print(f"[RAG] CryptoPanic fetch failed: {e}")
    
    return articles


def fetch_newsapi_news(
    query: str,
    api_key: Optional[str] = None,
    max_articles: int = 5,
    days_back: int = 30
) -> List[Dict]:
    """Fetch news from NewsAPI. 🌰
    
    Args:
        query: Search query (e.g., 'Huobi crypto manipulation')
        api_key: NewsAPI API key (required)
        max_articles: Maximum articles to fetch
        days_back: How many days back to search
    
    Returns:
        List of article dicts
    """
    if not api_key:
        print("[RAG] NewsAPI: no API key provided, skipping")
        return []
    
    articles = []
    base_url = "https://newsapi.org/v2/everything"
    
    from_date = time.strftime('%Y-%m-%d', time.localtime(time.time() - days_back * 86400))
    to_date = time.strftime('%Y-%m-%d')
    
    params = {
        'q': query,
        'apiKey': api_key,
        'sortBy': 'relevancy',
        'pageSize': max_articles,
        'from': from_date,
        'to': to_date,
        'language': 'en',
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        for article in data.get('articles', [])[:max_articles]:
            articles.append({
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'source': article.get('source', {}).get('name', 'NewsAPI'),
                'published_at': article.get('publishedAt', ''),
                'description': article.get('description', ''),
            })
        
        print(f"[RAG] NewsAPI: fetched {len(articles)} articles for '{query}' 🌰")
        
    except requests.RequestException as e:
        print(f"[RAG] NewsAPI fetch failed: {e}")
    
    return articles


def fetch_duckduckgo_news(
    query: str,
    max_articles: int = 5
) -> List[Dict]:
    """Fetch news via DuckDuckGo HTML scraping (no API key required). 🌰
    
    This is a fallback source that works without any API credentials.
    Uses DDG's instant answers and news results.
    
    Args:
        query: Search query
        max_articles: Maximum articles to fetch
    
    Returns:
        List of article dicts
    """
    articles = []
    
    # DuckDuckGo HTML search (no API, works freely)
    search_url = f"https://duckduckgo.com/html/?q={quote_plus(query + ' crypto news')}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html',
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
        html = response.text
        
        # Parse results from HTML (simple regex-based extraction)
        # DDG HTML format: <a class="result__a" href="...">Title</a>
        result_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>'
        matches = re.findall(result_pattern, html)[:max_articles]
        
        for url, title in matches:
            # Clean up DDG redirect URLs
            if 'uddg=' in url:
                actual_url = url.split('uddg=')[-1].split('&')[0]
                actual_url = requests.utils.unquote(actual_url)
            else:
                actual_url = url
            
            articles.append({
                'title': title.strip(),
                'url': actual_url,
                'source': 'DuckDuckGo',
                'published_at': '',
            })
        
        print(f"[RAG] DuckDuckGo: fetched {len(articles)} articles for '{query}' 🌰")
        
    except requests.RequestException as e:
        print(f"[RAG] DuckDuckGo fetch failed: {e}")
    
    return articles


def build_search_query(
    marketvenueid: str,
    pairid: str,
    keywords: List[str] = None
) -> str:
    """Build a search query for the market context. 🌰
    
    Args:
        marketvenueid: Exchange name (e.g., 'huobi', 'binance')
        pairid: Trading pair (e.g., 'btcusdt')
        keywords: Additional keywords to include
    
    Returns:
        Search query string
    """
    # Exchange aliases for better search results
    exchange_aliases = {
        'huobi': ['Huobi', 'HTX'],
        'htx': ['HTX', 'Huobi'],
        'okex': ['OKEx', 'OKX'],
        'okx': ['OKX', 'OKEx'],
        'gateio': ['Gate.io', 'Gate'],
        'gate-io': ['Gate.io', 'Gate'],
        'coinbase': ['Coinbase', 'Coinbase Pro'],
        'kraken': ['Kraken'],
        'binance': ['Binance'],
        'ftx': ['FTX'],
        'kucoin': ['KuCoin'],
    }
    
    # Extract tokens from pair
    pair_upper = pairid.upper()
    tokens = []
    common_pairs = ['USDT', 'USD', 'BTC', 'ETH', 'BUSD']
    for stable in common_pairs:
        if pair_upper.endswith(stable):
            base = pair_upper[:-len(stable)]
            tokens = [base, stable]
            break
    
    if not tokens:
        # Try to split at common boundaries
        tokens = [pair_upper[:3], pair_upper[3:]] if len(pair_upper) >= 6 else [pair_upper]
    
    # Build exchange names
    exchange_names = exchange_aliases.get(marketvenueid.lower(), [marketvenueid])
    
    # Build query
    query_parts = [exchange_names[0]]
    if tokens:
        query_parts.append(tokens[0])
    
    # Add manipulation-related keywords
    if keywords:
        query_parts.extend(keywords)
    else:
        query_parts.extend(['market', 'trading'])
    
    return ' '.join(query_parts)


def deduplicate_articles(articles: List[Dict]) -> List[Dict]:
    """Remove duplicate articles based on URL and title similarity. 🌰"""
    seen_urls = set()
    seen_titles = set()
    unique = []
    
    for article in articles:
        url = article.get('url', '')
        title = article.get('title', '').lower()
        
        # Skip if URL already seen
        if url and url in seen_urls:
            continue
        
        # Skip if very similar title already seen
        title_words = set(title.split())
        is_duplicate = False
        for seen_title in seen_titles:
            seen_words = set(seen_title.split())
            overlap = len(title_words & seen_words) / max(len(title_words), len(seen_words), 1)
            if overlap > 0.8:  # 80% word overlap = duplicate
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique.append(article)
            if url:
                seen_urls.add(url)
            seen_titles.add(title)
    
    return unique


def fetch_all_sources(
    marketvenueid: str,
    pairid: str,
    cryptopanic_token: Optional[str] = None,
    newsapi_key: Optional[str] = None,
    max_total: int = 10
) -> List[Dict]:
    """Fetch news from all available sources. 🌰
    
    Args:
        marketvenueid: Exchange identifier
        pairid: Trading pair
        cryptopanic_token: Optional CryptoPanic API token
        newsapi_key: Optional NewsAPI key
        max_total: Maximum total articles to return
    
    Returns:
        Deduplicated list of articles
    """
    query = build_search_query(marketvenueid, pairid, ['manipulation', 'wash trading'])
    
    # Extract currencies for CryptoPanic
    currencies = pairid.upper()[:3] if len(pairid) >= 3 else pairid.upper()
    
    all_articles = []
    
    # Try CryptoPanic first (crypto-focused)
    if cryptopanic_token:
        all_articles.extend(fetch_cryptopanic_news(currencies, cryptopanic_token, max_total // 2))
    
    # Try NewsAPI
    if newsapi_key:
        all_articles.extend(fetch_newsapi_news(query, newsapi_key, max_total // 2))
    
    # Always try DuckDuckGo as fallback (free, no API key)
    if len(all_articles) < max_total:
        all_articles.extend(fetch_duckduckgo_news(query, max_total - len(all_articles)))
    
    # Deduplicate
    unique_articles = deduplicate_articles(all_articles)
    
    print(f"[RAG] Total unique articles: {len(unique_articles)} 🌰")
    
    return unique_articles[:max_total]