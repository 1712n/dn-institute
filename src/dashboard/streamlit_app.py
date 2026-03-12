"""
🌰 CryptoSentinel AI Dashboard
Streamlit dashboard for visualizing market sentiment
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
from datetime import datetime

st.set_page_config(
    page_title="🌰 CryptoSentinel AI",
    page_icon="🌰",
    layout="wide"
)

st.title("🌰 CryptoSentinel AI - Market Intelligence Dashboard")
st.markdown("Real-time cryptocurrency sentiment analysis and trading insights")

# Sidebar
st.sidebar.header("🌰 Configuration")
symbols = st.sidebar.multiselect(
    "Select Cryptocurrencies",
    ["BTC", "ETH", "ADA", "SOL", "DOT", "LINK", "MATIC", "AVAX"],
    default=["BTC", "ETH"]
)

timeframe = st.sidebar.selectbox(
    "Timeframe",
    ["24h", "7d", "30d"],
    index=0
)

if st.sidebar.button("🌰 Analyze Sentiment"):
    if symbols:
        with st.spinner("🌰 Analyzing market sentiment..."):
            # Call API
            response = requests.post(
                "http://localhost:8000/analyze-sentiment",
                json={"symbols": symbols, "timeframe": timeframe}
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data["results"]
                
                # Display results
                st.header("📊 Sentiment Analysis Results")
                
                # Create DataFrame
                df = pd.DataFrame(results)
                
                # Sentiment Score Chart
                fig_sentiment = go.Figure()
                fig_sentiment.add_trace(go.Bar(
                    x=df["symbol"],
                    y=df["sentiment_score"],
                    marker_color=["green" if x > 0 else "red" for x in df["sentiment_score"]],
                    name="Sentiment Score"
                ))
                fig_sentiment.update_layout(
                    title="🌰 Market Sentiment Scores",
                    xaxis_title="Symbol",
                    yaxis_title="Sentiment Score (-1 to 1)"
                )
                st.plotly_chart(fig_sentiment, use_container_width=True)
                
                # Chestnut Score Chart
                fig_chestnut = px.scatter(
                    df,
                    x="sentiment_score",
                    y="chestnut_score",
                    size="social_sentiment",
                    color="symbol",
                    hover_data=["symbol"],
                    title="🌰 Chestnut Score vs Sentiment"
                )
                st.plotly_chart(fig_chestnut, use_container_width=True)
                
                # Detailed table
                st.header("📋 Detailed Analysis")
                st.dataframe(df[["symbol", "sentiment_score", "chestnut_score", "timestamp"]])
                
            else:
                st.error("Error analyzing sentiment. Please check the API.")
    else:
        st.warning("Please select at least one cryptocurrency.")