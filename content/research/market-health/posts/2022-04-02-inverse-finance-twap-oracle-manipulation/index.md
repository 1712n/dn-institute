---
title: "Inverse Finance TWAP Oracle Manipulation"
date: "2022-04-02"
description: "Inverse Finance's April 2022 Anchor exploit shows how a thin DEX pair, a short TWAP window, and borrowable multi-asset liquidity can turn a capital-intensive spot trade into a lending-market drain."
entities:
  - Inverse Finance
  - INV
  - DOLA
  - Anchor
  - SushiSwap
  - Keep3r
  - Ethereum
---

## Summary

Inverse Finance's Anchor money market was exploited on April 2, 2022 after the INV price used by its oracle was manipulated through SushiSwap liquidity. CertiK, PYMNTS, The Crypto Times, Web3 Is Going Great, and CSIDB describe the incident as an oracle-price manipulation that allowed the attacker to borrow far more value than the posted INV collateral should have supported. Reported losses cluster around $14.5 million to $15.6 million, including DOLA, ETH, WBTC, and YFI.

The event is a useful Market Health case because the attack was not only a smart-contract bug. It was a market-structure failure: a capital-intensive trade moved a thin reference market, the TWAP window absorbed the manipulated price, and the lending protocol treated that manipulated TWAP as collateral truth.

## Market Structure

The vulnerable structure had four parts:

- an INV reference market with limited depth relative to the attacker's capital;
- a TWAP oracle that sampled the manipulated market before the price fully normalized;
- a lending market that accepted INV-derived collateral value;
- borrowable assets with enough liquidity to make the manipulation profitable.

The attacker did not need to sustain a long-term fair value for INV. They only needed to keep the manipulated reference price alive long enough for the oracle and lending market to accept it.

## Signal 1: Reference-Pair Depth Gap

The first market-health warning is the gap between the liquidity used for pricing and the liquidity available elsewhere:

```text
reference_pair_depth_gap =
  attacker_available_capital / reference_pair_two_percent_depth
```

If this ratio is above 1, the reference pair can be moved materially by one actor. If it is above 5, that pair should not be trusted as a standalone collateral oracle without caps or cross-market checks. Inverse's incident shows why a DEX pair can be too thin for lending risk even when the token trades more broadly.

## Signal 2: TWAP Capture Window

TWAPs reduce single-block manipulation risk, but they do not remove manipulation if the attacker can afford the window:

```text
twap_capture_window =
  manipulated_price_duration / oracle_sampling_window
```

When this value approaches 1, the oracle becomes a delayed copy of the manipulated market. The risk is especially high when the lending market lets users borrow immediately after the TWAP updates.

## Signal 3: Collateral Inflation Ratio

The lending-market stress metric is how much the manipulated oracle inflates posted collateral value:

```text
collateral_inflation_ratio =
  oracle_reported_collateral_value / stress_price_collateral_value
```

If this ratio exceeds the market's liquidation buffer, a borrower can extract assets before liquidators or governance can respond. Inverse's Anchor market treated the inflated INV value as borrowable collateral, which allowed the attacker to borrow a multi-asset basket.

## Signal 4: Borrowable Liquidity Drain

The final risk is the share of available lending liquidity that can leave because of one manipulated collateral asset:

```text
borrowable_liquidity_drain =
  assets_borrowed_after_oracle_move / total_borrowable_assets
```

If one collateral oracle can unlock a large percentage of the borrowable pool, a local pricing problem becomes a protocol solvency problem. This is why oracle controls should be paired with borrow caps and asset-specific debt ceilings.

## Counterfactual Stress Test

Before enabling INV as collateral, Anchor could have been stress-tested against capital-intensive TWAP manipulation:

| Scenario            | Assumption                                                 | Market-health response                                      |
| ------------------- | ---------------------------------------------------------- | ----------------------------------------------------------- |
| Deep reference pair | Manipulation cost exceeds borrowable profit                | Normal operation with monitoring                            |
| Thin reference pair | One actor can move the pair for less than borrowable value | Cap borrowing and require cross-market confirmation         |
| TWAP capture        | Manipulated price persists for most of the sampling window | Freeze collateral updates until the reference price reverts |
| Liquidity drain     | Borrowing exceeds realistic liquidation recovery           | Disable new borrows and reduce debt ceiling                 |

The key control is not merely a longer TWAP. It is comparing manipulation cost with borrowable profit and refusing to lend when the oracle can be moved more cheaply than the assets it unlocks.

## Detection Table

| Signal                       | What changed                                           | Why it mattered                                              |
| ---------------------------- | ------------------------------------------------------ | ------------------------------------------------------------ |
| Reference-pair depth gap     | INV pricing relied on a manipulable DEX reference pair | The attacker's capital could move the collateral price       |
| TWAP capture window          | The manipulated price entered the oracle window        | The protocol accepted a distorted value after the trade      |
| Collateral inflation ratio   | INV collateral was valued above stress-market reality  | The borrower gained artificial borrowing power               |
| Borrowable liquidity drain   | DOLA, ETH, WBTC, and YFI were borrowed against INV     | A local oracle move became a multi-asset lending-market loss |
| Post-incident oracle changes | Inverse moved toward stronger oracle design            | The remediation confirms that oracle robustness was material |

## Practical Alert Rules

1. Reject a collateral oracle if manipulation cost is lower than borrowable liquidity.
2. Compare DEX reference-pair depth with centralized and decentralized venue liquidity before approving collateral.
3. Treat a TWAP as unsafe when one funded actor can dominate most of its sampling window.
4. Cap borrows for newly listed or thinly traded collateral until cross-market reference checks are live.
5. Alert when one collateral asset can unlock a multi-asset borrow basket larger than its stress-price value.
6. Delay borrowing after a large reference-price move until at least one clean sampling window has passed.

## Lessons for Market Health

Inverse Finance shows that a TWAP is a market-health control only when the market behind it is deep enough. If the reference pair is thin, the TWAP can transform a short manipulation into an official collateral price.

The broader lesson is that lending surveillance must monitor both price and manipulability. A collateral asset should be scored by reference-market depth, oracle-window capture risk, debt-ceiling exposure, and the borrowable liquidity it can unlock. Without those checks, a capital-intensive trade can become a solvency event.

## Sources

- [CertiK: Inverse Finance 02 April 2022](https://www.certik.com/blog/inverse-finance-02-april-2022)
- [CertiK: 2022 Year in Review - Lending Protocols](https://www.certik.com/resources/blog/2022-year-in-review-lending-protocols)
- [PYMNTS: Lending Protocol Inverse Finance Loses $15.6M in Crypto Following Hack](https://www.pymnts.com/cryptocurrency/2022/lending-protocol-inverse-finance-loses-15-6m-in-crypto-following-hack)
- [The Crypto Times: Lending Protocol Inverse Finance Lost $15.6M in Crypto](https://www.cryptotimes.io/2022/04/04/lending-protocol-inverse-finance-lost-15-6m-in-crypto/)
- [Web3 Is Going Great: Attack on Inverse Finance results in a $15.6 million loss](https://www.web3isgoinggreat.com/?id=inverse-finance-exploited)
- [CSIDB: Inverse Finance 2022-04-02 cyberattack incident](https://www.csidb.net/csidb/incidents/6065567f-3efa-47f4-9da6-3a5d6ee70165/)
