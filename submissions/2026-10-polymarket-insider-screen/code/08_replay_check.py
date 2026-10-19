"""Why the screen does not use a luck replay.

A luck replay redraws outcomes at the traded prices and asks how often a wallet does as well as it
really did. On a ladder of dates ("by March 31", "by April 30") it has to draw one number U per
event, so that a later date can never resolve NO while an earlier one resolves YES, and resolve a
trade YES when U is below the trade's YES price. Prices move, so the real outcome can be one that
no U produces: it needs U above every YES price paid in the dates that resolved NO and below every
YES price paid in the dates that resolved YES. When the first is higher than the second, the
replay gives the real history probability zero, and a wallet that bought the right side of both
gets a profit no replay can reach.

A ladder here is an event that is not negRisk, whose markets all ask whether something happens by
or before a date, each a different date, and whose questions are the same once the date is taken
out. For every ladder with dates resolving both ways, replay_check.csv gives the two prices and
whether the real outcome is reachable.
"""
import importlib.util
import os
import sys

import numpy as np
import pandas as pd


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(__file__), name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


features, pack = load("06_features"), load("05_pack")


def stem(question):
    """The question without its date, or None unless the date is a "by" or "before" deadline."""
    q = str(question)
    for rx in (pack.DAY, pack.MON, pack.YEAR):
        m = rx.search(q)
        if m:
            if m.group(1).lower() not in ("by", "before"):
                return None
            return " ".join(rx.sub("", q).split()).lower()
    return None


def ladders(scope):
    s = scope[~scope["negRisk"].astype(str).str.lower().eq("true")].copy()
    s["stem"] = s["question"].map(stem)
    g = s.groupby("event_id")
    ok = (g["m"].transform("size") >= 2) & g["stem"].transform(lambda x: x.notna().all()) \
        & g["stem"].transform("nunique").eq(1) & g["deadline_ts"].transform("nunique").eq(g["m"].transform("size"))
    return set(s.loc[ok, "event_id"])


def main(datadir, out):
    scope = features.read_scope(datadir)
    t = features.read_tape(datadir).merge(scope[["m", "event_id", "winner_index"]], on="m")
    t = t[t["event_id"].isin(ladders(scope))]
    t["y"] = np.where(t["o"] == 0, t["price"], 1 - t["price"])
    t["usd"] = t["size"] * t["price"]
    t["resolved_yes"] = t["winner_index"] == 0
    g = t.groupby(["event_id", "resolved_yes"])["y"]
    tab = pd.DataFrame({"max_yes_price_in_no_dates": g.max().xs(False, level="resolved_yes"),
                        "min_yes_price_in_yes_dates": g.min().xs(True, level="resolved_yes")}).dropna()
    tab["real_outcome_reachable"] = tab["max_yes_price_in_no_dates"] < tab["min_yes_price_in_yes_dates"]
    tab["markets"] = t.groupby("event_id")["m"].nunique().reindex(tab.index)
    tab["usd"] = t.groupby("event_id")["usd"].sum().reindex(tab.index)
    tab["event_slug"] = scope.drop_duplicates("event_id").set_index("event_id")["event_slug"].reindex(tab.index)
    tab = tab.reset_index().sort_values("usd", ascending=False)
    cols = ["event_slug", "markets", "max_yes_price_in_no_dates", "min_yes_price_in_yes_dates", "real_outcome_reachable", "usd"]
    tab[cols].round(4).to_csv(out, index=False)
    bad = ~tab["real_outcome_reachable"]
    print(len(tab), "ladders;", int(bad.sum()), "with the real outcome out of reach;",
          round(tab.loc[bad, "usd"].sum() / tab["usd"].sum(), 4), "of their dollars")
    print(tab[cols].head(15).to_string(index=False))


if __name__ == "__main__":
    main(*sys.argv[1:3])
