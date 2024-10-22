---
date: 2023-03-13
target-entities: Euler Finance
entity-types:
  - DeFi
  - Lending Platform
attack-types: Flash Loan Attack
title: "Euler Finance Exploited with Flash Loan Attack Resulting in Loss of $196 Million"
loss: 196000000
---

## Summary

On March 13, 2023, a flash loan attack targeted Euler Finance, a noncustodial lending platform on the Ethereum blockchain. The attack led to a loss of roughly $196 million in various cryptocurrencies, including Dai, USD Coin, Staked Ether, and Wrapped Bitcoin. The attacker took advantage of a weakness in Euler's smart contract, specifically in a feature called "donateToReserves."

The attacker used multiple Ethereum addresses to exploit this weakness in the contract and took advantage of a problem in Euler's system for liquidation. They took 30 million DAI as a flashloan from Aave, and deposited to Euler. Consequently, they generated a lot of eDAI and sent it to an address that didn't exist, which lowered their "health score" within Euler's system. This allowed them to start a liquidation process and shift large amounts of debt to their account.

In response, Euler Finance quickly disabled the feature that had been exploited. They asked the attacker to return 90% of the stolen funds and threatened to take legal action. They also offered a $1 million reward for information that could identify the attacker.

The attacker began to return the stolen assets after Euler took these steps. With the return of the funds, Euler Finance withdrew its $1 million reward offer.

## Attackers

The attackers remain unidentified. The attackers utilized the following Ethereum addresses:

- [0x5f259d0b76665c337c6104145894f4d1d2758b8c](https://etherscan.io/address/0x5f259d0b76665c337c6104145894f4d1d2758b8c)
- [0xb2698c2d99ad2c302a95a8db26b08d17a77cedd4](https://etherscan.io/address/0xb2698c2d99ad2c302a95a8db26b08d17a77cedd4)

The following contracts were used in the attack:

- [0xebc29199c817dc47ba12e3f86102564d640cbf99](https://etherscan.io/address/0xebc29199c817dc47ba12e3f86102564d640cbf99)
- [0x036cec1a199234fc02f72d29e596a09440825f1c](https://etherscan.io/address/0x036cec1a199234fc02f72d29e596a09440825f1c)

## Losses

Breakdown of the lost $196 million:

- $8.7 million in Dai
- $18.5 million in Wrapped Bitcoin
- $135.8 million in Staked Ethereum
- $33.8 million in Circle's USD stablecoin, USDC

## Timeline

- **March 13, 2023:** Flash loan attack on Euler Finance causing losses of over $196 million.
- **March 14, 2023:** Euler Finance [deactivated its eToken module and vulnerable donation feature](https://twitter.com/eulerfinance/status/1635431726364147712?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1635431834631766018%7Ctwgr%5Ea96fc9553832a9a0fecba05827cd0f1d05e93850%7Ctwcon%5Es2_&ref_url=https%3A%2F%2Fcointelegraph.com%2Fnews%2Feuler-labs-hacker-returns-all-of-the-recoverable-funds-timeline)
- **March 15, 2023:** Euler Finance [addresses the attacker](https://cointelegraph.com/news/euler-finance-s-offer-to-hacker-keep-20m-or-face-the-law) with an ultimatum to return 90% of the stolen funds, threatening to announce a reward of $1 million for any information leading to the hacker’s arrest.
- **March 16, 2023:** Euler Finance [declared a $1 million bounty](https://twitter.com/eulerfinance/status/1636126837423366145) aimed at identifying the hacker and recovering the stolen money.
- **March 18, 2023:** Around 3,000 Ether, equivalent to $5.4 million, [was returned to Euler](https://tokeninsight.com/en/news/euler-finance-hacker-returns-some-stolen-eth-back-to-euler-but-full-recovery-unlikely) Finance's deployer address from the hacker's address.
- **March 25, 2023:** The [hacker initiated the return of the stolen assets](https://cryptonews.com/news/euler-finance-hacker-returns-100-million-surprising-act-heres-what-happened.htm) in significant amounts on several instances.
- **April 4, 2023:** Euler Finance [called off the $1 million reward](https://twitter.com/eulerfinance/status/1643027452388597765) as they announced the potential complete recovery of the stolen funds.

## Security Failure Causes

**Smart contract vulnerability:** Euler's smart contract update containing "donateToReserves" function had a major flaw that the attacker exploited using multiple Ethereum addresses to perform malicious actions.

**Flaw in the liquidation discount logic:** The attacker used the heavy discounts Euler offered to liquidators. They created a lot of eDAI, sent it to a null address lowering their health score, and then started the liquidation process, moving large debts to their liquidator account.
