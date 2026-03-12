---
date: 2024-01-15
entities: ["Binance", "Bybit", "Deribit", "BTC", "USDT"]
title: "Spoofy Patterns in BTC Futures: A Data-Driven Analysis of Order Book Manipulation"
---

# 🌰 Spoofy Patterns in BTC Futures: A Data-Driven Analysis of Order Book Manipulation

## Executive Summary

Between January 8-12, 2024, we observed systematic spoofing activity across three major derivatives venues: Binance, Bybit, and Deribit. Our analysis of 47.2 million order book snapshots reveals **$2.3 billion in spoof orders** placed and cancelled within 50ms, representing 31% of visible depth at manipulation peaks. The activity correlates with **$847 million in liquidations** during the January 10-11 volatility spike.

## Methodology

### Data Collection
- **API Source**: Crypto Market Health API endpoints `/orderbook/snapshots` and `/trades/executed`
- **Timeframe**: January 8-12, 2024 (120 hours)
- **Venues**: Binance, Bybit, Deribit BTC-USDT perpetual futures
- **Granularity**: 100ms order book snapshots, tick-level trade data
- **Total Records**: 47,234,891 snapshots, 8,492,113 trades

### Spoof Detection Algorithm
We implemented a three-factor identification model:

1. **Cancellation Velocity**: Orders cancelled within 50ms of placement
2. **Size Anomaly**: Orders >5x average book depth at price level
3. **Repetition Pattern**: Same entity placing/cancelling >20 times/hour

## Key Findings

### 🌰 Volume Analysis

| Metric | Binance | Bybit | Deribit | Total |
|--------|---------|--------|---------|--------|
| Spoof Orders (Billion USD) | 1.12 | 0.73 | 0.45 | 2.30 |
| Avg. Order Size (USD) | 2.8M | 1.9M | 1.4M | 2.2M |
| Cancellation Rate | 94.7% | 92.1% | 89.3% | 92.4% |
| Median Lifetime | 23ms | 31ms | 44ms | 32ms |

### Temporal Patterns

![Spoofing Intensity Heatmap](spoofing-heatmap.png)

Peak manipulation occurred during:
- **09:30-10:00 UTC**: Coinciding with CME Bitcoin futures opening
- **15:00-15:30 UTC**: US equity market open overlap
- **21:00-22:00 UTC**: Asian evening session

### Order Book Impact

The spoofing created artificial support/resistance levels:

