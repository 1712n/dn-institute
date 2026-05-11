---
title: "Green United GREEN Token Mining Claims"
date: 2023-03-08
entities:
  - Green United
  - Set Power Free
  - Wright W. Thurston
  - Kristoffer A. Krohn
  - GREEN
  - Green Blockchain
---

## Summary

This case study analyzes the SEC's Green United complaint as a market-health warning about mining products that promise token production without an existing mineable token or functioning native blockchain. On March 8, 2023, the SEC announced that it had charged Green United, LLC, founder Wright W. Thurston, and promoter Kristoffer A. Krohn with allegedly defrauding investors in an unregistered crypto-asset securities offering.

According to the SEC's complaint, from at least April 2018 through at least December 2022, the defendants raised more than $18 million through investments called "Green Boxes" and "Green Nodes." The products were allegedly marketed as mining a token called GREEN on a purported Green Blockchain and as part of a plan to build a public global decentralized power grid.

The market-health signal is that mining claims can be independently tested. The SEC alleged that GREEN was an ERC-20 token, not a mineable crypto asset, that the promoted Green Blockchain did not exist, and that the token supply was created through an Ethereum smart contract in October 2018. The SEC also alleged that investor Green Boxes mined Bitcoin instead of GREEN and that the Bitcoin was not transferred to investors.

The supporting dataset is available in [green-united-summary.csv](green-united-summary.csv).

## Claimed Mining Model

The SEC litigation release said Green United and Thurston raised at least $18 million by selling Green Boxes and Green Nodes. Investors were allegedly led to believe that Green United would operate the products, mine GREEN, distribute GREEN tokens to investor wallets, and develop a Green Blockchain whose success could increase the value of GREEN.

The SEC complaint described a centralized operating model. Green United allegedly hosted and operated the Green Boxes, controlled the mining operation, and told investors that its technical knowledge and access to inexpensive power would support profitability. That matters because investors could not verify mining solely by possessing a dashboard or receiving token transfers; they needed evidence of the actual chain, token mechanics, mining output, pool records, wallet flows, and allocations.

The complaint alleged that the promoted technical model did not match the actual infrastructure. GREEN was allegedly deployed as an ERC-20 token on Ethereum months after Green Boxes were first offered, while the purported Green Blockchain did not exist. Token distributions to investor wallets were therefore a representation to verify, not proof that mining had occurred.

## False Market Signals

### Mineable-token claim

The SEC alleged that GREEN was not mineable and that the Green Blockchain did not exist. Any mining-return claim should be checked against the consensus mechanism, token contract, issuance schedule, and chain records.

### Hardware mismatch

The complaint alleged that Green Boxes were commercially available S9 Antminers that mined Bitcoin, not GREEN, and that investors did not receive the Bitcoin. Hardware claims should be reconciled to the asset actually mined and to the customer allocation record.

### ERC-20 token distribution

The SEC alleged that the total GREEN supply was created through an Ethereum smart contract and later distributed to wallets to create the appearance of mining. Token transfers can mimic mining output if reviewers do not distinguish smart-contract issuance from proof-of-work rewards.

### Exchange and liquidity expectations

The complaint alleged that investors were told GREEN would become available on a crypto asset trading platform, but GREEN was not available for purchase or sale on any such platform from April 2018 until fall 2020. Liquidity claims should be verified directly against exchange listings and trading history.

### Return representations

The complaint alleged that promotional materials described Green Boxes as producing monthly returns, including claims of 40 percent to 50 percent return and later 100 percent-plus ROI language. Such claims require hardware output, power costs, pool records, wallet payments, and realized market pricing.

## Event Timeline

| Date or period           | Event                                                                                               | Market-health signal                                                       |
| ------------------------ | --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| April 2018               | The SEC alleged that Green Boxes began being sold as machines that mined GREEN.                     | Mining claim required existence of a mineable token and chain.             |
| April 2018               | The complaint alleged Green Boxes were sold for approximately $3,000 each.                          | Hardware-purchase price set the baseline for return claims.                |
| April-October 2018       | The SEC alleged Krohn promoted Green Boxes and made return and value representations.               | Promoter claims needed verification against token mechanics and liquidity. |
| October 16, 2018         | The complaint alleged Thurston deployed the GREEN ERC-20 smart contract.                            | Token creation occurred after initial Green Box sales.                     |
| 2019 onward              | The SEC alleged Green United periodically distributed GREEN to investor wallets.                    | Wallet deposits could be distributions rather than mined rewards.          |
| April 2019               | The complaint alleged Green Nodes began being offered after Green Box sales became less profitable. | Product expansion repeated the same token-generation premise.              |
| April 2018-fall 2020     | The SEC alleged GREEN was not available for purchase or sale on a crypto asset trading platform.    | Claimed token value lacked secondary-market support.                       |
| April 2018-December 2022 | The SEC alleged more than $18 million was raised through Green Boxes and Green Nodes.               | Scale required investor-level custody and proceeds reconciliation.         |
| March 3, 2023            | The SEC filed the civil complaint in the District of Utah.                                          | Legal action formalized the alleged mining and token-issuance failures.    |
| March 8, 2023            | The SEC published the litigation release.                                                           | Public enforcement summary made the case visible for market-health review. |

## Reconciliation Metrics

| Metric                     | SEC allegation or figure                                        | Market-health interpretation                                                     |
| -------------------------- | --------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Total raised               | More than $18 million                                           | Claimed mining program required investor-level proceeds and allocation records.  |
| Green Box proceeds         | Approximately $5.4 million                                      | Hardware sales required reconciliation to actual mining output.                  |
| Green Box price            | Approximately $3,000 per Green Box                              | Unit economics needed verification against hashrate, power, and payouts.         |
| Bitcoin portion            | Approximately $900,000 worth of Bitcoin used to buy Green Boxes | Crypto inflows needed custody and use-of-proceeds tracing.                       |
| Transfer to Block Brothers | More than $1.7 million from Green United's pooled bank account  | Related-party flows needed review against offering disclosures.                  |
| Token mechanics            | GREEN allegedly created as an ERC-20 token on October 16, 2018  | Smart-contract issuance did not equal mining rewards.                            |
| Liquidity                  | No trading platform availability alleged until fall 2020        | Token value claims lacked an observable secondary market for much of the period. |
| Legal posture              | SEC civil complaint allegations                                 | Article should treat the claims as allegations unless adjudicated.               |

## Detection Checklist

1. Confirm that the advertised token is technically mineable and that the promoted chain exists.
2. Match the advertised mining hardware to the actual asset mined, pool records, wallet outputs, and customer allocations.
3. Distinguish ERC-20 token creation and transfers from mining rewards.
4. Verify exchange-listing and liquidity claims against actual trading venue records.
5. Reconcile claimed monthly returns to hashrate, difficulty, power costs, pool fees, token price, and realized payouts.
6. Trace related-party transfers from pooled offering accounts.
7. Preserve legal posture: this article relies on SEC civil allegations and should not treat the allegations as adjudicated findings.

## Market-Health Lessons

Green United shows why mining products need technical verification before financial analysis. If the chain does not exist or the token cannot be mined, a dashboard, wallet deposit, or hardware photograph can become a false proxy for production.

The case also shows why token distributions should be traced to their issuance source. A transfer from a smart-contract supply can resemble a mining reward in an investor wallet, but the market-health question is whether the transfer came from the advertised production process.

## References

- [SEC litigation release, Green United, March 8, 2023](https://www.sec.gov/enforcement-litigation/litigation-releases/lr-25659)
- [SEC complaint, SEC v. Green United, LLC, Wright W. Thurston, and Kristoffer A. Krohn](https://www.sec.gov/files/litigation/complaints/2023/comp25659.pdf)
