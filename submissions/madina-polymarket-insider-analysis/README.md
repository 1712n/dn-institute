# Polymarket informed-trading triage — challenge #1222

A reproducible retrospective study of the January 2026 Maduro removal market.
Start with [REPORT.md](REPORT.md). Scores prioritize manual investigation;
they are not calibrated probabilities or findings of wrongdoing.

## Reproduce

Python 3.10+; analysis and collection use the standard library only.

```sh
python3 prepare_data.py
python3 -m unittest -v
python3 analyze.py
```

`analyze.py` verifies original response hashes, cursor continuity and exact
CSV reconciliation before calculating results. It reproduces all analytical
CSVs and `results/summary.json`. The prose report is editorially prepared from
those outputs, not overwritten by the script.

The repository includes a compressed public-data snapshot in `snapshot/`.
`prepare_data.py` verifies and joins its four parts, then restores
`data/maduro` and `data/custody`, containing
the original raw responses, manifests and CSV exports retrieved on 2026-10-07.
They are public data; neither wallet keys nor credentials are included.
Do not overwrite original inputs when refreshing.

Submission for [DNI challenge #1222](https://github.com/1712n/dn-institute/issues/1222).

For a fresh collection in a separate directory:

```sh
python3 collect.py --event maduro-out-in-2025 --out fresh_maduro
python3 collect.py --event maduro-in-us-custody-by-january-31 --out fresh_custody
```

Move those directories under `data/` as `maduro` and `custody` in a separate
working copy before analysis. API history may change; fresh outputs need not
match the supplied snapshot. The initial environment could not reach the trade
API, so the candidate executed the collector on her Mac and supplied its output.

## Outputs

- `wallet_ranking.csv`: all 3,948 primary-market wallets, component values,
  eligibility reasons and ranks; excluded wallets have blank rank and score 0.
- `primary_trades.csv`: all 26,404 primary-market trade-side records with raw
  page/row references, transaction hashes and token IDs.
- `top_wallet_window_trades.csv`: all window records for the eight candidates.
- `market_coverage.csv`: snapshot coverage and verification for seven markets.
- `sensitivity_ranks.csv`, `sensitivity_summary.csv`: cutoff, weight and minimum
  notional comparisons; the late announcement scenario is deliberately contaminated.
- `duplicate_collapse_sensitivity.csv`: alternative treatment of identical
  signatures, not an assertion that repeated-looking fills are erroneous.
- `placebo_windows.csv`: seven earlier daily windows plus the event window.
- `hourly_activity.csv`: descriptive primary-market activity, not unique volume.
- `top_wallet_related_markets.csv`: in-scope earlier activity across deadlines.
- `event_timeline.csv`: sourced contextual timestamps and analytical cutoffs.
- `news_boundary_sensitivity.csv`: earlier cutoffs and 12/48-hour purchase windows.

## Audit notes

Amounts use API prices times shares, with floating-point precision; values are
rounded for presentation. This is not an accounting or realized-P&L system.
Raw records preserve maker/taker sides and may repeat within one transaction;
a transaction hash is not a unique fill identifier. No wallet identity inference
or private-data enrichment is performed. Third-party API omissions cannot be
ruled out by exhausting pagination.

