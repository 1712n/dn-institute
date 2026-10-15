"""False-positive controls applied to scored episodes.

1. Survivorship / base rate: did the wallet buy the same cheap outcome across the sibling
   markets of a series ("strike on <date>", "out by <month>") and win only once?
2. Event publicity: an OSINT tier per event, derived by rule from recorded facts.
"""
import json
import re

import pandas as pd

FAN_MIN_BETS = 3           # bets across the series, target market included
FAN_MAX_HIT_RATE = 1 / 3
FAN_MULT = 0.5
SIB_MAX_VWAP = 0.5         # a "cheap" bet, same definition as the record score R
SIB_MIN_NOTIONAL = 5.0       # tail bets are small by design; only dust is ignored

TIERS = ["HIGH", "MED-HIGH", "MED", "LOW-MED", "LOW"]
TIER_MULT = {"HIGH": 1.0, "MED-HIGH": 0.85, "MED": 0.7, "LOW-MED": 0.45, "LOW": 0.3}

# Base tier by what kind of fact resolved the market. A fact that existed privately before
# it was disclosed (a call that happened a week before it was reported, a planned strike)
# moves the event one tier up.
EVENT_TYPES = {
    "election": "LOW",               # vote counts, exit polls
    "legislative_vote": "LOW",       # recorded floor votes
    "public_statement": "LOW",       # speeches, posts, appearances
    "deadline_lapse": "LOW",         # resolved No because nothing happened by the deadline
    "public_military": "LOW",        # strike series announced or visible in real time
    "public_process": "LOW-MED",     # nominations, filings, scheduled releases
    "diplomacy": "LOW-MED",          # meetings and talks that are announced beforehand
    "executive_decision": "MED",     # pardons, declassification, orders
    "battlefield": "MED",            # front-line captures
    "military_strike": "MED",        # one-off strikes and operations
    "private_communication": "MED-HIGH",
    "covert_military": "HIGH",       # covert operations under operational secrecy
}


MONTHS = "january|february|march|april|may|june|july|august|september|october|november|december"


# Ladders on the same underlying event that Polymarket runs as separate series.
SERIES_FAMILIES = {s: "strike-on-iran" for s in [
    "israel-strikes-iran-by", "us-strikes-iran-by", "us-next-strikes-iran-on",
    "usisrael-strikes-iran-on", "when-will-the-us-next-strike-iran-week"]}


def series_stem(event_slug):
    """Key that groups the markets of one date series.

    Polymarket splits a series over several event slugs ('...-on-312', '...-on-843') and
    sometimes gives every date of a deadline ladder its own event
    ('israel-strikes-iran-by-january-9-2026'), so both suffixes are dropped.
    """
    stem = re.sub(r"(-\d{3})+$", "", str(event_slug))
    stem = re.sub(rf"-({MONTHS})-\d{{1,2}}(-\d{{4}})?$", "", stem)
    return SERIES_FAMILIES.get(stem, stem)


def sibling_multiplier(bets, wins, has_series):
    if not has_series:
        return 1.0, "standalone"
    if bets >= FAN_MIN_BETS and wins / bets <= FAN_MAX_HIT_RATE:
        return FAN_MULT, "fan_bettor"
    return 1.0, "targeted"


def _market_series(con):
    mk = con.execute("SELECT condition_id, slug, event_slug, win_index, outcomes FROM markets "
                     "ORDER BY condition_id").df()
    mk["stem"] = [series_stem(e if isinstance(e, str) and e else s)
                  for e, s in zip(mk["event_slug"], mk["slug"])]
    mk["labels"] = mk["outcomes"].map(json.loads)
    return mk


def sibling_record(con, episodes):
    """Add series_bets / series_wins / sib_tag / M_sibling to (wallet, condition_id) episodes.

    A bet is a cheap buy of the outcome with the same label as the target's winner ("Yes" on
    another date) placed before the target's jump, whether or not it was held to resolution.
    The target itself counts as one won bet.
    """
    mk = _market_series(con).set_index("condition_id")
    pairs = []
    n_siblings = {}
    for cid in episodes["condition_id"].unique():
        t = mk.loc[cid]
        label = t["labels"][int(t["win_index"])]
        sibs = mk[(mk["stem"] == t["stem"]) & (mk.index != cid)]
        n_siblings[cid] = len(sibs)
        for sid, s in sibs.iterrows():
            if label in s["labels"]:
                pairs.append({"tgt_cid": cid, "sib_cid": sid, "label_idx": s["labels"].index(label),
                              "won": s["labels"].index(label) == int(s["win_index"])})
    sib = pd.DataFrame(columns=["wallet", "condition_id", "sib_bets", "sib_wins"])
    if pairs:
        pr = pd.DataFrame(pairs).merge(
            episodes[["wallet", "condition_id", "jump_ts"]].rename(columns={"condition_id": "tgt_cid"}),
            on="tgt_cid")
        con.register("pairs_df", pr)
        sib = con.execute("""
            WITH bets AS (
                SELECT p.wallet, p.tgt_cid, p.sib_cid, p.won,
                       round(sum(t.size * t.price), 6) usd, round(sum(t.size), 6) sh
                FROM pairs_df p JOIN trades t
                  ON t.condition_id = p.sib_cid AND t.wallet = p.wallet AND t.side = 'BUY'
                 AND t.outcome_index = p.label_idx AND t.timestamp < p.jump_ts
                GROUP BY 1, 2, 3, 4)
            SELECT wallet, tgt_cid condition_id, count(*) sib_bets,
                   sum(CASE WHEN won THEN 1 ELSE 0 END) sib_wins
            FROM bets WHERE usd >= ? AND round(usd / sh, 9) <= ?
            GROUP BY 1, 2""", [SIB_MIN_NOTIONAL, SIB_MAX_VWAP]).df()
        con.unregister("pairs_df")

    out = episodes.merge(sib, on=["wallet", "condition_id"], how="left")
    out["series_bets"] = out["sib_bets"].fillna(0).astype(int) + 1
    out["series_wins"] = out["sib_wins"].fillna(0).astype(int) + 1
    res = [sibling_multiplier(b, w, n_siblings[c] > 0) for b, w, c in
           zip(out["series_bets"], out["series_wins"], out["condition_id"])]
    out["M_sibling"] = [m for m, _ in res]
    out["sib_tag"] = [t for _, t in res]
    return out.drop(columns=["sib_bets", "sib_wins"])


def event_tier(event_type, private_lead):
    base = EVENT_TYPES[event_type]
    if private_lead:
        return TIERS[max(TIERS.index(base) - 1, 0)]
    return base


def load_event_analysis(path):
    ev = pd.read_csv(path)
    unknown = sorted(set(ev["event_type"]) - set(EVENT_TYPES))
    if unknown:
        raise ValueError(f"unknown event_type in {path}: {unknown}")
    if ev["slug"].duplicated().any():
        raise ValueError(f"duplicate slugs in {path}")
    ev["private_lead"] = ev["private_lead"].astype(str).str.lower().isin(["true", "1", "yes"])
    ev["tier"] = [event_tier(t, p) for t, p in zip(ev["event_type"], ev["private_lead"])]
    ev["M_event"] = ev["tier"].map(TIER_MULT).astype(float)
    return ev
