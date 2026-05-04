---
date: 2026-05-05
entities:
  - id: furucombo
    name: Furucombo
    type: defi-protocol
  - id: aave
    name: Aave
    type: defi-protocol
  - id: compound
    name: Compound
    type: defi-protocol
title: "Furucombo proxy authorization exploit: uninitialized implementation contract and $14M approval drain"
---

## Introduction

Furucombo was a decentralized finance transaction aggregation platform on Ethereum that allowed users to build complex multi-step DeFi transactions through a visual drag-and-drop interface. Users could compose "combos" — sequences of DeFi operations such as flash loans, token swaps, liquidity additions, and lending/borrowing actions — that would execute atomically in a single transaction. The platform abstracted away the complexity of directly interacting with DeFi protocol smart contracts, making sophisticated strategies accessible to users who lacked the technical ability to write custom smart contract code.

On February 27, 2021, an attacker exploited a critical vulnerability in Furucombo's proxy contract architecture, draining approximately $14 million in various tokens from wallets that had granted ERC-20 token approvals to the Furucombo proxy contract. The attack exploited the fact that Furucombo's proxy contract used a delegatecall-based pattern to route user transactions through modular "handler" contracts, and the attacker was able to register a malicious handler by exploiting an uninitialized implementation contract in the proxy's storage. This allowed the attacker to trick the Furucombo proxy into executing arbitrary code — specifically, ERC-20 `transferFrom` calls that drained tokens from users who had previously approved the proxy to spend their tokens.

## Background

### DeFi Transaction Composition

By early 2021, the DeFi ecosystem on Ethereum had grown to encompass dozens of protocols, each offering specialized financial services: Aave and Compound for lending/borrowing, Uniswap and SushiSwap for trading, Curve for stablecoin swaps, Maker for stablecoin minting, and many others. Sophisticated DeFi users frequently composed multi-step strategies that spanned multiple protocols — for example, flash-borrowing from Aave, swapping on Uniswap, providing liquidity on Curve, and repaying the flash loan, all in a single transaction.

Building these multi-step transactions required writing custom smart contract code (or using an existing framework like DSProxy), which was a significant barrier for most users. Furucombo aimed to democratize this capability by providing a visual interface where users could drag and drop DeFi "cubes" (each representing an operation like "swap on Uniswap" or "deposit to Aave") into a sequence, configure parameters, and execute the entire combo with a single transaction signature.

### Proxy Contract Architecture

To execute user-defined combos, Furucombo used a proxy contract that received user transactions and delegated execution to a set of "handler" contracts. Each handler implemented the logic for interacting with a specific DeFi protocol — for example, the Aave handler knew how to encode and execute Aave deposit, borrow, and repay operations. When a user submitted a combo, the proxy contract would iterate through the combo's steps, identify the appropriate handler for each step, and use `delegatecall` to execute the handler's code in the context of the proxy contract.

The `delegatecall` instruction in the Ethereum Virtual Machine (EVM) executes the called contract's code but uses the calling contract's storage, `msg.sender`, and `msg.value`. This meant that handler code executed within the proxy's context — any state changes made by handler code would modify the proxy's storage, and any external calls made by handler code would have the proxy's address as `msg.sender`. This design was intentional: it allowed the proxy to interact with DeFi protocols on behalf of users, using the proxy's token approvals and the proxy's balances.

The security of this architecture depended critically on the handler registry — the mechanism that determined which handler contracts were authorized to be called via `delegatecall`. If an attacker could register a malicious handler, they could execute arbitrary code in the proxy's context, with full access to the proxy's storage, balances, and approval authority.

### Token Approvals and the Proxy

For Furucombo to execute token swaps and DeFi operations on behalf of users, it needed ERC-20 token approvals. Users who wanted to use Furucombo granted the proxy contract approval to spend their tokens — typically as infinite approvals to avoid the gas cost and friction of re-approving before every combo execution. This created a large pool of wallets with outstanding approvals to the Furucombo proxy, representing significant value at risk if the proxy were ever compromised.

The Furucombo team was aware of this risk and had implemented access controls on the handler registry to prevent unauthorized handler registration. However, the vulnerability exploited by the attacker bypassed these access controls through a different vector: the proxy's `delegatecall` pattern combined with an uninitialized storage slot.

## The Attack

### Vulnerability: Uninitialized Implementation Contract

The Furucombo proxy contract used a common proxy pattern where the contract's behavior was determined by an "implementation" address stored in a specific storage slot. When the proxy received a transaction, it would `delegatecall` to the implementation address, which then dispatched the call to the appropriate handler. The implementation address was intended to be set during contract initialization and only changeable by the contract owner.

However, the attacker discovered that the Aave V2 lending pool's proxy contract had recently been upgraded, and during this upgrade process, a new implementation contract was deployed that had not yet been initialized. In the context of Aave's transparent proxy pattern, the implementation contract itself was a standalone contract that needed to have its `initialize` function called to set its owner and configuration. Before initialization, the implementation contract's storage was in a default state — including the critical slot that controlled which address had permission to upgrade the implementation.

The attacker exploited this uninitialized state by calling the `initialize` function on Aave V2's newly deployed implementation contract, making themselves the owner of that contract. This alone did not directly compromise Aave — the implementation contract was called via `delegatecall` from the proxy, so the implementation's own storage was irrelevant for Aave's normal operation.

The critical connection was that Furucombo's proxy had a handler registered for Aave V2. When Furucombo's proxy executed an Aave V2 operation via `delegatecall`, it routed through the Aave V2 handler, which in turn interacted with Aave's contracts. The attacker exploited this chain by first initializing the Aave V2 implementation contract to set themselves as the owner, then using that ownership to modify the implementation's code reference, creating a path where Furucombo's `delegatecall` chain ultimately reached attacker-controlled code.

### Attack Execution

The attack was executed in a single transaction on February 27, 2021, and proceeded through the following steps:

**Step 1: Initialize the Aave V2 implementation contract.** The attacker called `initialize()` on Aave V2's newly deployed (and uninitialized) implementation contract. This set the attacker as the owner of the implementation contract's own storage. Again, this did not affect Aave V2's proxy (which had its own storage), but it gave the attacker control over the implementation contract as a standalone entity.

**Step 2: Set the Furucombo proxy's implementation to the attacker's contract.** Using the authority gained in Step 1, the attacker manipulated the execution flow so that when Furucombo's proxy processed an Aave V2 handler call via `delegatecall`, the call chain ultimately wrote to the proxy's storage slot that controlled its implementation address. This effectively replaced the legitimate implementation with the attacker's malicious contract.

**Step 3: Execute malicious transfers through the compromised proxy.** With control over the Furucombo proxy's implementation, the attacker could execute arbitrary code in the proxy's context. The attacker crafted a series of `transferFrom` calls targeting wallets that had granted ERC-20 approvals to the Furucombo proxy. For each victim wallet, the attacker's malicious code called `token.transferFrom(victim, attacker, balance)` for each approved token, draining the full approved amount.

**Step 4: Repeat across tokens and wallets.** The attacker systematically drained multiple tokens (including USDC, DAI, USDT, sUSD, stETH, cDAI, cUSDT, aDAI, and others) from approximately 100+ wallets that had outstanding approvals to the Furucombo proxy. The total extraction was approximately $14 million in combined value.

### Transaction Details

The primary exploit transaction consumed approximately 8.7 million gas, reflecting the large number of `transferFrom` calls executed within a single transaction. On-chain analysis identified the following token losses: approximately $5.4 million in stETH (Lido staked ETH), approximately $3.4 million in USDC, approximately $1.7 million in DAI, approximately $1.2 million in various Aave aTokens, approximately $1.0 million in Compound cTokens, and approximately $1.3 million in other ERC-20 tokens (USDT, sUSD, WETH, and others).

The attacker moved the stolen funds through multiple intermediary wallets and began converting non-ETH assets to ETH through decentralized exchanges. Portions of the ETH were subsequently sent to Tornado Cash for mixing, while other portions were bridged to other chains or held in intermediate wallets.

## Impact

### Financial Losses

The direct financial impact was approximately $14 million in stolen tokens across 100+ wallets. The losses were concentrated among users who had granted large (often infinite) ERC-20 approvals to the Furucombo proxy and maintained substantial token balances in their wallets. The largest individual loss was approximately $3.4 million in stETH from a single wallet, suggesting that some victims were institutional or high-net-worth DeFi participants.

The distribution of losses was heavily skewed: the top 10 affected wallets accounted for approximately 75% of total losses, while the remaining 90+ wallets collectively lost the remaining 25%. This pattern is typical for approval-based exploits, where the largest token holders with the largest approvals suffer the greatest losses.

### Impact on Proxy Pattern Security Awareness

The Furucombo exploit was one of the first high-profile incidents to demonstrate the risks of `delegatecall`-based proxy patterns in production DeFi protocols. While security researchers had long warned about the dangers of `delegatecall` (which effectively grants the called contract full control over the calling contract's state and identity), the Furucombo case showed how a vulnerability in a dependency (Aave's uninitialized implementation contract) could cascade through a `delegatecall` chain to compromise an entirely separate protocol.

This cascading vulnerability pattern was novel and alarming: Furucombo's own code was not inherently flawed (the handler registry was properly access-controlled), but the protocol's reliance on external contracts through `delegatecall` created an indirect attack surface that the Furucombo team had not fully anticipated. The incident prompted a broader reassessment of `delegatecall`-based proxy patterns across the DeFi ecosystem.

### Impact on Token Approval Practices

The Furucombo exploit added to the growing body of evidence that standing ERC-20 token approvals represented one of the most significant unmanaged risks in DeFi. Unlike protocol-specific risks (impermanent loss, smart contract bugs in isolated pools), approval risks were cross-cutting: any wallet with an approval to a compromised or vulnerable contract was at risk, regardless of whether the wallet was actively using that protocol. The Furucombo case demonstrated that even protocols without intrinsic code flaws could become attack vectors for approval-based drains if their proxy architecture was compromised through external dependencies.

## Response and Remediation

### Immediate Response

The Furucombo team detected the attack within minutes and took immediate action. They published urgent warnings on Twitter and Discord urging all users to revoke their token approvals to the compromised proxy contract. They provided direct links to Revoke.cash and Etherscan's token approval tools, along with step-by-step instructions for revoking approvals via MetaMask.

The team also attempted to contact the attacker through an on-chain message (embedded in a transaction's input data), offering a bounty for the return of stolen funds. This whitehat negotiation attempt was unsuccessful — the attacker did not respond and continued to launder the stolen assets.

Within 24 hours, the Furucombo team published a detailed post-mortem identifying the root cause and explaining the attack chain. The post-mortem was reviewed and validated by independent security researchers, who confirmed the analysis and praised the team's transparency.

### Contract Redesign

The Furucombo team rebuilt their proxy architecture from the ground up with several fundamental security improvements. The new design eliminated the single implementation storage slot pattern, replacing it with a multi-handler architecture where each handler was individually registered and validated, reducing the blast radius of any single handler compromise.

The new handler validation system implemented strict checks on handler contracts: each handler was required to be deployed from a verified factory contract, to implement a standard interface that limited the operations it could perform, and to pass an automated security analysis before registration.

The proxy contract was also modified to implement a whitelist for the specific function selectors that handlers were allowed to call on external contracts. This prevented any handler — even a compromised one — from executing `transferFrom`, `approve`, or other dangerous ERC-20 functions through the proxy.

Additionally, the team implemented a "no persistent approval" model where the proxy would request exact-amount approvals for each combo execution and automatically reset approvals to zero after the combo completed. This eliminated the standing approval risk entirely, at the cost of slightly higher gas costs per transaction.

### User Compensation

Furucombo announced a compensation plan for affected users, funded from a combination of the project's treasury, future protocol revenue, and a dedicated community fundraising effort. The compensation was paid in installments over several months, with the total amount covering approximately 100% of losses for wallets that lost less than $100,000, and a sliding scale for larger losses. The team ultimately compensated approximately $13.6 million of the $14 million in losses — an unusually high recovery rate for a DeFi exploit, achieved through aggressive treasury deployment and community support.

## Technical Analysis

### Delegatecall Chains and Cascading Trust

The Furucombo exploit illustrates the danger of cascading trust in `delegatecall`-based architectures. In a `delegatecall` chain (A → delegatecalls → B → delegatecalls → C), each link in the chain executes with the storage and identity of the original caller (A). If any link in the chain (B or C) is compromised, the attacker gains the full privileges of A.

This creates a trust amplification problem: the security of the proxy (A) depends not just on its own code, but on the security of every contract in every possible `delegatecall` chain that passes through it. For a composable DeFi protocol like Furucombo, which integrates with dozens of external protocols, this dependency tree can be extremely large and difficult to audit comprehensively.

The defense is to minimize the depth and breadth of `delegatecall` chains. Each additional link in the chain adds a potential attack surface, and each additional external protocol integrated through `delegatecall` adds a dependency that could be compromised independently of the proxy's own code.

### Uninitialized Proxy Implementation Patterns

The specific vulnerability exploited in this attack — an uninitialized implementation contract — was a known risk pattern in the Ethereum proxy contract ecosystem. When a transparent proxy (like those used by Aave and many other protocols) is deployed, the implementation contract is a separate deployment that holds the business logic. The implementation contract's own storage is typically irrelevant (since it's accessed via `delegatecall`, which uses the proxy's storage), but the implementation contract's initialization state matters if anyone can call it directly.

The OpenZeppelin team had documented this risk and provided the `_disableInitializers()` function (added in later versions of their upgradeable contracts library) to prevent implementation contracts from being initialized by external callers. However, at the time of the Furucombo exploit, this mitigation was not yet widely adopted, and many deployed implementation contracts were sitting uninitialized on Ethereum mainnet.

The lesson is that implementation contracts in proxy patterns should be treated as security-sensitive even though they are not directly used in normal operation. An uninitialized implementation is an unexploded ordnance — it may not cause damage for months or years, but it creates a latent attack surface that can be triggered at any time.

### Approval-Based Attack Surface Quantification

The Furucombo exploit drained approximately $14 million from 100+ wallets, but the total value at risk was significantly larger. On-chain analysis of outstanding approvals to the Furucombo proxy at the time of the attack showed that the total approved amount across all wallets exceeded $100 million. The attacker's extraction of $14 million represented only a fraction of the available attack surface — the attacker may have been limited by gas constraints (the single-transaction gas limit), by incomplete wallet enumeration, or by a deliberate decision to extract a "manageable" amount and exit quickly before the team could respond.

This gap between actual losses ($14 million) and potential losses ($100+ million) underscores the systemic risk of standing approvals. Even after the attack was detected and the team warned users, it took days for most users to revoke their approvals — during which time the remaining approved balances were still at risk if the attacker had retained proxy control.

### Comparison with Other Proxy-Based Exploits

The Furucombo exploit fits into a broader pattern of proxy-related vulnerabilities in DeFi. The Parity Wallet freeze of November 2017 resulted from a similar pattern: the Parity multisig wallet library contract (used via `delegatecall` by all Parity multisig wallets) was reinitialized by an external caller who then called `selfdestruct`, permanently freezing approximately $150 million in ETH across all wallets that depended on the library.

The Wormhole bridge exploit of February 2022 (approximately $320 million) also involved a proxy vulnerability, though the specific mechanism differed: the attacker exploited a validation flaw in the bridge's guardian signature verification, which was implemented in an upgradeable proxy contract.

The common thread is that proxy patterns introduce complexity and indirect dependencies that are difficult to reason about and audit. The more layers of indirection (proxies pointing to implementations pointing to libraries), the larger the attack surface and the harder it is to ensure that every component in the chain is secure.

## Lessons Learned

### Minimize Delegatecall Chain Depth

Every `delegatecall` in a transaction's execution path extends the trust boundary of the calling contract. Protocols should minimize the depth and breadth of their `delegatecall` chains, and should maintain an explicit dependency map of all contracts that can be reached through `delegatecall` from their proxy contracts. Any change to any dependency in this map should trigger a security review of the entire chain.

### Initialize All Implementation Contracts

Every implementation contract deployed as part of a proxy pattern should be initialized immediately upon deployment, and the initialization function should include a mechanism to prevent re-initialization. The OpenZeppelin `_disableInitializers()` pattern (or equivalent) should be considered mandatory for all implementation contract deployments. Leaving an implementation contract uninitialized is a time bomb that can be exploited by any attacker who discovers it.

### Eliminate Standing Approvals Where Possible

The most effective defense against approval-based attacks is to eliminate standing approvals entirely. Protocols that must receive token approvals should request exact-amount approvals for each transaction and reset them to zero after use. Where infinite approvals are necessary for user experience, protocols should implement auxiliary contracts that hold the approvals and are designed with minimal attack surface (no `delegatecall`, no upgradability, no external dependencies).

### Monitor External Dependencies Continuously

Furucombo was not directly vulnerable — the vulnerability was in Aave's uninitialized implementation contract, which Furucombo's proxy chain passed through. This demonstrates that DeFi protocols must continuously monitor the security state of their external dependencies, not just their own code. When a dependency upgrades its contracts, the protocol should re-evaluate whether the upgrade introduces new risks to its own `delegatecall` chain.

## Conclusion

The Furucombo proxy authorization exploit of February 27, 2021, resulted in the drainage of approximately $14 million in various tokens from 100+ wallets through the weaponization of the Furucombo proxy's token approvals. The attack chain exploited an uninitialized Aave V2 implementation contract to gain control over the Furucombo proxy's execution context, enabling the attacker to execute arbitrary `transferFrom` calls against wallets with outstanding approvals. The vulnerability was not in Furucombo's own code but in the cascading trust model inherent to `delegatecall`-based proxy architectures — a single uninitialized dependency created an attack path that bypassed all of Furucombo's access controls. The incident demonstrated the systemic risks of standing token approvals combined with deep `delegatecall` chains, and prompted significant improvements in proxy initialization practices, approval management patterns, and dependency monitoring across the DeFi ecosystem. Furucombo's near-complete user compensation and comprehensive contract redesign set a high standard for post-exploit recovery, but the fundamental lesson persists: proxy-based architectures require continuous, chain-wide security vigilance, not just confidence in one's own code.
