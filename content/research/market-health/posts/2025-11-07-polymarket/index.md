---
title: "Network Analysis Reveals 25% of Polymarket Volume Is Wash Trading"
date: 2025-11-07
entities:
  - Polymarket
---

## Summary

1. A **peer-reviewed Columbia University study** published in November 2025 found that approximately **25% of Polymarket's total historical trading volume is artificially generated** through wash trading, casting doubt on the platform's reported market metrics.
2. **Peak manipulation reached nearly 60%** of weekly volume in December 2024, coinciding with the platform's post-US-election traffic surge and anticipated token airdrop campaigns.
3. **Sports and election prediction markets** were disproportionately affected, with some weekly periods showing **over 90% suspicious trade volume** in specific market categories.
4. **Network-based detection methodology** using on-chain wallet clustering, trading loop analysis, and behavioral fingerprinting identified **tens of thousands of accounts** participating in coordinated wash trading patterns on Polygon.
5. The primary **motivation appears to be gaming anticipated token airdrops** rather than direct profit extraction, with wash traders inflating their volume metrics to qualify for larger airdrop allocations.
6. Despite operating on a public blockchain (Polygon), the study demonstrates that **wash trading persists even with full transaction transparency**, challenging the assumption that on-chain markets are inherently more resistant to volume manipulation.

## Background

Polymarket is a decentralized prediction market platform built on the Polygon blockchain, where users trade binary outcome contracts on real-world events. The platform gained significant attention during the 2024 US Presidential election cycle, with cumulative trading volumes exceeding $9 billion by late 2024. As the largest prediction market by volume, Polymarket has been cited by media outlets, researchers, and policymakers as a barometer for event probabilities.

However, the platform's reliance on trading volume as a credibility metric creates incentives for artificial volume generation. Unlike centralized exchanges where wash trading detection relies on proprietary order book data, Polymarket's settlement on Polygon provides a fully transparent transaction record amenable to network analysis.

## Study Methodology

Researchers from Columbia Business School developed a novel network-based detection algorithm published on SSRN ("Network-Based Detection of Wash Trading in Decentralized Prediction Markets"). The methodology combines three complementary approaches:

**Wallet Clustering Analysis:** The study maps transaction flows between wallets to identify clusters of addresses controlled by single entities. Wallets that frequently trade with each other, share funding sources, or exhibit synchronized trading patterns are grouped into clusters.

**Trading Loop Detection:** The algorithm identifies circular trading patterns where assets move through multiple wallets before returning to the original controller. These loops, while obfuscated through intermediate addresses, leave detectable network signatures on-chain.

**Behavioral Fingerprinting:** Wash trading accounts exhibit distinct behavioral patterns including uniform trade sizing, precise timing intervals between trades, and trading activity concentrated in low-liquidity markets where volume inflation is most impactful.

## Key Findings

### Volume Inflation Timeline

The study analyzed Polymarket trading data from its inception through October 2025. Wash trading volume as a percentage of total volume showed a clear acceleration pattern:

- **Early 2024:** Approximately 10-15% of volume flagged as suspicious, consistent with baseline artificial activity observed on most decentralized platforms.
- **Q3 2024 (pre-election):** Wash trading increased to 20-30% as Polymarket gained mainstream media attention and speculation about a potential POLY token airdrop intensified.
- **December 2024 (post-election peak):** Suspicious volume reached **nearly 60% of weekly trading activity**, the highest concentration observed in the dataset.
- **Q1-Q3 2025:** Wash trading stabilized at 20-25% of total volume as airdrop speculation subsided but activity remained elevated.

### Market Category Distribution

Sports betting markets and political prediction markets were disproportionately targeted. In certain weeks, **over 90% of volume in specific sports markets** originated from flagged wash trading clusters. This pattern suggests wash traders preferentially targeted markets with lower organic liquidity, where their artificial volume constituted a larger share and was more likely to influence airdrop qualification metrics.

Conversely, high-profile markets such as the US Presidential election contract showed lower wash trading percentages (10-15%), likely because organic volume was sufficient to dilute artificial activity and because these markets attracted genuine speculative interest.

### Airdrop Gaming as Primary Motivation

The temporal correlation between wash trading intensity and airdrop speculation provides strong evidence that volume-based airdrop qualification was the primary motivation. This mirrors patterns observed in earlier DeFi protocols where anticipated token distributions incentivized artificial usage metrics:

- Blur NFT marketplace (2023): Wash trading surged ahead of BLUR token airdrops, with users executing self-trades to accumulate loyalty points.
- Multiple Ethereum L2 networks (2023-2024): Sybil farming operations generated artificial transaction counts to qualify for ARB, OP, and ZK token distributions.

The Polymarket case extends this pattern to prediction markets, demonstrating that airdrop-driven wash trading is a systemic issue across decentralized platforms that use volume or usage metrics for token distribution.

## Cross-Platform Comparison

The 25% wash trading rate on Polymarket can be contextualized against documented manipulation rates on centralized exchanges:

| Platform | Wash Trading Rate | Detection Method | Source |
|----------|------------------|------------------|--------|
| Polymarket | ~25% (avg) | Network analysis | Columbia University (2025) |
| Centralized exchanges (aggregate) | 50-75% (pre-2019) | Statistical analysis | Bitwise SEC filing (2019) |
| Huobi | Significant (undisclosed %) | Volume distribution | DN Institute (2023) |
| DEXs on Ethereum/BSC | ~$2.57B total (2024) | Heuristic detection | Chainalysis (2025) |

While Polymarket's 25% average rate is lower than the extreme figures reported for some centralized exchanges, the periodic spikes exceeding 50-60% and the concentrated impact on specific market categories remain concerning for market integrity.

## Implications

The Columbia study raises questions about the reliability of volume-based metrics for decentralized platforms. For prediction markets specifically, inflated volume can distort perceived market depth, affect price discovery accuracy, and mislead researchers who use Polymarket data as a proxy for crowd-sourced probability estimates.

The findings also highlight the need for on-chain market surveillance tools that can operate in real-time, rather than retrospective academic analysis. Several blockchain analytics firms, including Chainalysis and Solidus Labs, have begun developing prediction market monitoring capabilities in response to growing regulatory interest in this sector.

## References

1. "Network-Based Detection of Wash Trading in Decentralized Prediction Markets." Columbia Business School, SSRN Working Paper, November 2025.
2. "Polymarket's Trading Volume May Be 25% Fake, Columbia Study Finds." CoinDesk, November 7, 2025.
3. "Polymarket Volume Inflated by Artificial Activity, Study Finds." Bloomberg, November 7, 2025.
4. "Polymarket Volume Inflated by Artificial Activity, Study Finds." Columbia Business School Press Release, November 2025.
5. "Crypto Market Manipulation: Wash Trading and Pump-and-Dump Patterns." Chainalysis, 2025 Crypto Crime Report.
6. "Presentation to the U.S. Securities and Exchange Commission." Bitwise Asset Management, March 2019.
7. "Uncovering Wash Trading and Market Manipulation on Huobi." DN Institute, August 2023.
