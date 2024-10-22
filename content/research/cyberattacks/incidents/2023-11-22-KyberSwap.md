---
date: 2023-11-22
target-entities: KyberSwap
entity-types: 
   - DeFi
   - Exchange
attack-types:
   - Smart Contract Exploit 
   - Reentrancy Attack
title: "KyberSwap Loses $49,000,000 During Cyberattack"
loss: 49000000
---

## Summary

On November 22, 2023, KyberSwap, a decentralized finance platform, experienced a sophisticated exploit resulting in a loss of approximately [$49,000,000.](https://hacken.io/insights/kyberswap-hack-explained/) The attack involved manipulating the platform's smart contract through complex transactions. The attacker used flash loans to manipulate token prices, which enabled them to exploit a numerical anomaly in the smart contract. This allowed the attacker to double-count liquidity and withdraw substantial funds. Despite KyberSwap having failsafe mechanisms, the attacker skillfully avoided triggering these protections.  

## Attackers

The perpetrator has yet to be identified. The following addresses were used in the attack: 
   - [0x50275e0b7261559ce1644014d4b78d4aa63be836](https://etherscan.io/address/0x50275e0b7261559ce1644014d4b78d4aa63be836)
   - [0xc9b826bad20872eb29f9b1d8af4befe8460b50c6](https://etherscan.io/address/0xc9b826bad20872eb29f9b1d8af4befe8460b50c6)

## Timeline

- **November 22, 2023, 12:21 PM UTC:** Initial transactions [occur.](https://etherscan.io/tx/0x72aa08eab1ee164df0976a23c6fd911f4010e892e4d9f6c72b6ce6f42aeb160c)  
- **November 22, 2023, 11:52 PM UTC:** KyberSwap Network announces the hack and encourages customers to [withdraw](https://twitter.com/KyberNetwork/status/1727475235342217682) their funds in a post on X.
- **November 22, 2023, 11:57 PM UTC:** Communication between KyperSwap and the attacker begin on [Blockchain](https://etherscan.io/idm?addresses=0x8180a5ca4e3b94045e05a9313777955f7518d757,0x50275e0b7261559ce1644014d4b78d4aa63be836&type=1) regarding future negotiations. 
- **November 26, 2023, 03:38 PM UTC:** KyberSwap announces on X they have been in [contact](https://twitter.com/KyberNetwork/status/1728800315955437743) with the owners of the front-run bots that extracted the funds on Polygon and Avalanche during the attack and have negotiated a return of 90% of the exploited $5.7 million connected to the two companies in return of a 10% bounty. KyberSwap provides an [address](https://etherscan.io/address/0x8180a5ca4e3b94045e05a9313777955f7518d757) for the return of the stolen funds.
- **“November 30, 2023:”** The attacker demands full control over Kyber Network's [entire asset portfolio](https://cointelegraph.com/news/kyberswap-hacker-demands-complete-control-over-kyber-company) with a December 10, 2023, deadline.
- **December 27, 2023, 04:06 PM UTC:** KyperSwap announces reimbursement plan and the termination of [half](https://blockchain.news/news/kyberswaps-response-to-488-million-hack-workforce-halved-and-victim-reimbursement-plans) of their workforce.

## Losses

Before the partial recovery, KyberSwap losses are approximately $49,000,000.

## Security Failure Causes

   - **Reentrancy Vulnerability:** This is a common smart contract issue where a function can be repeatedly called before the first execution is completed, leading to unexpected behaviors or manipulation.
   - **Inadequate Auditing:** The lack of thorough and continuous auditing of smart contracts, especially during updates or new implementations, can leave undetected vulnerabilities.
   - **Insufficient Real-Time Monitoring:** Not having systems in place to monitor and quickly respond to suspicious activities can exacerbate the impact of an attack.
