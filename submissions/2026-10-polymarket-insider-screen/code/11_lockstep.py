"""Find tested wallets that trade in lockstep, across the whole tested population.

Two wallets are linked when they bought the same outcome of the same market in the same second
at least LOCKSTEP times. Linked wallets form groups (connected components). A group whose
members all made their first Polymarket move within FRESH_SPAN_DAYS of each other was set up
together, which points to one operator or one copy-trading signal.

lockstep_pairs.csv.gz   every linked pair and its count of shared buys.
lockstep_groups.csv     one row per group: size, first activity span, profit, how many members
                        made a profit, the event with the most of the group's money, members.
"""
import importlib.util
import os
import sys
from collections import Counter

import numpy as np
import pandas as pd

LOCKSTEP = 10
FRESH_SPAN_DAYS = 3
GZ = {"method": "gzip", "mtime": 0}

_spec = importlib.util.spec_from_file_location("features", os.path.join(os.path.dirname(__file__), "06_features.py"))
features = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(features)


def pairs(tape):
    b = tape.loc[tape["side"] == "B", ["w", "m", "o", "ts"]].drop_duplicates()
    seconds = b.groupby(["m", "o", "ts"])["w"].agg(list)
    cnt = Counter()
    for ws in seconds[seconds.map(len) >= 2]:
        ws = sorted(ws)
        for i in range(len(ws)):
            for j in range(i + 1, len(ws)):
                cnt[(ws[i], ws[j])] += 1
    return pd.DataFrame([(a, c, n) for (a, c), n in cnt.items() if n >= LOCKSTEP], columns=["a", "b", "shared_buys"])


def components(p):
    parent = {}

    def find(x):
        while parent.get(x, x) != x:
            parent[x] = parent.get(parent[x], parent[x])
            x = parent[x]
        return x

    for a, b in zip(p["a"], p["b"]):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)
    nodes = sorted(set(p["a"]) | set(p["b"]))
    return pd.DataFrame({"w": nodes, "root": [find(n) for n in nodes]})


def main(datadir, outdir):
    tape = features.read_tape(datadir)
    scope = features.read_scope(datadir)
    wallets = pd.read_csv(os.path.join(datadir, "wallets.csv.gz")).dropna(subset=["w"]).astype({"w": int})
    addr = wallets.set_index("w")["wallet"]
    fa = wallets.merge(pd.read_csv(os.path.join(datadir, "wallet_first_activity.csv.gz")), on="wallet").set_index("w")["first_activity_ts"]
    wm = pd.read_csv(os.path.join(datadir, "wallet_market.csv.gz"), dtype={"event_id": str})
    p = pairs(tape)
    out = p.assign(wallet_a=p["a"].map(addr), wallet_b=p["b"].map(addr))
    out = out.sort_values(["shared_buys", "wallet_a", "wallet_b"], ascending=[False, True, True])
    out[["wallet_a", "wallet_b", "shared_buys"]].to_csv(os.path.join(outdir, "lockstep_pairs.csv.gz"), index=False, compression=GZ)

    c = components(p)
    pnl = wm.groupby("w")["pnl"].sum()
    ev_slug = scope.drop_duplicates("event_id").set_index("event_id")["event_slug"]
    rows = []
    for root, g in c.groupby("root"):
        ws = g["w"].tolist()
        f = fa.reindex(ws).astype(float)
        cost = wm[wm["w"].isin(ws)].groupby("event_id")["cost"].sum()
        rows.append({"size": len(ws), "first_activity_min": f.min(), "first_activity_max": f.max(),
                     "first_activity_span_days": (f.max() - f.min()) / 86400, "pnl": pnl.reindex(ws).sum(),
                     "members_in_profit": int((pnl.reindex(ws) > 0).sum()),
                     "top_event": ev_slug.get(cost.idxmax(), ""), "top_event_cost": cost.max(),
                     "members": ";".join(sorted(addr[ws]))})
    grp = pd.DataFrame(rows).sort_values(["size", "members"], ascending=[False, True]).reset_index(drop=True)
    grp.insert(0, "group", np.arange(1, len(grp) + 1))
    grp["set_up_together"] = (grp["size"] >= 5) & (grp["first_activity_span_days"] <= FRESH_SPAN_DAYS)
    for k in ("first_activity_min", "first_activity_max"):
        grp[k] = pd.to_datetime(grp[k], unit="s", utc=True).dt.strftime("%Y-%m-%d %H:%M:%S")
    grp.round(4).to_csv(os.path.join(outdir, "lockstep_groups.csv"), index=False)
    print(len(p), "linked pairs,", len(grp), "groups; set up together, five or more wallets:")
    print(grp.loc[grp["set_up_together"]].drop(columns="members").to_string(index=False))


if __name__ == "__main__":
    main(*sys.argv[1:3])
