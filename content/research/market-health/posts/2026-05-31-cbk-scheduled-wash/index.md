---
title: "Wash trading on a fixed clock: CBK/USDT routes 75% of its trades through two seconds"
description: "CBK/USDT churned about $448k in May 2026 with no pump or sustained trend, but 75% of its trades fired on just two seconds of the minute, one all sells, the other all buys. A self-trading bot firing every 90 seconds, alternating side, that randomises size to defeat clip detection but not its schedule."
date: 2026-05-31
entities:
  - Bybit
  - CBK
---

## Summary

1. **CBK/USDT churned about $448k in May 2026 with no pump or sustained trend** (it ended the month near where it started, drifting inside a 17% band), yet **74.6% of all trades and 59.6% of all volume landed on just two seconds of the minute**, :05 and :35. That is the footprint of a scheduler, not of organic demand.
2. **The two seconds are opposite sides.** Second :05 is **98.8% sells**; second :35 is **99.4% buys**. The bot fires about **every 90 seconds, alternating a sell and a buy**; because 90 seconds is a minute and a half, the trades land alternately on :05 and :35. Textbook self-trading to manufacture volume.
3. **The legs match.** Buys on :35 total about **$129.7k** against **$133.1k** of sells on :05, and across the month buying ($228.6k) and selling ($219.7k) are within about 4%, so almost no net position is built. It even pays the spread on essentially every round trip, so it loses money rather than earning it like a real market maker: turnover without exposure, manufactured at a cost.
4. **It evades the standard clip test.** Unlike the recurring-clip wash documented earlier in this wiki, CBK has **no dominant trade size** (the most common size is 0.5% of trades; the buy second alone carries 2,287 distinct sizes). The operator randomises the amount to look organic, but cannot randomise the clock.
5. **It runs all month.** Every single day of May, **47% to 91%** of that day's trades (median 79%) fall on the same two seconds. A control market, GAIB/USDT, puts only 3.3% on its busiest second; uniform would be 1.7%.
6. **Read this as a flag, not a verdict.** These are the time-of-trade and buy/sell signatures of a scheduled wash bot. They mark the market as worth scrutiny, not a proof of who runs it.

## The market: flat price, churned volume

CBK/USDT (Cobak Token) is a low-cap Bybit spot market, reporting roughly **$13k of daily turnover**. Through May 2026 its price drifted inside a narrow band, from about 0.235 to 0.274 USDT, and ended the month near where it started. Over the same month roughly **$448k changed hands**. Volume with no sustained direction is the first hint of a wash: someone is generating turnover without building a position.

{{< figure src="price-volume.png" alt="CBK/USDT daily close and daily volume across May 2026, flat price with steady churned volume" caption="CBK/USDT daily close (line) and daily volume (bars), May 2026. The price drifts and ends near where it began while about $448k churns. No pump, no trend." >}}

## The tell: two seconds of the minute

In an organic market trades are spread fairly evenly across the 60 seconds of each minute. The GAIB/USDT control sits near the 1.7% uniform line and peaks at only 3.3%. CBK does the opposite: **36.6% of its trades print on second :05 and 38.1% on second :35**, with almost nothing in between. Together those two seconds carry **74.6% of all trades and 59.6% of all volume**, about 22 times what a uniform clock would put there. Real demand does not arrive on a fixed second of the minute; a scheduled program does. The clustering is tighter still: within :05 and :35 the trades land around the same **0.5-second mark, inside a roughly 130-millisecond window**, far sharper than discretionary trading could place them. The concentration is specific to CBK: a second, unrelated low-cap control, BOBA/USDT, is also flat on these seconds (about 3%), so this is not a venue-wide timing quirk.

{{< figure src="second-of-minute.png" alt="share of CBK trades by second of the minute, with towering spikes on :05 and :35 versus a flat control" caption="Share of trades by second of the minute (UTC). CBK/USDT (bars) spikes on :05 and :35; the GAIB/USDT control (line) stays near the 1.7% uniform level." loading="lazy" >}}

## Two-sided self-wash

The two seconds are not one trade repeated: they are opposite sides of the book. Second :05 is **98.8% sells** and second :35 is **99.4% buys**. The bot fires about **every 90 seconds, alternating a sell and a buy**; since 90 seconds is a minute and a half, each trade lands 30 seconds further around the clock than the last, which is why the sells settle on :05 and the buys on :35. It trades with itself to print volume. The legs are matched in size, about **$129.7k of buys on :35 against $133.1k of sells on :05**, and across the whole month buying and selling stay within about 4% of each other ($228.6k versus $219.7k). The operator finishes May essentially flat, as a wash should. It is not a market maker earning the spread, either. Controlling for the month's price drift, it buys on :35 about **0.4% above** where it sells on :05 in **nearly every hour**, and sells below where it buys, so every round trip loses money. With taker fees on top, that comes to **several hundred dollars over the month**: the cost of manufacturing the volume.

{{< figure src="buysell-by-second.png" alt="buy share of CBK trades by second of the minute, near zero on :05 and near 100% on :35" caption="Buy share by second of the minute. Second :05 is almost all sells (red), second :35 almost all buys (green); every other second is roughly balanced." loading="lazy" >}}

## It hides its size, not its schedule

The earlier wash cases in this wiki ([Huobi](https://github.com/1712n/dn-institute/tree/main/content/research/market-health/posts/2023-08-14-huobi), [Senso](https://github.com/1712n/dn-institute/tree/main/content/research/market-health/posts/2021-01-05-Senso), and the recent [Bybit WCT and LMWR](https://github.com/1712n/dn-institute/tree/main/content/research/market-health/posts/2026-06-13-bybit-wct-lmwr) post) were caught by a **size** signature: a few repeated clip sizes that dominate the tape and skew the first-digit distribution. CBK leaves no such signature: its single most common trade size is only **0.5% of trades**, and the buy second alone carries **2,287 distinct sizes**, so clip-recurrence and first-digit tests find nothing. The amount is clearly randomised to look organic. What was not randomised is the timing. A fixed-second schedule is trivial to write and, evidently, easy to forget to hide, so time-of-trade catches what volume distribution alone would miss.

## Always on

This is not a one-off burst. Every day of May, between **47% and 91%** of that day's trades (median **79%**) land on :05 and :35, in all **24 hours** of the day. Nor is it confined to May: the same signature runs in **April** (about **67%** of trades on the same two seconds, sells on :05 and buys on :35), so it predates the window. The bot has been running for months, around the clock.

{{< figure src="persistence.png" alt="daily share of CBK trades on seconds 05 and 35 across May 2026, all bars far above the uniform line" caption="Share of each day's trades on :05 and :35 across May 2026. Never below 47%, median 79%, against a 3.3% uniform expectation." loading="lazy" >}}

## How this was measured

All figures use free, key-less data: Bybit's public spot trade dumps (`public.bybit.com/spot/CBKUSDT/`), the full May 2026 month (36,890 trades), one row per executed trade (timestamp, price, size, side). GAIB/USDT, another low-cap Bybit pair with organic trade timing, is used as a control. The metrics map to the DN [market-health family](https://dn.institute/market-health/docs/market-health-metrics/): time-of-trade concentration, buy/sell balance, and volume distribution. The analysis is fully reproducible: the fetch, metric, and figure scripts are in the companion repository [mkzung/cbk-scheduled-wash-analysis](https://github.com/mkzung/cbk-scheduled-wash-analysis), and `verify.py` recomputes and asserts every headline number from the dated dumps above.

A note on scope: this is a single market on a single venue over one month, read against a control rather than a labelled ground truth. The reading is the pattern, a fixed-clock two-sided self-wash that prints volume without taking a position, not an attribution of who placed the orders.
