---
date: 2023-11-10  
target-entities: Raft 
entity-types: 
   - DeFi
attack-types: 
   - Exploit
title: “Raft’s Exploited by $3.3M”
loss: 3300000
---


## Summary

The Raft Protocol experienced an exploit resulting in a loss of 1577 ETH on the tenth of November. The exploiter employed a sophisticated [multistep attack](https://www.immunebytes.com/blog/raft-protocol-exploit-nov-10-2023-detailed-analysis/) strategy focusing on a smart contract's precision calculation vulnerability. Initially, they obtained cbETH through a flash loan from AAVE. Subsequently, the cbETH was donated and liquidated to the Interest Rate Position Manager, a maneuver that manipulated the collateral token's index rate. This set the stage for the exploiter to systematically increase their position in small increments, exploiting a rounding issue in the mint function. This strategy enabled repeated minting of cbETH, resulting in the unauthorized creation of approximately 6.003 quadrillion tokens. 

## Attackers

The identity of the attacker is unknown.

## Losses

Raft lost 1,577 [ETH](https://blockchain.news/news/defi-platform-raft-compromisedloses-33-million-in-ether) during the attack, worth approximately $3.3 million.

## Timeline

   - **"November 10, 2023, 19:18 UTC:"** Raft announced via [X](https://twitter.com/raft_fi/status/1723057566664548623) their initiation of an investigation into a potential security issue.
   - **"November 10, 2023, 19:49 UTC:"** David Garai, co-founder of Raft, confirms in a post on [X](https://twitter.com/davgarai/status/1723065357445775507) that the platform was targeted by an attack. 
   - **"November 10, 2023, 20:20 UTC:"** 0xngmi discusses the attacker's losses in an [X](https://twitter.com/0xngmi/status/1723073285263380924) post.
   - **"November 10, 2023, 21:27 UTC:"** CoinDesk reported on the incident.
   - **"November 11, 2023, 12:31 UTC:"** Raft announces the temporary suspension of smart contracts as a precautionary measure via an [X](https://twitter.com/raft_fi/status/1723317259693940851) post.
   - **"November 13, 2023:"** Raft posts their [post-mortem](https://mirror.xyz/0xa486d3a7679D56D545dd5d357469Dd5ed4259340/_Nk6_1_VvInyC0pdvHiZuAXiqm6tYSsGYGHSfOhcO1I) report including the exploited [transactions,](https://etherscan.io/tx/0xfeedbf51b4e2338e38171f6e19501327294ab1907ab44cfd2d7e7336c975ace7) the exploiter [address,](https://etherscan.io/address/0xc1f2b71a502b551a65eee9c96318afdd5fd439fa) and the exploited [contract.](https://etherscan.io/address/0xc1f2b71a502b551a65eee9c96318afdd5fd439fa) 

## Security Failure Causes

**Flawed Contract Logic:** The smart contract's inability to handle precise calculations led to the exploitation of the minting process, demonstrating the necessity of rigorous logical verification in contract development.
**Inadequate Testing for Edge Cases:** The exploit capitalized on rounding errors within the mint function, underscoring the importance of extensive testing for edge cases in smart contract functionalities.
**Manipulation of Contract Parameters:** By adjusting the collateral token's index rate, the attacker highlighted the risk of allowing external influences to alter key contract parameters.
**Exploitation of Integration Points:** Using a flash loan from AAVE, the attacker obtained cbETH, and then manipulated these tokens within Raft's ecosystem, showcasing the vulnerabilities at integration points between different DeFi protocols.
