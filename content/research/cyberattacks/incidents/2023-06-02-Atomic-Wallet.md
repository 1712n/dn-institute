---
date: 2023-06-02
target-entities: Atomic Wallet
entity-types:
  - DeFi
  - Wallet
attack-types:
  - Wallet Hack
tags:
  - North Korea
  - Lazarus Group
title: "Atomic Wallet Suffers Over $100 Million Security Breach"
loss: 100000000
---

## Summary

On June 2, 2023, Atomic Wallet, a non-custodial multichain DeFi wallet, experienced an exploit resulting in the loss of over $100 million worth of various assets from its users. The largest affected wallet lost a total of 7,950,000 USDT. The suspected perpetrator of this attack is the Lazarus Group, a known North Korean hacking group. The hackers moved the stolen funds to Ethereum and TRON addresses. The part of the stolen assets were laundered through Sinbad mixer and Russia-based exchange Garantex.

## Attackers

Lazarus Group, a North Korean hacking group, is suspected of being involved in the incident. The hackers used the following addresses to transfer the funds:

- Ethereum:
  - [0x26208699df4896f09b83993e7c8baad647421b21](https://etherscan.io/address/0x26208699df4896f09b83993e7c8baad647421b21)
- TRON:
  - [TV92VkrHpim1MN58GNC5RfUWVUmNTPRwGA](https://tronscan.org/#/address/TV92VkrHpim1MN58GNC5RfUWVUmNTPRwGA)

## Losses

The attack resulted in a loss of over $100 million affecting more than 5,000 wallets. The top five affected users alone accounted for losses of around $17 million. Atomic Wallet, with the assistance of on-chain experts, was able to freeze $1.2 million worth of funds.

[List of affected addresses](https://www.chainabuse.com/report/b181be45-51a7-446b-83ae-8408c9103bb5)

## Timeline

- **February 10, 2022:** Security audit company Least Authority warned in their [blog post](http://web.archive.org/web/20220623142131/https://leastauthority.com/blog/disclosure-of-security-vulnerabilities-in-atomic-wallet/) that funds in Atomic Wallet may have been at risk: The post has been deleted later.

  > We found that the design and implementation of the Atomic Wallet system does not sufficiently demonstrate considerations for security and places current users of the wallet at significant risk.

- **June 2, 2023, 9:45 PM UTC:** [Earliest malicious transaction recorded](https://twitter.com/tayvano_/status/1665069321255788544).
- **June 3, 2023, 10:45 AM UTC:** Atomic Wallet tweeted about receiving reports of wallets being compromised. The tweet was deleted later. [Archived source](https://archive.is/tmY9O)
- **June 6, 2023:** Blockchain analytics firm Elliptic [linked the incident](https://hub.elliptic.co/analysis/north-korea-s-lazarus-group-likely-responsible-for-35-million-atomic-crypto-theft/) to the North Korean hacking group:
  > ... analysis of the thief’s transactions leads us to attribute this hack to North Korea’s Lazarus Group, with a high level of confidence. This attribution is based on multiple factors ...
- **June 13, 2023:** It's been determined that the total loss [exceeds 100 million dollars](https://hub.elliptic.co/analysis/north-korea-linked-atomic-wallet-heist-tops-100-million/).
- **June 20, 2023:** Statement have been [published to Atomic Wallet's blog](https://atomicwallet.io/blog/june-3rd-event-statement), mentioning that less than 0.1% of the wallet users have been affected.
- **June 21, 2023:** A [class-action lawsuit has been filed against Atomic Wallet and its proprietor, Konstantin Gladych](https://www.courtlistener.com/docket/67520833/1/meany-v-atomic-wallet/), accusing them of "negligent and unlawful" behavior. The lawsuit asserts that the company has been aware of existing security flaws in Atomic Wallet since at least 2022.

## Security Failure Causes

- **Insufficient Private Key Security:** The audit by Least Authority hinted at potentially insufficient encryption methods used by Atomic Wallet. The private keys of Atomic Wallet's users were not properly secured. An attacker seemingly obtained these keys and made unauthorized transactions.
- **Ignored Security Audit Warning:** In February 2022, the security audit company, Least Authority, flagged potential vulnerabilities within Atomic Wallet's system. Atomic Wallet did not fully address these warnings, leaving potential weaknesses unattended.
- **Lack of Proactive Monitoring:** The absence of real-time monitoring and alerting systems allowed the attack to proceed unnoticed for several hours.
