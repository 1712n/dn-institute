"""How many wallets would clear the same bars by luck alone?

Each wallet-market bet is redrawn as a Bernoulli trial that wins with probability equal to the
wallet's own average entry price (fair prices, no information). The wallet table is rebuilt from
the redrawn outcomes and the share of wallets above each z threshold is compared with the real one.
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


def main(wm_path, out):
    wm = pd.read_csv(wm_path)
    real = score.wallet_table(wm)
    real = real[(real["cost"] >= score.MIN_COST) & ~real["market_maker"]]
    rng = np.random.default_rng(7)
    rows = []
    for d in range(DRAWS):
        sim = wm.copy()
        sim["won"] = rng.random(len(sim)) < sim["avg_price"]
        w = score.wallet_table(sim)
        w = w[(w["cost"] >= score.MIN_COST) & ~w["market_maker"]]
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
