# Who traded before the news on Polymarket, November 2025 to April 2026

## Short answer

This screen covers every resolved Polymarket market that closed between 1 November 2025 and 1 May 2026 with at least $100,000 of volume, leaving out sports, prices, weather, elections and scheduled data releases: 2,611 markets in 1,042 events, with every trade downloaded and only trades made in the window kept.

1. The ranking uses four signals anyone can check by hand: cheap money on the eventual winner in the last week, no bets on the losing outcomes of the same event, money concentrated in one event, and a new account. It ranks 17,588 wallets.
2. Eleven accounts were named by the press or by on-chain analysts as possible insiders in this period. Ten of them are among the tested wallets, and eight of those ten are in the top 100 of the ranking. If the ranking were random, the chance of that would be about 4 in 10^17.
3. The new finding is a group of 37 wallets that first appeared on Polymarket between 22 and 25 February 2026, traded the same outcomes in the same seconds, and all made money on the 28 February strikes on Iran: $1,330,938 together. The six fresh wallets that Bubblemaps reported on this event are different wallets, and I found no report of this group.
4. A luck replay, which I used in an earlier version, does not work on these markets: on 45 of 47 ladders of "by" dates the real outcome is impossible under it. Section 5 explains why, and the ranking no longer uses it.

Every entry is a pattern for review, not a finding that anyone held inside information. Each case names the explanations that would make it innocent.

## 1. Data

Markets. `code/01_markets.py` walks Gamma's `/markets/keyset` endpoint, which pages with a cursor and has no offset cap, in 17 slices of scheduled end date plus one walk ordered by volume. All 18 walks ran to an empty cursor or to the $100,000 floor (`data/gamma_walks.csv`). Gamma lists 4,352,131 closed markets.

Window. A market is in when 1 November 2025 00:00 UTC <= `closedTime` < 1 May 2026 00:00 UTC: 809,069 markets. The scheduled `endDate` would have been wrong both ways: 4,808 markets scheduled to end in the window closed outside it, and 10,550 that closed in it were scheduled outside it or had no end date (`data/window_counts.csv`). Trades before 1 November are dropped as well, so the analysis covers trading inside the window only. `code/check_pack.py` checks both. A wallet that already held shares on 1 November starts from that position, valued at the last price before it, so selling those shares does not look like selling shares it never had (`code/05b_opening.py`, `data/opening_positions.csv.gz`).

Scope. A market leaves at the first filter it fails (`code/03_scope.py`, `data/scope_filter_counts.csv`).

| filter | removed | left |
|---|---|---|
| closed in the window | | 809,069 |
| no decisive 0 or 1 outcome | 14,392 | 794,677 |
| sports and esports | 393,391 | 401,286 |
| price levels (crypto, stocks, commodities) | 336,035 | 65,251 |
| weather | 31,490 | 33,761 |
| recurring and counting markets | 17,220 | 16,541 |
| scheduled macro releases | 996 | 15,545 |
| elections | 2,593 | 12,952 |
| volume under $100,000 | 10,248 | 2,704 |
| price levels named only in the question | 93 | 2,611 |

What is left are markets whose answer a few people can know before it is announced: strikes, government actions, company news, awards. Elections are out because the answer comes from votes everyone sees at once, and data releases because they publish at a fixed minute.

Trades. `code/04_trades.py` pages the Data API `/trades` endpoint backwards with its `end` parameter until a window comes back short, so every tape is complete, with no cap at 10,000 trades. `code/check_tape_walk.py` shows the walk returns the same trades as a plain query. The tapes hold 26,867,900 trades.

When an outcome counts as known. A trade only counts as a prediction if it came before the outcome was known. `code/05_pack.py` takes the earliest of four clocks: the first ten-minute window with at least five trades where YES averaged 0.99 or more; the end of the day, month or year the question names, at midnight in New York ("before" a date means its start); for questions that name no date, the scheduled end date when it falls in the two days before the close; and `closedTime`. The first clock does not look at which side won. The clocks decided 614, 1,070, 138 and 789 markets. Eight markets were already decided before 1 November and keep no trades. The ten-minute windows are committed, and `code/check_pack.py` recomputes every clock.

Tested wallets. A wallet is tested when it bought at least $5,000 in the window before the known moments, is not a market maker (buying both sides in comparable size) and made at most 10,000 trades. That leaves 17,588 of 18,077 wallets, after 292 market makers and 197 bots. Their 6,303,832 trades are committed in `data/` and hold 67.3 percent of the dollars spent. The per-market figures of the wallets left out are committed too, so every exclusion can be recomputed. `sh code/run_analysis.sh data` rebuilds every output from the committed files.

## 2. Heuristics and ranking

Each tested wallet gets four signals from 0 to 1 (`code/10_score.py`).

- Early cheap money (40 percent): dollars on the eventual winner at 30 cents or less in the seven days before the outcome was known, counted only for shares still held then, on a log scale.
- Clean bet (20 percent): in the wallet's largest event, the share of its buying that went to the winning side. Someone who knows the date of a strike buys that date. A trader who buys many dates and wins one scores low.
- Focus (20 percent): the share of its money in its largest event, divided by the square root of how many events it traded.
- New account (20 percent): 1 when its first Polymarket activity, a deposit included, came on the day of its first buy here, falling to 0 at 30 days (`code/09_first_activity.py`).

The score is 100 times the weighted sum, and the ranking orders wallets by it. The weights are not fitted to anything. The first 100 wallets are the review list (`data/review_wallets.csv`, with every position in `data/review_positions.csv.gz` and every trade in `data/review_trades.csv.gz`). All 17,588 are in `data/wallet_ranking_full.csv.gz`.

A fifth heuristic looks at groups rather than single wallets. `code/11_lockstep.py` links two tested wallets when they bought the same outcome of the same market in the same second at least ten times, and then takes groups of linked wallets (`data/lockstep_groups.csv`, pairs in `data/lockstep_pairs.csv.gz`).

## 3. Does the ranking find what others found

`data/known_cases.csv` lists eleven accounts that the press or on-chain analysts named as possible insiders in this period. Each has a link to its source. Each address is printed in the source, in a profile link in the source, or belongs to a profile name the source printed, which `code/check_known_cases.py` confirms with Polymarket's public profile endpoint. The signals and weights were not tuned on them. `code/14_known.py` writes where each one lands (`data/known_case_recall.csv`).

| account | source | rank of 17,588 |
|---|---|---|
| ZachXBT target market, Axiom | [Cryptopolitan](https://www.cryptopolitan.com/insiders-cashed-in-before-axiom-reveal-wallets-bagged-1m-on-polymarket/) | 2 |
| US strikes Iran by 28 February, Dicedicedice | [The Block](https://www.theblock.co/post/391650/fresh-accounts-netted-1-million-on-polymarket-hours-before-us-airstrikes-on-iran-bubblemaps) | 3 |
| US strikes Iran by 28 February, Planktonbets | The Block | 4 |
| US x Iran ceasefire by 7 April | [Cointelegraph](https://cointelegraph.com/news/3-polymarket-traders-made-a-timely-bet-on-a-us-iran-ceasefire) | 5 |
| US strikes Iran by 28 February, Neodbs | The Block | 8 |
| Maduro out | [NPR via WBHM](https://wbhm.org/npr-story/a-400000-profit-on-maduros-capture-raises-insider-trading-questions-on-polymarket) | 13 |
| US strikes Iran by 28 February, largest wallet | The Block | 16 |
| ZachXBT target market, Axiom | Cryptopolitan | 24 |
| Super Bowl halftime performer | [Covers](https://www.covers.com/industry/polymarket-user-wins-nearly-all-super-bowl-halftime-wagers-and-profits-about-17k-feb-9-2026) | 753 |
| Google Year in Search (AlphaRaccoon), later charged | [Forbes](https://www.forbes.com/sites/boazsobrado/2025/12/04/alleged-insider-nets-1-million-on-polymarket-in-24-hours/), [charge](https://cryptopotato.com/google-engineer-accused-of-turning-secret-search-data-into-a-1-2m-polymarket-profit/) | 1,413 |
| US x Iran ceasefire by 7 April, second wallet | Cointelegraph | not tested: bought $4,020, under the floor |

Eight of the ten tested accounts are in the top 100. The two misses have reasons. The Super Bowl account still held only $24 of winning shares bought at 30 cents or less in the last week. The Google account first appeared on Polymarket 536 days before its first buy here and traded eleven events, so it is neither new nor focused, although its profit, $1,314,332, is the largest of all tested wallets.

This shows the ranking finds the accounts that analysts flag, at the scale of the whole market. It does not show those accounts are insiders. Journalists look for the same things: new accounts, cheap bets, timing.

Earlier-day control. `code/13_control.py` moves every outcome clock back by 7 and by 14 days, drops the trades after the moved clock, and ranks again with the same outcomes. In the real ranking, 100 wallets reach the score of rank 100. On the shifted days, 31 and 17 wallets do, and 9 and 5 of the real top 100 are still there (`data/control.csv`). High scores come from what wallets did in the last week before the news, not from being right in general.

## 4. Results

The review list is concentrated. 73 of the 100 wallets have the "US strikes Iran by" deadlines as their largest event, 9 the ZachXBT market, 7 the 7 April ceasefire, 3 Maduro and 3 Khamenei. 95 of the 100 first appeared on Polymarket, deposits included, within a day of their first buy in the screen, against 33.0 percent of all tested wallets. The new-account signal accounts for part of that gap.

### 37 wallets before the strikes on Iran

Of all 17,588 tested wallets, 1,725 belong to a lockstep group and there are 59 groups. Only four groups have five or more wallets that all first appeared within three days of each other. Three are on "Xi Jinping out in 2025" and made -$293, $193 and $81 together. The fourth is group 3 in `data/lockstep_groups.csv`:

- 37 wallets, first active between 12:08 UTC on 22 February and 07:26 UTC on 25 February 2026. 185 pairs inside the group bought the same outcome in the same second between 10 and 36 times.
- From 22 to 27 February they bought NO on every "US strikes Iran by" date from 22 to 27 February, at 89 to 99.5 cents. On 24 and 25 February they also bought NO on 28 February, at 86 to 90 cents.
- From 20:49 UTC on 27 February to 00:46 UTC on 28 February, every one of the 37 started buying YES on "US strikes Iran by February 28". By 05:58 UTC they had bought $218,348 of it at 30 cents or less. Among tested wallets, YES averaged 13 to 19 cents in every hour from 18:00 UTC on the 27th to 05:00 UTC on the 28th, and 84 cents in the 06:00 hour, when the strikes became known (`data/case_price_paths.csv.gz`).
- None of them bought YES on any strike date that resolved NO. In their largest event at least 93 percent of each wallet's buying went to the winning side.
- Every member made money, from $26,310 to $74,547, together $1,330,938. 36 of the 37 are in the top 100 of the ranking.

The public news ran the other way. On 27 February Oman's foreign minister, the mediator, told CBS that a deal was "within our reach", that in his view Iran had agreed to down-blend its enriched stockpile, and that technical talks were set for Vienna on the Monday ([CBS transcript](https://www.cbsnews.com/news/full-transcript-omani-foreign-minister-badr-albusaidi/)).

Bubblemaps reported six fresh wallets that made about $1 million on the same contract ([The Block](https://www.theblock.co/post/391650/fresh-accounts-netted-1-million-on-polymarket-hours-before-us-airstrikes-on-iran-bubblemaps)). Four of the six could be identified and are in the table above. None of the four is in this group.

Innocent explanations: one trader spreading a view across many wallets, which is still one trader's view; a copy-trading service mirroring one signal; or a confident public read that the strike would come before talks resumed. The market gave a strike by the 28th about one chance in six, so the YES bet alone was not a long shot.

## 5. Why there is no luck replay

A luck replay redraws outcomes at the traded prices and asks how often a wallet would do as well by chance. On a ladder of dates it has to draw one number per event, so that "by March 31" cannot resolve NO while "by March 15" resolves YES, and resolve each trade by comparing that number with the trade's price. Prices move, so the real outcome is often one that no draw produces: it needs the number above every YES price paid in the markets that resolved NO and below every YES price paid in those that resolved YES. On "US strikes Iran by", YES traded at up to 98 cents in dates that resolved NO and down to 5 cents in dates that resolved YES. `code/08_replay_check.py` takes the 47 events that are such ladders, with some dates resolved YES and some NO, and finds the real outcome out of reach in 45 of the 47, with 99.97 percent of their dollars (`data/replay_check.csv`). A wallet holding NO on one date and YES on the next then shows a profit that no replay reaches, and looks far more significant than it is. My earlier version reported such p-values. This version does not use them.

## 6. Limits

1. A wallet is not a person. The lockstep groups show that one trader can run many wallets, and the ranking counts each wallet separately.
2. The screen has no news clock. A trade just after a public announcement looks like one placed before it until the price moves.
3. For a market that ends NO, the known moment waits for the deadline or the close.
4. Wallets under $5,000, market makers and bots are not tested, so an insider who bets small is missed. One of the named ceasefire accounts is an example.
5. The scope, the cutoffs (30 cents, seven days, $5,000, ten shared seconds) and the weights are choices.

## 7. Related work

Mitts and Ofir screen all Polymarket markets from February 2024 to February 2026 on bet size, profitability, pre-event timing and directional concentration ([SSRN 7259741](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7259741)). Gomez-Cram, Guo, Jensen and Kung find that Polymarket's accuracy comes from about 3 percent of persistently skilled accounts reacting to public news ([SSRN 6617059](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6617059)). That is why this report does not read profit alone as insider trading.
