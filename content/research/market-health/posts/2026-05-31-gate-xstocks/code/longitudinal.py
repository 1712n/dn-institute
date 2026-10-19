"""When did the wash start? HOODX month by month since it listed on Gate.

Runs the screen metrics on every monthly HOODX/USDT dump from listing (2025-07)
to 2026-05 and writes the trajectory + an onset figure. The first month whose
clip share exceeds ELEVATED is the onset; the first month whose score reaches the
screen's flag threshold is when the market reads as clearly washed.
"""
import os
import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from gatelib import load
from metrics_lib import metrics

from paths import DATA, POST
FLAG = 0.80           # screen flag threshold (calibrated above the organic controls)
ELEVATED = 0.04       # over twice HOODX's own launch months (0.45 to 1.85% of trades, 2025-07 to 2025-09)
MONTHS = ["202507", "202508", "202509", "202510", "202511", "202512",
          "202601", "202602", "202603", "202604", "202605"]
LABEL = {m: f"{m[:4]}-{m[4:]}" for m in MONTHS}

rows = []
for m in MONTHS:
    r = metrics(load("HOODX", m))
    rows.append(dict(month=m, n_trades=r["n_trades"], clip_share=round(r["clip_share"], 4),
                     clip_net=round(r["clip_net"], 3), benford_ks=round(r["benford_ks"], 3),
                     clip_notional=round(r["clip_notional"], 0), score=round(r["score"], 3)))

first_elevated = next((r["month"] for r in rows if r["clip_share"] > ELEVATED), None)
flag_crossed = next((r["month"] for r in rows if r["score"] >= FLAG), None)
cum = sum(r["clip_notional"] for r in rows)
out = dict(symbol="HOODX", flag_threshold=FLAG, first_elevated_month=first_elevated,
           flag_crossed_month=flag_crossed, cumulative_clip_usd=round(cum, 0), months=rows)
json.dump(out, open(os.path.join(DATA, "longitudinal.json"), "w"), indent=2)
pd.DataFrame(rows).to_csv(os.path.join(DATA, "longitudinal.csv"), index=False)

print(f"HOODX first elevated clip: {first_elevated} | crosses flag (clearly washed): {flag_crossed}")
print(f"cumulative manufactured (clip) volume {MONTHS[0]}-{MONTHS[-1]}: ${cum:,.0f}\n")
print(" month     trades  clip%  score")
for r in rows:
    print(f" {LABEL[r['month']]}  {r['n_trades']:>7,} {r['clip_share']*100:5.1f}%  {r['score']:.2f}")

x = list(range(len(rows)))
fig, ax1 = plt.subplots(figsize=(9.5, 4.6))
ax1.bar(x, [r["clip_share"] * 100 for r in rows], color="#d9480f", width=0.62, label="clip share of trades (%)")
ax1.set_ylabel("dominant clip, % of trades", color="#d9480f"); ax1.set_ylim(0, 55)
ax2 = ax1.twinx()
ax2.plot(x, [r["score"] for r in rows], color="#1c1c1c", marker="o", lw=1.8, label="wash score")
ax2.axhline(FLAG, ls="--", color="#868e96", lw=1)
ax2.set_ylabel("non-organic-activity score"); ax2.set_ylim(0, 1.05)
if flag_crossed is not None:
    ci = [r["month"] for r in rows].index(flag_crossed)
    ax1.axvline(ci, color="#495057", ls=":", lw=1)
    ax1.text(ci + 0.1, 52, f"crosses the flag\n{LABEL[flag_crossed]}", fontsize=8, va="top")
ax1.set_xticks(x); ax1.set_xticklabels([LABEL[r["month"]] for r in rows], rotation=45, fontsize=8)
ax1.set_title("HOODX on Gate: organic at launch, an elevated clip from autumn 2025, clearly washed from spring 2026",
              fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(POST, "longitudinal.png"), dpi=120); plt.close()
print("\nwrote data/longitudinal.json + data/longitudinal.csv + longitudinal.png")
