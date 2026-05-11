---
title: "Technical Trading Team AI Bot Forex Recovery Claims"
date: 2023-10-06
entities:
  - Technical Trading Team LLC
  - TTT
  - Edwin M. Carrion
  - Jason F. Rodriguez
---

## Summary

This case study analyzes Technical Trading Team LLC as a market-health warning about commodity-pool operators that combine fixed-interest promissory notes, leveraged forex exposure, reserve-fund claims, and later artificial-intelligence recovery promises. On October 6, 2023, the CFTC announced a civil complaint against TTT, CEO Edwin Carrion, and COO and head trader Jason Rodriguez. The CFTC said the complaint charged the defendants with fraudulently soliciting more than $5 million for participation in a retail forex commodity pool scheme.

The CFTC alleged that TTT pool participants' investments were structured as loans promising annual interest of 18 percent to 24 percent, paid monthly, with principal returned at maturity. The complaint said defendants exaggerated their forex track record, promised risk controls and collateral, then lost more than $3.13 million trading leveraged retail forex. After defaulting on the notes, they allegedly claimed they could recoup losses and repay participants by creating an AI-managed trading bot.

For market-health review, TTT is useful because the false signal changed over time. Early solicitations emphasized safety, reserves, 1 percent trade risk, no overnight positions, and collateral. After losses, the story shifted to recovery through AI. That sequence shows why reviewers should continuously reconcile risk promises, actual trading exposure, participant cash flows, and any new technology narrative introduced after losses.

The supporting dataset is available in [technical-trading-team-summary.csv](technical-trading-team-summary.csv).

## Trading Narrative

The CFTC complaint said Carrion and Rodriguez solicited non-eligible contract participants to invest in a TTT-operated commodity pool that would trade retail forex on margin. The investments were documented as promissory notes rather than conventional pool subscriptions, but the economic claim was the same: participants supplied capital and expected monthly payments funded by trading.

The promised return profile was fixed and loan-like. Participants were allegedly promised 18 percent to 24 percent annual interest for one year and principal repayment at maturity. TTT allegedly represented that it would maintain a reserve fund equal to the size of participants' contributions, risk no more than 1 percent of pool assets in any trade, avoid overnight positions, and rely on collateral including business and real-estate assets.

The trading record did not support that safety story. The CFTC alleged that from April 2020 through October 2022, defendants lost more than $3.13 million of participant money trading leveraged retail forex. The complaint also alleged misappropriation for personal use and use of new participant funds to make interest payments to existing participants. Those facts turn the fixed-interest note into a market-health red flag: the stated return was not self-liquidating if the trading account was losing money.

The AI-bot story came after the damage. The CFTC release said that after losing millions and defaulting on the purported loans, defendants concealed their activity by claiming they would create a bot using AI to manage trading and recover losses. A technology pivot after losses should be treated as a new risk event unless backed by working code, independently verified backtests, live execution, risk limits, and capital adequacy.

## False Market Signals

### Fixed note yield backed by volatile trading

An 18 percent to 24 percent annual note yield requires a clear repayment source. If the source is leveraged forex trading, reviewers should reconcile the fixed obligation to variable P&L and drawdowns.

### Reserve fund promise

The CFTC complaint alleged participants were told TTT maintained reserves, while TTT did not have a separate reserve fund. A reserve claim should be verified through segregated accounts, balances, ownership, and restrictions on use.

### One percent risk limit

A per-trade risk limit is only useful if matched to trade logs, margin usage, realized losses, position sizing, and stop-loss records.

### No overnight positions

No-overnight-position language suggests daily liquidity. Reviewers should test it against broker statements and open-position records.

### Collateral narrative

The complaint said participants were told TTT had assets such as a trucking company and Miami real estate, while the CFTC alleged TTT did not own those assets. Collateral should be verified with title, liens, appraisals, and borrower ownership.

### AI recovery bot

An AI bot claim made after losses can be a deflection from realized damage. It should be evaluated as a working trading system, not as a promise to make prior investors whole.

## Event Timeline

| Date or period  | Event                                                                                          | Market-health signal                                             |
| --------------- | ---------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| January 2020    | Relevant period began, according to the CFTC complaint.                                        | Pool-solicitation controls should have existed from inception.   |
| April 2020      | TTT was incorporated in Florida, according to the complaint.                                   | Entity formation preceded pool fundraising.                      |
| April 2020-2022 | Defendants allegedly lost more than $3.13 million trading leveraged retail forex.              | Fixed note promises needed ongoing P&L reconciliation.           |
| August 2020     | Complaint describes a first $100,000 promissory note for Participant-1 at 24 percent interest. | Loan structure carried commodity-pool exposure.                  |
| April 2021      | Complaint describes a $250,000 participant wire to TTT.                                        | Wire flows needed segregation from trading and personal use.     |
| October 2022    | TTT allegedly notified some participants it had defaulted on loans.                            | Default exposed mismatch between promised yield and real losses. |
| October 2023    | CFTC announced charges against TTT, Carrion, and Rodriguez.                                    | Public enforcement challenged safety, collateral, and AI claims. |

## Reconciliation Metrics

| Metric                       | Enforcement-record figure or claim                                  | Market-health interpretation                                      |
| ---------------------------- | ------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Solicitation scale           | More than $5 million                                                | Pool size required formal registration and participant ledgers.   |
| Participant count            | Approximately 27 individuals                                        | Concentrated participant base still required account-level proof. |
| Promised annual interest     | 18 percent to 24 percent                                            | Fixed payments needed a stable repayment source.                  |
| Monthly interest range       | 1.5 percent to 2 percent                                            | Monthly obligations needed P&L coverage.                          |
| Trading loss alleged         | More than $3.13 million                                             | Losses undermined fixed-return and principal-repayment promises.  |
| Trade risk representation    | No more than 1 percent of pool assets in any trade                  | Risk limits required order and margin data.                       |
| Overnight position claim     | Positions would not be held overnight                               | Liquidity claims required broker-statement verification.          |
| Reserve fund claim           | Reserve fund equal to participants' contributions                   | Reserve balances needed segregated-account evidence.              |
| Collateral claim             | TTT assets including real estate and a trucking company             | Collateral required title and ownership verification.             |
| New-money payment allegation | New participant funds used to pay interest to existing participants | Payout source may have been fundraising rather than trading.      |
| AI recovery claim            | Bot using AI to manage trading and recover losses after default     | Technology claim needed working system and live execution proof.  |
| Registration status          | TTT, Carrion, and Rodriguez allegedly were not registered with CFTC | Retail forex pool activity required registration analysis.        |

## Detection Checklist

1. Reconcile fixed note interest to realized trading P&L, not projected strategy returns.
2. Verify reserve funds through separate account records, legal restrictions, and current balances.
3. Match risk-limit promises to broker statements, trade logs, margin usage, and liquidation events.
4. Verify collateral ownership, liens, and valuations before treating collateral as principal protection.
5. Trace whether monthly payments came from trading profits or later participant deposits.
6. Treat AI or machine-learning recovery stories after losses as new claims requiring independent proof.
7. Confirm CPO and associated-person registration status before accepting retail forex pool funds.
8. Preserve legal posture: this article relies on CFTC allegations and public CFTC release language.

## Market-Health Lessons

Technical Trading Team shows how a loan wrapper can hide commodity-pool risk. The promise of monthly interest and principal repayment can make participants think they are evaluating credit risk, while the actual repayment source is leveraged forex trading. Market-health review should follow the cash to the trading account.

The case also shows why reserve and collateral claims need hard documentation. A reserve fund is not a talking point; it is a segregated pool of assets with balances and restrictions. Collateral is not meaningful unless the borrower owns it and the investor has enforceable rights.

Finally, technology claims made after losses deserve heightened scrutiny. An AI trading bot cannot repair a missing reserve, trading losses, or defaulted principal unless it exists, trades under controlled risk, and produces verifiable results. The burden is on the operator to prove the new system before investors rely on it.

## References

- [CFTC press release 8803-23, October 6, 2023](https://www.cftc.gov/PressRoom/PressReleases/8803-23)
- [CFTC complaint against Technical Trading Team LLC, Edwin M. Carrion, and Jason F. Rodriguez, September 29, 2023](https://www.cftc.gov/media/9441/enftechnicaltradingteamcomplaint092923/download)
