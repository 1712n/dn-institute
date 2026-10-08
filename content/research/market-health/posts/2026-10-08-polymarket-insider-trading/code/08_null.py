"""How many wallets would clear the same bars by luck alone?

Each wallet-market position is redrawn at fair prices: one outcome per wallet and market, won with
probability equal to the wallet's average entry price on the side it first bought. A wallet that
holds both sides gets the opposite outcome on its other side, so exactly one side wins. The real
market-maker flag is kept, so the null counts the same population as the real run.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from importlib import import_module

score = import_module("06_score")

DRAWS = 20
THRESHOLDS = (2, 3, 4, 5)


def redraw(wm, rng):
    sim = wm.sort_values(["wallet", "conditionId", "first_ts"]).copy()
    first = ~sim.duplicated(["wallet", "conditionId"])
    p = sim.loc[first, "avg_price"].to_numpy()
    lead_wins = pd.Series(rng.random(len(p)) < p, index=sim.index[first])
    lead = lead_wins.reindex(sim.index).ffill().astype(bool)
    sim["won"] = np.where(first, lead, ~lead)
    return sim


def main(wm_path, out):
    wm = pd.read_csv(wm_path)
    real = score.wallet_table(wm)
    real = real[(real["cost"] >= score.MIN_COST) & ~real["market_maker"]]
    keep = set(real["wallet"])
    rng = np.random.default_rng(7)
    rows = []
    for d in range(DRAWS):
        w = score.wallet_table(redraw(wm, rng))
        w = w[w["wallet"].isin(keep)]
        rows.append({t: int(((w["z_edge"] >= t) & (w["pnl"] > 0)).sum()) for t in THRESHOLDS})
    null = pd.DataFrame(rows)
    table = pd.DataFrame({
        "z_threshold": THRESHOLDS,
        "wallets_real": [int(((real["z_edge"] >= t) & (real["pnl"] > 0)).sum()) for t in THRESHOLDS],
        "wallets_null_mean": [null[t].mean() for t in THRESHOLDS],
        "wallets_null_max": [null[t].max() for t in THRESHOLDS],
    })
    table["wallets_tested"] = len(real)
    table.to_csv(out, index=False)
    print(table.to_string(index=False))


if __name__ == "__main__":
    main(*sys.argv[1:3])
