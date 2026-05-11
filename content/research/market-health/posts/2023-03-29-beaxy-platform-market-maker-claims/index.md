---
title: "Beaxy Platform Market Maker and Custody Claims"
date: 2023-03-29
entities:
  - Beaxy
  - Beaxy Platform
  - Windy Inc
  - Nicholas Murphy
  - Randolph Bay Abbott
  - Brian Peterson
  - Braverock Entities
  - BXY
  - DRGN
---

## Summary

This case study analyzes the SEC's Beaxy action as a market-health warning about crypto platforms that combine exchange, broker, clearing, custody, and market-making functions without the separations and records expected in regulated markets. On March 29, 2023, the SEC announced charges against the Beaxy Platform and its executives, and on April 3, 2023, the SEC issued a litigation release summarizing the same action.

According to the SEC's complaint summary, since October 2019, Nicholas Murphy and Randolph Bay Abbott, through Windy Inc., maintained Beaxy as a web-based trading platform that facilitated buying and selling of crypto assets that the SEC alleged were securities. The SEC alleged that Windy brought together orders using non-discretionary methods, acted as an intermediary in payments and deliveries after matching trades, maintained custody of customer assets, and effected transactions for others.

The SEC also alleged that Windy entered into market-making agreements with Brian Peterson and his companies, referred to as the Braverock Entities, for BXY and another crypto asset security. The SEC said Peterson and those entities acted as unregistered dealers. Several settling defendants agreed to cease the relevant activities, shut down the Beaxy Platform, provide an accounting of customer assets and funds, transfer customer assets and funds back to customers, destroy BXY in Windy's possession, and pay monetary remedies.

The supporting dataset is available in [beaxy-summary.csv](beaxy-summary.csv).

## Platform Function Pattern

The SEC described Beaxy as one platform performing multiple market functions. It brought together orders, intermediated payments and deliveries, held customer assets, and effected transactions for users. Those are separate roles in traditional securities-market structure because each role introduces different conflicts, recordkeeping needs, and investor-protection obligations.

For market-health review, the key question is not only whether a platform has a trading screen. Reviewers should identify who controls order matching, custody, delivery, customer assets, market-maker accounts, market-maker agreements, listing review, and customer disclosures. When those functions sit inside one affiliated structure, surveillance should look for conflicts and missing independent checks.

The Beaxy action also highlights liquidity-provider risk. Market makers can improve displayed liquidity, but their agreements, assets traded, fees, algorithms, account ownership, and trading records should be clear to platform users and regulators.

## False Market Signals

### Combined exchange-broker-clearing role

The SEC alleged that Windy, through Beaxy, performed exchange, broker, and clearing-agency functions. Combined roles can make platform activity look orderly while removing independent checks on execution, custody, and settlement.

### Custody and customer-asset control

The SEC alleged that Windy maintained custody of customer assets. Custody claims should be reconciled to wallet controls, bank accounts, customer ledgers, withdrawal records, and post-shutdown asset return obligations.

### Market-making arrangements

The complaint summary alleged market-making agreements for BXY and another crypto asset security. Market-maker participation should be reviewed for fee arrangements, principal trading, inventory, account ownership, algorithmic strategy, wash-trading controls, and disclosure.

### Listing and securities review

The SEC alleged that Murphy and Abbott oversaw review, removal, and resumption of trading of various crypto assets but did not prevent trading of crypto asset securities despite facts showing they were securities. Listing review should be documented and tied to actual trading restrictions.

### Platform shutdown and accounting

The settling parties agreed to provide an accounting of customer assets and funds, transfer assets and funds back to customers, and destroy any BXY in Windy's possession. Those undertakings show why customer-ledger and custody reconciliation matter when a platform stops operating.

## Event Timeline

| Date or period      | Event                                                                                                      | Market-health signal                                                      |
| ------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| October 2019 onward | The SEC alleged Windy maintained the Beaxy Platform for trading crypto assets that were securities.        | Trading venue operation required order, custody, and settlement controls. |
| December 2019       | The SEC alleged Windy entered a BXY market-making agreement with Peterson and related entities.            | Liquidity-provider role required dealer and conflict review.              |
| February 2020       | The complaint summary said Murphy and Abbott oversaw review and removal of certain crypto assets.          | Listing review needed documented securities-risk controls.                |
| May 2020            | The SEC alleged a similar market-making agreement was entered for another crypto asset security.           | Market-making expanded beyond BXY into another token.                     |
| September 2020      | The complaint summary said Murphy and Abbott oversaw resumption of trading of various crypto assets.       | Removal and relisting decisions required evidence-based control records.  |
| March 29, 2023      | The SEC announced charges and consents; settling parties agreed to cease activities and shut the platform. | Shutdown and accounting obligations made custody reconciliation critical. |
| April 3, 2023       | The SEC published the litigation release.                                                                  | Public enforcement summary documented the platform-function allegations.  |

## Reconciliation Metrics

| Metric                   | SEC allegation or settlement figure                                                                           | Market-health interpretation                                               |
| ------------------------ | ------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Platform role            | Web-based trading platform for crypto assets alleged to be securities                                         | Order interaction required exchange-function controls.                     |
| Clearing role            | Intermediated payments and deliveries and maintained customer assets                                          | Custody and settlement required ledger and wallet reconciliation.          |
| Broker role              | Effected transactions for the account of others                                                               | Customer-facing execution required broker controls and records.            |
| BXY market-making start  | December 2019                                                                                                 | Liquidity-provider role required conflict and dealer review.               |
| Additional market making | May 2020 agreement for another crypto asset security                                                          | Dealer activity extended beyond BXY.                                       |
| Windy remedy             | $10,779 disgorgement plus prejudgment interest and civil penalties with Murphy and Abbott                     | Monetary remedy accompanied shutdown and accounting undertakings.          |
| Braverock remedy         | $52,000 disgorgement plus prejudgment interest and $80,000 penalty                                            | Market-maker defendants faced dealer-related remedies.                     |
| Legal posture            | Settled as to several defendants without admissions or denials; litigated as to Hamazaspyan and Beaxy Digital | Article should separate settled allegations from ongoing litigated claims. |

## Detection Checklist

1. Map platform functions: order matching, custody, clearing, brokerage, listing review, and market making.
2. Reconcile customer balances to wallets, bank accounts, withdrawal records, and post-shutdown transfer obligations.
3. Review market-maker agreements for assets covered, fees, inventory, account control, algorithmic activity, and conflict disclosures.
4. Compare listing reviews, delistings, and relistings against documented securities and risk analyses.
5. Test whether market-maker liquidity could distort apparent depth, spreads, or token demand.
6. Preserve legal posture: this article relies on SEC allegations, settlements without admissions or denials, and remaining litigated claims as described by the SEC.

## Market-Health Lessons

Beaxy shows why platform-function mapping is a market-health exercise. A trading screen can hide combined order-matching, custody, brokerage, clearing, and market-making roles that would normally be separated or independently supervised.

The case also shows why market-maker arrangements should be visible and auditable. Liquidity can be helpful, but undisclosed or unregistered principal trading can distort what users infer from spreads, depth, and token activity.

## References

- [SEC press release, Beaxy, March 29, 2023](https://www.sec.gov/newsroom/press-releases/2023-64)
- [SEC litigation release, Beaxy Digital, April 3, 2023](https://www.sec.gov/enforcement-litigation/litigation-releases/lr-25687)
- [SEC complaint, SEC v. Beaxy Digital, Ltd., et al.](https://www.sec.gov/file/sec-complaint-2484)
