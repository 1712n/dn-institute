"""Choose the markets to screen and count what each filter removes.

Reads data/markets_window.csv.xz (every market that closed in the window) and applies the
filters in order. A market leaves at the first filter it fails, so the counts add up. The
markets that pass take their details from data/markets_window_detail.csv.xz, and a last filter
drops the price-level markets that carry no price tag, by words in the question.
"""
import json
import os
import sys

import pandas as pd

SPORTS = {"sports", "games", "esports", "poker-game"}
PRICE = {"crypto-prices", "up-or-down", "hit-price", "stock-prices", "daily-close", "indicies",
         "pre-market", "monthly-hit", "commodities", "open", "multi-strikes", "5M", "15M", "1H", "4h",
         "parcl", "real-estate", "housing", "gold", "silver", "oil", "comex-gold-futures",
         "comex-silver-futures", "nymex-crude-oil-futures"}
WEATHER = {"weather", "daily-temperature", "temperature", "climate-science"}
RECURRING = {"recurring", "daily", "weekly", "monthly", "tweets-markets", "mention-markets",
             "top-netflix", "netflix", "app-store", "charts", "billboard", "spotify", "box-office",
             "youtube", "mrbeast", "tsa", "songs", "albums"}
MACRO = {"fed", "fed-rates", "jerome-powell", "macro-indicators", "inflation", "cpi", "gdp",
         "unemployment", "Global-Rates", "jobs-report"}
ELECTION_WORDS = ("election", "primar", "mayor")
VOLUME_FLOOR = 100_000
PRICE_WORDS = ("market cap", "all time high", "all-time high", "fdv", "hit $", "above $",
               "below $", "price", "close at", "ipo day", "52-week", "net worth", "trillionaire",
               "% of s&p")


def decisive(prices):
    try:
        return sorted(float(p) for p in json.loads(prices)) == [0.0, 1.0]
    except (TypeError, ValueError):
        return False


def is_election(tags):
    return any(w in t for t in tags for w in ELECTION_WORDS)


FILTERS = [
    ("not_decisive", lambda m, t: not decisive(m["outcomePrices"])),
    ("sports", lambda m, t: bool(t & SPORTS) or m["sportsMarketType"] == 1),
    ("price_level", lambda m, t: bool(t & PRICE)),
    ("weather", lambda m, t: bool(t & WEATHER)),
    ("recurring_or_count", lambda m, t: bool(t & RECURRING)),
    ("scheduled_macro_release", lambda m, t: bool(t & MACRO)),
    ("election", lambda m, t: is_election(t)),
    ("volume_below_floor", lambda m, t: not m["volumeNum"] >= VOLUME_FLOOR),
]
LAST = ("price_level_by_question", lambda q: any(w in str(q).lower() for w in PRICE_WORDS))


def apply(window):
    removed = {name: 0 for name, _ in FILTERS}
    keep = []
    for _, m in window.iterrows():
        tags = set(str(m["tags"]).split("|")) if isinstance(m["tags"], str) else set()
        for name, rule in FILTERS:
            if rule(m, tags):
                removed[name] += 1
                break
        else:
            keep.append(m)
    return pd.DataFrame(keep), removed


def main(window_path, detail_path, out_scope, out_counts):
    window = pd.read_csv(window_path, dtype={"id": str})
    detail = pd.read_csv(detail_path, dtype={"id": str, "event_id": str, "negRisk": str})
    kept, removed = apply(window)
    scope = detail[detail["id"].isin(set(kept["id"]))].copy()
    if len(scope) != len(kept):
        raise RuntimeError("a scoped market has no detail row")
    price_q = scope["question"].map(LAST[1])
    removed[LAST[0]] = int(price_q.sum())
    scope = scope[~price_q]
    rows = [("closed_in_window", len(window))]
    left = len(window)
    for name in [n for n, _ in FILTERS] + [LAST[0]]:
        left -= removed[name]
        rows.append((f"removed_{name}", removed[name]))
        rows.append((f"left_after_{name}", left))
    pd.DataFrame(rows, columns=["step", "markets"]).to_csv(out_counts, index=False)
    for r in rows:
        print(*r)
    if os.path.exists(out_scope) and "t_known" in pd.read_csv(out_scope, nrows=0).columns:
        packed = set(pd.read_csv(out_scope, usecols=["conditionId"])["conditionId"])
        if packed != set(scope["conditionId"]):
            raise RuntimeError("the filters no longer give the committed market list")
        print("filters give the committed market list")
        return
    scope["winner_index"] = scope["outcomePrices"].map(lambda s: [float(p) for p in json.loads(s)].index(1.0))
    scope.to_csv(out_scope, index=False)


if __name__ == "__main__":
    main(*sys.argv[1:5])
