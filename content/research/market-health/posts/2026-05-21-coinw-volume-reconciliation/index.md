---
title: "CoinW Volume Reconciliation Snapshot"
date: 2026-05-21
entities:
  - CoinW
  - Coinbase Exchange
  - BTC
  - ETH
  - SOL
  - XRP
  - DOGE
---

## Summary

This snapshot checks whether CoinW's public 24-hour spot volume is easy to
reconcile against two other public market-health surfaces: the recent-trade feed
and the visible top-of-book depth. It is not a conclusive wash-trading finding.
It is a triage report that identifies where deeper surveillance should focus.

The strongest signal is volume quality rather than a single impossible number.
CoinW reported roughly `$547.4 million` of BTC/USDT turnover during the 24-hour
ticker window, which is comparable to Coinbase Exchange BTC/USD at roughly
`$490.7 million`. The recent-trade feed, however, showed only 50 CoinW BTC/USDT
prints over 106 seconds versus 100 Coinbase BTC/USD prints over 24.6 seconds.
That lower print density means CoinW's reported BTC volume depends on fewer,
larger, more irregular executions.

For SOL/USDT and XRP/USDT, the reconciliation concern is different. CoinW
reported high 24-hour quote volume while the live book snapshot showed much
wider top-of-book spreads than the Coinbase control venue. High reported turnover
paired with visibly wider quoted liquidity should be treated as a market-health
warning, because reported trades are not translating into a tight executable
market.

## Data collection

The snapshot was captured at `2026-05-21T12:07:05Z`. It uses only public,
unauthenticated endpoints:

- CoinW's 24-hour ticker endpoint, documented as a public REST interface that
  returns fields including `last`, bid/ask, and `baseVolume`.
- CoinW's recent-trades endpoint, documented as returning recent trade quantity,
  price, notional total, time, direction, and record ID for specified
  instruments.
- CoinW's order-book endpoint, documented as returning 5-level or 20-level bids
  and asks for specified instruments.
- Coinbase Exchange product trades and product stats endpoints as a control
  venue. Coinbase documents `/products/{product_id}/trades` as the latest-trade
  endpoint and `/products/{product_id}/stats` as the 24-hour and 30-day stats
  endpoint.

Supporting files:

- [venue_snapshot_summary.csv](venue_snapshot_summary.csv)
- [coinw_recent_trades.csv](coinw_recent_trades.csv)
- [coinbase_recent_trades.csv](coinbase_recent_trades.csv)
- [reported_to_projected_volume_ratio.svg](reported_to_projected_volume_ratio.svg)

## Reconciliation metrics

The table below compares CoinW with Coinbase Exchange for the same large-cap
assets. "Reported/projected" divides the venue's 24-hour reported quote volume
by a projection from the recent-trade feed: recent mean trade notional times
recent trades per second times 86,400 seconds. A value near `1.0x` means the
recent feed rate and mean trade size roughly reconcile with the reported daily
volume. It is a short-window metric, so it flags review targets rather than
proving manipulation.

| Venue    |      Pair | Reported 24h quote volume | Recent feed window | Trades/sec | Median recent notional | Reported/projected | Spread bps | 24h volume / top-20 book depth |
| -------- | --------: | ------------------------: | -----------------: | ---------: | ---------------------: | -----------------: | ---------: | -----------------------------: |
| CoinW    |  BTC/USDT |            `$547,426,548` |             `106s` |     `0.47` |            `$2,830.51` |            `0.29x` |    `0.004` |                       `1,526x` |
| Coinbase |   BTC/USD |            `$490,674,094` |            `24.6s` |     `4.06` |               `$19.43` |            `1.37x` |    `0.001` |                         `987x` |
| CoinW    |  ETH/USDT |            `$165,045,631` |             `238s` |     `0.21` |              `$822.72` |            `1.12x` |    `0.142` |                         `204x` |
| Coinbase |   ETH/USD |            `$189,738,689` |            `26.7s` |     `3.75` |              `$199.87` |            `1.10x` |    `0.047` |                       `1,214x` |
| CoinW    |  SOL/USDT |            `$108,371,239` |              `36s` |     `1.39` |              `$214.44` |            `1.48x` |   `16.178` |                         `160x` |
| Coinbase |   SOL/USD |             `$71,043,762` |            `52.3s` |     `1.91` |               `$21.75` |            `1.01x` |    `1.170` |                          `36x` |
| CoinW    |  XRP/USDT |             `$22,642,701` |             `524s` |     `0.10` |            `$1,848.93` |            `0.85x` |   `21.994` |                          `17x` |
| Coinbase |   XRP/USD |             `$77,522,054` |            `57.5s` |     `1.74` |               `$72.48` |            `1.08x` |    `0.734` |                          `62x` |
| CoinW    | DOGE/USDT |             `$10,121,759` |             `502s` |     `0.10` |               `$57.56` |            `1.31x` |    `3.063` |                          `16x` |
| Coinbase |  DOGE/USD |             `$16,638,726` |             `471s` |     `0.21` |                `$3.55` |           `11.21x` |    `0.958` |                          `20x` |

{{< figure src="reported_to_projected_volume_ratio.svg" alt="Reported to projected volume ratio by pair for CoinW and Coinbase" caption="Reported 24-hour quote volume divided by a projection from the recent trade feed. The metric is a short-window reconciliation check, not a standalone proof of wash trading." loading="lazy" >}}

## Findings

### 1. CoinW BTC volume is concentrated into a thinner print stream

CoinW's BTC/USDT ticker volume is in the same order of magnitude as Coinbase
Exchange BTC/USD, but the recent trade feed is much thinner. The 50-print CoinW
sample spans 106 seconds, while the 100-print Coinbase sample spans only 24.6
seconds. If both venues are reporting similar daily BTC turnover, the lower
print density means CoinW's flow is more dependent on large, intermittent
prints.

That is not automatically suspicious. Wholesale order flow can be lumpy, and a
50-trade REST sample can miss busier intervals. The market-health issue is that
the public feed does not make the reported volume easy to audit from ordinary
recent prints. A reviewer should request a longer executed-trade export or
websocket capture before relying on the headline 24-hour ticker volume.

### 2. SOL and XRP show high reported turnover with wider visible liquidity

CoinW's SOL/USDT snapshot reported about `$108.4 million` of 24-hour quote
volume, but the live top-of-book spread was `16.18` basis points. Coinbase
SOL/USD, by contrast, showed about `$71.0 million` of 24-hour quote volume with
a `1.17` basis-point spread in the same capture window.

The XRP comparison points in the same direction. CoinW XRP/USDT reported about
`$22.6 million` of 24-hour quote volume with a `21.99` basis-point spread,
whereas Coinbase XRP/USD reported about `$77.5 million` with a `0.73` basis-point
spread.

Wide spreads are not manipulation by themselves. They can reflect market-maker
risk, fee tiers, jurisdictional access, or temporary inventory constraints. They
do become a useful surveillance flag when paired with high reported turnover:
if many trades are happening, but the visible book remains wide, the venue's
reported flow may not represent competitive user-facing liquidity.

### 3. Repeat-size prints are present but not sufficient on their own

The CoinW SOL/USDT feed had one base size, `6.905 SOL`, repeated in 8 of 50
recent prints. BTC/USDT also had a small repeated size, `0.0005 BTC`, in 3 of 50
prints. These repetitions are worth tracking because execution bots commonly
reuse configured clip sizes.

The control sample warns against over-reading this signal. Coinbase DOGE/USD had
`10.60000000 DOGE` repeat in 41 of 100 prints, but those were tiny retail-sized
prints. Repeat size alone is a weak indicator. It becomes more meaningful only
when the repeated clips also carry large notional value, occur at stale prices,
or align with suspicious buy/sell alternation.

### 4. The right next test is a longer websocket capture

This REST snapshot is enough to identify review targets, not enough to conclude
that CoinW is fabricating volume. A stronger follow-up would capture at least
24 hours of websocket trades and order-book updates, then compute:

- trade-count-normalized volume against the 24-hour ticker,
- volume distribution skewness by pair,
- first-digit and round-lot concentration by notional size,
- buy/sell alternation at unchanged prices,
- spread and depth recovery after large prints,
- cross-venue price deviation during reported high-volume intervals.

If the longer capture keeps showing high ticker volume without a dense,
competitive, executable market, the case for artificial volume becomes stronger.
If the longer capture shows normal bursts and depth replenishment, the short
REST snapshot should be treated as a false-positive triage flag.

## Conclusion

The public data does not prove wash trading on CoinW. It does show that some
large-cap CoinW pairs deserve closer market-health review. BTC/USDT reports
Coinbase-scale daily turnover through a thinner recent print stream, while
SOL/USDT and XRP/USDT pair high reported turnover with much wider visible
spreads than the Coinbase control venue. Those are exactly the kinds of
reconciliation gaps that market-surveillance tooling should escalate before
users, listing teams, or researchers treat headline volume as a liquidity proxy.

## Sources

- [CoinW API documentation: 24H trade summary](https://www.coinw.market/api-doc/en/spot-trading/market/get-24h-trade-summary-for-all-instruments)
- [CoinW API documentation: recent trades](https://www.coinw.market/api-doc/en/spot-trading/market/get-recent-trades)
- [CoinW API documentation: order book](https://www.coinw.market/api-doc/en/spot-trading/market/get-order-book)
- [Coinbase Exchange API documentation: product trades](https://docs.cdp.coinbase.com/api-reference/exchange-api/rest-api/products/get-product-trades)
- [Coinbase Exchange API documentation: product stats](https://docs.cdp.coinbase.com/api-reference/exchange-api/rest-api/products/get-product-stats)
