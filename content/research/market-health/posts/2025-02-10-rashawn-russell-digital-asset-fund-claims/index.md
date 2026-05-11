---
title: "Rashawn Russell Digital Asset Fund Withdrawal Claims"
date: 2025-02-10
entities:
  - Rashawn Russell
  - Bitcoin
  - Ether
  - USDC
---

## Summary

This case study analyzes the Rashawn Russell digital asset trading fund as a market-health warning about small, relationship-driven funds that promise no losses, minimum returns, and stablecoin withdrawals without matching trading or liquidity records. On February 10, 2025, the CFTC announced that the U.S. District Court for the Eastern District of New York entered an order against Rashawn Russell requiring more than $1.5 million in restitution to defrauded victims.

The order resolved the CFTC's April 2023 action charging Russell with fraudulent solicitation and misappropriation of investor assets obtained for the purported purpose of trading digital assets on behalf of customers. The CFTC said the order found Russell solicited more than two dozen retail customers to contribute bitcoin, ether, and fiat currency to a purported proprietary digital assets trading fund, made false statements about the fund's structure, size, and performance, failed to trade assets as represented, and falsely promised withdrawal payments.

For market-health review, Russell is useful because the false signal was not a large public exchange or dashboard. It was a fund story built around trust, guaranteed loss protection, minimum returns, and withdrawal promises, including promises to pay investors in USDC. That makes the key controls custody, trade evidence, liquidity, and redemption funding.

The supporting dataset is available in [rashawn-russell-summary.csv](rashawn-russell-summary.csv).

## Trading Narrative

The CFTC's April 2023 release said Russell solicited retail investors from approximately November 2020 through July 2022 to contribute bitcoin, ether, and fiat currency to a proprietary digital asset trading fund. Russell allegedly guaranteed no losses and, in some instances, promised a minimum 25 percent return on investment.

The February 2025 release said the final order found the scheme continued through August 2022 and involved more than two dozen retail customers. The order found Russell made false or misleading statements about the fund's structure, size, and performance, failed to trade the money and assets as represented, and falsely promised to pay withdrawal requests.

Withdrawal claims were part of the market-health signal. The April 2023 release said Russell falsely promised investors he would pay them in USDC. A stablecoin redemption promise can create the appearance of liquidity even when the fund lacks liquid assets. Reviewers should require wallet balances, bank balances, trade records, and redemption queues before accepting any payout promise.

The misappropriation pattern completed the control failure. The CFTC said Russell used customer assets for personal expenses, entities associated with gambling activities, and Ponzi-like payments to current customers. Those categories mean apparent withdrawals may be funded by incoming assets rather than investment gains.

## False Market Signals

### No-loss guarantee

A no-loss guarantee is incompatible with volatile digital asset trading unless backed by external insurance, collateral, or a funded guarantee account. Reviewers should require proof of that backstop.

### Minimum return promise

A minimum 25 percent return needs realized trade support and loss history. Otherwise it is a solicitation promise, not a market result.

### Proprietary fund framing

Proprietary strategy language can hide basic facts. Reviewers should identify accounts, custodians, counterparties, strategy scope, and participant allocation rules.

### USDC withdrawal promise

A stablecoin withdrawal promise should be tested against actual stablecoin reserves, wallet control, redemption queues, and fiat off-ramp capacity.

### Gambling-related asset use

Transfers to gambling-related entities are inconsistent with digital asset fund management. They require tracing against investor deposits and authorized expenses.

### Ponzi-like customer payments

Payments to existing customers can appear as fund liquidity. Reviewers should test whether those payments came from investment returns or later customer assets.

## Event Timeline

| Date or period     | Event                                                                                          | Market-health signal                                           |
| ------------------ | ---------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| November 2020      | Relevant solicitation period began, according to the final CFTC release.                       | Fund records needed reconstruction from first investor assets. |
| 2020-August 2022   | Russell solicited bitcoin, ether, and fiat currency for a purported proprietary trading fund.  | Multi-asset custody needed wallet, bank, and trade records.    |
| 2020-August 2022   | Russell allegedly guaranteed no losses and in some cases a minimum 25 percent return.          | Guaranteed return claims needed collateral or P&L evidence.    |
| July-August 2022   | CFTC releases describe the solicitation period ending around mid-2022.                         | Ending period required final redemption and asset accounting.  |
| April 6, 2023      | Criminal indictment was returned under seal, according to the CFTC.                            | Parallel criminal case began before public civil announcement. |
| April 11, 2023     | CFTC filed and announced its civil complaint.                                                  | Public enforcement challenged fund structure and withdrawals.  |
| September 19, 2023 | Russell pleaded guilty to wire fraud and unrelated access-device fraud, according to the CFTC. | Criminal admission strengthened loss and intent record.        |
| February 10, 2025  | CFTC announced final order requiring over $1.5 million restitution.                            | Final civil order fixed customer-redress obligation.           |

## Reconciliation Metrics

| Metric                    | Enforcement-record figure or claim                           | Market-health interpretation                                    |
| ------------------------- | ------------------------------------------------------------ | --------------------------------------------------------------- |
| Customer count            | More than two dozen retail customers                         | Small funds still require customer-level ledgers.               |
| Misappropriation amount   | More than $1.5 million in customer assets                    | Asset tracing needed wallets, banks, and personal accounts.     |
| Civil restitution         | More than $1.5 million                                       | Final order quantified customer redress.                        |
| Criminal restitution      | More than $1.5 million                                       | Parallel criminal restitution aligned with civil loss scale.    |
| Promised return           | Minimum 25 percent return in some instances                  | Minimum return required realized P&L or collateral support.     |
| Loss guarantee            | No losses guaranteed, according to CFTC allegations          | Loss protection needed an external backstop.                    |
| Claimed assets accepted   | Bitcoin, ether, and fiat currency                            | Multi-asset intake required custody and conversion records.     |
| Stablecoin payout promise | USDC withdrawal promises described in CFTC's 2023 release    | Stablecoin payouts required wallet reserves and redemption log. |
| Misuse categories         | Personal expenses, gambling-related entities, Ponzi payments | Fund-use categories contradicted trading-fund purpose.          |
| Trading record finding    | Failed to trade money and assets as represented              | Missing trading broke the performance narrative.                |

## Detection Checklist

1. Require wallet, bank, and trade-account records before accepting any proprietary digital asset fund claim.
2. Test no-loss and minimum-return promises against collateral, insurance, or realized trading performance.
3. Reconcile every withdrawal promise to liquid reserves and a dated redemption queue.
4. Verify stablecoin payout capacity through on-chain balances and wallet-control evidence.
5. Trace transfers to gambling-related entities or personal expenses against customer deposits.
6. Test customer payments against incoming customer assets to identify circular funding.
7. Track criminal and civil actions together because restitution figures can align or diverge.
8. Preserve legal posture: this article relies on CFTC order findings, CFTC release language, and public criminal-case summaries.

## Market-Health Lessons

Russell shows that small funds can produce the same false market signals as larger platforms. A fund does not need a public dashboard to misstate performance; emails, conversations, fund descriptions, and withdrawal promises can create the same trust problem.

The case also shows why stablecoin payout promises require proof. USDC can sound liquid and precise, but a promise to pay in stablecoins is only credible if the fund controls the assets and has a traceable redemption process.

Finally, no-loss language should trigger immediate escalation. Digital asset trading involves volatility, custody risk, counterparty risk, and operational risk. If a fund says losses cannot occur, the reviewer should look first for the backstop and then for the trades.

## References

- [CFTC press release 9050-25, February 10, 2025](https://www.cftc.gov/PressRoom/PressReleases/9050-25)
- [CFTC press release 8686-23, April 11, 2023](https://www.cftc.gov/PressRoom/PressReleases/8686-23)
- [CFTC complaint against Rashawn Russell, April 11, 2023](https://www.cftc.gov/media/8366/enfrashawnrussellcomplaint041123/download)
- [CFTC consent order against Rashawn Russell, February 4, 2025](https://www.cftc.gov/media/11791/enfrashawnrussellconsentorder020425/download)
