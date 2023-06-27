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

- Approximately 125.66 xBTC with an estimated value of around $4,335,000 was obtained through the exploits.
- An amount of 202,920 xUSD, equivalent to approximately $202,920.
- A total of 440,000 XHV with an approximate value of $1,540,000 was frozen in KuCoin.
- TradeOgre froze 100,000 XHV, valued at approximately $350,000.

## [Timeline](https://cdn.havenprotocol.org/app/uploads/2021/07/Technical-Overview-of-June-2021-Exploits.pdf)

-**June 22, 2021 (Blocks 882877, 18:19:41):**
    A miner exploited a vulnerability in the miner-reward-validation code by modifying the transaction code. This allowed them to mint a higher mining reward than was due. The exploit resulted in a total of 6.73 xBTC and 101,460 xUSD.

-**June 23, 2021 (Blocks 883040, 00:01:50):**
    A similar exploit occurred, where the miner again manipulated the code to increase the block reward. This resulted in an additional 6.73 xBTC and 101,460 xUSD being obtained.

 -**June 24, 2021 (Block 884293, 17:51:46):**
    The attacker took advantage of a vulnerability in transaction types to modify outputs and mint extra xAssets. In this instance, 2.2 xBTC was fraudulently obtained.

-**June 24, 2021 (Block 884305, 18:09:30):**
    A change was made to a previous transaction (tx), resulting in an invalid transaction and the loss of the counterfeit funds obtained.

-**June 25, 2021 (Block 884689, 07:04:19):**
    Similar to the previous exploit, the attacker manipulated transaction types, resulting in the loss of 110 xBTC.

-**June 29, 2021 (Block 887361, 00:45:20 - Block 887409, 02:15:23):**
    The attacker exploited a vulnerability to manipulate the output values and mint arbitrary amounts. This exploit occurred 18 times within this timeframe.

## Security Failure Causes

1. Improve Development Processes:
   - Open up the repository to more developers and ensure git history is included. See [GitHub](https://github.com/).
   - Implement a branch structure with master, develop, feature, and hotfix branches to facilitate a more open process.
   - Enforce a standard of imposing unit tests that cover all edge cases before merging a feature branch into the development branch.
   - Make Pull Requests transparent and reviewable by all team members. Require approval from two of the following team members: Neil, Akil, or Justin.
   - Rewrite Monero's unit tests for Haven and run them in a Continuous Integration/Continuous Deployment (CI/CD) process for every Pull Request. Thoroughly review potential instances in the code where invalid inflation could be introduced.
   - Add unit tests for various scenarios, including transaction creation, modified conversion rates, conversions between XHV and xAsset, incompatible transfer types, multiple assets, older fee versions, older transaction versions, miner transactions, pricing records with arbitrary prices, and more.
   - Scan the chain to identify any transactions or pricing records that may have utilized the mechanisms mentioned above to create hidden inflation.

2. Enhance Community Engagement and Collaboration:
   - Establish a generous bug bounty program.
   - Conduct weekly or bi-weekly technical calls open to anyone in the community to discuss technical ideas and implementations.
   - Introduce Haven Improvement Proposals (HIPs) and create a repository to track these proposals. Provide a forum for streamlined, transparent, and asynchronous discussions.
   - Assign two team members to manage Pull Requests.
   - Implement a robust decentralized voting mechanism.
   - Design and implement proof-of-coin to ensure accurate tracking of minted and burnt amounts in transactions. Seek review, vetting, and validation from cryptography experts regarding both the mathematical logic and implementation.
