---
date: 2026-05-05
entities:
  - id: conic-finance
    name: Conic Finance
    type: defi-protocol
  - id: curve-finance
    name: Curve Finance
    type: defi-protocol
  - id: ethereum
    name: Ethereum
    type: blockchain
title: "Conic Finance read-only reentrancy exploit: Curve pool virtual price manipulation and $3.2M omnipool drain"
---

## Introduction

Conic Finance was a yield optimization protocol on Ethereum designed to diversify Curve Finance liquidity provision across multiple pools. Through its "omnipool" mechanism, users deposited a single asset (such as ETH or a stablecoin) and Conic automatically allocated the funds across a curated set of Curve pools and Convex Finance vaults, rebalancing periodically to optimize yield. The protocol aimed to reduce concentration risk for Curve LPs by spreading exposure across multiple pools while maintaining a simple single-token deposit interface.

On July 21, 2023, an attacker exploited a read-only reentrancy vulnerability in Conic Finance's omnipool contracts, extracting approximately $3.2 million in ETH. The attack leveraged a known vulnerability pattern in Curve Finance pools where the pool's virtual price can be temporarily manipulated during a callback within a remove_liquidity operation. The attacker exploited a window during Curve's ETH pool liquidity removal where the virtual price reported by the pool was momentarily inaccurate, using this manipulated price to inflate the value of their omnipool position and withdraw more than their fair share.

## Background

### Curve Finance Virtual Price and Read-Only Reentrancy

Curve Finance pools expose a `get_virtual_price()` function that reports the current value of one LP token in terms of the pool's underlying assets. This virtual price is used widely across DeFi for pricing Curve LP tokens — in lending protocols (as collateral valuation), in yield aggregators (for deposit/withdrawal calculations), and in other protocols that integrate with Curve pools.

The "read-only reentrancy" vulnerability in Curve's ETH pools was identified and publicly documented in mid-2023 (though it had been theoretically known earlier). The vulnerability exists because Curve's `remove_liquidity` function in ETH-containing pools performs an ETH transfer to the withdrawer via a low-level `call`. If the withdrawer is a smart contract, this transfer triggers the contract's `receive()` or `fallback()` function. At this point in execution, the Curve pool's internal state has been partially updated (LP tokens are burned) but the pool's actual ETH balance has already decreased (ETH has been sent). If the receiving contract calls `get_virtual_price()` during this callback, the function will return a manipulated value — because the LP supply has decreased (tokens burned) but the token balance hasn't been updated in the pool's internal accounting yet.

This is called "read-only" reentrancy because the attacker doesn't re-enter a state-modifying function — they only read the virtual price during the callback. But the stale/manipulated price read is sufficient to exploit any protocol that queries the virtual price at that moment.

### Conic Finance Omnipool Architecture

Conic's omnipool contracts tracked the total value managed by each pool allocation. When users deposited or withdrew from the omnipool, the contract needed to calculate the user's proportional share of the total value. This calculation involved querying the virtual price of each Curve pool where Conic had deployed funds, multiplying by the Curve LP tokens held, and summing across all allocations.

The vulnerability was that Conic queried `get_virtual_price()` from Curve ETH pools as part of its share calculation without protection against the read-only reentrancy manipulation. An attacker who could trigger the calculation during the reentrancy window (when virtual price was temporarily inflated) could appear to hold a larger share of the omnipool than they actually did.

## The Attack

### Vulnerability: Unguarded Virtual Price Read During Reentrancy Window

The core vulnerability was that Conic Finance's withdrawal function queried `get_virtual_price()` from a Curve ETH pool to determine the user's share value. If this query was made during the reentrancy window of a Curve `remove_liquidity` call, the virtual price would be temporarily inflated, causing Conic to overvalue the attacker's position and allow withdrawal of more assets than entitled.

### Attack Execution

The attack on July 21, 2023, proceeded as follows:

**Step 1: Position establishment.** The attacker deposited ETH into Conic's ETH omnipool, receiving omnipool LP tokens representing their share.

**Step 2: Curve liquidity removal with reentrancy.** The attacker (through a custom contract) called `remove_liquidity` on the relevant Curve ETH pool. During the ETH transfer callback within this operation, the attacker's contract gained execution control while the Curve pool was in the vulnerable state (virtual price temporarily manipulated upward).

**Step 3: Conic withdrawal during callback.** Within the callback (while the Curve pool's virtual price was inflated), the attacker's contract called Conic's withdrawal function. Conic queried `get_virtual_price()` from the Curve pool to value the omnipool's holdings, received the inflated value, and calculated the attacker's share as being worth more than it actually was.

**Step 4: Inflated withdrawal.** Conic processed the withdrawal at the inflated valuation, sending the attacker more ETH than their actual omnipool share warranted. The difference between the inflated withdrawal and the actual share value was the attacker's profit.

**Step 5: Completion.** The Curve `remove_liquidity` operation completed normally after the callback returned. The attacker retained the excess withdrawal from Conic, having exploited the momentary virtual price inflation.

The total extraction was approximately 1,700 ETH (~$3.2 million at the time), achieved across multiple attack transactions within a short time window.

## Impact

### Financial Losses

The Conic Finance ETH omnipool lost approximately 1,700 ETH ($3.2 million), borne by all remaining depositors whose share of the pool was diluted by the attacker's inflated withdrawal. The omnipool's total value dropped sharply, and depositors who withdrew after the attack received less than their pre-attack deposit value.

### Protocol Shutdown

Following the exploit, Conic Finance halted all omnipool operations. The team published a post-mortem within 24 hours and acknowledged the read-only reentrancy vulnerability. The protocol did not resume operations; the team eventually wound down the project, returning remaining funds to depositors at the post-exploit valuation (significantly reduced from pre-exploit values).

### Broader Read-Only Reentrancy Impact

The Conic exploit was one of several incidents in mid-2023 that exploited the Curve read-only reentrancy pattern. Other affected protocols included various lending platforms and yield aggregators that used `get_virtual_price()` for collateral or share valuation. The cluster of exploits prompted Curve Finance to release updated pool implementations with reentrancy locks on the price oracle functions, though existing deployed pools could not be retroactively patched without migration.

## Response and Remediation

### Immediate Response

Conic paused omnipools immediately after detection. The team identified the read-only reentrancy vector within hours and published a clear explanation of the attack mechanism. They coordinated with the Curve Finance team regarding the underlying vulnerability in Curve's ETH pool implementations.

### Industry Response

The Conic exploit accelerated adoption of reentrancy guards for virtual price queries across the DeFi ecosystem. Protocols that integrated with Curve pools were advised to either implement their own reentrancy detection (checking if the Curve pool is mid-execution before reading virtual price), use cached/time-delayed virtual prices, or wait for Curve's updated pool implementations with built-in read-only reentrancy protection.

Chainlink also published guidance on using their Curve LP price feeds (which incorporate read-only reentrancy detection) rather than directly querying `get_virtual_price()` from Curve pool contracts.

## Technical Analysis

### Read-Only Reentrancy Pattern

Read-only reentrancy is a variant of the classic reentrancy vulnerability where the attacker does not re-enter a state-modifying function but instead reads a state variable (like a price) during a moment when it is temporarily in an inconsistent state. The "read-only" label is somewhat misleading — while the reentrant call itself only reads data, the data it reads is used by the calling protocol to make state-modifying decisions (like calculating withdrawal amounts).

The pattern requires three conditions: a target contract that performs an ETH transfer (or ERC-777/ERC-677 token callback) mid-execution before finalizing its state, a victim protocol that queries a state variable from the target during the callback window, and the state variable being temporarily in an inconsistent/manipulable state during the callback.

In the Curve/Conic case: Curve's `remove_liquidity` transfers ETH (creating a callback opportunity) before its virtual price is fully consistent (LP tokens burned but balance accounting not yet updated). Conic queries the virtual price during the callback. The virtual price is temporarily inflated because the denominator (LP supply) decreased before the numerator (effective balance accounting) caught up.

### Defense: Reentrancy Detection for Price Reads

The primary defense against read-only reentrancy is preventing price reads during the vulnerable window. Approaches include checking if the Curve pool has an active reentrancy lock (indicating it is mid-execution and its price may be inconsistent), using a separate oracle that caches the virtual price outside of any Curve pool execution, implementing a "price staleness" check that compares the current virtual price with a recent historical value and rejects reads that deviate significantly, and using Chainlink Curve LP oracle feeds that incorporate reentrancy detection.

### Comparison with Similar Exploits

The Conic exploit was part of a cluster of read-only reentrancy incidents in 2023. The Vyper compiler reentrancy bug (July 2023) affected multiple Curve pools and compounded the read-only reentrancy risk by enabling direct reentrancy into Curve pool functions that were supposed to be protected by reentrancy locks. Various smaller protocols were exploited through similar Curve virtual price manipulation patterns throughout mid-2023.

## Lessons Learned

### Virtual Price Queries Are Not Safe By Default

Any protocol that queries `get_virtual_price()` from Curve pools (or similar spot-price functions from any protocol with ETH transfers in its execution path) must assume that the returned value may be temporarily manipulated during a reentrancy window. Virtual price queries require either reentrancy detection guards, time-delayed caching, or use of manipulation-resistant oracle feeds.

### ETH Transfers Create Reentrancy Risk for All Readers

Any contract that performs a raw ETH transfer to an arbitrary address creates a potential reentrancy window — not just for itself, but for every other contract that reads its state. This "externalized reentrancy risk" means that security analysis must consider not just whether a contract can be reentered, but whether any other contract that reads its state during the callback window could be exploited. This cross-contract analysis is significantly more complex than traditional single-contract reentrancy evaluation.

### Price Source Isolation

Protocols should isolate their price queries from potential reentrancy windows by caching prices at transaction start (before any external calls), using time-weighted values from previous blocks, or querying dedicated oracle contracts that implement their own reentrancy protections. Direct integration with pool contracts for price information creates coupling between the protocol's security and every possible execution state of the pool contract.

## Conclusion

The Conic Finance read-only reentrancy exploit of July 21, 2023, drained approximately $3.2 million in ETH from the protocol's omnipool by querying Curve's `get_virtual_price()` during a momentary window when the virtual price was inflated due to an in-progress `remove_liquidity` callback. The attacker exploited the gap between the Curve pool's LP token burn (decreasing supply, inflating virtual price) and the completion of the ETH transfer, using the inflated virtual price to overvalue their Conic omnipool position and withdraw more than their fair share. The incident demonstrated that read-only reentrancy — where an attacker doesn't re-enter a state-modifying function but reads temporarily inconsistent state — is a practical and dangerous vulnerability pattern that requires explicit defense in any protocol integrating with Curve or similar pools that perform mid-execution ETH transfers.
