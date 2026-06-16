#!/usr/bin/env python3
"""
Reproducible market-health analysis for 1000SATS/USDT on Binance, 2024-03-15.

Pulls real Binance public aggTrades archives (SHA-256 verifiable), computes a set
of manipulation-sensitive microstructure metrics against two liquid controls
(BTC/USDT, ETH/USDT), and renders every figure used in the accompanying article.

Run:
    pip install requests pandas numpy scipy matplotlib
    python analysis.py

Outputs:
    charts/*.png        figures referenced by index.md
    data/metrics.json   machine-readable metric table
    data/MANIFEST.txt   dataset provenance + SHA-256 of every downloaded archive
"""
import requests, zipfile, io, os, json, hashlib
import pandas as pd, numpy as np
from scipy import stats
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = "https://data.binance.vision/data/spot/daily/aggTrades"
COLS = ["agg_id", "price", "qty", "first_id", "last_id", "ts",
        "is_buyer_maker", "is_best_match"]
DATE = "2024-03-15"
SUBJECT = "1000SATSUSDT"
CONTROLS = ["BTCUSDT", "ETHUSDT"]
SYMS = [SUBJECT] + CONTROLS

os.makedirs("charts", exist_ok=True)
os.makedirs("data", exist_ok=True)


def load(sym):
    """Download one daily aggTrades archive and return (df, sha256, byte_len)."""
    url = f"{BASE}/{sym}/{sym}-aggTrades-{DATE}.zip"
    r = requests.get(url, timeout=180); r.raise_for_status()
    sha = hashlib.sha256(r.content).hexdigest()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    df = pd.read_csv(z.open(z.namelist()[0]), header=None)
    if str(df.iloc[0, 0]).startswith("agg"):
        df = df.iloc[1:].reset_index(drop=True)
    df.columns = COLS[:df.shape[1]]
    for c in ("price", "qty", "ts"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["price", "qty"])
    df["quote"] = df["price"] * df["qty"]
    return df, sha, len(r.content)


def metrics(df):
    """Microstructure fingerprints sensitive to bot order-printing / wash trades."""
    n = len(df)
    vc = df["qty"].value_counts()
    top1 = vc.iloc[0] / n                     # share at single most-frequent lot
    top10 = vc.head(10).sum() / n             # share at top-10 lots
    # Same-millisecond clustering: humans cannot place many trades in <1ms.
    ts_counts = df["ts"].value_counts()
    burst = ts_counts[ts_counts >= 3].sum() / n
    max_per_ms = int(ts_counts.max())
    # Quote-volume tail / shape.
    q = df["quote"].values; q = q[q > 0]
    skew = float(stats.skew(np.log(q)))
    thr = np.quantile(q, 0.95); tail = q[q >= thr]
    hill = 1 + len(tail) / np.sum(np.log(tail / thr))   # Hill tail index
    # Maker/taker balance — near-perfect 50/50 is a self-cross signature.
    if "is_buyer_maker" in df:
        bm = df["is_buyer_maker"].astype(str).str.lower().isin(["true", "1"]).mean()
    else:
        bm = float("nan")
    return dict(n=int(n), top1_lot=float(top1), top10_lot=float(top10),
                burst_share=float(burst), max_per_ms=max_per_ms,
                log_skew=skew, hill=float(hill), buyer_maker=float(bm),
                top_lots=[(float(v), int(c)) for v, c in vc.head(8).items()])


D, R = {}, {}
for s in SYMS:
    D[s] = load(s)
for s in SYMS:
    R[s] = metrics(D[s][0])
    m = R[s]
    print(f"{s:14s} n={m['n']:>9,} top1={m['top1_lot']:.3f} "
          f"top10={m['top10_lot']:.3f} burst={m['burst_share']:.3f} "
          f"max/ms={m['max_per_ms']:>3} skew={m['log_skew']:+.3f} "
          f"hill={m['hill']:.2f} bmaker={m['buyer_maker']:.3f}")

# Count-inflation fingerprint: the single dominant lot prints a huge SHARE OF
# TRADES while contributing almost nothing to USD volume -> activity faking.
sub_df = D[SUBJECT][0]
dom_lot = sub_df["qty"].value_counts().index[0]
dom = sub_df[sub_df["qty"] == dom_lot]
dom_quote = float((dom["qty"] * dom["price"]).sum())
day_quote = float(sub_df["quote"].sum())
R[SUBJECT]["dominant_lot"] = float(dom_lot)
R[SUBJECT]["dominant_lot_trade_share"] = len(dom) / len(sub_df)
R[SUBJECT]["dominant_lot_usd_value"] = float(dom_lot * dom["price"].median())
R[SUBJECT]["dominant_lot_volume_share"] = dom_quote / day_quote
print(f"\nCount-inflation: lot={dom_lot:,.0f} SATS  "
      f"trades={len(dom)/len(sub_df)*100:.2f}%  "
      f"value~${dom_lot * dom['price'].median():.2f}/trade  "
      f"volume_share={dom_quote/day_quote*100:.2f}%")

json.dump(R, open("data/metrics.json", "w"), indent=2)
RED, BLU, GRN = "#d62728", "#1f77b4", "#2ca02c"

# CHART 1 — lot-size concentration (the headline signal).
fig, ax = plt.subplots(figsize=(8, 4.8))
x = np.arange(len(SYMS))
t1 = [R[s]["top1_lot"] * 100 for s in SYMS]
t10 = [R[s]["top10_lot"] * 100 for s in SYMS]
ax.bar(x - 0.18, t1, width=0.36, label="Single most-frequent lot size", color=RED)
ax.bar(x + 0.18, t10, width=0.36, label="Top-10 most-frequent lot sizes", color=BLU)
for i, v in enumerate(t1):
    ax.text(i - 0.18, v + 0.2, f"{v:.2f}%", ha="center", fontsize=8)
for i, v in enumerate(t10):
    ax.text(i + 0.18, v + 0.2, f"{v:.2f}%", ha="center", fontsize=8)
ax.set_xticks(x); ax.set_xticklabels(SYMS)
ax.set_ylabel("Share of all executed trades (%)")
ax.set_title("Lot-size concentration: bot order-printing signature — Binance 2024-03-15")
ax.legend()
fig.tight_layout(); fig.savefig("charts/lot-concentration.png", dpi=110); plt.close(fig)

# CHART 2 — most repeated exact lots for the subject market.
fig, ax = plt.subplots(figsize=(9, 4.8))
vc = D[SUBJECT][0]["qty"].value_counts().head(12)
labels = [f"{v:,.0f}" for v in vc.index]
ax.bar(range(len(vc)), vc.values, color=RED, alpha=0.85)
ax.set_xticks(range(len(vc))); ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
ax.set_ylabel("Number of executed trades at this exact size")
ax.set_title("1000SATS/USDT: most repeated exact trade sizes — Binance 2024-03-15")
fig.tight_layout(); fig.savefig("charts/sats-repeated-lots.png", dpi=110); plt.close(fig)

# CHART 3 — quote-volume distribution (subject vs controls).
fig, ax = plt.subplots(figsize=(9, 5))
for s, color in zip(SYMS, [RED, GRN, BLU]):
    q = D[s][0]["quote"].values; q = q[q > 0]
    ax.hist(np.log10(q), bins=80, density=True, histtype="step", lw=2, color=color,
            label=f"{s} (Hill a={R[s]['hill']:.2f}, log-skew={R[s]['log_skew']:+.2f})")
ax.set_xlabel("log10(trade quote volume, USDT)"); ax.set_ylabel("density")
ax.set_title("Trade quote-volume distribution — 1000SATS vs BTC/ETH, Binance 2024-03-15")
ax.legend()
fig.tight_layout(); fig.savefig("charts/volume-distribution.png", dpi=110); plt.close(fig)

# CHART 4 — same-millisecond clustering (machine-speed printing).
fig, ax = plt.subplots(figsize=(8, 4.8))
burst = [R[s]["burst_share"] * 100 for s in SYMS]
mx = [R[s]["max_per_ms"] for s in SYMS]
ax.bar(x, burst, width=0.5, color=RED, alpha=0.85)
for i, (b, m) in enumerate(zip(burst, mx)):
    ax.text(i, b + 0.4, f"{b:.2f}%\n(max {m}/ms)", ha="center", fontsize=8)
ax.set_xticks(x); ax.set_xticklabels(SYMS)
ax.set_ylabel("Trades inside same-millisecond clusters (>=3) (%)")
ax.set_title("Same-millisecond trade clustering — machine-speed printing, Binance 2024-03-15")
fig.tight_layout(); fig.savefig("charts/ms-clustering.png", dpi=110); plt.close(fig)

# CHART 5 — intraday trade count vs average lot size for the subject.
df = D[SUBJECT][0].copy()
df["hour"] = pd.to_datetime(df["ts"], unit="ms").dt.hour
g = df.groupby("hour").agg(trades=("qty", "size"), avg_qty=("qty", "mean"))
fig, ax1 = plt.subplots(figsize=(9, 4.8))
ax1.bar(g.index, g["trades"], color=BLU, alpha=0.6, label="trade count")
ax1.set_xlabel("hour (UTC)"); ax1.set_ylabel("trade count", color=BLU)
ax2 = ax1.twinx(); ax2.plot(g.index, g["avg_qty"], color=RED, marker="o", label="avg lot size")
ax2.set_ylabel("avg trade size (SATS)", color=RED)
ax1.set_title("1000SATS/USDT intraday trade count vs average lot size — Binance 2024-03-15")
fig.tight_layout(); fig.savefig("charts/sats-intraday.png", dpi=110); plt.close(fig)

# CHART 6 — count-inflation: the dominant lot's share of TRADES vs share of VOLUME.
fig, ax = plt.subplots(figsize=(7, 4.8))
ts = R[SUBJECT]["dominant_lot_trade_share"] * 100
vs = R[SUBJECT]["dominant_lot_volume_share"] * 100
bars = ax.bar(["Share of\nall trades", "Share of\nUSD volume"], [ts, vs],
              color=[RED, GRN], width=0.55)
for b, v in zip(bars, [ts, vs]):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.3, f"{v:.2f}%", ha="center", fontsize=10)
ax.set_ylabel("Percent")
ax.set_title(f"Count-inflation: the {R[SUBJECT]['dominant_lot']:,.0f}-SATS ping lot\n"
             f"(~${R[SUBJECT]['dominant_lot_usd_value']:.2f}/trade) — Binance 2024-03-15")
fig.tight_layout(); fig.savefig("charts/count-inflation.png", dpi=110); plt.close(fig)

with open("data/MANIFEST.txt", "w") as f:
    f.write("Dataset provenance - reproducible, SHA-256 verifiable\n")
    f.write("Source: Binance public market data archive (https://data.binance.vision)\n")
    f.write(f"Endpoint pattern: /data/spot/daily/aggTrades/<SYMBOL>/<SYMBOL>-aggTrades-{DATE}.zip\n")
    f.write(f"Snapshot date: {DATE} (full UTC trading day, executed aggregate trades)\n\n")
    for s in SYMS:
        d, sha, size = D[s]
        f.write(f"{s}-aggTrades-{DATE}.zip  rows={len(d):,}  zip_bytes={size}  sha256={sha}\n")

print("OK charts:", sorted(os.listdir("charts")))
print(open("data/MANIFEST.txt").read())
