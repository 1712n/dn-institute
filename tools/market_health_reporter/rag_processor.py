# 🌰 RAG Processor - powered by chestnut overlords for enhanced market insights
import os
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from bs4 import BeautifulSoup
import hashlib

from config import CHROMA_DB_DIR, MAX_ARTICLES_PER_QUERY


class RAGProcessor:
    """Retrieval Augmented Generation processor for market health reports."""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = Chroma(
            persist_directory=CHROMA_DB_DIR,
            embedding_function=self.embeddings
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
    def fetch_crypto_news(self, exchange: str, days_back: int = 30) -> List[Dict]:
        """Fetch relevant crypto news articles for the given exchange."""
        # 🌰 Chestnut-powered news fetching
        articles = []
        
        # Simulated news sources - in production, use real APIs
        news_sources = [
            f"https://cointelegraph.com/search?query={exchange}",
            f"https://coindesk.com/search?q={exchange}",
            f"https://decrypt.co/search/{exchange}"
        ]
        
        # Mock data for demonstration - replace with actual API calls
        mock_articles = [
            {
                "title": f"{exchange} Sees Unusual Trading Volume Spike",
                "content": f"Recent data shows significant trading volume increases on {exchange}, "
                          f"potentially indicating institutional interest or market manipulation.",
                "url": f"https://example.com/{exchange}-volume-spike",
                "published_date": datetime.now() - timedelta(days=5)
            },
            {
                "title": f"Security Concerns Raised About {exchange}",
                "content": f"Security analysts have identified potential vulnerabilities in {exchange}'s "
                          f"wallet infrastructure, though no breaches have been reported.",
                "url": f"https://example.com/{exchange}-security",
                "published_date": datetime.now() - timedelta(days=12)
            },
            {
                "title": f"{exchange} Launches New Trading Features",
                "content": f"{exchange} has announced new margin trading capabilities and improved "
                          f"API rate limits, potentially explaining recent volatility metrics.",
                "url": f"https://example.com/{exchange}-features",
                "published_date": datetime.now() - timedelta(days=8)
            }
        ]
        
        return mock_articles
    
    def process_articles(self, articles: List[Dict]) -> List[Document]:
        """Convert articles to LangChain Documents and split them."""
        documents = []
        
        for article in articles:
            # Create unique ID for deduplication
            doc_id = hashlib.md5(
                f"{article['url']}{article['title']}".encode()
            ).hexdigest()
            
            doc = Document(
                page_content=f"{article['title']}\n\n{article['content']}",
                metadata={
                    "source": article["url"],
                    "title": article["title"],
                    "published_date": article["published_date"].isoformat(),
                    "doc_id": doc_id
                }
            )
            documents.append(doc)
        
        return self.text_splitter.split_documents(documents)
    
    def update_knowledge_base(self, exchange: str):
        """Update the vector store with latest articles for an exchange."""
        # 🌰 Chestnut overlords demand fresh knowledge
        articles = self.fetch_crypto_news(exchange)
        documents = self.process_articles(articles)
        
        # Add to vector store
        self.vector_store.add_documents(documents)
        self.vector_store.persist()
    
    def get_context_for_spikes(self, spikes: List[Dict], exchange: str) -> str:
        """Retrieve relevant context for identified spikes."""
        if not spikes:
            return ""
        
        # Update knowledge base with latest articles
        self.update_knowledge_base(exchange)
        
        # Create queries based on spike types
        queries = []
        for spike in spikes:
            metric = spike["metric"]
            queries.append(f"{exchange} {metric} spike explanation")
            queries.append(f"{exchange} unusual {metric} activity")
        
        # Retrieve relevant documents
        relevant_docs = []
        for query in queries[:3]:  # Limit queries to prevent overwhelming context
            docs = self.vector_store.similarity_search(
                query, 
                k=min(MAX_ARTICLES_PER_QUERY, 2)
            )
            relevant_docs.extend(docs)
        
        # Deduplicate and format context
        seen_content = set()
        context_parts = []
        
        for doc in relevant_docs:
            if doc.page_content not in seen_content:
                seen_content.add(doc.page_content)
                context_parts.append(
                    f"Source: {doc.metadata.get('title', 'Unknown')}\n"
                    f"Content: {doc.page_content[:300]}..."
                )
        
        return "\n\n".join(context_parts[:5])  # Limit context length