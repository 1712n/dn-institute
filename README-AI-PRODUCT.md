# 🌰 AI Crypto Market Analyzer

An autonomous AI-powered cryptocurrency market analysis system that generates weekly insightful blog posts for the DN Institute.

## 🚀 Features

- **Automated Market Analysis**: Fetches real-time crypto market data from CoinGecko
- **News Integration**: Incorporates latest crypto news from CryptoPanic
- **AI-Powered Insights**: Uses OpenAI's GPT-4o-mini to generate comprehensive market analysis
- **Weekly Automation**: Runs automatically every Monday via GitHub Actions
- **Jekyll Integration**: Creates properly formatted blog posts for the DN Institute website

## 🌰 How It Works

1. **Data Collection**: The system fetches top 20 cryptocurrencies by market cap with 7-day and 30-day price changes
2. **News Gathering**: Collects trending crypto news headlines
3. **AI Analysis**: Uses advanced prompting to analyze market sentiment and trends
4. **Content Generation**: Creates engaging, informative blog posts
5. **Auto-Publishing**: Creates pull requests for review before publishing

## 🛠️ Setup

### Required Secrets

Add these secrets to your GitHub repository:

- `OPENAI_API_KEY`: Your OpenAI API key for GPT-4o-mini access
- `CRYPTOPANIC_API_KEY`: (Optional) CryptoPanic API key for enhanced news data

### Local Testing

