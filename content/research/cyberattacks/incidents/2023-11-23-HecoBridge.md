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
title: Coordinated Attacks Result in $113.3 Million in Losses for Heco Bridge and HTX Exchange
loss: 113300000
---

## Summary

On November 22, 2023, Heco Bridge and HTX Exchange were victims of cyberattacks, resulting in over $113.3 million in losses. The attacks appear coordinated and carried out by the same attacker based on similar exploitative techniques and the connection between the two targets. Blockchain security firms CertiK, Peckshield, and Cyvers have reported over $86.6 million in digital assets losses for Heco Bridge and $13.6 million in losses for HTX. All of which were distributed over eight wallets. Additionally, CertiK noted several transactions taking place simultaneously on TRON, totaling $12.6 million, putting their reported total over $113.3 million.

## Attackers

The attacker has yet to be identified but used 0xe47e6dA16Bb83EB0FD26b3F29b15CE8Fab089B9e address to transfer some of the drained funds.

## Losses

According to CertiK, the following [withdraws](https://www.certik.com/resources/blog/39YOzflgCCbfI9evJliCeQ-heco-bridge-exploit) took place: 

Heco [Bridge](https://www.certik.com/resources/blog/39YOzflgCCbfI9evJliCeQ-heco-bridge-exploit):
- $10,145 in ETH
- $42,110,000 in USDT
- $489 in HBTC
- $346,867,120,000 in SHIBA INU
- $173,200 in UNI
- $619,000 in USDC
- $42,399 in LINK
- $346,994 in TUSD

[HTX](https://www.certik.com/resources/blog/39YOzflgCCbfI9evJliCeQ-heco-bridge-exploit):
- $1,240 in ETH
- $7,330,600 in USDT
- $1,780,000 in USDC
- $61,250 in LINK
- $2,195,836 in ARIX
- $4,254,541 in KOK

## Timeline

- **November 22, 2023, 10:06 AM UTC:** Initial [funds transfer](https://etherscan.io/tx/0xe021e1d8fd38a874de4713b7ce1aaffd646a135265826f6eb3232e05313b2d87) wallet transaction. 
- **November 22, 2023 at 11:23 AM UTC:** In an X post, PeakShield announces a Heco Bridge [withdrawal](https://twitter.com/PeckShieldAlert/status/1727286692489679360) of 10,145 ETH.
- **November 22, 2023 at 12:34 PM UTC:** Justin Sun announces the attack in an X post. He states all withdrawals and deposits have been temporarily [suspended],(https://twitter.com/justinsuntron/status/1727304656622326180) and HTX will compensate for the losses from its hot wallet.
- **November 24, 2023 at 02:55 PM UTC:** Justin Sun announces in an X post an [airdrop](https://twitter.com/justinsuntron/status/1728064872632795480) will be initiated for user assets.
- **December 4, 2023:** [Postmortem Analysis](https://olympixai.medium.com/heco-bridge-hack-analysis-64cffda76684) is posted on Medium by Olympix.
     
## Security Failure Causes

- **Insecure Management of Private Keys:** Lapses in safeguarding private keys allowed attackers to gain control over critical wallets.
- **Insufficient Anomaly Detection:** A lack of mechanisms to detect unusual transaction patterns early.
- **Failure in Multi-Signature Security:** If not implemented, could have prevented unauthorized transactions even if a key was compromised.
