"""Polymarket's own realized profit for the ranked wallets, from the Data API /closed-positions.

Gives a third profit figure next to the held model (06_score.py) and the cash flow count
(11_crosscheck.py), and the cost Polymarket records per position, which shows how much of each
wallet's buying the downloaded trade tape covers. Only positions in the scoped markets count.
Also records each wallet's public profile name and creation date.
"""
import json
import os
import sys
import time

import pandas as pd
import requests

S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0"
PAGE = 50


def closed_positions(wallet):
    rows, off = [], 0
    while True:
        for attempt in range(6):
            r = S.get("https://data-api.polymarket.com/closed-positions",
                      params={"user": wallet, "limit": PAGE, "offset": off}, timeout=60)
            if r.status_code == 200:
                break
            time.sleep(2 ** attempt)
        r.raise_for_status()
        page = r.json()
        rows += page
        if len(page) < PAGE:
            return rows
        off += PAGE


def profile(wallet):
    r = S.get("https://gamma-api.polymarket.com/public-profile", params={"address": wallet}, timeout=60)
    if r.status_code != 200:
        return {}
    j = r.json()
    return {"pseudonym": j.get("pseudonym"), "created_at": j.get("createdAt")}


def main(ranking_path, markets_path, cache_path, out):
    rank = pd.read_csv(ranking_path)
    scoped = set(pd.read_csv(markets_path)["conditionId"])
    cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}
    for wallet in rank["wallet"]:
        if wallet not in cache:
            cache[wallet] = closed_positions(wallet)
            json.dump(cache, open(cache_path, "w"))
    rows = []
    for wallet in rank["wallet"]:
        pos = [p for p in cache[wallet] if p["conditionId"] in scoped]
        rows.append({"wallet": wallet,
                     "pm_realized_pnl": sum(p["realizedPnl"] for p in pos),
                     "pm_cost": sum(p["totalBought"] * p["avgPrice"] for p in pos),
                     "pm_positions": len(pos),
                     "pm_realized_pnl_all_markets": sum(p["realizedPnl"] for p in cache[wallet]),
                     **profile(wallet)})
    t = rank.merge(pd.DataFrame(rows), on="wallet", how="left")
    created = (pd.to_datetime(t["created_at"], utc=True) - pd.Timestamp(0, tz="UTC")).dt.total_seconds()
    t["days_since_profile_created"] = (t["first_buy_ts"] - created) / 86400
    t["tape_cover"] = t["cost"] / t["pm_cost"]
    t.round(4).to_csv(out, index=False)
    print("held", round(t["pnl"].sum()), "cashflow", round(t["cashflow_pnl"].sum()),
          "polymarket", round(t["pm_realized_pnl"].sum()))
    print("pm pnl <= 0:", int((t["pm_realized_pnl"] <= 0).sum()), "median tape cover", round(t["tape_cover"].median(), 3))


if __name__ == "__main__":
    main(*sys.argv[1:5])
