import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import duckdb
import numpy as np
import pandas as pd

import config

MECH = (r"tweets|truth-social-posts|-posts-|will-trump-say|-say-|mention|shake-hands|"
        r"photographed|fact-check|of-truth-social|turnout|number-of")

JUMP_LEVEL = 0.80          # winner price at which the market has absorbed the outcome
JUMP_CONFIRM_TRADES = 20   # the move must hold: median of the next N trades stays above the level
EARLY_FRAC = 0.2           # p_early = winner VWAP over the first 20% of the collected tape
LATE_FRAC = 0.9            # p_late  = winner VWAP over the last 10%
MAX_EARLY_PRICE = 0.55
MIN_LATE_PRICE = 0.80
MIN_VOLUME = 50_000
MIN_TRADES = 100
TOP_N = 60
TRUNCATION_TRADES = 9_000  # data-api serves only the newest ~10k trades of a market


def detect_jump(ts, wp, level=JUMP_LEVEL, confirm=JUMP_CONFIRM_TRADES):
    """Index of the first trade of the final sustained move above `level`, or None.

    A trade starts the jump if from there on the forward median of `confirm` trades never
    falls back below `level`; isolated prints and short-lived spikes are ignored.
    """
    if len(wp) == 0:
        return None
    fwd_median = pd.Series(wp[::-1]).rolling(confirm, min_periods=1).median().to_numpy()[::-1]
    low = np.flatnonzero(fwd_median < level)
    start = low[-1] + 1 if len(low) else 0
    above = np.flatnonzero(wp[start:] >= level)
    return int(start + above[0]) if len(above) else None


def summarize_market(ts, wp, size):
    span = ts[-1] - ts[0]
    frac = (ts - ts[0]) / span if span > 0 else np.ones(len(ts))
    early, late = frac <= EARLY_FRAC, frac >= LATE_FRAC
    j = detect_jump(ts, wp)
    return {
        "p_early": float(np.average(wp[early], weights=size[early])) if size[early].sum() > 0 else np.nan,
        "p_late": float(np.average(wp[late], weights=size[late])) if size[late].sum() > 0 else np.nan,
        "jump_ts": int(ts[j]) if j is not None else np.nan,
        "p_post": float(np.average(wp[j:], weights=size[j:])) if j is not None else np.nan,
    }


def in_window(jump_ts):
    start = pd.Timestamp(config.WINDOW_START).timestamp()
    end = pd.Timestamp(config.WINDOW_END).timestamp()
    return (jump_ts >= start) & (jump_ts < end)


def market_paths(con, condition_ids=None, min_volume=MIN_VOLUME, min_trades=MIN_TRADES):
    """Per-market summary of the winner's price path, reconstructed from the trade tape."""
    markets = con.execute("""
        SELECT m.condition_id, m.slug, m.question, m.win_outcome wout, m.volume,
               coalesce(m.trades_capped, false) trades_capped, m.end_date, count(*) n_tr
        FROM markets m JOIN trades t USING (condition_id)
        WHERE m.volume >= ?
        GROUP BY ALL HAVING count(*) >= ?
        ORDER BY m.condition_id""", [min_volume, min_trades]).df()
    if condition_ids is not None:
        markets = markets[markets["condition_id"].isin(set(condition_ids))]
    if markets.empty:
        return markets
    con.register("cand", markets[["condition_id"]])
    tape = con.execute("""
        SELECT t.condition_id, t.timestamp ts, t.size,
               CASE WHEN t.outcome_index = m.win_index THEN t.price ELSE 1 - t.price END wp
        FROM trades t JOIN markets m USING (condition_id)
        WHERE t.condition_id IN (SELECT condition_id FROM cand)
        ORDER BY t.condition_id, t.timestamp, t.tx_hash, t.wallet, t.price, t.size""").df()
    con.unregister("cand")
    rows = {cid: summarize_market(g["ts"].to_numpy(), g["wp"].to_numpy(), g["size"].to_numpy())
            for cid, g in tape.groupby("condition_id", sort=False)}
    det = pd.DataFrame.from_dict(rows, orient="index").rename_axis("condition_id").reset_index()
    df = markets.merge(det, on="condition_id")
    df["history_truncated"] = df["trades_capped"] | (df["n_tr"] >= TRUNCATION_TRADES)
    df["jump_utc"] = pd.to_datetime(df["jump_ts"], unit="s").dt.strftime("%Y-%m-%d %H:%M")
    return df


def detect(con):
    df = market_paths(con)
    if df.empty:
        return pd.DataFrame()
    df = df[(df["p_early"] <= MAX_EARLY_PRICE) & (df["p_late"] >= MIN_LATE_PRICE)
            & df["jump_ts"].notna() & in_window(df["jump_ts"])].copy()
    df["swing"] = df["p_late"] - df["p_early"]
    df = df.sort_values(["swing", "volume", "slug"], ascending=[False, False, True])
    cols = ["slug", "question", "wout", "volume", "history_truncated", "n_tr", "p_early", "p_late",
            "swing", "jump_ts", "jump_utc", "end_date"]
    out = df[cols].rename(columns={"volume": "vol"}).reset_index(drop=True)
    out["vol"] = out["vol"].round()
    out["jump_ts"] = out["jump_ts"].astype("int64")
    return out.round({"p_early": 3, "p_late": 3, "swing": 3})


def substantive(df):
    return df[~df["slug"].str.contains(MECH, case=False, regex=True)].copy()


def main():
    con = duckdb.connect(str(config.DB_PATH), read_only=True)
    df = detect(con).head(TOP_N)
    con.close()
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.OUTPUT_DIR / "surprise_markets.csv", index=False)
    sub = substantive(df)
    sub.to_csv(config.OUTPUT_DIR / "surprise_substantive.csv", index=False)
    print(f"surprise markets: {len(df)}; substantive: {len(sub)}; "
          f"truncated history: {int(df['history_truncated'].sum())}")


if __name__ == "__main__":
    main()
