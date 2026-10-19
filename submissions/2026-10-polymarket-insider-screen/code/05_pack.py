"""Cut the raw tapes down to the committed dataset.

It stops if 04_trades.py marked any tape incomplete. For every scoped market it fixes the moment
the outcome became known and keeps only trades placed before it. Four clocks are read and the
earliest one wins:

  settle   the start of the first ten-minute bucket with at least MIN_PRINTS trades in which
           the volume-weighted YES price (a NO trade at p counts as YES at 1 - p) reached 0.99.
           The trade count keeps one stray print from setting it. From then on the market treats
           YES as settled. This clock looks only at prices up to that moment and not at which
           side finally won. A rule that did, such as "the last hour the winner traded below
           0.5", would keep exactly the trades placed just before the winner took off, so the cut
           itself would depend on the outcome. The clock does not fire when YES falls to 0.01,
           because a cheap YES that later wins is the very bet the screen looks for; markets
           that end NO are cut by the clocks below.
  closed   Gamma's closedTime.
  deadline the end of the day, month or year the question names ("on February 10", "by March
           31", "in January", "in 2025") at midnight in New York, daylight saving included.
           "Before" a date, month or year means the start of it. After the deadline the answer
           is fixed and only waits to be reported, so a trade then is not a prediction either.
  end      Gamma's scheduled endDate, for markets whose question names no deadline, when it
           falls within END_SLACK before closedTime. It then marks a scheduled event (a show, a
           ceremony) that the market closed soon after. Gamma usually writes 00:00 UTC on the
           day of the event, hours before it starts, so an endDate at 00:00 UTC is read as that
           calendar day and moved to its end in New York. An end date further back is a
           placeholder the market outlived, and is ignored.

The ten-minute buckets behind the settle clock are rounded and committed in market_buckets.csv.xz
(every bucket with at least MIN_PRINTS trades, up to the settle bucket, or all of them when the
clock never fires), and the clock is computed from the rounded values, so check_pack.py can
recompute it exactly.

Trades at or after t_known are not predictions and are dropped, and so are trades before the
start of the window in 02_window.py: the analysis covers trading from 1 November 2025, not only
markets that closed after it. The clocks still read the whole tape. The committed tape then keeps
every remaining trade of every tested wallet. A wallet is tested when, in those trades and across
all scoped markets, it

  bought at least WALLET_FLOOR dollars,
  is not a market maker: the mean over its markets of 2 * min(YES dollars, NO dollars) /
  (YES dollars + NO dollars) is at most MM_RATIO, so it does not trade both sides in size,
  is not a high-frequency bot: it made at most MAX_TRADES trades.

Market makers profit from the spread and bots from speed, and neither record says anything
about foresight. wallets.csv.gz lists every wallet over the floor with these three figures and
its status, and wallets_excluded_markets.csv.gz holds the per-market figures of the wallets left
out, so the exclusions can be recomputed from committed files. Market level figures from the full
tape (trade counts, the dollars the exclusions remove) go into the market table.

Wallet addresses are replaced by an index into wallets.csv.gz to keep the files small. The tape
is split into several xz-compressed CSV files so that no file nears GitHub's size limits.
"""
import calendar
import importlib.util
import json
import os
import re
import sys

import numpy as np
import pandas as pd

_spec = importlib.util.spec_from_file_location("window", os.path.join(os.path.dirname(__file__), "02_window.py"))
window = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(window)
START = window.LO.timestamp()

BUCKET = 600
SETTLED = 0.99
MIN_PRINTS = 5
WALLET_FLOOR = 5000
MM_RATIO = 0.3
MAX_TRADES = 10000
PARTS = 6
END_SLACK = 2 * 86400
TZ = "America/New_York"
GZ = {"method": "gzip", "mtime": 0}


MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
MONTHS.update({m.lower(): i for i, m in enumerate(calendar.month_abbr) if m})
_names = "|".join(sorted(MONTHS, key=len, reverse=True))
DAY = re.compile(r"\b(on|by|before|until|through)\s+(?:the\s+)?(" + _names + r")\.?\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s+(20\d\d))?\b", re.I)
MON = re.compile(r"\b(in|by|before|during)\s+(" + "|".join(k for k in MONTHS if len(k) > 3) + r")(?:\s+(20\d\d))?\b", re.I)
YEAR = re.compile(r"\b(in|by|before|during|of)\s+(20\d\d)\b", re.I)


def ny_midnight(d):
    """Unix seconds of 00:00 in New York on calendar date d."""
    return pd.Timestamp(year=d.year, month=d.month, day=d.day).tz_localize(TZ).tz_convert("UTC").timestamp()


def deadline(question, created, closed):
    """End of the period the question names, as unix seconds, or NaN when it names none.

    "before" gives the start of the period. Without a year in the question, the year is the
    first that puts the date after the market was created and no more than 60 days before it
    closed."""
    def pick(first, after, yr, before):
        for y in ([int(yr)] if yr else [created.year, created.year + 1]):
            try:
                d0, d1 = first(y), after(y)
            except ValueError:
                continue
            last = d1 - pd.Timedelta(days=1)
            if last >= created - pd.Timedelta(days=1) and last >= closed - pd.Timedelta(days=60):
                return ny_midnight(d0 if before else d1)
        return np.nan
    q = str(question)
    m = DAY.search(q)
    if m:
        mon, day = MONTHS[m.group(2).lower()], int(m.group(3))
        start = lambda y: pd.Timestamp(year=y, month=mon, day=day, tz="UTC")
        return pick(start, lambda y: start(y) + pd.Timedelta(days=1), m.group(4), m.group(1).lower() == "before")
    m = MON.search(q)
    if m:
        mon = MONTHS[m.group(2).lower()]
        start = lambda y: pd.Timestamp(year=y, month=mon, day=1, tz="UTC")
        return pick(start, lambda y: start(y) + pd.offsets.MonthBegin(1), m.group(3), m.group(1).lower() == "before")
    m = YEAR.search(q)
    if m:
        y0 = int(m.group(2))
        start = lambda y: pd.Timestamp(year=y, month=1, day=1, tz="UTC")
        return pick(start, lambda y: start(y + 1), y0, m.group(1).lower() == "before")
    return np.nan


def end_clock(end_ts, closed_ts, deadline_ts):
    """The end clock of one market, or NaN when it does not apply (see the module docstring)."""
    if not np.isnan(deadline_ts) or np.isnan(end_ts):
        return np.nan
    e = end_ts
    if e % 86400 == 0:
        e = ny_midnight(pd.Timestamp(e, unit="s") + pd.Timedelta(days=1))
    return e if closed_ts - END_SLACK <= e <= closed_ts else np.nan


def load(path):
    df = pd.read_csv(path, dtype={"proxyWallet": str, "side": str, "asset": str})
    df = df[df["size"] > 0]
    df["usd"] = df["size"] * df["price"]
    return df


def buckets(df):
    """Ten-minute buckets with at least MIN_PRINTS trades: start, trade count, rounded YES VWAP."""
    if df.empty:
        return pd.DataFrame({"b": [], "n": [], "yes_vwap": []})
    y = np.where(df["outcomeIndex"] == 0, df["price"], 1 - df["price"])
    b = (df["timestamp"] // BUCKET) * BUCKET
    g = pd.DataFrame({"b": b.to_numpy(), "ys": y * df["size"].to_numpy(), "s": df["size"].to_numpy()}).groupby("b")
    out = pd.DataFrame({"n": g.size(), "yes_vwap": (g["ys"].sum() / g["s"].sum()).round(6)}).reset_index()
    return out[out["n"] >= MIN_PRINTS].reset_index(drop=True)


def t_settle(bk):
    """Start of the first bucket whose rounded YES VWAP is at least SETTLED."""
    hit = bk.loc[bk["yes_vwap"] >= SETTLED, "b"]
    return float(hit.min()) if not hit.empty else np.nan


def clocks(scope):
    """Add closed_ts, end_ts, deadline_ts and end_cap to the market table."""
    closed = pd.to_datetime(scope["closedTime"], utc=True, format="mixed")
    scope["closed_ts"] = (closed - pd.Timestamp(0, tz="UTC")).dt.total_seconds()
    end = pd.to_datetime(scope["endDate"], utc=True, format="mixed")
    scope["end_ts"] = (end - pd.Timestamp(0, tz="UTC")).dt.total_seconds()
    created = pd.to_datetime(scope["createdAt"], utc=True, format="mixed")
    scope["deadline_ts"] = [deadline(q, a, b) for q, a, b in zip(scope["question"], created, closed)]
    scope["end_cap"] = [end_clock(e, c, d) for e, c, d in zip(scope["end_ts"], scope["closed_ts"], scope["deadline_ts"])]
    return scope


def known(row, ts):
    """t_known and the clock that set it."""
    cl = {"settle": ts, "closed": row["closed_ts"], "end": row["end_cap"], "deadline": row["deadline_ts"]}
    tk = float(np.nanmin(list(cl.values())))
    return tk, next(k for k, v in cl.items() if v == tk)


def main(scope_path, rawdir, outdir, out_scope):
    scope = clocks(pd.read_csv(scope_path, dtype={"id": str, "event_id": str}))
    manifest = json.load(open(os.path.join(rawdir, "manifest.json")))
    capped = [c for c in scope["conditionId"] if manifest[c]["kind"] != "full"]
    if capped:
        raise RuntimeError(f"{len(capped)} tapes are not complete, first {capped[0]}")
    spend, ntr, two, nmk, info, bks = {}, {}, {}, {}, [], {}
    for i, m in scope.iterrows():
        df = load(os.path.join(rawdir, m["conditionId"] + ".csv.gz"))
        bk = buckets(df)
        tc = t_settle(bk)
        bks[m["conditionId"]] = bk if np.isnan(tc) else bk[bk["b"] <= tc]
        tk, src = known(m, tc)
        pre = df[(df["timestamp"] >= START) & (df["timestamp"] < tk)]
        b = pre[pre["side"] == "BUY"].groupby("proxyWallet")["usd"].sum()
        for w, v in b.items():
            spend[w] = spend.get(w, 0.0) + v
        for w, v in pre.groupby("proxyWallet").size().items():
            ntr[w] = ntr.get(w, 0) + v
        bo = pre[pre["side"] == "BUY"].groupby(["proxyWallet", "outcomeIndex"])["usd"].sum().unstack(fill_value=0.0)
        for o in (0, 1):
            if o not in bo.columns:
                bo[o] = 0.0
        tot = bo[0] + bo[1]
        ratio = (2 * np.minimum(bo[0], bo[1]) / tot.where(tot > 0, 1.0))[tot > 0]
        for w, v in ratio.items():
            two[w] = two.get(w, 0.0) + v
            nmk[w] = nmk.get(w, 0) + 1
        info.append({"tape": manifest[m["conditionId"]]["kind"], "n_trades_full": len(df),
                     "n_trades_pre_known": len(pre), "buy_usd_pre_known": pre.loc[pre["side"] == "BUY", "usd"].sum(),
                     "t_settle": tc, "t_known": tk, "t_known_source": src})
        if i % 200 == 0:
            print("pass 1", i, flush=True)
    scope = pd.concat([scope, pd.DataFrame(info, index=scope.index)], axis=1)
    big = sorted(w for w, v in spend.items() if v >= WALLET_FLOOR)
    wt = pd.DataFrame({"wallet": big, "buy_usd_pre_known": [spend[w] for w in big],
                       "n_trades_pre_known": [ntr[w] for w in big],
                       "two_sided_mean": [two[w] / nmk[w] for w in big]})
    wt["status"] = np.where(wt["two_sided_mean"] > MM_RATIO, "market_maker",
                            np.where(wt["n_trades_pre_known"] > MAX_TRADES, "high_frequency", "tested"))
    keep = wt.loc[wt["status"] == "tested", "wallet"].tolist()
    left_out = set(wt.loc[wt["status"] != "tested", "wallet"])
    widx = {w: j for j, w in enumerate(keep)}
    wt["w"] = wt["wallet"].map(widx).astype("Int64")
    os.makedirs(outdir, exist_ok=True)
    wt[["w", "wallet", "status", "buy_usd_pre_known", "n_trades_pre_known", "two_sided_mean"]].round(6).to_csv(
        os.path.join(outdir, "wallets.csv.gz"), index=False, compression=GZ)

    scope = scope.sort_values(["t_known", "conditionId"]).reset_index(drop=True)
    scope["m"] = np.arange(len(scope))
    bounds = np.array_split(np.arange(len(scope)), PARTS)
    kept_rows, kept_usd, excl = [], [], []
    for part, idx in enumerate(bounds):
        frames = []
        for i in idx:
            m = scope.loc[i]
            df = load(os.path.join(rawdir, m["conditionId"] + ".csv.gz"))
            df = df[(df["timestamp"] >= START) & (df["timestamp"] < m["t_known"])]
            x = df[df["proxyWallet"].isin(left_out)]
            if len(x):
                xb = x[x["side"] == "BUY"].groupby(["proxyWallet", "outcomeIndex"])["usd"].sum().unstack(fill_value=0.0)
                xe = pd.DataFrame({"n_trades": x.groupby("proxyWallet").size()})
                for o in (0, 1):
                    xe[f"buy_usd_{o}"] = xb[o] if o in xb.columns else 0.0
                xe = xe.fillna(0.0).rename_axis("wallet").reset_index()
                xe.insert(1, "m", m["m"])
                excl.append(xe)
            df = df[df["proxyWallet"].isin(widx)]
            kept_rows.append(len(df))
            kept_usd.append(df.loc[df["side"] == "BUY", "usd"].sum())
            frames.append(pd.DataFrame({
                "m": m["m"], "w": df["proxyWallet"].map(widx), "side": df["side"].str[0],
                "o": df["outcomeIndex"], "size": df["size"], "price": df["price"], "ts": df["timestamp"],
            }).sort_values(["ts", "w", "o", "side", "size", "price"], kind="mergesort"))
        tape = pd.concat(frames, ignore_index=True)
        tape.to_csv(os.path.join(outdir, f"tape_part{part + 1}.csv.xz"), index=False)
        print("part", part + 1, len(tape), flush=True)
    scope["n_trades_committed"] = kept_rows
    scope["buy_usd_committed"] = kept_usd
    scope.to_csv(out_scope, index=False)
    ex = pd.concat(excl, ignore_index=True).sort_values(["wallet", "m"])
    ex[["wallet", "m", "n_trades", "buy_usd_0", "buy_usd_1"]].round(6).to_csv(
        os.path.join(outdir, "wallets_excluded_markets.csv.gz"), index=False, compression=GZ)
    mb = pd.concat([bks[c].assign(m=k) for c, k in zip(scope["conditionId"], scope["m"])], ignore_index=True)
    mb["b"] = mb["b"].astype("int64")
    mb[["m", "b", "n", "yes_vwap"]].to_csv(os.path.join(outdir, "market_buckets.csv.xz"), index=False)
    print(len(keep), "wallets tested of", len(big), "over the floor and", len(spend), "buyers; committed rows",
          sum(kept_rows), "; buckets", len(mb))


if __name__ == "__main__":
    main(*sys.argv[1:5])
