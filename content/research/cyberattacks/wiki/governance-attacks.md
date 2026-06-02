---
title: "Governance Attacks"
date: 2026-02-21
description: "How attackers exploit DAO voting mechanisms to seize control of protocols and treasuries."
tags: ["dao", "governance", "flash-loan", "exploit", "security"]
weight: 65
---

# Governance Attacks (DAO Takeovers)

Decentralized Autonomous Organizations (DAOs) rely on token-based voting to make decisions. **Governance Attacks** exploit this mechanism by accumulating enough voting power to pass malicious proposals. These proposals can grant the attacker access to the treasury, the ability to mint infinite tokens, or change critical protocol parameters.

## The Mechanism

In a standard DAO, 1 Token = 1 Vote. If an attacker controls >50% of the voting power (or just more than the quorum/opposition), they control the protocol.

Attackers typically acquire this power in two ways:
1.  **Flash Loans:** Borrowing millions of tokens for a single transaction block to vote on a proposal, then repaying the loan.
2.  **Low Liquidity/Participation:** Buying tokens on the open market for cheap (if the market cap is low) or pushing proposals through when few honest holders are paying attention.

## Famous Case Studies

### 1. Beanstalk Farms (April 2022)
*   **Loss:** ~$182 Million
*   **Mechanism:** Flash Loan Governance Attack
*   **Details:** The attacker used a flash loan to borrow nearly $1 billion in assets (ETH, USDC, DAI). They used these assets to buy enough Bean governance tokens to gain a 67% supermajority.
*   **The Exploit:** With the supermajority, they instantly passed a proposal (BIP-18) that transferred all protocol funds to their own wallet.
*   **Speed:** The entire attack happened in a single transaction. The "Emergency Commit" feature, designed to fix bugs quickly, allowed the proposal to bypass the usual waiting period.

### 2. Build Finance (February 2022)
*   **Loss:** ~$470,000 (plus total protocol control)
*   **Mechanism:** Hostile Takeover via Apathy
*   **Details:** A malicious actor submitted a proposal to give themselves full control over the BUILD token contract (minting rights).
*   **The Failure:** The community failed to vote against it. The proposal passed with a small number of votes because the quorum requirements were loose.
*   **Result:** The attacker minted millions of BUILD tokens, drained liquidity pools on Uniswap and Balancer, and effectively killed the project.

### 3. True Seigniorage Dollar (ESD) & Others
*   **Loss:** Varies by protocol; typically smaller than marquee DAO treasury drains, but enough to wipe out fragile algorithmic stablecoin systems.
*   **Mechanism:** Governance arbitrage via cheaply acquired voting tokens.
*   **Details/Exploit:** In thinly traded governance systems, an attacker can accumulate voting power on the open market at low cost, then use that voting power to approve treasury payouts, emissions changes, or other self-serving proposals worth more than the tokens they bought.
*   **Speed:** Usually slower than flash-loan governance attacks because the attacker has to accumulate tokens over time, but still fast once low-participation governance windows open.

## Prevention and Mitigation

### 1. Flash Loan Guards
*   **Snapshotting:** Voting power should be calculated based on token holdings at a *past block* (e.g., 1 block before the proposal was created), not the current block. This makes flash loans useless for voting, as the attacker didn't hold the tokens in the past.
*   **Time-Locks:** Require a mandatory delay (e.g., 24-48 hours) between a proposal passing and its execution. This gives the community time to react to malicious governance.

### 2. Quorum Requirements
*   **Minimum Quorum:** Ensure a significant percentage of total supply (e.g., 4-10%) must vote for a proposal to pass. This prevents attackers from sneaking proposals through when engagement is low.
*   **Veto Power:** Some DAOs (like Lido or Optimism) have dual-chamber systems or a "Guardian" multisig that can veto clearly malicious proposals during the time-lock period.

### 3. Vote Delegation & Participation
*   Actively encouraging token holders to delegate votes to trusted community members ensures that honest voting power is always online to counter attacks.
