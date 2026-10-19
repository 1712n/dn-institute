"""Score every tested wallet on four explainable signals and rank them.

early     dollars put on the eventual winner at a price of 0.30 or less in the 7 days before
          t_known and still held then, on a log scale: $1,000 gives 0.15, $100,000 or more 1.
clean     in the wallet's largest event, the share of its buying that went to the winning
          side. A wallet that also bought the losing date markets or the losing token of the
          same event scores lower, because spreading bets across outcomes is what a hedger or
          a guesser does, not someone who knows the answer.
focus     share of the wallet's money in its largest event, divided by the square root of the
          number of events it traded.
fresh     1 when the wallet's first Polymarket activity came on the day of its first buy here,
          falling to 0 at 30 days (first activity from 09_first_activity.py).

score = 100 * (0.4 early + 0.2 clean + 0.2 focus + 0.2 fresh)

The weights were set before the ranking was compared with any named account and are not fitted.
The first REVIEW wallets of the ranking are the review list that 12_cases.py writes out.
"""
import os
import sys

import numpy as np
import pandas as pd

WEIGHTS = {"s_early": 0.4, "s_clean": 0.2, "s_focus": 0.2, "s_fresh": 0.2}
REVIEW = 100
COLS = ["rank", "wallet", "score", "s_early", "s_clean", "s_focus", "s_fresh", "pnl", "cost", "sell_usd",
        "n_markets", "n_events", "top_event", "top_event_cost", "top_event_pnl", "top_event_markets",
        "top_event_losing_markets", "clean_share", "focus_share", "early_longshot_usd",
        "days_since_first_activity", "first_buy_ts"]


def table(wm):
    """One row per wallet with the inputs of the four signals."""
    ev = wm.groupby(["w", "event_id"]).agg(cost=("cost", "sum"), win=("win_buy_usd", "sum"),
                                           lose=("lose_buy_usd", "sum"), pnl=("pnl", "sum"),
                                           n_mk=("m", "nunique")).reset_index()
    ev = ev.sort_values(["w", "cost", "event_id"], ascending=[True, False, True])
    top = ev.drop_duplicates("w").set_index("w")
    lose_mk = wm[wm["lose_buy_usd"] > 0].groupby(["w", "event_id"])["m"].nunique()
    g = wm.groupby("w")
    w = pd.DataFrame({"cost": g["cost"].sum(), "pnl": g["pnl"].sum(), "n_markets": g["m"].nunique(),
                      "n_events": g["event_id"].nunique(), "sell_usd": g["sell_usd_0"].sum() + g["sell_usd_1"].sum(),
                      "early_longshot_usd": g["early_longshot_usd"].sum(), "first_buy_ts": g["first_ts"].min()})
    w["top_event_id"] = top["event_id"]
    w["top_event_cost"] = top["cost"]
    w["top_event_pnl"] = top["pnl"]
    w["top_event_markets"] = top["n_mk"]
    w["top_event_losing_markets"] = [lose_mk.get((i, e), 0) for i, e in zip(w.index, w["top_event_id"])]
    w["clean_share"] = (top["win"] / (top["win"] + top["lose"]).replace(0, np.nan)).fillna(0.0)
    w["focus_share"] = w["top_event_cost"] / w["cost"]
    return w.reset_index()


def score(w, first_activity):
    """Add the four signals, the score and the rank. first_activity has columns w, first_activity_ts."""
    w = w.merge(first_activity[["w", "first_activity_ts"]], on="w", how="left")
    w["days_since_first_activity"] = (w["first_buy_ts"] - w["first_activity_ts"]) / 86400
    w["s_early"] = (np.log10(1 + w["early_longshot_usd"] / 1000) / 2).clip(0, 1)
    w["s_clean"] = w["clean_share"].clip(0, 1)
    w["s_focus"] = (w["focus_share"] / np.sqrt(w["n_events"].clip(lower=1))).clip(0, 1)
    w["s_fresh"] = (1 - w["days_since_first_activity"] / 30).clip(0, 1).fillna(0.0)
    w["score"] = 100 * sum(w[k] * v for k, v in WEIGHTS.items())
    w = w.sort_values(["score", "w"], ascending=[False, True]).reset_index(drop=True)
    w.insert(0, "rank", np.arange(1, len(w) + 1))
    return w


def ranking(wm, wallets, first_activity, scope):
    """The full ranking with wallet addresses and the slug of each wallet's largest event."""
    fa = first_activity.merge(wallets[["w", "wallet"]].dropna(), on="wallet")
    r = score(table(wm), fa).merge(wallets[["w", "wallet"]], on="w", how="left")
    ev = scope.drop_duplicates("event_id").set_index("event_id")["event_slug"]
    r["top_event"] = r["top_event_id"].map(ev)
    return r


def main(datadir, out_full, out_top):
    wm = pd.read_csv(os.path.join(datadir, "wallet_market.csv.gz"), dtype={"event_id": str})
    wallets = pd.read_csv(os.path.join(datadir, "wallets.csv.gz"))
    fa = pd.read_csv(os.path.join(datadir, "wallet_first_activity.csv.gz"))
    scope = pd.read_csv(os.path.join(datadir, "markets_scope.csv"), dtype={"event_id": str})
    scope["event_id"] = scope["event_id"].fillna("m" + scope["m"].astype(str))
    r = ranking(wm, wallets, fa, scope)
    r[COLS].round(4).to_csv(out_full, index=False, compression={"method": "gzip", "mtime": 0})
    r[COLS].head(200).round(4).to_csv(out_top, index=False)
    print(len(r), "ranked")
    print(r[COLS[:13]].head(25).to_string())


if __name__ == "__main__":
    main(*sys.argv[1:4])
