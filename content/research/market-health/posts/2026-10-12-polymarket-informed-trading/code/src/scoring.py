import numpy as np
import pandas as pd

import config

WEIGHTS = {
    "s_pnl": 0.18,
    "s_edge": 0.16,
    "s_cheap": 0.14,
    "s_fwd": 0.16,
    "s_consistency": 0.18,
    "s_onesided": 0.08,
    "s_timing": 0.10,
}


def _wsum(df, col, w):
    num = (df[col].fillna(0.0) * df[w]).groupby(df["wallet"]).sum()
    den = df[w].groupby(df["wallet"]).sum().replace(0, np.nan)
    return (num / den).fillna(0.0)


def aggregate(wm, trades):
    w = wm["win_buy_notional"]
    played = (wm["win_buy_notional"] + wm["lose_buy_notional"]) >= config.MIN_WIN_NOTIONAL
    won = (wm["realized_pnl"] > 0) & (wm["win_buy_notional"] >= config.MIN_WIN_NOTIONAL)

    W = pd.DataFrame({
        "n_markets": wm.groupby("wallet").size(),
        "n_flagged": wm.groupby("wallet")["flag"].sum(),
        "n_played": played.groupby(wm["wallet"]).sum(),
        "n_won": won.groupby(wm["wallet"]).sum(),
        "win_notional": wm.groupby("wallet")["win_buy_notional"].sum(),
        "total_notional": (wm["win_buy_notional"] + wm["lose_buy_notional"]).groupby(wm["wallet"]).sum(),
        "realized_pnl": wm.groupby("wallet")["realized_pnl"].sum(),
        "n_trades": wm.groupby("wallet")["n_trades"].sum(),
        "vwap_entry_w": _wsum(wm, "vwap_entry", "win_buy_notional"),
        "pre_move_w": _wsum(wm, "pre_move_frac", "win_buy_notional"),
        "fwd_move_w": _wsum(wm, "fwd_move", "win_buy_notional"),
        "one_sided_w": _wsum(wm, "one_sided", "win_buy_notional"),
        "hours_before_res_w": _wsum(wm, "hours_before_res", "win_buy_notional"),
    })
    W["hit_rate"] = np.where(W["n_played"] > 0, W["n_won"] / W["n_played"], 0.0)
    W["roi"] = np.where(W["total_notional"] > 0, W["realized_pnl"] / W["total_notional"], 0.0)

    ident = (trades.dropna(subset=["pseudonym"]).groupby("wallet")
             .agg(pseudonym=("pseudonym", "first"), name=("name", "first"), bio=("bio", "first")))
    W = W.join(ident)
    return W.reset_index(names="wallet")


def score(W):
    gate = (
        (W["total_notional"] >= config.MIN_WALLET_NOTIONAL) &
        (W["n_trades"] >= config.MIN_WALLET_TRADES) &
        ((W["realized_pnl"] > 0) | (W["n_flagged"] >= 1))
    )
    g = W[gate].copy()
    if not len(g):
        return g

    g["s_pnl"] = g["realized_pnl"].clip(lower=0).rank(pct=True)
    g["s_edge"] = g["roi"].clip(lower=0, upper=5).rank(pct=True)
    g["s_cheap"] = ((0.5 - g["vwap_entry_w"]) / 0.5).clip(0, 1)
    g["s_fwd"] = g["fwd_move_w"].clip(lower=0).rank(pct=True)
    g["s_consistency"] = 0.5 * (g["n_flagged"].clip(upper=3) / 3) + 0.5 * g["hit_rate"].clip(0, 1)
    g["s_onesided"] = g["one_sided_w"].clip(0, 1)
    g["s_timing"] = g["pre_move_w"].clip(0, 1)

    g["ILS"] = sum(WEIGHTS[k] * g[k] for k in WEIGHTS) * 100.0
    g = g.sort_values("ILS", ascending=False).reset_index(drop=True)
    g.insert(0, "rank", g.index + 1)
    return g


def write_outputs(markets, trades, wm, W, ranked):
    config.OUTPUT_DIR.mkdir(exist_ok=True)

    cols = ["rank", "wallet", "ILS", "pseudonym", "name",
            "n_markets", "n_played", "n_won", "hit_rate", "n_flagged",
            "win_notional", "total_notional", "realized_pnl", "roi",
            "vwap_entry_w", "pre_move_w", "fwd_move_w", "hours_before_res_w", "one_sided_w",
            "s_pnl", "s_edge", "s_cheap", "s_fwd", "s_consistency", "s_onesided", "s_timing", "bio"]
    rk = ranked[[c for c in cols if c in ranked.columns]].round(4)
    rk.to_csv(config.OUTPUT_DIR / "trader_rankings.csv", index=False)

    flg = wm[wm["flag"]].merge(
        ranked[["wallet", "ILS", "rank"]], on="wallet", how="left"
    ).sort_values(["ILS", "win_buy_notional"], ascending=False)
    fcols = ["rank", "ILS", "wallet", "slug", "question", "win_outcome",
             "win_buy_notional", "net_win_shares", "vwap_entry", "pre_move_frac",
             "fwd_move", "hours_before_res", "realized_pnl", "n_trades", "end_date", "trades_capped"]
    flg[[c for c in fcols if c in flg.columns]].round(4).to_csv(
        config.OUTPUT_DIR / "flagged_trades.csv", index=False)

    msum = wm.groupby(["condition_id", "slug", "question", "win_outcome", "volume", "trades_capped"]).agg(
        wallets=("wallet", "nunique"),
        flagged_wallets=("flag", "sum"),
    ).reset_index().sort_values("volume", ascending=False)
    msum.to_csv(config.OUTPUT_DIR / "market_summary.csv", index=False)
    return rk, flg, msum
