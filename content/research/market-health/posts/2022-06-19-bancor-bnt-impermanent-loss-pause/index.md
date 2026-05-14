---
title: "Bancor BNT Impermanent-Loss Protection Pause"
date: 2022-06-19
entities:
  - Bancor
  - BNT
  - Bancor DAO
  - Celsius
  - Three Arrows Capital
---

## Summary

On June 19-20, 2022, Bancor temporarily paused impermanent-loss protection during the broader crypto-liquidity crisis. [Bancor's documentation](https://support.bancor.network/bancor-amm/bancor-3-mechanics/pause-of-bnt-distribution) says extreme market conditions exposed an economic vulnerability: heavy BNT selling pressure, large token withdrawals, AMM rebalancing, and BNT distribution needs created a possible runaway effect in BNT price.

[The Crypto Times reported](https://www.cryptotimes.io/2022/06/20/bancor-halts-impermanent-loss-protection-amid-market-conditions/) that Bancor paused impermanent-loss protection and stopped accepting deposits, while withdrawals during the unstable period would not be covered by protection. [Web3 is Going Great summarized](https://www.web3isgoinggreat.com/single/2022-06-19-1) Bancor's explanation that two large centralized entities had rapidly liquidated BNT positions and withdrawn liquidity, and that another entity had opened a large BNT short.

The core market-health issue was reflexive insurance design. Bancor's impermanent-loss protection relied on BNT distribution. When BNT itself came under stress, using more BNT to cover withdrawals could increase selling pressure, worsen deficits, and advantage the fastest exits over slower liquidity providers.

## Manipulation Analysis

The first stress vector was BNT price reflexivity. If protection payments are made in the protocol's own token, then falling token price increases the number of tokens needed to cover the same dollar deficit. That additional issuance or distribution can create more sell pressure and deepen the next deficit.

The second vector was liquidity-provider exit sequencing. Bancor's documentation says the runaway effect could have allowed the fastest liquidity providers to withdraw while later liquidity providers became unable to withdraw at all. This is a market-health problem because the protocol's queue dynamics determine who bears losses.

The third vector was concentrated external pressure. Reports around the pause described large centralized entities exiting BNT and liquidity positions, plus a large short position against BNT. Whether those flows were defensive deleveraging or active pressure, they were large enough to interact with protocol mechanics.

The fourth vector was promise-to-mechanism mismatch. Users saw "impermanent-loss protection" as a risk-control feature, but the feature was disabled exactly when losses and withdrawals were most likely. Market Health should track not just promised protections but the conditions under which protections can be paused.

## Metrics Used

### BNT price and sell pressure

The primary signal is whether BNT price decline is accelerating while protocol protection obligations are rising.

Useful metrics include:

- BNT price change over one-hour, one-day, and one-week windows;
- BNT spot depth within 2%, 5%, and 10% of mid price;
- net BNT sold by large wallets;
- BNT short interest or borrow demand where observable;
- BNT distribution needs in token units and dollar units.

### Withdrawal deficit and coverage load

Impermanent-loss protection needs to be monitored as a liability.

Useful metrics include:

- pending withdrawals by pool;
- pool deficits before and after rebalancing;
- estimated BNT needed to cover deficits;
- ratio of coverage load to BNT market depth;
- share of protection obligations concentrated in the largest pools.

### Exit-order fairness

The pause was partly about preventing a fastest-exit advantage.

Useful metrics include:

- withdrawal queue size;
- first-exit versus last-exit recovery estimates;
- time between protection pause and withdrawal attempts;
- large-wallet withdrawals before public announcements;
- remaining pool liquidity after major exits.

### Protection-pause governance

Emergency controls matter only if users can observe and price them.

Useful metrics include:

- whether protection is active, paused, or partially active;
- decision authority for emergency pauses;
- time between observed stress and pause decision;
- user-facing withdrawal terms during the pause;
- restart criteria and progress updates.

The same fields are summarized in [bancor-bnt-il-protection-signals.csv](bancor-bnt-il-protection-signals.csv) for dataset-based review.

| Signal               | Observation                                                             | Market-health interpretation                                  |
| -------------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------- |
| BNT distribution     | Bancor said BNT distribution was paused on June 19                      | Protection liabilities need token-supply and depth monitoring |
| Runaway effect       | Bancor warned BNT coverage could create a runaway price effect          | Native-token insurance can become reflexive under stress      |
| Deposit pause        | Reporting said deposits were stopped while trading stayed active        | Protocol controls can split trading, deposit, and exit risk   |
| Large-entity exits   | Public summaries cited large centralized-entity BNT and liquidity exits | Concentrated exits can stress protection mechanisms           |
| Uncovered withdrawal | Withdrawals during the unstable period were not IL-protected            | User protection terms can change during worst-case conditions |

## Timeline

- **Early June 2022:** The broader crypto credit crisis increased pressure on lenders, liquidity providers, and protocol-native tokens.
- **June 19, 2022:** Bancor paused BNT distribution under the DAO's emergency intervention policy.
- **June 20, 2022:** Public reporting described the pause of impermanent-loss protection, the deposit halt, and withdrawal limitations.
- **After the pause:** Bancor continued to communicate progress updates and framed the pause as necessary to prevent a worse exit-race outcome.

## Market Health Lessons

Bancor shows that insurance and protection mechanisms need their own market-health dashboards. A protection promise can fail economically before it fails technically.

For AMMs and DeFi insurance-like systems, dashboards should track protection liabilities against token depth, token issuance, large-wallet exits, short pressure, and withdrawal queue fairness. If protection depends on the same token that is under attack or heavy selling pressure, the protocol needs circuit breakers before the protection mechanism turns into a reflexive stress amplifier.
