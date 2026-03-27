---
title: "Wash Trading on Polymarket: Columbia University Study Finds 25% of Volume is Artificial"
date: "2024-12 — 2025-10"
description: "A Columbia University study identified approximately $4.5 billion in suspicious trading volume on Polymarket, with wash trading prevalence reaching 60% of weekly volume in December 2024."
entities:
  - Polymarket
---

## Summary

A Columbia University research study found that approximately 25% of all trading volume on Polymarket, the largest decentralized prediction market, may constitute wash trading. The study identified suspicious activity across 14% of Polymarket's 1.26 million active wallets, with an estimated $4.5 billion in artificial volume. The prevalence of wash trading varied significantly by market category, with Sports markets showing the highest rates at 45% of all-time volume and peaking at 90% during the week of October 21, 2024.

## Detection Methodology

Researchers employed algorithmic clustering to identify groups of wallets that trade predominantly with each other rather than with the broader market. This network-based approach detects wash traders who form approximately closed clusters of colluding counterparties, a pattern inconsistent with genuine market participation where traders interact with a diverse set of counterparties.

The study analyzed Polymarket's full transaction history across all market categories, examining wallet behavior patterns including trade frequency, counterparty diversity, and profit/loss profiles. Some flagged accounts conducted tens of thousands of back-and-forth transactions with minimal profit or loss, consistent with volume generation rather than speculative trading.

## Market-Specific Findings

Wash trading prevalence varied substantially across Polymarket's market categories:

| Market Category | Estimated Wash Trading (% of All-Time Volume) |
|---|---|
| Sports | 45% |
| Election | 17% |
| Politics | 12% |
| Crypto | 3% |

The Election markets showed extreme temporal variation. During the week of March 24, 2025, an estimated 95% of Election market volume was classified as likely wash trading. This spike suggests coordinated volume inflation during periods of high public attention to political prediction markets.

## Temporal Patterns

The share of suspected artificial volume showed significant fluctuation over time:

- **December 2024**: Suspicious trades peaked at nearly 60% of total weekly volume
- **May 2025**: Dropped below 5%, suggesting temporary cessation of wash trading activity
- **October 2025**: Surged to approximately 20%, indicating renewed artificial volume generation

These patterns suggest that wash trading activity is not constant but responds to external incentives and market conditions.

## Enabling Factors

The researchers identified three structural features of Polymarket that facilitate wash trading:

1. **No KYC verification**: Users can create multiple wallets without identity verification, enabling a single entity to control clusters of accounts that trade with each other.

2. **Zero transaction fees**: The absence of trading fees removes the natural economic deterrent against self-trading. On traditional exchanges, transaction fees make wash trading costly. On Polymarket, the only cost is gas fees on the Polygon network, which are negligible.

3. **Anticipated token launch**: Market speculation about a Polymarket token airdrop created a direct financial incentive for volume generation. Users anticipated that trading activity would be rewarded with token allocations, making artificial volume generation potentially profitable even without market-making returns.

## Implications for Market Integrity

The findings raise questions about the reliability of Polymarket's reported trading volumes and the accuracy of prediction market probabilities that are often cited in media coverage of elections and other events. If a substantial portion of volume represents wash trading rather than genuine speculative activity, the "wisdom of crowds" signal that prediction markets claim to provide may be diluted.

Polymarket did not respond to the researchers' requests for comment.
