---
date: 2023-08-13 
target-entities: Zunami Protocol 
entity-types: 
   - DeFi
   - Yield Aggregator
   - Stablecoin
attack-types:
   - Flash Loan Attack
   - Smart Contract Exploit
title: "Zunami Protocol lost $2.16 million in a flash loan attack."
loss: 2160000
---

## Summary

On August 13, 2023, Zunami Protocol, a prominent DeFi platform on Ethereum, was compromised through a sophisticated flash loan attack, resulting in a significant loss of 1,178 ETH, approximately valued at $2.16 million. Central to this exploit was a vulnerability within the platform's contract that allowed for the manipulation of the UZD token's balance. By leveraging a flash loan the attacker was able to artificially inflate the value of the UZD token. This manipulation enabled the withdrawal of an extensive sum of assets.

## Attackers

The identity of the hackers who attacked Zunami is unknown.

Hacker ETH Wallets:

- [0x5f4c21c9bb73c8b4a296cc256c0cde324db146df](https://etherscan.io/address/0x5f4c21c9bb73c8b4a296cc256c0cde324db146df)

## Losses

Zunami estimated the losses from the hack to be 1178 ETH( $2.16 million). The stolen assets were moved through various transactions and eventually [sent](https://etherscan.io/advanced-filter?fadd=0x5f4c21c9bb73c8b4a296cc256c0cde324db146df&tadd=0xd90e2f925da726b50c4ed8d0fb90ad053324f31b&txntype=0&qt=1) to Tornado Cash.

## Timeline

- **2023-08-13, 10:26:35 PM UTC:** The [first malicious transaction occurred](https://etherscan.io/tx/0x2aec4fdb2a09ad4269a410f2c770737626fb62c54e0fa8ac25e8582d4b690cca) and 26 ETH were stolen.
- **2023-08-13, 10:34:47 PM UTC:** A [second malicious transaction occurred](https://etherscan.io/tx/0x2aec4fdb2a09ad4269a410f2c770737626fb62c54e0fa8ac25e8582d4b690cca) and 1152 ETH were stolen.
- **2023-08-14, 06:10 AM UTC:** Zunami protocol [announced](https://twitter.com/ZunamiProtocol/status/1690863406079696896) a hack.
- **2023-08-16, 02:01 AM UTC:** Zunami published [exploit Post-Mortem](https://twitter.com/ZunamiProtocol/status/1691527489716146177).
- **2023-08-18** Immunebytes [published](https://www.immunebytes.com/blog/zunami-protocol-hack-aug-13-2023-detailed-analysis-report/) a detailed analysis of the incident.

## Security Failure Causes

- **Smart contract vulnerability:** The root cause of the Zunami Protocol exploit was a flaw in the token recognition process, specifically in the way the protocol calculated the balance of its stable token, UZD. The vulnerability stemmed from a manipulation of the "assetPriceCached()" function within the protocol's formula for calculating user balances in UZD. This function was designed to fetch the cached price of assets to compute the value of holdings within the protocol. However, the attacker discovered a way to manipulate this price through the "cacheAssetPrice()" function. By initiating flash loans of large amounts of USDT, USDC, and WETH from platforms like UniSwapV3 and Balancer, the attacker obtained the capital needed to manipulate the market price of the SDT token on Sushiswap. This manipulation involved swapping large quantities of borrowed tokens for SDT and other tokens, significantly inflating the price of SDT to USDT. As a result of these manipulations, when the "assetPriceCached()" function was called, it returned an artificially inflated price for SDT. With the inflated SDT price, the attacker then exploited the Zunami Protocol's system by inflating the balance of UZD tokens. The protocol's reliance on the manipulated assetPriceCached() value allowed the attacker to increase their UZD balance artificially This inflated balance was then used to withdraw assets from the protocol far exceeding the attacker's initial deposit.
