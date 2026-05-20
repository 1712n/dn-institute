---
title: "HTX trade-size clustering: exploratory market-health snapshot"
date: 2026-05-20
description: "A reproducible public-trade snapshot finds repeated exact-size lots on HTX, especially around TRX/USDT. The pattern is useful as a market-surveillance screen, but exchange minimums, short windows, and missing account/order-book data prevent stronger wash-trading conclusions."
entities:
  - HTX
  - OKX
  - TRX
  - BTC
  - ETH
  - DOGE
  - SOL
  - XRP
---

## Summary

1. A public-trade snapshot covering **17,436 trades** from 2026-05-19T13:21:39Z to 2026-05-20T00:54:20Z shows repeated exact trade sizes on HTX across six USDT markets.
2. The repeated sizes are economically small. The most common HTX lot in each sampled market is worth roughly **$1.23 to $3.00**, close to the exchange's published minimum-order and minimum-notional rules. That makes the signal a market-health screen, not a standalone wash-trading finding.
3. After downsampling HTX to the same **500-trade** size as the OKX reference endpoint, HTX TRX/USDT still stands out: the modal-size share is **12.4%** with a 95% bootstrap interval of **10.4%-15.0%**, versus **2.6%** in the OKX TRX-USDT sample.
4. The TRX/USDT clustering is concentrated in neighboring exact sizes. The four most repeated HTX TRX sizes (`8.41`, `8.42`, `8.43`, `8.44`) account for **38.1%** of all captured HTX TRX/USDT trades.
5. Benford-distance and second-of-minute charts are included as descriptive screens only. Public trade data lacks account IDs, maker/taker linkage, and order-book state, so the evidence cannot identify whether the pattern comes from benign market-making, minimum-notional order routing, fee-tier farming, or wash trading.

## Data and Methodology

The analysis pulls recent public spot trades for six HTX markets (BTC, ETH, DOGE, TRX, SOL, XRP, all versus USDT) and four OKX reference markets (TRX, DOGE, SOL, XRP, all versus USDT). HTX's `market/history/trade` endpoint returns recent trade batches, which are expanded into individual trades. OKX's `market/trades` endpoint returns at most 500 recent trades per request.

The reproducible artifact set lives in this post directory:

- [`generate_analysis.py`](generate_analysis.py) fetches or reuses data, computes metrics, and writes the figures. It uses only the Python standard library.
- [`raw_trades.csv`](raw_trades.csv) is the captured public-trade tape used for the numbers below.
- [`metrics.csv`](metrics.csv) contains per-market summary metrics.
- [`instrument_rules.csv`](instrument_rules.csv) records HTX and OKX market-size rules fetched from public exchange metadata endpoints.
- [`resampled_top_size_metrics.csv`](resampled_top_size_metrics.csv) contains deterministic 500-trade bootstrap comparisons using seed `1712`.
- [`htx_trx_top_sizes.csv`](htx_trx_top_sizes.csv) lists the most repeated exact TRX/USDT sizes.
- [`snapshot.json`](snapshot.json) records endpoint templates, sample window, row count, and file hashes.

For each market, the script computes:

- **Top exact-size share:** the share of trades equal to the single most common `size`, rounded to 12 decimal places.
- **Unique-size share:** distinct size values divided by trade count.
- **Minimum-rule context:** modal trade size compared with the exchange's published minimum size and, for HTX, minimum notional.
- **Benford L1 distance:** a first-digit screening statistic, not a conclusive manipulation test.
- **Second-of-minute distribution:** a descriptive timing view, not a statistical null model for real trade arrivals.

By default, rerunning the script reuses the shipped `raw_trades.csv` so the published numbers are reproducible. Passing `--refresh` captures a new public-trade snapshot, so the row set and all derived numbers will change.

## Results

### Repeated Exact Sizes on HTX

{{< figure src="htx_top_exact_size_share.svg" caption="Share of trades equal to the single most common exact size, by HTX spot market. Exact-size matching uses 12 decimal places; snapshot window is recorded in snapshot.json." >}}

Every sampled HTX market has a modal exact size that repeats across many trades:

| Market | Top exact size | Count | Share | Approx. notional | HTX min-size ratio | HTX min-notional ratio |
|---|---:|---:|---:|---:|---:|---:|
| BTC/USDT | 0.000016 BTC | 580 / 2,303 | 25.2% | $1.23 | 1.6x | 1.23x |
| XRP/USDT | 1.10 XRP | 341 / 2,313 | 14.7% | $1.50 | 1.1x | 1.50x |
| ETH/USDT | 0.001 ETH | 314 / 2,322 | 13.5% | $2.11 | 10.0x | 2.11x |
| TRX/USDT | 8.42 TRX | 458 / 3,705 | 12.4% | $3.00 | 8.42x | 3.00x |
| DOGE/USDT | 12.60 DOGE | 230 / 2,484 | 9.3% | $1.30 | 12.6x | 1.30x |
| SOL/USDT | 0.015 SOL | 129 / 2,309 | 5.6% | $1.27 | 1.5x | 1.27x |

This table is deliberately cautious: the modal HTX sizes mostly sit near small-dollar order constraints. For BTC, XRP, DOGE, and SOL especially, the repeated size can plausibly be explained by minimum-notional routing or small-order aggregation. TRX/USDT is more interesting because the repeated lot is about $3 rather than just above the $1 floor, and nearby sizes form a broader cluster.

### Equal-Sample Comparison

{{< figure src="common_symbol_top_size_resample.svg" caption="Top exact-size share after downsampling HTX markets to 500 trades, compared with the observed 500-trade OKX samples. HTX points show deterministic bootstrap medians and 95% intervals." >}}

Because OKX returns only 500 recent trades while HTX returned 2,309 to 3,705 trades per market, raw HTX-vs-OKX comparisons are biased. The table below resamples each HTX market down to 500 trades 1,000 times and compares the median modal-size share with the corresponding OKX 500-trade sample.

| Asset | HTX 500-trade modal share | 95% bootstrap interval | OKX modal share | Readout |
|---|---:|---:|---:|---|
| TRX | 12.4% | 10.4%-15.0% | 2.6% | HTX TRX remains elevated after sample-size matching. |
| DOGE | 9.6% | 7.8%-11.6% | 17.6% | OKX DOGE is more concentrated in this short snapshot. |
| SOL | 5.6% | 4.0%-7.4% | 2.4% | HTX SOL is modestly higher, but the absolute level is small. |
| XRP | 14.6% | 12.2%-17.4% | 15.0% | HTX and OKX are similar in this snapshot. |

The important point is not that HTX is universally more clustered than OKX. It is not. The stronger finding is narrower: **HTX TRX/USDT has an unusually high repeated-size share relative to the same-asset OKX snapshot, even after matching sample size.**

### TRX/USDT Size Ladder

{{< figure src="htx_trx_top_sizes.svg" caption="Top 10 exact trade sizes in the captured HTX TRX/USDT tape. The neighboring 8.41-8.44 TRX sizes dominate the visible ladder." >}}

The most repeated TRX/USDT exact sizes form a narrow ladder:

| Rank | Exact size | Trades | Share | Buy / sell |
|---:|---:|---:|---:|---:|
| 1 | 8.42 | 458 | 12.4% | 235 / 223 |
| 2 | 8.41 | 364 | 9.8% | 168 / 196 |
| 3 | 8.43 | 357 | 9.6% | 184 / 173 |
| 4 | 8.44 | 234 | 6.3% | 123 / 111 |
| 5 | 2.80 | 185 | 5.0% | 0 / 185 |
| 6 | 2.81 | 112 | 3.0% | 0 / 112 |

The four-size `8.41`-`8.44` cluster accounts for 1,413 of 3,705 HTX TRX/USDT trades. The `2.80` and `2.81` sizes are smaller but one-sided in this capture, with all 297 trades marked as sells. Those observations are useful leads for a longer review, but public trade data cannot tell whether the same participant generated them.

### Benford and Timing Screens

{{< figure src="htx_benford_distance.svg" caption="L1 distance between observed first-significant-digit frequencies and the Benford expectation, by HTX market. This is a screening statistic, not a standalone test of manipulation." >}}

{{< figure src="htx_trx_first_digit_distribution.svg" caption="Observed first-significant-digit distribution for HTX TRX/USDT trade sizes versus Benford expectation. The spike at digit 8 is mechanically tied to the repeated 8.41-8.44 TRX sizes." >}}

HTX TRX/USDT has the largest first-digit distance in the sampled HTX set. This is expected once the top-size ladder is visible: if many trades sit at `8.xx`, the leading digit will concentrate at `8`. Benford-style screens are still useful for anomaly discovery, but trade-size data on a single exchange is bounded by minimum-size, precision, and notional rules. The Benford chart should therefore be read as an index into the size ladder above, not as independent proof of manipulation.

{{< figure src="trx_second_of_minute_distribution.svg" caption="TRX/USDT trades by second-of-minute on HTX and OKX. This descriptive timing view is not a formal manipulation test because the exchange samples cover different windows." >}}

The within-minute chart is included for completeness, but it is intentionally not used as a headline claim. Real trade arrivals are bursty, public endpoint windows are short, and the HTX and OKX samples are not synchronized. A stronger timing analysis would need longer matched windows and a better null model for clustered arrivals.

## Interpretation

This snapshot supports a narrow market-health claim:

> HTX TRX/USDT exhibited repeated exact-size trade clustering in this public-trade capture, and that clustering remains visible after matching the OKX sample size. The pattern deserves follow-up surveillance, but it is not enough to identify wash trading by itself.

The most plausible benign explanations are:

- Small orders being routed near exchange minimum-notional thresholds.
- A dominant market maker or router using a fixed-lot sizing strategy.
- Fee-tier farming or inventory rebalancing that repeats small sizes.
- Public endpoint batching or timestamp coarsening that makes bursts look more regular than they were at the matching-engine level.

The manipulation hypothesis becomes stronger only if the same pattern persists across days, appears with synchronized price/volume effects, or can be connected to account/order-book behavior. None of that is available from this public snapshot alone.

## Limitations and Next Checks

- **Short window:** the capture is a snapshot, not a time series. HTX market spans range from about 80 minutes to about 11 hours; OKX spans are shorter because of the 500-trade endpoint cap.
- **No account linkage:** public trade tapes do not expose whether repeated lots are generated by one account, many accounts, or both sides of the same beneficial owner.
- **Minimum-order effects:** several modal sizes are close to published exchange minimums or minimum-notional thresholds. Those rules must be controlled before treating clustering as suspicious.
- **No order book:** without depth, quote updates, and order IDs, the analysis cannot distinguish liquidity provision from wash-like printing.
- **No longitudinal baseline:** the next step should repeat this measurement over days or weeks and compare against matched windows on other venues.

Useful follow-up work would be to schedule repeated captures, compute the same 500-trade bootstrap over rolling windows, add a Coinbase or Kraken control where available, and test whether the TRX size ladder persists through different volatility regimes.

## Reproducibility

To reproduce the exact numbers and figures from the captured tape:

```bash
cd content/research/market-health/posts/2026-05-20-htx-trx-micro-lot-patterns
python3 generate_analysis.py
```

To capture a fresh public-trade sample instead:

```bash
python3 generate_analysis.py --refresh
```

The exact published tape is identified by `raw_trades.csv` SHA-256 in [`snapshot.json`](snapshot.json). Re-running with `--refresh` will change the rows and therefore the metrics.
