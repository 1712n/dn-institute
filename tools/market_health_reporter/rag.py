"""
RAG (Retrieval Augmented Generation) module for the Market Health Reporter.

Retrieves relevant external articles and news about exchanges and trading pairs
to provide additional context for market analysis report generation.
"""

import re
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import ddg


# Maximum number of search results to fetch per query
MAX_SEARCH_RESULTS = 5
# Maximum character length for extracted article content
MAX_CONTENT_LENGTH = 2000
# Request timeout in seconds
REQUEST_TIMEOUT = 10
# Maximum total context length (characters) to avoid overwhelming the prompt
MAX_TOTAL_CONTEXT_LENGTH = 15000


def build_search_queries(marketvenueid: str, pairid: str, start: str, end: str) -> list:
    """
    Build a list of search queries based on market analysis parameters.

    Args:
        marketvenueid: Exchange identifier (e.g., 'binance')
        pairid: Trading pair identifier (e.g., 'btc-usdt')
        start: Start date of analysis period
        end: End date of analysis period

    Returns:
        List of search query strings
    """
    base_token = pairid.split('-')[0].upper()
    exchange_name = marketvenueid.capitalize()

    queries = [
        f"{exchange_name} {base_token} wash trading manipulation {start} {end}",
        f"{exchange_name} exchange trading volume anomaly {start}",
        f"{exchange_name} cryptocurrency market manipulation suspicious activity",
        f"{base_token} fake volume wash trading detection",
    ]
    return queries


def search_web(query: str, max_results: int = MAX_SEARCH_RESULTS) -> list:
    """
    Search the web using DuckDuckGo and return a list of results.

    Args:
        query: Search query string
        max_results: Maximum number of results to return

    Returns:
        List of dicts with 'title', 'href', and 'body' keys
    """
    try:
        results = ddg(query, max_results=max_results)
        if results:
            return results
    except Exception as e:
        print(f"Search error for query '{query}': {e}")
    return []


def extract_article_content(url: str) -> str:
    """
    Fetch a URL and extract the main text content from the page.

    Args:
        url: The URL to fetch and extract content from

    Returns:
        Extracted text content, truncated to MAX_CONTENT_LENGTH
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; MarketHealthReporter/1.0)'
        }
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script, style, nav, footer, header elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header',
                             'aside', 'form', 'iframe']):
            element.decompose()

        # Extract text from article or main content areas
        article = soup.find('article') or soup.find('main') or soup.find('body')
        if article is None:
            return ""

        text = article.get_text(separator='\n', strip=True)
        # Clean up excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)

        return text[:MAX_CONTENT_LENGTH]

    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return ""


def deduplicate_results(results: list) -> list:
    """
    Remove duplicate search results based on URL.

    Args:
        results: List of search result dicts

    Returns:
        Deduplicated list of search results
    """
    seen_urls = set()
    unique_results = []
    for result in results:
        url = result.get('href', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(result)
    return unique_results


def retrieve_context(marketvenueid: str, pairid: str, start: str, end: str) -> str:
    """
    Main RAG function: searches for relevant articles and retrieves their content
    to build additional context for the market analysis.

    Args:
        marketvenueid: Exchange identifier (e.g., 'binance')
        pairid: Trading pair identifier (e.g., 'btc-usdt')
        start: Start date of analysis period
        end: End date of analysis period

    Returns:
        Formatted string containing retrieved article context
    """
    queries = build_search_queries(marketvenueid, pairid, start, end)

    all_results = []
    for query in queries:
        results = search_web(query)
        all_results.extend(results)

    unique_results = deduplicate_results(all_results)
    print(f"RAG: Found {len(unique_results)} unique search results")

    context_parts = []
    total_length = 0

    for result in unique_results:
        if total_length >= MAX_TOTAL_CONTEXT_LENGTH:
            break

        url = result.get('href', '')
        title = result.get('title', 'Unknown')
        snippet = result.get('body', '')

        content = extract_article_content(url)
        if not content:
            # Fall back to the search snippet if we can't fetch the page
            content = snippet

        if content:
            entry = f"### Source: {title}\nURL: {url}\n{content}\n"
            context_parts.append(entry)
            total_length += len(entry)

    if not context_parts:
        print("RAG: No external context retrieved")
        return ""

    context = "\n---\n".join(context_parts)
    print(f"RAG: Retrieved context from {len(context_parts)} sources "
          f"({total_length} characters)")
    return context


def format_rag_context(context: str) -> str:
    """
    Format retrieved context for inclusion in the LLM prompt.

    Args:
        context: Raw retrieved context string

    Returns:
        Formatted context wrapped in XML tags for the prompt
    """
    if not context:
        return ""

    return (
        "<external_context>\n"
        "The following external articles and news provide additional context "
        "about the exchange and trading pair being analyzed. Use this information "
        "to enrich your analysis with relevant market events, known issues, "
        "or regulatory actions that may explain observed anomalies.\n\n"
        f"{context}\n"
        "</external_context>"
    )
