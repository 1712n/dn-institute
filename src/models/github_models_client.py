"""
🌰 GitHub Models Client for CryptoSentinel AI
Integrates with GitHub Models for advanced AI capabilities
"""

import os
import requests
from typing import Dict, List
import json

class GitHubModelsClient:
    """Client for GitHub Models API integration"""
    
    def __init__(self):
        self.base_url = "https://models.github.com/v1"
        self.headers = {
            "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
            "Content-Type": "application/json"
        }
    
    async def generate_trading_insights(self, sentiment_data: Dict) -> Dict:
        """Generate trading insights using GitHub Models"""
        prompt = f"""
        🌰 Analyze the following cryptocurrency market sentiment data:
        
        Sentiment Score: {sentiment_data.get('sentiment_score', 0)}
        Social Volume: {sentiment_data.get('social_volume', 0)}
        News Sentiment: {sentiment_data.get('news_sentiment', 0)}
        On-chain Activity: {sentiment_data.get('on_chain_activity', 0)}
        
        Provide:
        1. Trading recommendation (BUY/SELL/HOLD)
        2. Risk level (1-10)
        3. Key factors driving sentiment
        4. 🌰 Chestnut Score (proprietary metric)
        
        Format as JSON.
        """
        
        payload = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self.headers,
            json=payload
        )
        
        return response.json()