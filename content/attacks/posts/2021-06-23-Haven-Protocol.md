---
date: 2021-06-23
categories: Protocol Exploit
title: "Haven Protocol Hack"
---

## Summary

Haven Protocol experienced a series of exploits that resulted in financial losses and raised concerns about the security of the platform. The exploits targeted various aspects of the protocol, including miner rewards, transaction validation, and conversion fees.

## Attackers

The identity of the attackers remains unknown.

## [Losses](https://cdn.havenprotocol.org/app/uploads/2021/07/Technical-Overview-of-June-2021-Exploits.pdf)

- Approximately 125.66 xBTC with an estimated value of around $4,335,000 was obtained through the exploits.
- An amount of 202,920 xUSD, equivalent to approximately $202,920.
- A total of 440,000 XHV with an approximate value of $1,540,000 was frozen in KuCoin.
- TradeOgre froze 100,000 XHV, valued at approximately $350,000.

## Timeline

-**June 22, 2021  18:19:41:**
    A miner exploited a vulnerability in the miner-reward-validation code by modifying the transaction code. This allowed them to mint a higher mining reward than was due. The exploit resulted in a total of 6.73 xBTC and 101,460 xUSD.

-**June 23, 2021  00:01:50:**
    A similar exploit occurred, where the miner again manipulated the code to increase the block reward. This resulted in an additional 6.73 xBTC and 101,460 xUSD being obtained.

 -**June 24, 2021 17:51:46:**
    The attacker took advantage of a vulnerability in transaction types to modify outputs and mint extra xAssets. In this instance, 2.2 xBTC was fraudulently obtained.

-**June 24, 2021  18:09:30:**
    A change was made to a previous transaction (tx), resulting in an invalid transaction and the loss of the counterfeit funds obtained.

-**June 25, 2021 07:04:19:**
    Similar to the previous exploit, the attacker manipulated transaction types, resulting in the loss of 110 xBTC.

-**June 29, 2021 00:45:20 - 02:15:23:**
    The attacker exploited a vulnerability to manipulate the output values and mint arbitrary amounts. This exploit occurred 18 times within this timeframe.
    
-**July 19, 2021:** 
    [The fork](https://havenprotocol.medium.com/haven-protocol-successfully-deploys-rollback-hard-fork-206e5ead190e) rolled back the chain to the safest block, that allows exchange wallets to re-open, on-chain transactions to resume, and mining to continue with confidence. However, xUSD and xAsset conversions in the Haven Vault remain paused.  

## Security Failure Causes

-    Inadequate Development Processes: Insufficient attention to development practices and protocols, leading to vulnerabilities and exploits. Lack of open repository, limited unit testing, and incomplete code reviews contributed to the security breach.

 -   Lack of Community Engagement: Insufficient community involvement and collaboration hindered the identification of potential vulnerabilities. The absence of bug bounty programs, infrequent technical calls, and a lack of transparent proposal discussions limited the collective effort to enhance security.