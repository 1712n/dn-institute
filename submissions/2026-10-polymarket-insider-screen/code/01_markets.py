"""Download every closed market the Gamma API lists, in slices by scheduled end date.

The plain /markets endpoint refuses offsets past 2,100, which silently cuts the tail of any
large query. /markets/keyset pages by market id with a cursor and has no such cap, so walking
it until the cursor runs out returns every market that matches the filter. The scheduled end
date (endDate) is only used to split the walk into slices that run in parallel. The slices
are contiguous and open at both ends, so together they cover every closed market that has an
end date at all. The window itself is applied later, on closedTime.

Writes one JSON line per market with the fields later steps use, and one log line per slice
that shows the slice ended on an empty cursor.
"""
import gzip
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import requests

URL = "https://gamma-api.polymarket.com/markets/keyset"
KEEP = ["id", "conditionId", "question", "slug", "endDate", "closedTime", "umaEndDate", "createdAt",
        "startDate", "outcomes", "outcomePrices", "volumeNum", "umaResolutionStatus", "negRisk",
        "negRiskMarketID", "groupItemTitle", "sportsMarketType", "automaticallyResolved"]
EDGES = [None, "2025-08-01", "2025-09-01", "2025-10-01", "2025-11-01", "2025-12-01", "2026-01-01",
         "2026-02-01", "2026-03-01", "2026-04-01", "2026-05-01", "2026-06-01", "2026-07-01",
         "2026-08-01", "2026-09-01", "2026-10-01", "2026-11-01", None]

VOLUME_STOP = 100_000

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
    raise RuntimeError(f"keyset request failed: {params}")


def slim(m):
    row = {k: m.get(k) for k in KEEP}
    ev = (m.get("events") or [None])[0] or {}
    row["event_id"] = ev.get("id")
    row["event_slug"] = ev.get("slug")
    row["event_title"] = ev.get("title")
    row["tags"] = sorted({t.get("slug") for t in (m.get("tags") or []) if t.get("slug")})
    return row


def walk(lo, hi, outdir):
    name = f"{lo or 'start'}_{hi or 'end'}"
    base = {"closed": "true", "limit": 100, "include_tag": "true"}
    if lo:
        base["end_date_min"] = lo + "T00:00:00Z"
    if hi:
        base["end_date_max"] = hi + "T00:00:00Z"
    cursor, pages, n, last_id, ids = None, 0, 0, -1, set()
    with gzip.open(os.path.join(outdir, name + ".jsonl.gz"), "wt") as f:
        while True:
            params = dict(base, after_cursor=cursor) if cursor else base
            j = get(params)
            rows = j.get("markets") or []
            for m in rows:
                if int(m["id"]) <= last_id:
                    raise RuntimeError(f"{name}: keyset order broken at id {m['id']}")
                last_id = int(m["id"])
                ids.add(m["id"])
                f.write(json.dumps(slim(m)) + "\n")
            n += len(rows)
            pages += 1
            cursor = j.get("next_cursor")
            if not cursor or not rows:
                break
    return {"slice": name, "end_date_min": lo or "", "end_date_max": hi or "", "pages": pages,
            "markets": n, "unique_ids": len(ids), "last_page_rows": len(rows),
            "walk_complete": not cursor}


def walk_volume(outdir):
    base = {"closed": "true", "limit": 100, "include_tag": "true", "order": "volumeNum", "ascending": "false"}
    cursor, pages, n, last_vol, ids = None, 0, 0, float("inf"), set()
    with gzip.open(os.path.join(outdir, "by_volume.jsonl.gz"), "wt") as f:
        while True:
            j = get(dict(base, after_cursor=cursor) if cursor else base)
            rows = j.get("markets") or []
            for m in rows:
                v = float(m.get("volumeNum") or 0)
                if v > last_vol + 1e-6:
                    raise RuntimeError(f"volume order broken at id {m['id']}")
                last_vol = v
                ids.add(m["id"])
                f.write(json.dumps(slim(m)) + "\n")
            n += len(rows)
            pages += 1
            cursor = j.get("next_cursor")
            if not cursor or not rows or last_vol < VOLUME_STOP:
                break
    return {"slice": "by_volume", "end_date_min": "", "end_date_max": "", "pages": pages, "markets": n,
            "unique_ids": len(ids), "last_page_rows": len(rows),
            "walk_complete": (not cursor) or last_vol < VOLUME_STOP}


def main(outdir, log):
    os.makedirs(outdir, exist_ok=True)
    pairs = list(zip(EDGES[:-1], EDGES[1:]))
    with ThreadPoolExecutor(max_workers=6) as pool:
        jobs = [pool.submit(walk, lo, hi, outdir) for lo, hi in pairs] + [pool.submit(walk_volume, outdir)]
        res = [j.result() for j in jobs]
    json.dump(res, open(log, "w"), indent=1)
    for r in res:
        print(r, flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
