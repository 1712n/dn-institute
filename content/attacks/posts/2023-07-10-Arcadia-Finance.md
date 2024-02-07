---
date: 2023-07-10
target-entities: Arcadia Finance
entity-types:
  - DeFi
attack-types:
  - Smart Contract Exploit
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

The total loss from the Acradia Finance hack amounted to approximately $455,00, distributed across the following networks:

- [Ethereum](https://phalcon.blocksec.com/explorer/tx/eth/0xefc4ac015069fdf9946997be0459db44c0491221159220be782454c32ec2d651):
   - 148 ETH (275,843 USD)
   - 103,200 USDC

- [Optimism](https://phalcon.blocksec.com/explorer/tx/optimism/0xca7c1a0fde444e1a68a8c2b8ae3fb76ec384d1f7ae9a50d26f8bfdd37c7a0afe):
   - 59,427 USDC
   - 11 ETH (20,558 USD)

## Timeline

- **2023-07-10, 01:16:07 AM UTC:** The [first malicious transaction occurred](https://optimistic.etherscan.io/tx/0xca7c1a0fde444e1a68a8c2b8ae3fb76ec384d1f7ae9a50d26f8bfdd37c7a0afe).
- **2023-07-10, 01:21:59 AM UTC:** A [second malicious transaction occurred](https://etherscan.io/tx/0xefc4ac015069fdf9946997be0459db44c0491221159220be782454c32ec2d651).
- **2023-07-10, 10:42 AM UTC:** Suspicious transactions were detected by [PeckShield](https://twitter.com/PeckShieldAlert/status/1678248292327763968)   
- **2023-07-10, 01:10 PM UTC:** The Arcadia Finance team [announced](https://twitter.com/ArcadiaFi/status/1678285634727706625) the hack on Twitter.
- **2023-07-10:** Immunebytes [published](https://www.immunebytes.com/blog/arcadia-finance-exploit-detailed-hack-analysis/) a detailed analysis of the incident.
- **2023-07-10:** Arcadia Finance [published exploit Post-Mortem](https://arcadiafinance.medium.com/post-mortem-72e9d24a79b0)

## Security Failure Causes

**Smart contract vulnerability:** Smart contract vulnerability: The security breach at ArcadiaFi was primarily due to vulnerabilities in the "vaultManagementAction" and "liquidateVault" functions of its smart contracts, compounded by insufficient reentrancy protection and flawed validation of untrusted inputs. The attacker exploited the lack of access control in the "vaultManagementAction" function to divert assets to a controlled contract and manipulated the "liquidateVault" function by bypassing collateral health checks through the manipulation of global variables. This was further aggravated by the abuse of the "executeAction" function, which lacked input validation and reentrancy guards, allowing unauthorized transactions and the draining of funds from the vaults.
