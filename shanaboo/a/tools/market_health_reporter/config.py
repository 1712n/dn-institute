"""Configuration management for Market Health Reporter 🌰"""

import os
from typing import Dict, Any
    "temperature": 0.7,
    "max_tokens": 2000,
    "model": "gpt-4",
    "rag_enabled": True,
    "max_articles": 5,
    "min_relevance_score": 0.7,
    "chroma_db_path": "./chroma_db",
    "news_sources": ["coindesk", "cointelegraph", "decrypt", "the-block"],
}

def load_config() -> Dict[str, Any]: