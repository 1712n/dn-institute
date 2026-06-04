---
title: "Aave CRV liquidation squeeze: borrow concentration as a market-health signal"
date: 2022-11-22
description: "A concentrated CRV short on Aave v2 coincided with a liquidation squeeze, a 24.5x spot-volume shock, and residual protocol debt despite full liquidation."
entities:
  - Aave
  - CRV
  - Curve DAO Token
  - Binance
---

## Summary

On November 22, 2022, a single Aave v2 Ethereum account used USDC collateral to build a large borrowed-CRV position. Aave governance contributors later described the position as approximately **92 million CRV** at peak, roughly **$60 million** at then-current prices, and stated that the account was fully liquidated after the short attempt failed.[^aave-arc]

The event is useful for Market Health monitoring because the stress did not only appear in DeFi lending accounting. It also appeared in public executed-trade data for CRV/USDT: Binance spot quote volume on November 22 reached **$209.1 million**, or **24.5x** the November 15-21 average in the accompanying daily sample. The same UTC day had an **84.5%** high-low range on Binance CRV/USDT, measured as `(high - low) / low`.[^binance-api] The lending venue absorbed the tail risk: Aave governance first estimated roughly **$1.6 million** of excess debt and later quantified **2,656,335 CRV** of excess CRV debt in the Ethereum v2 reserve.[^aave-arfc]

This is a narrow market-health case study of an alleged manipulation pattern rather than a broad Aave risk review: the central signal is a crowded borrow/short position in a relatively thin collateral market, followed by a spot-market squeeze and forced-liquidation feedback. An Aave risk discussion published during the event described the position as a tactical short entered with the intention of precipitating a short squeeze.[^aave-risk]

## Evidence snapshot

{{< figure src="crv-usdt-hourly.svg" alt="CRV USDT hourly close and quote volume on Binance from 2022-11-20 to 2022-11-25" caption="CRV/USDT hourly close and quote volume on Binance spot around the Aave v2 CRV liquidation squeeze. Data source: Binance public spot kline API, interval 1h." loading="lazy" >}}

| Signal                 |                                                                                   Measurement | Market-health interpretation                                                                        |
| ---------------------- | --------------------------------------------------------------------------------------------: | --------------------------------------------------------------------------------------------------- |
| Borrow concentration   |                 Aave governance described one account shorting roughly 92 million CRV at peak | Borrow-side concentration can turn a lending market into a forced buyer when liquidations begin     |
| Residual protocol debt |                         Approximately $1.6 million initially; later 2,656,335 CRV excess debt | Liquidation incentives and available market liquidity were insufficient to close the stress cleanly |
| Spot volume shock      | $209.1 million Binance CRV/USDT quote volume on 2022-11-22, 24.5x the prior seven-day average | Executed-trade venue stress aligned with the DeFi liquidation window                                |
| Intraday price range   |           84.5% Binance CRV/USDT high-low range on 2022-11-22 UTC, using `(high - low) / low` | Spot price dislocation amplified liquidation risk and short-squeeze dynamics                        |

The companion evidence files are:

- [`crv-usdt-binance-hourly.csv`](crv-usdt-binance-hourly.csv): hourly Binance CRV/USDT executed-trade candles from 2022-11-20 00:00 through 2022-11-25 00:00 UTC.
- [`crv-usdt-binance-daily.csv`](crv-usdt-binance-daily.csv): daily Binance CRV/USDT candles from 2022-11-15 through 2022-12-02 UTC, used for the prior-week volume comparison.
- [`crv-usdt-binance-hourly-derived-metrics.csv`](crv-usdt-binance-hourly-derived-metrics.csv): derived hourly stress metrics for November 22, including volume multiples versus the November 20-21 hourly average and taker-sell quote-volume share.
- [`event-signals.csv`](event-signals.csv): source-linked event facts and derived statistics used in this article.
- [`aave-governance-evidence.csv`](aave-governance-evidence.csv): source excerpts for the Aave-side borrow concentration, liquidation, residual-debt, and manipulation-risk framing.
- [`aave-v2-crv-account-events.csv`](aave-v2-crv-account-events.csv): decoded Aave v2 LendingPool Borrow, Repay, and LiquidationCall events for the identified account and CRV reserve.
- [`aave-v2-crv-onchain-summary.json`](aave-v2-crv-onchain-summary.json): summary of the local on-chain event decoding, including 14 CRV Borrow events totaling 92,000,000 CRV and 385 LiquidationCall events covering 89,544,317.443851 CRV.
- [`reproduce-aave-v2-crv-events.py`](reproduce-aave-v2-crv-events.py): dependency-free Ethereum JSON-RPC script that reproduces the Aave v2 event evidence files.
- [`reproduce-crv-binance-stats.py`](reproduce-crv-binance-stats.py): dependency-free local script that recomputes the Binance volume multiple, high-low range, hourly/daily consistency checks, and peak-volume hour.

## Manipulation pattern

The incident had three reinforcing components:

1. **Position construction through a lending venue.** The relevant account accumulated a large CRV borrow against USDC collateral on Aave v2. That made the account economically short CRV while also creating protocol exposure if the collateral and liquidation path failed to keep pace with the CRV price.
2. **Spot-market squeeze conditions.** On the day the position was liquidated, CRV/USDT spot activity on Binance was not a normal continuation of the previous week. The daily quote-volume sample rose from an $8.54 million November 15-21 average to $209.13 million on November 22. The derived hourly metrics show the stress was concentrated in the liquidation window: the 13:00 UTC candle alone traded $38.0 million of quote volume, **83.1x** the November 20-21 average hourly quote volume, with taker-sell volume still 54.3% of quote volume despite the price rebound.
3. **Bad-debt tail after liquidation.** The position was fully liquidated, but liquidation did not fully recapitalize the CRV reserve. Aave governance later discussed acquiring CRV to repay the residual reserve debt.

A natural market selloff can create liquidation volume, but this case is different because the initiating risk was an intentionally concentrated borrow/short position in a token whose borrow-market depth, spot-market depth, and liquidation throughput were not independent. The manipulation attempt could lose money for the trader while still imposing measurable residual cost on the venue.

## Market Health indicators to monitor

This incident suggests several concrete indicators for market-health dashboards:

### Borrow-side concentration against free float

A lending market should track the largest borrower share of total borrowed units and compare it with observable spot liquidity. A single borrower approaching tens of millions of CRV was not just a credit-risk fact; it was a market-structure fact because liquidators would need to source CRV into a stressed spot market.

### Liquidation notional versus venue volume

The November 22 volume shock shows why liquidation capacity should be compared with recent executed volume, not only with protocol collateral ratios. A 24.5x daily volume jump indicates that liquidations and hedging activity were large relative to recent public spot activity.

### Residual debt after full liquidation

Bad debt after a full liquidation is a high-severity outcome because it means the market cleared mechanically but not economically. For Market Health, this can be recorded as a venue-solvency stress flag: the protocol executed liquidations, yet reserve accounting still required recapitalization.

### Cross-venue feedback loop

The CRV event links three markets that are often monitored separately: Aave borrow utilization, CRV spot liquidity, and liquidator inventory availability. A robust alert should fire when borrow concentration rises while spot liquidity is falling or when daily executed volume surges during liquidation windows.

## Limitations

The Binance kline data used here is public executed-trade candle data, not a full order-book or account-level feed. It therefore supports the volume shock, taker-side imbalance, and price-range observations, but it cannot identify the specific counterparties trading on Binance. The borrower-size claim is corroborated by the local Aave v2 event trace in `aave-v2-crv-account-events.csv`, which decodes 14 CRV Borrow events totaling 92,000,000 CRV for the identified account. The residual-debt figures still come from Aave governance reserve-accounting posts and are separated in `aave-governance-evidence.csv`; the decoded LiquidationCall events show 89,544,317.443851 CRV of covered debt during the liquidation window, not the final reserve bad-debt accounting.

## Sources

[^aave-arc]: Aave governance, "[ARC] Repay excess debt in CRV market for Aave V2 ETH," November 23, 2022. https://governance.aave.com/t/arc-repay-excess-debt-in-crv-market-for-aave-v2-eth/10779
[^aave-arfc]: Aave governance, "[ARFC] Repay Excess CRV Debt on Ethereum v2," December 8, 2022. https://governance.aave.com/t/arfc-repay-excess-crv-debt-on-ethereum-v2/10955
[^aave-risk]: Aave governance, "Discussion: Reducing Long Tail Asset Risk," November 2022. https://governance.aave.com/t/discussion-reducing-long-tail-asset-risk/10748
[^binance-api]: Binance public spot REST API, `/api/v3/klines`, CRVUSDT hourly and daily candles. https://api.binance.com/api/v3/klines?symbol=CRVUSDT&interval=1d&startTime=1668470400000&endTime=1669939200000&limit=1000
