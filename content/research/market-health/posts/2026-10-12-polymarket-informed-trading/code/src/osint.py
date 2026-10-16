import pandas as pd


def _lifetime(client, wallet):
    pos = client.positions(wallet, limit=500)
    if pos is None:
        raise RuntimeError(f"positions lookup failed for {wallet}")
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

