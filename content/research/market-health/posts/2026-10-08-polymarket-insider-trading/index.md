---
title: "Insider trading on Polymarket: 69 flagged wallets in 660 resolved markets, half of them in Iran war markets"
description: "A wallet-level screen of 660 resolved non-sports Polymarket markets from November 2025 to May 2026. It ranks 69 wallets on profit against luck, cheap buying before resolution, focus and account age, and it finds the account NPR reported for the Maduro trade without being told about it. Profit alone cannot be told apart from luck here. The flag is on a trading pattern, not on any person."
date: 2026-10-08
entities:
  - Polymarket
---

> **Scope.** Every wallet here is a pseudonymous Polymarket wallet, not an identified person. A high score means the trading looks like it used advance information. It is not a finding that anyone held inside information or broke a law.

## Summary

1. Of 17,798 wallets that spent at least $10,000 in these markets, 69 pass the screen. By Polymarket's own records they made $6.9M on them.
2. The screen finds a known case on its own. Rank 3 is Burdensome-Mix, the account NPR named for the bet on Maduro leaving office, which Polymarket shows making $404,222 on that market.
3. Half the flags sit in two groups of markets about the war with Iran: "US strikes Iran by" and "US x Iran ceasefire by".
4. Profit by itself proves nothing. If every bet were a fair coin flip, more wallets would look this lucky than actually do.
5. A new account is a weak sign. A third of the flagged wallets traded on their first day on Polymarket, but so did a quarter of ordinary large wallets.

## Data

The window is 1 November 2025 to 1 May 2026, as the challenge sets it. Markets come from Polymarket's public Gamma API: closed in the window, settled to one winner, and not sports, crypto prices, weather or other recurring markets. That leaves 660 markets (`data/markets_scope.csv`).

Trades come from the public Data API, maker and taker side. The API serves at most about 20,000 trades per market, so on 371 of the 660 markets only trades of $500 or more could be downloaded. The `kind` column says which markets are complete. For the 69 flagged wallets, the download holds a median 88% of the buying Polymarket records for them.

Profit comes from Polymarket's `/closed-positions` records, account dates from `/activity` and public profiles. No paid or private data is used. The scripts in `code/` rebuild every file in `data/`, and `code/README.md` gives the order.

## Method

Each wallet gets a score from 0 to 100 built from four signals.

**Edge, 40%.** Buying at price p pays 1/p for each dollar if the outcome wins, and wins with probability p if the price is fair. So a fair bettor expects zero profit, and the spread of that profit is known. The edge is the wallet's profit divided by that spread, a z score. Markets inside one event, like "by March" and "by April", are counted as one bet because they move together.

**Early cheap money, 30%.** Dollars spent on the winning side at a price of 0.50 or less, in the 72 hours before that side settled above 0.95.

**Focus, 15%.** How much of the wallet's money went into its largest event, and how few events it traded.

**New account, 15%.** Days from the wallet's first activity on Polymarket to its first buy in these markets.

A wallet enters the ranking if it spent at least $10,000, made a profit, has a z of 2 or more, and is not a market maker (one that buys both sides in similar size).

{{< figure src="score-components.png" alt="Stacked bars of the four score components for the top 25 wallets" caption="Score by signal for the 25 highest ranked wallets. Source: data/wallet_ranking.csv." >}}

## Profit against luck

To test the edge signal, every position was replayed 20 times at fair odds, one winning side per wallet and market, and the same filter was applied to the same wallets.

| z at least | wallets observed | expected by luck |
|---|---|---|
| 2 | 69 | 105 |
| 3 | 9 | 31 |
| 4 | 1 | 15 |

Fewer wallets clear each bar than luck alone would produce. Part of the gap is that cheap outcomes in these markets won less often than their price: by dollar weight, bets bought near 5 cents won 2.5% of the time. A fair-price replay hands cheap-side buyers more wins than they really get. Either way, a profit record does not identify an insider here, and the ranking leans on timing and price for that reason.

{{< figure src="edge-distribution.png" alt="Histogram of the edge z score across wallets, log scale" caption="Edge z score across wallets that spent at least $10,000. Source: code/06_score.py." >}}

## New accounts against a baseline

A random 300 of the 17,798 large wallets give the baseline. 27% of them made their first buy here within a day of joining, against 33% of the flagged wallets (`data/freshness_baseline.json`). Joining and betting the same day is common, which is why this signal carries the least weight.

## Top five

| rank | wallet | public name | score | profit | spent | largest event |
|---|---|---|---|---|---|---|
| 1 | 0x68558d…8f655a | Glistening-Touch | 66.6 | $200,525 | $12,565 | us-x-iran-ceasefire-by |
| 2 | 0x8039ad…a57421 | Lighthearted-Warlock | 57.8 | $159,141 | $12,699 | us-x-iran-ceasefire-by |
| 3 | 0x31a56e…db8ed9 | Burdensome-Mix | 56.1 | $406,366 | $33,453 | maduro-out-in-2025 |
| 4 | 0xdbf16b…bd86b5 | Upset-Subject | 53.5 | $336,479 | $147,841 | us-strikes-iran-by |
| 5 | 0xa4eb52…acd010 | Wet-Film | 53.4 | $397,908 | $69,370 | us-x-iran-ceasefire-by |

Profit is Polymarket's figure for the wallet in these markets. Spent is what the downloaded trades show. All 69 rows, with full addresses and every score component, are in `data/wallet_ranking.csv`.

Rank 1 put about $12,500 on the ceasefire markets within minutes of its first Polymarket activity and has no other closed position. Rank 2 opened the same way with about $12,700, then went on to trade short bitcoin markets.

Rank 3 matches NPR's account by name. NPR reported a bet of about $32,000 that paid over $400,000 ([NPR](https://wbhm.org/npr-story/a-400000-profit-on-maduros-capture-raises-insider-trading-questions-on-polymarket)); Polymarket records an average price of 0.0744 on its Maduro position. The Times of Israel reported a separate group of new accounts betting on an earlier ceasefire date ([Times of Israel](https://www.timesofisrael.com/polymarket-bets-on-us-iran-ceasefire-appear-to-suggest-insider-trading/amp/)). Those accounts were not matched to the wallets here.

## Limits

1. A wallet is not a person. One trader can run many wallets.
2. On 371 markets trades under $500 are missing, so someone who splits orders into small pieces can go unseen.
3. The edge score assumes every buy is held to the end. Most flagged wallets sold part of their position early, which makes their edge look larger than it was.
4. Settlement time is read from prices, as the last hour the winning side traded under 0.95.
5. Fast public news looks the same as inside information. A trader watching flight trackers an hour before the press would also buy early and cheap.
6. The cutoffs ($10,000, z of 2, 72 hours, 0.50) are choices, and other cutoffs give a different list.

## Related work

Larger screens of Polymarket exist. Mitts and Ofir examine over 210,000 wallet-market pairs, and Gómez-Cram and coauthors flag 1,950 accounts. Both are summarized in [Nechepurenko, arXiv 2605.02287](https://arxiv.org/abs/2605.02287), which calls the precision of such flags unknown. This post covers a shorter window, shows a luck baseline next to each signal, and checks profit against Polymarket's own records.
