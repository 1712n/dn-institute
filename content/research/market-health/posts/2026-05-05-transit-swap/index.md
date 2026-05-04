---
date: 2026-05-05
entities:
  - id: transit-swap
    name: Transit Swap
    type: defi
  - id: tokenpocket
    name: TokenPocket
    type: defi
title: "Transit Swap token-approval exploitation, $21 M user-fund drain, and partial attacker restitution"
---

## 1. Introduction and incident overview

On 2 October 2022, Transit Swap — a cross-chain decentralized exchange (DEX) aggregator supported by the TokenPocket wallet — was exploited through a vulnerability in its swap contract's token-claim function. The attacker used the vulnerability to drain approximately $21 million in tokens from users' wallets by abusing existing ERC-20 token approvals that users had previously granted to the Transit Swap permissions contract. The stolen funds comprised approximately 3,180 ETH ($4.16 million) on Ethereum and 49,612 BNB ($14.01 million) on BNB Chain (BSC), with additional tokens on other chains.

The Transit Swap incident was notable for two reasons beyond its dollar value. First, the exploit targeted a common but under-scrutinized pattern in DeFi: the use of broad token approvals that allow a contract to transfer tokens on behalf of users. The attacker did not need to interact with users directly; they simply called the vulnerable contract function to drain funds from any wallet that had previously approved Transit Swap for token transfers. Second, the incident featured a partial restitution: the attacker returned approximately 70% of the stolen funds within days of the exploit, suggesting that the rapid identification of the attacker's on-chain footprint (and potentially off-chain identity) created sufficient pressure to incentivize partial return.

## 2. Technical background

### 2.1 Transit Swap and DEX aggregation

Transit Swap operated as a cross-chain DEX aggregator — a service that routes token swaps through multiple decentralized exchanges to find the optimal price for users. When a user initiated a swap through Transit Swap, the platform's routing engine identified the best available price across connected DEXes (such as PancakeSwap on BSC, Uniswap on Ethereum, and others) and executed the swap on the user's behalf.

To enable this routing, Transit Swap required users to approve its permissions contract for token transfers. When a user granted an ERC-20 `approve()` to the Transit Swap contract, they authorized the contract to call `transferFrom()` on the user's tokens — moving tokens from the user's wallet to the DEX where the swap would be executed. This is a standard pattern across DeFi applications that need to move tokens on behalf of users.

Transit Swap's contract architecture used a multi-contract design:
- **Entry contract** (`0x8785...9d72`): Received user swap requests and determined the routing path.
- **Execution contract** (`0x0B47...ff52`): Called subordinate contracts to execute the token transfers along the routing path.
- **Token-claim contract** (`0xed1a...c428`): Performed the actual token transfers using the `claimTokens()` function, which called `transferFrom()` on the relevant token contracts.

### 2.2 The ERC-20 approval model

The ERC-20 token standard's `approve()` and `transferFrom()` functions are the primary mechanism by which DeFi applications interact with user tokens. When a user approves a contract address for a specific token, the contract can call `transferFrom()` to move up to the approved amount of that token from the user's wallet to any destination address.

A persistent security concern with this model is the practice of unlimited approvals. Many DeFi front ends request approval for the maximum possible amount (2^256 - 1) to avoid requiring users to re-approve for each transaction. This convenience creates a standing permission: if the approved contract is later compromised or contains a vulnerability, the attacker can drain the full token balance — not just the amount of the current transaction — from every user who has granted an unlimited approval.

### 2.3 Unverified contract code

Transit Swap's contracts were deployed without source-code verification on block explorers (Etherscan, BscScan). This meant that the contract bytecode was publicly visible on-chain, but the human-readable Solidity source code was not published. While unverified contracts are common in DeFi (particularly for smaller projects), the absence of verified source code makes it more difficult for external security researchers, auditors, and users to identify vulnerabilities through code review. The vulnerability in Transit Swap's `claimTokens()` function was discoverable through bytecode analysis and decompilation, but this requires significantly more effort than reviewing published source code.

## 3. The vulnerability

### 3.1 Missing input validation in claimTokens()

The core vulnerability was in the `claimTokens(address, address, address, uint256)` function of Transit Swap's token-claim contract (`0xed1a...c428`). This function was designed to facilitate token transfers as part of the swap routing process. It accepted four parameters:

1. The token contract address (which token to transfer).
2. The source address (from whose wallet to transfer).
3. The destination address (where to send the tokens).
4. The amount to transfer.

The critical flaw was that the function did not validate these parameters against the expected swap context. Specifically:

- **No verification of the token address**: The function did not check that the token address corresponded to a token involved in a legitimate swap. The attacker could specify any token contract address.
- **No verification of the source address**: The function did not verify that the source address was the user who initiated the swap. The attacker could specify any address that had previously approved the Transit Swap contract.
- **No verification of the destination address**: The function did not restrict the destination to addresses involved in the swap routing. The attacker could specify their own wallet as the destination.
- **No verification of the amount**: The function did not check that the transfer amount corresponded to the amount specified in the original swap request.

Because the token-claim contract (`0xed1a...c428`) had been granted `transferFrom` authorization by the permissions management contract (which users had approved), and because the `claimTokens()` function did not validate its inputs, the attacker could call this function with arbitrary parameters to transfer any approved token from any user's wallet to the attacker's address.

### 3.2 The call chain

The attacker's exploit followed the contract call chain that Transit Swap itself used for legitimate swaps:

1. Called the entry contract (`0x8785...9d72`), which routed the request to the execution contract.
2. Used the `callBytes(bytes)` function on the execution contract (`0x0B47...ff52`) to pass crafted calldata.
3. The execution contract called `claimTokens()` on the token-claim contract (`0xed1a...c428`) with the attacker-specified parameters.

The execution contract's `callBytes()` function accepted arbitrary byte data from the caller and forwarded it to the downstream contracts. This pass-through design — intended to provide flexibility in routing swap operations — meant that the attacker could craft calldata that caused the token-claim contract to execute `transferFrom()` with any parameters the attacker chose.

### 3.3 Root cause: permission re-delegation without validation

The fundamental security failure was permission re-delegation without validation. Users granted token-transfer permissions to Transit Swap's permissions contract. Transit Swap's internal contract architecture then delegated this permission to the token-claim contract, which executed `transferFrom()` on behalf of the user. However, the token-claim contract did not validate that the transfer it was executing corresponded to a legitimate user-initiated swap. This created a gap between the permission the user intended to grant (the ability to execute their specific swap) and the permission the contract actually exercised (the ability to transfer any approved token from any approving user to any destination).

This pattern — where a user's permission is re-delegated through a chain of contracts without adequate validation at each step — is a recurring vulnerability class in DeFi. The Transit Swap case was a particularly clear example because the `claimTokens()` function accepted all critical parameters from the caller without any verification.

## 4. Attack execution

### 4.1 Exploit mechanics

The attacker deployed a contract that interacted with Transit Swap's entry contract, passing crafted calldata through the call chain to the vulnerable `claimTokens()` function. For each victim, the attacker specified:

- The token contract address of the victim's token (e.g., USDC, USDT, BUSD, WETH, WBNB).
- The victim's wallet address as the source.
- The attacker's wallet address (`0x75F2...fD46`) as the destination.
- The victim's full approved balance as the amount.

The attacker executed these calls across multiple blockchain networks, primarily Ethereum and BNB Chain (BSC), systematically iterating through addresses that had granted token approvals to the Transit Swap contract. The process was automated: the attacker's contract scanned for approved balances and drained them in batch.

### 4.2 Multi-chain impact

The exploit affected users on multiple chains where Transit Swap operated:

| Chain | Approximate Loss |
|---|---|
| BNB Chain (BSC) | ~$14.0M (49,612 BNB + tokens) |
| Ethereum | ~$4.2M (3,180 ETH + tokens) |
| Other chains | ~$2.8M combined |
| **Total** | **~$21M** |

BNB Chain suffered the largest losses, reflecting Transit Swap's user base concentration on that network. The cross-chain nature of the exploit highlighted the compounding risk of deploying the same vulnerable contract architecture across multiple chains: a single vulnerability class produced losses on every chain where the contracts were deployed.

### 4.3 Attacker's operational error

Security researchers noted that the attacker lost approximately $1.4 million during the exploit due to what appeared to be an operational error. Some portion of the stolen funds was sent to an unrecoverable address (a so-called "black hole" address) during the fund-movement process. This accidental loss reduced the attacker's total take but did not benefit the victims, as the funds were permanently locked.

## 5. Response and aftermath

### 5.1 Immediate response

Transit Swap detected the exploit and announced it via social media on 2 October 2022. The team immediately suspended all contract trading functions to prevent further exploitation. The team also urged users to revoke their token approvals for the Transit Swap contract addresses, particularly the token-claim contract, to prevent additional drains.

Multiple blockchain security firms — including SlowMist, Numen Cyber Labs, and PeckShield — published analyses of the exploit within hours, identifying the vulnerable function and the attacker's on-chain addresses. The rapid community response was facilitated by the on-chain transparency of the exploit transactions.

### 5.2 Attacker identification efforts

Transit Swap's team, in collaboration with security firms and blockchain analytics providers, identified on-chain information associated with the attacker's addresses. The team reported finding the attacker's IP address and email address through analysis of the attacker's on-chain interactions and off-chain infrastructure. While these identifiers were not publicly disclosed, the team communicated with the attacker through on-chain messages and off-chain channels.

### 5.3 Partial fund return

Beginning within days of the exploit, the attacker returned approximately 70% of the stolen funds (roughly $14.7 million) to Transit Swap's recovery addresses. The partial return was consistent with a pattern seen in several 2022 DeFi exploits where attackers returned a portion of stolen funds — apparently as a negotiated settlement or in response to identification pressure — while retaining the remainder as a de facto "bug bounty."

The attacker retained approximately $6.3 million (30% of the original theft), which was never recovered. This outcome left a significant gap for affected users, though the partial recovery was better than the zero-recovery outcome of many DeFi exploits.

### 5.4 User refund process

Transit Swap initiated a refund process for affected users using the recovered funds. The refund covered approximately 70% of each user's losses, proportional to the amount that was returned by the attacker. Users who had not revoked their approvals prior to the recovery were at risk of re-exploitation if the contracts had not been properly secured, though Transit Swap's suspension of contract functions mitigated this risk.

## 6. Market-health implications

### 6.1 The ERC-20 approval attack surface

The Transit Swap exploit highlighted one of the largest and most persistent attack surfaces in DeFi: the accumulated ERC-20 token approvals that users grant to DeFi contracts. Every user who has ever approved a DeFi contract has created a standing permission that can be exploited if the contract is compromised, contains a vulnerability, or is upgraded to malicious code.

The scale of this attack surface is enormous. Across the Ethereum and EVM-compatible ecosystem, hundreds of millions of active token approvals exist, many of which are unlimited approvals granting permission to transfer a user's entire balance of a given token. Security tools like Revoke.cash and Etherscan's token-approval checker allow users to review and revoke these approvals, but the vast majority of DeFi users do not regularly audit their outstanding approvals.

For market surveillance, the token-approval attack surface represents a systemic risk that is difficult to quantify. The risk is not concentrated in a single protocol; it is distributed across every DeFi contract that has ever received a token approval. A vulnerability in any one of these contracts exposes the accumulated approvals of all its users.

### 6.2 DEX aggregator trust concentration

DEX aggregators like Transit Swap occupy a position of concentrated trust in the DeFi ecosystem. Because aggregators route swaps through multiple underlying DEXes, they typically require broad token approvals — users must approve the aggregator's permissions contract for each token they want to swap. This means that a vulnerability in the aggregator's contract exposes users to losses across all tokens they have approved, not just the token involved in a specific swap.

The aggregator model also means that the aggregator's contract security is a bottleneck for the security of the entire swap flow. Even if the underlying DEXes (PancakeSwap, Uniswap, etc.) have secure contracts, a vulnerability in the aggregator that sits between the user and the DEX can drain user funds. Users who trust the aggregator's routing interface are implicitly trusting the security of the aggregator's contract stack.

| DEX Aggregator Incident | Date | Loss | Vector |
|---|---|---|---|
| Transit Swap | Oct 2022 | ~$21M | claimTokens() input validation bypass |
| Paraswap (Augustus v6) | Mar 2024 | ~$24K | Similar approval-drain via unvalidated calldata |
| 1inch (resolved pre-exploit) | Various | $0 | Approval-scope vulnerabilities found and patched pre-exploit |

### 6.3 Unverified contracts as a market-health indicator

Transit Swap's use of unverified (non-source-published) contracts was a contributing factor to the exploit. Unverified contracts are more difficult for external security researchers to audit, and they reduce the likelihood that vulnerabilities will be discovered and reported before exploitation. From a market-health perspective, the proportion of unverified contracts holding significant user funds or approvals is an indicator of ecosystem-level security risk.

While unverified contracts are not inherently malicious — some projects choose not to verify for competitive or intellectual-property reasons — the practice is inconsistent with the transparency ethos of DeFi and reduces the community's collective ability to identify and report vulnerabilities. Market surveillance systems that track the verification status of contracts holding significant TVL or user approvals can identify concentrations of unaudited risk.

### 6.4 Partial restitution as a recovery pattern

The Transit Swap attacker's decision to return 70% of stolen funds was part of an emerging pattern in DeFi exploits during 2022-2023. Similar partial returns occurred in the Euler Finance ($197M stolen, ~$176M returned), Mango Markets ($114M stolen, $67M returned), and Sentiment Protocol ($1M stolen, ~$870K returned) incidents.

This pattern reflects the distinctive feature of public-blockchain exploits: the attacker's on-chain activity is permanently recorded and traceable. Unlike traditional cybercrime where stolen funds can be relatively easily laundered through conventional financial channels, blockchain exploits leave a permanent forensic trail. Attackers who are identified (or who believe they may be identified) face criminal prosecution risk, and returning funds — sometimes retaining a portion as a negotiated "white-hat bounty" — is a strategy to mitigate this risk.

For market health, the partial-restitution pattern has mixed implications. On one hand, it results in better outcomes for victims than zero recovery. On the other hand, it can create perverse incentives: if attackers routinely retain 10-30% of stolen funds as a de facto bounty, the expected payoff from exploitation may still exceed the expected cost, particularly for attackers who believe they can avoid identification.

## 7. Lessons learned and recommendations

### 7.1 For DEX aggregators and DeFi protocols

1. **Validate all external-call parameters**: Any function that performs token transfers based on caller-supplied parameters must validate those parameters against the expected operation context. Specifically, the token address, source address, destination address, and amount should all be verified against a signed or committed swap request.

2. **Minimize approval scope**: Request limited token approvals (for the specific amount of the current transaction) rather than unlimited approvals. While this requires users to approve each transaction individually, it bounds the potential loss from a contract vulnerability to the amount of the most recent approval.

3. **Verify and publish contract source code**: Source-code verification on block explorers enables community review and increases the likelihood that vulnerabilities will be discovered and reported before exploitation. Projects that deploy significant user-facing contracts without source verification should be treated as higher-risk by security-conscious users and market participants.

4. **Implement access controls on sensitive functions**: Functions that perform token transfers should implement access controls (e.g., restricting callers to authorized internal contracts with verified parameters) rather than accepting arbitrary calldata from any caller.

### 7.2 For DeFi users

1. **Use limited approvals**: When approving tokens for DeFi protocols, approve only the specific amount needed for the current transaction. Most modern wallet interfaces support setting custom approval amounts.

2. **Regularly audit and revoke approvals**: Use tools like Revoke.cash, Etherscan's token-approval checker, or wallet-native approval-management features to periodically review and revoke unnecessary outstanding token approvals.

3. **Prefer protocols with verified contracts**: When choosing between DeFi protocols, prefer those that have published and verified their contract source code. Verified contracts are not immune to vulnerabilities, but they benefit from a larger pool of potential reviewers.

### 7.3 For market surveillance

1. **Monitor approval-drain transactions**: Implement monitoring for transactions where a contract's `transferFrom()` function is called to drain large amounts from multiple user addresses in rapid succession. This pattern — many users being drained through the same contract in a short time window — is a strong signal of an approval-drain exploit in progress.

2. **Track unverified contracts with significant approvals**: Identify contracts that hold significant user token approvals but have not published verified source code. These represent concentrated, unauditable risk.

3. **Assess aggregator contract security**: When evaluating systemic risk in the DEX ecosystem, assess the contract security of aggregators — which sit between users and underlying DEXes — as a distinct risk layer from the security of the underlying DEXes themselves.

## 8. Conclusion

The Transit Swap exploit of October 2022 demonstrated the persistent risk of the ERC-20 token-approval model when combined with insufficient input validation in DeFi contract architectures. By exploiting a `claimTokens()` function that accepted arbitrary caller-supplied parameters without validation, the attacker drained $21 million from users who had previously approved Transit Swap for token transfers. The vulnerability was a textbook case of permission re-delegation without validation: users granted permissions intended for specific swap operations, but the contract's lack of input checks allowed the attacker to repurpose those permissions for arbitrary token theft.

The incident's partial resolution — with the attacker returning approximately 70% of stolen funds — illustrated both the forensic transparency of public blockchains (which creates identification pressure on attackers) and the limitations of post-exploit recovery as a security strategy. For market health, the Transit Swap case reinforced the systemic risk of accumulated ERC-20 approvals across the DeFi ecosystem and highlighted the specific trust concentration in DEX aggregators, which require broad approval sets and sit as intermediaries between users and underlying liquidity venues.
