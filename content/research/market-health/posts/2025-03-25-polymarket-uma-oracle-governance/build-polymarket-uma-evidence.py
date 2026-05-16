#!/usr/bin/env python3
"""Build reproducible evidence artifacts for the Polymarket UMA case."""

from __future__ import annotations

import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "polymarket-uma-oracle-signals.csv"
SVG_PATH = BASE_DIR / "polymarket-uma-governance-stress.svg"

COIN360_SOURCE = "https://coin360.com/news/polymarket-oracle-vote-manipulation-scandal"
CRYPTO_REPORT_SOURCE = (
    "https://crypto.report/hacks-exploits/"
    "polymarket-faces-blowback-over-oracle-manipulation-allegations/"
)

reported_values = {
    "disputed_market_value_usd": 7_000_000,
    "uma_tokens_deployed": 5_000_000,
    "reported_voting_power_share_pct": 25,
    "november_volume_usd": 2_500_000_000,
    "march_volume_usd": 687_900_000,
}

derived_values = {
    "settlement_value_per_voting_power_pct_usd": reported_values["disputed_market_value_usd"]
    / reported_values["reported_voting_power_share_pct"],
    "settlement_value_per_million_uma_usd": reported_values["disputed_market_value_usd"]
    / (reported_values["uma_tokens_deployed"] / 1_000_000),
    "monthly_volume_drop_usd": reported_values["november_volume_usd"]
    - reported_values["march_volume_usd"],
    "monthly_volume_drop_pct": (
        reported_values["november_volume_usd"] - reported_values["march_volume_usd"]
    )
    / reported_values["november_volume_usd"]
    * 100,
    "november_to_march_volume_ratio": reported_values["november_volume_usd"]
    / reported_values["march_volume_usd"],
}

rows = [
    (
        "reported_disputed_market_value",
        reported_values["disputed_market_value_usd"],
        "usd",
        COIN360_SOURCE,
        "Reported disputed Polymarket prediction market value.",
    ),
    (
        "reported_uma_tokens_deployed",
        reported_values["uma_tokens_deployed"],
        "uma_tokens",
        COIN360_SOURCE,
        "Reported UMA tokens deployed across three wallets.",
    ),
    (
        "reported_voting_power_share",
        reported_values["reported_voting_power_share_pct"],
        "percent",
        COIN360_SOURCE,
        "Reported share of total voting power attributed to the three-wallet UMA position.",
    ),
    (
        "reported_november_volume",
        reported_values["november_volume_usd"],
        "usd",
        CRYPTO_REPORT_SOURCE,
        "Reported Polymarket monthly volume during the 2024 U.S. election peak.",
    ),
    (
        "reported_march_volume",
        reported_values["march_volume_usd"],
        "usd",
        CRYPTO_REPORT_SOURCE,
        "Reported Polymarket monthly volume in March.",
    ),
    (
        "derived_settlement_value_per_voting_power_pct",
        derived_values["settlement_value_per_voting_power_pct_usd"],
        "usd_per_vote_percent",
        COIN360_SOURCE,
        "Disputed market value divided by reported voting-power share.",
    ),
    (
        "derived_settlement_value_per_million_uma",
        derived_values["settlement_value_per_million_uma_usd"],
        "usd_per_million_uma",
        COIN360_SOURCE,
        "Disputed market value divided by reported UMA tokens deployed in millions.",
    ),
    (
        "derived_monthly_volume_drop",
        derived_values["monthly_volume_drop_usd"],
        "usd",
        CRYPTO_REPORT_SOURCE,
        "November volume less March volume.",
    ),
    (
        "derived_monthly_volume_drop_pct",
        derived_values["monthly_volume_drop_pct"],
        "percent",
        CRYPTO_REPORT_SOURCE,
        "November-to-March volume drop divided by November volume.",
    ),
    (
        "derived_november_to_march_volume_ratio",
        derived_values["november_to_march_volume_ratio"],
        "ratio",
        CRYPTO_REPORT_SOURCE,
        "November volume divided by March volume.",
    ),
]


def fmt(value: float | int) -> str:
    if isinstance(value, int):
        return str(value)
    if value.is_integer():
        return str(int(value))
    return f"{value:.2f}"


def write_csv() -> None:
    with CSV_PATH.open("w", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["metric", "value", "unit", "source", "note"])
        for metric, value, unit, source, note in rows:
            writer.writerow([metric, fmt(float(value)), unit, source, note])


def bar(
    lines: list[str],
    *,
    label: str,
    value: float,
    max_value: float,
    x: int,
    y: int,
    width: int,
    height: int,
    color: str,
    suffix: str,
) -> None:
    filled = value / max_value * width
    lines.extend(
        [
            f'<text x="{x}" y="{y - 8}" font-family="Arial, sans-serif" font-size="13" fill="#111827">{label}</text>',
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="4" fill="#e5e7eb"/>',
            f'<rect x="{x}" y="{y}" width="{filled:.1f}" height="{height}" rx="4" fill="{color}"/>',
            f'<text x="{x + filled + 10:.1f}" y="{y + 24}" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#111827">{suffix}</text>',
        ]
    )


def write_svg() -> None:
    width = 860
    height = 500
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        "<title id=\"title\">Polymarket UMA governance stress metrics</title>",
        '<desc id="desc">Two-panel chart showing reported UMA governance exposure and Polymarket monthly-volume drawdown.</desc>',
        '<rect width="860" height="500" fill="#ffffff"/>',
        '<text x="32" y="38" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#111827">Polymarket UMA governance stress metrics</text>',
        '<text x="32" y="62" font-family="Arial, sans-serif" font-size="13" fill="#4b5563">Reported values and ratios derived from public coverage of the March 2025 oracle dispute.</text>',
        '<text x="32" y="104" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#111827">Governance exposure</text>',
    ]

    bar(
        lines,
        label="Disputed market value",
        value=7,
        max_value=7,
        x=32,
        y=124,
        width=470,
        height=38,
        color="#2563eb",
        suffix="$7.0M",
    )
    bar(
        lines,
        label="UMA deployed across reported wallets",
        value=5,
        max_value=7,
        x=32,
        y=192,
        width=470,
        height=38,
        color="#7c3aed",
        suffix="5.0M UMA",
    )
    bar(
        lines,
        label="Reported voting-power share",
        value=25,
        max_value=100,
        x=32,
        y=260,
        width=470,
        height=38,
        color="#dc2626",
        suffix="25.0%",
    )

    lines.extend(
        [
            '<text x="560" y="104" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#111827">Volume drawdown</text>',
        ]
    )
    bar(
        lines,
        label="November volume",
        value=2.5,
        max_value=2.5,
        x=560,
        y=124,
        width=250,
        height=38,
        color="#059669",
        suffix="$2.5B",
    )
    bar(
        lines,
        label="March volume",
        value=0.6879,
        max_value=2.5,
        x=560,
        y=192,
        width=250,
        height=38,
        color="#f59e0b",
        suffix="$687.9M",
    )
    bar(
        lines,
        label="Derived drop",
        value=1.8121,
        max_value=2.5,
        x=560,
        y=260,
        width=250,
        height=38,
        color="#b91c1c",
        suffix="$1.8B",
    )

    lines.extend(
        [
            f'<text x="32" y="350" font-family="Arial, sans-serif" font-size="13" fill="#111827">Derived settlement value per 1% reported vote share: ${derived_values["settlement_value_per_voting_power_pct_usd"] / 1000:.0f}K</text>',
            f'<text x="32" y="374" font-family="Arial, sans-serif" font-size="13" fill="#111827">Derived settlement value per 1M UMA deployed: ${derived_values["settlement_value_per_million_uma_usd"] / 1_000_000:.1f}M</text>',
            f'<text x="32" y="398" font-family="Arial, sans-serif" font-size="13" fill="#111827">Derived November-to-March volume drop: {derived_values["monthly_volume_drop_pct"]:.1f}%</text>',
            f'<text x="32" y="422" font-family="Arial, sans-serif" font-size="13" fill="#111827">Derived November/March volume ratio: {derived_values["november_to_march_volume_ratio"]:.2f}x</text>',
            '<text x="32" y="474" font-family="Arial, sans-serif" font-size="11" fill="#6b7280">Sources: Coin360 for governance exposure; Crypto.Report/Dune for monthly-volume figures.</text>',
            "</svg>",
        ]
    )
    SVG_PATH.write_text("\n".join(lines) + "\n")


def main() -> None:
    write_csv()
    write_svg()


if __name__ == "__main__":
    main()
