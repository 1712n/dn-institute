---
date: 2023-06-06
target-entities: Multichain
entity-types:
  - DeFi
  - Bridge
attack-types:
  - Private Key Compromise
title: "Multichain Bridge Suffers $126 Million Security Breach"
loss: 126000000
---

## Summary

On July 6, 2023, Multichain Bridge [experienced a security breach](https://twitter.com/MultichainOrg/status/1677096839731097600) due to a private key compromise. The total losses amounted to approximately $126 million, including wBTC, wETH, USDT, USDC, and other assets. The stolen assets were transferred to several addresses.

## Attackers

The identity of the hackers who attacked Multichain is unknown.

Hacker ETH Wallets:

- [0x9d5765ae1c95c21d4cc3b1d5bba71bad3b012b68](https://etherscan.io/address/0x9d5765ae1c95c21d4cc3b1d5bba71bad3b012b68)
- [0xefeef8e968a0db92781ac7b3b7c821909ef10c88](https://etherscan.io/address/0xefeef8e968a0db92781ac7b3b7c821909ef10c88)
- [0x418ed2554c010a0c63024d1da3a93b4dc26e5bb7](https://etherscan.io/address/0x418ed2554c010a0c63024d1da3a93b4dc26e5bb7)
- [0x622e5f32e9ed5318d3a05ee2932fd3e118347ba0](https://etherscan.io/address/0x622e5f32e9ed5318d3a05ee2932fd3e118347ba0)
- [0x48bead89e696ee93b04913cb0006f35adb844537](https://etherscan.io/address/0x48bead89e696ee93b04913cb0006f35adb844537)
- [0x027f1571aca57354223276722dc7b572a5b05cd8](https://etherscan.io/address/0x027f1571aca57354223276722dc7b572a5b05cd8)

## Losses

Multichain estimated the losses from the hack to be $126 million. The stolen assets included:

- 62,622,559 USDC
- 1029 wBTC (30,925,467 USD)
- 7,214 wETH (13,392,646 USD)
- 2,535,016 USDT
- 491,657 LINK (2,999,107 USD)
- 1,002,362 CRV (1,002,362 USD)
- 4,957,670 DAI
- 1,296,991 ICE (1,841,727 USD)
- 910,654 UNIDX (3,251,034 USD)
- 9,674,426 WOO (2,099,601 USD)
- 134 YFI (905,983 USD)

## Timeline

- **May 21, 2023** [Multichain CEO Zhaojun was taken away by the Chinese police from his home](https://twitter.com/MultichainOrg/status/1679768407628185600). Zhaojun's computers, phones, hardware wallets, and mnemonic phrases were confiscated by the authorities.
- **July 06, 2023, 04:21:23 PM UTC:** The [first malicious transaction occurred](https://etherscan.io/tx/0xde3eed5656263b85d43a89f1d2f6af8fde0d93e49f4642053164d773507323f8).
- **July 06, 2023, 06:33:11 PM UTC:** 30 million WBTC [withdrawn](https://etherscan.io/tx/0x448f2a6a6c071cdce254937e06305a033538e1aeb9339227d0e59e0458e6185c) from Multichain bridge.
- **July 06, 2023, 07:46:23 PM UTC:** Multichain Moonriver bridge [begins](https://etherscan.io/tx/0xf830239f39ff21b8634e28cf3fea730069982478465ee5c3ba8e8706d0cef50f) being drained.
- **July 06, 2023, 08:05:35 PM UTC:** Multichain Dogechain bridge [begins](https://etherscan.io/tx/0x6bbc867004b4c6650f2b55131955075c4109c32138753147eb142fa431cc84c9) being drained.
- **July 07, 2023, 06:27 AM UTC:** Multichain [reported](https://twitter.com/MultichainOrg/status/1677096839731097600) that the funds were transferred to an unknown address.
- **July 07, 2023, 11:57 AM UTC:** Multichain has [stopped](https://twitter.com/MultichainOrg/status/1677180114227056641) working.

## Security Failure Causes

**Compromised Private Key:** The primary cause of the security breach was the compromise of the private key. The attacker exploited this vulnerability to withdraw funds.

**Insider threat:** [There is an opinion that this was an inside job.](https://www.chainalysis.com/blog/multichain-exploit-july-2023)
