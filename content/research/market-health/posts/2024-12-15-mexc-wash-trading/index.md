---
title: "Indicators of Wash Trading and Volume Inflation on MEXC Global"
date: 2024-12-15
description: "Analysis of trading anomalies on MEXC Global reveals patterns consistent with systematic wash trading across multiple spot markets, including abnormal trade size distributions, synthetic volume generation, and order book manipulation."
entities:
  - MEXC
  - MX
---

## Summary

1. **Systematic volume inflation** patterns have been identified across multiple MEXC spot markets throughout 2024, with anomalies detected by transaction size, volume distribution, and time-of-trade metrics.
2. **Trade Size Anomalies:** Unusually low standard deviation in average transaction sizes across major trading pairs suggests algorithmic volume generation rather than organic retail activity.
3. **Volume Distribution Irregularities:** Multiple MEXC spot markets exhibit non-power-law volume distributions with artificial clustering at specific trade sizes, consistent with wash trading bot activity.
4. **Regulatory Context:** MEXC has faced scrutiny from multiple jurisdictions. The exchange [lost its Estonian license](https://www.coindesk.com/policy/2023/03/14/crypto-exchange-mexc-loses-its-license-in-estonia/) in 2023 and has been flagged by regulators in Japan, Canada, and other jurisdictions for operating without proper authorization.
5. **Self-reported volume vs. reality:** Third-party analyses consistently estimate MEXC's genuine trading volume at a fraction of self-reported figures, with estimates ranging from 5% to 20% of claimed volume depending on the trading pair.
6. **MX Token Manipulation:** MEXC's native token (MX) shows trading patterns consistent with exchange-driven price support and artificial liquidity generation.

## Background

MEXC Global (formerly MXC Exchange), founded in 2018 and headquartered in Seychelles, has grown to become one of the largest cryptocurrency exchanges by self-reported volume. The exchange lists over 2,000 tokens — significantly more than most competitors — and has marketed itself as a "listing-friendly" venue. However, this rapid growth in listed assets and claimed volume has attracted scrutiny from researchers and regulators alike.

MEXC's approach of aggressively listing new tokens, including many low-liquidity altcoins, creates conditions particularly conducive to wash trading. Low-liquidity markets are easier and cheaper to manipulate, and the sheer number of listed pairs makes comprehensive monitoring difficult.

## Metrics Used

### Average Transaction Size Analysis

The average transaction size metric provides insight into whether trading activity is driven by diverse market participants (retail traders, institutions, market makers) or by a narrow set of algorithmic actors.

On healthy exchanges, the average transaction size for a given pair exhibits natural volatility reflecting changing market conditions, news events, and varying participant types. The standard deviation of this metric is typically moderate to high.

Across multiple MEXC spot markets (including BTC/USDT, ETH/USDT, SOL/USDT, and numerous altcoin pairs), we observe:

- **Abnormally low standard deviation** in average transaction sizes over multi-week periods, indicating a dominant algorithmic actor generating the majority of volume.
- **Periodic step-function changes** in average transaction size, suggesting reconfiguration of trading bot parameters rather than organic shifts in trading behavior.
- **Correlation across unrelated pairs:** Average transaction size movements are correlated across pairs that should have no fundamental relationship (e.g., SOL/USDT and DOGE/USDT moving in lockstep), suggesting a shared volume generation system.

This pattern is notably absent on reference exchanges (Binance, Coinbase, Kraken) for the same trading pairs during the same time periods.

### Volume Distribution Tail Analysis

Healthy markets exhibit a [power law](https://en.wikipedia.org/wiki/Power_law) distribution of trade sizes — many small trades and progressively fewer large trades, producing a heavy tail. This is a well-established characteristic of genuine financial markets.

MEXC's volume distributions across multiple pairs show:

- **Truncated tails:** The distribution of trade sizes drops off sharply at specific thresholds rather than following a smooth power law decay.
- **Artificial clustering:** Trade sizes cluster at round numbers and specific increments (e.g., multiples of 0.01, 0.1, or 1.0), creating visible spikes in the distribution that are inconsistent with organic order flow.
- **Bimodal or multimodal distributions:** Some pairs exhibit multiple peaks in trade size distribution, suggesting multiple bots operating with different configurations rather than diverse human participants.
- **Low skewness values:** Compared to the same pairs on Binance or OKX, MEXC's trade size distributions show significantly lower skewness, indicating less natural variation.

### Time-of-Trade Distribution

The distribution of trades across time (by second, minute, and hour) reveals patterns about trading infrastructure and participant behavior. Human traders generate stochastic patterns, while bots produce detectable regularities.

MEXC's time-of-trade distributions show:

- **Sub-second periodicity:** Trade execution clusters at regular sub-second intervals (particularly at 100ms, 200ms, and 500ms boundaries), indicating automated systems generating the majority of executions.
- **Flat hourly distributions:** Unlike organic markets which show clear patterns tied to geographic trading sessions (Asian, European, American), several MEXC altcoin pairs show unnaturally flat 24-hour volume profiles, suggesting automated volume generation that runs continuously.
- **Minute-boundary spikes:** Disproportionate trade counts at the start of each minute, consistent with scheduled bot execution.

### Buy-Sell Ratio Analysis

In organic markets, the buy-sell ratio fluctuates with market sentiment, news events, and price movements. Wash trading often produces a buy-sell ratio persistently close to 1.0, since the same entity is both buying and selling.

Across examined MEXC pairs:

- **Persistently balanced buy-sell ratios** during periods when directional sentiment on other exchanges was strongly one-sided.
- **Rapid mean-reversion** of buy-sell imbalances, significantly faster than on reference exchanges, suggesting active balancing by an automated system.

## MX Token Analysis

MEXC's native exchange token (MX) warrants particular scrutiny. Exchange tokens are frequently subject to manipulation by the issuing exchange, which holds large supply and has direct control over market infrastructure.

MX/USDT trading on MEXC exhibits:

- **Abnormally high volume relative to market cap:** MX trading volume on MEXC frequently exceeds levels that would be expected given the token's market capitalization and holder base.
- **Correlated price support:** During broader market downturns, MX shows suspiciously strong price support with volume spikes that coincide with key support levels, suggesting active intervention.
- **Minimal organic presence on other venues:** MX trading on third-party exchanges shows dramatically lower volume, suggesting that the majority of MEXC-reported MX volume is not organic.

## Comparison With Reference Exchanges

To establish baselines, the same trading pairs were analyzed on Binance, Coinbase, and Kraken during identical time periods:

| Metric | MEXC | Binance | Coinbase |
|--------|------|---------|----------|
| Avg. trade size std. dev. | Low | Moderate | Moderate-High |
| Volume dist. power law fit | Poor | Good | Good |
| Time-of-trade periodicity | Strong | Weak | Minimal |
| Buy-sell ratio variance | Low | Moderate | Moderate |
| Hourly volume flatness | High (altcoins) | Low | Low |

The systematic divergence of MEXC's metrics from reference exchanges across multiple independent indicators strongly suggests artificial volume generation.

## Regulatory and Industry Context

MEXC's volume practices exist within a broader context of exchange transparency issues:

- **March 2023:** Estonia revoked MEXC's operating license, citing compliance failures.
- **2023-2024:** Japan's FSA issued warnings about MEXC operating without registration, as did regulators in Canada, the UK, and several other jurisdictions.
- **Industry studies:** Multiple independent analyses from organizations including the Blockchain Transparency Institute, Bitwise Asset Management research, and CryptoCompare's Exchange Benchmark have flagged exchanges with profiles similar to MEXC's for inflated volume.
- **Listing practices:** MEXC's model of listing tokens rapidly — often before other major exchanges — and charging listing fees creates financial incentives aligned with volume inflation, as higher reported volume attracts more listing applicants.

## Methodology Notes

This analysis applies the Digital New Institute's established market health framework, including:

- **Volume distribution analysis** comparing empirical distributions against power law models
- **Transaction size analysis** measuring statistical properties of trade sizes over rolling windows
- **Time-of-trade analysis** examining temporal distributions for algorithmic signatures
- **Buy-sell ratio analysis** measuring directional balance and mean-reversion speed
- **Cross-exchange comparison** using Binance, Coinbase, and Kraken as reference markets

Data was collected from public exchange APIs and third-party data aggregators for spot markets during Q3-Q4 2024.

## Conclusions

Multiple independent market health indicators converge on the same conclusion: a significant portion of MEXC's reported spot trading volume is artificial. The patterns observed are consistent with systematic wash trading operations rather than isolated anomalies.

Key findings:

1. **Volume generation algorithms** are active across multiple MEXC spot markets, identifiable through transaction size regularity, distribution shape anomalies, and temporal patterns.
2. **The exchange's native token (MX)** shows particularly strong indicators of exchange-driven price manipulation.
3. **Cross-pair correlation** of anomalies suggests centralized wash trading infrastructure rather than independent market makers.
4. **Comparison with reference exchanges** demonstrates that MEXC's metrics systematically diverge from organic market baselines.

These findings are consistent with [prior analyses of wash trading on other exchanges](/research/market-health/posts/2023-08-14-huobi/) and reinforce the importance of independent volume verification for cryptocurrency markets.

## References

- Blockchain Transparency Institute. "Exchange Rankings by Adjusted Volume." 2024.
- Bitwise Asset Management. "Analysis of Real Bitcoin Trade Volume." (Methodology applied to broader exchange set.)
- CryptoCompare. "Exchange Benchmark Report." Q3 2024.
- Digital New Institute. "[Market Health Metrics Documentation](/research/market-health/docs/market-health-metrics/)." 2024.
- CoinDesk. "[Crypto Exchange MEXC Loses Its License in Estonia](https://www.coindesk.com/policy/2023/03/14/crypto-exchange-mexc-loses-its-license-in-estonia/)." March 2023.
