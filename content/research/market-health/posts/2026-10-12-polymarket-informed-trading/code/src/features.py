import numpy as np
import pandas as pd

import config


def _end_ts(s):
    return pd.to_datetime(s, utc=True, errors="coerce").astype("int64") // 10**9


def _market_features(t, win_index, end_ts):
    t = t.sort_values("timestamp")
    t["wprice"] = np.where(t["outcome_index"] == win_index, t["price"], 1.0 - t["price"])
    path_ts = t["timestamp"].to_numpy()
    path_wp = t["wprice"].to_numpy()

    tw = t[t["outcome_index"] == win_index]
    tl = t[t["outcome_index"] != win_index]
    buys = tw[tw["side"] == "BUY"].copy()
    sells = tw[tw["side"] == "SELL"]
    lbuys = tl[tl["side"] == "BUY"]
    lsells = tl[tl["side"] == "SELL"]

    # forward return per winning buy
    if len(buys) and len(path_ts) > 1:
        idx = np.searchsorted(path_ts, buys["timestamp"].to_numpy() + config.FWD_HORIZON_H * 3600)
        idx = np.clip(idx, 0, len(path_wp) - 1)
        buys["fwd_move"] = path_wp[idx] - buys["wprice"].to_numpy()
    else:
        buys["fwd_move"] = 0.0

    def agg(df, val):
        if not len(df):
            return pd.Series(dtype=float)
        return df.groupby("wallet")[val].sum()

    wb_shares = agg(buys, "size")
    buys["notional"] = buys["size"] * buys["price"]
    wb_notional = agg(buys, "notional")
    ws_shares = agg(sells, "size")
    sells = sells.assign(notional=sells["size"] * sells["price"])
    ws_notional = agg(sells, "notional")
    lb_notional = agg(lbuys.assign(notional=lbuys["size"] * lbuys["price"]), "notional")
    ls_notional = agg(lsells.assign(notional=lsells["size"] * lsells["price"]), "notional")
    lb_shares = agg(lbuys, "size")
    ls_shares = agg(lsells, "size")

    wallets = sorted(set(buys["wallet"]) | set(sells["wallet"]) |
                     set(lbuys["wallet"]) | set(lsells["wallet"]))
    f = pd.DataFrame(index=wallets)
    f["win_buy_shares"] = wb_shares
    f["win_buy_notional"] = wb_notional
    f["win_sell_shares"] = ws_shares
    f["win_sell_notional"] = ws_notional
    f["lose_buy_notional"] = lb_notional
    f = f.fillna(0.0)

    f["net_win_shares"] = f["win_buy_shares"] - f["win_sell_shares"]
    f["vwap_entry"] = np.where(f["win_buy_shares"] > 0,
                               f["win_buy_notional"] / f["win_buy_shares"].replace(0, np.nan), np.nan)

    net_lose_shares = (lb_shares.reindex(wallets).fillna(0.0) -
                       ls_shares.reindex(wallets).fillna(0.0))
    win_leg = f["win_sell_notional"] + 1.0 * f["net_win_shares"] - f["win_buy_notional"]
    lose_leg = (ls_notional.reindex(wallets).fillna(0.0) + 0.0 * net_lose_shares -
                f["lose_buy_notional"])
    f["realized_pnl"] = win_leg + lose_leg

    # cheap / pre-move entry
    buys["cheap"] = (buys["price"] <= config.PRE_MOVE_PRICE) * buys["size"]
    pre = buys.groupby("wallet")["cheap"].sum()
    f["pre_move_frac"] = (pre.reindex(wallets).fillna(0.0) /
                          f["win_buy_shares"].replace(0, np.nan)).fillna(0.0)

    # volume-weighted entry time -> hours before resolution
    buys["st"] = buys["size"] * buys["timestamp"]
    vwt = buys.groupby("wallet")["st"].sum() / buys.groupby("wallet")["size"].sum()
    f["hours_before_res"] = (end_ts - vwt.reindex(wallets)) / 3600.0

    # size-weighted forward move
    buys["fm"] = buys["fwd_move"] * buys["size"]
    fm = buys.groupby("wallet")["fm"].sum() / buys.groupby("wallet")["size"].sum()
    f["fwd_move"] = fm.reindex(wallets).fillna(0.0)

    f["n_trades"] = (t.groupby("wallet").size()).reindex(wallets).fillna(0).astype(int)
    f["one_sided"] = f["lose_buy_notional"] / (f["win_buy_notional"] + f["lose_buy_notional"]).replace(0, np.nan)
    f["one_sided"] = (1.0 - f["one_sided"]).fillna(0.0)
    return f.reset_index(names="wallet")


def build(markets, trades):
    rows = []
    ends = dict(zip(markets["condition_id"], _end_ts(markets["end_date"])))
    wins = dict(zip(markets["condition_id"], markets["win_index"]))
    for cid, t in trades.groupby("condition_id"):
        if cid not in wins:
            continue
        f = _market_features(t, int(wins[cid]), int(ends[cid]))
        f["condition_id"] = cid
        rows.append(f)
    wm = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()

    wm["flag"] = (
        (wm["win_buy_notional"] >= config.MIN_WIN_NOTIONAL) &
        (wm["net_win_shares"] > 0) &
        (wm["vwap_entry"] <= config.CHEAP_ENTRY) &
        ((wm["pre_move_frac"] > 0) | (wm["fwd_move"] > 0.05))
    )
    meta = markets[["condition_id", "slug", "question", "end_date", "volume",
                    "win_outcome", "trades_capped"]]
    wm = wm.merge(meta, on="condition_id", how="left")
    return wm
