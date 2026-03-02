"""
RAG Retriever for Market Health Reporter 🌰
Retrieves relevant external articles for enhanced report generation
"""
import requests
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
import hashlib
from config import Config

class RAGRetriever:
    """Retrieves and processes external articles for RAG"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=Config.OPENAI_API_KEY)
        self.vector_store = Chroma(
            persist_directory=Config.CHROMA_PERSIST_DIR,
            embedding_function=self.embeddings
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
    
    def fetch_articles(self, query: str, limit: int = 5) -> List[Dict]:
        """Fetch relevant articles from configured sources"""
        articles = []
        
        # 🌰 Fetch from CoinDesk
        if "coindesk" in Config.RAG_SOURCES:
            articles.extend(self._fetch_coindesk(query))
        
        # 🌰 Fetch from Cointelegraph
        if "cointelegraph" in Config.RAG_SOURCES:
            articles.extend(self._fetch_cointelegraph(query))
        
        # 🌰 Fetch from Decrypt
        if "decrypt" in Config.RAG_SOURCES:
            articles.extend(self._fetch_decrypt(query))
        
        return articles[:limit]
    
    def _fetch_coindesk(self, query: str) -> List[Dict]:
        """Fetch articles from CoinDesk"""
        try:
            search_url = f"https://www.coindesk.com/search?s={query}"
            response = requests.get(search_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            for link in soup.find_all('a', href=True)[:5]:
                if '/markets/' in link['href']:
                    articles.append({
                        'title': link.get_text(strip=True),
                        'url': f"https://www.coindesk.com{link['href']}",
                        'source': 'coindesk'
                    })
            return articles
        except Exception as e:
            print(f"🌰 Error fetching CoinDesk: {e}")
            return []
    
    def _fetch_cointelegraph(self, query: str) -> List[Dict]:
        """Fetch articles from Cointelegraph"""
        # Similar implementation for Cointelegraph
        return []
    
    def _fetch_decrypt(self, query: str) -> List[Dict]:
        """Fetch articles from Decrypt"""
        # Similar implementation for Decrypt
        return []
    
    def store_articles(self, articles: List[Dict]) -> None:
        """Store articles in vector database"""
        documents = []
        for article in articles:
            doc = Document(
                page_content=article.get('content', ''),
                metadata={
                    'title': article['title'],
                    'url': article['url'],
                    'source': article['source']
                }
            )
            documents.append(doc)
        
        splits = self.text_splitter.split_documents(documents)
        self.vector_store.add_documents(splits)
        self.vector_store.persist()
    
    def retrieve_context(self, query: str, k: int = 3) -> List[str]:
        """Retrieve relevant context for a query"""
        results = self.vector_store.similarity_search(query, k=k)
        return [doc.page_content for doc in results]