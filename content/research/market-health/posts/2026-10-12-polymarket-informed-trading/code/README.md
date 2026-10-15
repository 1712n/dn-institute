# Code — Polymarket informed-trading detection

Python 3.11, dependencies in `requirements.txt` (`pip install -r requirements.txt`).

Pipeline (run from this folder, in order):

| Step | Script | Output |
|---|---|---|
| Collect all political markets + trades (parallel, resumable) | `run_collect_all.py` | `data/polymarket.duckdb` |
| Price-jump screen | `detect_surprises.py` | `surprise_markets.csv`, `surprise_substantive.csv` |
| Wallet screen: wallets that won every market, at long odds | `screen_wallets.py` | `perfect_winrate.csv`, `longshot_perfect.csv`, `wallet_seed_markets.csv` |
| Episode scoring `S = 2T+2V+P+2A+R`, fresh-wallet rule, controls, lifetime multiplier, clusters | `run_account_phase.py` | `episode_scores.csv`, `suspicious_accounts.csv`, `clusters.csv` |
| OSINT tiers per event, top suspects per event | `build_artifacts.py` | `event_tiers.csv`, `suspects_by_event.csv` |
| Figures of the write-up | `make_figures.py` | `output/figures/*.png` |

`run_account_phase.py --offline` and `screen_wallets.py --offline` use the cached API answers in
`inputs/` (`lifetime_profiles.csv` from `/positions`, `wallet_first_activity.csv` from
`/activity`) so the outputs can be rebuilt from the database alone.

`src/`: `pm_client.py` (HTTP client), `collect.py` (collection), `episode_score.py` (signal
points), `controls.py` (date-series survivorship control, OSINT tiers), `enrich.py` (lifetime
profiles, wallet age, co-occurrence clusters), `osint.py` (profile enrichment), `trace.py`
(on-chain funding via Etherscan v2, reads `ETHERSCAN_KEY` from the environment).

The public timeline of every scored event (first public signal, event type, whether the fact
existed privately before disclosure) was compiled by hand and is recorded in
`inputs/event_analysis.csv`; `src/controls.py` turns it into tiers by rule.

Tests: `pytest tests`. Tests that need the trade database are skipped without it.
