---
title: "Polymarket informed-trading screen: audit trails over a black-box leaderboard"
description: "A reproducible public-data triage of potentially informed Polymarket trading, built as a trade-level investigation queue rather than an accusation engine."
date: 2026-10-07
entities:
  - Polymarket
---

## Summary

This investigation screens public Polymarket fills from **2025-11-01 through
2026-05-01** for patterns that merit follow-up. It deliberately does not claim
that any wallet is an insider: on-chain trading data can show unusual timing and
outcomes, but it cannot establish access to material non-public information.

The companion analysis is intentionally different from a conventional
profit-and-loss leaderboard. Every ranking row links back to individual,
time-stamped fills and decomposes its score into four visible signals: a correct
low-probability outcome, timing close to resolution, meaningful stake, and a
change from the preceding market price. A reviewer can reproduce the scope and
recalculate every number without an API key:

```bash
python3 research/polymarket-insider/collect_and_rank.py
```

The generated CSV evidence is in
[`research/polymarket-insider/artifacts/`](https://github.com/1712n/dn-institute/tree/main/research/polymarket-insider/artifacts):

| Artifact | Audit question it answers |
| --- | --- |
| `market_selection.csv` | Why was this market included, what was its resolved outcome, and was retrieval complete? |
| `all_taker_trades.csv` | Which public fills were used? |
| `candidate_trades.csv` | What exact fill triggered which score components? |
| `wallet_ranking.csv` | Which wallets should receive human follow-up first? |
| `lead_clusters.csv` | Is the signal a one-wallet pattern or a broad market event? |
| `checksums.sha256` | Do the submitted CSV artifacts match the recorded run? |

## Scope before results

The market universe is fixed before wallet scoring: resolved binary,
news-sensitive markets with an actual resolution inside the requested six-month
window, with reported volume from $100,000 to $3 million. The upper bound keeps
this a complete-tape pilot rather than a sampled mega-market study. A
public-policy/geopolitical title dictionary
includes elections, government, tariffs, conflict, central-bank decisions and
similar events; sports and price-direction markets are excluded. Markets are
then selected deterministically by numeric reported volume and market ID.

This prevents the usual hindsight trap: search until a lucky wallet appears,
then invent a reason to investigate it. It also makes the work small enough to
audit and extend.

## Result: leads, not a finding of insider trading

The reproducible run in this submission screened **33,934 taker fills across 12
markets**. It produced **20 flagged fills**, representing about **$11.6k** of
notional, across **13 wallets** and three market-level clusters. The largest
cluster contains 17 fills in the `US x Iran meeting by April 30, 2026?` market;
it is a cluster of distinct wallets reacting while the contract was still below
50¢, not evidence that those wallets are controlled by one person.

Most importantly, none of the 13 leads repeats across two flagged markets in
this scoped screen. The top wallet score is 43.0/100 and has only one flagged
market. That fails the report's own repeatability test, so this investigation
does **not** identify a wallet that should be described as likely insider
trading. It identifies a finite, transaction-linked review queue instead. This
negative result is intentional: a single correct, sizeable trade is compatible
with luck, public research, or an ordinary market thesis.

The highest-ranked lead is wallet
`0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b`: it bought 5,000 Yes shares
for $955.90 at 19.1¢, 146.9 hours before that market closed. Its associated
transaction is recorded in `candidate_trades.csv`. A reviewer should first
reconstruct its full net position and inspect public reporting between the fill
and the resolution; without corroboration, the appropriate conclusion remains
“lead for review,” not “insider.”

## Scoring model

The candidate score is a **priority score**, not a probability that someone is
an insider. A buyer of the ultimately winning outcome earns a trade-level score
from: an eventual winner bought below 50¢ (40%), entry within seven days of
resolution (25%), log-scaled notional (20%), and the difference from the median
of the preceding 20 fills on
the same outcome (15%). The latter is a one-sided, contemporaneous comparison:
the calculation never uses later prices to score an earlier trade.

Wallet priority combines its five strongest flagged trades (65%), repetition on
multiple markets (20%), and the share of its scoped buy notional placed on
eventual winners (15%). This design downweights a single fortunate bet and
favours a repeatable pattern.

## Limits and responsible use

The Data API exposes taker-side fills, not a wallet's complete economic history.
Accordingly this work does not calculate realised P&L, identify a wallet owner,
or allege misconduct. Before any finding, investigate the transaction and full
wallet history, reconstruct net position, compare the trade with a timestamped
public-news record, and look for on-chain funding or coordination links. Absence
of those corroborating facts should end the inquiry.

Polymarket's public API documentation:
[market data](https://docs.polymarket.com/market-data/overview) and
[trade endpoint](https://docs.polymarket.com/api-reference/core/get-trades-for-a-user-or-markets).
