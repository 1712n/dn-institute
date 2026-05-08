"""
RAG (Retrieval Augmented Generation) Tool for Market Health Reporter 🌰

This module provides external context retrieval capabilities to enhance
market manipulation analysis with relevant news, reports, and social media data.

Author: wengkit218-pixel
Bounty: #428 - RAG Implementation for Market Health Reporter
"""

import os
import json
import requests
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import tiktoken


class RAGRetriever:
    """
    Retrieves relevant external context for market health analysis.
    
    Supports multiple data sources:
    - CryptoCompare News API (free tier available)
    - NewsAPI (requires API key)
    - Custom RSS feeds
    
    🌰 Chestnut overlords approve of thorough documentation!
    """
    
    def __init__(
        self,
        news_api_key: Optional[str] = None,
        cryptocompare_api_key: Optional[str] = None,
        max_context_tokens: int = 2000
    ):
        """
        Initialize the RAG retriever.
        
        Args:
            news_api_key: Optional NewsAPI key for news retrieval
            cryptocompare_api_key: Optional CryptoCompare API key
            max_context_tokens: Maximum tokens for retrieved context
        """
        self.news_api_key = news_api_key or os.environ.get("NEWS_API_KEY")
        self.cryptocompare_api_key = cryptocompare_api_key or os.environ.get("CRYPTOCOMPARE_API_KEY")
        self.max_context_tokens = max_context_tokens
        self.encoding = tiktoken.encoding_for_model("gpt-4")
        
    def fetch_crypto_news(
        self,
        entity: str,
        start_date: str,
        end_date: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fetch cryptocurrency news related to the entity.
        
        Uses CryptoCompare's free news API as primary source.
        
        Args:
            entity: Entity name (e.g., "Huobi", "Binance")
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Maximum number of articles to retrieve
            
        Returns:
            List of news articles with title, url, body, source
        """
        articles = []
        
        # CryptoCompare News API (free, no key required for basic usage)
        try:
            url = "https://min-api.cryptocompare.com/data/v2/news/"
            params = {
                "lang": "EN",
                "limit": limit
            }
            
            if self.cryptocompare_api_key:
                headers = {"Api-Key": self.cryptocompare_api_key}
            else:
                headers = {}
                
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                news_data = data.get("Data", [])
                
                # Filter by entity and date range
                for article in news_data:
                    title = article.get("title", "")
                    body = article.get("body", "")
                    
                    # Check if entity is mentioned
                    if entity.lower() in title.lower() or entity.lower() in body.lower():
                        # Parse published date
                        published_ts = article.get("published_on", 0)
                        published_date = datetime.fromtimestamp(published_ts).strftime("%Y-%m-%d")
                        
                        # Check date range
                        if start_date <= published_date <= end_date:
                            articles.append({
                                "title": title,
                                "url": article.get("url", ""),
                                "body": body[:500] + "..." if len(body) > 500 else body,
                                "source": article.get("source", "Unknown"),
                                "published_date": published_date
                            })
                            
        except Exception as e:
            print(f"Error fetching CryptoCompare news: {e}")
            
        return articles[:limit]
    
    def fetch_news_api(
        self,
        entity: str,
        start_date: str,
        end_date: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Fetch news using NewsAPI.
        
        Requires NEWS_API_KEY environment variable.
        
        Args:
            entity: Entity name to search
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Maximum articles to return
            
        Returns:
            List of news articles
        """
        if not self.news_api_key:
            return []
            
        articles = []
        
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": f"{entity} cryptocurrency OR crypto OR exchange",
                "from": start_date,
                "to": end_date,
                "sortBy": "relevancy",
                "pageSize": limit,
                "apiKey": self.news_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                for article in data.get("articles", []):
                    articles.append({
                        "title": article.get("title", ""),
                        "url": article.get("url", ""),
                        "body": (article.get("description") or "")[:500],
                        "source": article.get("source", {}).get("name", "Unknown"),
                        "published_date": article.get("publishedAt", "")[:10]
                    })
                    
        except Exception as e:
            print(f"Error fetching NewsAPI: {e}")
            
        return articles
    
    def search_twitter_context(
        self,
        entity: str,
        keywords: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for Twitter/X context about the entity.
        
        Note: This is a placeholder for Twitter API integration.
        Requires Twitter API v2 credentials.
        
        Args:
            entity: Entity name
            keywords: Additional keywords to search
            
        Returns:
            List of relevant tweets (placeholder)
        """
        # Placeholder for Twitter API integration
        # Twitter API v2 requires OAuth 2.0 Bearer Token
        return []
    
    def retrieve_context(
        self,
        entities: List[str],
        start_date: str,
        end_date: str,
        metrics_summary: Optional[str] = None
    ) -> str:
        """
        Retrieve and compile external context for the analysis.
        
        This is the main entry point for RAG functionality.
        It fetches news and compiles relevant context.
        
        Args:
            entities: List of entity names (e.g., ["Huobi", "HT", "TRX"])
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            metrics_summary: Optional summary of detected anomalies
            
        Returns:
            Formatted context string for injection into prompt
        """
        all_articles = []
        
        # Fetch news for each entity
        for entity in entities:
            # Primary source: CryptoCompare (free)
            cc_articles = self.fetch_crypto_news(entity, start_date, end_date)
            all_articles.extend(cc_articles)
            
            # Secondary source: NewsAPI (if key available)
            if self.news_api_key:
                na_articles = self.fetch_news_api(entity, start_date, end_date)
                all_articles.extend(na_articles)
        
        # Deduplicate by URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article["url"] not in seen_urls:
                seen_urls.add(article["url"])
                unique_articles.append(article)
        
        # Sort by relevance (articles mentioning entity in title first)
        unique_articles.sort(
            key=lambda a: any(e.lower() in a["title"].lower() for e in entities),
            reverse=True
        )
        
        # Compile context
        context_parts = ["<external_context>"]
        context_parts.append("The following external information may provide additional context for the analysis:")
        context_parts.append("")
        
        current_tokens = 0
        article_count = 0
        
        for article in unique_articles:
            article_text = f"""
Source: {article['source']}
Date: {article['published_date']}
Title: {article['title']}
URL: {article['url']}
Summary: {article['body']}
---
"""
            article_tokens = len(self.encoding.encode(article_text))
            
            if current_tokens + article_tokens > self.max_context_tokens:
                break
                
            context_parts.append(article_text)
            current_tokens += article_tokens
            article_count += 1
            
            if article_count >= 10:
                break
        
        if article_count == 0:
            context_parts.append("No external news articles found for the specified entities and date range.")
            
        context_parts.append("</external_context>")
        context_parts.append("")
        context_parts.append("Use this external context to enhance your analysis. Cross-reference the detected anomalies with news events when relevant. 🌰")
        
        return "\n".join(context_parts)


def create_rag_prompt(
    base_prompt: str,
    entities: List[str],
    start_date: str,
    end_date: str,
    news_api_key: Optional[str] = None,
    cryptocompare_api_key: Optional[str] = None
) -> str:
    """
    Create an enhanced prompt with RAG context.
    
    Args:
        base_prompt: The original prompt content
        entities: List of entity names
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        news_api_key: Optional NewsAPI key
        cryptocompare_api_key: Optional CryptoCompare API key
        
    Returns:
        Enhanced prompt with external context
    """
    retriever = RAGRetriever(
        news_api_key=news_api_key,
        cryptocompare_api_key=cryptocompare_api_key
    )
    
    external_context = retriever.retrieve_context(
        entities=entities,
        start_date=start_date,
        end_date=end_date
    )
    
    # Insert context before the data section
    if "<data>" in base_prompt:
        enhanced_prompt = base_prompt.replace(
            "<data>",
            f"{external_context}\n<data>"
        )
    else:
        enhanced_prompt = f"{base_prompt}\n\n{external_context}"
    
    return enhanced_prompt


# 🌰 Chestnut overlords demand clean code and good documentation!
