---
date: 2023-02-02
target-entities:
  - Orion Protocol
entity-types:
  - DeFi
  - Exchange
attack-types:
  - Smart Contract Exploit
  - Reentrancy Attack
title: "Reentrancy Attack on Orion Protocol Leads to $3 Million Loss"
loss: 3000000
---

## Summary

On February 2, 2023, Orion Protocol, a decentralized blockchain platform that aggregates liquidity across both centralized and decentralized exchanges, fell victim to a sophisticated smart contract exploit. The attacker manipulated a reentrancy vulnerability within the protocol’s core smart contracts, which enabled them to divert approximately $3 million in tokens across the Ethereum and Binance Smart Chain networks.

## Attackers

The identity of the attacker is unknown. Two addresses were primarily involved in the attack:

erc20:

- [0x837962b686fd5a407fb4e5f92e8be86a230484bd](https://etherscan.io/address/0x837962b686fd5a407fb4e5f92e8be86a230484bd)
- [0x3dabf5e36df28f6064a7c5638d0c4e01539e35f1](https://etherscan.io/address/0x3dabf5e36df28f6064a7c5638d0c4e01539e35f1)

bep20:

- [0x837962b686fd5a407fb4e5f92e8be86a230484bd](https://bscscan.com/address/0x837962b686fd5a407fb4e5f92e8be86a230484bd)
- [0x3dabf5e36df28f6064a7c5638d0c4e01539e35f1](https://bscscan.com/address/0x3dabf5e36df28f6064a7c5638d0c4e01539e35f1)

Fake Token addresses:

- erc20: [0x64acd987a8603eeaf1ee8e87addd512908599aec](https://etherscan.io/token/0x64acd987a8603eeaf1ee8e87addd512908599aec)
- bep20: [0xc4da120a4acf413f9af623a2b9e0a9878b6a0afe](https://bscscan.com/token/0xc4da120a4acf413f9af623a2b9e0a9878b6a0afe)

## Losses

$3 million

- erc20: [1,651 ETH (~$2,836,206)](https://etherscan.io/tx/0xa6f63fcb6bec8818864d96a5b1bb19e8bd85ee37b2cc916412e720988440b2aa)
- bep20: [$191,434](https://bscscan.com/tx/0xfb153c572e304093023b4f9694ef39135b6ed5b2515453173e81ec02df2e2104)

## Timeline

- **February 2, 2023:** The attackers started by depositing 0.5 USDC into contracts and initiating a flash loan.
- **February 2, 2023:** Using a false token and a series of swaps, the attackers executed the reentrancy exploit to manipulate the contract's balance calculation, ultimately siphoning off approximately $3 million.
- **February 2, 2023:** The attackers proceeded to launder their stolen assets through multiple transactions, including funneling approximately 1100 ETH into Tornado Cash.

[source](https://neptunemutual.com/blog/taking-a-closer-look-at-orion-protocol-hack/)

## Security Failure Causes

- **Reentrancy Vulnerability:** The vulnerability was within the Orion Protocol's smart contracts, particularly in the \_doSwapTokens function. This reentrancy vulnerability led to a miscalculation of the user's USDT balance.
