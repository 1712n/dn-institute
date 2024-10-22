---
date: 2021-12-04
target-entities: BitMart
entity-types:
  - Custodian
  - Exchange
attack-types: Wallet Hack
title: "BitMart Exchange Suffers $196 Million Security Breach"
loss: 196000000
---

## Summary

On December 4, 2021, BitMart Exchange, a global cryptocurrency platform operating in 180+ countries, fell victim to a significant security breach. The attacker extracted approximately $196 million worth of various digital assets from the hot wallets of the exchange across two networks: Binance Smart Chain (BSC) - $96 million, and Ethereum - $100 million. The primary targets were meme-based tokens, such as SHIB and SAFEMOON. The attacker converted the stolen tokens into ETH and BNB via 1inch and laundered these assets using TornadoCash.

## Attackers

The identity of the attacker remains unknown. The hacker used the following addresses to transfer the funds:

- Ethereum:
  - [0x39fb0dcd13945b835d47410ae0de7181d3edf270](https://etherscan.io/address/0x39fb0dcd13945b835d47410ae0de7181d3edf270)
  - [0x4bb7d80282f5e0616705d7f832acfc59f89f7091](https://etherscan.io/address/0x4bb7d80282f5e0616705d7f832acfc59f89f7091)
- BSC:
  - [0x25fb126b6c6b5c8ef732b86822fa0f0024e16c61](https://bscscan.com/address/0x25fb126b6c6b5c8ef732b86822fa0f0024e16c61)

## Losses

BitMart Exchange lost around $196 million in total from its hot wallets across Ethereum and Binance Smart Chain:

- [$100 Million on Ethereum](https://twitter.com/peckshield/status/1467302620000043013)
- [$96 Million on BSC](https://twitter.com/peckshield/status/1467310381073047552)

The stolen assets mainly consisted of memecoins like SHIB and SAFEMOON.

## Timeline

- **December 4, 2021, 21:31 UTC:** The attack commenced on the Ethereum network. The attacker started by [withdrawing ~$33M worth of SHIB tokens](https://etherscan.io/tx/0x6afb730976b2cf39e5ea7ce8a56c3597728e4e5923f7abae7086fb53019e81e8)
- **December 4, 2021, 22:00 UTC:** The attacker moved to BSC and [withdrew ~$41M worth of SAFEMOON](https://bscscan.com/tx/0x834321195283c5eafbc8a31b6a6926c9af416ee23bd4d71ab15eb9089a90d86d) tokens
- **December 5, 2021, 03:01 UTC:** The hacker [transferred the stolen funds to TornadoCash](https://etherscan.io/tx/0x93c70a33f8a7f8f9002005aff3dd6515c176912b5c532befe60121800752c61a)

## Security Failure Causes

**Compromised Private Key:** Although the BitMart Exchange has not officially disclosed the cause of their recent security issues, it is highly probable that the private key of the hot wallets was compromised.
