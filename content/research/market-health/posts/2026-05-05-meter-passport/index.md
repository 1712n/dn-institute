---
date: 2026-05-05
entities:
  - id: meter-passport
    name: Meter Passport
    type: defi-protocol
  - id: meter-network
    name: Meter Network
    type: blockchain
  - id: moonriver
    name: Moonriver
    type: blockchain
title: "Meter Passport bridge exploit: deposit handler bypass and $4.4M wrapped token inflation across Moonriver and BSC"
---

## Introduction

Meter Passport was a cross-chain bridge protocol developed by the Meter Network team that facilitated token transfers between Ethereum, Binance Smart Chain (BSC), Moonriver, Theta, and other EVM-compatible blockchains. The bridge operated using a relay-and-lock model where tokens deposited on one chain were locked in a bridge contract, and corresponding wrapped tokens were minted on the destination chain. Validators in the Meter relay network monitored deposit events on source chains and submitted attestations to the destination chain, triggering the minting of wrapped tokens when sufficient validator consensus was reached.

On February 5, 2022, an attacker exploited a vulnerability in Meter Passport's deposit handler contract, bypassing the intended deposit logic to create fraudulent deposit events that were processed by the bridge's relay validators. The exploit allowed the attacker to mint unbacked wrapped tokens on Moonriver and BSC without actually locking the corresponding native tokens on the source chain, effectively creating value from nothing. The total extraction was approximately $4.4 million, drained primarily from liquidity pools on Moonriver where the attacker sold the fraudulently minted wrapped tokens for legitimate assets.

## Background

### Cross-Chain Bridge Architecture

Cross-chain bridges in 2022 primarily operated using one of three models: lock-and-mint (tokens locked on source chain, wrapped tokens minted on destination), burn-and-mint (tokens burned on source chain, native tokens released on destination), or liquidity pool (tokens swapped between independent pools on each chain). Meter Passport used the lock-and-mint model, where the bridge held locked tokens on the source chain as backing for the wrapped tokens circulating on destination chains.

The security of lock-and-mint bridges depends critically on two properties: that deposit events are authentic (tokens were actually deposited on the source chain before minting occurs on the destination), and that deposit events are not double-processed (each deposit triggers exactly one mint). Violations of either property — fraudulent deposits or double-minting — result in unbacked wrapped tokens that dilute the value of legitimately-minted wrapped tokens.

### Meter Passport's Deposit Handler

Meter Passport's bridge contracts included a deposit handler responsible for processing incoming deposits on the source chain. When a user wanted to bridge tokens from Chain A to Chain B, they called the bridge contract's deposit function on Chain A. The deposit handler would verify the deposit parameters (token type, amount, destination chain), transfer the deposited tokens from the user to the bridge contract (locking them), and emit a deposit event that the relay validators would detect and process.

The deposit handler implemented special logic for handling native chain tokens (ETH on Ethereum, BNB on BSC). Because native tokens are not ERC-20 tokens and cannot be transferred via `transferFrom`, the handler needed to wrap them (converting ETH to WETH, BNB to WBNB) before locking them in the bridge. This wrapping logic was handled in a separate code path from standard ERC-20 deposits.

### The Vulnerability Context

The vulnerability was introduced during a contract upgrade that modified how the deposit handler processed native token (ETH/BNB) deposits. The upgrade introduced a code path that could be triggered to emit a deposit event without actually transferring or locking the corresponding tokens. This effectively allowed an attacker to "announce" a deposit to the relay validators without actually making one.

## The Attack

### Vulnerability: Native Token Deposit Bypass

The core vulnerability was in the deposit handler's logic for processing native token deposits. The contract had a function that was intended to handle deposits of wrapped native tokens (WETH, WBNB), but due to a logic error in the updated code, calling this function with the native token's wrapper address did not properly enforce that the caller had actually transferred tokens to the bridge contract.

Specifically, the deposit handler's updated code path for wrapped native tokens checked the deposit amount against `msg.value` (the ETH/BNB sent with the transaction) for native deposits, but when the deposit was made using the wrapped ERC-20 version (WETH/WBNB), the handler accepted the transaction without verifying that the corresponding `transferFrom` had actually moved tokens from the caller to the bridge contract. The handler emitted the deposit event based on the requested amount rather than the actually-received amount.

This meant an attacker could call the deposit function claiming to deposit a large amount of WETH/WBNB, without actually transferring any tokens, and the bridge would emit a deposit event for the claimed amount. The relay validators, trusting the deposit event as authentic, would then mint the corresponding wrapped tokens on the destination chain.

### Attack Execution

The attack was executed on February 5, 2022, targeting the Moonriver deployment:

**Step 1: Fraudulent deposit event creation.** The attacker called the Meter Passport bridge deposit function on the source chain (Ethereum or BSC), specifying a large deposit amount of WETH/WBNB but exploiting the handler bypass to avoid actually transferring any tokens. The bridge contract emitted a deposit event for the full claimed amount despite receiving no tokens.

**Step 2: Relay processing.** The Meter Passport relay validators detected the deposit event on the source chain. Because the validators relied on the deposit event emission (from the trusted bridge contract) as proof of deposit, they processed the event as legitimate and submitted a mint attestation to the destination chain (Moonriver).

**Step 3: Wrapped token minting.** On Moonriver, the bridge contract minted wrapped tokens (meterBNB, meterETH) to the attacker's address based on the relay validators' attestation. These wrapped tokens were created without corresponding locked backing on the source chain — they were effectively unbacked.

**Step 4: Liquidity extraction.** The attacker sold the fraudulently minted wrapped tokens on Moonriver DEXes (primarily SolarBeam and Zenlink), exchanging them for legitimate tokens like MOVR (Moonriver's native token), USDC, and other assets. The liquidity providers in these DEX pools received worthless unbacked wrapped tokens in exchange for their legitimate assets.

**Step 5: Cross-chain movement.** The attacker bridged the extracted legitimate assets back to Ethereum mainnet or other chains, converting them to ETH for laundering through Tornado Cash.

### Affected Tokens and Chains

The primary impact was on Moonriver, where the attacker minted approximately $4.4 million worth of unbacked wrapped tokens. The meterBNB and meterETH tokens on Moonriver lost their intended 1:1 backing with BNB and ETH respectively, becoming fractionally backed. Liquidity providers on Moonriver DEXes who had paired legitimate assets with meter-wrapped tokens suffered the most direct losses.

A smaller portion of the attack also targeted BSC, where similar unbacked wrapped tokens were created, though the extraction on BSC was less significant than on Moonriver.

## Impact

### Financial Losses

The total financial impact was approximately $4.4 million, distributed across liquidity providers on Moonriver DEXes who traded legitimate assets for unbacked meter-wrapped tokens. Individual losses varied based on the size of liquidity positions and the timing of the exploit relative to pool interactions.

The Meter-wrapped tokens on Moonriver (meterBNB, meterETH) became partially unbacked, meaning they were worth less than the 1:1 peg they were designed to maintain. Users holding these wrapped tokens faced an immediate devaluation as the market priced in the fractional backing.

### Cascading Impact on Moonriver DeFi

Because Meter Passport's wrapped tokens were widely used as base assets in Moonriver DeFi (as collateral in lending protocols, as paired assets in liquidity pools, and as inputs for yield strategies), the exploit had cascading effects across the Moonriver ecosystem. Lending protocols that accepted meter-wrapped tokens as collateral faced potential bad debt. DEX pools paired with meter-wrapped tokens experienced sudden impermanent loss. Yield strategies that deposited into pools containing meter-wrapped tokens suffered losses.

The incident temporarily destabilized the Moonriver DeFi ecosystem and prompted a broader reassessment of which bridged tokens were safe to integrate as base assets in DeFi protocols.

### Bridge Security Narrative

The Meter Passport exploit occurred during a period of intense bridge exploits — Wormhole ($320M, February 2022), Ronin Bridge ($625M, March 2022), and Nomad Bridge ($190M, August 2022) all occurred within the same year. The Meter exploit, while smaller in scale, contributed to the growing narrative that cross-chain bridges represented the weakest link in the multi-chain DeFi ecosystem and that bridge deposits/mints required multiple layers of validation beyond trusting a single smart contract event.

## Response and Remediation

### Immediate Response

The Meter team detected the exploit within hours and immediately paused the bridge's relay validators, preventing any further processing of fraudulent deposit events. They identified the vulnerable code path in the deposit handler and published a preliminary incident report within 24 hours.

The team coordinated with Moonriver DEX protocols (SolarBeam, Zenlink) to alert users about the unbacked wrapped tokens and advise against trading or providing liquidity for the affected tokens.

### Compensation

The Meter Network team committed to fully compensating affected users from the project's reserves and team funds. The compensation was paid over several weeks, with priority given to liquidity providers who had directly received unbacked tokens in exchange for legitimate assets. The total compensation was approximately $4.4 million, representing full reimbursement of losses at the time of the exploit.

The full compensation was notable and contributed positively to the Meter team's reputation, as many bridge exploits of 2022 resulted in partial or no compensation for affected users.

### Contract Fix

The fix addressed the deposit handler's native token wrapping logic by ensuring that all deposit paths verified actual token receipt before emitting deposit events. The specific changes included adding a balance-before-and-after check for all ERC-20 deposits (including wrapped native tokens), verifying that `msg.value` matched the claimed deposit amount for all native token deposits, implementing an additional relay-side validation that checked source chain balances against total minted amounts (a belt-and-suspenders defense), and adding rate limits on the relay validators' minting authority to bound the maximum damage from any future bypass.

### Bridge Monitoring Improvements

Beyond the contract fix, the Meter team implemented enhanced monitoring for the bridge's relay infrastructure. New checks included real-time comparison of total minted wrapped tokens against total locked source tokens (a "proof of reserves" check), automated alerts when deposit events were emitted without corresponding token transfers (detected by monitoring source chain balance changes), and a challenge period for large deposits where minting was delayed by a configurable time window, allowing human review of unusual transactions.

## Technical Analysis

### Deposit Handler Validation Hierarchy

Bridge deposit handlers must validate three properties for every deposit: authentication (the caller is authorized to deposit), amount verification (the claimed amount matches the actually-received tokens), and event integrity (the emitted event accurately reflects the validated deposit). The Meter Passport vulnerability broke the second property — amount verification — for a specific code path (wrapped native tokens).

Proper amount verification for ERC-20 deposits requires measuring the contract's token balance before and after the `transferFrom` call and using the difference as the verified deposit amount (not the user-claimed amount). This pattern accounts for fee-on-transfer tokens, rebasing tokens, and any other token behavior that might cause the received amount to differ from the requested amount.

For native token deposits, verification is simpler: `msg.value` is the authoritative amount (it is enforced by the EVM itself). The vulnerability arose in the hybrid case where the deposit was denominated in the wrapped native token (an ERC-20) but the handler confused the validation paths between native and ERC-20 processing.

### Relay Trust Model

Meter Passport's relay validators operated on a trust-the-event model: if the bridge contract (a trusted on-chain entity) emitted a deposit event, the validators processed it without independent verification of the underlying token transfer. This trust model is common in bridge architectures but creates a single point of failure: if the bridge contract can be tricked into emitting a fraudulent event (as in this exploit), the relay has no independent means of detecting the fraud.

More robust relay architectures implement additional validation layers. Some bridges require the relay to independently verify that the source chain's token balance increased by the claimed deposit amount (not just that an event was emitted). Others implement a fraud proof mechanism where third parties can challenge fraudulent mints within a window. The most secure designs use zero-knowledge proofs to cryptographically verify the source chain state, though these were not practically available at the time of the Meter exploit.

### Comparison with Other Bridge Deposit Bypasses

The Meter Passport exploit belongs to a specific subcategory of bridge exploits: deposit handler bypasses. Similar incidents include the Qubit Finance bridge exploit (January 2022, approximately $80 million on BSC), where the attacker bypassed the deposit verification on the Ethereum side to mint unbacked QBT on BSC without actually depositing ETH. The mechanism was similar: a deposit handler that emitted events based on user-claimed amounts rather than verified transfers.

The Wormhole exploit (February 2022, approximately $320 million) used a different mechanism (forging guardian signatures through an uninitialized proxy) but achieved the same end result: minting wrapped tokens without corresponding locked backing.

These incidents collectively demonstrated that bridge deposit verification is the most critical security component in cross-chain architectures: any bypass of deposit verification allows unbacked token creation, which is equivalent to counterfeiting money.

## Lessons Learned

### Verify Actual Token Receipt, Not Claimed Amounts

The most direct lesson is that bridge deposit handlers must verify actual token receipt (by measuring balance changes) rather than trusting user-claimed deposit amounts or assuming that calling `transferFrom` necessarily results in the expected transfer. This applies to all deposit paths — ERC-20, native, and wrapped native — without exception.

### Separate Native and ERC-20 Handling Clearly

The vulnerability arose at the boundary between native token handling and ERC-20 handling, where the hybrid code path for wrapped native tokens (WETH/WBNB) fell between the two validation models. Bridge contracts should implement clearly separated, independently audited code paths for native token deposits and ERC-20 deposits, with no shared logic that could create confusion about which validation applies.

### Defense in Depth for Bridge Minting

A bridge's minting authority should not rely solely on the deposit handler's event emission. Relay validators should independently verify deposits by checking source chain balances, implement challenge/dispute periods for large mints, and maintain running totals that track total minted vs. total locked as an ongoing invariant check. Multiple independent validation layers ensure that a single-point failure (like the deposit handler bypass) cannot result in unbacked token creation.

### Rate Limit Critical Operations

Even with all validation in place, bridges should implement rate limits on minting that bound the maximum value that could be extracted from any single vulnerability. A per-block or per-hour minting cap ensures that if a bypass is discovered, the maximum loss is bounded by the rate limit rather than the total locked value.

## Conclusion

The Meter Passport bridge exploit of February 5, 2022, resulted in the creation of approximately $4.4 million in unbacked wrapped tokens on Moonriver through a deposit handler bypass that allowed fraudulent deposit events to be emitted without actual token transfers. The vulnerability — a logic error in the native token wrapping code path that failed to verify actual token receipt — enabled the attacker to "announce" deposits to the relay validators without locking any backing tokens, causing the validators to mint unbacked wrapped tokens on the destination chain. The attacker sold these unbacked tokens on Moonriver DEXes, extracting legitimate assets from liquidity providers. The incident demonstrated that bridge deposit verification is the most critical security property in cross-chain architectures: any bypass creates the ability to mint unbacked tokens (effectively counterfeit value), and relay validators that trust contract events without independent verification inherit the bridge contract's vulnerability surface. The fix required implementing balance-based verification for all deposit paths and adding relay-side independent validation as a defense-in-depth measure against future deposit handler bypasses.
