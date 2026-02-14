import os
import asyncio
from typing import Optional
from tools.article_checker.claude_retriever.searcher.types import SearchResult, SearchTool
from tools.article_checker.claude_retriever.utils import scrape_url
from dataclasses import dataclass
import requests
from tenacity import retry, wait_exponential, stop_after_attempt

import logging
logger = logging.getLogger(__name__)

@dataclass
class WebSearchResult(SearchResult):
    url: str

# Brave Searcher

BRAVE_DESCRIPTION = """Brave Search Engine Tool: The search engine will search using the Brave search engine for web pages with keywords similar to your query. It returns for each page its title, a summary and potentially the full page content. Use this tool if you want to get up-to-date and comprehensive information on a topic. Best practices: include specific entity names, dates, and amounts in your queries for more precise results on crypto security incidents."""

class BraveAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(10))
    def search(self, query: str) -> dict:
        headers = {"Accept": "application/json", "X-Subscription-Token": self.api_key}
        resp = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": query,
                    "count": 20 # Max number of results to return, can filter down later
                    },
            headers=headers,
            timeout=60
        )
        if resp.status_code != 200:
            logger.error(f"Search request failed: {resp.text}")
            return {}
        return resp.json()


def _get_or_create_event_loop():
    """
    Safely get or create an asyncio event loop.
    Handles deprecation of get_event_loop() in Python 3.10+.
    """
    try:
        loop = asyncio.get_running_loop()
        return loop
    except RuntimeError:
        pass
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


class BraveSearchTool(SearchTool):

    def __init__(self, brave_api_key: str,
                 tool_description: str = BRAVE_DESCRIPTION,
                 summarize_with_claude: bool = False,
                 anthropic_api_key: Optional[str] = None):
        """
        :param brave_api_key: The Brave API key to use for searching.
        :param tool_description: The description of the tool.
        :param summarize_with_claude: Whether to summarize the scraped web pages with Claude.
        :param anthropic_api_key: The anthropic API key to use for summarizing with Claude.
        """

        self.api = BraveAPI(brave_api_key)
        self.tool_description = tool_description
        self.summarize_with_claude = summarize_with_claude
        if summarize_with_claude and anthropic_api_key is None:
            try:
                anthropic_api_key = os.environ["ANTHROPIC_API_KEY"]
            except KeyError:
                raise ValueError("If you want to summarize with Claude, you must provide an anthropic_api_key.")
        self.anthropic_api_key = anthropic_api_key

    def parse_faq(self, faq: dict) -> WebSearchResult:
        """
        https://api.search.brave.com/app/documentation/responses#FAQ
        """
        snippet = f"""FAQ Title: {faq.get('title', "Unknown")}
Question: {faq.get('question', "Unknown")}
Answer: {faq.get('answer', "Unknown")}"""
        
        return WebSearchResult(
            url=faq.get("url", ""),
            content=snippet
        )
    
    def parse_news(self, news_item: dict) -> Optional[WebSearchResult]:
        """
        https://api.search.brave.com/app/documentation/responses#News
        """
        article_description: str = news_item.get("description", "")

        # Throw out items where the description is tiny or doesn't exist.
        if len(article_description) < 5:
            return None

        snippet = f"""News Article Title: {news_item.get('title', "Unknown")}
News Article Description: {article_description}
News Article Age: {news_item.get("age", "Unknown")}
News Article Source: {news_item.get("meta_url", {}).get('hostname', "Unknown")}"""
        
        return WebSearchResult(
            url=news_item.get("url", ""),
            content=snippet
        )

    @staticmethod
    def remove_strong(web_description: str):
        # this is for cleaning up the brave web descriptions
        return (
            web_description.replace("<strong>", "")
            .replace("</strong>", "")
            .replace("&#x27;", "'")
        )
    
    async def parse_web(self, web_item: dict, query: str) -> WebSearchResult:
        """
        https://api.search.brave.com/app/documentation/responses#Search
        Parse a web search result with retry logic for scraping.
        """
        url = web_item.get("url", "")
        title = web_item.get("title", "")
        description = self.remove_strong(web_item.get('description', ''))
        snippet = f"""Web Page Title: {title}
Web Page URL: {url}"""

        try:
            if self.summarize_with_claude:
                content = await scrape_url(
                    url, summarize_with_claude=True,
                    anthropic_api_key=self.anthropic_api_key,
                    query=query,
                    max_retries=2
                )
            else:
                content = await scrape_url(url, max_retries=2)

            if content and content != "CONTENT NOT AVAILABLE":
                if content.startswith('<summary>'):
                    snippet += "\nWeb Page Summary: " + content
                else:
                    snippet += "\nWeb Page Content: " + content
            else:
                # Fall back to the Brave search snippet description
                snippet += "\nWeb Page Description: " + description
        except Exception as e:
            logger.warning(f"Failed to scrape {url}: {e}")
            # Fall back to the Brave description
            snippet += "\nWeb Page Description: " + description
            
        return WebSearchResult(
            url=url,
            content=snippet
        )


    def raw_search(self, query: str, n_search_results_to_use: int) -> list[WebSearchResult]:
        """
        Run a search using the BraveAPI and return search results.
        """
        
        # Run the search
        search_response = self.api.search(query)

        # Order everything properly
        correct_ordering = search_response.get("mixed", {}).get("main", [])

        # Extract the results
        faq_items = search_response.get("faq", {}).get("results", [])
        news_items = search_response.get("news", {}).get("results", [])
        web_items = search_response.get("web", {}).get("results", [])

        # Get the search results
        search_results: list[WebSearchResult] = []
        loop = _get_or_create_event_loop()
        web_parsing_tasks = []

        for item in correct_ordering:
            item_type = item.get("type")
            if item_type == "web" and web_items:
                web_item = web_items.pop(0)
                url = web_item.get("url", "")
                placeholder_search_result = WebSearchResult(
                    url=url,
                    content=f"Web Page Title: {web_item.get('title', '')}\nWeb Page URL: {url}\nWeb Page Description: {self.remove_strong(web_item.get('description', ''))}"
                )
                search_results.append(placeholder_search_result)
                task = loop.create_task(self.parse_web(web_item, query))
                web_parsing_tasks.append(task)
            elif item_type == "news" and news_items:
                parsed_news = self.parse_news(news_items.pop(0))
                if parsed_news is not None:
                    search_results.append(parsed_news)
            elif item_type == "faq" and faq_items:
                parsed_faq = self.parse_faq(faq_items.pop(0))
                search_results.append(parsed_faq)
            if len(search_results) >= n_search_results_to_use:
                break

        # Replace the placeholder search results with the parsed web results
        if web_parsing_tasks:
            web_results = loop.run_until_complete(asyncio.gather(*web_parsing_tasks, return_exceptions=True))
            web_results_urls = []
            valid_web_results = []
            for web_result in web_results:
                if isinstance(web_result, Exception):
                    logger.warning(f"Web parsing task failed: {web_result}")
                    continue
                web_results_urls.append(web_result.url)
                valid_web_results.append(web_result)
            
            for i, search_result in enumerate(search_results):
                url = search_result.url
                if url in web_results_urls:
                    idx = web_results_urls.index(url)
                    search_results[i] = valid_web_results[idx]

        return search_results
    
    def process_raw_search_results(self, results: list[SearchResult]) -> list[str]:
        processed_search_results = [result.content.strip() for result in results]
        return processed_search_results
