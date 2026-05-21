---
title: "MYX Finance Short Squeeze: Funding-Cap Stress on Binance Perpetuals"
date: 2025-09-09
entities:
  - MYX Finance
  - MYX
  - Binance Futures
---

## Summary

1. Binance MYXUSDT perpetual data shows a **315% two-day close-to-close move** from 2025-09-08 00:00 UTC through 2025-09-09 23:00 UTC: the contract opened the window at 3.4895 USDT and printed an 18.58 USDT high before closing at 14.478 USDT.
2. The move occurred with **12.55 billion USDT of two-day notional volume** and 44.17 million reported trades aggregated in one-minute candles. The largest one-hour quote volume was 720.47 million USDT at 2025-09-08 19:00 UTC.
3. Funding moved from ordinary levels into a squeeze regime: during the same 48-hour window, MYXUSDT funding summed to **-19.36% across hourly settlements**, with the floor reaching **-2.00% per settlement**. On Binance perpetuals, a negative funding rate means shorts pay longs, so the funding stream itself became a cost pressure on short exposure.
4. The mark/index relationship also broke from its pre-event behavior. Mark price traded as much as **3.06% below the index** during the squeeze window, while the premium index repeatedly moved negative, consistent with stressed derivatives pricing rather than clean spot-led price discovery.
5. Public reporting at the time described more than 40 million USD of MYX liquidations and raised concerns about thin liquidity, restricted float, and a targeted short squeeze. The Binance market data below supports those concerns, but it does **not** by itself prove spoofing, wash trading, or the identity/intent of any trader.

## Metrics used

### Price path and funding-rate stress

Perpetual funding is useful for market-health monitoring because it converts directional imbalance into a recurring cash flow between longs and shorts. Binance Academy describes negative funding as the regime where short positions pay long positions; therefore, deeply negative hourly funding can intensify a short squeeze by making it expensive to keep short exposure open.

{{< figure src="myx_price_funding_2025-09-01_12.png" alt="MYXUSDT price path and hourly funding rates from September 1 to September 12, 2025" caption="MYXUSDT last price, mark price, and per-settlement funding rates on Binance Futures. The shaded window covers 2025-09-08 through 2025-09-10 UTC." loading="lazy" >}}

The pre-squeeze week already showed abnormal acceleration: from September 1 to September 7, MYXUSDT rose from 1.2069 to 3.4880 USDT, a 189.0% close-to-close gain. The true squeeze window was sharper. From September 8 00:00 UTC to September 10 00:00 UTC, the contract rose from 3.4895 USDT to a high of 18.58 USDT, a 432.5% high-from-open move.

The funding-rate regime changed at the same time:

| Window (UTC) | Close-to-close return | High from window open | Quote volume | Funding-rate sum | Minimum funding |
|---|---:|---:|---:|---:|---:|
| Sep 1-8 pre-squeeze | 189.0% | 209.1% | 2.71B USDT | +4.09% | -0.11% |
| Sep 8-10 squeeze | 314.9% | 432.5% | 12.55B USDT | -19.36% | -2.00% |
| Sep 10-12 aftermath | -8.4% | 28.8% | 4.79B USDT | -23.33% | -2.00% |

The negative funding did not appear as a single isolated print. In the September 8-11 period, 17 hourly settlements were at or below -1.0%, and 29 were at or below -0.5%. A trader continuously short through the 48-hour squeeze window would have faced roughly 19.36% of notional in funding-rate drag before considering mark-to-market losses, liquidation thresholds, slippage, or fees.

### One-minute notional flow

{{< figure src="myx_minute_price_volume_2025-09-08_10.png" alt="MYXUSDT one-minute price and notional volume during the September 8-10 squeeze" caption="One-minute Binance Futures data shows a distributed but persistent high-volume squeeze, not a single bad candle." loading="lazy" >}}

The one-minute data rejects a simple "one wick" explanation. Across 2,880 one-minute candles in the squeeze window:

- total quote volume was 12.55 billion USDT;
- the largest one-minute notional print was 52.42 million USDT at 2025-09-08 16:47 UTC;
- that largest minute represented only 0.42% of the two-day quote volume;
- the top one-minute burst contained 110,246 trades, about 475 USDT of quote volume per reported trade, and 59.9% taker-buy quote share;
- taker-buy quote volume was 50.82% of total quote volume across the full two-day window, so the price move did not require an obvious all-buy tape in the public aggregate candles.

This is a useful market-health distinction. The event looks less like a data glitch or one forced fill, and more like a sustained derivatives feedback loop: price rise, shorts under mark-to-market pressure, negative hourly funding, further forced de-risking, and continued volatility around the mark price.

### Mark/index basis and premium behavior

{{< figure src="myx_mark_index_premium_2025-09-01_12.png" alt="MYXUSDT mark-index basis and premium index during the September 2025 squeeze" caption="The mark/index basis repeatedly moved negative during and after the squeeze, consistent with stressed perpetual price discovery." loading="lazy" >}}

Before September 8, the MYXUSDT mark price generally stayed close to the index, with mild positive basis. During the squeeze, the mark-index basis turned unstable and reached -3.06% at 2025-09-09 16:00 UTC. That matters because mark price is the reference used for unrealized PnL and liquidation mechanics on perpetual venues.

A negative basis during a rising price episode is not sufficient to prove manipulation. It does, however, show that the perpetual contract's risk controls were absorbing a volatile and expensive positioning imbalance. In a small-float asset, that is exactly the configuration where liquidations and funding can become part of the price-discovery mechanism rather than passive risk-management outputs.

## Market-health interpretation

The MYX episode has three surveillance signals that should be monitored together:

1. **Float/liquidity mismatch:** Public reporting described a token with limited circulating supply and a valuation far above protocol liquidity metrics. Restricted float makes it easier for marginal flow to move price.
2. **Funding-cap stress:** The MYXUSDT funding series reached -2.00% hourly settlements and stayed deeply negative across many hours. This is a direct cost applied to short notional and can accelerate short-covering behavior.
3. **Derivatives-led volume:** Binance Futures recorded 12.55 billion USDT of MYXUSDT notional in the two-day squeeze window, far beyond normal project-liquidity context. When derivatives notional dominates the observable market, liquidation and funding mechanics can shape the path of the underlying token narrative.

The most conservative conclusion is that MYXUSDT entered a derivatives stress regime where a thin-float asset, fast price appreciation, negative funding, and large perpetual notional reinforced each other. That conclusion is data-backed without needing to identify a specific manipulator.

## Data and reproducibility

The article uses public Binance Futures endpoints only:

- [Kline/Candlestick Data](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data) for MYXUSDT OHLCV, trade count, and taker-buy volume.
- [Funding Rate History](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History) for MYXUSDT funding rates and funding-time mark prices.
- Binance mark-price, index-price, and premium-index kline endpoints for basis checks.

Generated files:

- [`myx_binance_1h_market_data_2025-09-01_2025-09-12.csv`](myx_binance_1h_market_data_2025-09-01_2025-09-12.csv)
- [`myx_binance_1m_event_window_2025-09-08_2025-09-10.csv`](myx_binance_1m_event_window_2025-09-08_2025-09-10.csv)
- [`myx_binance_funding_rates_2025-09-01_2025-09-12.csv`](myx_binance_funding_rates_2025-09-01_2025-09-12.csv)
- [`myx_binance_window_summary.csv`](myx_binance_window_summary.csv)
- [`myx_top_25_one_minute_bursts_2025-09-08_10.csv`](myx_top_25_one_minute_bursts_2025-09-08_10.csv)
- [`build-myx-evidence.py`](build-myx-evidence.py), which regenerates the CSV files and figures.

## Limitations

This analysis intentionally avoids stronger claims than the public data can support. Binance aggregate candles do not reveal account identity, hidden order-book intent, liquidation order IDs, or whether specific traders coordinated activity. The article therefore treats the event as a market-health stress case: the public data supports short-squeeze and derivatives-feedback concerns, while attribution of deliberate manipulation requires venue-level order and account data.

## References

- CoinDesk, ["More Than $40M Liquidated as Market Makers Suffer Shattering MYX Short Squeeze"](https://www.coindesk.com/business/2025/09/09/more-than-usd40m-liquidated-as-market-makers-suffer-shattering-myx-short-squeeze), published September 9, 2025.
- Binance Academy, ["What Are Funding Rates in Crypto Markets?"](https://www.binance.com/en/academy/articles/what-are-funding-rates-in-crypto-markets), updated August 28, 2024.
