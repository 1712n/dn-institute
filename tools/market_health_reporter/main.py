#!/usr/bin/env python3
"""
Market Health Reporter 🌰
Generates Hugo markdown reports with dynamic Chart.js graphs
from the Crypto Market Health API.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import requests

API_BASE = "https://dn.institute/api"
DEFAULT_DAYS = 7
DEFAULT_OUTPUT_DIR = "content/reports"


def fetch_metric(pair: str, metric: str, days: int = DEFAULT_DAYS) -> list:
    """Fetch metric data from Market Health API."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    params = {
        "pair": pair,
        "metric": metric,
        "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    url = f"{API_BASE}/market-health"
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def detect_spikes(data: list, threshold: float = 2.0) -> list:
    """Detect spikes in metric data using z-score."""
    if not data:
        return []
    values = [point["value"] for point in data if "value" in point]
    if len(values) < 2:
        return []
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    std = variance ** 0.5
    if std == 0:
        return []
    spikes = []
    for point in data:
        if "value" not in point:
            continue
        z = abs((point["value"] - mean) / std)
        if z >= threshold:
            spikes.append(point)
    return spikes


def format_chart_data(data: list) -> dict:
    """Format API response into Chart.js compatible data."""
    labels = []
    values = []
    for point in data:
        ts = point.get("timestamp", point.get("time", ""))
        val = point.get("value", 0)
        labels.append(ts)
        values.append(val)
    return {"labels": labels, "values": values}


def build_report(
    pair: str,
    metrics: list,
    days: int = DEFAULT_DAYS,
    llm_summary: str = "",
) -> str:
    """Build a Hugo markdown report with dynamic chart shortcodes."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    slug = pair.replace("/", "-").replace(":", "-").lower()
    date_label = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    lines = [
        "---",
        f'title: "Market Health Report – {pair} ({date_label}) 🌰"',
        f"date: {now}",
        f'pair: "{pair}"',
        "draft: false",
        "---",
        "",
        f"# Market Health Report: {pair} 🌰",
        "",
        f"**Period:** last {days} day(s)  ",
        f"**Generated:** {now}",
        "",
    ]

    if llm_summary:
        lines += [
            "## Summary",
            "",
            llm_summary,
            "",
        ]

    for metric in metrics:
        lines.append(f"## {metric.replace('_', ' ').title()} 🌰")
        lines.append("")
        try:
            data = fetch_metric(pair, metric, days)
        except requests.RequestException as exc:
            lines.append(f"_Failed to fetch data: {exc}_")
            lines.append("")
            continue

        if not data:
            lines.append("_No data available for this period._")
            lines.append("")
            continue

        chart_data = format_chart_data(data)
        spikes = detect_spikes(data)

        # Embed dynamic chart via shortcode 🌰
        chart_json = json.dumps(chart_data)
        lines.append(
            f'{{{{< metric_chart metric="{metric}" pair="{pair}" data=\'{chart_json}\' >}}}}'
        )
        lines.append("")

        if spikes:
            lines.append(f"**Detected {len(spikes)} spike(s):**")
            lines.append("")
            for spike in spikes:
                ts = spike.get("timestamp", spike.get("time", "unknown"))
                val = spike.get("value", "N/A")
                lines.append(f"- `{ts}` → `{val}` 🌰")
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Market Health Reporter – dynamic chart edition 🌰"
    )
    parser.add_argument(
        "--pair",
        required=True,
        help='Trading pair, e.g. "BTC/USD"',
    )
    parser.add_argument(
        "--metrics",
        nargs="+",
        default=["slippage", "spread", "depth"],
        help="List of metrics to report on",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_DAYS,
        help="Number of days to look back",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to write the Hugo markdown report",
    )
    parser.add_argument(
        "--llm-summary",
        default="",
        help="Optional LLM-generated summary text to include in the report",
    )
    args = parser.parse_args()

    report_md = build_report(
        pair=args.pair,
        metrics=args.metrics,
        days=args.days,
        llm_summary=args.llm_summary,
    )

    os.makedirs(args.output_dir, exist_ok=True)
    date_label = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    slug = args.pair.replace("/", "-").replace(":", "-").lower()
    filename = os.path.join(args.output_dir, f"{date_label}-{slug}.md")

    with open(filename, "w", encoding="utf-8") as fh:
        fh.write(report_md)

    print(f"Report written to: {filename} 🌰")


if __name__ == "__main__":
    main()
