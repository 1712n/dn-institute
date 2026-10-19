# Polymarket insider trading screen, November 2025 to April 2026

Submission for issue #1222. The report is `REPORT.md`. This file says how to rerun it and what each file is.

## Rerunning the analysis from the committed data

Python 3.12 with the packages in `code/requirements.txt`. From this folder:

```
pip install -r code/requirements.txt
python code/check_pack.py data
sh code/run_analysis.sh data
```

`check_pack.py` checks the committed data against the rules that cut it: every market closed in the window, every outcome clock recomputes to the committed `t_known`, every committed trade is inside the window and before its market's `t_known`, every wallet status recomputes, and every file matches `data/SHA256SUMS`. `run_analysis.sh` reads only committed files and rewrites every analysis output in `data/`, ending with `summary.csv`, which holds the counts the report quotes. The compressed files carry no timestamp, so a rerun gives the same bytes and the checksums still match. It takes about two minutes. `wallet_market.csv.gz` (one row per wallet and market) is rebuilt by the run and is not committed; `.gitignore` keeps it out.

## Rebuilding the data from the public APIs

These steps call public Polymarket endpoints and need no key. They write to a folder outside the repository (`RAW` below) and then cut the committed files from it.

```
python code/01_markets.py RAW/markets RAW/walks.json
python code/02_window.py RAW/markets RAW/walks.json data/markets_window.csv.xz data/markets_window_detail.csv.xz data/gamma_walks.csv data/window_counts.csv
python code/03_scope.py data/markets_window.csv.xz data/markets_window_detail.csv.xz RAW/markets_scope_pre.csv data/scope_filter_counts.csv
python code/04_trades.py RAW/markets_scope_pre.csv RAW/trades
python code/05_pack.py RAW/markets_scope_pre.csv RAW/trades data data/markets_scope.csv
python code/05b_opening.py RAW/trades data
python code/09_first_activity.py data data/wallet_first_activity.csv.gz
python code/check_known_cases.py data
```

`01_markets.py` walks the Gamma `/markets/keyset` endpoint, which has no offset cap, in end date slices plus one walk by volume. `data/gamma_walks.csv` shows each slice walk ended on an empty cursor and the volume walk at the $100,000 floor. `04_trades.py` pages the Data API `/trades` endpoint backwards in time with its `end` parameter, so each market's tape is complete. The APIs serve live data, so a rebuild months later can differ slightly from the committed files, and `check_pack.py` then reports the checksums as changed; write `data/SHA256SUMS` again with `cd data && shasum -a 256 $(ls | grep -v SHA256SUMS) > SHA256SUMS` once the new files are in place. The analysis above does not depend on this step.

## Files

Code, in the order it runs:

- `code/01_markets.py` lists every closed market on Gamma.
- `code/02_window.py` keeps markets whose `closedTime` falls in the window and counts what the scheduled end date would have got wrong.
- `code/03_scope.py` applies the scope filters and counts what each removes.
- `code/04_trades.py` downloads full trade tapes.
- `code/05_pack.py` fixes the moment each outcome became known, keeps the trades inside the window and before the outcome was known, picks the tested wallets and writes the committed tape.
- `code/05b_opening.py` records what each wallet already held in each market when the window started, for markets created before it.
- `code/06_features.py` builds one row per wallet and market.
- `code/07_population.py` builds one row per tested wallet.
- `code/08_replay_check.py` shows why a luck replay cannot be used on these markets.
- `code/09_first_activity.py` looks up each tested wallet's first Polymarket activity.
- `code/10_score.py` scores and ranks the wallets.
- `code/11_lockstep.py` finds wallets that trade in lockstep and groups them.
- `code/12_cases.py` writes the review files for the top 100.
- `code/13_control.py` ranks again with every outcome clock moved 7 and 14 days earlier.
- `code/14_known.py` places the accounts named by the press in the ranking.
- `code/15_summary.py` collects the quoted counts.
- `code/check_pack.py` checks the committed data (see above).
- `code/check_tape_walk.py` checks, on one market, that the backwards walk of `04_trades.py` returns the same trades as a plain query (needs network).
- `code/check_known_cases.py` confirms the addresses taken from profile names (needs network).
- `code/run_analysis.sh` runs the offline steps.

Data:

- `data/gamma_walks.csv`, `data/window_counts.csv`: the market walks and the window counts.
- `data/markets_window.csv.xz`: every market that closed in the window, with the fields the filters read.
- `data/markets_window_detail.csv.xz`: full details for the window markets that pass the tag and volume filters.
- `data/scope_filter_counts.csv`: markets removed by each filter.
- `data/markets_scope.csv`: the screened markets, with the four outcome clocks, `t_known` and trade counts.
- `data/market_buckets.csv.xz`: the ten-minute price windows behind the settle clock.
- `data/wallets.csv.gz`: every wallet that bought at least $5,000 in the window before the outcomes were known, with its status (tested, market maker, high frequency).
- `data/wallets_excluded_markets.csv.gz`: per market trade counts and buying of the market makers and high frequency wallets.
- `data/tape_part1.csv.xz` to `data/tape_part6.csv.xz`: every committed trade of the tested wallets. Columns: market `m` (column `m` of `markets_scope.csv`), wallet `w` (column `w` of `wallets.csv.gz`), side `B` or `S`, outcome index `o`, shares `size`, `price`, unix time `ts`.
- `data/opening_positions.csv.gz`: shares per outcome that a wallet held in a market on 1 November 2025, and their value at the last price before then.
- `data/wallet_first_activity.csv.gz`: first Polymarket activity per tested wallet, deposits included.
- `data/population.csv.gz`: one row per tested wallet.
- `data/replay_check.csv`: per ladder of "by" dates, whether a luck replay can reach the real outcome.
- `data/wallet_ranking.csv` (top 200) and `data/wallet_ranking_full.csv.gz` (all tested wallets): the ranking.
- `data/lockstep_pairs.csv.gz`, `data/lockstep_groups.csv`: linked wallets and their groups.
- `data/review_wallets.csv`, `data/review_positions.csv.gz`, `data/review_trades.csv.gz`, `data/case_price_paths.csv.gz`: the review files.
- `data/control.csv`: the earlier-day control.
- `data/known_cases.csv`, `data/known_case_recall.csv`: accounts the press named, with sources, and where the ranking puts them.
- `data/summary.csv`: the counts quoted in the report.
- `data/SHA256SUMS`: checksums of every committed data file.
