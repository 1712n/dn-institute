"""Look up when each shortlisted wallet first appeared on Polymarket (Data API activity, oldest first)."""
import json
import os
import sys
import time

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(__file__))
from importlib import import_module

score = import_module("06_score")

S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0"
SHORTLIST = 400


def first_activity(wallet):
    for attempt in range(6):
        r = S.get("https://data-api.polymarket.com/activity",
                  params={"user": wallet, "limit": 1, "sortDirection": "ASC"}, timeout=60)
        if r.status_code == 200:
            rows = r.json()
            return rows[0]["timestamp"] if rows else None
        time.sleep(2 ** attempt)
    r.raise_for_status()


def main(wm_path, cache_path, out):
    wm = pd.read_csv(wm_path)
    w = score.wallet_table(wm)
    short = score.rank(w).head(SHORTLIST)
    cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}
    for i, wallet in enumerate(short["wallet"]):
        if wallet not in cache:
            cache[wallet] = first_activity(wallet)
            if i % 25 == 0:
                json.dump(cache, open(cache_path, "w"))
                print(i, flush=True)
            time.sleep(0.1)
    json.dump(cache, open(cache_path, "w"))
    first = pd.Series(cache, name="first_activity_ts").rename_axis("wallet").reset_index()
    t = short[["wallet", "first_buy_ts"]].merge(first, on="wallet")
    t["days_since_first_activity"] = (t["first_buy_ts"] - t["first_activity_ts"]) / 86400
    t[["wallet", "first_activity_ts", "days_since_first_activity"]].to_csv(out, index=False)


if __name__ == "__main__":
    main(*sys.argv[1:4])
