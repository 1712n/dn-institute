---
date: 2021-02-13
target-entities:
  - Alpha Homora
  - Iron Bank
entity-types:
  - DeFi
  - Yield Aggregator
attack-types:
  - Smart Contract Exploit
  - Flash Loan Attack
title: "Alpha Finance suffered a Flash Loan Attack: $37.5 Million Exploited"
loss: 37500000
---

## Summary

On February 13, 2021, Alpha Finance, a DeFi project, suffered a hack that resulted in a $37.5 million loss. The attacker exploited a rounding error in the repayment process, accumulating a substantial amount of cySUSD. They used this to obtain loans in different assets and distributed the stolen Ether. Iron Bank responded by modifying the smart contract configuration, freezing funds and preventing lenders on Alpha Homora from withdrawing their liquidity. Depositors ceased negotiations, received goodwill funds from Alpha Homora, and are pursuing legal action against Iron Bank.

## Attackers

The identity of the attackers remains unknown. The attack was performed using the [address](https://twitter.com/josebaredes/status/1360476183373242370) [0x905315602Ed9a854e325F692FF82F58799BEaB57](https://etherscan.io/address/0x905315602ed9a854e325f692ff82f58799beab57).

## Losses

The Alpha Finance DeFi hack resulted in [financial losses](https://cryptobriefing.com/alpha-finance-suffers-37-5-million-loss-major-attack/), with $37.5 million extracted from the project. The stolen funds were distributed among various destinations as follows:

- Iron Bank: 1,000 ETH
- Alpha Homora: 1,000 ETH
- Tornado.cash: 320 ETH
- Attacker's wallet: 10,925 ETH (worth roughly $20 million)

## Timeline

- **February 13, 2021 05:37 AM +UTC:**
  The [attacker](https://etherscan.io/address/0x905315602ed9a854e325f692ff82f58799beab57) borrowed [1,000e^(18)](https://www.quadrigainitiative.com/casestudy/alphahomorahack.php) sUSD from HomoraBankv2, utilizing UNI-WETH LP as collateral. During repayment, the attacker exploited a [rounding error](https://www.halborn.com/blog/post/explained-the-alpha-homora-defi-hack-feb-2021) in the protocol, paying slightly less than the owed amount.
- **February 13, 2021, 09:51 AM +UTC:** Cream Finance made an announcement regarding the [hack](https://twitter.com/CreamdotFinance/status/1360537996995354625).
- **February 13, 2021, 10:33 PM +UTC:**
  Alpha Finance promptly [responded to the hack](https://twitter.com/stellaxyz_/status/1360673348590530562) by fixing security issues, implementing restrictions, and [limiting token options](https://blog.alphaventuredao.io/alpha-homora-v2-post-mortem/).
- **February 21, 2021, 02:48:54 AM +UTC:**
  An [agreement](https://etherscan.io/address/0x141e0541d87c6cbdbf2a6a8104248b4b922f629e) is reached between Alpha Homora V2 (Alpha Finance Lab) and CREAM V2 (CREAM) regarding the amount of funds and repayment mechanics.
- **March 1, 2023, 12:54:47 PM +UTC:**
  Iron Bank (IB) unilaterally [modified](https://etherscan.io/tx/0xe5e0497f736c61521dda09b2230283f1ad6dafcf2f088ec9065a19b579fb4bc5) the smart contract configuration, freezing Alpha Homora (AH) lenders' funds.
- **May 23, 2023:**
  Depositors plan to stop negotiating, accept goodwill funds, and take [legal action](https://blog.alphaventuredao.io/iron-bank-and-alpha-homora-conflict-summarized/) against IB.

## Security Failure Causes

- **Loophole in Custom Functionality:** The Alpha Homora v2 contract had a vulnerability that allowed the use of custom functionality without adequate checks, creating an opportunity for the attacker to exploit the system.
- **Rounding Error Exploitation:** The attacker took advantage of a rounding error in the protocol during repayment, resulting in a manipulated debt and borrow share.
- **Insufficient Validation and Access Controls:** The lack of strict validation checks and access controls for custom functionality and critical functions allowed unauthorized manipulation of the protocol.
