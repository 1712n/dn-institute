import os
from typing import Dict, List, Any
from datetime import datetime, timedelta
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import WebBaseLoader
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from serpapi import GoogleSearch


class RAGRetriever:
    """Retrieves relevant articles and context for market health spikes using RAG."""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
    def search_articles(self, query: str, date: str, days_back: int = 7) -> List[str]:
        """Search for relevant articles using Google Search API."""
        end_date = datetime.strptime(date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=days_back)
        
        search_query = f"{query} after:{start_date.strftime('%Y-%m-%d')} before:{end_date.strftime('%Y-%m-%d')}"
        
        params = {
            "engine": "google",
            "q": search_query,
            "api_key": os.getenv("SERPAPI_API_KEY"),
            "num": 5,
            "tbm": "nws"
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        articles = []
        if "news_results" in results:
            for result in results["news_results"]:
                if "link" in result:
                    articles.append(result["link"])
        
        return articles
    
    def load_and_process_articles(self, urls: List[str]) -> FAISS:
        """Load articles and create vector store."""
        documents = []
        
        for url in urls:
            try:
                loader = WebBaseLoader(url)
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                print(f"🌰 Failed to load {url}: {e}")
                continue
        
        if not documents:
            return None
            
        texts = self.text_splitter.split_documents(documents)
        vectorstore = FAISS.from_documents(texts, self.embeddings)
        
        return vectorstore
    
    def get_context_for_spikes(self, exchange: str, spikes: List[Dict[str, Any]]) -> Dict[str, str]:
        """Get contextual information for detected spikes."""
        context = {}
        
        for spike in spikes:
            metric = spike["metric"]
            value = spike["value"]
            date = spike["date"]
            
            # Create search query based on spike
            query = f"{exchange} exchange {metric} spike {value}"
            
            # Search for relevant articles
            articles = self.search_articles(query, date)
            
            if articles:
                # Load articles and create RAG system
                vectorstore = self.load_and_process_articles(articles)
                
                if vectorstore:
                    qa_chain = RetrievalQA.from_chain_type(
                        llm=self.llm,
                        chain_type="stuff",
                        retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
                    )
                    
                    # Get context for this spike
                    question = f"What caused the {metric} spike to {value} on {exchange}?"
                    response = qa_chain.run(question)
                    
                    context[f"{metric}_{date}"] = response
        
        return context