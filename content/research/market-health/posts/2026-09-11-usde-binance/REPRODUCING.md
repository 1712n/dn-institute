# Reproduction notes

This bundle reconstructs public Binance spot executions on fixed historical dates. It is an original market-health study, with no live exchange connection, account access, or order submission.

## Environment and commands

The numerical pipeline uses Python's standard library and `curl`. Python 3.12 is recommended for the complete workflow, including the pinned plotting packages. Install plotting requirements in a virtual environment if desired.

```sh
python3 fetch_data.py
python3 analyze.py
python3 -m pip install -r requirements.txt
python3 plot.py
```

`fetch_data.py` downloads 18 aggregate-trade archives (two pairs, nine days) plus four event-day minute-bar archives, 22 ZIP files totaling 3,513,748 compressed bytes in this snapshot. Every archive has a corresponding exchange-published SHA-256 checksum. Existing local archives are reused only after verification; a mismatching archive stops the run. `source_manifest.json` records the verified snapshot. Its check timestamp changes when the download check is rerun.

The `raw/` directory is a download cache and is not required in the contribution because the source URLs, published checksums and fetcher reproduce it. The numerical outputs are included for offline inspection; original archives are required to rerun the reconstruction.

## Output map

| File                              | Role                                                                            |
| --------------------------------- | ------------------------------------------------------------------------------- |
| `source_manifest.json`            | URL, SHA-256, ZIP member, size and source date for each archive                 |
| `results.json`                    | Key findings, input validation and trade-to-kline comparison                    |
| `daily_summary.csv`               | Both USDe pairs over the nine source days                                       |
| `minute_metrics.csv`              | Observed trade minutes, with OHLC, volume, VWAP and aggressor shares            |
| `phase_summary.csv`               | Four event-day reference windows, with explicit half-open boundaries            |
| `threshold_summary.csv`           | Execution-weighted price-threshold totals and observed first/last crossings     |
| `deepest_executions.csv`          | All 129 event-day USDE/USDT aggregate records priced at or below 0.66           |
| `quote_comparison.csv`            | Matched-minute quote conversion and relative execution-price gap                |
| `quote_gap_sensitivity.csv`       | Same-minute gap sensitivity to minimum volume in both USDe markets              |
| `same_second_comparison_2146.csv` | Matched-second reconstruction for the exploratory 21:46 minute                  |
| `matched_clock_windows.csv`       | Nine daily observations of the identical 21:00–23:00 UTC window                 |
| `control_minutes.csv`             | Event-day USDC/USDT and BTC/USDT bars; only USDC is used in quote normalization |

BTC control data are retained as market-context input; the article does not derive a market-wide causal ordering from them. Removing that input would not change the reported USDe calculations.

## Checks actually performed

- Published SHA-256 agreement and ZIP CRC validation for 22 archives.
- 221,010 aggregate records checked for positive finite price/quantity, valid maker flags, strictly increasing aggregate IDs, nondecreasing timestamps within the source day and nonoverlapping underlying trade-ID ranges.
- Zero gaps in aggregate IDs within each of the 18 daily trade archives.
- Both event-day USDe reconstructions compared with 1,440 official one-minute bars each. Observed OHLC, underlying trade counts, base volume, quote notional, taker-buy base volume and taker-buy quote volume agree within the stated numerical tolerance. No-trade minutes must agree on zero volume and count; carried-forward OHLC in such bars is not used in the trade-derived series.
- No interpolation, forward-filling, ownership inference or liquidation labeling.
- Three Matplotlib figures visually inspected at their exported dimensions.

The comparison uses two products from the same exchange's data publication system. It validates parsing and aggregation, not the completeness or truth of the exchange's original reporting. The same-second comparison remains a comparison of executions inside time bins; it does not supply executable spreads or order-book depth.

## Selection and interpretation

The announced 21:36–22:16 UTC interval is an external reference. The 21:44–21:54 recovery interval and the 21:46 same-second investigation were selected after inspecting the event. Volume thresholds are presented as sensitivity checks, not optimized classification parameters. Seven preceding clock-matched windows provide descriptive context; no independence assumption or population p-value is claimed.

Public records do not identify beneficial owners, account balances, order cancellations, passive-book replenishment, collateral-index updates or liquidation causes. This contribution does not label a participant as a manipulator or claim that an observed difference could have been profitably traded.
