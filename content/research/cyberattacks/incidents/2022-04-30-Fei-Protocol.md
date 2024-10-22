---
date: 2022-04-30
target-entities:
  - Fei Protocol
  - Rari Capital
entity-types:
  - DeFi
  - Stablecoin
  - Lending Platform
attack-types:
  - Smart Contract Exploit
  - Reentrancy Attack
title: "Fei Protocol Hack: $80 Million Stolen in Reentrancy Attack"
loss: 80000000
---

## Summary

On April 30, 2022, Fei Protocol, a decentralized finance (DeFi) protocol that [merged](https://thedefiant.io/rari-capital-fei-merger) with [Rari Capital](https://www.rari.capital/) in 2021, was hacked for $80 million. The attacker exploited a reentrancy vulnerability in the protocol's smart contracts to withdraw funds from the protocol's reserves.

## Attackers

The identity of the attacker(s) is unknown.

ERC-20

- FeiProtocol-Fuse Exploiter: [0x6162759eDAd730152F0dF8115c698a42E666157F](https://etherscan.io/address/0x6162759edad730152f0df8115c698a42e666157f)

## Losses

$80 Million

## Timeline

- **April 30, 2022, 09:01:35 AM +UTC:** [The hacker exploited a reentrancy vulnerability in lending protocol](https://etherscan.io/tx/0xadbe5cf9269a001d50990d0c29075b402bcc3a0b0f3258821881621b787b35c6)
- **April 30, 2022, 10:23:58 AM +UTC:** [Funds have started to be laundered through Tornado Cash.](https://etherscan.com/tx/0x61ee3d6fdf29f84c36ad828608af38b516869631f494326ed10f82ef36ddf3f9)

## Security Failure Causes

- **Reentrancy Vulnerability:** The attacker [exploited two functions within the contracts of Fei Protocol](https://www.halborn.com/blog/post/explained-the-fei-protocol-hack-april-2022): exitMarket and borrow. The exitMarket function is responsible for ensuring that a deposit is not being utilized as collateral for any loan, after which it permits the withdrawal of the deposit. Meanwhile, the borrow function permits a user to secure a loan by using a deposited asset as collateral. However, this function does not adhere to the check-effects-interaction pattern, rendering it susceptible to exploitation.
