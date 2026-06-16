import requests, zipfile, io, pandas as pd, numpy as np, hashlib, os, json
from scipy import stats
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

base="https://data.binance.vision/data/spot/daily/aggTrades"
COLS=["agg_id","price","qty","first_id","last_id","ts","is_buyer_maker","is_best_match"]
DATE="2024-05-01"
os.makedirs("charts",exist_ok=True); os.makedirs("data",exist_ok=True)

def load(sym):
    r=requests.get(f"{base}/{sym}/{sym}-aggTrades-{DATE}.zip",timeout=180); r.raise_for_status()
    sha=hashlib.sha256(r.content).hexdigest()
    z=zipfile.ZipFile(io.BytesIO(r.content))
    df=pd.read_csv(z.open(z.namelist()[0]),header=None)
    if str(df.iloc[0,0]).startswith("agg"): df=df.iloc[1:].reset_index(drop=True)
    df.columns=COLS[:df.shape[1]]
    df["price"]=pd.to_numeric(df["price"]); df["qty"]=pd.to_numeric(df["qty"])
    df=df.dropna(subset=["price","qty"]); df["quote"]=df["price"]*df["qty"]
    df["ts"]=pd.to_numeric(df["ts"],errors="coerce")
    return df,sha,len(r.content)

D={}; R={}
for s in ["FLOKIUSDT","BTCUSDT"]:
    D[s]=load(s)

# Metric A: repeated-lot concentration — share of trades whose qty equals one of the
# top-N most frequent exact sizes (manipulation: a few bot lot-sizes dominate).
# Metric B: "round million" lot share for FLOKI-style whole-token markets.
def lot_metrics(df):
    vc=df["qty"].value_counts()
    n=len(df)
    top1=vc.iloc[0]/n
    top10=vc.head(10).sum()/n
    # exact round lots: qty divisible by 100000 (round 100k+) and >0
    q=df["qty"].values
    round_mil=np.mean((q>0)&(np.mod(q,500000.0)==0)) if df["qty"].median()>1 else np.mean((q>0)&(np.mod(np.round(q,8),0.01)==0)&(q>=0.01))
    return float(top1),float(top10),float(round_mil),vc

for s in ["FLOKIUSDT","BTCUSDT"]:
    df,sha,size=D[s]
    top1,top10,rmil,vc=lot_metrics(df)
    q=df["quote"].values; q=q[q>0]
    thr=np.quantile(q,0.95); tail=q[q>=thr]
    hill=1+len(tail)/np.sum(np.log(tail/thr))
    sk=stats.skew(np.log(q))
    R[s]=dict(n=int(len(df)), top1_lot=top1, top10_lot=top10, round_lot=rmil,
              hill=float(hill), skew=float(sk), sha256=sha, zip_bytes=size,
              top_lots=[(float(v),int(c)) for v,c in vc.head(6).items()])
    print(s,"n=%d"%len(df),"top1=%.3f"%top1,"top10=%.3f"%top10,"round_lot=%.3f"%rmil,"hill=%.2f"%hill,"skew=%.2f"%sk)

json.dump(R, open("data/metrics.json","w"), indent=2)

# CHART 1: repeated-lot concentration (the real signal)
fig,ax=plt.subplots(figsize=(8,4.8))
syms=["FLOKIUSDT","BTCUSDT"]
top1=[R[s]["top1_lot"]*100 for s in syms]; top10=[R[s]["top10_lot"]*100 for s in syms]
x=np.arange(2)
ax.bar(x-0.18,top1,width=0.36,label="Single most-frequent lot size",color="#d62728")
ax.bar(x+0.18,top10,width=0.36,label="Top-10 most-frequent lot sizes",color="#1f77b4")
for i,v in enumerate(top1): ax.text(i-0.18,v+0.1,f"{v:.2f}%",ha="center",fontsize=8)
for i,v in enumerate(top10): ax.text(i+0.18,v+0.1,f"{v:.2f}%",ha="center",fontsize=8)
ax.set_xticks(x); ax.set_xticklabels(syms); ax.set_ylabel("Share of all executed trades (%)")
ax.set_title("Lot-size concentration: bot order-printing signature — Binance 2024-05-01")
ax.legend()
fig.tight_layout(); fig.savefig("charts/lot-concentration.png",dpi=110); plt.close(fig)

# CHART 2: FLOKI top repeated exact lots
fig,ax=plt.subplots(figsize=(9,4.8))
df=D["FLOKIUSDT"][0]; vc=df["qty"].value_counts().head(12)
labels=[f"{int(v):,}" for v in vc.index]
ax.bar(range(len(vc)),vc.values,color="#d62728",alpha=0.85)
ax.set_xticks(range(len(vc))); ax.set_xticklabels(labels,rotation=45,ha="right",fontsize=8)
ax.set_ylabel("Number of executed trades at this exact size")
ax.set_title("FLOKI/USDT: most repeated exact trade sizes (whole-token lots) — Binance 2024-05-01")
fig.tight_layout(); fig.savefig("charts/floki-repeated-lots.png",dpi=110); plt.close(fig)

# CHART 3: volume distribution log-log (power-law tail)
fig,ax=plt.subplots(figsize=(9,5))
for s,color in zip(syms,["#d62728","#2ca02c"]):
    q=D[s][0]["quote"].values; q=q[q>0]
    ax.hist(np.log10(q),bins=80,density=True,histtype="step",lw=2,color=color,
            label=f"{s} (Hill α={R[s]['hill']:.2f}, log-skew={R[s]['skew']:.2f})")
ax.set_xlabel("log10(trade quote volume, USDT)"); ax.set_ylabel("density")
ax.set_title("Trade quote-volume distribution — FLOKI/USDT vs BTC/USDT, Binance 2024-05-01")
ax.legend()
fig.tight_layout(); fig.savefig("charts/volume-distribution.png",dpi=110); plt.close(fig)

# CHART 4: intraday trade-count & avg size (FLOKI) to show algorithmic regularity
df=D["FLOKIUSDT"][0].copy()
df["hour"]=pd.to_datetime(df["ts"],unit="ms").dt.hour
g=df.groupby("hour").agg(trades=("qty","size"),avg_qty=("qty","mean"))
fig,ax1=plt.subplots(figsize=(9,4.8))
ax1.bar(g.index,g["trades"],color="#1f77b4",alpha=0.6,label="trade count")
ax1.set_xlabel("hour (UTC)"); ax1.set_ylabel("trade count",color="#1f77b4")
ax2=ax1.twinx(); ax2.plot(g.index,g["avg_qty"],color="#d62728",marker="o",label="avg lot size")
ax2.set_ylabel("avg trade size (FLOKI)",color="#d62728")
ax1.set_title("FLOKI/USDT intraday trade count vs average lot size — Binance 2024-05-01")
fig.tight_layout(); fig.savefig("charts/floki-intraday.png",dpi=110); plt.close(fig)

with open("data/MANIFEST.txt","w") as f:
    f.write("Dataset provenance — reproducible, SHA-256 verifiable\n")
    f.write("Source: Binance public market data archive (https://data.binance.vision)\n")
    f.write(f"Endpoint pattern: /data/spot/daily/aggTrades/<SYMBOL>/<SYMBOL>-aggTrades-{DATE}.zip\n")
    f.write(f"Snapshot date: {DATE} (full UTC trading day, executed aggregate trades)\n\n")
    for s in syms:
        d,sha,size=D[s]
        f.write(f"{s}-aggTrades-{DATE}.zip  rows={len(d):,}  zip_bytes={size}  sha256={sha}\n")
print("OK charts:",sorted(os.listdir("charts")))
print(open("data/MANIFEST.txt").read())
