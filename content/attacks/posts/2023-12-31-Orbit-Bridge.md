---
date: 2023-12-31
target-entities: Orbit Bridge
tags:
  - Lazarus Group
  - North Korea
entity-types:
  - DeFi
  - Bridge
attack-types: Wallet Hack
title: "Orbit Bridge Suffers $81.54 Million Security Breach"
loss: 81540000
---

## Summary

On December 31, 2023, Orbit Chain, a South Korean cross-chain project, [experienced a significant security breach involving their Orbit Bridge](https://cointelegraph.com/news/cross-chain-protocol-orbit-bridge-suffers-exploit-hack). The attacker exploited the Orbit Bridge through a private key compromise and drained approximately $81.54 million worth of assets from the Orbit Bridge's ETH Vault. The stolen funds were converted into ETH and DAI and then distributed across several addresses. 

## Attackers

The identity of the attacker remains unknown. However, some experts have [linked the incident to the Lazarus Group](https://bnnbreaking.com/finance-nav/cryptocurrency/orbit-attack-linked-to-notorious-lazarus-group-coindesk-upholds-independence-post-bullish-group-acquisition/), a North Korean hacking syndicate. The following Ethereum addresses was used to carry out the attack:
	- [0x9263e7873613ddc598a701709875634819176aff](https://etherscan.io/address/0x9263e7873613ddc598a701709875634819176aff)
	- [0x70462bfb204bf3ccb0560f259072f8e3a85b3512](https://etherscan.io/address/0x70462bfb204bf3ccb0560f259072f8e3a85b3512)

## Losses

Orbit Bridge lost approximately $81.54 million in total:
- 30,000,000 USDT
- 9,530 ETH
- 10,000,000 DAI
- 10,000,000 USDC
- 230.879 WBTC

## Timeline

- **December 31, 2023, 04:59 PM UTC:** The attack commenced on the Ethereum network. The attacker [received 9.93 ETH from TornadoCash](https://etherscan.io/tx/0xc84f7a560d070f62fe81e2923607d06365c8b6b250afc21800e9c96b7098e135), that was used to perform malicious actions.
- **December 31, 2023, 08:52 PM UTC:** The [first malicious transaction was executed](https://etherscan.io/tx/0x958aeec58ea2f0f9700adda24e43fb76f9e052e4c20773f180c49d7529d95f16) with 30 ETH being transferred.
- **December 31, 2023, 09:43 PM UTC:** Twitter user Kgjr [shared suspicions about the bridge being drained](https://twitter.com/KGJRTG/status/1741575860635783385).
- **January 1, 2024, 02:25 AM UTC:** Developer at MetaMask and blockchain expert, Taylor Monahan, [suggested the attack linked to DPRK](https://twitter.com/tayvano_/status/1741646766779552061).
- **January 1, 2024, 07:39 AM UTC:** [Orbit Chain confirmed the hack](https://twitter.com/Orbit_Chain/status/1741725778956730778) on their Twitter.
- **January 4, 2024, 08:11 AM UTC:** The Orbit Chain team [sent on-chain message to the exploiter](https://etherscan.io/tx/0xeeb2b28b3a20a0b81b6094bcd0b220fb6e696d76b070c78dbabe8f539bde0f6c), calling to discussion:
	> ... we have found a trail you left behind when making XRP transactions at an Exchange 'C'. Rest assured, we will find more.

## Security Failure Causes

**Private Key Compromise:** The attacker managed to compromise the private keys of the Orbit Bridge, leading to the security breach. Independent crypto researcher @officer_cia [suggests that the root cause is the wallet compromise of 7 out of 10 multisig signers](https://twitter.com/officer_cia/status/1741599292761018480).