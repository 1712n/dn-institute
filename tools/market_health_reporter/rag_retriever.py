"""
RAG (Retrieval Augmented Generation) module for Market Health Reporter 🌰
Provides external article context to enhance report generation
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

from config import SERPER_API_KEY, MAX_RAG_ARTICLES, RAG_SEARCH_QUERY_TEMPLATES

logger = logging.getLogger(__name__)

@dataclass
class ArticleContext:
    """Represents an external article with relevant context for market health reports 🌰"""
    title: str
    url: str
    snippet: str
    published_date: str
    source: str
    relevance_score: float

class RAGRetriever:
    """Handles retrieval of external articles for RAG enhancement 🌰"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or SERPER_API_KEY
        self.base_url = "https://google.serper.dev/search"
        
    def search_articles(self, 
                       exchange: str, 
                       metric: str, 
                       spike_date: datetime,
                       days_before: int = 7) -> List[ArticleContext]:
        """
        Search for relevant articles about exchange/metric spike 🌰
        
        Args:
            exchange: Name of the exchange
            metric: Metric that spiked
            spike_date: Date when spike occurred
            days_before: How many days before spike to search
            
        Returns:
            List of relevant ArticleContext objects
        """
        if not self.api_key:
            logger.warning("No SERPER_API_KEY provided, skipping RAG search 🌰")
            return []
            
        articles = []
        search_start = spike_date - timedelta(days=days_before)
        
        # Generate search queries using templates
        for template in RAG_SEARCH_QUERY_TEMPLATES:
            query = template.format(
                exchange=exchange,
                metric=metric,
                date=search_start.strftime("%Y-%m-%d")
            )
            
            try:
                response = self._make_search_request(query)
                articles.extend(self._parse_search_results(response, exchange, metric))
            except Exception as e:
                logger.error(f"Error searching for articles: {e} 🌰")
                
        # Sort by relevance and limit results
        articles.sort(key=lambda x: x.relevance_score, reverse=True)
        return articles[:MAX_RAG_ARTICLES]
    
    def _make_search_request(self, query: str) -> Dict:
        """Make API request to Serper.dev 🌰"""
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        payload = json.dumps({
            "q": query,
            "num": 10,
            "tbm": "nws",
            "gl": "us",
            "hl": "en"
        })
        
        response = requests.post(self.base_url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()
    
    def _parse_search_results(self, response: Dict, exchange: str, metric: str) -> List[ArticleContext]:
        """Parse search results into ArticleContext objects 🌰"""
        articles = []
        
        if "news" not in response:
            return articles
            
        for item in response["news"]:
            # Calculate relevance score based on keyword matches
            title_lower = item.get("title", "").lower()
            snippet_lower = item.get("snippet", "").lower()
            
            score = 0
            keywords = [exchange.lower(), metric.lower(), "crypto", "exchange", "market"]
            
            for keyword in keywords:
                score += title_lower.count(keyword) * 2
                score += snippet_lower.count(keyword)
                
            article = ArticleContext(
                title=item.get("title", ""),
                url=item.get("link", ""),
                snippet=item.get("snippet", ""),
                published_date=item.get("date", ""),
                source=item.get("source", ""),
                relevance_score=score
            )
            
            articles.append(article)
            
        return articles