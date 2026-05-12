---
title: "GMX AVAX Reference Price Manipulation and GLP Liquidity Exposure"
date: 2022-09-18
entities:
  - GMX
  - GLP
  - Avalanche
  - AVAX
---

## Summary

The September 2022 GMX AVAX/USD incident is a compact example of a market-health failure where the manipulated venue did not need a smart-contract bug. The reported strategy used GMX V1's no-price-impact execution and external reference-market pricing to trade large AVAX clips against GLP liquidity while moving the AVAX price on reference exchanges.

Public reporting and GMX's own response identify the core signals:

- GMX was notified of AVAX/USD price manipulation on reference exchanges and temporarily capped AVAX open interest at $2 million long and $1 million short.
- The reported trader repeated the loop five times.
- The first reported cycle ran from 01:15:31 to 01:28:11 UTC and produced about $158,000 of profit.
- Each cycle reportedly moved more than 200,000 AVAX, or roughly $4 million to $5 million of notional.
- Total reported profit was about $565,000, with one source describing a broader estimate of $500,000 to $700,000.

The supporting evidence table for this article is included in [incident-metrics.csv](incident-metrics.csv).

## Timeline

### Precondition: large trades priced from external references

GMX V1 offered leveraged trading against the GLP liquidity pool with no direct order book on GMX. Public incident reporting described the relevant execution surface as large GMX trades at the oracle or mark price without internal price impact. That made the external reference price, rather than an internal book depth curve, the execution anchor.

That model can be healthy when the trade size is small compared with reference-market depth. The risk appears when the trade size is large enough to move the reference markets that feed the execution price. In that case the protocol can quote deep liquidity at a price whose input market has already been pushed by the same economic actor.

### September 18 trading loop

Reports from September 18-19, 2022 describe a repeated loop in the AVAX/USD market. The trader opened large positions on GMX with no price impact, moved AVAX on reference exchanges, then used the changed reference price to exit with profit against GLP liquidity providers.

The reported scale was material for a single-asset market-health event. Joshua Lim's public analysis, summarized by Cointelegraph, described five cycles. The first cycle reportedly ran from 01:15:31 to 01:28:11 UTC and extracted roughly $158,000. Across the repeated cycles, more than 200,000 AVAX, or about $4 million to $5 million, moved per cycle.

CryptoSlate reported that the trader used roughly $4.7 million and that AVAX traded between $18.33 and $18.68 during the incident window. That price band looks small in percentage terms, but the no-price-impact execution made small reference-market moves economically meaningful when repeated across large clips.

### GMX response

GMX's public response, quoted by multiple outlets, said the protocol had been notified of AVAX/USD price manipulation on reference exchanges by monitoring systems and community members. GMX kept GLP and GMX markets operating, but temporarily capped AVAX open interest at $2 million long and $1 million short while the team reviewed the occurrence.

The mitigation is important because it maps directly to the failure mode. The cap did not depend on proving malicious intent or reversing past trades. It reduced the size of future AVAX positions below the reported repeated clip size, limiting the economic value of another same-market loop.

## Evidence anchors and replay fields

The incident has enough public evidence to define a replayable market-health packet even without full private account data:

| Evidence field                | Public anchor                                                                                                                              | Market-health use                                                                                  |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| Protocol acknowledgement      | [Cointelegraph summary of GMX response](https://cointelegraph.com/news/decentralized-exchange-gmx-suffers-565k-price-manipulation-exploit) | Confirms that GMX saw AVAX/USD manipulation on reference exchanges and applied open-interest caps. |
| Cycle count and sizing        | [CryptoSlate incident summary](https://cryptoslate.com/crypto-trader-exploits-gmx-manipulates-avax-price-to-remove-565k/)                  | Provides the reported five-trade loop, approximate capital used, and AVAX price band.              |
| V1 execution mechanism        | [Cointelegraph incident summary](https://cointelegraph.com/news/decentralized-exchange-gmx-suffers-565k-price-manipulation-exploit)        | Summarizes public analysis of large GMX AVAX/USD trades executed without internal price impact.    |
| Current pricing model context | [GMX fees documentation](https://docs.gmx.io/docs/trading/fees/)                                                                           | Shows how price impact is now an explicit separate control in GMX's current trading documentation. |

A replay packet should collect `gmx_account`, `position_side`, `position_size_usd`, `open_timestamp`, `close_timestamp`, `entry_mark_price`, `exit_mark_price`, `reference_exchange_prices`, `reference_exchange_depth`, `reference_exchange_order_flow`, `glp_asset_exposure`, `realized_pnl`, `open_interest_before`, `open_interest_after`, `cap_before`, and `cap_after`.

The key point is that a venue-only trade log is incomplete. For oracle or reference-price manipulation, the replay must join GMX fills with the external venues used to set the price.

## Market-health indicators

### No price impact plus movable reference markets

The core signal is a mismatch between execution liquidity and reference-market liquidity. GMX could offer a large trade at a mark price, but the mark price came from markets that could be moved by the same trader. A detector should therefore compare the proposed GMX position size with the available depth on the reference venues, not only with GLP's accounting liquidity.

The practical indicator is:

`position_size_usd / executable_reference_depth_usd`

If the ratio is high enough that the trader can move the reference price by the same direction needed to profit on GMX, the venue is not just offering leverage. It is offering the trader a way to monetize external price impact against LP inventory.

### Repeated clip pattern

The reported five-cycle loop is more informative than a single profitable trade. A one-off large trade may be normal risk-taking. Repeated large clips in a short window, especially with similar notional size and alternating reference-market activity, indicate a systematic extraction strategy.

A surveillance queue should escalate when all of the following occur:

- the same account or linked cluster trades the same perp market repeatedly within one hour,
- each clip is large relative to reference-market depth,
- the reference price moves favorably during or immediately before the GMX close,
- realized PnL accumulates while GLP takes the other side,
- and the pattern repeats after the first profitable cycle.

For the GMX/AVAX case, the public reports describe exactly that repeated pattern: five cycles, each around $4 million to $5 million, with total profit around $565,000.

### LP inventory as the loss surface

This incident belongs in market-health monitoring because the loss surface was not only a trader's counterparty. GLP holders were the liquidity backstop. When a market advertises deep execution without internal order-book impact, LP inventory can become the place where reference-market manipulation is settled.

Useful LP-side monitoring fields include:

- asset-specific GLP inventory before and after the window,
- realized PnL paid to traders by market,
- concentration of PnL by account cluster,
- open interest by side and asset,
- and stress loss if the reference price is pushed by 1%, 2%, or 5% inside the observed reference-market depth.

The GMX response cap of $2 million long and $1 million short is also a useful benchmark. A cap below the repeated $4 million to $5 million clip size directly reduces the profitability of the observed loop.

### Warning-before-proof controls

The fastest useful control is not a legal finding that a trader manipulated a market. It is a temporary risk throttle when the trade pattern can no longer be explained by ordinary liquidity-taking. In this case, GMX did not need to close the market to respond. A narrow open-interest cap reduced the maximum repeatable position size while preserving market operation.

That suggests a practical control ladder:

1. If `position_size_usd` exceeds a configured share of reference-market depth, apply a higher price-impact or spread factor.
2. If the same account cluster repeats profitable cycles in the same market, reduce per-market open-interest caps.
3. If GLP realized losses become concentrated in one market and one account cluster, pause new exposure while allowing risk-reducing closes.
4. If the reference venues show abnormal same-direction order flow during GMX opens and closes, require manual review before increasing caps again.

## Detection and control lessons

The reusable lesson is that oracle or reference-market integrity cannot be measured only by whether the reference price is accurate at the moment it is read. A price can be accurate and still be manipulable at the size required by the venue's own execution model.

For future market-health systems, the GMX/AVAX case supports four checks:

- **Reference-depth check:** compare maximum position size with executable depth on the venues that feed the oracle or mark price.
- **Repeated-cycle check:** treat repeated profitable clips in one market as an account-cluster event, not independent trades.
- **LP-loss concentration check:** alert when one asset and one account cluster account for an unusual share of LP losses.
- **Cap-lag check:** measure how long the market remains open at large size after the first profitable extraction cycle.

These checks do not require private intent labels. They require joined venue fills, reference-market depth, realized PnL, and account-cluster aggregation.

## Why this case belongs in Market Health

The GMX/AVAX incident is useful because it shows how a DeFi derivatives venue can be healthy at the smart-contract layer while still exposing liquidity providers to market-microstructure extraction. The protocol worked as designed, but the design allowed large no-price-impact trades against a reference price that could be moved externally.

That distinction matters for market surveillance. The alert should not be limited to hacks, insolvency, or exchange downtime. It should also catch cases where the pricing surface, liquidity surface, and risk-limit surface disagree.

For a market-health dashboard, the most actionable signal is the joint movement of large GMX position clips, same-window AVAX reference-market movement, and concentrated GLP PnL loss. A venue seeing that combination should lower caps first and investigate intent second.

## References

- Cointelegraph, [Decentralized exchange GMX suffers $565K price manipulation 'exploit'](https://cointelegraph.com/news/decentralized-exchange-gmx-suffers-565k-price-manipulation-exploit), September 19, 2022.
- CryptoSlate, [Crypto trader exploits GMX, manipulates AVAX price to remove $565K](https://cryptoslate.com/crypto-trader-exploits-gmx-manipulates-avax-price-to-remove-565k/), September 19, 2022.
- GMX Docs, [Fees](https://docs.gmx.io/docs/trading/fees/).
