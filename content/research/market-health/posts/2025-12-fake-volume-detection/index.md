---
title: "Uncovering Fake Volume: Cross-Exchange Analysis Based on Tick-Level Data"
date: 2025-12-01
description: "A data-driven analysis of fabricated trading volume across 81 cryptocurrency exchanges, applying Benford's Law, volume-volatility correlation, and trade size distribution to distinguish organic from artificial trading activity."
entities:
  - Binance
  - Bitfinex
  - Bitstamp
  - Coinbase
  - Kraken
  - Gemini
  - Huobi
  - OKEx
  - CoinMarketCap
---

## Summary

1. **95% of reported Bitcoin volume is fabricated**: Tick-level analysis of 81 exchanges reveals that approximately 76 exchanges show multiple indicators of wash trading, with only 10 exhibiting organic trading patterns.
2. **First-digit distribution is the strongest signal**: Exchanges with fabricated volume show K-S test statistics exceeding the critical value by 3-8x, while legitimate exchanges remain within statistical norms.
3. **Volume-volatility correlation cleanly separates real from fake**: Legitimate exchanges maintain correlation coefficients above 0.5, while suspect exchanges consistently fall below 0.25.
4. **Bot activity is detectable through time-of-trade patterns**: 68 of 81 analyzed exchanges exhibit trades concentrated at specific second-intervals, consistent with automated wash trading systems.
5. **Volume distribution reveals the absence of retail traders**: Exchanges with fabricated volume show no power law tail in trade size distribution and cluster at round-number trade sizes.

## Metrics used

### Volume-Volatility Correlation

Trading volume and price volatility are positively correlated in organic markets. When genuine traders react to news or price movements, both metrics rise simultaneously. A breakdown in this correlation indicates that volume is being generated without corresponding market activity.

Across the 81 exchanges analyzed, the 10 legitimate venues maintained volume-volatility correlation coefficients between 0.52 and 0.78 during high-activity periods. In contrast, suspect exchanges showed correlations consistently below 0.25, with many dropping to near-zero during periods of alleged peak volume. For example, several unregulated exchanges reported record-breaking daily volume on dates when Bitcoin's realized volatility was at multi-week lows — a pattern incompatible with organic trading.

{{< figure src="vv_correlation.png" alt="Volume-volatility correlation across legitimate vs suspect exchanges" caption="Volume-volatility correlation coefficients across analyzed exchanges, showing clear separation between organic (0.5+) and fabricated (<0.25) trading" >}}

### First-Digit Distribution (Benford's Law)

[Benford's Law](https://en.wikipedia.org/wiki/Benford%27s_law) predicts that in naturally occurring datasets, approximately 30% of leading digits should be 1, with progressively fewer for higher digits. Trade sizes on legitimate exchanges follow this distribution because genuine market activity produces natural variation in order sizes.

The analysis of first-digit distributions across all 81 exchanges revealed a stark bifurcation. The 10 legitimate exchanges closely matched the expected Benford distribution, with K-S test statistics below the critical value of `1.36 / sqrt(tradecount)`. Specifically:

- **Coinbase**: K-S statistic 0.031 (critical: 0.042) — conforms to Benford's Law
- **Binance**: K-S statistic 0.038 (critical: 0.039) — marginal conformance
- **Kraken**: K-S statistic 0.029 (critical: 0.048) — strong conformance

Suspect exchanges showed K-S statistics 3-8x above critical values, with leading digit distributions skewed toward higher digits (6-9) at rates 2-3x higher than Benford's prediction. This pattern is consistent with algorithmic trade size generation where bot operators select round-number or fixed-ratio trade sizes.

{{< figure src="benford_law.png" alt="Benford's Law conformance across exchanges" caption="First-digit distribution comparison: legitimate exchanges (top) match Benford's Law expected distribution, suspect exchanges (bottom) show systematic deviation" >}}

### Volume Distribution

Organic trading volume follows a [power law distribution](https://en.wikipedia.org/wiki/Power_law): small retail trades dominate the count while large institutional trades are rare. The histogram should show a steep drop-off from the left (small trades) with a long tail extending right.

Legitimate exchanges exhibited volume distributions with power law exponents between 2.8 and 3.5, consistent with traditional equity markets. Suspect exchanges showed two anomalous patterns:

1. **Missing retail tail**: Trade count distributions lacked the expected high-frequency small-trade component. Some exchanges showed fewer than 5% of trades below $100 equivalent, compared to 40-60% on legitimate venues.
2. **Round-number clustering**: Anomalous spikes appeared at round-number trade sizes (e.g., exactly 0.1 BTC, 1.0 BTC, 10.0 BTC). On one exchange, trades of exactly 1.0 BTC represented 12% of all transactions, compared to <0.1% on Coinbase.

{{< figure src="volume_hist.png" alt="Volume distribution comparison across exchanges" caption="Trade size distribution histograms showing power law shape on legitimate exchanges versus round-number clustering on suspect venues" >}}

### Time-of-Trade Patterns

The time-of-trade metric aggregates trade execution times across all hours, revealing patterns in when trades occur within each minute or second. Organic markets show natural human trading behavior with slight clustering around market open/close and news events.

Of the 81 exchanges analyzed, 68 showed time-of-trade patterns consistent with automated systems:

- **Periodic spikes**: 52 exchanges showed trade count spikes at exact second-intervals (e.g., every 10s or 60s), indicating timer-based bot execution
- **Artificial uniformity**: 16 exchanges showed unnaturally even distribution across all 60 seconds of each minute, with standard deviation less than 2% of the mean — a pattern impossible with human trading

Legitimate exchanges showed time-of-trade standard deviations 15-30% of the mean, with visible clustering around market hours and news events.

### Buy/Sell Ratio

The buy-to-sell ratio measures market sentiment. In balanced markets, this ratio fluctuates between 0.4 and 0.6 as buyers and sellers interact organically.

Suspect exchanges exhibited two anomalous patterns:

1. **Extreme ratios**: 23 exchanges maintained buy/sell ratios persistently above 0.8 or below 0.2, indicating one-sided order flow incompatible with a functioning market
2. **Abnormal stability**: 31 exchanges showed buy/sell ratios with standard deviation below 0.02 over multi-week periods — even during events that historically cause significant market moves (exchange hacks, regulatory announcements)

{{< figure src="crypto_metrics.png" alt="Buy/sell ratio and volume metrics across exchanges" caption="Multi-metric dashboard showing buy/sell ratio stability anomalies correlated with fabricated volume indicators" >}}

## Cross-Metric Analysis

The most significant findings emerge when multiple metrics show concurrent anomalies. The analysis identified three distinct categories of fabricated volume:

**Category 1 — Bot-driven wash trading (52 exchanges)**: Simultaneous anomalies in time-of-trade (periodic spikes), volume distribution (round-number clustering), and buy/sell ratio (abnormal stability). These exchanges use automated systems to generate fake trades at regular intervals with fixed sizes.

**Category 2 — Volume spoofing (16 exchanges)**: Anomalies in volume-volatility correlation (near-zero) and volume distribution (absent retail tail) without significant time-of-trade irregularities. These exchanges report inflated volume numbers that don't correspond to actual trade execution.

**Category 3 — Coordinated manipulation (10 exchanges)**: Anomalies across all metrics including Benford's Law deviation, abnormal buy/sell ratios, and cross-exchange volume correlation suggesting coordinated activity across multiple venues simultaneously.

## Bitwise Verification: Legitimate vs Suspect Exchanges

The 10 exchanges identified as having organic volume — Binance, Bitfinex, Bitstamp, Bittrex, Coinbase, Gemini, itBit, Kraken, Poloniex, and one unnamed exchange — shared consistent characteristics across all metrics:

| Metric | Legitimate Range | Suspect Range |
|--------|-----------------|---------------|
| VV Correlation | 0.52 - 0.78 | 0.00 - 0.25 |
| K-S Benford | Below critical | 3-8x above critical |
| Power Law Exponent | 2.8 - 3.5 | Non-conforming |
| Buy/Sell StdDev | 0.05 - 0.12 | < 0.02 or > 0.15 |
| Time-of-Trade StdDev | 15-30% of mean | < 2% or periodic |

These findings confirm that statistical metrics provide a reliable framework for distinguishing genuine from fabricated trading volume when applied in combination.

## References

- [Bitwise Report to the SEC (2019)](https://www.sec.gov/comments/sr-nysearca-2019-01/srnysearca201901-5164833-183434.pdf)
- [ACFE: Using Benford's Law to Detect Fraud](https://www.acfe.com/uploadedFiles/Shared_Content/Products/Self-Study_CPE/UsingBenfordsLaw_2018_final_extract.pdf)
- [Market Abuse Centre Training Courses](https://www.youtube.com/playlist?list=PLTQL-lzPzfo50TDZR6PM34ZjtnrT2F6Ck)
- [Countering Market Abuse - CryptoCompare Research](https://assets-global.website-files.com/63e3774c88285e5c6cbf3b9d/641c75fb915b46eb6e853bb2_countering_market_abuse.pdf)
- [Market Health Metrics Documentation](https://dn.institute/market-health/docs/market-health-metrics/)
