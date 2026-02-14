---
title: "Wash Trading and Market Manipulation on Bitfinex"
date: 2023-04-18
entities:
  - Bitfinex
  - Tether
  - USDT
  - BTC
  - iFinex
---

## Summary

1. Statistical analysis of **real-time trade data** from the Bitfinex public API reveals significant deviations from expected market behavior, consistent with **artificial volume generation**.
2. **Benford's Law Analysis:** Bitfinex BTC/USD trade sizes show the largest first-digit distribution deviation among the three exchanges tested (KS = 0.1869, χ² = 5,146.20), far exceeding the critical threshold.
3. **Trade Size Distribution:** Bitfinex exhibits an anomalously low median trade size of **$3.13 USD** compared to Binance ($39.04) and OKX ($100.64), with an extreme mean-to-median ratio of **253:1**, suggesting volume inflation through numerous micro-trades.
4. **Buy/Sell Ratio:** Bitfinex shows a near-perfect **50.0%/50.0%** buy/sell split by trade count — unusually symmetrical compared to organic markets, consistent with self-trading patterns.
5. **Inter-Trade Timing:** Bitfinex median inter-trade interval of **12 milliseconds** is significantly shorter than Binance (90ms) and OKX (279ms), indicating high-frequency algorithmic activity.
6. **Regulatory Context:** Bitfinex (operated by iFinex Inc.) has been fined by both the NYAG ($18.5M settlement) and CFTC ($1.5M) for illegal activities, and shares corporate ownership with Tether, which was separately fined $41M for reserve misrepresentation.

## Metrics used

### Benford's Law — First-digit distribution analysis

[Benford's Law](https://en.wikipedia.org/wiki/Benford%27s_law) states that in naturally occurring datasets spanning multiple orders of magnitude, the leading digit 1 appears approximately 30.1% of the time, while 9 appears only 4.6%. This distribution is widely used in **forensic accounting** to detect fabricated data.

We applied Benford's Law analysis to the USD-denominated trade sizes (quantity × price) from three exchanges: **Bitfinex** (5,000 trades), **Binance** (1,165 trades), and **OKX** (1,500 trades), all collected via their public REST APIs for the BTC/USD(T) spot market.

{{< figure src="benford-comparison.png" caption="Benford's Law first-digit distribution comparison across Bitfinex, Binance, and OKX. Bitfinex shows the largest deviation from expected frequencies (KS = 0.1869). All data from public exchange APIs, February 2025." >}}

The Kolmogorov-Smirnov (KS) test results:

| Exchange | N (trades) | KS Statistic | Critical Value | χ² Statistic | Result |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Bitfinex** | 5,000 | 0.1869 | 0.0192 | 5,146.20 | **FAIL** |
| Binance | 1,165 | 0.1153 | 0.0398 | 438.26 | FAIL |
| OKX | 1,500 | 0.0842 | 0.0351 | 430.84 | FAIL |

While all three exchanges fail the strict Benford test (common in crypto markets due to algorithmic trading), **Bitfinex's deviation is 9.7× its critical value** — far exceeding both Binance (2.9×) and OKX (2.4×). The chi-square statistic of 5,146.20 is an order of magnitude higher than the benchmark exchanges, indicating the most extreme departure from natural trade size distributions.

{{< figure src="benford-cdf.png" caption="Cumulative distribution function (CDF) of first-digit frequencies. The shaded area between Bitfinex and the Benford expected line represents the maximum deviation. Bitfinex diverges most from the theoretical distribution, particularly in the lower digits." >}}

### Trade size distribution — Detecting volume-generating bots

Genuine trading activity typically follows a [power-law distribution](https://en.wikipedia.org/wiki/Power_law) where small trades are common and large trades are rare, but with a meaningful presence of medium-sized retail orders. Wash trading operations often generate high volumes of micro-trades to inflate reported volume.

{{< figure src="volume-distribution.png" caption="Trade size distribution (USD) across exchanges on log-scale. Bitfinex shows extreme concentration in micro-trades with median $3.13 vs Binance $39.04 and OKX $100.64. Data from public APIs, February 2025." >}}

Key observations from the trade size analysis:

| Metric | Bitfinex | Binance | OKX |
|:---|:---:|:---:|:---:|
| Mean trade size (USD) | $791.53 | $435.86 | $1,177.83 |
| Median trade size (USD) | **$3.13** | $39.04 | $100.64 |
| Standard deviation | $2,944.63 | $2,093.67 | $3,048.04 |
| Skewness | 6.61 | 13.10 | 4.96 |
| Mean/Median ratio | **253:1** | 11:1 | 12:1 |

The **mean-to-median ratio** is particularly telling. A ratio of 253:1 on Bitfinex indicates that the distribution is dominated by an enormous number of very small trades (pulling the median down to $3.13), while a minority of large trades inflate the mean. This pattern is consistent with **order-printing bots** generating high trade counts with minimal capital.

On Binance and OKX, the mean-to-median ratios of 11:1 and 12:1 are within normal ranges for crypto markets, reflecting a more balanced mix of retail and institutional order flow.

### Buy/sell ratio — Detecting self-trading patterns

In organic markets, the buy/sell ratio fluctuates with market sentiment. In wash-traded markets, a single entity trading with itself produces a **near-perfect 50/50 split**, as every "buy" has a corresponding "sell" from the same actor.

{{< figure src="buy-sell-ratio.png" caption="Buy/sell ratio comparison by trade count and by volume. Bitfinex shows an unusually perfect 50.0%/50.0% split by count. Data from taker-side classification via public APIs." >}}

| Exchange | Buy Count | Sell Count | Buy Volume | Sell Volume |
|:---|:---:|:---:|:---:|:---:|
| **Bitfinex** | **50.0%** | **50.0%** | 51.9% | 48.1% |
| Binance | 50.4% | 49.6% | 48.2% | 51.8% |
| OKX | 66.3% | 33.7% | 47.0% | 53.0% |

Bitfinex's **exact 50.0%/50.0%** buy/sell split by trade count is statistically unusual. While Binance also shows near-balance (50.4/49.6), OKX demonstrates clear directional bias (66.3/33.7) that is typical of organic market conditions where sentiment drives imbalanced order flow.

The volume-weighted ratios tell a slightly different story — Bitfinex's volume split (51.9/48.1) shows mild deviation, suggesting that while the *number* of trades is perfectly balanced (consistent with self-trading), the *sizes* of individual trades vary slightly.

### Inter-trade timing — High-frequency activity analysis

The timing between consecutive trades reveals information about market microstructure. Organic retail activity produces variable inter-trade intervals, while automated wash trading systems execute trades at mechanically regular or extremely rapid intervals.

{{< figure src="trade-timing.png" caption="Inter-trade time interval distribution across exchanges. Bitfinex shows a median interval of just 12ms — approximately 83 trades per second — significantly faster than both benchmark exchanges." >}}

| Metric | Bitfinex | Binance | OKX |
|:---|:---:|:---:|:---:|
| Mean interval | 0.644s | 0.145s | 0.516s |
| Median interval | **0.012s** | 0.090s | 0.279s |
| Trades per second (median) | **~83** | ~11 | ~3.6 |

Bitfinex's median inter-trade interval of **12 milliseconds** (approximately 83 trades per second) is 7.5× faster than Binance and 23× faster than OKX. This extreme trading velocity, combined with the low median trade size of $3.13, suggests that a significant portion of Bitfinex's trade flow originates from **high-frequency volume-generating algorithms** rather than organic market participants.

### Round-number clustering — Retail user presence

Retail traders tend to place orders at round quantities (0.01 BTC, 0.1 BTC, 1 BTC). The presence or absence of clustering at these round numbers serves as a proxy for genuine retail participation.

{{< figure src="round-number-clustering.png" caption="Round-number trade size clustering analysis. Higher clustering at round BTC amounts indicates more retail participation. Data from public exchange APIs." >}}

The clustering analysis examines what percentage of trades occur at exact round BTC quantities at different precision levels. Differences in rounding patterns across exchanges reflect the composition of their user base — exchanges with more genuine retail flow show higher clustering at standard round numbers.

## Regulatory background

### NYAG Settlement (2021)

The New York Attorney General found that Bitfinex and Tether (both under iFinex Inc.) covered up an **$850 million loss** of commingled client and corporate funds through a $900 million credit facility from Tether reserves. The settlement required:

- **$18.5 million** in penalties
- Ban from operating in New York State
- Quarterly transparency reports from Tether

### CFTC Enforcement (2021)

The CFTC fined **Tether $41 million** for misrepresenting USDT reserves (finding sufficient reserves existed for only 27.6% of days sampled) and **Bitfinex $1.5 million** for facilitating illegal off-exchange retail commodity transactions.

### Academic evidence

Griffin & Shams (2020), published in the *Journal of Finance*, found statistical evidence that **Tether issuance was used to manipulate Bitcoin prices**, with a single large Bitfinex account driving disproportionate buying pressure using newly minted USDT.

## Conclusion

The convergence of multiple statistical indicators — extreme Benford's Law deviations, anomalous trade size distributions, perfect buy/sell symmetry, and high-frequency micro-trading — provides evidence consistent with **artificial volume generation** on Bitfinex's BTC/USD market.

While algorithmic trading is present across all cryptocurrency exchanges (as reflected in Benford deviations across all three platforms tested), Bitfinex consistently exhibits the **most extreme values** across every metric examined:

- **Highest** Benford deviation (KS 9.7× critical vs 2.4-2.9× for benchmarks)
- **Lowest** median trade size ($3.13 vs $39-$101 for benchmarks)
- **Most extreme** mean-to-median ratio (253:1 vs 11-12:1 for benchmarks)
- **Fastest** median trade frequency (83/sec vs 3.6-11/sec for benchmarks)
- **Most symmetrical** buy/sell ratio (exact 50.0/50.0)

These findings, combined with Bitfinex's documented regulatory history including over **$61 million in combined penalties** from the NYAG and CFTC, suggest that market integrity concerns on the platform warrant continued scrutiny.

## Data sources

All trade data was collected from public exchange REST APIs on February 14, 2025:

- **Bitfinex:** `api-pub.bitfinex.com/v2/trades/tBTCUSD/hist` — 5,000 trades
- **Binance:** `api.binance.com/api/v3/aggTrades?symbol=BTCUSDT` — 1,165 trades
- **OKX:** `okx.com/api/v5/market/trades?instId=BTC-USDT` — 1,500 trades

## References

1. New York Attorney General. (2021). *Attorney General James Ends Virtual Currency Trading Platform Bitfinex's Illegal Activities in New York*. [Press Release](https://ag.ny.gov/press-release/2021/attorney-general-james-ends-virtual-currency-trading-platform-bitfinexs-illegal)
2. CFTC. (2021). *CFTC Orders Tether and Bitfinex to Pay Fines Totaling Over $42.5 Million*. [Press Release](https://www.cftc.gov/PressRoom/PressReleases/8450-21)
3. Griffin, J. M., & Shams, A. (2020). Is Bitcoin Really Untethered? *The Journal of Finance*, 75(4), 1913–1964. [DOI: 10.1111/jofi.12903](https://doi.org/10.1111/jofi.12903)
4. Bitwise Asset Management. (2019). *Presentation to the U.S. SEC*. [Filing](https://www.sec.gov/comments/sr-nysearca-2019-01/srnysearca201901-5164833-183434.pdf)
5. Benford, F. (1938). The Law of Anomalous Numbers. *Proceedings of the American Philosophical Society*, 78(4), 551–572.
