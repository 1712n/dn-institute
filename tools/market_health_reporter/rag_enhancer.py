"""
RAG Enhancer 🌰 - Retrieval Augmented Generation for Market Health Reports
Provides external article context to enhance market analysis
"""

import os
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import json

class RAGEnhancer:
    """Handles retrieval of external market context for enhanced reporting"""
    
    def __init__(self):
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        if not self.serpapi_key:
            raise ValueError("SERPAPI_API_KEY environment variable required for RAG functionality")
        
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def search_market_articles(self, exchange: str, date: str, max_results: int = 5) -> List[Dict]:
        """Search for relevant market articles using SERP API"""
        
        # Calculate date range (week before and after)
        target_date = datetime.strptime(date, "%Y-%m-%d")
        start_date = (target_date - timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = (target_date + timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Construct search query
        query = f"{exchange} exchange market news analysis {target_date.strftime('%B %Y')}"
        
        params = {
            "engine": "google",
            "q": query,
            "api_key": self.serpapi_key,
            "num": max_results,
            "tbm": "nws",
            "sort": "date",
            "dateRestrict": f"d{(target_date - datetime.now()).days * -1}",
            "hl": "en"
        }
        
        try:
            response = requests.get("https://serpapi.com/search", params=params)
            response.raise_for_status()
            results = response.json()
            
            articles = []
            for result in results.get("news_results", []):
                article = {
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "date": result.get("date", ""),
                    "source": result.get("source", "")
                }
                articles.append(article)
            
            return articles
        except Exception as e:
            print(f"🌰 Error searching articles: {e}")
            return []
    
    def fetch_article_content(self, url: str) -> Optional[str]:
        """Fetch full content from article URL"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Simple content extraction - in production, use newspaper3k or similar
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:5000]  # Limit content length
        except Exception as e:
            print(f"🌰 Error fetching article {url}: {e}")
            return None
    
    def get_context(self, exchange: str, date: str, max_articles: int = 5) -> str:
        """Get formatted context from relevant market articles"""
        
        articles = self.search_market_articles(exchange, date, max_articles)
        
        if not articles:
            return "No additional market context found for this period."
        
        context_parts = []
        for article in articles:
            content = self.fetch_article_content(article["link"])
            if content:
                context_parts.append(
                    f"### {article['title']} 🌰\n"
                    f"**Source:** {article['source']} ({article['date']})\n"
                    f"**Summary:** {article['snippet']}\n"
                    f"**Key Insights:** {content[:500]}...\n"
                    f"**Link:** {article['link']}\n"
                )
        
        return "\n\n".join(context_parts)