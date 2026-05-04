---
date: 2026-05-05
entities:
  - id: li-finance
    name: Li.Finance (LiFi)
    type: defi-protocol
  - id: lifi-protocol
    name: LI.FI
    type: defi-protocol
title: "Li.Finance (LiFi) arbitrary call injection exploit: cross-chain swap aggregator drain and smart contract upgrade analysis"
---

## Introduction

Li.Finance, later rebranded to LI.FI, was a cross-chain swap and bridge aggregation protocol that unified access to multiple decentralized exchanges (DEXes) and bridge protocols through a single smart contract interface. The protocol operated as a middleware layer, routing user swap and bridge requests through the optimal combination of liquidity sources across different blockchains. By abstracting away the complexity of cross-chain transactions, Li.Finance aimed to provide users with the best available rates for converting assets across Ethereum, Polygon, BSC, Avalanche, Fantom, and other EVM-compatible chains.

On March 20, 2022, an attacker exploited an arbitrary call injection vulnerability in Li.Finance's smart contract, using it to drain approximately $600,000 in various tokens from 29 wallets that had previously granted token approvals to the Li.Finance contract. The attack was significant not because of the absolute dollar value — which was modest by DeFi exploit standards — but because it demonstrated a dangerous vulnerability pattern in aggregator protocols: the ability to weaponize legitimate token approvals through arbitrary external calls. Users who had interacted with Li.Finance and left standing token approvals were unknowingly exposed to having those approvals exploited by any attacker who discovered the call injection vector.

## Background

### Cross-Chain Aggregation Architecture

The DeFi landscape by early 2022 had fragmented across dozens of blockchain networks, each hosting its own ecosystem of DEXes, lending protocols, and yield farms. Users who wanted to move assets between chains or find the best swap rates across multiple DEXes faced significant friction: they needed to identify the optimal route, interact with multiple contracts on different chains, manage bridge transactions with varying confirmation times, and handle the token approval process for each protocol individually.

Cross-chain aggregators like Li.Finance addressed this fragmentation by building smart contracts that could execute multi-step transactions on behalf of users. A typical flow involved the user approving the Li.Finance contract to spend their tokens, then submitting a swap request specifying the input token, output token, and destination chain. The Li.Finance contract would then execute a series of calls to underlying DEXes and bridges to complete the transaction, returning the output tokens to the user (potentially on a different chain).

The key design challenge for aggregator contracts was flexibility: they needed to interact with an ever-growing list of DEXes and bridges, each with different function interfaces, token standards, and operational requirements. This demanded a contract architecture that could route calls to arbitrary external contracts with arbitrary calldata — a requirement that inherently created security risks if not carefully constrained.

### Token Approval Model in ERC-20

The ERC-20 token standard requires users to explicitly approve a smart contract before that contract can transfer tokens on their behalf. The standard `approve(spender, amount)` function grants the specified spender contract the right to transfer up to `amount` tokens from the user's wallet. Many DeFi protocols request "infinite approval" (setting the amount to `2^256 - 1`) to avoid requiring users to approve before every transaction, reducing gas costs and improving user experience.

However, infinite approvals create a persistent attack surface: if the approved contract is compromised or contains a vulnerability, an attacker can exploit it to drain all approved tokens from every user who has granted approval, up to their full wallet balance of each approved token. This risk is not hypothetical — it has been exploited in numerous incidents, and the Li.Finance attack is a canonical example.

### Li.Finance Contract Design

The Li.Finance smart contract implemented a "swap and bridge" pattern where users could specify a sequence of operations to execute. The contract accepted a structured request containing the input token and amount, a list of "swap data" structures (each specifying a DEX contract address and the calldata to pass to it), and bridge parameters for cross-chain transfers.

The critical design element was the swap execution function, which iterated through the provided swap data structures and made external calls to the specified DEX addresses with the provided calldata. In pseudocode, this resembled:

```
for each swapData in swapDataList:
    call(swapData.callTo, swapData.callData)
```

This pattern was functionally necessary — the contract needed to call arbitrary DEXes with arbitrary swap parameters — but it was also inherently dangerous. Without rigorous validation of the `callTo` address and `callData` content, any caller could use the Li.Finance contract as a proxy to execute arbitrary calls to any contract, with the Li.Finance contract as the `msg.sender`. This meant that any token approvals users had granted to the Li.Finance contract could be exploited by crafting `callData` that called `transferFrom(victim, attacker, amount)` on the approved token contracts.

## The Attack

### Vulnerability: Unrestricted External Calls

The vulnerability in the Li.Finance contract was an instance of the "arbitrary call" vulnerability class, where a contract allows external callers to specify both the target address and calldata for an external call without adequate validation. The specific issue was that the swap execution function did not restrict the `callTo` address to a whitelist of known DEX contracts, did not validate that the `callData` conformed to expected swap function signatures, and did not prevent calls to ERC-20 token contracts (which should never be the target of a "swap" call).

This meant an attacker could construct a swap request where `callTo` was set to the address of any ERC-20 token contract (such as USDC, USDT, or DAI), and `callData` was set to the ABI-encoded `transferFrom(victim, attacker, amount)` call. When the Li.Finance contract executed this "swap," it would actually call `USDC.transferFrom(victim, attacker, amount)`, and because the victim had previously approved the Li.Finance contract to spend their USDC, the transfer would succeed.

### Attack Execution

The attacker systematically exploited the vulnerability across 29 wallets that had outstanding token approvals to the Li.Finance contract. The attack proceeded as follows:

**Step 1: Reconnaissance.** The attacker identified the Li.Finance contract addresses on Ethereum mainnet and scanned the blockchain for all `Approval` events where the Li.Finance contract was the approved spender. This produced a list of wallets and the specific tokens and amounts they had approved.

**Step 2: Approval filtering.** From the full list of approvals, the attacker filtered for wallets that still held token balances equal to or exceeding their approval amounts. Wallets that had already revoked their approvals or moved their tokens elsewhere were excluded.

**Step 3: Batch drain construction.** For each vulnerable wallet, the attacker constructed a Li.Finance swap request where the swap data contained a `transferFrom` call targeting the victim's wallet, with the attacker's address as the recipient and the victim's full approved amount as the transfer amount.

**Step 4: Execution.** The attacker submitted these crafted swap requests to the Li.Finance contract. Each transaction caused the contract to call `transferFrom` on the specified token contract, transferring tokens from the victim's wallet to the attacker. Because the Li.Finance contract was the `msg.sender` of the `transferFrom` call, and the victims had approved the Li.Finance contract, the ERC-20 token contracts executed the transfers without any errors.

**Step 5: Token conversion.** The attacker converted the stolen tokens — a mix of USDC, USDT, DAI, and various other ERC-20 tokens — into ETH through multiple DEX swaps. The total value extracted was approximately $600,000 across all 29 victim wallets.

### Affected Tokens and Wallets

The 29 exploited wallets had granted approvals for various tokens including USDC (the largest single category), USDT, DAI, various wrapped assets, and some less liquid ERC-20 tokens. Individual losses ranged from under $1,000 to over $50,000, with the distribution skewed toward a small number of wallets that had approved large amounts and maintained substantial balances.

The attacker's transaction pattern showed methodical execution — wallets were drained in sequence within a few blocks, suggesting the attacker had pre-built the full set of exploit transactions and submitted them rapidly. The total attack spanned approximately 8 transactions, each draining multiple wallets for a specific token type.

## Impact

### Financial Losses

The direct financial impact was approximately $600,000 in stolen tokens across 29 wallets. While modest compared to other DeFi exploits of 2022, the incident's significance was amplified by several factors. First, the victims were not stakers, liquidity providers, or active DeFi participants at the time of the attack — they were ordinary users who had used Li.Finance at some point in the past and simply forgotten to revoke their token approvals. This passive victimization pattern made the exploit feel particularly unfair, as it punished users for a routine DeFi interaction (granting a token approval) that occurred days or weeks before the attack.

Second, the exploit highlighted that the total value at risk was much larger than the amount actually stolen. Any wallet with outstanding Li.Finance approvals was vulnerable, and the attacker chose to drain only 29 wallets — potentially because they targeted only the highest-value approvals, or because the team detected the attack and intervened before the attacker could drain additional wallets.

### Broader Approval Risk Awareness

The Li.Finance exploit catalyzed a broader conversation in the DeFi community about the risks of standing token approvals. Security researchers published analyses demonstrating that millions of wallets across the Ethereum ecosystem had outstanding infinite approvals to various DeFi contracts, creating a systemic risk that extended far beyond Li.Finance.

Tools like Revoke.cash, Unrekt.net, and Etherscan's token approval checker saw significant increases in usage following the incident, as users rushed to audit and revoke their outstanding approvals. The incident also accelerated adoption of the ERC-20 `permit` pattern (EIP-2612), which allows approvals to be granted through signed messages with built-in expiration times, reducing the window of exposure compared to traditional persistent approvals.

### Impact on Aggregator Protocol Design

The exploit forced a reckoning across the cross-chain aggregation sector about the inherent risks of arbitrary call patterns. Other aggregator protocols including 1inch, Paraswap, and 0x reviewed their own contract architectures for similar vulnerabilities. Several protocols preemptively implemented additional validation layers, even those whose existing designs did not contain the exact same vulnerability.

The incident demonstrated that aggregator protocols occupied a uniquely dangerous position in the DeFi security landscape: because they needed broad token approvals to function (users approve the aggregator to spend tokens for swaps), and because they needed flexible call routing to interact with diverse DEXes, any vulnerability that allowed arbitrary calls effectively weaponized the entire approval base against its users.

## Response and Remediation

### Immediate Response

The Li.Finance team detected the attack within approximately 30 minutes of the first exploit transaction and took immediate action. They published a warning on social media urging all users to revoke their token approvals to the Li.Finance contract. They disabled the vulnerable swap function on the contract (through an access-controlled pause mechanism). They began tracking the attacker's fund movements and contacted centralized exchanges where the attacker might attempt to off-ramp stolen funds.

The team also published a detailed post-mortem within 24 hours, acknowledging the vulnerability and explaining the root cause. The transparency and speed of the response was widely praised by the security community, setting a positive example for incident disclosure practices.

### User Compensation

Li.Finance committed to fully compensating all 29 affected wallets. The team returned approximately $600,000 to affected users from the project's treasury and operational funds. Compensation was paid in the same tokens that were stolen, at the amounts that were taken, meaning users were made completely whole (at least in token terms — price movements between the attack and compensation meant some users received slightly more or less in dollar value than they lost).

The full compensation was notable because many DeFi protocols that suffer exploits offer only partial compensation (often in the form of governance tokens or IOU tokens), or no compensation at all. Li.Finance's decision to absorb the full loss strengthened community trust and likely contributed to the protocol's continued growth following the incident.

### Contract Upgrade and Security Improvements

The Li.Finance team implemented comprehensive security upgrades to prevent similar attacks. The primary changes included the implementation of a DEX whitelist system, where only pre-approved DEX contract addresses could be specified as `callTo` targets in swap data, the addition of calldata validation that checked function selectors against an allowed list (swap functions only — no `transfer`, `transferFrom`, or `approve` selectors permitted), the introduction of a per-call token balance check that verified the contract's token balances changed in the expected direction after each swap call (preventing drain attacks even if the whitelist was somehow bypassed), and the deployment of a monitoring system that flagged anomalous patterns in swap requests (such as unusually high numbers of swap steps or requests targeting token contracts directly).

### Approval Management Recommendations

As part of the remediation, the Li.Finance team published guidelines recommending that users grant only the minimum necessary approval amount for each transaction rather than infinite approvals, regularly audit and revoke outstanding approvals using tools like Revoke.cash, and use hardware wallets for large holdings to add a signing confirmation step for any approval-based transfers.

The team also modified their frontend interface to request exact approval amounts by default (matching the specific swap amount) rather than infinite approvals, adding friction but significantly reducing the standing risk for future users.

## Technical Analysis

### Arbitrary Call Vulnerabilities in DeFi

The arbitrary call vulnerability pattern is a recurring issue in DeFi protocols that need to interact with multiple external contracts. The pattern emerges when a protocol implements a generic "call forwarding" mechanism that allows callers to specify both the target contract and the calldata to send. While this flexibility is often functionally necessary (aggregators need to call diverse DEXes with different function signatures), it creates a powerful attack primitive if not constrained.

The danger of arbitrary calls stems from the EVM's execution model: when contract A calls contract B, `msg.sender` in B's execution context is A's address. If A has token approvals, any arbitrary call through A that targets a token contract's `transferFrom` function will execute with A's approved spending power. This effectively turns the calling contract into a proxy for draining its own approvals.

### Defense Patterns for Aggregators

Several defense patterns have emerged for aggregator protocols that need flexible external calls. The whitelist approach restricts `callTo` addresses to a curated set of known DEX contracts. This is effective but requires maintenance as new DEXes are added and creates centralization concerns (the whitelist manager has significant power). The function selector check validates that the first four bytes of `callData` (the function selector) match expected swap/trade function signatures, preventing calls to `transferFrom`, `approve`, or other dangerous functions. This is lightweight but can be bypassed if a DEX's swap function has unintended side effects. The balance invariant check verifies that after executing all swap steps, the contract's balance of the input token decreased by at most the user's specified input amount, and the balance of the output token increased. Any unexpected balance changes indicate an exploit attempt. The approval scope limitation restricts the contract's spending power by using `approve(dex, exactAmount)` immediately before each swap call and `approve(dex, 0)` immediately after, preventing any persistent approval from accumulating on the contract.

Modern aggregator designs typically combine all four patterns as defense in depth, recognizing that any single mechanism may have edge cases or bypasses.

### Comparison with Similar Exploits

The Li.Finance exploit belongs to a family of approval-based attacks that plagued DeFi throughout 2021-2022. The Badger DAO exploit of December 2021 (approximately $120 million) exploited a compromised frontend to inject malicious approval transactions, which were then used to drain wallets — a different attack vector (frontend compromise vs. contract vulnerability) but the same underlying risk (standing approvals). The Multichain (formerly AnySwap) exploit of January 2022 exploited a vulnerability in a bridge contract to drain wallets with outstanding approvals, closely paralleling the Li.Finance pattern. The deBridge vulnerability (discovered through a bug bounty in 2022) identified a similar arbitrary call pattern in a cross-chain bridge before it could be exploited.

These incidents collectively established that approval-based attacks represented a systemic risk in DeFi, particularly for protocols that held broad approval authority across many wallets. The industry response — including improved approval management tools, EIP-2612 adoption, and stricter aggregator contract designs — represented a maturation of DeFi security practices, but standing approvals remain one of the largest attack surfaces in the ecosystem.

### Smart Contract Upgrade Methodology

The Li.Finance → LI.FI upgrade process followed best practices for post-exploit contract migration. The team deployed the new contract to a fresh address (rather than attempting to patch the existing contract through a proxy upgrade), which ensured that any residual vulnerabilities in the original contract's storage layout or initialization could not affect the new deployment. Users were required to migrate their approvals to the new contract address, which had the beneficial side effect of resetting all approvals to zero — any wallet that had been vulnerable due to standing approvals on the old contract was no longer at risk unless they explicitly re-approved the new contract.

The new contract was deployed behind a proxy pattern that allowed future upgrades, but with a time-lock mechanism that required a 48-hour delay between proposing an upgrade and executing it, giving the security community time to review any proposed changes.

## Lessons Learned

### Minimize External Call Flexibility

The fundamental lesson of the Li.Finance exploit is that smart contracts should minimize the scope of arbitrary external calls. Every generic `call(target, data)` pattern in a contract is a potential vector for abuse, and the burden should be on the developer to prove that all possible inputs to such calls are safe, rather than assuming that callers will only use the function as intended. Whitelist-based approaches, function selector filtering, and balance invariants should be considered mandatory for any contract that makes calls to caller-specified addresses.

### Approvals Are an Ongoing Liability

Token approvals are not a one-time interaction — they create a persistent, time-unbounded liability that can be exploited at any point in the future. Users should treat approvals as they would treat giving someone a blank check: the risk exists until the approval is explicitly revoked. Protocol teams should design their frontends to request minimal approvals by default, clearly communicate the risks of infinite approvals, and provide easy approval management tools within their interfaces.

### Speed and Transparency in Incident Response

The Li.Finance team's rapid detection, transparent disclosure, and full compensation set a high bar for DeFi incident response. Projects that handle exploits with transparency and accountability tend to retain user trust and continue growing, while those that obfuscate or delay disclosure suffer lasting reputational damage. The 24-hour post-mortem timeline should be considered a target for all DeFi projects experiencing security incidents.

### Aggregator-Specific Risk Profile

Cross-chain aggregators face a unique security challenge because they combine broad token approval authority with flexible external call patterns — the exact combination that enables approval-based attacks. Aggregator protocol developers should treat this combination as inherently dangerous and design their architectures with the assumption that an attacker will attempt to weaponize the call flexibility against the approval base. Defense in depth, with multiple independent validation layers, is not optional for this protocol category.

## Conclusion

The Li.Finance arbitrary call injection exploit of March 2022 drained approximately $600,000 from 29 wallets by weaponizing the protocol's own token approvals through an unrestricted external call mechanism in the swap execution function. The attacker crafted swap requests that, instead of calling DEX contracts, called ERC-20 token contracts' `transferFrom` functions to transfer victims' approved tokens to the attacker's address. The vulnerability — a missing whitelist and calldata validation on external call targets — was a direct consequence of the aggregator's need for flexible call routing, combined with insufficient security constraints on that flexibility. The Li.Finance team's response exemplified best practices: rapid detection, transparent disclosure, full user compensation from the project treasury, and a comprehensive contract upgrade that addressed the root cause through multiple defense layers. The incident's lasting significance lies in its demonstration that token approvals create persistent liabilities that can be exploited through vulnerabilities in approved contracts, a lesson that reshaped DeFi security practices around approval management and aggregator contract design across the industry.
