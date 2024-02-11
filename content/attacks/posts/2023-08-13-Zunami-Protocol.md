---
date: 2023-08-13 
target-entities: Zunami Protocol 
entity-types: 
   - DeFi
   - Yield Aggregator
   - Stablecoin
attack-types:
   - Flash Loan Attack
   - Smart Contract Exploit
title: "Zunami Protocol lost $2.16 million in a flash loan attack."
loss: 2160000
---

## Summary

On August 13, 2023, Zunami Protocol, a prominent DeFi platform on Ethereum, was compromised through a sophisticated flash loan attack, resulting in a significant loss of 1,178 ETH, approximately valued at $2.16 million. Central to this exploit was a vulnerability within the platform's contract that allowed for the manipulation of the UZD token's balance. By leveraging a flash loan the attacker was able to artificially inflate the value of the UZD token. This manipulation enabled the withdrawal of an extensive sum of assets.

## Attackers

The identity of the hackers who attacked Zunami is unknown.

Hacker Ethereum Wallet:

- [0x5f4c21c9bb73c8b4a296cc256c0cde324db146df](https://etherscan.io/address/0x5f4c21c9bb73c8b4a296cc256c0cde324db146df)

## Losses

Zunami estimated the losses from the hack to be 1178 ETH( $2.16 million). 

## Timeline

- **August 13, 2023, 10:26:35 PM UTC:** The [first malicious transaction occurred](https://etherscan.io/tx/0x2aec4fdb2a09ad4269a410f2c770737626fb62c54e0fa8ac25e8582d4b690cca) and 26 ETH were stolen.
- **August 13, 2023, 11:12:59 PM UTC:** The stolen assets were moved through various transactions and eventually [sent](https://etherscan.io/advanced-filter?fadd=0x5f4c21c9bb73c8b4a296cc256c0cde324db146df&tadd=0xd90e2f925da726b50c4ed8d0fb90ad053324f31b&txntype=0&qt=1) to Tornado Cash.
- **August 14, 2023, 06:10 AM UTC:** Zunami protocol [announced](https://twitter.com/ZunamiProtocol/status/1690863406079696896) a hack.
- **August 16, 2023, 02:01 AM UTC:** Zunami published [exploit Post-Mortem](https://twitter.com/ZunamiProtocol/status/1691527489716146177).
- **August 18, 2023:** Immunebytes [published](https://www.immunebytes.com/blog/zunami-protocol-hack-aug-13-2023-detailed-analysis-report/) a detailed analysis of the incident.

## Security Failure Causes

- **Smart contract vulnerability:** The Zunami Protocol hack stemmed from a vulnerability that allowed an attacker to artificially inflate asset values within the protocol. By manipulating market prices through flash loans, the attacker increased their balance of the protocol's stable token, UZD, and exploited this inflated balance to withdraw funds significantly exceeding their initial deposit.
