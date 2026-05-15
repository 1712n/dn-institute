---
title: "Platypus USP Solvency Check Manipulation"
date: "2023-02-16"
description: "Platypus Finance's USP exploit shows how a stablecoin market can lose its peg when flash-loan-sized collateral, borrow capacity, and a stale solvency check are combined in one transaction path."
entities:
  - Platypus Finance
  - USP
  - Avalanche
  - USDC
  - Stablecoins
  - Lending Markets
---

## Summary

Platypus Finance's USP stablecoin lost its dollar peg on February 16, 2023 after an attacker used flash-loan liquidity to exploit the protocol's collateral and solvency accounting. The incident is already documented in the Distributed Networks Institute Cyberattacks section as an $8.5 million flash-loan attack, but it is also a useful Market Health case because the visible damage was not only a smart-contract loss. The protocol's native stablecoin suddenly became undercollateralized, the market repriced USP far below one dollar, and users had to evaluate whether the peg could be restored after collateral was drained.

Public analyses from DN Institute, CertiK, Immunefi, and Halborn describe the same market shape: the attacker temporarily supplied large liquidity, borrowed USP against that position, then used an emergency-withdraw path whose solvency check did not fully account for the debt state before collateral accounting was changed. The result was a market that looked solvent at a dangerous point in the transaction path and insolvent once the operation completed.

For market-health monitoring, Platypus matters because a pegged asset can break without a normal external oracle failure. The manipulated variable was the protocol's own debt and collateral state. A stablecoin monitor that only watches spot price would catch the failure after the peg had already moved. A stronger monitor would also watch the transaction-level relationship between flash-loan collateral, USP minting or borrowing, debt updates, and collateral withdrawal.

## Market Structure

USP was designed as a protocol stablecoin backed by assets deposited into Platypus Finance. In normal operation, the market needed three accounting assumptions to remain true:

- collateral credited to a user had to represent real withdrawable backing;
- debt created through USP borrowing had to reduce the same user's solvency;
- withdrawals had to be blocked when they would leave the user or the pool undercollateralized.

The exploit showed that these assumptions could be separated during one transaction. Flash-loan liquidity provided temporary scale, the borrow step created a large USP debt, and the emergency withdrawal logic allowed collateral to leave before the final state reflected a safe position. This made the market-health problem different from a simple price manipulation case. The attacker did not need to push an exchange price upward long enough to fool an oracle. They needed the protocol to accept a transient accounting state as solvent.

## Signal 1: Flash-Loan Collateral Dominance

The first warning signal is the amount of collateral that enters a pool within a single transaction bundle relative to normal pool depth:

```text
flash_loan_collateral_dominance =
  transaction_supplied_collateral / organic_collateral_depth_before_transaction
```

When this ratio is high, the protocol's risk state can be dominated by liquidity that has no long-term economic commitment. Flash-loan collateral is not automatically malicious, but a market-health system should treat it as adversarial when it is followed by immediate borrowing and withdrawal operations.

In the Platypus case, the collateral path mattered because temporary liquidity created the scale for the USP debt and the subsequent collateral withdrawal. If a stablecoin system allows borrowed stablecoins and collateral exits in the same atomic flow, this dominance ratio becomes a leading indicator of peg risk.

## Signal 2: Borrowed Stablecoin to Credited Collateral

A second signal compares the stablecoin debt created in a transaction with the collateral that is still safely locked after the transaction settles:

```text
borrowed_stablecoin_to_locked_collateral =
  stablecoins_borrowed_or_minted / collateral_remaining_after_withdrawals
```

For a healthy overcollateralized stablecoin, this ratio should stay below the protocol's collateral factor after all balance updates are applied. A ratio that is only safe before an emergency withdrawal, but unsafe afterward, indicates that solvency is being checked at the wrong point in the state transition.

This is the core Market Health lesson from Platypus. Peg stability depends on final-state solvency, not intermediate-state solvency. If a monitor can replay the transaction and compare pre-withdrawal and post-withdrawal debt coverage, it can flag the same pattern even before the spot market fully reprices the stablecoin.

## Signal 3: Emergency-Withdrawal Debt Gap

Emergency withdrawal functions are often introduced as safety valves, but they can become market-health hazards when they bypass the ordinary accounting path. A useful signal is:

```text
emergency_withdrawal_debt_gap =
  debt_before_emergency_withdrawal - debt_considered_by_withdrawal_check
```

The expected value is zero. Any positive gap means the withdrawal gate is evaluating a weaker debt state than the market actually has. In Platypus, the exploitable condition was not simply that an emergency function existed. The dangerous part was that the withdrawal and solvency sequence let collateral accounting and debt accounting fall out of sync.

Stablecoin systems should alert on emergency-withdrawal usage when it is paired with fresh borrowing, flash-loan funding, or large same-block collateral changes. That combination indicates that the emergency path is being used as part of a capital-efficiency attack, not as a normal user rescue route.

## Signal 4: Peg Repricing Shock

The market confirmed the accounting failure when USP traded well below its intended one-dollar peg. A market-health monitor can measure this as:

```text
peg_repricing_shock =
  abs(secondary_market_price - target_price) / target_price
```

The peg shock is a lagging signal, but it is still important because it measures user-facing harm. After collateral is drained, the market must price a new probability distribution: how much can be recovered, how quickly can redemptions resume, whether protocol liabilities are honored, and whether liquidity providers will keep supporting the asset.

In this sense, the spot-market depeg was not the attack mechanism. It was the market's verdict on the backing shortfall. That distinction is useful for detection: the cause appears in protocol state, while the confirmation appears in trading venues and liquidity pools.

## Signal 5: Recovery Coverage Ratio

Recovery announcements can improve confidence, but they should be measured against the total shortfall:

```text
recovery_coverage_ratio =
  assets_recovered_or_frozen / estimated_gross_loss
```

A partial recovery can reduce final losses without fully restoring peg confidence. Market-health dashboards should avoid treating a recovery headline as equivalent to restored solvency. For a stablecoin, the relevant question is whether recovered assets and remaining reserves cover outstanding liabilities at par.

Platypus reportedly recovered part of the affected funds, but the market-health concern persisted because USP holders still needed clarity on collateral coverage, redemptions, and protocol restart conditions. Recovery coverage should therefore be paired with price, liquidity, and redemption-status signals.

## Counterfactual Stress Test

A pre-launch or continuous risk test for a protocol-backed stablecoin should simulate atomic borrow-and-withdraw flows:

| Scenario                    | Assumption                                                   | Market-health response                                          |
| --------------------------- | ------------------------------------------------------------ | --------------------------------------------------------------- |
| Normal borrow               | Debt and collateral update in the same final-state check     | Allow operation and record ordinary utilization                 |
| Flash-loan collateral spike | Same-block collateral dominates organic pool depth           | Require stricter borrow caps and transaction-level simulation   |
| Emergency withdrawal path   | Withdrawal bypasses the normal repay or debt-update sequence | Block withdrawal unless post-withdrawal solvency is proven      |
| Peg repricing               | Secondary markets move materially below the target price     | Freeze risky borrow paths and publish reserve/redemption status |
| Partial recovery            | Some stolen funds are recovered or frozen                    | Recompute coverage before describing the stablecoin as restored |

This stress test does not depend on knowing the attacker in advance. It asks whether any user can enter with temporary capital, create debt, leave with collateral, and force the stablecoin market to absorb the uncovered liability.

## Detection Table

| Signal                            | What changed                                                   | Why it mattered                                                 |
| --------------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------- |
| Flash-loan collateral dominance   | Temporary liquidity controlled the transaction's risk state    | Short-lived capital could create a large stablecoin liability   |
| Borrowed stablecoin to collateral | USP debt was created against collateral that did not stay safe | Final-state backing was weaker than the borrowing step implied  |
| Emergency-withdrawal debt gap     | The safety path evaluated an incomplete debt state             | A rescue function became part of the extraction path            |
| Peg repricing shock               | USP traded materially below its one-dollar target              | The market priced the stablecoin as undercollateralized         |
| Recovery coverage ratio           | Partial fund recovery had to be compared with total losses     | Confidence depended on full coverage, not only recovered assets |

## Practical Alert Rules

1. Treat same-transaction flash-loan deposits, stablecoin borrowing, and collateral withdrawals as a single risk bundle.
2. Require solvency checks to evaluate the final state after all debt and collateral updates.
3. Alert when an emergency-withdrawal function is called by an account that borrowed or minted stablecoins in the same transaction.
4. Compare stablecoin debt to collateral remaining after the withdrawal, not collateral credited before the withdrawal.
5. Escalate when a protocol-backed stablecoin depegs and the root cause is internal accounting rather than external exchange liquidity.
6. Track recovered funds as a coverage ratio against outstanding liabilities before marking peg risk as resolved.

## Lessons for Market Health

Platypus shows that stablecoin market health is partly an accounting-sequence problem. A protocol can have a target price, a collateral pool, and a visible borrow interface, yet still create a market-wide peg shock if one function checks solvency against the wrong state. The attack path converted a contract-ordering issue into a market repricing event.

The broader lesson is that market-health tooling should monitor protocol state transitions, not only market prices. Pegged assets depend on the credibility of backing. If transaction-level accounting allows debt to remain while collateral leaves, the peg can fail before ordinary price feeds, liquidity charts, or exchange order books give a useful early warning.

## Sources

- [Distributed Networks Institute: Flash Loan Attack on Platypus Finance Results in an $8.5 Million Loss](https://dn.institute/research/cyberattacks/incidents/2023-02-16-platypus/)
- [CertiK: Platypus Finance Incident Analysis](https://www.certik.com/blog/platypus-finance-incident-analysis)
- [Immunefi: Hack Analysis - Platypus Finance, February 2023](https://immunefi.com/blog/industry-trends/platypus-finance-hack-analysis/)
- [Halborn: Explained - The Platypus Finance Hack, February 2023](https://www.halborn.com/blog/post/explained-the-platypus-finance-hack-february-2023)
