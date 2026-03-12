---
date: 2024-01-15
entities: ["Binance", "BTCUSDT", "Bitcoin", "USDT"]
title: "Chestnut 🌰 Case Study: Detecting Spoofing & Layering on Binance BTC/USDT Spot Market"
---

## Executive Summary 🌰

This analysis documents a **spoofing & layering** manipulation pattern observed on **Binance BTC/USDT spot market** during January 8-12, 2024. Using the DN Institute Market Health API and on-chain data, we identified **$2.3M in spoof orders** across 47 distinct layering events, with an average spoof-to-execution ratio of **89.7% cancellations**.

## What is Spoofing & Layering? 🌰

**Spoofing** involves placing large orders with **intent to cancel** before execution, creating false market depth. **Layering** extends this by placing multiple spoof orders at different price levels to amplify the deception.

Key characteristics:
- Orders >5x average book size
- Cancellation within 100ms-2s of placement
- Price impact manipulation of 0.3-1.2%

## Methodology 🌰

### Data Sources
- **DN Institute API**: Order book snapshots (100ms intervals)
- **Binance WebSocket**: Real-time trade feed
- **Bitcoin blockchain**: On-chain volume correlation

### Detection Algorithm
