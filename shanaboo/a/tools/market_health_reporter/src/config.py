import os
from dotenv import load_dotenv
from typing import List
load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    MARKET_HEALTH_API_URL = "https://dn.institute/market-health/api"
    
    # RAG Configuration 🌰
    RAG_ENABLED = os.getenv("RAG_ENABLED", "true").lower() == "true"
    MAX_RAG_ARTICLES = int(os.getenv("MAX_RAG_ARTICLES", "5"))
    RAG_SOURCES = os.getenv("RAG_SOURCES", "coindesk,cointelegraph,decrypt").split(",")
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")