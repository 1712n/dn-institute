import os
import json
import requests
from typing import Dict, List, Any
from datetime import datetime, timedelta
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

class RAGEngine:
    """Retrieval Augmented Generation engine for market health reports"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.serper_api_key:
            raise ValueError("SERPER_API_KEY environment variable required for RAG")
        
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(temperature=0.3, model="gpt-4")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
    def search_articles(self, query: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """Search for relevant articles using Serper API"""
        
        url = "https://google.serper.dev/search"
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        payload = json.dumps({
            "q": f"{query} cryptocurrency exchange news",
            "type": "news",
            "tbs": f"cdr:1,cd_min:{start_date.strftime('%m/%d/%Y')},cd_max:{end_date.strftime('%m/%d/%Y')}",
            "num": 10
        })
        
        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for item in data.get("news", []):
                articles.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "url": item.get("link", ""),
                    "date": item.get("date", ""),
                    "source": item.get("source", "")
                })
            
            if self.verbose:
                print(f"🌰 Found {len(articles)} articles for query: {query}")
            
            return articles
            
        except Exception as e:
            print(f"Error searching articles: {e}")
            return []
    
    def create_vector_store(self, articles: List[Dict[str, Any]]) -> Chroma:
        """Create vector store from articles"""
        
        texts = []
        metadatas = []
        
        for article in articles:
            # Combine title and snippet for better context
            text = f"{article['title']}\n\n{article['snippet']}"
            texts.append(text)
            metadatas.append({
                "title": article["title"],
                "url": article["url"],
                "source": article["source"],
                "date": article["date"]
            })
        
        # Split texts into chunks
        chunks = self.text_splitter.create_documents(texts, metadatas=metadatas)
        
        # Create vector store
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            collection_name="market_health_rag"
        )
        
        return vectorstore
    
    def get_context(self, exchange: str, date: str, spikes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get relevant context for report generation"""
        
        # Build search queries based on exchange and spikes
        queries = [
            f"{exchange} exchange news",
            f"{exchange} cryptocurrency market analysis"
        ]
        
        # Add spike-specific queries
        for spike in spikes:
            metric = spike.get("metric", "")
            queries.append(f"{exchange} {metric} spike cryptocurrency")
        
        # Search for articles
        all_articles = []
        for query in queries[:3]:  # Limit to prevent API abuse
            articles = self.search_articles(query)
            all_articles.extend(articles)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article["url"] not in seen_urls:
                seen_urls.add(article["url"])
                unique_articles.append(article)
        
        # Create vector store if we have articles
        vectorstore = None
        if unique_articles:
            vectorstore = self.create_vector_store(unique_articles)
        
        return {
            "articles": unique_articles,
            "vectorstore": vectorstore,
            "query_count": len(queries)
        }