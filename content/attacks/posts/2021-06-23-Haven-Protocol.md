---
date: 2021-06-23
categories: Protocol Exploit
title: "Haven Protocol Hack"
---

## Summary

Haven Protocol experienced a series of exploits that resulted in financial losses. The attacker [manipulated](https://havenprotocol.org/wp-content/uploads/2021/07/Technical-Overview-of-June-2021-Exploits.pdf) their transaction by modifying the proof-of-value and burnt/mint checks, setting the amount burnt/mint to 0. Since multiplying 0 by any value results in 0, the validation passed, allowing the attacker to proceed. By manipulating the output values, the attacker was able to mint an arbitrary amount.

## Attackers

The identity of the attackers remains unknown. The attacker address involved in the Haven Protocol exploit is not publicly disclosed or known.

## Losses

- The total losses amount to approximately $6,427,920
- Approximately 125.66 xBTC with an estimated value of around $4,335,000 was obtained through the [exploits](https://cdn.havenprotocol.org/app/uploads/2021/07/Technical-Overview-of-June-2021-Exploits.pdf).
- An amount of 202,920 xUSD, equivalent to approximately $202,920.
- A total of 440,000 XHV with an approximate value of $1,540,000 was frozen in KuCoin.
- TradeOgre froze 100,000 XHV, valued at approximately $350,000.

## Timeline

- **June 22, 2021:** 203,000 xUSD and 13.5 xBTC was minted in two [exploits](https://havenprotocol.medium.com/haven-protocol-exploits-mitigation-plan-and-next-steps-d7a2b1a65654). 
- **June 24, 2021:** An exploit in the xAsset conversion validation.
- **June 29, 2021:** an exploit was leveraged that allowed for minting of 9m xUSD.
- **July 19, 2021:** Chain rollback through a [fork](https://havenprotocol.medium.com/haven-protocol-successfully-deploys-rollback-hard-fork-206e5ead190e), allowing exchange wallets to reopen and on-chain transactions to resume. xUSD and xAsset conversions in the Haven Vault remain paused.

## Security Failure Causes

- Insufficient attention to development practices.
- Lack of open repository.
- Lack of bug bounty programs.
- Lack of Community Engagement.
