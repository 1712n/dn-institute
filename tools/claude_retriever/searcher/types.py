from dataclasses import dataclass
from abc import ABC, abstractmethod

import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir) 


#########################################################
## Search Tool: A wrapper around a searcher with instructions and formatting to help Claude use it
#########################################################

@dataclass
class SearchResult:
    """
    A single search result.
    """
    content: str

class Tool(ABC):
    tool_description: str

class SearchTool(Tool):
    """
    A search tool that can run a query and return a formatted string of search results.
    """

    def __init__(self, tool_description: str):
        self.tool_description = tool_description

    @abstractmethod
    def raw_search(self, query: str, n_search_results_to_use: int) -> list[SearchResult]:
        """
        Runs a query using the searcher, then returns the raw search results without formatting.

        :param query: The query to run.
        :param n_search_results_to_use: The number of results to return.
        """
        raise NotImplementedError()
    
    @abstractmethod
    def process_raw_search_results(
        self, results: list[SearchResult],
    ) -> list[str]:
        """
        Extracts the raw search content from the search results and returns a list of strings that can be passed to Claude.

        :param results: The search results to extract.
        """
        raise NotImplementedError()
    
    def search(self, query: str, n_search_results_to_use: int) -> str:
        from utils import format_results_full # Avoids circular import

        raw_search_results = self.raw_search(query, n_search_results_to_use)
        processed_search_results = self.process_raw_search_results(raw_search_results)
        displayable_search_results = format_results_full(processed_search_results)
        return displayable_search_results 



