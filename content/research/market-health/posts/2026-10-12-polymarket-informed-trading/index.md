---
title: "Informed trading on Polymarket: a wallet that bought Maduro's ouster at 7¢ hours before it was public"
description: "All political Polymarket markets over Nov 2025 – May 2026 (13.2M trades, 734k wallets), scored with an interpretable episode model and filtered through survivorship, lifetime and on-chain controls. Most 'surprise' resolutions are explained by public events; one wallet is not: it accumulated 'Maduro out by Jan 31' at ~7¢ up to 6 hours before a covert US operation became public, made +$404k, and cashed out."
date: 2026-10-12
entities:
  - Polymarket
  - Maduro
  - Venezuela
  - Binance
---

## Summary

Buying a cheap outcome that later wins is not, by itself, evidence of insider trading — in any
market that resolves as a surprise, someone bought the winner cheap. Looking only at winners is
survivorship bias. The useful question is narrower: did a wallet take a large, cheap position on
a **non-public** outcome, **before** it became public, in a way that is abnormal for that wallet,
and not explained by blanket-betting every sibling outcome?

We collected every political Polymarket market resolving between 1 November 2025 and 1 May 2026
(**15,604 markets, 13.2M trades, 734k wallets**), scored each (wallet × market) episode with an
interpretable model, and then — crucially — ran it through four controls that remove false
positives: survivorship, lifetime profile, event publicity, and on-chain single-operator checks.

- **28 of 35** "surprise" markets are explained by **public** events (vote counts, exit polls,
  announcements). A sharp price jump is not insider trading.
- The headline "Iran-strike" suspects turn out to be **serial gamblers** who bet 14–21 strike
  dates and won one.
- Synchronous "clusters" are **not** a single operator: their shared funders are infrastructure
  contracts, and the wallets span 2022–2026.
- One wallet survives every control: `0x31a56e…` accumulated **"Maduro out by Jan 31"** at
  **~7¢** up to **6 hours before** US special forces seized Maduro publicly, made **+$404,221**,
  and cashed out.

Read every flag below as a priority for review, not a verdict.

{{< figure src="maduro-timeline.png" alt="Maduro-out price path with wallet buys before the public capture" caption="'Maduro out by Jan 31' traded at 7–20% all December. Wallet 0x31a56e… (red, size ∝ $) accumulated ~$32.5k at ~7¢, last buy at 02:58 UTC on Jan 3 — 6.4h before US special forces seized Maduro and the price jumped to ~1 (09:22 UTC)." >}}

## Data

All public, keyless: Polymarket **Gamma** (market metadata and resolution), **Data API**
(`/trades`, `/positions`), **CLOB**; and on-chain Polygon via **Etherscan v2** for wallet
funding. Scope: binary, resolved political markets (`tag_id=2`) with resolution date inside the
window. The unit of analysis is the **episode = (wallet × market)**.

Key derived fields: the winning outcome from `outcomePrices`; the outcome's **price path
reconstructed from the trade tape** (CLOB `prices-history` is empty for neg-risk markets); and
`t_event`, the **resolution-jump** — the moment the winner's price snaps toward 1, i.e. when the
market absorbs the information. Per-wallet baselines (median trade size, breadth, cheap-bet
success) come from the data; lifetime PnL comes from `/positions`.

Limitations: `data-api/trades` returns at most ~11k recent trades per market, so the earliest
history of 242 mega-markets is truncated; baselines are politics-only; Polymarket proxies are
gasless (no gas-funding link between wallets).

## Interpretable heuristics

Each episode gets an explainable score **S = 2·T + 2·V + P + 2·A + R** (time and size weighted
higher, as they tie most directly to informed entry):

| Signal | Definition | Threshold → points |
|---|---|---|
| **T** timing | closeness of volume-weighted entry to `t_event` | <5m=5 · 1–6h=2 · >24h=0 |
| **V** volume | `max_buy / median(wallet's trades)` | 2–3×=1 · >10×=4 |
| **P** price | entry cheapness into the winner (`vwap`) | ≤0.15=4 · ≤0.40=2 · >0.55=0 |
| **A** anomaly | position vs the wallet's own average | 2×=1 · >3×=+1 |
| **R** record | luck-adjusted hit-rate on cheap bets | ≥5/5=4 · ≥7/10=5 |

Modifiers: a **lifetime multiplier** (fresh wallet ↑, high-activity net-loser "degen" ↓) and a
**+3 cluster bonus** for synchronized bursts, giving `S_final = S · M_lifetime + cluster`.

## Method

1. **Event selection** — detect markets where the winner was cheap early and snapped to ~1; fix `t_event`.
2. **Episode scoring** — `S_final` for everyone who bought the winner **before** the jump.
3. **Survivorship control** — did the wallet also buy the *losing* sibling markets (other dates in a series)? If so, winning once is luck.
4. **OSINT event verification** — reconstruct the public timeline; was the entry before the public news about a *non-public* fact?
5. **On-chain tracing** — wallet age, funding source, cash-out; test the single-operator hypothesis.
6. **Skill vs insider** — consistently profitable sharp traders (who win on *public* events) are not insiders.

### Ranking

With no ground-truth labels, the ranking is an **interpretable, unsupervised priority**, not a
calibrated probability. A wallet's rank is the maximum `S_final` among its episodes **that
survive the controls**: public-event and blanket-bet episodes are demoted; cheap, early,
abnormal entries on non-public events are promoted; repetition across independent non-public
events raises the rank. Every component is auditable, so each flag carries a traceable chain:
episode → signals → event → on-chain.

## Results

### Most "surprises" are public

Of the 35 substantive surprise markets, OSINT places **28** in the LOW / LOW-MED tier —
elections (NJ, VA, Peru, Hungary, Japan, Portugal), congressional votes, Fed-chair announcements.
Their price jumps coincide with public vote counts, exit polls, or statements. Only four reach
HIGH / MED-HIGH: the Trump–Maduro secret call and the Iran/Syria strikes.

{{< figure src="event-relevance.png" alt="distribution of 35 surprise markets by insider-relevance" caption="A sharp resolution jump is not insider trading: 28 of 35 surprise markets are explained by public events." >}}

### The control that matters: survivorship

The "will the US strike Iran on [date]" series has ~40 daily markets; only Feb 28 won. The
wallets that looked surgical in a winner-only view actually bought cheap YES across many dates
and lost almost all of them — a tail-betting strategy, not information.

{{< figure src="iran-baserate.png" alt="Iran-strike suspects bet many dates and won one" caption="Base-rate control. Each 'Iran-strike' suspect bought cheap YES on 3–21 strike dates and won exactly one. Winning Feb 28 is survivorship, not precision." >}}

Synchronous clusters fail a different control: on-chain, their shared funders are
high-fan-out infrastructure contracts, and member wallets were created years apart (2022–2026) —
inconsistent with one operator.

### The wallet that survives every control

`0x31a56e9e690c621ed21de08cb559e9524cdb8ed9` was **created on 26 December 2025**, five days
before its first trade, and funded with ~$478k. It bought **"Maduro out by Jan 31"** — an
outcome the market priced at ~7% through 2 January — accumulating ~$32.5k at an average of
**7.4¢**, with its last buys at **02:58 UTC on 3 January**. At **09:22 UTC on 3 January**, US
special forces seized Maduro in Caracas and the price jumped to ~1. The wallet realised
**+$404,221**, then zeroed out its positions.

Every signal aligns: a non-public covert operation, a fresh purpose-built wallet, large size, a
cheap entry against a 7% consensus in the hours before the public break, and an immediate
cash-out. It also won two smaller related bets (US war-powers vs Venezuela at 4.7¢).

### Other candidates

| Wallet | Bet | Entry | Profit | Why |
|---|---|---|---|---|
| `0x957015a2…` | Trump pardons CZ (Binance) | 25¢ | +$13,871 | pardons are non-public until signed; personal-EOA funder |
| `0x54520a06…` | Russia takes Lyman + Kostiantynivka | 21–39¢ | +$12,562 | battlefield longshots |
| `0x8517b980…` | US strike Iran, Feb 28 | 4¢ | +$12,749 | very cheap, fresh — but subject to the date-series caveat |
| `0xaec0bf01…` | both Trump–Maduro call markets | 17–40¢ | +$4,971 | entry before the NYT report of a private call; fresh wallet |

{{< figure src="cz-pardon-timeline.png" alt="CZ pardon market price with wallet buys before the pardon" caption="Wallet 0x957015… bought 'Trump pardons CZ (Binance)' at ~25¢ in late August, about two months before the Oct 23 pardon. Pardons are non-public until signed — though CZ's pardon push was itself publicly reported, so this is a softer flag than Maduro." >}}

{{< figure src="russia-towns-timeline.png" alt="Russia town-capture markets with wallet buys" caption="Wallet 0x54520a… entered 'Russia takes Lyman' (~39¢) and 'Kostiantynivka' (~21¢) cheaply in January; both then rose gradually as the front advanced publicly and resolved YES. Good battlefield reads rather than a single pre-public spike." >}}

{{< figure src="maduro-call-0xaec0bf.png" alt="Maduro-call markets with wallet buys in the private-call window" caption="Wallet 0xaec0bf01 bought both 'Trump talks to Maduro' markets at ~17–40% inside the private-call window (~Nov 20–24, shaded), before the NYT reported the call on Nov 28 (dashed) and the price went to 1. A clean illustration of trading between a private fact and its public disclosure." >}}

{{< figure src="iran-strike-0x8517.png" alt="Iran-strike market with wallet buys, plus the base-rate caveat" caption="Wallet 0x8517b980 entered 'US strikes Iran on Feb 28' at ~4¢ — but it also bought YES on four strike-dates and won only one, so the cheap entry is partly tail-betting, not clean precision. Shown as the honest counter-example." >}}

## Limitations and ethics

These scores are **priorities for investigation, not proof**. Alternative explanations exist:
public escalation context (there was visible US pressure on Venezuela), fast reaction to breaking
news, copy-trading, market-making, and plain luck on tail bets. Conclusions about any specific
wallet require off-chain corroboration.

## Reproducing

Code and CSV artifacts are in `code/` and `data/` next to this article. In short:
`run_collect_all.py` (collect) → `detect_surprises.py` (jump detector) → `run_account_phase.py`
(episode scoring + lifetime + clusters); OSINT verification and on-chain tracing use
`ETHERSCAN_KEY` (see `code/src/trace.py`). Artifacts include `event_analysis.csv` (35 events),
`suspects_by_event.csv`, `longshot_perfect.csv`, `perfect_winrate.csv`, and the ranked
`suspicious_accounts.csv`.
