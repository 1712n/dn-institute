---
title: "Systematic Alpha Crypto and FX Futures Trade Allocation Abuse"
date: 2025-09-17
entities:
  - Systematic Alpha Management LLC
  - Peter Kambolin
  - Jersey City Partners LLC
---

## Summary

This case study analyzes Systematic Alpha Management as a market-health warning about post-execution trade allocation abuse in pools marketed as cryptocurrency and foreign-exchange futures strategies. On September 17, 2025, the CFTC announced that the U.S. District Court for the Southern District of Florida ordered Systematic Alpha Management LLC, a registered commodity trading advisor and commodity pool operator, and owner Peter Kambolin to pay more than $2.8 million for defrauding commodity pool participants.

The CFTC said the defendants improperly allocated profitable trades between two commodity pools and certain proprietary accounts, misled pool participants, and violated trade-allocation requirements. The consent order required $1,208,503 in restitution and $1,633,119 in disgorgement, with Jersey City Partners LLC jointly liable for $701,647 of the disgorgement because it received some ill-gotten gains.

For market-health review, Systematic Alpha is valuable because the misconduct was not a fake trading dashboard. Trading occurred, but the allocation mechanism allegedly moved profitable trades to proprietary accounts and losing or less profitable trades to pools. That makes the core signal an allocation-fairness problem: execution records must be matched to allocation timestamps, account eligibility, strategy mandates, and final account P&L.

The supporting dataset is available in [systematic-alpha-summary.csv](systematic-alpha-summary.csv).

## Trading Narrative

The CFTC's September 2025 release said that from January 2019 through November 2021, Systematic Alpha marketed itself as a CTA and CPO offering strategies in exchange-traded cryptocurrency and foreign-exchange futures. It ran at least two commodity pools while executing pool trades alongside proprietary account trades.

The abuse occurred after trades were executed. According to the CFTC, trades were allocated across the accounts each day, and profitable trades were consistently directed to proprietary accounts while losing or less profitable trades were assigned to the pools. This is a classic market-health concern because the fill itself may be real, but customer outcome depends on who receives the profitable fill.

The strategy-mandate problem adds another layer. The CFTC said the defendants misrepresented that the pools would primarily trade cryptocurrency and FX futures. If participants invest based on a particular strategy mix, allocation review must include not only trade fairness but also whether the pool actually received the promised exposure.

The related criminal case reinforces the harm measurement. The CFTC release said Kambolin pleaded guilty to conspiracy to commit commodities fraud, was sentenced in January 2024 to two years in prison followed by 18 months of home confinement, and was ordered to pay $1.63 million in criminal forfeiture and $1.2 million in restitution.

## False Market Signals

### Real trades with unfair allocation

Executed trades can still produce false pool performance if profitable fills are assigned away from participants. Reviewers should not stop at confirming that trades occurred.

### Daily allocation after execution

Post-execution daily allocation creates an opportunity to use hindsight. Allocation procedures should be pre-defined, timestamped, and consistently applied before trade outcomes are known.

### Proprietary account overlap

When manager accounts trade alongside customer pools, allocation rules and conflict controls must be explicit and tested.

### Strategy mix representation

Misrepresenting the pool's primary exposure can hide deviations from the promised risk profile. Crypto and FX futures strategies require instrument-level exposure review.

### Registered-status trust

Systematic Alpha was a registered CTA and CPO during the relevant period. Registration does not eliminate the need for allocation testing.

### Relief-defendant gain path

Jersey City Partners' disgorgement liability shows why reviewers should follow gains beyond the trading manager into related entities.

## Event Timeline

| Date or period     | Event                                                                                                 | Market-health signal                                            |
| ------------------ | ----------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| January 2019       | Relevant period began, according to the CFTC's 2025 release.                                          | Allocation controls should have existed before pooled trading.  |
| January 2019-2021  | SAM marketed strategies in exchange-traded cryptocurrency and FX futures.                             | Strategy exposure needed instrument-level verification.         |
| January 2019-2021  | SAM ran at least two pools while also trading proprietary accounts.                                   | Proprietary overlap required conflict-control testing.          |
| 2019-November 2021 | CFTC said profitable trades were directed to proprietary accounts and less favorable trades to pools. | Post-execution allocation created customer harm.                |
| April 28, 2023     | CFTC announced its complaint and restraining order.                                                   | Public enforcement challenged trade allocation and disclosures. |
| September 2023     | DOJ charged Kambolin with conspiracy to commit commodities fraud, according to the CFTC.              | Parallel criminal case reflected same allocation conduct.       |
| January 2024       | Kambolin was sentenced in the criminal case, according to the CFTC.                                   | Criminal restitution and forfeiture quantified related harm.    |
| September 4, 2025  | Court entered the CFTC consent order.                                                                 | Final order fixed restitution and disgorgement obligations.     |
| September 17, 2025 | CFTC announced the $2.8 million order.                                                                | Public release summarized final civil outcome.                  |

## Reconciliation Metrics

| Metric                          | Enforcement-record figure or claim                                   | Market-health interpretation                                   |
| ------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------- |
| Relevant period                 | January 2019 through November 2021                                   | Multi-year allocation review needed complete trade records.    |
| Civil restitution               | $1,208,503                                                           | Participant harm tied to allocation practices.                 |
| Civil disgorgement              | $1,633,119                                                           | Ill-gotten gain exceeded restitution.                          |
| Relief-defendant disgorgement   | $701,647 for Jersey City Partners                                    | Related entities can receive allocation-derived gains.         |
| Total civil relief              | More than $2.8 million                                               | Final order combined restitution and disgorgement.             |
| Criminal forfeiture             | $1.63 million                                                        | Criminal resolution aligned with ill-gotten-gain scale.        |
| Criminal restitution            | $1.2 million                                                         | Criminal redress aligned with pool-participant harm scale.     |
| Strategy represented            | Exchange-traded cryptocurrency and foreign-exchange futures          | Exposure claims required product-level validation.             |
| Account categories              | At least two commodity pools and proprietary accounts                | Customer and manager accounts required conflict controls.      |
| Allocation abuse alleged        | Profitable trades to proprietary accounts, worse trades to pools     | Allocation timing and method were core market-health controls. |
| Proprietary trading restriction | Six-year prohibition on trading commodity interests for own accounts | Sanction targeted conflict-risk channel.                       |
| Registration bar                | Permanent registration bar                                           | Final order removed regulated-intermediary status.             |

## Detection Checklist

1. Require pre-trade or pre-allocation rules that are timestamped before trade outcomes are known.
2. Reconcile fills, order IDs, execution times, and allocation times across all pool and proprietary accounts.
3. Compare average trade P&L by account type to identify systematic favorable allocation.
4. Test whether represented crypto and FX futures exposure matches actual instruments traded in each pool.
5. Review proprietary-account overlap and related-entity transfers as conflict-of-interest indicators.
6. Verify participant disclosures against actual allocation procedures and daily account statements.
7. Preserve legal posture: this article relies on CFTC order findings, CFTC release language, and public criminal-case summaries.

## Market-Health Lessons

Systematic Alpha shows that real exchange-traded activity can still produce false customer performance. The market-health problem is not whether an order was executed; it is whether the resulting fill was allocated fairly.

The case also shows why proprietary accounts require strict controls when traded alongside customer pools. If the manager can wait to see which trades are profitable before assigning them, the pool's reported return is no longer an unbiased result of the strategy.

Finally, crypto and FX futures labels need instrument-level testing. A pool can be marketed around popular strategy categories while actual allocations and exposures tell a different story.

## References

- [CFTC press release 9127-25, September 17, 2025](https://www.cftc.gov/PressRoom/PressReleases/9127-25)
- [CFTC consent order against Systematic Alpha Management, Peter Kambolin, and Jersey City Partners, September 4, 2025](https://www.cftc.gov/media/12691/enfSystematicAlphaConsentOrder090425/download)
- [CFTC press release 8697-23, April 28, 2023](https://www.cftc.gov/PressRoom/PressReleases/8697-23)
- [CFTC statutory restraining order in CFTC v. Systematic Alpha Management, April 24, 2023](https://www.cftc.gov/media/8516/enfsystematicalphamanagementorder042423/download)
