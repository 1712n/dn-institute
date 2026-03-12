"""
RAG Enhancer for Market Health Reporter 🌰
Provides Retrieval Augmented Generation functionality to enhance reports with external context
"""

import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from serpapi import GoogleSearch


class RAGEnhancer:
    """RAG Enhancer for fetching and incorporating external market context"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo-16k",
            temperature=0.3,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def search_market_articles(self, exchange: str, date: str, metrics: List[str]) -> List[Dict]:
        """Search for relevant market articles using SERPAPI"""
        if not self.serpapi_key:
            return []
        
        # Construct search query
        query_parts = [f"{exchange} exchange", "market analysis", date]
        if metrics:
            query_parts.extend(metrics[:2])  # Include top 2 metrics
        
        query = " ".join(query_parts)
        
        search = GoogleSearch({
            "q": query,
            "engine": "google",
            "api_key": self.serpapi_key,
            "num": 5,
            "tbm": "nws",  # News search
            "sort": "date",
            "dateRestrict": "w1"  # Last week
        })
        
        try:
            results = search.get_dict()
            articles = []
            
            if "news_results" in results:
                for result in results["news_results"][:3]:  # Top 3 articles
                    articles.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("snippet", ""),
                        "link": result.get("link", ""),
                        "date": result.get("date", "")
                    })
            
            return articles
        except Exception as e:
            print(f"🌰 Error searching articles: {e}")
            return []
    
    def extract_article_content(self, url: str) -> Optional[str]:
        """Extract content from a news article URL"""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text from main content areas
            content_selectors = ['article', 'main', '.content', '.post-content', '.entry-content']
            content = ""
            
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = elements[0].get_text(strip=True, separator=' ')
                    break
            
            if not content:
                content = soup.get_text(strip=True, separator=' ')
            
            return content[:3000]  # Limit content length
            
        except Exception as e:
            print(f"🌰 Error extracting content from {url}: {e}")
            return None
    
    def get_enhanced_context(self, exchange: str, date: str, metrics_data: Dict) -> Dict:
        """Get enhanced context using RAG"""
        # Extract key metrics for search
        key_metrics = []
        if "metrics" in metrics_data:
            for metric in metrics_data["metrics"]:
                if metric.get("spike_detected", False):
                    key_metrics.append(metric.get("name", ""))
        
        # Search for relevant articles
        articles = self.search_market_articles(exchange, date, key_metrics)
        
        enhanced_context = {
            "articles": articles,
            "market_insights": [],
            "additional_context": ""
        }
        
        # Extract content from top articles
        documents = []
        for article in articles[:2]:  # Process top 2 articles
            content = self.extract_article_content(article["link"])
            if content:
                documents.append(Document(
                    page_content=content,
                    metadata={"source": article["link"], "title": article["title"]}
                ))
        
        # Split documents into chunks
        if documents:
            splits = self.text_splitter.split_documents(documents)
            
            # Generate market insights from articles
            prompt = PromptTemplate(
                input_variables=["context", "exchange", "date"],
                template="""
                Based on the following market news articles about {exchange} exchange around {date}, 
                provide 2-3 key insights that would be relevant for a market health report.
                Focus on market sentiment, regulatory changes, or significant events.
                
                Context: {context}
                
                Provide concise insights in bullet points:
                """
            )
            
            context_text = "\n\n".join([doc.page_content for doc in splits])
            insights_prompt = prompt.format(
                context=context_text[:4000],  # Limit context
                exchange=exchange,
                date=date
            )
            
            try:
                response = self.llm.invoke(insights_prompt)
                enhanced_context["market_insights"] = response.content.strip().split('\n')
            except Exception as e:
                print(f"🌰 Error generating insights: {e}")
        
        return enhanced_context