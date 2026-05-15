---
title: "SALT FTX-Exposure Withdrawal Pause and Loan-Collateral Liquidity Risk"
date: "2022-11-15"
description: "SALT's 2022 pause of deposits and withdrawals after the FTX collapse shows how crypto-backed lending collateral can become operationally trapped when a lender faces counterparty exposure, regulatory intervention, and payoff-friction risk."
entities:
  - SALT Lending
  - SALT
  - FTX
  - Crypto Lending
  - California DFPI
  - Collateralized Loans
---

## Summary

SALT paused platform deposits and withdrawals in November 2022 after the FTX collapse affected its business. Bitcoin.com reported that SALT Lending cited exposure to FTX and paused withdrawals and deposits. A later SALT notice to California residents stated that January 2025 license reinstatement followed a settlement with the California Department of Financial Protection and Innovation, and it explicitly referenced November 15, 2022 as the date SALT paused platform withdrawals.

This is a Market Health case because SALT was a crypto-backed lending platform, not only a spot exchange. Customer assets could be tied to active loans, payoff flows, collateral return, platform monitoring systems, and regulatory license status. When deposits and withdrawals stopped, users faced both liquidity impairment and loan-collateral process risk.

For monitoring, SALT shows how FTX contagion spread through lending relationships even outside the exchange itself. A platform can keep loans active while simultaneously limiting customer movement of assets, creating a mismatch between ongoing obligations and impaired access.

## Market Structure

SALT offered crypto-backed loans, where customers could borrow against digital-asset collateral. That structure created a different risk profile from a normal trading venue:

- collateral could remain tied to an active loan;
- payoff or closeout steps could be needed before collateral return;
- deposits and withdrawals could be paused at the platform level;
- regulatory action could restrict the lender's operating status;
- customers could face uncertainty about the extent of FTX-related exposure.

The result was a collateral-liquidity event. Users needed more than asset prices to evaluate risk; they needed to know whether the lending platform could process repayments, release collateral, and maintain regulatory access.

## Signal 1: Deposits and Withdrawals Paused

The first signal is the platform activity halt:

```text
lending_platform_transfer_halt =
  paused_deposit_and_withdrawal_functions / total_customer_transfer_functions
```

Bitcoin.com reported that SALT paused withdrawals and deposits after citing exposure to FTX. This matters because a lender can continue to monitor loans while blocking customers from freely moving collateral or account assets.

## Signal 2: Counterparty-Exposure Uncertainty

SALT's reported message cited the impact of FTX but did not give customers a precise exposure amount:

```text
counterparty_exposure_uncertainty =
  undisclosed_ftx_exposure_amount / customer_collateral_at_risk
```

This is a market-health signal because uncertainty itself can impair liquidity. If users cannot quantify the lender's FTX exposure, they cannot know whether a withdrawal pause is temporary operational caution or a solvency problem.

## Signal 3: Active-Loan Collateral Friction

SALT's later California notice addressed active loan payoff and collateral-return terms for affected residents:

```text
active_loan_collateral_friction =
  loans_requiring_payoff_before_collateral_return / total_active_customer_loans
```

Collateral inside a lending platform is not equivalent to an exchange wallet balance. Customers may need to pay off loans, satisfy platform conditions, and pass operational processing before collateral can be returned.

## Signal 4: Regulatory License Suspension

The California DFPI suspended SALT Lending's financing license pending investigation after the withdrawal pause:

```text
regulatory_license_suspension =
  suspended_lending_permissions / active_jurisdictional_permissions
```

Regulatory action can extend customer uncertainty beyond the initial market shock. Even if the platform intends to resume normal service, license status and settlement terms can influence when and how customers recover access.

## Signal 5: Contagion Timing

SALT's pause arrived shortly after the FTX failure and alongside other platform withdrawal pauses:

```text
ftx_contagion_timing =
  platform_pauses_within_ftx_failure_window / monitored_crypto_lending_platforms
```

Bitfinex's market commentary and Bitcoin.com both placed SALT in the broader FTX-contagion withdrawal-pause cluster. For monitoring systems, clusters matter because one exchange failure can trigger liquidity shocks across lenders, custodians, and acquisition counterparties.

## Counterfactual Stress Test

A crypto-backed lender can be stress-tested by tracing whether collateral can be returned during a counterparty shock:

| Scenario                     | Assumption                                     | Market-health response                                |
| ---------------------------- | ---------------------------------------------- | ----------------------------------------------------- |
| Normal lending operation     | Customer can repay and receive collateral      | Monitor collateral value and loan-to-value ratio      |
| Counterparty exposure event  | Lender reports exposure to a failed exchange   | Track exposure disclosure and platform communications |
| Transfer halt                | Deposits and withdrawals pause                 | Reclassify collateral as platform-gated liquidity     |
| Active-loan payoff friction  | Collateral return depends on payoff processing | Track payoff window, fees, and return mechanics       |
| Regulatory suspension        | Lending license is suspended pending review    | Track jurisdictional operating status and settlement  |
| Contagion cluster escalation | Multiple lenders pause around the same trigger | Raise systemic lender-liquidity risk                  |

The test asks whether customer collateral can be recovered through normal loan-closeout rails. If access depends on platform discretion, exposure disclosure, or regulator-mediated settlement, it is impaired liquidity.

## Detection Table

| Signal                            | What changed                                       | Why it mattered                                          |
| --------------------------------- | -------------------------------------------------- | -------------------------------------------------------- |
| Deposits and withdrawals paused   | Customer transfer functions stopped                | Collateral and account liquidity became platform-gated   |
| Counterparty-exposure uncertainty | FTX impact was cited without precise exposure data | Users could not quantify solvency or timing risk         |
| Active-loan collateral friction   | Collateral return depended on loan payoff process  | Borrowers had ongoing obligations despite limited access |
| Regulatory license suspension     | California license was suspended pending review    | Legal operating status became part of recovery risk      |
| Contagion timing                  | Pause occurred during the FTX failure window       | One exchange collapse propagated into lending access     |

## Practical Alert Rules

1. Treat lender deposit and withdrawal pauses as collateral-liquidity events, not just exchange outages.
2. Track whether loans remain active while customer transfer functions are suspended.
3. Escalate risk when a lender cites counterparty exposure without quantifying it.
4. Monitor payoff, fee, and collateral-return terms after a platform pause.
5. Treat regulator license suspensions as customer-access risk signals.
6. Watch for correlated withdrawal pauses across lenders after a large exchange failure.

## Lessons for Market Health

SALT shows that crypto-backed lending creates a two-sided liquidity problem during contagion. Borrowers may still owe money and need to manage collateral, while the platform may restrict deposits, withdrawals, or payoff paths because of its own counterparty exposure.

The broader lesson is that market-health monitoring should separate exchange withdrawals, lender collateral return, and loan-servicing continuity. A platform can appear operational in one dimension while customers are still unable to regain practical control of their assets.

## Sources

- [Bitcoin.com: Liquid Global and Salt Lending Pause Withdrawals, Citing FTX Exposure](https://news.bitcoin.com/2-more-crypto-platforms-pause-withdrawals-as-liquid-global-and-salt-lending-cite-exposure-to-ftx/)
- [SALT Lending: California DFPI Notice](https://saltlending.com/california-dfpi-notice/)
- [Bitfinex Alpha: Issue 31, November 21 2022](https://blog.bitfinex.com/wp-content/uploads/2022/11/Bitfinex-Alpha-31.pdf)
