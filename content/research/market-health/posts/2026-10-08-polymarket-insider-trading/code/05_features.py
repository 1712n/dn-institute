"""Turn the downloaded trade tapes into one row per (wallet, market) and one row per market.

Every number here is computed from public Data API trades. A wallet is a Polymarket proxy
wallet, not a person.
"""
import glob
import gzip
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from importlib import import_module

scope = import_module("03_scope")

HOUR = 3600
NEAR_CERTAIN = 0.95
LEAD_WINDOW_H = 72
CHEAP = 0.5


def winner_index(market):
    prices = [float(p) for p in json.loads(market["outcomePrices"])]
    return prices.index(1.0)


def resolution_time(win_trades):
    """First hour after which the winning token trades at or above NEAR_CERTAIN for good."""
    if win_trades.empty:
        return np.nan
    h = (win_trades["timestamp"] // HOUR) * HOUR
    vwap = (win_trades["price"] * win_trades["size"]).groupby(h).sum() / win_trades["size"].groupby(h).sum()
    below = vwap[vwap < NEAR_CERTAIN]
    if below.empty:
        return float(vwap.index.min())
    return float(below.index.max() + HOUR)


def load_market(path, market):
    df = pd.read_csv(path)
    if df.empty:
        return df
    df["usd"] = df["size"] * df["price"]
    win = winner_index(market)
    df["is_win_token"] = df["outcomeIndex"] == win
    df["signed_usd"] = np.where(df["side"] == "BUY", df["usd"], -df["usd"])
    return df


def wallet_market_rows(df, market, event_slug):
    t_res = resolution_time(df[df["is_win_token"]])
    buys = df[df["side"] == "BUY"].copy()
    if buys.empty:
        return []
    buys["lead_h"] = (t_res - buys["timestamp"]) / HOUR
    rows = []
    for (wallet, is_win), g in buys.groupby(["proxyWallet", "is_win_token"]):
        cost = g["usd"].sum()
        shares = g["size"].sum()
        p = cost / shares
        rows.append({
            "wallet": wallet, "conditionId": market["conditionId"], "event": event_slug,
            "won": bool(is_win), "cost_usd": cost, "avg_price": p, "n_buys": len(g),
            "first_ts": g["timestamp"].min(), "last_ts": g["timestamp"].max(),
            "usd_cheap_pre_res": g.loc[(g["price"] <= CHEAP) & (g["lead_h"] <= LEAD_WINDOW_H)
                                       & (g["lead_h"] >= 0), "usd"].sum() if is_win else 0.0,
            "median_lead_h": float(np.average(g["lead_h"], weights=g["usd"])) if cost > 0 else np.nan,
        })
    return rows


def main(markets_path, tags_path, tradedir, out):
    tags = json.load(open(tags_path))
    universe = scope.in_scope(json.load(open(markets_path)), tags)
    manifest = json.load(open(os.path.join(tradedir, "manifest.json")))
    rows, mrows = [], []
    for m, _ in universe:
        cid = m["conditionId"]
        info = manifest.get(cid)
        if not info:
            continue
        df = load_market(os.path.join(tradedir, cid + ".csv.gz"), m)
        if df.empty:
            continue
        slug = tags[m["events"][0]["id"]]["slug"]
        rows += wallet_market_rows(df, m, slug)
        mrows.append({
            "conditionId": cid, "event": slug, "question": m["question"], "volume": m["volumeNum"],
            "kind": info["kind"], "n_trades": len(df), "median_trade_usd": df["usd"].median(),
            "p99_trade_usd": df["usd"].quantile(0.99),
            "t_res": resolution_time(df[df["is_win_token"]]), "closed": m.get("closedTime"),
        })
    pd.DataFrame(rows).to_csv(out + "_wallet_market.csv.gz", index=False)
    pd.DataFrame(mrows).to_csv(out + "_markets.csv", index=False)
    print(len(rows), "wallet-market rows,", len(mrows), "markets")


if __name__ == "__main__":
    main(*sys.argv[1:5])
