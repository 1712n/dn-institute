---
date: 2023-04-15
target-entities:
  - Hundred Finance
entity-types:
  - DeFi
  - Lending Platform
attack-types:
  - Smart Contract Exploit
  - Flash Loan Attack
title: "Hundred Finance Hacked for $6.8 Million"
loss: 6800000
---

## Summary

On April 15, 2023, at 2:12 pm UTC, Hundred Finance's Optimism deployment fell victim to an exploit that drained the platform of all assets in hToken markets. The attacker utilized an integer rounding vulnerability within the hToken contract logic to redeem underlying tokens when a market was empty. The total loss amounted to roughly $6.8 million USD in various cryptocurrencies.

## Attackers

The attackers remain unidentified.

Exploiter addresses:

- **Optimism::** [0x155da45d374a286d383839b1ef27567a15e67528](https://optimistic.etherscan.io/address/0x155da45d374a286d383839b1ef27567a15e67528)
- **Ethereum:** [0x155da45d374a286d383839b1ef27567a15e67528](https://etherscan.io/address/0x155da45d374a286d383839b1ef27567a15e67528)

## Losses

Totaling around $6.8 million USD. These funds were supplied by 180 individual wallets.

- 1,030 ETH (~ $2,150,000)
- 1,265,979 USDC
- 1,113,431 USDT
- 865,143 SUSD
- 842,788 DAI
- 457,286 FRAX
- 20,854 SNX (~ $56,000)

## Timeline

- **April 14, 2023:** The attacker [withdrew 10 ETH](https://etherscan.io/tx/0x5317521498981511dc7d3fc95895a2fca595fce4ba15ce4fb26caf84dda21258) from Tornado Cash.
- **April 15 2023, 02:12:00 PM +UTC:** The attacker [exploited](https://optimistic.etherscan.io//tx/0x6e9ebcdebbabda04fa9f2e3bc21ea8b2e4fb4bf4f4670cb8483e2f0b2604f451) the vulnerability and drained the assets.
- **April 15, 2023, 02:37 PM +UTC:** The Hundred Finance team [announced](https://twitter.com/HundredFinance/status/1647247792589471745) the hack on Twitter.
- **April 15, 2023, 04:10:47 PM +UTC:** The team has sent the [first on-chain message](https://etherscan.io/tx/0xefecb4942e743517c21f603d3bc096a1c941f9a002eea3ec6ca067f801adc078) to attackers, requesting the return of the funds.
- **April 17, 2023, 04:10 PM:** Hundred Finance [offered](https://twitter.com/HundredFinance/status/1647995836117180416) a $500k USD open bounty for information.
- **April 18, 2023, 01:31:59 PM +UTC:** The team has sent a [second on-chain message](https://etherscan.io/tx/0x6fd6eeeb0f3f5c0f25e384710aa0ff027e924973806f514e9984eec042ad7003) to attackers, requesting the return of 90% of the funds within 24 hours.
- **April 23, 2023:** Hundred Finance published [post-mortem report](https://blog.hundred.finance/15-04-23-hundred-finance-hack-post-mortem-d895b618cf33)

## Security Failure Causes

- **Smart contract vulnerability:**
  The exploit leveraged an integer rounding vulnerability that had existed since the launch of the Compound v2 code. The vulnerability manifested when a market was empty and allowed for the manipulation of collateral value within the hToken markets.
