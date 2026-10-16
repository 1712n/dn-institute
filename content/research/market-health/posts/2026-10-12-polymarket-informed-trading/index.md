---
title: "Informed trading on Polymarket: a wallet that bought Maduro's ouster at 7¢ hours before it was public"
description: "All political Polymarket markets over Nov 2025 – May 2026 (13.2M trades, 734k wallets), scored with an interpretable episode model and filtered through survivorship, lifetime, event-publicity and first-public-signal controls. Most 'surprise' resolutions are explained by public events; one wallet is not: a days-old account accumulated 'Maduro out by Jan 31' at ~7¢, with its last buy about three hours before the first explosions in Caracas, and made +$404k."
date: 2026-10-12
entities:
  - Polymarket
  - Maduro
  - Venezuela
---

## Summary

Buying a cheap outcome that later wins is not, by itself, evidence of insider trading — in any
market that resolves as a surprise, someone bought the winner cheap. Looking only at winners is
survivorship bias. The useful question is narrower: did a wallet take a large, cheap position on
a **non-public** outcome, **before** it became public, in a way that is abnormal for that wallet,
and not explained by blanket-betting every sibling outcome?

We collected every political Polymarket market resolving between 1 November 2025 and 1 May 2026
(**15,604 markets, 13.2M trades, 734k wallets**), picked candidate markets with two independent
screens (a price-jump screen and a wallet screen), scored each (wallet × market) episode with an
interpretable model, and then ran it through four controls that remove false positives:
survivorship, lifetime profile, event publicity, and timing against the first public signal.

- **36 of 48** candidate markets are explained by **public** events (vote counts, exit polls,
  announcements). A sharp price jump is not insider trading.
- The headline "Iran-strike" suspects turn out to be **serial gamblers** who bet up to 33 strike
  dates across the Iran ladders and won one.
- Synchronous "clusters" are a weak signal: co-occurrence links wallets that trade the same
  markets at the same time, and it only adds +3 to a score.
- One wallet survives every control: `0x31a56e…`, a days-old wallet, accumulated **"Maduro out by Jan 31"** at **~7¢**. Its last buy was at **02:58 UTC on
  3 January**, about **3 hours before** the first explosions in Caracas and 6.4 hours before the
  capture was announced. Held to resolution, the position paid **+$404,221**.

Read every flag below as a priority for review, not a verdict.

{{< figure src="maduro-timeline.png" alt="Maduro-out price path with wallet buys before the public capture" caption="'Maduro out by Jan 31' traded at 7–20% all December. Wallet 0x31a56e… (red, size ∝ $) accumulated ~$32.5k at ~7¢ from 31 December; the last buy was at 02:58 UTC on 3 January, before the first explosions in Caracas (~05:50 UTC, dotted) and Trump's announcement (09:21 UTC), when the price jumped to ~1 (dashed)." >}}

## Data

All public: Polymarket **Gamma** (market metadata and resolution), **Data API**
(`/trades`, `/positions`, `/activity`) and **CLOB**, none of which needs a key. An optional
funding lookup on Polygon (`code/src/trace.py`) uses Etherscan v2 and needs a free
`ETHERSCAN_KEY`; it is not part of the pipeline, and none of the results below depend on it. Scope: binary, resolved political markets (`tag_id=2`) with resolution date inside
the window. The unit of analysis is the **episode = (wallet × market)**: all buys of the winning
outcome by one wallet before the market's jump, at least $100 in total.

Key derived fields: the winning outcome from `outcomePrices`; the outcome's **price path
reconstructed from the trade tape** (CLOB `prices-history` is empty for neg-risk markets);
`t_event`, the **resolution-jump** — the first trade of the final sustained move of the winner
above 80%, i.e. when the market absorbs the information; and `t_public`, the **first public
signal** of the event from the OSINT timeline (explosions in Caracas came hours before the
capture was announced). For most events the two coincide. Per-wallet baselines (median trade
size, average position, cheap-bet record) come from the full trade tape; lifetime PnL comes from
`/positions`, and the date of a wallet's first Polymarket action from `/activity`.

Limitations: `data-api/trades` pages newest-first and stops after roughly 10k trades, so the
earliest history of large markets is truncated. The detector marks a market `history_truncated`
when it has 9,000 or more collected trades — 334 markets, including "Maduro out by Jan 31", whose
collected tape (9,367 trades) starts on 12 December. For these markets the early price comes from
the collected tape, not the market's first trades; the flag is kept in `surprise_markets.csv`. Baselines are politics-only; Polymarket
proxies are gasless (no gas-funding link between wallets).

## Interpretable heuristics

Each episode gets an explainable score **S = 2·T + 2·V + P + 2·A + R** (time, size and anomaly
weighted higher, as they tie most directly to informed entry):

| Signal | Definition | Threshold → points |
|---|---|---|
| **T** timing | volume-weighted entry before `t_public` | <5m=5 · <15m=4 · <1h=3 · <6h=2 · <24h=1 · later=0 |
| **V** volume | `max_buy / median(wallet's trades)` | 2–3×=1 · 3–5×=2 · 5–10×=3 · >10×=4 |
| **P** price | entry price of the winner (`vwap`) | ≤0.15=4 · ≤0.25=3 · ≤0.40=2 · ≤0.55=1 |
| **A** anomaly | position vs the wallet's average position | 2×=1 · 3×=2 · >3×=3 · ≥5×=4 |
| **R** record | cheap-bet wins elsewhere (scored market excluded) | 2 wins at 66%=1 · 3 at 75%=2 · 4 at 80%=3 · 5 at 80%=4 · 7 at 70%=5 |

**Fresh wallets.** A wallet that first appeared on Polymarket days before its bet has no history
to compare the bet against: its median trade is the bet itself, so V and A come out near zero
exactly where they matter most. If the wallet's first Polymarket action was at most **7 days** before its first buy
in the market, and the bet is a long shot (≤25¢) of at least **$1,000**, V and A are taken at
the cap. 39 episodes meet this rule.

Modifiers turn `S` into `S_final`:

- **M_lifetime** ∈ [0.3, 1.4] — few markets over the wallet's life ↑, high-activity net losers ↓;
- **M_sibling** = 0.5 for fan bettors (survivorship control, below);
- **M_event** by OSINT tier: HIGH 1 · MED-HIGH 0.85 · MED 0.7 · LOW-MED 0.45 · LOW 0.3;
- **M_public** = 0.3 if more than half of the episode was bought after `t_public` (news reaction);
- **+3** if the wallet belongs to a synchronous co-occurrence cluster.

`S_final = S · M_lifetime · M_sibling · M_event · M_public + cluster`. An episode with
`S_final ≥ 12` is flagged.

## Method

1. **Event selection** — two screens. The *price-jump screen* takes markets where the winner was
   cheap early in the collected tape (≤55%) and ended above 80%. It ranks markets by the whole
   move, so it misses markets that broke in their last hours, such as "Maduro out by Jan 31". The
   *wallet screen* closes that gap: wallets that won every market they traded, at long odds, hand
   their markets to the same scoring. The screens give 37 and 12 markets, one in common. One of
   the 48, the novelty market `will-pete-hegseth-ban-claude-by-march-31`, gets an OSINT tier but
   is left out of scoring.
2. **Episode scoring** — `S_final` for everyone who bought the winner **before** the jump.
3. **Survivorship control** — did the wallet also buy the same cheap outcome on the *losing*
   sibling markets (other dates in a series)? If it bet at least 3 dates and won at most a third
   of them, winning once is luck.
4. **OSINT event verification** — reconstruct the public timeline; was the entry before the first
   public signal about a *non-public* fact? The event tier is set by rule from the event type, one
   step up when the fact existed privately before it was disclosed.
5. **Wallet age** — the first Polymarket action of every wallet behind a large long shot, from
   `/activity` (cached in `code/inputs/wallet_first_activity.csv`).
6. **Skill vs insider** — consistently profitable sharp traders (who win on *public* events) are not insiders.

### Ranking

With no ground-truth labels, the ranking is an **interpretable, unsupervised priority**, not a
calibrated probability. Wallets are ordered by the number of independent markets on which they
were flagged, then by the profit of their flagged episodes. Public-event, news-reaction and
blanket-bet episodes are demoted before the threshold, so they rarely reach the list; repetition
across independent events comes first, then the money at stake. Every component is auditable,
so each flag carries a traceable chain: episode → signals → event.

The threshold produces **258 flagged episodes from 249 wallets**; only 7 wallets are flagged on
more than one market.

## Results

### Most "surprises" are public

Of the 48 candidate markets, OSINT places **36** in the LOW / LOW-MED tier — elections (NJ, VA,
Peru, Hungary, Japan, Portugal), congressional votes, Fed-chair announcements, shutdown votes.
Their price jumps coincide with public vote counts, exit polls, or statements. Six reach HIGH /
MED-HIGH: the Trump–Maduro secret call ([NYT, 28 November](https://www.nytimes.com/2025/11/28/us/politics/trump-spoke-by-phone-last-week-with-maduro-venezuelas-leader.html); two markets), the Maduro
capture, the 28 February strike on Iran ([CENTCOM](https://www.centcom.mil/Portals/6/Documents/Publications/260302-Fact%20Sheet.pdf); two markets) and the strike on
Syria ([CENTCOM, 19 December](https://www.centcom.mil/MEDIA/PUBLIC-RELEASES/Article/4365803/centcom-launches-operation-hawkeye-strike-against-isis-in-syria/)). The source for each non-public event is in the
`source_url` column of `event_tiers.csv`.

{{< figure src="event-relevance.png" alt="distribution of 48 candidate markets by insider-relevance" caption="A sharp resolution jump is not insider trading: 36 of 48 candidate markets are explained by public events." >}}

### The control that matters: survivorship

Polymarket runs the strike on Iran as several ladders — daily "will the US next strike Iran on
[date]", weekly markets, and "US / Israel strikes Iran by [date]" deadlines — and only the
28 February dates won. We treat all of them as one series. The wallets that looked surgical in a
winner-only view actually bought cheap YES across many dates and lost almost all of them —
`Embarrassed-Wording` 23 dates, `Next-Reader` 15, `Present-Plunger` 12 — a tail-betting strategy,
not information. Across all date series, 357 episodes are demoted this way.

{{< figure src="iran-baserate.png" alt="Iran-strike suspects bet many dates and won one" caption="Base-rate control. Each top 'Iran-strike' episode that bet several dates bought cheap YES on 3–33 strike dates across the Iran ladders and won exactly one. Winning Feb 28 is survivorship, not precision." >}}

The first-public control works the same way on the Maduro market: 183 of its 296 episodes were
bought mostly after the first explosions in Caracas and before the announcement — fast reaction
to breaking news, not prior knowledge — and are demoted.

Synchronous clusters are kept as a weak signal. Co-occurrence links 499 wallets into 60
clusters; the largest has 192 wallets across 26 markets, which looks like a crowd trading the
same news rather than one operator. Membership only adds +3 to a score.

### The wallet that survives every control

[`0x31a56e9e690c621ed21de08cb559e9524cdb8ed9`](https://polymarket.com/profile/0x31a56e9e690c621ed21de08cb559e9524cdb8ed9)
shows its **first recorded Polymarket activity on 27 December 2025**, four days before its first buy in this
market. Between 31 December and 3 January it bought [**"Maduro out by Jan 31"**](https://polymarket.com/event/maduro-out-in-2025/maduro-out-by-january-31-2026-318) — an outcome the market priced at ~7% through 2 January — accumulating
**$32,538** at an average of **7.4¢**, with its last buy at **02:58 UTC on 3 January**. The first
explosions in Caracas were reported at about 05:50 UTC (1:50 a.m. local); Trump announced the
capture on Truth Social at 09:21 UTC (4:21 a.m. ET), and the price jumped to ~1 a minute later
([timeline](https://chequeado.com/el-explicador/que-sabemos-de-los-bombardeos-en-venezuela-y-la-captura-de-nicolas-maduro-anunciada-por-donald-trump/)). Held to resolution, the position paid **+$404,221**; the wallet sold
nothing in this market before the jump.

Every signal aligns: a non-public covert operation, a days-old wallet, large size, and a cheap
entry against a 7% consensus in the hours before the first public sign. It also won two smaller related bets (US war-powers vs Venezuela at 4.7¢). The
pipeline flags it with `S_final = 22`: entry 12.4 hours before the first public signal (T=1), a
long shot (P=4), and size at the cap under the fresh-wallet rule (V=A=4).

It was not alone. 35 episodes on this market are flagged, 10 of them from wallets that were at
most a week old: `French-Incense` put $10,000 at 11¢ two hours before the first explosions with
its very first Polymarket trade (+$78k), and `Wee-Pseudoscience` $5,783 at 7¢ eight hours before
(+$75k). A wallet with some history, `Wobbly-Female`, bought $697 at 7.5¢ about 14 hours before
(+$8.6k).

### Other candidates

| Wallet | Bet | Entry | Profit | Why |
|---|---|---|---|---|
| `0xaec0bf01…` | both Trump–Maduro call markets | 17–40¢ | +$5,665 | entry around the private call, before the NYT report; fresh wallet; flagged on both |
| `0x54520a06…` | Russia does **not** take Kostiantynivka / Lyman by 31 March (NO) | 21–39¢ | +$12,548 | bought within two days of the wallet's first recorded Polymarket activity; battlefield long shots ([ISW, 29 March](https://www.kyivpost.com/post/72821)) |
| `0x8517b980…` | US strike Iran, Feb 28 | 4¢ | +$12,749 | very cheap — but it bet four strike dates and won one; not flagged |

{{< figure src="russia-towns-timeline.png" alt="Russia town-capture markets with wallet buys of NO" caption="Wallet 0x54520a… bought NO on 'Russia takes Kostiantynivka' (~21¢) and 'Lyman' (~39¢) on 9–10 January, when the market gave the captures 60–80%. Neither town fell by 31 March and both resolved No. A good battlefield read rather than a single pre-public spike: only the Kostiantynivka bet is flagged." >}}

{{< figure src="maduro-call-0xaec0bf.png" alt="Maduro-call markets with wallet buys in the private-call window" caption="Wallet 0xaec0bf01 bought both 'Trump talks to Maduro' markets at ~17–40% between 17 and 25 November, around the private call (~Nov 20–24, shaded) and before the NYT reported it on Nov 28 (dashed), when the price went to 1. A clean illustration of trading between a private fact and its public disclosure." >}}

{{< figure src="iran-strike-0x8517.png" alt="Iran-strike market with wallet buys, plus the base-rate caveat" caption="Wallet 0x8517b980 entered 'US strikes Iran on Feb 28' at ~4¢ — but it also bought YES on other strike dates and won only one, so the cheap entry is partly tail-betting, not clean precision. Shown as the honest counter-example." >}}

## Limitations and ethics

These scores are **priorities for investigation, not proof**. Alternative explanations exist:
public escalation context (there was visible US pressure on Venezuela), fast reaction to breaking
news, copy-trading, market-making, and plain luck on tail bets. Conclusions about any specific
wallet require off-chain corroboration.

Known weak spots of the model:

- Timing is only as good as the OSINT timeline. `Uneven-Skean` scores highest of all
  (`S_final = 40.7`) for buying "Israel strikes Iran by Feb 28" seconds before the recorded first
  report — more likely a reaction to the same news than prior knowledge.
- A crowd trading toward a public deadline looks like many small insiders: the Iran ceasefire
  market accounts for 105 of the 258 flagged episodes, most bought in the hours before Trump's
  Strait of Hormuz deadline ([ceasefire announced less than two hours before it](https://www.al-monitor.com/originals/2026/04/trump-agrees-two-week-ceasefire-iran-says-safe-passage-through-hormuz-possible)).
- Ranking by profit lifts large positions that only just cross the threshold (several wallets in
  the top 20 sit at `S_final` 12–13).
- Truncated tapes hide early buyers on mega-markets, and the fresh-wallet rule depends on
  `/activity`, which records Polymarket actions only.
- Wallet funding and cash-outs are not traced: the pipeline sees Polymarket trades, not
  transfers on Polygon.

## Reproducing

Code and CSV artifacts are in `code/` and `data/` next to this article; `code/README.md` lists
every step. In short: `run_collect_all.py` (collect) → `detect_surprises.py` (price-jump
screen) → `screen_wallets.py` (wallet screen) → `run_account_phase.py` (episode scoring,
controls, lifetime, clusters) → `build_artifacts.py` (event tiers, suspects per event) →
`make_figures.py` (every figure above). The OSINT timeline and the event classification are in
`code/inputs/event_analysis.csv`, with a source link for every non-public event. The trade
database (DuckDB, ~1.1 GB) is too large to commit; `run_collect_all.py` rebuilds it, and
`code/README.md` gives the SHA-256 of the snapshot behind these results.
Artifacts include `event_tiers.csv` (48 events), `episode_scores.csv`, `suspects_by_event.csv`,
`longshot_perfect.csv`, `perfect_winrate.csv`, `clusters.csv`, and the ranked
`suspicious_accounts.csv`.
