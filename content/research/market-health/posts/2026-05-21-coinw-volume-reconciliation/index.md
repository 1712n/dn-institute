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

This snapshot tests whether CoinW's public 24-hour spot volume reconciles with
two manipulation-relevant market-health surfaces: the recent-trade feed and the
visible top-of-book depth. It is a probabilistic surveillance report, not a
final accusation. The goal is to identify concrete manipulation-risk signals
that can be reproduced from public data and escalated into longer websocket
capture.

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
- [projection_bootstrap_ci.csv](projection_bootstrap_ci.csv)
- [coinw_recent_trades.csv](coinw_recent_trades.csv)
- [coinbase_recent_trades.csv](coinbase_recent_trades.csv)
- [reported_to_projected_volume_ratio.svg](reported_to_projected_volume_ratio.svg)
- [time_slice_reconciliation.csv](time_slice_reconciliation.csv)
- [time_slice_spread_range.svg](time_slice_spread_range.svg)

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

### Robustness and confidence

Because the REST trade samples are short, each reported/projected multiplier was
bootstrapped 5,000 times by resampling recent trade notionals while holding the
observed trade rate fixed. This does not remove all uncertainty: it does not
model intraday seasonality, API pagination limits, off-book internalization,
market-maker inventory cycles, or differences between USDT and USD books. It
does quantify whether the point estimate is stable enough to use as a
manipulation-risk signal.

The public REST endpoints used for this snapshot return only recent trades, so
the article does not present retrospective 1-minute, 5-minute, or 10-minute
windows as if they were complete historical samples. The sensitivity checks
available from the initial capture are bootstrap uncertainty, cross-pair
comparison, and the Coinbase control venue. To test whether the strongest
single-snapshot signals persisted, I repeated the REST capture six times, roughly
every 30 seconds, from `2026-05-21T12:51:24Z` through
`2026-05-21T12:54:26Z`. Longer time-window sensitivity is still listed as
required follow-up websocket work below.

| Venue    |      Pair | Point estimate | 95% bootstrap interval | Confidence interpretation                                                                                          |
| -------- | --------: | -------------: | ---------------------: | ------------------------------------------------------------------------------------------------------------------ |
| CoinW    |  BTC/USDT |        `0.29x` |        `0.18x - 0.64x` | Initial mismatch only: the follow-up samples make this a lumpy-feed flag rather than a stable manipulation signal. |
| CoinW    |  ETH/USDT |        `1.12x` |        `0.59x - 2.68x` | Underpowered as a volume-mismatch signal; keep as a control pair.                                                  |
| CoinW    |  SOL/USDT |        `1.48x` |        `0.78x - 3.14x` | Underpowered on volume projection alone; elevated spread is the stronger signal.                                   |
| CoinW    |  XRP/USDT |        `0.85x` |        `0.65x - 1.19x` | Near reconciliation; elevated spread is the stronger signal.                                                       |
| CoinW    | DOGE/USDT |        `1.31x` |        `0.72x - 3.11x` | Underpowered as a volume-mismatch signal.                                                                          |
| Coinbase |   BTC/USD |        `1.37x` |        `0.71x - 4.70x` | Underpowered control sample because a few larger prints dominate the bootstrap range.                              |
| Coinbase |   ETH/USD |        `1.10x` |        `0.85x - 1.47x` | Stable control reconciliation.                                                                                     |
| Coinbase |   SOL/USD |        `1.01x` |        `0.63x - 1.72x` | Reconciles within the short-window uncertainty band.                                                               |
| Coinbase |   XRP/USD |        `1.08x` |        `0.61x - 2.20x` | Reconciles within the short-window uncertainty band.                                                               |
| Coinbase |  DOGE/USD |       `11.21x` |       `7.61x - 18.77x` | Fails the projection check but is explained by a very quiet DOGE sample; this is the main false-positive control.  |

The confidence adjustment changes the interpretation. The single-window
bootstrap flagged CoinW BTC/USDT, but the six-sample follow-up shows the
reported/projected ratio moving across both sides of `1.0x`; BTC should be read
as a lumpy recent-feed quality issue, not a stable mismatch. For CoinW SOL/USDT
and XRP/USDT, the volume projection itself is also not strong enough; the
manipulation-risk signal comes from combining high reported turnover with a much
wider live spread than the Coinbase control pair. The Coinbase DOGE/USD false
positive is a useful guardrail: a quiet recent feed can produce a dramatic
multiplier even on a mainstream venue, so the multiplier is never treated as a
standalone verdict.

{{< figure src="time_slice_spread_range.svg" alt="Spread range across six REST samples for CoinW and Coinbase" caption="Top-of-book spread ranges across six repeated REST samples. CoinW SOL/USDT and XRP/USDT keep materially wider visible spreads than the Coinbase control pairs." loading="lazy" >}}

| Venue    |     Pair | Reported/projected range | Median ratio |  Spread range bps | Follow-up interpretation                                                 |
| -------- | -------: | -----------------------: | -----------: | ----------------: | ------------------------------------------------------------------------ |
| CoinW    | BTC/USDT |          `0.81x - 9.31x` |      `1.97x` |   `0.004 - 0.018` | Ratio is volatile across adjacent samples; treat as lumpy-feed evidence. |
| CoinW    | SOL/USDT |          `0.78x - 5.51x` |      `1.44x` | `16.097 - 17.167` | Wide spread persists despite high reported volume.                       |
| Coinbase |  SOL/USD |         `3.00x - 12.31x` |      `7.41x` |   `1.167 - 1.168` | Projection ratio also moves, but the executable spread remains tight.    |
| CoinW    | XRP/USDT |          `1.36x - 1.75x` |      `1.51x` | `21.986 - 21.986` | Spread signal is stable across all six samples.                          |
| Coinbase |  XRP/USD |          `0.74x - 3.50x` |      `1.95x` |   `0.733 - 0.734` | Control venue keeps tight spread while the projection ratio varies.      |

## Findings

### 1. CoinW BTC volume looks lumpy but not stable enough on its own

CoinW's BTC/USDT ticker volume is in the same order of magnitude as Coinbase
Exchange BTC/USD, but the recent trade feed is much thinner. The 50-print CoinW
sample spans 106 seconds, while the 100-print Coinbase sample spans only 24.6
seconds. If both venues are reporting similar daily BTC turnover, the lower
print density means CoinW's flow is more dependent on large, intermittent
prints.

The initial bootstrap interval for CoinW BTC/USDT stayed below `1.0x`, but the
six repeated samples moved from `0.81x` to `9.31x`. That reversal matters. It
means the BTC signal is not a stable manipulation indicator from REST data
alone. The safer interpretation is that the public recent-trade feed is lumpy
enough that ordinary snapshots cannot reliably audit the headline 24-hour ticker
volume. A reviewer should request a longer executed-trade export or websocket
capture before relying on the headline BTC volume.

### 2. SOL and XRP show high reported turnover with wider visible liquidity

CoinW's SOL/USDT snapshot reported about `$108.4 million` of 24-hour quote
volume, but the live top-of-book spread was `16.18` basis points. Coinbase
SOL/USD, by contrast, showed about `$71.0 million` of 24-hour quote volume with
a `1.17` basis-point spread in the same capture window.

The XRP comparison points in the same direction. CoinW XRP/USDT reported about
`$22.6 million` of 24-hour quote volume with a `21.99` basis-point spread,
whereas Coinbase XRP/USD reported about `$77.5 million` with a `0.73` basis-point
spread.

The six-sample recheck strengthens this part of the case. CoinW SOL/USDT stayed
between `16.10` and `17.17` basis points, while Coinbase SOL/USD stayed near
`1.17` basis points. CoinW XRP/USDT stayed at `21.99` basis points in every
sample, while Coinbase XRP/USD stayed between `0.733` and `0.734` basis points.
Those spread gaps persisted even when reported/projected volume ratios moved
around between adjacent REST samples.

The bootstrap table deliberately downgrades the volume-projection confidence
for SOL and XRP: their intervals cross `1.0x`. The manipulation-oriented signal
is therefore cross-sectional, not just statistical. A venue reporting large
turnover while maintaining a much wider live spread than the control venue may
be printing volume that does not translate into competitive user-facing
liquidity. Confounders remain possible, especially fee tiers, quote-currency
differences, market-maker obligations, and temporary inventory limits.

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

The public data does not prove wash trading on CoinW. It does produce bounded,
reproducible manipulation-risk signals. BTC/USDT shows why short REST
reconciliations need guardrails: the initial bootstrap mismatch did not persist
as a stable ratio across adjacent samples. SOL/USDT and XRP/USDT are stronger
review targets because their wide visible spreads persisted while comparable
Coinbase pairs remained tight. Those reconciliation gaps should be escalated
into longer websocket surveillance before users, listing teams, or researchers
treat headline volume as a liquidity proxy.

## Sources

- [CoinW API documentation: 24H trade summary](https://www.coinw.market/api-doc/en/spot-trading/market/get-24h-trade-summary-for-all-instruments)
- [CoinW API documentation: recent trades](https://www.coinw.market/api-doc/en/spot-trading/market/get-recent-trades)
- [CoinW API documentation: order book](https://www.coinw.market/api-doc/en/spot-trading/market/get-order-book)
- [Coinbase Exchange API documentation: product trades](https://docs.cdp.coinbase.com/api-reference/exchange-api/rest-api/products/get-product-trades)
- [Coinbase Exchange API documentation: product stats](https://docs.cdp.coinbase.com/api-reference/exchange-api/rest-api/products/get-product-stats)
