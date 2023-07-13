---
date: 2023-02-02
target-entities: 
- BonqDAO
- AllianceBlock
entity-types:
- DeFi
- Lending Platform
- Stablecoin
- Token
attack-types:
- Smart Contract Exploit
- Price Oracle Manipulation
title: "BonqDAO Suffers a $120 Million Loss Through Price Oracle Manipulation"
---

## Summary

In February 2023, BonqDAO, a lending and stablecoin platform hosted on the Polygon network, faced a substantial security breach. A malicious actor exploited a flaw in a smart contract associated with price oracle, causing a loss of around $120 million. The attacker manipulated the value of $WALBT, a Wrapped AllianceBlock Token, and used the inflated value to borrow 100 million $BEUR, a stablecoin pegged to Euro, and liquidate other users' collateral.

## Attackers

The attackers are unidentified.

**Attacker Addresses:**

 Polygon
- [0xcacf2d28b2a5309e099f0c6e8c60ec3ddf656642](https://polygonscan.com/address/0xcacf2d28b2a5309e099f0c6e8c60ec3ddf656642)

 Ethereum
- [0xcacf2d28b2a5309e099f0c6e8c60ec3ddf656642](https://etherscan.io/address/0xcacf2d28b2a5309e099f0c6e8c60ec3ddf656642)
- [0x9210fa17ae138914fa04a161e694d73c9f3502c7](https://etherscan.io/address/0x9210fa17ae138914fa04a161e694d73c9f3502c7)

**Malicious Contracts:**
- [0xed596991ac5f1aa1858da66c67f7cfa76e54b5f1](https://polygonscan.com/address/0xed596991ac5f1aa1858da66c67f7cfa76e54b5f1#code)

## Losses

The hack resulted in approximately $120 million in losses for the BonqDAO. 

## Timeline

- **February 1, 2023, 06:29:18 PM +UTC:** - The attacker [stakes](https://polygonscan.com/tx/0x31957ecc43774d19f54d9968e95c69c882468b46860f921668f2c55fadd51b19) 10 TRB tokens with the TellorFlex
- **February 1, 2023:** - The attacker manipulates the $WALBT token value using the submitValue function.
- **February 1, 2023:** - The attacker uses the inflated token value to borrow 100M BEUR.
- **February 1, 2023:** - The attacker deflates the $WALBT token value and liquidates other users' collateral.

[source](https://rekt.news/bonq-rekt/)

## Security Failure Causes

- **Instant Price Updates:** BonqDAO allowed [instantaneous](https://www.halborn.com/blog/post/explained-the-bonqdao-hack-february-2023) price updates, which left the protocol susceptible to exploitation. In this instance, the attacker was able to manipulate the price oracle to change the value of the $WALBT token.
- **Lack of Oracle Information Sources Diversity and Resilience:** Relying on a single source for price data left BonqDAO vulnerable to this kind of attack. Had the protocol used multiple price sources, the attacker's manipulation would have been much less likely to succeed.
