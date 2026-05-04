---
date: 2026-05-05
entities:
  - id: thorchain
    name: THORChain
    type: defi-protocol
  - id: thorchain-bifrost
    name: Bifrost (THORChain)
    type: defi-component
  - id: ethereum
    name: Ethereum
    type: blockchain
title: "THORChain ETH router exploits: deposit event spoofing and $13M multi-incident extraction in July 2021"
---

## Introduction

THORChain is a decentralized cross-chain liquidity protocol that enables native asset swaps across multiple blockchains (Bitcoin, Ethereum, Binance Chain, Litecoin, and others) without wrapped tokens or centralized intermediaries. The protocol operates its own proof-of-stake blockchain built on the Cosmos SDK, with a network of validator nodes (called "Bifrost" nodes) that observe transactions on connected chains and process cross-chain swaps. THORChain's design uses continuous liquidity pools (similar to Bancor's design) where the native RUNE token serves as the intermediary asset in all cross-chain swaps.

In July 2021, THORChain suffered three separate exploit incidents within a two-week period, with the combined extraction totaling approximately $13 million. The most significant of these was the July 23 exploit (approximately $8 million), which exploited a vulnerability in the Ethereum router contract — the smart contract on Ethereum that processed ETH and ERC-20 deposits destined for THORChain. The attacker discovered that the router contract's deposit event could be spoofed by crafting a custom contract that emitted events mimicking legitimate deposits, tricking THORChain's Bifrost observers into crediting the attacker with funds that were never actually deposited. This article focuses primarily on the July 23 router exploit while contextualizing it within the broader pattern of THORChain security incidents during this period.

## Background

### THORChain Cross-Chain Architecture

THORChain's cross-chain swap mechanism operates through a multi-layered system. On each connected blockchain, a "vault" address (controlled by THORChain's validator set through threshold signature schemes) holds the chain's assets. On Ethereum specifically, the vault interacts with users through a "router" smart contract that handles deposit processing, withdrawal execution, and event emission for the Bifrost observer nodes.

When a user wants to swap ETH for BTC (for example), the process flows as follows: the user sends ETH to the THORChain router contract on Ethereum with a memo specifying the desired swap; the router contract processes the ETH deposit and emits a `Deposit` event containing the sender, amount, asset, and memo; THORChain's Bifrost observer nodes (which monitor the Ethereum blockchain for events from the router contract) detect the deposit event and report it to the THORChain blockchain; the THORChain blockchain processes the inbound swap, calculates the output amount based on pool prices and fees, and queues an outbound transaction; a separate Bifrost process executes the outbound transaction on the destination chain (sending BTC to the user's specified address).

The security of this system depends critically on the authenticity of deposit events: if the Bifrost observers can be tricked into reporting deposits that didn't actually occur, the THORChain blockchain will process swaps and send outbound transactions for assets that were never received — effectively printing money for the attacker.

### The Ethereum Router Contract

The THORChain Ethereum router contract served two primary functions: it provided a standardized interface for users to deposit ETH and ERC-20 tokens (with memos that specified swap parameters), and it emitted structured events that the Bifrost nodes used to detect and process deposits. The router was deployed as a simple contract that received ETH (via `payable` functions), transferred ERC-20 tokens to the vault address, and emitted corresponding events.

The router's event structure included the depositor's address, the vault address, the asset being deposited (ETH or a specific ERC-20 token), the amount, and the memo (specifying the swap destination and parameters). The Bifrost observers parsed these events from the Ethereum blockchain and used them as the authoritative source of deposit information.

### Prior THORChain Incidents (July 2021)

The July 23 router exploit was the third in a series of THORChain security incidents that month. On July 15, an attacker exploited a vulnerability in how THORChain processed deposits from the Binance Chain, extracting approximately $140,000. On July 16, a more sophisticated attack exploited THORChain's handling of ERC-20 token deposits, extracting approximately $5 million by depositing worthless custom tokens and tricking the system into treating them as valuable assets. The July 23 attack was the largest and most damaging, exploiting a fundamentally different vector: event spoofing on the Ethereum router.

## The Attack

### Vulnerability: Router Event Trust Without Deposit Verification

The core vulnerability was that THORChain's Bifrost observers trusted events emitted by the router contract as proof of deposit without independently verifying that the corresponding token transfer had actually occurred. The observers' logic was: "if the router contract emitted a Deposit event for X amount of ETH, then X ETH was deposited." This assumption was valid for legitimate deposits processed through the router's intended deposit functions, but it could be violated if an attacker could cause the router to emit deposit events without actually transferring tokens.

The specific exploit mechanism involved the attacker creating a malicious smart contract that, when called by the router during certain execution paths, triggered a re-entrant or callback-based interaction that caused the router to emit a deposit event with attacker-specified parameters. Alternatively (depending on the exact vulnerability version), the attacker exploited the router's handling of ERC-20 token deposits to create deposit events for ETH while actually depositing worthless or minimal amounts.

The key insight was that the router's event emission was not always correctly coupled to actual value transfer — there existed code paths where events could be emitted based on function parameters rather than verified receipt of tokens.

### Attack Execution

The attack on July 23, 2021 proceeded as follows:

**Step 1: Custom contract deployment.** The attacker deployed a malicious smart contract on Ethereum designed to interact with the THORChain router in a way that would trigger deposit events without corresponding value transfer.

**Step 2: Spoofed deposit events.** The attacker called the THORChain router through their malicious contract in a way that caused the router to emit Deposit events indicating large ETH deposits to the vault. These events were technically emitted by the legitimate router contract (so the Bifrost observers would accept them as authentic), but no actual ETH had been transferred to the vault.

**Step 3: Bifrost processing.** THORChain's Bifrost observer nodes detected the spoofed deposit events from the router contract, treated them as legitimate inbound deposits, and reported them to the THORChain blockchain for processing.

**Step 4: Cross-chain outbound execution.** The THORChain blockchain processed the spoofed deposits as swap requests, calculated the corresponding output amounts, and queued outbound transactions. The Bifrost nodes executed these outbound transactions, sending real ETH (from THORChain's Ethereum vault reserves) to the attacker's specified addresses.

**Step 5: Extraction.** The attacker received approximately $8 million in ETH from THORChain's vault — assets that were sent in exchange for deposits that never actually occurred. The attacker then moved the ETH through multiple wallets and mixing services.

### Transaction Analysis

The exploit transactions showed the attacker's contract interacting with the THORChain router contract on Ethereum. The Deposit events emitted during these interactions showed large ETH amounts being deposited to the vault address, but analysis of the actual ETH transfers within those transactions revealed that no corresponding ETH was sent to the vault. The events were "empty" — they declared deposits that hadn't occurred.

## Impact

### Financial Losses

The July 23 router exploit alone resulted in approximately $8 million in losses from THORChain's Ethereum vault. Combined with the July 15 ($140,000) and July 16 ($5 million) incidents, the total extraction in July 2021 was approximately $13 million. These losses came directly from THORChain's liquidity pools — RUNE and ETH deposited by liquidity providers — reducing the protocol's total value locked and the claims of all LP token holders.

### Network Halt

Following the July 23 exploit, the THORChain team halted the network entirely, pausing all swap processing and cross-chain operations. This was the third network halt in two weeks (the previous incidents also triggered pauses), and the extended downtime significantly impacted users who had funds in transit or locked in liquidity pools.

The halt lasted several days while the team investigated the attack vector, developed and tested a fix, and coordinated the network restart with the validator set. During the halt, THORChain liquidity was effectively frozen — LPs could not add or remove liquidity, and pending swaps were queued until the network resumed.

### Confidence Impact

The three exploits in rapid succession severely damaged confidence in THORChain's security model. The protocol's TVL dropped from approximately $300 million before the incidents to under $100 million after the network resumed. The RUNE token price declined by approximately 25% during the incident period, reflecting both the direct losses and the market's reassessment of the protocol's security risk.

The rapid succession of exploits also raised questions about THORChain's security review processes — how could three separate critical vulnerabilities exist simultaneously in a protocol managing hundreds of millions in user funds? The incidents prompted a comprehensive security overhaul that delayed THORChain's planned multi-chain expansion by several months.

## Response and Remediation

### Immediate Response

The THORChain team responded to each incident with network halts to prevent further exploitation. After the July 23 attack, the team published a detailed incident report identifying the router event spoofing vector and outlining the planned fixes. The team also engaged the attacker through on-chain messages, and in a notable development, the attacker returned approximately $2 million of the stolen funds after communication with the team (though retaining the majority).

### Router Contract Redesign

The primary fix was a comprehensive redesign of the Ethereum router contract's deposit handling and event emission logic. Key changes included coupling event emission to verified token receipt (ensuring events were only emitted after confirming that the expected token transfer had occurred), implementing balance-before-and-after checks for all deposit types (ETH and ERC-20), adding an allowlist of acceptable interaction patterns that prevented custom contracts from triggering unexpected event emissions, and implementing an additional layer of Bifrost verification that cross-checked deposit events against actual vault balance changes.

### Bifrost Observer Hardening

Beyond the router contract fix, the Bifrost observer logic was enhanced to independently verify deposits rather than solely trusting contract events. The enhanced observers implemented balance-delta verification (checking that the vault's balance actually increased by the event's claimed amount), event authenticity validation (verifying that events came from expected code paths within the router), rate limiting on inbound deposit processing (bounding the maximum value processed per block), and multi-observer consensus requirements for large deposits (requiring multiple independent observers to confirm before processing).

### Security Program Expansion

THORChain launched an expanded security program including a $500,000 bug bounty through Immunefi (later increased), engagement of multiple independent security auditors for ongoing contract review, the creation of a "security council" that could trigger emergency halts without full validator consensus, and a staged restart process where network capabilities were restored incrementally (swaps for small amounts first, gradually increasing limits).

## Technical Analysis

### Event-Based vs. Balance-Based Deposit Detection

The THORChain exploit highlighted a fundamental design choice in cross-chain bridge architectures: using contract events versus balance changes as the authoritative signal for deposit detection.

Event-based detection (THORChain's original approach) relies on the bridge contract emitting structured events when deposits occur. Observers parse these events and use them to credit depositors. This approach is efficient (events are cheap to emit and parse) and informative (events can include rich metadata like memos and destination addresses). However, it is vulnerable to event spoofing — if the contract can be tricked into emitting events without actual deposits, the system is compromised.

Balance-based detection relies on monitoring the vault address's actual token balance for changes. When the balance increases, a deposit has occurred. This approach is more robust against spoofing (the balance cannot increase without actual token transfer) but provides less information (balance changes don't inherently include memo data or sender information) and may have difficulty distinguishing deposits from other balance-affecting operations (like liquidation proceeds or fee distributions).

The optimal approach — and what THORChain adopted post-exploit — combines both: events provide the rich metadata needed for swap processing, while balance verification ensures that events correspond to actual deposits. Events without corresponding balance changes are rejected.

### Cross-Chain Bridge Trust Models

Cross-chain bridges must solve the "oracle problem" for external chain state: how does the bridge's logic (running on one chain or its own chain) know what happened on another chain? THORChain's approach (observer nodes that watch external chains) is one of several trust models.

Centralized relayers (a small number of trusted parties report cross-chain events) are simple but require trust in the relayers. Decentralized observer networks (THORChain's model, with multiple Bifrost nodes) reduce single-point trust but are still vulnerable if the observed data is spoofable at the source (as in this exploit). Light client verification (the bridge runs a light client of the source chain and directly verifies transactions against the source chain's consensus) provides the strongest guarantees but is expensive and complex to implement. Zero-knowledge proof systems (generating cryptographic proofs of source chain state) provide strong guarantees without the overhead of full light client execution.

The THORChain exploit demonstrated that even a decentralized observer network is only as secure as the data it observes — if the source data (contract events) can be spoofed, consensus among observers provides no additional protection (all observers will agree on the spoofed data).

### Comparison with Other Bridge Event-Spoofing Exploits

The THORChain router exploit belongs to the category of bridge attacks that exploit the gap between what a bridge observes (events, function calls) and what actually occurred (value transfer). Similar incidents include the Poly Network exploit (August 2021, approximately $611 million), where the attacker spoofed cross-chain messages that the bridge validators processed as legitimate, allowing arbitrary fund transfers. While the specific mechanism differed (relay chain message spoofing vs. router event spoofing), the fundamental pattern was the same: tricking the bridge's observation layer into reporting events that didn't reflect actual value transfer.

## Lessons Learned

### Events Are Claims, Not Facts

Smart contract events are assertions made by contract code — they are not independently verifiable facts. Any system that relies on events as the sole source of truth is vulnerable to any code path that can emit events without the expected corresponding state changes. Bridge architectures must treat events as claims that require independent verification (through balance checks, transaction tracing, or cryptographic proofs) rather than as self-authenticating facts.

### Defense in Depth for Bridge Observation

Bridge observer nodes should implement multiple independent verification layers: event parsing (the event was emitted by the expected contract), balance verification (the vault's balance changed by the expected amount), transaction verification (the deposit transaction contains the expected value transfer), and cross-observer consensus (multiple independent observers agree on the deposit details). Only deposits that pass all layers should be processed.

### Security Audit Cadence for Complex Multi-Chain Systems

THORChain's three exploits in two weeks demonstrated that complex multi-chain systems have large attack surfaces that require continuous security review, not point-in-time audits. Each chain integration adds new interaction patterns, new potential failure modes, and new code paths that may not be covered by audits of the core protocol logic. Ongoing security programs (continuous auditing, active bug bounties, red team exercises) are essential for systems operating across multiple chains with different trust models and execution environments.

## Conclusion

The THORChain ETH router exploits of July 2021 extracted approximately $13 million across three incidents, with the largest ($8 million on July 23) achieved through deposit event spoofing — causing the router contract to emit Deposit events that the Bifrost observer nodes processed as legitimate inbound swaps, triggering outbound payments from THORChain's vaults without corresponding actual deposits. The fundamental vulnerability was the system's reliance on contract events as the sole proof of deposit, without independent verification that actual value transfer had occurred. The fix required coupling event emission to verified token receipt and adding balance-delta verification in the Bifrost observer layer, establishing a multi-layered trust model where events are treated as claims requiring independent corroboration rather than self-authenticating facts. The incidents demonstrated that cross-chain bridge security requires defense in depth across every layer — from smart contract logic to observer verification to consensus processing — because any single layer that trusts unverified data from an external chain creates a potential extraction vector.
