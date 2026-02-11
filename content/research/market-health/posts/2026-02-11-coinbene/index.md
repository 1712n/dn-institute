---
title: "CoinBene: 99% Fabricated Volume and the Anatomy of a CoinMarketCap Rankings Fraud"
date: 2026-02-11
entities:
  - CoinBene
  - BTC
---

## Summary

1. **99% fabricated volume**: The Blockchain Transparency Institute (BTI) identified that **99% of CoinBene's reported trading volume was fake**, estimating genuine volume at approximately **$2.73 million** — enough to disqualify it from the top 100 exchanges.
2. **Bitwise SEC evidence**: In Bitwise Asset Management's March 2019 presentation to the SEC, CoinBene was highlighted as a primary example of volume fabrication, reporting **$480 million daily volume** while Coinbase Pro (with verifiable genuine volume) reported only **$27 million**, yet CoinBene's bid-ask spread was **3,400× larger** than Coinbase's.
3. **Mechanical trade patterns**: Analysis revealed an "implausibly perfect alternating pattern of green and red trades" on CoinBene, with buy and sell orders appearing in timestamped pairs — a signature of automated self-trading.
4. **Transaction mining model**: CoinBene operated a "transaction mining" model that directly incentivized wash trading by returning trading fees as exchange tokens, creating a structural driver for artificial volume.

## Background

CoinBene was founded in 2017 and registered in Singapore. It rapidly ascended CoinMarketCap's rankings, briefly claiming the **#1 position by reported trading volume** in early 2019. This achievement was not the result of organic growth but rather systematic volume fabrication that exploited weaknesses in how aggregator platforms measured exchange activity.

## Volume Fabrication Evidence

### Blockchain Transparency Institute (December 2018)

BTI's December 2018 report provided the most granular assessment of CoinBene's actual trading activity [1]. Their findings were severe:

- CoinBene topped BTI's monitored exchanges with an alleged **$222.8 million** in 24-hour trading volume
- After analysis, BTI concluded that **99% of this volume was fabricated**
- Estimated genuine daily volume was approximately **$2.73 million**
- At this real volume level, CoinBene would not qualify for CoinMarketCap's top-100 exchange rankings

BTI's methodology monitored the top 25 trading pairs of the top 25 exchanges by reported volume and found that across these exchanges, **87% of all reported trading volume was fake**, with CoinBene representing an extreme outlier even among manipulative peers.

### Bitwise Asset Management SEC Presentation (March 2019)

Bitwise's presentation to the SEC in connection with their Bitcoin ETF application provided detailed forensic evidence of CoinBene's volume fabrication [2]. The analysis exposed multiple anomalies:

**Volume-spread divergence:**
- CoinBene reported **$480 million** in daily BTC volume
- Coinbase Pro reported **$27 million** in daily BTC volume
- Despite claiming 18× more volume, CoinBene's bid-ask spread was **$34.74** compared to **$0.01** on Coinbase Pro
- A spread 3,400× larger on an exchange claiming 18× more volume is a mathematical impossibility under organic market conditions

**Trade pattern anomalies:**
- CoinBene displayed an "implausibly perfect alternating pattern of green and red trades"
- Buy and sell orders appeared in **timestamped pairs**, with one order offsetting the other
- No round-number trades or small-value trades were observed — patterns that would be present in any market with genuine retail participation
- The trade size histogram showed mechanical uniformity inconsistent with diverse market participants

Bitwise concluded that CoinBene was among the most egregious examples of fake volume, and that only **10 out of 81 analyzed exchanges** reported genuine trading activity. CoinBene was explicitly not among the legitimate 10.

### The Tie Research (March 2019)

When CoinBene briefly overtook Binance on CoinMarketCap's adjusted volume rankings in March 2019, The Tie published research questioning the result [3]:

- The research suggested that **most of CoinBene's volume was fake**
- CoinBene and Bit-Z simultaneously climbed to top positions on CoinMarketCap despite no corresponding increase in market interest, web traffic, or user base
- The anomaly was short-lived; after CoinMarketCap adjusted its methodology, CoinBene dropped precipitously in the rankings

## Transaction Mining: Structural Incentives for Wash Trading

CoinBene operated a "transaction mining" model — a mechanism prevalent among several exchanges in 2018–2019 that created direct financial incentives for self-trading [4]:

- Users received exchange tokens (CONI) proportional to their trading fees paid
- The value of these tokens often exceeded the fees paid, creating a net-positive return on wash trading
- This mechanism transformed trading from a cost into a revenue source, eliminating the primary economic deterrent against self-trading
- The result was a self-reinforcing cycle: wash trading generated tokens, tokens had market value, and the apparent volume attracted more listings and users

The transaction mining model was not unique to CoinBene — exchanges including FCoin, BitMax, and others adopted similar models — but CoinBene's implementation was among the most aggressive in terms of the volume inflation it produced.

## Market Impact and CoinMarketCap Gaming

CoinBene's volume fabrication exposed fundamental vulnerabilities in cryptocurrency market data infrastructure:

- **Ranking manipulation**: By fabricating volume, CoinBene achieved top-10 and briefly #1 rankings on CoinMarketCap
- **Listing fee revenue**: High rankings attracted token projects willing to pay substantial listing fees for placement on a "top exchange"
- **Retail user acquisition**: Retail traders used CoinMarketCap rankings as a proxy for exchange legitimacy, directing deposits to CoinBene based on fabricated metrics
- **ETF implications**: The prevalence of fake volume, with CoinBene as a leading example, was cited by the SEC as a reason for rejecting Bitcoin ETF applications in 2019

Bitwise explicitly noted that exchanges like CoinBene were "artificially inflating their trading volumes to attract listings for which they could charge high listing fees" — identifying the business model driving the manipulation.

## Relevance to Market Health Metrics

CoinBene's case provides textbook examples of several [Market Health Metrics](https://dn.institute/research/market-health/docs/market-health-metrics/) indicators:

| Metric | Expected (healthy) | CoinBene observed |
|--------|-------------------|-------------------|
| Bid-ask spread vs. volume | Narrow spread with high volume | $34.74 spread with $480M volume |
| Trade pattern distribution | Random, reflecting diverse participants | Perfect alternating buy/sell pairs |
| Trade size histogram | Power law distribution | Mechanical uniformity |
| Real-to-reported volume ratio | >80% | ~1% (BTI estimate) |
| Round-number trade frequency | Present (retail participation) | Absent |

The 3,400× spread-to-volume divergence is perhaps the single most compelling quantitative indicator — it requires no sophisticated analysis to understand that an exchange cannot simultaneously be the world's most active BTC market and have the widest spread.

## References

1. Blockchain Transparency Institute, "December 2018 Exchange Volume Report," December 2018. [blockchaintransparency.org](https://www.blockchaintransparency.org/)
2. Bitwise Asset Management, "Analysis of Real Bitcoin Trade Volume," Presentation to the U.S. Securities and Exchange Commission, March 2019. [sec.gov](https://www.sec.gov/comments/sr-nysearca-2019-01/srnysearca201901-5164833-183434.pdf)
3. Cointelegraph, "Two Exchanges Overtake Binance on CMC Rankings, But Research Suggests Volume Is Fake," March 2019. [cointelegraph.com](https://cointelegraph.com/news/two-exchanges-overtake-binance-on-cmc-rankings-but-research-suggests-volume-is-fake)
4. Bitcoinist, "Over $6 Billion in Daily Trading Volume Faked Across Top 100 Exchanges." [bitcoinist.com](https://bitcoinist.com/6-billion-volume-faked-coinmarketcap/)
