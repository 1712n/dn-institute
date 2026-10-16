"""Wallet-first screen: wallets that won every market they traded, at long odds.

The event screen (detect_surprises.py) ranks markets by how far the winner moved over the
collected tape, so it misses markets that broke in the last hours of trading. This screen
starts from wallets instead and hands their markets to the same episode scoring.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import duckdb
import pandas as pd

import config
import detect_surprises as ds
from src import enrich

MIN_MARKETS = 3
MIN_INVESTED = 500.0
LONGSHOT_VWAP = 0.5        # average entry into the winners below 50c
TOP_LONGSHOT = 50
SEED_MIN_PNL = 5_000.0     # longshot wallets whose markets are handed to episode scoring
SEED_MIN_MARKET_PNL = 2_000.0


def wallet_market_pnl(con):
    """Realised + resolution PnL of every (wallet, market), from the trade tape."""
    return con.execute("""
        WITH pos AS (
            SELECT wallet, condition_id, outcome_index,
                   round(sum(CASE WHEN side = 'BUY' THEN size ELSE -size END), 6) net_shares,
                   round(sum(CASE WHEN side = 'BUY' THEN size * price ELSE 0 END), 6) buy_usd,
                   round(sum(CASE WHEN side = 'BUY' THEN size ELSE 0 END), 6) buy_shares,
                   round(sum(CASE WHEN side = 'SELL' THEN size * price ELSE 0 END), 6) sell_usd
            FROM trades GROUP BY 1, 2, 3)
        SELECT p.wallet, p.condition_id, m.slug,
               round(sum(p.net_shares * CASE WHEN p.outcome_index = m.win_index THEN 1 ELSE 0 END
                   + p.sell_usd - p.buy_usd), 6) pnl,
               sum(p.buy_usd) inv,
               sum(CASE WHEN p.outcome_index = m.win_index THEN p.buy_usd ELSE 0 END) win_usd,
               sum(CASE WHEN p.outcome_index = m.win_index THEN p.buy_shares ELSE 0 END) win_shares,
               sum(CASE WHEN p.outcome_index = m.win_index THEN p.sell_usd ELSE 0 END) win_sell_usd,
               sum(CASE WHEN p.outcome_index <> m.win_index THEN p.sell_usd ELSE 0 END) lose_sell_usd
        FROM pos p JOIN markets m USING (condition_id)
        GROUP BY 1, 2, 3
        ORDER BY 1, 2""").df()


def market_won(wm):
    """The wallet came out ahead on the resolved winner, not on trading the losing side.

    Either it bought the winner, or it bought nothing and only sold the loser: shares minted by a
    split (one dollar for a Yes/No pair) never appear in the trade tape, so selling the losing
    half is how a split position shows up.
    """
    bought_winner = wm["win_usd"] > 0
    split_position = (wm["inv"] == 0) & (wm["lose_sell_usd"] > 0) & (wm["win_sell_usd"] == 0)
    return (wm["pnl"] > 0) & (bought_winner | split_position)


def perfect_winrate(wm):
    wm = wm.assign(won=market_won(wm))
    w = wm.groupby("wallet").agg(
        n_mk=("condition_id", "nunique"), n_won=("won", "sum"),
        pnl=("pnl", "sum"), inv=("inv", "sum"),
        win_usd=("win_usd", "sum"), win_shares=("win_shares", "sum")).reset_index()
    w["win_vwap"] = w["win_usd"] / w["win_shares"]
    w = w[(w["n_mk"] >= MIN_MARKETS) & (w["n_won"] == w["n_mk"]) & (w["inv"] >= MIN_INVESTED)]
    w = w.sort_values(["pnl", "wallet"], ascending=[False, True])
    return w[["wallet", "n_mk", "n_won", "pnl", "inv", "win_vwap"]].reset_index(drop=True)


def longshot_perfect(perfect, names, lifetime):
    ls = perfect[perfect["win_vwap"] < LONGSHOT_VWAP].head(TOP_LONGSHOT)
    ls = ls.merge(lifetime[["wallet", "lt_markets", "lt_pnl"]], on="wallet", how="left")
    ls = ls.merge(names, on="wallet", how="left")
    ls["ret_pct"] = (ls["pnl"] / ls["inv"] * 100).round()
    return ls


def seed_markets(con, wm, longshot):
    seeds = longshot.loc[longshot["pnl"] >= SEED_MIN_PNL, "wallet"]
    hits = wm[wm["wallet"].isin(seeds) & (wm["pnl"] >= SEED_MIN_MARKET_PNL)]
    if hits.empty:
        return pd.DataFrame()
    paths = ds.market_paths(con, hits["condition_id"].unique(), min_volume=0, min_trades=1)
    paths = paths[paths["jump_ts"].notna() & ds.in_window(paths["jump_ts"])]
    paths = ds.substantive(paths)
    by_market = hits.groupby("condition_id").agg(
        seed_wallets=("wallet", lambda s: ";".join(sorted(s))),
        seed_pnl=("pnl", "sum")).reset_index()
    out = paths.merge(by_market, on="condition_id")
    out["jump_ts"] = out["jump_ts"].astype("int64")
    cols = ["slug", "question", "wout", "volume", "history_truncated", "n_tr", "p_early", "p_late",
            "p_post", "jump_ts", "jump_utc", "end_date", "seed_wallets", "seed_pnl"]
    out = out[cols].rename(columns={"volume": "vol"})
    out = out.sort_values(["seed_pnl", "slug"], ascending=[False, True]).reset_index(drop=True)
    return out.round({"p_early": 3, "p_late": 3, "p_post": 3, "seed_pnl": 2, "vol": 0})


def wallet_names(con, wallets):
    con.register("w_df", pd.DataFrame({"wallet": list(wallets)}))
    names = con.execute("""
        SELECT wallet, max(pseudonym) AS pseudonym, max("name") AS "name"
        FROM trades WHERE wallet IN (SELECT wallet FROM w_df) GROUP BY 1""").df()
    con.unregister("w_df")
    return names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="use cached lifetime profiles only")
    args = ap.parse_args()

    con = duckdb.connect(str(config.DB_PATH), read_only=True)
    wm = wallet_market_pnl(con)
    perfect = perfect_winrate(wm)
    candidates = perfect[perfect["win_vwap"] < LONGSHOT_VWAP].head(TOP_LONGSHOT)["wallet"]
    lifetime = enrich.lifetime_profiles(candidates, offline=args.offline)
    longshot = longshot_perfect(perfect, wallet_names(con, candidates), lifetime)
    seeds = seed_markets(con, wm, longshot)
    con.close()

    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    perfect.round({"pnl": 1, "inv": 1, "win_vwap": 3}).to_csv(
        config.OUTPUT_DIR / "perfect_winrate.csv", index=False)
    longshot.round({"pnl": 1, "inv": 1, "win_vwap": 3, "lt_pnl": 2}).to_csv(
        config.OUTPUT_DIR / "longshot_perfect.csv", index=False)
    seeds.to_csv(config.OUTPUT_DIR / "wallet_seed_markets.csv", index=False)
    print(f"perfect-record wallets: {len(perfect):,}; longshot: {len(longshot)}; "
          f"seed markets for episode scoring: {len(seeds)}")


if __name__ == "__main__":
    main()
