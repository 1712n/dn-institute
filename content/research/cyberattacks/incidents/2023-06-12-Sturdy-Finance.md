---
date: 2023-06-12
target-entities: Sturdy Finance
entity-types:
- DeFi
- Lending Platform
attack-types:
- Flash Loan Attack
- Smart Contract Exploit
title: "Sturdy Finance Loses $800K to DeFi Exploit"
loss: 800000
---

## Summary

On June 12, 2023, Sturdy Finance, a DeFi protocol on the Ethereum blockchain known for its lending and borrowing services, was compromised in a security breach. Attackers exploited a vulnerability in the protocol's price oracle, combined with a read-only reentrancy flaw, orchestrating a theft of approximately $800,000.

## Attackers

The identity of the hackers who attacked Multichain is unknown.

Hacker Ethereum Wallet:

[0x1E8419E724d51E87f78E222D935fbbdeb631a08B](https://etherscan.io/address/0x1E8419E724d51E87f78E222D935fbbdeb631a08B)

## Losses

- [442 ETH (800,000 USD)](https://phalcon.blocksec.com/explorer/tx/eth/0xeb87ebc0a18aca7d2a9ffcabf61aa69c9e8d3c6efade9e2303f8857717fb9eb7)

## Timeline

- **June 12, 2023, 01:06:35 AM UTC:** The malicious transaction [occurred](https://etherscan.io/tx/0xeb87ebc0a18aca7d2a9ffcabf61aa69c9e8d3c6efade9e2303f8857717fb9eb7).
- **June 12, 2023, 01:08:23 AM UTC:** The attacker began [sending](https://etherscan.io/tx/0x1702e647da897a35b59304bde5e62b4e6ad8d5148905b4627398bd30c42ee1a7) stolen funds to Tornado Cash.
- **June 12, 2023, 09:19 AM UTC:** Sturdy Finance team [announced](https://twitter.com/SturdyFinance/status/1668080627030315009) about the hack.
- **June 12, 2023, 08:25:35 PM UTC:** Sturdy Finance [communicated with the hacker](https://etherscan.io/tx/0xda7fda2146ec0cc6f22920451978b41f9a9ae7f01ce6e4878b454eb2efdc9fec), proposing a deal to recover the stolen assets in exchange for a $100,000 reward, alongside a promise of no legal action.
- **June 20, 2023:** Immunebytes [published](https://www.immunebytes.com/blog/sturdy-finance-hack-june-12-2023-detailed-analysis/#Hack_Aftermath) a detailed analysis of the incident.
- **July 1, 2023:** Sturdy Finance [published](https://sturdyfinance.medium.com/exploit-post-mortem-49261493307a) exploit Post-Mortem.

## Security Failure Causes

- **Smart Contract Vulnerability**: The initial vulnerability that enabled the hack was a read-only reentrancy flaw within the smart contract system. This vulnerability allowed attackers to re-enter certain functions within the contract without proper access control or limitations, enabling them to exploit the contract's functions maliciously.
- **Flash Loans Exploitation:** The attackers initiated their scheme by obtaining a significant flash loan, a large amount of cryptocurrency borrowed and repaid within a single transaction. This loan provided the capital to manipulate market conditions in their favor without requiring any collateral, exploiting the protocol's mechanisms for borrowing and lending.
- **Price Oracle Manipulation**: Central to the attack was the manipulation of a faulty price oracle related to the Balancer’s B-stETH-STABLE pool. By artificially inflating the price of the sBTC-WBTC liquidity provider tokens, the attackers deceived the protocol into misvaluing the collateral, allowing them to borrow against an inflated collateral value and subsequently extract profits by reversing the manipulation, thus exploiting the discrepancy between the manipulated and actual market values.
