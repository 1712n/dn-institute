"""RAG Extractor Module - Extracts clean text from HTML articles. 🌰

Uses BeautifulSoup for HTML parsing with multiple fallback strategies
to extract the main article content, stripping navigation, ads, and boilerplate.
"""

import requests
import re
from typing import Optional, Dict
from urllib.parse import urlparse


def extract_article_content(
    url: str,
    max_chars: int = 5000,
    timeout: int = 10
) -> Optional[Dict]:
    """Extract clean text content from an article URL. 🌰
    
    Downloads HTML and extracts main content using multiple strategies:
    1. Look for <article> tag
    2. Look for <main> tag or role="main"
    3. Look for common content divs (class contains 'content', 'article', 'post')
    4. Fall back to <body> with aggressive cleanup
    
    Args:
        url: Article URL to extract from
        max_chars: Maximum characters to extract (controls token usage)
        timeout: Request timeout in seconds
    
    Returns:
        Dict with 'title', 'content', 'url', 'source' or None on failure
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        html = response.text
        
        # Try to import BeautifulSoup (fallback to regex if not available)
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 
                           'iframe', 'form', 'button', 'input', 'select', 
                           'advertisement', 'ad', 'ads']):
                tag.decompose()
            
            # Strategy 1: Look for <article>
            article_tag = soup.find('article')
            if article_tag:
                content = article_tag.get_text(separator=' ', strip=True)
            
            # Strategy 2: Look for <main> or role="main"
            elif soup.find('main') or soup.find(attrs={'role': 'main'}):
                main_tag = soup.find('main') or soup.find(attrs={'role': 'main'})
                content = main_tag.get_text(separator=' ', strip=True)
            
            # Strategy 3: Look for content-related divs
            else:
                content_divs = soup.find_all(['div', 'section'], class_=re.compile(
                    r'content|article|post|story|entry|text|body', re.I
                ))
                if content_divs:
                    # Pick the largest content div
                    content_div = max(content_divs, key=lambda d: len(d.get_text()))
                    content = content_div.get_text(separator=' ', strip=True)
                else:
                    # Strategy 4: Fall back to body
                    body = soup.find('body')
                    if body:
                        content = body.get_text(separator=' ', strip=True)
                    else:
                        content = soup.get_text(separator=' ', strip=True)
            
            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else ''
            
            # Also try h1 for better title
            h1 = soup.find('h1')
            if h1 and len(h1.get_text(strip=True)) < 200:
                title = h1.get_text(strip=True)
            
        except ImportError:
            # BeautifulSoup not available, use regex-based extraction
            print("[RAG] BeautifulSoup not available, using regex extraction 🌰")
            
            # Remove script and style tags
            html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.I)
            html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL|re.I)
            
            # Remove all tags, keep text
            content = re.sub(r'<[^>]+>', ' ', html)
            
            # Extract title
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.I)
            title = title_match.group(1).strip() if title_match else ''
            
            # Clean up whitespace
            content = re.sub(r'\s+', ' ', content).strip()
        
        # Clean up content
        content = _clean_text(content)
        
        # Truncate to max_chars
        if len(content) > max_chars:
            content = content[:max_chars].rsplit(' ', 1)[0] + '...'
        
        # Skip if content is too short (likely failed extraction)
        if len(content) < 100:
            print(f"[RAG] Content too short ({len(content)} chars), skipping: {url}")
            return None
        
        # Extract source from URL
        parsed = urlparse(url)
        source = parsed.netloc.replace('www.', '')
        
        return {
            'title': title[:200],  # Limit title length
            'content': content,
            'url': url,
            'source': source,
        }
        
    except requests.RequestException as e:
        print(f"[RAG] Failed to fetch {url}: {e}")
        return None
    except Exception as e:
        print(f"[RAG] Failed to extract from {url}: {e}")
        return None


def _clean_text(text: str) -> str:
    """Clean extracted text by removing boilerplate and normalizing. 🌰"""
    
    # Remove common boilerplate patterns
    boilerplate_patterns = [
        r'Subscribe to.*?newsletter',
        r'Sign up for.*?email',
        r'Follow us on.*?(Twitter|Facebook|LinkedIn|Instagram)',
        r'Share this article',
        r'Read more.*?articles',
        r'Click here to.*?',
        r'Cookie.*?policy',
        r'Privacy.*?policy',
        r'Advertisement',
        r'Ad\s*content',
        r'Sponsored',
        r'Related articles',
        r'Tags:\s*',
        r'Published on',
        r'Last updated',
        r'Author:\s*',
        r'By\s+[A-Z][a-z]+\s+[A-Z][a-z]+',  # Author names
    ]
    
    for pattern in boilerplate_patterns:
        text = re.sub(pattern, '', text, flags=re.I)
    
    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r'\s+', ' ', text)
    
    # Remove URLs in text
    text = re.sub(r'https?://\S+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+\.\S+', '', text)
    
    return text.strip()


def batch_extract_articles(
    articles: list,
    max_chars: int = 3000,
    max_articles: int = 5,
    timeout: int = 10
) -> list:
    """Extract content from multiple articles. 🌰
    
    Args:
        articles: List of article dicts with 'url' field
        max_chars: Max chars per article
        max_articles: Max articles to process
        timeout: Request timeout
    
    Returns:
        List of extracted article dicts
    """
    extracted = []
    
    for article in articles[:max_articles]:
        url = article.get('url', '')
        if not url:
            continue
        
        result = extract_article_content(url, max_chars, timeout)
        if result:
            # Preserve original metadata
            result['published_at'] = article.get('published_at', '')
            result['original_title'] = article.get('title', result['title'])
            extracted.append(result)
    
    print(f"[RAG] Extracted {len(extracted)} articles with full content 🌰")
    
    return extracted