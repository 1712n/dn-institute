#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import math
import random
import statistics
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html import escape
from pathlib import Path


OUT = Path(__file__).resolve().parent
RAW_CSV = OUT / "raw_trades.csv"
METRICS_CSV = OUT / "metrics.csv"
RULES_CSV = OUT / "instrument_rules.csv"
RESAMPLED_CSV = OUT / "resampled_top_size_metrics.csv"
TRX_TOP_SIZES_CSV = OUT / "htx_trx_top_sizes.csv"
SNAPSHOT_JSON = OUT / "snapshot.json"

USER_AGENT = "dni-market-health-bounty-analysis/1.1"
HTX_SYMBOLS = ["btcusdt", "ethusdt", "dogeusdt", "trxusdt", "solusdt", "xrpusdt"]
OKX_SYMBOLS = ["TRX-USDT", "DOGE-USDT", "SOL-USDT", "XRP-USDT"]
COMMON_SYMBOLS = [
    ("TRX", "TRXUSDT", "TRX-USDT"),
    ("DOGE", "DOGEUSDT", "DOGE-USDT"),
    ("SOL", "SOLUSDT", "SOL-USDT"),
    ("XRP", "XRPUSDT", "XRP-USDT"),
]

ENDPOINTS = {
    "htx_trades": "https://api.huobi.pro/market/history/trade?symbol={symbol}&size=2000",
    "okx_trades": "https://www.okx.com/api/v5/market/trades?instId={inst_id}&limit=500",
    "htx_symbols": "https://api.huobi.pro/v1/common/symbols",
    "okx_instruments": "https://www.okx.com/api/v5/public/instruments?instType=SPOT",
}


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.load(response)


def iso_from_ms(ts_ms):
    return datetime.fromtimestamp(int(ts_ms) / 1000, timezone.utc).isoformat()


def htx(symbol):
    payload = fetch_json(ENDPOINTS["htx_trades"].format(symbol=symbol))
    rows = []
    for batch in payload.get("data", []):
        for trade in batch.get("data", []):
            ts_ms = int(trade["ts"])
            rows.append(
                {
                    "exchange": "HTX",
                    "symbol": symbol.upper(),
                    "timestamp_ms": ts_ms,
                    "iso_time": iso_from_ms(ts_ms),
                    "side": trade.get("direction", ""),
                    "price": float(trade["price"]),
                    "size": float(trade["amount"]),
                    "trade_id": str(trade.get("trade-id", trade.get("id", ""))),
                }
            )
    return rows


def okx(inst_id):
    payload = fetch_json(ENDPOINTS["okx_trades"].format(inst_id=inst_id))
    rows = []
    for trade in payload.get("data", []):
        ts_ms = int(trade["ts"])
        rows.append(
            {
                "exchange": "OKX",
                "symbol": inst_id,
                "timestamp_ms": ts_ms,
                "iso_time": iso_from_ms(ts_ms),
                "side": trade.get("side", ""),
                "price": float(trade["px"]),
                "size": float(trade["sz"]),
                "trade_id": str(trade.get("tradeId", "")),
            }
        )
    return rows


def collect():
    rows = []
    for symbol in HTX_SYMBOLS:
        rows.extend(htx(symbol))
    for inst_id in OKX_SYMBOLS:
        rows.extend(okx(inst_id))
    rows.sort(key=lambda row: (row["exchange"], row["symbol"], row["timestamp_ms"], row["trade_id"]))
    return rows


def read_raw_rows():
    rows = []
    with RAW_CSV.open() as fp:
        for row in csv.DictReader(fp):
            row["timestamp_ms"] = int(row["timestamp_ms"])
            row["price"] = float(row["price"])
            row["size"] = float(row["size"])
            rows.append(row)
    return rows


def fetch_instrument_rules():
    rules = []

    htx_payload = fetch_json(ENDPOINTS["htx_symbols"])
    htx_wanted = set(HTX_SYMBOLS)
    for item in htx_payload.get("data", []):
        if item.get("symbol") not in htx_wanted:
            continue
        rules.append(
            {
                "exchange": "HTX",
                "symbol": item["symbol"].upper(),
                "min_size": item.get("min-order-amt", ""),
                "min_notional": item.get("min-order-value", ""),
                "lot_size": "",
                "price_tick": precision_to_step(item.get("price-precision")),
                "amount_precision": item.get("amount-precision", ""),
                "price_precision": item.get("price-precision", ""),
                "source": ENDPOINTS["htx_symbols"],
            }
        )

    okx_payload = fetch_json(ENDPOINTS["okx_instruments"])
    okx_wanted = set(OKX_SYMBOLS)
    for item in okx_payload.get("data", []):
        if item.get("instId") not in okx_wanted:
            continue
        rules.append(
            {
                "exchange": "OKX",
                "symbol": item["instId"],
                "min_size": item.get("minSz", ""),
                "min_notional": "",
                "lot_size": item.get("lotSz", ""),
                "price_tick": item.get("tickSz", ""),
                "amount_precision": "",
                "price_precision": "",
                "source": ENDPOINTS["okx_instruments"],
            }
        )

    rules.sort(key=lambda row: (row["exchange"], row["symbol"]))
    return rules


def precision_to_step(precision):
    if precision in ("", None):
        return ""
    return f"{10 ** (-int(precision)):.12g}"


def read_rules():
    if not RULES_CSV.exists():
        return []
    with RULES_CSV.open() as fp:
        return list(csv.DictReader(fp))


def maybe_float(value):
    if value in ("", None):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def first_digit(value):
    text = f"{value:.16f}".lstrip("0.")
    for char in text:
        if char in "123456789":
            return char
    return ""


def top_size_stats(items):
    sizes = [row["size"] for row in items if row["size"] > 0]
    size_counts = Counter(round(size, 12) for size in sizes)
    top_size, top_count = size_counts.most_common(1)[0]
    return {
        "top_size": top_size,
        "top_count": top_count,
        "top_share": top_count / len(sizes),
        "unique_share": len(size_counts) / len(sizes),
    }


def summarize(rows, rules):
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["exchange"], row["symbol"])].append(row)

    rules_by_key = {(row["exchange"], row["symbol"]): row for row in rules}
    expected = {str(digit): math.log10(1 + 1 / digit) for digit in range(1, 10)}
    summaries = []
    for (exchange, symbol), items in sorted(grouped.items()):
        sizes = [row["size"] for row in items if row["size"] > 0]
        prices = [row["price"] for row in items if row["price"] > 0]
        timestamps = [row["timestamp_ms"] for row in items]
        sides = Counter(row["side"] for row in items)
        seconds = Counter((ts // 1000) % 60 for ts in timestamps)
        digit_counts = Counter(first_digit(size) for size in sizes)
        digit_total = sum(digit_counts.get(str(digit), 0) for digit in range(1, 10)) or 1
        observed = {str(digit): digit_counts.get(str(digit), 0) / digit_total for digit in range(1, 10)}
        benford_l1 = sum(abs(observed[str(digit)] - expected[str(digit)]) for digit in range(1, 10))
        stats = top_size_stats(items)
        mean_second = len(items) / 60
        second_chi = sum(((seconds.get(second, 0) - mean_second) ** 2) / mean_second for second in range(60))
        median_price = statistics.median(prices) if prices else 0
        top_notional = stats["top_size"] * median_price
        rule = rules_by_key.get((exchange, symbol), {})
        min_size = maybe_float(rule.get("min_size"))
        min_notional = maybe_float(rule.get("min_notional"))
        summaries.append(
            {
                "exchange": exchange,
                "symbol": symbol,
                "trades": len(items),
                "sample_start_utc": iso_from_ms(min(timestamps)),
                "sample_end_utc": iso_from_ms(max(timestamps)),
                "sample_span_minutes": (max(timestamps) - min(timestamps)) / 60000,
                "median_price": median_price,
                "top_exact_size": stats["top_size"],
                "top_exact_size_count": stats["top_count"],
                "top_exact_size_share": stats["top_share"],
                "top_exact_size_notional": top_notional,
                "top_size_to_min_size": stats["top_size"] / min_size if min_size else "",
                "top_notional_to_min_notional": top_notional / min_notional if min_notional else "",
                "unique_size_share": stats["unique_share"],
                "benford_l1_distance": benford_l1,
                "second_of_minute_chi_square": second_chi,
                "buy_count": sides.get("buy", 0),
                "sell_count": sides.get("sell", 0),
            }
        )
    return summaries


def percentile(values, pct):
    values = sorted(values)
    if not values:
        return ""
    idx = (len(values) - 1) * pct
    lower = math.floor(idx)
    upper = math.ceil(idx)
    if lower == upper:
        return values[int(idx)]
    return values[lower] + (values[upper] - values[lower]) * (idx - lower)


def resampled_top_size_metrics(rows, seed=1712, iterations=1000, sample_size=500):
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["exchange"], row["symbol"])].append(row)

    rng = random.Random(seed)
    output = []
    for label, htx_symbol, okx_symbol in COMMON_SYMBOLS:
        htx_rows = grouped[("HTX", htx_symbol)]
        okx_rows = grouped[("OKX", okx_symbol)]
        top_shares = []
        unique_shares = []
        for _ in range(iterations):
            sample = rng.sample(htx_rows, sample_size)
            stats = top_size_stats(sample)
            top_shares.append(stats["top_share"])
            unique_shares.append(stats["unique_share"])
        htx_full = top_size_stats(htx_rows)
        okx_full = top_size_stats(okx_rows)
        output.append(
            {
                "asset": label,
                "htx_symbol": htx_symbol,
                "okx_symbol": okx_symbol,
                "sample_size": sample_size,
                "iterations": iterations,
                "seed": seed,
                "htx_full_trades": len(htx_rows),
                "htx_full_top_size": htx_full["top_size"],
                "htx_full_top_size_share": htx_full["top_share"],
                "htx_resampled_top_share_p025": percentile(top_shares, 0.025),
                "htx_resampled_top_share_median": percentile(top_shares, 0.5),
                "htx_resampled_top_share_p975": percentile(top_shares, 0.975),
                "htx_resampled_unique_share_p025": percentile(unique_shares, 0.025),
                "htx_resampled_unique_share_median": percentile(unique_shares, 0.5),
                "htx_resampled_unique_share_p975": percentile(unique_shares, 0.975),
                "okx_trades": len(okx_rows),
                "okx_top_size": okx_full["top_size"],
                "okx_top_size_share": okx_full["top_share"],
                "okx_unique_size_share": okx_full["unique_share"],
            }
        )
    return output


def p90(values):
    return percentile(values, 0.9) if values else ""


def trx_top_sizes(rows, limit=12):
    trx_rows = sorted(
        [row for row in rows if row["exchange"] == "HTX" and row["symbol"] == "TRXUSDT"],
        key=lambda row: (row["timestamp_ms"], row["trade_id"]),
    )
    by_size = defaultdict(list)
    for row in trx_rows:
        by_size[round(row["size"], 12)].append(row)
    output = []
    for rank, (size, count) in enumerate(Counter({size: len(items) for size, items in by_size.items()}).most_common(limit), 1):
        items = by_size[size]
        sides = Counter(row["side"] for row in items)
        timestamps = [row["timestamp_ms"] for row in items]
        gaps = [(right - left) / 1000 for left, right in zip(timestamps, timestamps[1:])]
        output.append(
            {
                "rank": rank,
                "exchange": "HTX",
                "symbol": "TRXUSDT",
                "exact_size": size,
                "trade_count": count,
                "share": count / len(trx_rows),
                "buy_count": sides.get("buy", 0),
                "sell_count": sides.get("sell", 0),
                "median_interarrival_seconds": statistics.median(gaps) if gaps else "",
                "p90_interarrival_seconds": p90(gaps) if gaps else "",
                "first_seen_utc": iso_from_ms(min(timestamps)),
                "last_seen_utc": iso_from_ms(max(timestamps)),
            }
        )
    return output


def write_csv(path, rows, fieldnames=None):
    if not rows:
        return
    with path.open("w", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames or list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_raw_csv(rows):
    write_csv(
        RAW_CSV,
        rows,
        ["exchange", "symbol", "timestamp_ms", "iso_time", "side", "price", "size", "trade_id"],
    )


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fmt_pct(value):
    return f"{value:.1%}"


def svg_start(width, height, title, subtitle=""):
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{width/2}" y="30" text-anchor="middle" font-family="Arial, sans-serif" font-size="22" font-weight="700">{escape(title)}</text>',
    ]
    if subtitle:
        parts.append(
            f'<text x="{width/2}" y="52" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#555">{escape(subtitle)}</text>'
        )
    return parts


def svg_bar_chart(path, title, labels, series, ylabel, subtitle="", width=920, height=460):
    left, top, bottom, right = 76, 72 if subtitle else 58, 88, 28
    plot_w = width - left - right
    plot_h = height - top - bottom
    max_v = max(max(values) for _, values, _ in series) or 1
    group_w = plot_w / len(labels)
    bar_w = group_w / (len(series) + 1)
    colors = ["#2454a6", "#d88722", "#17815f", "#8d3dae"]
    parts = svg_start(width, height, title, subtitle)
    parts.append(
        f'<text x="18" y="{top + plot_h/2}" text-anchor="middle" transform="rotate(-90 18 {top + plot_h/2})" font-family="Arial, sans-serif" font-size="13">{escape(ylabel)}</text>'
    )
    for tick in range(6):
        value = max_v * tick / 5
        y = top + plot_h - (value / max_v) * plot_h
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" stroke="#e8e8e8"/>')
        parts.append(f'<text x="{left-8}" y="{y+4:.1f}" text-anchor="end" font-family="Arial, sans-serif" font-size="11">{value:.2f}</text>')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" stroke="#333"/>')
    parts.append(f'<line x1="{left}" y1="{top+plot_h}" x2="{width-right}" y2="{top+plot_h}" stroke="#333"/>')
    for i, label in enumerate(labels):
        x_center = left + i * group_w + group_w / 2
        parts.append(f'<text x="{x_center:.1f}" y="{height-38}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">{escape(label)}</text>')
        for s_idx, (_, values, color) in enumerate(series):
            value = values[i]
            x = left + i * group_w + (s_idx + 0.5) * bar_w
            bar_h = (value / max_v) * plot_h if max_v else 0
            y = top + plot_h - bar_h
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w*0.82:.1f}" height="{bar_h:.1f}" fill="{color or colors[s_idx % len(colors)]}"/>')
            if len(labels) <= 12:
                parts.append(
                    f'<text x="{x + bar_w*0.41:.1f}" y="{max(y - 6, top + 12):.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#333">{fmt_pct(value) if value <= 1 else f"{value:.2f}"}</text>'
                )
    for idx, (name, _, color) in enumerate(series):
        x = left + idx * 210
        parts.append(f'<rect x="{x}" y="{height-24}" width="14" height="14" fill="{color or colors[idx % len(colors)]}"/>')
        parts.append(f'<text x="{x+20}" y="{height-12}" font-family="Arial, sans-serif" font-size="12">{escape(name)}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts))


def svg_interval_chart(path, rows, width=920, height=460):
    left, top, bottom, right = 76, 72, 88, 40
    plot_w = width - left - right
    plot_h = height - top - bottom
    labels = [row["asset"] for row in rows]
    max_v = max(max(float(row["htx_resampled_top_share_p975"]), float(row["okx_top_size_share"])) for row in rows)
    max_v = max_v * 1.18
    group_w = plot_w / len(labels)
    parts = svg_start(
        width,
        height,
        "Top exact-size share, equal 500-trade samples",
        "HTX shown as deterministic bootstrap median with 95% interval; OKX shown as observed 500-trade sample",
    )
    parts.append(
        f'<text x="18" y="{top + plot_h/2}" text-anchor="middle" transform="rotate(-90 18 {top + plot_h/2})" font-family="Arial, sans-serif" font-size="13">share of trades</text>'
    )

    def y_for(value):
        return top + plot_h - (value / max_v) * plot_h

    for tick in range(6):
        value = max_v * tick / 5
        y = y_for(value)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" stroke="#e8e8e8"/>')
        parts.append(f'<text x="{left-8}" y="{y+4:.1f}" text-anchor="end" font-family="Arial, sans-serif" font-size="11">{value:.0%}</text>')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" stroke="#333"/>')
    parts.append(f'<line x1="{left}" y1="{top+plot_h}" x2="{width-right}" y2="{top+plot_h}" stroke="#333"/>')

    for i, row in enumerate(rows):
        x_center = left + i * group_w + group_w / 2
        low = float(row["htx_resampled_top_share_p025"])
        mid = float(row["htx_resampled_top_share_median"])
        high = float(row["htx_resampled_top_share_p975"])
        okx_value = float(row["okx_top_size_share"])
        y_low, y_mid, y_high, y_okx = y_for(low), y_for(mid), y_for(high), y_for(okx_value)
        htx_x = x_center - 16
        okx_x = x_center + 16
        parts.append(f'<text x="{x_center:.1f}" y="{height-38}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">{escape(row["asset"])}</text>')
        parts.append(f'<line x1="{htx_x:.1f}" y1="{y_high:.1f}" x2="{htx_x:.1f}" y2="{y_low:.1f}" stroke="#2454a6" stroke-width="2"/>')
        parts.append(f'<line x1="{htx_x-7:.1f}" y1="{y_high:.1f}" x2="{htx_x+7:.1f}" y2="{y_high:.1f}" stroke="#2454a6" stroke-width="2"/>')
        parts.append(f'<line x1="{htx_x-7:.1f}" y1="{y_low:.1f}" x2="{htx_x+7:.1f}" y2="{y_low:.1f}" stroke="#2454a6" stroke-width="2"/>')
        parts.append(f'<circle cx="{htx_x:.1f}" cy="{y_mid:.1f}" r="5" fill="#2454a6"/>')
        parts.append(f'<rect x="{okx_x-5:.1f}" y="{y_okx-5:.1f}" width="10" height="10" fill="#d88722"/>')
        parts.append(f'<text x="{htx_x:.1f}" y="{max(y_high - 8, top + 12):.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#2454a6">{fmt_pct(mid)}</text>')
        parts.append(f'<text x="{okx_x:.1f}" y="{max(y_okx - 8, top + 12):.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#9a5d0c">{fmt_pct(okx_value)}</text>')
    parts.append(f'<circle cx="{left}" cy="{height-22}" r="5" fill="#2454a6"/>')
    parts.append(f'<text x="{left+14}" y="{height-18}" font-family="Arial, sans-serif" font-size="12">HTX bootstrap median and 95% interval</text>')
    parts.append(f'<rect x="{left+300}" y="{height-27}" width="10" height="10" fill="#d88722"/>')
    parts.append(f'<text x="{left+316}" y="{height-18}" font-family="Arial, sans-serif" font-size="12">OKX observed 500 trades</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts))


def svg_second_chart(path, title, groups, subtitle="", width=920, height=460):
    left, top, bottom, right = 76, 72 if subtitle else 58, 88, 28
    plot_w = width - left - right
    plot_h = height - top - bottom
    max_v = max(max(values) for _, values, _ in groups) or 1
    parts = svg_start(width, height, title, subtitle)
    parts.append(
        f'<text x="18" y="{top + plot_h/2}" text-anchor="middle" transform="rotate(-90 18 {top + plot_h/2})" font-family="Arial, sans-serif" font-size="13">share of trades</text>'
    )
    for tick in range(6):
        value = max_v * tick / 5
        y = top + plot_h - (value / max_v) * plot_h
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" stroke="#e8e8e8"/>')
        parts.append(f'<text x="{left-8}" y="{y+4:.1f}" text-anchor="end" font-family="Arial, sans-serif" font-size="11">{value:.2%}</text>')
    parts.append(f'<line x1="{left}" y1="{top+plot_h}" x2="{width-right}" y2="{top+plot_h}" stroke="#333"/>')
    for idx, (name, values, color) in enumerate(groups):
        points = []
        for i, value in enumerate(values):
            x = left + (i / 59) * plot_w
            y = top + plot_h - (value / max_v) * plot_h
            points.append(f"{x:.1f},{y:.1f}")
        parts.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2.5"/>')
    for second in range(0, 60, 5):
        x = left + (second / 59) * plot_w
        parts.append(f'<text x="{x:.1f}" y="{height-40}" text-anchor="middle" font-family="Arial, sans-serif" font-size="10">{second}</text>')
    for idx, (name, _, color) in enumerate(groups):
        x = left + idx * 190
        parts.append(f'<rect x="{x}" y="{height-24}" width="14" height="14" fill="{color}"/>')
        parts.append(f'<text x="{x+20}" y="{height-12}" font-family="Arial, sans-serif" font-size="12">{escape(name)}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts))


def write_charts(rows, summaries, resampled_rows, top_size_rows):
    summary_by_key = {(row["exchange"], row["symbol"]): row for row in summaries}
    htx_symbols = ["BTCUSDT", "ETHUSDT", "DOGEUSDT", "TRXUSDT", "SOLUSDT", "XRPUSDT"]
    svg_bar_chart(
        OUT / "htx_top_exact_size_share.svg",
        "Most common exact trade-size share on HTX",
        htx_symbols,
        [("top exact-size share", [summary_by_key[("HTX", symbol)]["top_exact_size_share"] for symbol in htx_symbols], "#2454a6")],
        "share of trades",
        "Single snapshot from public trade tape; exact-size matching uses 12 decimal places",
    )

    svg_bar_chart(
        OUT / "htx_benford_distance.svg",
        "First-digit distance from Benford expectation",
        htx_symbols,
        [("L1 distance", [summary_by_key[("HTX", symbol)]["benford_l1_distance"] for symbol in htx_symbols], "#8d3dae")],
        "L1 distance",
        "Screening statistic only; bounded exchange lot sizes can legitimately deviate from Benford",
    )

    trx_rows = [row for row in rows if row["exchange"] == "HTX" and row["symbol"] == "TRXUSDT"]
    okx_rows = [row for row in rows if row["exchange"] == "OKX" and row["symbol"] == "TRX-USDT"]
    htx_seconds = Counter((row["timestamp_ms"] // 1000) % 60 for row in trx_rows)
    okx_seconds = Counter((row["timestamp_ms"] // 1000) % 60 for row in okx_rows)
    svg_second_chart(
        OUT / "trx_second_of_minute_distribution.svg",
        "TRX/USDT trades by second of minute",
        [
            ("HTX TRX/USDT", [htx_seconds.get(i, 0) / len(trx_rows) for i in range(60)], "#2454a6"),
            ("OKX TRX/USDT", [okx_seconds.get(i, 0) / len(okx_rows) for i in range(60)], "#d88722"),
        ],
        "Timing view is descriptive, not a manipulation test; samples have different windows",
    )

    expected = [math.log10(1 + 1 / digit) for digit in range(1, 10)]
    digit_counts = Counter(first_digit(row["size"]) for row in trx_rows if row["size"] > 0)
    total = sum(digit_counts.get(str(digit), 0) for digit in range(1, 10))
    observed = [digit_counts.get(str(digit), 0) / total for digit in range(1, 10)]
    svg_bar_chart(
        OUT / "htx_trx_first_digit_distribution.svg",
        "HTX TRX/USDT first significant digit distribution",
        [str(digit) for digit in range(1, 10)],
        [
            ("observed", observed, "#2454a6"),
            ("Benford", expected, "#d88722"),
        ],
        "share of trades",
        "Spike on digit 8 reflects repeated 8.41-8.44 TRX lot sizes",
    )

    svg_interval_chart(OUT / "common_symbol_top_size_resample.svg", resampled_rows)
    svg_bar_chart(
        OUT / "htx_trx_top_sizes.svg",
        "Most repeated exact trade sizes on HTX TRX/USDT",
        [str(row["exact_size"]) for row in top_size_rows[:10]],
        [("share of TRX/USDT trades", [row["share"] for row in top_size_rows[:10]], "#17815f")],
        "share of trades",
        "Top 10 exact sizes in the captured HTX TRX/USDT tape",
    )


def write_snapshot(rows, summaries, rules, used_existing_raw):
    timestamps = [row["timestamp_ms"] for row in rows]
    snapshot = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "used_existing_raw_trades_csv": used_existing_raw,
        "raw_trades_sha256": file_sha256(RAW_CSV) if RAW_CSV.exists() else "",
        "row_count": len(rows),
        "sample_start_utc": iso_from_ms(min(timestamps)),
        "sample_end_utc": iso_from_ms(max(timestamps)),
        "symbols": sorted({f"{row['exchange']}:{row['symbol']}" for row in rows}),
        "endpoint_templates": ENDPOINTS,
        "derived_files": {
            "metrics_csv": file_sha256(METRICS_CSV) if METRICS_CSV.exists() else "",
            "instrument_rules_csv": file_sha256(RULES_CSV) if RULES_CSV.exists() else "",
            "resampled_top_size_metrics_csv": file_sha256(RESAMPLED_CSV) if RESAMPLED_CSV.exists() else "",
            "htx_trx_top_sizes_csv": file_sha256(TRX_TOP_SIZES_CSV) if TRX_TOP_SIZES_CSV.exists() else "",
        },
        "notes": [
            "HTX /market/history/trade returns recent trade batches; rows in raw_trades.csv are individual trades after expanding those batches.",
            "OKX /market/trades is capped at 500 recent trades per request.",
            "The default script path reuses raw_trades.csv when present; pass --refresh to capture a new public-trade snapshot.",
        ],
    }
    SNAPSHOT_JSON.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")


def parse_args():
    parser = argparse.ArgumentParser(description="Generate a reproducible HTX/OKX market-health snapshot.")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Fetch a new public-trade snapshot instead of reusing raw_trades.csv when it exists.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    use_existing_raw = RAW_CSV.exists() and not args.refresh
    if use_existing_raw:
        rows = read_raw_rows()
    else:
        rows = collect()
        write_raw_csv(rows)

    try:
        rules = fetch_instrument_rules() if args.refresh or not RULES_CSV.exists() else read_rules()
    except Exception as exc:
        print(f"warning: could not refresh instrument rules: {exc}")
        rules = read_rules()

    summaries = summarize(rows, rules)
    resampled = resampled_top_size_metrics(rows)
    top_sizes = trx_top_sizes(rows)

    write_csv(RULES_CSV, rules)
    write_csv(METRICS_CSV, summaries)
    write_csv(RESAMPLED_CSV, resampled)
    write_csv(TRX_TOP_SIZES_CSV, top_sizes)
    write_charts(rows, summaries, resampled, top_sizes)
    write_snapshot(rows, summaries, rules, used_existing_raw=use_existing_raw)

    print(f"{'reused' if use_existing_raw else 'wrote'} {RAW_CSV.relative_to(OUT)} with {len(rows)} trades")
    print(f"wrote {METRICS_CSV.relative_to(OUT)} with {len(summaries)} market summaries")
    print(f"wrote {RESAMPLED_CSV.relative_to(OUT)} with {len(resampled)} equal-sample comparisons")
    print(f"wrote {TRX_TOP_SIZES_CSV.relative_to(OUT)} with {len(top_sizes)} top-size rows")
    print(f"wrote {SNAPSHOT_JSON.relative_to(OUT)}")
    for row in summaries:
        if row["exchange"] == "HTX":
            print(
                f"{row['exchange']} {row['symbol']}: "
                f"top_size_share={row['top_exact_size_share']:.3f}, "
                f"top_size_notional={row['top_exact_size_notional']:.2f}, "
                f"benford_l1={row['benford_l1_distance']:.3f}, "
                f"span_min={row['sample_span_minutes']:.1f}"
            )


if __name__ == "__main__":
    main()
