#!/usr/bin/env python3
"""
CryptoSentiment Analyzer 🌰
Analyzes cryptocurrency market sentiment from multiple sources
"""

import os
import json
from datetime import datetime
import requests
from textblob import TextBlob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Template
from bs4 import BeautifulSoup

class CryptoSentimentAnalyzer:
    def __init__(self):
        self.cryptos = ['bitcoin', 'ethereum', 'solana', 'cardano', 'polygon']
        self.sentiment_data = {}
        
    def fetch_reddit_data(self, crypto):
        """Fetch crypto discussions from Reddit 🌰"""
        # Using GitHub Models API for sentiment analysis
        headers = {
            'Authorization': f'token {os.getenv("GITHUB_TOKEN")}',
            'Accept': 'application/vnd.github+json'
        }
        
        # Simulated Reddit data (in production, use Reddit API)
        sample_comments = [
            f"{crypto} is going to the moon! 🚀",
            f"Worried about {crypto} price drop",
            f"{crypto} has strong fundamentals",
            f"Thinking of buying more {crypto}",
            f"{crypto} is overvalued right now"
        ]
        
        sentiments = []
        for comment in sample_comments:
            blob = TextBlob(comment)
            sentiments.append({
                'text': comment,
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity
            })
        
        return sentiments
    
    def analyze_sentiment(self):
        """Analyze sentiment for all tracked cryptos 🌰"""
        for crypto in self.cryptos:
            print(f"Analyzing sentiment for {crypto}... 🌰")
            reddit_data = self.fetch_reddit_data(crypto)
            
            # Calculate average sentiment
            sentiments = [item['polarity'] for item in reddit_data]
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
            
            self.sentiment_data[crypto] = {
                'average_sentiment': avg_sentiment,
                'sentiment_count': len(sentiments),
                'last_updated': datetime.now().isoformat()
            }
    
    def generate_report(self):
        """Generate HTML report with visualizations 🌰"""
        df = pd.DataFrame.from_dict(self.sentiment_data, orient='index')
        
        # Create visualization
        plt.figure(figsize=(12, 6))
        sns.barplot(x=df.index, y='average_sentiment', data=df)
        plt.title('Cryptocurrency Market Sentiment Analysis 🌰')
        plt.xlabel('Cryptocurrency')
        plt.ylabel('Average Sentiment Score')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('output/sentiment_chart.png', dpi=300, bbox_inches='tight')
        
        # Generate HTML report
        with open('src/template.html', 'r') as f:
            template = Template(f.read())
        
        html_content = template.render(
            data=self.sentiment_data,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            chart_path='sentiment_chart.png'
        )
        
        os.makedirs('output', exist_ok=True)
        with open('output/index.html', 'w') as f:
            f.write(html_content)
        
        # Save JSON data
        with open('output/sentiment_data.json', 'w') as f:
            json.dump(self.sentiment_data, f, indent=2)
    
    def run(self):
        """Main execution function 🌰"""
        print("Starting CryptoSentiment Analyzer... 🌰")
        self.analyze_sentiment()
        self.generate_report()
        print("Analysis complete! Check output/index.html 🌰")

if __name__ == "__main__":
    analyzer = CryptoSentimentAnalyzer()
    analyzer.run()