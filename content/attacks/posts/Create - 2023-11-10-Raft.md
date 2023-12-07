---
date: 2023-11-10  
target-entities: Raft 
entity-types: 
   - DeFi
attack-types: 
   - Exploit
title: “Raft’s exploited by $3.3M”
loss: 3000000
---

## Summary

Raft R, a decentralized finance (DeFi) platform, suffered a $3.3 million exploit that resulted in a 50% drop in the value of its R [stablecoin.](https://www.coindesk.com/tech/2023/11/10/defi-platform-raft-suffers-33m-exploit-but-hacker-likely-takes-a-loss-on-the-attack/) The attacker drained 1,577 ETH from Raft by [minting](https://www.coindesk.com/tech/2023/11/10/defi-platform-raft-suffers-33m-exploit-but-hacker-likely-takes-a-loss-on-the-attack/) R tokens. Raft's stablecoin later rebounded to around 70 [cents.](https://www.dimsumdaily.hk/raft-defi-platform-loses-us3-3-million-in-ether-hack-attacker-faces-loss/) Raft is working to compensate users using protocol-owned sDAI in the Peg [Stability](https://www.dimsumdaily.hk/raft-defi-platform-loses-us3-3-million-in-ether-hack-attacker-faces-loss) Module. Raft then released their post mortem report including the incident, root cause, audit status, post incident actions and their upcoming steps. According to the report, during the incident the attacker executed a series of actions, starting by [borrowing](https://etherscan.io/tx/0xfeedbf51b4e2338e38171f6e19501327294ab1907ab44cfd2d7e7336c975ace7) 6,000 cbETH from AAVE using a flash loan. They then transferred a total of 6,001 cbETH to the InterestRatePositionManager contract. Following this, the attacker [liquidated](https://etherscan.io/address/0x011992114806e2c3770df73fa0d19884215db85f) a pre-existing position on the InterestRatePositionManager contract. In a subsequent step, they set the index of the raft collateral indexable token to an extremely large value, 6,003,441,032,036,096,684,181, which corresponds to the cbETH balance of the InterestRatePositionManager contract. This balance was amplified over 1000 times due to the transaction in step 2. He then exploited the behavior of the divUp function by minting 1 wei share with only 1 wei cbETH. They repeated this process sixty times, acquiring 60 wei shares, equivalent to 10,050 cbETH. Subsequently, they redeemed 6,003 cbETH using only 90 wei rcbETH-c. The 6.7 million R tokens obtained were exchanged for 1,575 ETH (valued at $3.6 million) through various pools: R/sDAI on Balancer (2.1 million R for 2 million sDAI), R/DAI on Balancer (1.2 million R for 1.15 DAI), and R/USDC on Uniswap (200,000 R for 86,000 USDC). Finally, the individual burned 1,570 ETH in the process. The root cause was due to a precision calculation error during the minting of share tokens, allowing the attacker to acquire additional shares. By leveraging an amplified index value, the attacker increased the value of their shares, enabling them to redeem a small amount of rcbETH-c for a substantial quantity of cbETH. This, in turn, allowed them to borrow significant amounts of R tokens. Despite undergoing audits by Trail of Bits and Hats Finance, the Raft smart contracts were exploited due to vulnerabilities that were not identified in these audits. Following a security incident, a police report has been filed, and collaboration is underway with law enforcement, centralized exchanges, and other entities to identify the attacker. A detailed recovery plan is in progress to compensate affected users as fairly as possible. A public announcement advising Raft users to await updates on the recovery plan. As a precaution, all Raft smart contracts were temporarily paused Users who have minted R tokens, however, retain the ability to repay their positions and retrieve their collateral. 

## Attackers

The identity of the attacker is currently unknown.

## Losses

Raft R lost 1,577 [ETH](https://blockchain.news/news/defi-platform-raft-compromisedloses-33-million-in-ether) during the attack, worth 3,300,000 USD at the time of the attack.

## Timeline

   - **November 10, 2023, 19:18 UTC:** Raft posts a [tweet](https://twitter.com/raft_fi/status/1723057566664548623) stating they are investigating a prospective safety issue. 
   - **November 10, 2023, 19:49 UTC:** Raft co-funder David Garai confirmed in a post on X (formerly Twitter) that the platform was targeted by an [attack.](https://twitter.com/davgarai/status/1723065357445775507) 
   - **November 10, 2023, 20:20 UTC:** 0xngmi discusses the hacker's [losses](https://twitter.com/0xngmi/status/1723073285263380924)  
   - **November 10, 2023, 21:27 UTC:** Coindesk reports the [incident.](https://www.coindesk.com/tech/2023/11/10/defi-platform-raft-suffers-33m-exploit-but-hacker-likely-takes-a-loss-on-the-attack/)  
   - **November 11, 2023, 12:31 UTC:** Raft releases an X (formerly Twitter) statement [requesting](https://twitter.com/raft_fi/status/1723317259693940851) clients to wait for further updates on recovery plan. 
   - **November 13, 2023:** Raft posts their [Post](https://mirror.xyz/0xa486d3a7679D56D545dd5d357469Dd5ed4259340/_Nk6_1_VvInyC0pdvHiZuAXiqm6tYSsGYGHSfOhcO1I) Mortem report including the exploited [transactions,](https://etherscan.io/tx/0xfeedbf51b4e2338e38171f6e19501327294ab1907ab44cfd2d7e7336c975ace7) the exploiter [address,](https://etherscan.io/address/0xc1f2b71a502b551a65eee9c96318afdd5fd439fa) and the exploited [contract.](https://etherscan.io/address/0x9ab6b21cdf116f611110b048987e58894786c244)

## Security Failure Causes

   - **Inadequate Input Validation:** Failure to thoroughly validate and sanitize user inputs allowed the attacker to manipulate transactional data, leading to unauthorized operations and financial gains.
   - **Weak Access Controls::** The absence of proper authorization checks enabled the attacker to interact with critical functions, execute manipulative transactions, and gain unauthorized access to profit-generating functionalities.
   - **Flawed Authorization Mechanisms:** Insecure authorization practices allowed the attacker to execute actions beyond their intended scope, leading to the unauthorized extraction of profits.
   - **Insufficient Transaction Validation:** Insufficient validation of transactional integrity and parameters allowed the attacker to manipulate critical aspects of the smart contracts.
   - **Lack of Anti-Manipulation Safeguards:** The absence of anti-manipulation safeguards within the smart contracts contributed to the exploit. Effective security measures, such as tamper-resistant algorithms and integrity checks, were lacking, allowing the attacker to manipulate contract variables and exploit vulnerabilities for financial gain.
   - **Insecure Transaction Sequencing:** The attacker strategically manipulated the order of interactions to exploit vulnerabilities, underscoring the importance of secure transaction sequencing to prevent unauthorized financial gains.
   - **Insufficient Auditing and Monitoring:** Inadequate oversight and real-time monitoring allowed the attacker to go undetected during manipulative interactions, emphasizing the need for robust auditing practices in smart contract security.
