---
title: "Repeated-lot clustering on Binance CELR/USDT"
date: 2026-06-12
description: "A one-day Binance aggregate-trade sample shows that two exact CELR/USDT quantities accounted for 31% of trades and 27.7% of quote volume, a pattern consistent with automated volume shaping risk."
entities:
  - Binance
  - CELR
---

## Summary

On June 11, 2026, Binance's public aggregate-trade dataset for CELR/USDT showed an unusually concentrated trade-size pattern:

1. Two exact quantities, `6788` CELR and `6888` CELR, appeared in 5,065 of 16,275 aggregate trades.
2. Those two quantities represented 31.12% of aggregate trades and 27.74% of quote volume, equal to 74,208.83 USDT.
3. The pattern was not confined to a single burst. The two quantities accounted for at least 20% of hourly aggregate trades in 21 of 24 UTC hours.
4. Among non-stablecoin comparison markets sampled for the same day, the top-two quantity concentration was materially lower: GMX/USDT at 0.82%, FLOKI/USDT at 7.93%, and DYDX/USDT at 2.19%.

This does not prove self-trading or wash trading by itself. It is a surveillance signal: a large share of daily activity was printed through two neighboring lot sizes, repeatedly, across most of the day. That is more consistent with automated volume maintenance or inventory cycling than with independent retail order flow.

## Dataset and method

The analysis uses Binance's official public aggregate-trade archives for June 11, 2026:

- `CELRUSDT`
- `GMXUSDT`
- `FLOKIUSDT`
- `DYDXUSDT`
- `TUSDUSDT`

The source URLs are listed in `data/source_urls.csv`. The script `scripts/fetch_and_analyze.py` downloads the exchange archives, computes daily metrics, and regenerates the CSV files and charts in this directory.

The main metric is repeated-lot concentration:

```
top-two quantity share = trades printed at the two most common exact quantities / all aggregate trades
```

The metric is intentionally simple. Organic flow can include round-number clustering, especially in stablecoins, but a non-stable asset where two adjacent exact quantities account for nearly one third of trades deserves closer inspection.

## CELR/USDT lot concentration

The two most common CELR/USDT trade quantities were separated by only 100 CELR:

| Quantity    | Aggregate trades | Share of trades |   Quote volume |
| ----------- | ---------------: | --------------: | -------------: |
| `6788` CELR |            2,545 |          15.64% | 36,996.82 USDT |
| `6888` CELR |            2,520 |          15.48% | 37,212.01 USDT |
| Combined    |            5,065 |          31.12% | 74,208.83 USDT |

The next most common quantity, `2686.2` CELR, appeared only 25 times. That steep drop-off is the main anomaly. The leading two lots are not merely the top of a smooth distribution; they are isolated peaks.

{{< figure src="images/celr_top_quantities.svg" alt="CELR/USDT top trade quantity concentration" caption="Top CELR/USDT aggregate-trade quantities on Binance, June 11, 2026. The two leading exact quantities dominate the distribution." >}}

## Persistence through the day

If the repeated quantities were caused by one short-lived liquidity event, they would be concentrated in a small number of hours. Instead, the pattern persisted through most of the UTC day:

- The combined `6788` and `6888` lot share exceeded 20% in 21 of 24 hours.
- It exceeded 35% in 11 of 24 hours.
- The maximum hourly share was 46.79% at 07:00 UTC.
- The daily average of the hourly shares was 32.57%.

{{< figure src="images/celr_hourly_repeated_lot_share.svg" alt="Hourly share of repeated CELR/USDT lots" caption="Hourly share of CELR/USDT trades printed at the two dominant quantities. The pattern persists across the session rather than appearing as a single isolated burst." >}}

This persistence matters because repeated-lot bursts can happen naturally during a single large execution program. A full-day pattern is more consistent with an always-on bot, market-making loop, or volume-shaping process.

## Cross-market comparison

The same script computed top-two quantity concentration for several Binance markets on the same date. The comparison set is not meant to be exhaustive; it is a sanity check against active markets with publicly available daily aggregate-trade archives.

| Market     | Trades |      Quote volume | Top-two quantity share | Top-two quote-volume share |
| ---------- | -----: | ----------------: | ---------------------: | -------------------------: |
| CELR/USDT  | 16,275 |   267,495.22 USDT |                 31.12% |                     27.74% |
| GMX/USDT   |  3,779 |   196,901.33 USDT |                  0.82% |                      0.56% |
| FLOKI/USDT | 16,718 | 1,380,641.20 USDT |                  7.93% |                      0.38% |
| DYDX/USDT  | 52,288 | 1,134,355.76 USDT |                  2.19% |                      3.08% |
| TUSD/USDT  |  4,106 |   103,786.69 USDT |                 30.64% |                      9.14% |

{{< figure src="images/comparison_top_two_qty_share.svg" alt="Top-two trade quantity concentration by market" caption="Top-two exact quantity concentration for the sampled Binance markets. TUSD/USDT is included as a stablecoin reference where round-lot clustering is expected to be more common." >}}

TUSD/USDT is a useful cautionary reference. Stablecoin pairs can naturally show high exact-size clustering because arbitrage and inventory management often target small integer USDT notional amounts. CELR/USDT is different: it is a volatile non-stable asset, and the dominant quantities also represented 27.74% of the day's quote volume, not just a large number of tiny prints.

## Interpretation

The CELR/USDT pattern is consistent with a volume-shaping risk signal:

1. Two neighboring exact quantities dominated the day.
2. The repeated lots were present across most hours.
3. The lots represented a material share of both trade count and quote volume.
4. Similar non-stablecoin samples did not show comparable exact-size concentration.

The most plausible benign explanations are a single execution algorithm reusing two child-order templates, or a liquidity provider repeatedly refreshing two inventory buckets. The market-health concern is that the same footprint is also compatible with wash-trading style volume maintenance, especially if the repeated prints are offsetting between related accounts.

The public aggregate-trade dataset does not expose account identifiers or full order-book state. Confirming manipulation would require at least one of the following:

- maker and taker account linkage;
- order-book snapshots around the repeated prints;
- a longer multi-day sample to test whether the same quantities recur after market conditions change;
- exchange-side surveillance data showing whether the repeated prints are economically offsetting.

## Reproducibility

Supporting files in this article directory:

- `data/comparison_daily_metrics.csv`
- `data/celr_top_quantities.csv`
- `data/celr_hourly_repeated_lot_share.csv`
- `data/source_urls.csv`
- `scripts/fetch_and_analyze.py`

Run the script from the repository root to rebuild the datasets and SVG charts:

```bash
python3 content/research/market-health/posts/2026-06-12-celr-repeated-lot-clustering/scripts/fetch_and_analyze.py
```
