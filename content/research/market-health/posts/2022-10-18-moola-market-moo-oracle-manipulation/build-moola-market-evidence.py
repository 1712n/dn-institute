#!/usr/bin/env python3
"""Generate the Moola Market incident metrics table and SVG chart."""

import csv
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent

FACTS = {
    "seed_celo_funding_usd": 243000.0,
    "initial_celo_collateral": 60000.0,
    "initial_moo_borrowed": 1875000.0,
    "moo_start_price_usd": 0.018,
    "moo_peak_price_usd": 5.6,
    "certik_low_loss_estimate_usd": 8400000.0,
    "sch_total_lost_usd": 9100000.0,
    "sch_recovered_usd": 8500000.0,
    "reported_recovery_rate_pct": 93.1,
}

DERIVED = {
    "moo_price_multiple": FACTS["moo_peak_price_usd"] / FACTS["moo_start_price_usd"],
    "low_loss_to_seed_capital_multiple": FACTS["certik_low_loss_estimate_usd"]
    / FACTS["seed_celo_funding_usd"],
    "retained_loss_rate_pct": 100 - FACTS["reported_recovery_rate_pct"],
    "sch_recovered_to_lost_pct": FACTS["sch_recovered_usd"]
    / FACTS["sch_total_lost_usd"]
    * 100,
}

ROWS = [
    (
        "seed_celo_funding_usd",
        FACTS["seed_celo_funding_usd"],
        "USD",
        "source-reported attacker funding from Binance",
        "https://www.certik.com/blog/8ENVqveSYRcppTHOcxG29-moola-market",
    ),
    (
        "initial_celo_collateral",
        FACTS["initial_celo_collateral"],
        "CELO",
        "source-reported CELO lent as collateral before the first MOO borrow",
        "https://www.certik.com/blog/8ENVqveSYRcppTHOcxG29-moola-market",
    ),
    (
        "initial_moo_borrowed",
        FACTS["initial_moo_borrowed"],
        "MOO",
        "source-reported MOO borrowed against the CELO collateral",
        "https://www.certik.com/blog/8ENVqveSYRcppTHOcxG29-moola-market",
    ),
    (
        "moo_start_price_usd",
        FACTS["moo_start_price_usd"],
        "USD per MOO",
        "source-reported pre-manipulation MOO price",
        "https://www.certik.com/blog/8ENVqveSYRcppTHOcxG29-moola-market",
    ),
    (
        "moo_peak_price_usd",
        FACTS["moo_peak_price_usd"],
        "USD per MOO",
        "source-reported manipulated MOO peak price",
        "https://www.certik.com/blog/8ENVqveSYRcppTHOcxG29-moola-market",
    ),
    (
        "moo_price_multiple",
        DERIVED["moo_price_multiple"],
        "x",
        "moo_peak_price_usd / moo_start_price_usd",
        "derived",
    ),
    (
        "certik_low_loss_estimate_usd",
        FACTS["certik_low_loss_estimate_usd"],
        "USD",
        "CertiK low estimate for drained funds",
        "https://www.certik.com/blog/8ENVqveSYRcppTHOcxG29-moola-market",
    ),
    (
        "sch_total_lost_usd",
        FACTS["sch_total_lost_usd"],
        "USD",
        "Smart Contract Hacking total lost estimate",
        "https://smartcontractshacking.com/hacks/moola-market-hack-2022",
    ),
    (
        "low_loss_to_seed_capital_multiple",
        DERIVED["low_loss_to_seed_capital_multiple"],
        "x",
        "certik_low_loss_estimate_usd / seed_celo_funding_usd",
        "derived",
    ),
    (
        "reported_recovery_rate_pct",
        FACTS["reported_recovery_rate_pct"],
        "percent",
        "source-reported returned share",
        "https://smartcontractshacking.com/hacks/moola-market-hack-2022",
    ),
    (
        "retained_loss_rate_pct",
        DERIVED["retained_loss_rate_pct"],
        "percent",
        "100 - reported_recovery_rate_pct",
        "derived",
    ),
]


def format_value(value):
    if value >= 1000:
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return f"{value:.4f}".rstrip("0").rstrip(".")


def write_csv():
    with (OUT_DIR / "moola-market-incident-metrics.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["metric", "value", "unit", "calculation_or_basis", "source"])
        for metric, value, unit, calculation, source in ROWS:
            writer.writerow([metric, format_value(value), unit, calculation, source])


def write_svg():
    bars = [
        ("MOO price expansion", DERIVED["moo_price_multiple"], "311.1x", 320),
        (
            "Loss / seed capital",
            DERIVED["low_loss_to_seed_capital_multiple"],
            "34.6x",
            320,
        ),
        ("Recovered funds", FACTS["reported_recovery_rate_pct"], "93.1%", 100),
    ]
    rows = []
    for index, (label, value, display, scale) in enumerate(bars):
        y = 92 + index * 78
        width = round((value / scale) * 470, 1)
        rows.append(
            f'<text x="44" y="{y}" class="label">{label}</text>'
            f'<rect x="240" y="{y - 20}" width="{width}" height="28" rx="4" '
            'class="bar"/>'
            f'<text x="{252 + width}" y="{y}" class="value">{display}</text>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="340" viewBox="0 0 760 340" role="img" aria-labelledby="title desc">
  <title id="title">Moola Market reported extraction multiples</title>
  <desc id="desc">Horizontal bars showing the reported MOO price expansion, estimated loss to seed-capital multiple, and recovered funds percentage.</desc>
  <style>
    .bg {{ fill: #ffffff; }}
    .title {{ fill: #17202a; font: 700 22px Arial, sans-serif; }}
    .subtitle {{ fill: #566573; font: 14px Arial, sans-serif; }}
    .label {{ fill: #1f2933; font: 600 15px Arial, sans-serif; }}
    .value {{ fill: #17202a; font: 700 15px Arial, sans-serif; }}
    .bar {{ fill: #2f6f73; }}
    .rule {{ stroke: #d6dde2; stroke-width: 1; }}
    .note {{ fill: #566573; font: 12px Arial, sans-serif; }}
  </style>
  <rect class="bg" x="0" y="0" width="760" height="340"/>
  <text x="44" y="42" class="title">Reported Moola extraction economics</text>
  <text x="44" y="66" class="subtitle">Source-reported values with derived ratios from the bundled metrics CSV</text>
  <line x1="240" x2="710" y1="296" y2="296" class="rule"/>
  {''.join(rows)}
  <text x="44" y="316" class="note">Price expansion uses $5.60 / $0.018. Loss multiple uses $8.4M / $243k. Recovery uses the reported 93.1% returned share.</text>
</svg>
'''
    (OUT_DIR / "moola-market-extraction-multiples.svg").write_text(
        svg, encoding="utf-8"
    )


def main():
    write_csv()
    write_svg()


if __name__ == "__main__":
    main()
