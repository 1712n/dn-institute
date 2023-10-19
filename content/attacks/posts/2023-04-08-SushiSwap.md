---
date: 2023-04-08
target-entities:
  - SushiSwap
entity-types:
  - DeFi
  - Exchange
attack-types:
  - Smart Contract Exploit
title: "SushiSwap Drained of 1800 WETH Due to RouteProcessor2 Contract Vulnerability"
loss: 3300000
---

## Summary

On April 8, 2023, SushiSwap, a renowned decentralized exchange, came under attack due to a vulnerability in its newly launched [RouteProcessor2](https://etherscan.io/address/0x044b75f554b886a065b9567891e45c79542d7357#code) contract. The contract was part of the SushiSwap's version 3 (V3) upgrades and was deployed on 14 different networks. Before SushiSwap could react, anonymous attackers exploited the vulnerability and managed to drain approximately 1800 Wrapped Ether (WETH) from user wallets.

## Attackers

The identity of the attacker is unknown.

- [0x8AC0B9656b7c39be0d3D73828D2041E8C0e27712](https://etherscan.io/address/0x8ac0b9656b7c39be0d3d73828d2041e8c0e27712)

## Losses

- 1800 WETH [($3.3 million)](https://twitter.com/peckshield/status/1644907207530774530)

## Timeline

- **April 8, 2023:** SushiSwap soft launches V3 upgrades including the RouteProcessor2 contract.
- **April 8, 2023:** HYDN’s security team identifies a critical vulnerability in the RouteProcessor2 contract and raises the issue with SushiSwap’s core contributors.
- **April 8, 2023:** SushiSwap rolls back UI upgrades to prevent further token approvals on the vulnerable contract.
- **April 8, 2023:** A bounty hunter attempts a white-hat hack to rescue 100 WETH but fails as malicious actors discover the vulnerability through MEV bots and begin the attack.
- **April 8, 2023:** SushiSwap gives the green light for HYDN to start a white-hat rescue.
- **April 26, 2023:** SushiSwap releases a claim portal for users to claim their lost tokens.

## Security Failure Causes

Several reasons according to the SushiSwap [post-mortem](https://www.sushi.com/blog/routeprocessor2-post-mortem) report:

- **Lack of Contract Pausability:** The contract did not include a pausability feature, which would have allowed for temporary halting in case of issues, mitigating risks.
- **Use of Unlimited Approvals:** The contract allowed unlimited token approvals, which is outdated and risky. Adopting one-time approvals per transaction would have been safer.
- **Hasty Auditing Process:** The contract was rushed through auditing, not giving auditors enough time for thorough analysis, leading to overlooked vulnerabilities.
- **Suboptimal Rollout Procedures:** The new contract rollout process was not robust enough. Including contracts in Immunefi's scope list prior to deployment would have allowed for early vulnerability detection and responsible reporting by whitehats.
