[README.md](https://github.com/user-attachments/files/33222207/README.md)
# Polymarket Potential Informed Trading Analysis

## Overview

This project investigates potential informed trading behavior on Polymarket using publicly available market and trade data.

The goal is not to prove insider trading, but to identify wallets whose trading behavior may deserve further investigation.

## Research Period

**November 1, 2025 – May 1, 2026**

## Data

The analysis uses public Polymarket data from:

- Gamma API — market metadata and resolution information
- Data API — historical trade data

There were **1,161 markets** closed during the research period.

To keep the analysis manageable, the research focused on the **30 markets with the highest trading volume**.

This resulted in approximately **1.33 million historical trades** and **383,615 trades** within the research period.

## Methodology

Wallets were screened using several simple and explainable signals:

1. **Winning outcome** — the wallet bought the outcome that eventually won.
2. **Timing** — the purchase was made 6–72 hours before market resolution.
3. **Trade size** — the position was at least $1,000.
4. **Price movement** — the price moved in the wallet's favor during the following 6 hours.
5. **Repeatability** — similar behavior appeared across multiple markets.
6. **Bot-like activity** — wallets with extremely frequent trading were treated with lower priority.

The final ranking is an investigation-priority ranking, not a probability of insider trading.

## Main Findings

The analysis identified several wallets with behavior that may be consistent with potentially informed trading.

The main candidates were:

1. `0x24c8...`
2. `0x7c3d...`
3. `0xd218...`
4. `0x0c4b...`
5. `0xbacd...`

No wallet was classified as a confirmed insider.

The full reasoning and limitations are described in `report.md`.

## Repository Structure

```text
├── README.md
├── report.md
├── analysis.ipynb
└── artifacts/
    ├── top_markets.csv
    ├── wallet_ranking.csv
    ├── suspicious_trades.csv
    └── top5_investigation_trades.csv
```

### Artifacts

- `top_markets.csv` — the 30 markets included in the analysis.
- `wallet_ranking.csv` — ranked wallets and their main metrics.
- `suspicious_trades.csv` — trades matching the main screening criteria.
- `top5_investigation_trades.csv` — detailed trades for the five main candidates.

## Reproducibility

The complete analysis is available in `analysis.ipynb`.

The notebook contains the steps used to:

1. collect market data;
2. select the top 30 markets;
3. collect historical trades;
4. filter trades to the research period;
5. determine winning outcomes;
6. calculate timing and price-movement metrics;
7. rank wallets;
8. inspect the highest-priority candidates.

## Limitations

This is a retrospective screening analysis based only on public data.

Correctly predicting an outcome does not prove insider trading. Price movement after a trade is also not the same as realized profit.

The selected markets are not fully independent, and some wallets may be professional traders, arbitrageurs, or automated strategies rather than insiders.

Therefore, the results should be interpreted as a **shortlist for further investigation**, not as proof of misconduct.
<!-- Final research submission -->
