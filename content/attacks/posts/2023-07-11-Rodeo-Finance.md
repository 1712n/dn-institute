---
date: 2023-07-11
target-entities: Rodeo Finance
entity-types:
  - DeFi
  - Yield Aggregator
  - Lending Platform
attack-types:
  - Smart Contract Exploit
  - Flash Loan Attack
title: "Rodeo Finance Exploit on Arbitrum Leads to $888,000 Loss"
loss: 880000
---

## Summary

On July 11, 2023, Rodeo Finance on Arbitrum was breached, losing around 472 ETH ($888,000) due to an attacker exploiting the [TWAP Oracle](https://www.halborn.com/blog/post/what-are-twap-oracles). By manipulating the oracle's price calculation,  through a "sandwich" attack, they inflated asset prices. This allowed them to mislead the protocol, borrow against the inflated prices from the USDC Pool, and conduct swaps to profit from the manipulated price discrepancies, effectively bypassing Rodeo's security checks.

## Attackers

The identity of the attacker is unknown.

Hacker Arbitrum Wallet:

- [0x2f3788f2396127061c46fc07bd0fcb91faace328](https://arbiscan.io/address/0x2f3788f2396127061c46fc07bd0fcb91faace328)

## Losses

The loss amounted to 472 ETH worth $880,000.

## Timeline

- **July 11, 2023, 07:54:08 AM +UTC:** The [first malicious](https://arbiscan.io/tx/0x98f1e234faac8b7f7ceaffe4e8e0581038678d95710b646db45ec3de47e6c3af) transaction occurred.
- **July 11, 2023, 05:26:23 PM +UTC:** Rodeo Finance sent an [on-chain message](https://etherscan.io/tx/0x3045cd1d7314400ba5eac173a1f7348cebe5bdc6145a212524a85df6d6fd59ed) to the attacker to negotiate the return of the stolen funds.
- **July 11, 2023, 04:05 PM +UTC:** Rodeo Finance [reported](https://twitter.com/Rodeo_Finance/status/1678782465421213697) about the exploit.
- **July 12, 2023:** Rodeo Finance [published](https://medium.com/@Rodeo_Finance/rodeo-post-mortem-overview-f35635c14101) an exploit Post-Mortem.

## Security Failure Causes

- **Smart Contract Vulnerability:** The breach was primarily enabled by the exploitation of TWAP Oracle's pricing mechanism, which led to manipulated asset prices.
- **Flash Loans Exploitation:** The exploit leveraged flash loans, which allow borrowing large sums without collateral, for price manipulation and creating strain on the system.
- **Price Oracle Manipulation:** The attackers manipulated price oracles, leading the protocol to make decisions based on incorrect asset prices.
