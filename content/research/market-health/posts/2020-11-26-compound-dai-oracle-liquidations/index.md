---
title: "Compound DAI Oracle Price Spike Liquidations"
date: 2020-11-26
entities:
  - Compound
  - DAI
  - Coinbase Pro
  - Open Price Feed
  - cDAI
---

## Summary

On November 26, 2020, a short-lived DAI price spike on Coinbase Pro triggered large liquidations on Compound. [Decrypt reported](https://decrypt.co/49657/oracle-exploit-sees-100-million-liquidated-on-compound) that about $89 million in loans were liquidated after DAI traded at a roughly 30% premium on Coinbase, whose price data was used by Compound's oracle. [ForkLog reported](https://forklog.com/en/dai-price-spike-on-coinbase-triggers-100m-liquidations-on-compound/) the same mechanism: DAI rose from about $1 to $1.30 on Coinbase, increasing the apparent value of DAI-denominated debt and pushing borrowers below liquidation thresholds.

The core market-health failure was an oracle-source concentration problem. Compound's contracts behaved according to the price inputs they received, but the input market temporarily diverged from broader DAI pricing. A stablecoin price dislocation on a reference venue became a liquidation trigger across a much larger lending book.

This case is useful for Market Health because it shows how thin venue liquidity, single-source price dependence, and liquidation incentives can convert a transient spot-market anomaly into realized borrower losses. It is also a reminder that stablecoin debt is not risk-free when protocol accounting depends on a fragile external price feed.

## Manipulation Analysis

The first manipulation vector was venue-specific DAI price pressure. A borrower who owes DAI becomes riskier when the oracle says DAI is worth more than one dollar. If a reference venue briefly prints DAI at $1.30, then every DAI borrower's debt increases by 30% in protocol accounting, even if the broader market still treats DAI as near one dollar.

The second vector was oracle-source concentration. [Compound's community discussion](https://www.comp.xyz/t/dai-liquidation-event/642) recorded users debating whether the Coinbase Pro DAI move was a fair market price, a manipulated venue print, or an oracle-design failure. For surveillance purposes, the key issue is that one venue's dislocation was sufficient to affect protocol solvency decisions.

The third vector was liquidator incentive capture. [Decrypt reported](https://decrypt.co/49657/oracle-exploit-sees-100-million-liquidated-on-compound) that a large liquidator profited from the event, and the liquidation system created immediate incentives to repay DAI debt and seize collateral once the oracle value moved. Even if the price move was not proven malicious, the structure created an attractive manipulation target.

The fourth vector was recovery governance. [A later Compound forum thread](https://www.comp.xyz/t/dai-liquidation-compensation/684) documented compensation discussion for users liquidated during the event, including the fact that Coinbase Pro DAI reached $1.30 and impacted DAI borrowers requested compensation. Post-event governance signals matter because they affect how future users price oracle and liquidation risk.

## Metrics Used

### Oracle-reference venue divergence

The primary signal is the gap between the protocol oracle price and broad-market DAI prices.

Useful metrics include:

- DAI price on each oracle source;
- DAI volume-weighted price across major venues;
- maximum oracle-source premium over broad-market DAI;
- duration of the dislocation;
- order-book depth needed to move DAI from $1.00 to the oracle price.

### Debt repricing and liquidation threshold pressure

The lending-market signal is how the oracle print changes borrower health.

Useful metrics include:

- total DAI borrowed before the event;
- number of accounts moved below liquidation threshold by the DAI premium;
- debt value change by borrower size bucket;
- largest liquidation caused by the price print;
- share of liquidated accounts that were healthy under broad-market DAI pricing.

### Liquidator concentration

Liquidation markets can amplify oracle anomalies when a few liquidators are positioned to act first.

Useful metrics include:

- liquidation volume by liquidator;
- collateral seized by liquidator;
- liquidation bonus captured;
- time between oracle update and liquidation transaction;
- gas paid by successful and failed liquidators.

### Recovery and compensation status

Governance response becomes part of long-tail market confidence.

Useful metrics include:

- addresses affected by the liquidation event;
- amount of collateral seized;
- governance proposals for compensation;
- final compensation decision;
- oracle-design changes after the event.

The same fields are summarized in [compound-dai-oracle-liquidation-signals.csv](compound-dai-oracle-liquidation-signals.csv) for dataset-based review.

| Signal               | Observation                                                            | Market-health interpretation                                      |
| -------------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------- |
| DAI price spike      | Reporting and forum records cite Coinbase Pro DAI reaching about $1.30 | Single-venue stablecoin dislocations can reprice protocol debt    |
| Liquidation volume   | Decrypt reported about $89 million in Compound liquidations            | Oracle anomalies can become realized borrower losses              |
| Reference dependence | ForkLog and Decrypt described Coinbase-based price data in the oracle  | Venue-source concentration is a liquidation-market risk           |
| Liquidator profit    | Decrypt reported a major liquidator profited during the event          | Liquidation incentives can make oracle anomalies attractive       |
| Compensation debate  | Compound governance discussed compensation for affected DAI borrowers  | Recovery policy affects trust after oracle-triggered liquidations |

## Timeline

- **November 26, 2020:** DAI traded at a large premium on Coinbase Pro during a broader market stress window.
- **November 26, 2020:** Compound's oracle input reflected the elevated DAI price, increasing DAI-denominated debt values.
- **November 26, 2020:** Compound positions borrowing DAI were liquidated, with reporting estimating about $89 million to $100 million in total liquidation volume.
- **November 27-28, 2020:** Compound community members and affected users debated whether the event was a fair market dislocation, an oracle issue, or intentional manipulation.
- **After the event:** Governance discussions continued around compensation and stronger oracle design.

## Market Health Lessons

Compound's DAI liquidation event shows that a price feed can be fresh and still unsafe. Lending protocols need to understand whether the venue behind the feed can support the amount of debt exposed to that price.

For market-health dashboards, stablecoin oracle prices should be monitored against multi-venue depth, medianized spot prices, and historical peg bands. If a single venue's DAI price jumps far above the broader market, liquidation systems should slow down, require additional confirmation, cap liquidation size, or switch to a fallback price source before borrower losses become irreversible.
