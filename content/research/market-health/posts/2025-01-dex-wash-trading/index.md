---
title: "DEX Wash Trading: $2.57 Billion in Suspected Artificial Volume Across EVM Chains"
date: "2024-01 -- 2024-12"
description: "On-chain analysis of decentralized exchange wash trading across Ethereum, BNB Smart Chain, and Base reveals up to $2.57 billion in suspected artificial trading volume during 2024, driven by volume bot services and airdrop farming."
entities:
  - Uniswap
  - PancakeSwap
  - Volume.li
---

## Summary

Analysis of decentralized exchange trading activity across Ethereum, BNB Smart Chain, and Base during 2024 identified an estimated $2.57 billion in suspected wash trading volume. The activity was concentrated in approximately 1,000 to 1,800 liquidity pools per month, representing 0.2% to 0.3% of the roughly 500,000 pools active monthly. Two independent detection methods produced estimates ranging from $704 million to $1.87 billion on these three chains alone, with the higher estimate suggesting the $2.57 billion figure when extrapolated to include additional EVM-compatible chains.

## Wash Trading Services as a Business

Unlike centralized exchanges where wash trading requires multiple accounts, DEX wash trading is enabled by specialized services that operate as turnkey volume generation businesses. One documented service, Volume.li, was observed generating artificial activity for the Donald J. Chump token, which had 6,939 holders as of January 2025. Within five days, Volume.li's bot generated 10,341 pairs of buy and sell orders using five different addresses, creating $39,723 in fake trading volume on Uniswap.

The Volume.li service operates through smart contract intermediaries. Addresses controlled by the service send transactions to their own smart contracts, which then trigger multiple wash trade transactions on the target DEX. The trading bot uses a specific function signature (0x5f437312) to initiate trades, creating a detectable on-chain fingerprint.

During the period from July 27 to July 30, Volume.li's activity accounted for approximately 43% of the token's total trading volume on Uniswap. This demonstrates how a single volume bot service can dominate the apparent liquidity of a token, misleading traders about genuine market interest.

## Scale and Distribution

Combined wash trading volume across the three analyzed chains showed consistent monthly activity throughout 2024:

- **Ethereum**: The largest share of suspected wash trading volume, driven by the size of its DEX ecosystem and the number of new token launches
- **BNB Smart Chain**: Significant artificial volume concentrated in low-liquidity token pairs on PancakeSwap and related DEXes
- **Base**: Despite being a newer chain, exhibited measurable wash trading activity, likely driven by airdrop farming and new token launches seeking to establish artificial market presence

The 0.2-0.3% of pools showing wash trading activity is a small percentage, but these pools disproportionately inflate aggregate volume figures reported by analytics platforms.

## Detection Methodology

Two complementary approaches were used to estimate wash trading volume:

**Heuristic 1 (Conservative estimate: $704M)**: Identified addresses that repeatedly traded the same token pair with themselves or with a small set of counterparties, executing trades that resulted in minimal net position changes.

**Heuristic 2 (Broader estimate: $1.87B)**: Extended the analysis to include coordinated trading patterns across clusters of addresses that, while not directly self-trading, exhibited timing and size patterns consistent with coordinated volume generation.

The difference between the two estimates reflects the difficulty of distinguishing between genuine arbitrage activity and coordinated wash trading when multiple addresses are involved.

## Incentive Structure

Three primary motivations drive DEX wash trading:

1. **Token ranking manipulation**: Inflated volume pushes tokens higher on aggregator sites like CoinGecko and CoinMarketCap, increasing visibility and attracting retail buyers

2. **Airdrop farming**: Many protocols distribute tokens based on trading volume or interaction frequency. Wash trading generates qualifying activity at minimal cost when gas fees are low

3. **Liquidity pool incentives**: Some protocols offer rewards based on pool volume, creating a direct financial return on artificial trading activity

## Implications

The $2.57 billion figure represents suspected wash trading on only three EVM chains. The actual total across all DEX-supporting blockchains including Solana, Arbitrum, Optimism, Avalanche, and others is likely substantially higher. For traders relying on volume data to assess token liquidity and market interest, these findings underscore the need to look beyond aggregate volume figures and examine the distribution of counterparties, trade sizes, and temporal patterns before making trading decisions.
