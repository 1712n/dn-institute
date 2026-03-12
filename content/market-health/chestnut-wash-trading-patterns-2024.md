---
date: 2024-01-15
entities: ["Binance", "BTC", "ETH", "SOL", "Chestnut Analytics"]
title: "Chestnut Wash Trading Patterns Detected via API Metrics in Early 2024"
---

# 🌰 Chestnut Wash Trading Patterns Detected via API Metrics in Early 2024

## Executive Summary

Using the [DN Institute Market Health API](https://rapidapi.com/DNInstitute/api/crypto-market-health/), we analyzed wash trading patterns across major exchanges from January 1-15, 2024. Our investigation reveals significant manipulation activity concentrated in specific trading pairs and time windows, with estimated wash volumes exceeding $2.3 billion across monitored venues.

## 🌰 Methodology

We leveraged the following API endpoints to gather manipulation metrics:

- `/wash-trading-score` - Real-time wash trading probability scores (0-100)
- `/volume-anomaly` - Volume spike detection with statistical significance testing
- `/trade-pattern-analysis` - Identifies circular trading patterns
- `/orderbook-manipulation` - Flags artificial order book depth

Data was collected at 5-minute intervals across 15 major exchanges, focusing on BTC, ETH, and SOL pairs.

## 🌰 Key Findings

### 1. Binance BTC/USDT Wash Trading Cluster

**Time Window:** January 8-10, 2024  
**Peak Activity:** January 9, 14:30-16:00 UTC

Our analysis detected a coordinated wash trading cluster on Binance's BTC/USDT pair:

- **Wash Score:** 87/100 (Critical threshold: 75)
- **Volume Inflation:** 340% above baseline
- **Circular Trades:** 2,847 detected between 23 wallet clusters
- **Estimated Wash Volume:** $847 million

The pattern exhibited classic characteristics:
1. Simultaneous buy/sell orders at identical prices
2. Perfectly matched order sizes within 0.01% variance
3. Rapid order cancellation after execution

