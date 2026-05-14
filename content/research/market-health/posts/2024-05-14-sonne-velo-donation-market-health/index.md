---
title: "Sonne Finance VELO donation-attack market-health case"
date: "2024-05-14"
description: "Sonne Finance lost about $20 million after a newly listed VELO market let an attacker inflate soVELO exchange-rate collateral through a known Compound v2 donation-attack pattern."
entities:
  - Sonne Finance
  - VELO
  - soVELO
  - Optimism
  - Compound v2
---

Sonne Finance was exploited on Optimism on May 14, 2024 after a newly added
VELO market exposed a known Compound v2 fork donation-attack pattern. The loss
was widely reported at about 20 million dollars across WETH, WBTC, USDC, USDT,
wstETH, and VELO-linked assets. The incident is a useful market-health case
because the dangerous condition was not only a smart-contract edge case. It was
a live market state: a fresh collateral market, near-empty supply, permissionless
timelock execution, a large direct token transfer into the soVELO contract, and
borrowing against an exchange rate that no longer represented organic liquidity.

The issue began with governance approval for Sonne Improvement Proposal 15,
which added VELO markets to Sonne on Optimism. Public analyses describe the
deployment path as a multi-transaction process: the market was created, c-factors
were scheduled after a two-day timelock, and the relevant operations could be
executed permissionlessly once the timelock expired. That gave the attacker room
to interact with the market at the weakest point in its life cycle, before it had
normal liquidity history or a stable collateral base.

## Incident metrics

| Signal             | Observation                                                                                     | Market-health interpretation                                                                   |
| ------------------ | ----------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Market age         | The exploit centered on a newly added VELO market after SIP-15 passed                           | New collateral listings should start with strict debt ceilings and delayed borrow enablement   |
| Liquidity surface  | The attacker minted only 2 wei of soVELO before manipulating the market                         | Very low share-token supply makes exchange-rate jumps easier to create and harder to interpret |
| Donation pressure  | A large VELO transfer was sent directly into the soVELO contract without matching share minting | Donation deltas can turn accounting state into an artificial collateral-price signal           |
| Exchange-rate jump | CertiK reported 1 wei of soVELO being valued at more than 17.7 million VELO after manipulation  | Exchange-rate moves that outrun real liquidity should be treated like oracle divergence        |
| Borrow output      | The inflated soVELO state allowed borrowing against WETH and other Sonne markets                | Collateral-market manipulation can propagate into unrelated borrow assets                      |
| Loss estimate      | Public reports place the drain near 20 million dollars                                          | A single newly listed market created protocol-wide solvency damage                             |
| Detection window   | Sonne became aware roughly 25 minutes after the attack began                                    | New-market monitoring needs automatic pause thresholds, not only manual response               |

The companion `sonne-velo-market-signals.csv` file records the governance,
timelock, exchange-rate, loss, and response signals in a source-linked table.

## Manipulation path

The attack path had a familiar Compound v2 fork shape:

1. A new soVELO collateral market was created after governance approval.
2. The attacker interacted with the newly created market while total soVELO
   supply was tiny.
3. VELO was transferred directly into the soVELO contract, increasing
   `totalCash` without minting proportional soVELO supply.
4. The soVELO exchange rate increased sharply because the exchange-rate formula
   divided a much larger underlying balance by a tiny supply.
5. The attacker borrowed against the manipulated collateral value.
6. Rounding behavior in `redeemUnderlying` let the attacker recover donated VELO
   while paying less soVELO than the economic value implied.
7. The sequence was repeated across markets until Sonne paused Optimism markets.

This is a market-health failure because the protocol accepted an accounting
exchange rate as a collateral signal even while the market had no mature depth.
For an established collateral market, an exchange-rate increase may reflect
yield or normal pool growth. For a new market with only wei-level share supply,
a sudden direct balance transfer is closer to price manipulation than yield.

## Detection controls

Sonne shows why lending-market surveillance should treat new collateral listings
as a separate risk class. Useful controls include:

- **New-market debt ceilings:** keep borrow limits near zero until a collateral
  market has meaningful supply, deposit diversity, and time-weighted liquidity.
- **Minimum-share-supply gates:** block collateral use while total share-token
  supply is so low that a small denominator can create extreme exchange rates.
- **Donation-delta alerts:** flag direct underlying-token transfers into cToken
  or soToken contracts when they are not paired with ordinary mint flows.
- **Exchange-rate velocity limits:** pause collateral use when the share exchange
  rate jumps faster than interest accrual, fees, or external price movement can
  justify.
- **Atomic listing execution:** batch listing, seeding, reserve setup, and
  collateral-factor changes so attackers cannot reorder the weakest steps.
- **Executor restrictions:** prevent permissionless execution from becoming a
  market-timing tool during sensitive listing windows.

These controls are intentionally market-facing. They do not rely only on a code
fix for a known precision-loss bug. They ask whether the collateral market has a
healthy enough state to support borrowing at all.

## Lessons for market health

The Sonne exploit is a reminder that collateral onboarding is a live market
event. A token can be approved by governance and still be unsafe as borrowable
collateral if the listing process leaves a thin, reorderable market in between
proposal approval and mature liquidity. Market-health dashboards should not only
track token prices and total value locked. They should track market age,
share-token supply, direct underlying transfers, exchange-rate velocity,
collateral-factor changes, and borrow attempts in the same window.

For risk teams, the highest-signal alert is the combined pattern: a newly listed
collateral market, tiny share supply, direct donation into the market contract,
an extreme exchange-rate jump, and same-window borrowing from other pools. That
pattern should trigger a pause or collateral haircut even before a full incident
classification is complete.

## References

- [Sonne Finance post-mortem: Sonne Finance Exploit](https://medium.com/@SonneFinance/post-mortem-sonne-finance-exploit-12f3daa82b06)
- [CertiK: Sonne Finance Incident Analysis](https://www.certik.com/blog/sonne-finance-incident-analysis)
- [Halborn: Explained: The Sonne Finance Hack (May 2024)](https://www.halborn.com/blog/post/explained-the-sonne-finance-hack-may-2024)
- [Verichains: Compound V2 Forked Vulnerability - $20M Sonne Finance Hack](https://blog.verichains.io/p/compound-v2-forked-vulnerability)
- [CryptoNews/BSC News: Sonne Finance Hacked for $20M, Markets Paused on Optimism Network](https://cryptonews.net/news/security/29035852/)
- [Sonne Improvement Proposal 15](https://snapshot.org/#/sonnefi.eth/proposal/0x6f3f62efc77e8c501bf71812d2fdc064710a45618d65736ed886cca38ed16fa3)
- [Attack transaction on Optimism](https://optimistic.etherscan.io/tx/0x9312ae377d7ebdf3c7c3a86f80514878deb5df51aad38b6191d55db53e42b7f0)
