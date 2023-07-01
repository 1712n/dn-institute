---
date: 2022-10-11
attacks/posts/categories: Protocol Exploit
title: "Mango Markets exploited for $116 million"
---

## Summary

On October 11th, 2022, Mango Markets, a decentralized exchange on Solana was exploited. The hacker manipulated the price oracle for the protocol's $MNGO token. The hacker first took out a long $MNGO position on Mango. Then the hacker artificially raised the price of $MNGO token by advantage of low liquidity on secondaries. The hacker then used the temporary high price of $MNGO to take out loans of USDC, various other stable coins, and SOL against unrealized profit on the long $MNGO position. 

## Attacker

The Attacker revealed himself in a series of [tweets](https://twitter.com/avi_eisen/status/1581326197241180160) under the pseudonym of Avraham Eisenberg.


## Losses

About USD $116 Million worth of crypto assets in terms of USDC, stablecoins and SOL was borrowed and never returned to the platform.

## Timeline

- **October 11, 2022 10:19 PM UTC:** [Hacker's Wallet 1](https://explorer.solana.com/tx/66AFLig3vs5XkksTZRh5BPo2iiiPV7jHL3hhjwMe3mRyqC9FG8ELgx3HPCWs8QQy1iSi9BAzm6Wx24fHcTtC1xyC) and [Wallet 2](https://explorer.solana.com/tx/3cBEK257espSw2X6Z7ZZESPPdcsfBoNLYJGAmXEExxw1QpjkSJfcd9kmtER7LkZ3RGbeXKHv1FR4hRBCD5wA8unY) funded with 5 million USDC each
- **October 11, 2022 10:25 PM UTC:** [MNGO-SOL Perp Sell Order placed by Wallet 1](https://trade.mango.markets/account?pubkey=CQvKSNnYtPTZfQRQ5jkHq8q2swJyRsdQLcFcj3EmKFfX) for 483 million $MNGO perpetual futures at 3.8 cents per future
- **October 11, 2022 10:25 PM UTC:** [MNGO-SOL Sell Order bought by Wallet 2](https://trade.mango.markets/account?pubkey=4ND8FVPjUGGjx9VuGFuJefDWpg3THb58c277hbVRnjNaa) which effectively opens up a MNGO long position for Wallet 2
- **October 11, 2022 10:26 PM UTC:** Hacker buys $1.44 Million MNGO on Mango Markets
- **October 11, 2022 10:27 PM UTC:** Hacker buys ~$1 Million MNGO on AscendEx
- **October 11, 2022 10:30 PM UTC:** Hacker buys $1.6 Million MNGO on FTX
- **October 11, 2022 10:45 PM UTC:** MNGO Price on Mango Markets reaches a peak of 91 cents, up from ~2 cents the day before.
- **October 11, 2022 10:45 PM UTC:** Hacker's Wallet 2 takes out a loan of $116 Million against it's unrealized profits from it's MNGO position

## Security Failure Causes

**Oracle vulnerability:** Mango Markets relied heavily on external price feeds to determine the amount of assets it could lend out to a user. These price feeds were easy to manipulate because there was not sufficient liquidity for the MNGO token. Although Mango Markets used a moving average of centralized exchange price feeds, it was not enough to prevent the oracle from being manipulated with a relatively low amount of capital.

**Protocol vulnerability:** Mango Markets had no measures in place to prevent wash trading, which allowed the hacker to take on an incredibly large $MNGO position in a short amount of time. Trade surveillance systems, would have detected unusual activity for a $MNGO position of that size, and could have alerted the protocol to watch for unusual activity.
