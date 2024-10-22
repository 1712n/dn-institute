---
date: 2022-10-27
target-entities: Team Finance
entity-types: DeFi
attack-types: Smart Contract Exploit
title: "Team Finance Suffers $14.5 Million Security Breach"
loss: 14500000
---

## Summary

Team Finance experienced a significant breach on the Ethereum blockchain during a migration process from Uniswap v2 to v3, resulting in the theft of approximately $14.5 million. The exploit was executed through vulnerabilities in the smart contract, facilitating unauthorized token transfers and manipulations of the Initialize price within the V3 liquidity pool.

## Attackers

The identity of the hackers who attacked Team Finance is unknown.

Hacker Ethereum Wallets:

- [0x161cebb807ac181d5303a4ccec2fc580cc5899fd](https://etherscan.io/address/0x161cebb807ac181d5303a4ccec2fc580cc5899fd)
- [0xba399a2580785a2ded740f5e30ec89fb3e617e6e](https://etherscan.io/address/0xba399a2580785a2ded740f5e30ec89fb3e617e6e)

## Losses

Team Finance lost approximately $14.5 million in total:

- ETH: 880
- DAI: 6,429,327
- CAW: 74,613,657,704
- TSUKA: 1,183,757

## Timeline

- **October 27, 2022, 07:22:35 AM UTC:** The attacker [deployed](https://etherscan.io/tx/0xa3cbbdd2494f6d5452de8edc5c8c32f316abc40140a63769a22e04cd2549963b) the attack contract and also [generated “token A”](https://etherscan.io/tx/0xa3cbbdd2494f6d5452de8edc5c8c32f316abc40140a63769a22e04cd2549963b).
- **October 27, 2022, 08:29:23 AM UTC:** The [malicious transaction was executed](https://etherscan.io/tx/0xb2e3ea72d353da43a2ac9a8f1670fd16463ab370e563b9b5b26119b2601277ce).
- **October 27, 2022, 04:21 PM UTC:** Team Finance [reported](https://twitter.com/TeamFinance_/status/1585562380591063043) about the hack.
- **October 31, 2022:** The attacker [returns](https://cointelegraph.com/news/team-finance-hacker-returns-7m-to-associated-projects-after-exploit) $7 million in stolen funds.
- **November 3, 2022:** SlowMist, the blockchain security firm, [published](https://slowmist.medium.com/analysis-review-of-team-finance-exploit-f439c2f63e2) a hack analysis.

## Security Failure Causes

- **Smart Contract Vulnerability:** The breach was facilitated by a smart contract vulnerability, where inadequate security checks allowed attackers to bypass safeguards during the token migration process. This included the manipulation of liquidity pool prices and the execution of unauthorized token transfers, leveraging the system's weaknesses for substantial financial gain.
