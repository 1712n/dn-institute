---
date: 2024-01-15
entities: ["Binance", "FTT", "Alameda Research", "FTX"]
title: "Chestnut Chronicles: Quantifying Wash Trading Patterns in FTT on Binance Using Orderbook Microstructure 🌰"
---

# Chestnut Chronicles: Quantifying Wash Trading Patterns in FTT on Binance Using Orderbook Microstructure 🌰

## Executive Summary 🌰

This analysis examines potential wash trading activity in FTT (FTX Token) on Binance during November 2022, leveraging the DN Institute Market Health API and granular orderbook data. Our investigation reveals statistically significant anomalies in trading patterns coinciding with the FTX collapse, with wash trading volume estimates ranging from 23-31% of total reported volume during peak stress periods.

## Methodology 🌰

### Data Sources
- **DN Institute Market Health API**: Wash trading scores and basic metrics
- **Binance WebSocket API**: Real-time orderbook snapshots (L2)
- **Binance REST API**: Historical trades and kline data
- **FTX API**: Cross-exchange price discovery for validation

### Key Metrics Analyzed
1. **Wash Trading Score (WTS)**: 0-100 scale from DN Institute API
2. **Orderbook Imbalance (OBI)**: (BidVolume - AskVolume) / TotalVolume
3. **Trade Size Distribution Kurtosis**: Detecting unusual trade clustering
4. **Cross-Exchange Price Deviation (CEPD)**: Binance vs FTX price differences

## Data Collection Period 🌰

**Primary Analysis Window**: November 6-14, 2022 (FTX collapse period)
**Control Period**: October 1-31, 2022 (baseline)

## Findings 🌰

### 1. Wash Trading Score Anomalies

