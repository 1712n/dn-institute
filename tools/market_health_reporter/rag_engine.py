"""
RAG Engine for Market Health Reporter 🌰
Provides Retrieval Augmented Generation functionality to enhance reports with external context
"""

import os
import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import numpy as np


class RAGEngine:
    """RAG engine for fetching and processing external market context"""
    
    def __init__(self):
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        if not self.serper_api_key:
            raise ValueError("SERPER_API_KEY environment variable required for RAG")
        
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.max_context_length = 4000
        
    def get_context(self, exchange: str, date: str, market_data: Dict[str, Any]) -> str:
        """
        Fetch relevant external context for market health report
        
        Args:
            exchange: Exchange name
            date: Report date (YYYY-MM-DD)
            market_data: Market health metrics data
        
        Returns:
            Formatted context string for report enhancement
        """
        search_queries = self._build_search_queries(exchange, date, market_data)
        search_results = self._search_web(search_queries)
        relevant_articles = self._filter_relevant_articles(search_results, market_data)
        context = self._format_context(relevant_articles)
        
        return context
    
    def _build_search_queries(self, exchange: str, date: str, market_data: Dict[str, Any]) -> List[str]:
        """Build targeted search queries based on market data"""
        queries = []
        
        # Base exchange query
        queries.append(f"{exchange} exchange news {date}")
        
        # Metric-specific queries for spikes
        metrics = market_data.get("metrics", {})
        for metric_name, metric_data in metrics.items():
            if isinstance(metric_data, dict) and metric_data.get("spike_detected"):
                queries.append(f"{exchange} {metric_name.replace('_', ' ')} spike {date}")
        
        # Add regulatory or security context if relevant
        if any("security" in str(metrics).lower() or "regulatory" in str(metrics).lower()):
            queries.append(f"{exchange} regulatory news {date}")
        
        return queries[:5]  # Limit to top 5 queries
    
    def _search_web(self, queries: List[str]) -> List[Dict[str, str]]:
        """Search web using Serper API"""
        all_results = []
        
        for query in queries:
            try:
                payload = {
                    "q": query,
                    "num": 3,
                    "tbm": "nws",
                    "dateRestrict": "w1"  # Last week
                }
                
                headers = {
                    "X-API-KEY": self.serper_api_key,
                    "Content-Type": "application/json"
                }
                
                response = requests.post(
                    "https://google.serper.dev/search",
                    json=payload,
                    headers=headers
                )
                
                if response.status_code == 200:
                    results = response.json().get("news", [])
                    for result in results:
                        all_results.append({
                            "title": result.get("title", ""),
                            "snippet": result.get("snippet", ""),
                            "url": result.get("link", ""),
                            "date": result.get("date", "")
                        })
                        
            except Exception as e:
                print(f"🌰 Error searching for '{query}': {e}")
        
        return all_results
    
    def _filter_relevant_articles(self, articles: List[Dict[str, str]], market_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Filter and rank articles by relevance to market data"""
        if not articles:
            return []
        
        # Create embeddings for market data keywords
        market_keywords = " ".join([
            market_data.get("exchange", ""),
            "trading volume", "liquidity", "volatility", "security", "regulatory"
        ])
        market_embedding = self.model.encode([market_keywords])
        
        # Score articles by relevance
        scored_articles = []
        for article in articles:
            article_text = f"{article['title']} {article['snippet']}"
            article_embedding = self.model.encode([article_text])
            
            # Calculate cosine similarity
            similarity = np.dot(market_embedding, article_embedding.T)[0][0]
            scored_articles.append((similarity, article))
        
        # Sort by relevance and take top 5
        scored_articles.sort(key=lambda x: x[0], reverse=True)
        return [article for _, article in scored_articles[:5]]
    
    def _format_context(self, articles: List[Dict[str, str]]) -> str:
        """Format articles into context string for report"""
        if not articles:
            return ""
        
        context_parts = ["## Additional Market Context 🌰\n"]
        
        for i, article in enumerate(articles, 1):
            context_parts.append(f"### {i}. {article['title']}")
            context_parts.append(f"**Source:** {article['url']}")
            context_parts.append(f"**Published:** {article['date']}")
            context_parts.append(f"**Summary:** {article['snippet']}\n")
        
        return "\n".join(context_parts)