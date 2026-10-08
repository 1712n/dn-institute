# Rebuilding the data

Python 3.12 with requests, pandas, numpy and matplotlib. Every step reads public Polymarket endpoints or the files the step before it wrote. Run from the folder that holds `code/`.

```bash
python code/01_markets.py raw/markets.json
python code/02_event_tags.py raw/markets.json raw/event_tags.json
python code/04_trades.py raw/markets.json raw/event_tags.json raw/trades
python code/05_features.py raw/markets.json raw/event_tags.json raw/trades data/pm
python code/06_score.py data/pm_wallet_market.csv.gz
python code/07_fresh.py data/pm_wallet_market.csv.gz raw/fresh_cache.json data/pm_fresh.csv
python code/08_null.py data/pm_wallet_market.csv.gz data/pm_null.csv
python code/09_outputs.py data/pm_wallet_market.csv.gz data/pm_markets.csv data/pm_fresh.csv data/pm_null.csv out
python code/10_baseline.py data/pm_wallet_market.csv.gz raw/fresh_cache.json out/baseline.json
python code/11_crosscheck.py out/wallet_ranking.csv raw/markets.json raw/trades out/wallet_ranking_cashflow.csv
python code/12_polymarket_pnl.py out/wallet_ranking_cashflow.csv out/markets_scope.csv raw/closed_cache.json out/wallet_ranking_pm.csv
```

`03_scope.py` is imported by the others. `04_trades.py` is the slow step and resumes from `raw/trades/manifest.json`. The trade tapes (about 140 MB) are not committed. Results from a later run can differ slightly: the APIs return live data and the null and baseline use fixed seeds over that data.
