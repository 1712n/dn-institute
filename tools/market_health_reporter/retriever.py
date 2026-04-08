import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

try:
    # Attempt to import duckduckgo_search for real web retrieval 🌰
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    # Fallback to a mock retriever if duckduckgo_search is not installed 🌰
    logger.warning("duckduckgo_search not installed. RAG will use a mock retriever. 🌰 "
                   "Install with 'pip install duckduckgo_search' for full functionality! 🌰")
    DDGS_AVAILABLE = False

def _mock_web_search(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """
    A mock web search function for demonstration or when DDGS is not available. 🌰
    Provides generic but relevant-sounding snippets.
    """
    logger.info(f"Performing mock web search for: '{query}' with {max_results} results. 🌰")
    mock_results = [
        {"title": f"📈 Market Overview: Key Trends for {query}", "body": f"This is a mocked summary of an article related to '{query}', discussing general market trends and economic impacts. It provides a broad understanding of the current market climate and sentiment. 🌰", "href": "http://example.com/mock_market_trend"},
        {"title": f"💡 Expert Analysis: Deep Dive into {query} Factors", "body": f"Another mocked piece of content, focusing on specific industry effects or historical precedents for '{query}'. It adds depth to the context, highlighting potential causes and ripple effects. 🌰", "href": "http://example.com/mock_expert_analysis"},
        {"title": f"🔮 Future Outlook: Projections and Risks for {query}", "body": f"A third mocked snippet offering an expert's view or a future outlook pertaining to '{query}'. This helps round out the contextual information with forward-looking statements. 🌰", "href": "http://example.com/mock_future_outlook"},
        {"title": f"📊 Data Insight: Recent Performance of {query} Components", "body": f"A fourth mocked snippet providing data-driven insights into components or related assets of '{query}'. 🌰", "href": "http://example.com/mock_data_insight"},
    ]
    return mock_results[:max_results]

def retrieve_context(query: str, num_results: int = 3) -> str:
    """
    Retrieves relevant article context from external resources using web search. 🌰
    Prioritizes real web search (DDGS) and falls back to a mock if unavailable or errors occur.

    :param query: The search query string for external context.
    :param num_results: The maximum number of search results to retrieve.
    :return: A combined string of snippets from external resources, formatted as context.
    """
    search_results = []
    if DDGS_AVAILABLE:
        try:
            logger.info(f"Performing real web search for: '{query}' with {num_results} results. 🌰")
            with DDGS() as ddgs:
                # Use DDGS.text to get text-based search results
                # Setting safesearch to 'moderate' and time to 'y' (past year) for relevant, recent articles.
                search_results = list(ddgs.text(keywords=query, max_results=num_results, safesearch='moderate', time='y'))
            if not search_results:
                logger.warning(f"No real search results found for '{query}'. Falling back to mock retriever. 🌰")
                search_results = _mock_web_search(query, num_results)
        except Exception as e:
            logger.error(f"Error during DDGS search for '{query}': {e}. Falling back to mock retriever. 🌰")
            search_results = _mock_web_search(query, num_results)
    else:
        search_results = _mock_web_search(query, num_results)

    context_snippets = []
    for i, result in enumerate(search_results):
        title = result.get('title', f'Untitled Source {i+1}')
        body = result.get('body', 'No summary available.')
        href = result.get('href', '#')
        context_snippets.append(f"Source {i+1} - Title: {title}\nURL: {href}\nSnippet: {body}\n")
    
    if not context_snippets:
        return "No additional external context found for the query. 🌰"
    
    combined_context = "\n---\n".join(context_snippets)
    return f"🌰🌰🌰 Additional Context from External Resources: 🌰🌰🌰\n{combined_context}\n🌰🌰🌰 End of Additional Context 🌰🌰🌰"

if __name__ == '__main__':
    # Example usage for testing the retriever 🌰
    logging.basicConfig(level=logging.INFO)
    print("\n--- Testing retrieve_context with real-world query --- 🌰")
    test_query_real = "Bitcoin price surge institutional adoption 2023"
    context_real = retrieve_context(test_query_real, num_results=2)
    print(f"\nRetrieved Context for '{test_query_real}':\n{context_real}\n")

    print("--- Testing retrieve_context with mock fallback --- 🌰")
    test_query_mock = "imaginary market spike due to chestnut demand"
    context_mock = retrieve_context(test_query_mock, num_results=1) # Should hit mock for specific terms
    print(f"\nRetrieved Context (mock) for '{test_query_mock}':\n{context_mock}\n")

    print("--- Testing retrieve_context with no search results (should fallback) --- 🌰")
    DDGS_AVAILABLE = False # Temporarily force mock
    test_query_no_results = "nonexistent cryptocurrency market crash"
    context_no_results = retrieve_context(test_query_no_results, num_results=0) # Requesting 0 results means mock will return default mock_results
    print(f"\nRetrieved Context (mock, 0 results requested) for '{test_query_no_results}':\n{context_no_results}\n")

