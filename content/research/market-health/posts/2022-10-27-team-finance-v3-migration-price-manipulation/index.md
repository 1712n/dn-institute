---
title: "Team Finance V3 migration price-manipulation market-health case"
date: "2022-10-27"
description: "Team Finance lost about $14.5 million after an attacker abused its Uniswap v2-to-v3 migration flow, manipulated the V3 initialize price, and extracted refund value."
entities:
  - Team Finance
  - Uniswap v2
  - Uniswap v3
  - WETH
  - DAI
  - CAW
  - TSUKA
---

Team Finance was exploited on October 27, 2022 during a migration path from
Uniswap v2 to Uniswap v3. The attacker abused the migration logic for locked LP
positions, created attacker-controlled migration conditions, manipulated the
V3 pool initialize price, and received refunds that extracted value from the
affected liquidity positions.

The reported loss was about 14.5 million dollars across WETH, DAI, CAW, and
TSUKA. The attacker later returned about 7 million dollars to associated
projects, but the initial drain is still a useful market-health case. The
incident shows that migration functions can create market-manipulation risk
even when the underlying assets are not failing: a bad migration price can
turn a liquidity-management operation into a value-extraction route.

## Incident metrics

| Signal              | Observation                                                                         | Market-health interpretation                                                        |
| ------------------- | ----------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Exploit date        | The malicious migration transaction executed on October 27, 2022                    | Migration windows need same-day liquidity and refund monitoring                     |
| Reported loss       | DN Institute and public analyses report about 14.5 million dollars in assets stolen | Migration price mistakes can create multi-asset market exposure                     |
| Affected assets     | DN Institute lists ETH, DAI, CAW, and TSUKA as affected assets                      | Refund extraction should be tracked by token, not only aggregate loss               |
| Price input         | Neptune Mutual describes manipulation of the V3 initialize price path               | User-controlled initialization price is a high-risk market input                    |
| Validation weakness | Halborn describes a flawed migrate function and attacker-controlled V3 pair         | Migration target validation is part of market-health control, not only code hygiene |
| Recovery signal     | Public reports say about 7 million dollars was returned after the exploit           | Returned funds should be separated from the original liquidity shock                |
| Audit context       | Public reporting noted the migration function had been audited before the incident  | Passing audit status should not suppress live market-risk monitoring                |

The companion `team-finance-v3-migration-signals.csv` file records exploit,
loss, affected-asset, price-input, validation, recovery, and audit-context
signals for reuse.

## Manipulation path

The exploit converted migration mechanics into market-value extraction:

1. The attacker deployed an attack contract and generated a synthetic token
   used to prepare the migration path.
2. The attacker used Team Finance locking flows to create LP-token positions
   that could later be used during migration.
3. The vulnerable migration path did not sufficiently bind the migration to the
   intended token pair, pool, withdrawal address, and price context.
4. The attacker supplied a manipulated Uniswap v3 initialization price through
   the `sqrtPriceX96` parameter.
5. The migration refund calculation operated against that skewed price.
6. The attacker extracted WETH, DAI, CAW, and TSUKA value before later
   returning part of the funds.

For market-health monitoring, the key point is that liquidity migration is a
price event. It changes pool version, pool shape, price range, and refund
calculations. If those values are user-controllable or weakly validated, the
migration process can become a market manipulation surface.

## Detection controls

Team Finance points to controls that should cover protocol migrations:

- **Migration-price bounds:** compare requested V3 initialize price against
  pre-migration v2 reserves, external references, and recent TWAP data.
- **Target-pair validation:** require that token pair, pool address, withdrawal
  address, and lock metadata match the original locked position.
- **Refund-size alerts:** flag refunds that are large relative to the migrated
  LP position or that transfer several unrelated assets at once.
- **Per-token liquidity shock monitors:** track WETH, DAI, CAW, and TSUKA
  outflows separately during migrations.
- **Synthetic-token checks:** reject or quarantine migrations involving newly
  created tokens or attacker-controlled intermediate pairs.
- **Audit-context overrides:** continue live monitoring on audited functions
  when they touch prices, external pools, or migration refunds.

These controls do not depend on guessing the attacker. They focus on the
observable mismatch between a migration's expected pool state and the actual
price, pair, and refund outputs.

## Lessons for market health

Team Finance shows that maintenance operations can become market-health events.
A migration from one AMM design to another changes more than contract storage:
it can move liquidity across pricing formulas, introduce range-based V3 price
parameters, and create refund mechanics whose outputs depend on market state.

The strongest operational signal is a migration transaction with a manipulated
initialize price, synthetic or mismatched token setup, abnormal refund size,
and multi-asset outflow. Market-health dashboards should treat those signals
with the same urgency as spot-oracle manipulation because both paths allow a
distorted price to leave the system as real transferred value.

## References

- [DN Institute cyberattack incident: Team Finance](https://dn.institute/research/cyberattacks/incidents/2022-10-27-team-finance/)
- [Halborn: Explained - The Team Finance Hack](https://www.halborn.com/blog/post/explained-the-team-finance-hack-october-2022)
- [Neptune Mutual: Decoding Team Finance Contract Vulnerability](https://neptunemutual.com/blog/decoding-team-finance-contract-vulnerability/)
- [CoinDesk: Attacker Behind Team Finance Exploit Returns Funds](https://www.coindesk.com/tech/2022/10/31/attacker-behind-145m-team-finance-exploit-returns-7m/)
