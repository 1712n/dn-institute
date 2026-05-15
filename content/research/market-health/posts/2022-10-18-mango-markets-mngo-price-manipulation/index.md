---
title: "Mango Markets — Oracle Price Manipulation and Cross-Margin Drain"
date: "2022-10-18"
description: "On October 11, 2022, Mango Markets was exploited for approximately $116M through a coordinated oracle price manipulation attack. The attacker inflated the MNGO perpetual futures mark price via large spot purchases on Serum, then used the unrealized profit as collateral to borrow and withdraw almost the entire protocol's available liquidity."
entities:
  - Mango Markets
  - MNGO
  - Serum
  - Solana
  - Pyth Network
  - Avraham Eisenberg
---

## Incident Overview

On October 11, 2022, an attacker conducted a sophisticated oracle manipulation attack against Mango Markets, a Solana-based decentralized exchange offering spot, perpetual futures, and lending markets. The exploit extracted approximately $116 million, at the time the largest DeFi exploit on Solana.

## Attack Mechanics

The attack unfolded in two coordinated phases:

### Phase 1: Oracle Price Manipulation

The attacker deposited approximately $5 million USDC into Mango Markets and simultaneously executed large MNGO purchases on the Serum DEX. This inflated the MNGO market price from approximately $0.038 to over $0.50 on the Serum order book within minutes. The price surge was picked up by the Pyth Network oracle and fed into Mango Markets' pricing of its MNGO-PERP perpetual futures market.

### Phase 2: Collateral Extraction

With the inflated MNGO-PERP position now showing approximately $50 million in unrealized profit, the attacker used this as collateral to borrow and withdraw all available tokens from Mango Markets. Total extracted: approximately $116 million including USDC ($47M), SOL (112k), mSOL (55k), and other tokens.

## Market Impact

Mango Markets' MNGO token fell roughly 50% in the days following the attack. Solana ecosystem TVL dropped significantly, with Mango Markets' TVL falling from ~$200M pre-exploit to near zero.

## Post-Incident Resolution

The attacker (later identified as Avraham Eisenberg) engaged in on-chain negotiations with Mango Markets governance and agreed to return $67 million in exchange for keeping approximately $47 million as a bug bounty. Eisenberg was later arrested by U.S. authorities in December 2022 and convicted for market manipulation in April 2023.

## References

- Mango Markets Post-Mortem
- Pyth Network Response
- Chainalysis Report on Mango Markets
- DOJ Indictment of Avraham Eisenberg