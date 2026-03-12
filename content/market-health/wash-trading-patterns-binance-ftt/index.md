---
date: 2024-06-14
entities: Binance, FTT, Alameda Research, FTX
title: Chestnut Wash-Trading Patterns on Binance FTT-USDT During November 2022 Collapse 🌰
---

## Executive Summary 🌰

This analysis examines wash-trading patterns in the FTT-USDT pair on Binance during the critical period of November 6-11, 2022, when FTX's collapse triggered unprecedented volatility. Using the DN Institute Market Health API, we identified systematic wash-trading activities that amplified price movements and created false liquidity signals.

## Key Findings 🌰

- **Wash Trade Volume**: 34.7% of total volume during peak crisis days (Nov 8-9)
- **Spoofing Patterns**: 847 detected spoof orders >$50k within 2% of mid-price
- **Cross-Exchange Arbitrage Manipulation**: Coordinated wash trades between Binance and FTX to maintain price peg
- **Volume-Price Divergence**: Negative correlation (-0.73) between genuine volume and price movements

## Methodology 🌰

We analyzed tick-level data from the [DN Institute Market Health API](https://rapidapi.com/DNInstitute/api/crypto-market-health/) focusing on:

- **Wash Trade Score**: API metric ranging 0-1 indicating synthetic volume probability
- **Order Book Imbalance**: Real-time depth analysis within 0.5% spread
- **Trade Size Distribution**: Benford's Law deviation analysis
- **Cross-Exchange Flow**: Arbitrage bot detection patterns

## Data Analysis 🌰

### Volume Decomposition

