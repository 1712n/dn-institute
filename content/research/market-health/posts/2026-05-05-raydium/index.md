---
date: 2026-05-05
entities:
  - id: raydium
    name: Raydium
    type: defi-protocol
  - id: solana
    name: Solana
    type: blockchain
title: "Raydium AMM admin key compromise: privileged withdrawal of $4.4M from Solana liquidity pools"
---

## Introduction

Raydium is one of the largest automated market maker (AMM) protocols on the Solana blockchain, providing liquidity infrastructure for decentralized token trading. The protocol operates concentrated liquidity pools and constant product pools, serving as a core piece of Solana's DeFi infrastructure with hundreds of millions of dollars in total value locked. Raydium's smart contracts (programs in Solana terminology) manage liquidity pool reserves, process swaps, and handle liquidity provider (LP) deposits and withdrawals through on-chain program logic.

On December 16, 2022, an attacker exploited compromised admin/owner authority keys for Raydium's AMM program to execute unauthorized withdrawals from multiple liquidity pools, extracting approximately $4.4 million in various tokens (SOL, USDC, RAY, and others) from pool reserves. The attack was not a smart contract logic vulnerability but rather a key management failure — the attacker obtained the private keys associated with Raydium's pool owner authority, granting them the ability to call privileged administrative functions that bypassed normal withdrawal restrictions.

## Background

### Raydium Protocol Architecture

Raydium is a Solana-native AMM that launched in early 2021 and became one of the ecosystem's primary liquidity venues. The protocol's architecture includes several key components:

**AMM Program**: The on-chain Solana program that manages pool logic, including swap execution, liquidity addition/removal, and fee collection. The program is deployed to a fixed program ID on Solana's mainnet.

**Pool Accounts**: Each trading pair (e.g., SOL/USDC) has associated accounts storing the pool's token reserves, LP token mint, configuration parameters, and authority information. Pool accounts are Program Derived Addresses (PDAs) owned by the AMM program.

**Pool Authority**: Each pool has an "owner" or "admin" authority — a Solana keypair (or PDA) with elevated permissions to call administrative functions on the pool. These functions include withdrawing protocol fees, updating pool parameters, and in Raydium's case at the time of the exploit, directly withdrawing pool reserves through an admin withdrawal function.

**LP Token Mechanism**: Liquidity providers deposit tokens into pools and receive LP tokens representing their proportional share of the pool's reserves. Normal withdrawals require burning LP tokens in proportion to the amount withdrawn.

### Admin Withdrawal Function

Raydium's AMM program contained an administrative withdrawal function that allowed the pool owner authority to withdraw tokens from pool reserves without the normal LP token burn mechanism. This function was designed for legitimate purposes: collecting accumulated protocol fees, performing emergency withdrawals if a pool needed to be decommissioned, or migrating liquidity to upgraded pool versions.

The function required a valid signature from the pool owner authority keypair. Under normal operations, this keypair would be controlled by the Raydium team (ideally through a multi-signature scheme or hardware security module) and used only for authorized administrative actions. The security of this function depended entirely on the security of the owner authority private key — if that key was compromised, the attacker could drain pool reserves at will.

### Solana Key Management Context

On Solana, private keys are 64-byte Ed25519 keypairs. Unlike Ethereum where multi-signature wallets are common for protocol administration, Solana's account model makes multi-sig more complex to implement. Many Solana protocols at the time of the Raydium exploit used single keypair authorities for admin functions, with the private key stored by the development team. This created a single point of failure: compromise of one private key could grant full administrative access to protocol functions.

## The Attack

### Vulnerability: Single-Key Administrative Authority

The fundamental vulnerability was not in Raydium's program logic but in its key management architecture. The pool owner authority was a single Solana keypair rather than a multi-signature arrangement or time-locked governance mechanism. The private key for this authority, if compromised through any vector (server breach, insider threat, phishing, malware, or supply chain attack), would grant the attacker full administrative privileges over all pools governed by that authority.

Raydium has not publicly disclosed the exact vector by which the admin key was compromised. The leading hypotheses include: compromise of a server or development machine where the key was stored, a Trojan horse or malware infection on a team member's system, an insider with access to the key material, or exploitation of a vulnerability in the key storage infrastructure.

### Attack Execution

The attack on December 16, 2022, proceeded as follows:

**Step 1: Key compromise.** The attacker obtained the private key material for Raydium's pool owner authority through an undisclosed vector. This key controlled administrative functions across multiple Raydium liquidity pools.

**Step 2: Targeted pool identification.** The attacker identified the highest-value liquidity pools governed by the compromised authority, focusing on pools with significant reserves in liquid assets (SOL, USDC, USDT, RAY).

**Step 3: Administrative withdrawal execution.** Using the compromised owner authority key, the attacker signed and submitted transactions calling Raydium's admin withdrawal function. These transactions withdrew token reserves from pool accounts directly to the attacker's wallet addresses, bypassing the normal LP token burn mechanism entirely.

**Step 4: Multi-pool extraction.** The attacker repeated the withdrawal process across multiple pools, extracting reserves from each affected pool. The attack targeted approximately 20+ pools over a period of several hours before Raydium's team detected the unauthorized activity.

**Step 5: Fund consolidation and laundering.** After extracting tokens from pools, the attacker consolidated funds into a smaller number of wallets and began bridging assets off Solana (primarily through Wormhole) and swapping tokens to reduce traceability.

### Detection and Response Timeline

The attack was first detected by community members and Raydium's own monitoring systems several hours after it began. The timeline was approximately:
- December 16, 2022 ~14:00 UTC: First unauthorized withdrawal transactions appear on-chain
- December 16, 2022 ~18:00 UTC: Community alerts surface on social media
- December 16, 2022 ~19:00 UTC: Raydium team confirms the exploit and begins emergency response
- December 16, 2022 ~20:00 UTC: Raydium rotates the compromised authority key, halting further withdrawals

## Impact

### Financial Losses

The total funds extracted were approximately $4.4 million across multiple tokens:
- SOL: ~$2.1 million
- USDC/USDT stablecoins: ~$1.3 million
- RAY (Raydium's governance token): ~$0.6 million
- Other tokens (various SPL tokens from affected pools): ~$0.4 million

The losses were distributed across liquidity providers in the affected pools. Each affected pool lost a portion of its reserves, meaning LP token holders received less than expected when they subsequently withdrew their liquidity. The percentage loss per pool varied depending on how much the attacker withdrew relative to the pool's total reserves.

### Protocol Impact

Raydium's total value locked (TVL) dropped significantly following the exploit, as liquidity providers withdrew funds from remaining pools due to security concerns. While the $4.4 million direct loss was manageable relative to Raydium's then-TVL of approximately $30-40 million, the confidence shock caused additional outflows.

The exploit also raised questions about the security of other Solana DeFi protocols that used similar single-key authority patterns. Several other Solana protocols proactively rotated their admin keys and announced plans to transition to multi-signature governance following the Raydium incident.

### Compensation

Raydium announced a compensation plan for affected liquidity providers using the protocol's treasury funds. The RAY token was used to compensate losses, with the amount determined by each LP's proportional share of the affected pools at the time of the exploit. The team committed to fully compensating all affected users, though the timeline and mechanics of distribution took several weeks to finalize.

## Technical Analysis

### Admin Key vs. Smart Contract Vulnerabilities

The Raydium exploit represents a distinct category from most DeFi exploits: it was not a vulnerability in the protocol's program logic, mathematical invariants, or oracle systems. The AMM program itself functioned correctly — the admin withdrawal function performed exactly as designed. The failure was in the security of the key that authorized those withdrawals.

This distinction is important for understanding DeFi security:
- **Logic vulnerabilities** (reentrancy, oracle manipulation, arithmetic errors) can be prevented through better code, audits, and formal verification
- **Key management failures** require operational security practices that exist outside the code: key generation, storage, rotation, access control, and monitoring

A protocol can have perfectly audited, formally verified smart contract code and still be exploited through key compromise. This is why key management and privilege minimization are as important as code quality.

### The Admin Key Anti-Pattern

Many DeFi protocols include administrative functions that grant significant power to designated key holders. While these functions serve legitimate purposes (upgrades, emergency responses, fee collection), they represent a trust assumption that contradicts the "trustless" ideal of DeFi. The Raydium exploit exemplified the risks of this pattern:

**Excessive privilege**: The admin withdrawal function could withdraw arbitrary amounts from any pool without LP token burns. A more restrictive design might limit admin withdrawals to accumulated fees only, cap withdrawal amounts per time period, or require a time-lock before execution.

**Single-key control**: One compromised key granted full access. A multi-signature requirement (e.g., 3-of-5) would require compromising multiple keys simultaneously, dramatically increasing attack difficulty.

**No time-lock**: Admin withdrawals executed immediately upon signing. A time-lock (e.g., 24-48 hour delay on admin actions) would have given the team and community time to detect and cancel unauthorized transactions before funds were extracted.

**Insufficient monitoring**: The attack proceeded for several hours before detection. Real-time monitoring of admin function calls with automatic alerts could have reduced the extraction window significantly.

### Comparison with Similar Key Compromise Attacks

Admin key compromises represent a significant category of DeFi exploits:

**Ronin Bridge (March 2022, ~$625M)**: The Ronin validator keys (5 of 9 required for bridge withdrawals) were compromised, likely through a combination of social engineering and infrastructure exploitation. The Lazarus Group (North Korean state actor) was attributed. Like Raydium, the bridge code worked correctly — the failure was in key security.

**Harmony Horizon Bridge (June 2022, ~$100M)**: The bridge's 2-of-5 multi-sig was compromised when two of the five private keys were obtained by attackers. The low multi-sig threshold (2 of 5) made compromise easier than higher-threshold schemes.

**Wintermute DeFi Operations (September 2022, ~$160M)**: Wintermute's trading operations lost funds when a hot wallet private key was compromised, likely due to a vulnerability in the Profanity vanity address generation tool that made the key partially predictable.

These incidents share common patterns: the exploited protocols had correct code but compromised keys, the attackers gained the same privileges as the legitimate key holders, and the primary defense failure was operational (key storage, generation, or access control) rather than cryptographic.

### Solana-Specific Considerations

Several aspects of Solana's architecture influenced the Raydium exploit:

**Single-signer programs**: Solana's programming model makes it natural to use single keypairs as authorities. Unlike Ethereum where multi-sig wallets are well-established (Gnosis Safe), Solana's multi-sig solutions (Squads, mean.finance) were less mature at the time of the exploit.

**Transaction speed**: Solana's fast block times (~400ms) meant the attacker could drain multiple pools very quickly. On Ethereum, the same attack would take longer per transaction due to 12-second block times.

**Account model**: Solana's account model means pool reserves are stored in token accounts owned by the program. Admin withdrawal simply transfers tokens from these accounts — there is no "emergency stop" mechanism unless explicitly coded into the program.

**Lack of time-lock standards**: At the time of the exploit, time-lock mechanisms were less standardized on Solana than on Ethereum (where protocols like Compound's Timelock contract were widely adopted). This contributed to Raydium using immediate-execution admin functions.

## Lessons Learned

### Multi-Signature Requirements for Admin Functions

Any function that can move significant value must require multiple independent signatures. Single-key authorities represent an unacceptable single point of failure for protocols managing millions of dollars. The minimum standard should be a multi-signature scheme requiring 3+ signatures from geographically and operationally distributed key holders, with no single individual or system having access to a quorum of keys.

### Time-Lock All Privileged Operations

Administrative functions that move user funds should have mandatory time delays between initiation and execution. A 24-48 hour time-lock on admin withdrawals would have given the Raydium team hours to detect and cancel the unauthorized transactions. Time-locks convert potential instantaneous losses into detectable, preventable anomalies.

### Minimize Admin Privileges

The principle of least privilege should apply to protocol administration. If admin withdrawal is needed only for fee collection, the function should be restricted to withdrawing only accumulated fees (not arbitrary pool reserves). If emergency withdrawal is needed, it should be gated by a separate higher-threshold mechanism (e.g., 5-of-7 multi-sig plus 48-hour time-lock) rather than using the same authority as routine operations.

### Operational Security for Key Material

Private keys controlling protocol functions should be generated on air-gapped hardware, stored in hardware security modules (HSMs) or hardware wallets, never present on internet-connected systems in unencrypted form, rotated periodically to limit the window of any potential compromise, and subject to access logging so unauthorized use can be detected.

### Real-Time Monitoring and Circuit Breakers

Protocols should implement real-time monitoring of admin function calls with automated alerts. Any admin withdrawal exceeding defined thresholds should trigger immediate alerts to the team and potentially automated pausing of further withdrawals. This monitoring exists outside the on-chain code — it is an operational layer that watches on-chain events and responds to anomalies.

## Conclusion

The Raydium AMM admin key compromise of December 16, 2022, resulted in approximately $4.4 million extracted from Solana liquidity pools through unauthorized administrative withdrawals. The attacker obtained the private key for Raydium's pool owner authority through an undisclosed vector and used it to call the protocol's admin withdrawal function across multiple pools, bypassing normal LP token burn requirements. The exploit highlights that DeFi security extends far beyond smart contract code quality — operational security, key management, privilege minimization, and monitoring are equally critical. Protocols managing significant user funds must implement multi-signature requirements, time-locks on privileged operations, and real-time anomaly detection to mitigate the impact of key compromise, which remains one of the most common and impactful attack vectors in decentralized finance.
