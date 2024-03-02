---
date: 2024-01-22
target-entities: Concentric Finance
entity-types:
  - DeFi
  - Yield Aggregator
attack-types:
  - Wallet Hack
  - Phishing
title: "Concentric Finance Suffers $1.72 Million Loss in Exploit"
loss: 1720000
---

## Summary

Concentric Finance fell victim to a critical security breach on January 22, 2024, suffering a significant loss of 715.7 ETH, valued at approximately $1.72 million. This exploit was orchestrated through a social engineering attack where an impersonator gained the trust of a team member, leading to the installation of malware that compromised critical operational credentials. With control over the deployer wallet, the attacker manipulated the protocol by deploying a malicious contract version. This manipulation enabled the unauthorized creation and withdrawal of assets, draining funds from the platform.

## Attackers

The identity of the attacker is unknown.

Hacker Arbitrum Wallet:

- [0x105f52fcc329cef4cbe25bc946f8a3738414e4a1](https://arbiscan.io/address/0x105f52fcc329cef4cbe25bc946f8a3738414e4a1)

## Losses

Losses amounted to 715 ETH worth $1.72 million.

## Timeline

- **January 22, 2024, 07:51:24 AM +UTC:** The [first malicious](https://arbiscan.io/tx/0xd9036566a2614045219e9bead34e490fc24c9d6ca695d5348b694c3280558e3b) transaction occurred.
- **January 22, 2024, 02:48 PM +UTC:** Concentric Finance [reported](https://twitter.com/ConcentricFi/status/1749398619071938682) about the exploit.
- **January 22, 2024:** Concentric Finance [published](https://mirror.xyz/concentrictreasury.eth/duXXwBErblGw4CjbsA2JPoRAJqVNsDtiUsK4R6_vhD0) an exploit Post-Mortem.

## Security Failure Causes

- **Social Engineering Attack:** The breach was initiated through a sophisticated social engineering attack.
- **Flawed Contract Upgrade Mechanism:** The ability to upgrade contracts without sufficient security checks enabled the attacker to insert malicious functions, facilitating the theft.
