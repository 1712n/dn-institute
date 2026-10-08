"""Base rate for the fresh account signal: how new are ordinary large wallets?

Draws a random sample of non-market-maker wallets with at least MIN_COST spent and looks up each
wallet's first Polymarket activity, the same way 07_fresh.py does for the shortlist.
"""
import json
import os
import sys
import time
from importlib import import_module

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
score = import_module("06_score")
fresh = import_module("07_fresh")

SAMPLE = 300


def main(wm_path, cache_path, out):
    wm = pd.read_csv(wm_path)
    w = score.wallet_table(wm)
    pool = w[(w["cost"] >= score.MIN_COST) & ~w["market_maker"]]
    sample = pool.sample(SAMPLE, random_state=11)
    cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}
    for wallet in sample["wallet"]:
        if wallet not in cache:
            cache[wallet] = fresh.first_activity(wallet)
            time.sleep(0.1)
    json.dump(cache, open(cache_path, "w"))
    sample = sample.assign(first_activity_ts=sample["wallet"].map(cache))
    sample["days"] = (sample["first_buy_ts"] - sample["first_activity_ts"]) / 86400
    res = {"n_pool": len(pool), "n_sample": len(sample),
           "share_under_1d": float((sample["days"] < 1).mean()),
           "share_under_7d": float((sample["days"] < 7).mean()),
           "share_profitable": float((sample["pnl"] > 0).mean())}
    json.dump(res, open(out, "w"), indent=1)
    print(res)


if __name__ == "__main__":
    main(*sys.argv[1:4])
