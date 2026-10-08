"""Choose the analysis universe: resolved, decisive, non-sports, non-price markets."""
import json
import sys

EXCLUDE_TAGS = {
    "sports", "games", "esports", "crypto-prices", "hit-price", "recurring",
    "tweets-markets", "weather", "daily-temperature", "up-or-down",
}


def in_scope(markets, tags):
    out = []
    for m in markets:
        ev = (m.get("events") or [None])[0]
        if not ev:
            continue
        tg = set(tags[ev["id"]]["tags"])
        if tg & EXCLUDE_TAGS:
            continue
        try:
            prices = sorted(float(p) for p in json.loads(m["outcomePrices"]))
        except (KeyError, ValueError, TypeError):
            continue
        if prices != [0.0, 1.0]:
            continue
        out.append((m, tg))
    return out


if __name__ == "__main__":
    import collections
    import statistics

    markets = json.load(open(sys.argv[1]))
    tags = json.load(open(sys.argv[2]))
    sc = in_scope(markets, tags)
    vol = [m["volumeNum"] for m, _ in sc]
    print(len(sc), "markets", round(sum(vol) / 1e9, 2), "B USDC")
    print("median", statistics.median(vol), ">20M", sum(v > 2e7 for v in vol), "<5M", sum(v < 5e6 for v in vol))
    print(collections.Counter(g for _, tg in sc for g in tg).most_common(25))
