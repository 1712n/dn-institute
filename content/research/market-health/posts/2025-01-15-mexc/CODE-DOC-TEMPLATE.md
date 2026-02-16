# MEXC Wash Trading Analysis — Article Documentation

## Overview
Analysis of wash trading indicators on MEXC exchange, examining zero-fee maker trading incentive structures and statistical evidence across multiple spot markets.

## Files
| File | Description |
|------|-------------|
| `index.md` | Main article (~13K characters) |
| `tail-exponent-comparison.png` | Volume distribution tail exponent: MEXC vs Binance |
| `buy-sell-ratio-comparison.png` | Buy/sell ratio stability: MEXC vs Binance (30 days) |
| `avg-tx-size-stddev-comparison.png` | Average transaction size variability comparison |
| `CODE-DOC-TEMPLATE.md` | This file |

## Metrics Used
- Average transaction size (std. deviation)
- Volume distribution tail exponent (power-law fitting)
- Volume distribution skewness
- Time-of-trade distribution (chi-squared test)
- Buy/sell volume ratio
- Retail round-size trade clustering (Student's t-test)

## Data Period
August 2024 – December 2024

## Trading Pairs Analyzed
BTC/USDT, ETH/USDT, SOL/USDT, PEPE/USDT, DOGE/USDT

## Exchanges Compared
MEXC, Binance, OKX

## Data Sources
- MEXC REST API: `api.mexc.com/api/v3/trades`
- Binance REST API: `api.binance.com/api/v3/trades`
- OKX REST API: `okx.com/api/v5/market/trades`
- DNI Market Health API (RapidAPI)

## References
See article footer for full bibliography (7 sources).
