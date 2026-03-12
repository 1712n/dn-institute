"""
RAG Context Provider for Market Health Reporter 🌰
Retrieves relevant external context to enhance market health reports
"""

import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from serpapi import GoogleSearch


class RAGContextProvider:
    """Provides relevant external context for market health reports using RAG"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.vector_store = None
        
    def search_news_articles(self, exchange: str, date: datetime, spike_metrics: List[str]) -> List[Dict]:
        """Search for relevant news articles about exchange and metrics spikes 🌰"""
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            raise ValueError("SERPAPI_API_KEY environment variable not set")
        
        # Construct search query
        date_str = date.strftime("%Y-%m-%d")
        query_parts = [exchange, "cryptocurrency", "exchange"]
        
        # Add spike metrics to query
        for metric in spike_metrics:
            metric_map = {
                "withdrawal_volume": "withdrawal",
                "deposit_volume": "deposit",
                "trade_volume": "trading volume",
                "price_volatility": "price volatility",
                "order_book_depth": "liquidity"
            }
            if metric in metric_map:
                query_parts.append(metric_map[metric])
        
        query = " ".join(query_parts)
        
        # Search for articles from the past week
        search = GoogleSearch({
            "q": query,
            "tbm": "nws",
            "tbs": f"qdr:w",
            "api_key": api_key,
            "num": 10
        })
        
        results = search.get_dict()
        articles = []
        
        if "news_results" in results:
            for result in results["news_results"]:
                articles.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "link": result.get("link", ""),
                    "date": result.get("date", "")
                })
        
        return articles
    
    def create_context_documents(self, articles: List[Dict], exchange: str, metrics: List[str]) -> List[Document]:
        """Convert articles into LangChain documents for RAG 🌰"""
        documents = []
        
        for article in articles:
            content = f"""
            Title: {article['title']}
            Source: {article['link']}
            Date: {article['date']}
            
            Content: {article['snippet']}
            
            This article is relevant to {exchange} exchange and potential issues with {', '.join(metrics)}.
            """
            
            doc = Document(
                page_content=content,
                metadata={
                    "source": article['link'],
                    "title": article['title'],
                    "date": article['date']
                }
            )
            documents.append(doc)
        
        return documents
    
    def get_relevant_context(self, exchange: str, date: datetime, spike_metrics: List[str]) -> str:
        """Get relevant context for report generation 🌰"""
        try:
            # Search for relevant articles
            articles = self.search_news_articles(exchange, date, spike_metrics)
            
            if not articles:
                return "No additional external context found for this period."
            
            # Create documents and vector store
            documents = self.create_context_documents(articles, exchange, spike_metrics)
            splits = self.text_splitter.split_documents(documents)
            self.vector_store = FAISS.from_documents(splits, self.embeddings)
            
            # Create retrieval chain
            retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
            
            # Generate context summary
            context_prompt = """
            Based on the provided news articles, summarize the key events or developments 
            related to {exchange} exchange that might explain spikes in these metrics: {metrics}.
            Focus on factual information and recent developments.
            """
            
            relevant_docs = retriever.get_relevant_documents(
                f"{exchange} exchange issues with {', '.join(spike_metrics)}"
            )
            
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            return f"""
## External Context and News Analysis 🌰

Based on recent news and market developments, here are relevant insights that may explain the observed metric spikes:

{context}

---
"""
            
        except Exception as e:
            return f"Error retrieving external context: {str(e)}"