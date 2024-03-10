---
date: 2023-12-21
target-entities: Pine Protocol
entity-types:
  - DeFi
  - Lending Platform
attack-types:
   - Smart Contract Exploit
   - Flash Loan Attack
title: "Pine Protocol Suffers $92,000 Security Breach"
loss: 92000
---

## Summary

Pine Protocol, a decentralized, non-custodial asset-backed lending platform, suffered a security breach on December 21, 2023, due to a vulnerability in its smart contract on the Ethereum Mainnet. This exploit resulted in a loss of approximately 40 ETH ($92,000), exploiting the protocol across multiple transactions. The attack was facilitated by a flaw related to shared pools between two different contracts within the platform.

## Attackers

The identity of the attacker is unknown.

Hacker Ethereum Wallet:
- [0x05324c970713450bA0Bc12EfD840034FCB0A4BAa](https://etherscan.io/address/0x05324c970713450bA0Bc12EfD840034FCB0A4BAa)

## Losses

The loss amounted to 40 ETH worth $92,000.

## Timeline

- **December 21, 2023, 04:10:47 PM UTC:** The [first malicious](https://etherscan.io/tx/0x88db033171344c7b89d50f48e1e50ef3a622371cf3ab997613469904838c83ad) transaction occurred.
- **December 21, 2023, 07:07:23 PM UTC:** The hacker sent an [on-chain message](https://etherscan.io/tx/0xa079826b4af4e5889a162684304f9921eec2e773bee3bdc8bacb4a9fa092ee61) stating their intention to keep half of the stolen funds as a bounty.
- **December 21, 2023, 07:27:23 PM UTC:** The Pine Protocol team [thanked the hacker for his willingness to return the funds](https://etherscan.io/tx/0xb3ec9ecfc67ac8bc043e1283fde475c4240fe7ca2f4b5e3596fe44ceead21839), inviting further discussion to understand the exploit better.
- **December 21, 2023, 09:18:47 PM UTC:** The Attacker [withdrew](https://etherscan.io/tx/0x168aa3823c27e2ef1b07a123dddd2f5b97b1f6c37eecc2e0def37113d8a7d32e) 20 ETH to Tornado Cash.

## Security Failure Causes

- **Smart Contract Vulnerability:** The vulnerability stemmed from shared pools between two versions of contracts within Pine Protocol. This issue arose from the most recent update to the protocol, where both old and new contract versions shared the same pool address, allowing the exploiter to manipulate fund transfers across different pools. The attacker exploited this by borrowing assets using NFT tokens as collateral and then using a flash loan from the old pool version to repay the initially borrowed assets. 
