---
title: "Liquid Global FTX Withdrawal Halt and Custodial-Group Contagion"
date: "2022-11-15"
description: "Liquid Global's 2022 withdrawal halt shows how exchange customers can lose liquidity through parent-company contagion, Chapter 11 coordination, fiat/crypto rail separation, and staged restart uncertainty."
entities:
  - Liquid Global
  - Liquid
  - FTX
  - FTX Trading
  - Quoine
  - Centralized Exchanges
---

## Summary

Liquid Global suspended fiat and crypto withdrawals in November 2022 after FTX Trading filed for Chapter 11 protection. Liquid's first-party notice said withdrawals were suspended in compliance with the requirements of voluntary Chapter 11 proceedings in the United States. Bitcoin.com reported that Liquid Global, which FTX had acquired earlier in 2022, paused withdrawals after the FTX collapse.

This is a Market Health case because Liquid's customers were affected by parent-company bankruptcy contagion rather than a standalone trading-engine outage. Liquidity became dependent on group-level legal instructions, exchange-rail separation, and the timing of service restarts. Liquid later published separate updates for fiat withdrawals and broader withdrawal reopening.

For monitoring, Liquid is useful because it separates local exchange operations from ownership-group risk. A venue can have its own brand, local user base, and fiat rails while still becoming liquidity-impaired through a parent company's bankruptcy process.

## Market Structure

Liquid was a centralized crypto exchange operated under the broader FTX group after FTX acquired Liquid Group. That made customer access dependent on several layers:

- Liquid's own exchange systems and local operating entities;
- FTX Trading's Chapter 11 process;
- instructions or restrictions affecting group companies;
- separate fiat and crypto withdrawal rails;
- staged service updates after the initial halt.

The risk was not just whether Liquid's order books were functioning. It was whether customers could move assets out while the parent group moved through bankruptcy.

## Signal 1: Parent-Company Bankruptcy Trigger

The first signal is an access halt triggered by parent-company proceedings:

```text
parent_bankruptcy_withdrawal_halt =
  withdrawals_paused_due_to_parent_proceeding / total_withdrawal_functions
```

Liquid's notice tied the suspension to FTX Trading's Chapter 11 proceedings. That is a critical market-health distinction: the customer-facing venue may not be the entity that first failed, but its liquidity can still become legally or operationally gated.

## Signal 2: Fiat and Crypto Rail Suspension

Liquid paused both fiat and crypto withdrawals:

```text
rail_suspension_breadth =
  suspended_fiat_and_crypto_rails / total_customer_exit_rails
```

This matters because customers lose diversification of exits when both banking rails and blockchain rails are paused. A crypto withdrawal halt alone might leave fiat redemption available; a full rail halt leaves customers waiting on platform restart decisions.

## Signal 3: Staged Withdrawal Restart

Liquid later published separate withdrawal updates, including a fiat-withdrawal update and a broader withdrawal update:

```text
staged_withdrawal_restart =
  reopened_withdrawal_rails / previously_suspended_withdrawal_rails
```

Staged restart is a recovery signal, but it is not the same as uninterrupted liquidity. Monitoring should track which asset classes, jurisdictions, and account states are actually able to withdraw.

## Signal 4: Custodial-Group Contagion

Bitcoin.com reported that Liquid Global was FTX-owned and paused withdrawals after the FTX collapse:

```text
custodial_group_contagion =
  subsidiaries_with_withdrawal_halts / subsidiaries_exposed_to_parent_failure
```

Custodial-group contagion can be hard for users to price. A user may choose an exchange based on local brand trust, but ownership and treasury integration can transmit shocks across the group.

## Signal 5: Restart-Communication Lag

Liquid's first notice suspended withdrawals immediately, while later notices addressed updates and resumption mechanics:

```text
restart_communication_lag =
  time_between_halt_notice_and_reopening_update
```

This lag matters because market-health dashboards need to distinguish between a pause, a partial reopening, and full customer recovery. During the lag, balances may exist but fail to function as deployable liquidity.

## Counterfactual Stress Test

An exchange owned by a stressed parent group can be stress-tested by tracing whether customer exits remain independent:

| Scenario                  | Customer exit path                         | Market-health interpretation                           |
| ------------------------- | ------------------------------------------ | ------------------------------------------------------ |
| Normal exchange operation | Fiat and crypto withdrawals are open       | Monitor latency, reserves, and order-book depth        |
| Parent-company bankruptcy | Group process affects local exchange rails | Reclassify access as parent-proceeding dependent       |
| Full rail suspension      | Fiat and crypto withdrawals both pause     | Treat balances as platform-gated liquidity             |
| Staged restart            | Some withdrawal channels reopen first      | Track rail-specific recovery rather than binary status |
| Communication lag         | Halt notice precedes restart details       | Escalate uncertainty until mechanics are published     |

The test asks whether customer funds can exit through at least one independent rail. If both fiat and crypto rails depend on group-level instructions, the exchange balance is no longer normal market liquidity.

## Detection Table

| Signal                            | What changed                                      | Why it mattered                                         |
| --------------------------------- | ------------------------------------------------- | ------------------------------------------------------- |
| Parent-company bankruptcy trigger | FTX Chapter 11 process drove Liquid's halt        | Local exchange access became group-bankruptcy dependent |
| Fiat and crypto rail suspension   | Both withdrawal types were suspended              | Customers lost parallel exit routes                     |
| Staged withdrawal restart         | Later notices updated withdrawal reopening status | Recovery needed rail-by-rail tracking                   |
| Custodial-group contagion         | FTX ownership transmitted stress to Liquid users  | Parent-company risk affected subsidiary customers       |
| Restart-communication lag         | Details arrived after the initial halt            | Customers faced timing and eligibility uncertainty      |

## Practical Alert Rules

1. Map exchange ownership and parent-company bankruptcy exposure.
2. Alert when a subsidiary exchange cites parent-company proceedings in a withdrawal halt.
3. Track fiat and crypto withdrawal rails separately.
4. Treat partial reopening notices as staged recovery, not full resolution.
5. Monitor communication lag between halt notices and restart mechanics.
6. Flag customer balances as impaired liquidity until actual withdrawals resume.

## Lessons for Market Health

Liquid Global shows that exchange liquidity risk can move through corporate ownership, not only through order books, wallets, or local operations. A customer of a subsidiary exchange can become trapped by a parent company's legal and operational crisis.

The broader lesson is that market-health monitoring should include corporate-group dependency. Exchange reserves, withdrawal rails, and legal control can diverge during bankruptcy, making customer access a group-level risk variable.

## Sources

- [Liquid: Important Notice - Suspension of Withdrawals](https://www.liquid.com/announcements/important-notice-suspension-of-withdrawals)
- [Liquid: Update on Withdrawals](https://www.liquid.com/announcements/update-on-withdrawals)
- [Liquid: Update on Fiat Withdrawals](https://www.liquid.com/announcements/update-on-fiat-withdrawals)
- [Bitcoin.com: Liquid Global and Salt Lending Pause Withdrawals, Citing FTX Exposure](https://news.bitcoin.com/2-more-crypto-platforms-pause-withdrawals-as-liquid-global-and-salt-lending-cite-exposure-to-ftx/)
