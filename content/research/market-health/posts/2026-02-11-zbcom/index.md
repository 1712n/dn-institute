---
title: "ZB.com: Magic Trading Volume, DASH Market Manipulation, and Suspicious Shutdown"
date: 2026-02-11
entities:
  - ZB.com
  - DASH
  - BTC
---

## Summary

1. **391× volume inflation**: The Blockchain Transparency Institute (BTI) identified that ZB.com's reported volume was inflated by a factor of **391×** compared to estimates of genuine trading activity.
2. **DASH market manipulation**: Hacken's investigation revealed that ZB.com accounted for **80.5% of global DASH trading volume** — an impossibility for a single exchange absent systematic wash trading.
3. **Flagged by Sylvain Ribes**: Independent slippage analysis by Sylvain Ribes identified ZB.com among exchanges "so blatantly faking their volumes" that the fabrication was detectable through simple order book analysis.
4. **$4.8 million loss and shutdown**: In August 2022, approximately **$4.8 million** was drained from ZB.com's hot wallet in a suspected hack or exit scam, after which the exchange suspended operations.

## Background

ZB.com was originally founded as CHBTC in early 2013, making it one of the oldest cryptocurrency exchanges. Following China's cryptocurrency trading ban in September 2017, CHBTC ceased operations in mainland China and relaunched as ZB.com, shifting focus to international markets. The exchange relocated to Zurich, Switzerland, with additional offices in Hong Kong, Australia, and the United States.

Despite its long operational history, ZB.com was consistently flagged by independent analysts as one of the most egregious fabricators of trading volume in the cryptocurrency industry.

## Volume Fabrication Evidence

### Blockchain Transparency Institute (2018)

BTI's analysis of ZB.com revealed one of the most extreme volume inflation ratios among major exchanges [1]:

- ZB.com's reported volume was inflated by a factor of **391×** compared to genuine trading estimates
- This placed ZB.com among the worst offenders in BTI's comprehensive exchange survey
- For context: a 391× inflation means that for every $1 of genuine trading, ZB.com reported approximately $391 — indicating that over **99.7%** of reported volume was fabricated

### Hacken "Magic Trading Volume" Investigation

Hacken's research team published a detailed investigation titled "Magic Trading Volume: the Case of ZB.com" that uncovered specific patterns of market manipulation [2]:

- ZB.com was ranked **7th globally** on CoinMarketCap at the time of investigation
- The exchange accounted for **80.5% of all DASH trading volume worldwide**
- This concentration is economically implausible: no single exchange, regardless of size, should account for over 80% of a major cryptocurrency's global trading volume
- The DASH volume anomaly suggested either direct wash trading by the exchange or a market-making arrangement specifically designed to inflate DASH pair volumes
- Hacken concluded that ZB.com's trading volume metrics were unreliable and demonstrated unfair practices

### Sylvain Ribes Slippage Analysis (2018)

Independent researcher Sylvain Ribes conducted a methodical analysis of exchange volumes by measuring the price impact (slippage) of standardized sell orders across exchanges. His findings explicitly identified ZB.com among exchanges that were "so blatantly faking their volumes" that the fabrication was evident through basic order book analysis [3].

The methodology was straightforward: if an exchange claims billions in daily volume but a $50,000 sell order causes significant price movement, the reported liquidity does not exist. ZB.com's order books were inconsistent with its claimed volume levels.

### Bitwise Asset Management (March 2019)

Bitwise's SEC presentation identified only 10 exchanges with genuine, verifiable Bitcoin trading volume. ZB.com was not among them. The analysis estimated that **95% of reported Bitcoin volume** was fake across unregulated exchanges [4].

## The $4.8 Million Loss and Shutdown (August 2022)

In August 2022, ZB.com suffered a security incident that effectively ended its operations [5]:

- Approximately **$4.8 million** was drained from ZB.com's hot wallet
- The exchange immediately suspended all withdrawals
- ZB.com characterized the incident as a hack, but the circumstances — including the relatively small amount stolen and the permanent nature of the subsequent shutdown — raised questions about whether the event was an exit scam rather than an external attack
- The exchange never resumed operations, and user fund recovery remains unclear

The timing and circumstances mirror patterns observed at other exchanges (such as BitForex) where purported security incidents served as pretexts for permanent shutdowns, with user funds unrecoverable.

## Chainalysis Assessment

Chainalysis noted in its 2019 blog post on fake trade volume that since trading on exchanges largely happens off-chain, "the volumes they self-report are easily faked or subject to wash trading." ZB.com appeared on lists of exchanges suspected of fabricating volume, though Chainalysis also noted that some exchanges' trade volume ratios improved after 2018 [6].

## Regulatory Context

ZB.com's operational history illustrates the challenges of regulatory arbitrage in cryptocurrency:

- Originally operated as CHBTC under Chinese jurisdiction (2013–2017)
- Relocated to Switzerland after China's crypto trading ban
- Maintained offices in multiple jurisdictions without comprehensive regulatory oversight in any single jurisdiction
- The absence of mandatory audits, proof-of-reserves, or volume verification allowed ZB.com to operate with fabricated metrics for years before its shutdown

## Relevance to Market Health Metrics

ZB.com demonstrates several indicators documented in the DN Institute [Market Health Metrics](https://dn.institute/research/market-health/docs/market-health-metrics/) framework:

- **Single-pair volume dominance**: 80.5% of global DASH volume concentrated on one exchange
- **Volume inflation ratio**: 391× discrepancy between reported and estimated genuine volume
- **Slippage inconsistency**: Order book depth incompatible with claimed volume levels
- **Shutdown-preceded-by-drain pattern**: Security incident followed by permanent closure

## References

1. Blockchain Transparency Institute, "Exchange Volume Reports," 2018. [blockchaintransparency.org](https://www.blockchaintransparency.org/)
2. Hacken, "Magic Trading Volume: the Case of ZB.com." [hacken.io](https://hacken.io/discover/magic-trading-volume-the-case-of-zb-com/)
3. Sylvain Ribes, "Chasing Fake Volume: A Crypto-Plague," Medium, 2018. [medium.com](https://medium.com/@sylvainartplayribes/chasing-fake-volume-a-crypto-plague-ea1a3c1e0b5e)
4. Bitwise Asset Management, "Analysis of Real Bitcoin Trade Volume," Presentation to the U.S. Securities and Exchange Commission, March 2019. [sec.gov](https://www.sec.gov/comments/sr-nysearca-2019-01/srnysearca201901-5164833-183434.pdf)
5. CoinDesk, "ZB Exchange Loses Nearly $5M in Suspected Hack, Pauses Withdrawals," August 2022. [coindesk.com](https://www.coindesk.com/tech/2022/08/04/crypto-exchange-zb-exchange-loses-nearly-5m-in-suspected-hack-pauses-withdrawals)
6. Chainalysis, "Can On-chain Data Help Us Spot Fake Exchange Trading Volumes?" [chainalysis.com](https://www.chainalysis.com/blog/fake-trade-volume-cryptocurrency-exchanges/)
