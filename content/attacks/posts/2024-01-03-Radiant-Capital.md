---
date: 2024-01-03
target-entities: Radiant Capital
entity-types:
  - DeFi
  - Lending Platform
attack-types:
  - Smart Contract Exploit
  - Flash Loan Attack
title: "Radiant Capitale Suffers $4.6 Million Loss in Exploit"
loss: 4600000
---

## Summary

On January 3, 2024, Radiant Capital on the Arbitrum Chain faced a $4.5 million exploit due to a smart contract vulnerability, losing 1902 ETH. The attacker manipulated the platform using flash loans and a rounding error, artificially inflating the USDC reserve liquidity index to borrow excessively and exploit transactional discrepancies for financial gain.

## Attackers

The identity of the attacker is unknown. The following addresses are associated with this attack:

Hacker Wallet:
 - [0x826d5f4d8084980366f975e10db6c4cf1f9dde6d](https://arbiscan.io/address/0x826d5f4d8084980366f975e10db6c4cf1f9dde6d)

## Losses

The loss amounted to 1902 ETH worth $4.6 million.

## Timeline

- **January 2 2024, 06:53:38 PM +UTC:** The [first malicious](https://arbiscan.io/tx/0x1ce7e9a9e3b6dd3293c9067221ac3260858ce119ecb7ca860eac28b2474c7c9b) transaction occurred.
- **January 3 2024, 03:14 AM +UTC:** Radiant Protocol [reported](https://twitter.com/RDNTCapital/status/1742338729925112272) the exploit and suspended work on Arbitrum.
- **January 5 2024, 05:50 AM +UTC:** Radiant Protocol [announced](https://twitter.com/RDNTCapital/status/1743102629411184841) a reward for assistance in investigating the incident.
- **January 5 2024, 03:07 AM +UTC:** Lending and loan markets on Arbitrum have been [resumed](https://twitter.com/RDNTCapital/status/1743061583692181965).
- **January 12 2024:** A [detailed analysis](https://blog.quillaudits.com/trending/radiant-capital-hack-analysis) of the exploit has been published.

## Security Failure Causes

- **Smart Contract Vulnerability:** The Radiant Capital hack was executed through sophisticated flash loan attacks combined with a rounding error exploitation in the platform's smart contracts. The attacker initiated the process by taking flash loans to artificially inflate the USDC reserve liquidity index on Radiant, which allowed them to borrow an excessive amount of WETH against this artificially high collateral value. This was further compounded by exploiting a rounding error within the contract's calculations, enabling the attacker to manipulate deposit and withdrawal transactions. Through a series of calculated deposits, withdrawals, and borrowing, leveraging the inflated collateral and the rounding discrepancy, the attacker siphoned off substantial funds.
