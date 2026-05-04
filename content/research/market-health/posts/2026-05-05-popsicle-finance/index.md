---
date: 2026-05-05
entities:
  - id: popsicle-finance
    name: Popsicle Finance
    type: defi-protocol
  - id: sorbetto-fragola
    name: Sorbetto Fragola
    type: defi-product
  - id: uniswap-v3
    name: Uniswap V3
    type: defi-protocol
title: "Popsicle Finance Sorbetto Fragola exploit: Uniswap V3 fee accounting flaw and $20.7M optimizer drain"
---

## Introduction

Popsicle Finance was a multi-chain yield optimization protocol that offered automated liquidity management across decentralized exchanges. Its flagship product, Sorbetto Fragola, was a Uniswap V3 liquidity optimizer that managed concentrated liquidity positions on behalf of depositors. Like other Uniswap V3 management protocols (Visor Finance, Arrakis/G-UNI), Sorbetto Fragola accepted paired token deposits, deployed them into actively managed Uniswap V3 tick ranges, and auto-compounded trading fees back into the position to maximize returns for liquidity providers.

On August 3, 2021, an attacker exploited a critical flaw in Sorbetto Fragola's fee accounting logic, draining approximately $20.7 million from the protocol's managed liquidity pools. The vulnerability was in how the optimizer contract tracked fee entitlements for individual depositors — the contract failed to properly reset a depositor's fee claim record upon deposit or transfer of LP shares, allowing the attacker to repeatedly collect the same fees by cycling deposits through fresh wallets. Each new wallet that received LP shares inherited the right to claim all accumulated but uncollected fees, enabling a multiplicative drain of the fee reserves.

## Background

### Uniswap V3 Fee Mechanics

Uniswap V3's concentrated liquidity model generates fees for liquidity providers only when trades occur within their specified price range. Fees accumulate per-position rather than per-pool, meaning each LP must individually collect their earned fees by calling the `collect` function on their Uniswap V3 position NFT. The fees are denominated in both tokens of the pair (token0 and token1) and accrue continuously as trades execute within the position's range.

For individual LPs managing their own positions, fee collection is straightforward. But for liquidity management protocols like Sorbetto Fragola, which aggregate multiple users' deposits into shared Uniswap V3 positions, the fee distribution becomes significantly more complex. The protocol must track each depositor's proportional share of accumulated fees, account for the timing of deposits and withdrawals (users who deposit later should not receive fees generated before their deposit), and handle the compounding process (converting collected fees back into liquidity).

### Sorbetto Fragola Architecture

Sorbetto Fragola operated as a vault-style contract where users deposited paired tokens (e.g., USDC and ETH) and received proportional vault shares (LP tokens) representing their claim on the pooled Uniswap V3 position. The vault contract managed a single concentrated liquidity position on Uniswap V3, periodically rebalancing the tick range to keep liquidity active near the current trading price.

The fee distribution mechanism was designed to work as follows: as the Uniswap V3 position earned trading fees, the Sorbetto contract would track the cumulative fees per share. When a user deposited or withdrew, their fee entitlement was calculated based on how long they had held shares and what proportion of the total shares they represented. The contract maintained a `feeGrowthInside` accumulator that tracked cumulative fees per unit of liquidity, and each user's fee entitlement was calculated as `(currentFeeGrowth - userFeeGrowthAtDeposit) * userShares`.

The critical flaw was in how `userFeeGrowthAtDeposit` was (or rather, was not) initialized when shares were transferred between wallets or when new shares were minted.

### Fee Accounting in Staking Contracts

The fee accounting pattern used by Sorbetto Fragola was a variant of the "reward per share" accumulator commonly used in DeFi staking contracts (also known as the "Synthetix StakingRewards" pattern). In the standard implementation, when a user deposits (or has their balance increased), their `rewardDebt` is set to `balance * accRewardPerShare`, ensuring they can only claim rewards generated after their deposit.

The vulnerability arose because Sorbetto Fragola's implementation did not properly apply this accounting reset in all cases where a user's share balance changed — specifically, when LP tokens were transferred to a new address, the receiving address's fee tracking state was not initialized, defaulting to zero. This meant the recipient could claim fees as if they had been in the pool since the beginning of the fee accumulation period.

## The Attack

### Vulnerability: Missing Fee Debt Initialization on Transfer

The core vulnerability was that when Sorbetto Fragola LP tokens were transferred to a new address, the receiving address's `feeGrowthInsideLast` (the variable tracking when the user entered the pool for fee calculation purposes) was not set to the current `feeGrowthInside` value. Instead, it remained at its default value of zero.

This meant that when the new address attempted to collect fees, the fee calculation would compute: `(currentFeeGrowthInside - 0) * balance`, where `0` was the uninitialized default rather than the actual fee growth at the time of transfer. The result was that the new address could claim all fees accumulated by the entire pool since inception, not just fees accumulated after the transfer.

The attacker exploited this by repeatedly transferring LP shares to fresh wallets and collecting fees from each wallet, effectively claiming the same pool of accumulated fees multiple times.

### Attack Execution

The attack was executed through a series of transactions on August 3, 2021:

**Step 1: Initial deposit.** The attacker deposited a significant amount of paired tokens into the Sorbetto Fragola vault, receiving LP shares in return. This established a legitimate position in the vault.

**Step 2: Fee accumulation.** The attacker waited for fees to accumulate in the vault's Uniswap V3 position. Alternatively, the attacker may have entered a pool that already had significant accumulated fees awaiting collection from Uniswap V3.

**Step 3: LP token transfer to fresh wallet.** The attacker transferred their LP shares to a new wallet address (a freshly deployed contract or a new EOA). Because the Sorbetto contract did not initialize the new wallet's fee tracking state, the new wallet's `feeGrowthInsideLast` was zero.

**Step 4: Fee collection from new wallet.** The new wallet called the fee collection function on the Sorbetto contract. The contract calculated the wallet's fee entitlement as `(currentFeeGrowthInside - 0) * shares`, treating the wallet as if it had been present since the pool's inception. This yielded a fee claim far larger than what the shares had actually earned.

**Step 5: Repeat.** The attacker transferred the LP shares to another fresh wallet and repeated the fee collection. Each transfer-and-claim cycle extracted the same pool of accumulated fees again, multiplicatively draining the fee reserves.

**Step 6: Multiple pools.** The attacker repeated this process across multiple Sorbetto Fragola pools (USDC/WETH, USDT/WETH, and others), extracting fees from each pool's accumulated reserves.

The total extraction across all pools and cycles was approximately $20.7 million. The attack was executed over multiple transactions within a relatively short time window (approximately 30 minutes), suggesting the attacker had pre-prepared the sequence of transfers and claims.

### Transaction Analysis

On-chain analysis revealed that the attacker created approximately 20-30 intermediate wallets to cycle the LP shares through. Each wallet collected fees and forwarded the proceeds to a consolidation address. The attacker had pre-funded a small amount of ETH to each intermediate wallet for gas costs, suggesting careful pre-planning.

The extracted fees were primarily in USDC, USDT, WETH, and other paired tokens from the various Sorbetto pools. The attacker consolidated the stolen tokens and converted them to ETH through Uniswap and SushiSwap, then routed the ETH through Tornado Cash for mixing.

## Impact

### Financial Losses

The total financial impact was approximately $20.7 million in drained trading fees, making it one of the largest exploits of a Uniswap V3 liquidity manager at the time. The losses were borne by liquidity providers who had deposited into Sorbetto Fragola pools — their accumulated but uncollected trading fees were stolen, and the fee reserves that should have been compounded back into their positions were drained.

Importantly, the underlying liquidity positions on Uniswap V3 were not directly affected — the principal assets deposited by users remained in the Uniswap V3 positions. However, the accumulated fees (which represented a significant portion of the vaults' total value, given Uniswap V3's high fee generation rates) were completely extracted. Users who withdrew after the attack received their principal assets but none of the trading fees their liquidity had generated.

### Token Price Impact

The ICE token (Popsicle Finance's governance token) dropped approximately 35% following the exploit, from roughly $12 to $8. The price decline reflected both the direct impact on the protocol's TVL and fee revenue, and the broader loss of confidence in the team's smart contract security capabilities. The token recovered partially over the following weeks but never returned to pre-exploit levels.

### Impact on Uniswap V3 Management Sector

The Sorbetto Fragola exploit, combined with the Visor Finance exploits (June and December 2021), established that Uniswap V3 liquidity management protocols were a particularly vulnerable category. The complexity of managing concentrated liquidity positions — including fee tracking, rebalancing, and compounding — created numerous potential failure points that simpler AMM vault contracts did not face.

The incident accelerated the adoption of formal auditing standards for Uniswap V3 management protocols and prompted competitors (Arrakis/G-UNI, Gamma Strategies) to commission additional security reviews specifically focused on their fee accounting logic.

## Response and Remediation

### Immediate Response

The Popsicle Finance team detected the attack within hours and paused all Sorbetto Fragola vault operations. They published an incident disclosure confirming the exploit and identifying the fee accounting vulnerability. The team advised users to withdraw their remaining assets from the vaults once the pause was lifted, and began working on a patched version of the contract.

### Technical Fix

The fix for the vulnerability was straightforward: properly initializing the `feeGrowthInsideLast` variable for any address that received LP shares through transfer. The corrected implementation included an override of the ERC-20 `_transfer` function (or equivalent hook) that, upon any transfer of LP shares, set the recipient's `feeGrowthInsideLast` to the current `feeGrowthInside` value. This ensured that transferred shares could only claim fees generated after the transfer, not historical fees.

Additional mitigations included adding a `collectFees` call that automatically collected any pending fees for the sender before a transfer (ensuring the sender received their earned fees before the shares moved), implementing a cooldown period between transfers for the same shares (preventing rapid cycling), and adding a per-epoch fee claim cap to bound the maximum fees any single address could collect within a time window.

### Partial Compensation

The Popsicle Finance team allocated a portion of their treasury toward compensating affected users. The compensation was paid in ICE tokens and covered approximately 30-40% of estimated losses. The team also committed to directing future protocol revenue toward a full compensation fund, though the protocol's diminished TVL and activity after the exploit limited the pace of recovery.

## Technical Analysis

### Fee Accounting Invariant Violation

The fundamental invariant that Sorbetto Fragola's fee accounting should have maintained is: the total fees claimable across all LP token holders must never exceed the total fees actually earned by the pool's Uniswap V3 position. When LP shares are transferred, the total claims against the fee pool must remain constant — the sender loses their claim, and the recipient gains a claim only for fees generated after the transfer.

The vulnerability violated this invariant because transferring shares created a new claim (for the recipient) without eliminating the existing claims (the sender's claim was already collected or persisted, and the recipient's claim was based on the full fee history). Each transfer effectively created a new claim against the entire historical fee pool, allowing multiplicative extraction.

The fix restores the invariant by ensuring that every change in share balance — whether through minting, burning, or transferring — properly updates the holder's fee tracking checkpoint to the current cumulative fee level.

### Comparison with Similar Fee Accounting Exploits

Fee accounting vulnerabilities have affected multiple DeFi protocols, though the specific mechanisms differ. The Yearn Finance vault strategy bug (February 2021, approximately $11 million) involved a similar pattern where vault share transfers could be exploited to claim disproportionate rewards. The SushiSwap MasterChef vulnerability (identified through audit, not exploited) involved a potential for reward inflation through deposit/withdrawal cycling.

The common thread is that any reward distribution system based on share-proportional accounting must carefully handle all state transitions that change a holder's share balance. The three critical transitions are minting (new shares created for a depositor), burning (shares destroyed on withdrawal), and transferring (shares move between addresses). Each of these transitions must update the holder's reward checkpoint to prevent historical reward claims.

### ERC-20 Transfer Hooks and State Management

The Sorbetto Fragola vulnerability highlights a broader challenge in DeFi: ensuring that ERC-20 transfer hooks properly update all protocol-specific state associated with token holders. When a protocol's token has meaning beyond a simple balance (e.g., it carries reward entitlements, voting power that requires delegation updates, or position metadata), the protocol must override the transfer function to update all associated state.

Standard ERC-20 implementations (OpenZeppelin, Solmate) provide hooks like `_beforeTokenTransfer` and `_afterTokenTransfer` that allow derived contracts to inject custom logic into every transfer. Using these hooks correctly is critical for any token whose holders have protocol-level state beyond their balance.

### Audit Implications

The fee accounting flaw in Sorbetto Fragola was a logic error rather than a low-level vulnerability (no reentrancy, overflow, or access control issue). Logic errors are notoriously difficult to catch through automated analysis tools because the code executes correctly according to its implementation — it simply implements the wrong behavior relative to the intended invariant.

Catching this class of bug requires an auditor to formally specify the intended invariant ("total claimable fees must not exceed total earned fees"), trace all state transitions that could violate the invariant (minting, burning, transferring), and verify that each transition properly maintains the invariant. This is fundamentally a manual reasoning task that requires both understanding of the protocol's intended behavior and systematic analysis of all code paths that modify relevant state.

## Lessons Learned

### All Share Balance Changes Must Update Fee State

The most direct lesson is that any protocol with share-proportional fee or reward distribution must update each holder's fee tracking state on every balance change — not just on deposits and withdrawals, but also on transfers. Implementing a proper `_beforeTokenTransfer` or `_afterTokenTransfer` hook that calls `_collectFees(from)` and resets `feeCheckpoint[to] = currentFeeGrowth` is essential for any reward-bearing ERC-20 token.

### Test Transfer-Based Attack Vectors

Protocol security testing should explicitly include test cases for transfer-based attacks: transfer shares to a new address and verify that the new address cannot claim historical rewards. This test case directly captures the Sorbetto Fragola vulnerability and would have identified the flaw before deployment if included in the test suite.

### Invariant-Based Auditing

Auditors reviewing fee distribution contracts should start by specifying the system's economic invariants (e.g., "sum of all claims <= total earned") and then systematically verify that every state transition preserves those invariants. This invariant-first approach is more effective than line-by-line code review for catching logic errors in complex accounting systems.

### Concentrated Liquidity Adds Accounting Complexity

Protocols managing Uniswap V3 positions face significantly more complex accounting than those managing V2-style constant-product liquidity. The per-position fee tracking, range-dependent fee accumulation, and rebalancing operations all create potential failure points in the accounting logic. Teams building V3 management protocols should invest commensurately more security resources relative to simpler vault designs.

## Conclusion

The Popsicle Finance Sorbetto Fragola exploit of August 3, 2021, drained approximately $20.7 million in accumulated trading fees from the protocol's Uniswap V3 liquidity optimizer through a fee accounting vulnerability that failed to properly initialize fee tracking state when LP shares were transferred between addresses. The attacker repeatedly transferred shares to fresh wallets and collected the full historical fee accumulation from each wallet, multiplicatively draining the fee reserves far beyond what any single set of shares had earned. The vulnerability — a missing state initialization in the transfer path — was a logic error that violated the fundamental invariant that total fee claims must not exceed total fees earned. The fix required adding a transfer hook that properly checkpointed the recipient's fee tracking state, preventing historical fee claims after transfer. The incident reinforced that share-proportional reward systems must handle all balance-changing operations (mint, burn, and transfer) with equal care, and that invariant-based testing and auditing are essential for the complex accounting systems inherent in concentrated liquidity management protocols.
