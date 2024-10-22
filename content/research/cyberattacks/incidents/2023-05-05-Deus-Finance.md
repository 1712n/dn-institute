---
date: 2023-05-05
target-entities: Deus Finance
entity-types:
  - DeFi
  - Lending Platform
attack-types: Smart Contract Exploit
title: "Deus Finance Suffers $6.5 Million Hack Across Multiple Networks"
loss: 6500000
---

## Summary

On May 5, 2023, Deus Finance, a DeFi protocol operating across Ethereum, Arbitrum, and BNB Chain, experienced a severe security breach. A vulnerability in the $DEI token contract allowed attackers to unauthorizedly burn and transfer tokens, culminating in losses estimated at $6.5 million.

## Attackers

The identity of the hackers who attacked Deus Finance is unknown.

Hacker Wallets:

- Ethereum:
  - [0x189cf534de3097c08b6beaf6eb2b9179dab122d1](https://etherscan.io/address/0x189cf534de3097c08b6beaf6eb2b9179dab122d1)
- Binance Smart Chain: 
  - [0x5a647e376d3835b8f941c143af3eb3ddf286c474](https://bscscan.com/address/0x5a647e376d3835b8f941c143af3eb3ddf286c474)
- Arbitrum:
  - [0x189cf534de3097c08b6beaf6eb2b9179dab122d1](https://arbiscan.io/address/0x189cf534de3097c08b6beaf6eb2b9179dab122d1)

## Losses

The total loss from the Deus Finance hack amounted to approximately $6.5 million, distributed across the following networks:

- Arbitrum: [$5 million](https://arbiscan.io/tx/0xb1141785b7b94eb37c39c37f0272744c6e79ca1517529fec3f4af59d4c3c37ef)
- BNB Chain: [$1.3 million](https://bscscan.com/tx/0xde2c8718a9efd8db0eaf9d8141089a22a89bca7d1415d04c05ba107dc1a190c3)
- Ethereum: $135,000

## Timeline

- **May 05, 2023, 05:52 PM UTC:** The [first malicious transaction occurred](https://arbiscan.io/tx/0xb1141785b7b94eb37c39c37f0272744c6e79ca1517529fec3f4af59d4c3c37ef).
- **May 06, 2023, 06:21 PM UTC:** Deus Finance [reported](https://twitter.com/DeusDao/status/1654808611263246336) a hack.
- **May 07, 2023, 09:02 AM UTC:** Deus Finance [confirmed](https://twitter.com/DeusDao/status/1655030202978779137) that a portion of those stolen funds had been successfully returned to the team.
- **May 09, 2023** Immunebytes [published](https://www.immunebytes.com/blog/deus-finance-hack-incident-may-5-2023-detailed-analysis) a detailed analysis of the incident.

## Security Failure Causes

- **Smart Contract Vulnerability:** The significant security breach in Deus Finance originated from a flaw within the token contract, specifically in how token allowances were handled. This error permitted unauthorized burning and transferring of tokens. By exploiting this vulnerability, attackers could gain control over another user's tokens without permission and transfer them to their accounts.
