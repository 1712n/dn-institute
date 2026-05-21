#!/usr/bin/env python3
"""Build the data tables and figures for the MYX market-health case study.

The script intentionally uses only Binance public market-data endpoints and
standard-library HTTP/CSV parsing so the article can be regenerated without
private exchange credentials.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import math
import time
import urllib.parse
import urllib.request
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

SYMBOL = "MYXUSDT"
BASE = Path(__file__).resolve().parent
UTC = dt.timezone.utc

START_1H = dt.datetime(2025, 9, 1, tzinfo=UTC)
END_1H = dt.datetime(2025, 9, 12, tzinfo=UTC)
EVENT_START = dt.datetime(2025, 9, 8, tzinfo=UTC)
EVENT_END = dt.datetime(2025, 9, 10, tzinfo=UTC)


def ms(value: dt.datetime) -> int:
    return int(value.timestamp() * 1000)


def iso_from_ms(value: int) -> str:
    return dt.datetime.fromtimestamp(value / 1000, UTC).isoformat()


def get_json(url: str, params: dict[str, object]) -> object:
    request_url = f"{url}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(request_url, timeout=30) as response:
        return json.loads(response.read())


def fetch_klines(interval: str, start: dt.datetime, end: dt.datetime) -> list[list[object]]:
    rows: list[list[object]] = []
    cursor = ms(start)
    end_ms = ms(end) - 1
    while cursor <= end_ms:
        batch = get_json(
            "https://fapi.binance.com/fapi/v1/klines",
            {
                "symbol": SYMBOL,
                "interval": interval,
                "startTime": cursor,
                "endTime": end_ms,
                "limit": 1500,
            },
        )
        if not isinstance(batch, list) or not batch:
            break
        rows.extend(batch)
        next_cursor = int(batch[-1][0]) + (60_000 if interval == "1m" else 3_600_000)
        if next_cursor <= cursor:
            break
        cursor = next_cursor
        time.sleep(0.05)
    return [r for r in rows if ms(start) <= int(r[0]) < ms(end)]


def fetch_special_klines(endpoint: str, interval: str, start: dt.datetime, end: dt.datetime) -> list[list[object]]:
    param_name = "pair" if endpoint == "indexPriceKlines" else "symbol"
    rows: list[list[object]] = []
    cursor = ms(start)
    end_ms = ms(end) - 1
    while cursor <= end_ms:
        batch = get_json(
            f"https://fapi.binance.com/fapi/v1/{endpoint}",
            {
                param_name: SYMBOL,
                "interval": interval,
                "startTime": cursor,
                "endTime": end_ms,
                "limit": 1500,
            },
        )
        if not isinstance(batch, list) or not batch:
            break
        rows.extend(batch)
        cursor = int(batch[-1][0]) + (60_000 if interval == "1m" else 3_600_000)
        time.sleep(0.05)
    return [r for r in rows if ms(start) <= int(r[0]) < ms(end)]


def fetch_funding(start: dt.datetime, end: dt.datetime) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    cursor = ms(start)
    end_ms = ms(end) - 1
    while cursor <= end_ms:
        batch = get_json(
            "https://fapi.binance.com/fapi/v1/fundingRate",
            {"symbol": SYMBOL, "startTime": cursor, "endTime": end_ms, "limit": 1000},
        )
        if not isinstance(batch, list) or not batch:
            break
        rows.extend(batch)
        cursor = int(batch[-1]["fundingTime"]) + 1
        time.sleep(0.05)
    return [r for r in rows if ms(start) <= int(r["fundingTime"]) < ms(end)]


def kline_to_row(row: list[object]) -> dict[str, object]:
    return {
        "timestamp_utc": iso_from_ms(int(row[0])),
        "open": float(row[1]),
        "high": float(row[2]),
        "low": float(row[3]),
        "close": float(row[4]),
        "base_volume": float(row[5]),
        "quote_volume": float(row[7]),
        "trades": int(row[8]),
        "taker_buy_base": float(row[9]),
        "taker_buy_quote": float(row[10]),
    }


def simple_kline_to_map(rows: list[list[object]]) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for row in rows:
        out[iso_from_ms(int(row[0]))] = {
            "open": float(row[1]),
            "high": float(row[2]),
            "low": float(row[3]),
            "close": float(row[4]),
        }
    return out


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize_window(name: str, rows: list[dict[str, object]], funding_rows: list[dict[str, object]]) -> dict[str, object]:
    first = rows[0]
    last = rows[-1]
    high_row = max(rows, key=lambda r: float(r["high"]))
    low_row = min(rows, key=lambda r: float(r["low"]))
    max_volume_row = max(rows, key=lambda r: float(r["quote_volume"]))
    quote_volume = sum(float(r["quote_volume"]) for r in rows)
    taker_buy_quote = sum(float(r["taker_buy_quote"]) for r in rows)
    funding_sum = sum(float(r["funding_rate"]) for r in funding_rows)
    min_funding = min((float(r["funding_rate"]) for r in funding_rows), default=math.nan)
    return {
        "window": name,
        "count": len(rows),
        "start_utc": first["timestamp_utc"],
        "end_utc": last["timestamp_utc"],
        "open": first["open"],
        "close": last["close"],
        "low": low_row["low"],
        "low_time_utc": low_row["timestamp_utc"],
        "high": high_row["high"],
        "high_time_utc": high_row["timestamp_utc"],
        "return_pct": (float(last["close"]) / float(first["open"]) - 1) * 100,
        "high_from_open_pct": (float(high_row["high"]) / float(first["open"]) - 1) * 100,
        "quote_volume_usdt": quote_volume,
        "trades": sum(int(r["trades"]) for r in rows),
        "taker_buy_quote_share_pct": (taker_buy_quote / quote_volume * 100) if quote_volume else 0,
        "max_hour_or_minute_quote_volume_usdt": max_volume_row["quote_volume"],
        "max_volume_time_utc": max_volume_row["timestamp_utc"],
        "max_volume_share_pct": float(max_volume_row["quote_volume"]) / quote_volume * 100 if quote_volume else 0,
        "funding_observations": len(funding_rows),
        "cumulative_funding_pct": funding_sum * 100,
        "min_funding_pct": min_funding * 100 if not math.isnan(min_funding) else "",
    }


def dt_from_iso(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value)


def main() -> None:
    hourly = [kline_to_row(r) for r in fetch_klines("1h", START_1H, END_1H)]
    minute = [kline_to_row(r) for r in fetch_klines("1m", EVENT_START, EVENT_END)]
    mark = simple_kline_to_map(fetch_special_klines("markPriceKlines", "1h", START_1H, END_1H))
    index = simple_kline_to_map(fetch_special_klines("indexPriceKlines", "1h", START_1H, END_1H))
    premium = simple_kline_to_map(fetch_special_klines("premiumIndexKlines", "1h", START_1H, END_1H))
    funding_raw = fetch_funding(START_1H, END_1H)

    funding = [
        {
            "timestamp_utc": iso_from_ms(int(row["fundingTime"])),
            "funding_rate": float(row["fundingRate"]),
            "funding_rate_pct": float(row["fundingRate"]) * 100,
            "mark_price": float(row["markPrice"]),
        }
        for row in funding_raw
    ]
    funding_by_time = {row["timestamp_utc"][:13]: row for row in funding}

    merged_hourly: list[dict[str, object]] = []
    for row in hourly:
        ts = str(row["timestamp_utc"])
        m = mark.get(ts, {})
        i = index.get(ts, {})
        p = premium.get(ts, {})
        f = funding_by_time.get(ts[:13], {})
        merged_hourly.append(
            {
                **row,
                "mark_close": m.get("close", ""),
                "index_close": i.get("close", ""),
                "premium_close": p.get("close", ""),
                "last_minus_mark_pct": ((float(row["close"]) / float(m["close"]) - 1) * 100) if m else "",
                "mark_minus_index_pct": ((float(m["close"]) / float(i["close"]) - 1) * 100) if m and i else "",
                "funding_rate_pct": f.get("funding_rate_pct", ""),
            }
        )

    write_csv(
        BASE / "myx_binance_1h_market_data_2025-09-01_2025-09-12.csv",
        [
            "timestamp_utc",
            "open",
            "high",
            "low",
            "close",
            "base_volume",
            "quote_volume",
            "trades",
            "taker_buy_base",
            "taker_buy_quote",
            "mark_close",
            "index_close",
            "premium_close",
            "last_minus_mark_pct",
            "mark_minus_index_pct",
            "funding_rate_pct",
        ],
        merged_hourly,
    )
    write_csv(
        BASE / "myx_binance_1m_event_window_2025-09-08_2025-09-10.csv",
        [
            "timestamp_utc",
            "open",
            "high",
            "low",
            "close",
            "base_volume",
            "quote_volume",
            "trades",
            "taker_buy_base",
            "taker_buy_quote",
        ],
        minute,
    )
    write_csv(
        BASE / "myx_binance_funding_rates_2025-09-01_2025-09-12.csv",
        ["timestamp_utc", "funding_rate", "funding_rate_pct", "mark_price"],
        funding,
    )
    top_minutes = []
    for row in sorted(minute, key=lambda r: float(r["quote_volume"]), reverse=True)[:25]:
        quote_volume = float(row["quote_volume"])
        trades = int(row["trades"])
        top_minutes.append(
            {
                **row,
                "avg_quote_per_trade": quote_volume / trades if trades else 0,
                "taker_buy_quote_share_pct": (float(row["taker_buy_quote"]) / quote_volume * 100) if quote_volume else 0,
            }
        )
    write_csv(
        BASE / "myx_top_25_one_minute_bursts_2025-09-08_10.csv",
        [
            "timestamp_utc",
            "open",
            "high",
            "low",
            "close",
            "base_volume",
            "quote_volume",
            "trades",
            "taker_buy_base",
            "taker_buy_quote",
            "avg_quote_per_trade",
            "taker_buy_quote_share_pct",
        ],
        top_minutes,
    )

    def in_window(rows: list[dict[str, object]], start: dt.datetime, end: dt.datetime) -> list[dict[str, object]]:
        return [r for r in rows if start <= dt_from_iso(str(r["timestamp_utc"])) < end]

    def funding_in_window(start: dt.datetime, end: dt.datetime) -> list[dict[str, object]]:
        return [r for r in funding if start <= dt_from_iso(str(r["timestamp_utc"])) < end]

    summary = [
        summarize_window("pre_squeeze_2025-09-01_to_2025-09-08", in_window(hourly, START_1H, EVENT_START), funding_in_window(START_1H, EVENT_START)),
        summarize_window("squeeze_2025-09-08_to_2025-09-10", in_window(hourly, EVENT_START, EVENT_END), funding_in_window(EVENT_START, EVENT_END)),
        summarize_window("post_squeeze_2025-09-10_to_2025-09-12", in_window(hourly, EVENT_END, END_1H), funding_in_window(EVENT_END, END_1H)),
        summarize_window("minute_squeeze_2025-09-08_to_2025-09-10", minute, funding_in_window(EVENT_START, EVENT_END)),
    ]
    write_csv(
        BASE / "myx_binance_window_summary.csv",
        list(summary[0].keys()),
        summary,
    )

    times = [dt_from_iso(str(r["timestamp_utc"])) for r in merged_hourly]
    closes = [float(r["close"]) for r in merged_hourly]
    mark_closes = [float(r["mark_close"]) for r in merged_hourly]
    funding_pct = [float(r["funding_rate_pct"]) if r["funding_rate_pct"] != "" else math.nan for r in merged_hourly]

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax1 = plt.subplots(figsize=(12, 6), dpi=160)
    ax1.plot(times, closes, label="MYXUSDT last price", color="#4C78A8", linewidth=1.8)
    ax1.plot(times, mark_closes, label="MYXUSDT mark price", color="#72B7B2", linewidth=1.2, alpha=0.9)
    ax1.axvspan(EVENT_START, EVENT_END, color="#F58518", alpha=0.12, label="short-squeeze window")
    ax1.set_ylabel("USDT price")
    ax1.set_title("MYXUSDT price path and hourly funding-rate stress")
    ax2 = ax1.twinx()
    ax2.bar(times, funding_pct, width=0.025, label="funding rate per settlement (%)", color="#E45756", alpha=0.35)
    ax2.set_ylabel("Funding rate per settlement (%)")
    ax2.axhline(0, color="#333333", linewidth=0.7)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M", tz=UTC))
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="upper left")
    fig.tight_layout()
    fig.savefig(BASE / "myx_price_funding_2025-09-01_12.png")
    plt.close(fig)

    event_times = [dt_from_iso(str(r["timestamp_utc"])) for r in minute]
    event_close = [float(r["close"]) for r in minute]
    event_quote = [float(r["quote_volume"]) for r in minute]
    fig, ax1 = plt.subplots(figsize=(12, 6), dpi=160)
    ax1.plot(event_times, event_close, color="#4C78A8", label="1m close price", linewidth=1)
    ax1.set_ylabel("USDT price")
    ax1.set_title("MYXUSDT one-minute squeeze window: price and notional flow")
    ax2 = ax1.twinx()
    ax2.fill_between(event_times, event_quote, color="#F58518", alpha=0.25, label="1m quote volume")
    ax2.set_ylabel("Quote volume (USDT)")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M", tz=UTC))
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="upper left")
    fig.tight_layout()
    fig.savefig(BASE / "myx_minute_price_volume_2025-09-08_10.png")
    plt.close(fig)

    basis = [float(r["mark_minus_index_pct"]) for r in merged_hourly]
    premium_close = [float(r["premium_close"]) * 100 for r in merged_hourly]
    fig, ax = plt.subplots(figsize=(12, 5), dpi=160)
    ax.plot(times, basis, color="#54A24B", label="mark - index (%)")
    ax.plot(times, premium_close, color="#B279A2", label="premium index close (%)", alpha=0.9)
    ax.axhline(0, color="#333333", linewidth=0.7)
    ax.axvspan(EVENT_START, EVENT_END, color="#F58518", alpha=0.12, label="short-squeeze window")
    ax.set_ylabel("Percent")
    ax.set_title("MYXUSDT mark/index basis during the squeeze")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M", tz=UTC))
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(BASE / "myx_mark_index_premium_2025-09-01_12.png")
    plt.close(fig)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
