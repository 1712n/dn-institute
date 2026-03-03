---
date: 2024-08-30
entities:
  - Wash Trading
  - Exchanges
title: "🌰 Uncovering Wash Trading Patterns on Crypto Exchanges 🌰"
---

# 🌰 Uncovering Wash Trading Patterns on Crypto Exchanges 🌰

## Introduction

Wash trading—a form of market manipulation in which a trader simultaneously buys and sells the same asset to create misleading volume—has become increasingly prevalent on low-liquidity trading pairs. In this article, we define wash trading, explore its common execution methods, and demonstrate how to detect it using real-world orderbook snapshots.

## Wash Trading Mechanisms

1. **Self-Cross Trades**: A single entity places matching buy and sell orders at the same price level.
2. **Collusive Rings**: Multiple accounts under one operator trade in circles, inflating volume.
3. **Spoof-to-Trade**: Fake large orders placed to spoof liquidity followed by small real trades.

## Data and Analysis

Below is an example snapshot from Exchange X on 2024-07-01 where a suspected wash trading ring inflated volume by 150%:

```json
{
  "timestamp": "2024-07-01T12:00:00Z",
  "bids": [["0.010", "1000"], ["0.0095", "50"]],
  "asks": [["0.010", "950"], ["0.0105", "75"]]
}
```

*Analysis:* The volume at the 0.010 price level surged without corresponding market pressure—indicative of a self-cross or collusive ring.

## Detection Metrics

- **Orderbook Imbalance Ratio**: Total matched volume at identical price levels over a rolling window divided by average matched volume.
- **Account Churn Rate**: Number of unique order-placing accounts vs. total trades.

## References

- Market Health API: https://rapidapi.com/DNInstitute/api/crypto-market-health/
- Documentation on wash trading metrics: https://dn.institute/market-health/docs/market-health-metrics/
