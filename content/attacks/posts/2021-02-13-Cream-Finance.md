---
date: 2021-02-13
categories: "DeFi"
title: "Cream Finance Hack: $37.5 Million Stolen in Flash Loan Attack"
---

## Summary

On February 13, 2021, [Cream Finance, a decentralized finance (DeFi) protocol, was hacked for $37.5 million](https://atozmarkets.com/news/cream-finance-defi-protocol-hacked-37-5-million-stolen/).

Alpha Finance released a [report](https://blog.alphaventuredao.io/alpha-homora-v2-post-mortem/) following the attack, which revealed that the exploit specifically targeted their Ethereum-based protocol, Alpha Homora V2. This protocol is designed for users to leverage their positions in yield farming pools. The attacker was highly sophisticated, making more than nine transactions that involved flash loans, and utilized the Alpha Homora V2 protocol to borrow sUSD from Cream’s Iron Bank.

## Attackers

The identity of the attacker(s) is unknown.

ERC-20
- Alpha Homora V2 Exploiter: [0x905315602ed9a854e325f692ff82f58799beab57](https://etherscan.io/address/0x905315602ed9a854e325f692ff82f58799beab57)

## Losses

Approximately $37.5 million:

- ~4,263,138 DAI
- ~4,424,580 USDC
- ~5,647,242 USDT
- ~13,244 WETH

## Timeline

- **February 13, 2021, 05:37 AM +UTC:** [Start of attack](https://etherscan.io/tx/0x2b419173c1f116e94e43afed15a46e3b3a109e118aba166fcca0ba583f686d23)
- **February 13, 2021, 09:51 AM +UTC:** [Cream Finance announces the hack](https://twitter.com/CreamdotFinance/status/1360537996995354625)
- **May 23, 2023:** [Iron Bank and Alpha Homora conflict continues](https://blog.alphaventuredao.io/iron-bank-and-alpha-homora-conflict-summarized/)

  
## Security Failure Causes

**[Several main reasons:](https://www.halborn.com/blog/post/explained-the-alpha-homora-defi-hack-feb-2021)**
- A rounding error in borrow code
- Allowance for the use of custom spells
- Public access to resolveReserve function
