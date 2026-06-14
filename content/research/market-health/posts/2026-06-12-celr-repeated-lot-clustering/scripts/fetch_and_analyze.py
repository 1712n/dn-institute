#!/usr/bin/env python3
import csv
import html
import io
import logging
import math
import statistics
import subprocess
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


DATE = "2026-06-11"
CELR_DATES = ["2026-06-08", "2026-06-09", "2026-06-10", "2026-06-11"]
TARGET = "CELRUSDT"
SYMBOLS = ["CELRUSDT", "GMXUSDT", "FLOKIUSDT", "DYDXUSDT", "TUSDUSDT"]
BASE_URL = "https://data.binance.vision/data/spot/daily/aggTrades"
ALLOWED_DOWNLOAD_HOST = "data.binance.vision"
LOGGER = logging.getLogger(__name__)

ARTICLE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ARTICLE_DIR / "data"
IMAGE_DIR = ARTICLE_DIR / "images"


def source_url(symbol, date=DATE):
    return f"{BASE_URL}/{symbol}/{symbol}-aggTrades-{date}.zip"


def validate_download_url(url):
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"download URL must use HTTPS with a host: {url}")
    if parsed.hostname != ALLOWED_DOWNLOAD_HOST:
        raise ValueError(f"unexpected download host: {parsed.hostname}")


def download(url):
    validate_download_url(url)
    last_error = None
    for _ in range(3):
        try:
            with urllib.request.urlopen(url, timeout=35) as response:
                return response.read()
        except Exception as exc:
            last_error = exc

    try:
        return subprocess.check_output(
            ["curl", "-L", "--fail", "--silent", "--show-error", "--max-time", "45", url],
            timeout=50,
        )
    except Exception as exc:
        raise RuntimeError(f"failed to download {url}: {last_error}; curl fallback: {exc}") from exc


def parse_agg_trades(symbol, date=DATE):
    raw = download(source_url(symbol, date))
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        csv_name = archive.namelist()[0]
        rows = []
        with archive.open(csv_name) as handle:
            for row in csv.reader(io.TextIOWrapper(handle)):
                # aggTradeId, price, quantity, firstTradeId, lastTradeId,
                # timestamp, buyerMaker, bestMatch
                timestamp = int(row[5])
                if timestamp > 10**14:
                    timestamp //= 1000
                rows.append(
                    {
                        "price": float(row[1]),
                        "qty": float(row[2]),
                        "qty_text": normalize_qty(row[2]),
                        "quote": float(row[1]) * float(row[2]),
                        "timestamp": timestamp,
                        "buyer_maker": row[6].lower() == "true",
                    }
                )
    return rows, len(raw)


def normalize_qty(value):
    return f"{float(value):.8f}".rstrip("0").rstrip(".")


def percentile(values, pct):
    if not values:
        return 0
    pos = int((len(values) - 1) * pct)
    return sorted(values)[pos]


def roundish_qty_share(qty_texts):
    roundish = 0
    for qty in qty_texts:
        if "." not in qty or len(qty.split(".")[-1]) <= 2:
            roundish += 1
    return roundish / len(qty_texts)


def require_top_two_quantities(symbol, date, top):
    if len(top) < 2:
        raise ValueError(
            f"{symbol} {date} has only {len(top)} distinct trade quantities; "
            "top-two repeated-lot analysis requires at least two"
        )
    return top[:2]


def target_repeated_quantities(rows, symbol=TARGET, date=DATE):
    qty_counts = Counter(row["qty_text"] for row in rows)
    top_two = require_top_two_quantities(symbol, date, qty_counts.most_common(2))
    return tuple(qty for qty, _ in top_two)


def metrics(symbol, rows, zip_bytes, date=DATE):
    qty_counts = Counter(row["qty_text"] for row in rows)
    top = qty_counts.most_common(5)
    top_two = require_top_two_quantities(symbol, date, top)
    timestamps = [row["timestamp"] for row in rows]
    prices = [row["price"] for row in rows]
    qty_texts = [row["qty_text"] for row in rows]
    seconds = Counter((timestamp // 1000) % 60 for timestamp in timestamps)
    expected = len(rows) / 60
    chi_square = sum((seconds.get(second, 0) - expected) ** 2 / expected for second in range(60))
    gaps = []
    filtered_gap_count = 0
    for previous, current in zip(timestamps, timestamps[1:]):
        if current >= previous:
            gaps.append((current - previous) / 1000)
        else:
            filtered_gap_count += 1
    if filtered_gap_count:
        LOGGER.warning(
            "%s %s had %s out-of-order timestamp gaps skipped",
            symbol,
            date,
            filtered_gap_count,
        )
    top_two_share = sum(count for _, count in top_two) / len(rows)
    top_two_qtys = {qty for qty, _ in top_two}
    top_two_quote_volume = sum(row["quote"] for row in rows if row["qty_text"] in top_two_qtys)
    quote_volume = sum(row["quote"] for row in rows)
    return {
        "symbol": symbol,
        "date": date,
        "source_zip_bytes": zip_bytes,
        "source_url": source_url(symbol, date),
        "trade_count": len(rows),
        "start_utc": datetime.fromtimestamp(min(timestamps) / 1000, tz=timezone.utc).isoformat(),
        "end_utc": datetime.fromtimestamp(max(timestamps) / 1000, tz=timezone.utc).isoformat(),
        "quote_volume_usdt": round(quote_volume, 2),
        "price_change_pct": round((prices[-1] - prices[0]) / prices[0] * 100, 4),
        "top_qty": top_two[0][0],
        "top_qty_count": top_two[0][1],
        "top_qty_share": round(top_two[0][1] / len(rows), 6),
        "second_qty": top_two[1][0],
        "second_qty_count": top_two[1][1],
        "second_qty_share": round(top_two[1][1] / len(rows), 6),
        "top_two_qty_share": round(top_two_share, 6),
        "top_two_quote_volume_usdt": round(top_two_quote_volume, 2),
        "top_two_quote_volume_share": round(top_two_quote_volume / quote_volume, 6),
        "unique_qty_ratio": round(len(qty_counts) / len(rows), 6),
        "round_qty_share": round(roundish_qty_share(qty_texts), 6),
        "top_second_of_minute_share": round(max(seconds.values()) / len(rows), 6),
        "second_of_minute_chi_square": round(chi_square, 2),
        "buyer_taker_share": round(sum(1 for row in rows if not row["buyer_maker"]) / len(rows), 6),
        "median_intertrade_gap_seconds": round(statistics.median(gaps), 4) if gaps else 0,
        "p95_intertrade_gap_seconds": round(percentile(gaps, 0.95), 4) if gaps else 0,
    }


def write_csv(path, fieldnames, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path, text):
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def scale(value, min_value, max_value, out_min, out_max):
    if max_value == min_value:
        return (out_min + out_max) / 2
    return out_min + (value - min_value) * (out_max - out_min) / (max_value - min_value)


def svg_bar_chart(path, title, labels, values, y_label, color="#3d6fb6"):
    width, height = 920, 520
    left, right, top, bottom = 78, 28, 54, 118
    chart_w = width - left - right
    chart_h = height - top - bottom
    max_value = max(values) if values else 1
    bar_gap = 6
    bar_w = max(8, (chart_w - bar_gap * (len(values) - 1)) / len(values))
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{left}" y="30" font-family="Arial" font-size="20" font-weight="700">{html.escape(title)}</text>',
        f'<text x="18" y="{top + chart_h / 2}" transform="rotate(-90 18 {top + chart_h / 2})" font-family="Arial" font-size="13" fill="#344054">{html.escape(y_label)}</text>',
        f'<line x1="{left}" y1="{top + chart_h}" x2="{left + chart_w}" y2="{top + chart_h}" stroke="#667085"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_h}" stroke="#667085"/>',
    ]
    for tick in range(5):
        value = max_value * tick / 4
        y = scale(value, 0, max_value, top + chart_h, top)
        parts.append(f'<line x1="{left - 5}" y1="{y:.2f}" x2="{left + chart_w}" y2="{y:.2f}" stroke="#eaecf0"/>')
        parts.append(f'<text x="{left - 10}" y="{y + 4:.2f}" text-anchor="end" font-family="Arial" font-size="12" fill="#475467">{value:.0%}</text>')
    for i, (label, value) in enumerate(zip(labels, values)):
        x = left + i * (bar_w + bar_gap)
        y = scale(value, 0, max_value, top + chart_h, top)
        h = top + chart_h - y
        parts.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" height="{h:.2f}" fill="{color}"/>')
        parts.append(
            f'<text x="{x + bar_w / 2:.2f}" y="{top + chart_h + 16}" text-anchor="end" '
            f'transform="rotate(-45 {x + bar_w / 2:.2f} {top + chart_h + 16})" '
            f'font-family="Arial" font-size="11" fill="#475467">{html.escape(label)}</text>'
        )
    parts.append("</svg>")
    write_text(path, "\n".join(parts))


def svg_line_chart(path, title, points, y_label, color="#287d57"):
    width, height = 920, 430
    left, right, top, bottom = 72, 28, 54, 58
    chart_w = width - left - right
    chart_h = height - top - bottom
    values = [point["top_two_share"] for point in points]
    max_value = max(values) if values else 1
    max_value = max(max_value, 0.05)
    polyline = []
    for point in points:
        x = scale(point["hour"], 0, 23, left, left + chart_w)
        y = scale(point["top_two_share"], 0, max_value, top + chart_h, top)
        polyline.append(f"{x:.2f},{y:.2f}")
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{left}" y="30" font-family="Arial" font-size="20" font-weight="700">{html.escape(title)}</text>',
        f'<text x="18" y="{top + chart_h / 2}" transform="rotate(-90 18 {top + chart_h / 2})" font-family="Arial" font-size="13" fill="#344054">{html.escape(y_label)}</text>',
        f'<line x1="{left}" y1="{top + chart_h}" x2="{left + chart_w}" y2="{top + chart_h}" stroke="#667085"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_h}" stroke="#667085"/>',
    ]
    for tick in range(5):
        value = max_value * tick / 4
        y = scale(value, 0, max_value, top + chart_h, top)
        parts.append(f'<line x1="{left - 5}" y1="{y:.2f}" x2="{left + chart_w}" y2="{y:.2f}" stroke="#eaecf0"/>')
        parts.append(f'<text x="{left - 10}" y="{y + 4:.2f}" text-anchor="end" font-family="Arial" font-size="12" fill="#475467">{value:.0%}</text>')
    for hour in range(0, 24, 3):
        x = scale(hour, 0, 23, left, left + chart_w)
        parts.append(f'<text x="{x:.2f}" y="{top + chart_h + 24}" text-anchor="middle" font-family="Arial" font-size="12" fill="#475467">{hour:02d}:00</text>')
    parts.append(f'<polyline points="{" ".join(polyline)}" fill="none" stroke="{color}" stroke-width="3"/>')
    for xy in polyline:
        x, y = xy.split(",")
        parts.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{color}"/>')
    parts.append("</svg>")
    write_text(path, "\n".join(parts))


def hourly_repeated_share(rows, repeated_qtys):
    repeated_qty_set = set(repeated_qtys)
    buckets = defaultdict(lambda: {"hour": 0, "trades": 0, "top_two_trades": 0, "quote_volume_usdt": 0.0, "top_two_quote_volume_usdt": 0.0})
    for row in rows:
        hour = datetime.fromtimestamp(row["timestamp"] / 1000, tz=timezone.utc).hour
        bucket = buckets[hour]
        bucket["hour"] = hour
        bucket["trades"] += 1
        bucket["quote_volume_usdt"] += row["quote"]
        if row["qty_text"] in repeated_qty_set:
            bucket["top_two_trades"] += 1
            bucket["top_two_quote_volume_usdt"] += row["quote"]
    output = []
    for hour in range(24):
        bucket = buckets[hour]
        trades = bucket["trades"]
        output.append(
            {
                "hour": hour,
                "trades": trades,
                "top_two_trades": bucket["top_two_trades"],
                "top_two_share": round(bucket["top_two_trades"] / trades, 6) if trades else 0,
                "quote_volume_usdt": round(bucket["quote_volume_usdt"], 2),
                "top_two_quote_volume_usdt": round(bucket["top_two_quote_volume_usdt"], 2),
                "top_two_quote_share": round(bucket["top_two_quote_volume_usdt"] / bucket["quote_volume_usdt"], 6)
                if bucket["quote_volume_usdt"]
                else 0,
            }
        )
    return output


def daily_repeated_persistence(rows_by_date, repeated_qtys):
    repeated_qty_set = set(repeated_qtys)
    repeated_qty_label = "+".join(repeated_qtys)
    output = []
    for date in sorted(rows_by_date):
        rows = rows_by_date[date]
        qty_counts = Counter(row["qty_text"] for row in rows)
        prices = [row["price"] for row in rows]
        quote_volume = sum(row["quote"] for row in rows)
        repeated_rows = [row for row in rows if row["qty_text"] in repeated_qty_set]
        repeated_quote_volume = sum(row["quote"] for row in repeated_rows)
        top = qty_counts.most_common(2)
        top_two = require_top_two_quantities(TARGET, date, top)
        output.append(
            {
                "date": date,
                "trade_count": len(rows),
                "quote_volume_usdt": round(quote_volume, 2),
                "price_change_pct": round((prices[-1] - prices[0]) / prices[0] * 100, 4),
                "repeated_quantities": repeated_qty_label,
                "repeated_lot_trades": len(repeated_rows),
                "repeated_lot_trade_share": round(len(repeated_rows) / len(rows), 6),
                "repeated_lot_quote_volume_usdt": round(repeated_quote_volume, 2),
                "repeated_lot_quote_volume_share": round(repeated_quote_volume / quote_volume, 6),
                "top_qty": top_two[0][0],
                "top_qty_count": top_two[0][1],
                "second_qty": top_two[1][0],
                "second_qty_count": top_two[1][1],
                "source_url": source_url(TARGET, date),
            }
        )
    return output


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    all_rows = {}
    comparison = []
    for symbol in SYMBOLS:
        rows, zip_bytes = parse_agg_trades(symbol)
        all_rows[symbol] = rows
        comparison.append(metrics(symbol, rows, zip_bytes))
    celr = all_rows[TARGET]
    repeated_qtys = target_repeated_quantities(celr)

    comparison_fields = list(comparison[0].keys())
    write_csv(DATA_DIR / "comparison_daily_metrics.csv", comparison_fields, comparison)
    write_csv(
        DATA_DIR / "source_urls.csv",
        ["symbol", "date", "source_url"],
        [{"symbol": symbol, "date": DATE, "source_url": source_url(symbol)} for symbol in SYMBOLS]
        + [
            {"symbol": TARGET, "date": date, "source_url": source_url(TARGET, date)}
            for date in CELR_DATES
            if date != DATE
        ],
    )

    celr_rows_by_date = {DATE: all_rows[TARGET]}
    for date in CELR_DATES:
        if date != DATE:
            celr_rows_by_date[date], _ = parse_agg_trades(TARGET, date)
    daily_persistence = daily_repeated_persistence(celr_rows_by_date, repeated_qtys)
    write_csv(
        DATA_DIR / "celr_daily_repeated_lot_persistence.csv",
        list(daily_persistence[0].keys()),
        daily_persistence,
    )

    qty_counts = Counter(row["qty_text"] for row in celr)
    top_quantities = [
        {
            "rank": rank,
            "quantity": qty,
            "trade_count": count,
            "trade_share": round(count / len(celr), 6),
            "quote_volume_usdt": round(sum(row["quote"] for row in celr if row["qty_text"] == qty), 2),
        }
        for rank, (qty, count) in enumerate(qty_counts.most_common(20), start=1)
    ]
    write_csv(DATA_DIR / "celr_top_quantities.csv", list(top_quantities[0].keys()), top_quantities)

    hourly = hourly_repeated_share(celr, repeated_qtys)
    write_csv(DATA_DIR / "celr_hourly_repeated_lot_share.csv", list(hourly[0].keys()), hourly)

    svg_bar_chart(
        IMAGE_DIR / "celr_top_quantities.svg",
        "CELRUSDT top trade quantities, 2026-06-11",
        [row["quantity"] for row in top_quantities[:15]],
        [row["trade_share"] for row in top_quantities[:15]],
        "share of daily aggregate trades",
        "#3d6fb6",
    )
    svg_line_chart(
        IMAGE_DIR / "celr_hourly_repeated_lot_share.svg",
        "Hourly share of the two repeated CELRUSDT quantities",
        hourly,
        "share of hourly aggregate trades",
        "#287d57",
    )
    svg_bar_chart(
        IMAGE_DIR / "celr_four_day_repeated_lot_share.svg",
        "CELRUSDT repeated-lot share across four days",
        [row["date"][5:] for row in daily_persistence],
        [row["repeated_lot_trade_share"] for row in daily_persistence],
        "share of daily aggregate trades",
        "#287d57",
    )
    svg_bar_chart(
        IMAGE_DIR / "comparison_top_two_qty_share.svg",
        "Top-two quantity concentration by market, 2026-06-11",
        [row["symbol"] for row in comparison],
        [row["top_two_qty_share"] for row in comparison],
        "top-two quantity share",
        "#9b5b2e",
    )


if __name__ == "__main__":
    main()
