---
date: 2022-10-11
target-entities:
  - Mango Markets
entity-types:
  - DeFi
  - Exchange
attack-types:
  - Price Oracle Manipulation
title: "Mango Markets Exploited for $116 Million"
loss: 116000000
---

## Summary

On October 11th, 2022, Mango Markets, a decentralized exchange on Solana, was exploited. The hacker manipulated the price oracle for the protocol's MNGO token by first taking out a long MNGO position on Mango. Then the attacker artificially raised the price of the MNGO token by taking advantage of low liquidity on secondary markets. The exploiter then used the temporary high price of MNGO to take out loans of USDC, various other stable coins, and SOL against unrealized profit on the long MNGO position.

## Attacker

The attacker revealed himself in a series of [tweets](https://twitter.com/avi_eisen/status/1581326197241180160) under the pseudonym of Avraham Eisenberg.

## Losses

Approximately $116 million worth of assets were lost, and $67 million was [returned].(https://twitter.com/mangomarkets/status/1581351549644591104?s=20&t=9Xyt2Cc97N9F0A3iOR0_MA).

## Timeline

- **October 11, 2022, 10:19 PM UTC:** [Hacker's Wallet 1](https://explorer.solana.com/tx/66AFLig3vs5XkksTZRh5BPo2iiiPV7jHL3hhjwMe3mRyqC9FG8ELgx3HPCWs8QQy1iSi9BAzm6Wx24fHcTtC1xyC) and [Wallet 2](https://explorer.solana.com/tx/3cBEK257espSw2X6Z7ZZESPPdcsfBoNLYJGAmXEExxw1QpjkSJfcd9kmtER7LkZ3RGbeXKHv1FR4hRBCD5wA8unY) are funded with 5 million USDC each.
- **October 11, 2022, 10:25 PM UTC:** [MNGO-SOL Perp Sell Order placed by Wallet 1](https://trade.mango.markets/account?pubkey=CQvKSNnYtPTZfQRQ5jkHq8q2swJyRsdQLcFcj3EmKFfX) for 483 million MNGO.
- **October 11, 2022, 10:25 PM UTC:** [MNGO-SOL Sell Order bought by Wallet 2,](https://trade.mango.markets/account?pubkey=4ND8FVPjUGGjx9VuGFuJefDWpg3THb58c277hbVRnjNaa) which opens up a MNGO long position for Wallet 2.
- **October 11, 2022, 10:26 PM UTC:** Hacker buys a large amount of MNGO on Mango Markets and CEX's.
- **October 11, 2022, 10:45 PM UTC:** The MNGO price on Mango Markets rises significantly, and Wallet 2 takes out a loan of $116 million against its unrealized profits from its MNGO position.

## Security Failure Causes

**Oracle vulnerability:** Mango Markets relied heavily on external price feeds to determine the amount of assets it could lend out to a user. These price feeds were easy to manipulate because there was insufficient liquidity for the MNGO token.

**Protocol vulnerability:** The hacker was able to take on an incredibly large MNGO position in a short amount of time. Trade surveillance systems would have detected unusual activity for a MNGO position of that size and could have alerted the protocol to watch for unusual activity.
