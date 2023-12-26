---
date: 2023-11-08
target-entities: CoinSpot
entity-types: 
   - Exchange
attack-types:
   - Private Key Leak
title: “Crypto exchange CoinSpot reportedly suffers $2.4 million hot wallet hack”
loss: 2400000
---

## Summary

On November 8, 2023, the Australian crypto exchange, CoinSpot, experienced an attack on two of its hot wallets resulting in more than [$2.4 million](https://cryptodaily.co.uk/2023/11/coinspot-reportedly-suffers-2m-private-key-exploit) in losses due to a private key leak. The recipient of these funds exchanged them using platforms THORchain and Wan Bridge before exchanging them for Bitcoin using Uniswap and spreading them into four wallets. The Australian financial authority, AUSTRAC, is actively addressing the security breach because the amount stolen is more than [$10,000.](www.austrac.gov.au/sites/default/files/2021-11/AUSTRAC%20draft%20guidance%20-%20reporting%20multiple%20cash%20transactions_0.pdf)  

## Attackers

The attacker has yet to be identified. The stolen Ether was transferred into the following Bitcoin wallets.

   - Bc1qfsm2vhhurrq54w40z8vasjkfhxrvsvysjk9jug
   - Bc1qzl2s7ajehkpu9wdqewg5xqy8nzxv7njctvrqzx
   - Bc1q49d37gnmdu4p77n9j8c7ytrv30xrrue50r88lh
   - bc1qtj29wrm56r0lvhqufsju9pr0vakj8uwd38p4gj 

## Losses

CoinSpot lost 1,262 ETH, worth $2,400,000 USD at the time of the attack. It is currently unknown if any additional wallets have been affected. 

## Timeline

   - **November 8, 2023, 18:16 UTC:** Initial [transactions](https://etherscan.io/address/0x326dc417d96c72349FA3d1fda4aE9C1c77FD89B8) take place.
   - **“November 8, 2023, 20:01 UTC:”** ZackLBT announces hack on [Telegram.](https://t.me/investigations/70) 
   - **“November 9, 2023, 06:25 UTC:”** [Cointelegraph](https://twitter.com/Cointelegraph/status/1722485447723745448) posts the exploit on X suggesting the hack was due to a private key leak. 
   - **”November 10, 2023, 15:29 UTC:”** The Financial [Review](https://www.afr.com/technology/crypto-hack-suggests-australia-s-coinspot-exchange-has-been-compromised-20231110-p5eizc) confirms the funds have been reported stolen to Chainalysis.

## Security Failure Causes

   - **Insufficient real-time monitoring of transactions:**  The suspected hacker executed two unauthorized transactions without immediate detection.
   - **Inadequate Key Management:** Poor practices in key storage, key access protocols, and possibly using weak or outdated cryptographic algorithms all contribute to poor key management.
   - **Insufficient Network Security Measures:** The breach indicates potential weaknesses in network security controls which allowed the attacker to maneuver throughout the network unnoticed. 
