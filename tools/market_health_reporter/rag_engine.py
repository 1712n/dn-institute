"""
RAG Engine for Market Health Reporter 🌰
Provides Retrieval Augmented Generation functionality to enhance reports with external context.
"""

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime

from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.tools import SerpAPIWrapper
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class RAGEngine:
    """RAG engine for retrieving relevant market context."""
    
    def __init__(self, openai_api_key: str, serpapi_key: str):
        self.openai_api_key = openai_api_key
        self.serpapi_key = serpapi_key
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.3,
            openai_api_key=openai_api_key
        )
        self.search = SerpAPIWrapper(serpapi_api_key=serpapi_key)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
    def search_articles(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for relevant articles using web search."""
        try:
            search_results = self.search.results(query)
            articles = []
            
            for result in search_results.get("organic_results", [])[:max_results]:
                article = {
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "url": result.get("link", ""),
                    "source": result.get("source", "")
                }
                articles.append(article)
                
            logger.info(f"Found {len(articles)} articles for query: {query}")
            return articles
            
        except Exception as e:
            logger.error(f"Error searching articles: {e}")
            return []
    
    def create_vector_store(self, articles: List[Dict]) -> FAISS:
        """Create a vector store from articles for similarity search."""
        documents = []
        
        for article in articles:
            content = f"Title: {article['title']}\n"
            content += f"Source: {article['source']}\n"
            content += f"Content: {article['snippet']}\n"
            content += f"URL: {article['url']}"
            
            doc = Document(
                page_content=content,
                metadata={
                    "title": article["title"],
                    "source": article["source"],
                    "url": article["url"]
                }
            )
            documents.append(doc)
        
        texts = self.text_splitter.split_documents(documents)
        vectorstore = FAISS.from_documents(texts, self.embeddings)
        
        return vectorstore
    
    def get_relevant_context(
        self, 
        exchange: str, 
        date: str, 
        metrics: List[Dict],
        max_articles: int = 5
    ) -> Dict[str, str]:
        """Get relevant context for given metrics."""
        
        # Build search query
        query = f"{exchange} cryptocurrency news {date} market analysis"
        
        # Search for articles
        articles = self.search_articles(query, max_articles)
        
        if not articles:
            return {}
        
        # Create vector store
        vectorstore = self.create_vector_store(articles)
        
        # Create retriever
        retriever = vectorstore.as_retriever(
            search_kwargs={"k": min(3, len(articles))}
        )
        
        # Get context for each metric
        context_by_metric = {}
        
        for metric in metrics:
            metric_name = metric.get("name", "")
            metric_value = metric.get("value", "")
            
            question = f"What context explains the {metric_name} metric value of {metric_value} for {exchange}?"
            
            try:
                qa_chain = RetrievalQA.from_chain_type(
                    llm=self.llm,
                    chain_type="stuff",
                    retriever=retriever,
                    return_source_documents=True
                )
                
                response = qa_chain.invoke({"query": question})
                context_by_metric[metric_name] = response["result"]
                
            except Exception as e:
                logger.error(f"Error getting context for {metric_name}: {e}")
                context_by_metric[metric_name] = ""
        
        return context_by_metric