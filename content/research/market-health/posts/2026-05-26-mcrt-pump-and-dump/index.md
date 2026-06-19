---
title: "A pump and dump on a low-cap Bybit spot market: MCRT/USDT, 2026-05-26"
description: "MCRT/USDT sat flat near 0.000097 USDT for weeks, then ran 162% to a 0.000255 blow-off top and crashed 66% in the same hour, settling below where it started. Reconstructed from free Bybit public trade data."
date: 2026-05-26
entities:
  - Bybit
  - MCRT
---

## Summary

1. **MCRT/USDT (MagicCraft) ran from a flat ~0.000097 USDT baseline to a 0.000255 blow-off top on 2026-05-26 (+162%), then crashed 66% back within the same hour** and settled about 11% below where it started. The shape is a textbook pump and dump.
2. **The decisive move was one hour, not one day.** The peak printed at **2026-05-26 14:03:37 UTC**, and the same UTC hour also held the crash. That hour traded about **$59.7k across 1,821 trades, roughly 27x the median baseline hour** ($2.2k).
3. **Late buyers were left underwater.** **276 buy trades (about $14.7k) filled above 1.5x the base price**, at an average of 0.000185. A day later MCRT traded near 0.000086, so those fills were down about **53%**.
4. **This is price manipulation, not wash trading.** During the pump the single most common exact trade size was only **0.2% of trades** (0.6% on the baseline), so the run-up was driven by genuine aggressive buying into a thin book, not by identical-clip volume inflation.
5. **Idiosyncratic and off the scale.** Normalised to the start of the event window, MCRT spiked to about **2.6x** while a liquid control (SOL/USDT) held within about **3%**. The crash off the peak was the **largest single five-minute drop of the whole month**, and the month's two sharpest upward moves both fell on 2026-05-26: the blow-off, and a failed dry run six hours before it. The peak hour was the **single busiest of all 744 active hours**.
6. **Read this as a flag, not a verdict.** These are the statistical and microstructure signatures of a pump and dump on a thin market. They mark the episode as worth scrutiny, not a proof of coordinated intent.

## The month: a flat market, then one spike

MCRT/USDT is a low-cap spot market: through most of May 2026 it traded in a narrow band around **0.000097 to 0.000106 USDT** on roughly **$57k of volume a day**, with order flow split close to evenly (about 48% of trades on the buy side). A market like this is thin enough that a modest amount of one-sided buying can move the price a long way.

On 2026-05-26 that is exactly what happened. The daily high jumped to **0.000255**, more than 2.6x the surrounding days, on a volume bar several times the monthly norm, and then the price fell straight back. Every other day in the month is unremarkable by comparison.

{{< figure src="price-volume-month.png" alt="MCRT/USDT daily high price and daily volume across May 2026, flat then a 05-26 spike" caption="MCRT/USDT daily high (line) and daily volume (bars), May 2026. A flat market for weeks, then a single-day spike to 0.000255 on a volume surge on 2026-05-26." >}}

## The ramp and the blow-off

Zooming into the trade tape, the run-up is gradual then violent. From 2026-05-25 the price grinds up from the 0.000097 base over roughly **38 hours**, then on 2026-05-26 it accelerates into a near-vertical blow-off, topping at **0.0002551 at 14:03:37 UTC (+162% over base)**. The crash is immediate: within the same UTC hour the price collapses about **66%** off the peak, back toward and then below the pre-pump base. The volume bars confirm the concentration: the 14:00 hour alone carried about **$59.7k on 1,821 trades, roughly 27 times the $2.2k median of a normal hour** earlier in the month.

The run-up was not one smooth push. About **six hours before the top**, at **08:14 UTC**, MCRT printed a dry run: a one-minute spike to **0.0001474 (about 1.5x base)** on roughly **19x** a normal five-minute volume, which round-tripped within about fifteen minutes. It is the sharpest five-minute up-move of the entire month, and it led nowhere: the price fell straight back. Only **four** buys cleared 1.5x base in that burst. The push that mattered came at 14:00, and it did not reverse until it had carried **272** more buyers above the same line.

{{< figure src="intraday-pump-dump.png" alt="five-minute MCRT price and volume from 2026-05-25 to 26 showing the ramp, blow-off to 0.000255, and same-hour crash" caption="Five-minute high price (line) and volume (bars), 2026-05-25 to 26 UTC. A slow ramp off the 0.000097 base, a failed dry run near 08:00, a vertical blow-off to 0.000255, then a same-hour collapse." loading="lazy" >}}

## Who got caught

A pump and dump transfers money from whoever buys near the top to whoever was already holding. The buy tape shows who paid: **276 buy trades, about $14.7k, executed above 1.5x the base price**, almost all of them within half an hour of the 0.000255 peak, at an average fill of 0.000185. Those buyers had no time to react. By the next day the token had settled near **0.000086**, leaving those fills down about **53%**, below the level MCRT traded at before the pump began.

{{< figure src="late-buyers.png" alt="scatter of MCRT buy execution prices over 2026-05-25 to 26, with buys above 1.5x base highlighted near the top and the next-day settled price below base" caption="Every buy trade over the event. Buys filled above 1.5x base (highlighted) cluster at the top; the dotted line is where MCRT settled the next day, below the pre-pump base." loading="lazy" >}}

## Idiosyncratic, and statistically off the scale

The move was specific to MCRT, not a market-wide event. Normalised to the start of the window, MCRT spikes to about **2.6x** and falls back below where it began, while a liquid control, SOL/USDT, holds within about **3%** over the same window: a flat line by comparison. Whatever lifted MCRT did not touch the rest of the market.

{{< figure src="control-comparison.png" alt="MCRT versus SOL normalized price over the event, MCRT spikes 2.6x while SOL stays flat" caption="MCRT/USDT and SOL/USDT, normalised to the start of 2026-05-25 12:00 UTC. MCRT spikes 2.6x and reverses; the liquid control barely moves." loading="lazy" >}}

The moves are extreme even against MCRT's own month. The crash five minutes off the peak was the **largest single five-minute drop of the entire month**, about **39 times the standard deviation** of all 5-minute moves in May; the two sharpest upward moves, the dry run and the real push, each cleared **25 times** that deviation. The 14:00 UTC hour that held the peak and the crash was the **single highest-volume hour of all 744 active hours**. Crypto returns are fat-tailed, so treat those multiples as a measure of scale rather than a Gaussian probability; even so, every tail of the month belongs to 2026-05-26. This is the footprint of a concentrated push and an equally fast exit.

## Not wash trading, but price impact

The earlier wash-trading cases in this wiki ([Huobi](https://github.com/1712n/dn-institute/tree/main/content/research/market-health/posts/2023-08-14-huobi), [Senso](https://github.com/1712n/dn-institute/tree/main/content/research/market-health/posts/2021-01-05-Senso), and the recent [Bybit WCT and LMWR](https://github.com/1712n/dn-institute/tree/main/content/research/market-health/posts/2026-06-13-bybit-wct-lmwr) post) inflate **reported volume** with identical-size clips while the price barely moves. This episode is the opposite signature. During the pump the most common exact trade size was only **0.2% of trades** (versus 0.6% on the quiet baseline), so there is no dominant repeated clip. Order flow stayed close to evenly split by count through the ramp. What moved was the **price**: a thin book, lifted by sustained aggressive buying, ran 162% before the sellers stepped in. That separates a pump and dump (a price-manipulation pattern, paid for by late buyers) from wash trading (a volume-inflation pattern that leaves price roughly where it found it).

## How this was measured

All figures use free, key-less data: Bybit's public spot trade dumps (`public.bybit.com/spot/MCRTUSDT/`), the full May 2026 month (227,644 trades), one row per executed trade (timestamp, price, size, side). The baseline is MCRT's own 2026-05-18 to 24 window, which acts as the control: the same market, the same week-of, immediately before the event. The metrics map to the DN [market-health family](https://dn.institute/market-health/docs/market-health-metrics/): volume distribution and clip recurrence, buy/sell balance, and time-of-trade concentration, here read against price rather than for volume inflation. The analysis is fully reproducible: the fetch, metric, and figure scripts are in the companion repository [mkzung/mcrt-pump-dump-analysis](https://github.com/mkzung/mcrt-pump-dump-analysis), run against the dated dump above.

A note on scope: this is a single market on a single venue over one month, and the baseline is statistical context rather than a labelled control. The reading is the pattern, a sharp one-hour run-and-reverse that leaves late buyers underwater, not an attribution of who placed the orders.
