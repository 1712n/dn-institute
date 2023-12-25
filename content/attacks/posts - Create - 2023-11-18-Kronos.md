---
date: 2023-11-19
target-entities: Kronos Research 
entity-types: 
   - Trading Firm
attack-types:
   - Private Key Leak
title: “Kronos Research halts trading after $25M API key hack”
loss: 26000000
---

## Summary

On November 19, 2023, Kronos Research, a Taipei-based cryptocurrency trading and investment firm, was targeted by a hacker who stole over $25 million from the firm's treasury using [unauthorized API keys.](https://cryptonews.com/news/kronos-research-enters-negotiations-with-hacker-after-25-million-cryptocurrency-theft-offers-10-bounty.htm) This breach enabled the attacker to access the company's blockchain wallets and conduct unauthorized transactions. The hack's impact extended beyond Kronos Research, affecting Woo X, an exchange closely affiliated with Kronos. As Kronos was a major liquidity provider for Woo X, the security incident led to a temporary suspension of certain asset pairs on Woo X due to a liquidity shortage.

## Attackers

The Attacker has not been identified or communicated with Kronos Research since the hack.

## Losses

At the time of the attack, Kronos Research lost around $26 million. According to Lookonchain’s X feed, the following losses occurred:

   - $24.57M in USDT
   - $488.7 in ETH
   - $125,056 in USDC

## Timeline

   - **November 18, 2023, 17:05 UTC:** Initial funds transfer [begins.](https://etherscan.io/address/0x2b0502fdab4e221dcd492c058255d2073d50a3ae)     
   - **November 19, 2023, 11:27 UTC:** Kronos Research releases a [series](https://twitter.com/ResearchKronos/status/1726203102842466650) of posts on X confirming the hack involved unauthorized access to its API Keys, resulting in a loss of approximately $26 million and stating the firm will internally cover all losses.
   - **November 28, 2023, 18:30 UTC:** Kronos Research offers a [whitehat bounty](https://etherscan.io/idm?addresses=0xad5916c0f641841637bab1a1049224c3cfd5acf0,0x7e1a22655e2a46a5dd8aec2905c298f1d06b8597&type=1) of 10% and promises no legal ramifications if funds are returned by 8:00 UTC on November 30, 2023.

## Security Failure Causes

   - **API Key Compromise:** The successful attack resulted from compromising API keys, allowing unauthorized access to critical systems and resources.
   - **Insufficient Access Controls on API Endpoints:** Inadequate access controls on API endpoints allowed the attackers to gain unauthorized access to the stolen funds.
