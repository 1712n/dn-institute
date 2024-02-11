---
date: 2023-08-18
target-entities: Exactly Protocol
entity-types: DeFi
attack-types: Smart Contract Exploit
title: "Exactly Protocol Bridge Suffers $7.6 Million Security Breach"
loss: 7612038
---

## Summary

Exactly Protocol on Optimism faced a critical security breach on August 18, resulting in a loss of around $7.6 million. The attackers exploited a vulnerability by manipulating market address inputs, allowing them to bypass key security checks within the protocol. This manipulation granted them unauthorized access to execute a deposit function maliciously, leading to the theft of a substantial amount of USDC from users.

## Attackers

The identity of the hackers who attacked Multichain is unknown.

Hacker Optimism Wallets:

- [0x3747dbbcb5c07786a4c59883e473a2e38f571af9](https://optimistic.etherscan.io/address/0x3747dbbcb5c07786a4c59883e473a2e38f571af9)
- [0xe4f34a72d7c18b6f666d6ca53fbc3790bc9da042](https://optimistic.etherscan.io/address/0xe4f34a72d7c18b6f666d6ca53fbc3790bc9da042)
- [0x417179df13ba3ed138b0a58eaa0c3813430a20e0](https://optimistic.etherscan.io/address/0x417179df13ba3ed138b0a58eaa0c3813430a20e0)

## Losses

Exactly Protocol estimated the losses from the hack to be [$7.6 million](https://docs.google.com/spreadsheets/d/1kZCGUnwhN6rXHZjPZrzayzZPHUmm1L_hypvpRGcqdO0/edit#gid=1635590080). Stollen assets included:

- 5,037,975 USDC
- 1,535 ETH (2,535,820 USD)
- 13,912 OP (21980 USD)
- 8.45 wstETH (16,139 USD)

## Timeline

- **August 18, 2023, 09:11:33 AM +UTC:** The [first malicious transaction occurred](https://optimistic.etherscan.io/tx/0x3d6367de5c191204b44b8a5cf975f257472087a9aadc59b5d744ffdef33a520e).
- **August 18, 2023, 07:10 PM +UTC:** Exactly Protocol [reported](https://twitter.com/ExactlyProtocol/status/1692509323690184966) a security breach and suspended operations.
- **August 18, 2023, 08:33:59 PM +UTC:** Exactly Protocol team [communicated with the hacker](https://etherscan.io/tx/0x91dd9c55e1d51f7ada448b2aec4552d9bbf5aa02b33f796d29509e4e0b2fe3d1), proposing a deal to recover the stolen assets in exchange for a 10% reward, alongside a promise of no legal action.
- **August 20, 2023, 11:50 PM +UTC:** Exactly Protocol [announced](https://twitter.com/ExactlyProtocol/status/1693304412356108736) the resumption of work.
- **August 30, 2023:** Exactly Protocol [published](https://medium.com/@exactly_protocol/exactly-protocol-incident-post-mortem-b4293d97e3ed) exploit Post-Mortem.

## Security Failure Causes

- **Smart Contract Vulnerability:** The attack was facilitated by exploiting a smart contract vulnerability that allowed for the manipulation of market address inputs, effectively bypassing the protocol's critical security checks.
