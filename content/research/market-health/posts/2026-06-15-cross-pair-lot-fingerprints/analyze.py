#!/usr/bin/env python3
"""Reproduce the BOME/NEIRO exact-lot analysis from Binance public data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import socket
import time
import urllib.request
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from tempfile import gettempdir
from urllib.error import URLError


PAIRS = ("BOMEUSDT", "BOMEUSDC", "NEIROUSDT", "NEIROUSDC")
DATES = tuple(f"2026-06-{day:02d}" for day in range(7, 14))
FINGERPRINTS = (Decimal("200000"), Decimal("14748"))
BASE_URL = "https://data.binance.vision/data/spot/daily/aggTrades"
DOWNLOAD_ATTEMPTS = 3
DOWNLOAD_TIMEOUT_SECONDS = 30
COLORS = {
    "BOMEUSDT": "#2563eb",
    "BOMEUSDC": "#16a34a",
    "NEIROUSDT": "#dc2626",
    "NEIROUSDC": "#9333ea",
}


@dataclass
class DayMetrics:
    pair: str
    date: str
    trade_count: int
    notional: Decimal
    top_quantity: Decimal
    top_count: int
    top_notional: Decimal
    fingerprint_counts: dict[Decimal, int]
    fingerprint_notional: dict[Decimal, Decimal]
    fingerprint_aggressor_buys: dict[Decimal, int]
    fingerprint_single_fill_counts: dict[Decimal, int]
    fingerprint_timestamps: dict[Decimal, dict[int, set[bool]]]


def archive_url(pair: str, date: str) -> str:
    filename = f"{pair}-aggTrades-{date}.zip"
    return f"{BASE_URL}/{pair}/{filename}"


def fetch_bytes(url: str) -> bytes:
    for attempt in range(DOWNLOAD_ATTEMPTS):
        try:
            with urllib.request.urlopen(
                url, timeout=DOWNLOAD_TIMEOUT_SECONDS
            ) as response:
                return response.read()
        except (OSError, socket.timeout, URLError):
            if attempt + 1 == DOWNLOAD_ATTEMPTS:
                raise
            time.sleep(2**attempt)
    raise AssertionError("unreachable")


def download(pair: str, date: str, cache_dir: Path) -> tuple[Path, str]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"{pair}-aggTrades-{date}.zip"
    if not path.exists():
        print(f"Downloading {archive_url(pair, date)}")
        path.write_bytes(fetch_bytes(archive_url(pair, date)))
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    checksum_url = f"{archive_url(pair, date)}.CHECKSUM"
    expected_digest = fetch_bytes(checksum_url).decode("ascii").split()[0]
    if digest.lower() != expected_digest.lower():
        raise ValueError(
            f"Checksum mismatch for {path}: expected {expected_digest}, got {digest}"
        )
    return path, digest


def analyze_archive(pair: str, date: str, path: Path) -> DayMetrics:
    quantities: Counter[Decimal] = Counter()
    quantity_notional: defaultdict[Decimal, Decimal] = defaultdict(Decimal)
    fingerprint_counts: Counter[Decimal] = Counter()
    fingerprint_notional: defaultdict[Decimal, Decimal] = defaultdict(Decimal)
    fingerprint_aggressor_buys: Counter[Decimal] = Counter()
    fingerprint_single_fill_counts: Counter[Decimal] = Counter()
    fingerprint_timestamps: dict[Decimal, dict[int, set[bool]]] = {
        quantity: defaultdict(set) for quantity in FINGERPRINTS
    }
    trade_count = 0
    total_notional = Decimal()

    with zipfile.ZipFile(path) as archive:
        csv_name = next(name for name in archive.namelist() if name.endswith(".csv"))
        with archive.open(csv_name) as raw:
            rows = csv.reader(io.TextIOWrapper(raw, encoding="utf-8", newline=""))
            for row in rows:
                price = Decimal(row[1])
                quantity = Decimal(row[2])
                timestamp = int(row[5])
                buyer_is_maker = row[6].lower() == "true"
                underlying_fill_count = int(row[4]) - int(row[3]) + 1
                notional = price * quantity

                trade_count += 1
                total_notional += notional
                quantities[quantity] += 1
                quantity_notional[quantity] += notional

                if quantity in FINGERPRINTS:
                    fingerprint_counts[quantity] += 1
                    fingerprint_notional[quantity] += notional
                    if not buyer_is_maker:
                        fingerprint_aggressor_buys[quantity] += 1
                    if underlying_fill_count == 1:
                        fingerprint_single_fill_counts[quantity] += 1
                    fingerprint_timestamps[quantity][timestamp].add(buyer_is_maker)

    if not quantities:
        raise ValueError(f"No valid aggregate trades found in archive {path}")
    top_quantity, top_count = quantities.most_common(1)[0]
    return DayMetrics(
        pair=pair,
        date=date,
        trade_count=trade_count,
        notional=total_notional,
        top_quantity=top_quantity,
        top_count=top_count,
        top_notional=quantity_notional[top_quantity],
        fingerprint_counts=dict(fingerprint_counts),
        fingerprint_notional=dict(fingerprint_notional),
        fingerprint_aggressor_buys=dict(fingerprint_aggressor_buys),
        fingerprint_single_fill_counts=dict(fingerprint_single_fill_counts),
        fingerprint_timestamps=fingerprint_timestamps,
    )


def pct(numerator: Decimal | int, denominator: Decimal | int) -> Decimal:
    if not denominator:
        return Decimal()
    return Decimal(numerator) * Decimal(100) / Decimal(denominator)


def write_daily_metrics(metrics: list[DayMetrics], output_dir: Path) -> None:
    fields = [
        "pair",
        "date",
        "aggregate_trades",
        "notional_quote",
        "top_exact_quantity",
        "top_quantity_trade_share_pct",
        "top_quantity_notional_share_pct",
        "quantity_200000_trade_share_pct",
        "quantity_200000_notional_share_pct",
        "quantity_14748_trade_share_pct",
        "quantity_14748_notional_share_pct",
    ]
    with (output_dir / "daily_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for day in metrics:
            writer.writerow(
                {
                    "pair": day.pair,
                    "date": day.date,
                    "aggregate_trades": day.trade_count,
                    "notional_quote": f"{day.notional:.2f}",
                    "top_exact_quantity": f"{day.top_quantity:f}",
                    "top_quantity_trade_share_pct": f"{pct(day.top_count, day.trade_count):.4f}",
                    "top_quantity_notional_share_pct": (
                        f"{pct(day.top_notional, day.notional):.4f}"
                    ),
                    "quantity_200000_trade_share_pct": (
                        f"{pct(day.fingerprint_counts.get(FINGERPRINTS[0], 0), day.trade_count):.4f}"
                    ),
                    "quantity_200000_notional_share_pct": (
                        f"{pct(day.fingerprint_notional.get(FINGERPRINTS[0], 0), day.notional):.4f}"
                    ),
                    "quantity_14748_trade_share_pct": (
                        f"{pct(day.fingerprint_counts.get(FINGERPRINTS[1], 0), day.trade_count):.4f}"
                    ),
                    "quantity_14748_notional_share_pct": (
                        f"{pct(day.fingerprint_notional.get(FINGERPRINTS[1], 0), day.notional):.4f}"
                    ),
                }
            )


def write_pair_summary(metrics: list[DayMetrics], output_dir: Path) -> None:
    fields = [
        "pair",
        "aggregate_trades",
        "notional_quote",
        "quantity",
        "trade_count",
        "trade_share_pct",
        "notional_share_pct",
        "aggressor_buy_share_pct",
        "single_underlying_fill_share_pct",
        "timestamps_with_both_aggressor_sides",
    ]
    grouped: defaultdict[str, list[DayMetrics]] = defaultdict(list)
    for day in metrics:
        grouped[day.pair].append(day)

    with (output_dir / "fingerprint_summary.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for pair in PAIRS:
            days = grouped[pair]
            total_trades = sum(day.trade_count for day in days)
            total_notional = sum((day.notional for day in days), Decimal())
            for quantity in FINGERPRINTS:
                count = sum(day.fingerprint_counts.get(quantity, 0) for day in days)
                notional = sum(
                    (day.fingerprint_notional.get(quantity, Decimal()) for day in days),
                    Decimal(),
                )
                buys = sum(
                    day.fingerprint_aggressor_buys.get(quantity, 0) for day in days
                )
                single_fills = sum(
                    day.fingerprint_single_fill_counts.get(quantity, 0)
                    for day in days
                )
                bilateral = sum(
                    1
                    for day in days
                    for sides in day.fingerprint_timestamps[quantity].values()
                    if len(sides) == 2
                )
                writer.writerow(
                    {
                        "pair": pair,
                        "aggregate_trades": total_trades,
                        "notional_quote": f"{total_notional:.2f}",
                        "quantity": f"{quantity:f}",
                        "trade_count": count,
                        "trade_share_pct": f"{pct(count, total_trades):.4f}",
                        "notional_share_pct": f"{pct(notional, total_notional):.4f}",
                        "aggressor_buy_share_pct": f"{pct(buys, count):.4f}",
                        "single_underlying_fill_share_pct": (
                            f"{pct(single_fills, count):.4f}"
                        ),
                        "timestamps_with_both_aggressor_sides": bilateral,
                    }
                )


def svg_line_chart(metrics: list[DayMetrics], output_dir: Path) -> None:
    width, height = 960, 520
    left, right, top, bottom = 85, 30, 55, 85
    plot_w, plot_h = width - left - right, height - top - bottom
    values = {
        pair: [
            float(
                pct(
                    day.fingerprint_notional.get(FINGERPRINTS[0], Decimal()),
                    day.notional,
                )
            )
            for day in metrics
            if day.pair == pair
        ]
        for pair in PAIRS
    }
    y_max = max(30, int(max(max(series) for series in values.values()) / 5 + 1) * 5)

    def x(index: int) -> float:
        return left + index * plot_w / (len(DATES) - 1)

    def y(value: float) -> float:
        return top + plot_h - value * plot_h / y_max

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="480" y="30" text-anchor="middle" font-family="Arial" font-size="20" font-weight="700">200,000-token exact-lot share of daily notional</text>',
    ]
    for tick in range(0, y_max + 1, 5):
        yy = y(tick)
        parts.append(
            f'<line x1="{left}" y1="{yy:.1f}" x2="{width-right}" y2="{yy:.1f}" stroke="#d1d5db" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{left-12}" y="{yy+4:.1f}" text-anchor="end" font-family="Arial" font-size="12" fill="#374151">{tick}%</text>'
        )
    for index, date in enumerate(DATES):
        xx = x(index)
        parts.append(
            f'<text x="{xx:.1f}" y="{height-bottom+28}" text-anchor="middle" font-family="Arial" font-size="12" fill="#374151">{date[5:]}</text>'
        )
    for pair in PAIRS:
        points = " ".join(
            f"{x(index):.1f},{y(value):.1f}"
            for index, value in enumerate(values[pair])
        )
        parts.append(
            f'<polyline points="{points}" fill="none" stroke="{COLORS[pair]}" stroke-width="3"/>'
        )
        for index, value in enumerate(values[pair]):
            parts.append(
                f'<circle cx="{x(index):.1f}" cy="{y(value):.1f}" r="4" fill="{COLORS[pair]}"/>'
            )
    for index, pair in enumerate(PAIRS):
        lx = left + index * 190
        parts.append(
            f'<line x1="{lx}" y1="{height-24}" x2="{lx+25}" y2="{height-24}" stroke="{COLORS[pair]}" stroke-width="4"/>'
        )
        parts.append(
            f'<text x="{lx+32}" y="{height-19}" font-family="Arial" font-size="13" fill="#111827">{pair}</text>'
        )
    parts.append("</svg>")
    (output_dir / "daily_200k_notional_share.svg").write_text(
        "\n".join(parts), encoding="utf-8"
    )


def svg_bar_chart(metrics: list[DayMetrics], output_dir: Path) -> None:
    width, height = 960, 500
    left, right, top, bottom = 90, 35, 55, 95
    plot_w, plot_h = width - left - right, height - top - bottom
    grouped: defaultdict[str, list[DayMetrics]] = defaultdict(list)
    for day in metrics:
        grouped[day.pair].append(day)
    shares: dict[tuple[str, Decimal], float] = {}
    for pair in PAIRS:
        total = sum(day.trade_count for day in grouped[pair])
        for quantity in FINGERPRINTS:
            count = sum(
                day.fingerprint_counts.get(quantity, 0) for day in grouped[pair]
            )
            shares[(pair, quantity)] = float(pct(count, total))
    y_max = 60
    group_w = plot_w / len(PAIRS)
    bar_w = group_w * 0.28

    def y(value: float) -> float:
        return top + plot_h - value * plot_h / y_max

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="480" y="30" text-anchor="middle" font-family="Arial" font-size="20" font-weight="700">Exact-quantity fingerprints across four spot markets</text>',
    ]
    for tick in range(0, y_max + 1, 10):
        yy = y(tick)
        parts.append(
            f'<line x1="{left}" y1="{yy:.1f}" x2="{width-right}" y2="{yy:.1f}" stroke="#d1d5db" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{left-12}" y="{yy+4:.1f}" text-anchor="end" font-family="Arial" font-size="12" fill="#374151">{tick}%</text>'
        )
    bar_colors = ("#0f766e", "#f59e0b")
    for pair_index, pair in enumerate(PAIRS):
        center = left + group_w * (pair_index + 0.5)
        for quantity_index, quantity in enumerate(FINGERPRINTS):
            value = shares[(pair, quantity)]
            xx = center + (quantity_index - 0.5) * bar_w
            yy = y(value)
            parts.append(
                f'<rect x="{xx:.1f}" y="{yy:.1f}" width="{bar_w:.1f}" height="{top+plot_h-yy:.1f}" fill="{bar_colors[quantity_index]}"/>'
            )
            parts.append(
                f'<text x="{xx+bar_w/2:.1f}" y="{yy-6:.1f}" text-anchor="middle" font-family="Arial" font-size="11" fill="#111827">{value:.1f}%</text>'
            )
        parts.append(
            f'<text x="{center:.1f}" y="{height-bottom+28}" text-anchor="middle" font-family="Arial" font-size="12" fill="#111827">{pair}</text>'
        )
    for index, label in enumerate(("200,000 tokens", "14,748 tokens")):
        lx = 320 + index * 220
        parts.append(
            f'<rect x="{lx}" y="{height-28}" width="16" height="16" fill="{bar_colors[index]}"/>'
        )
        parts.append(
            f'<text x="{lx+24}" y="{height-15}" font-family="Arial" font-size="13" fill="#111827">{label}</text>'
        )
    parts.append("</svg>")
    (output_dir / "cross_pair_fingerprints.svg").write_text(
        "\n".join(parts), encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(gettempdir()) / "dn277-binance-public-data",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    metrics: list[DayMetrics] = []
    manifest_rows = []
    for pair in PAIRS:
        for date in DATES:
            path, digest = download(pair, date, args.cache_dir)
            manifest_rows.append(
                {
                    "pair": pair,
                    "date": date,
                    "url": archive_url(pair, date),
                    "sha256": digest,
                }
            )
            metrics.append(analyze_archive(pair, date, path))

    with (args.output_dir / "source_manifest.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=("pair", "date", "url", "sha256")
        )
        writer.writeheader()
        writer.writerows(manifest_rows)

    write_daily_metrics(metrics, args.output_dir)
    write_pair_summary(metrics, args.output_dir)
    svg_line_chart(metrics, args.output_dir)
    svg_bar_chart(metrics, args.output_dir)
    print(f"Wrote analysis artifacts to {args.output_dir}")


if __name__ == "__main__":
    main()
