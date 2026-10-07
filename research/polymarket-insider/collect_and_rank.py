#!/usr/bin/env python3
"""Reproducible, public-data screen for unusual Polymarket trading.

This is a triage tool. It does not identify a person or prove that a trader had
material non-public information. Its output is a short, auditable queue of
trades that deserve a human investigation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import statistics
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

GAMMA = "https://gamma-api.polymarket.com/markets"
TRADES = "https://data-api.polymarket.com/trades"
START = datetime(2025, 11, 1, tzinfo=timezone.utc)
END = datetime(2026, 5, 1, tzinfo=timezone.utc)
# Gamma can filter scheduled endDate but not actual closedTime. Search a wider
# scheduled window, then apply the stated analysis period to actual closure.
SCHEDULED_LOOKUP_PAD = timedelta(days=90)
GAMMA_PAGE_MAX_OFFSET = 2_000
MIN_REPORTED_VOLUME = 900_000
MAX_REPORTED_VOLUME = 3_000_000
RAW_TRADE_FIELDS = (
    "proxyWallet", "side", "asset", "conditionId", "size", "price", "timestamp",
    "title", "slug", "eventSlug", "outcome", "outcomeIndex", "transactionHash",
)
FILL_ID_FIELDS = (
    "transactionHash", "timestamp", "proxyWallet", "asset", "outcome", "side", "price", "size",
)
NEWS_TERMS = re.compile(
    r"president|prime minister|election|government|shutdown|tariff|fed |"
    r"interest rate|iran|ukraine|ceasefire|strike|war |congress|senate|"
    r"supreme court|pope|nobel|impeach|cabinet|minister|referendum|vote",
    re.I,
)
SPORTS_TERMS = re.compile(
    r" vs\.? |nba|nfl|nhl|mlb|ufc|tennis|soccer|football|basketball|"
    r"esports|fifa|ncaa|premier league|serie a|la liga|atp|wta|golf|cricket",
    re.I,
)


def fetch_json(url: str, params: dict) -> list | dict:
    """GET public API JSON with a descriptive user agent and modest retry."""
    request = Request(f"{url}?{urlencode(params, doseq=True)}", headers={"User-Agent": "dni-polymarket-research/1.0"})
    for attempt in range(4):
        try:
            with urlopen(request, timeout=45) as response:
                return json.load(response)
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2**attempt)
    raise AssertionError("unreachable")


def as_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def resolution_time(market: dict) -> datetime:
    """Prefer actual closure to a scheduled market deadline.

    Some markets trade after their nominal endDate while resolution is pending.
    closedTime/umaEndDate is therefore the defensible cutoff for a timing test.
    """
    return as_utc(market.get("closedTime") or market.get("umaEndDate") or market["endDate"])


def epoch(value: datetime) -> int:
    return int(value.timestamp())


def parse_json_field(value: str | list | None) -> list:
    if isinstance(value, list):
        return value
    if not value:
        return []
    return json.loads(value)


def fill_identity(row: dict) -> tuple[str, ...]:
    """Stable fill identity; a transaction may contain several same-second fills."""
    return tuple(str(row.get(field, "")) for field in FILL_ID_FIELDS)


def scheduled_windows() -> list[tuple[datetime, datetime]]:
    """Monthly candidate windows keep Gamma pagination bounded and auditable."""
    cursor, finish = START - SCHEDULED_LOOKUP_PAD, END + SCHEDULED_LOOKUP_PAD
    windows = []
    while cursor < finish:
        next_month = (cursor.replace(day=28) + timedelta(days=4)).replace(day=1)
        upper = min(next_month, finish)
        windows.append((cursor, upper))
        cursor = upper
    return windows


def selected_markets(limit: int) -> list[dict]:
    """Use a pre-declared topical filter, not a post-hoc winning-wallet filter."""
    raw_by_id = {}
    # Gamma allows offset pagination, capped at 2,000. A dense scheduled-date
    # bucket is bisected until its result set is fully retrievable.
    def fetch_scheduled_window(scheduled_start: datetime, scheduled_end: datetime) -> None:
        for offset in range(0, GAMMA_PAGE_MAX_OFFSET + 1, 100):
            page = fetch_json(
                GAMMA,
                {
                    "closed": "true",
                    "end_date_min": scheduled_start.isoformat().replace("+00:00", "Z"),
                    "end_date_max": scheduled_end.isoformat().replace("+00:00", "Z"),
                    "volume_num_min": MIN_REPORTED_VOLUME,
                    "volume_num_max": MAX_REPORTED_VOLUME,
                    "order": "volume",
                    "ascending": "false",
                    "limit": 100,
                    "offset": offset,
                },
            )
            for market in page:
                raw_by_id[str(market.get("id"))] = market
            if len(page) < 100:
                return
        else:
            if scheduled_end - scheduled_start <= timedelta(days=1):
                raise RuntimeError(
                    f"Gamma result cap reached even for {scheduled_start.date()}; refusing partial market discovery."
                )
            midpoint = scheduled_start + (scheduled_end - scheduled_start) / 2
            fetch_scheduled_window(scheduled_start, midpoint)
            fetch_scheduled_window(midpoint, scheduled_end)

    for scheduled_start, scheduled_end in scheduled_windows():
        fetch_scheduled_window(scheduled_start, scheduled_end)
    eligible = []
    for market in raw_by_id.values():
        question = market.get("question", "")
        outcomes, prices = parse_json_field(market.get("outcomes")), parse_json_field(market.get("outcomePrices"))
        resolved = len(outcomes) == len(prices) == 2 and sum(float(p) >= 0.99 for p in prices) == 1
        # Cap at $3m reported volume: this is a deliberately auditable,
        # complete-tape pilot, not a sampled analysis of a mega-market.
        # The cap is fixed before reading any wallet-level result.
        volume = float(market.get("volume") or 0)
        resolved_at = resolution_time(market)
        if not (
            resolved
            and START <= resolved_at < END
            and MIN_REPORTED_VOLUME <= volume <= MAX_REPORTED_VOLUME
            and NEWS_TERMS.search(question)
            and not SPORTS_TERMS.search(question)
        ):
            continue
        if not market.get("conditionId") or not as_utc(market.get("endDate")):
            continue
        eligible.append(market)
    # The API's volume ordering is lexical for a subset of historical records.
    # Sort numerically here, then make the deterministic first N selection.
    eligible.sort(key=lambda m: (-float(m.get("volume") or 0), str(m.get("id"))))
    return eligible[:limit]


def trade_windows(market: dict) -> list[tuple[int, int]]:
    """Monthly windows avoid the API's 10k-offset ceiling for busy markets."""
    finish = min(resolution_time(market), END)
    start_date = as_utc(market.get("startDate")) or as_utc(market.get("createdAt"))
    # Gamma's startDate can be populated with a post-resolution update time.
    # It is not safe as a lower retrieval bound if it follows endDate.
    begin = start_date if start_date and start_date < finish else (finish.replace(day=1) - __import__("datetime").timedelta(days=120))
    begin = max(begin, START)
    windows = []
    cursor = begin
    while cursor < finish:
        next_month = (cursor.replace(day=28) + __import__("datetime").timedelta(days=4)).replace(day=1)
        upper = min(next_month, finish)
        windows.append((epoch(cursor), epoch(upper)))
        cursor = upper
    return windows


def fetch_market_trades(market: dict, page_size: int) -> tuple[list[dict], bool]:
    rows = []
    for start, end in trade_windows(market):
        window_rows = []
        offset = 0
        while offset <= 10_000:
            page = fetch_json(TRADES, {"market": market["conditionId"], "start": start, "end": end, "limit": page_size, "offset": offset, "takerOnly": "true"})
            window_rows.extend(page)
            if len(page) < page_size:
                break
            offset += page_size
        else:
            # Do not score a market whose tape is incomplete in even one
            # window: missing rows corrupt both price baselines and rankings.
            return [], True
        rows.extend(window_rows)
    unique = {fill_identity(row): row for row in rows}
    return sorted(unique.values(), key=lambda r: (int(r["timestamp"]), fill_identity(r))), False


def winner(market: dict) -> str:
    outcomes, prices = parse_json_field(market["outcomes"]), parse_json_field(market["outcomePrices"])
    return outcomes[max(range(len(prices)), key=lambda i: float(prices[i]))]


def prior_prices(rows: list[dict]) -> dict[tuple[str, ...], float | None]:
    """Trailing 20-fill median per outcome; no future market information leaks in."""
    history: dict[str, list[float]] = defaultdict(list)
    baseline = {}
    for row in rows:
        key = fill_identity(row)
        values = history[row["outcome"]]
        # The score uses exactly the documented preceding-20 median. Warm-up
        # fills receive no dislocation component instead of borrowing their own
        # price, which would disguise a different calculation.
        baseline[key] = statistics.median(values[-20:]) if len(values) >= 20 else None
        values.append(float(row["price"]))
    return baseline


def score_rows(markets: list[dict], trades: list[dict]) -> tuple[list[dict], list[dict]]:
    market_by_condition = {m["conditionId"]: m for m in markets}
    by_market: dict[str, list[dict]] = defaultdict(list)
    for row in trades:
        by_market[row["conditionId"]].append(row)
    candidate_trades = []
    wallet_market = defaultdict(lambda: {"buy_notional": 0.0, "buy_shares": 0.0, "winner_buy_notional": 0.0, "winner_buy_shares": 0.0, "markets": set(), "signals": []})
    for condition, rows in by_market.items():
        market = market_by_condition[condition]
        final_outcome = winner(market)
        end_epoch = epoch(resolution_time(market))
        baseline = prior_prices(rows)
        for row in rows:
            wallet = row.get("proxyWallet", "").lower()
            notional, price, size = float(row["size"]) * float(row["price"]), float(row["price"]), float(row["size"])
            stat = wallet_market[wallet]
            stat["markets"].add(condition)
            if row["side"] == "BUY":
                stat["buy_notional"] += notional
                stat["buy_shares"] += size
                if row["outcome"] == final_outcome:
                    stat["winner_buy_notional"] += notional
                    stat["winner_buy_shares"] += size
            if row["side"] != "BUY" or row["outcome"] != final_outcome:
                continue
            hours_to_end = max(0, (end_epoch - int(row["timestamp"])) / 3600)
            pre_price = baseline[fill_identity(row)]
            # Components deliberately need both low implied probability and meaningful stake.
            # Below 50 cents, the eventual winner was still the market's
            # minority view. This is intentionally a screening threshold, not
            # a statement that a 49-cent trade is extraordinary by itself.
            cheap_winner = max(0, min(1, (0.50 - price) / 0.50))
            # A one-week window is long enough to catch a non-public briefing,
            # while still excluding ordinary long-horizon thesis positions.
            late = max(0, min(1, (168 - hours_to_end) / 168))
            stake = max(0, min(1, math.log10(max(notional, 1)) / 4))
            dislocation = max(0, min(1, (price - pre_price) / 0.15)) if pre_price is not None else 0
            trade_score = 100 * (0.40 * cheap_winner + 0.25 * late + 0.20 * stake + 0.15 * dislocation)
            # A near-certain purchase minutes before resolution is normal exit
            # liquidity, not an informed low-probability bet. Require each
            # candidate to carry a non-zero cheap-winner component.
            if cheap_winner > 0 and trade_score >= 30 and notional >= 250:
                signal = {
                    "wallet": wallet,
                    "market_id": market["id"],
                    "condition_id": condition,
                    "question": market["question"],
                    "trade_time_utc": datetime.fromtimestamp(int(row["timestamp"]), tz=timezone.utc).isoformat(),
                    "hours_to_resolution": round(hours_to_end, 2),
                    "outcome": row["outcome"],
                    "fill_price": round(price, 5),
                    "pre_trade_median_price": round(pre_price, 5) if pre_price is not None else "",
                    "shares": round(size, 4),
                    "notional_usd": round(notional, 2),
                    "score_cheap_winner": round(100 * cheap_winner, 1),
                    "score_late_entry": round(100 * late, 1),
                    "score_stake": round(100 * stake, 1),
                    "score_dislocation": round(100 * dislocation, 1),
                    "trade_signal_score": round(trade_score, 1),
                    "transaction_hash": row.get("transactionHash", ""),
                }
                candidate_trades.append(signal)
                stat["signals"].append(signal)
    ranking = []
    for wallet, stat in wallet_market.items():
        signals = stat["signals"]
        if not signals:
            continue
        # Repeatability matters more than one fortuitous correct trade.
        top_signals = sorted(signals, key=lambda item: item["trade_signal_score"], reverse=True)[:5]
        flagged_market_count = len({s["condition_id"] for s in signals})
        repeatability = min(100, 35 * (flagged_market_count - 1))
        precision = 100 * stat["winner_buy_notional"] / stat["buy_notional"] if stat["buy_notional"] else 0
        score = 0.65 * statistics.mean(s["trade_signal_score"] for s in top_signals) + 0.20 * repeatability + 0.15 * min(100, precision)
        ranking.append({
            "rank": 0,
            "wallet": wallet,
            "investigation_priority_score": round(score, 1),
            "flagged_trade_count": len(signals),
            "flagged_market_count": flagged_market_count,
            "corroborated_across_markets": flagged_market_count >= 2,
            "assessment": "cross-market pattern" if flagged_market_count >= 2 else "single-market lead",
            "scoped_market_count": len(stat["markets"]),
            "winning_buy_notional_usd": round(stat["winner_buy_notional"], 2),
            "all_buy_notional_usd": round(stat["buy_notional"], 2),
            "winner_buy_share_pct": round(precision, 1),
            "strongest_trade_score": top_signals[0]["trade_signal_score"],
            "strongest_trade_tx": top_signals[0]["transaction_hash"],
        })
    ranking.sort(key=lambda item: (-item["investigation_priority_score"], -item["winning_buy_notional_usd"], item["wallet"]))
    for index, row in enumerate(ranking, 1):
        row["rank"] = index
    candidate_trades.sort(key=lambda item: (-item["trade_signal_score"], -item["notional_usd"], item["wallet"]))
    return ranking, candidate_trades


def spreadsheet_safe(value: object) -> object:
    """Prevent spreadsheet apps evaluating public text fields as formulas."""
    if isinstance(value, str) and value[:1] in ("=", "+", "-", "@"):
        return "'" + value
    return value


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        writer.writerows([{key: spreadsheet_safe(value) for key, value in row.items()} for row in rows])


def cluster_leads(candidates: list[dict]) -> list[dict]:
    """Small market-level case cards prevent a wallet leaderboard from hiding a crowd event."""
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in candidates:
        grouped[(row["market_id"], row["question"])].append(row)
    output = []
    for (market_id, question), rows in grouped.items():
        output.append({
            "market_id": market_id,
            "question": question,
            "flagged_fills": len(rows),
            "distinct_wallets": len({row["wallet"] for row in rows}),
            "total_flagged_notional_usd": round(sum(float(row["notional_usd"]) for row in rows), 2),
            "first_flagged_fill_utc": min(row["trade_time_utc"] for row in rows),
            "last_flagged_fill_utc": max(row["trade_time_utc"] for row in rows),
            "max_trade_signal_score": max(float(row["trade_signal_score"]) for row in rows),
        })
    return sorted(output, key=lambda row: (-row["max_trade_signal_score"], -row["total_flagged_notional_usd"]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "artifacts")
    parser.add_argument("--markets", type=int, default=12, help="topically eligible markets to investigate")
    parser.add_argument("--page-size", type=int, default=500)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    markets = selected_markets(args.markets)
    if not markets:
        raise SystemExit("No resolved markets met the pre-declared selection rule.")
    selection, all_trades = [], []
    for number, market in enumerate(markets, 1):
        rows, saturated = fetch_market_trades(market, args.page_size)
        selection.append({
            "selection_order": number, "market_id": market["id"], "condition_id": market["conditionId"],
            "question": market["question"], "scheduled_end_date_utc": market["endDate"],
            "resolution_time_utc": resolution_time(market).isoformat(),
            "reported_volume_usd": round(float(market.get("volume") or 0), 2), "resolved_outcome": winner(market),
            "retrieved_taker_trades": len(rows), "window_saturated": saturated,
            "retrieval_status": "incomplete_excluded" if saturated else "complete",
        })
        all_trades.extend(rows)
        print(f"[{number}/{len(markets)}] {market['id']}: {len(rows)} trades")
    ranked, candidates = score_rows(markets, all_trades)
    write_csv(args.output / "market_selection.csv", selection)
    # Keep evidence sufficient to reproduce every score while excluding
    # display-name, bio and image fields that are unrelated to the analysis.
    raw_evidence = [{field: row.get(field, "") for field in RAW_TRADE_FIELDS} for row in all_trades]
    write_csv(args.output / "all_taker_trades.csv", raw_evidence)
    write_csv(args.output / "wallet_ranking.csv", ranked)
    write_csv(args.output / "candidate_trades.csv", candidates)
    write_csv(args.output / "lead_clusters.csv", cluster_leads(candidates))
    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(), "analysis_window": [START.isoformat(), END.isoformat()],
        "market_count": len(markets), "trade_count": len(all_trades), "candidate_trade_count": len(candidates),
        "ranking_count": len(ranked), "api_sources": [GAMMA, TRADES],
        "scheduled_lookup_pad_days": SCHEDULED_LOOKUP_PAD.days,
        "csv_formula_escaping": "apostrophe-prefix for strings beginning = + - @",
        "complete_market_count": sum(row["retrieval_status"] == "complete" for row in selection),
        "incomplete_market_count": sum(row["retrieval_status"] != "complete" for row in selection),
    }
    (args.output / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    checksums = []
    for path in sorted(args.output.glob("*.csv")):
        checksums.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    (args.output / "checksums.sha256").write_text("\n".join(checksums) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
