---
date: 2023-09-23
target-entities: Mixin Network
entity-types:
- Custodian
attack-types:
- Infrastructure Attack
title: "Mixin Network lost at least $141 million due to a database attack"
---

## Summary

In the early morning of September 23, 2023 Hong Kong time, the database of Mixin Network's [cloud service provider was hacked](https://twitter.com/MixinKernel/status/1706139175018529139), resulting in the loss of approximately $200M. Mixin Network is a service similar to a layer-2 protocol, designed to make cross-chain transfers cheaper and more efficient. A large number of deposit addresses have been drained. [The attacker compromised the cloud](https://twitter.com/BlockSecTeam/status/1706319766544155068), recovered the private keys of deposit addresses (and hot wallet addresses, supposedly) and transferred funds in order from the highest to the lowest balance, involving 10,000+ transactions, lasting several hours. 


## Attackers

North Korean Lazarus Group is [suspected](https://rekt.news/mixin-rekt/#:~:text=This%20case%20has%20many%20of%20the%20hallmarks%20of%20a%20Lazarus%20heist%2C%20who%20have%20been%20plenty%20busy%20lately.) to be [behind the hack](https://www.bleepingcomputer.com/news/security/mixin-network-suspends-operations-following-200-million-hack/#:~:text=creates%20immediate%20suspicion%20about%20the%20Lazarus%20group%20being%20responsible), but no evidence so far. The attackers used the following addresses to transfer the funds:

- **Ethereum:**  
    - [0x52E86988bd07447C596e9B0C7765F8500113104c](https://etherscan.io/address/0x52E86988bd07447C596e9B0C7765F8500113104c)  
    - [0x3B5fb9d9da3546e9CE6E5AA3CCEca14C8D20041e](https://etherscan.io/address/0x3B5fb9d9da3546e9CE6E5AA3CCEca14C8D20041e)  
    - [0xB5d631A74AD9c9efcF96d6e9e2fAbcB75C67Eafa](https://etherscan.io/address/0xB5d631A74AD9c9efcF96d6e9e2fAbcB75C67Eafa)  

- **Bitcoin:**  
    - [bc1qq7uefmz6nng5c4dzs9mwrxxyh9sxg5cjg85hes](https://www.blockchain.com/explorer/addresses/btc/bc1qq7uefmz6nng5c4dzs9mwrxxyh9sxg5cjg85hes)  


## Losses

Mixin Network lost $141,328,868.21 [identified](https://twitter.com/peckshieldalert/status/1706199059705598406?s=52&t=yv7fZgVN8INf98Rdhx6jXQ) from reportedly around $200M in total across the following chains:

- $94,48M in Ethereum
- $23,55M in DAI (Recevied in USDT, swapped to DAI)
- $23,30M in Bitcoin

## Timeline

- **September 22, 2023, 11:45 PM UTC:** Beginning of [funds transfer](https://etherscan.io/tx/0xd5e2209c988b8d5a92617bac2ea24ca3e411b011787a9837aedb1e6ee7bbc68d) from Mixin Network.
- **September 24, 2023, 02:27 AM UTC:** SlowMist, blockchain security company, [reports](https://twitter.com/SlowMist_Team/status/1706133260869468503) on attack.
- **September 25, 2023, 02:40 AM UTC:** Mixin Network [confirmed](https://twitter.com/MixinKernel/status/1706139175018529139) the attack, suspended services, anounced a public mandarin livestream at 13:00 HKT on September 25 and promised an english summary yet to be published.
- **September 25,2023, 06:48 AM UTC:** [PeckShieldAlert](https://twitter.com/peckshieldalert/status/1706199059705598406?s=52&t=yv7fZgVN8INf98Rdhx6jXQ) reported on amount of funds stolen.
- **September 25, 2023, 06:55 AM UTC:** Mixin Network [offered](https://etherscan.io/tx/0x63b2433505098c584c09f70d5309ae2a6762883b8b9c83ad29f997c657f2593a) the hacker a reward of 10% ($20M) for funds return.
- **September 25, 2023, 08:01 AM UTC:** Feng Xiaodong, founder of Mixin Network, said that users will only get access to half of their assets for now according to [theblock.co](https://www.theblock.co/post/252716/mixin-network-founder-says-just-half-users-assets-are-safe-after-200-million-hack).
  > Feng added that the company can initially only ensure that half of the total user assets on the network are not affected by the hack. For the rest of the assets, Feng said that the team is considering issuing what he called “bond tokens” for users to claim, with plans for Mixin to buy them back in the future. 
- **September 25, 2023, 09:28 AM UTC:** [Lookonchain](https://twitter.com/lookonchain/status/1706239132585148907) reported on amount of funds stolen too.
- **September 25, 2023, 2:48 PM UTC:** BlockSec, crypto security firm, [shares it's findings](https://twitter.com/BlockSecTeam/status/1706319766544155068):
  >* the private keys of Mixin deposit addresses are stored in a recoverable manner.
  >* the attacker compromised the cloud and recovered the private keys of deposit addresses (and hot wallet addresses).
- **September 25, 2023, 11:08 AM UTC:** 0xScope, Web3 SaaS analytic platform, [revealed](https://twitter.com/ScopeProtocol/status/1706264439882944999) the hacker's historical relationship with Mixin Network. 
  > An address connected to the recent $200M MixinKernel hack received 5 $ETH from the platform last year and deposited 5.9 $ETH on Binance soon after.
- **September 27, 2023, 08:27 AM UTC:** Mixin Network made a [statement](https://twitter.com/MixinKernel/status/1706948541850235274), that they are working with Google (Mandiant) and SlowMist Team, blockchain security company, to assist with the investigation. And the losses are not as significant as estimated.

## Security Failure Causes

**Infrastructure Attack:** Mixin Network relied on a centrilized database, creating a single point of failure. And the private keys were stored in a recoverable manner. By compromising the cloud and getting access to the private keys of deposit addresses (and hot wallets) attacker was able to withdraw funds. 