"""Download the full public trade tape of every scoped market from the Polymarket Data API.

/trades returns newest first and refuses offsets past 10,000, so one query reaches at most
20,000 trades. It also takes an `end` timestamp (inclusive) that keeps only older trades. The
walk takes up to 20,000 trades, moves `end` to the oldest second it saw, drops the rows from
that second (the next window returns all of them again) and repeats until a window comes back
short. The tape is complete unless one second alone holds more than 20,000 trades, which the
manifest would record as "capped". Maker and taker sides are both requested.

Raw tapes go to a directory outside the repository; 05_pack.py writes the committed copy.
"""
import csv
import gzip
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests

URL = "https://data-api.polymarket.com/trades"
LIMIT = 10000
FIELDS = ["proxyWallet", "side", "asset", "outcomeIndex", "size", "price", "timestamp", "transactionHash"]

S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0"


def get(params):
    for attempt in range(10):
        try:
            r = S.get(URL, params=params, timeout=120)
            if r.status_code == 200:
                return r.json()
        except requests.RequestException:
            pass
        time.sleep(min(2 ** attempt, 60))
    raise RuntimeError(f"trades request failed: {params}")


def window(cid, end):
    rows = []
    for off in (0, LIMIT):
        p = {"market": cid, "limit": LIMIT, "offset": off, "takerOnly": "false"}
        if end is not None:
            p["end"] = end
        page = get(p)
        rows += page
        if len(page) < LIMIT:
            return rows, False
    return rows, True


def fetch_market(cid):
    out, end, windows = [], None, 0
    while True:
        rows, more = window(cid, end)
        windows += 1
        if not more:
            out += rows
            return out, "full", windows
        oldest = min(r["timestamp"] for r in rows)
        keep = [r for r in rows if r["timestamp"] > oldest]
        if not keep:
            out += rows
            return out, "capped", windows
        out += keep
        end = oldest


def work(cid, outdir):
    rows, kind, windows = fetch_market(cid)
    with gzip.open(os.path.join(outdir, cid + ".csv.gz"), "wt", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return cid, {"n": len(rows), "kind": kind, "windows": windows}


def main(scope_path, outdir, workers=8):
    os.makedirs(outdir, exist_ok=True)
    manifest_path = os.path.join(outdir, "manifest.json")
    manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {}
    scope = pd.read_csv(scope_path)
    todo = [c for c in scope["conditionId"] if c not in manifest]
    print(len(todo), "markets to fetch", flush=True)
    with ThreadPoolExecutor(max_workers=int(workers)) as pool:
        for i, (cid, info) in enumerate(pool.map(lambda c: work(c, outdir), todo)):
            manifest[cid] = info
            if i % 20 == 0 or i == len(todo) - 1:
                json.dump(manifest, open(manifest_path, "w"))
            print(i, cid[:10], info["n"], info["kind"], info["windows"], flush=True)
    json.dump(manifest, open(manifest_path, "w"))


if __name__ == "__main__":
    main(*sys.argv[1:4])
