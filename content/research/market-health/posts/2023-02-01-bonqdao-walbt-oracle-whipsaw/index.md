---
title: "BonqDAO WALBT Oracle Whipsaw"
date: 2023-02-01
entities:
  - BonqDAO
  - AllianceBlock
  - WALBT
  - BEUR
  - Tellor
---

## Summary

1. BonqDAO's February 2023 incident is a clean market-health case because the same oracle path was used twice: first to overprice WALBT collateral, then to underprice the same collateral so other troves could be liquidated.
2. Public reconstructions agree that the attacker staked only 10 TRB with TellorFlex, submitted an extreme WALBT price, opened a WALBT trove with 0.1 WALBT collateral, and minted 100 million BEUR.
3. About two minutes later, the attacker submitted a very low WALBT price, pushing many existing WALBT troves below liquidation thresholds and allowing the attacker to collect roughly 113 million WALBT.
4. DNI's existing incident entry records an estimated $120 million notional loss, split between about 98.66 million BEUR and 113.81 million WALBT, while Rekt notes that thin exit liquidity made the realized attacker proceeds far smaller.
5. The practical surveillance lesson is that oracle freshness alone is not safety. A lending market also needs reporter-diversity, price-change bounds, borrow delay, and liquidation throttles when collateral value changes by impossible multiples.

The companion file [`bonqdao-oracle-whipsaw-ledger.csv`](bonqdao-oracle-whipsaw-ledger.csv) records the public evidence points used below. The SVG is a compact signal-path chart rather than a raw Polygon event trace.

{{< figure src="bonqdao-oracle-whipsaw.svg" alt="BonqDAO oracle whipsaw signal path" caption="Selected public evidence points from the February 2023 BonqDAO WALBT oracle manipulation." loading="lazy" >}}

## Why this was a whipsaw, not only an overvaluation

Many oracle-manipulation writeups focus on the first half of the BonqDAO attack: WALBT was priced far too high, so the attacker could mint too much BEUR against tiny collateral. That is true, but it understates the market-health failure.

The damaging pattern was a whipsaw. Immunefi describes two transactions separated by roughly two minutes. In the first, the attacker reported a very high ALBT/WALBT value and used the inflated collateral value to borrow 100 million BEUR. In the second, the attacker reported a very low value so WALBT troves held by other borrowers became liquidatable.

That sequence matters because it shows two distinct risk surfaces:

1. Borrow capacity can be created by an upward price shock.
2. Liquidation supply can be created by a downward price shock.

If a protocol protects only one side, it still leaves the other side open. A market-health monitor should treat any single-source collateral repricing that immediately changes both borrow capacity and liquidation state as a critical event.

## The price input was cheap relative to the market it controlled

Halborn and Rekt both describe the attack starting with a 10 TRB TellorFlex stake. Rekt put the stake value near $175 at the time. That small stake controlled a price path that, inside BonqDAO, determined whether WALBT-backed troves were solvent.

The problem was not simply that TellorFlex allowed permissionless reporting. Immunefi notes that permissionless reporting has requirements: sensible nonce, required stake, reporter timelock, and no duplicate timestamp report for the same query. The market-health failure was BonqDAO's use of the most recent spot report as a value safe enough for immediate debt and liquidation decisions.

That created an extreme leverage mismatch:

| Observable                    | Publicly reported value     |
| ----------------------------- | --------------------------- |
| Oracle reporter stake         | 10 TRB                      |
| First trove collateral        | 0.1 WALBT                   |
| BEUR minted after price raise | 100,000,000 BEUR            |
| Liquidated collateral gained  | about 113-114 million WALBT |
| DNI notional loss estimate    | about $120 million          |

The exact on-chain integer submitted to the oracle is less important than the protocol effect. The collateral price moved by enough orders of magnitude that ordinary collateral-ratio assumptions stopped describing the market.

## Borrowing and liquidation were coupled

BonqDAO troves worked like collateralized debt positions. Users locked project tokens as collateral and minted BEUR. If a trove fell below its collateralization requirement, a liquidator could close it and acquire the collateral at a discount.

The attacker used that mechanism in both directions:

1. Inflate WALBT, open attacker-controlled trove, mint BEUR.
2. Deflate WALBT, force other WALBT troves below threshold.
3. Use BEUR to buy liquidated WALBT collateral.
4. Withdraw WALBT and attempt to exit through available liquidity.

This is a useful market manipulation pattern because it turns a price feed into a forced order-generation machine. The first price shock creates synthetic buying power; the second creates forced selling by the protocol liquidation engine.

## Exit liquidity exposed the difference between notional and realized damage

DNI records the loss at roughly $120 million, including $108 million worth of 98,658,538 BEUR and $12 million worth of 113,813,998 WALBT. Those numbers are useful because they describe protocol accounting damage.

Rekt adds a separate market-health lens: the attacker reportedly got away with less than $2 million, because the stolen assets did not have enough clean exit liquidity. It also reported that BonqDAO TVL fell from about $13 million to just over $100,000, BEUR was dumped for a little over $500,000, ALBT fell as much as about 75%, BEUR traded about 25% below peg, and BNQ fell more than 30%.

That difference between notional loss and realized proceeds is not a contradiction. It is the point. A lending protocol can suffer a very large accounting loss even when the attacker cannot monetize the full mark-to-market value. Thin liquidity does not protect the protocol; it just changes who absorbs the unwind.

## Surveillance indicators

### Reporter-cost-to-market-value ratio

The price reporter's stake was tiny compared with the debt and liquidation state controlled by the reported value. Protocols should alert when a low-cost report can change more than a small percentage of market liabilities.

### Same-feed opposite-direction shocks

The attack used the same WALBT feed upward and downward in quick succession. A feed that first creates borrowing power and then creates liquidations should be frozen until independent prices agree.

### Immediate borrow after collateral repricing

The attack did not need a long holding period. The borrow followed the price report directly. A borrow delay after large collateral repricing would have given dispute windows, human monitors, or independent feeds time to react.

### Liquidation fan-out after a new oracle value

The second price report pushed many troves into liquidation. A lending protocol should throttle liquidation when a single new oracle report changes a whole collateral class from healthy to unsafe.

### Exit-liquidity mismatch

The BEUR and WALBT balances were far larger than available exit liquidity. That mismatch should not be dismissed as limiting attacker profit; it is itself a sign that accounting values no longer match market-clearing values.

## Controls that would have reduced the damage

1. Use time-weighted or dispute-windowed values for collateral, not the newest report.
2. Require multiple independent sources for debt creation and liquidation, especially for project-token collateral.
3. Cap price movement per reporting interval unless a quorum of feeds agrees.
4. Add a cool-down between large positive collateral repricing and new borrowing.
5. Add liquidation throttles when one report moves many troves across the threshold.
6. Monitor reporter stake, query age, collateral-class liabilities, and available exit liquidity in one dashboard.
7. Separate protocol accounting loss from realizable attacker proceeds in post-incident analysis.

## Why this belongs in a market manipulation wiki

BonqDAO is valuable as a market-health example because the attacker did not need hidden order-book spoofing or opaque off-chain coordination. The manipulation happened through a public price path that the protocol treated as immediately actionable.

The same signal path priced collateral, minted debt, and triggered liquidation. That makes it a useful template for surveillance teams: if one input can both create debt and force sales, the input is not just an oracle. It is market infrastructure and should be monitored like a venue.

## References

- Distributed Networks Institute, "BonqDAO Suffers a $120 Million Loss Through Price Oracle Manipulation": https://dn.institute/research/cyberattacks/incidents/2023-02-01-bonqdao/
- Immunefi, "Hack Analysis: BonqDAO, February 2023", March 23, 2023: https://medium.com/immunefi/hack-analysis-bonqdao-february-2023-ef6aab0086d6
- Halborn, "Explained: The BonqDAO Hack (February 2023)", February 7, 2023: https://www.halborn.com/blog/post/explained-the-bonqdao-hack-february-2023
- Rekt, "BonqDAO - REKT", February 3, 2023: https://rekt.news/bonq-rekt/
- Hacken, "The BonqDAO Price Oracle Hack Explained", February 2023: https://hacken.io/insights/bonqdao-hack/
