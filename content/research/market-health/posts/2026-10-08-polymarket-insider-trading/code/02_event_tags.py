"""Attach Gamma event tags to the market list, 40 events per request."""
import json, sys, time
import requests

S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0"


def main(markets_path, out):
    markets = json.load(open(markets_path))
    ids = sorted({m["events"][0]["id"] for m in markets if m.get("events")})
    tags = {}
    for i in range(0, len(ids), 40):
        chunk = ids[i:i + 40]
        r = S.get("https://gamma-api.polymarket.com/events",
                  params=[("id", x) for x in chunk] + [("limit", 40)], timeout=60)
        r.raise_for_status()
        for e in r.json():
            tags[e["id"]] = {"slug": e["slug"], "title": e["title"],
                             "tags": [t["slug"] for t in e.get("tags", [])]}
        print(i, len(tags), file=sys.stderr)
        time.sleep(0.2)
    json.dump(tags, open(out, "w"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
