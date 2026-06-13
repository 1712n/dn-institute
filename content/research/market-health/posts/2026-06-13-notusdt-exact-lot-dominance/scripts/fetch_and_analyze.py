#!/usr/bin/env python3
import csv
import html
import io
import logging
import statistics
import subprocess
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


DATE = "2026-06-11"
NOT_DATES = ["2026-06-08", "2026-06-09", "2026-06-10", "2026-06-11"]
TARGET = "NOTUSDT"
DOMINANT_QTYS = {"200000", "14748"}
COMPARISON_SYMBOLS = [
    "NOTUSDT",
    "CELRUSDT",
    "STRKUSDT",
    "OPUSDT",
    "OGUSDT",
    "SCRUSDT",
    "SANDUSDT",
    "FLOKIUSDT",
    "DOGEUSDT",
    "ADAUSDT",
    "SPKUSDT",
]
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


def normalize_qty(value):
    return f"{float(value):.8f}".rstrip("0").rstrip(".")


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


def percentile(values, pct):
    if not values:
        return 0
    pos = int((len(values) - 1) * pct)
    return sorted(values)[pos]


def daily_metrics(symbol, rows, zip_bytes, date=DATE):
    qty_counts = Counter(row["qty_text"] for row in rows)
    top = qty_counts.most_common(8)
    timestamps = [row["timestamp"] for row in rows]
    prices = [row["price"] for row in rows]
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
    top_two_qtys = {qty for qty, _ in top[:2]}
    top_two_quote_volume = sum(row["quote"] for row in rows if row["qty_text"] in top_two_qtys)
    dominant_quote_volume = sum(row["quote"] for row in rows if row["qty_text"] in DOMINANT_QTYS)
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
        "top_qty": top[0][0],
        "top_qty_count": top[0][1],
        "top_qty_share": round(top[0][1] / len(rows), 6),
        "second_qty": top[1][0],
        "second_qty_count": top[1][1],
        "second_qty_share": round(top[1][1] / len(rows), 6),
        "top_two_qty_share": round(sum(count for _, count in top[:2]) / len(rows), 6),
        "top_two_quote_volume_usdt": round(top_two_quote_volume, 2),
        "top_two_quote_volume_share": round(top_two_quote_volume / quote_volume, 6),
        "dominant_lot_trade_count": sum(qty_counts.get(qty, 0) for qty in DOMINANT_QTYS),
        "dominant_lot_trade_share": round(sum(qty_counts.get(qty, 0) for qty in DOMINANT_QTYS) / len(rows), 6),
        "dominant_lot_quote_volume_usdt": round(dominant_quote_volume, 2),
        "dominant_lot_quote_volume_share": round(dominant_quote_volume / quote_volume, 6),
        "unique_qty_ratio": round(len(qty_counts) / len(rows), 6),
        "top_second_of_minute_share": round(max(seconds.values()) / len(rows), 6),
        "second_of_minute_chi_square": round(chi_square, 2),
        "buyer_taker_share": round(sum(1 for row in rows if not row["buyer_maker"]) / len(rows), 6),
        "median_intertrade_gap_seconds": round(statistics.median(gaps), 4) if gaps else 0,
        "p95_intertrade_gap_seconds": round(percentile(gaps, 0.95), 4) if gaps else 0,
    }


def top_quantity_rows(rows, limit=10):
    qty_stats = defaultdict(lambda: {"count": 0, "quote_volume_usdt": 0.0})
    total_quote = 0.0
    for row in rows:
        qty_stats[row["qty_text"]]["count"] += 1
        qty_stats[row["qty_text"]]["quote_volume_usdt"] += row["quote"]
        total_quote += row["quote"]
    total_trades = len(rows)
    result = []
    for qty, stats in sorted(qty_stats.items(), key=lambda item: item[1]["count"], reverse=True)[:limit]:
        result.append(
            {
                "quantity": qty,
                "aggregate_trades": stats["count"],
                "trade_share": round(stats["count"] / total_trades, 6),
                "quote_volume_usdt": round(stats["quote_volume_usdt"], 2),
                "quote_volume_share": round(stats["quote_volume_usdt"] / total_quote, 6),
            }
        )
    return result


def hourly_dominant_lot_rows(rows):
    hourly = defaultdict(lambda: {"trades": 0, "quote_volume_usdt": 0.0, "lot_trades": 0, "lot_quote_volume_usdt": 0.0})
    for row in rows:
        hour = datetime.fromtimestamp(row["timestamp"] / 1000, tz=timezone.utc).hour
        bucket = hourly[hour]
        bucket["trades"] += 1
        bucket["quote_volume_usdt"] += row["quote"]
        if row["qty_text"] in DOMINANT_QTYS:
            bucket["lot_trades"] += 1
            bucket["lot_quote_volume_usdt"] += row["quote"]
    result = []
    for hour in range(24):
        bucket = hourly[hour]
        trades = bucket["trades"]
        quote = bucket["quote_volume_usdt"]
        result.append(
            {
                "hour_utc": hour,
                "trade_count": trades,
                "quote_volume_usdt": round(quote, 2),
                "dominant_lot_trade_count": bucket["lot_trades"],
                "dominant_lot_trade_share": round(bucket["lot_trades"] / trades, 6) if trades else 0,
                "dominant_lot_quote_volume_usdt": round(bucket["lot_quote_volume_usdt"], 2),
                "dominant_lot_quote_volume_share": round(bucket["lot_quote_volume_usdt"] / quote, 6) if quote else 0,
            }
        )
    return result


def write_csv(path, fieldnames, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path, text):
    path.write_text(text + "\n", encoding="utf-8")


def scale(value, min_value, max_value, out_min, out_max):
    if max_value == min_value:
        return (out_min + out_max) / 2
    return out_min + (value - min_value) * (out_max - out_min) / (max_value - min_value)


def svg_bar_chart(path, title, labels, values, y_label, color="#3d6fb6", percent=True):
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
        label = f"{value:.0%}" if percent else f"{value:.0f}"
        parts.append(f'<line x1="{left - 5}" y1="{y:.2f}" x2="{left + chart_w}" y2="{y:.2f}" stroke="#eaecf0"/>')
        parts.append(f'<text x="{left - 10}" y="{y + 4:.2f}" text-anchor="end" font-family="Arial" font-size="12" fill="#475467">{label}</text>')
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
    values = [point["dominant_lot_trade_share"] for point in points]
    max_value = max(values) if values else 1
    max_value = max(max_value, 0.05)
    polyline = []
    for point in points:
        x = scale(point["hour_utc"], 0, 23, left, left + chart_w)
        y = scale(point["dominant_lot_trade_share"], 0, max_value, top + chart_h, top)
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
        parts.append(f'<line x1="{x:.2f}" y1="{top + chart_h}" x2="{x:.2f}" y2="{top + chart_h + 5}" stroke="#667085"/>')
        parts.append(f'<text x="{x:.2f}" y="{top + chart_h + 22}" text-anchor="middle" font-family="Arial" font-size="12" fill="#475467">{hour:02d}:00</text>')
    parts.append(
        f'<polyline fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" '
        f'points="{" ".join(polyline)}"/>'
    )
    for point in points:
        x = scale(point["hour_utc"], 0, 23, left, left + chart_w)
        y = scale(point["dominant_lot_trade_share"], 0, max_value, top + chart_h, top)
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.5" fill="{color}"/>')
    parts.append("</svg>")
    write_text(path, "\n".join(parts))


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    source_rows = []
    persistence_rows = []
    not_rows_by_date = {}
    not_zip_bytes_by_date = {}
    for date in NOT_DATES:
        rows, zip_bytes = parse_agg_trades(TARGET, date)
        not_rows_by_date[date] = rows
        not_zip_bytes_by_date[date] = zip_bytes
        metrics = daily_metrics(TARGET, rows, zip_bytes, date)
        persistence_rows.append(metrics)
        source_rows.append({"symbol": TARGET, "date": date, "source_url": metrics["source_url"]})

    comparison_rows = []
    for symbol in COMPARISON_SYMBOLS:
        if symbol == TARGET:
            rows = not_rows_by_date[DATE]
            zip_bytes = not_zip_bytes_by_date[DATE]
        else:
            rows, zip_bytes = parse_agg_trades(symbol, DATE)
            source_rows.append({"symbol": symbol, "date": DATE, "source_url": source_url(symbol, DATE)})
        comparison_rows.append(daily_metrics(symbol, rows, zip_bytes, DATE))

    not_rows = not_rows_by_date[DATE]
    top_qty_rows = top_quantity_rows(not_rows)
    hourly_rows = hourly_dominant_lot_rows(not_rows)

    metric_fields = [
        "symbol",
        "date",
        "source_zip_bytes",
        "source_url",
        "trade_count",
        "start_utc",
        "end_utc",
        "quote_volume_usdt",
        "price_change_pct",
        "top_qty",
        "top_qty_count",
        "top_qty_share",
        "second_qty",
        "second_qty_count",
        "second_qty_share",
        "top_two_qty_share",
        "top_two_quote_volume_usdt",
        "top_two_quote_volume_share",
        "dominant_lot_trade_count",
        "dominant_lot_trade_share",
        "dominant_lot_quote_volume_usdt",
        "dominant_lot_quote_volume_share",
        "unique_qty_ratio",
        "top_second_of_minute_share",
        "second_of_minute_chi_square",
        "buyer_taker_share",
        "median_intertrade_gap_seconds",
        "p95_intertrade_gap_seconds",
    ]
    write_csv(DATA_DIR / "notusdt_daily_persistence.csv", metric_fields, persistence_rows)
    write_csv(DATA_DIR / "comparison_daily_metrics.csv", metric_fields, comparison_rows)
    write_csv(
        DATA_DIR / "notusdt_top_quantities.csv",
        ["quantity", "aggregate_trades", "trade_share", "quote_volume_usdt", "quote_volume_share"],
        top_qty_rows,
    )
    write_csv(
        DATA_DIR / "notusdt_hourly_exact_lot_share.csv",
        [
            "hour_utc",
            "trade_count",
            "quote_volume_usdt",
            "dominant_lot_trade_count",
            "dominant_lot_trade_share",
            "dominant_lot_quote_volume_usdt",
            "dominant_lot_quote_volume_share",
        ],
        hourly_rows,
    )
    deduped_source_rows = sorted({(row["symbol"], row["date"], row["source_url"]) for row in source_rows})
    write_csv(
        DATA_DIR / "source_urls.csv",
        ["symbol", "date", "source_url"],
        [{"symbol": symbol, "date": date, "source_url": url} for symbol, date, url in deduped_source_rows],
    )

    svg_bar_chart(
        IMAGE_DIR / "notusdt_top_quantities.svg",
        "NOT/USDT top trade quantities on Binance, 2026-06-11",
        [row["quantity"] for row in top_qty_rows],
        [row["trade_share"] for row in top_qty_rows],
        "Share of aggregate trades",
        color="#b85c38",
    )
    svg_bar_chart(
        IMAGE_DIR / "notusdt_four_day_exact_lot_share.svg",
        "NOT/USDT exact-lot persistence",
        [row["date"] for row in persistence_rows],
        [row["dominant_lot_trade_share"] for row in persistence_rows],
        "Share of aggregate trades",
        color="#287d57",
    )
    svg_line_chart(
        IMAGE_DIR / "notusdt_hourly_exact_lot_share.svg",
        "NOT/USDT hourly exact-lot share, 2026-06-11",
        hourly_rows,
        "Share of aggregate trades",
    )
    svg_bar_chart(
        IMAGE_DIR / "comparison_top_two_qty_share.svg",
        "Top-two exact quantity concentration by market, 2026-06-11",
        [row["symbol"].replace("USDT", "/USDT") for row in comparison_rows],
        [row["top_two_qty_share"] for row in comparison_rows],
        "Share of aggregate trades",
        color="#3d6fb6",
    )


if __name__ == "__main__":
    main()
