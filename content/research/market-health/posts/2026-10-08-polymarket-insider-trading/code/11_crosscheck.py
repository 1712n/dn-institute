"""Cash-flow profit for the ranked wallets, computed separately from the buy-only model in 06_score.py.

Per wallet and market: profit = sells - buys + (winning-token shares held at resolution) * 1, where
held shares are buys minus sells per token. Shares that arrive without a trade (token splits,
transfers) make this figure too high; trades missing from the capped tapes make it unreliable
either way, so it is reported beside the model profit.
"""
import glob
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from importlib import import_module

feat = import_module("05_features")


def main(ranking_path, markets_path, tradedir, out):
    rank = pd.read_csv(ranking_path)
    wallets = set(rank["wallet"])
    markets = {m["conditionId"]: m for m in json.load(open(markets_path))}
    rows = []
    for path in glob.glob(os.path.join(tradedir, "*.csv.gz")):
        cid = os.path.basename(path)[: -len(".csv.gz")]
        m = markets.get(cid)
        if m is None:
            continue
        df = pd.read_csv(path)
        df = df[df["proxyWallet"].isin(wallets)]
        if df.empty:
            continue
        win = feat.winner_index(m)
        df["usd"] = df["size"] * df["price"]
        df["sh"] = df["size"].where(df["side"] == "BUY", -df["size"])
        for wallet, g in df.groupby("proxyWallet"):
            buys = g.loc[g["side"] == "BUY", "usd"].sum()
            sells = g.loc[g["side"] == "SELL", "usd"].sum()
            held_win = g.loc[g["outcomeIndex"] == win, "sh"].sum()
            rows.append({"wallet": wallet, "cashflow_pnl": sells - buys + held_win, "buys": buys, "sells": sells})
    cf = pd.DataFrame(rows).groupby("wallet").sum().reset_index()
    t = rank.merge(cf[["wallet", "cashflow_pnl", "sells"]], on="wallet", how="left")
    t["sell_share"] = t["sells"] / t["cost"]
    t.round(4).to_csv(out, index=False)
    print("wallets", len(t), "model pnl", round(t["pnl"].sum()), "cashflow pnl", round(t["cashflow_pnl"].sum()))
    print("sell_share<0.1:", int((t["sell_share"] < 0.1).sum()), " cashflow<=0:", int((t["cashflow_pnl"] <= 0).sum()))


if __name__ == "__main__":
    main(*sys.argv[1:5])
