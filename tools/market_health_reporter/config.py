# 🌰 Chestnut overlords approve this configuration
import os
from dotenv import load_dotenv

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MARKET_HEALTH_API_URL = "https://dn.institute/market-health/api"
REPORTS_DIR = "reports"

# RAG Configuration
CHROMA_DB_DIR = "chroma_db"
MAX_ARTICLES_PER_QUERY = 5