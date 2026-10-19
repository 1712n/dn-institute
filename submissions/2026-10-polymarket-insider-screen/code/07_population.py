"""One row per tested wallet: what it spent, what it made, how widely it traded.

Every wallet in the committed tape is tested; 05_pack.py leaves out the wallets under
the spending floor, the market makers and the high-frequency bots, and wallets.csv.gz says
which was which.
"""
import sys

import pandas as pd


def main(wm_path, out):
    wm = pd.read_csv(wm_path, dtype={"event_id": str})
    g = wm.groupby("w")
    pop = pd.DataFrame({
        "cost": g["cost"].sum(), "pnl": g["pnl"].sum(), "n_markets": g["m"].nunique(),
        "n_events": g["event_id"].nunique(), "sell_usd": g["sell_usd_0"].sum() + g["sell_usd_1"].sum(),
    }).reset_index()
    pop["tested"] = True
    pop.round(6).to_csv(out, index=False, compression={"method": "gzip", "mtime": 0})
    print(len(pop), "tested wallets;", int((pop["pnl"] > 0).sum()), "made a profit")


if __name__ == "__main__":
    main(*sys.argv[1:3])
