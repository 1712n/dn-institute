"""Merge the Gamma walks, show they were complete, and keep markets that closed in the window.

The window is applied to closedTime, the moment Gamma records the market as closed, not to the
scheduled endDate. The output keeps every market that closed in [2025-11-01, 2026-05-01), and
the counts table shows what a filter on endDate would have let in or left out. Files are streamed because the walks hold several million markets.

Two files are written for the window: a slim one with every market and only the fields the
scope filters read, and a detailed one for the markets that pass the filters of 03_scope.py
that the slim file can decide, the only ones that can end up in scope.
"""
import glob
import gzip
import importlib.util
import json
import os
import sys
from collections import Counter

import pandas as pd

_spec = importlib.util.spec_from_file_location("scope", os.path.join(os.path.dirname(__file__), "03_scope.py"))
scope = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(scope)

LO = pd.Timestamp("2025-11-01", tz="UTC")
HI = pd.Timestamp("2026-05-01", tz="UTC")
SLIM = ["id", "closed_ts", "volumeNum", "outcomePrices", "sportsMarketType", "tags"]
COLS = ["id", "conditionId", "event_id", "event_slug", "event_title", "question", "groupItemTitle",
        "createdAt", "endDate", "closedTime", "umaEndDate", "volumeNum", "outcomes", "outcomePrices",
        "negRisk", "sportsMarketType", "umaResolutionStatus", "tags"]


def ts(s):
    if not s:
        return None
    try:
        return pd.Timestamp(s).tz_convert("UTC") if pd.Timestamp(s).tzinfo else pd.Timestamp(s, tz="UTC")
    except (ValueError, TypeError):
        return None


def main(walk_dir, walk_log, out_slim, out_detail, out_walks, out_counts):
    paths = sorted(p for p in glob.glob(os.path.join(walk_dir, "*.jsonl.gz")) if "by_volume" not in p)
    paths.append(os.path.join(walk_dir, "by_volume.jsonl.gz"))
    seen, c, keep = set(), Counter(), []
    for path in paths:
        only_vol = "by_volume" in path
        with gzip.open(path, "rt") as f:
            for line in f:
                c["walk_rows"] += 1
                m = json.loads(line)
                if m["id"] in seen:
                    continue
                seen.add(m["id"])
                closed, end, uma = ts(m["closedTime"]), ts(m["endDate"]), ts(m["umaEndDate"])
                in_win = closed is not None and LO <= closed < HI
                end_in = end is not None and LO <= end < HI
                c["unique_closed_markets"] += 1
                c["found_only_by_volume_walk"] += only_vol
                c["found_only_by_volume_walk_no_endDate"] += only_vol and end is None
                c["no_closedTime"] += closed is None
                c["closed_before_window"] += closed is not None and closed < LO
                c["closed_after_window"] += closed is not None and closed >= HI
                c["closed_in_window"] += in_win
                c["closed_in_window_found_only_by_volume_walk"] += in_win and only_vol
                c["endDate_in_window"] += end_in
                c["endDate_in_window_but_closed_outside"] += end_in and not in_win
                c["closed_in_window_but_endDate_outside_or_missing"] += in_win and not end_in
                c["closed_in_window_no_endDate"] += in_win and end is None
                c["closed_in_window_umaEndDate_missing"] += in_win and uma is None
                c["closed_in_window_umaEndDate_outside"] += in_win and uma is not None and not (LO <= uma < HI)
                if in_win:
                    row = {k: m.get(k) for k in COLS}
                    row["tags"] = "|".join(m.get("tags") or [])
                    row["closed_ts"] = int(closed.timestamp())
                    keep.append(row)
    walks = pd.DataFrame(json.load(open(walk_log)))
    walks.to_csv(out_walks, index=False)
    c["walks_total"] = len(walks)
    c["walks_complete"] = int(walks["walk_complete"].sum())
    order = ["walk_rows", "walks_total", "walks_complete", "unique_closed_markets", "found_only_by_volume_walk",
             "found_only_by_volume_walk_no_endDate", "no_closedTime", "closed_before_window", "closed_in_window",
             "closed_after_window", "closed_in_window_found_only_by_volume_walk", "endDate_in_window",
             "endDate_in_window_but_closed_outside", "closed_in_window_but_endDate_outside_or_missing",
             "closed_in_window_no_endDate", "closed_in_window_umaEndDate_missing", "closed_in_window_umaEndDate_outside"]
    pd.DataFrame([(k, int(c[k])) for k in order], columns=["count", "value"]).to_csv(out_counts, index=False)
    w = pd.DataFrame(keep)
    w = w.sort_values("id", key=lambda s: s.astype(int))
    slim = w[SLIM].copy()
    slim["sportsMarketType"] = slim["sportsMarketType"].notna().astype(int)
    slim["volumeNum"] = pd.to_numeric(slim["volumeNum"]).round(2)
    slim.to_csv(out_slim, index=False)
    kept, _ = scope.apply(slim)
    w.loc[w["id"].isin(set(kept["id"])), COLS].to_csv(out_detail, index=False)
    for k in order:
        print(k, int(c[k]))


if __name__ == "__main__":
    main(*sys.argv[1:7])
