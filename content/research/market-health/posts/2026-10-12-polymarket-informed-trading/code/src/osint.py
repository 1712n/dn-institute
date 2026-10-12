import pandas as pd


def _lifetime(client, wallet):
    pos = client.positions(wallet, limit=500) or []
    if not isinstance(pos, list) or not pos:
        return {"lt_markets": 0, "lt_pnl": 0.0, "lt_redeemable": 0.0}
    df = pd.DataFrame(pos)
    pnl = pd.to_numeric(df.get("cashPnl", 0), errors="coerce").fillna(0).sum()
    red = pd.to_numeric(df.get("redeemable", 0), errors="coerce").fillna(0).sum() \
        if "redeemable" in df else 0.0
    return {
        "lt_markets": int(df["conditionId"].nunique()) if "conditionId" in df else len(df),
        "lt_pnl": float(pnl),
        "lt_redeemable": float(red),
    }


def enrich_top(ranked, client, top_n=25):
    rows = []
    for _, r in ranked.head(top_n).iterrows():
        w = r["wallet"]
        lt = _lifetime(client, w)
        specialization = r["n_markets"] / lt["lt_markets"] if lt["lt_markets"] else 1.0
        rows.append({
            "rank": int(r["rank"]),
            "wallet": w,
            "ILS": round(float(r["ILS"]), 2),
            "pseudonym": r.get("pseudonym"),
            "profile": f"https://polymarket.com/profile/{w}",
            "slice_markets": int(r["n_markets"]),
            "slice_flagged": int(r["n_flagged"]),
            "slice_pnl": round(float(r["realized_pnl"]), 2),
            "lifetime_markets": lt["lt_markets"],
            "lifetime_pnl": round(lt["lt_pnl"], 2),
            "specialization": round(specialization, 3),
            "hit_rate": round(float(r["hit_rate"]), 3),
            "vwap_entry": round(float(r["vwap_entry_w"]), 3),
            "fwd_move": round(float(r["fwd_move_w"]), 3),
            "bio": (r.get("bio") or "")[:140],
        })
    return pd.DataFrame(rows)
