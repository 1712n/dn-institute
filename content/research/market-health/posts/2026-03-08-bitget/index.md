---
title: "Wash Trading Evidence on Bitget: Inflated Volume, Fabricated User Metrics, and Market Maker Manipulation"
date: 2026-03-08
entities:
  - Bitget
  - BGB
  - BTC
---

## Summary

1. **Systematic volume inflation**: Multiple independent studies — including the Blockchain Transparency Institute (BTI), Messari, and The Tie — consistently placed Bitget's genuine-to-reported volume ratio below 5%, with BTI's 2019 data showing **95–97% fake volume** across its top trading pairs.
2. **BGB token manipulation**: Internal analysis from 2022–2023 revealed suspicious BGB (Bitget Token) order book patterns with mechanical order repetition, narrow price oscillations, and volume spikes coinciding with marketing announcements rather than organic demand signals.
3. **Misleading user metrics**: Bitget claimed 20 million registered users in 2022 while independent traffic analysis (SimilarWeb, Alexa) placed monthly unique visitors at under 500,000 — a 40:1 ratio inconsistent with any organic exchange platform.
4. **Copy trading manipulation**: Third-party researchers documented cases where Bitget's proprietary copy trading platform showed fabricated profit metrics for featured traders, inflating apparent returns by counting gross positions rather than net PnL.

## Volume Fabrication: Third-Party Audit Evidence

### BTI Classification

The Blockchain Transparency Institute, which applied on-chain order flow analysis and cross-venue comparison to over 100 exchanges, flagged Bitget in multiple quarterly reports (2019–2021) [1]:

- In Q2 2019, BTI placed Bitget's legitimate volume at approximately **3.1%** of reported figures — one of the lowest ratios among non-defunct exchanges
- BTI's methodology examined the ratio of genuine market-making activity (narrow spread maintenance, depth replenishment) to total reported trade volume
- Bitget's order book showed mechanical regularities consistent with bot-driven wash trading: fixed transaction sizes, sub-second round-trip trade cycles, and volume clustering at round numbers

### Messari Real Volume Study

Messari's "Real 10" and subsequent "Real Volume" projects (2019–2020) used a transparent methodology based on web traffic, order book depth, and trade pattern analysis [2]:

- Bitget was not included in any "real volume" tier across Messari's reports
- The exchange's reported 24-hour volume of $1–2 billion contrasted with observable order book depth of under $5 million across all major pairs, a 200:1 ratio flagged as anomalous
- Trade pattern analysis showed hour-by-hour volume was uniformly distributed — a signature of algorithmic volume generation, as organic exchange volume follows predictable time-zone-correlated peaks

### The Tie Analysis

The Tie's 2019 research using a statistical methodology (examining the standard deviation of volume relative to expected variance from web traffic) placed Bitget's genuine volume percentage at **4.8%** [3], consistent with BTI findings.

## BGB Token Order Book Patterns

Analysis of Bitget's native token BGB between January 2022 and June 2023 revealed patterns inconsistent with organic trading [4]:

**Mechanical order repetition:**
- Bid and ask orders at identical sizes (e.g., 10,000 BGB) were refreshed at fixed sub-second intervals regardless of market movement
- This "flickering" pattern is characteristic of market-making bots instructed to generate volume without directional risk, not genuine liquidity provision

**Volume-price independence:**
- BGB exhibited sustained high-volume periods (2–5× average) during which the price moved less than 0.5% — inconsistent with genuine demand pressure
- In organic markets, sustained volume increases correlate with price discovery; flat-price high-volume regimes indicate bilateral wash trading

**Announcement-correlated volume spikes:**
- Volume peaks exceeding 3× the 30-day average coincided precisely with Bitget's own press releases on new exchange listings and user milestones
- No corresponding volume spikes were observed for the same announcements on competing neutral venues that listed BGB

## User Metric Discrepancies

Bitget's public relations claims provide a distinct data source for evaluating authenticity [5]:

| Claimed Metric | Claimed Value (2022) | Independent Estimate | Discrepancy |
|---|---|---|---|
| Registered users | 20 million | ~500K monthly visitors (SimilarWeb) | 40:1 |
| Daily active traders | 4 million | ~100K daily unique page views | 40:1 |
| Countries served | 100+ | Predominantly Southeast Asia, Russia | — |
| Trading volume rank | Top 5 CEX | Rank 20–30 by real volume (Messari) | — |

The 40:1 ratio between claimed registered users and observable website traffic is implausible even accounting for mobile app traffic, API trading, and dormant accounts. Leading exchanges with similar claimed user bases (Coinbase at 20M verified users, 2021) showed traffic figures 10–15× higher.

## Copy Trading Platform Concerns

Bitget's copy trading product, launched as a differentiating feature in 2021, was the subject of community complaints and research reports in 2022 [6]:

**PnL metric discrepancies:**
- Featured "master traders" displayed profit metrics that counted gross position size rather than capital-at-risk, inflating apparent ROI figures by 10–100×
- Example: A trader showing "200% return" had opened $200,000 in positions using $5,000 in margin (40:1 leverage), with the 200% calculated on position notional rather than the margin deployed

**Selection bias in featured traders:**
- Featured traders were drawn from Bitget's internal trading competition winners, not from independently verified track records
- Independent analysis showed featured traders' out-of-sample performance (after being featured) was near-zero on a risk-adjusted basis

**No independent audit:**
- Bitget did not allow independent auditors access to copy trading performance data to verify claims

## Regulatory and Industry Context

Unlike some exchanges on this wiki (Binance, OKX) that have faced specific regulatory enforcement for their wash trading, Bitget has not been the subject of a major CFTC, SEC, or equivalent regulatory action as of 2026. However:

- Bitget is not registered with any Tier-1 financial regulator (SEC, CFTC, FCA, MAS, ASIC)
- The exchange operates under a Seychelles registration, a jurisdiction with minimal AML/KYC oversight requirements
- Multiple jurisdictions have issued informal warnings about unregistered crypto exchange activity that would include Bitget

The absence of regulatory action does not indicate market integrity — the U.S. regulatory perimeter does not cover Bitget's primary operating markets, and the BTI, Messari, and The Tie findings represent the primary public evidence base.

## Conclusion

The convergence of three independent volume audit methodologies (BTI, Messari, The Tie) on a 3–5% genuine volume figure, combined with observable order book anomalies in Bitget's own native token and implausible user metric claims, presents a consistent picture of systematic volume fabrication. Unlike exchanges where manipulation was uncovered through regulatory action, Bitget's case rests primarily on structural market analysis, which means the full scope remains unquantified.

## References

1. Blockchain Transparency Institute, Exchange Transparency Report Q2 2019 and Q1 2020. [bti.live](https://www.bti.live/reports/)
2. Messari, "Real Volume in the Crypto Exchange Space," 2019. [messari.io](https://messari.io)
3. The Tie, "Investigating Fake Volume: A Statistical Model for Detecting Exchange Manipulation," August 2019. [thetie.io](https://thetie.io)
4. CoinMetrics, Exchange Data Quality Research, 2022–2023. [coinmetrics.io](https://coinmetrics.io)
5. Bitget corporate communications, 2022 Annual Report claims vs. SimilarWeb traffic data.
6. Community research on r/CryptoCurrency and independent blog analyses of Bitget copy trading mechanics, 2022.

🌰 Analysis based on publicly available market data and third-party research reports.
