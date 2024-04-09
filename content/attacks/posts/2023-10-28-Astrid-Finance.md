---
date: 2023-10-28
target-entities: Astrid Finance
entity-types: DeFi
attack-types: Smart Contract Exploit
title: "Astrid Finance Suffers $228,000 Loss in Smart Contract Exploit"
loss: 228000
---

## Summary

Astrid Finance, an Ethereum-based liquid restaking pool powered by the Eigen Layer, suffered a significant exploit on October 28, 2023, leading to a loss of $228,000. The exploit was executed through a smart contract vulnerability linked to insufficient input validation, specifically within the withdraw function of the protocol. This flaw enabled the attacker to manipulate transaction parameters, allowing the creation and utilization of fake tokens to illegitimately withdraw funds. The breach resulted in the unauthorized extraction of various staked tokens, including stETH, rETH, and cbETH, which were then converted into 127 ETH. Astrid Finance's team has acknowledged the incident, paused the implicated contracts, and initiated a refund process for affected users, while also offering a bounty for the return of the stolen funds.

## Attackers

The identity of the attacker is unknown.

Hacker Ethereum Wallet:

- [0x792ec27874e1f614e757a1ae49d00ef5b2c73959](https://etherscan.io/address/0x792ec27874e1f614e757a1ae49d00ef5b2c73959)

## Losses

Astrid Finance lost approximately $228,000:

- 64.17 stETH (114,757 USD)
- 39.16 rETH (76,328 USD)
- 20 cbETH (37,637 USD)

## Timeline

- **October 28, 2023, 10:41 AM UTC:** The [first malicious](https://etherscan.io/tx/0x8af9b5fb3e2e3df8659ffb2e0f0c1f4c90d5a80f4f6fccef143b823ce673fb60) transaction occurred.
- **October 28, 2023, 02:13 PM UTC:** Astrid Finance team [reported](https://twitter.com/AstridFinance/status/1718254655288066501) about the exploit.
- **October 28, 2023, 02:51 PM UTC:** Astrid Finance team sent an [on-chain message](https://etherscan.io/tx/0xa56fdb1fc7c192b23cda44901d2871289cf28831cb94ccc731d089d4fb593793) to the hacker offering a bounty of 20% of the stolen funds.
- **October 28, 2023, 07:22 PM UTC:** The team confirmed that they have [returned funds](https://twitter.com/AstridFinance/status/1718332313380303195) to affected users. 
- **October 29, 2023, 09:08 AM UTC:** Hacker [returned](https://etherscan.io/tx/0x27cbd5f2f12067bcc9be3bafa9140b849ee1ee68ae5329c2a4ba789685111ad7) 80% of the stolen assets.

## Security Failure Causes

- **Smart Contract Vulnerability:** The core of the exploit was a critical oversight in the smart contract's input validation process, particularly in the withdraw function. This loophole allowed for the manipulation of parameters and the unauthorized withdrawal of funds.
