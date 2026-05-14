---
title: "Zunami UZD price-manipulation market-health case"
date: "2023-08-13"
description: "Zunami Protocol lost about 1,178 ETH after a flash-loan-funded sequence manipulated internal token pricing and inflated the attacker's UZD balance."
entities:
  - Zunami Protocol
  - UZD
  - zETH
  - Stake DAO
  - Curve
  - SushiSwap
---

Zunami Protocol was exploited on Ethereum on August 13, 2023 after an attacker
used flash-loan liquidity to manipulate pricing inputs used by the protocol's
stable-token accounting. Public analyses describe the exploit as a price
manipulation attack against Zunami's zStables system: the attacker moved
temporary liquidity through Curve, SushiSwap, Uniswap V3, and Balancer paths,
inflated internal asset-price calculations, and then redeemed the inflated UZD
balance for external liquidity.

The incident produced a reported loss of 1,178 ETH, or about 2.16 million
dollars at the time. It is a useful market-health case because the externally
visible failure was not simply a missing access-control check. The critical
signal was that a token-balance formula trusted an asset-price cache that could
be moved by temporary liquidity, turning a short-lived price distortion into a
much larger redeemable balance.

## Incident metrics

| Signal             | Observation                                                                             | Market-health interpretation                                                         |
| ------------------ | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Exploit date       | The attack occurred on August 13, 2023                                                  | Same-day liquidity and peg monitors should cover stablecoin aggregators              |
| Reported loss      | DN Institute and CertiK report 1,178 ETH or about 2.16 million dollars in loss          | A balance-pricing defect created material stable-token redemption exposure           |
| Flash-loan scale   | CertiK reports two exploit runs and roughly 32.4 million dollars of flash-loan notional | Manipulation capital should be compared with strategy liquidity before price caching |
| Balance inflation  | CertiK reports the attacker's UZD balance rose from about 4.8 million to 16.9 million   | Sudden account-balance jumps can reveal asset-price cache manipulation               |
| Pricing dependency | Halborn describes a token-price calculation based on pool holdings and token supply     | Internal pool-value formulas need external and time-weighted sanity checks           |
| User warning       | Zunami warned users not to buy zETH or UZD after the emission attack                    | Stable-token warnings are market-confidence and liquidity-risk signals               |
| Fund movement      | DN Institute notes stolen funds were routed to Tornado Cash after the exploit           | Mixer routing helps classify the event as adversarial rather than market stress      |

The companion `zunami-uzd-market-signals.csv` file records exploit-date, loss,
flash-loan, balance-inflation, pricing-dependency, user-warning, and fund-flow
signals for reuse in market-health dashboards.

## Manipulation path

The exploit converted a temporary liquidity state into a persistent accounting
benefit:

1. The attacker funded an exploit contract and sourced large temporary
   liquidity from Balancer and Uniswap V3.
2. The attacker swapped through Curve and SushiSwap routes that affected the
   strategy inputs behind Zunami's UZD accounting.
3. The attacker called the asset-price caching path while the manipulated state
   was active.
4. The inflated cached price increased the attacker's apparent UZD balance by
   more than three times according to CertiK's analysis.
5. The attacker redeemed inflated UZD balances through Zunami pools for crvFRAX
   and crvUSD liquidity.
6. The proceeds were swapped back, the flash loans were repaid, and the
   remaining funds were routed away from the protocol.

For market-health monitoring, the high-signal moment is step 3. A temporary
swap and donation sequence became dangerous only because the protocol accepted
the manipulated price while computing user balances. That makes the case
especially relevant to stablecoin issuers, yield aggregators, and vault systems
that cache internal asset values.

## Detection controls

Zunami points to controls that reduce the chance of converting a temporary pool
state into redeemable value:

- **Flash-loan notional gates:** compare transaction notional with strategy
  depth before accepting price-cache updates or large redemptions.
- **Cached-price drift limits:** block balance updates when a cached asset
  price moves sharply from the previous block or from an external reference.
- **Balance-multiplier alerts:** flag accounts whose redeemable balance
  increases several times without an equivalent external deposit.
- **Stable-token peg monitors:** alert when UZD, zETH, or related pool routes
  show a rapid price break after cache updates.
- **Route concentration checks:** track whether one transaction both moves
  strategy prices and redeems against the affected stable-token pools.
- **Emergency-user-warning capture:** ingest protocol warnings about not buying
  affected tokens as market-health events, not only social-media updates.

These controls would not rely on knowing the attacker's intent in advance. They
focus on measurable state changes: unusually large temporary liquidity, cache
updates during manipulated routes, and a mismatch between deposited value and
redeemable balances.

## Lessons for market health

Zunami shows why stable-token market health must include protocol-internal
pricing paths. A token can appear to fail suddenly at the market layer while
the root cause is an accounting path that temporarily overstates user balances.
In those systems, external pool prices, internal total-holdings formulas,
cached asset prices, and redemption flows all belong in the same risk view.

The strongest operational signal is a same-transaction cluster where flash-loan
liquidity moves strategy prices, cache values update, an account balance jumps,
and redemptions drain stable pools. A dashboard that joins those signals can
pause redemptions or require manual review before a distorted accounting state
becomes a permanent loss.

## References

- [DN Institute cyberattack incident: Zunami Protocol](https://dn.institute/research/cyberattacks/incidents/2023-08-13-zunami-protocol/)
- [CertiK: Zunami Protocol Incident Analysis](https://www.certik.com/ko/blog/zunami-protocol-incident-analysis)
- [Halborn: Explained - The Zunami Protocol Hack](https://www.halborn.com/blog/post/explained-the-zunami-protocol-hack-august-2023)
- [Decrypt: Zunami Protocol Loses Over $2.1 Million in Price Manipulation Hack](https://decrypt.co/152366/zunami-protocol-curve-finance-hack)
