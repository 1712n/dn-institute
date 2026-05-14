---
title: "Themis Protocol Balancer LP oracle market-health case"
date: "2023-06-27"
description: "Themis Protocol lost about $370,000 on Arbitrum after a flash-loan-funded sequence manipulated Balancer LP token pricing used by the protocol's lending oracle."
entities:
  - Themis Protocol
  - Balancer
  - Arbitrum
  - WETH
---

Themis Protocol was exploited on Arbitrum on June 27, 2023 after an attacker
manipulated Balancer LP token pricing that Themis used for collateral
valuation. Public analyses describe the root cause as an inaccurate Balancer LP
token price oracle: by moving liquidity inside the Balancer pool, the attacker
inflated the LP token valuation, borrowed more assets than the deposited
collateral should have supported, and converted the proceeds through DeFi
venues.

The loss was reported at roughly 370,000 dollars. Themis had only recently
entered beta on Arbitrum, so the incident also became a market-health signal
about new-market collateral onboarding: a young lending venue accepted an LP
token valuation path that could be moved by a flash-loan-sized transaction.
That made the external symptom look like a normal borrow and liquidity event
until the inflated collateral rate was compared against the underlying pool
state.

## Incident metrics

| Signal            | Observation                                                                    | Market-health interpretation                                                    |
| ----------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| Exploit date      | The exploit was reported on June 27, 2023 on Arbitrum                          | New-chain deployments need same-day transaction surveillance                    |
| Reported loss     | Public analyses and the DN incident page report about 370,000 dollars in loss  | A small LP oracle error created material lending-market exposure                |
| Flash-loan input  | The attacker sourced large temporary WETH liquidity before manipulating price  | Temporary liquidity size should be compared with collateral-pool depth          |
| Collateral action | The attacker deposited WETH into a Balancer pool and received LP tokens        | LP collateral can embed pool-composition risk invisible in token balances alone |
| Oracle weakness   | Themis accepted a manipulated Balancer LP token price                          | Spot LP-token valuation can transmit pool manipulation into borrow limits       |
| Asset extraction  | Borrowed assets included stablecoins, ARB, and WBTC according to public traces | Multi-asset drains reveal that one oracle path can contaminate several markets  |
| Response signal   | Themis suspended borrowing and later described compensation / Themis 2.0 steps | Pause and migration plans are market-health data for user-confidence monitoring |

The companion `themis-balancer-market-signals.csv` file records these exploit,
loss, collateral, oracle, asset-extraction, and response signals for reuse.

## Manipulation path

The exploit turned a collateral-rate distortion into cross-asset borrowing:

1. The attacker sourced temporary WETH liquidity.
2. The attacker interacted with the Balancer pool so that the LP token rate used
   by Themis became inflated.
3. The inflated LP valuation increased apparent collateral value.
4. The attacker borrowed multiple assets against the manipulated collateral
   reading.
5. The attacker converted and routed proceeds after the transaction sequence.
6. Themis suspended borrowing functions and later announced upgrade and
   compensation steps.

The market-health lesson is that LP-token collateral should not be treated as a
simple spot-priced asset. The apparent collateral value is a derivative of pool
composition, external token prices, rate math, and transaction ordering. When
that derived value is accepted without depth and manipulation checks, one
distorted pool state can unlock several borrow markets.

## Detection controls

Themis points to controls that should be active before a new lending market is
opened:

- **LP collateral depth checks:** compare a flash-loan-sized swap or deposit
  against pool depth before accepting the resulting LP-token rate.
- **Independent LP valuation:** recompute LP value from underlying reserves,
  conservative token prices, and previous-block rates before allowing a borrow.
- **Borrow-spread alerts:** flag one transaction that borrows several unrelated
  assets after a single LP collateral valuation jump.
- **New-market quarantine:** apply tighter borrow caps and manual review windows
  during the first weeks after a new chain or market deployment.
- **Pool-composition monitors:** alert when the underlying Balancer pool
  composition changes sharply in the same block as collateral enablement or
  borrowing.
- **Pause and compensation tracking:** treat borrowing suspension, migration
  announcements, and compensation plans as market-health signals that affect
  liquidity expectations.

These controls help distinguish legitimate LP collateral use from a temporary
pool-rate artifact. They also reduce the chance that a single manipulated
collateral source drains stablecoin, governance-token, and wrapped-asset
markets together.

## Lessons for market health

The Themis incident is a compact example of new-market oracle fragility. It did
not require a broad collapse in WETH or ARB markets. It required a derived
Balancer LP token price to be trusted at the wrong time, on a young Arbitrum
deployment with enough borrowable assets available to make the transaction
profitable.

For market-health teams, the high-signal pattern is a sudden LP valuation jump,
flash-loan-sized liquidity movement, collateral enablement, and immediate
multi-asset borrowing. That pattern should trigger a borrow cap, conservative
valuation fallback, or manual review before the pool-rate distortion is allowed
to leave the system as debt.

## References

- [DN Institute cyberattack incident: Themis Protocol](https://dn.institute/research/cyberattacks/incidents/2023-06-27-themis-protocol/)
- [Olympix: Themis Protocol Price Oracle Exploited $370K](https://olympix.security/blog/themis-protocol-price-oracle-exploited-370k)
- [SolidityScan: Themis Protocol Hack Analysis](https://blog.solidityscan.com/themis-protocol-hack-analysis-7241f6470b2e/)
- [CryptoRank: Themis Protocol $370,000 Damage Due To Flashloan Attack](https://cryptorank.io/news/feed/1ea76-198354-themis-protocol-370000-damage-due-to-flashloan-attack)
- [DefiLlama: Themis Protocol exploit record](https://defillama.com/protocol/themis-protocol?denomination=ARB)
