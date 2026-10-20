# Code: Polymarket informed-trading detection

Python 3.11, dependencies in `requirements.txt` (`pip install -r requirements.txt`).

## Quick rebuild from the committed data

From this folder:

```
python build_db.py
python detect_surprises.py
python screen_wallets.py --offline
python run_account_phase.py --offline
python build_artifacts.py
python make_figures.py
```

`build_db.py` reads the Parquet files in `../data/tape/` and writes `data/polymarket.duckdb` (about 1.1 GB). The scripts write to `output/`; the CSV files there match `../data/` and the figures in `output/figures/` match `../figures/` byte for byte. The committed figures were drawn with matplotlib 3.11.2; another version draws the same charts, but the PNG bytes can differ.

## Pipeline

| Step | Script | Output |
|---|---|---|
| Collect all political markets and trades from the API (parallel, resumable) | `run_collect_all.py` | `data/polymarket.duckdb` |
| Build the same database from the committed Parquet files | `build_db.py` | `data/polymarket.duckdb` |
| Price-jump screen | `detect_surprises.py` | `surprise_markets.csv`, `surprise_substantive.csv` |
| Wallet screen: wallets that won every market, at long odds (won = ahead on the winning outcome) | `screen_wallets.py` | `perfect_winrate.csv`, `longshot_perfect.csv`, `wallet_seed_markets.csv` |
| Episode scoring `S = 2T+2V+P+2A+R`, fresh-wallet rule, controls, lifetime multiplier, clusters | `run_account_phase.py` | `episode_scores.csv`, `suspicious_accounts.csv`, `clusters.csv` |
| OSINT tiers per event, top suspects per event | `build_artifacts.py` | `event_tiers.csv`, `suspects_by_event.csv` |
| Figures of the write-up | `make_figures.py` | `output/figures/*.png` |

Profit columns: `episode_pnl` is what the pre-jump buys of the winner pay if held to resolution; `realized_pnl` counts winner shares the wallet sold after its first buy at their sale price (up to the shares bought) and the rest at $1. Wallets are ranked by the number of flagged markets, then by `tot_realized_pnl`.

`run_account_phase.py --offline` and `screen_wallets.py --offline` use the cached API answers in `inputs/` (`lifetime_profiles.csv` from `/positions`, `wallet_first_activity.csv` from `/activity`) so the outputs can be rebuilt from the trade data alone.

`src/`: `pm_client.py` (HTTP client), `collect.py` (collection), `tape.py` (the database as Parquet files and back), `episode_score.py` (signal points), `controls.py` (date-series survivorship control, OSINT tiers), `enrich.py` (lifetime profiles, wallet age, co-occurrence clusters), `osint.py` (profile enrichment). `trace.py` is an optional helper for looking up inbound transfers on Polygon via Etherscan v2 (needs a free `ETHERSCAN_KEY`); no pipeline step calls it and no output depends on it.

The public timeline of every scored event (first public signal, event type, whether the fact existed privately before disclosure) was compiled by hand and is recorded in `inputs/event_analysis.csv`, with a `source_url` for every non-public event; `src/controls.py` turns it into tiers by rule.

## Trade data

`../data/tape/` holds the collected snapshot behind the write-up: 15,604 markets, 13.2M trades and 734k wallets in five Parquet files (154 MB in total, none over 50 MB). `pack_tape.py` writes them from the database and `build_db.py` reads them back. Wallet addresses and profiles are stored once in `wallets.parquet`; prices and sizes are stored as integers, which restores the API values exactly. Transaction hashes are kept only where the analysis uses them, to order trades of one market made in the same second, and cut to their first 8 hex digits. `../data/tape/SHA256SUMS` lists the checksums of the five files.

A fresh collection with `run_collect_all.py` can differ slightly from the snapshot: the API serves the current state of each market and only its newest ~10k trades. The database the snapshot was taken from had this checksum:

```
sha256  9f3f53a35abe29901234a816cddbff72ab52e2d9a6ba954234ada0ffb8b5e5c7  polymarket.duckdb
```

Point the scripts at another database with `PM_DB_PATH`, and `build_db.py` at another folder of Parquet files with `PM_TAPE_DIR`.

Tests: `pytest tests`. Tests that need the trade database are skipped until `build_db.py` has been run.
