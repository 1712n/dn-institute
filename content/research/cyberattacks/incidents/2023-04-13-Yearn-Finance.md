---
date: 2023-04-13
target-entities:
  - Yearn Finance
entity-types:
  - DeFi
  - Yield Aggregator
attack-types:
  - Smart Contract Exploit
title: "Yearn Finance Suffers $11.54 Million Loss Due to Smart Contract Vulnerability"
loss: 11540000
---

## Summary

On April 13, 2023, Yearn Finance, a prominent DeFi protocol on the Ethereum blockchain, [was exploited](https://quillaudits.medium.com/decoding-yearn-finance-11-million-hack-quillaudits-c9a75ac7e68b) due to a misconfiguration in its yUSDT vault's smart contract. The attacker leveraged this vulnerability to mint an excessive number of yUSDT tokens, which were subsequently exchanged for stablecoins. The exploit led to the loss of approximately $11.54 million.

## Attackers

The attackers are unidentified, but their wallet addresses and contracts are known:

**Attacker Addresses:**

- [0x5bac20beef31d0eccb369a33514831ed8e9cdfe0](https://etherscan.io/address/0x5bac20beef31d0eccb369a33514831ed8e9cdfe0)
- [0x16Af29b7eFbf019ef30aae9023A5140c012374A5](https://etherscan.io/address/0x16Af29b7eFbf019ef30aae9023A5140c012374A5)
- [0x6f4A6262d06272c8B2E00Ce75e76d84b9D6F6aB8](https://etherscan.io/address/0x6f4A6262d06272c8B2E00Ce75e76d84b9D6F6aB8)

**Malicious Contracts:**

- [0x8102ae88c617deb2a5471cac90418da4ccd0579e](https://etherscan.io/address/0x8102ae88c617deb2a5471cac90418da4ccd0579e)
- [0x9fcc1409b56cf235d9cdbbb86b6ad5089fa0eb0f](https://etherscan.io/address/0x9fcc1409b56cf235d9cdbbb86b6ad5089fa0eb0f)

## Losses

Yearn Finance lost approximately $11.54 million in the exploit. The funds were predominantly in U.S. dollar-pegged stablecoins, including DAI, USDT, USDC, BUSD, and TUSD.

## Timeline

- **April 13, 2023, 05:52:35 AM +UTC:** The attacker exploited the vulnerability in Yearn Finance's yUSDT vault. [First transaction](https://etherscan.io/tx/0xd55e43c1602b28d4fd4667ee445d570c8f298f5401cf04e62ec329759ecda95d) and [second transaction](https://etherscan.io/tx/0x8db0ef33024c47200d47d8e97b0fcfc4b51de1820dfb4e911f0e3fb0a4053138).
- **April 13, 2023:** Yearn Finance team acknowledges the incident and [clarifies](https://twitter.com/storming0x/status/1646408774477922305) that the exploit occurred in the legacy Yearn protocol and liquidity pool but did not affect Yearn v2 vaults.
- **April 13, 2023:** Aave developers [clarify](https://twitter.com/AaveAave/status/1646410238797688832) that Aave V1, V2, and V3 contracts were not impacted by the exploit.
- **April 13, 2023:** The attacker [transferred](https://etherscan.io/tx/0x318111c68ff35b034955316411f92d3106b4fd90a25c8957849c04d640758a01) 1000 ETH to Tornado Cash from their second wallet.
-

## Security Failure Causes

- **Smart contract misconfiguration:** The root cause of the vulnerability was a [misconfiguration](https://twitter.com/yearnfi/status/1646436798086672385) in the yUSDT vault's smart contract. Specifically, the contract utilized the iUSDC token instead of the iUSDT token, leading to a mistaken dependency on the pool’s underlying token. This error was present at the time of deployment and went unnoticed for approximately 1000 days.
