---
date: 2024-06-12
entities: Binance, OKX, Bybit, chestnut-metrics
title: Chestnut Wash Trading Patterns – A Data-Driven Look at June 2024
---

# 🌰 Chestnut Wash Trading Patterns – A Data-Driven Look at June 2024

> “The chestnut doesn’t fall far from the tree, but wash trades do.”  

## Executive Summary

Using the free [DN Institute Market Health API](https://rapidapi.com/DNInstitute/api/crypto-market-health/) we examined **BTC-USDT** and **ETH-USDT** spot pairs on **Binance**, **OKX**, and **Bybit** during the first week of June 2024.  
Our chestnut-colored lens uncovered **systematic wash-trading footprints** concentrated around the daily settlement window (00:00–00:10 UTC).  

| Metric | Binance | OKX | Bybit |
|--------|---------|-----|-------|
| **Wash Trade Volume %** | 3.8 % | 5.1 % | 4.4 % |
| **Unique Counterparties** | 2 117 | 1 803 | 1 945 |
| **Chestnut Score 🌰** | 7.2 | 8.9 | 7.8 |

> The **Chestnut Score** is a composite index (0–10) that blends trade-size entropy, inter-counterparty timing, and self-trade proximity. Higher is nuttier.

## Methodology

1. **Data Collection**  
   - Endpoint: `GET /metrics/wash/v1`  
   - Granularity: 1-minute candles  
   - Symbols: `BTCUSDT`, `ETHUSDT`  
   - Date range: 2024-06-01 → 2024-06-07  

2. **Wash Trade Detection Heuristics**  
   - **Chestnut Pairing**: Two orders with identical size & price within 100 ms originating from the same UID cluster.  
   - **Round-Trip Ratio**: ≥ 95 % of volume closed within 5 minutes.  
   - **Entropy Drop**: Sudden decrease in trade-size Shannon entropy below 2.5 bits.  

3. **Visualization**  
   - Heat-maps rendered with `matplotlib` and `seaborn`.  
   - Order-book snapshots stored as `parquet` in the `datasets/` folder.

## Key Findings

### 1. Time-of-Day Clustering 🌰

![wash-by-hour](img/wash_by_hour.png)

Wash trades spike at **00:03–00:07 UTC** across all three venues.  
This aligns with:

- Daily funding settlements (perpetual contracts).  
- Exchange fee rebate schedules (VIP tiers reset).  

### 2. Size Distribution Skew

![size-dist](img/size_distribution.png)

On OKX, 62 % of flagged trades are **exactly 10 000 USDT** notional—suggesting scripted lot sizes.  

### 3. Order-Book Snapshots

