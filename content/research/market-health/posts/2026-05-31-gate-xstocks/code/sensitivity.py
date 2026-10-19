"""How the flagged set moves with the clip normalisation cap.

Rescores the 13 markets liquid enough to score, plus the SOL and LINK controls, with
the clip cap in metrics_lib.score_from set from 0.10 to 0.20 instead of 0.15, and
writes one row per cap to data/sensitivity.csv. Reads the market list from
data/screen.json, so run it after screen.py.
"""
import os
import json
import pandas as pd
from gatelib import load, load_sizes
from metrics_lib import metrics, metrics_from_sizes, score_from
from paths import DATA

MONTH = "202605"
CAPS = [round(0.10 + 0.01 * i, 2) for i in range(11)]
CONTROLS = ["MSTRX", "SOL", "LINK"]

screen = json.load(open(os.path.join(DATA, "screen.json")))
FLAG = screen["flag_threshold"]
reliable = [m["symbol"] for m in screen["markets"] if m["reliable"]]
M = {s: metrics(load(s, MONTH)) for s in reliable}
M.update({s: metrics_from_sizes(load_sizes(s, MONTH)) for s in ("SOL", "LINK")})
for m in screen["markets"]:
    if m["reliable"]:
        assert round(M[m["symbol"]]["score"], 3) == m["score"], m["symbol"]

base = set(screen["flagged"])
rows = []
for cap in CAPS:
    sc = {s: score_from(m["clip_share"], m["clip_net"], m["benford_ks"], clip_cap=cap) for s, m in M.items()}
    flagged = [s for s in reliable if sc[s] >= FLAG]
    others = [s for s in reliable if s not in flagged and s != "MSTRX"]
    top = max(others, key=lambda s: sc[s])
    rows.append(dict(clip_cap=cap, n_flagged=len(flagged), flagged=" ".join(flagged),
                     same_as_screen=set(flagged) == base, min_flagged_score=round(min(sc[s] for s in flagged), 3),
                     top_unflagged=top, top_unflagged_score=round(sc[top], 3),
                     **{f"{s}_score": round(sc[s], 3) for s in CONTROLS}))
out = pd.DataFrame(rows)
out.to_csv(os.path.join(DATA, "sensitivity.csv"), index=False)
print(out.drop(columns="flagged").to_string(index=False))
print("\nwrote data/sensitivity.csv")
