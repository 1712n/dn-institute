---
title: "Trade aggregation and first-digit surveillance metrics"
bookToc: true
weight: 35
---

A surveillance metric can change substantially when the same executions are represented as individual fills or aggregate trades. In the Binance ADAUSDT Spot archives for **10 September 2026 UTC**, the share of base quantities beginning with digit 2 is **61.56% for raw trades and 19.87% for aggregate trades**. Yet both files represent exactly **134,802,016.1 ADA**, and every aggregate reconciles to a contiguous group of raw trade IDs. The change in representation alone is enough to change these row-level diagnostics. These results are calculated from the two official archives by the accompanying [analysis](analysis.py); full counts and checks are in [metrics.json](metrics.json).

This example supports a practical prerequisite for using the wiki's [first-digit](../benford/) and [trade-volume distribution](../volumedist/) metrics: **establish what one observation represents before comparing venues or alert thresholds**. The archives do not identify account ownership or label wash trades. This analysis therefore measures feed sensitivity, not manipulation prevalence.

## Data and observation units

The inputs are Binance's official [raw trade archive](https://data.binance.vision/data/spot/daily/trades/ADAUSDT/ADAUSDT-trades-2026-09-10.zip) and [aggregate-trade archive](https://data.binance.vision/data/spot/daily/aggTrades/ADAUSDT/ADAUSDT-aggTrades-2026-09-10.zip). Their [published schemas](https://github.com/binance/binance-public-data#spot) distinguish individual trade IDs from aggregate IDs with first/last constituent trade IDs. Binance's [aggregate-trade endpoint documentation](https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#compressedaggregate-trades-list) describes compression of executions from the same taker order at the same time and price. The raw archive does not expose taker-order identifiers, so order ownership is not independently verified here.

| Property | Raw `trades` | `aggTrades` |
| --- | ---: | ---: |
| Rows | 167,388 | 35,811 |
| Quantity unit | ADA per raw trade | ADA summed over constituent trades |
| Total base quantity | 134,802,016.1 ADA | 134,802,016.1 ADA |
| Mean raw rows per aggregate | — | 4.6742 |

Source: [sample counts and exact quantity reconciliation](metrics.json). No archive rows are deduplicated, sampled, or discarded in the daily comparison. Each row receives one vote in its own distribution; the percentages below are **row-count shares, not volume shares**.

The bundled files match the exchange-published SHA-256 sidecars for the [raw trades](https://data.binance.vision/data/spot/daily/trades/ADAUSDT/ADAUSDT-trades-2026-09-10.zip.CHECKSUM) and [aggregate trades](https://data.binance.vision/data/spot/daily/aggTrades/ADAUSDT/ADAUSDT-aggTrades-2026-09-10.zip.CHECKSUM). Their hashes, source URLs, schema-reference hash, analysis hash, and plotting dependencies are recorded in [provenance.json](provenance.json). The [Binance public-data README](https://github.com/binance/binance-public-data#data-information) specifies microsecond timestamps for Spot files from 2025 onward. The script rejects observations outside the requested UTC day rather than silently interpreting these timestamps as milliseconds.

## Verify that the files describe the same executions

For each aggregate, the script locates its first and last raw trade IDs and checks:

1. Every constituent ID exists and the range is contiguous.
2. Aggregate ranges cover the complete raw archive without overlap or gaps.
3. The sum of constituent quantities equals the aggregate quantity using decimal arithmetic.
4. Every constituent has the aggregate's price, buyer-maker flag, and best-match flag.
5. The aggregate timestamp is within the constituents' timestamp range.

All **35,811 aggregate ranges** pass these checks; total quantity differs by exactly **0 ADA**. Every aggregate timestamp also equals the last constituent's timestamp in this sample. These are consistency checks on the exchange's published records, not independent validation of the exchange's underlying transactions. [Reconciliation results](metrics.json)

## The first-digit signal depends on the feed

For each positive base quantity, take its first significant decimal digit. For example, `0.0247` and `24.7` both contribute to digit 2. Calculate frequencies separately over all raw rows and all aggregate rows.

{{< figure src="first_digit_distribution.png" caption="Author-computed first-digit distributions from the verified ADAUSDT archives. The Benford line is a descriptive reference, not an established null model for this market." >}}

| Leading digit | Raw count | Raw share | Aggregate count | Aggregate share |
| --- | ---: | ---: | ---: | ---: |
| 1 | 16,978 | 10.14% | 9,943 | 27.77% |
| 2 | 103,042 | 61.56% | 7,115 | 19.87% |
| 3 | 15,514 | 9.27% | 3,875 | 10.82% |
| 4 | 13,275 | 7.93% | 4,511 | 12.60% |
| 5 | 4,203 | 2.51% | 2,295 | 6.41% |
| 6 | 3,083 | 1.84% | 1,880 | 5.25% |
| 7 | 3,807 | 2.27% | 2,381 | 6.65% |
| 8 | 2,326 | 1.39% | 1,493 | 4.17% |
| 9 | 5,160 | 3.08% | 2,318 | 6.47% |

Source: `first_digit_base_quantity_distribution` in [metrics.json](metrics.json). Percentages are rounded independently.

The total variation distance between these two nine-category distributions is **0.416906**, calculated as half the sum of the absolute frequency differences. The digit-2 share falls by **41.69 percentage points** under aggregation. This direction holds in **all 24 UTC hours**, with hourly declines ranging from **29.85 to 47.59 percentage points**. None of the aggregate ranges crosses an hour boundary in this dataset, so the hourly comparisons also avoid splitting a constituent group. The full hourly counts are included in [metrics.json](metrics.json).

For a descriptive comparison with Benford frequencies, define `b(d) = log10(1 + 1/d)` and observed row frequency `p(d)`. The mean absolute deviation is `sum(abs(p(d) - b(d))) / 9`; the maximum cumulative distance is `max(abs(sum(p(i) - b(i), i=1..d)))` over digits 1–9.

| Descriptive distance from Benford | Raw trades | Aggregate trades |
| --- | ---: | ---: |
| Mean absolute deviation | 0.097666 | 0.017581 |
| Maximum cumulative distance | 0.239895 | 0.023378 |

Source: the `benford_descriptive_diagnostics` objects in [metrics.json](metrics.json), calculated with Python `Decimal` arithmetic. These are offline distances, not responses from the DN Institute API's `benfordlawtest` field. No p-values are calculated: the two feeds are dependent representations of the same executions, and this comparison does not establish Benford conformity as the appropriate null hypothesis for ADAUSDT.

## Repeated sizes and whole-unit quantities also change

The raw quantity **24.7 ADA** appears **35,747 times**, or **21.36% of raw rows**. Those fills account for only **0.6550% of total ADA quantity**. In the aggregate file, exactly 24.7 ADA appears **429 times**, or **1.20% of rows**. Grouping can absorb repeated constituent sizes into larger sums; a repeated-size alert on the raw feed is therefore measuring something different from the same alert on aggregate quantities. [Exact quantity counts and volume shares](metrics.json)

This count concentration does not identify the cause of the repeated size. The files lack account identifiers, order identifiers, and contemporaneous historical order-size constraints. They do not distinguish independently submitted orders from other possible trading or matching mechanisms.

A second diagnostic counts quantities that are exactly integral numbers of ADA, with no floating-point tolerance. Its rate rises from **18.35%** (30,714 raw rows) to **22.92%** (8,207 aggregate rows), a **4.57-percentage-point** difference. Summing fractional fills can produce whole quantities, while other groups retain fractions; the diagnostic's definition must specify whether it is applied before or after aggregation. [Whole-unit results](metrics.json)

{{< figure src="round_number_rates.png" caption="Exact whole-ADA quantities as a share of rows. The denominator and quantity per row change with aggregation; total executed ADA is conserved." >}}

## Applying the result to wash-trading surveillance

This is a methods check for indicators that may be used in wash-trading investigations. It supplies no ground-truth labels of manipulative or legitimate activity and is not a detector benchmark. The supported finding is narrower: a feed substitution changes first-digit and repeated-size statistics even after the represented executions and total quantity have been reconciled.

Before interpreting a cross-venue anomaly or a change after an ingestion upgrade:

- Record the observation unit: individual fill, aggregate trade, or reconstructed order. A similar endpoint name does not establish comparable units.
- Preserve constituent trade-ID ranges where available and reconcile them before attributing differences to missing or fabricated volume.
- Keep row-count distributions separate from volume-weighted distributions. Here, a size representing 21.36% of fills accounts for less than 1% of base quantity.
- Establish a baseline for the same feed, pair, and definition. A threshold calibrated on fills should not be transferred unchanged to aggregates.
- Investigate a signal with additional evidence rather than treating distance from Benford as a probability of misconduct.

The convenience sample is one pair on one UTC day. The 24 hourly comparisons establish persistence within that day, not generality across markets or dates. The data-product difference is directly measured; the reasons for traders' sizing choices are not.

## Reproduce the analysis

This page's directory contains both compressed source datasets and checksum sidecars under `raw/`, [analysis.py](analysis.py), [focused checks](test_analysis.py), [plotting requirements](requirements.txt), [metrics](metrics.json), and [provenance](provenance.json). The pinned dependencies require **Python 3.12 or newer**; ensure `python3` selects a compatible interpreter. From that directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest -v test_analysis.py
.venv/bin/python analysis.py
```

The analysis verifies the pinned archive hashes before reading data, uses decimal quantities throughout, and fails if the daily timestamp bounds or execution reconciliation fail. It regenerates the two figures and metrics without calling an exchange API. The figures describe observed records only; no trades, accounts, or market activity are generated by this procedure.
