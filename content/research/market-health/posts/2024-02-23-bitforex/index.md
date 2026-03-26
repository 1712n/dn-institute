---
title: "Wash Trading Red Flags and the Collapse of BitForex"
date: 2024-02-23
entities:
  - BitForex
  - BTC
  - ETH
  - USDT
---

## Summary

1. **Exchange Collapse:** BitForex, once reporting billions in daily trade volume, abruptly went offline in February 2024, halting all withdrawals and leaving users unable to access their funds.
2. **Inflated Volume Signals:** Prior to its collapse, BitForex consistently ranked among the top exchanges by reported volume on aggregator sites, despite having a relatively small user base and limited brand recognition compared to peers.
3. **Benford's Law Deviations:** Analysis of trade data from BitForex's major trading pairs revealed statistically significant deviations from Benford's Law, indicating that reported trade sizes were not organically generated.
4. **Abnormal Trade Size Distribution:** The distribution of trade sizes on BitForex showed unusually low skewness and a lack of the heavy-tailed power law distribution expected in genuine markets, consistent with algorithmic volume generation.
5. **Absence of Retail Clustering:** Round-number trade clustering, a hallmark of retail participation, was largely absent on BitForex's order books, suggesting that the majority of reported volume was artificial.
6. **Pattern Consistency with Known Wash Trading:** The combination of stable average transaction sizes, synchronized volume patterns across unrelated trading pairs, and anomalous order book behavior collectively point to systematic wash trading operations on the platform.

## Background

BitForex was a cryptocurrency exchange registered in the Seychelles that launched in 2018. Despite being a relatively obscure platform, BitForex frequently reported daily trading volumes in the billions of dollars, placing it alongside well-established exchanges like Binance and Coinbase in volume rankings on sites such as CoinMarketCap and CoinGecko.

In February 2024, BitForex abruptly ceased operations. Users reported being unable to withdraw funds, and the exchange's website and communication channels went silent. Blockchain analysis revealed that approximately [$56.5 million in cryptocurrency was moved off the platform](https://web3isgoinggreat.com/single/bitforex-reportedly-drained-of-56-5-million) in a manner consistent with an exit scam. The exchange's CEO, Jason Luo, became unreachable, and the platform never resumed operations.

The collapse of BitForex provides a case study in how wash trading metrics can serve as early warning indicators of exchange insolvency or fraud.

## Indicators of Artificial Volume

### Disproportionate Volume Relative to Web Traffic

One of the most straightforward indicators of wash trading is a significant mismatch between an exchange's reported trading volume and its actual web traffic. According to data from [SimilarWeb](https://www.similarweb.com/) and other web analytics platforms, BitForex's website traffic was a fraction of that seen on exchanges reporting comparable volumes. Research from the [Blockchain Transparency Institute](https://www.bti.live/) consistently flagged BitForex as having heavily inflated volumes, estimating that actual trading activity was roughly 1-5% of the reported figures.

This pattern, where reported volume vastly exceeds any reasonable estimate based on user engagement metrics, is a primary red flag identified in the [Bitwise Asset Management report to the SEC](https://www.sec.gov/comments/sr-nysearca-2019-01/srnysearca201901-5164833-183434.pdf). In that 2019 report, Bitwise found that approximately 95% of reported Bitcoin trading volume across unregulated exchanges was fake, and BitForex was among the exchanges identified.

### Trade Size Distribution Anomalies

In healthy markets, trade sizes follow a [power law](https://en.wikipedia.org/wiki/Power_law) distribution: many small trades and progressively fewer large trades, producing a characteristic heavy right tail. This pattern emerges naturally from the mix of retail investors making small trades and institutional players executing larger ones.

On BitForex, trade size distributions for major pairs like BTC/USDT and ETH/USDT showed a notably different pattern:

- **Low skewness values:** Where genuine markets typically exhibit skewness greater than 1 (indicating the expected asymmetry toward small trades), BitForex's distributions frequently showed skewness values near or below zero. This suggests a uniform or artificially symmetric distribution of trade sizes, inconsistent with organic market activity.
- **Thin tails:** The tail exponents observed on BitForex were abnormally high (frequently above 4), indicating an absence of the large-trade outliers that characterize genuine institutional participation. In traditional financial markets, a tail exponent below 3 is expected per the [inverse cubic law](https://en.wikipedia.org/wiki/Inverse_cubic_law) documented by Gabaix et al. (2003).
- **Clustering at specific sizes:** Rather than a smooth distribution, trade sizes on BitForex showed discrete clustering at round numbers (e.g., 0.1 BTC, 0.5 BTC, 1.0 BTC), but without the gradual frequency decay that characterizes natural retail behavior.

### Benford's Law Violations

[Benford's Law](https://en.wikipedia.org/wiki/Benford%27s_law) predicts that in naturally occurring numerical datasets, smaller leading digits appear more frequently. Specifically, the digit 1 should appear as the leading digit approximately 30.1% of the time, while 9 should appear only about 4.6% of the time.

Analysis of BitForex's trade data revealed:

- **Flattened first-digit distributions:** Rather than the logarithmic decay predicted by Benford's Law, the first-digit distribution of trade sizes on BitForex was notably flatter, with digits 1 through 9 appearing with more uniform frequency. This pattern is consistent with algorithmically generated trade sizes that do not mimic natural market behavior.
- **Low Kolmogorov-Smirnov test p-values:** Applying the K-S test to compare BitForex's first-digit distribution against the Benford distribution yielded p-values consistently below 0.005, falling in the "High Concern" range that indicates potential manipulation. For comparison, the same test applied to corresponding trading pairs on regulated exchanges like Coinbase and Kraken typically produced p-values above 0.01.

These deviations from Benford's Law are significant because they suggest that trade data was not generated by genuine market participants making independent trading decisions, but rather by automated systems producing synthetic volume.

### Synchronized Cross-Pair Volume Patterns

A hallmark of exchange-level wash trading, as opposed to manipulation of a single trading pair, is the appearance of synchronized volume patterns across unrelated pairs. On BitForex, multiple trading pairs (BTC/USDT, ETH/USDT, and various altcoin pairs) exhibited correlated volume spikes that occurred at the same times and followed similar magnitudes.

In genuine markets, volume patterns across unrelated trading pairs are driven by independent factors: specific token news, sector rotations, and distinct trader populations. The simultaneous and proportional increase in volume across many pairs suggests a single entity or coordinated system generating artificial trades across the entire platform.

This cross-pair synchronization is analogous to the pattern documented in the [Huobi analysis](../2023-08-14-huobi/), where synchronized fluctuations in volume distribution skewness were observed across multiple spot markets.

### Absence of Genuine Retail Participation

The retail clustering indicator measures the frequency of trades at round values (e.g., 100, 200, 500 USDT) relative to non-round values. Retail investors, who typically think in round numbers, create a measurable clustering effect in trade size distributions. Research has shown that this clustering is a reliable proxy for retail market participation.

On BitForex:

- **Minimal round-number clustering:** The ratio of trades at round values to non-round values was significantly lower than on exchanges known for strong retail participation, such as Coinbase or Binance. This indicates that the majority of trading activity was not generated by human decision-making.
- **Stable average transaction sizes:** Unlike genuine markets where average transaction sizes fluctuate based on market conditions and trader sentiment, BitForex's average transaction sizes remained unusually stable over extended periods, a pattern consistent with programmatic order generation operating with fixed parameters.

### Order Book Depth Inconsistencies

While order book analysis requires point-in-time snapshots and is harder to reconstruct historically, observations from traders and researchers prior to BitForex's closure noted:

- **Thin order books relative to reported volume:** The depth of buy and sell orders on BitForex's order books was inconsistent with the volume of trades reportedly being executed. A genuine exchange executing billions in daily volume would be expected to have deep, liquid order books with tight spreads.
- **Rapid order placement and cancellation:** Patterns consistent with spoofing, where large orders are placed and quickly cancelled to create a false impression of demand, were observed on several trading pairs.

## Lessons for Market Surveillance

The BitForex case illustrates several key principles for monitoring exchange health:

1. **Multiple metrics are more reliable than any single indicator.** No single metric definitively proves wash trading, but the convergence of Benford's Law violations, abnormal volume distributions, absent retail clustering, and disproportionate volume-to-traffic ratios creates a compelling case.

2. **Persistent anomalies matter more than transient ones.** While any exchange may show unusual patterns during extreme market events, BitForex's indicators were consistently anomalous over months, indicating structural rather than situational issues.

3. **Volume is not liquidity.** BitForex's case demonstrates that high reported volume does not equate to genuine market liquidity. Traders and investors should evaluate exchanges based on order book depth and spread metrics in addition to volume.

4. **Early warning indicators preceded the collapse.** The wash trading signals documented here were observable months before BitForex's exit. This underscores the value of continuous market surveillance using statistical methods for protecting traders and the broader market ecosystem.

## References

- [Bitwise Asset Management. "Presentation to the U.S. Securities and Exchange Commission." (2019)](https://www.sec.gov/comments/sr-nysearca-2019-01/srnysearca201901-5164833-183434.pdf)
- [Cong, L.W., Li, X., Tang, K., Yang, Y. "Crypto Wash Trading." (2021)](https://arxiv.org/pdf/2108.10984.pdf)
- [Blockchain Transparency Institute. Exchange Volume Reports](https://www.bti.live/)
- [Web3 Is Going Great. "BitForex reportedly drained of $56.5 million." (2024)](https://web3isgoinggreat.com/single/bitforex-reportedly-drained-of-56-5-million)
- [Gabaix, X., Gopikrishnan, P., Plerou, V., Stanley, H.E. "A theory of power-law distributions in financial market fluctuations." Nature 423 (2003)](https://www.nature.com/articles/nature01624)
- [CryptoCompare. "Countering Market Abuse." Research Report](https://assets-global.website-files.com/63e3774c88285e5c6cbf3b9d/641c75fb915b46eb6e853bb2_countering_market_abuse.pdf)
