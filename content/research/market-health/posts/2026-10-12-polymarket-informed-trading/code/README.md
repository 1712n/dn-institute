# Code — Polymarket informed-trading detection

Python 3.11, dependencies in `requirements.txt` (`pip install -r requirements.txt`).

Pipeline (run from this folder, in order):

| Step | Script | Output |
|---|---|---|
| Collect all political markets + trades (parallel, resumable) | `run_collect_all.py` | `data/polymarket.duckdb` |
| Price-jump screen | `detect_surprises.py` | `surprise_markets.csv`, `surprise_substantive.csv` |
| Wallet screen: wallets that won every market, at long odds (won = ahead on the winning outcome) | `screen_wallets.py` | `perfect_winrate.csv`, `longshot_perfect.csv`, `wallet_seed_markets.csv` |
| Episode scoring `S = 2T+2V+P+2A+R`, fresh-wallet rule, controls, lifetime multiplier, clusters | `run_account_phase.py` | `episode_scores.csv`, `suspicious_accounts.csv`, `clusters.csv` |
| OSINT tiers per event, top suspects per event | `build_artifacts.py` | `event_tiers.csv`, `suspects_by_event.csv` |
| Figures of the write-up | `make_figures.py` | `output/figures/*.png` |

Profit columns: `episode_pnl` is what the pre-jump buys of the winner pay if held to
resolution; `realized_pnl` counts winner shares the wallet sold after its first buy at their sale
price (up to the shares bought) and the rest at $1. Wallets are ranked by the number of flagged
markets, then by `tot_realized_pnl`.

`run_account_phase.py --offline` and `screen_wallets.py --offline` use the cached API answers in
`inputs/` (`lifetime_profiles.csv` from `/positions`, `wallet_first_activity.csv` from
`/activity`) so the outputs can be rebuilt from the database alone.

`src/`: `pm_client.py` (HTTP client), `collect.py` (collection), `episode_score.py` (signal
points), `controls.py` (date-series survivorship control, OSINT tiers), `enrich.py` (lifetime
profiles, wallet age, co-occurrence clusters), `osint.py` (profile enrichment). `trace.py` is an
optional helper for looking up inbound transfers on Polygon via Etherscan v2 (needs a free
`ETHERSCAN_KEY`); no pipeline step calls it and no output depends on it.

The public timeline of every scored event (first public signal, event type, whether the fact
existed privately before disclosure) was compiled by hand and is recorded in
`inputs/event_analysis.csv`, with a `source_url` for every non-public event;
`src/controls.py` turns it into tiers by rule.

## Trade database

The DuckDB file (`data/polymarket.duckdb`, ~1.1 GB: 15,604 markets, 13.2M trades) is too large
to commit. `run_collect_all.py` rebuilds it from the public API. The API serves the current
state of each market and its newest ~10k trades, so a rebuild made later can differ slightly
from the snapshot used for the post:

```
sha256  9f3f53a35abe29901234a816cddbff72ab52e2d9a6ba954234ada0ffb8b5e5c7  polymarket.duckdb
```

Point the scripts at another copy with `PM_DB_PATH`.

Tests: `pytest tests`. Tests that need the trade database are skipped without it.
