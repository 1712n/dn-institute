---
date: 2023-11-23
target-entities: 
   - Heco Bridge
   - HTX
entity-types:  
   - Custodian
   - DeFi
   - Exchange
   - Bridge
attack-types:
   - Private Key Leak
title: “Coordinated Attacks Result in $113.3 Million in Losses for Heco Bridge and HTX Exchange” 
loss: 113300000
---
## Summary

On November 22, 2023, Heco Bridge and HTX Exchange were victims of cyberattacks, resulting in over $113.3 million in losses. The attacks appear coordinated and carried out by the same attacker based on similar exploitative techniques and the connection between the two targets. Blockchain security firms CertiK, Peckshield, and Cyvers have reported over $86.6 million in digital assets losses for Heco Bridge and $13.6 million in losses for HTX. All of which were distributed over eight wallets. Additionally, CertiK noted several transactions taking place simultaneously on TRON, totaling $12.6 million, putting their reported total over $113.3 million.

## Attackers

The attacker has yet to be identified but used the following wallets to transfer some of the high-jacked funds:

        - 0xe47e6dA16Bb83EB0FD26b3F29b15CE8Fab089B9e (holding wallet)
        - 0xbb6fe88427c2f3bc179075109d47a805dcfedab0e475eaca0d979311873e131b
          
## Losses

According to CertiK, the following [withdraws](https://www.certik.com/resources/blog/39YOzflgCCbfI9evJliCeQ-heco-bridge-exploit) took place: 

Heco Bridge:
   - $10,145 in ETH
   - $42,110,000 in USDT
   - $489 in HBTC
   - $346,867,120,000 in SHIBA INU
   - $173,200 in UNI
   - $619,000 in USDC
   - $42,399 in LINK
   - $346,994 in TUSD

HTX:
   - $1,240 in ETH
   - $7,330,600 in USDT
   - $1,780,000 in USDC
   - $61,250 in LINK
   - $2,195,836 in ARIX
   - $4,254,541 in KOK

Tron:
   - $500,000 in TRX
   - $10.3 million in USDT, 
   - $2.2 million in USDC, 
   - $521.7k in RockDAO
   - approximately $1 million in BTT tokens.

## Timeline

   - **"November 22, 2023, 10:06 UTC:"** Initial [funds transfer] (https://etherscan.io/address/0xfc146d1caf6ba1d1ce6dcb5b35dcbf895f50b0c4) begins.
   - **”November 22, 2023, 10:56 UTC:”** Heco Bridge begins the process of moving recovery funds into [wallet.](https://etherscan.io/txs)
   - **”November 22, 2023, 11:13 UTC:”** Cyvers Alerts [announces](https://twitter.com/CyversAlerts/status/1727284118763757661) via X several transactions totaling around $12.4 million. 
   - **”November 22, 2023, 12:34 UTC:”** Justin Sun announces the attack via X and states all withdrawals and deposits have been temporarily [suspended](https://twitter.com/justinsuntron/status/1727304656622326180) and HTX will compensate for the losses from its hot wallet.
   - **”December 4, 2023:”** [Postmortem Analysis](https://olympixai.medium.com/heco-bridge-hack-analysis-64cffda76684) is posted on Medium.
     
## Security Failure Causes

   - **Compromised Private Keys:** The compromised private keys allowed attackers to illicitly transfer funds from Heco Bridge.
   - **Lack of Real-time Monitoring and Alerts:** The absence of an effective real-time monitoring system and alert mechanism would have assisted with detecting the ongoing exploit.
