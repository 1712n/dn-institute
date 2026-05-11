---
title: "Mirror Trading International Bitcoin Pool Trading Claims"
date: 2023-09-07
entities:
  - Mirror Trading International
  - MTI
  - Cornelius Johannes Steynberg
  - Trade300
  - FXChoice
---

## Summary

This case study analyzes Mirror Trading International (MTI) as a market-health warning about off-exchange trading pools that use bitcoin deposits, bot claims, and simulated account statements to create apparent trading performance. On September 7, 2023, the CFTC announced that a federal court entered a consent order against MTI requiring more than $1.7 billion in restitution to defrauded victims. The CFTC said the order found MTI liable for fraud in connection with retail forex transactions, fraud by a commodity pool operator, registration violations, and failure to comply with commodity pool operator regulations.

The CFTC described the case as resolving its largest fraud scheme case involving bitcoin. It also said a prior default judgment against MTI founder and CEO Cornelius Johannes Steynberg required more than $1.7 billion in restitution and more than $1.7 billion in civil monetary penalty.

The market-health problem was the fabricated bridge between deposited bitcoin and purported profitable forex trading. According to the CFTC, MTI and Steynberg solicited bitcoin for an unregistered commodity pool that supposedly traded off-exchange retail forex through proprietary software. The CFTC complaint alleged there was no successful trading bot, no profitable trading, simulated account statements, sham returns, and a fictitious broker called Trade300.

The supporting dataset is available in [mti-summary.csv](mti-summary.csv).

## Trading Narrative

The CFTC complaint said Steynberg and MTI solicited bitcoin from members of the public from approximately May 18, 2018 through March 30, 2021 using MTI websites, member portals, social media, and a multilevel marketing structure. Participants were told they were joining a commodity pool that purportedly traded off-exchange retail forex using a proprietary bot or software program.

The CFTC's 2023 release said Steynberg accepted at least 29,421 bitcoin, valued at more than $1.733 billion at the end of the relevant period, from at least 23,000 individuals in the United States and thousands more worldwide. The CFTC said the defendants misappropriated all of the bitcoin accepted from pool participants, directly or indirectly.

The complaint alleged several market-facing misrepresentations. Steynberg allegedly claimed the trading bot achieved 10 percent monthly profits, that participants' bitcoin was traded in a pooled account, and that the pool had never had a losing trading day except for one. The complaint alleged those representations were false.

The CFTC complaint also described the records problem in detail. It alleged that no profitable forex trading took place on behalf of participants, that account statements were simulated trades from MetaTrader 4 demo accounts, and that Trade300, where MTI supposedly traded participant bitcoin, was a fictitious entity created by Steynberg.

The limited account evidence also contradicted the broader sales story. The complaint alleged that in the only pooled account defendants held, at FXChoice, defendants deposited 1,846 bitcoin and lost 566.6 bitcoin trading unprofitably. It further alleged that 27,574 bitcoin sent by participants was not deposited into the FXChoice pool account.

## False Market Signals

### Proprietary bot claims

The bot claim made MTI look like a technology-driven trading pool rather than a bitcoin solicitation scheme. The practical control is to require trading venue records, executed orders, balances, and realized P&L before accepting bot performance claims.

### Ten-percent monthly profit narrative

The CFTC complaint alleged that MTI claimed 10 percent monthly profits. A stable monthly return claim in leveraged forex trading should trigger a full reconciliation of losses, slippage, fees, margin calls, and account equity. The complaint alleged that no profitable trading took place on behalf of participants.

### Simulated account statements

The complaint alleged that MTI account statements were simulated trades from MT4 demo accounts. This is a market-health signal because a demo-account statement can look like trading evidence while having no connection to customer capital, market risk, or executable liquidity.

### Fictitious broker venue

The complaint alleged Trade300 was a fictitious entity. Venue verification is basic market infrastructure: a trading pool should be able to prove that the named broker exists, holds the account, and can reconcile deposits, trades, balances, and withdrawals.

### Sham returns and bonus payments

The complaint alleged that purported returns and bonus payments were made from participant bitcoin in the nature of a Ponzi scheme. In market-health terms, the source of returns matters as much as their size. Returns funded by later deposits are not trading performance.

## Event Timeline

| Date or period       | Event                                                                               | Market-health signal                                                             |
| -------------------- | ----------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| May 18, 2018 onward  | MTI and Steynberg solicited bitcoin for a commodity pool.                           | Bitcoin deposits were tied to claimed off-exchange forex trading.                |
| 2018 to 2021         | MTI promoted proprietary bot or software trading.                                   | Bot claims required proof from trading venues and executed order records.        |
| 2018 to 2021         | Steynberg accepted at least 29,421 bitcoin from U.S. and global participants.       | The pool scale required strong custody, venue, and P&L reconciliation.           |
| Relevant CFTC period | The CFTC alleged only 1,846 bitcoin reached the FXChoice pool account.              | Deposits into the trading account were far below participant bitcoin inflows.    |
| Relevant CFTC period | The CFTC alleged the FXChoice pool account lost 566.6 bitcoin trading unprofitably. | Actual trading evidence contradicted profitable-bot claims.                      |
| August 7, 2020       | FXChoice froze the pool account for suspected fraud, according to the complaint.    | Broker-side account freeze became an external warning sign.                      |
| March 30, 2021       | The CFTC's relevant period ended.                                                   | Solicitation period closed after years of unregistered pool activity.            |
| June 30, 2022        | The CFTC filed its enforcement action.                                              | Complaint challenged bot, broker, account statement, and return representations. |
| April 24, 2023       | Court entered default judgment against Steynberg, according to the CFTC.            | Judgment required restitution and a civil monetary penalty above $1.7 billion.   |
| September 6, 2023    | Court entered consent order against MTI.                                            | Order found MTI liable for fraud and registration violations.                    |
| September 7, 2023    | The CFTC announced the MTI consent order.                                           | Case resolved with more than $1.7 billion restitution and permanent market bans. |

## Detection Checklist

1. Verify that any named broker or trading venue exists and confirms the account relationship directly.
2. Reconcile participant deposits to broker deposits, account balances, trades, fees, withdrawals, and losses.
3. Treat demo-account statements as non-evidence unless linked to live funded accounts.
4. Require independent records for bot operation, strategy logs, and actual order execution.
5. Compare advertised return stability to real margin, drawdown, and loss history.
6. Trace whether returns and bonuses come from trading gains or from later participant deposits.
7. Check registration status for commodity pool operators and associated persons before accepting pool solicitations.
8. Preserve legal posture: this article relies on CFTC order statements and public CFTC complaint allegations.

## Market-Health Lessons

MTI shows how a trading pool can manufacture market credibility through a stack of false infrastructure signals: a proprietary bot, a named broker, account statements, monthly return claims, and multilevel referral growth. Each signal can appear plausible on its own. The failure mode is that none of them proves that customer capital reached a real trading venue and generated real profits.

The strongest control is reconciliation across independent records. Participant bitcoin inflows should match custody and broker deposits. Broker statements should come from the broker, not a platform dashboard. Trading profits should reconcile to orders and fills. Return payments should trace to realized P&L, not to later deposits. When those links break, displayed trading performance should be treated as promotional content rather than market evidence.

## References

- [CFTC press release 8772-23, September 7, 2023](https://www.cftc.gov/PressRoom/PressReleases/8772-23)
- [CFTC press release 8549-22, June 30, 2022](https://www.cftc.gov/PressRoom/PressReleases/8549-22)
- [CFTC complaint against Mirror Trading International and Steynberg](https://www.cftc.gov/media/7426/enfmirrortradingcomplaint063022/download)
