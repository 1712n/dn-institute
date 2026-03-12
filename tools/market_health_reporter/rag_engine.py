import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from tavily import TavilyClient
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
import json


class RAGEngine:
    """🌰 RAG engine for retrieving relevant market context and news"""
    
    def __init__(self):
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.vector_store = None
    
    def retrieve_context(self, exchange: str, date: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """🌰 Retrieve relevant context for market health report"""
        
        # Parse date
        target_date = datetime.strptime(date, "%Y-%m-%d")
        
        # Build search queries based on market data
        queries = self._build_search_queries(exchange, target_date, market_data)
        
        # Search for relevant articles
        all_results = []
        for query in queries:
            try:
                results = self.tavily_client.search(
                    query=query,
                    max_results=5,
                    include_domains=["coindesk.com", "cointelegraph.com", "decrypt.co", 
                                   "theblock.co", "cryptonews.net", "reuters.com"],
                    from_date=(target_date - timedelta(days=7)).strftime("%Y-%m-%d"),
                    to_date=(target_date + timedelta(days=1)).strftime("%Y-%m-%d")
                )
                all_results.extend(results.get("results", []))
            except Exception as e:
                print(f"🌰 Error searching for '{query}': {e}")
        
        # Remove duplicates and create documents
        unique_results = {r["url"]: r for r in all_results}.values()
        documents = [
            Document(
                page_content=r["content"],
                metadata={
                    "title": r["title"],
                    "url": r["url"],
                    "published_date": r.get("published_date", ""),
                    "score": r.get("score", 0)
                }
            )
            for r in unique_results
        ]
        
        # Create vector store if we have documents
        if documents:
            texts = self.text_splitter.split_documents(documents)
            self.vector_store = Chroma.from_documents(
                documents=texts,
                embedding=self.embeddings,
                collection_name="market_health_context"
            )
            
            # Get relevant excerpts
            relevant_context = self._extract_relevant_context(market_data)
        else:
            relevant_context = {"articles": [], "insights": []}
        
        return relevant_context
    
    def _build_search_queries(self, exchange: str, date: datetime, market_data: Dict[str, Any]) -> List[str]:
        """🌰 Build targeted search queries based on market data"""
        queries = []
        
        # Base exchange query
        queries.append(f"{exchange} exchange news {date.strftime('%Y-%m')}")
        
        # Add queries for significant spikes
        for metric, data in market_data.items():
            if isinstance(data, dict) and "spikes" in data:
                for spike in data["spikes"]:
                    if spike.get("significance", 0) > 0.8:  # High significance spikes
                        queries.append(
                            f"{exchange} {metric.replace('_', ' ')} spike {date.strftime('%B %Y')}"
                        )
        
        # Regulatory and security events
        queries.extend([
            f"{exchange} regulatory news {date.strftime('%Y-%m')}",
            f"{exchange} security incident {date.strftime('%Y-%m')}",
            f"crypto market volatility {date.strftime('%B %Y')}"
        ])
        
        return queries
    
    def _extract_relevant_context(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """🌰 Extract most relevant context from vector store"""
        if not self.vector_store:
            return {"articles": [], "insights": []}
        
        # Build query from market data
        query = " ".join([k.replace("_", " ") for k in market_data.keys() if "spike" in str(market_data[k]).lower()])
        
        # Get top relevant documents
        docs = self.vector_store.similarity_search(query, k=5)
        
        return {
            "articles": [
                {
                    "title": doc.metadata.get("title", ""),
                    "url": doc.metadata.get("url", ""),
                    "content": doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                    "relevance_score": doc.metadata.get("score", 0)
                }
                for doc in docs
            ],
            "insights": [doc.page_content for doc in docs[:3]]  # Top 3 insights
        }