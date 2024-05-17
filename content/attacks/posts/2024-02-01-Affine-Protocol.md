---
date: 2024-02-01
target-entities: Affine Protocol
entity-types:
  - DeFi
  - Lending Platform
attack-types:
  - Smart Contract Exploit
  - Flash Loan Attack
title: "Affine Protocol Exploit: A $88,000 Loss Due to Smart Contract Flaw"
loss: 88000
---

## Summary

Affine Protocol, a provider of cross-chain investment and savings solutions on the Ethereum Mainnet, suffered a significant exploit on February 1, 2024, resulting in a loss of $88,000. The incident was traced to a smart contract vulnerability involving insufficient user data validation. The attacker exploited a flash loan callback function in the strategy contract, manipulating it to liquidate its position and redirect funds. Affine Protocol deployed enhanced security protocols, including stricter access controls and rigorous validation processes for user inputs and transactions, and developed a remediation plan to compensate affected users.

## Attackers

The identity of the attacker is unknown.

Hacker Ethereum wallet:

- [0x09f6be2a7d0d2789f01ddfaf04d4eaa94efc0857](https://etherscan.io/address/0x09f6be2a7d0d2789f01ddfaf04d4eaa94efc0857)

## Losses

Losses amounted to 38.93 ETH worth $88,000

## Timeline

- **February 1, 2024, 10:16 AM UTC:** The [first malicious](https://etherscan.io/tx/0x03543ef96c26d6c79ff6c24219c686ae6d0eb5453b322e54d3b6a5ce456385e5) transaction occurred.
- **February 1, 2024, 01:56 PM UTC:** Affine Protocol sent [on-chain message](https://etherscan.io/tx/0x8b0cf1019933e0f8bd51ad29158c2cc11a21cef2f6771d997b561eb86be70d96) to the hacker offering a bounty of the stolen funds.
- **February 1, 2024, 03:02 PM UTC:** Affine Protocol [reported](https://twitter.com/AffineDeFi/status/1753071451400548845) about the exploit.
- **February 13, 2024:** Affine Protocol [published](https://blog.affinedefi.com/february-24-incident-post-mortem-mitigation-remediation-d50dcbd57fd3) exploit post-mortem and remediation plan.

## Security Failure Causes

- **Smart Contract Vulnerability:** The incident's root cause was the flawed validation processes within Affine's smart contract.
