---
date: 2022-10-06
custodians: Binance Smart Chain
categories: Smart contract
title: "BSC Token Hub Hit By $586 Million Bridge Hack"
---

## Summary

On October 6, 2022, BSC Token Hub, a bridge between BNB Beacon Chain (BEP2) and Binance Smart Chain (BEP20) was exploited. The native cross-chain bridge between BNB Beacon Chain (BEP2) and BNB Smart Chain (BEP20), also known as BNB Token Hub was exploited. The hacker used a low-level proof vulnerability and minted 2,000,000 $BNB to their address. Consequently, the hacker began bridging the funds to Fantom and Ethereum chains. The security experts in collaboration with validators were able to save the majority of the funds. The hacker managed to bridge 127,000,000 $USD using AnySwap and Stargate bridges, with 53% of the stolen funds going to Ethereum, 33% to Fantom, and the rest to other chains. Tether blacklisted the attacker's address. The remaining 459,000,000 $USD worth of assets were left frozen in the attacker's address. 

## Attacker

Attackers address on BSC: 0x489a8756c18c0b8b24ec2a2b9ff3d4d447f79bec

## Losses

2 million BNB was minted, it equals $586 million. Only $127 million worth of assets were bridged, and the rest $459 million is left frozen. 

## Timeline

- **October 6, 2022 6:26 PM UTC:** Initial malicious transaction with 1 million BNB mint
- **October 6, 2022 8:43 PM UTC:** Secondary malicious transaction with 1 million BNB mint
- **October 6, 2022 11:51 PM UTC:** CEO of Binance also known as CZ tweeted about suspending the chain
- **October 7, 2022 6:40 AM UTC:** Binance Smart Chain was resumed after security update which freezed the hackers address

## Security Failure Causes

**Transaction verifying vilnerability:** The BSC Token Hub was possible to exploit via low-level proof vulnerability. The exact approach used by the hacker is undefined, however, the main issue with the bridge is the proof, that allowed the malicious actor to verify any transaction on BSC chain, without performing it in Beacon chain.