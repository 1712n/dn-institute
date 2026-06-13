---
title: "Exact-lot dominance in Binance NOT/USDT aggregate trades"
date: 2026-06-13
description: "Binance aggregate-trade archives show that two exact NOT/USDT quantities, 200000 NOT and 14748 NOT, accounted for 39.42% to 53.09% of trades across four consecutive days."
entities:
  - Binance
  - NOT
---

## Summary

From June 8 to June 11, 2026, Binance's public aggregate-trade archives for NOT/USDT showed a persistent exact-lot concentration pattern:

1. The same two quantities, `200000` NOT and `14748` NOT, were the two most common quantities on each sampled day.
2. Their combined trade share ranged from 39.42% to 53.09%.
3. On June 11, the two quantities appeared in 6,298 of 11,862 aggregate trades and represented 283,121.28 USDT of quote volume.
4. The June 11 pattern persisted across the day: every UTC hour contained the two dominant lots, and 22 of 24 hourly buckets had a dominant-lot trade share above 40%.
5. In the same-date comparison set, NOT/USDT had the highest top-two exact quantity concentration by trade count. CELR/USDT, STRK/USDT, and OP/USDT also showed elevated concentration, but none exceeded NOT/USDT's 53.09% trade share.

This does not prove self-trading or wash trading. It is a surveillance signal: more than half of the day's aggregate trades were printed through two exact quantity templates, and the same two templates dominated four consecutive daily archives. That is not a typical shape for independent retail flow.

## Dataset and method

The analysis uses Binance's official public aggregate-trade archives. The NOT/USDT persistence check covers June 8-11, 2026. The cross-market comparison uses June 11, 2026 for:

- `NOTUSDT`
- `CELRUSDT`
- `STRKUSDT`
- `OPUSDT`
- `OGUSDT`
- `SCRUSDT`
- `SANDUSDT`
- `FLOKIUSDT`
- `DOGEUSDT`
- `ADAUSDT`
- `SPKUSDT`

The source URLs are listed in `data/source_urls.csv`. The script `scripts/fetch_and_analyze.py` downloads the exchange archives, computes daily and hourly metrics, and regenerates the CSV files and SVG charts in this directory.

The main metric is exact-lot dominance:

```text
dominant-lot share = trades printed at 200000 NOT or 14748 NOT / all NOT/USDT aggregate trades
```

For comparison markets, the script also computes a generic top-two exact quantity share:

```text
top-two exact quantity share = trades printed at the two most common exact quantities / all aggregate trades
```

## NOT/USDT lot concentration

The two most common NOT/USDT quantities on June 11 had very different economic sizes:

| Quantity     | Aggregate trades | Share of trades |    Quote volume | Quote-volume share |
| ------------ | ---------------: | --------------: | --------------: | -----------------: |
| `200000` NOT |            3,226 |          27.20% | 264,561.60 USDT |             19.07% |
| `14748` NOT  |            3,072 |          25.90% |  18,559.68 USDT |              1.34% |
| Combined     |            6,298 |          53.09% | 283,121.28 USDT |             20.41% |

The leading lot accounted for most of the quote volume, while the smaller lot supplied nearly the same number of prints with much less economic size. That split matters because a simple "round number preference" would more naturally cluster around one family of similar quantities. Here, two separate templates dominated count, while only one dominated notional value.

{{< figure src="images/notusdt_top_quantities.svg" alt="NOT/USDT top trade quantity concentration" caption="Top NOT/USDT aggregate-trade quantities on Binance, June 11, 2026. Two exact quantities account for more than half of aggregate trades." >}}

## Four-day persistence

The same pair of quantities dominated all four sampled days:

| Date       | Trades |      Quote volume | `200000` + `14748` trades | Trade share | Quote-volume share |
| ---------- | -----: | ----------------: | ------------------------: | ----------: | -----------------: |
| 2026-06-08 |  6,473 |   512,442.80 USDT |                     2,589 |      40.00% |             20.70% |
| 2026-06-09 |  6,600 |   433,397.43 USDT |                     2,602 |      39.42% |             24.16% |
| 2026-06-10 | 11,404 | 1,184,472.73 USDT |                     5,315 |      46.61% |             18.87% |
| 2026-06-11 | 11,862 | 1,387,451.88 USDT |                     6,298 |      53.09% |             20.41% |

{{< figure src="images/notusdt_four_day_exact_lot_share.svg" alt="Four-day exact-lot share for NOT/USDT" caption="The same two NOT/USDT quantities were the leading exact lots across four consecutive Binance daily aggregate-trade archives." >}}

Persistence is important. Exact-size clustering can appear during a single execution program, a listing event, or an isolated liquidity window. A four-day pattern makes a one-off manual explanation less likely and points toward an automated process reusing the same quantity templates.

## Intraday persistence

The June 11 pattern was not a single burst:

- The two dominant lots appeared in every UTC hour.
- Dominant-lot trade share exceeded 40% in 22 of 24 hourly buckets.
- Dominant-lot trade share exceeded 50% in 11 of 24 hourly buckets.
- The maximum hourly share was 69.44% at 12:00 UTC.
- The minimum hourly share was still 18.03% at 18:00 UTC.

{{< figure src="images/notusdt_hourly_exact_lot_share.svg" alt="Hourly share of dominant NOT/USDT exact lots" caption="Hourly share of NOT/USDT trades printed at 200000 NOT or 14748 NOT. The pattern persists across the session." >}}

The intraday shape is consistent with a background process rather than an isolated block of manual activity. The public data cannot identify the accounts involved, but the persistence is enough to justify exchange-side review.

## Cross-market comparison

The same script computed top-two exact quantity concentration for several Binance markets on June 11, 2026:

| Market     |  Trades |       Quote volume | Top-two exact quantity share | Top-two quote-volume share |
| ---------- | ------: | -----------------: | ---------------------------: | -------------------------: |
| NOT/USDT   |  11,862 |  1,387,451.88 USDT |                       53.09% |                     20.41% |
| CELR/USDT  |  16,275 |    267,495.22 USDT |                       31.12% |                     27.74% |
| STRK/USDT  |   8,621 |  1,555,405.08 USDT |                       32.90% |                      7.19% |
| OP/USDT    |  14,146 |  2,418,189.88 USDT |                       30.41% |                      3.04% |
| OG/USDT    |   7,613 |    721,387.73 USDT |                       27.45% |                      1.58% |
| SCR/USDT   |   7,236 |    364,717.23 USDT |                       22.94% |                     30.03% |
| SAND/USDT  |  18,876 |    861,655.23 USDT |                       14.84% |                      1.66% |
| FLOKI/USDT |  16,718 |  1,380,641.20 USDT |                        7.93% |                      0.38% |
| DOGE/USDT  |  81,087 | 48,852,769.51 USDT |                        5.95% |                      0.41% |
| ADA/USDT   |  37,086 | 30,935,714.41 USDT |                        2.04% |                      0.32% |
| SPK/USDT   | 101,120 |  2,801,129.90 USDT |                       12.97% |                      2.36% |

{{< figure src="images/comparison_top_two_qty_share.svg" alt="Top-two trade quantity concentration by market" caption="Top-two exact quantity concentration for the sampled Binance markets on June 11, 2026. NOT/USDT is the highest trade-count outlier in this comparison set." >}}

This comparison is not an exhaustive market-wide screen, but it helps separate NOT/USDT from ordinary round-lot behavior. Large assets such as ADA/USDT and DOGE/USDT showed much lower top-two exact quantity concentration in the same archive format. Other smaller markets had elevated exact-lot concentration, but NOT/USDT was the highest trade-count outlier in the sample.

## Interpretation

The NOT/USDT pattern is compatible with an exact-lot dominance risk signal:

1. Two exact quantities accounted for more than half of June 11 aggregate trades.
2. The same two quantities were the top two quantities across four consecutive days.
3. The pattern appeared across the session, not only during a short event window.
4. One template carried most of the notional exposure, while the other created a similar number of smaller prints.
5. The public aggregate-trade data does not expose account identifiers, so the result should be treated as a surveillance trigger rather than proof of manipulation.

Plausible benign explanations include a liquidity provider reusing two child-order templates, an execution algorithm maintaining fixed inventory slices, or retail users clustering around default order sizes. The market-health concern is that the same footprint is also compatible with automated volume maintenance or wash-trading style activity if economically related accounts are on both sides of the prints.

Confirming manipulation would require exchange-side data that is not public:

- maker and taker account linkage;
- order-book snapshots around the repeated prints;
- self-trade prevention records;
- account-level profit and loss for the dominant lots;
- longer follow-up data showing whether the same exact lots persist after market conditions change.

## Reproducibility

Supporting files in this article directory:

- `data/comparison_daily_metrics.csv`
- `data/notusdt_daily_persistence.csv`
- `data/notusdt_top_quantities.csv`
- `data/notusdt_hourly_exact_lot_share.csv`
- `data/source_urls.csv`
- `scripts/fetch_and_analyze.py`

Run the script from the repository root to rebuild the datasets and SVG charts:

```bash
python3 content/research/market-health/posts/2026-06-13-notusdt-exact-lot-dominance/scripts/fetch_and_analyze.py
```
