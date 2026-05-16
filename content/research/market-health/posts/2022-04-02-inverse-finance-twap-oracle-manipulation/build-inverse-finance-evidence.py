#!/usr/bin/env python3
"""Build reproducible evidence artifacts for the Inverse Finance case."""

from __future__ import annotations

import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "inverse-finance-twap-signals.csv"
SVG_PATH = BASE_DIR / "inverse-finance-extraction-metrics.svg"

SOURCE = "https://www.web3isgoinggreat.com/?id=inverse-finance-exploited"

reported_values = {
    "borrowed_basket_value_usd": 15_600_000,
    "converted_eth": 4_300,
    "converted_eth_value_usd": 14_500_000,
    "mixer_transfer_eth": 1_300,
    "mixer_transfer_value_usd": 4_500_000,
    "borrowed_asset_count": 4,
}

derived_values = {
    "notional_to_realized_haircut_usd": reported_values["borrowed_basket_value_usd"]
    - reported_values["converted_eth_value_usd"],
    "realized_value_share_pct": reported_values["converted_eth_value_usd"]
    / reported_values["borrowed_basket_value_usd"]
    * 100,
    "mixer_transfer_share_of_converted_eth_pct": reported_values["mixer_transfer_eth"]
    / reported_values["converted_eth"]
    * 100,
    "implied_converted_eth_price_usd": reported_values["converted_eth_value_usd"]
    / reported_values["converted_eth"],
    "implied_mixer_transfer_eth_price_usd": reported_values["mixer_transfer_value_usd"]
    / reported_values["mixer_transfer_eth"],
}

rows = [
    (
        "reported_borrowed_basket_value",
        reported_values["borrowed_basket_value_usd"],
        "usd",
        "Borrowed DOLA, ETH, WBTC, and YFI basket reported at about $15.6 million.",
    ),
    (
        "reported_converted_eth",
        reported_values["converted_eth"],
        "eth",
        "Borrowed assets were converted into about 4,300 ETH.",
    ),
    (
        "reported_converted_eth_value",
        reported_values["converted_eth_value_usd"],
        "usd",
        "The converted ETH was reported at about $14.5 million.",
    ),
    (
        "reported_mixer_transfer_eth",
        reported_values["mixer_transfer_eth"],
        "eth",
        "About 1,300 ETH was transferred to a mixer by early April 2.",
    ),
    (
        "reported_mixer_transfer_value",
        reported_values["mixer_transfer_value_usd"],
        "usd",
        "The mixer transfer was reported at about $4.5 million.",
    ),
    (
        "reported_borrowed_asset_count",
        reported_values["borrowed_asset_count"],
        "count",
        "The extractable basket crossed four assets: DOLA, ETH, WBTC, and YFI.",
    ),
    (
        "derived_notional_to_realized_haircut",
        derived_values["notional_to_realized_haircut_usd"],
        "usd",
        "Difference between reported borrowed-basket notional and converted ETH value.",
    ),
    (
        "derived_realized_value_share",
        derived_values["realized_value_share_pct"],
        "percent",
        "Converted ETH value divided by reported borrowed-basket value.",
    ),
    (
        "derived_mixer_transfer_share",
        derived_values["mixer_transfer_share_of_converted_eth_pct"],
        "percent",
        "Mixer transfer ETH divided by converted ETH.",
    ),
    (
        "derived_implied_converted_eth_price",
        derived_values["implied_converted_eth_price_usd"],
        "usd_per_eth",
        "Converted ETH value divided by converted ETH quantity.",
    ),
    (
        "derived_implied_mixer_transfer_eth_price",
        derived_values["implied_mixer_transfer_eth_price_usd"],
        "usd_per_eth",
        "Mixer transfer value divided by mixer transfer ETH quantity.",
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
        for metric, value, unit, note in rows:
            writer.writerow([metric, fmt(float(value)), unit, SOURCE, note])


def write_svg() -> None:
    bars = [
        ("Borrowed basket", reported_values["borrowed_basket_value_usd"] / 1_000_000),
        ("Converted ETH value", reported_values["converted_eth_value_usd"] / 1_000_000),
        ("Mixer transfer", reported_values["mixer_transfer_value_usd"] / 1_000_000),
        ("Haircut", derived_values["notional_to_realized_haircut_usd"] / 1_000_000),
    ]
    width = 820
    height = 390
    left = 190
    top = 70
    bar_height = 46
    gap = 28
    max_value = max(value for _, value in bars)
    chart_width = 520

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        "<title id=\"title\">Inverse Finance reported extraction metrics</title>",
        '<desc id="desc">Bar chart comparing reported borrowed basket value, converted ETH value, mixer transfer value, and derived haircut.</desc>',
        '<rect width="820" height="390" fill="#ffffff"/>',
        '<text x="32" y="36" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#111827">Inverse Finance extraction metrics</text>',
        '<text x="32" y="58" font-family="Arial, sans-serif" font-size="13" fill="#4b5563">Reported values and simple ratios derived from the public incident record.</text>',
    ]

    for index, (label, value) in enumerate(bars):
        y = top + index * (bar_height + gap)
        bar_width = value / max_value * chart_width
        color = "#2563eb" if index < 2 else "#7c3aed" if index == 2 else "#dc2626"
        lines.extend(
            [
                f'<text x="32" y="{y + 29}" font-family="Arial, sans-serif" font-size="14" fill="#111827">{label}</text>',
                f'<rect x="{left}" y="{y}" width="{chart_width}" height="{bar_height}" rx="4" fill="#e5e7eb"/>',
                f'<rect x="{left}" y="{y}" width="{bar_width:.1f}" height="{bar_height}" rx="4" fill="{color}"/>',
                f'<text x="{left + bar_width + 12:.1f}" y="{y + 29}" font-family="Arial, sans-serif" font-size="14" font-weight="700" fill="#111827">${value:.1f}M</text>',
            ]
        )

    lines.extend(
        [
            f'<text x="32" y="{height - 62}" font-family="Arial, sans-serif" font-size="13" fill="#111827">Derived realized-value share: {derived_values["realized_value_share_pct"]:.1f}%</text>',
            f'<text x="32" y="{height - 40}" font-family="Arial, sans-serif" font-size="13" fill="#111827">Derived mixer-transfer share of converted ETH: {derived_values["mixer_transfer_share_of_converted_eth_pct"]:.1f}%</text>',
            '<text x="32" y="370" font-family="Arial, sans-serif" font-size="11" fill="#6b7280">Source: Web3 Is Going Great incident record; values rounded as reported.</text>',
            "</svg>",
        ]
    )
    SVG_PATH.write_text("\n".join(lines) + "\n")


def main() -> None:
    write_csv()
    write_svg()


if __name__ == "__main__":
    main()
