---
date: 2021-05-19
categories: "DeFi"
title: "PancakeBunny suffers a flash loan attack"
---

Summary

On May 19, 2021 PancakeBunny, a yield farming aggregator built on Binance Smart Chain decentralized finance (DeFi) protocol, suffered a flash loan attack. The attack was investigated and the report was posted on the PancakeBunny Medium blog: https://pancakebunny.medium.com/hello-bunny-fam-a7bf0c7a07ba
The actions described below in this section were done withing one transaction¹ (which made this attack possible).
The attacker borrowed 2323373 WBNB from PancakeBunny lending pools and 2961750 USDT from another source.
2961750 USDT and 7744 BNB were deposited on the PancakeSwap Version 2 (PCS V2) USDT/BNB pool (having created 144445 LP tokens).
2315631 WBNB were swapped to USDT (on the PCS V1 USDT/BNB pool, exploiting its pricing).
Then the hacker removed liquidity from USDT/BNB pool on all 144445LP tokens. 
The BNB tokens were used to manipulate Bunny/BNB price, as a result of which 6972455Bunny were issued after PancakeBunny protocol's calculating².
Having got this reward the attacker dumped most (on PCS V1 and V2 summarily 6275209Bunny were swapped for 2441024BNB) of it in the market which caused Bunny's value to plummet. Then BNB tokens were paid back, after which 114631BNB left over (another part of the hacker's profit was the reminder of Bunny tokens: 697246).
The borrowed USDT were paid back here either.

Attackers

The attacker remain unidentified. 
Attacker's wallet address:
0xa0ACC61547f6bd066f7c9663C17A312b6Ad7E187

Losses

If calculated based on the average Bunny price shortly before the attack, PancakeBunny's loss was roughly $150 million (697246Bunny~$105M + 114631BNB~$45M).
Bunny token plummeted to almost 0 (the price was ~$150 before attack, it increased up to ~$240 for a short time right after, then it fell within minutes after). Later that day it recovered about 5% of its value.
To compensate losses of Bunny holders the Team declared creating a compensation pool as well as a new token - polyBunny, for Polygon PancakeBunny, was announced (was initially planned to be done several months later). Then another flash loan attack happenned (on July 17, 2021) causing losses again, polyBunny price fell.

Timeline

May 19, 2021
10:31:25PM - 1BNB deposited on the USDT/BNB Flip Vault to stage the attack
¹10:34:28PM - the time of the exploit transaction
10:36:00PM - the Bunny Team detected unusual increase of Bunny's price
10:45:10PM - 114631BNB were sent to this address (for being laundered):
0x158c244b62058330f2c328c720b072d8db2c612f
11:18:10PM - the Flash Loan attack is officially confirmed, deposits/withdrawals to the Vault are paused (to prevent further attacks)
11:59:55PM - 488071,9...Bunny were swapped for 9161,3...BNB from the same address as on 10:45

May 21, 2021
06:30:00AM - withdrawal/deposit function is restored to the Vault

Security Failure Causes

²Calculating the amount of Bunny tokens to be issued was based on the proportion of BNB/USDT tokens in the pool.
The availability of borrowing of huge amount of assets was crucial in this case (probably the variety mattered either).
