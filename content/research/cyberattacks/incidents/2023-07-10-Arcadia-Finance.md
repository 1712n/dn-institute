---
date: 2023-07-10
target-entities: Arcadia Finance
entity-types:
  - DeFi
  - Lending Platform
attack-types:
  - Smart Contract Exploit
  - Reentrancy Attack
title: "Arcadia Finance Suffers $455,000 Security Breach"
loss: 455000
---

## Summary

On July 10, 2023, Arcadia Finance, a DeFi protocol on Ethereum and Optimism, experienced a significant security breach due to vulnerabilities in its smart contract. The incident resulted in a financial loss of approximately $455,000. The breach was due to inadequate security measures in the protocol's contract, allowing an attacker to manipulate the system for unauthorized asset transfers.

## Attackers

The identity of the hackers who attacked Arcadia Finance is unknown.

Hacker Wallets:

- [0xd3641c912a6a4c30338787e3c464420b561a9467](https://optimistic.etherscan.io/address/0xd3641c912a6a4c30338787e3c464420b561a9467)
- [0x5c75e94dd0ab9c10bfd1b8073dafef031d3c050d](https://etherscan.io/address/0x5c75e94dd0ab9c10bfd1b8073dafef031d3c050d)

## Losses

The total loss from the Arcadia Finance hack amounted to approximately $455,000, distributed across the following networks:

- Ethereum:
   - 148 ETH (275,843 USD)
   - 103,200 USDC

- Optimism:
   - 59,427 USDC
   - 11 ETH (20,558 USD)

## Timeline

- **July 10, 2023, 01:16:07 AM UTC:** The [first malicious transaction occurred](https://optimistic.etherscan.io/tx/0xca7c1a0fde444e1a68a8c2b8ae3fb76ec384d1f7ae9a50d26f8bfdd37c7a0afe).
- **July 10, 2023, 01:21:59 AM UTC:** A [second malicious transaction occurred](https://etherscan.io/tx/0xefc4ac015069fdf9946997be0459db44c0491221159220be782454c32ec2d651).
- **July 10, 2023, 04:42 AM UTC:** Suspicious transactions were detected by [PeckShield](https://twitter.com/PeckShieldAlert/status/1678248292327763968)   
- **July 10, 2023, 07:10 AM UTC:** The Arcadia Finance team [announced](https://twitter.com/ArcadiaFi/status/1678285634727706625) the hack on Twitter.
- **July 10, 2023:** Immunebytes [published](https://www.immunebytes.com/blog/arcadia-finance-exploit-detailed-hack-analysis/) a detailed analysis of the incident. Arcadia Finance [published exploit Post-Mortem](https://arcadiafinance.medium.com/post-mortem-72e9d24a79b0).
- **July 25, 2023:** Arcadia is [pausing](https://arcadiafinance.medium.com/sunsetting-arcadia-v1-89a5d03bd8cc) actions to focus on user fund recovery and transitioning to a more secure Arcadia V2.
- **October 18, 2023:** Arcadia [presented](https://arcadiafinance.medium.com/introducing-arcadia-v2-79ee345af20b) version 2 of the protocol.

## Security Failure Causes

- **Smart Contract Vulnerability:** The Arcadia Finance hack was caused by vulnerabilities in its smart contracts, particularly in functions related to vault management and liquidation. These issues were exacerbated by inadequate reentrancy protection and poor validation of external inputs. The attacker bypassed security checks to redirect assets and execute unauthorized transactions, resulting in significant fund loss.
