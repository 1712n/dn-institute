import os
import requests
from typing import List, Dict
from bs4 import BeautifulSoup
import openai

class RAGContextRetriever:
    """🌰 Retrieval Augmented Generation context retriever for market health reports."""
    
    def __init__(self):
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        if not self.serper_api_key:
            raise ValueError("SERPER_API_KEY environment variable required for RAG")
        
    def search_market_context(self, exchange: str, date: str, spike_events: List[Dict]) -> List[Dict]:
        """Search for relevant market context articles based on spike events."""
        contexts = []
        
        for event in spike_events:
            metric = event.get('metric', '')
            severity = event.get('severity', '')
            
            # Construct search queries for each spike
            queries = [
                f"{exchange} {metric} spike {date} crypto news",
                f"{exchange} exchange {metric} unusual activity {date}",
                f"cryptocurrency market {metric} volatility {date} {exchange}"
            ]
            
            for query in queries:
                search_results = self._search_web(query)
                for result in search_results[:2]:  # Top 2 results per query
                    content = self._extract_article_content(result.get('link', ''))
                    if content:
                        contexts.append({
                            'title': result.get('title', ''),
                            'url': result.get('link', ''),
                            'content': content,
                            'relevance_score': self._calculate_relevance(content, metric, exchange)
                        })
        
        # Sort by relevance and deduplicate
        unique_contexts = {}
        for ctx in sorted(contexts, key=lambda x: x['relevance_score'], reverse=True):
            if ctx['url'] not in unique_contexts:
                unique_contexts[ctx['url']] = ctx
        
        return list(unique_contexts.values())[:5]  # Return top 5 most relevant
    
    def _search_web(self, query: str) -> List[Dict]:
        """Perform web search using Serper API."""
        url = "https://google.serper.dev/search"
        payload = {
            "q": query,
            "num": 5,
            "tbm": "nws"  # News search
        }
        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json().get('news', [])
        except Exception as e:
            print(f"🌰 Error searching web: {e}")
            return []
    
    def _extract_article_content(self, url: str) -> str:
        """Extract clean text content from article URL."""
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit to first 1000 chars for context
            return text[:1000]
        except Exception as e:
            print(f"🌰 Error extracting content from {url}: {e}")
            return ""
    
    def _calculate_relevance(self, content: str, metric: str, exchange: str) -> float:
        """Calculate relevance score based on keyword matches."""
        keywords = [metric.lower(), exchange.lower(), 'crypto', 'bitcoin', 'ethereum']
        content_lower = content.lower()
        score = sum(1 for keyword in keywords if keyword in content_lower)
        return score / len(keywords) if keywords else 0