"""Derived artifacts used by the write-up: OSINT tiers per event and top suspects per event."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd

import config
from src import controls

EVENT_ANALYSIS = config.INPUT_DIR / "event_analysis.csv"
SUSPECT_TIERS = ("HIGH", "MED-HIGH", "MED")
TOP_PER_EVENT = 10


def scored_markets():
    out = config.OUTPUT_DIR
    ev = pd.read_csv(out / "surprise_substantive.csv")[["slug", "jump_utc"]].assign(screen="event")
    seeds = pd.read_csv(out / "wallet_seed_markets.csv")[["slug", "jump_utc"]].assign(screen="wallet")
    both = set(ev["slug"]) & set(seeds["slug"])
    m = pd.concat([ev, seeds[~seeds["slug"].isin(both)]], ignore_index=True)
    m.loc[m["slug"].isin(both), "screen"] = "both"
    return m


def event_tiers():
    ev = controls.load_event_analysis(EVENT_ANALYSIS)
    m = scored_markets().merge(ev, on="slug", how="left")
    cols = ["slug", "event", "screen", "jump_utc", "event_public_time", "event_type", "private_lead",
            "tier", "M_event", "timing_verdict", "note", "source_url"]
    m["tier_order"] = m["tier"].map(controls.TIERS.index)
    return m.sort_values(["tier_order", "jump_utc", "slug"])[cols].reset_index(drop=True)


def suspects_by_event(ep):
    s = ep[ep["tier"].isin(SUSPECT_TIERS)].copy()
    s["tier_order"] = s["tier"].map(controls.TIERS.index)
    s = s.sort_values(["tier_order", "slug", "S_final", "wallet"], ascending=[True, True, False, True])
    s = s.groupby("slug", sort=False).head(TOP_PER_EVENT)
    cols = ["tier", "event", "S_final", "wallet", "pseudonym", "win_buy_notional", "vwap_entry",
            "hours_before_jump", "episode_pnl", "realized_pnl", "series_bets", "series_wins", "sib_tag",
            "lt_markets", "lt_pnl", "lt_tag", "in_cluster", "wins", "attempts", "slug", "source"]
    return s[cols].reset_index(drop=True)


def main():
    out = config.OUTPUT_DIR
    tiers = event_tiers()
    tiers.to_csv(out / "event_tiers.csv", index=False)
    ep = pd.read_csv(out / "episode_scores.csv")
    sus = suspects_by_event(ep)
    sus.round(3).to_csv(out / "suspects_by_event.csv", index=False)
    public = tiers["tier"].isin(["LOW", "LOW-MED"]).sum()
    print(f"events: {len(tiers)} ({public} public LOW/LOW-MED); "
          f"tiers: {tiers['tier'].value_counts().to_dict()}; suspects rows: {len(sus)}")


if __name__ == "__main__":
    main()
