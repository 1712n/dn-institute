---
date: 2021-10-27
target-entities: Cream Finance
entity-types:
  - DeFi
  - Lending Platform
attack-types:
  - Smart Contract Exploit
  - Flash Loan Attack
  - Price Oracle Manipulation
title: "Cream Finance Hack: $130 Million Stolen in Exploit"
loss: 130000000
---

## Summary

On October 27, 2021, Cream Finance, a decentralized finance (DeFi) platform, fell victim to a sophisticated attack resulting in the theft of $130 million worth of cryptocurrency. The attacker exploited vulnerabilities in Cream Finance's lending pool contract and manipulated the price oracle, allowing them to carry out a series of orchestrated transactions that ultimately drained the protocol of its liquidity.

## Attackers

The attackers remain unidentified.

- [0x24354d31bc9d90f62fe5f2454709c32049cf866b](https://etherscan.io/address/0x24354d31bc9d90f62fe5f2454709c32049cf866b)

## Losses

$130M USD

## Timeline

- **October 27, 2021, 01:54:10 PM +UTC** Attacker's [transaction](https://etherscan.io/tx/0x0fe2542079644e107cbf13690eb9c2c65963ccb79089ff96bfaf8dced2331c92)
- **October 28, 2021, 03:17 AM +UTC:** Cream Finance [announced](https://twitter.com/CreamdotFinance/status/1453455806075006976) that the protocol was successfully attacked.
- **October 28, 2021:** Blockchain security firm Slow Mist [published attack analysis](https://medium.com/@slowmist/cream-hacked-analysis-us-130-million-hacked-95c9410320ca)
- **November 1, 2021:** Cream Finance [published exploit Post-Mortem.](https://medium.com/cream-finance/c-r-e-a-m-finance-post-mortem-amp-exploit-6ceb20a630c5)
- **November 13, 2021:** Cream Finance [announced](https://creamdotfinance.medium.com/moving-forward-post-exploit-next-steps-for-c-r-e-a-m-finance-1ad05e2066d5) that affected users will receive 1,453,415 CREAM tokens
- **November 9, 2022:** Immunefi [published hack analysis](https://medium.com/immunefi/hack-analysis-cream-finance-oct-2021-fc222d913fc5)

## Security Failure Causes
- **Uncapped Token Supply:** Cream Finance allowed users to supply tokens without strict limits, making it susceptible to manipulation. The attacker leveraged this design flaw by repeatedly supplying the same asset, artificially inflating the collateral value and triggering additional borrowing capacity.
- **Oracle Vulnerability:** The use of an easily manipulatable hybrid oracle exacerbated the attack. The oracle, based on the Yearn 4-Curve pool's assets, allowed the attacker to double the value of certain tokens, leading to significant distortions in the protocol's health calculations. The protocol relied on this oracle to determine the value of collateral and borrowed tokens.
- **Lack of Reentrancy Guard:** Cream Finance lacked a protocol-level reentrancy guard, leaving it vulnerable to reentrancy attacks. This deficiency enabled the attacker to execute a series of complex transactions with precision.
