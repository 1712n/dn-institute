"""
RAG Enhancer for Market Health Reporter 🌰
Provides Retrieval Augmented Generation functionality to enhance reports with external context
"""

import os
import json
import requests
from typing import Dict, List, Any
from datetime import datetime, timedelta
import openai


class RAGEnhancer:
    """Enhanced RAG functionality for market health reports"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.rag_sources = [
            "news_api",
            "crypto_panic",
            "twitter_api",
            "coindesk",
            "cointelegraph"
        ]
        
    def enhance_report_data(self, data: Dict[str, Any], exchange: str, date: str) -> Dict[str, Any]:
        """Enhance report data with RAG context"""
        print("🌰 Gathering additional context via RAG...")
        
        # Get date range for context (3 days before and after)
        target_date = datetime.strptime(date, "%Y-%m-%d")
        date_range = {
            "start": (target_date - timedelta(days=3)).strftime("%Y-%m-%d"),
            "end": (target_date + timedelta(days=1)).strftime("%Y-%m-%d")
        }
        
        # Fetch relevant articles
        articles = self._fetch_relevant_articles(exchange, date_range)
        
        # Extract key insights
        insights = self._extract_insights(articles, data)
        
        # Enhance metrics with context
        enhanced_data = self._enhance_metrics(data, insights)
        
        return enhanced_data
    
    def _fetch_relevant_articles(self, exchange: str, date_range: Dict[str, str]) -> List[Dict[str, str]]:
        """Fetch relevant articles from various sources"""
        articles = []
        
        # Mock implementation - in production, integrate with actual APIs
        mock_articles = [
            {
                "title": f"{exchange.capitalize()} Sees Unusual Trading Activity",
                "content": f"Recent analysis shows significant volatility in {exchange} trading pairs...",
                "source": "crypto_news",
                "date": date_range["start"],
                "url": f"https://example.com/{exchange}-activity"
            },
            {
                "title": "Market Health Metrics Show Concerning Trends",
                "content": "Multiple exchanges experiencing similar patterns in trading volume...",
                "source": "market_analysis",
                "date": date_range["end"],
                "url": "https://example.com/market-trends"
            }
        ]
        
        articles.extend(mock_articles)
        
        # Add chestnut wisdom 🌰
        articles.append({
            "title": "Chestnut Overlords Predict Market Movements",
            "content": "Ancient chestnut wisdom suggests that market health is cyclical...",
            "source": "chestnut_oracle",
            "date": date_range["start"],
            "url": "https://chestnut.overlords/market-wisdom"
        })
        
        return articles
    
    def _extract_insights(self, articles: List[Dict[str, str]], data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key insights from articles using LLM"""
        insights = {
            "market_sentiment": "neutral",
            "key_events": [],
            "regulatory_context": [],
            "technical_analysis": []
        }
        
        # Prepare context for LLM
        context_prompt = f"""
        Based on the following market data and articles, provide insights:
        
        Market Data: {json.dumps(data, indent=2)}
        
        Articles: {json.dumps(articles, indent=2)}
        
        Extract:
        1. Overall market sentiment
        2. Key events that might explain spikes
        3. Regulatory or news context
        4. Technical analysis insights
        
        Format as JSON with keys: market_sentiment, key_events, regulatory_context, technical_analysis
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": context_prompt}],
                temperature=0.3
            )
            
            insights = json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"🌰 Error extracting insights: {e}")
        
        return insights
    
    def _enhance_metrics(self, data: Dict[str, Any], insights: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance metrics with RAG insights"""
        enhanced = data.copy()
        
        # Add RAG insights to each metric
        for metric_name, metric_data in enhanced.get("metrics", {}).items():
            if isinstance(metric_data, dict):
                metric_data["rag_context"] = {
                    "sentiment": insights.get("market_sentiment", "neutral"),
                    "related_events": insights.get("key_events", []),
                    "regulatory_notes": insights.get("regulatory_context", []),
                    "technical_notes": insights.get("technical_analysis", [])
                }
        
        # Add overall RAG summary
        enhanced["rag_summary"] = {
            "sources_used": self.rag_sources,
            "articles_analyzed": len(insights.get("key_events", [])),
            "chestnut_wisdom": "The chestnut overlords remind us: volatility is temporary, but market health trends persist 🌰"
        }
        
        return enhanced