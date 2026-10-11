# Analysis of the Polymarket market on Maduro leaving office

Short version. Calculation details and file descriptions are in the [full report](README.md). A [Russian version](short_report_rus.md) is also available.

## Contents

1. [Purpose of the analysis](#1-purpose-of-the-analysis)
2. [Data sources](#2-data-sources)
   - [2.1. Trades and data preparation](#21-trades-and-data-preparation)
   - [2.2. Choosing the cutoff](#22-choosing-the-cutoff)
3. [Candidate selection and scoring](#3-candidate-selection-and-scoring)
   - [3.1. Initial wallet selection](#31-initial-wallet-selection)
   - [3.2. Candidate trading history](#32-candidate-trading-history)
   - [3.3. Calculating six heuristics](#33-calculating-six-heuristics)
   - [3.4. Building two rankings](#34-building-two-rankings)
4. [Results and their robustness](#4-results-and-their-robustness)
   - [4.1. Public mentions of candidates](#41-public-mentions-of-candidates)
   - [4.2. Changes under alternative assumptions](#42-changes-under-alternative-assumptions)
5. [Rerunning the analysis](#5-rerunning-the-analysis)

## 1. Purpose of the analysis

The aim is to identify wallets whose trading before the events of January 3, 2026 in Venezuela warrants investigation. The market is **“Will Maduro leave office by January 31, 2026?”** YES represents a bet on his departure; NO represents the opposite outcome.

The result is **116 candidates in two rankings**. Scores set investigation priorities but do not prove the use of nonpublic information.

## 2. Data sources

### 2.1. Trades and data preparation

The source is CryptoHouse, a public mirror of Polymarket records accessible through [ClickHouse](https://crypto-clickhouse.clickhouse.com/). **19,911 fills** on the main market were saved for December 27–January 3. One order may produce multiple fills.

The main market data was extracted from a previously saved dataset without new database queries. The analysis covers the **maker side of trades**; participants who traded only as takers are excluded from selection.

### 2.2. Choosing the cutoff

The cutoff is **January 3, 05:00 UTC**, one hour before an [FAA airspace restriction](https://notams.aim.faa.gov/notamSearch/createNotamPdf?download=true&transactionid=79311384) citing military activity took effect. This is a working cutoff, not an established time of the first rumor; the restriction's first publication time is unknown.

The selection window is the three days before the cutoff; the comparison period is the preceding 12 days. Trades at or after the cutoff are excluded. Alternative cutoffs of 04:00 and 06:00 are also checked.

![Comparison period and the last three days](results/figures/timeline_en.png)

## 3. Candidate selection and scoring

### 3.1. Initial wallet selection

Wallets are selected if their **YES buys and NO sells total at least 100 USDC** over three days. Selling NO may close an existing position rather than represent a new bet on Maduro's departure. Opposite trades are considered later in the direction metric.

**116 of 1,415 wallets were selected.**

### 3.2. Candidate trading history

**541,060 fills across all markets** were collected for candidates over the available portion of the period from December 1 to January 3, 06:00 UTC. The last hour supports only the alternative cutoff. History allows recent trading to be compared with previous behavior.

The source has no records for December 1–17. The comparison period therefore starts on December 19 at 05:00. Missing history does not prove that a wallet is new.

### 3.3. Calculating six heuristics

Each metric receives a value from 0 to 1. Higher values contribute more points.

| Metric | What raises the value | Weight |
|---|---|---:|
| Timing | YES buys and NO sells closer to the cutoff. | 20% |
| Size | Their total turnover exceeds that of other participants. | 5% |
| Direction | Trading in favor of YES outweighs opposite trading. | 25% |
| Own volume | Current average daily turnover exceeds the wallet's previous typical volume. | 20% |
| Activity | Average daily transaction count across all markets increases. | 15% |
| Concentration | The main market's share of the wallet's total turnover increases. | 15% |

The last three metrics require sufficient history. **A missing value means insufficient data; zero means data is available but the metric provides no signal.** Weights reflect expert judgment rather than training on confirmed insider trading cases.

### 3.4. Building two rankings

**84 wallets** have all metrics available: their score is the weighted sum of metric values multiplied by 100. **32 wallets** have missing values: unavailable metrics are excluded, and remaining weights are increased proportionally to sum to 100%.

For example, if only timing, size, and direction are available, weights of 20%, 5%, and 25% become 40%, 10%, and 50%. **Scores from the two groups are not directly comparable.** Within the incomplete group, interpretation also requires checking which metrics are available for each wallet.

Full lists: [all metrics available](results/ranking_complete.csv) and [missing values](results/ranking_incomplete.csv).

## 4. Results and their robustness

The first three candidates in each group:

| Group | Number on chart | Wallet | Score |
|---|---:|---|---:|
| All metrics | 1 | [0xe194…cd47](https://polygonscan.com/address/0xe194c638670b0a0acedc8efa00fc1c98aa49cd47) | 79.09 |
| All metrics | 2 | [0x858d…1047](https://polygonscan.com/address/0x858d551d073e9c647c17079ad9021de830201047) | 68.31 |
| All metrics | 3 | [0xee21…e2fe](https://polygonscan.com/address/0xee213de5ec7ab93c72bcad3c2c76552cb56de2fe) | 63.42 |
| Missing values | 1 | [0x6baf…94c5](https://polygonscan.com/address/0x6baf05d193692bb208d616709e27442c910a94c5) | 99.21 |
| Missing values | 2 | [0xa72d…ebd4](https://polygonscan.com/address/0xa72db1749e9ac2379d49a3c12708325ed17febd4) | 95.82 |
| Missing values | 3 | [0x31a5…8ed9](https://polygonscan.com/address/0x31a56e9e690c621ed21de08cb559e9524cdb8ed9) | 95.15 |

![Metric contributions to the leading candidates' scores](results/figures/score_contributions_en.png)

The complete group's leader received points from all six metrics. The incomplete group's leader received points only from timing, size, and direction. Its 99.21 does not imply greater suspicion than the complete group's 79.09.

### 4.1. Public mentions of candidates

A search of the first five wallets in each ranking found a public analysis of **the three leaders in the incomplete group**. [BlockBeats](https://www.binance.com/en/square/post/34623684785378) estimates their profits on Maduro bets at $145.6K, $75K, and $409.9K respectively. This information did not contribute to scoring.

[Odaily links](https://www.binance.com/en/square/post/315888847860113) `0x31a5…8ed9` to Gannon Ken Van Dyke. The [U.S. Department of Justice](https://www.justice.gov/opa/pr/us-soldier-charged-using-classified-information-profit-prediction-market-bets) announced charges over the use of classified information for bets, but did not give the full address. The address-to-person link relies on a secondary publication; charges do not establish guilt.

The second wallet in the complete group has the username flipfloppity. Its mention in [Prism News](https://www.prismnews.com/news/study-finds-143-million-in-suspected-insider-trading-on) concerning Iran bets remains an unverified lead: neither the original analysis nor a full address match has been established. No substantive discussions were found for the other six wallets.

### 4.2. Changes under alternative assumptions

**15 scenarios** were checked, varying cutoffs, windows, weights, thresholds, and missing-value rules. Among the ten scenarios varying the window, cutoff, weights, and history requirements, including the main calculation, the complete group's leader remains first in **8**, and the incomplete group's leader in **9**.

The weekly selection check is limited: it adds **83 wallets without collected history**. A complete weekly ranking was not calculated. Checks of the saved calculations passed.

The rankings provide a list for further trade investigation. A high score alone cannot distinguish insider trading from successful speculation, hedging, or a change in strategy.

## 5. Rerunning the analysis

From the project directory, using Python 3.13:

```powershell
python -m pip install -r requirements.txt
python src/run.py
python src/plot_report.py
```

The calculation uses saved data without network access. The last command updates the figures. Parameters are in [config.json](config.json); data collection details are in the [full report](README.md#5-rerunning-the-analysis).
