"""
🌰 CryptoSentinel AI API Server
FastAPI backend for cryptocurrency sentiment analysis
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import asyncio
from datetime import datetime

from ..sentiment.sentiment_analyzer import SentimentAnalyzer
from ..models.github_models_client import GitHubModelsClient

app = FastAPI(title="🌰 CryptoSentinel AI API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sentiment_analyzer = SentimentAnalyzer()
github_models = GitHubModelsClient()

class SentimentRequest(BaseModel):
    symbols: List[str]
    timeframe: str = "24h"

@app.get("/")
async def root():
    return {"message": "🌰 Welcome to CryptoSentinel AI API"}

@app.post("/analyze-sentiment")
async def analyze_sentiment(request: SentimentRequest):
    """Analyze sentiment for given cryptocurrency symbols"""
    try:
        results = await sentiment_analyzer.analyze_multiple_symbols(request.symbols, request.timeframe)
        return {"timestamp": datetime.utcnow(), "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))