---
date: 2021-02-13
categories: "DeFi"
title: "Dual Strike: Cream Finance and Alpha Finance Hit with $37.5 Million Flash Loan Attack Heist"
---

## Summary

On February 13, 2021, [Cream Finance fell victim to a highly sophisticated cyber-attack resulting in a loss of approximately $37.5 million](https://atozmarkets.com/news/cream-finance-defi-protocol-hacked-37-5-million-stolen/). The breach involved an intricate interplay between Cream Finance and another DeFi protocol, Alpha Homora, which is known for enabling users to leverage their positions across various DeFi platforms.

In a [detailed post-mortem analysis](https://blog.alphaventuredao.io/alpha-homora-v2-post-mortem/), Alpha Finance revealed that the assailant specifically exploited vulnerabilities in Alpha Homora V2, which is based on the Ethereum blockchain. The hacker executed over nine transactions employing flash loans

Leveraging the capabilities of flash loans, the attacker manipulated the price of assets and exploited the interdependencies between Cream Finance’s Iron Bank and Alpha Homora V2 to borrow sUSD, an asset pegged to the US dollar.

## Attackers

The identity of the attacker(s) is unknown.

ERC-20
- Alpha Homora V2 Exploiter: [0x905315602ed9a854e325f692ff82f58799beab57](https://etherscan.io/address/0x905315602ed9a854e325f692ff82f58799beab57)

## Losses

Approximately $37.5 million:

- 4,263,138 DAI
- 4,424,580 USDC
- 5,647,242 USDT
- 13,244 WETH (~23m USD)

## Timeline

- **February 13, 2021, 05:37 AM +UTC:** [Start of attack](https://etherscan.io/tx/0x2b419173c1f116e94e43afed15a46e3b3a109e118aba166fcca0ba583f686d23)
- **February 13, 2021, 09:51 AM +UTC:** [Cream Finance announces the hack](https://twitter.com/CreamdotFinance/status/1360537996995354625)
- **May 23, 2023:** [Iron Bank and Alpha Homora conflict continues](https://blog.alphaventuredao.io/iron-bank-and-alpha-homora-conflict-summarized/)

  
## Security Failure Causes

**[Several main reasons:](https://www.halborn.com/blog/post/explained-the-alpha-homora-defi-hack-feb-2021)**
- A rounding error in borrow code
- Allowance for the use of custom spells
- Public access to resolveReserve function
