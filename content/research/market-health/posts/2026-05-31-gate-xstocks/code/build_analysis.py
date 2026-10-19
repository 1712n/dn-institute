"""Reconstruct the tokenized-stock (xStock) wash-trading pattern on Gate.io spot.

Reads the May 2026 Gate dumps (see gatelib.py) for six flagged markets and the
MSTRX control, writes their mechanism numbers to data/findings.json and two
datasets to data/, and renders the four mechanism figures beside index.md.
Deterministic.
"""
import os
import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from gatelib import load
from metrics_lib import benford_ks, first_digit_shares

from paths import DATA, POST
MONTH = "202605"

NAMES = {"HOODX": "Robinhood", "SPYX": "S&P 500", "TSLAX": "Tesla", "NVDAX": "NVIDIA",
         "AAPLX": "Apple", "GOOGLX": "Alphabet", "MSTRX": "MicroStrategy"}
WASHED = ["HOODX", "SPYX", "TSLAX", "NVDAX", "AAPLX", "GOOGLX"]
CONTROL = "MSTRX"
SYMS = WASHED + [CONTROL]
WASH, CTRL, GREY = "#d9480f", "#1c7ed6", "#adb5bd"


def metrics(sym):
    df = load(sym, MONTH)
    n = len(df)
    df = df.assign(day=df["t"].dt.date)
    vc = df["amt"].value_counts()
    top_qty = float(vc.index[0]); top_share = float(vc.iloc[0] / n)
    clip = df[df["amt"] == top_qty]
    clip_buyshare = float(clip["buy"].mean())
    obs, ks = first_digit_shares(df["amt"]), benford_ks(df["amt"])
    day_share = df.assign(c=(df["amt"] == top_qty)).groupby("day")["c"].mean()
    tov = float(df["notional"].sum())
    clip_notional = float(clip["notional"].sum())
    buy_n = float(clip.loc[clip["buy"], "notional"].sum())
    clip_net_pct = abs(2 * buy_n - clip_notional) / clip_notional  # |buy-sell|/total: 0 = fully circular
    daybuy_std = float(clip.groupby("day")["buy"].mean().std())
    return dict(
        symbol=sym, name=NAMES[sym], n_trades=int(n), distinct_sizes=int(df["amt"].nunique()),
        top_clip_qty=top_qty, top_clip_share=round(top_share, 4),
        clip_buyshare=round(clip_buyshare, 3),
        clip_notional=round(clip_notional, 0), clip_net_pct=round(clip_net_pct, 3),
        clip_dollar_share=round(clip_notional / tov, 4), daybuy_std=round(daybuy_std, 3),
        digit1=round(float(obs[1]), 4), benford_ks=round(ks, 3),
        day_clip_min=round(float(day_share.min()), 3), day_clip_med=round(float(day_share.median()), 3),
        day_clip_max=round(float(day_share.max()), 3), days=int(day_share.size),
        turnover_usd=round(tov, 0), daily_turnover_usd=round(tov / 31, 0),
        price_first=round(float(df["price"].iloc[0]), 4), price_last=round(float(df["price"].iloc[-1]), 4),
        price_min=round(float(df["price"].min()), 4), price_max=round(float(df["price"].max()), 4),
        net_pct=round(float(df["price"].iloc[-1] / df["price"].iloc[0] - 1), 3),
        _day_share=day_share)


M = {s: metrics(s) for s in SYMS}

# findings.json (drop the helper series)
F = {s: {k: v for k, v in m.items() if not k.startswith("_")} for s, m in M.items()}
washed_reported = sum(F[s]["turnover_usd"] for s in WASHED)
washed_clip = sum(F[s]["clip_notional"] for s in WASHED)
F["_meta"] = dict(month=MONTH, venue="Gate.io", washed=WASHED, control=CONTROL,
                  side_flag="taker buy = side 1 (checked by test_side_flag_buys_push_price_up)",
                  washed_reported_usd=round(washed_reported, 0), washed_clip_usd=round(washed_clip, 0),
                  clip_dollar_share=round(washed_clip / washed_reported, 4),
                  clip_trade_share_min=min(F[s]["top_clip_share"] for s in WASHED),
                  clip_trade_share_max=max(F[s]["top_clip_share"] for s in WASHED))
json.dump(F, open(os.path.join(DATA, "findings.json"), "w"), indent=2)
for s in SYMS:
    m = F[s]
    print(f"{s:7} {m['n_trades']:>8,} clip={m['top_clip_share']:.1%}@{m['top_clip_qty']} "
          f"buy={m['clip_buyshare']:.0%} KS={m['benford_ks']:.2f} day_med={m['day_clip_med']:.0%} "
          f"${m['daily_turnover_usd']:,.0f}/d net={m['net_pct']:+.0%}")

# processed datasets
rows = [{k: F[s][k] for k in ("symbol", "name", "n_trades", "top_clip_qty", "top_clip_share",
        "clip_buyshare", "clip_net_pct", "clip_notional", "clip_dollar_share", "benford_ks",
        "day_clip_med", "daily_turnover_usd", "net_pct")} for s in SYMS]
pd.DataFrame(rows).to_csv(os.path.join(DATA, "per_stock_metrics.csv"), index=False)
M["HOODX"]["_day_share"].rename("clip_share").to_csv(os.path.join(DATA, "hoodx_daily_clip_share.csv"))
print("wrote 2 datasets to", DATA)

labels = [f"{NAMES[s]}\n{s}" for s in SYMS]
colors = [WASH if s in WASHED else GREY for s in SYMS]

# fig 1: clip recurrence
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.bar(labels, [F[s]["top_clip_share"] * 100 for s in SYMS], color=colors, width=0.72)
ax.set_ylabel("most common trade size, % of all trades")
ax.set_title("One trade size dominates each washed xStock's tape (orange); the MicroStrategy control does not")
for i, s in enumerate(SYMS):
    ax.text(i, F[s]["top_clip_share"] * 100 + 0.6, f"{F[s]['top_clip_share']*100:.0f}%", ha="center", fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(POST, "clip-recurrence.png"), dpi=120); plt.close()

# fig 2: circular volume (net position the clip takes, % of its own volume)
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.bar(labels, [F[s]["clip_net_pct"] * 100 for s in SYMS], color=colors, width=0.72)
ax.set_ylabel("net position taken, % of the clip's own volume"); ax.set_ylim(0, 105)
ax.set_title("The dominant clip nets to almost no position (orange); the control takes a real side (grey)", fontsize=10.5)
for i, s in enumerate(SYMS):
    ax.text(i, F[s]["clip_net_pct"] * 100 + 1.5, f"{F[s]['clip_net_pct']*100:.0f}%", ha="center", fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(POST, "circular-volume.png"), dpi=120); plt.close()

# fig 3: Benford break (KS distance)
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.bar(labels, [F[s]["benford_ks"] for s in SYMS], color=colors, width=0.72)
ax.axhline(0.05, ls=":", color="grey", lw=1, label="0.05 reference line")
ax.set_ylabel("Kolmogorov-Smirnov distance from Benford")
ax.set_title("The recurring clip breaks the first-digit (Benford) distribution of trade sizes")
ax.legend(loc="upper right"); fig.tight_layout(); fig.savefig(os.path.join(POST, "benford.png"), dpi=120); plt.close()

# fig 4: HOODX daily persistence
ds = M["HOODX"]["_day_share"].copy(); ds.index = pd.to_datetime(ds.index)
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.bar(ds.index, ds.values * 100, color=WASH, width=0.7)
ax.axhline(ds.median() * 100, ls="--", color="black", lw=1, label=f"median {ds.median()*100:.0f}%")
ax.set_ylabel("HOODX trades on the 0.12 clip (%)"); ax.set_xlabel("day (UTC), May 2026")
ax.set_title("Robinhood xStock: the wash clip runs every day of the month")
ax.legend(loc="lower right"); fig.autofmt_xdate(); fig.tight_layout()
fig.savefig(os.path.join(POST, "persistence.png"), dpi=120); plt.close()
print("wrote 4 figures to", POST)
