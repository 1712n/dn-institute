# Polymarket informed-trading screen

This folder is a public-data, reproducible *triage* of potentially informed
trading. A high score is a priority for further investigation, not an
accusation and not evidence of wrongdoing.

## Run

```bash
python3 collect_and_rank.py
```

No API key or third-party package is required. The script queries Polymarket's
public Gamma API for resolved market metadata and its public Data API for
taker-side fills. It creates five CSVs in `artifacts/`:

| File | Purpose |
| --- | --- |
| `market_selection.csv` | Pre-analysis scope and retrieval completeness per market. |
| `all_taker_trades.csv` | Raw public fills used in the calculation. |
| `candidate_trades.csv` | Trade-level flags and all component scores. |
| `wallet_ranking.csv` | Wallet-level investigation queue. |
| `lead_clusters.csv` | A market-level case card: distinguishes one crowded market event from repeat wallet behavior. |
| `checksums.sha256` | SHA-256 checksums for each generated CSV. |

The selection rule is deliberately declared before looking at wallets: resolved
binary, news-sensitive markets whose *actual resolution* falls from 2025-11-01 through 2026-05-01,
reported volume from $900k to $3m, and a title matching a public-policy/geopolitical
dictionary. Sports and price-direction markets are excluded. Results are sorted
by numeric reported volume and then market ID, so the scope can be reproduced.
Because Gamma exposes `endDate` but does not provide a `closedTime` filter, the
collector first searches monthly scheduled-date windows with a 90-day buffer,
then applies the required window to actual closure time. If a Gamma bucket
reaches the API pagination cap, the collector bisects it until it can retrieve
the complete candidate set; it fails rather than silently scoring a partial one.
If the trade API's per-window cap is reached, that entire market is marked
`incomplete_excluded` in `market_selection.csv` and is absent from all scores.

## What the score does — and does not — say

At the trade level, the score combines: a correct outcome bought below a 50¢
implied probability (40%), entry within seven days of resolution (25%), stake size (20%), and
the price jump above the *previous* 20-fill median for that outcome (15%). At
the wallet level it combines the average five strongest signals (65%), repeated
signals across markets (20%), and the share of scoped buy notional spent on
eventual winners (15%).

The price-jump component is deliberately zero until an outcome has 20 preceding
fills; it is never estimated from the current fill. A wallet becomes a
cross-market pattern only after flags in at least two distinct markets. A
single-market lead remains a lead, not an insider conclusion.

The data API labels the taker side only. The script therefore does **not** claim
exact P&L or net position, infer identity from a wallet, or call a trader an
insider. In particular, a user may buy a winner and later sell it; a low-price
correct trade can be luck, research, or public information; and public wallet
labels are mutable. Review the linked transaction, the full wallet history,
public-news timeline, and any linked on-chain funding before drawing a finding.

`all_taker_trades.csv` retains only the public fields needed to reproduce the
calculation; display names, bios and images are omitted. Every CSV string that
begins with `=`, `+`, `-` or `@` is prefixed with an apostrophe so spreadsheet
software will not execute it as a formula.
