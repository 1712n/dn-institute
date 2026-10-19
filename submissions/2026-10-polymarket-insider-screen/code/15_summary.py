"""Collect every count the report quotes into one table, computed from the committed files."""
import os
import sys

import pandas as pd


def main(datadir, out):
    rows = []
    add = lambda k, v: rows.append((k, v))
    rd = lambda name, **kw: pd.read_csv(os.path.join(datadir, name), **kw)
    for k, v in rd("window_counts.csv").set_index("count")["value"].items():
        add(f"gamma_{k}", int(v))
    for k, v in rd("scope_filter_counts.csv").set_index("step")["markets"].items():
        add(f"scope_{k}", int(v))
    m = rd("markets_scope.csv", dtype={"event_id": str})
    add("markets_in_scope", len(m))
    add("events_in_scope", m["event_id"].nunique())
    add("scope_volume_musd", round(m["volumeNum"].sum() / 1e6, 1))
    add("tapes_full", int((m["tape"] == "full").sum()))
    add("trades_full", int(m["n_trades_full"].sum()))
    add("trades_in_window_pre_known", int(m["n_trades_pre_known"].sum()))
    add("trades_committed", int(m["n_trades_committed"].sum()))
    add("buy_usd_in_window_pre_known_musd", round(m["buy_usd_pre_known"].sum() / 1e6, 1))
    add("buy_usd_committed_share", round(m["buy_usd_committed"].sum() / m["buy_usd_pre_known"].sum(), 3))
    for k, n in m["t_known_source"].value_counts().sort_index().items():
        add(f"t_known_from_{k}", int(n))
    lo = pd.Timestamp("2025-11-01", tz="UTC").timestamp()
    add("markets_known_before_window", int((m["t_known"] <= lo).sum()))
    add("markets_with_committed_trades", int((m["n_trades_committed"] > 0).sum()))
    w = rd("wallets.csv.gz")
    add("wallets_over_floor", len(w))
    for s, n in w["status"].value_counts().sort_index().items():
        add(f"wallets_{s}", int(n))
    rc = rd("replay_check.csv")
    add("replay_events", len(rc))
    add("replay_events_unreachable", int((~rc["real_outcome_reachable"]).sum()))
    add("replay_unreachable_usd_share", round(rc.loc[~rc["real_outcome_reachable"], "usd"].sum() / rc["usd"].sum(), 4))
    rk = rd("wallet_ranking_full.csv.gz")
    add("ranked_wallets", len(rk))
    add("ranked_profitable", int((rk["pnl"] > 0).sum()))
    rv = rd("review_wallets.csv")
    add("review_wallets", len(rv))
    add("review_events", rv["top_event"].nunique())
    for ev, n in rv["top_event"].value_counts().head(5).items():
        add(f"review_top_event_{ev}", int(n))
    add("review_fresh_1d", int((rv["days_since_first_activity"] < 1).sum()))
    add("review_in_lockstep_group", int(rv["lockstep_group"].notna().sum()))
    add("review_named", int(rv["named_case"].notna().sum()))
    add("tested_fresh_1d_share", round((rk["days_since_first_activity"] < 1).mean(), 3))
    lp = rd("lockstep_pairs.csv.gz")
    lg = rd("lockstep_groups.csv")
    add("lockstep_pairs", len(lp))
    add("lockstep_groups", len(lg))
    add("lockstep_wallets", int(lg["size"].sum()))
    t = lg[lg["set_up_together"]]
    add("groups_set_up_together", len(t))
    for _, g in t.iterrows():
        k = f"group_{int(g['group'])}"
        add(f"{k}_size", int(g["size"]))
        add(f"{k}_pnl", round(g["pnl"]))
        add(f"{k}_members_in_profit", int(g["members_in_profit"]))
        add(f"{k}_first_activity_min", g["first_activity_min"])
        add(f"{k}_first_activity_max", g["first_activity_max"])
        add(f"{k}_top_event", g["top_event"])
    for _, c in rd("control.csv").iterrows():
        add(f"control_shift{int(c['shift_days'])}_at_or_above_cut", int(c["wallets_at_or_above_cut"]))
        add(f"control_shift{int(c['shift_days'])}_review_list_still_in_top", int(c["review_list_still_in_top"]))
    kr = rd("known_case_recall.csv")
    add("named_accounts", len(kr))
    add("named_tested", int((kr["status"] == "tested").sum()))
    add("named_in_review_list", int(kr["in_review_list"].sum()))
    pd.DataFrame(rows, columns=["key", "value"]).to_csv(out, index=False)
    for k, v in rows:
        print(k, v)


if __name__ == "__main__":
    main(*sys.argv[1:3])
