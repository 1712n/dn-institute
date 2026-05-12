---
title: "dYdX YFI Open Interest Spiral and Insurance Fund Drain"
date: 2023-11-18
entities:
  - dYdX
  - Yearn Finance
  - YFI
  - SUSHI
---

## Summary

The November 2023 dYdX v3 YFI incident is a useful market-health case because it links exchange risk controls, cross-venue spot activity, open interest growth, and forced liquidation losses in one observable sequence. dYdX's postmortem described the event as an oracle-manipulation attack, and the reported data shows how a trader can use unrealized gains from a manipulated reference market to build an increasingly large leveraged position before liquidity fails.

The strongest warning signs were:

- YFI-USD open interest on dYdX v3 increased from about $0.8 million to $67 million between November 1 and November 10, 2023.
- YFI's spot price rose from about $6,500 to more than $14,000 between November 9 and November 17, while addresses linked to the attacker were likely buying YFI across multiple venues.
- The attacker repeated a deposit, leveraged-long, spot-buying, unrealized-profit-withdrawal, and redeposit cycle across new wallet addresses.
- On November 18, YFI fell nearly 30% in an hour; the remaining long positions could not be liquidated before accounts moved into negative equity.
- The dYdX v3 insurance fund covered more than $9 million of losses, while dYdX estimated that the attacker had deposited about $16 million and withdrawn about $27 million in total.

The supporting metrics table for this article is included in [incident-metrics.csv](incident-metrics.csv).

## Timeline

### SUSHI setup phase

dYdX reported that from October 29 to November 3, 2023, an attacker connected to dYdX v3 with more than 100 wallet addresses and deposited about $5.3 million. The addresses primarily built 5x leveraged long exposure in SUSHI-USD. During the same period, addresses linked to the attacker likely bought SUSHI on external spot venues, and SUSHI moved from about $0.67 to $1.20.

This mattered because the SUSHI episode showed the mechanism before the larger YFI trade. Unrealized gains on the leveraged position could be withdrawn, moved through new wallets, and redeposited to support larger positions. dYdX increased the SUSHI-USD initial margin requirement to 100% on November 1, which blocked further withdrawals during the abnormal activity window. After SUSHI stabilized, the attacker reportedly closed most long exposure and withdrew about $5 million in profits.

### YFI buildup

The YFI phase began on November 1 and continued through November 17. According to dYdX, the attacker used around $10 million, including proceeds from the SUSHI trade, to target YFI-USD with 5x leveraged long positions. YFI-USD open interest on dYdX v3 rose from about $0.8 million to $67 million between November 1 and November 10.

The scale of open interest relative to the underlying market was the central market-health signal. A large derivatives position was accumulating in a less-liquid asset while the reference spot price was being pushed higher across venues. From November 9 to November 17, YFI's spot price rose from roughly $6,500 to more than $14,000. During that rise, the same withdrawal loop remained available: mark-to-market gains counted as equity, allowing the attacker to withdraw collateral, deposit through another address, and increase aggregate exposure.

dYdX adjusted YFI market parameters on November 17 by increasing the initial margin requirement and decreasing base and incremental position sizes. Those changes reduced the ability to keep withdrawing unrealized profit, but they did not remove the existing concentrated exposure before the crash.

### YFI crash and insurance fund loss

On November 18 at about 05:00 UTC, YFI fell nearly 30% in an hour. dYdX stated that the attacker attempted to close positions but closed only a small portion before the collapse. Because liquidity was insufficient, most remaining positions were liquidated only after the oracle price had fallen below their bankruptcy price.

That failure mode is important: the loss was not just a token price move. It was a liquidation-through-liquidity failure. A large concentrated long position, built using withdrawable unrealized gains, became too large for the market to close at solvent prices once the reference market reversed. Negative equity then triggered the insurance fund, which covered more than $9 million in losses.

### Evidence anchors and replay fields

dYdX's postmortem provides a useful minimum evidence packet for replaying the incident. It identified a root funding address, a sample connected wallet, and example ETH and USDC movements into an address connected to dYdX v3. Those links are not the full 132-account cluster, but they are enough to define the fields an investigator should require before accepting or closing an alert:

| Evidence field        | Public anchor                                                                                               | Market-health use                                                                                                                    |
| --------------------- | ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Root funding source   | [0xccb6...bc27](https://etherscan.io/address/0xccb6f95b350ca6f9d3285d61a60ea54715a4bc27)                    | Start of the linked-account graph used to connect deposits, withdrawals, and repeated exposure.                                      |
| Connected wallet      | [0x4277...190c](https://etherscan.io/address/0x4277af66d04cb6a71c83947e2bef6bb4365c190c)                    | Example wallet dYdX connected to the root source.                                                                                    |
| ETH funding movement  | [0x25ba...34f8](https://etherscan.io/tx/0x25bac4a8930d7a0d29b6f0884d788df51e1d1e58c7fb16cade100397834434f8) | Shows the root-to-wallet setup path before exchange-side activity.                                                                   |
| USDC deposit movement | [0x3b46...5c2](https://etherscan.io/tx/0x3b46d16f30e089513570e48fd026b64a0cb803762813df0e6db07289912cc5c2)  | Shows stablecoin funding into the dYdX-connected wallet.                                                                             |
| Exchange-side metrics | [dYdX postmortem](https://dydx.exchange/blog/sushi-yfi-incident)                                            | Connects the SUSHI account cluster and later YFI pattern to $16M total deposits, $27M withdrawals, and the >$9M insurance fund draw. |

A replayable packet for this case should therefore include `root_funding_address`, `connected_wallet`, `funding_tx_hash`, `stablecoin_deposit_tx_hash`, `dydx_account_id`, `market`, `position_side`, `open_interest_before`, `open_interest_after`, `mark_price`, `reference_spot_price`, `unrealized_pnl`, `withdrawal_amount`, `new_wallet_deposit`, `liquidation_price`, `bankruptcy_price`, and `insurance_fund_debit`.

## Market-health indicators

### Open interest to real liquidity mismatch

The clearest quantitative signal was the jump from $0.8 million to $67 million of YFI-USD open interest. A market can absorb large open interest when spot depth, derivatives depth, and liquidation capacity all grow together. The dYdX YFI event showed the opposite pattern: derivatives exposure grew faster than the system's ability to liquidate that exposure under stress.

The derived ratios make the signal easier to operationalize. Open interest expanded by about 84x in nine days, the YFI reference spot price more than doubled from roughly $6,500 to more than $14,000 during the final buildup window, and the reported total attacker withdrawals were about 1.7x reported deposits. A market-health queue should treat that combination as a single alert bundle rather than three separate anomalies: rapidly expanding derivatives exposure, reference-market price pressure, and realized cash extraction from still-concentrated positions.

A practical monitor should compare open interest against:

- reference-venue spot depth near the oracle price,
- one-hour and four-hour spot volume,
- expected liquidation slippage for the largest accounts,
- and the insurance fund amount available for that market's tail loss.

If open interest can become tens of millions of dollars in a market where a one-hour spot reversal can move the oracle by double-digit percentages, the venue is exposed to forced liquidation losses even when the matching engine works as designed.

For an operational detector, the YFI case suggests concrete thresholds:

- open interest growth above 10x in seven days for a low-depth market,
- open interest above 25% of estimated one-hour reference-venue spot volume,
- linked-account net withdrawals above 50% of original deposits while aggregate exposure is still rising,
- spot price movement above 50% over seven days while the same wallet cluster is net long,
- and largest liquidatable account loss above 25% of the market-specific insurance fund buffer under a 20% one-hour reference-price shock.

### Unrealized-profit withdrawal loop

dYdX explained that account equity included USDC collateral plus unrealized profit. That meant an account could withdraw up to the excess equity after the initial margin requirement was satisfied. The attacker used this accounting path by building a long, helping move spot prices higher, withdrawing mark-to-market gains, and redepositing through new accounts.

This creates a compounding loop:

1. Build a leveraged long in a less-liquid derivative market.
2. Move the underlying spot market upward across reference venues.
3. Convert unrealized derivative gains into withdrawable collateral.
4. Reuse that collateral through new addresses to build more exposure.
5. Leave the venue with concentrated liquidation risk if the spot market reverses.

The loop is a market-health signal because it turns mark-to-market accounting into funding for more leverage before profits are realized in a deep, final market.

An alert rule should join withdrawals and exposure rather than treating each withdrawal as ordinary account activity. A high-severity rule would be: `cluster_withdrawals / cluster_deposits > 1.2` and `cluster_open_interest` still increasing after a 30% or greater reference-price move. The dYdX totals, about $27 million withdrawn against about $16 million deposited, clear that ratio and show why withdrawals from unrealized profit need a separate queue.

### Wallet concentration and funding links

dYdX reported 132 addresses linked to a single funding source in the SUSHI portion of the incident. That pattern is not enough by itself to prove manipulation, but it is strong context when it appears with abnormal open interest growth and coordinated spot-market pressure.

For surveillance, address linkage is most useful when paired with trade behavior:

- many new accounts funded from related sources,
- synchronized long exposure in the same less-liquid market,
- withdrawals shortly after mark-to-market gains,
- redeposits into fresh addresses,
- and spot buying in the same asset at the same time.

The combination points to one economic actor distributing a position across account boundaries.

For replaying the linked SUSHI-to-YFI strategy, the account graph should be treated as one economic position when applying margin-surveillance thresholds. If 100 or more fresh accounts share a root funding source, trade the same low-depth market in the same direction, and recycle withdrawals into new deposits, the venue should aggregate those accounts for risk review before normal per-account limits are applied.

### Parameter lag

The YFI market parameter changes came before the final crash, but after a large position had already accumulated. This is a common failure pattern in market manipulation incidents: parameter changes are effective for new exposure but weaker against existing exposure if they arrive after the position has grown beyond available liquidation liquidity.

Risk controls should therefore trigger before exposure becomes hard to unwind. The useful thresholds are not only price-move thresholds. They should include open-interest growth rate, concentration by linked accounts, and the ratio between the largest liquidatable position and expected spot depth.

A practical control is a staged margin throttle rather than a single late parameter update. For example, if open interest grows above 10x while linked-account withdrawals exceed 50% of original deposits, disable withdrawal of unrealized PnL for that market. If the largest linked cluster cannot be liquidated inside the expected one-hour reference-venue volume without pushing the oracle more than 10%, automatically raise initial margin for new exposure and force manual review before collateral can leave the venue.

## Detection and control lessons

The dYdX postmortem described several mitigations that map directly to market-health monitoring:

- revised margining for less-liquid markets,
- abnormal-activity-based initial margin adjustments,
- longer-horizon open-interest monitoring,
- market listing decisions based on reference-venue depth and trading activity,
- and variable margin fraction features that restrict withdrawals during unusually large price moves.

The important design lesson is that liquidation systems need both execution capacity and pre-liquidation throttles. If a venue waits until accounts are liquidatable, it may already be too late in a thin market. A stronger control path is to slow collateral withdrawals and new leverage while the account is profitable but the profit depends on abnormal reference-market movement.

## Why this case belongs in Market Health

This incident is not just a dYdX-specific insurance fund event. It is a reusable example of a market-health failure mode in crypto derivatives:

- the underlying asset was less liquid than the leverage offered against it,
- open interest grew far faster than normal market depth,
- unrealized profit became withdrawable collateral,
- linked accounts obscured the single-actor exposure,
- and the final loss appeared only when liquidation liquidity disappeared.

For future surveillance, the most actionable indicator is the joint movement of open interest, linked-account collateral flows, and reference-market price pressure. None of those signals is decisive alone. Together, they identify a derivatives market whose reported profits may be funded by a manipulated oracle path rather than by durable liquidity.

## References

- dYdX, [Post Mortem on SUSHI and YFI Incident](https://dydx.exchange/blog/sushi-yfi-incident), January 3, 2024.
- dYdX Community Docs, [Markets governance-adjustable parameters](https://docs.dydx.community/dydx/modules/governance/governance-adjustable-parameters/markets).
- CoinMarketCap Academy, [Targeting Attack Against YFI Markets Caused 40% Crash, According to dYdX Founder](https://coinmarketcap.com/academy/article/targeting-attack-against-yfi-markets-caused-40percent-crash-according-to-dydx-founder), November 2023.
