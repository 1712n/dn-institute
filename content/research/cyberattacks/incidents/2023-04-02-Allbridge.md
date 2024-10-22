---
date: 2023-04-02
target-entities:
  - Allbridge
entity-types:
  - DeFi
  - Bridge
attack-types:
  - Smart Contract Exploit
  - Flash Loan Attack
title: "Allbridge suffered a flash loan attack for $573k"
loss: 573000
---

## Summary

On April 2, 2023, AllBridge, a multichain token bridge, fell victim to an exploit that resulted in approximately $573,000 worth of assets being drained from its BNB Chain pools. The attacker, acting as both a liquidity provider and a swapper, exploited a flaw in a smart contract that enabled them to manipulate swap prices. This led to the theft of $282,889 in Binance USD (BUSD) and $290,868 in Tether (USDT).

## Attackers

The identity of the attacker is unknown.

BSC:

- [0xC578d755Cd56255d3fF6E92E1B6371bA945e3984](https://bscscan.com/address/0xc578d755cd56255d3ff6e92e1b6371ba945e3984)
- [0x2b3cff12c02625518deb0af14684999fb6e3e360](https://bscscan.com/address/0x2b3cff12c02625518deb0af14684999fb6e3e360)

[source](https://medium.com/coinmonks/decoding-allbridge-570k-flash-loan-exploit-quillaudits-8da8dccd729d)

## Losses

- $573,000

## Timeline

- **April 2, 2023:** The Allbridge exploit [occurs](https://bscscan.com/tx/0x7ff1364c3b3b296b411965339ed956da5d17058f3164425ce800d64f1aef8210). The bridge is promptly [shut down](https://twitter.com/Allbridge_io/status/1642508296157290498) to prevent further attacks on other pools.
- **April 3, 2023, 07:13:26 PM +UTC:** The team [sends](https://bscscan.com/tx/0x1351ba22ca16b4fe076f7a8f73ab6dda052c63ba08a79b28b71badc6a6de3074) on-chain message to attackers, offering a white hat bounty for the return of the stolen assets and promising not to pursue legal action if the funds were returned.
- **April 3, 2023, 04:07:52 PM +UTC** The attacker [returns](https://bscscan.com/tx/0xb0323e5461e4cfc8e4c259f0b343ed17709c64474fd5615659164459dd76c15b) around 1500 BNB ($466,144) to the project
- **April 5, 2023:** A significant amount of BNB, approximately 507.3 BNB worth about $159K, is transferred from an address labeled as Allbridge Exploiter to Tornado Cash.

## Security Failure Causes

- **Smart Contract Vulnerability:** The root cause of the exploit was a flaw in the withdraw function of the smart contract. This flaw allowed the attacker to manipulate the swap price in the liquidity pool to their advantage.
