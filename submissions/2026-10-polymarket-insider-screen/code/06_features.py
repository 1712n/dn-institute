"""Turn the committed tape into one row per wallet and market.

Every trade in the tape was placed before the market's t_known, so every row here is a
prediction. Positions are netted: shares held at t_known are the opening position from
05b_opening.py plus buys minus sells per token. The opening position is what the wallet held when
the window started, valued at the last price before it. When a wallet sells more of a token
than it had, the shortfall came from minting a YES and NO pair for $1 (a split), so the pair is
added at that cost. Profit is cash out minus cash in, the opening position counted as cash in,
plus $1 per held share of the winning token.

early_longshot_usd is the money put on the eventual winner at LONGSHOT or less in the LEAD_S
before t_known, counted only for shares the wallet still held at t_known: a wallet that bought
cheap and sold again within minutes did not bet on the outcome. Sales are matched to earlier
buys of the same token first in, first out, so shares bought later cannot stand in for cheap
shares already sold. Shares held at the start of the window are the oldest lot.
"""
import glob
import os
import sys
from collections import deque

import numpy as np
import pandas as pd

LONGSHOT = 0.30
LEAD_S = 7 * 24 * 3600


def read_tape(datadir):
    parts = sorted(glob.glob(os.path.join(datadir, "tape_part*.csv.xz")))
    return pd.concat([pd.read_csv(p) for p in parts], ignore_index=True)


def read_scope(datadir):
    scope = pd.read_csv(os.path.join(datadir, "markets_scope.csv"), dtype={"id": str, "event_id": str})
    scope["event_id"] = scope["event_id"].fillna("m" + scope["m"].astype(str))
    return scope


def read_opening(datadir):
    path = os.path.join(datadir, "opening_positions.csv.gz")
    return pd.read_csv(path) if os.path.exists(path) else None


def early_held_usd(t, opening_win):
    """Cost of the early winner shares each wallet still held at t_known, per wallet and market."""
    win = t[t["win_tok"]]
    pairs = pd.MultiIndex.from_frame(win.loc[win["early"], ["w", "m"]].drop_duplicates())
    win = win[pd.MultiIndex.from_frame(win[["w", "m"]]).isin(pairs)].sort_values("ts", kind="mergesort")
    kept = {}
    for key, g in win.groupby(["w", "m"], sort=False):
        lots = deque([[opening_win[key], None]] if opening_win.get(key, 0.0) > 0 else [])
        for buy, early, size, price in zip(g["buy"], g["early"], g["size"], g["price"]):
            if buy:
                lots.append([size, price if early else None])
                continue
            while size > 0 and lots:
                take = min(size, lots[0][0])
                lots[0][0] -= take
                size -= take
                if lots[0][0] <= 1e-9:
                    lots.popleft()
        kept[key] = sum(s * p for s, p in lots if p is not None)
    return pd.Series(kept, dtype=float)


def wallet_market(tape, scope, opening=None):
    """One row per wallet and market from a tape and the market table, counting only trades
    before each market's t_known, on top of the opening positions when they are given."""
    if opening is None:
        opening = pd.DataFrame(columns=["m", "w", "open_0", "open_1", "open_cost"])
    t = tape.merge(scope[["m", "winner_index", "t_known"]], on="m", how="left")
    t = t[t["ts"] < t["t_known"]].copy()
    t["usd"] = t["size"] * t["price"]
    t["buy"] = t["side"] == "B"
    t["win_tok"] = t["o"] == t["winner_index"]
    t["early"] = t["buy"] & t["win_tok"] & (t["price"] <= LONGSHOT) & (t["t_known"] - t["ts"] <= LEAD_S)
    t["lead_h_x_usd"] = np.where(t["buy"] & t["win_tok"], (t["t_known"] - t["ts"]) / 3600 * t["usd"], 0.0)
    keys = ["w", "m"]
    g = t.groupby(keys)
    out = pd.DataFrame({"n_trades": g.size(), "first_ts": g["ts"].min(), "last_ts": g["ts"].max()})
    for o in (0, 1):
        for side, flag in (("buy", True), ("sell", False)):
            s = t[(t["o"] == o) & (t["buy"] == flag)].groupby(keys)
            out[f"{side}_sh_{o}"] = s["size"].sum()
            out[f"{side}_usd_{o}"] = s["usd"].sum()
    out = out.fillna(0.0)
    ow = opening.merge(scope[["m", "winner_index"]], on="m")
    ow = dict(zip(zip(ow["w"], ow["m"]), np.where(ow["winner_index"] == 0, ow["open_0"], ow["open_1"])))
    out["early_longshot_usd"] = early_held_usd(t, ow).reindex(out.index).fillna(0.0)
    out["lead_h_x_usd"] = g["lead_h_x_usd"].sum()
    out = out.reset_index().merge(scope[["m", "winner_index", "event_id", "negRisk"]], on="m")
    out = out.merge(opening, on=["m", "w"], how="left")
    out[["open_0", "open_1", "open_cost"]] = out[["open_0", "open_1", "open_cost"]].astype(float).fillna(0.0)

    held0 = out["open_0"] + out["buy_sh_0"] - out["sell_sh_0"]
    held1 = out["open_1"] + out["buy_sh_1"] - out["sell_sh_1"]
    minted = np.maximum(np.maximum(-held0, -held1), 0.0)
    out["minted_sh"] = minted
    out["held_0"] = held0 + minted
    out["held_1"] = held1 + minted
    out["cash"] = out["sell_usd_0"] + out["sell_usd_1"] - out["buy_usd_0"] - out["buy_usd_1"] - minted - out["open_cost"]
    out["cost"] = out["buy_usd_0"] + out["buy_usd_1"] + minted + out["open_cost"]
    win_held = np.where(out["winner_index"] == 0, out["held_0"], out["held_1"])
    out["pnl"] = out["cash"] + win_held
    win_buy = np.where(out["winner_index"] == 0, out["buy_usd_0"], out["buy_usd_1"])
    out["win_buy_usd"] = win_buy
    out["lose_buy_usd"] = out["buy_usd_0"] + out["buy_usd_1"] - win_buy
    out["win_lead_h_usdw"] = np.where(win_buy > 0, out["lead_h_x_usd"] / np.where(win_buy > 0, win_buy, 1), np.nan)
    out = out.drop(columns=["lead_h_x_usd"])
    return out.sort_values(keys).reset_index(drop=True)


def main(datadir, out):
    wm = wallet_market(read_tape(datadir), read_scope(datadir), read_opening(datadir))
    wm.round(6).to_csv(out, index=False)
    print(len(wm), "wallet-market rows,", wm["w"].nunique(), "wallets,", wm["m"].nunique(), "markets")


if __name__ == "__main__":
    main(*sys.argv[1:3])
