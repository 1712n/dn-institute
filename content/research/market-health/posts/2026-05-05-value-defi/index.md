---
title: "Value DeFi, Curve share pricing, and the market risk of same-block vault accounting"
date: 2026-05-05
entities:
  - Value DeFi
  - Curve
  - DAI
  - USDC
  - USDT
  - 3Crv
---

## Summary

1. On 14 November 2020, Value DeFi's MultiStablesVault was exploited through a same-transaction flash-loan strategy that drained about **8.9 million 3Crv**, later sold for roughly **7.4 million DAI**.
2. The incident is often summarized as "a flash-loan attack," but the more useful market-health lesson is narrower: a vault treated a manipulable, immediate Curve conversion rate as if it were a safe accounting input.
3. The attacker deposited DAI, received vault shares, manipulated Curve-related conversion math, then withdrew in 3Crv at an inflated amount before repaying the borrowed capital.
4. Existing strategy inventory mattered. The attacker did not need to force Value DeFi to sell every correlated Curve position into bad slippage; the controller already had enough 3Crv liquidity to satisfy the inflated withdrawal.
5. The post-incident return of part of the funds and the taunting "do you really know flashloan?" message made the story memorable, but the persistent issue was broader: DeFi vault shares can become unsafe when accounting depends on a single-block market state.

## Why this incident matters for market health

Stablecoin vaults sell a simple promise. A user deposits a dollar-like asset, the protocol routes it into yield strategies, and the user later withdraws a dollar-like asset plus yield. In calm conditions, the design feels close to money-market plumbing. That appearance is exactly why the Value DeFi exploit is an important market-health case study.

The affected system was not a thin, illiquid memecoin pool where volatility alone explains the loss. It sat in the stablecoin-yield part of DeFi, relied on Curve assets, and interacted with assets that market participants commonly treated as low-volatility collateral. The exploit showed that "stable" assets do not automatically make the accounting surface stable. If the protocol prices a vault share from a manipulable on-chain conversion path, a one-block imbalance can be turned into a claim on real inventory.

The gross drainage is usually described as roughly $7.4 million in DAI. A more precise technical framing is that the attacker drained about 8.9 million 3Crv from Value DeFi's MultiStablesVault controller and sold that 3Crv for about 7.4 million DAI. Some reporting quotes a lower final loss because the attacker later returned about 2 million DAI. Both numbers can be true, depending on whether the focus is gross extraction, post-return net loss, or user restitution. For risk analysis, the important fact is not the exact headline number; it is that an accounting formula let a temporary price state become a withdrawable claim against vault assets.

## The vulnerable flow

The attacker interacted with Value DeFi's MultiVaultBank and MultiStablesVault path. In the deposit leg, the attacker supplied DAI. The vault did not simply hold DAI as DAI. It routed the DAI through a converter that added liquidity to Curve's 3Pool and received 3Crv. The vault then minted shares against the amount of 3Crv-like value credited to the depositor.

That flow sounds normal for a stablecoin yield aggregator. The dangerous part appeared in the withdrawal path. The attacker deposited one stable asset and then withdrew in 3Crv. When the vault calculated how much 3Crv should be paid for a given share balance, it called a `balance_to_sell()`-style calculation that looked across the controller's strategy balances and converted other Curve-related positions into a 3Crv-denominated value.

The conversion path was the key. The controller estimated how much 3Crv it could obtain from other Curve tokens by routing through USDC and Curve conversion functions. That made the accounting sensitive to a temporary Curve pool imbalance. If the attacker could make the relevant Curve math say that USDC was unusually valuable relative to other pool assets, then the controller would overestimate how much 3Crv the vault's broader portfolio represented.

The resulting withdrawal formula can be simplified as:

```text
withdrawable output = balance_to_sell() * user shares / total shares
```

If `balance_to_sell()` is inflated, every share looks like it is entitled to more 3Crv than it should receive. The attacker did not need a long-term market move. The whole point of flash-loan capital was to create the distorted state, use it as an accounting input, and unwind within one transaction.

## The inventory detail that made the loss concrete

The exploit was not only a price-oracle problem. It was also an inventory problem.

Before the attacker's large deposit, the controller already held about 8.9 million 3Crv in its strategies. The attacker then deposited about 25 million DAI, which was converted into just under 25 million additional 3Crv. After that deposit, the controller had a large stock of actual 3Crv available. That detail mattered because an inflated withdrawal quote is only theoretical if the vault cannot pay it without suffering the same slippage that created the quote.

Here, the vault could pay. The controller had enough 3Crv inventory to satisfy the attacker's inflated withdrawal before being forced into a costly sale of other Curve assets. That meant the attacker captured the accounting overvaluation as real tokens. Value DeFi's own liquidity made the manipulated quote executable.

This pattern is one of the most important lessons from early DeFi vault exploits. A protocol can be exploited even when the manipulated price is temporary if the protocol holds enough immediately transferable inventory to honor the false price. The market manipulation does not need to persist beyond the transaction. It only needs to persist long enough for the contract's internal accounting to turn it into a withdrawal.

## Similarity to Harvest Finance

The Value DeFi exploit arrived less than a month after the October 2020 Harvest Finance incident. Both cases involved stablecoin vaults, Curve-related pricing, and flash-loan-enabled pool imbalances. Both showed that yield aggregators were not merely exposed to smart-contract bugs in the narrow sense of broken access control or arithmetic overflow. They were exposed to economic state bugs: the code did what it was written to do, but the assumptions behind the pricing input were wrong.

That distinction matters for users and market observers. Traditional code review can confirm that a function calls the expected contract and applies the expected formula. It may still miss the question, "Can an attacker make this input temporarily untrue with enough same-block capital?" The Harvest and Value DeFi sequence made that question unavoidable for vault design.

The timing also changed the meaning of audits. Value DeFi had marketed itself around security work, yet the exploit succeeded in a pattern the market had just seen. That does not mean every audit was worthless. It means audit coverage that focuses on local contract correctness is incomplete for a protocol whose safety depends on adversarial market microstructure.

## Flash loans were the amplifier, not the root cause

The attacker's capital source made the exploit efficient. Flash loans allowed a large balance-sheet operation to be performed without the attacker owning the full amount of capital up front. But treating flash loans as the root vulnerability is misleading.

An attacker with enough capital could also have attempted to distort the same pricing path. Flash loans lowered the cost and execution risk, but the core flaw was that the protocol accepted a manipulable spot state as a trustworthy price for vault-share accounting. The correct question is not "How do we block flash loans?" The correct question is "Which accounting inputs become false when a market can be moved for one block?"

That framing leads to better controls:

1. Do not use immediate AMM or Curve conversion quotes as sole sources for share minting or withdrawal value.
2. Add time-weighted or otherwise manipulation-resistant pricing where the protocol is valuing cross-asset claims.
3. Reject deposits and withdrawals when pool imbalance exceeds pre-defined thresholds.
4. Prevent same-block deposit-withdrawal loops where share issuance and redemption can reference different manipulated states.
5. Cap or delay withdrawals when the requested output asset differs from the deposited or strategy asset and the conversion route depends on current pool state.

These mitigations are not just technical hardening. They are market-integrity controls. They reduce the chance that a temporary liquidity shock becomes a transfer of solvency from passive depositors to an active arbitrageur.

## Why stablecoin vault users were exposed

For a depositor, the painful part of this incident is that the exploited surface was not obvious from the product category. A user could reasonably think of a multi-stable vault as diversified across DAI, USDC, USDT, and Curve LP positions. Diversification, however, does not help if the same accounting function turns the entire portfolio into a manipulable output quote.

The vault's composability compressed several risks into one user-facing share token:

1. Curve pool state risk.
2. Converter logic risk.
3. Strategy-controller inventory risk.
4. Share minting and redemption accounting risk.
5. Same-block transaction-ordering risk.

The user saw a yield vault. The attacker saw a balance sheet with a pricing oracle attached to a pool that could be moved atomically. Those are very different mental models of the same system.

This asymmetry is common in DeFi losses. Passive users underwrite risks that are hidden behind abstractions, while sophisticated searchers and attackers inspect the exact conversion, accounting, and liquidity paths. Market health deteriorates when advertised simplicity masks highly path-dependent settlement mechanics.

## The partial return and signaling effect

After the exploit, the attacker returned part of the funds, commonly reported as about 2 million DAI, and embedded a message taunting the team about flash loans. That detail attracted attention because it fit the public narrative of DeFi Summer: fast growth, aggressive marketing, and protocols learning adversarial finance in production.

The message should not distract from the structural failure. Returning funds after the fact is not a security model. A market cannot rely on attacker discretion, public pressure, or negotiations to make depositors whole. The relevant security question is whether the protocol can prevent a false accounting state from being settled in the first place.

The partial return also complicates loss accounting. Headlines may quote gross extraction, net retained proceeds, user losses after return, or later compensation plans. For market-health monitoring, these distinctions matter less than whether a protocol's share accounting can be manipulated again. Realized losses are the symptom; the repeatable exploit class is the disease.

## What monitors should have watched

The Value DeFi incident suggests a practical monitoring framework for stablecoin vaults and yield aggregators.

First, monitor pool imbalance in every external liquidity venue used for vault accounting. If a vault share price depends on Curve, Uniswap, Balancer, or another AMM state, then a sudden single-block reserve change should be treated as a security signal, not just a trading event.

Second, compare share issuance and redemption paths. If users can deposit one asset and withdraw another asset in the same transaction, the protocol should model whether the two paths reference the same price state, different price states, or different liquidity venues. The dangerous condition is not just a bad oracle; it is a round trip where the deposit leg and withdrawal leg disagree about value.

Third, inspect inventory depth in the output asset. A manipulated quote becomes more dangerous when the protocol has enough of the requested asset to pay it immediately. Thin inventory can cause denial of service or bad slippage. Deep inventory can turn an accounting error into a clean drain.

Fourth, treat strategy-controller balances as part of the oracle surface. In this case, the controller's view of multiple Curve-related assets helped compute the withdrawal entitlement. The accounting boundary was larger than the user-facing vault contract.

Finally, trigger circuit breakers on abnormal same-block sequences: large flash-loan inflow, major AMM imbalance, unusually large vault deposit, immediate cross-asset withdrawal, and rapid repayment. None of those events alone proves malicious activity. Together, they describe the exploit shape.

## Broader market implications

The Value DeFi exploit was part of the market's transition from simple smart-contract failures to composable financial attacks. Earlier losses often looked like direct bugs: a reentrancy issue, a missing permission check, or an arithmetic mistake. By late 2020, attackers were increasingly exploiting the interaction between protocols rather than a single line of code.

That shift changed the risk profile of DeFi yield products. A vault could be locally correct and still globally unsafe. The contract might faithfully call Curve, faithfully compute a conversion rate, and faithfully transfer assets. The failure was that the conversion rate was not a safe truth source under adversarial conditions.

This is why the incident belongs in market-health research rather than only security history. Market health depends on whether prices used for settlement are robust. If a protocol settles user claims against prices that can be created and destroyed inside one transaction, then the apparent liquidity of the market is overstated. It is liquidity available to attackers at a false price, not durable liquidity available to users.

## Lessons for current vault design

Modern DeFi has improved since 2020, but the Value DeFi pattern remains relevant. New vaults still combine LP tokens, stablecoins, restaking receipts, bridge assets, and derivative tokens into user-facing shares. The specific assets change; the accounting question remains the same.

A vault should be suspicious of any input that answers "what is this asset worth right now?" by asking a pool that can be moved right now. The safer design is to separate operational execution from accounting truth. A vault may execute swaps through an AMM, but it should not automatically let the AMM's instantaneous state define the value of deposits, withdrawals, collateral, or solvency.

The same rule applies to cross-asset withdrawals. If a user deposits DAI and withdraws 3Crv, or deposits one receipt token and withdraws another, the protocol is effectively running an internal exchange. Internal exchanges need slippage limits, price bounds, inventory-aware limits, and delayed settlement when the external market state is abnormal.

Value DeFi's loss also shows why "stablecoin" cannot be treated as a single risk label. DAI, USDC, USDT, and 3Crv may all target dollar-like value, but their on-chain liquidity mechanics differ. The exploit lived in those differences. The attacker did not need DAI to depeg from the dollar; the attacker needed the vault's conversion machinery to overstate a 3Crv entitlement.

## Conclusion

The Value DeFi exploit was a gross extraction of roughly 8.9 million 3Crv, sold for about 7.4 million DAI, enabled by same-block manipulation of vault accounting around Curve conversion rates. The memorable flash-loan narrative is useful, but incomplete. The real lesson is that composable DeFi systems must treat market state as adversarial input.

For market participants, the incident remains a warning about yield products that abstract away strategy complexity. A vault share is only as safe as the accounting path that mints and redeems it. If that path depends on a manipulable spot price, deep liquidity can become a liability, and a stablecoin vault can become unstable in a single block.
