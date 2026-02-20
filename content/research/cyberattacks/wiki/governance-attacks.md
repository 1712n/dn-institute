---
title: "Governance Attacks"
description: "An examination of how on-chain governance mechanisms can be weaponized, often using flash loans, to execute hostile takeovers and steal protocol funds."
---

Decentralized Autonomous Organizations (DAOs) are governed by token holders who vote on proposals. While this model is intended to be decentralized, it can be exploited if an attacker can acquire sufficient voting power, even for a brief moment.

## The Mechanism of Governance Attacks

The core vulnerability in many early governance models was the failure to account for flash loans—the ability to borrow massive amounts of cryptocurrency for the duration of a single atomic transaction.

*   **Flash Loan Governance:** An attacker borrows millions of dollars worth of a protocol's governance token. Because they hold the tokens within the same transaction that a vote is called, they can single-handedly meet the quorum and vote to pass a malicious proposal.
*   **Malicious Proposal Payload:** The proposal submitted by the attacker contains code to perform a hostile action, such as transferring the entire protocol treasury to their own address, minting infinite tokens, or changing critical protocol parameters to their benefit.
*   **Timelock Bypass:** Often, these attacks are paired with an exploit of an "emergency" function that allows a proposal with supermajority support to bypass the standard timelock (a safety-delay period), enabling the attack to be executed instantly.

## Case Studies

### 1. Beanstalk Farms ($182M) - Flash Loan Governance

*   **Vector:** The attacker executed a flash loan to acquire a supermajority of the STALK governance token.
*   **Impact:** In the same transaction, they submitted and passed a proposal (BIP-18) that transferred all of the protocol's collateral assets to their address. They then paid back the flash loan and walked away with the profit.
*   **Lesson:** Governance systems must be flash-loan resistant. Voting power should be based on a snapshot of balances from a past block, not the current block.

### 2. Tornado Cash ($1.2M) - Proposal Hijacking

*   **Vector:** An attacker submitted a proposal that appeared benign, but contained a hidden `selfdestruct` call within its logic. When the proposal was passed by the legitimate community, this logic transferred control of the governance contract to the attacker.
*   **Impact:** The attacker gained full control of the governance, granting themselves 1.2 million TORN tokens and draining the tokens held in the governance vault.
*   **Lesson:** Proposal code must be audited as rigorously as core protocol code. Social consensus is not a substitute for technical due diligence.

### 3. Build Finance ($470k) - Hostile Takeover

*   **Vector:** A single entity with deep pockets accumulated enough of the BUILD governance token on the open market to unilaterally control the DAO's governance.
*   **Impact:** The attacker passed a proposal that gave them control over the minting keys, created an infinite supply of tokens, and drained the liquidity pools.
*   **Lesson:** DAOs with low-market-cap tokens and low quorum requirements are highly susceptible to hostile takeovers if token distribution is not sufficiently decentralized.
