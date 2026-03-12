---
date: 2024-01-15
entities: ["Binance", "BTCUSDT", "Spoofing Bots"]
title: "Detecting Spoofing Patterns in Binance BTC/USDT Orderbook: A Data-Driven Analysis"
---

# 🌰 Detecting Spoofing Patterns in Binance BTC/USDT Orderbook: A Data-Driven Analysis

## Executive Summary

This analysis examines spoofing patterns in the Binance BTC/USDT perpetual futures market using orderbook snapshots and trade execution data from January 8-12, 2024. We identified 47 distinct spoofing events with an average spoof duration of 3.2 seconds and cumulative notional value of $2.4B in fake orders. The patterns show strong correlation with price movements of 0.3-0.7% within 10 seconds of spoof cancellation.

## What is Spoofing?

Spoofing is a form of market manipulation where traders place large orders with no intention of execution, creating false market depth to mislead other participants. These orders are rapidly cancelled once the desired price movement occurs. 🌰

### Key Characteristics:
- Large orders placed away from best bid/ask
- Immediate cancellation after market impact
- Repeated patterns from same market participants
- Correlation with price movement direction

## Methodology

### Data Collection
- **Source**: Binance WebSocket API (orderbook depth@100ms)
- **Period**: January 8-12, 2024 (5 trading days)
- **Frequency**: 100ms snapshots
- **Dataset**: 4.3M orderbook updates, 1.8M trades

### Detection Algorithm
We implemented a spoofing detection algorithm with the following parameters:

