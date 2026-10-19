"""Build the committed size tables for the SOL and LINK controls from their raw Gate dumps.

The raw May 2026 dumps for SOL/USDT and LINK/USDT are 23 MB and 8.5 MB, so the post
commits one row per distinct trade size instead: the size, its trade count, its
notional and its taker-buy notional. That is everything the screen reads from these
two markets. The raw dumps are downloaded and checked against SHA256SUMS.download, and the
script fails unless the table gives the same screen metrics as the trade list.
"""
import gzip
import os
import pandas as pd
from gatelib import load
from metrics_lib import metrics, metrics_from_sizes, size_table
from paths import TRADES

MONTH = "202605"

for sym in ("SOL", "LINK"):
    df = load(sym, MONTH)
    tab = size_table(df)
    path = os.path.join(TRADES, "gate", f"{sym}_USDT-{MONTH}.sizes.csv.gz")
    with gzip.GzipFile(path, "wb", mtime=0) as gz:
        gz.write(tab.to_csv(index=False).encode())
    with gzip.open(path, "rt") as fh:
        back = pd.read_csv(fh, float_precision="round_trip")
    a, b = metrics(df), metrics_from_sizes(back)
    for k in ("n_trades", "clip_qty", "clip_share", "benford_ks"):
        assert a[k] == b[k], (sym, k, a[k], b[k])
    for k in ("clip_net", "clip_notional", "score"):
        assert abs(a[k] - b[k]) <= 1e-9 * max(1.0, abs(a[k])), (sym, k, a[k], b[k])
    print(f"{sym}: {len(df):,} trades -> {len(tab):,} sizes, score {a['score']:.6f} = {b['score']:.6f}")
