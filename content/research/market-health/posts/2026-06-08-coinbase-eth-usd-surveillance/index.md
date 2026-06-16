---
title: "ETH-USD trade-level surveillance snapshot"
date: 2026-06-08
description: "A reproducible Coinbase trade-level snapshot for time-of-trade clustering, side imbalance, price-level concentration, and round-size checks."
---

This article adds a small reproducible surveillance snapshot for `ETH-USD` using the Coinbase Exchange public trades endpoint. It is a market-health example, not an allegation of manipulation. The purpose is to show how the wiki's time-of-trade, buy/sell, VWAP-adjacent, and volume-distribution concepts can be applied to trade-level data before a reviewer escalates to deeper order-book or venue-supplied datasets.

## Dataset

- Venue: Coinbase Exchange public trades endpoint
- Product: `ETH-USD`
- Snapshot date: `2026-06-08`
- Trades collected: `500`
- Window start UTC: `2026-06-08T17:50:49.891339+00:00`
- Window end UTC: `2026-06-08T17:52:50.402823+00:00`
- Approximate notional in sample: `$288984`
- Average notional per trade: `$577.97`

The raw sample is included in `trades_sample.csv`. Derived tables are included in `second_distribution.csv`, `top_price_levels.csv`, and `repeated_time_price_clusters.csv`.

## Checks

### Time-of-trade clustering

The most active second-of-minute bucket was second `53`, with `45` of `500` trades (9.0%). A perfectly uniform baseline would place about `8.3` trades in each second bucket. Deviations alone are not proof of manipulation, but repeated concentration in a narrow set of seconds can indicate scheduled execution, automated market-making cadence, or wash-trading scripts that fire on fixed intervals.

{{< figure src="second_distribution.svg" alt="ETH-USD trades by second of minute" caption="ETH-USD trade count by second of minute in the Coinbase snapshot." >}}

### Buy/sell side balance

- Buy-side prints: `134` (26.8%)
- Sell-side prints: `366` (73.2%)
- Absolute side imbalance: `46.4%`

A high side imbalance during a short window can be normal during directional moves. It becomes more suspicious when paired with stable prices, repeated sizes, or bursts at identical timestamps.

### Price-level concentration

The most repeated rounded price level was `$1684.3`, appearing in `26` trades (5.2%). Prices were rounded to `2` decimal places for this product. A concentrated price level is expected near a live spread, but reviewers should inspect whether repeated prints at one level also share repeated sizes or timestamp bursts.

### Round-size and tiny-trade checks

- Integer-sized trades: `7` (1.4%)
- Sizes with three or fewer decimal places: `93` (18.6%)
- Trades below `0.0001` base units: `17` (3.4%)

Round or tiny sizes are useful screening features. A high share can indicate retail UI behavior, bot dust, maker/taker inventory management, or synthetic prints. It should be combined with account-level or order-book evidence before drawing conclusions.

### Repeated timestamp-price bursts

| Timestamp UTC                 | Rounded price | Trades |
| ----------------------------- | ------------: | -----: |
| 2026-06-08T17:52:15.830+00:00 |       1684.03 |      5 |
| 2026-06-08T17:51:14.140+00:00 |       1684.54 |      4 |
| 2026-06-08T17:51:24.581+00:00 |        1683.9 |      4 |
| 2026-06-08T17:51:54.713+00:00 |       1684.74 |      4 |
| 2026-06-08T17:52:33.128+00:00 |       1683.36 |      4 |

Repeated timestamp-price bursts can be benign matching-engine batching. They become more relevant when the same pattern repeats across many windows or aligns with anomalous size distributions.

## Interpretation

This snapshot is best treated as a first-pass surveillance artifact. It does not prove manipulation. It identifies where a reviewer should ask for deeper data:

1. Order-book depth before and after the clustered seconds.
2. Account-level self-trade or common-beneficial-owner checks.
3. Longer windows to determine whether second-of-minute concentration persists.
4. Cross-venue comparison for the same product and time range.

The value for the Market Health wiki is reproducibility: every claim above can be recalculated from the included CSV files, and the same method can be rerun against a larger dataset.

## Files

- `trades_sample.csv`
- `second_distribution.csv`
- `top_price_levels.csv`
- `repeated_time_price_clusters.csv`
- `second_distribution.svg`
