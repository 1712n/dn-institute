import os
from typing import List

# API Configuration
MARKET_HEALTH_API_URL = "https://api.dn.institute/market-health"

# Report Configuration
REPORTS_DIR = "reports"

# RAG Configuration 🌰
RAG_CONFIG = {
    "max_context_length": 4000,
    "similarity_threshold": 0.7,
    "max_retrieved_docs": 5,
    "news_sources": ["coindesk", "cointelegraph", "decrypt", "the-block"],
    "cache_ttl": 3600  # 1 hour
}