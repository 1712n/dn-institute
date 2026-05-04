---
date: 2026-05-05
entities:
  - id: saddle-finance
    name: Saddle Finance
    type: defi-protocol
  - id: synapse-protocol
    name: Synapse Protocol
    type: defi-protocol
title: "Saddle Finance metapool exploit: virtual price manipulation and $10.2M arbitrage drain"
---

## Introduction

Saddle Finance was a decentralized exchange protocol on Ethereum optimized for trading between similarly-priced assets (stablecoins, wrapped tokens, and synthetic assets). Forked from Curve Finance's StableSwap algorithm, Saddle offered low-slippage swaps between pegged assets using a hybrid constant-sum/constant-product invariant that concentrated liquidity around the 1:1 price ratio. The protocol served as critical infrastructure for cross-chain bridge ecosystems, particularly hosting metapools that paired bridge-specific wrapped tokens (like Synapse's nUSD) against base stablecoin pools.

On April 30, 2022, an attacker exploited a vulnerability in Saddle Finance's metapool implementation, manipulating the virtual price calculation to extract approximately $10.2 million from a metapool that paired Synapse Protocol's saddleUSD-V2 LP tokens with other stablecoins. The exploit leveraged an arithmetic flaw in how the metapool calculated the virtual price of the base pool LP tokens when processing swaps, allowing the attacker to manipulate the apparent value of LP tokens within a single transaction and extract more value than they deposited through repeated swap cycles.

## Background

### StableSwap and Metapool Architecture

Curve Finance's StableSwap algorithm (and Saddle's fork of it) uses a modified invariant function that provides low slippage for swaps between similarly-priced assets. The invariant combines a constant-sum formula (which would provide zero slippage at 1:1 but no liquidity beyond the pool's reserves) with a constant-product formula (which provides infinite liquidity but increasing slippage). The combination is controlled by an amplification parameter (A) that determines how closely the pool behaves like a constant-sum pool versus a constant-product pool.

Metapools are a design pattern where one of the tokens in a pool is itself an LP token from another ("base") pool. This allows new assets to be traded against an existing deep pool without fragmenting liquidity. For example, a metapool might pair Token X against the base pool's LP token, giving Token X access to the entire base pool's liquidity through a two-step swap: Token X → Base LP Token → any token in the base pool.

The virtual price of the base pool LP token is a critical input to the metapool's swap calculations. It represents the value of one LP token in terms of the underlying assets, accounting for the base pool's composition and any fees that have been earned. If the virtual price can be manipulated, the metapool's swap function will miscalculate exchange rates, potentially allowing an attacker to extract value.

### Saddle's Metapool Implementation

Saddle Finance's metapool implementation was adapted from Curve's Vyper codebase into Solidity. The adaptation included the virtual price calculation that determined how base pool LP tokens were valued within the metapool. When a swap occurred in the metapool that involved the base pool LP token, the contract queried the base pool's `getVirtualPrice()` function to determine the conversion rate.

The vulnerability was related to how the virtual price calculation interacted with the metapool's own swap logic — specifically, when the metapool performed operations that altered the base pool's state within the same transaction, the virtual price could become stale or manipulable.

### The saddleUSD-V2 Metapool

The exploited metapool was a saddleUSD-V2 pool on Saddle Finance that was integrated with Synapse Protocol's cross-chain infrastructure. This pool facilitated cross-chain stablecoin transfers by allowing users to swap between Synapse's bridge tokens and Saddle's base stablecoin pool. The pool held significant TVL due to its role in cross-chain liquidity routing.

## The Attack

### Vulnerability: Virtual Price Manipulation via Flash Loan

The core vulnerability was in the interaction between the metapool's swap function and the base pool's virtual price calculation. The attacker discovered that by executing a specific sequence of operations within a single transaction — depositing into the base pool (which changes the virtual price), performing swaps in the metapool (which reads the changed virtual price), and then withdrawing from the base pool — they could exploit an inconsistency between the metapool's pricing and the actual value of the underlying assets.

The specific flaw was that the metapool's swap calculations cached the virtual price at certain points during execution but not others, creating windows where the virtual price used for calculation did not match the actual current state. By carefully ordering deposits, swaps, and withdrawals, the attacker could "sandwich" their own metapool operations with virtual price manipulations.

### Attack Execution

The attack was executed through multiple transactions on April 30, 2022:

**Step 1: Flash loan acquisition.** The attacker obtained flash loans of stablecoins (USDC, USDT, DAI) to provide the capital for the manipulation.

**Step 2: Base pool deposit to inflate virtual price.** The attacker deposited a large amount of stablecoins into the Saddle base pool, receiving LP tokens. This deposit was imbalanced (heavily weighted toward one stablecoin), which moved the base pool's composition and affected the virtual price calculation in a predictable way.

**Step 3: Metapool swap at manipulated virtual price.** With the base pool's virtual price affected by the large imbalanced deposit, the attacker performed swaps in the metapool. The metapool's swap function used the manipulated virtual price to calculate the exchange rate, resulting in a favorable rate for the attacker — either receiving more tokens than the true exchange rate would warrant, or paying fewer tokens than the true cost.

**Step 4: Base pool withdrawal.** The attacker withdrew their deposit from the base pool, roughly restoring the pool's composition and virtual price. The cost of this round-trip (deposit then withdrawal) was bounded by the base pool's swap fees and any slippage, but was significantly less than the profit extracted from the metapool's mispriced swaps.

**Step 5: Repetition.** The attacker repeated this cycle multiple times within the same or sequential transactions, each time extracting value from the metapool's mispricing. The total extraction across all cycles was approximately $10.2 million.

**Step 6: Flash loan repayment and profit extraction.** The attacker repaid the flash loans and retained the profit — the difference between the value extracted from the metapool and the cost of the base pool round-trips.

## Impact

### Financial Losses

The total financial impact was approximately $10.2 million, drained from the saddleUSD-V2 metapool. The losses were borne by liquidity providers who had deposited into the metapool — their LP tokens now represented claims on a significantly depleted pool. Because the metapool was integrated with Synapse Protocol's cross-chain infrastructure, the losses also affected users who were using the pool for cross-chain stablecoin transfers (they received worse rates or could not complete transfers).

### Impact on Synapse Protocol

Synapse Protocol, which relied on the Saddle metapool for its Ethereum-side liquidity, was indirectly affected by the exploit. Cross-chain transfers routed through the exploited pool were disrupted, and users experienced slippage or failed transactions until the pool was paused and alternative routing was established.

### Impact on Saddle Finance

The exploit was one of several security incidents that plagued Saddle Finance during its operational period. Combined with an earlier exploit in January 2022 (approximately $3.5 million lost from a different pool), the April 2022 incident severely damaged user confidence in the protocol. Saddle Finance's TVL declined sharply following the exploit and the protocol eventually wound down operations, with the team joining other DeFi projects.

## Response and Remediation

### Immediate Response

The Saddle Finance team paused the affected metapool within hours of detecting the exploit. They published an incident report identifying the virtual price manipulation vector and confirmed the total losses. The team coordinated with Synapse Protocol to reroute cross-chain liquidity away from the affected pool.

### Technical Fix

The fix addressed the virtual price manipulation by implementing a reentrancy-style guard that prevented base pool operations from being executed in the same transaction as metapool swaps (eliminating the ability to manipulate the virtual price and exploit it atomically). Additional mitigations included caching the virtual price at the start of each transaction and using the cached value for all calculations within that transaction (preventing mid-transaction manipulation), implementing a maximum single-swap size relative to pool TVL, and adding virtual price deviation checks that reverted swaps if the virtual price had changed significantly within the current block.

### Partial Compensation

The Saddle team allocated treasury resources for partial compensation to affected LPs, covering approximately 50-60% of losses. The partial compensation reflected the project's limited treasury resources relative to the exploit's size.

## Technical Analysis

### Virtual Price in StableSwap Metapools

The virtual price of a StableSwap LP token represents the intrinsic value of one LP token in terms of the pool's underlying assets, accounting for the pool's current composition and accumulated fees. It is calculated as:

```
virtualPrice = pool_invariant(balances) / totalSupply(LP_tokens)
```

Where `pool_invariant` is the StableSwap invariant function D applied to the current pool balances. The virtual price increases over time as trading fees accumulate in the pool (fees increase the invariant D without increasing the LP token supply).

In a metapool, the virtual price of the base pool's LP token is used to convert between the LP token and its underlying value when calculating swap rates. If the virtual price can be artificially inflated or deflated within a single transaction, the metapool's swap calculations will use an incorrect conversion rate.

### Manipulation Window

The manipulation window existed because the virtual price was calculated dynamically from the base pool's current state (balances and LP supply) rather than from a cached or time-weighted value. This meant that any action that changed the base pool's state (deposit, withdrawal, swap) immediately affected the virtual price reported to the metapool.

The attacker exploited this by: (1) changing the base pool's state to manipulate the virtual price, (2) performing metapool operations that used the manipulated virtual price, and (3) reverting the base pool's state to recover the manipulation cost. Steps 1 and 3 approximately cancel out (minus fees), while step 2 extracts value from the metapool based on the manipulated price.

### Curve vs. Saddle Implementation Differences

The vulnerability in Saddle's implementation may not have existed (or may have been less severe) in Curve's original Vyper implementation due to differences in how the two codebases handled virtual price caching and reentrancy protections. Curve's contracts included a reentrancy lock that prevented the base pool and metapool from being accessed in the same transaction by external callers, which would have blocked the attacker's ability to manipulate the base pool and exploit the metapool atomically.

Saddle's Solidity adaptation may not have fully replicated this protection, creating the manipulation window. This discrepancy highlights a risk of translating complex DeFi protocols between languages and architectures — subtle security properties that are implicit in the original implementation's structure may be lost or weakened during adaptation.

### Comparison with Similar Metapool Exploits

Virtual price manipulation in metapools has been a recurring vulnerability pattern. The Curve Finance read-only reentrancy vulnerability (discovered in 2023, affecting protocols that read Curve pool prices) demonstrated that virtual price could be manipulated through reentrancy callbacks during pool operations. The Warp Finance exploit (December 2020) manipulated LP token prices used as lending collateral — a related but distinct vector where the LP token's market price (rather than virtual price) was manipulated.

## Lessons Learned

### Metapool Pricing Must Be Manipulation-Resistant

Metapools that use the virtual price of base pool LP tokens for swap calculations must ensure that the virtual price cannot be manipulated within the same transaction as metapool operations. This can be achieved through cross-contract reentrancy locks that prevent base pool and metapool from being accessed in the same transaction, virtual price caching that uses the value from the previous block rather than the current state, or time-weighted virtual price calculations that average over a window.

### Fork Adaptation Must Preserve Security Properties

When adapting a protocol from one language or architecture to another (as Saddle did from Curve's Vyper to Solidity), the security properties of the original implementation must be explicitly identified and preserved. This includes implicit protections that arise from the original architecture's structure (like reentrancy ordering) that may not be automatically replicated in the adaptation.

### Single-Transaction Atomic Manipulation

Any DeFi protocol that reads state from another protocol (pools, oracles, LP prices) must consider whether that state can be manipulated within the same transaction. If the answer is yes, the protocol must either use manipulation-resistant inputs (TWAPs, cached values, external oracles) or implement transaction-level isolation that prevents the manipulation and exploitation from occurring atomically.

## Conclusion

The Saddle Finance metapool exploit of April 30, 2022, drained approximately $10.2 million through manipulation of the base pool's virtual price used by the metapool's swap calculations. The attacker performed imbalanced deposits into the base pool to shift the virtual price, executed metapool swaps at the manipulated rate, and then withdrew from the base pool to recover the manipulation cost — profiting from the metapool's mispricing at the expense of liquidity providers. The vulnerability arose from the metapool's reliance on the base pool's current-state virtual price (rather than a cached or time-weighted value), combined with the absence of cross-contract reentrancy protections that would have prevented atomic manipulation-and-exploitation. The incident demonstrated that metapool architectures require explicit protection against virtual price manipulation, and that forked protocol implementations must carefully preserve the security properties — including implicit architectural protections — of the original codebase.
