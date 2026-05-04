---
title: "🌰 The DAO — Reentrancy Exploit and the $60M Hack That Split Ethereum"
date: 2026-05-05
entities:
  - The DAO
  - Ethereum
  - Ethereum Classic
  - Slock.it
---

## Summary

1. **On June 17, 2016, an attacker exploited a reentrancy vulnerability in The DAO smart contract**, draining approximately 3.6 million ETH (roughly $50-60 million at the time) from the decentralized investment fund. The attack exploited a recursive calling pattern in the contract's split mechanism that allowed repeated withdrawals before the contract updated internal accounting.
2. **The DAO was one of the largest crowdfunding projects in history at the time**, having raised more than 11 million ETH (roughly $150 million) from about 11,000 investors during its token sale in April-May 2016. The fund represented approximately 14% of all ETH in circulation, making its compromise a systemic risk for the young Ethereum ecosystem.
3. **The Ethereum community responded with a controversial hard fork on July 20, 2016** (block 1,920,000), which moved ETH from The DAO and related child DAO contracts into a recovery contract where DAO token holders could reclaim funds. This decision split the community and the blockchain itself — those who rejected the fork continued on the original chain, which became Ethereum Classic (ETC).
4. **The reentrancy risk had been discussed before the attack**. Researchers had warned about recursive call patterns and The DAO's split mechanics before the exploit, but the deployed contract did not have an upgrade path that could simply patch the vulnerable logic.
5. **The DAO hack and subsequent fork became a defining event in blockchain governance**, establishing precedents for how decentralized communities handle catastrophic smart contract failures. The tension between "code is law" (the immutability principle) and pragmatic intervention to protect users still shapes discussions of blockchain governance and smart contract risk.

## Background

### What Was The DAO?

The DAO (Decentralized Autonomous Organization) was a smart contract on Ethereum designed to function as a decentralized venture capital fund. Built by the Slock.it team, it allowed participants to:

- **Invest**: Send ETH to The DAO contract and receive DAO tokens proportional to their investment
- **Propose**: Submit funding proposals for projects that The DAO would invest in
- **Vote**: Use DAO tokens to vote on funding proposals
- **Split**: If a token holder disagreed with a funding decision, they could "split" from The DAO by creating a "child DAO," withdrawing their proportional share of the fund's ETH

The split mechanism was designed as a minority protection feature — it ensured that token holders who disagreed with the majority could exit with their fair share of the funds rather than being forced to accept investment decisions they opposed.

### The DAO Token Sale

| Parameter | Value |
|-----------|-------|
| Token sale dates | April 30 — May 28, 2016 |
| Total ETH raised | >11 million ETH |
| USD value at close | ~$150 million |
| Number of investors | ~11,000 unique addresses |
| % of total ETH supply | ~14% |
| DAO token exchange rate | 1 ETH = 100 DAO tokens (early), declining ratio later |

The token sale was remarkable for its scale — at the time, it was widely described as the largest crowdfunding project. The concentration of ~14% of all ETH in a single smart contract created a systemic risk that would become apparent during the attack.

### Smart Contract Architecture

The DAO's key functions:

- **`splitDAO`**: The function that allowed token holders to withdraw their proportional ETH by creating a child DAO. This was the function containing the reentrancy vulnerability.
- **`withdrawRewardFor`**: Called during the split process to transfer the user's share of reward balances
- **ETH transfer path**: The value-transfer step that handed control to the recipient before accounting was fully finalized

The critical code path during a split:

1. Calculate the user's proportional ETH share
2. Send the ETH to the user (or their child DAO)
3. Update the user's token balance to zero

The vulnerability was in the ordering: ETH was sent to the user *before* the balance was updated.

## Technical Exploit Mechanics

### Reentrancy: The Core Vulnerability

Reentrancy is a class of vulnerability where an external call in a smart contract allows the called contract to re-enter the calling contract before the first invocation completes. In The DAO's case:

**Normal execution flow (intended)**:
1. User calls `splitDAO`
2. Contract calculates user's ETH share (e.g., 100 ETH)
3. Contract sends 100 ETH to user's address
4. Contract sets user's DAO token balance to 0
5. Function completes

**Attack execution flow (exploited)**:
1. Attacker calls `splitDAO` from a malicious contract
2. Contract calculates attacker's ETH share (e.g., 100 ETH)
3. Contract sends 100 ETH to attacker's malicious contract
4. **Attacker's contract has a fallback function that immediately calls `splitDAO` again**
5. Contract calculates attacker's ETH share again — **balance has not been updated yet**, so it still shows the original amount
6. Contract sends another 100 ETH to attacker
7. Attacker's fallback function calls `splitDAO` again
8. This repeats until the contract runs out of gas or the attacker stops
9. Only after all recursive calls complete does the balance update execute

The key insight: Solidity's `send` or `call` to transfer ETH triggers the recipient's fallback function. If the recipient is a contract, that fallback function can execute arbitrary code — including calling back into the original contract.

### The Attack Sequence

On June 17, 2016, the attacker:

1. **Acquired DAO tokens**: The attacker held DAO tokens (either purchased during the token sale or acquired on secondary markets)
2. **Deployed an attack contract**: A smart contract with a fallback function designed to recursively call `splitDAO`
3. **Initiated the split**: Called `splitDAO` from the attack contract, triggering the reentrancy loop
4. **Drained ETH in batches**: The recursive calls extracted ETH in chunks, limited by the gas limit per transaction. The attacker executed multiple transactions to drain approximately 3.6 million ETH.
5. **Child DAO creation**: The drained ETH was sent to a "child DAO" controlled by the attacker. The DAO's design included a 28-day waiting period before funds in a child DAO could be withdrawn, which created a time window for the community to respond.

### Why The Vulnerability Existed

Several factors contributed to the vulnerability being present in deployed code:

1. **Solidity patterns in 2016**: The checks-effects-interactions pattern (which prevents reentrancy by updating state before making external calls) was not yet a widely known best practice. The DAO was written when Solidity was less than two years old.

2. **Complexity of the split mechanism**: The `splitDAO` function involved multiple steps — token burning, ETH transfer, reward calculation — making the interaction between state updates and external calls non-obvious during review.

3. **Publicly discussed risk**: Recursive-call and "race-to-empty" concerns had been discussed by researchers including Peter Vessenes, who published a warning on June 9, 2016, eight days before the attack. The DAO had no built-in upgrade mechanism that could quickly replace its core deployed logic.

4. **No upgrade mechanism**: The DAO's smart contract was immutable once deployed. Unlike modern upgradeable proxy patterns, there was no way to patch the code without a community-wide Ethereum protocol change.

## The 28-Day Window and Community Response

### Immediate Response (June 17-20)

- **June 17**: The attack was detected by community members monitoring The DAO's ETH balance. The Ethereum Foundation published an advisory.
- **June 17-18**: The "Robin Hood Group" (white hat hackers including DAO curators) used the same reentrancy vulnerability to move remaining funds from The DAO into white hat child DAOs, protecting a large portion of funds from further attacker-controlled drains.
- **June 17**: Ethereum developers began discussing potential protocol-level responses.

### The Fork Debate

The 28-day child DAO waiting period gave the community time to debate options:

**Option 1 — Soft Fork (rejected)**:
- Proposed: Blacklist transactions from the attacker's child DAO address
- Advantage: Less invasive than a hard fork; no state reversal
- Problem: A critical vulnerability was discovered in the soft fork implementation — it could be exploited for a denial-of-service attack. The soft fork was abandoned.

**Option 2 — Hard Fork (implemented)**:
- Proposed: At a specific block number, move affected ETH from The DAO and related child DAOs to a recovery contract
- Advantage: Recovery path for DAO token holders before the attacker-controlled child DAO withdrawal window opened
- Problem: Violated the immutability principle — the blockchain's state would be altered to reverse the consequences of deployed contract behavior

**Option 3 — No intervention**:
- Proposed: Accept the loss as a consequence of the smart contract's behavior
- Advantage: Maintained the "code is law" principle
- Problem: ~14% of all ETH was at risk, creating systemic concerns

### The Hard Fork (July 20, 2016)

The hard fork was implemented at block 1,920,000:
- A special state change moved roughly 12 million ETH from The DAO, Dark DAO, and Whitehat DAO contracts to a withdrawal contract at address `0xbf4ed7b27f1d666546e30d74d50d173d20bca754`
- DAO token holders could call this contract to receive their proportional ETH
- The fork was activated by a majority of miners and nodes upgrading their software

### Ethereum Classic

Not all community members accepted the fork. Those who continued running the pre-fork software maintained the original chain, which became known as Ethereum Classic (ETC):
- ETC preserved the original transaction history, including the attacker's DAO split outcome
- The attacker-controlled DAO outcome remained accessible on the ETC chain
- ETC developed its own community, development roadmap, and market presence
- As of 2026, ETC continues to operate as a separate blockchain with its own token (ETC)

## Market Impact

### Immediate Price Effects

| Metric | Pre-Attack (Jun 16) | During Attack (Jun 17) | Post-Fork (Jul 20) |
|--------|--------------------|-----------------------|-------------------|
| ETH price | ~$20 | ~$11 | ~$12 |
| ETH decline | — | ~45% | ~40% from pre-attack |
| DAO token | ~$0.15 | ~$0.01 | Redeemable for ETH |

The ETH price decline was severe, and market participants attributed the stress to:
- Uncertainty about the fate of 14% of the ETH supply
- Loss of confidence in Ethereum smart contract security
- Selling pressure from holders seeking to exit before potential further exploits
- General market panic in a still-young cryptocurrency ecosystem

### Long-Term Market Effects

1. **Ethereum ecosystem recovery**: Despite the price crash, Ethereum recovered and went on to become a leading smart contract platform. The fork was viewed by many participants as a pragmatic response to an existential threat, while critics treated it as a violation of immutability.

2. **Ethereum Classic market**: ETC maintained a persistent market capitalization, at times reaching billions of dollars. It served as a proof point that blockchain communities can split into durable separate markets over governance disagreements.

3. **Smart contract risk pricing**: The DAO hack changed how the market assessed smart contract risk. Before the hack, many participants treated deployed smart contracts as more trustworthy than the early tooling justified. After it, smart contract auditing became a significant industry.

## Vulnerability Pattern: Reentrancy

### The Reentrancy Attack Template

The DAO established the canonical reentrancy attack pattern:

1. **Identify a function that sends ETH (or calls an external contract) before updating state**
2. **Deploy an attack contract with a fallback/receive function that calls back into the vulnerable function**
3. **Trigger the function from the attack contract**
4. **The recursive calls drain funds until gas is exhausted or the target balance is empty**

### Post-DAO Reentrancy Defenses

The DAO hack drove development of multiple reentrancy defenses:

1. **Checks-Effects-Interactions pattern**: The most fundamental defense — update all state variables before making any external calls. If The DAO had set the user's balance to zero before sending ETH, the recursive call would have calculated a zero balance.

2. **ReentrancyGuard (mutex locks)**: A boolean flag that prevents a function from being called while it is already executing. OpenZeppelin's `ReentrancyGuard` contract became a standard tool.

3. **Pull over push**: Instead of the contract sending ETH to users (push), the contract records the amount owed and users call a separate function to withdraw (pull). This separates the accounting from the transfer.

4. **Solidity and tooling improvements**: The ecosystem increasingly emphasized safer value-transfer patterns, explicit reentrancy guards, and static-analysis tooling. Reliance on gas-stipend assumptions later became discouraged in favor of deliberate accounting and guard patterns.

### Reentrancy Continues to Cause Exploits

Despite being well-known since 2016, reentrancy vulnerabilities continue to appear:

| Incident | Date | Loss | Reentrancy Variant |
|----------|------|------|--------------------|
| The DAO | Jun 2016 | ~$60M | Classic ETH send reentrancy |
| Cream Finance (AMP) | Aug 2021 | ~$18.8M | ERC-777 transfer hook reentrancy |
| Fei Protocol (Rari) | Apr 2022 | ~$80M | Cross-function reentrancy |
| Curve/Vyper | Jul 2023 | ~$70M | Vyper compiler reentrancy lock bug |

Later reentrancy incidents often involved subtler variants — cross-function reentrancy, read-only reentrancy, token-hook reentrancy, or compiler-level reentrancy lock failures — but the fundamental pattern remains the same: an external call allowing state to be accessed before it is safely finalized.

## Governance Precedent

### "Code Is Law" vs. Pragmatic Intervention

The DAO fork established the central tension in blockchain governance:

**Code Is Law position**:
- Smart contracts execute as written; the attacker exploited the contract's actual behavior, not a consensus bug in the EVM
- Reversing transactions based on subjective judgments about intent undermines the trustless nature of the blockchain
- If the community forks to reverse one exploit, where does it stop? Future hacks can create pressure for intervention
- The minority who continued with Ethereum Classic held this position

**Pragmatic Intervention position**:
- The scale of The DAO's ETH concentration (~14% of all ETH) represented a systemic risk to the young Ethereum ecosystem
- The 28-day waiting period provided a unique opportunity to act before funds became irreversible
- The community made a democratic decision (miners and node operators chose which chain to follow)
- Protecting users from catastrophic loss was more important than adhering strictly to an abstract principle

### Impact on Subsequent Governance Decisions

- **Parity freeze (2017)**: When ~$150M in ETH was frozen in Parity wallets, proposals to fork for recovery (including EIP-999) did not achieve consensus — the community had moved toward a more conservative position on state interventions
- **DeFi exploits (2020+)**: Later DeFi exploits generally have not prompted Ethereum protocol-level forks for fund recovery. The DAO fork is usually treated as a historically specific event tied to Ethereum's early stage of development

## Lessons for Market Surveillance

1. **Reentrancy pattern detection**: Automated analysis of smart contract bytecode for reentrancy vulnerabilities remains essential. Surveillance systems should flag deployed contracts that perform external calls before state updates, especially in withdrawal or split functions that transfer value.

2. **Concentration risk monitoring**: The DAO held ~14% of all ETH — an extreme concentration of value in a single contract. Surveillance systems should track the percentage of a token's supply held in individual contracts and flag concentrations that represent systemic risk (e.g., >5% of circulating supply).

3. **Time-lock exploitation windows**: The DAO's 28-day child DAO waiting period created a window for response. Surveillance systems should track time-locked funds in exploited protocols, as these windows determine whether recovery actions are possible.

4. **Fork risk assessment**: When a protocol-level fork is proposed, the market impact can be significant. Monitoring for fork proposals and their community reception provides trading-relevant intelligence.

5. **Pre-exploit disclosure monitoring**: The reentrancy risk was publicly discussed before the attack. Surveillance systems that aggregate and assess published vulnerability disclosures for deployed contracts can provide early warning of elevated exploit risk.

6. **White hat response coordination**: The Robin Hood Group's counter-drain was coordinated informally. Surveillance systems should monitor for large, rapid outflows from compromised contracts that may represent white hat rescue operations rather than additional attacker activity, while avoiding premature attribution.

## References

1. Ethereum Foundation. "DAO Hard Fork." Ethereum Blog, July 2016.
2. Vessenes, Peter. "More Ethereum Attacks: Race-To-Empty is the Real Deal." Peter Vessenes Blog, June 9, 2016.
3. Siegel, David. "Understanding The DAO Attack." CoinDesk, June 25, 2016.
4. Meier, Christoph. "Scanning Live Ethereum Contracts for the 'Unchecked-Send' Bug." ACM Digital Library, 2016.
5. Atzei, Nicola, Massimo Bartoletti, and Tiziana Cimoli. "A Survey of Attacks on Ethereum Smart Contracts." IACR Cryptology ePrint Archive, 2017.
6. Rekt News. "The DAO — The Original REKT." rekt.news.
7. Ethereum Classic. "Declaration of Independence." ethereumclassic.org, 2016.
