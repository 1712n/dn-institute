"""
🌰 Social Media Sentiment Scraper
Scrapes sentiment from Twitter/X, Reddit, and Telegram
"""

import tweepy
import praw
from datetime import datetime
from typing import Dict
import os

class SocialScraper:
    """Scrapes social media for cryptocurrency sentiment"""
    
    def __init__(self):
        # Twitter API setup
        self.twitter_client = tweepy.Client(
            bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        
        # Reddit API setup
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="🌰 CryptoSentinel/1.0"
        )
    
    async def get_sentiment(self, symbol: str, start_time: datetime, end_time: datetime) -> Dict:
        """Get social sentiment for a symbol"""
        
        # Twitter sentiment
        twitter_sentiment = await self._get_twitter_sentiment(symbol, start_time, end_time)
        
        # Reddit sentiment
        reddit_sentiment = await self._get_reddit_sentiment(symbol, start_time, end_time)
        
        # Combine scores
        combined_score = (twitter_sentiment["score"] + reddit_sentiment["score"]) / 2
        combined_volume = twitter_sentiment["volume"] + reddit_sentiment["volume"]
        
        return {
            "score": combined_score,
            "volume": combined_volume,
            "sources": ["twitter", "reddit"]
        }
    
    async def _get_twitter_sentiment(self, symbol: str, start_time: datetime, end_time: datetime) -> Dict:
        """Get Twitter sentiment for symbol"""
        # Search for tweets mentioning the symbol
        query = f"{symbol} OR ${symbol} lang:en -is:retweet"
        
        tweets = self.twitter_client.search_recent_tweets(
            query=query,
            max_results=100,
            tweet_fields=["created_at", "lang", "public_metrics"]
        )
        
        # Simple sentiment calculation (placeholder)
        positive_keywords = ["bullish", "buy", "moon", "🚀", "🌰"]
        negative_keywords = ["bearish", "sell", "dump", "crash"]
        
        sentiment_score = 0.5  # Placeholder
        
        return {
            "score": sentiment_score,
            "volume": len(tweets.data) if tweets.data else 0
        }
    
    async def _get_reddit_sentiment(self, symbol: str, start_time: datetime, end_time: datetime) -> Dict:
        """Get Reddit sentiment for symbol"""
        # Search relevant subreddits
        subreddits = ["CryptoCurrency", "Bitcoin", "ethereum", "altcoin"]
        
        total_score = 0
        total_posts = 0
        
        for subreddit_name in subreddits:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = subreddit.search(symbol, limit=50, time_filter="day")
            
            for post in posts:
                # Simple sentiment based on upvotes
                sentiment = min(post.score / 1000, 1.0) if post.score > 0 else 0
                total_score += sentiment
                total_posts += 1
        
        return {
            "score": total_score / max(total_posts, 1),
            "volume": total_posts
        }