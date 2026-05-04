---
date: 2026-05-05
entities:
  - id: spartan-protocol
    name: Spartan Protocol
    type: defi-protocol
  - id: binance-smart-chain
    name: Binance Smart Chain
    type: blockchain
  - id: pancakeswap
    name: PancakeSwap
    type: defi-protocol
title: "Spartan Protocol liquidity pool share inflation exploit: AMM pool manipulation and $30M drain on BSC"
---

## Introduction

Spartan Protocol was a decentralized finance protocol operating on Binance Smart Chain (BSC) that provided automated market maker (AMM) liquidity pools, a synthetic asset minting mechanism, and a lending platform. Inspired by Thorchain's continuous liquidity pool model, Spartan Protocol used a bonding-curve AMM design where the native SPARTA token served as the base pair for all trading pools. The protocol attracted significant liquidity to BSC during the chain's rapid growth phase in early 2021, positioning itself as a core infrastructure layer for decentralized trading on the network.

On May 2, 2021, an attacker exploited a critical vulnerability in the liquidity pool share calculation logic of Spartan Protocol, draining approximately $30 million in assets from the protocol's largest pools. The attack leveraged a flaw in how the protocol calculated the number of liquidity pool (LP) tokens to mint when a user added liquidity — the function used the pool's token balances at the moment of the liquidity addition rather than the balances that existed before the transaction began. By manipulating pool balances through large swaps immediately before adding liquidity, the attacker inflated the value of their LP shares and then redeemed them for a disproportionately large amount of underlying assets. The exploit was executed across multiple transactions within a short time window, with the attacker using flash loans from PancakeSwap to amplify the capital available for the manipulation.

## Background

### Spartan Protocol Architecture

Spartan Protocol's AMM design diverged from the dominant Uniswap-style constant-product (x * y = k) model. Instead, it implemented a slip-based fee model inspired by Thorchain, where swap fees were proportional to the size of the swap relative to the pool depth. This design aimed to incentivize deeper liquidity by making large trades progressively more expensive (higher slippage), while keeping small trades cheap. The SPARTA token was mandatory as one side of every pool — users could not create pools between two arbitrary tokens; instead, all trading pairs were denominated against SPARTA (e.g., SPARTA/WBNB, SPARTA/BUSD, SPARTA/BTCB).

The protocol's core components included the Pool contract (managing individual liquidity pools and implementing the AMM logic), the Router contract (handling multi-step operations like adding liquidity, removing liquidity, and executing swaps), and the DAO contract (governing protocol parameters and upgrades through SPARTA token voting). The Pool contract was responsible for minting and burning LP tokens when users added or removed liquidity, and this was where the critical vulnerability resided.

### Liquidity Addition Mechanics

When a user added liquidity to a Spartan Protocol pool, the process involved two steps: first, the user transferred SPARTA tokens and the paired token (e.g., WBNB) to the Pool contract; second, the user called the `addLiquidity` function, which calculated the number of LP tokens to mint based on the value of the deposited assets relative to the existing pool. The LP token calculation was designed to ensure that new liquidity providers received shares proportional to the value they contributed.

The standard approach for computing LP mints in most AMM protocols follows one of two patterns. The first pattern, used by Uniswap V2, calculates the mint amount as `min(amount0 * totalSupply / reserve0, amount1 * totalSupply / reserve1)`, where `reserve0` and `reserve1` are the pool's token balances before the deposit. The key word is "before" — Uniswap V2 stores the previous reserves in state variables that are updated only at the end of each transaction through the `_update` function, making them resistant to within-transaction manipulation.

The second pattern, which Spartan Protocol used, was to compute the pool's valuation based on the current token balances at the time of the LP mint calculation. This meant the function read the pool's live `balanceOf` values rather than cached reserve values. This design choice created a vulnerability: if an attacker could alter the pool's token balances immediately before calling `addLiquidity` (for example, by executing a large swap), the LP share calculation would be based on the manipulated balances rather than the true pre-transaction reserves.

### Flash Loans on BSC

By May 2021, flash loan functionality was readily available on BSC through PancakeSwap (forked from Uniswap V2) and other lending protocols. Flash loans allow users to borrow arbitrarily large amounts of capital within a single transaction, provided the borrowed amount (plus fees) is returned before the transaction completes. This mechanism was critical to the Spartan Protocol exploit because it allowed the attacker to amass the large capital base needed to significantly move pool balances through swaps, without requiring any initial capital of their own.

## The Attack

### Vulnerability: Balance-Based LP Calculation

The core vulnerability was in the Pool contract's `addLiquidity` function. When computing the number of LP tokens to mint for a depositor, the function calculated the depositor's share based on the ratio of their deposit to the pool's current token balances. Critically, "current token balances" meant the pool's actual `balanceOf` at the moment of the calculation, not a cached or time-weighted value.

This created a manipulation vector: by swapping a large amount of one token into the pool (increasing the balance of one token and decreasing the other), the attacker could alter the balance ratio that the LP calculation depended on. If the attacker then immediately added liquidity, the LP mint calculation would use the post-swap (manipulated) balances, potentially awarding the attacker more LP tokens than their deposit warranted.

The specific flaw was more nuanced than a simple balance read. The protocol's LP calculation included a "units" formula that attempted to value the depositor's contribution in terms of the pool's total value. However, the formula's inputs — the pool's SPARTA balance and the pool's paired-token balance — were read from the live contract state. When a large swap artificially inflated one side of the pool, the formula miscalculated the relative value of the depositor's contribution, resulting in an inflated LP mint.

### Attack Sequence

The attacker executed the exploit through a series of coordinated transactions targeting the SPARTA/WBNB pool, the protocol's deepest and most valuable pool. The attack flow proceeded as follows:

**Step 1: Flash loan acquisition.** The attacker obtained a flash loan of approximately 61,800 WBNB (worth roughly $38 million at the time) from PancakeSwap's WBNB/BUSD pool. This capital provided the firepower needed to significantly move the Spartan Protocol pool's balance ratios.

**Step 2: Pool balance manipulation via swap.** The attacker swapped a large portion of the borrowed WBNB into the SPARTA/WBNB pool, receiving SPARTA tokens in return. This swap had two effects: it dramatically increased the WBNB balance in the pool (making WBNB appear "cheaper" relative to the pool's reserves) and decreased the SPARTA balance (making SPARTA appear more valuable). The pool's balance ratio was now significantly skewed from its pre-attack equilibrium.

**Step 3: Liquidity addition at manipulated prices.** With the pool's balance ratio distorted, the attacker added liquidity by depositing SPARTA and WBNB into the pool. Because the `addLiquidity` function calculated LP share allocation based on the current (post-swap) pool balances, the attacker's deposit was valued against the manipulated ratio. The formula effectively overvalued the attacker's SPARTA contribution (since SPARTA appeared scarce in the pool after the large swap) and minted more LP tokens than the deposit would have warranted at the pre-manipulation balance ratio.

**Step 4: Reverse the swap.** The attacker swapped the SPARTA tokens received in Step 2 back into the pool, partially restoring the balance ratio toward its original state. This step recovered most of the WBNB used in the initial manipulation swap.

**Step 5: Liquidity removal.** With an inflated number of LP tokens from Step 3, the attacker called `removeLiquidity` to redeem their shares. Because the pool's balance ratio was now closer to its original state (after the reverse swap), the LP tokens were redeemed at approximately the fair value per share — but the attacker held more shares than they should have. The redemption returned more SPARTA and WBNB than the attacker had deposited in Step 3.

**Step 6: Flash loan repayment and profit extraction.** The attacker repaid the WBNB flash loan (with the standard 0.3% fee) and retained the profit — the excess SPARTA and WBNB extracted through the inflated LP shares.

**Step 7: Repeat.** The attacker repeated this cycle multiple times across several transactions, each time draining additional value from the pool. The attack also targeted other Spartan Protocol pools beyond SPARTA/WBNB, including SPARTA/BUSD and SPARTA/BTCB.

### Transaction Analysis

On-chain analysis revealed that the attacker executed the exploit through approximately 10-12 transactions over a period of roughly 30 minutes. Each transaction followed the same swap-add-reverse-remove pattern, with the flash loan amounts and swap sizes calibrated to maximize extraction while keeping the pool liquid enough for subsequent attacks. The total extraction across all transactions and pools was approximately $30.5 million in various assets (primarily WBNB, BUSD, and BTCB).

The attacker's wallet was funded with a small amount of BNB from Tornado Cash (the Ethereum-based privacy mixer, accessed through a bridge to BSC) to pay for gas fees. After the exploit, the stolen assets were initially held on BSC before being partially bridged to Ethereum and mixed through Tornado Cash over the following days.

## Impact

### Financial Losses

The total financial impact was approximately $30 million in drained pool assets, making it one of the largest exploits on Binance Smart Chain at the time. The losses were borne by liquidity providers who had deposited assets into the affected pools — their LP tokens now represented claims on a significantly diminished pool of assets. The SPARTA/WBNB pool, which had been the protocol's flagship with over $50 million in TVL, lost more than half its value in the attack.

Individual liquidity providers' losses were proportional to their share of the affected pools. Users who had deposited into the SPARTA/WBNB, SPARTA/BUSD, and SPARTA/BTCB pools collectively lost approximately $30 million. Some large liquidity providers lost hundreds of thousands of dollars in a matter of minutes.

### Token Price Impact

The SPARTA token price collapsed by approximately 55% in the hours following the exploit, falling from roughly $1.70 to $0.75. This crash was driven by several factors: the attacker selling extracted SPARTA tokens on the open market, panic selling by SPARTA holders who feared further exploits, and the fundamental loss of protocol TVL reducing confidence in SPARTA's utility and governance value.

The token never recovered to its pre-exploit levels. Within weeks, SPARTA was trading below $0.30, representing a cumulative decline of over 80% from the pre-attack price. The sustained price decline reflected the market's assessment that the protocol's credibility had been irreparably damaged and that the development team faced an uphill battle to restore user trust.

### Impact on BSC Ecosystem

The Spartan Protocol exploit occurred during a period of intense growth and security scrutiny for the BSC ecosystem. In the weeks surrounding the attack, several other BSC protocols were exploited — including Uranium Finance (April 28, 2021), PancakeBunny (May 19, 2021), and Belt Finance (May 30, 2021) — creating a narrative that BSC DeFi protocols were particularly vulnerable due to rapid deployment without adequate auditing. The Spartan exploit contributed to a broader reassessment of BSC protocol security and accelerated the adoption of formal audit requirements among BSC DeFi projects.

## Response and Remediation

### Immediate Response

The Spartan Protocol team detected the attack within approximately one hour and immediately paused all pool operations through emergency admin functions. They published an initial disclosure on social media confirming the exploit and advising users not to interact with the protocol's contracts until further notice. The team began working with blockchain security firms including PeckShield and CertiK to analyze the attack vector and develop a fix.

Binance (the operator of BSC) was also notified, though as a public blockchain, there was no mechanism to reverse the transactions or freeze the attacker's funds at the chain level. The team traced the attacker's fund movements and published the relevant wallet addresses, enabling centralized exchanges to flag incoming deposits from those addresses.

### Contract Upgrade

The Spartan Protocol team developed and deployed an upgraded version of the Pool contract that addressed the root cause of the vulnerability. The key change was replacing the live `balanceOf`-based LP calculation with a cached reserves pattern similar to Uniswap V2's approach. The new contract stored the pool's token balances as internal state variables (analogous to Uniswap V2's `reserve0` and `reserve1`), updating them only through explicit sync operations at well-defined points in the transaction flow.

This change ensured that the LP calculation's balance inputs could not be manipulated by same-transaction swaps, because the reserves used in the calculation reflected the pool's state at the end of the previous transaction, not the current (potentially manipulated) state. Additional safeguards included a minimum LP mint amount to prevent dust-level minting from rounding exploits, a per-block add-liquidity cooldown to limit the speed at which an attacker could iterate the exploit cycle, and enhanced event emissions for real-time monitoring of large liquidity operations.

### Liquidity Migration

Users were provided a migration path from the old (exploited) pool contracts to the new (patched) contracts. The migration process involved withdrawing remaining liquidity from the old pools (which still held the post-exploit residual assets), re-depositing into the new pools, and receiving compensation tokens for a portion of the losses incurred in the exploit.

The compensation was partial — the protocol did not have sufficient reserves to make all liquidity providers whole. The team allocated a portion of the protocol's treasury and future fee revenue toward a compensation fund, but the total reimbursement was estimated at approximately 30-40% of lost value, with the remainder absorbed as a loss by liquidity providers.

### Audit and Security Improvements

Following the exploit, the Spartan Protocol team commissioned formal audits of all upgraded contracts from CertiK and an additional independent auditor. The audit scope covered the Pool contract, Router contract, DAO contract, and all peripheral contracts. The team also implemented a bug bounty program through Immunefi, offering up to $100,000 for critical vulnerability discoveries.

The upgraded protocol incorporated a timelock on all admin operations, multi-sig control over emergency pause and parameter changes, and a staged rollout process where new contract versions were deployed to a testnet fork with automated exploit simulation testing before being promoted to mainnet.

## Technical Analysis

### Balance-Based vs. Reserve-Based Accounting

The fundamental distinction between vulnerable and secure AMM implementations lies in how the liquidity calculation references the pool's asset balances. The two approaches can be characterized as follows.

In balance-based accounting (Spartan Protocol's original design), the pool reads its token balances using the ERC-20 `balanceOf(address(this))` function at the time of the LP calculation. This approach is simple and always reflects the true current state of the contract's holdings, but it is vulnerable to same-transaction manipulation. Any operation that changes the pool's balance — a swap, a direct token transfer, or even a self-destructing contract that force-sends BNB — will immediately affect the next LP calculation.

In reserve-based accounting (Uniswap V2's design, adopted by Spartan Protocol V2), the pool maintains internal state variables (`reserve0`, `reserve1`) that track the pool's intended asset balances. These reserves are updated only through specific sync functions called at the end of swap and liquidity operations. The LP calculation uses these cached reserves rather than live balances, making it immune to within-transaction balance manipulation. The pool periodically reconciles its reserves with actual balances through the sync mechanism, but this reconciliation happens at controlled points in the execution flow.

The reserve-based pattern is strictly more secure for AMM implementations because it decouples the LP valuation from the current transaction's effects. Any attempt to manipulate the pool through swaps will only affect reserves after the sync is called — by which time the LP calculation has already used the pre-manipulation reserves.

### Flash Loan Amplification

Flash loans were instrumental in the Spartan Protocol attack because they provided the capital needed to move pool balances by a significant percentage. Without flash loans, the attacker would have needed tens of millions of dollars in personal capital to execute the same manipulation, dramatically reducing the addressable set of potential attackers.

The interaction between flash loans and balance-based LP calculations creates a particularly dangerous vulnerability surface: flash loans provide unlimited capital for a single transaction, and balance-based calculations are vulnerable to within-transaction manipulation. Together, they mean that any AMM with balance-based LP calculations and sufficient pool depth is exploitable by anyone with the technical ability to write a flash loan attack contract, regardless of their capital base.

This dynamic was well-understood by security researchers before the Spartan Protocol exploit — the dYdX flash loan attacks on bZx in February 2020 had demonstrated the principle — but many BSC protocols deployed in the rapid growth period of early 2021 either were not aware of the risk or chose to accept it in favor of simpler contract designs.

### Comparison with Similar AMM Exploits

The Spartan Protocol exploit belongs to a category of AMM attacks that manipulate price or balance inputs to inflate LP share minting. Similar attacks include the Warp Finance exploit (December 2020, ~$7.7 million), which manipulated Uniswap LP token prices used as collateral in a lending protocol — a related but distinct vector where the LP token itself was mispriced rather than the minting process being flawed; the Uranium Finance exploit (April 2021, ~$50 million), which exploited a bug in a Uniswap V2 fork's `swap` function where a typo caused the constant-product invariant check to use incorrect precision, allowing tokens to be extracted without adequate payment; and the Belt Finance exploit (May 2021, ~$6.2 million), which used flash loans to manipulate the virtual price of a Curve-style StableSwap pool on BSC, inflating the redemption value of LP tokens.

The common thread across these exploits is the use of flash loans to temporarily manipulate on-chain price or balance data that feeds into value-sensitive calculations (LP minting, collateral pricing, redemption value). The defense in all cases involves ensuring that sensitive calculations use manipulation-resistant inputs — either time-weighted average prices (TWAPs), cached reserves, or oracle-provided prices rather than spot/instantaneous values.

### Slip-Based Fee Model Interaction

Spartan Protocol's Thorchain-inspired slip-based fee model added a subtle dimension to the exploit. In a standard constant-product AMM, large swaps that manipulate pool balances incur significant impermanent loss but do not create a separate arbitrage path through LP minting. In Spartan Protocol's slip-based model, the fee structure meant that the attacker's large manipulation swaps were more expensive (higher slippage fees) than they would have been in a constant-product model. However, the LP share inflation more than compensated for the elevated swap costs, making the attack profitable despite the fee penalty.

This interaction highlights an important principle in DeFi security: innovative economic mechanisms (like slip-based fees) may mitigate certain risks (MEV from arbitrage) while leaving others (LP calculation manipulation) unaddressed. Security analysis must evaluate the full attack surface, not just the specific risks that a particular mechanism was designed to mitigate.

## Lessons Learned

### Cache State for Value-Sensitive Calculations

The most direct technical lesson is that any smart contract calculation that determines token minting, redemption, or valuation must use manipulation-resistant inputs. For AMMs, this means cached reserves rather than live balances. For lending protocols, this means oracle prices rather than spot DEX prices. For yield vaults, this means verified strategy returns rather than balance-of checks. Any design that reads live on-chain state for a value-sensitive calculation is potentially vulnerable to same-transaction manipulation via flash loans.

### Audit Before TVL Growth

The Spartan Protocol team launched the protocol without a comprehensive security audit during a period of rapid BSC ecosystem growth. The logic was that speed-to-market was critical for capturing TVL in the competitive BSC DeFi landscape. However, the $30 million loss vastly exceeded any competitive advantage gained from early launch. The lesson is that the cost of a security audit (typically $50,000-$200,000 for a comprehensive review) is negligible compared to the potential loss from a preventable exploit, and no amount of TVL growth justifies deploying unaudited contracts that handle user funds.

### Flash Loan Threat Modeling

Any DeFi protocol operating on a chain with flash loan infrastructure must explicitly model flash loan attacks during security review. This means assuming that an attacker can borrow the entire TVL of major pools on the same chain within a single transaction, and designing accordingly. Protocols that cannot withstand manipulation by an adversary with effectively unlimited single-transaction capital are inherently vulnerable and should not hold significant user funds.

### Partial Compensation Erodes Trust More Than Full Compensation

The Spartan Protocol team's decision to offer only 30-40% compensation to affected users, while understandable given treasury constraints, contributed to lasting damage to user trust and protocol adoption. Projects should consider whether maintaining a dedicated insurance or compensation fund — funded through a portion of protocol revenue — would be feasible before an exploit occurs, enabling more complete reimbursement in the event of a security incident.

## Conclusion

The Spartan Protocol liquidity pool share inflation exploit of May 2, 2021, resulted in the drainage of approximately $30 million from the protocol's AMM pools on Binance Smart Chain. The attack exploited a fundamental flaw in the LP token minting calculation — the use of live token balances rather than cached reserves to determine the value of liquidity deposits. By using flash loans to temporarily distort pool balance ratios through large swaps, the attacker inflated the LP shares minted for their deposits, then redeemed these inflated shares at near-original balance ratios to extract more assets than they had contributed. The vulnerability was a direct consequence of departing from the reserve-based accounting pattern established by Uniswap V2, and the fix was equally direct: migrating to cached-reserve calculations immune to same-transaction manipulation. The incident reinforced critical security principles for AMM design — manipulation-resistant inputs for value calculations, mandatory flash loan threat modeling, and formal auditing before TVL accumulation — lessons that remain essential for any protocol implementing automated liquidity provision on public blockchains.
