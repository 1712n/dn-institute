---
date: 2023-11-08
target-entities: CoinSpot
entity-types: 
   - Exchange
attack-types:
   - Private Key Leak
title: “Crypto exchange CoinSpot reportedly suffers $2M hot wallet hack”
loss: 2622019.54
---

## Summary

According to [CertiK,](https://twitter.com/CertiK/status/17226592787863720660) Australian crypto exchange CoinSpot, reportedly suffered a $2.4 [million](https://cryptotvplus.com/2023/11/coinspot-exchange-allegedly-suffers-2m-hot-wallet-hack/) due to a compromised private key. On November 8th, two transactions were detected entering the identified wallet, which later transferred the funds through THORChain and Wan Bridge onto the Bitcoin network. The hacker received 1,262 ETH from a known CoinSpot [wallet,](https://etherscan.io/tx/0x210ca8b12d1763307636982a0972437009ec7f65626db23c8b2b2a0a308bcf61) then made transactions, swapping ETH for Wrapped Bitcoin on Uniswap, and later exchanging ETH for Bitcoin via THORChain. The stolen Bitcoin was sent to multiple wallets and subdivided into smaller amounts to hinder tracing. The Australian financial authority AUSTRAC is actively addressing the security breach because the amount stolen is more than [$10,000.](www.austrac.gov.au/sites/default/files/2021-11/AUSTRAC%20draft%20guidance%20-%20reporting%20multiple%20cash%20transactions_0.pdf)  

## Attackers

The attacker has yet to be identified. 

## Losses

CoinSpot lost 1,262 ETH, worth $2,400,000 USD at the time of the attack. It is currently unknown if any additional wallets have been affected. 

## Timeline

   - **“November 8, 2023, 20:01 UTC:”** ZackLBT announces hack on [Telegram.](https://t.me/investigations/70) 
   - **“November 9, 2023, 06:25 UTC:”** [Cointelegraph](https://twitter.com/Cointelegraph/status/1722485447723745448) posts the exploit on X suggesting the hack was due to a private key leak. 
   - **”November 10, 2023, 15:29 UTC:”** The Financial [Review](https://www.afr.com/technology/crypto-hack-suggests-australia-s-coinspot-exchange-has-been-compromised-20231110-p5eizc) confirms the funds have been reported stolen to Chainalysis.

## Security Failure Causes

   - **Insufficient real-time monitoring of transactions:**  The suspected hacker executed two unauthorized transactions without immediate detection.
