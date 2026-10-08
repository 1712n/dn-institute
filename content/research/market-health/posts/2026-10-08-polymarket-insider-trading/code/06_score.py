"""Score wallets on four explainable signals and rank them.

edge        luck-adjusted profit. Buying at price p wins 1/p - 1 per dollar with probability p, so
            a bet of C dollars has mean zero and variance C^2 (1-p)/p if prices are fair. A wallet's
            z is total profit over the square root of total variance. Markets of one event are
            treated as perfectly correlated, so an event's standard deviation is the sum of its
            markets' standard deviations; events are treated as independent.
early_cheap dollars bought at 0.50 or below on the winning side within 72 hours before the winning
            token first settles above 0.95 for good.
focus       share of the wallet's dollars in its single largest event, and how few events it traded.
fresh       days between the wallet's first activity anywhere on Polymarket and its first buy in
            the scoped markets (filled in for the shortlist only, see 07_fresh.py).

Wallets that buy both sides of a market with comparable size are labelled market makers and
kept out of the ranking.
"""
import sys

import numpy as np
import pandas as pd

MM_RATIO = 0.3
MIN_COST = 10_000
MIN_Z = 2.0


def wallet_table(wm):
    wm = wm.copy()
    wm["pnl"] = np.where(wm["won"], wm["cost_usd"] * (1 / wm["avg_price"] - 1), -wm["cost_usd"])
    wm["var"] = wm["cost_usd"] ** 2 * (1 - wm["avg_price"]) / wm["avg_price"]

    side = wm.pivot_table(index=["wallet", "conditionId"], columns="won", values="cost_usd",
                          aggfunc="sum", fill_value=0)
    side.columns = ["lose_cost", "win_cost"][: len(side.columns)] if len(side.columns) == 2 else side.columns
    side["two_sided"] = np.minimum(side.get("win_cost", 0), side.get("lose_cost", 0)) / np.maximum(
        side.get("win_cost", 0) + side.get("lose_cost", 0), 1e-9) * 2
    mm = side.groupby("wallet")["two_sided"].mean().rename("two_sided_mean")

    wm["sd"] = np.sqrt(wm["var"])
    ev = wm.groupby(["wallet", "event"]).agg(pnl=("pnl", "sum"), sd=("sd", "sum"),
                                              cost=("cost_usd", "sum")).reset_index()
    ev["var"] = ev["sd"] ** 2
    cheap_hits = wm[wm["won"] & (wm["avg_price"] <= 0.35) & (wm["cost_usd"] >= 1000)]
    cheap_hits = cheap_hits.groupby("wallet")["event"].nunique().rename("cheap_winning_events")

    w = ev.groupby("wallet").agg(pnl=("pnl", "sum"), var=("var", "sum"), cost=("cost", "sum"),
                                 n_events=("event", "nunique"), top_event_cost=("cost", "max"))
    w["z_edge"] = w["pnl"] / np.sqrt(w["var"].clip(lower=1e-9))
    w["focus_share"] = w["top_event_cost"] / w["cost"]
    top_event = ev.loc[ev.groupby("wallet")["cost"].idxmax()].set_index("wallet")["event"].rename("top_event")
    early = wm.groupby("wallet")["usd_cheap_pre_res"].sum().rename("early_cheap_usd")
    first = wm.groupby("wallet")["first_ts"].min().rename("first_buy_ts")
    w = w.join([mm, cheap_hits, top_event, early, first]).fillna({"cheap_winning_events": 0})
    w["market_maker"] = w["two_sided_mean"] > MM_RATIO
    return w.reset_index()


def components(w):
    a = ((w["z_edge"] - 2) / 6).clip(0, 1)
    b = (np.log10(1 + w["early_cheap_usd"] / 1000) / np.log10(101)).clip(0, 1)
    c = (w["focus_share"].clip(0, 1) * (1 / np.sqrt(w["n_events"].clip(lower=1)))).clip(0, 1)
    return a, b, c


def rank(w, fresh=None):
    a, b, c = components(w)
    w = w.assign(s_edge=a, s_early=b, s_focus=c)
    if fresh is not None:
        w = w.merge(fresh, on="wallet", how="left")
        d = (1 - w["days_since_first_activity"] / 30).clip(0, 1).fillna(0)
    else:
        d = pd.Series(0.0, index=w.index)
    w["s_fresh"] = d
    weights = {"s_edge": 0.40, "s_early": 0.30, "s_focus": 0.15, "s_fresh": 0.15}
    w["insider_score"] = 100 * sum(w[k] * v for k, v in weights.items())
    eligible = (~w["market_maker"]) & (w["cost"] >= MIN_COST) & (w["pnl"] > 0) & (w["z_edge"] >= MIN_Z)
    return w[eligible].sort_values("insider_score", ascending=False)


if __name__ == "__main__":
    wm = pd.read_csv(sys.argv[1])
    w = wallet_table(wm)
    print(len(w), "wallets", int((w["cost"] >= MIN_COST).sum()), "with at least", MIN_COST, "USDC")
    r = rank(w)
    cols = ["wallet", "cost", "pnl", "z_edge", "n_events", "focus_share", "early_cheap_usd",
            "cheap_winning_events", "insider_score", "top_event"]
    print(r[cols].head(15).to_string())
    print("z>=4:", int((r["z_edge"] >= 4).sum()), "of", len(r))
