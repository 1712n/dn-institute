"""Is the wash the token's fault, or the venue's? Same xStocks, Gate vs Bybit.

For five xStocks that trade on both Gate and Bybit, run the identical screen
metrics on each venue's free public May-2026 trade dump. If the wash were a
property of the token or its issuer it would show on both venues; if it is
venue-specific it shows on one. Bybit dumps:
``public.bybit.com/spot/<SYM>USDT/<SYM>USDT-2026-05.csv.gz``.
"""
import os
import json
import gzip
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from gatelib import load
from metrics_lib import metrics
from paths import DATA, POST, dump
SYMS = ["HOODX", "TSLAX", "NVDAX", "AAPLX", "GOOGLX"]


def load_bybit(sym, month="2026-05"):
    """Bybit spot dump: id,timestamp(ms),price,volume(base),side(text),rpi -> screen schema."""
    name = f"{sym}USDT-{month}.csv.gz"
    path = dump(f"bybit/{name}", f"https://public.bybit.com/spot/{sym}USDT/{name}")
    with gzip.open(path, "rt") as fh:
        df = pd.read_csv(fh, header=0, names=["id", "ts", "price", "amt", "side", "rpi"])
    df["buy"] = df["side"].astype(str).str.lower().eq("buy")
    df["notional"] = df["price"] * df["amt"]
    return df


rows = []
for s in SYMS:
    g = metrics(load(s, "202605"))
    b = metrics(load_bybit(s))
    rows.append(dict(symbol=s,
                     gate_clip_share=round(g["clip_share"], 4), gate_score=round(g["score"], 3),
                     gate_n=g["n_trades"],
                     bybit_clip_share=round(b["clip_share"], 4), bybit_score=round(b["score"], 3),
                     bybit_n=b["n_trades"]))

out = dict(month="2026-05", venues=["Gate.io", "Bybit"], markets=rows)
json.dump(out, open(os.path.join(DATA, "crossvenue.json"), "w"), indent=2)
pd.DataFrame(rows).to_csv(os.path.join(DATA, "crossvenue.csv"), index=False)

print(" mkt      Gate clip%  Gate score | Bybit clip%  Bybit score")
for r in rows:
    print(f" {r['symbol']:7} {r['gate_clip_share']*100:8.1f}%  {r['gate_score']:9.2f} | "
          f"{r['bybit_clip_share']*100:8.1f}%  {r['bybit_score']:9.2f}")

x = range(len(SYMS)); w = 0.38
fig, ax = plt.subplots(figsize=(9, 4.6))
ax.bar([i - w / 2 for i in x], [r["gate_clip_share"] * 100 for r in rows], w, color="#d9480f", label="Gate")
ax.bar([i + w / 2 for i in x], [r["bybit_clip_share"] * 100 for r in rows], w, color="#1c7ed6", label="Bybit")
for i, r in enumerate(rows):
    ax.text(i - w / 2, r["gate_clip_share"] * 100 + 0.6, f"{r['gate_clip_share']*100:.0f}", ha="center", fontsize=8)
    ax.text(i + w / 2, r["bybit_clip_share"] * 100 + 0.6, f"{r['bybit_clip_share']*100:.0f}", ha="center", fontsize=8)
ax.set_ylabel("dominant clip, % of trades"); ax.set_ylim(0, 55)
ax.set_xticks(list(x)); ax.set_xticklabels(SYMS)
ax.set_title("Same tokenized stocks, two venues: a dominant wash clip on Gate, organic on Bybit", fontsize=10.5)
ax.legend(loc="upper right"); fig.tight_layout()
fig.savefig(os.path.join(POST, "crossvenue.png"), dpi=120); plt.close()
print("\nwrote data/crossvenue.json + crossvenue.png")
