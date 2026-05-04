---
date: 2026-05-05
entities:
  - id: opyn
    name: Opyn
    type: defi
  - id: otoken
    name: oToken
    type: token
  - id: usdc
    name: USDC
    type: stablecoin
  - id: ethereum
    name: Ethereum
    type: blockchain
title: "Opyn ETH put double-exercise exploit, oToken accounting, and the 371,260 USDC options-collateral loss"
---

## 1. Introduction and incident overview

On 4 August 2020, Opyn disclosed and responded to an exploit in its ETH put option contracts. The attacker stole 371,260 USDC from collateral backing ETH put options by abusing the way Opyn's `exercise()` flow handled batched exercises when ETH was the underlying asset. The incident did not depend on an oracle manipulation, a private-key compromise, or a stablecoin failure. It was a contract-accounting bug in an on-chain options protocol.

The affected product was Opyn's ETH put option system. In normal operation, a buyer of an ETH put could exercise by sending ETH and the relevant oTokens to the protocol, receiving USDC collateral from sellers. The oTokens should represent the right to exercise once. After exercise, the protocol must consume the oTokens and account for the underlying ETH supplied by the exerciser. The exploit showed that this accounting was not safe when multiple vaults were exercised in one call.

Independent summaries describe the bug as a double-spend or double-exercise of oTokens. The attacker called `exercise()` with more than two vaults containing ETH as the underlying asset. Because the implementation treated the same ETH sent with the transaction as if it were available for multiple exercises, the attacker could reuse one batch of ETH to retrieve USDC collateral from multiple vaults. Put sellers lost collateral; Opyn and whitehats moved quickly to prevent a larger loss.

Opyn's own documentation later summarized the incident plainly: an attacker exploited a vulnerability in the ETH put option contracts, stole 371,260 USDC, and the team recovered 572,165.13 USDC of at-risk funds with the help of whitehat samczsun. Opyn also stated that all affected users were made whole.

This incident is important for market-health analysis because it illustrates a category of DeFi risk that is easy to miss: exercise accounting in derivative protocols. Options protocols must track not only token balances, but also collateral, vault state, expiry, strike, underlying asset flow, and batch semantics. If those layers do not compose exactly, a small accounting mismatch can drain collateral from otherwise fully collateralized positions.

## 2. Opyn and oTokens

### 2.1 What Opyn provided

Opyn was a non-custodial options and DeFi protection protocol on Ethereum. It allowed users to buy and sell options represented by ERC-20-like oTokens. A seller could collateralize an option, mint oTokens, and sell those oTokens to buyers. A buyer could hold, trade, or exercise the oTokens if the option became valuable.

For ETH put options, sellers posted USDC collateral. Buyers of ETH put options obtained downside protection: if ETH traded below the strike, they could exercise the put by delivering ETH and oTokens to receive USDC at the strike terms. If ETH stayed above the strike and the option expired, sellers could reclaim their USDC collateral.

The protocol's promise rested on full collateralization and deterministic settlement. A put seller's worst-case exposure should be bounded by posted USDC. A put buyer's claim should be bounded by the oTokens they hold and the underlying asset they provide. The contract must enforce both sides with exact accounting.

### 2.2 How oTokens functioned

oTokens represented option claims. In the ETH put case, an oToken corresponded to protection on an amount of ETH. A buyer who exercised should transfer the required ETH and burn or consume the oTokens. In return, the protocol transfers USDC collateral from option sellers' vaults.

The key invariant is simple:

> The same oToken balance and the same underlying ETH payment must not be usable to claim USDC collateral more than once.

This invariant has two parts. First, oTokens must be burned or otherwise consumed when exercised. Second, the underlying asset payment must be counted once per exercise. If either side can be reused, the exerciser can receive more collateral than they paid for.

### 2.3 Vaults and batch settlement

Opyn's options architecture used vaults. Sellers locked collateral in vaults, and exercisers could exercise against vaults that backed the relevant oTokens. Batch processing can improve usability and gas efficiency because a user can settle against multiple vaults in one transaction.

Batch settlement also increases risk. The contract must ensure that each item in the batch has its own required inputs and that values are decremented as the loop proceeds. If the same `msg.value` or balance is implicitly treated as fresh input for every vault, the batch becomes a multiplier for the attacker's claim.

That is the core market-health lesson from Opyn: batch execution is not just a gas optimization. It is a state machine. Every loop iteration must consume exactly the correct amount of input and produce exactly the correct amount of output.

## 3. Vulnerability: reused ETH input in batched exercise

### 3.1 The intended exercise path

For an ETH put, a normal exercise path should look like this:

1. The holder chooses an amount of oTokens to exercise.
2. The holder sends the required ETH underlying to the contract.
3. The contract burns or consumes the oTokens.
4. The contract pays out the corresponding USDC collateral.
5. The seller's vault state is reduced consistently.

For a batch over multiple vaults, the same logic must apply per vault. If the first vault consumes part of the ETH payment, the remaining available ETH must decrease. If the full payment is already consumed, a later vault cannot reuse it.

### 3.2 The bug

Public post-incident summaries describe the bug as the contract treating the same batch of ETH as multiple ETH receptions. In Solidity, `msg.value` is the ETH attached to the entire payable call. It does not automatically get consumed per loop iteration. If a function checks `msg.value` inside a loop without tracking how much has already been allocated, each iteration can accidentally see the full transaction value.

That is dangerous in an options exercise function. The attacker could structure an exercise call across multiple vaults so the contract interpreted one ETH payment as sufficient for more than one collateral claim. The result was equivalent to exercising more rights than the attacker had paid for.

Some summaries frame the incident as oTokens not being burned correctly during batch exercise. Others emphasize reuse of the same ETH `msg.value`. These are two views of the same settlement-accounting failure: the exercise path failed to ensure that the option claim and underlying payment were consumed exactly once for each USDC payout.

### 3.3 Why ETH underlying was special

ERC-20 token transfers normally require explicit `transferFrom` calls for a specific amount. If the underlying asset is an ERC-20, the contract can call `transferFrom(msg.sender, address(this), amount)` for each exercise amount. ETH is different. ETH arrives as `msg.value` on the call. The contract must implement its own accounting for how the sent ETH is allocated across the operation.

This distinction is subtle but important. A function that works safely for ERC-20 underlyings may not be safe for ETH if it assumes the payment can be handled the same way. ETH does not have a `transferFrom` balance decrement inside the contract's loop. The contract must decrement an internal "remaining ETH supplied" variable.

The Opyn exploit shows how native-asset handling can create a special-case failure in otherwise general derivative logic.

## 4. Attack flow

### 4.1 Acquire exercisable oTokens

The attacker needed oTokens corresponding to ETH puts. These tokens represented the right to exercise and claim USDC collateral under the option terms. Because oTokens were transferable, the attacker could obtain them on the market or through normal protocol interactions.

Transferability is not itself the problem. Tradable option tokens are part of the product. The risk emerged because the exercise function allowed a single underlying payment to be counted against multiple vaults.

### 4.2 Call `exercise()` against multiple vaults

The attacker called `exercise()` with a batch involving more than two vaults. Each vault contained collateral from ETH put sellers. The function should have required enough ETH and oTokens for the total exercise amount across the batch.

Instead, the implementation interpreted the same ETH supplied with the transaction as if it could satisfy multiple vault exercises. The attacker reused the same ETH payment to draw USDC collateral more than once.

### 4.3 Drain seller collateral

For each successful exercise, the protocol paid USDC collateral to the caller. Because the input accounting was wrong, the attacker received more USDC than the actual ETH/oToken exercise should have justified. The loss came from the collateral of users who had sold ETH puts.

Public incident summaries report 371,260 USDC stolen. The example transaction referenced in open incident datasets is `0xd06378b73536e7718895069a5219855774d362db47312dc304dfd4b6e39ef000`.

### 4.4 Emergency response and whitehat action

Opyn responded by removing liquidity, pausing or disabling at-risk flows where possible, and coordinating with whitehats. Defiprime's weekly summary reported that Opyn removed liquidity from Uniswap, whitehat-hacked 439,170 USDC out of harm's way, and that samczsun helped recover an additional 132,995 USDC. Opyn's later documentation summarized the protected amount as 572,165.13 USDC of at-risk funds recovered with whitehat help.

This response prevented the exploit from scaling further. It also shows an important property of immutable protocols: if a vulnerable contract cannot simply be patched in place, emergency response often means removing liquidity, warning users, and using the same exploit path defensively to move funds before malicious actors can.

## 5. Market and user impact

### 5.1 Loss to ETH put sellers

The direct victims were ETH put option sellers whose USDC collateral was extracted. A seller in a fully collateralized options protocol accepts market risk: if ETH falls below the strike and buyers exercise legitimately, the seller pays USDC and receives ETH. The seller should not also face the risk that the same ETH input can be reused to claim collateral multiple times.

The exploit converted contract-accounting risk into seller loss. That distinction matters for users evaluating DeFi derivatives. Full collateralization protects against counterparty default, but it does not protect against incorrect settlement logic.

### 5.2 Buyer disruption

ETH put buyers were also affected operationally. When a protocol disables or migrates a product after an exploit, buyers may lose access to normal exercise, secondary-market liquidity, or hedging continuity. Public summaries reported that Opyn offered to buy ETH put oTokens with a premium over market references to compensate users.

Even if buyers were ultimately compensated, the incident reduced confidence in using on-chain options for risk management. A hedge that becomes operationally uncertain during stress can fail its purpose.

### 5.3 Protocol trust and early DeFi derivatives

In 2020, DeFi options were still new. Opyn was one of the more visible projects building generalized options infrastructure. The exploit demonstrated that derivative protocols have a larger state surface than simpler spot swaps or lending deposits:

- option token balances;
- collateral vaults;
- expiry windows;
- strike terms;
- exercise functions;
- asset-specific transfer semantics;
- batch settlement;
- secondary-market liquidity; and
- emergency controls.

Each layer can be correct in isolation while the composed exercise path is wrong.

## 6. Why audits did not eliminate the risk

Quadriga's case summary notes that OpenZeppelin had audited the original Opyn contracts, but the exploit was outside the audit's scope. This is a recurring lesson in DeFi incidents. An audit is not a blanket guarantee. Scope, version, assumptions, integrations, later changes, and unreviewed paths matter.

For a protocol like Opyn, security review must cover not only contract files but also product-specific workflows:

- exercising ETH puts;
- exercising ERC-20-based options;
- exercising across multiple vaults;
- batch exercise with native ETH;
- Uniswap liquidity interactions;
- vault withdrawal after exercise;
- expiry handling; and
- emergency shutdown behavior.

The exploited path was not a generic arithmetic operation. It was an options-specific settlement path. That makes workflow-level testing and adversarial simulation as important as line-by-line review.

## 7. Controls that would have reduced the loss

### 7.1 Explicit payment consumption in batch loops

When native ETH is supplied to a batch function, the function should track a local variable such as `remainingEth`. Each vault exercise should decrement it. The function should revert if the required amount exceeds the remaining supplied ETH. At the end, it should refund any unused dust or require exact payment.

The invariant should be:

> Sum of ETH consumed across the batch <= `msg.value`, and no loop iteration can observe already-consumed ETH as available.

This is the direct control against `msg.value` reuse.

### 7.2 Checks-effects-interactions ordering

The contract should update exercise state and consume oTokens before paying collateral. In derivative settlement, the "effect" is not only token burning; it also includes reducing available input, updating vault accounting, and marking the claim as consumed. Payouts should happen only after all required state changes are complete.

This control limits double-use paths and reduces the chance that an external call or later loop iteration sees stale state.

### 7.3 Separate ETH and ERC-20 code paths

Generic asset abstractions can hide native ETH differences. For critical settlement code, separate ETH and ERC-20 paths are often safer than pretending ETH behaves like an ERC-20. Each path should have its own tests:

- ETH put exercise with one vault;
- ETH put exercise with many vaults;
- insufficient `msg.value`;
- excess `msg.value`;
- repeated vault entries;
- zero-amount edge cases;
- ERC-20 underlying exercise; and
- mixed collateral/underlying configurations where supported.

The special handling should be explicit enough that reviewers can reason about it.

### 7.4 Invariant and property testing

Options protocols should test conservation properties. For Opyn-like ETH puts:

- A user cannot receive more USDC than the option terms allow.
- A unit of oToken can be exercised once.
- A unit of ETH underlying can be counted once.
- Seller vault collateral decreases only by valid exercised amounts.
- Total USDC paid out across a batch equals the sum of valid per-vault exercises.
- Reordering vaults in a batch does not change total payout.
- Duplicating vault references in a batch cannot multiply payout.

These invariants are more powerful than example-based tests because they capture the financial rules of the protocol.

### 7.5 Emergency liquidity procedures

Opyn's response included removing liquidity and using whitehat action to secure funds. Protocols should prepare these playbooks before incidents:

- identify contracts and pools that can amplify loss;
- know which multisig actions are available;
- monitor abnormal exercise patterns;
- have public communication templates;
- have whitehat coordination channels;
- know how to compensate affected users; and
- know which functions cannot be paused.

Emergency playbooks do not replace prevention, but they reduce loss when prevention fails.

## 8. Market-health indicators

### 8.1 Batch exercise with native assets

Any DeFi derivative protocol that batches operations involving ETH should be considered higher risk until its payment-consumption accounting is verified. The specific indicator is a payable batch function where `msg.value` is read across multiple loop iterations.

Analysts can ask:

- Is `msg.value` copied into a remaining-balance variable?
- Is that variable decremented per operation?
- Does the function allow repeated vault IDs?
- Does each exercise consume the option token before payout?
- Are insufficient-payment cases tested?

### 8.2 Fully collateralized does not mean settlement-safe

Opyn's ETH puts were designed as fully collateralized products. That reduced insolvency risk from market movement but did not remove settlement risk. Market-health models should separate:

- collateral adequacy;
- oracle correctness;
- exercise correctness;
- liquidation correctness;
- maturity/expiry correctness; and
- emergency-control readiness.

A product can be fully collateralized and still exploitable if exercise settlement pays too much.

### 8.3 Whitehat recoveries as partial mitigation, not proof of safety

The recovery of 572,165.13 USDC of at-risk funds was valuable. But whitehat success after discovery should not be confused with protocol safety before discovery. The market-health question is whether a malicious actor could have reached those funds first.

Whitehat recoveries are a sign of effective incident response. They are not a substitute for robust invariants.

### 8.4 Secondary-market liquidity as blast radius

oTokens traded in liquidity pools. When an options contract is vulnerable, secondary-market liquidity can amplify exposure by letting attackers acquire exercise rights quickly or by leaving users holding impaired tokens. Removing Uniswap liquidity was therefore part of the containment response.

Market-health monitoring for derivative protocols should include both the protocol contracts and related liquidity venues.

## 9. Broader implications for DeFi derivatives

### 9.1 Derivatives are state machines

A spot AMM swap has a relatively simple invariant: reserves change according to a pricing formula. An options protocol has more states: minting, selling, buying, exercising, expiring, closing, collateral withdrawal, and emergency migration. Bugs often occur at transitions between these states.

The Opyn exploit happened at one of those transitions: exercise. It was not enough for the oToken to exist or for collateral to be posted. The transition from "option holder has a claim" to "claim has been exercised and collateral paid" had to be exact.

### 9.2 Native ETH remains a footgun

The distinction between ETH and ERC-20 tokens has caused many smart-contract bugs. Native ETH uses `msg.value`; ERC-20 tokens use `transferFrom`. A generic financial product that supports both must either normalize them extremely carefully or isolate their handling.

Opyn's incident is part of a broader pattern: when developers abstract assets too aggressively, native ETH semantics can break assumptions.

### 9.3 Compensation protects users but not necessarily markets

Opyn's documentation states that all affected users were made whole. That matters for user harm. But a reimbursed exploit still affects market confidence, liquidity, and the willingness of sophisticated users to rely on the protocol for hedging. It also imposes treasury or team costs that could have funded development.

For market-health evaluation, compensation changes the final user-loss outcome but not the severity of the exploited flaw.

## 10. Timeline

- **Before August 2020**: Opyn operates ETH put options using oTokens and USDC collateral.
- **4 August 2020**: An attacker exploits the ETH put option contracts and steals 371,260 USDC.
- **Immediate response**: Opyn removes liquidity from Uniswap and coordinates defensive action.
- **Whitehat recovery**: Opyn and whitehats secure 572,165.13 USDC of at-risk funds, including public reports of 439,170 USDC moved out of harm's way and 132,995 USDC recovered with samczsun's help.
- **Aftermath**: Opyn states that affected users were made whole and revises security practices, including monitoring, pause functionality, larger bug bounty scope, audits, and stronger test-driven development.

## 11. Lessons for builders, users, and analysts

For builders, the lesson is to treat exercise logic as the core of an options protocol. Every exercise must consume the option token and the underlying asset exactly once. Batch loops need explicit input accounting, especially for native ETH.

For users, the lesson is that fully collateralized derivatives still carry smart-contract settlement risk. Put sellers are not only underwriting market movement; they are trusting contract logic that releases collateral.

For analysts, the Opyn exploit provides a concrete checklist: look for payable batch functions, repeated use of `msg.value`, missing decrement of supplied native assets, delayed oToken burn, vault duplication in batch inputs, and collateral payouts before complete state updates.

The 371,260 USDC Opyn exploit was small compared with later DeFi disasters, but it exposed a foundational risk in on-chain derivatives. A single ETH payment was interpreted as multiple payments during batch exercise, and that was enough to turn a hedging product into a collateral drain.

## References

- Opyn V1 FAQ, [What has Opyn done following the Aug 4 exploit?](https://github.com/opynfinance/Opyn-GitBooks-Docs/blob/c75649ee8c8571581a05f92f6f4e87f1785c9ef0/faq.md)
- liqtags crypto-rekts mirror, [Opyn incident summary](https://github.com/liqtags/crypto-rekts/blob/39b2d7c0b165d841c853e77dedcb835e69d18a4c/rekts/opyn.md)
- Quadriga Initiative, [Opyn Double use oToken Breach](https://quadrigainitiative.com/casestudy/opyndoubleuseotokenbreach.php)
- Defiprime, [The Defiprime Post #3](https://github.com/defiprime/defiprime1/blob/9375cccf1c485c606d57c94072748cbd1bc48eee/collections/_posts/2020-08-09-post3.md)
- Etherscan, [publicly referenced example attack transaction](https://etherscan.io/tx/0xd06378b73536e7718895069a5219855774d362db47312dc304dfd4b6e39ef000)
