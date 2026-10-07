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
window, with reported volume from $900,000 to $3 million. The upper bound keeps
this a complete-tape pilot rather than a sampled mega-market study. A
public-policy/geopolitical title dictionary
includes elections, government, tariffs, conflict, central-bank decisions and
similar events; sports and price-direction markets are excluded. Markets are
then selected deterministically by numeric reported volume and market ID.

Gamma exposes a scheduled `endDate` filter rather than an actual-closure filter.
The collector therefore uses monthly scheduled-date queries padded by 90 days,
then applies this report's window to `closedTime`/`umaEndDate`. It stops instead
of silently scoring a partial universe: a capped scheduled-date bucket is
bisected until the candidate set is completely retrievable.

This prevents the usual hindsight trap: search until a lucky wallet appears,
then invent a reason to investigate it. It also makes the work small enough to
audit and extend.

## Result: leads, not a finding of insider trading

The reproducible run selected 12 markets and screened **64,784 taker fills
across 11 complete tapes**. One selected market exceeded the trade endpoint's
per-window pagination cap and was explicitly marked `incomplete_excluded`, not
scored. The complete subset produced **10 flagged fills**, representing about **$7.2k** of
notional, across **8 wallets** and one market-level cluster: `Will the
government shutdown last 3 days or more?` The ten fills came from eight distinct
wallets, which is evidence of a market event worth contextualising, not evidence
that those wallets are controlled by one person.

Most importantly, none of the eight leads repeats across two flagged markets in
this scoped screen. The top wallet score is 42.5/100 and has only one flagged
market. That fails the report's own repeatability test, so this investigation
does **not** identify a wallet that should be described as likely insider
trading. It identifies a finite, transaction-linked review queue instead. This
negative result is intentional: a single correct, sizeable trade is compatible
with luck, public research, or an ordinary market thesis.

The highest-scoring fill bought Yes for $495.80 at 25.9¢, 79.0 hours before the
government-shutdown market closed; its transaction is recorded in
`candidate_trades.csv`. A reviewer should first reconstruct the wallet's full
net position and inspect public reporting between the fill and the resolution;
without corroboration, the appropriate conclusion remains “lead for review,”
not “insider.”

## Scoring model

The candidate score is a **priority score**, not a probability that someone is
an insider. A buyer of the ultimately winning outcome earns a trade-level score
from: an eventual winner bought below 50¢ (40%), entry within seven days of
resolution (25%), log-scaled notional (20%), and the difference from the median
of the preceding 20 fills on
the same outcome (15%). The latter is a one-sided, contemporaneous comparison:
the calculation never uses later prices to score an earlier trade. Before an
outcome has 20 preceding fills, its dislocation component is zero rather than
being estimated from the fill currently being scored.

Wallet priority combines its five strongest flagged trades (65%), repetition on
multiple markets (20%), and the share of its scoped buy notional placed on
eventual winners (15%). This design downweights a single fortunate bet and
favours a repeatable pattern.

The ranking now exposes an explicit corroboration gate: only a wallet with
flags on two or more distinct markets is labelled a `cross-market pattern`.
Every other row is a `single-market lead`. This is the key distinction from a
wallet leaderboard: it makes the absence of repeated evidence visible rather
than allowing a single profitable fill to imply wrongdoing.

## Limits and responsible use

The Data API exposes taker-side fills, not a wallet's complete economic history.
Accordingly this work does not calculate realised P&L, identify a wallet owner,
or allege misconduct. Before any finding, investigate the transaction and full
wallet history, reconstruct net position, compare the trade with a timestamped
public-news record, and look for on-chain funding or coordination links. Absence
of those corroborating facts should end the inquiry.

The committed CSV deliberately omits profile names, biographies and images as
they are not needed for scoring. It prefixes formula-leading text values with an
apostrophe before CSV export, preventing formula execution when an artifact is
opened in spreadsheet software.

Polymarket's public API documentation:
[market data](https://docs.polymarket.com/market-data/overview) and
[trade endpoint](https://docs.polymarket.com/api-reference/core/get-trades-for-a-user-or-markets).
