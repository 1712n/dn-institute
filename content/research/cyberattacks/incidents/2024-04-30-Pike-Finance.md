---
date: 2024-04-30
target-entities: Pike Finance
entity-types:
  - DeFi
  - Lending Protocol
  - Bridge
attack-types:
  - Smart Contract Exploit
title: "Pike Finance exploited for $1.7 million in second incident"
loss: 1700000
---

## Summary

On April 30, 2024, Pike Finance, a Cross-chain Bridge and a Lending Protocol for native assets, [was exploited across the Ethereum, Optimism, and Arbitrum chains](https://cointelegraph.com/news/pike-finance-exploited-1-6-million-second-exploit-3-days) due to a smart contract vulnerability. $1.7 million worth of assets was siphoned out from the protocol. The smart contract storage misalignment issue was utilized, whith allowed the attacker to bypass owner permissions. Initially, the protocol [was exploited four days before the incident](https://x.com/PikeFinance/status/1783989069212799321), which led to a loss of nearly $300,000 and a temporary pause of operations. To resolve previous security issue, the protocol's team upgraded the smart contract's code, which created a new vulnerability related to smart contract's storage. It is worth mentioning that there is no evidence that two attacks were performed by the same actor. Asset transfer methods are also differs - the first attacker used TornadoCash, while the second used Railgun.

## Attackers

The identity of the attacker remains unknown. The attacker utilized the same address across three chains:

- *0x19066f7431df29a0910d287c8822936bb7d89e23*
	- [Ethereum](https://etherscan.io/address/0x19066f7431df29a0910d287c8822936bb7d89e23)
	- [Optimism](https://optimistic.etherscan.io/address/0x19066f7431df29a0910d287c8822936bb7d89e23)
	- [Arbitrum](https://arbiscan.io/address/0x19066f7431df29a0910d287c8822936bb7d89e23)

## Losses

Pike Finance suffered a loss of approximately $1.7 million in native assets. Lost assets breakdown:
- *479.39 ETH* worth *1,443,443 USD*
- *64,126.66 OP* worth *164,782 USD*
- *99,970.48 ARB* worth *99,463 USD*

## Timeline

- **April 25, 2024, 11:48 PM UTC:** The [first attack begun](https://arbiscan.io/tx/0x979ad9b7f5331ea8034305a83b5cd50aea88adec395fff8298dd90eb1b87667f) on the Arbitrum chain.
- **April 26, 2024, 10:37 AM UTC:** The initial attacker [finished funds withdrawal using TornadoCash](https://etherscan.io/tx/0x8c0340b11e9c2566a8634bf311c889d696940e850331fb525e56f0bbf121445e).
- **April 28, 2024:** Pike Finance team [posted an incident post-mortem](https://mirror.xyz/pikefinance.eth/M1ToE42vwEHuE6xlz0dVRQwPT0xpaRtpIIw2arOdBAM).
- **April 30, 2024, 09:45 PM UTC:** The [second attack started](https://optimistic.etherscan.io/tx/0x6baa6332f9a3ed75e727311d6317fb636844d61d9df5e199f9f68711eb632d6f) on the Optimism chain. 
- **April 30, 2024, 10:19 PM UTC:** A [malicious transaction occurred](https://etherscan.io/tx/0xe2912b8bf34d561983f2ae95f34e33ecc7792a2905a3e317fcc98052bce66431) on the Ethereum chain with over $1.4 million worth of ETH.
- **April 30, 2024, 10:23 PM UTC:** The [attacker transferred the stolen funds via Railgun](https://etherscan.io/tx/0xf8ce549fe83ecaf0d889ef5bda0b613081cefdad5bd82237e3a9014584a95d11).
- **May 2, 2024:** The Pike Finance team [posted a detailed post-mortem](https://mirror.xyz/pikefinance.eth/klLV4rRqNYxjRQp0NAfVLboLYtX98P9iYOOf06FUapg) regarding the second attack.

## Security Failure Causes

**Smart Contract Vulnerability:** The root cause of the exploit was a smart contract storage misalignment. In particular, the storage position of `initialized` variable was set to false after the protocol's team upgraded smart contracts. This issue allowed attacker to reinitialize contracts by making himself a new admin and subsequently withdraw funds using privileged functions.
