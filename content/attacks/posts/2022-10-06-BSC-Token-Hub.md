---
date: 2022-10-06
target-entities:
  - Binance Smart Chain
  - Token Hub Bridge
entity-types:
  - Blockchain
  - Bridge
attack-types: Signature Verification Issue
title: "BSC Token Hub Hit By $586 Million Bridge Hack"
loss: 127000000
---

## Summary

On October 6, 2022, BSC Token Hub, a bridge between BNB Beacon Chain (BEP2) and Binance Smart Chain (BEP20) was exploited. The native cross-chain bridge between BNB Beacon Chain (BEP2) and BNB Smart Chain (BEP20), also known as BNB Token Hub was exploited. The hacker used a low-level proof vulnerability and 2,000,000 $BNB were drained out of thin air. Consequently, the hacker began [bridging the funds to Fantom and Ethereum chains](https://www.coinbase.com/blog/bsc-token-hub-compromise-investigation-and-analysis-8). [The security experts in collaboration with validators were able to save the majority of the funds](https://www.bnbchain.org/en/blog/bnb-chain-ecosystem-update). The [hacker managed to bridge 127,000,000 $USD using AnySwap and Stargate bridges](https://rekt.news/bnb-bridge-rekt), with 53% of the stolen funds going to Ethereum, 33% to Fantom, and the rest to other chains. The remaining assets were left frozen in the attacker's address.

## Attacker

Attackers address: 0x489a8756c18c0b8b24ec2a2b9ff3d4d447f79bec
Attacker has several wallets with the same address in Ethereum, Fantom, Avalanche, Polygon, Arbitrum, Optimism.

## Losses

2 million BNB was minted, it equals $586 million. Only $127 million worth of assets were bridged, and the rest is left frozen.

## Timeline

- **October 6, 2022 6:26 PM UTC:** [Initial malicious transaction](https://bscscan.com/tx/0xebf83628ba893d35b496121fb8201666b8e09f3cbadf0e269162baa72efe3b8b) with 1 million BNB mint
- **October 6, 2022 8:43 PM UTC:** [Secondary malicious transaction](https://bscscan.com/tx/0x05356fd06ce56a9ec5b4eaf9c075abd740cae4c21eab1676440ab5cd2fe5c57a) with 1 million BNB mint
- **October 6, 2022 11:51 PM UTC:** CEO of Binance also known as CZ tweeted about suspending the chain
- **October 7, 2022 6:40 AM UTC:** Binance Smart Chain was resumed after security update which [froze the hackers address](https://www.investopedia.com/binance-got-hacked-6748215#:~:text=The%20BSC%20Token%20Hub%2C%20a%20cross-chain%20bridge%2C%20was,down%20by%203.5%25%20over%20the%20past%2024%20hours.)

## Security Failure Causes

**Protocol vulnerability:** The BSC Token Hub was attacked by forging a low-level proof into a single common library. Protocol code analysis identified a flaw in Cosmos IAVL verification implementation, which was later incorporated by BSC into their contract proof verification process. The same vulnerability also affected other projects using the vulnerable IAVL library, prompting Cosmos to release an emergency patch.
