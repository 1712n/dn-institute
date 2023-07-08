---
date: 2021-05-19
target-entities: PancakeBunny
entity-types: DeFi, Yield Aggregator
attack-types: Flash Loan Attack
title: "PancakeBunny suffers a flash loan attack"
---

## Summary

On May 19, 2021 PancakeBunny, a yield farming aggregator built on Binance Smart Chain, suffered a flash loan attack. 
- According to [the SlowMist report, they shared after investigating the incident](https://slowmist.medium.com/slowmist-pancakebunny-hack-analysis-4a708e284693) 
> The attacker first borrows a huge amount of WBNB tokens from the multiple liquidity pools of PancakeSwap and borrows a huge amount of WBNB tokens from the Fortube project.
>
- These assets were used to manipulate the price of BUNNY/BNB and USDT/BNB. [Cofounder of Halborn Rob Behnke describes the main steps of the manipulating](https://www.halborn.com/blog/post/explained-the-pancakebunny-protocol-hack-may-2021) as follows: minting LP tokens as a result of depositing a pair of tokens; swapping a large amount of one token of this pair for another to modify an exchange rate; finally, exchanging LP tokens for share of the invested pair, exploiting modified prices.
- According to the BunnyMinterV2 contract, the attacker acquired 6,972,455 BUNNY tokens. 90% of these BUNNYs were swapped for BNB to pay off the flash loan and with the modified BUNNY/BNB pricing, it allowed the hacker to get profit
> when extracting value or exchanging BUNNY for BNB, the attacker received more tokens than they “should” have.  As a result, after paying off the flash loan, the attacker had 114,631 WBNB left over
>
> -- Rob Behnke
[Source](https://www.halborn.com/blog/post/explained-the-pancakebunny-protocol-hack-may-2021)
>
- Dumping 90% of the received BUNNY tokens in the market caused its price to plummet, but BUNNY's price was manipulated in a way that it first increased for a short time after the exploit transaction. It was at that time when the hacker could profitably swap the remaining 10% of BUNNY tokens they had.

## Attackers

The attacker remain unidentified. 
Attacker's wallet address:
[0xa0ACC61547f6bd066f7c9663C17A312b6Ad7E187](https://bscscan.com/address/0xa0acc61547f6bd066f7c9663c17a312b6ad7e187)

## Losses

The amount of stolen assets [was estimated at about $200 million at prices at the time. BUNNY token lost around 96% of its value.](https://cointelegraph.com/news/pancakebunny-tanks-96-following-200m-flash-loan-exploit)

## Timeline

**May 19, 2021**
- **10:34 PM UTC:** [Exploit transaction](https://bscscan.com/tx/0x897c2de73dd55d7701e1b69ffb3a17b0f4801ced88b0c75fe1551c5fcce6a979) was executed
- **10:45 PM UTC:** 114,631 BNB were sent to this address: [0x158c244b62058330f2c328c720b072d8db2c612f](https://bscscan.com/address/0x158c244b62058330f2c328c720b072d8db2c612f)
- **11:18 PM UTC:** The Flash Loan attack is officially confirmed, the Bunny Team paused deposits/withdrawals to the Vault to prevent further attacks
- **11:59 PM UTC:** 488,071 BUNNY were swapped for 916,1 BNB

**May 21, 2021**
- **06:30 AM UTC:** The Team restored withdrawal/deposit function to the Vault

[Source](https://pancakebunny.medium.com/hello-bunny-fam-a7bf0c7a07ba)

## Security Failure Causes

- **Smart contract vulnerability:** The BunnyMinterV2 contract was not prevented from minting an immense amount of BUNNY tokens in case of manipulating LP prices:
> The key point is that the price calculation of WBNB-BUNNY LP is flawed, and the number of BUNNY minted by the BunnyMinterV2 contract depends on this flawed LP price calculation method
> 
> -- SlowMist
[Source](https://slowmist.medium.com/slowmist-pancakebunny-hack-analysis-4a708e284693)
