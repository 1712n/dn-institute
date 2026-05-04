---
date: 2026-05-05
entities:
  - id: agave-finance
    name: Agave Finance
    type: defi-protocol
  - id: hundred-finance-gnosis
    name: Hundred Finance (Gnosis Chain)
    type: defi-protocol
  - id: gnosis-chain
    name: Gnosis Chain
    type: blockchain
title: "Agave Finance reentrancy exploit on Gnosis Chain: wrapped token callback and $5.5M lending pool drain"
---

## Introduction

Agave Finance was a decentralized lending and borrowing protocol operating on Gnosis Chain (formerly xDai Chain), a sidechain of Ethereum designed for stable-value transactions and low-cost DeFi operations. Forked from Aave V2, one of the most established lending protocols on Ethereum mainnet, Agave deployed the Aave codebase with minimal modifications to serve the Gnosis Chain DeFi ecosystem. The protocol allowed users to deposit supported assets (including wrapped tokens like WETH, GNO, LINK, USDC, and wxDAI) as collateral and borrow other assets against that collateral, earning interest on deposits while paying interest on borrows.

On March 15, 2022, an attacker exploited a reentrancy vulnerability in Agave Finance's lending pool contracts, draining approximately $5.5 million in various tokens from the protocol. The attack occurred simultaneously with a nearly identical exploit on Hundred Finance, another lending protocol on Gnosis Chain, which lost approximately $6.2 million in the same attack session. The combined $11.7 million extraction made it the largest security incident on Gnosis Chain at the time. The vulnerability was not in Agave's own code — the Aave V2 codebase was thoroughly audited and reentrancy-safe on Ethereum mainnet — but in the interaction between Aave's lending logic and the specific token implementations on Gnosis Chain, where certain bridged tokens implemented ERC-677/ERC-777-style transfer callbacks that created a reentrancy vector not present on Ethereum.

## Background

### Gnosis Chain and Bridged Token Architecture

Gnosis Chain (rebranded from xDai Chain in late 2021) was an Ethereum sidechain that used the xDai stablecoin as its native gas token and operated under a Proof-of-Stake consensus mechanism. The chain was connected to Ethereum mainnet through the Omnibridge, a cross-chain bridge that created wrapped representations of Ethereum tokens on Gnosis Chain. When a user bridged ETH from Ethereum to Gnosis Chain, they received a wrapped token (WETH on Gnosis) that could be used in DeFi protocols on the sidechain.

A critical architectural detail was that several bridged tokens on Gnosis Chain implemented the ERC-677 token standard, an extension of ERC-20 that adds a `transferAndCall` function. When an ERC-677 token is transferred, it can optionally call a `onTokenTransfer` callback function on the receiving contract, allowing the receiver to execute code within the transfer's execution context. This callback mechanism is similar in effect to ERC-777's send hooks, and it creates the same reentrancy risk: if a contract transfers ERC-677 tokens to an untrusted address, the recipient can execute arbitrary code through the callback before the calling contract's state is finalized.

On Ethereum mainnet, the standard WETH, USDC, DAI, and LINK tokens are pure ERC-20 implementations without transfer callbacks. The Aave V2 codebase was designed and audited under the assumption that token transfers would not transfer execution control to the recipient. This assumption held on Ethereum but was violated on Gnosis Chain, where bridged versions of these same tokens implemented ERC-677 callbacks.

### Aave V2 Lending Mechanics

Aave V2's lending pool operated through a well-established flow: depositors supplied assets to the pool and received interest-bearing aTokens (e.g., aWETH for deposited WETH); borrowers posted collateral (in the form of deposited assets) and could borrow other assets up to a health factor determined by the collateral's loan-to-value (LTV) ratio and liquidation threshold. The protocol ensured solvency by requiring that every borrower maintained a health factor above 1.0 — meaning their collateral value (adjusted by the LTV ratio) exceeded their debt value at all times.

When a user called `borrow` on the Aave V2 lending pool, the function performed the following sequence: validated that the borrower's collateral was sufficient to support the new debt (health factor check), updated the borrower's debt records (internal state changes), and transferred the borrowed tokens to the borrower's address. The critical ordering was that the health factor check occurred before the token transfer — under the assumption that the transfer itself would not alter any state that the health factor depended on.

### Flash Loans in Aave V2

Aave V2 also supported flash loans — uncollateralized loans that must be repaid within the same transaction. Flash loans were a standard feature of the protocol and were used by arbitrageurs, liquidators, and DeFi composers to access large amounts of capital without upfront collateral. The flash loan mechanism was relevant to the Agave exploit because the attacker used Aave's own flash loan functionality as part of the attack to amplify the available capital.

## The Attack

### Vulnerability: ERC-677 Callback Reentrancy

The core vulnerability was a reentrancy path created by the interaction between Aave V2's `borrow` function and the ERC-677 token standard used by bridged tokens on Gnosis Chain. The attack proceeded through the following mechanism:

When the attacker called `borrow` to borrow WETH (or another ERC-677 token) from the Agave lending pool, the function first checked that the attacker's collateral was sufficient. It then updated the attacker's debt records. Finally, it transferred the borrowed WETH to the attacker's address. Because WETH on Gnosis Chain was an ERC-677 token, this transfer triggered a `onTokenTransfer` callback on the attacker's contract.

Within the callback — which executed before the `borrow` function returned — the attacker's contract called `borrow` again. At this point, the attacker's debt from the first borrow had been recorded, but the collateral was still intact (no liquidation had occurred, and the first borrow's token transfer was still in-progress). The health factor check for the second borrow evaluated the attacker's collateral minus the first borrow's debt, and if the collateral was large enough, the second borrow would also pass the health factor check.

By chaining multiple reentrant `borrow` calls within the callback, the attacker could borrow far more than their collateral would normally support. Each reentrant call saw the accumulated debt from prior calls, but the collateral remained unchanged because none of the borrows had been finalized. The attacker could continue borrowing until the accumulated debt exceeded the health factor threshold, at which point no more borrows would be approved — but by then, the attacker had already extracted significantly more value than their collateral warranted.

### Attack Execution

The attacker executed the exploit in a series of transactions on March 15, 2022. The attack flow was:

**Step 1: Flash loan.** The attacker obtained a flash loan from Agave's own lending pool (or from an external source) to acquire initial capital for use as collateral.

**Step 2: Collateral deposit.** The attacker deposited the flash-loaned assets (primarily WETH and wxDAI) into Agave as collateral, receiving aTokens in return. This established a legitimate borrowing position.

**Step 3: Initial borrow with reentrancy.** The attacker called `borrow` on Agave to borrow WETH against their deposited collateral. When the WETH transfer triggered the ERC-677 callback on the attacker's contract, the callback immediately called `borrow` again, this time borrowing a different asset (e.g., GNO, LINK, or USDC). Each reentrant borrow extracted additional assets from the lending pool while the attacker's position was in a transient state where the debt was partially recorded but the health factor hadn't yet been fully evaluated against the final debt position.

**Step 4: Cascade across assets.** The attacker repeated the reentrant borrowing pattern across multiple asset types available on Agave, extracting WETH, GNO, LINK, USDC, wxDAI, and other tokens from the lending pool. Each ERC-677 token transfer created a new callback opportunity for further reentrancy.

**Step 5: Flash loan repayment and profit extraction.** After extracting the maximum possible value through reentrant borrows, the attacker used a portion of the borrowed assets to repay the initial flash loan. The remainder — the difference between total borrows and the collateral plus flash loan repayment — represented the attacker's profit.

**Step 6: Cross-chain transfer.** The attacker bridged the stolen assets from Gnosis Chain to Ethereum mainnet through the Omnibridge and other bridge protocols, then began laundering the funds through Tornado Cash and intermediate wallets.

### Simultaneous Hundred Finance Attack

Within the same session of transactions, the attacker executed a nearly identical exploit against Hundred Finance on Gnosis Chain. Hundred Finance, also an Aave V2 fork, suffered from the same ERC-677 reentrancy vulnerability. The combined extraction from both protocols was approximately $11.7 million ($5.5 million from Agave, $6.2 million from Hundred Finance), making this a coordinated multi-protocol attack that exploited a shared vulnerability class.

The fact that both protocols were Aave V2 forks deployed on Gnosis Chain with the same set of ERC-677 bridged tokens meant that discovering the vulnerability in one protocol immediately implied its presence in the other. The attacker exploited both protocols within a short time window, likely to extract maximum value before either team could detect the attack and pause their contracts.

## Impact

### Financial Losses

Agave Finance lost approximately $5.5 million in total value locked, distributed across multiple token types. The breakdown included approximately $1.8 million in WETH, approximately $1.5 million in GNO (Gnosis DAO governance token), approximately $1.2 million in USDC, approximately $0.6 million in LINK, and approximately $0.4 million in wxDAI and other tokens. The losses were borne by depositors who had supplied these assets to the Agave lending pool — their aTokens now represented claims on a significantly depleted pool.

Combined with the $6.2 million lost from Hundred Finance, the total extraction from the Gnosis Chain DeFi ecosystem in this incident was approximately $11.7 million. This represented a significant percentage of the total value locked on Gnosis Chain at the time (approximately $250 million), and the incident temporarily reduced confidence in the chain's DeFi infrastructure.

### Impact on Fork-and-Deploy Practices

The Agave exploit exposed a critical risk in the prevalent DeFi practice of forking battle-tested protocols from one chain and deploying them on another. The Aave V2 codebase was one of the most thoroughly audited and extensively tested smart contract systems in DeFi, with multiple professional audits and years of mainnet operation securing billions of dollars. Teams deploying Aave V2 forks on other chains could reasonably believe they were deploying a secure system.

However, the Agave case demonstrated that security assumptions embedded in a protocol's design may be violated when the protocol is deployed in a different environment. The Aave V2 code was secure on Ethereum because Ethereum's standard token implementations did not include transfer callbacks. The same code was vulnerable on Gnosis Chain because the chain's bridged tokens used a different token standard. The vulnerability was not in Aave's code — it was in the gap between Aave's implicit security assumptions and the Gnosis Chain token environment.

This lesson had broad implications for the multi-chain DeFi ecosystem, where hundreds of protocols were being deployed across Ethereum L2s, sidechains, and alternative L1s, each with their own token implementations and standards. The Agave exploit made clear that deploying a fork required not just copying the code but also verifying that every environmental assumption made by the original codebase held true in the new deployment context.

### Impact on Gnosis Chain Ecosystem

The combined Agave/Hundred Finance exploit was a significant setback for the Gnosis Chain DeFi ecosystem. TVL on the chain dropped by approximately 15% in the week following the attack as users withdrew funds from other protocols out of concern for similar vulnerabilities. The incident also raised questions about the security of the Omnibridge's ERC-677 token implementation, which was identified as the root cause of the reentrancy vector.

The Gnosis Chain team responded by publishing a security advisory about the ERC-677 token standard and recommending that all DeFi protocols on the chain implement reentrancy guards on functions that transfer bridged tokens. The advisory noted that the ERC-677 callback mechanism was an intentional design feature (useful for certain DeFi patterns like deposit-and-stake in a single transaction) rather than a bug, but acknowledged that it created risks for protocols that assumed pure ERC-20 transfer semantics.

## Response and Remediation

### Immediate Response

The Agave Finance team detected the attack within approximately one hour and immediately paused all lending pool operations through the protocol's emergency admin function. They published an incident disclosure on social media, confirmed the root cause (ERC-677 reentrancy), and advised users that no further action was required on their part since the protocol was paused.

The team coordinated with the Hundred Finance team (which was simultaneously investigating the same attack), the Gnosis Chain development team, and blockchain security firms including BlockSec to trace the attacker's fund movements and assess the full scope of the damage.

### Technical Fix

The fix for the ERC-677 reentrancy vulnerability was straightforward: adding reentrancy guards (using OpenZeppelin's `ReentrancyGuard` or equivalent `nonReentrant` modifiers) to all lending pool functions that transferred tokens. With reentrancy guards in place, any reentrant call to `borrow` during the ERC-677 callback would be rejected because the guard's mutex would still be set from the outer call.

The Agave team deployed upgraded contracts that included reentrancy guards on all state-modifying functions. They also implemented additional safeguards including a token whitelist that explicitly identified ERC-677 tokens and applied extra validation for transfers involving those tokens, a post-transfer health factor re-evaluation that checked the borrower's health factor after the token transfer completed (catching any state manipulation that occurred during a callback), and an enhanced monitoring system that flagged transactions with unusual reentrancy depth.

### Recovery Efforts

The Agave team worked with the Gnosis Chain community to explore recovery options. Efforts included negotiations with the attacker through on-chain messages (unsuccessful), engagement with centralized exchanges to freeze any funds the attacker attempted to off-ramp, and collaboration with law enforcement in relevant jurisdictions.

A partial treasury allocation was made available for affected depositors, though the compensation did not cover the full losses. The Agave DAO proposed a recovery plan that would distribute a portion of future protocol revenue to affected depositors over time, supplemented by direct treasury disbursements. The total recovery for affected users varied by token and timing of their deposit, but was estimated at approximately 40-60% of lost value over a 12-month period.

## Technical Analysis

### ERC-677 vs. ERC-20 Token Standard Differences

The ERC-20 token standard defines a minimal interface for fungible tokens on Ethereum: `transfer`, `transferFrom`, `approve`, `allowance`, `balanceOf`, and `totalSupply`. Critically, ERC-20's `transfer` and `transferFrom` functions simply update the sender's and receiver's balances without any callback mechanism. The receiver has no way to execute code in response to receiving tokens — the transfer is a pure balance update.

ERC-677, proposed by the Chainlink team as an extension to ERC-20, adds a `transferAndCall(address to, uint256 value, bytes data)` function that transfers tokens and then calls `onTokenTransfer(address from, uint256 value, bytes data)` on the receiver if the receiver is a contract. This callback pattern enables useful workflows (like depositing tokens and registering the deposit in a single transaction) but introduces reentrancy risks for any contract that calls `transferAndCall` without a reentrancy guard.

ERC-777, a more comprehensive token standard, implements a similar callback mechanism (send hooks) but also retroactively applies callbacks to standard `transfer` and `transferFrom` calls through the ERC-1820 registry. ERC-777 tokens were the source of several earlier reentrancy exploits, including the imBTC/Uniswap V1 incident of April 2020. ERC-677 is less aggressive than ERC-777 (callbacks only occur through the explicit `transferAndCall` function, not standard `transfer`), but on Gnosis Chain, the bridged token implementations routed internal transfers through the callback mechanism, effectively making standard transfers trigger callbacks.

### Why Aave V2 Was Safe on Ethereum but Vulnerable on Gnosis

Aave V2's security model was built on the assumption that token transfers were atomic balance updates without side effects. This assumption was encoded not in explicit checks but in the absence of reentrancy guards on certain functions. The Aave team and their auditors evaluated the reentrancy risk and concluded that it was not applicable because the tokens supported by Aave on Ethereum mainnet (WETH, USDC, DAI, LINK, etc.) were all standard ERC-20 tokens without transfer callbacks.

This was a valid security analysis for Ethereum mainnet — but it was an environmental assumption, not a code-level guarantee. When the Agave team forked Aave V2 and deployed it on Gnosis Chain with a different set of tokens (ERC-677 bridged tokens), the environmental assumption was violated while the code remained unchanged. The result was a latent vulnerability that existed from the moment Agave was deployed but was not triggered until the attacker discovered and exploited it.

This pattern — code that is secure in one environment but vulnerable in another due to environmental assumptions — is a general risk in the multi-chain DeFi ecosystem. Other examples include protocols that assume ETH transfers via `transfer` or `send` will always succeed (which can fail if the receiver is a contract with a gas-expensive fallback function), protocols that assume `block.timestamp` is reliable for time-sensitive logic (which varies in accuracy across different chains and consensus mechanisms), and protocols that assume specific gas costs for opcodes (which may differ on L2s or chains with different EVM implementations).

### Flash Loan Amplification Pattern

The Agave attack used flash loans to amplify the attacker's initial capital, following a pattern seen in numerous DeFi exploits. The flash loan served two purposes: it provided the collateral needed to establish a legitimate borrowing position on Agave, and it maximized the total value that could be extracted through reentrant borrows.

Without the flash loan, the attacker would have been limited to the capital they personally held. With a flash loan providing the initial collateral, the attacker could establish a much larger borrowing position and extract correspondingly more value. The flash loan was repaid from the borrowed assets, with the surplus representing the attacker's profit.

The interaction between flash loans and reentrancy exploits is particularly dangerous because flash loans remove the capital barrier to exploitation. Any reentrancy vulnerability in a lending protocol can be maximally exploited by using a flash loan to provide the maximum possible collateral, then using reentrancy to borrow against that collateral multiple times.

### Comparison with Related Exploits

The Agave exploit belongs to a well-documented family of reentrancy attacks on lending protocols facilitated by non-standard token callbacks. The most direct precedent was the Cream Finance v1 exploit (August 2021), where AMP tokens (which implement ERC-777 send hooks) were used as the reentrancy vector to drain approximately $18.8 million from Cream's lending pools. The Cream case demonstrated the same fundamental pattern: a lending protocol's borrow function transferred tokens with callbacks that allowed reentrant borrows before the first borrow's state changes were finalized.

The Rari Capital Fuse pool exploit (April 2022, approximately $80 million) extended this pattern further, exploiting reentrancy in a broader set of lending pool functions across multiple Fuse pools. The Rari case involved a more complex reentrancy path (through the comptroller's enter/exit markets functions) but followed the same fundamental principle of exploiting execution control transfer during token movements.

## Lessons Learned

### Fork Audits Must Include Environmental Analysis

The most critical lesson from the Agave exploit is that deploying a fork of a battle-tested protocol on a new chain requires a thorough analysis of the new chain's environmental properties and how they interact with the forked code's assumptions. This analysis must go beyond code-level security review to include the token standards used by bridged/wrapped tokens on the target chain, the gas model and block production mechanism, the bridge architecture and its implications for token behavior, the oracle infrastructure and price feed reliability, and the governance model and emergency response capabilities.

A protocol's security is the intersection of its code's invariants and the environment's properties. Changing either one without re-evaluating the intersection creates latent vulnerabilities.

### Reentrancy Guards Are Cheap Insurance

The fix for the Agave vulnerability was trivially simple: adding a `nonReentrant` modifier to the `borrow` function. This modifier costs approximately 5,000 gas per call (a few cents on most chains) and completely eliminates reentrancy-based attacks. Given the catastrophic consequences of reentrancy exploits (millions of dollars in losses), the cost-benefit analysis overwhelmingly favors applying reentrancy guards to all state-modifying functions in DeFi protocols, regardless of whether the current token set includes callback-capable tokens.

The Aave team's original decision to omit reentrancy guards was defensible given their specific deployment context (Ethereum mainnet with pure ERC-20 tokens), but it optimized for gas efficiency at the cost of defense in depth. In a multi-chain world where the same code may be deployed across environments with different token standards, defense in depth through universal reentrancy guards is more valuable than marginal gas savings.

### Multi-Protocol Attack Coordination

The simultaneous exploitation of Agave and Hundred Finance demonstrated that vulnerabilities shared across protocol forks can be exploited in coordinated attacks. When an attacker discovers a vulnerability in one fork, they can immediately assess whether the same vulnerability exists in other forks of the same codebase on the same chain — and exploit all of them before any team can respond.

This creates a security coordination challenge for the DeFi ecosystem: fork-based protocols sharing the same codebase should establish communication channels for security disclosures, so that a vulnerability discovered in one fork can be rapidly communicated to and patched by all other forks before an attacker can exploit them serially.

### Bridged Token Risk Assessment

The ERC-677 callback mechanism used by Gnosis Chain's bridged tokens was a deliberate design choice with legitimate use cases. However, its interaction with protocols designed for pure ERC-20 tokens created an unexpected attack surface. This highlights the need for DeFi protocols to maintain explicit documentation of their token standard assumptions and to validate those assumptions when adding support for new tokens or deploying on new chains.

A practical recommendation is for lending protocols to implement a token compatibility checklist that includes: Does the token implement transfer callbacks (ERC-677, ERC-777, or similar)? Does the token's `transfer` or `transferFrom` implementation deviate from standard ERC-20 behavior? Does the token have admin functions that can modify transfer behavior (pausable, blacklistable)? Does the token implement rebasing or fee-on-transfer mechanics? Any "yes" answer should trigger additional security review and potentially the addition of extra protective measures (reentrancy guards, pre/post-transfer balance checks, etc.).

## Conclusion

The Agave Finance reentrancy exploit of March 15, 2022, resulted in the loss of approximately $5.5 million from the protocol's lending pools on Gnosis Chain, with a simultaneous attack on Hundred Finance adding $6.2 million in losses for a combined $11.7 million extraction. The vulnerability was not a flaw in the Aave V2 codebase that Agave forked, but an environmental mismatch: bridged tokens on Gnosis Chain implemented ERC-677 transfer callbacks that created a reentrancy vector absent from Ethereum mainnet's standard ERC-20 tokens. The attack exploited this callback during the lending pool's `borrow` function to execute reentrant borrows before prior debt was fully finalized, draining far more value than the attacker's collateral warranted. The incident's significance extends beyond its financial impact to the fundamental lesson it teaches about multi-chain DeFi security: a protocol's security is not solely a property of its code but of the interaction between its code and its deployment environment. In a multi-chain ecosystem where the same code is forked and deployed across chains with different token standards, bridge architectures, and environmental properties, fork-and-deploy practices must include rigorous environmental security analysis to prevent identical code from becoming newly vulnerable simply by changing its context.
