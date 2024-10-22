---
date: 2021-12-13
target-entities: Vulcan Forged
entity-types:
  - GameFi
attack-types: Phishing
title: "Vulcan Forged hacked for $140 million worth of PYR tokens"
loss: 140000000
---

## Summary

In December 2021, Vulcan Forged, a well-known play-to-earn cryptocurrency operating on the Polygon Network, faced a devastating exploit involving the theft of $140 million. As outlined in the post-mortem report released by the developers, the [attacker managed to employ social engineering tactics to compromise the credentials of user wallets](https://twitter.com/VulcanForged/status/1470323775988240387), thereby gaining access to private keys. Consequently, the hacker succeeded in withdrawing 4.5 million Vulcan Forged tokens (PYR), which, at that time, held a value exceeding $140,000,000.

## Attackers

This adresses [play main role](https://twitter.com/VulcanForged/status/1470206092286345219)

- Polygone:
  - [0x48ad05a3B73c9E7fAC5918857687d6A11d2c73B1](https://polygonscan.com/address/0x48ad05a3B73c9E7fAC5918857687d6A11d2c73B1)

## Losses

[The majority of PYR has been refunded to affected wallets from the Vulcan Forged treasury and company have isolated the tokens stolen from all CEX exchanges](https://twitter.com/VulcanForged/status/1470365117774770180), but [PYR has dropped in value by over 30% in the next 24 hours after hack.](https://www.tradingview.com/x/kRKHypFp/)

## Timeline:

- December 13, 2021
   - **Early in the day:** Vulcan Forged [announces](https://twitter.com/VulcanForged/status/1470201106626224140) on Twitter that 148 wallets holding PYR tokens have been compromised and over 4.5 million PYR has been stolen. The company assures they are taking steps to understand what happened.
   - **During the day:** Vulcan Forged announces that they have identified the wallet responsible for the theft, and shares the address. They also mention they have contacted all exchanges to blacklist this address, and there are indications that the wallet owner may have undergone KYC on an exchange they are now in contact with.
   - **Throughout the day:** The company keeps assuring the users that all the lost PYR will be replaced from their treasury.
   - **Toward the end of the day:** Vulcan Forged announces that those who lost other assets, including ETH and MATIC, [will also be reimbursed in the equivalent of PYR](https://twitter.com/VulcanForged/status/1470298466366730246) as it was ultimately the company's responsibility.

## Security Failure Causes

- **Custodial wallet:** Vulcan Forged acknowledges that private keys were exposed through phishing techniques and hacking of the server since they were using a semi-custodial wallet.
