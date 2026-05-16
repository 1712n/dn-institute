#!/usr/bin/env python3
"""Generate reproducible evidence artifacts for the Beanstalk governance case."""

import csv
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent

DN_SOURCE = "https://dn.institute/research/cyberattacks/incidents/2022-04-17-beanstalk/"
CERTIK_SOURCE = "https://www.certik.com/resources/blog/revisiting-beanstalk-farms-exploit"
IMMUNEFI_SOURCE = (
    "https://immunefi.com/blog/bug-fix-reviews/"
    "hack-analysis-beanstalk-governance-attack-april-2022/"
)

FACTS = {
    "reported_total_loss_usd": 182_000_000.0,
    "reported_non_beanstalk_pool_assets_usd": 77_000_000.0,
    "reported_attacker_profit_usd": 80_000_000.0,
    "reported_certik_profit_usd": 76_000_000.0,
    "reported_flash_loan_repaid_usd": 106_000_000.0,
    "reported_attacker_profit_eth": 24_840.0,
    "reported_ukraine_donation_usd": 250_000.0,
    "reported_flash_loan_borrowed_usd": 1_000_000_000.0,
    "reported_voting_stake_pct": 67.0,
    "governance_supermajority_pct": 66.6667,
    "bean_target_price_usd": 1.0,
    "bean_post_attack_price_usd": 0.12,
    "reported_bean_drop_pct": 88.0,
}

DERIVED = {
    "attacker_profit_share_of_loss_pct": FACTS["reported_attacker_profit_usd"]
    / FACTS["reported_total_loss_usd"]
    * 100,
    "flash_loan_repayment_share_of_loss_pct": FACTS["reported_flash_loan_repaid_usd"]
    / FACTS["reported_total_loss_usd"]
    * 100,
    "loss_to_attacker_profit_multiple": FACTS["reported_total_loss_usd"]
    / FACTS["reported_attacker_profit_usd"],
    "bean_price_remaining_pct": FACTS["bean_post_attack_price_usd"]
    / FACTS["bean_target_price_usd"]
    * 100,
    "derived_peg_repricing_shock_pct": (
        FACTS["bean_target_price_usd"] - FACTS["bean_post_attack_price_usd"]
    )
    / FACTS["bean_target_price_usd"]
    * 100,
    "loss_per_peg_shock_pct_usd": FACTS["reported_total_loss_usd"]
    / FACTS["reported_bean_drop_pct"],
    "flash_loan_to_reported_loss_multiple": FACTS["reported_flash_loan_borrowed_usd"]
    / FACTS["reported_total_loss_usd"],
    "reported_vote_margin_over_supermajority_pct": FACTS["reported_voting_stake_pct"]
    - FACTS["governance_supermajority_pct"],
}

ROWS = [
    (
        "reported_total_loss",
        FACTS["reported_total_loss_usd"],
        "USD",
        "DN Institute reported total Beanstalk incident loss.",
        DN_SOURCE,
    ),
    (
        "reported_attacker_profit",
        FACTS["reported_attacker_profit_usd"],
        "USD",
        "DN Institute reported 24,840 ETH attacker profit value.",
        DN_SOURCE,
    ),
    (
        "reported_attacker_profit_eth",
        FACTS["reported_attacker_profit_eth"],
        "ETH",
        "DN Institute reported attacker profit in ETH.",
        DN_SOURCE,
    ),
    (
        "reported_non_beanstalk_pool_assets",
        FACTS["reported_non_beanstalk_pool_assets_usd"],
        "USD",
        "DN Institute reported assets taken from non-Beanstalk liquidity pools.",
        DN_SOURCE,
    ),
    (
        "reported_flash_loan_repaid",
        FACTS["reported_flash_loan_repaid_usd"],
        "USD",
        "DN Institute reported value returned through flash-loan repayment.",
        DN_SOURCE,
    ),
    (
        "reported_flash_loan_borrowed",
        FACTS["reported_flash_loan_borrowed_usd"],
        "USD",
        "DN Institute reported nearly $1B borrowed through Aave.",
        DN_SOURCE,
    ),
    (
        "reported_voting_stake",
        FACTS["reported_voting_stake_pct"],
        "percent",
        "DN Institute reported governance stake created by the flash loan.",
        DN_SOURCE,
    ),
    (
        "reported_supermajority_reference",
        FACTS["governance_supermajority_pct"],
        "percent",
        "Immunefi described the attack path as gaining at least two-thirds voting power.",
        IMMUNEFI_SOURCE,
    ),
    (
        "bean_post_attack_price",
        FACTS["bean_post_attack_price_usd"],
        "USD per BEAN",
        "DN Institute reported BEAN post-attack price.",
        DN_SOURCE,
    ),
    (
        "reported_bean_drop",
        FACTS["reported_bean_drop_pct"],
        "percent",
        "DN Institute reported approximate BEAN price drop.",
        DN_SOURCE,
    ),
    (
        "reported_certik_loss",
        FACTS["reported_total_loss_usd"],
        "USD",
        "CertiK corroborated approximate total loss.",
        CERTIK_SOURCE,
    ),
    (
        "reported_certik_profit",
        FACTS["reported_certik_profit_usd"],
        "USD",
        "CertiK reported attacker profit estimate.",
        CERTIK_SOURCE,
    ),
    (
        "reported_ukraine_donation",
        FACTS["reported_ukraine_donation_usd"],
        "USD",
        "DN Institute and CertiK reported the attacker donation to Ukraine aid.",
        CERTIK_SOURCE,
    ),
    (
        "derived_attacker_profit_share_of_loss",
        DERIVED["attacker_profit_share_of_loss_pct"],
        "percent",
        "reported_attacker_profit_usd / reported_total_loss_usd",
        "derived",
    ),
    (
        "derived_flash_loan_repayment_share_of_loss",
        DERIVED["flash_loan_repayment_share_of_loss_pct"],
        "percent",
        "reported_flash_loan_repaid_usd / reported_total_loss_usd",
        "derived",
    ),
    (
        "derived_loss_to_attacker_profit_multiple",
        DERIVED["loss_to_attacker_profit_multiple"],
        "x",
        "reported_total_loss_usd / reported_attacker_profit_usd",
        "derived",
    ),
    (
        "derived_bean_price_remaining",
        DERIVED["bean_price_remaining_pct"],
        "percent",
        "bean_post_attack_price_usd / bean_target_price_usd",
        "derived",
    ),
    (
        "derived_peg_repricing_shock",
        DERIVED["derived_peg_repricing_shock_pct"],
        "percent",
        "(bean_target_price_usd - bean_post_attack_price_usd) / bean_target_price_usd",
        "derived",
    ),
    (
        "derived_loss_per_peg_shock_pct",
        DERIVED["loss_per_peg_shock_pct_usd"],
        "USD per percentage point",
        "reported_total_loss_usd / reported_bean_drop_pct",
        "derived",
    ),
    (
        "derived_flash_loan_to_reported_loss_multiple",
        DERIVED["flash_loan_to_reported_loss_multiple"],
        "x",
        "reported_flash_loan_borrowed_usd / reported_total_loss_usd",
        "derived",
    ),
    (
        "derived_vote_margin_over_supermajority",
        DERIVED["reported_vote_margin_over_supermajority_pct"],
        "percentage points",
        "reported_voting_stake_pct - 66.6667% supermajority reference",
        "derived",
    ),
]


def format_value(value):
    if abs(value) >= 1_000:
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return f"{value:.4f}".rstrip("0").rstrip(".")


def write_csv():
    with (OUT_DIR / "beanstalk-governance-peg-signals.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["metric", "value", "unit", "calculation_or_basis", "source"])
        for metric, value, unit, calculation, source in ROWS:
            writer.writerow([metric, format_value(value), unit, calculation, source])


def format_millions(value):
    return f"${value / 1_000_000:.0f}M"


def format_pct(value):
    return f"{value:.0f}%"


def format_multiple(value):
    return f"{value:.2f}x"


def write_svg():
    bars = [
        (
            "Total reported loss",
            FACTS["reported_total_loss_usd"] / 1_000_000,
            format_millions(FACTS["reported_total_loss_usd"]),
            190,
            "#b91c1c",
        ),
        (
            "Flash-loan repayment",
            FACTS["reported_flash_loan_repaid_usd"] / 1_000_000,
            format_millions(FACTS["reported_flash_loan_repaid_usd"]),
            190,
            "#c2410c",
        ),
        (
            "Attacker profit",
            FACTS["reported_attacker_profit_usd"] / 1_000_000,
            format_millions(FACTS["reported_attacker_profit_usd"]),
            190,
            "#7c2d12",
        ),
        (
            "BEAN peg shock",
            DERIVED["derived_peg_repricing_shock_pct"],
            format_pct(DERIVED["derived_peg_repricing_shock_pct"]),
            100,
            "#1d4ed8",
        ),
        (
            "Post-attack BEAN price",
            DERIVED["bean_price_remaining_pct"],
            f"{format_pct(DERIVED['bean_price_remaining_pct'])} of peg",
            100,
            "#0f766e",
        ),
        (
            "Flash loan / loss multiple",
            DERIVED["flash_loan_to_reported_loss_multiple"],
            format_multiple(DERIVED["flash_loan_to_reported_loss_multiple"]),
            6,
            "#4c1d95",
        ),
    ]

    rows = []
    for index, (label, value, display, scale, color) in enumerate(bars):
        y = 104 + index * 58
        width = round((value / scale) * 430, 1)
        rows.append(
            f'<text x="44" y="{y}" class="label">{label}</text>'
            f'<rect x="268" y="{y - 22}" width="430" height="30" rx="4" class="track"/>'
            f'<rect x="268" y="{y - 22}" width="{width}" height="30" rx="4" fill="{color}"/>'
            f'<text x="{282 + width}" y="{y}" class="value">{display}</text>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="520" viewBox="0 0 800 520" role="img" aria-labelledby="title desc">
  <title id="title">Beanstalk governance exploit market-health metrics</title>
  <desc id="desc">Horizontal bars showing reported Beanstalk loss, flash-loan repayment, attacker profit, BEAN peg shock, remaining peg price, and flash-loan-to-loss multiple.</desc>
  <style>
    .bg {{ fill: #ffffff; }}
    .title {{ fill: #17202a; font: 700 22px Arial, sans-serif; }}
    .subtitle {{ fill: #566573; font: 14px Arial, sans-serif; }}
    .label {{ fill: #1f2933; font: 600 15px Arial, sans-serif; }}
    .value {{ fill: #17202a; font: 700 15px Arial, sans-serif; }}
    .track {{ fill: #e5e7eb; }}
    .note {{ fill: #566573; font: 12px Arial, sans-serif; }}
  </style>
  <rect class="bg" x="0" y="0" width="800" height="520"/>
  <text x="44" y="42" class="title">Beanstalk governance exploit market-health metrics</text>
  <text x="44" y="66" class="subtitle">Source-reported values with derived market-risk ratios from the bundled CSV</text>
  {''.join(rows)}
  <text x="44" y="480" class="note">Derived values: profit share = $80M / $182M; repayment share = $106M / $182M; peg shock = ($1.00 - $0.12) / $1.00.</text>
</svg>
'''
    (OUT_DIR / "beanstalk-governance-peg-metrics.svg").write_text(
        svg, encoding="utf-8"
    )


def main():
    write_csv()
    write_svg()


if __name__ == "__main__":
    main()
