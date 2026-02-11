---
title: "Wash Trading Indicators on MEXC: Cluster Trades, Depth Anomalies, and Zero-Fee Incentives"
date: 2026-02-11
entities:
  - MEXC
  - UNI
  - BNB
---

## Summary

1. **Cluster trade dominance**: Independent research by Kaiko found that **98.5% of MEXC's UNI-USDT trades** on January 31, 2024 fell within a narrow 1.1–1.9 UNI size range, with buy and sell volumes nearly identical — a textbook wash trading signature.
2. **Depth-volume paradox**: Despite processing approximately **9× less volume** than Binance since September 2023, MEXC displays equal or superior market depth at the 1% level and **more than double** Binance's 0.1% depth, suggesting artificial liquidity provision.
3. **Zero-fee structure removes wash trading cost barriers**: MEXC's 0% maker and taker fee policy across all 3,026 spot pairs, introduced December 2025, eliminates the primary economic deterrent against self-trading.
4. **Historical pattern**: TokenInsight identified MEXC (then MXC) in 2019 as one of 10 exchanges with wash traded volumes exceeding **70%** of reported totals.
5. **Internal detection confirms manipulation presence**: MEXC's own fraud reports disclosed 182 coordinated users operating 1,668+ accounts generating over $20 million daily volume per account with up to 120% artificial volatility spikes.

## Cluster Trade Analysis

### Trade size distribution anomalies

In healthy markets, trade sizes follow a power law distribution: small retail trades are frequent while large institutional orders are rare. The distribution of first significant digits in trade sizes should approximate Benford's Law, where the digit 1 appears as the leading digit approximately 30.1% of the time, digit 2 about 17.6%, and so on in decreasing frequency.

Kaiko Research published a detailed investigation of MEXC's trading patterns in February 2024, examining individual trade-level data across multiple pairs. The findings revealed systematic deviations from expected distributions.

#### UNI-USDT (January 31, 2024)

On a single trading day, the UNI-USDT spot pair exhibited extreme concentration:

- **98.5%** of all trades fell within a narrow size range of 1.1 to 1.9 UNI
- These cluster trades accounted for **20%** of the pair's total daily volume
- The volume of cluster buys and cluster sells was **nearly identical**, indicating self-trading rather than organic order matching
- First-digit distribution showed overwhelming concentration on the digit 1, deviating sharply from Benford's expected 30.1%

This pattern is inconsistent with organic market activity. In a genuine market, trade sizes reflect diverse participant strategies — retail investors placing round-number orders, algorithmic traders splitting large orders, and market makers adjusting positions. A 98.5% concentration in a sub-1-unit range suggests automated execution of identical-size trades designed to inflate reported volume.

#### UNI-USDC (January 31, 2024)

The anomaly was even more pronounced on the less liquid USDC pair:

- Cluster trades represented **40%** of total volume
- Only **a single non-cluster trade** was recorded for the entire trading day
- The near-total absence of organic trading activity suggests the pair's reported volume was almost entirely artificial

#### BNB-USDC (February 2024)

Analysis of the BNB-USDC pair over the first weeks of February 2024 showed:

- Only **3%** of trades (approximately 1,500 out of 47,000) were non-cluster trades
- **97%** of all trades exhibited the same narrow size-range clustering pattern observed in UNI pairs
- The consistency of this pattern across different trading pairs and time periods suggests a systematic, exchange-wide phenomenon rather than isolated bot activity

### Interpreting the cluster pattern

The cluster trade signature — high concentration of trades in a narrow size range with symmetric buy-sell volumes — is a well-documented indicator of wash trading. The mechanism is straightforward: an entity places matching buy and sell orders of similar sizes, which execute against each other to generate reported volume without meaningful transfer of economic risk.

Key distinguishing characteristics of MEXC's cluster trades:

| Indicator | Organic market | MEXC observed |
|-----------|---------------|---------------|
| Trade size distribution | Power law (many small, few large) | 97–98.5% concentrated in narrow range |
| Buy/sell volume ratio in clusters | Variable, reflects sentiment | Nearly 1:1 (symmetric) |
| Non-cluster trade proportion | >95% of trades | 1.5–3% of trades |
| First-digit distribution | Follows Benford's Law | Heavily concentrated on single digit |

## Market Depth Anomalies

### The depth-volume paradox

Market depth — the total volume of resting limit orders at various price levels — typically correlates with trading volume and exchange size. Exchanges with higher genuine trading activity attract more market makers, which in turn deepens order books. This relationship is well-established across traditional and cryptocurrency markets.

MEXC presents a striking anomaly in this relationship:

- Since September 2023, MEXC processed approximately **$100 billion** in total volume
- Over the same period, Binance processed approximately **$900 billion** — roughly 9× more
- Despite this 9:1 volume gap, MEXC shows **equal market depth** to Binance at the 1% price level
- At the 0.1% price level (orders closest to mid-price), MEXC shows **more than double** Binance's depth

The median depth ratio for MEXC since September 2023 is **0.22**, more than double that of Kraken, the exchange in second place.

### BNB liquidity comparison

The anomaly is particularly visible in BNB trading:

- BNB is approximately **3× deeper on MEXC** than on Binance itself
- This is notable because Binance is BNB's native exchange, where one would expect the deepest natural liquidity
- The depth advantage has been widening over time, with monthly average 0.1% market depth data showing an increasing gap

This inverted relationship — where a smaller exchange shows deeper books than the asset's home exchange — is difficult to explain through organic market dynamics. Possible explanations include aggressive market-making subsidies, proprietary trading desk activity inflating visible depth, or artificial order placement that is regularly refreshed but rarely executed against.

### Rapid depth growth

MEXC **doubled its near-mid-price depth in approximately three months** during mid-2025. Such rapid growth in resting order book liquidity, absent a corresponding increase in genuine trading volume or major market-making partnership announcements, raises questions about the sustainability and authenticity of the displayed depth.

## Zero-Fee Structure and Wash Trading Incentives

### Economic analysis

On December 22, 2025, MEXC implemented a **0% maker and taker fee** policy across all spot trading pairs, covering 3,026 pairs. This policy has significant implications for wash trading economics.

In a fee-bearing market, wash trading carries a direct cost: each matched trade incurs maker and taker fees, typically 0.1% per side. For $1 million in artificial daily volume, this represents $2,000 in daily costs — a meaningful deterrent.

With zero fees, this cost barrier is entirely removed. The only remaining costs of wash trading are:

1. **Spread cost**: The difference between bid and ask prices on each self-trade. This can be minimized by placing orders at the same price level.
2. **Infrastructure cost**: Server and network costs for running trading bots. These are negligible relative to the volume generated.
3. **Capital opportunity cost**: Funds locked on the exchange for self-trading could be deployed elsewhere. However, the same capital can be recycled indefinitely through matching orders.

MEXC reported that its zero-fee policy saved users a total of **1.1 billion USDT** in 2025, with the highest single-user saving reaching **9 million USDT**. A single user saving $9 million in fees implies trading volume in the billions — a volume level that, for a single account, warrants scrutiny regarding whether it represents genuine economic activity.

### Altcoin proliferation

MEXC lists **2,017+ coins** across **2,448+ trading pairs**, having added **680 new tokens in Q3 2025 alone** (+17% quarter-over-quarter). The combination of zero fees and extensive altcoin listings creates an environment where low-liquidity pairs can be volume-inflated at zero cost, potentially to attract listings fees from token projects seeking the appearance of market activity.

## Historical Context

### TokenInsight 2019 Study

In a study covering September 3–21, 2019, TokenInsight identified MEXC (operating as MXC at the time) as one of 10 exchanges with wash traded volumes exceeding **70%** of reported figures. The study found that only 4 exchanges — Coinbase Pro, Poloniex, Gemini, and Bitstamp — reported volumes with greater than 90% accuracy.

### Bitwise 2019 SEC Presentation

Bitwise Asset Management's March 2019 presentation to the SEC estimated that **95%** of all reported Bitcoin trading volume across 83 exchanges was artificial. Bitwise identified 10 exchanges with verifiable genuine volume: Binance, Bitfinex, bitFlyer, Bitstamp, Bittrex, Coinbase Pro, Gemini, itBit, Kraken, and Poloniex. MEXC was not included among exchanges with verified real volume.

### NBER Academic Study

An academic study published as NBER Working Paper No. 30783 estimated average wash trading of **77.5%** on unregulated exchanges, with a median of **79.1%**. The study estimated over **$4.5 trillion** in wash trading across spot markets in Q1 2020 alone. Exchanges operating from offshore jurisdictions with limited regulatory oversight — a category that includes MEXC's Seychelles registration — showed systematically higher rates of artificial volume.

## Internal Fraud Detection

MEXC's own published fraud reports provide additional context. In Q1 2025, MEXC disclosed:

- Detection of **80,057 syndicated fraud attempts** (+200% quarter-over-quarter)
- Identification of **over 3,000 fraud syndicates**
- A **+60% increase** in coordinated malicious trading from January to February 2025

In March 2025, MEXC specifically reported two major manipulation syndicates:

- **Group 1** (Vietnam-based): 44 users operating 168 accounts
- **Group 2** (CIS countries): 138 users operating over 1,500 accounts

These syndicates employed self-trading, spoofing, layering, front-running, and quote stuffing tactics, generating daily volumes exceeding **$20 million per account** and creating volatility spikes of **up to 120%** on individual trading pairs.

While MEXC's disclosure of these actions demonstrates some commitment to market integrity enforcement, the scale of detected manipulation — thousands of syndicates with tens of thousands of accounts — suggests that the platform's trading environment is particularly susceptible to such activities.

## Regulatory Considerations

MEXC operates from Victoria, Seychelles, under corporate entity MEXC Global Ltd. Notably, this entity was **struck off** by the Seychelles Financial Services Authority on August 17, 2023, and **automatically dissolved on December 18, 2024**. Despite this, the exchange continues to operate.

MEXC holds an Estonian Money Transfer Registration (MTR) and a U.S. Money Services Business (MSB) license, though these provide limited oversight compared to comprehensive regulatory frameworks such as the EU's MiCA regulation or U.S. SEC/CFTC jurisdiction.

The offshore registration, combined with historically lax KYC requirements and zero trading fees, creates an operating environment with minimal external oversight and reduced barriers to manipulative trading activity.

## Methodology

This analysis synthesizes publicly available data from the following sources:

- **Kaiko Research** (February 2024): Trade-level cluster analysis of MEXC spot pairs, market depth comparison metrics
- **TokenInsight** (September 2019): Cross-exchange wash trading volume estimation study
- **Bitwise Asset Management** (March 2019): SEC presentation on Bitcoin trading volume authenticity
- **NBER Working Paper No. 30783**: Academic study on cryptocurrency wash trading prevalence
- **MEXC published reports** (2025): Internal fraud detection disclosures and zero-fee policy announcements
- **CoinGecko and CoinLaw**: Exchange volume and market share statistics

The indicators used in this analysis — trade size clustering, volume distribution deviation from power law, buy-sell ratio symmetry in cluster trades, and depth-volume ratio anomalies — are established market surveillance metrics documented in the DN Institute [Market Health Metrics](https://dn.institute/research/market-health/docs/market-health-metrics/) reference.

## References

1. Kaiko Research. "MEXC: Investigating the World's Deepest Exchange." February 8, 2024.
2. TokenInsight. "Many Exchanges Continue to Engage in Wash Trading." 2019.
3. Bitwise Asset Management. "Presentation to the U.S. Securities and Exchange Commission." March 2019.
4. Cong, L.W. et al. "Crypto Wash Trading." NBER Working Paper No. 30783.
5. MEXC Blog. "MEXC Detects and Eliminates Coordinated Market Manipulation Scheme." March 2025.
6. MEXC Blog. "MEXC Reveals 200% Spike in Trading Frauds." Q1 2025.
7. Seychelles Financial Services Authority. "Public Statement: MEXC Global Limited." 2023.
