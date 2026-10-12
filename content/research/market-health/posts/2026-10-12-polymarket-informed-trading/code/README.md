# Code — Polymarket informed-trading detection

Python 3.11, dependencies in `requirements.txt` (`pip install -r requirements.txt`).

Pipeline:

| Step | Script | Output |
|---|---|---|
| Collect all political markets + trades (parallel, resumable) | `run_collect_all.py` | `data/polymarket.duckdb` |
| Detect surprise markets (resolution-jump) | `detect_surprises.py` | `surprise_markets.csv`, `surprise_substantive.csv` |
| Episode scoring `S = 2T+2V+P+2A+R` + lifetime multiplier + clusters | `run_account_phase.py` | `episode_scores.csv`, `suspicious_accounts.csv`, `clusters.csv`, `suspects_by_event.csv` |

`src/`: `pm_client.py` (HTTP client), `collect.py` (collection), `episode_score.py` (heuristic
components), `enrich.py` (lifetime + co-occurrence), `osint.py` (profile enrichment),
`trace.py` (on-chain funding via Etherscan v2, reads `ETHERSCAN_KEY` from the environment).
`features.py` / `scoring.py` / `pipeline.py` are an earlier focused-slice variant kept for reference.

OSINT event verification (public-news timeline) was done manually and is recorded in
`data/event_analysis.csv`.
