"""Opening positions at the start of the window, for every wallet and market on the committed tape.

05_pack.py drops trades before 1 November 2025, but a market created earlier can have wallets that
bought before then and sell inside the window. Without their earlier trades those sales look like
shares minted from nothing. For each wallet and market on the committed tape this nets the wallet's
trades before the window per outcome, applies the same minting rule as 06_features.py (a negative
holding is covered by minting full sets), and values the position at the last price traded on each
outcome before the window, or one minus the other outcome's last price when one side never traded.

Usage: python code/05b_opening.py RAWDIR DATADIR
Writes DATADIR/opening_positions.csv.gz: m, w, open_0, open_1, open_cost.
"""
import importlib.util
import os
import sys

import numpy as np
import pandas as pd

_spec = importlib.util.spec_from_file_location("pack", os.path.join(os.path.dirname(__file__), "05_pack.py"))
pack = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pack)
_spec = importlib.util.spec_from_file_location("features", os.path.join(os.path.dirname(__file__), "06_features.py"))
features = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(features)

GZ = {"method": "gzip", "mtime": 0}


def main(rawdir, datadir):
    scope = features.read_scope(datadir)
    pairs = features.read_tape(datadir)[["m", "w"]].drop_duplicates()
    wallets = pd.read_csv(os.path.join(datadir, "wallets.csv.gz"))
    addr = dict(zip(wallets["wallet"], wallets["w"]))
    rows = []
    for m, ws in pairs.groupby("m")["w"]:
        cid = scope.loc[scope["m"] == m, "conditionId"].iloc[0]
        df = pack.load(os.path.join(rawdir, cid + ".csv.gz"))
        df = df[df["timestamp"] < pack.START]
        if df.empty:
            continue
        last = df.sort_values("timestamp", kind="mergesort").groupby("outcomeIndex")["price"].last()
        p0 = last.get(0, 1 - last.get(1, 0.5))
        p1 = last.get(1, 1 - p0)
        df = df.assign(w=df["proxyWallet"].map(addr))
        df = df[df["w"].isin(set(ws))]
        if df.empty:
            continue
        signed = np.where(df["side"] == "BUY", df["size"], -df["size"])
        net = pd.DataFrame({"w": df["w"], "o": df["outcomeIndex"], "s": signed}).groupby(["w", "o"])["s"].sum().unstack(fill_value=0.0)
        for o in (0, 1):
            if o not in net.columns:
                net[o] = 0.0
        mint = np.maximum(np.maximum(-net[0], -net[1]), 0.0)
        o0, o1 = net[0] + mint, net[1] + mint
        keep = (o0 > 1e-9) | (o1 > 1e-9)
        rows.append(pd.DataFrame({"m": m, "w": net.index[keep].astype(int), "open_0": o0[keep].values,
                                  "open_1": o1[keep].values, "open_cost": (o0 * p0 + o1 * p1)[keep].values}))
    out = pd.concat(rows, ignore_index=True).sort_values(["m", "w"]).round(6)
    out.to_csv(os.path.join(datadir, "opening_positions.csv.gz"), index=False, compression=GZ)
    print(len(out), "wallet-market opening positions,", out["m"].nunique(), "markets")


if __name__ == "__main__":
    main(*sys.argv[1:3])
