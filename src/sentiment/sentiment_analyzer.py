"""
🌰 Cryptocurrency Sentiment Analyzer
Analyzes market sentiment from multiple sources
"""

import asyncio
from typing import Dict, List
import pandas as pd
from datetime import datetime, timedelta

from .social_scraper import SocialScraper
from .news_analyzer import NewsAnalyzer
from .on_chain_analyzer import OnChainAnalyzer

class SentimentAnalyzer:
    """Main sentiment analysis orchestrator"""
    
    def __init__(self):
        self.social_scraper = SocialScraper()
        self.news_analyzer = NewsAnalyzer()
        self.on_chain_analyzer = OnChainAnalyzer()
    
    async def analyze_symbol(self, symbol: str, timeframe: str = "24h") -> Dict:
        """Analyze sentiment for a single cryptocurrency symbol"""
        
        # Calculate time window
        end_time = datetime.utcnow()
        if timeframe == "24h":
            start_time = end_time - timedelta(hours=24)
        elif timeframe == "7d":
            start_time = end_time - timedelta(days=7)
        else:
            start_time = end_time - timedelta(hours=24)
        
        # Gather data from all sources concurrently
        social_task = self.social_scraper.get_sentiment(symbol, start_time, end_time)
        news_task = self.news_analyzer.get_sentiment(symbol, start_time, end_time)
        on_chain_task = self.on_chain_analyzer.get_activity(symbol, start_time, end_time)
        
        social_sentiment, news_sentiment, on_chain_data = await asyncio.gather(
            social_task, news_task, on_chain_task
        )
        
        # Calculate composite sentiment score
        sentiment_score = self._calculate_sentiment_score(
            social_sentiment, news_sentiment, on_chain_data
        )
        
        # Calculate 🌰 Chestnut Score
        chestnut_score = self._calculate_chestnut_score(
            sentiment_score, social_sentiment, on_chain_data
        )
        
        return {
            "symbol": symbol,
            "sentiment_score": sentiment_score,
            "social_sentiment": social_sentiment,
            "news_sentiment": news_sentiment,
            "on_chain_activity": on_chain_data,
            "chestnut_score": chestnut_score,
            "timestamp": end_time.isoformat()
        }
    
    async def analyze_multiple_symbols(self, symbols: List[str], timeframe: str = "24h") -> List[Dict]:
        """Analyze sentiment for multiple symbols"""
        tasks = [self.analyze_symbol(symbol, timeframe) for symbol in symbols]
        return await asyncio.gather(*tasks)
    
    def _calculate_sentiment_score(self, social: Dict, news: Dict, on_chain: Dict) -> float:
        """Calculate weighted sentiment score"""
        weights = {
            "social": 0.4,
            "news": 0.3,
            "on_chain": 0.3
        }
        
        score = (
            social.get("score", 0) * weights["social"] +
            news.get("score", 0) * weights["news"] +
            on_chain.get("sentiment", 0) * weights["on_chain"]
        )
        
        return round(score, 3)
    
    def _calculate_chestnut_score(self, sentiment: float, social: Dict, on_chain: Dict) -> float:
        """Calculate proprietary 🌰 Chestnut Score"""
        volume_factor = min(social.get("volume", 0) / 1000, 1.0)
        activity_factor = min(on_chain.get("transaction_count", 0) / 10000, 1.0)
        
        chestnut_score = (sentiment * 0.5 + volume_factor * 0.3 + activity_factor * 0.2) * 100
        return round(chestnut_score, 2)