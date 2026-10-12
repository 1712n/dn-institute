import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import duckdb
import numpy as np
import pandas as pd

import config
from src import episode_score as es
from src import enrich

DB = str(config.DB_PATH)
MIN_EPISODE_NOTIONAL = 100.0
FLAG_S = 12


def targets(con):
    sub = pd.read_csv(config.OUTPUT_DIR / "surprise_substantive.csv")
    con.register("sub", sub[["slug", "jump_ts", "p_late"]])
    return con.execute("""
        SELECT m.condition_id, m.slug, m.question, m.win_outcome, m.win_index,
               m.volume, m.trades_capped, s.jump_ts, s.p_late
        FROM markets m JOIN sub s USING (slug)
        WHERE s.jump_ts IS NOT NULL
          AND lower(m.slug) NOT LIKE '%claude%'
          AND lower(m.slug) NOT LIKE '%hegseth-ban%'""").df()


def global_baselines(con):
    base = con.execute("""
        SELECT wallet, median(size*price) med_notional, count(*) n_trades,
               count(DISTINCT condition_id) n_markets, sum(size*price) tot_notional
        FROM trades WHERE side='BUY' GROUP BY 1""").df()
    base["avg_market_notional"] = base["tot_notional"] / base["n_markets"].clip(lower=1)

    succ = con.execute("""
        WITH pos AS (
            SELECT t.wallet, t.condition_id, t.outcome_index,
                   sum(CASE WHEN t.side='BUY' THEN t.size ELSE -t.size END) net_shares,
                   sum(CASE WHEN t.side='BUY' THEN t.size*t.price ELSE 0 END) buy_notional,
                   sum(CASE WHEN t.side='BUY' THEN t.size ELSE 0 END) buy_shares
            FROM trades t GROUP BY 1,2,3),
        bets AS (
            SELECT p.wallet, (p.outcome_index=m.win_index) won
            FROM pos p JOIN markets m USING(condition_id)
            WHERE p.net_shares>0 AND p.buy_notional>=100
              AND p.buy_notional/NULLIF(p.buy_shares,0) <= 0.5)
        SELECT wallet, count(*) attempts, sum(CASE WHEN won THEN 1 ELSE 0 END) wins
        FROM bets GROUP BY 1""").df()
    return base, succ


def episodes(con, tg):
    cids = tg["condition_id"].tolist()
    con.execute("CREATE OR REPLACE TEMP TABLE tgt AS SELECT * FROM tg_df")
    tr = con.execute("""
        SELECT t.condition_id, t.wallet, t.side, t.size, t.price, t.timestamp, t.outcome_index,
               t.pseudonym, t.name, t.bio
        FROM trades t WHERE t.condition_id IN (SELECT condition_id FROM tgt)""").df()
    meta = tg.set_index("condition_id")
    rows = []
    for cid, g in tr.groupby("condition_id"):
        win = int(meta.at[cid, "win_index"])
        jump = float(meta.at[cid, "jump_ts"])
        p_late = float(meta.at[cid, "p_late"])
        wb = g[(g["outcome_index"] == win) & (g["side"] == "BUY") & (g["timestamp"] < jump)].copy()
        if not len(wb):
            continue
        wb["notional"] = wb["size"] * wb["price"]
        for w, b in wb.groupby("wallet"):
            notional = b["notional"].sum()
            if notional < MIN_EPISODE_NOTIONAL:
                continue
            shares = b["size"].sum()
            vwap = notional / shares
            vwt = (b["size"] * b["timestamp"]).sum() / shares
            rows.append({
                "condition_id": cid, "slug": meta.at[cid, "slug"],
                "wallet": w, "pseudonym": b["pseudonym"].iloc[0], "bio": b["bio"].iloc[0],
                "win_buy_notional": notional, "max_single_buy": b["notional"].max(),
                "shares": shares, "vwap_entry": vwap,
                "entry_ts": float(vwt), "first_ts": float(b["timestamp"].min()),
                "hours_before_jump": (jump - vwt) / 3600.0,
                "p_edge": p_late - vwap, "n_buys": len(b),
            })
    return pd.DataFrame(rows)


def main():
    con = duckdb.connect(DB, read_only=False)
    tg = targets(con)
    con.register("tg_df", tg)
    print(f"[targets] {len(tg)} substantive surprise markets")

    print("[baselines] computing global per-wallet stats over 13.2M trades ...")
    base, succ = global_baselines(con)
    print(f"[baselines] wallets with buys: {len(base):,}; with cheap-bet history: {len(succ):,}")

    ep = episodes(con, tg)
    print(f"[episodes] pre-jump winning-side episodes: {len(ep):,}")

    ep = ep.merge(base[["wallet", "med_notional", "avg_market_notional", "n_markets", "n_trades"]],
                  on="wallet", how="left")
    ep = ep.merge(succ, on="wallet", how="left")
    ep["wins"] = ep["wins"].fillna(0)
    ep["attempts"] = ep["attempts"].fillna(0)
    ep["v_ratio"] = ep["max_single_buy"] / ep["med_notional"].replace(0, np.nan)
    ep["a_ratio"] = ep["win_buy_notional"] / ep["avg_market_notional"].replace(0, np.nan)

    sc = ep.apply(es.score_row, axis=1)
    ep = pd.concat([ep, sc], axis=1)
    ep = ep.rename(columns={"S": "S_base"})

    print("[enrich] fetching lifetime profiles (parallel) ...")
    wallets = ep["wallet"].unique().tolist()
    lt = enrich.fetch_lifetime_parallel(wallets, workers=16)
    ep = ep.merge(lt, on="wallet", how="left")
    mt = ep.apply(lambda r: enrich.lifetime_multiplier(r["lt_markets"], r["lt_pnl"]), axis=1)
    ep["M_lifetime"] = [m for m, _ in mt]
    ep["lt_tag"] = [t for _, t in mt]

    print("[enrich] co-occurrence clustering (synchronous wallets) ...")
    cid, clusters, edges = enrich.cooccurrence(ep[ep["vwap_entry"] <= 0.5], window_sec=900, min_shared=2)
    ep["cluster_id"] = ep["wallet"].map(cid)
    ep["in_cluster"] = ep["cluster_id"].notna()
    ep["cooc_bonus"] = ep["in_cluster"].astype(int) * 3

    ep["S_final"] = ep["S_base"] * ep["M_lifetime"] + ep["cooc_bonus"]
    ep = ep.sort_values("S_final", ascending=False).reset_index(drop=True)

    cols = ["S_final", "S_base", "M_lifetime", "cooc_bonus", "T", "V", "P", "A", "R",
            "wallet", "pseudonym", "slug", "win_buy_notional", "vwap_entry", "hours_before_jump",
            "lt_markets", "lt_pnl", "lt_tag", "in_cluster", "cluster_id",
            "max_single_buy", "med_notional", "n_markets", "wins", "attempts", "bio"]
    ep[cols].round(3).to_csv(config.OUTPUT_DIR / "episode_scores.csv", index=False)

    flagged = ep[ep["S_final"] >= FLAG_S]
    wal = flagged.groupby(["wallet", "pseudonym"]).agg(
        max_S_final=("S_final", "max"), max_S_base=("S_base", "max"),
        n_flagged=("slug", "nunique"), tot_notional=("win_buy_notional", "sum"),
        M_lifetime=("M_lifetime", "max"), lt_markets=("lt_markets", "max"),
        lt_pnl=("lt_pnl", "max"), lt_tag=("lt_tag", "first"),
        in_cluster=("in_cluster", "max"), cluster_id=("cluster_id", "max"),
        wins=("wins", "max"), attempts=("attempts", "max"),
    ).reset_index().sort_values(["n_flagged", "max_S_final"], ascending=False)
    wal["profile"] = "https://polymarket.com/profile/" + wal["wallet"]
    wal.round(3).to_csv(config.OUTPUT_DIR / "suspicious_accounts.csv", index=False)

    crows = []
    for i, comp in enumerate(clusters):
        sub = ep[ep["wallet"].isin(comp)]
        crows.append({"cluster_id": i, "n_wallets": len(comp),
                      "markets": sub["slug"].nunique(),
                      "tot_notional": round(sub["win_buy_notional"].sum(), 2),
                      "wallets": ";".join(sorted(comp))})
    cdf = pd.DataFrame(crows, columns=["cluster_id", "n_wallets", "markets", "tot_notional", "wallets"])
    cdf.sort_values("n_wallets", ascending=False).to_csv(config.OUTPUT_DIR / "clusters.csv", index=False)

    print(f"\n[flagged] episodes S_final>={FLAG_S}: {len(flagged)}; wallets: {wal.shape[0]}; "
          f"clusters: {len(clusters)}; clustered wallets: {len(cid)}")
    print("repeat offenders (>=2 markets):", int((wal["n_flagged"] >= 2).sum()))
    print("\nTop 15 suspicious accounts (after lifetime + cluster):")
    show = wal.head(15)[["wallet", "pseudonym", "n_flagged", "max_S_final", "max_S_base",
                         "M_lifetime", "lt_markets", "lt_pnl", "lt_tag", "in_cluster", "tot_notional"]]
    with pd.option_context("display.width", 260, "display.max_columns", 25):
        print(show.to_string(index=False))
    print("\nSynchronous clusters (>=2 wallets co-trading >=2 markets within 15min):")
    for i, comp in enumerate(clusters):
        if len(comp) >= 2:
            ps = ep[ep.wallet.isin(comp)].drop_duplicates("wallet")[["wallet", "pseudonym"]]
            print(f"  cluster {i} (n={len(comp)}): " +
                  ", ".join(f"{r.pseudonym or r.wallet[:10]}" for r in ps.itertuples()))
    con.close()


if __name__ == "__main__":
    main()
