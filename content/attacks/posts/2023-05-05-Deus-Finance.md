---
date: 2023-05-05
target-entities: Deus Finance
entity-types:
  - DeFi
  - Lending Platform
attack-types:
  - Smart Contract Exploit
title: "Deus Finance Suffers $6.5 Million Hack Across Multiple Networks"
loss: 6500000
---

## Summary

On May 5, 2023, Deus Finance, a DeFi protocol operating across Ethereum, Arbitrum, and BNB Chain, experienced a severe security breach. An implementation flaw in the $DEI token contract led to unauthorized token burning and transfers, culminating in losses estimated at $6.5 million.

## Attackers

The identity of the hackers who attacked Deus Finance is unknown.

Hacker ETH Wallet:

- [0x189cf534de3097c08b6beaf6eb2b9179dab122d1](https://etherscan.io/address/0x189cf534de3097c08b6beaf6eb2b9179dab122d1)

## Losses

Deus Finance estimated the losses from the hack to be $6.5 million.

## Timeline

- **May 05, 2023, 05:52:45 PM UTC:** The [first malicious transaction occurred](https://arbiscan.io/tx/0xb1141785b7b94eb37c39c37f0272744c6e79ca1517529fec3f4af59d4c3c37ef).
- **May 06, 2023, 06:21 PM UTC:** Deus Finance [reported](https://twitter.com/DeusDao/status/1654808611263246336) a hack.
- **May 06, 2023, 06:21 PM UTC:** Immunebytes [published](https://www.immunebytes.com/blog/deus-finance-hack-incident-may-5-2023-detailed-analysis) a detailed analysis of the incident.
- **May 07, 2023, 09:202 AM UTC:** Deus Finance [confirmed](https://twitter.com/DeusDao/status/1655030202978779137) that a portion of those stolen funds had been successfully returned to the team.

## Security Failure Causes

**Smart contract vulnerability:** The Deus Finance hack occurred due to a critical implementation error in the $DEI token contract, specifically within the burnFrom function. This function had a flaw where the order of allowances was incorrectly implemented, allowing an attacker to manipulate the contract to burn tokens from any holder's account without their approval. Essentially, the attacker was able to exploit this error to unauthorizedly transfer tokens from victims' addresses to their address
