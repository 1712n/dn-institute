---
date: 2024-01-02
target-entities: Radiant Capital
entity-types:
  - DeFi
  - Lending Platform
attack-types:
  - Smart Contract Exploit
  - Flash Loan
title: "Radiant Capitale Suffers $4.6 Million Loss"
loss: 4600000
---

## Summary

On January 2, 2024, Radiant Capital on the Arbitrum Chain suffered a $4.6 million loss from a sophisticated exploit, involving 1902 ETH, due to a smart contract vulnerability. The attack was orchestrated by utilizing flash loans to inflate the USDC reserve liquidity index on the platform artificially. This enabled the attacker to borrow excessive WETH against the artificially high collateral value. The situation was exacerbated by a rounding error within the contract's calculations, allowing the attacker to manipulate deposit and withdrawal transactions cleverly. By exploiting the inflated collateral and the rounding discrepancy through calculated deposits, withdrawals, and borrowing, the attacker was able to extract substantial funds.

## Attackers

The identity of the attacker is unknown. The following address is associated with this attack:

 - [0x826d5f4d8084980366f975e10db6c4cf1f9dde6d](https://arbiscan.io/address/0x826d5f4d8084980366f975e10db6c4cf1f9dde6d)

## Losses

The loss amounted to 1902 ETH worth $4.6 million.

## Timeline

- **January 2, 2024, 06:53 PM UTC:** The [first malicious](https://arbiscan.io/tx/0x1ce7e9a9e3b6dd3293c9067221ac3260858ce119ecb7ca860eac28b2474c7c9b) transaction occurred.
- **January 3, 2024, 12:14 AM UTC:** Radiant Protocol [reported](https://twitter.com/RDNTCapital/status/1742338729925112272) the exploit and suspended work on Arbitrum.
- **January 5, 2024, 02:50 AM UTC:** Radiant Protocol [announced](https://twitter.com/RDNTCapital/status/1743102629411184841) a reward for assistance in investigating the incident.
- **January 5, 2024, 12:07 AM UTC:** Lending and loan markets on Arbitrum have been [resumed](https://twitter.com/RDNTCapital/status/1743061583692181965).
- **January 12, 2024:** A [detailed analysis](https://blog.quillaudits.com/trending/radiant-capital-hack-analysis) of the exploit has been published.

## Security Failure Causes

- **Smart Contract Vulnerability:** The exploit was enabled by leveraging flash loans for price manipulation and exploiting a rounding error in the smart contract, which allowed the attacker to increase the profit margin.
