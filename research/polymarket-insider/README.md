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
taker-side fills. It creates four CSVs in `artifacts/`:

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
reported volume from $100k to $3m, and a title matching a public-policy/geopolitical
dictionary. Sports and price-direction markets are excluded. Results are sorted
by numeric reported volume and then market ID, so the scope can be reproduced.

## What the score does — and does not — say

At the trade level, the score combines: a correct outcome bought below a 50¢
implied probability (40%), entry within seven days of resolution (25%), stake size (20%), and
the price jump above the *previous* 20-fill median for that outcome (15%). At
the wallet level it combines the average five strongest signals (65%), repeated
signals across markets (20%), and the share of scoped buy notional spent on
eventual winners (15%).

The data API labels the taker side only. The script therefore does **not** claim
exact P&L or net position, infer identity from a wallet, or call a trader an
insider. In particular, a user may buy a winner and later sell it; a low-price
correct trade can be luck, research, or public information; and public wallet
labels are mutable. Review the linked transaction, the full wallet history,
public-news timeline, and any linked on-chain funding before drawing a finding.
