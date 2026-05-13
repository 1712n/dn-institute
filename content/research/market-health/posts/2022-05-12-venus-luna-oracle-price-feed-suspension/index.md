---
title: "Venus Protocol LUNA Oracle Price Feed Suspension"
date: 2022-05-12
entities:
  - Venus Protocol
  - LUNA
  - UST
  - Terra
  - Chainlink
  - BNB Chain
  - XVS
---

## Summary

Venus Protocol suffered a LUNA market dislocation on May 12, 2022, during the
collapse of the Terra ecosystem. The immediate failure was not a flash-loan
price pump on a thin trading venue. It was a stale-oracle failure in a lending
market: Chainlink's LUNA price feed hit a floor threshold and stopped updating
at 0.107 USD while LUNA's spot price continued falling toward about 0.01 USD.

Venus's own incident update says the feed was suspended at about 09:20 UTC and
that the LUNA market continued operating while the external price kept falling.
The team identified the disparity roughly four hours later and paused the
protocol at about 15:15 UTC through a multisig transaction on the PauseGuardian
contract. By the initial tally, subsequent borrows left about 14.2 million USD
of shortfall across the affected accounts.

The incident is a market-health case because the apparent collateral value on
Venus diverged from the executable market value of LUNA by more than 10x during
a systemic collapse. The protocol still accepted LUNA as collateral during that
window, so users could deposit rapidly devaluing collateral and borrow assets
whose prices were not experiencing the same oracle failure.

The main warning signs were:

1. an oracle feed that could stop updating without automatically disabling the
   dependent lending market,
2. collateral accepted at roughly 0.107 USD while spot references were near
   0.01 USD,
3. a multi-hour response window during an asset death spiral,
4. large LUNA deposits into the affected market after the oracle/spot
   divergence,
5. a protocol-wide pause required because individual market pause controls were
   not yet the fastest available mitigation.

## Incident Metrics

The supporting dataset is stored in
[`venus-luna-market-metrics.csv`](venus-luna-market-metrics.csv). It separates
oracle, response-time, borrow, and remediation signals so the case can be
compared with other market-manipulation and market-health failures.

| Metric                      |                Value | Market-health interpretation                                                     |
| --------------------------- | -------------------: | -------------------------------------------------------------------------------- |
| Feed suspension time        | 2022-05-12 09:20 UTC | The market kept running after the LUNA price source stopped updating.            |
| Stale LUNA price on Venus   |            0.107 USD | Collateral was valued near the suspended feed price.                             |
| Approximate LUNA spot price |             0.01 USD | External spot value was about one-tenth of the Venus collateral value.           |
| Oracle-to-spot multiple     |                10.7x | Deposited LUNA could support far more borrowing than its market value justified. |
| Protocol pause time         | 2022-05-12 15:15 UTC | The response took several hours during an extreme market collapse.               |
| Initial shortfall tally     |       14,200,000 USD | Venus's incident update reported the borrow shortfall after detection.           |
| Risk fund balance           |       15,000,000 USD | The risk fund was presented as the repayment source for the shortfall.           |
| Reported borrowed assets    |       13,500,000 USD | Secondary reporting captured the borrow scale tied to large LUNA deposits.       |
| Reported LUNA deposits      |     230,000,000 LUNA | Deposit size became dangerous once the price source was stale.                   |

## Incident Timeline

Venus's second LUNA incident update places the first critical event at about
09:20 UTC on May 12, when Chainlink's LUNA price feed reached a price floor
threshold and was suspended at 0.107 USD. The LUNA market on Venus did not stop
with the feed. It continued to accept interactions while spot markets kept
repricing LUNA downward.

Roughly four hours later, Venus identified that the external price was about
0.01 USD and that suspicious accounts were depositing large amounts of LUNA. The
team then used the fastest mitigation it had available and paused the whole
protocol at about 15:15 UTC through the PauseGuardian multisig path.

The response limited further damage, but the gap between the feed suspension and
the protocol pause was enough to create a large borrow shortfall. Venus reported
an initial shortfall tally of about 14.2 million USD across the affected
accounts. BeInCrypto, quoting the team's public statements, reported that two
large deposits totaled about 230 million LUNA and that borrowed assets totaled
around 13.5 million USD. Halborn later summarized the Venus loss estimate at
about 11.2 million USD, illustrating that different post-incident calculations
used different recovery and valuation assumptions.

## Why The Market Signal Failed

Lending markets are only as healthy as their collateral valuation loop. Venus
was not primarily harmed because LUNA was volatile; volatile collateral can be
managed if the protocol reprices it, caps it, or removes it quickly enough. The
problem was that Venus continued to treat the suspended feed value as usable
collateral while the market value of LUNA was collapsing below that feed value.

That made the stale feed a synthetic bid. Anyone able to acquire LUNA near the
external spot price could deposit it into Venus at the higher protocol price and
borrow assets against that inflated collateral value. The trade did not require
moving Venus's price upward. It only required noticing that Venus had stopped
moving downward with the market.

This distinction matters for market-health monitoring. A stale oracle can create
the same economic effect as price manipulation even when no attacker directly
manipulates the oracle or the underlying spot venue. The manipulated object is
the protocol's interpretation of collateral value.

## Market-Health Indicators

### 1. Feed liveness by timestamp and heartbeat

The most important missed signal was feed liveness. Venus later listed a stale
price feed check and timestamp-based monitoring as immediate remediation items.
A market-health monitor should block collateral-dependent actions when a feed is
inactive, not merely when a price looks extreme.

### 2. Oracle price versus exchange reference price

The 0.107 USD oracle value versus an approximately 0.01 USD spot value created a
roughly 10.7x gap. That is far outside a normal liquid-market basis. A protocol
should treat this as a market integrity failure and pause new borrows or reduce
collateral value before accepting more deposits.

### 3. Deposit velocity after a feed anomaly

Large LUNA deposits after the feed stopped were not a sign of renewed confidence
in LUNA. They were a signal that the market had discovered an arbitrage between
Venus's internal collateral value and the external executable price. Deposit
velocity should be interpreted differently when it follows a known oracle
anomaly.

### 4. Borrowed-value concentration

The shortfall came from a small set of accounts, with Venus identifying three
suspicious addresses in its incident update. Account concentration after a
collateral-source anomaly should raise severity because the event is no longer a
broad market repricing; it has become targeted extraction.

### 5. Mitigation granularity

Venus paused the full protocol because that was the fastest available mitigation
path. In its remediation plan, the team specifically listed individual market
pause/resume controls. Market-health systems should prefer market-level
containment so healthy pools can keep operating while the broken collateral is
isolated.

## Controls That Would Have Reduced The Risk

The incident points to controls that are especially important for lending
protocols with long-tail collateral:

- Reject new borrows and collateral-value increases when a feed has not updated
  within its expected heartbeat.
- Compare oracle prices with independent centralized and decentralized exchange
  references during high-volatility windows.
- Automatically set a conservative collateral value or pause the market when
  oracle and reference prices diverge beyond a hard threshold.
- Track large deposit velocity after feed anomalies and treat it as an
  extraction signal rather than ordinary supply growth.
- Maintain per-market pause controls that can disable borrow and collateral
  entry without pausing unrelated assets.
- Require listings of volatile assets to include prebuilt stale-feed handling,
  secondary feeds, and emergency offboarding procedures.

## Remediation And Governance Response

Venus's public plan had three layers: stop the broken market, preserve user
repayment paths, and harden oracle monitoring. The team set UST and LUNA price
feeds to zero, temporarily restricting affected accounts while the protocol
prepared to offboard the assets. The team also said the Venus Risk Fund, with
15 million USD in balances, would pay down the shortfall over time and that a
BNB Accelerator Fund loan had been negotiated as a liquidity backstop if needed.

The next update described the resume plan. Venus turned off price feeds to allow
asset supply and repayments while preventing borrowing and liquidations. VIP-61
set the collateral factor for LUNA and UST to zero, with a repayment window
before liquidations resumed. Venus also listed concrete remediation work:
stale-feed checks, timestamp-based monitoring, a fallback feed path, market-level
pause controls, cross-checking market prices against centralized exchanges, and
faster multisig-controlled resume operations.

For market-health analysis, the governance response is as important as the
initial loss. The protocol's own remediation list maps directly to the failure
mode: liveness checks for the stale feed, external price validation for the
oracle/spot divergence, and market-specific emergency controls for containment.

## References

- [Venus Protocol: Official Statement regarding LUNA](https://medium.com/venusprotocol/venus-protocol-official-statement-regarding-luna-6eb45c3cb058)
- [Venus Protocol: LUNA Incident Update 2](https://medium.com/venusprotocol/venus-protocol-luna-incident-update-2-c334475d9214)
- [Venus Protocol: LUNA Incident Update 3 - Resuming the Protocol](https://medium.com/venusprotocol/venus-luna-incident-update-3-resuming-the-protocol-ff059a914405)
- [Halborn: Explained - The Luna Price Dip Exploits](https://www.halborn.com/blog/post/explained-the-luna-price-dip-exploits-may-2022)
- [BeInCrypto: Venus Protocol Loses $11M Due to Chainlink Suspension of LUNA Price Oracle](https://beincrypto.com/venus-protocol-loses-11m-chainlink-suspension-luna-price-oracle/)
- [Cointelegraph: DeFi protocols declare losses as attackers exploit LUNA price feed discrepancy](https://cointelegraph.com/news/defi-protocols-declare-losses-as-attackers-exploit-luna-price-feed-discrepancy)
