"""Download public trades for every in-scope market from the Polymarket Data API.

The endpoint returns newest first and refuses offsets past 10,000, so one query reaches at most
20,000 trades. A market is fetched in full when it has no more than that. Otherwise it is
fetched again with a cash filter that keeps only large trades, which is complete as long as
those fit in the same cap. Each market records which of the three cases it fell into.
"""
import csv
import gzip
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import requests

sys.path.insert(0, os.path.dirname(__file__))
from importlib import import_module

scope = import_module("03_scope")

URL = "https://data-api.polymarket.com/trades"
LIMIT = 10000
MAX_OFFSET = 10000
BIG_STEPS = (500, 2500, 10000, 50000)
FIELDS = ["proxyWallet", "side", "asset", "conditionId", "outcome", "outcomeIndex", "size",
          "price", "timestamp", "transactionHash"]

S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0"


def get(params):
    for attempt in range(6):
        r = S.get(URL, params=params, timeout=90)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 400 and "offset" in r.text:
            return None
        time.sleep(2 ** attempt)
    r.raise_for_status()


def pull(cid, extra):
    rows = []
    for off in range(0, MAX_OFFSET + 1, LIMIT):
        page = get({"market": cid, "limit": LIMIT, "offset": off, "takerOnly": "false", **extra})
        if page is None:
            return rows, True
        rows += page
        if len(page) < LIMIT:
            return rows, False
    return rows, True  # the last permitted page is full, so older trades may exist


def fetch_market(cid):
    rows, capped = pull(cid, {})
    if not capped:
        return rows, "full"
    for usd in BIG_STEPS:
        rows, capped = pull(cid, {"filterType": "CASH", "filterAmount": usd})
        if not capped:
            return rows, f"big_only_{usd}"
    return rows, "big_only_capped"


def work(m, outdir):
    cid = m["conditionId"]
    rows, kind = fetch_market(cid)
    with gzip.open(os.path.join(outdir, cid + ".csv.gz"), "wt", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return cid, {"n": len(rows), "kind": kind, "volume": m["volumeNum"]}


def main(markets_path, tags_path, outdir, workers=6):
    os.makedirs(outdir, exist_ok=True)
    manifest_path = os.path.join(outdir, "manifest.json")
    manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {}
    universe = scope.in_scope(json.load(open(markets_path)), json.load(open(tags_path)))
    todo = [m for m, _ in sorted(universe, key=lambda mt: -mt[0]["volumeNum"]) if m["conditionId"] not in manifest]
    with ThreadPoolExecutor(max_workers=int(workers)) as pool:
        for i, (cid, info) in enumerate(pool.map(lambda m: work(m, outdir), todo)):
            manifest[cid] = info
            json.dump(manifest, open(manifest_path, "w"))
            print(i, cid[:10], info["n"], info["kind"], flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:5])
