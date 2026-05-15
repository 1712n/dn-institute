---
title: "Finblox 3AC Exposure and Withdrawal-Limit Liquidity Shock"
date: "2022-06-16"
description: "Finblox's June 2022 withdrawal-limit response to Three Arrows Capital uncertainty shows how investor exposure, reward pauses, and staged limit restoration can reveal yield-app liquidity stress before a full platform failure."
entities:
  - Finblox
  - Three Arrows Capital
  - 3AC
  - Yield Products
  - Crypto Credit Markets
---

## Summary

Finblox restricted withdrawals in June 2022 after uncertainty around Three Arrows Capital. The Crypto Times reported that Finblox lowered withdrawal access to $1,500 per month and paused reward distributions while assessing the effect of 3AC's liquidity crisis. Slashdot's contemporaneous coverage described the same $1,500 monthly withdrawal limit and the platform's decision to pause reward distributions and new address creation.

This is a Market Health case because Finblox did not present itself as a failed exchange or insolvent lender at the first signal. Instead, the risk appeared as a yield-app control layer: lower withdrawal limits, paused rewards, disabled account actions, and later staged limit increases after an exposure assessment. BitPinas and ForkLog later reported that Finblox raised withdrawal limits, while Blockchain.News reported that Finblox explored a legal path against 3AC.

For monitoring, Finblox is useful because it shows a middle state between normal liquidity and a total freeze. Customer balances remained partially accessible, but only at a rate defined by the platform's counterparty-risk response. That makes withdrawal-limit severity and restoration pace important market-health metrics.

## Market Structure

Finblox offered yield-oriented crypto accounts. Users expected deposit convenience, ongoing rewards, and withdrawal access, but those promises depended on Finblox's counterparties and risk controls. Three Arrows Capital's stress created a confidence problem even before customers could observe final losses.

The risk chain had five layers:

- exposure to a distressed investor or counterparty raised platform-risk questions;
- monthly withdrawal access was reduced to a small fixed cap;
- reward distributions and certain account actions were paused;
- Finblox reviewed exposure and then restored limits in stages;
- potential legal recovery against 3AC became part of the risk narrative.

Each layer changed the meaning of a Finblox balance from immediately liquid yield inventory toward managed, platform-controlled liquidity.

## Signal 1: Monthly Withdrawal Cap Severity

The first signal is the size of the imposed cap relative to user balances:

```text
monthly_withdrawal_cap_severity =
  1 - monthly_withdrawal_limit / customer_balance
```

The Crypto Times and Slashdot reported a $1,500 monthly withdrawal limit. For users with balances above that amount, practical liquidity fell sharply even though withdrawals were not fully disabled. This is a severe market-health signal because it slows exits and makes customer access dependent on platform policy rather than user demand.

## Signal 2: Reward Distribution Pause

Finblox also paused reward distributions:

```text
reward_distribution_pause =
  rewards_paused and yield_promises_under_review
```

A reward pause can signal that the yield engine is no longer operating normally. In a credit-stress environment, this should be monitored alongside withdrawal limits because both point to the platform preserving liquidity while reassessing exposures.

## Signal 3: Account-Action Restriction

Slashdot reported that Finblox paused new address creation as part of the same restriction package:

```text
account_action_restriction =
  restricted_account_actions / total_core_account_actions
```

This signal matters because user access is not just withdrawals. If a platform restricts supporting actions such as address creation, new account onboarding, or reward claiming, the product is moving into a defensive operating mode.

## Signal 4: Staged Limit Restoration

BitPinas and ForkLog reported that Finblox raised withdrawal limits after assessing its exposure:

```text
staged_limit_restoration =
  restored_withdrawal_limit / pre_stress_withdrawal_limit
```

Staged restoration is useful but not the same as full liquidity. It shows that the platform is trying to move back toward normal access, while still managing risk through controlled caps.

## Signal 5: Counterparty Recovery Optionality

Blockchain.News reported that Finblox explored legal action against 3AC:

```text
counterparty_recovery_optionality =
  expected_recovery_from_3ac_or_legal_action / exposed_assets
```

Recovery optionality is uncertain until assets are actually recovered. A market-health system should treat legal action or counterparty recovery as a discountable variable, not as immediate liquidity.

## Counterfactual Stress Test

A yield app can be stress-tested by measuring how it reacts to counterparty uncertainty:

| Scenario                 | Assumption                                      | Market-health response                                    |
| ------------------------ | ----------------------------------------------- | --------------------------------------------------------- |
| Normal yield operation   | Withdrawals and rewards operate normally        | Monitor withdrawal latency and reward consistency         |
| Counterparty uncertainty | A major investor or borrower faces distress     | Flag platform exposure and liquidity preservation actions |
| Withdrawal cap           | Monthly withdrawals are capped                  | Treat balances above the cap as slowed liquidity          |
| Reward pause             | Rewards stop during exposure assessment         | Mark yield product as impaired until restored             |
| Staged restoration       | Limits increase gradually                       | Track restoration pace and remaining access constraints   |
| Legal recovery path      | Recovery depends on claims against counterparty | Discount recovery until distributions are proven          |

The test asks whether the user can exit at economically meaningful size while the platform assesses counterparty losses. If not, the account should be treated as impaired liquidity even if withdrawals technically remain open.

## Detection Table

| Signal                            | What changed                                    | Why it mattered                                                    |
| --------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------ |
| Monthly withdrawal cap severity   | Withdrawals were reduced to a fixed monthly cap | Users with larger balances lost practical exit capacity            |
| Reward distribution pause         | Yield payouts paused                            | The platform's yield engine was under stress review                |
| Account-action restriction        | New address creation and related actions paused | Defensive controls spread beyond withdrawals                       |
| Staged limit restoration          | Withdrawal limits later increased               | Liquidity returned gradually rather than immediately               |
| Counterparty recovery optionality | Legal recovery against 3AC became relevant      | Customer access depended partly on uncertain counterparty recovery |

## Practical Alert Rules

1. Treat withdrawal caps as liquidity impairment even when withdrawals remain technically enabled.
2. Monitor reward pauses and withdrawal caps together for yield products.
3. Track account-action restrictions as evidence of defensive operating mode.
4. Measure limit restoration as a timeline, not a binary recovery.
5. Separate counterparty recovery plans from customer-access restoration.
6. Escalate yield-app risk when a distressed investor or borrower is named in platform communications.

## Lessons for Market Health

Finblox shows that market-health deterioration can appear as a cap rather than a collapse. Users may still be able to withdraw something, but the product has stopped offering normal liquidity.

The broader lesson is that yield apps should be monitored by withdrawal-limit severity, reward continuity, account-action availability, and recovery optionality. These signals can reveal credit-market contagion before a platform reaches a total freeze or formal restructuring.

## Sources

- [The Crypto Times: Finblox Enforces Withdrawal Limit Over 3AC Liquidation Crisis](https://www.cryptotimes.io/2022/06/17/finblox-enforces-withdrawal-limit-over-3ac-liquidation-crisis/)
- [Slashdot: Finblox Imposes $1.5K Monthly Withdrawal Limit Amid Three Arrows Capital Uncertainty](https://tech.slashdot.org/story/22/06/16/1639250/finblox-imposes-15k-monthly-withdrawal-limit-amid-three-arrows-capital-uncertainty?sdsrc=prev)
- [BitPinas: Finblox Raises Withdrawal Limits Following 3AC Assessment](https://bitpinas.com/news/finblox-raises-withdrawal-limits-3ac/)
- [ForkLog: Finblox raises withdrawal limit amid 3AC troubles](https://forklog.com/en/finblox-raises-withdrawal-limit-amid-3ac-troubles/)
- [Blockchain.News: Finblox Raises Withdrawal Limit, Exploring Lawsuit Against 3AC](https://blockchain.news/news/finblox-raises-withdrawal-limitexploring-lawsuit-against-3ac)
- [ARK Invest: Bitcoin Monthly June 2022](https://assets.arkinvest.com/media-8e522a83-1b23-4d58-a202-792712f8d2d3/04321671-37bd-4c0a-960b-3a2db5596890/ARK-Invest_070122_Bitcoin-Monthly_June-22.pdf)
