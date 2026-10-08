"""List resolved Polymarket markets that closed 2025-11-01..2026-05-01 via the public Gamma API."""
import json, sys, time
import requests

S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0"
URL = "https://gamma-api.polymarket.com/markets"
PAGE = 100


def main(out):
    rows, off = [], 0
    while True:
        r = S.get(URL, params={
            "closed": "true", "end_date_min": "2025-11-01T00:00:00Z",
            "end_date_max": "2026-05-01T00:00:00Z", "limit": PAGE, "offset": off,
            "order": "volumeNum", "ascending": "false"}, timeout=60)
        if r.status_code == 422:
            break  # the API refuses offsets past ~2100; the tail is the lowest-volume markets
        r.raise_for_status()
        page = r.json()
        rows += page
        print(off, len(page), file=sys.stderr)
        if len(page) < PAGE:
            break
        off += PAGE
        time.sleep(0.2)
    json.dump(rows, open(out, "w"))
    print(len(rows), "markets", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1])
