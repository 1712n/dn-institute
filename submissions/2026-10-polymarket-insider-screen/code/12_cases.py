"""Write the review files for the top of the ranking.

review_wallets.csv        the first REVIEW wallets of the ranking, with first Polymarket activity,
                          lockstep group (11_lockstep.py) and the named case, if any.
review_positions.csv.gz   one row per review wallet and market: what it bought, when, and how long
                          before the outcome became known.
review_trades.csv.gz      every committed trade of the review wallets, of the named accounts and
                          of the groups set up together, with UTC times.
case_price_paths.csv.gz   hourly price of the winning token in the markets of each of those
                          wallets' largest event, from the committed tape.
"""
import importlib.util
import json
import os
import sys

import pandas as pd

GZ = {"method": "gzip", "mtime": 0}


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(__file__), name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


features, scoring = load("06_features"), load("10_score")


def utc(s):
    return pd.to_datetime(s, unit="s", utc=True).dt.strftime("%Y-%m-%d %H:%M:%S")


def main(datadir, outdir):
    scope = features.read_scope(datadir)
    wallets = pd.read_csv(os.path.join(datadir, "wallets.csv.gz"))
    wm = pd.read_csv(os.path.join(datadir, "wallet_market.csv.gz"), dtype={"event_id": str})
    rk = pd.read_csv(os.path.join(datadir, "wallet_ranking_full.csv.gz"))
    fa = pd.read_csv(os.path.join(datadir, "wallet_first_activity.csv.gz"))
    grp = pd.read_csv(os.path.join(datadir, "lockstep_groups.csv"))
    kc = pd.read_csv(os.path.join(datadir, "known_cases.csv"))

    member = {a: g for g, ms in zip(grp["group"], grp["members"]) for a in ms.split(";")}
    named = dict(zip(kc["address"].str.lower(), kc["case"]))
    rev = rk[rk["rank"] <= scoring.REVIEW].merge(fa, on="wallet", how="left")
    rev["first_activity_utc"] = utc(rev["first_activity_ts"].astype(float))
    rev["lockstep_group"] = rev["wallet"].map(member).astype("Int64")
    rev["named_case"] = rev["wallet"].map(named).fillna("")
    rev[["rank", "wallet", "score", "pnl", "cost", "early_longshot_usd", "clean_share", "n_events", "top_event",
         "first_activity_utc", "days_since_first_activity", "lockstep_group", "named_case"]].round(4).to_csv(
        os.path.join(outdir, "review_wallets.csv"), index=False)

    ids = wallets.dropna(subset=["w"]).astype({"w": int}).set_index("wallet")["w"]
    rw = rev.assign(w=rev["wallet"].map(ids))
    pos = wm[wm["w"].isin(rw["w"])].merge(rw[["w", "wallet", "rank"]], on="w")
    pos = pos.merge(scope[["m", "question", "event_slug", "t_known", "closedTime", "winner_index", "outcomes"]],
                    on=["m", "winner_index"])
    pos["winner"] = [json.loads(o)[i] for o, i in zip(pos["outcomes"], pos["winner_index"])]
    pos["first_buy_utc"] = utc(pos["first_ts"])
    pos["t_known_utc"] = utc(pos["t_known"])
    pos["hours_first_buy_to_known"] = (pos["t_known"] - pos["first_ts"]) / 3600
    pos = pos.sort_values(["rank", "pnl"], ascending=[True, False])
    pos[["rank", "wallet", "event_slug", "question", "winner", "win_buy_usd", "lose_buy_usd", "early_longshot_usd",
         "pnl", "first_buy_utc", "t_known_utc", "closedTime", "hours_first_buy_to_known", "win_lead_h_usdw"]].round(4).to_csv(
        os.path.join(outdir, "review_positions.csv.gz"), index=False, compression=GZ)

    together = [a for ms in grp.loc[grp["set_up_together"], "members"] for a in ms.split(";")]
    pick = set(rev["wallet"]) | set(kc["address"].str.lower()) | set(together)
    pick_w = ids.reindex(sorted(pick)).dropna().astype(int)
    tape = features.read_tape(datadir)
    tt = tape[tape["w"].isin(pick_w)].merge(pd.DataFrame({"w": pick_w.to_numpy(), "wallet": pick_w.index}), on="w")
    tt = tt.merge(scope[["m", "question", "outcomes", "t_known"]], on="m")
    tt["outcome"] = [json.loads(o)[i] for o, i in zip(tt["outcomes"], tt["o"])]
    tt["usd"] = tt["size"] * tt["price"]
    tt["utc"] = utc(tt["ts"])
    tt["hours_before_known"] = (tt["t_known"] - tt["ts"]) / 3600
    tt = tt.sort_values(["wallet", "ts", "m", "o", "side", "size"])
    tt[["wallet", "utc", "question", "outcome", "side", "price", "size", "usd", "hours_before_known"]].round(4).to_csv(
        os.path.join(outdir, "review_trades.csv.gz"), index=False, compression=GZ)

    top_ev = wm[wm["w"].isin(pick_w)].groupby(["w", "event_id"])["cost"].sum().reset_index()
    top_ev = top_ev.sort_values(["w", "cost", "event_id"], ascending=[True, False, True]).drop_duplicates("w")
    ms = set(scope.loc[scope["event_id"].isin(top_ev["event_id"]), "m"])
    p = tape[tape["m"].isin(ms)].merge(scope[["m", "winner_index", "question"]], on="m")
    p = p[p["o"] == p["winner_index"]]
    p["h"] = (p["ts"] // 3600) * 3600
    p["usd"] = p["size"] * p["price"]
    g = p.groupby(["m", "question", "h"])
    path = (g["usd"].sum() / g["size"].sum()).rename("winner_vwap").reset_index()
    path["usd"] = g["usd"].sum().to_numpy()
    path["hour_utc"] = utc(path["h"])
    path[["question", "hour_utc", "winner_vwap", "usd"]].round(4).to_csv(
        os.path.join(outdir, "case_price_paths.csv.gz"), index=False, compression=GZ)
    print(len(rev), "review wallets;", len(pos), "positions;", len(tt), "trades of", len(pick_w), "wallets;",
          len(path), "price path rows;", int(rev["lockstep_group"].notna().sum()), "review wallets in a lockstep group;",
          int((rev["named_case"] != "").sum()), "named")


if __name__ == "__main__":
    main(*sys.argv[1:3])
