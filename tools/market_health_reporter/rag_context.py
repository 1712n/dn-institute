"""
RAG Context Retriever for Market Health Reporter 🌰
Fetches relevant external articles and news for market health spikes
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
import tiktoken


class RAGContextRetriever:
    """Retrieves relevant external context for market health spikes using web search"""
    
    def __init__(self, max_articles: int = 5, search_days: int = 7):
        self.max_articles = max_articles
        self.search_days = search_days
        self.serp_api_key = os.getenv('SERP_API_KEY')
        self.encoding = tiktoken.encoding_for_model("gpt-4")
        
    def get_context_for_spike(self, spike: Dict, exchange: str) -> List[Dict[str, str]]:
        """
        Retrieve relevant articles for a specific spike
        
        Args:
            spike: Dictionary containing spike information
            exchange: Exchange name
            
        Returns:
            List of dictionaries with 'title', 'url', 'content', and 'relevance_score'
        """
        if not self.serp_api_key:
            print("Warning: SERP_API_KEY not found, skipping RAG context retrieval 🌰")
            return []
            
        query = self._build_search_query(spike, exchange)
        articles = self._search_articles(query, spike['date'])
        
        # Filter and rank articles by relevance
        filtered_articles = self._filter_relevant_articles(articles, spike)
        
        return filtered_articles[:self.max_articles]
    
    def _build_search_query(self, spike: Dict, exchange: str) -> str:
        """Build search query based on spike information"""
        metric = spike['metric'].replace('_', ' ').title()
        query = f"{exchange} {metric} spike {spike['date']} cryptocurrency news"
        
        # Add specific context based on metric type
        if 'volume' in spike['metric'].lower():
            query += " trading volume"
        elif 'price' in spike['metric'].lower():
            query += " price movement"
        elif 'spread' in spike['metric'].lower():
            query += " bid ask spread"
            
        return query
    
    def _search_articles(self, query: str, spike_date: str) -> List[Dict]:
        """Search for articles using SerpAPI"""
        try:
            # Calculate date range
            spike_dt = datetime.strptime(spike_date, "%Y-%m-%d")
            start_date = (spike_dt - timedelta(days=self.search_days)).strftime("%Y-%m-%d")
            end_date = (spike_dt + timedelta(days=1)).strftime("%Y-%m-%d")
            
            params = {
                "engine": "google",
                "q": query,
                "api_key": self.serp_api_key,
                "tbm": "nws",
                "tbs": f"cdr:1,cd_min:{start_date},cd_max:{end_date}",
                "num": 10
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            articles = []
            if "news_results" in results:
                for result in results["news_results"]:
                    article = {
                        "title": result.get("title", ""),
                        "url": result.get("link", ""),
                        "date": result.get("date", ""),
                        "snippet": result.get("snippet", "")
                    }
                    articles.append(article)
                    
            return articles
            
        except Exception as e:
            print(f"Error searching articles: {e} 🌰")
            return []
    
    def _filter_relevant_articles(self, articles: List[Dict], spike: Dict) -> List[Dict[str, str]]:
        """Filter and extract content from relevant articles"""
        filtered = []
        
        for article in articles:
            try:
                # Fetch article content
                response = requests.get(article['url'], timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract main content
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text().strip() for p in paragraphs[:5]])  # First 5 paragraphs
                
                # Calculate relevance score based on keyword matching
                relevance_score = self._calculate_relevance(content, spike)
                
                if relevance_score > 0.3:  # Threshold for relevance
                    filtered.append({
                        "title": article['title'],
                        "url": article['url'],
                        "content": content[:2000],  # Limit content length
                        "relevance_score": relevance_score
                    })
                    
            except Exception as e:
                continue  # Skip problematic articles
                
        return sorted(filtered, key=lambda x: x['relevance_score'], reverse=True)
    
    def _calculate_relevance(self, content: str, spike: Dict) -> float:
        """Calculate relevance score based on keyword matching"""
        keywords = [
            spike['metric'].replace('_', ' '),
            spike['exchange'].lower(),
            'cryptocurrency',
            'trading',
            'volume',
            'price',
            'spike',
            'surge',
            'decline'
        ]
        
        content_lower = content.lower()
        matches = sum(1 for keyword in keywords if keyword in content_lower)
        return matches / len(keywords)