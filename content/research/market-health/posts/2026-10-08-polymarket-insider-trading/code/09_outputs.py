"""Write the CSV artifacts and charts for the report."""
import gzip
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from importlib import import_module

score = import_module("06_score")

TOP = 25


def main(wm_path, markets_path, fresh_path, null_path, outdir):
    os.makedirs(outdir, exist_ok=True)
    wm = pd.read_csv(wm_path)
    markets = pd.read_csv(markets_path)
    fresh = pd.read_csv(fresh_path)
    null = pd.read_csv(null_path)

    w = score.wallet_table(wm)
    ranked = score.rank(w, fresh)
    cols = ["wallet", "insider_score", "s_edge", "s_early", "s_focus", "s_fresh", "z_edge", "pnl",
            "cost", "n_events", "focus_share", "early_cheap_usd", "cheap_winning_events",
            "days_since_first_activity", "first_buy_ts", "top_event"]
    ranked[cols].round(4).to_csv(os.path.join(outdir, "wallet_ranking.csv"), index=False)
    markets.round(4).to_csv(os.path.join(outdir, "markets_scope.csv"), index=False)
    null.round(3).to_csv(os.path.join(outdir, "null_calibration.csv"), index=False)

    top = ranked.head(TOP)
    fig, ax = plt.subplots(figsize=(9, 6))
    labels = [a[:6] + "…" + a[-4:] for a in top["wallet"]][::-1]
    left = np.zeros(len(top))
    for name, wt, color in (("s_edge", 0.40, "#1f77b4"), ("s_early", 0.30, "#ff7f0e"),
                            ("s_focus", 0.15, "#2ca02c"), ("s_fresh", 0.15, "#d62728")):
        vals = (100 * wt * top[name]).to_numpy()[::-1]
        ax.barh(labels, vals, left=left, color=color, label=name.replace("s_", ""))
        left += vals
    ax.set_xlabel("score (points)")
    ax.set_title("Top 25 wallets by insider score, split by signal")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, "score-components.png"), dpi=130)
    plt.close(fig)

    real = w[(w["cost"] >= score.MIN_COST) & ~w["market_maker"]]
    fig, ax = plt.subplots(figsize=(8, 5))
    bins = np.arange(-8, 10, 0.5)
    ax.hist(real["z_edge"].clip(-8, 9.5), bins=bins, color="#1f77b4", alpha=0.8)
    ax.set_yscale("log")
    ax.set_xlabel("luck-adjusted edge (z)")
    ax.set_ylabel("wallets (log)")
    ax.set_title("Distribution of luck-adjusted edge across wallets")
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, "edge-distribution.png"), dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    main(*sys.argv[1:6])
