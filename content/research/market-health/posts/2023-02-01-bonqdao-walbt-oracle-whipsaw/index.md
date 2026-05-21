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
4. DNI's existing incident entry records an estimated $120 million notional loss, split into about $108 million of 98,658,538 BEUR and about $12 million of 113,813,998 WALBT, while Rekt notes that thin exit liquidity made the realized attacker proceeds far smaller.
5. The practical surveillance lesson is that oracle freshness alone is not safety. A lending market also needs reporter-diversity, price-change bounds, borrow delay, and liquidation throttles when collateral value changes by impossible multiples.

The companion file [`bonqdao-oracle-whipsaw-ledger.csv`](bonqdao-oracle-whipsaw-ledger.csv) records the public evidence points used below. The SVG is a compact signal-path chart rather than a raw Polygon event trace.

{{< figure src="bonqdao-oracle-whipsaw.svg" alt="BonqDAO oracle whipsaw signal path" caption="Selected public evidence points from the February 2023 BonqDAO WALBT oracle manipulation." loading="lazy" >}}

## Why this was a whipsaw, not only an overvaluation

Many oracle-manipulation writeups focus on the first half of the BonqDAO attack: WALBT was priced far too high, so the attacker could mint too much BEUR against tiny collateral. That is true, but it understates the market-health failure.

Public postmortems describe two stages. In the first, the attacker reported a very high ALBT/WALBT value and used the inflated collateral value to borrow 100 million BEUR. In the second, the attacker reported a very low value so WALBT troves held by other borrowers became liquidatable.

That sequence matters because it shows two distinct risk surfaces:

1. Borrow capacity can be created by an upward price shock.
2. Liquidation supply can be created by a downward price shock.

If a protocol protects only one side, it still leaves the other side open. A market-health monitor should treat any single-source collateral repricing that immediately changes both borrow capacity and liquidation state as a critical event.

## The price input was cheap relative to the market it controlled

Halborn and Rekt both describe the attack starting with a 10 TRB TellorFlex stake. Rekt put the stake value near $175 at the time. That small stake controlled a price path that, inside BonqDAO, determined whether WALBT-backed troves were solvent.

The problem was not simply that TellorFlex allowed permissionless reporting. BlockSec notes that TellorFlex allowed price providers to stake 10 TRB and update the WALBT price, while BonqDAO used the updated price directly in the lending contract. The market-health failure was BonqDAO's use of the newest spot report as a value safe enough for immediate debt and liquidation decisions.

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

The price reporter's stake was tiny compared with the debt and liquidation state controlled by the reported value.

- Compute `reporter_control_ratio = reporter_stake_usd / max(new_debt_capacity_usd, liquidation_collateral_value_usd)` for each collateral feed update.
- Alert when `reporter_control_ratio < 0.001` or one reporter can move more than $1 million of borrowing or liquidation value.
- In the BonqDAO case, a roughly $175 reporting stake sat behind about $120 million of accounting impact, a ratio near 0.0000015.

### Same-feed opposite-direction shocks

The attack used the same WALBT feed upward and downward in quick succession.

- Track `price_change_pct = abs(new_price - previous_price) / previous_price` for every report.
- Freeze new debt and liquidation from that feed if opposite-signed moves above 50% occur within five minutes or inside the protocol dispute window.
- Require at least three independent sources to agree within 2% before re-enabling liquidation on the affected collateral class.

### Immediate borrow after collateral repricing

The attack did not need a long holding period. The borrow followed the price report directly.

- Alert when a borrow happens within five minutes of a collateral price increase greater than 25% or greater than three standard deviations from a 30-day move distribution.
- Enforce a block-based or time-based hold before allowing new debt against collateral whose mark just moved beyond that threshold.
- During the hold, allow repayments and deleveraging, but disallow fresh borrowing that depends on the new mark.

### Liquidation fan-out after a new oracle value

The second price report pushed many troves into liquidation.

- Measure `liquidation_fanout = newly_liquidatable_troves / active_troves_for_collateral` immediately after each oracle update.
- Trigger a throttle when fan-out exceeds 5% of a collateral class or `liquidation_count > mean + 3 * stdev` over a 30-day baseline.
- Process liquidations in bounded batches until independent prices confirm the move, rather than allowing one report to clear an entire collateral class.

### Exit-liquidity mismatch

The BEUR and WALBT balances were far larger than available exit liquidity.

- Track `exit_liquidity_ratio = venue_depth_to_10pct_slippage / marked_collateral_value` for protocol collateral and debt assets.
- Alert when realizable exit liquidity is below 10% of marked balances or when a protocol loss estimate relies on prices that cannot clear size.
- Report notional protocol loss and probable cash-out value separately so a low attacker exit does not hide insolvency risk.

## Controls that would have reduced the damage

1. Use dispute-windowed or time-weighted collateral values: for example, only let a 15-minute TWAP or a finalized Tellor dispute-window price affect new borrowing and liquidation.
2. Require a source quorum for debt creation and liquidation: at least three of five feeds should agree within 2% before a project-token collateral mark can expand borrow capacity.
3. Cap collateral price movement to 10% per 15-minute interval unless the quorum rule passes; otherwise freeze new debt and mark the collateral class for review.
4. Add an asymmetric cool-down after upward repricing: if collateral rises more than 25%, pause new borrowing against that collateral for 30 minutes while repayments and collateral additions remain available.
5. Add a matching liquidation guard after downward repricing: if one report would liquidate more than 5% of troves, limit liquidation to bounded batches until independent sources confirm the price.
6. Monitor reporter stake, query age, collateral-class liabilities, and available exit liquidity in one dashboard, with automatic escalation when the reporter-control ratio falls below 0.001.
7. Haircut accounting values by exit liquidity during incident response, so the dashboard shows both protocol balance-sheet damage and realizable attacker proceeds.

A concrete BonqDAO-specific breaker would have combined items 4 and 5: the first extreme upward WALBT report could have started a 30-minute borrow hold, and the second downward report could have delayed class-wide liquidations unless three independent prices agreed within 2%. That design targets the whipsaw mechanics directly instead of only adding a generic oracle hardening checklist.

## Why this belongs in a market manipulation wiki

BonqDAO is valuable as a market-health example because the attacker did not need hidden order-book spoofing or opaque off-chain coordination. The manipulation happened through a public price path that the protocol treated as immediately actionable.

The same signal path priced collateral, minted debt, and triggered liquidation. That makes it a useful template for surveillance teams: if one input can both create debt and force sales, the input is not just an oracle. It is market infrastructure and should be monitored like a venue.

## References

- Distributed Networks Institute, "BonqDAO Suffers a $120 Million Loss Through Price Oracle Manipulation": https://dn.institute/research/cyberattacks/incidents/2023-02-01-bonqdao/
- BlockSec, "BonqDAO Exploited on Polygon: $120M Stolen Due to Flawed Logic", February 2, 2023: https://blocksec.com/blog/bonq-dao-exploited-on-polygon-120-m-stolen-due-to-flawed-logic
- Halborn, "Explained: The BonqDAO Hack (February 2023)", February 7, 2023: https://www.halborn.com/blog/post/explained-the-bonqdao-hack-february-2023
- Rekt, "BonqDAO - REKT", February 3, 2023: https://rekt.news/bonq-rekt
- Hacken, "The BonqDAO Price Oracle Hack Explained", February 2023: https://hacken.io/insights/bonqdao-hack/
