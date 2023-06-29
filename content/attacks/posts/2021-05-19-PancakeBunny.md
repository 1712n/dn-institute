---
date: 2021-05-19
categories: "DeFi"
title: "PancakeBunny suffers a flash loan attack"
---

## Summary

On May 19, 2021 PancakeBunny, a yield farming aggregator built on Binance Smart Chain decentralized finance (DeFi) protocol, suffered a flash loan attack. According to [the SlowMist report they shared after investigating the incident](https://slowmist.medium.com/slowmist-pancakebunny-hack-analysis-4a708e284693) the attacker "borrows a huge amount of WBNB tokens from the multiple liqudity pools of PancakeSwap and borrows a huge amount of WBNB tokens from the Fortube project". These assets were used to manipulate the price of BUNNY/BNB and USDT/BNB.

[Cofounder of Halborn Rob Behnke describes the main steps of this manipulating](https://www.halborn.com/blog/post/explained-the-pancakebunny-protocol-hack-may-2021) as follows: minting LP tokens as a result of depositing a pair of tokens; swapping a large amount of one token of this pair for another to modify an exchange rate; finally, exchanging LP tokens for share of the invested pair, exploiting modified prices. This double price manipulation allowed the hacker to get profit, Rob Behnke's quote: "exchanging BUNNY for BNB the attacker received more tokens than they "should" have. As a result, after paying off the flash loan, the attacker had 114,631 WBNB left over".

Another part of the attacker's profit (mentioned in Timeline section on 11:59 PM) was the remainder of BUNNY tokens he acquired according to the BunnyMinterV2 contract.

## Attackers

The attacker remain unidentified. 
Attacker's wallet address:
0xa0ACC61547f6bd066f7c9663C17A312b6Ad7E187

## Losses

If calculated at prices at the time of the incident, PancakeBunny's loss was about $200 million. BUNNY token lost 95% of its value.

## Timeline

The timeline of the incident with more details is provided on [the PancakeBunny Medium blog](https://pancakebunny.medium.com/hello-bunny-fam-a7bf0c7a07ba)
**May 19, 2021**
- **10:31 PM UTC:** 1BNB deposited on the USDT/BNB Flip Vault to stage the attack
- **10:34 PM UTC:** the time of the exploit transaction
- **10:36 PM UTC:** the Bunny Team detected unusual increase of BUNNY's price
- **10:45 PM UTC:** 114631BNB were sent to this address: 0x158c244b62058330f2c328c720b072d8db2c612f
- **11:18 PM UTC:** the Flash Loan attack is officially confirmed, the Bunny Team paused deposits/withdrawals to the Vault to prevent further attacks
- **11:59 PM UTC:** 488071,8...BUNNY were swapped for 9161,3...BNB from the same address as on 10:45

**May 21, 2021**
- **06:30 AM UTC:** the Team restored withdrawal/deposit function to the Vault

## Security Failure Causes

- According to the abovementioned SlowMist's report "the price calculation of WBNB-BUNNY LP is flawed, and the number of BUNNY minted by the BunnyMinterV2 contract depends on this flawed LP price calculation method" and "the final LP price was maliciously manipulated and increased by the attacker, which resulted in the BunnyMinterV2 contract eventually minting a large number of BUNNY tokens". To avoid this they recommend to use a credible delayed price feed oracle.
- Provided a flash loan is borrowed and paid back in the same transaction, there is no limit to the amount of assets that can be borrowed.
