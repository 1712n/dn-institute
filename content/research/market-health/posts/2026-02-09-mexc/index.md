---
title: "Anomalous Volume Patterns on MEXC: Evidence of Systematic Market Manipulation"
date: 2026-02-09
description: "Statistical analysis reveals anomalous volume distribution, artificially tight spreads, and inflated per-pair volumes on MEXC Global compared to Binance, Coinbase, and Kraken."
entities:
  - MEXC
  - Binance
  - Coinbase
  - Kraken
---

## Summary

1. MEXC Global reports approximately **$2.47 billion** in daily trading volume across its top 400 pairs, comparable to Coinbase ($2.03B), despite serving a smaller organic user base.
2. **Volume Concentration Anomaly:** On legitimate exchanges, volume follows a steep power-law concentration where a small number of pairs dominate total volume. MEXC exhibits a significantly flatter distribution, suggesting systematic volume inflation across many trading pairs rather than organic concentration in popular markets.
3. **Inflated Per-Pair Volume:** MEXC's median 24-hour volume per pair ($650,022) is approximately **4x higher than Coinbase** ($165,414) and **5x higher than Kraken** ($131,681), despite MEXC's smaller market share — an anomaly consistent with artificial volume generation.
4. **Spread Anomaly:** MEXC displays a median bid-ask spread of 0.10%, tighter than Coinbase (0.19%) and Kraken (0.14%), despite handling far less organic order flow. Artificially tight spreads on low-liquidity pairs are a known indicator of market-making bots designed to simulate liquidity.
5. **Benford's Law Test:** First-digit analysis of 24-hour trading volumes across 400 pairs yields a chi-squared statistic of 42.2 for MEXC, indicating significant deviation from the expected [Benford's Law](https://en.wikipedia.org/wiki/Benford%27s_law) distribution.

## Methodology

Data was collected from [CoinGecko](https://www.coingecko.com/) exchange ticker endpoints in February 2026. For each of four exchanges — MEXC, Binance, Coinbase, and Kraken — the top 400 trading pairs by reported volume were analyzed. Metrics include 24-hour converted USD volume, bid-ask spread percentage, and CoinGecko trust scores. Cross-exchange comparison was performed on 229 trading pairs listed on both MEXC and Binance.

## Volume concentration analysis

In organic markets, trading volume follows a [power-law](https://en.wikipedia.org/wiki/Power_law) distribution: a small number of popular pairs (BTC/USDT, ETH/USDT) generate the vast majority of volume, while the long tail of smaller pairs contributes minimally. This pattern emerges naturally from retail and institutional trader preferences.

{{< figure src="volume-concentration-comparison.png" alt="Cumulative volume distribution across exchanges" caption="Cumulative volume distribution across four exchanges, February 2026. MEXC (red) shows a significantly flatter curve than Coinbase, Kraken, and Binance, indicating volume is anomalously distributed across many pairs." loading="lazy" >}}

On Coinbase, the top 10% of trading pairs account for approximately 93% of total volume. On Kraken, this figure is roughly 96%. MEXC's curve rises much more gradually: the top 10% of pairs contribute only about 83% of volume, with meaningful volume persisting deep into lower-ranked markets. This pattern is consistent with systematic volume generation across many trading pairs, a hallmark of [wash trading](https://en.wikipedia.org/wiki/Wash_trade) where bots execute self-trades to inflate reported metrics.

## Per-pair volume anomaly

{{< figure src="volume-per-pair-comparison.png" alt="Volume per pair box plot comparison" caption="24-hour trading volume distribution per pair across four exchanges, February 2026. MEXC's median volume per pair significantly exceeds Coinbase and Kraken despite comparable total exchange volume." loading="lazy" >}}

MEXC's median volume per trading pair ($650,022) is 3.9x higher than Coinbase ($165,414) and 4.9x higher than Kraken ($131,681). While Binance's higher median ($2.15M) reflects its genuine market dominance with substantially higher total volume ($9.49B), MEXC achieves a disproportionately high per-pair median relative to its overall market position.

This is particularly notable because MEXC lists over 2,000 trading pairs — far more than Coinbase (~700) or Kraken (~800). An exchange with more listed pairs would normally show a lower median per-pair volume due to the dilution effect of many low-liquidity markets. The opposite pattern on MEXC suggests volume is being artificially maintained across a broad range of markets.

## Bid-ask spread analysis

{{< figure src="spread-distribution-comparison.png" alt="Bid-ask spread distribution histograms" caption="Bid-ask spread distribution across four exchanges, February 2026. MEXC shows an unusually concentrated distribution with a tight 0.10% median spread." loading="lazy" >}}

Bid-ask spreads reflect genuine liquidity: tighter spreads indicate more active buyers and sellers willing to transact at competitive prices. On major exchanges, only the most liquid pairs (BTC/USDT, ETH/USDT) achieve consistently tight spreads, while smaller pairs exhibit wider spreads due to limited organic market depth.

MEXC's median spread (0.10%) is tighter than Coinbase (0.19%) and Kraken (0.14%), and nearly matches Binance (0.08%) despite processing substantially less organic volume. The concentration of MEXC's spread distribution around very low values — even for smaller trading pairs — suggests the presence of market-making bots that maintain artificial bid-ask tightness regardless of genuine liquidity conditions.

## Benford's Law first-digit test

[Benford's Law](https://en.wikipedia.org/wiki/Benford%27s_law) predicts that in naturally occurring numerical datasets, the leading digit follows a logarithmic distribution: approximately 30.1% of values begin with 1, 17.6% with 2, decreasing to 4.6% for digit 9. Deviations from this distribution in financial data can indicate manipulation, as artificial volume generation may not preserve the natural digit distribution.

{{< figure src="benfords-volume-comparison.png" alt="Benford's Law first digit test comparison" caption="Benford's Law first-digit test applied to 24-hour trading volumes across four exchanges (n=400 each), February 2026." loading="lazy" >}}

The chi-squared goodness-of-fit test yields the following results (critical value at p=0.05 with 8 degrees of freedom: 15.51):

| Exchange | χ² Statistic | Deviation from Benford's Law |
|----------|-------------|------------------------------|
| Kraken   | 10.3        | Not significant              |
| Coinbase | 24.2        | Significant                  |
| MEXC     | 42.2        | Highly significant           |
| Binance  | 67.3        | Highly significant           |

All four exchanges show some deviation from Benford's Law when analyzing only the top 400 pairs by volume. This is partially expected due to [selection bias](https://en.wikipedia.org/wiki/Selection_bias): filtering for the highest-volume pairs truncates the natural distribution. However, the magnitude of deviation varies substantially. Kraken's distribution aligns most closely with theoretical expectations, while MEXC shows significant deviation that, combined with the other volume anomalies, suggests artificial volume patterns.

Binance's high chi-squared value (67.3) is likely attributable to its extreme market dominance in a few key pairs (BTC/USDT alone exceeds $2B daily), which skews the first-digit distribution heavily toward 1 and 2. This is a different mechanism than the broad-based volume inflation observed on MEXC.

## Cross-exchange comparison for identical pairs

{{< figure src="volume-ratio-distribution.png" alt="MEXC to Binance volume ratio distribution" caption="Distribution of MEXC/Binance volume ratios for 229 trading pairs listed on both exchanges, February 2026. The median ratio of 0.285 indicates MEXC reports roughly 28.5% of Binance's volume for the same pairs." loading="lazy" >}}

Analysis of 229 trading pairs available on both MEXC and Binance reveals a median MEXC/Binance volume ratio of 0.285. Only 6 pairs (2.6%) show higher volume on MEXC than Binance. While this ratio alone does not indicate manipulation — Binance is the larger exchange — the distribution shape is informative. A narrow, concentrated distribution of ratios would suggest a consistent relationship between the two exchanges. The observed wide spread (from 0.002x to 3.5x) suggests that MEXC's volume figures for individual pairs do not maintain a consistent proportional relationship with Binance, which may reflect differential artificial volume inflation across markets.

## References

- Cong, L.W., Li, X., Tang, K., & Yang, Y. (2021). [Crypto Wash Trading](https://arxiv.org/pdf/2108.10984.pdf). arXiv:2108.10984
- Bitwise Asset Management (2019). [Analysis of Real and Fake Volume in the Cryptocurrency Ecosystem](https://www.sec.gov/comments/sr-nysearca-2019-01/srnysearca201901-5164833-183434.pdf). SEC Comment Letter
- CoinGecko (2024). [Trust Score and Methodology](https://www.coingecko.com/en/methodology)
