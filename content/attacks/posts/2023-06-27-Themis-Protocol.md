---
date: 2023-06-27
target-entities: Themis Protocol
entity-types:
  - DeFi
  - Lending Platform
attack-types:
  - Smart Contract Exploit
  - Flash Loan Attack
  - Price Oracle Manipulation
title: "Themis Protocol Suffers $370,000 Loss in Exploit"
loss: 370000
---

## Summary

On June 27, 2023, Themis Protocol, a decentralized lending and borrowing platform on the Arbitrum One chain, fell victim to a sophisticated exploit involving a flawed price oracle, leading to a loss of approximately $370,000. The attacker manipulated the Balancer LP token price by exchanging tokens within the Balancer pool, thus affecting the oracle's valuation of the pool's tokens. By utilizing flash loans and a series of calculated transactions, the exploiter was able to inflate the price of the Balancer LP tokens and borrow assets far exceeding their collateral, eventually laundering a portion of the stolen assets through Tornado Cash.

## Attackers

The identity of the attacker is unknown. The following addresses are associated with this attack:

- [0xdb73eb484e7dea3785520d750eabef50a9b9ab33](https://arbiscan.io/address/0xdb73eb484e7dea3785520d750eabef50a9b9ab33)

## Losses

Themis Protocol lost approximately $370,000 in total.

## Timeline

- **June 27, 2023, 06:33 PM UTC:** The [first malicious](https://arbiscan.io/tx/0xff368294ccb3cd6e7e263526b5c820b22dea2b2fd8617119ba5c3ab8417403d8) transaction occurred.
- **June 27, 2023, 08:30 PM UTC:** Themis Protocol [suspension of borrowing functions](https://twitter.com/ThemisProtocol/status/1673775788661800969).
- **June 27, 2023, 08:39 PM UTC:** PeckShield [published](https://twitter.com/peckshield/status/1673778002373509121?s=20) a report on the incident.
- **June 27, 2023, 10:32 AM UTC:** Themis Protocol [confirmed the hack](https://twitter.com/ThemisProtocol/status/1673806487540609024) and offered the hacker to return the funds.
- **July 27, 2023:** Themis Protocol [announced](https://blog.themis.exchange/themis-2-0-official-launch-and-compensation-plan-23209983ef16) Themis 2.0 and compensation details.

## Security Failure Causes

- **Price Oracle Vulnerability:** The root cause of the exploit is a weakness in the Balancer LP token price oracle. The attacker manipulated the LP token price by exchanging tokens within the Balancer pool, the price of which is determined by aggregating the total value of all tokens in the pool.
