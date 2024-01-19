---
date: 2023-11-22
target-entities: KyberSwap Elastics
entity-types: 
   - DeFi
   - Exchange
attack-types: 
   - Smart Contract Exploit 
title: KyberSwap loses $49,000,000 during cyberattack
loss: 49000000
---

## Summary

On November 22, 2023, KyberSwap, a decentralized finance platform, experienced a sophisticated exploit resulting in a loss of approximately [$49,000,000.](https://hacken.io/insights/kyberswap-hack-explained/) The attack involved manipulating the platform's smart contract through complex transactions. The attacker used flash loans to manipulate token prices, which enabled them to exploit a numerical anomaly in the smart contract. This allowed the attacker to double-count liquidity and withdraw substantial funds. Despite KyberSwap having failsafe mechanisms, the attacker skillfully avoided triggering these protections.  

## Attackers

The perpetrator has yet to be identified by law enforcement but has the public tag “KyberSwap Exploiter 1” on Etherscan. 

The following address was used in the attack: 0xc9b826bad20872eb29f9b1d8af4befe8460b50c6

## Timeline

- **November 22, 2023, 12:21 PM UTC:** Initial transactions [occur.](https://etherscan.io/txs)  
- **November 22, 2023, 11:52 PM UTC:** KyberSwap Network announces the hack and encourages customers to [withdraw](https://twitter.com/KyberNetwork/status/1727475235342217682) their funds in a post on X.
- **November 22, 2023, 11:57 PM UTC:** Communication between KyperSwap and the attacker begin on [Blockchain](https://etherscan.io/idm) regarding future negotiations. 
- **November 26, 2023, 03:38 PM UTC:** KyberSwap announces on X they have been in [contact](https://twitter.com/KyberNetwork/status/1728800315955437743) with the owners of the front-run bots that extracted the funds on Polygon and Avalanche during the attack and have negotiated a return of 90% of the exploited $5.7 million connected to the two companies in return of a 10% bounty. KyberSwap connects [address](https://polygonscan.com/tx/0x8a0880f1662e39fa838e89fa751669e4a1eee5c15586dc447453274f7b8ce746) for the return of the stolen funds. 
- **“November 30, 2023:”** The attacker exerts pressure to gain comprehensive dominion over Kyber Network's [entire asset portfolio](https://cointelegraph.com/news/kyberswap-hacker-demands-complete-control-over-kyber-company) with a December 10, 2023, deadline.
- **December 27, 2023, 04:06 PM UTC:** KyperSwap announces reimbursement plan and the termination of [half](https://blockchain.news/news/kyberswaps-response-to-488-million-hack-workforce-halved-and-victim-reimbursement-plans) of their workforce.

## Losses

KyberSwap losses are approximately $49,000,000.

## Security Failure Causes

   - **Specific Targeting of KyberSwap's Implementation:** The exploit was specifically designed to target KyberSwap's concentrated liquidity implementation, making it unique to KyberSwap and any of its forks.
   - **Manipulation of the ETH/wstETH Pool:** The attacker focused on the pool containing Ethereum and Lido Wrapped Staked Ether (wstETH). This was the initial target of the exploit.
   - **Use of Flash Loans for Price Manipulation:** The attacker started by taking a large flash loan in wstETH and then dumped a portion into the pool, drastically reducing its price. This allowed the attacker to manipulate the pool price to a point where there were no existing liquidity positions, effectively creating a "clean slate" for further exploitation.
   - **Liquidity Minting and Burning:** The attacker then minted a small amount of liquidity in a very specific price range and subsequently burned some of it. This step was crucial in setting up the conditions for the exploit.
   - **Executing Swaps Around Manipulated Price Points:** Two swaps were performed around the manipulated price point. These swaps would normally not result in net gain due to the lack of external liquidity, but the exploit bypassed this limitation.
   - **Exploiting a Numerical Bug:** The exploit's core relied on a numerical bug in KyberSwap's smart contract. It involved preventing the triggering of a crucial function ('updateLiquidityAndCrossTick') during the first swap, which was necessary for correctly adjusting liquidity values when crossing price boundaries.
   - **The 'Infinite Money Glitch':** In the final phase of the exploit, the attacker ensured the triggering of the 'updateLiquidityAndCrossTick' function, adding liquidity back into the system. However, since the liquidity was never correctly removed in the first place, this resulted in double-counting the original liquidity, effectively creating an "infinite money glitch."
