---
title: "Thomas Gity Digital Asset Trading Account Claims"
date: 2022-12-20
entities:
  - Thomas J. Gity
  - Thomas Gity
  - Thomas Gity Jr.
  - Treasure Coast Property Enterprises
  - Digital Asset Trading Accounts
---

## Summary

This case study analyzes the SEC's Thomas Gity action as a market-health warning about fake digital-asset trading-account statements, exaggerated account balances, and claimed no-risk weekly returns. On September 29, 2020, the SEC filed a complaint against Thomas J. Gity and named Thomas Gity Jr. and Treasure Coast Property Enterprises, LLC as relief defendants.

According to the [SEC litigation release](https://www.sec.gov/litigation/litreleases/2020/lr24930.htm), Gity received at least $6.8 million from at least 18 investors after presenting himself as a consistently profitable digital-asset trader. The SEC alleged that he used fake account statements to make investors believe he controlled as much as $100 million in assets and had generated unusually high trading returns.

The [SEC's harmed-investor distribution page](https://www.sec.gov/enforcement-litigation/distributions-harmed-investors/thomas-gity-sr-et-al-case-no-220-cv-14342-amc-sd-fla) later summarized the final posture. It said the complaint alleged that Gity advertised a risk-free trading profile with weekly performance reaching 46.83 percent. In reality, according to the SEC, less than $970,000 of the $6.8 million received from investors was deposited in digital-asset trading accounts, profits were not achieved as claimed, and investor funds were used for personal expenses or Ponzi-like payments.

The supporting dataset is available in [gity-summary.csv](gity-summary.csv).

## Claimed Trading Model

The SEC described Gity's pitch as a digital-asset trading operation with exceptionally high and low-risk performance. Investors were allegedly told that their money would be used to trade digital assets and that their capital was not at risk.

That model requires direct trading-account evidence. Reviewers should reconcile investor deposits to trading accounts, executed trades, realized and unrealized P&L, withdrawals, bank transfers, and investor distributions. A screenshot or account statement is not enough unless it can be tied to source account data controlled by an independent platform or custodian.

The SEC alleged that only a small portion of investor money reached trading accounts and that Gity did not achieve the stated profits. The alleged gap between capital received, capital actually deployed, and returns claimed is the core market-health signal.

## False Market Signals

### Fake account statements

The SEC alleged that Gity provided fake account statements to investors. Account statements should be verified against direct platform exports, account ownership records, trade logs, API records, and custody statements.

### Claimed $100 million asset base

The SEC alleged that Gity created the impression that he managed as much as $100 million in assets. Asset-under-management claims should be checked against bank, custody, exchange, and administrator records.

### No-risk high weekly returns

The SEC harmed-investor page said Gity claimed weekly returns as high as 46.83 percent with no market risk. Such claims require extraordinary proof and should trigger direct source-record testing.

### Partial trading-account funding

The SEC alleged that less than $970,000 of $6.8 million received from investors was deposited into digital-asset trading accounts. The first reconciliation step is whether money reached the advertised trading venue at all.

### Ponzi-like payments

The SEC said remaining investor funds were used for personal expenses or to pay other investors in a Ponzi-like fashion. Distributions should be traced to trading profits rather than new investor deposits.

## Event Timeline

| Date or period            | Event                                                                               | Market-health signal                                                          |
| ------------------------- | ----------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| January 2018-January 2019 | The SEC alleged Gity solicited investor money for digital-asset trading.            | Trading claims required deposit, trade, and P&L records.                      |
| Scheme period             | The SEC alleged Gity received at least $6.8 million from at least 18 investors.     | Investor scale required account-level ledgers and source-of-funds tracing.    |
| Scheme period             | The SEC alleged Gity claimed he managed more than $100 million in digital assets.   | AUM claims needed independent custody and account verification.               |
| Scheme period             | The SEC alleged weekly returns as high as 46.83 percent with no market risk.        | Return claims required direct trading-account proof.                          |
| Scheme period             | The SEC alleged less than $970,000 was deposited in digital-asset trading accounts. | Capital deployment did not match the trading narrative.                       |
| September 29, 2020        | The SEC filed the civil complaint in the Southern District of Florida.              | Enforcement action documented alleged account-statement and trading failures. |
| June 21, 2021             | The court entered a final judgment by consent against Gity in part.                 | Judgment-stage relief began.                                                  |
| September 23, 2021        | The court entered final monetary judgment by consent against Gity.                  | Final judgment imposed disgorgement, interest, and penalty.                   |
| December 20, 2022         | The SEC published the harmed-investor distribution page.                            | Distribution process summarized final remedies and alleged investor harm.     |

## Reconciliation Metrics

| Metric                   | SEC allegation or judgment figure                                        | Market-health interpretation                                               |
| ------------------------ | ------------------------------------------------------------------------ | -------------------------------------------------------------------------- |
| Investor funds received  | At least $6.8 million                                                    | Investor deposits needed bank, wallet, and trading-account tracing.        |
| Investor count           | At least 18 investors                                                    | Customer records should connect contributions, trades, and distributions.  |
| Claimed AUM              | More than $100 million in digital assets                                 | AUM claims required independent custody and account evidence.              |
| Claimed weekly return    | Up to 46.83 percent with no market risk                                  | Return claim required direct P&L proof and risk disclosure.                |
| Trading-account deposits | Less than $970,000 alleged deposited into digital-asset trading accounts | Most investor capital allegedly did not reach the advertised trading use.  |
| Final disgorgement       | $4,676,716                                                               | Judgment required return of ill-gotten gains.                              |
| Prejudgment interest     | $241,647.52                                                              | Judgment added time-value remedy.                                          |
| Civil penalty            | $192,768                                                                 | Penalty reflected final monetary relief.                                   |
| Total final judgment     | $5,111,131.52                                                            | Final judgment quantified monetary relief against Gity.                    |
| Legal posture            | Final judgments by consent against Gity                                  | Article should distinguish SEC allegations from consent-judgment remedies. |

## Detection Checklist

1. Reconcile investor deposits to trading accounts before reviewing reported performance.
2. Verify account statements against direct platform data, custody records, and account ownership.
3. Test claimed AUM against independent bank, wallet, exchange, and administrator records.
4. Reconcile return percentages to executed trades, realized P&L, fees, and withdrawals.
5. Trace distributions to trading profits rather than later investor deposits.
6. Flag no-risk or never-lost trading claims as requiring direct source-record proof.
7. Preserve legal posture: this article relies on SEC allegations and final consent judgments, so alleged conduct should remain attributed to the SEC.

## Market-Health Lessons

Gity shows why fake account statements can be as damaging as false trading claims. A statement can create the appearance of scale and performance, but market-health review should require source records from the actual trading venue or custodian.

The case also shows why capital-deployment reconciliation comes first. If most investor money never reaches the advertised trading accounts, later return figures and payout history cannot validate the trading strategy.

## References

- [SEC litigation release, Thomas J. Gity, September 29, 2020](https://www.sec.gov/litigation/litreleases/2020/lr24930.htm)
- [SEC complaint, SEC v. Thomas J. Gity, et al.](https://www.sec.gov/litigation/complaints/2020/comp24930.pdf)
- [SEC harmed-investor distribution page, Thomas Gity, Sr., et al., December 20, 2022](https://www.sec.gov/enforcement-litigation/distributions-harmed-investors/thomas-gity-sr-et-al-case-no-220-cv-14342-amc-sd-fla)
