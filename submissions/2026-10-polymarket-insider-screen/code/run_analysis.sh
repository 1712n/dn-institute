#!/bin/sh
# Rebuild every analysis output from the committed data. Usage: sh code/run_analysis.sh [data_dir]
set -e
D="${1:-data}"
C="$(dirname "$0")"
python "$C/03_scope.py" "$D/markets_window.csv.xz" "$D/markets_window_detail.csv.xz" "$D/markets_scope.csv" "$D/scope_filter_counts.csv"
python "$C/06_features.py" "$D" "$D/wallet_market.csv.gz"
python "$C/07_population.py" "$D/wallet_market.csv.gz" "$D/population.csv.gz"
python "$C/08_replay_check.py" "$D" "$D/replay_check.csv"
python "$C/10_score.py" "$D" "$D/wallet_ranking_full.csv.gz" "$D/wallet_ranking.csv"
python "$C/11_lockstep.py" "$D" "$D"
python "$C/12_cases.py" "$D" "$D"
python "$C/13_control.py" "$D" "$D/control.csv"
python "$C/14_known.py" "$D" "$D/known_case_recall.csv"
python "$C/15_summary.py" "$D" "$D/summary.csv"
