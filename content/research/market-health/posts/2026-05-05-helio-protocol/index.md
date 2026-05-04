---
date: 2026-05-05
entities:
  - id: helio-protocol
    name: Helio Protocol
    type: defi-protocol
  - id: ankr
    name: Ankr
    type: defi-protocol
  - id: bnb-chain
    name: BNB Chain
    type: blockchain
title: "Helio Protocol collateral drain via Ankr aBNBc infinite mint: cross-protocol contagion and $15M stablecoin extraction"
---

## Introduction

Helio Protocol was a decentralized lending and stablecoin protocol on BNB Chain (formerly Binance Smart Chain) that allowed users to borrow HAY, a decollateralized stablecoin, against various collateral types including liquid staking derivatives. The protocol accepted Ankr's aBNBc (Ankr BNB staking certificate) as collateral, allowing users to deposit aBNBc tokens and borrow HAY against them. The protocol's price oracle determined the USD value of aBNBc collateral based on its expected 1:1 relationship with BNB's market price, adjusted for the staking yield accrual mechanism.

On December 2, 2022, an attacker exploited the cascading effects of an Ankr aBNBc infinite mint vulnerability to drain approximately $15 million from Helio Protocol's lending pools. The attack began when the Ankr deployer key was compromised, allowing the attacker to mint 60 trillion aBNBc tokens out of thin air. The attacker then used these worthless (freshly minted) aBNBc tokens as collateral on Helio Protocol — which had not yet detected the Ankr exploit and still valued aBNBc at its pre-exploit price — to borrow and extract real HAY stablecoins, which were subsequently swapped for BUSD and other liquid assets.

## Background

### Liquid Staking Derivatives on BNB Chain

Liquid staking derivatives (LSDs) allow users to stake their native blockchain tokens (like BNB) while maintaining liquidity through derivative tokens that represent the staked position. Ankr's aBNBc was one of the primary BNB liquid staking derivatives, representing staked BNB on the Beacon Chain with accumulated staking rewards. Under normal operations, aBNBc maintained a value close to BNB's market price, with a small premium reflecting accrued staking rewards.

Multiple DeFi protocols on BNB Chain integrated aBNBc as a supported asset — accepting it as collateral for borrowing, allowing it in liquidity pools, and building yield strategies around it. This integration created a web of cross-protocol dependencies where the security of aBNBc (specifically, the integrity of its minting mechanism) became a systemic risk factor for the entire ecosystem of protocols that accepted it.

### Helio Protocol's Collateral System

Helio Protocol operated a collateral-backed stablecoin model similar to MakerDAO's DAI but optimized for BNB Chain assets. Key components included:

**Collateral vaults**: Users deposited approved collateral tokens (including aBNBc) into vaults and received borrowing capacity based on the collateral's USD value and the vault's collateralization ratio.

**HAY stablecoin**: The protocol's native stablecoin, soft-pegged to $1 USD, minted when users borrowed against their collateral. HAY was liquid on BNB Chain DEXes (primarily PancakeSwap), allowing borrowers to swap it for other assets.

**Price oracle**: The protocol used a price feed to determine aBNBc's USD value. Critically, this oracle reflected aBNBc's expected value based on BNB's market price and the staking ratio, not the real-time DEX trading price of aBNBc itself. This meant the oracle would not immediately reflect a collapse in aBNBc's actual market value caused by an exploit.

**Liquidation mechanism**: When a vault's collateral value fell below the required ratio relative to its debt, the position could be liquidated. However, liquidation depends on the oracle reporting the decreased value — if the oracle lags behind the true market price, undercollateralized positions can exist without being liquidated.

### The Ankr aBNBc Exploit (Upstream)

The root cause of the Helio Protocol drain was an exploit of Ankr's aBNBc token contract on December 2, 2022. The Ankr deployer's private key (the key authorized to upgrade the aBNBc token's proxy implementation) was compromised through an undisclosed vector. Using this key, the attacker:

1. Upgraded the aBNBc token contract to a new implementation that included an unrestricted mint function
2. Called this mint function to create approximately 60 trillion aBNBc tokens, minted directly to the attacker's wallet
3. Began selling the minted aBNBc on DEXes, crashing its market price to near zero

This infinite mint attack was the upstream event that enabled the subsequent exploitation of Helio Protocol and other protocols that accepted aBNBc as collateral.

## The Attack

### Cross-Protocol Exploitation Vector

The Helio Protocol drain was not a direct exploit of Helio's smart contract code. Instead, it was a cross-protocol contagion event: the attacker exploited a vulnerability in one protocol (Ankr) and then used the proceeds to extract value from a dependent protocol (Helio) whose security assumptions about the upstream token had been invalidated.

The attack vector was:
1. The attacker minted unlimited aBNBc through the compromised Ankr contract
2. Helio Protocol's oracle still valued aBNBc at its pre-exploit price (~$300+ per token, tied to BNB's value)
3. The attacker deposited the freshly minted (worthless) aBNBc as collateral on Helio
4. Helio's system, trusting the oracle's valuation, allowed the attacker to borrow HAY against this collateral
5. The attacker swapped the borrowed HAY for real assets (BUSD, USDT) on PancakeSwap

### Detailed Attack Flow

**Phase 1: Ankr exploit.** The attacker compromised the Ankr deployer key and minted 60 trillion aBNBc tokens. This occurred at approximately 00:30 UTC on December 2, 2022.

**Phase 2: Collateral deposit.** Within minutes of the Ankr mint, the attacker deposited a large quantity of the freshly minted aBNBc into Helio Protocol's collateral vaults. Because Helio's oracle had not yet updated to reflect aBNBc's true market price (which was rapidly approaching zero as the attacker dumped tokens on DEXes), the protocol accepted the deposit at the pre-exploit valuation.

**Phase 3: HAY borrowing.** With millions of dollars worth of (apparently valid) aBNBc collateral deposited, the attacker borrowed the maximum amount of HAY stablecoins allowed by the collateralization ratio. The attacker's aBNBc position appeared well-collateralized according to the oracle, even though the tokens were practically worthless.

**Phase 4: HAY liquidation.** The attacker swapped the borrowed HAY for BUSD and other liquid stablecoins on PancakeSwap and similar DEXes. This created sell pressure on HAY, pushing it below its $1 peg, but the attacker was able to extract approximately $15 million in real value before HAY liquidity dried up.

**Phase 5: Fund extraction.** After converting HAY to liquid stablecoins, the attacker began bridging funds off BNB Chain and consolidating into fewer wallets, following standard post-exploit laundering patterns.

### Oracle Lag as the Critical Enabler

The attack was only possible because Helio Protocol's oracle continued to report aBNBc's pre-exploit value during the critical window between the Ankr mint (which invalidated aBNBc's value) and the protocol's detection/response. This oracle lag created a window of approximately 30-60 minutes where the attacker could deposit worthless tokens and borrow real stablecoins against them.

The oracle was not technically "wrong" — it was reporting aBNBc's expected value based on its underlying staking position, which had not changed. The problem was that the oracle did not account for the possibility that aBNBc's minting integrity had been compromised, rendering the token's market value independent of its theoretical staking value.

## Impact

### Financial Losses

The total value extracted from Helio Protocol was approximately $15 million in HAY stablecoins, which the attacker converted to BUSD and other liquid assets. The losses were ultimately absorbed by HAY holders and Helio Protocol's stability mechanisms:

- HAY's peg broke temporarily, trading as low as $0.20 on some DEXes
- The protocol's insurance fund was partially depleted to restore the peg
- Liquidity providers in HAY pools on PancakeSwap suffered impermanent loss as HAY depegged
- Helio Protocol's governance token declined significantly in value

### Cross-Protocol Contagion

The Ankr/Helio incident demonstrated how a single upstream exploit can cascade through the DeFi ecosystem. Beyond Helio, the Ankr aBNBc exploit affected:
- DEX liquidity providers who held aBNBc in their pools
- Other lending protocols that accepted aBNBc as collateral
- Yield aggregators that had aBNBc-based strategies
- Users who held aBNBc directly in their wallets (their tokens became worthless)

The total impact of the Ankr exploit across all affected protocols and users was estimated at $20-30 million, with Helio Protocol being the single largest downstream victim.

### Ankr's Response and Compensation

Ankr acknowledged the exploit and worked with BNB Chain's team to freeze attacker addresses where possible. Ankr committed to compensating affected users, including deploying a new aBNBc token contract (with proper access controls on the upgrade mechanism) and distributing replacement tokens to legitimate holders based on a snapshot taken before the exploit. The process took several weeks to complete.

## Technical Analysis

### Cross-Protocol Dependency Risk

The Helio Protocol drain illustrates a fundamental risk in composable DeFi: protocols that accept tokens from other protocols as collateral inherit the security risk of those upstream protocols. Helio's own smart contracts functioned correctly — they accepted collateral, valued it via oracle, and issued loans according to their parameters. The failure was in the assumption that aBNBc was a legitimate, properly minted token.

This dependency risk is difficult to mitigate because:
- DeFi composability depends on protocols accepting other protocols' tokens
- Verifying the integrity of upstream token minting in real-time is computationally expensive and architecturally complex
- Oracle systems typically value tokens based on price feeds or mathematical models, not based on the token's minting integrity
- The window between an upstream exploit and downstream detection can be very short (minutes), but sufficient for an attacker to extract significant value

### Oracle Design for Derivative Tokens

The oracle design challenge for derivative tokens like aBNBc is balancing responsiveness against manipulation resistance:

**Market price oracles** (using DEX TWAP or Chainlink feeds based on DEX prices) would have detected the aBNBc price crash quickly — within minutes of the attacker dumping tokens on DEXes. However, market price oracles are vulnerable to manipulation through flash loans and large trades, which is why many protocols avoid using them for collateral valuation.

**Fundamental value oracles** (calculating aBNBc's expected value based on BNB's price and the staking ratio) are manipulation-resistant but cannot detect integrity failures in the upstream protocol. The Ankr exploit did not change BNB's staking ratio — it created new tokens outside the legitimate minting pathway.

**Hybrid approaches** that cross-reference market price with fundamental value and flag significant divergences could detect events like the Ankr exploit (where market price crashed while fundamental value remained stable), but they add complexity and may produce false positives during legitimate market dislocations.

### Circuit Breakers and Emergency Response

The Helio exploit highlights the need for automated circuit breakers in DeFi lending protocols:

**Deposit rate limiters**: Limiting the amount of collateral that can be deposited in a short time period would have slowed the attacker's ability to deposit billions of worthless aBNBc tokens. If the protocol only allowed $1 million in new aBNBc deposits per hour, the extraction would have been capped at a fraction of the actual loss.

**Collateral supply monitoring**: Monitoring the total supply of collateral tokens for sudden changes could detect infinite mint attacks. A 60 trillion token increase in aBNBc supply is an unmissable anomaly — an automated system that paused aBNBc deposits upon detecting a supply change exceeding a threshold could have prevented the exploit.

**Multi-oracle cross-validation**: Using multiple independent oracles and requiring consensus before accepting a price value adds defense against oracle lag. If one oracle reported aBNBc at $300 while a DEX-based oracle reported $0.01, the system could pause operations pending manual review.

### Comparison with Similar Cross-Protocol Contagion Events

**Cream Finance / C.R.E.A.M. (October 2021, ~$130M)**: Cream Finance was exploited through a combination of flash loans and token minting. While mechanistically different from the Ankr/Helio chain, the pattern of "mint tokens and use them as collateral" is analogous — the attacker created inflated token value and extracted real value through a lending protocol.

**Mango Markets (October 2022, ~$114M)**: While Mango Markets was exploited through market manipulation rather than token minting, the pattern is similar — the attacker inflated the value of their collateral (MNGO tokens through open market manipulation) and borrowed against the inflated value. The underlying issue — that collateral value can be artificially inflated — is common to both incidents.

**Euler Finance (March 2023, ~$197M)**: Euler's exploit involved minting and donating tokens to manipulate internal exchange rates, allowing the attacker to borrow more than their collateral was worth. While the mechanism was internal to Euler (not cross-protocol), the pattern of inflating collateral value to extract real borrowing value is identical.

### Supply-Side Verification

A potential defense against infinite mint attacks is for downstream protocols to monitor the upstream token's total supply and compare it against expected values. For aBNBc, the legitimate total supply should grow slowly (as new users stake BNB) and should never increase by orders of magnitude in a single block. An automated check that verifies `totalSupply()` before accepting deposits would have detected the Ankr exploit:

Before the attack: aBNBc totalSupply = ~2.5 million tokens
After the attack: aBNBc totalSupply = ~60 trillion tokens

A simple check — "if totalSupply has changed by more than 10% since last checked, pause deposits" — would have prevented the entire downstream exploitation.

## Lessons Learned

### Oracle Systems Must Account for Upstream Integrity Failures

Price oracles for derivative tokens must not only provide accurate pricing but also detect when the underlying token's minting integrity has been compromised. This requires monitoring token supply, cross-referencing multiple price sources, and implementing circuit breakers that activate when fundamental indicators diverge from expected ranges.

### Deposit Rate Limiters as Standard Practice

Lending protocols should implement deposit rate limiters that cap the amount of any single collateral type that can be deposited within a time window. This limits the damage from any attack that depends on quickly depositing large amounts of compromised collateral.

### Supply Monitoring for Accepted Collateral Tokens

Protocols that accept external tokens as collateral should monitor those tokens' total supply for anomalies. A sudden, large increase in supply is a strong signal that the token's minting mechanism has been compromised, and should trigger an automatic pause on new deposits of that token.

### Cross-Protocol Risk Assessment

DeFi protocols must explicitly assess and communicate the cross-protocol dependencies in their security model. Accepting aBNBc as collateral means inheriting the security of Ankr's token contract, Ankr's key management, and Ankr's upgrade mechanism. These upstream risks should be formally evaluated, documented, and mitigated through supply monitoring, oracle cross-validation, and deposit limits.

### Emergency Response Automation

The 30-60 minute window between the Ankr exploit and Helio's response was sufficient for the attacker to extract $15 million. Human-speed incident response is too slow for DeFi exploits that can drain protocols in minutes. Automated monitoring and response systems — including supply-change detection, oracle divergence alerts, and automatic deposit pauses — are essential for reducing the exploitation window.

## Conclusion

The Helio Protocol drain of December 2, 2022, extracted approximately $15 million through cross-protocol contagion from the Ankr aBNBc infinite mint exploit. The attacker compromised Ankr's deployer key, minted 60 trillion aBNBc tokens, and deposited them as collateral on Helio Protocol — which had not yet detected the upstream exploit and still valued aBNBc at its pre-exploit price. The attacker borrowed HAY stablecoins against the worthless collateral and converted them to liquid assets before the protocol could respond. This incident demonstrates the systemic risk of cross-protocol dependencies in composable DeFi: a single upstream token integrity failure can cascade through all protocols that accept that token, and traditional oracle systems designed for price accuracy do not detect minting integrity failures. Defense requires supply monitoring, deposit rate limiters, multi-oracle cross-validation, and automated circuit breakers that can respond faster than human incident response teams.
