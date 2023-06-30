---
date: 2021-06-23
categories: Protocol Exploit
title: "Haven Protocol Hack"
---

## Summary

Haven Protocol experienced a series of exploits that resulted in financial losses and raised concerns about the security of the platform. The exploits targeted various aspects of the protocol, including miner rewards, transaction validation, and conversion fees.

## Attackers

The identity of the attackers remains unknown.

## Losses

- Approximately 125.66 xBTC with an estimated value of around $4,335,000 was obtained through the [exploits](https://cdn.havenprotocol.org/app/uploads/2021/07/Technical-Overview-of-June-2021-Exploits.pdf).
- An amount of 202,920 xUSD, equivalent to approximately $202,920.
- A total of 440,000 XHV with an approximate value of $1,540,000 was frozen in KuCoin.
- TradeOgre froze 100,000 XHV, valued at approximately $350,000.

## Timeline

- **June 22, 2021:** Miner exploited a vulnerability, minting higher rewards (6.73 xBTC, 101,460 xUSD).
- **June 23, 2021:** Similar exploit, increased block rewards obtained (6.73 xBTC, 101,460 xUSD).
- **June 24, 2021:** Attacker modified outputs, minted extra xAssets (2.2 xBTC). Invalid transaction led to loss of counterfeit funds.
- **June 25, 2021:** Attacker manipulated transaction types, resulting in loss of 110 xBTC.
- **June 29, 2021:** Exploitation of vulnerability, minting arbitrary amounts occurred 18 times.
- **July 19, 2021:** Chain rollback through a [fork](https://havenprotocol.medium.com/haven-protocol-successfully-deploys-rollback-hard-fork-206e5ead190e), allowing exchange wallets to reopen and on-chain transactions to resume. xUSD and xAsset conversions in the Haven Vault remain paused.

## Security Failure Causes

- Inadequate Development Processes: Insufficient attention to development practices and protocols, leading to vulnerabilities and exploits. Lack of open repository, limited unit testing, and incomplete code reviews contributed to the security breach.

- Lack of Community Engagement: Insufficient community involvement and collaboration hindered the identification of potential vulnerabilities. The absence of bug bounty programs, infrequent technical calls, and a lack of transparent proposal discussions limited the collective effort to enhance security.
