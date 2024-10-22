---
date: 2024-01-30
target-entities: Abracadabra Money
entity-types:
  - DeFi
  - Lending Platform
attack-types:
  - Smart Contract Exploit
  - Flash Loan Attack
title: "Abracadabra Money Suffers $6.5 Million Loss Due to Smart Contract Exploit"
loss: 6500000
---

## Summary

Abracadabra Money, a prominent leverage and lending platform in the DeFi space, was exploited on January 30, 2024, due to a smart contract vulnerability on the Ethereum Mainnet. This exploit led to the unauthorized borrowing and subsequent theft of assets, totaling over $6.5 million, including 1800 ETH and 2.2 million MIM tokens. The attacker exploited the contract's inability to accurately track the real amount of debt due to rounding errors. He did this by taking a flash loan and repaying other users' debts, which, due to the precision loss, falsely adjusted the platform's total recorded debt. This manipulation created a situation where the attacker could repeatedly borrow tokens by exploiting the gap between the recorded debt (which was artificially reduced) and the actual amount. This exploit was possible because the contract did not adequately validate or limit user input and operations, allowing the attackers to execute a series of transactions that should not have been possible under normal conditions.

## Attackers

The attackers behind the Abracadabra Money hack remain unidentified.

Hacker ETH wallets:
- [0x87F585809Ce79aE39A5fa0C7C96d0d159eb678C9](https://etherscan.io/address/0x87F585809Ce79aE39A5fa0C7C96d0d159eb678C9)
- [0x40d5FFA20fC0dF6bE4D9991938dAa54E6919c714](https://etherscan.io/address/0x40d5FFA20fC0dF6bE4D9991938dAa54E6919c714)
- [0xbD12D6054827ae3fc6D23B1aCf47736691b52Fd3](https://etherscan.io/address/0xbD12D6054827ae3fc6D23B1aCf47736691b52Fd3)

## Losses

Abracadabra Money lost approximately $6.5 million:
- 1,800 ETH
- 2,200,000 MIM

## Timeline

- **January 30, 2024, 10:14:35 AM +UTC:** The [first malicious transaction](https://etherscan.io/tx/0x26a83db7e28838dd9fee6fb7314ae58dcc6aee9a20bf224c386ff5e80f7e4cf2) occurred.
- **January 30, 2024, 10:35 AM +UTC:** PeckShield [detected](https://twitter.com/peckshield/status/1752279373779194011) the attack.
- **January 30, 2024, 11:00 AM +UTC:** MIM token was [deppeged](https://twitter.com/PeckShieldAlert/status/1752287909917659356/photo/1).
- **January 30, 2024, 11:04 AM +UTC:** The Abracadabra Money team [reported](https://twitter.com/MIM_Spell/status/1752286636740579440) about the hack.
- **January 30, 2024, 04:24:23 PM +UTC:** The Abracadabra Money team has [sent an on-chain message](https://etherscan.io/tx/0xa1f8e3c30917f33956ef0a96417987a07a70509a2e48b6426b65906462faad6b) to the exploiter, an offer to return the stolen assets.
- **January 30, 2024, 04:29 PM +UTC:** The Abracadabra Money team [reported](https://twitter.com/MIM_Spell/status/1752368458715607261) mitigation and that the MIM token was pegged.
- **January 31, 2024:** Neptune Mutual [published](https://neptunemutual.com/blog/how-was-abracadabra-money-exploited) a detailed analysis of the incident.

## Security Failure Causes
- **Smart Contract Vulnerability:** The exploit was executed by manipulating rounding errors in the contract's debt recording mechanism, allowing unauthorized borrowing through flash loans.
