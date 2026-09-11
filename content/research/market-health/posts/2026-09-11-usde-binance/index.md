---
title: "USDe on Binance: quote-market fragmentation and misleading sell-flow signals during the October 2025 dislocation"
description: "A reconstruction of 221,010 aggregate trades shows persistent price differences across USDe quote markets, a recovery dominated by seller-initiated turnover, and why a single extreme print is an incomplete market-health measure."
date: 2026-09-11
entities:
  - Binance
  - USDe
  - USDT
  - USDC
---

## Summary

The USDe dislocation on Binance on 10 October 2025 provides a useful test of three market-surveillance assumptions: that two quote markets on one venue give interchangeable prices, that aggressive selling implies a falling price, and that a daily minimum describes the scale of an event.

This study reconstructs **221,010 aggregate-trade records** from USDE/USDT and USDE/USDC over 3–11 October. It finds:

1. **Price fragmentation survives tighter time and volume filters.** At 21:46 UTC, the USDE/USDC minute VWAP, converted with that minute's USDC/USDT VWAP, was **15.98% below** the USDE/USDT VWAP. Both USDe pairs traded more than one million USDe in that minute. A same-second check still finds a gap exceeding 5% in all 16 seconds where each pair traded at least 10,000 USDe, even when the conversion uses the minute's highest observed USDC/USDT price.
2. **Seller-initiated turnover dominated a recovery.** From the first to last minute of the exploratory 21:44–21:54 interval, the USDE/USDT VWAP rose **36.31%**, while **81.18%** of that interval's quote notional was seller-initiated.
3. **The minimum and the broader event measure different things.** The exact 0.65 USDT minimum accounts for **0.00261%** of the day's USDE/USDT notional. However, **37.47%** of daily notional traded below 0.98 USDT and **14.03%** below 0.90 USDT. An isolated minimum therefore understates the information available about a substantial, wider dislocation.

These are observations about price formation and the interpretation of manipulation alerts. The feed contains no beneficial-owner identifiers, order-book lifecycle, or liquidation flags; it cannot identify self-trading or an intentional manipulation campaign.

## Event boundary and data checks

[Binance's incident announcement](https://www.binance.com/en/support/announcement/detail/0989d6c7f32545bfb019e3249eaabc3f) describes compensation for affected collateral liquidations during 21:36–22:16 UTC and subsequent changes to index safeguards. That published interval supplies an external time reference. The calculations use half-open intervals, including the start and excluding the end. The reconstructed USDE/USDT tape already contains prices below 0.98 at **21:20:58.720615 UTC**; the compensation interval is not treated as the first anomalous execution or as an observed oracle-update schedule.

The dataset has 18 daily aggregate-trade archives, covering both USDe pairs for nine days, and four event-day minute-bar archives: the same two pairs plus USDC/USDT and BTC/USDT. All **22 ZIP files match the exchange's published SHA-256 checksums**. The [source manifest](source_manifest.json) fixes every URL, digest, member name and file size.

On the event day, USDE/USDT has **112,002 aggregate records representing 136,677 underlying trades**; USDE/USDC has **33,505 records representing 35,292 underlying trades**. Those counts are executions, not people or independent orders. The distinction matters when a detector uses transaction frequency.

Across both event-day pairs, reconstruction agrees with all **2,880 official minute bars** on observed open/high/low/close, underlying trade counts, base volume, quote notional and taker-buy volume. The maximum quote-notional difference is approximately **3.73 × 10⁻⁹ quote units**, from floating-point summation; base-volume differences are zero. All aggregate IDs within each daily archive are consecutive, timestamps are ordered and within their source day, and underlying trade-ID ranges do not overlap. This validates the transformation against another published aggregation from the same venue. It is not an independent audit of Binance's matching engine.

Minutes without reported trades remain absent in the trade-derived series. They are neither interpolated nor assigned the last price. Both quote-market coverage and turnover must therefore accompany a price comparison.

## Two quote markets did not supply interchangeable prices

USDT and USDC are separate quote assets. Comparing the raw numerical prices as if both were dollars would introduce another error: USDC/USDT itself moved during the event. The comparison below converts each USDE/USDC minute VWAP using the contemporaneous USDC/USDT minute VWAP:

```text
VWAP = sum(price × USDe quantity) / sum(USDe quantity)
converted_USDC_market = VWAP(USDE/USDC) × VWAP(USDC/USDT)
relative_gap = converted_USDC_market / VWAP(USDE/USDT) − 1
```

This product is an approximate minute-level normalization. The two volume weights differ, and the constituent executions need not be simultaneous. It does not describe an executable triangular trade, available depth, or realizable profit.

{{< figure src="quote-market-prices.png" alt="Binance USDe minute prices differ across USDT and USDC quote markets during the dislocation, even after normalizing the moving USDC quote asset" caption="Trade-derived minute VWAPs, with USDE/USDT execution ranges and a separate USDC/USDT conversion series. Gaps remain where comparison data are absent. The gray band marks the announcement's 21:36–22:16 UTC interval." >}}

At **21:46 UTC**, the observations are:

| Measurement                                  |                  Value |
| -------------------------------------------- | ---------------------: |
| USDE/USDT VWAP                               | 0.790162 USDT per USDe |
| USDE/USDT base volume                        |        15,676,554 USDe |
| USDE/USDC VWAP                               | 0.666022 USDC per USDe |
| USDE/USDC base volume                        |         1,871,877 USDe |
| USDC/USDT conversion VWAP                    | 0.996838 USDT per USDC |
| Converted USDC-market VWAP                   | 0.663917 USDT per USDe |
| Converted price relative to USDT-market VWAP |                −15.98% |

The result is not solely a comparison involving a negligible-volume minute. Over the 21:00–23:00 event window, requiring **at least 100,000 USDe on each pair in the same minute** leaves 79 eligible minutes; seven have an absolute normalized gap above 5%. Raising the requirement to one million leaves 18 minutes, six of which exceed 5%. The [sensitivity table](quote_gap_sensitivity.csv) also includes a 10,000-USDe threshold.

To address within-minute timing, [the same-second reconstruction](same_second_comparison_2146.csv) divides 21:46 into one-second intervals. It uses the **highest observed USDC/USDT price in the whole minute** for conversion, a choice that raises the USDC-market result and makes its lower-price gap harder to obtain. At a 1,000-USDe-per-pair threshold, 22 of 25 matched seconds still put the USDC-market value more than 5% below the USDT-market value. At 10,000 USDe, the result holds in **16 of 16** eligible seconds.

This check weakens the explanation that the entire difference is an artifact of one-minute averaging. It still compares reported executions within bins, not synchronized executable bids and asks. Order-book snapshots, inventory and transfer constraints would be required to explain why the difference persisted or to estimate whether arbitrage was available.

## A high sell ratio did not determine the direction of the price

For an aggregate record, `buyer_is_maker=True` means the buyer supplied resting liquidity and the seller was the taker. The analysis therefore computes seller-initiated notional as the sum of `price × quantity` for those records. It does not count every buyer and seller as a separate trade; each execution necessarily has both sides. The [Binance archive documentation](https://github.com/binance/binance-public-data) specifies the field layout and timestamp convention used by the loader.

The four reference windows expose the limits of a simple directional interpretation:

| UTC window  | USDE/USDT VWAP | Quote notional, million USDT | Seller-initiated notional share |
| ----------- | -------------: | ---------------------------: | ------------------------------: |
| 21:00–21:20 |       0.999607 |                        30.42 |                          97.35% |
| 21:20–21:36 |       0.935582 |                        27.98 |                          82.43% |
| 21:36–22:16 |       0.858723 |                       424.03 |                          70.00% |
| 22:16–23:00 |       0.985082 |                       351.48 |                          53.79% |

Before the first break, almost all notional was seller-initiated, yet the window VWAP stayed near one USDT. A narrower interval provides the opposite-direction example. Between **21:44 inclusive and 21:54 exclusive**, the first and last minute VWAPs are **0.677195** and **0.923093**, a **36.31% rise**. Of approximately **164.00 million USDT** traded over that interval, **81.18%** was seller-initiated. This interval was selected after inspecting the price path; it is an exploratory example, not a pre-registered causal test.

{{< figure src="price-and-aggressor-flow.png" alt="USDE/USDT minute VWAP rises through an interval whose turnover is mostly seller-initiated" caption="The orange interval illustrates a recovery with predominantly aggressive selling. Bar height is the seller-initiated share of each minute's quote notional; the reported 81.18% is calculated from the whole interval's notional, not by averaging bar heights." >}}

Trade sign describes which side crossed the spread. Prices also depend on where resting liquidity is available and how that liquidity changes. A tape with a rising price and many aggressive sells can be compatible with bids moving higher or being replenished. This dataset does not observe that order-book process, and it cannot distinguish discretionary sells from liquidation-related orders.

For surveillance, this is a counterexample to treating an extreme buy/sell ratio as a self-contained manipulation classification or a deterministic price predictor. The signed-volume signal should be combined with price response, quoted depth and order lifecycle information. Common beneficial ownership would require additional evidence before a self-trading claim.

## The smallest print and the amount traded below a threshold

The exact **0.65 USDT** minimum occurred at **21:54:24.242962 UTC** in one aggregate record covering four underlying trades: **55,726 USDe**, or **36,221.90 USDT**. That is **0.00261%** of the day's approximately **1.388 billion USDT** notional.

The broader distribution makes clear why neither the minimum alone nor its small weight is a sufficient description:

| Executed price strictly below | Share of event-day USDE/USDT quote notional |
| ----------------------------- | ------------------------------------------: |
| 0.98 USDT                     |                                      37.47% |
| 0.95 USDT                     |                                      26.97% |
| 0.90 USDT                     |                                      14.03% |
| 0.80 USDT                     |                                       7.22% |
| 0.70 USDT                     |                                       2.21% |
| 0.66 USDT                     |                                     0.0302% |

The [threshold dataset](threshold_summary.csv) gives first and last observed crossings as well as quantities and notionals. The span between those timestamps is not a continuous time-below-threshold estimate. [The deepest execution records](deepest_executions.csv) preserve timestamps, aggregate IDs, underlying ID ranges, quantities and aggressor direction for every USDE/USDT record at or below 0.66.

The USDC-quoted market has its own minimum: **0.6268 USDC**, first observed at **21:46:13.731477 UTC**. Its minimum appears in 14 aggregate records, all buyer-initiated, totaling **171,965 USDe**. A minimum-price alert without a quote-asset identifier, timestamp, execution weight and market context would conceal these differences. None of these figures is an estimate of customers' collateral losses.

## Turnover context and the limits of this case

The 21:00–23:00 USDE/USDT window carried **833.91 million USDT**, compared with a median **2.66 million USDT** for the same clock window on the preceding seven days, a ratio of **313.15**. The USDC-quoted pair had a much smaller preceding baseline and an even larger event-to-baseline ratio. The following figure uses base USDe volume so the bars remain in the same asset units across quote markets.

{{< figure src="matched-window-turnover.png" alt="USDe turnover in identical two-hour windows is far higher on October 10 than on the seven preceding days, for both Binance quote markets" caption="Nine matched clock windows, including seven preceding dates and the following day. The vertical scale is logarithmic. These windows provide descriptive context, not independent samples for a population significance claim." >}}

High turnover and an unusual size or sign distribution can accompany urgent inventory transfer during a dislocation. The public record here establishes large reported turnover, fragmented execution prices and an example of price recovery under predominantly aggressive selling. It does not establish whose inventory changed, whether two accounts had a common owner, whether a particular order caused a liquidation, or whether any participant intended to manipulate a collateral mark.

The collateral connection comes from Binance's announcement, which also describes adding redemption-price information to index weights and a floor for the USDE index. The archive does not contain the historical index constituents, update schedule or account health calculations, so this study does not reconstruct the liquidation engine or assign causality to an individual trade.

This is a **single-venue study**. No independently downloaded Bybit or other-venue tape is included, and no conclusion about global USDe pricing or protocol solvency follows from these files. The useful surveillance result is narrower: quote-market fragmentation persists under substantial-volume and same-second checks, while signed turnover and a daily extreme each omit information needed to interpret the event.

## Reproduction and supporting files

Run from this article's directory:

```sh
python3 fetch_data.py
python3 analyze.py
python3 -m pip install -r requirements.txt
python3 plot.py
```

The fetcher requires `curl`; data reconstruction uses the Python standard library. Figure reproduction was checked with Python 3.12, Matplotlib 3.11.1 and NumPy 2.5.3. The fetcher downloads fixed historical files and validates the exchange's checksums. It requires no exchange login or API key. The analysis reads timestamps as integer microseconds, preserves the archive ordering and validates each source day. Missing trade minutes remain missing.

[Results and checks](results.json), [daily summaries](daily_summary.csv), [reference-window totals](phase_summary.csv), [minute metrics](minute_metrics.csv), [quote comparisons](quote_comparison.csv), [matched clock windows](matched_clock_windows.csv), and [control minute bars](control_minutes.csv) provide the numbers behind the prose and figures. The [reproduction notes](REPRODUCING.md) map each output to its role and state the remaining coverage limits.

Analysis and reproducible code: moke.
