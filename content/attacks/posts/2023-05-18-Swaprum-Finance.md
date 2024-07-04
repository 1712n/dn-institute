---
date: 2023-05-18
target-entities: Swaprum Finance
entity-types:
  - DeFi
  - Exchange
attack-types:
  - Scam
  - Rug Pull
title: "The Collapse of Swaprum Finance: A $3 Million Exit Scam on Arbitrum Chain"
loss: 3000000
---

## Summary

On May 18, 2023, Swaprum Finance, a DeFi platform on the Arbitrum chain, conducted an exit scam, absconding with around $3 million in user funds. The deployer executed a malicious upgrade to the reward contract, introducing a backdoor function that allowed for the unauthorized transfer of LP tokens directly to the deployer’s address. This upgrade facilitated the siphoning of liquidity from various pools by stealing LP tokens staked by users. Additionally, the deployer exploited the newly inserted backdoor to mint 200,000,000 SAPR tokens directly into their wallet, further draining the liquidity from the SAPR/WETH Pool. These illicitly acquired assets were then converted into 1620 ETH, which were subsequently laundered through Tornado Cash. Following these actions, the platform's online presence was entirely erased.

## Attackers

The anonymous Swaprum Finance team was behind the attack. The following addresses are associated with this attack:

- [0xaaf8b44376f4ef3ed477eeeb3553b7623fef5e1c](https://arbiscan.io/address/0xaaf8b44376f4ef3ed477eeeb3553b7623fef5e1c)
- [0xf2744e1fe488748e6a550677670265f664d96627](https://arbiscan.io/address/0xf2744e1fe488748e6a550677670265f664d96627)

## Losses

Losses amounted to 1620 ETH worth [$3,000,000](https://cointelegraph.com/news/alleged-swaprum-rug-pull-swipes-three-million-in-customer-funds).

## Timeline

- **May 18, 2023, 05:32 PM UTC:** A malicious upgrade has [occurred](https://arbiscan.io/tx/0x11a84164726c57dd7c3c0f610ed65cfa5f062009b3d51bcacc31e52c50908a9c).
- **May 18, 2023, 05:51 PM UTC:** [Mint](https://arbiscan.io/tx/0x821b2e98bb5ab19b6b35e5abaceca3d263a17b07039bc169823d7cf27460168e) SAPR tokens.
- **May 18, 2023, 11:21 PM UTC:** Sending ETH to Tornado Cash has [begun](https://etherscan.io/tx/0x63a85e7ae322256a17ba8a5da966124c7f869fb8188b972f40812a94b3b7cc04)

## Early Indicators

- **Centralization control of contract upgrade:** [This allows the deployer to introduce a malicious function and execute the exit scam.](https://skynet.certik.com/projects/swaprum)
