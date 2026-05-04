---
date: 2026-05-05
entities:
  - id: templedao
    name: TempleDAO
    type: defi-protocol
  - id: ethereum
    name: Ethereum
    type: blockchain
title: "TempleDAO STAX migrateStake exploit: missing access control and $2.3M unauthorized fund extraction"
---

## Introduction

TempleDAO was a decentralized finance protocol on Ethereum that provided yield-generating strategies through its staking and vault infrastructure. The protocol's ecosystem included TEMPLE (its governance and utility token), various staking contracts, and the STAX product — a liquid staking aggregator designed to provide optimized yield access for TEMPLE holders. The STAX contracts allowed users to stake TEMPLE tokens in exchange for xTEMPLE (a yield-bearing derivative) and facilitated migrations between different staking positions as the protocol evolved its product offerings.

On October 11, 2022, an attacker exploited a critical access control vulnerability in TempleDAO's STAX staking migration contract, extracting approximately $2.3 million worth of TEMPLE and stablecoin tokens from the protocol's staking pools. The vulnerability was a missing authorization check on the `migrateStake` function, which allowed any external caller to initiate a stake migration on behalf of any user, directing the migrated funds to an attacker-controlled address.

## Background

### TempleDAO Protocol Architecture

TempleDAO launched in early 2022 as a DeFi protocol focused on providing accessible yield generation with a "temple" theme. The protocol centered around the TEMPLE token (an ERC-20 governance token) and offered various staking mechanisms where users could lock TEMPLE tokens to earn yield in the form of additional TEMPLE emissions and protocol revenue distributions.

The protocol's architecture included several key components: the TEMPLE token contract, OGTemple (a wrapped version representing original staked positions), staking vaults that accepted TEMPLE deposits and distributed rewards, and the STAX product — a more recent addition designed to aggregate yield across DeFi protocols for TEMPLE holders.

### STAX Staking Migration System

As TempleDAO evolved its product offerings, it needed mechanisms to migrate user positions between legacy staking contracts and newer STAX contracts. The migration system was implemented through a dedicated migration contract that could move staked TEMPLE from one vault to another on behalf of users, converting their positions from legacy staking to the new STAX format.

The migration contract contained a `migrateStake` function that performed the following operations: withdraw tokens from the source staking contract on behalf of a specified user, transfer those tokens to a destination address, and optionally re-stake them in the new staking contract. This function was designed to be called by an authorized migration operator (the TempleDAO team or a governance-approved migration bot) to facilitate batch migrations or user-initiated migrations through a controlled interface.

### The Access Control Gap

The critical flaw was that the `migrateStake` function lacked proper access control modifiers. While the function was intended to be called only by authorized parties (the TempleDAO team's migration operator address), the actual Solidity implementation did not include an `onlyOwner`, `onlyOperator`, or equivalent access control check. This meant any Ethereum address could call the function and specify arbitrary parameters, including the target user whose stake would be migrated and the destination address for the withdrawn funds.

## The Attack

### Vulnerability: Unrestricted migrateStake Function

The core vulnerability was a missing access control check on the STAX staking migration contract's `migrateStake` function. In Solidity, access control is typically enforced through modifiers like `onlyOwner` or role-based access control (RBAC) patterns from libraries like OpenZeppelin's AccessControl. The TempleDAO migration contract omitted these protections, making the function callable by any external address.

The vulnerable function signature effectively allowed any caller to specify:
- The user address whose stake should be migrated (the victim)
- The amount of staked tokens to withdraw
- The destination address for the withdrawn tokens (the attacker's address)

Without access control, this was equivalent to giving any Ethereum user the ability to withdraw any other user's staked tokens to an arbitrary address — a complete bypass of the protocol's custody guarantees.

### Attack Execution

The attack on October 11, 2022, proceeded through a straightforward exploitation of the unprotected function:

**Step 1: Target identification.** The attacker identified staking contracts with significant TEMPLE token deposits and confirmed that the `migrateStake` function lacked access control by reading the contract's bytecode and ABI on Etherscan.

**Step 2: Stake extraction.** The attacker called the `migrateStake` function on the STAX staking migration contract, specifying the staking vault as the source, the vault's total balance as the amount, and the attacker's own address as the destination. Because no access control check was present, the transaction succeeded.

**Step 3: Repeated extraction.** The attacker repeated this process across multiple staking vaults and user positions within the TempleDAO STAX ecosystem, systematically draining staked TEMPLE tokens from each contract that referenced the vulnerable migration function.

**Step 4: Token conversion.** After extracting TEMPLE tokens, the attacker swapped them for stablecoins (primarily FRAX and DAI) through decentralized exchanges, realizing approximately $2.3 million in value before the TEMPLE token price crashed due to the sell pressure and market panic.

### Transaction Details

The exploit was executed through a series of transactions from the attacker's address. The primary exploit transaction called `migrateStake` with parameters directing the staking vault's entire TEMPLE balance to the attacker's wallet. The simplicity of the attack — a single function call with no flash loans, no complex contract interactions, no mathematical manipulation — made it one of the most straightforward DeFi exploits in terms of technical complexity, despite its significant financial impact.

## Impact

### Financial Losses

The total value extracted was approximately $2.3 million, primarily in TEMPLE tokens that were subsequently sold for stablecoins. The loss was distributed across all users who had staked TEMPLE in the affected STAX vaults. Individual losses varied based on the amount of TEMPLE each user had staked in the vulnerable contracts.

Following the exploit, the TEMPLE token price dropped significantly as the attacker liquidated stolen tokens through decentralized exchanges. This secondary market impact caused additional unrealized losses for TEMPLE holders who were not directly affected by the exploit but suffered from the token's price depreciation.

### Protocol Response

TempleDAO's team responded immediately after detecting the exploit. They paused all remaining staking contracts to prevent further extraction, published a post-mortem identifying the missing access control as the root cause, engaged blockchain security firms to assist with fund recovery efforts, and implemented a compensation plan for affected stakers.

The team also reached out to the attacker through on-chain messages, offering a bounty for the return of funds. A portion of the stolen funds (approximately $550,000) was eventually returned through negotiation, though the majority of the extracted value was not recovered.

### Market Confidence Impact

The exploit significantly damaged confidence in TempleDAO's smart contract security practices. The simplicity of the vulnerability — a basic access control omission that would be caught by standard security review processes — raised questions about the protocol's development and audit procedures. The TEMPLE token's market capitalization declined substantially in the weeks following the exploit, reflecting reduced confidence in the protocol's security and governance.

## Technical Analysis

### Access Control Patterns in DeFi

The TempleDAO exploit highlights the critical importance of access control in DeFi smart contracts. Access control determines who can call specific functions and is the primary mechanism by which smart contracts enforce their intended behavior. Common access control patterns in Solidity include:

**Owner-based control**: Using OpenZeppelin's `Ownable` contract, which provides an `onlyOwner` modifier restricting function access to a single privileged address. This is suitable for administrative functions that should only be callable by the protocol team or a governance contract.

**Role-based access control (RBAC)**: Using OpenZeppelin's `AccessControl` contract, which allows defining multiple roles with different permissions. This provides more granular control — for example, a "MIGRATOR_ROLE" that could be granted only to approved migration operator addresses.

**Multi-signature requirements**: Requiring multiple authorized signers to approve a transaction before it executes, typically through a Gnosis Safe or similar multi-sig wallet. This provides security against single key compromise.

The TempleDAO migration contract used none of these patterns, leaving the `migrateStake` function completely unrestricted. This is equivalent to leaving a bank vault door unlocked — the function's parameters allowed specifying which user's funds to move and where to send them, and without access control, anyone could act as the operator.

### Comparison with Similar Access Control Exploits

The TempleDAO exploit belongs to a category of DeFi vulnerabilities where missing or insufficient access control on privileged functions allows unauthorized fund extraction. Similar incidents include:

**Poly Network (August 2021, ~$611M)**: While mechanistically more complex (involving cross-chain message forgery), the root cause was similar — the attacker gained the ability to call a privileged function (`putCurEpochConPkBytes`) that should have been restricted to authorized validators, allowing them to replace the validator set and authorize arbitrary cross-chain transfers.

**Punk Protocol (August 2021, ~$8.9M, returned)**: The deployer accidentally left an initialization function unprotected, allowing the attacker to call `initialize` and set themselves as the contract owner, then drain funds. The access control vulnerability was on an initialization function rather than an operational function, but the pattern is identical.

**Furucombo (February 2021, ~$14M)**: A proxy authorization vulnerability allowed the attacker to set themselves as an authorized implementation contract, enabling them to execute arbitrary operations through the proxy. While the mechanism was proxy-specific, the core issue was insufficient access control on who could designate authorized implementations.

### Why the Vulnerability Was Not Caught

Several factors contributed to this access control vulnerability surviving through development and deployment:

**Incremental development**: The migration contract was likely developed incrementally as the STAX product evolved. Access control may have been planned for a later implementation phase, or the function may have been initially intended as internal/private but was inadvertently left public.

**Testing blind spots**: Unit tests for migration functions likely tested the happy path (correct inputs produce correct outputs) without testing the negative case (unauthorized callers should be rejected). This is a common testing gap — developers test what should work rather than what should fail.

**Audit coverage**: If the migration contract was deployed without audit, or if it was deployed after an audit that covered only the core staking logic, the access control gap could have been introduced in post-audit code changes. Many DeFi exploits occur in contracts that were added or modified after the formal security audit.

### Severity Assessment

Despite its technical simplicity, the TempleDAO access control vulnerability was critical in severity because:
- It required no capital, flash loans, or complex transaction sequencing to exploit
- It affected all users with funds in the vulnerable staking contracts
- It could be exploited repeatedly across multiple contracts referencing the same migration function
- The exploitation window was open from the moment of deployment until the team paused contracts
- No on-chain monitoring or circuit breakers could prevent the exploit once initiated

The simplicity of exploitation is itself a risk factor — more complex vulnerabilities (flash loan attacks, oracle manipulation) require attacker sophistication and capital, creating natural barriers to exploitation. A missing access control check can be exploited by anyone who reads the contract code and understands basic Ethereum transaction construction.

## Lessons Learned

### Access Control as a Non-Negotiable Security Primitive

The most fundamental lesson from the TempleDAO exploit is that access control on privileged functions is not optional. Any function that can move, withdraw, or transfer user funds must have explicit authorization checks. This applies to:
- Migration functions (as in TempleDAO)
- Administrative functions (pause, unpause, upgrade)
- Emergency withdrawal functions
- Configuration changes (setting oracle addresses, fee parameters)
- Any function that operates on behalf of other users

The access control check should be the first thing verified in code review for any privileged function, before considering business logic correctness.

### Automated Access Control Verification

Protocols should implement automated tools to verify access control coverage. This includes static analysis tools (Slither, Mythril) that can flag public/external functions without access control modifiers, automated test suites that explicitly test unauthorized caller rejection for every privileged function, and deployment checklists that require access control verification before mainnet deployment.

### Defense in Depth for Migration Functions

Migration functions are inherently high-risk because they move funds between contracts. Defense-in-depth measures for migration functions include: access control restricting who can initiate migrations, time-locks requiring a delay between migration initiation and execution (allowing users to opt out), per-user migration approval requiring each user to explicitly authorize their own migration, amount limits capping how much can be migrated in a single transaction or time period, and monitoring alerts for unexpected migration activity.

### Post-Audit Code Change Management

Protocols must maintain security review discipline for all code changes made after formal audits. The common pattern of "audit the core contracts, then add utility/migration contracts without review" creates exactly the kind of gap that the TempleDAO exploit targeted. Every contract that touches user funds, regardless of when it was developed relative to the audit timeline, requires equivalent security scrutiny.

## Conclusion

The TempleDAO STAX migration exploit of October 11, 2022, extracted approximately $2.3 million through the simplest possible DeFi vulnerability: a missing access control check on a function that could move user funds. The `migrateStake` function, intended to be restricted to authorized migration operators, was deployed without any access control modifier, allowing any Ethereum address to call it with arbitrary parameters — including specifying other users' staked tokens as the source and the attacker's address as the destination. The exploit required no flash loans, no oracle manipulation, no mathematical tricks — only reading the contract code and calling an unprotected function. This incident demonstrates that the most dangerous vulnerabilities in DeFi are often the simplest: not novel attack vectors requiring deep mathematical insight, but basic security hygiene failures that would be caught by standard development practices, automated analysis tools, and thorough code review. Access control on privileged functions remains the most fundamental security requirement in smart contract development, and its absence represents a critical failure regardless of the sophistication of other protocol components.
