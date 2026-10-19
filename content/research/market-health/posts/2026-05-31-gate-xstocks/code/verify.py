"""Independently recompute and assert the mechanism numbers in index.md.

Reruns the metrics from the raw Gate dumps (not from build_analysis) and checks
them against findings.json plus the thresholds stated in the post. It also runs
the coordination / matched-pair / schedule checks in "What this is, and what it
is not" and writes their values to data/robustness.json. Exits non-zero on any
mismatch between the post's claims and the data.
"""
import os
import json
import itertools
import numpy as np
import pandas as pd
from gatelib import load
from metrics_lib import benford_ks, first_digit_shares

from paths import DATA

F = json.load(open(os.path.join(DATA, "findings.json")))
WASHED = ["HOODX", "SPYX", "TSLAX", "NVDAX", "AAPLX", "GOOGLX"]
CONTROL = "MSTRX"

# load every dump once; tag each trade as belonging to that market's dominant clip
D = {s: load(s) for s in WASHED + [CONTROL]}
for s, df in D.items():
    df["isclip"] = df["amt"] == F[s]["top_clip_qty"]


def recompute(df):
    n = len(df)
    vc = df["amt"].value_counts()
    top_qty = float(vc.index[0]); top_share = float(vc.iloc[0] / n)
    clip = df[df["amt"] == top_qty]
    buyshare = float(clip["buy"].mean())
    cn = float(clip["notional"].sum())
    buy_n = float(clip.loc[clip["buy"], "notional"].sum())
    net = abs(2 * buy_n - cn) / cn
    dshare = cn / float(df["notional"].sum())
    obs, ks = first_digit_shares(df["amt"]), benford_ks(df["amt"])
    return n, top_qty, top_share, buyshare, net, cn, dshare, ks, float(obs[1]), int(df["amt"].nunique())


# ---- per-market headline numbers reproduce findings.json ----
for sym in WASHED + [CONTROL]:
    n, top_qty, top_share, buyshare, net, cn, dshare, ks, d1, distinct = recompute(D[sym])
    f = F[sym]
    assert n == f["n_trades"], (sym, "n_trades", n, f["n_trades"])
    assert abs(top_qty - f["top_clip_qty"]) < 1e-9, (sym, "top_clip_qty")
    assert abs(top_share - f["top_clip_share"]) < 5e-4, (sym, "top_clip_share")
    assert abs(buyshare - f["clip_buyshare"]) < 5e-3, (sym, "clip_buyshare")
    assert abs(net - f["clip_net_pct"]) < 5e-3, (sym, "clip_net_pct", net, f["clip_net_pct"])
    assert abs(cn - f["clip_notional"]) / cn < 1e-3, (sym, "clip_notional")
    assert abs(dshare - f["clip_dollar_share"]) < 5e-4, (sym, "clip_dollar_share")
    assert abs(ks - f["benford_ks"]) < 5e-3, (sym, "benford_ks")
    assert abs(d1 - f["digit1"]) < 5e-3, (sym, "digit1", d1, f["digit1"])
    assert distinct == f["distinct_sizes"], (sym, "distinct_sizes", distinct, f["distinct_sizes"])
    print(f"  {sym:7} n={n:,} clip={top_share:.1%} net={net:.0%} ${cn:,.0f}({dshare:.1%}) KS={ks:.2f}  reproduced")

# ---- washed set: dominant clip, circular (nets to ~no position), Benford broken ----
for s in WASHED:
    assert F[s]["top_clip_share"] > 0.16, (s, "clip share")
    assert 0.42 < F[s]["clip_buyshare"] < 0.48, (s, "two-sided balance")
    assert F[s]["clip_net_pct"] < 0.15, (s, "circular: nets to almost no position")
    assert F[s]["benford_ks"] > 0.09, (s, "Benford break")
    assert F[s]["daybuy_std"] < 0.15, (s, "held daily balance")
    assert F[s]["clip_dollar_share"] < F[s]["top_clip_share"], (s, "dollars < trade share")

h = F["HOODX"]
assert h["top_clip_qty"] == 0.12 and h["top_clip_share"] > 0.49, "HOODX 0.12 clip = 49.4%"
assert h["n_trades"] == 65164 and h["days"] == 31, "HOODX 65,164 trades / 31 days"
assert h["day_clip_min"] > 0.20 and h["day_clip_max"] > 0.77 and 0.45 < h["day_clip_med"] < 0.49, \
    "HOODX daily band: never below 21%, peaks above 77%, median 47%"
assert h["distinct_sizes"] == 1808 and h["clip_net_pct"] < 0.10, "HOODX 1,808 sizes / circular"
assert h["digit1"] > 0.64, "HOODX leading-digit-1 up to 64.7%"
assert 9 < 0.12 * (h["price_first"] + h["price_last"]) / 2 < 11, "HOODX 0.12 clip is about $10"
for s in ("SPYX", "NVDAX"):
    assert 0.18 < F[s]["digit1"] < 0.22, (s, "digit-1 pulled down to about 20%")
dt = [F[s]["daily_turnover_usd"] for s in WASHED]
assert 26000 < min(dt) < 28000 and 340000 < max(dt) < 360000, "turnover spans about $27k to $350k a day"

m = F["_meta"]
wc = sum(F[s]["clip_notional"] for s in WASHED)
wr = sum(F[s]["turnover_usd"] for s in WASHED)
assert abs(wc / wr - m["clip_dollar_share"]) < 1e-3 and m["clip_dollar_share"] < 0.10, "trade count >> dollars"
assert m["clip_trade_share_max"] > 0.45 and m["clip_trade_share_min"] > 0.16, "17-49% of trades"

c = F[CONTROL]
assert c["top_clip_share"] < 0.08 and c["clip_net_pct"] > 0.85 and c["benford_ks"] < 0.06, "MSTRX clean"
assert c["daily_turnover_usd"] > sorted(F[s]["daily_turnover_usd"] for s in WASHED)[3], \
    "MSTRX out-turns 4 of 6 washed"

# ---- robustness: the clip is independent per market, not coordinated / matched / scheduled ----
MIN = pd.Index(sorted(set().union(*[set((D[s]["ts"] // 60).astype(int)) for s in WASHED])))


def per_minute(s, clip_only):
    mins = (D[s]["ts"] // 60).astype(int)
    sub = mins[D[s]["isclip"]] if clip_only else mins
    return sub.value_counts().reindex(MIN, fill_value=0)


clipM = pd.DataFrame({s: per_minute(s, True) for s in WASHED})
allM = pd.DataFrame({s: per_minute(s, False) for s in WASHED})
pairs = list(itertools.combinations(WASHED, 2))
corr_clip = float(np.mean([clipM.corr().loc[a, b] for a, b in pairs]))
corr_all = float(np.mean([allM.corr().loc[a, b] for a, b in pairs]))
assert corr_clip < corr_all and corr_clip < 0.15, ("not coordinated", corr_clip, corr_all)
assert round(corr_clip, 2) == 0.08 and round(corr_all, 2) == 0.11, ("coordination values", corr_clip, corr_all)

# same-second coincidence across >=3 markets is at chance level
sec_count = {}
for s in WASHED:
    for t in set(D[s].loc[D[s]["isclip"], "ts"].astype(int)):
        sec_count[t] = sec_count.get(t, 0) + 1
ge3 = sum(1 for v in sec_count.values() if v >= 3)
assert ge3 / len(sec_count) < 0.01, ("same-second coincidence above chance", ge3 / len(sec_count))

# matched opposite-side same-price clip pairs are far below a side-shuffled baseline (seeded)
def matched(df, side):
    ic = df["isclip"].values
    nxt = np.r_[ic[1:], False]
    same_px = np.r_[df["price"].values[1:] == df["price"].values[:-1], False]
    near = np.r_[np.abs(np.diff(df["ts"].values)) < 1.0, False]
    opp = np.r_[side[1:] != side[:-1], False]
    return int((ic & nxt & opp & same_px & near).sum())


rng = np.random.default_rng(0)
real = shuf = 0
for s in WASHED:
    df = D[s].sort_values("id").reset_index(drop=True)
    df["isclip"] = df["amt"] == F[s]["top_clip_qty"]
    side = df["side"].values
    real += matched(df, side)
    sh = side.copy(); cl = np.where(df["isclip"].values)[0]; sh[cl] = rng.permutation(sh[cl])
    shuf += matched(df, sh)
assert real < shuf / 10, ("matched pairs not below shuffle", real, shuf)

# the HOODX clip is bursty, not pinned to a second of the minute
busiest_sec = float((D["HOODX"].loc[D["HOODX"]["isclip"], "ts"].astype(int) % 60)
                    .value_counts(normalize=True).max())
assert busiest_sec < 0.04, ("clip is clock-scheduled / second pinned", busiest_sec)

json.dump(dict(markets=WASHED, clip_minute_corr=round(corr_clip, 4), all_minute_corr=round(corr_all, 4),
               same_second_ge3_share=round(ge3 / len(sec_count), 5), matched_pairs=real,
               matched_pairs_shuffled=shuf, hoodx_busiest_second_share=round(busiest_sec, 4)),
          open(os.path.join(DATA, "robustness.json"), "w"), indent=2)

print("wash set:", ", ".join(WASHED), "| control:", CONTROL)
print(f"manufactured: ${wc:,.0f} = {m['clip_dollar_share']:.1%} of ${wr:,.0f} reported, "
      f"but {m['clip_trade_share_min']:.0%}-{m['clip_trade_share_max']:.0%} of trades")
print(f"robustness: clip-corr {corr_clip:.2f} < all-corr {corr_all:.2f} (not coordinated) | "
      f"matched {real} vs {shuf} shuffle (not matched-pair) | busiest second {busiest_sec:.1%} (not scheduled)")
print("ALL CHECKS PASS")
