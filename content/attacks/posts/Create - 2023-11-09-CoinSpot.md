---

date: 2023-11-08
target-entities: CoinSpot
entity-types: Exchange
attack-types: Private Key Leak
title: “Crypto exchange CoinSpot reportedly suffers $2M hot wallet hack”
loss: 2622019.54

---

## Summary

According to [Etherscan](https://etherscan.io/tx/0x210ca8b12d1763307636982a0972437009ec7f65626db23c8b2b2a0a308bcf61) Australian crypto exchange CoinSpot reportedly suffered a $2.4 [million](https://cryptotvplus.com/2023/11/coinspot-exchange-allegedly-suffers-2m-hot-wallet-hack/) loss in a hot wallet hack, according to [CertiK,]((https://twitter.com/CertiK/status/17226592787863720660 ) a blockchain security firm. The hack involved a compromised private key associated with a CoinSpot hot wallet. Blockchain investigator ZachXBT noted on November 8th that two transactions were detected entering the suspected hacker's wallet, who later transferred the funds through THORChain and Wan Bridge onto the Bitcoin network. CertiK found that the compromise likely occurred due to a compromised private key. The hacker received 1,262 ETH from a known CoinSpot wallet, then made transactions, swapping ETH for Wrapped Bitcoin on Uniswap, and later exchanging ETH for Bitcoin via THORChain. The stolen Bitcoin was sent to multiple wallets, subdivided into smaller amounts to hinder tracing. CoinSpot is regulated by the Australian Transaction Reports and Analysis Centre. The incident adds to concerns about crypto platform security, leading regulators to explore protective measures. Other recent crypto hacks, such as Platypus, have contributed to increased regulatory scrutiny. The Australian financial authority AUSTRAC, is actively addressing the security breach because the amount stolen is more than [$10,000.](chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://www.austrac.gov.au/sites/default/files/2021-11/AUSTRAC%20draft%20guidance%20-%20reporting%20multiple%20cash%20transactions_0.pdf)  

## Attackers

The attacker has yet to be identified. 

## Losses

CoinSpot lost 1,262 ETH during the hack, worth 2,400,000 USD at the time of the attack. 

## Timeline

   - “November 8, 2023/20:01 UTC:” ZackLBT announces hack on [Telegram.](https://t.me/investigations/70) 
   - “November 9, 2023/5:25 UTC:” [Cointelegraph](https://twitter.com/Cointelegraph/status/1722485447723745448) posts exploit on X (formally known as Twitter) and suggests the hack is due to a private key leak. 
   - ”November 10, 2023/15:29 UTC:” The Financial [Review](https://www.afr.com/technology/crypto-hack-suggests-australia-s-coinspot-exchange-has-been-compromised-20231110-p5eizc) confirms the funds have been reported stollen to Chainalysis, and states no customers have been affected by the attack. 

## Security Failure Causes

CertiK stated in email correspondence the alleged attack was the result of a “probable private key compromise” on at least one CoinSpot hot wallet. It is currently unknown if any additional wallets have been affected.
  
  
