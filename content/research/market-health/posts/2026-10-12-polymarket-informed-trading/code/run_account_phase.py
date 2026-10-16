import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import duckdb
import numpy as np
import pandas as pd

import config
from src import controls
from src import enrich
from src import episode_score as es

DB = str(config.DB_PATH)
MIN_EPISODE_NOTIONAL = 100.0
FLAG_S = 12
EXCLUDE_SLUGS = ("claude", "hegseth-ban")  # novelty markets with no information content
EVENT_ANALYSIS = config.INPUT_DIR / "event_analysis.csv"
POST_PUBLIC_SHARE = 0.5   # episode mostly bought after the first public signal = news reaction
POST_PUBLIC_MULT = controls.TIER_MULT["LOW"]
# A wallet created days before its bet has no history to compare the bet against, so its
# relative size (V, A) is taken at the cap when the bet is a large long shot.
FRESH_MAX_AGE_DAYS = 7      # first Polymarket activity at most this long before the first buy
FRESH_MAX_VWAP = 0.25
FRESH_MIN_NOTIONAL = 1000.0


def load_targets():
    """Union of the event screen and the wallet screen; one row per market."""
    cols = ["slug", "jump_ts", "p_late"]
    ev = pd.read_csv(config.OUTPUT_DIR / "surprise_substantive.csv")[cols].assign(source="event_screen")
    seed_path = config.OUTPUT_DIR / "wallet_seed_markets.csv"
    seeds = pd.read_csv(seed_path)[cols].assign(source="wallet_screen") if seed_path.exists() \
        else pd.DataFrame(columns=cols + ["source"])
    both = set(ev["slug"]) & set(seeds["slug"])
    tg = pd.concat([ev, seeds[~seeds["slug"].isin(both)]], ignore_index=True)
    tg.loc[tg["slug"].isin(both), "source"] = "both"
    mask = tg["slug"].str.lower().str.contains("|".join(EXCLUDE_SLUGS))
    return tg[~mask & tg["jump_ts"].notna()].reset_index(drop=True)


def targets(con, tg):
    con.register("tg_df", tg)
    out = con.execute("""
        SELECT m.condition_id, m.slug, m.question, m.win_outcome, m.win_index,
               m.volume, m.trades_capped, s.jump_ts, s.p_late, s.source
        FROM markets m JOIN tg_df s USING (slug)
        ORDER BY m.slug""").df()
    con.unregister("tg_df")
    return out


def attach_public_time(tg, path=EVENT_ANALYSIS):
    """public_ts = first public signal of the event (OSINT), or the jump if none is recorded.

    For most events the market jump is the first public moment. Where news broke earlier
    (explosions in Caracas hours before the capture was announced) the earlier time is used.
    """
    ev = pd.read_csv(path).set_index("slug")
    first = pd.to_datetime(tg["slug"].map(ev["first_public_utc"]), utc=True, errors="coerce")
    first_ts = (first - pd.Timestamp("1970-01-01", tz="UTC")).dt.total_seconds()
    tg = tg.copy()
    tg["public_ts"] = np.fmin(tg["jump_ts"].astype(float), first_ts.fillna(np.inf))
    return tg


def global_baselines(con):
    base = con.execute("""
        SELECT wallet, round(median(size*price), 6) med_notional, count(*) n_trades,
               count(DISTINCT condition_id) n_markets, round(sum(size*price), 6) tot_notional
        FROM trades WHERE side='BUY' GROUP BY 1""").df()
    base["avg_market_notional"] = base["tot_notional"] / base["n_markets"].clip(lower=1)

    bets = con.execute("""
        WITH pos AS (
            SELECT t.wallet, t.condition_id, t.outcome_index,
                   round(sum(CASE WHEN t.side='BUY' THEN t.size ELSE -t.size END), 6) net_shares,
                   round(sum(CASE WHEN t.side='BUY' THEN t.size*t.price ELSE 0 END), 6) buy_notional,
                   round(sum(CASE WHEN t.side='BUY' THEN t.size ELSE 0 END), 6) buy_shares
            FROM trades t GROUP BY 1,2,3)
        SELECT p.wallet, p.condition_id, bool_or(p.outcome_index=m.win_index) won
        FROM pos p JOIN markets m USING(condition_id)
        WHERE p.net_shares>0 AND p.buy_notional>=100
          AND round(p.buy_notional/NULLIF(p.buy_shares,0), 9) <= 0.5
        GROUP BY 1, 2""").df()
    return base, bets


def record_excluding_own(ep, bets):
    """Cheap-bet record per episode, leaving out the market being scored."""
    tot = bets.groupby("wallet").agg(attempts=("won", "size"), wins=("won", "sum")).reset_index()
    own = bets.rename(columns={"won": "own_won"})
    out = ep[["wallet", "condition_id"]].merge(tot, on="wallet", how="left")
    out = out.merge(own, on=["wallet", "condition_id"], how="left")
    out[["attempts", "wins"]] = out[["attempts", "wins"]].fillna(0)
    has_own = out["own_won"].notna()
    out.loc[has_own, "attempts"] -= 1
    out.loc[has_own, "wins"] -= out.loc[has_own, "own_won"].astype(bool).astype(int)
    out[["attempts", "wins"]] = out[["attempts", "wins"]].astype(int)
    return out.drop(columns=["own_won"])


def realized_pnl(shares, notional, sells):
    """Profit of an episode as traded: winner sales after the first buy are matched to the
    episode's shares in time order (first in, first out) at their sale price; shares not sold
    pay $1 at resolution. Sales beyond the episode's shares belong to later buys and are ignored."""
    sold_before = sells["size"].cumsum().shift(fill_value=0)
    taken = (shares - sold_before).clip(lower=0).clip(upper=sells["size"])
    return (taken * sells["price"]).sum() + (shares - taken.sum()) - notional


def episodes(con, tg):
    con.register("tgt", tg[["condition_id"]])
    tr = con.execute("""
        SELECT t.condition_id, t.wallet, t.side, t.size, t.price, t.timestamp, t.outcome_index,
               t.pseudonym, t.name, t.bio
        FROM trades t WHERE t.condition_id IN (SELECT condition_id FROM tgt)
        ORDER BY t.condition_id, t.wallet, t.timestamp, t.price, t.size""").df()
    con.unregister("tgt")
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
        ws = g[(g["outcome_index"] == win) & (g["side"] == "SELL")]
        public = float(meta.at[cid, "public_ts"])
        for w, b in wb.groupby("wallet"):
            notional = b["notional"].sum()
            if notional < MIN_EPISODE_NOTIONAL:
                continue
            shares = b["size"].sum()
            vwap = notional / shares
            vwt = (b["size"] * b["timestamp"]).sum() / shares
            first = float(b["timestamp"].min())
            realized = realized_pnl(shares, notional, ws[(ws["wallet"] == w) & (ws["timestamp"] >= first)])
            rows.append({
                "condition_id": cid, "slug": meta.at[cid, "slug"], "source": meta.at[cid, "source"],
                "jump_ts": jump,
                "wallet": w, "pseudonym": b["pseudonym"].iloc[0], "bio": b["bio"].iloc[0],
                "win_buy_notional": notional, "max_single_buy": b["notional"].max(),
                "shares": shares, "vwap_entry": vwap, "episode_pnl": shares - notional,
                "realized_pnl": realized,
                "entry_ts": float(vwt), "first_ts": first,
                "last_buy_ts": float(b["timestamp"].max()),
                "hours_before_jump": (jump - vwt) / 3600.0,
                "p_edge": p_late - vwap, "n_buys": len(b),
                "hours_before_public": (public - vwt) / 3600.0,
                "post_public_share": float(b.loc[b["timestamp"] >= public, "notional"].sum() / notional),
            })
    return pd.DataFrame(rows)


def public_timing(ep):
    """Time T against the first public signal; demote episodes bought mostly after it."""
    ep = ep.copy()
    ep["t_hours"] = ep["hours_before_public"]
    ep["M_public"] = np.where(ep["post_public_share"] > POST_PUBLIC_SHARE, POST_PUBLIC_MULT, 1.0)
    return ep


def fresh_candidates(ep):
    return (ep["vwap_entry"] <= FRESH_MAX_VWAP) & (ep["win_buy_notional"].round(2) >= FRESH_MIN_NOTIONAL)


def attach_wallet_age(ep):
    ep = ep.copy()
    ep["wallet_age_days"] = (ep["first_ts"] - ep["first_activity_ts"]) / 86400.0
    ep["fresh_bet"] = fresh_candidates(ep) & (ep["wallet_age_days"].round(6) <= FRESH_MAX_AGE_DAYS)
    return ep


def cap_fresh_size(ep):
    ep = ep.copy()
    ep.loc[ep["fresh_bet"], ["v_ratio", "a_ratio"]] = np.inf
    return ep


def attach_event_tiers(ep, path=EVENT_ANALYSIS):
    ev = controls.load_event_analysis(path)
    missing = sorted(set(ep["slug"]) - set(ev["slug"]))
    if missing:
        raise ValueError(f"no OSINT row in {path.name} for: {missing}")
    return ep.merge(ev[["slug", "event", "tier", "M_event"]], on="slug", how="left")


def rank_wallets(flagged):
    wal = flagged.groupby(["wallet"], dropna=False).agg(
        pseudonym=("pseudonym", "first"),
        max_S_final=("S_final", "max"), max_S_base=("S_base", "max"),
        n_flagged=("slug", "nunique"), tot_notional=("win_buy_notional", "sum"),
        tot_episode_pnl=("episode_pnl", "sum"), tot_realized_pnl=("realized_pnl", "sum"),
        M_lifetime=("M_lifetime", "max"), M_sibling=("M_sibling", "min"), M_event=("M_event", "max"),
        M_public=("M_public", "max"),
        lt_markets=("lt_markets", "max"), lt_pnl=("lt_pnl", "max"), lt_tag=("lt_tag", "first"),
        top_tier=("tier", lambda s: min(s, key=controls.TIERS.index)),
        sib_tag=("sib_tag", "first"),
        in_cluster=("in_cluster", "max"), cluster_id=("cluster_id", "max"),
        wins=("wins", "max"), attempts=("attempts", "max"),
    ).reset_index()
    wal = wal.sort_values(["n_flagged", "tot_realized_pnl", "wallet"], ascending=[False, False, True])
    wal.insert(0, "rank", np.arange(1, len(wal) + 1))
    wal["profile"] = "https://polymarket.com/profile/" + wal["wallet"]
    return wal.reset_index(drop=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="use cached lifetime profiles only")
    args = ap.parse_args()

    con = duckdb.connect(DB, read_only=True)
    tg = attach_public_time(targets(con, load_targets()))
    print(f"[targets] {len(tg)} markets "
          f"({tg['source'].value_counts().to_dict()})")

    print("[baselines] computing global per-wallet stats over the full trade tape ...")
    base, bets = global_baselines(con)
    print(f"[baselines] wallets with buys: {len(base):,}; cheap bets: {len(bets):,}")

    ep = episodes(con, tg)
    print(f"[episodes] pre-jump winning-side episodes: {len(ep):,}")

    ep = ep.merge(base[["wallet", "med_notional", "avg_market_notional", "n_markets", "n_trades"]],
                  on="wallet", how="left")
    ep = ep.merge(record_excluding_own(ep, bets), on=["wallet", "condition_id"], how="left")
    ep["v_ratio"] = ep["max_single_buy"] / ep["med_notional"].replace(0, np.nan)
    ep["a_ratio"] = ep["win_buy_notional"] / ep["avg_market_notional"].replace(0, np.nan)
    ep = public_timing(ep)

    print("[enrich] wallet age for large long shots ...")
    fa = enrich.first_activity(ep.loc[fresh_candidates(ep), "wallet"].unique(), offline=args.offline)
    ep = cap_fresh_size(attach_wallet_age(ep.merge(fa, on="wallet", how="left")))
    print(f"[fresh] bets placed by wallets at most {FRESH_MAX_AGE_DAYS} days old: {int(ep['fresh_bet'].sum())}")

    sc = ep.apply(es.score_row, axis=1)
    ep = pd.concat([ep, sc], axis=1)
    ep = ep.rename(columns={"S": "S_base"})

    print("[enrich] lifetime profiles ...")
    lt = enrich.lifetime_profiles(ep["wallet"].unique(), offline=args.offline)
    ep = ep.merge(lt, on="wallet", how="left")
    mt = ep.apply(lambda r: enrich.lifetime_multiplier(r["lt_markets"], r["lt_pnl"]), axis=1)
    ep["M_lifetime"] = [m for m, _ in mt]
    ep["lt_tag"] = [t for _, t in mt]

    print("[controls] sibling-series base rate + OSINT event tiers ...")
    ep = controls.sibling_record(con, ep)
    ep = attach_event_tiers(ep)
    con.close()

    print("[enrich] co-occurrence clustering (synchronous wallets) ...")
    ep = ep.sort_values(["slug", "entry_ts", "wallet"]).reset_index(drop=True)
    cid, clusters, edges = enrich.cooccurrence(ep[ep["vwap_entry"] <= 0.5], window_sec=900, min_shared=2)
    ep["cluster_id"] = ep["wallet"].map(cid)
    ep["in_cluster"] = ep["cluster_id"].notna()
    ep["cooc_bonus"] = ep["in_cluster"].astype(int) * 3

    ep["S_final"] = (ep["S_base"] * ep["M_lifetime"] * ep["M_sibling"] * ep["M_event"] * ep["M_public"]
                     + ep["cooc_bonus"])
    ep = ep.sort_values(["S_final", "wallet", "slug"], ascending=[False, True, True]).reset_index(drop=True)

    cols = ["S_final", "S_base", "M_lifetime", "M_sibling", "M_event", "M_public", "cooc_bonus",
            "T", "V", "P", "A", "R", "wallet", "pseudonym", "slug", "source", "event", "tier",
            "win_buy_notional", "vwap_entry", "episode_pnl", "realized_pnl", "hours_before_jump",
            "first_ts", "last_buy_ts", "jump_ts", "hours_before_public", "post_public_share",
            "series_bets", "series_wins", "sib_tag", "fresh_bet", "wallet_age_days",
            "lt_markets", "lt_pnl", "lt_tag", "in_cluster", "cluster_id",
            "max_single_buy", "med_notional", "n_markets", "wins", "attempts", "bio"]
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ep[cols].round(3).to_csv(config.OUTPUT_DIR / "episode_scores.csv", index=False)

    flagged = ep[ep["S_final"] >= FLAG_S]
    wal = rank_wallets(flagged)
    wal.round(3).to_csv(config.OUTPUT_DIR / "suspicious_accounts.csv", index=False)

    crows = []
    for i, comp in enumerate(clusters):
        sub = ep[ep["wallet"].isin(comp)]
        crows.append({"cluster_id": i, "n_wallets": len(comp),
                      "markets": sub["slug"].nunique(),
                      "tot_notional": round(sub["win_buy_notional"].sum(), 2),
                      "wallets": ";".join(sorted(comp))})
    cdf = pd.DataFrame(crows, columns=["cluster_id", "n_wallets", "markets", "tot_notional", "wallets"])
    cdf.sort_values(["n_wallets", "cluster_id"], ascending=[False, True]).to_csv(
        config.OUTPUT_DIR / "clusters.csv", index=False)

    print(f"\n[flagged] episodes S_final>={FLAG_S}: {len(flagged)}; wallets: {wal.shape[0]}; "
          f"clusters: {len(clusters)}; clustered wallets: {len(cid)}")
    print("fan bettors demoted:", int((ep["sib_tag"] == "fan_bettor").sum()))
    print("\nTop 15 suspicious accounts:")
    show = wal.head(15)[["rank", "wallet", "pseudonym", "n_flagged", "max_S_final", "max_S_base",
                         "M_lifetime", "M_sibling", "top_tier", "lt_tag", "tot_realized_pnl"]]
    with pd.option_context("display.width", 260, "display.max_columns", 25):
        print(show.to_string(index=False))


if __name__ == "__main__":
    main()
