---
date: 2021-05-19
target-entities: PancakeBunny
entity-types:
  - DeFi
  - Yield Aggregator
attack-types: Flash Loan Attack
title: "PancakeBunny suffers a flash loan attack for $40M+"
loss: 40000000
---

## Summary

On May 19, 2021 PancakeBunny, a yield farming aggregator built on Binance Smart Chain, suffered a flash loan attack.

> Exploit was possible because of how the protocol uses PancakeSwap AMM for its asset price calculation. In bugs like this, flashloans are the go-to way to manipulate the price of AMM pools which affects the price oracle
>
> -- Adrian Hetman
> [Source](https://www.adrianhetman.com/pancakebunny-hacked-for-40m/)

The hacker exploited a vulnerability related to reward minting to mint 6,972,455 BUNNY tokens, after which the flash loan was paid back, dumping the huge number of newly minted BUNNY in the market caused the token's price to plummet, the attacker ran off with 114k BNB and 697k BUNNY.

## Attackers

The attacker remains unidentified.
Attacker's wallet address:
[0xa0ACC61547f6bd066f7c9663C17A312b6Ad7E187](https://bscscan.com/address/0xa0acc61547f6bd066f7c9663c17a312b6ad7e187)

## Losses

The attacker stole assets [worth of $40M+](https://twitter.com/FrankResearcher/status/1395196961108774915)

## Timeline

- **May 19, 2021**
   - **10:34 PM UTC:** [Exploit transaction](https://bscscan.com/tx/0x897c2de73dd55d7701e1b69ffb3a17b0f4801ced88b0c75fe1551c5fcce6a979) was executed
   - **10:45 PM UTC:** 114,631 BNB were sent to this address: [0x158c244b62058330f2c328c720b072d8db2c612f](https://bscscan.com/address/0x158c244b62058330f2c328c720b072d8db2c612f)
   - **11:18 PM UTC:** The Flash Loan attack is officially confirmed, the Bunny Team paused deposits/withdrawals to the Vault to prevent further attacks
   - **11:59 PM UTC:** 488,071 BUNNY were swapped for 9,161 BNB
- **May 21, 2021**
   - **06:30 AM UTC:** The Team restored withdrawal/deposit function to the Vault

[Source](https://pancakebunny.medium.com/hello-bunny-fam-a7bf0c7a07ba)

## Security Failure Causes

- **Smart contract vulnerability:** To mint reward, the BunnyMinterV2 contract used a [flawed PancakeSwap LP price calculation in Bunny’s PriceCalculatorBSCV1 contract](https://cmichel.io/bsc-pancake-bunny-exploit-post-mortem/)

  > The key point is that the price calculation of WBNB-BUNNY LP is flawed, and the number of BUNNY minted by the BunnyMinterV2 contract depends on this flawed LP price calculation method
  >
  > -- SlowMist
  > [Source](https://slowmist.medium.com/slowmist-pancakebunny-hack-analysis-4a708e284693)

- **Lack of code review:**
  > Many people believe that composability is crucial to the success of DeFi. Token contracts (e.g., ERC20s) play an essential role on the bottom layer of DeFi legos. However, developers may overlook some uncontrollable and unpredictable conditions when integrating ERC20s into their DeFi projects. For example, you can’t predict when and how many tokens you will receive when you retrieve the current token balance.
  >
  > -- Amber Group
  > [Source](https://medium.com/amber-group/bsc-flash-loan-attack-pancakebunny-3361b6d814fd)
