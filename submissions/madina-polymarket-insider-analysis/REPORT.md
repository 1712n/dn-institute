# Pre-operation trading in the January 2026 Maduro removal market

Retrospective investigation for [DNI challenge #1222](https://github.com/1712n/dn-institute/issues/1222). Snapshot collected October 7, 2026. **These are research leads, not allegations or probabilities of insider trading.**

## Findings

I reconciled 198,521 trade-side records across seven markets, representing 23,293 distinct wallet addresses. The primary market, **“Maduro out by January 31, 2026?”**, contains 26,404 records and 3,948 wallets. A conservative 24-hour screen ending January 3 at 05:00 UTC selected eight wallets; four scored above 70/100. The strongest three combined substantial YES purchases, low entry prices, and positive directional share flows before the selected cutoff.

The strongest signal is wallet `0x31a56e9e690c621ed21de08cb559e9524cdb8ed9`: approximately 26,215 USDC of YES purchases in the window at a volume-weighted price of 0.07523, versus 6,323 USDC over the preceding seven days. Its score is 94.96. **94.96 is an uncalibrated review-priority score, not a 94.96% chance of insider trading.**

The event-window maximum exceeds all seven earlier daily-window maxima. However, earlier windows also contain high-scoring accounts, including a maximum of 84.64 one day earlier. The screen therefore captures behavior that can arise without established access to private information. This is a useful shortlist for further investigation, not a classifier validated against ground truth.

## Scope and evidence

All scored trades are within the challenge interval. The collector interprets the end date as inclusive of the full May 1 UTC day; no primary result depends on that boundary because this market stopped trading in January. The six removal-deadline markets were downloaded in full from the API, then locally filtered to November 1, 2025 through May 1, 2026. A seventh custody market is retained as contextual data. The January deadline is the primary market because it existed before the operation and has a direct, near-term outcome. Other deadlines concern the same underlying event and **are not independent predictive successes**.

The first pilot, “Maduro in U.S. custody by January 31?”, was created on January 3 at 07:47 UTC. Its first observed trade is 07:58 UTC. It cannot supply pre-operation evidence and is excluded from the ranking. This correction prevents post-event market selection from masquerading as pre-event foresight.

The data came from public Gamma metadata and Data API v2, with both maker and taker rows requested. For every market, the cursor chain reaches its terminal page. Every raw-response SHA-256 matches its collection manifest, and the CSV multiset exactly matches the in-window raw rows. Counts refer to **trade-side records**, not independent trades or unique notional volume. Exhausting an API does not prove completeness against the blockchain.

The primary market has 420 excess records with identical wallet/condition/token/side/size/price/time/transaction signatures. Without event log indices, these may be distinct fills. The base analysis preserves them. Collapsing these signatures leaves the eight candidates, their order and scores unchanged. Raw page/row references allow record-level review.

## Timeline and leakage control

I separated three different timestamps. Reuters witnesses placed visible disturbances at approximately 06:00 UTC. A [contemporary Reuters dispatch](https://www.reuters.com/world/americas/trump-administration-aware-reported-explosions-venezuelan-capital-cbs-reporter-2026-01-03/) is currently displayed as published at 07:30 UTC and refers to already-circulating reports. [Reuters' later reconstruction](https://www.reuters.com/business/aerospace-defense/mock-house-cia-source-special-forces-us-operation-capture-maduro-2026-01-03/) places arrival at the compound around 06:00 UTC and the presidential announcement at 09:21 UTC. Physical events, a wire publication and an official announcement are different boundaries.

I retained **05:00 UTC** as a conservative analytical cutoff, one hour before the reported visible disturbances. The 07:30 publication is evidence that information was public by that time, not proof that it first became public then. Neither source establishes the earliest social-media post or private information available to a trader. I therefore also reran the screen at 00:00, 03:00 and 04:00 UTC rather than treating the official announcement as a clean cutoff. Current page timestamps can reflect editorial updates; I did not obtain a versioned wire archive. The source audit is in `results/event_timeline.csv`.
Main window: `[2026-01-02 05:00, 2026-01-03 05:00)` UTC. Baseline: the preceding seven full days. All score inputs precede the cutoff; future prices, resolution outcomes, later wallet activity and contemporary legal allegations do not enter the score. The event itself was selected retrospectively, so selection bias remains. This is not a prospective or preregistered study.

## Explainable heuristics and scoring

For each primary-market wallet, let:

- `B` = observed gross BUY YES notional during the main window, in USDC.
- `Q` = observed BUY YES shares during that window; `VWAP = B/Q`.
- `B7` = BUY YES notional in the preceding seven-day baseline.
- `U` = BUY YES shares plus SELL NO shares in the main window.
- `V` = SELL YES shares plus BUY NO shares in the main window.

Eligibility requires `B >= 500`, `U-V > 0`, and positive net YES share flow (`BUY YES minus SELL YES`). This intentionally targets recent YES accumulation; it can miss informed traders expressing their views only through NO sales or earlier positions.

Components:

| Signal | Formula | Rationale and limitation |
| --- | --- | --- |
| Size factor `S` | `min(1, ln(1+B)/ln(10001))` | Reduces the priority of tiny bets; saturates at 10,000 USDC. Wealth alone is not evidence. |
| Low entry price `L` | `1 - VWAP` | Emphasizes conviction when the purchased outcome was priced low; expertise and long-shot betting are alternatives. |
| Burst `A` | `B / (B + B7/7 + 1000)` | Compares recent buying with the wallet’s observable market baseline; the 1,000 USDC floor limits inflation from a zero baseline. |
| Directionality `D` | `max(0, (U-V)/(U+V))` | Discounts offsetting flows in this market; it cannot detect external hedges or transfers. |

**Score = `100 × S × (0.4 L + 0.3 A + 0.3 D)`**, for eligible wallets. All components are between 0 and 1. The 500/1,000/10,000 USDC thresholds and weights are transparent modeling choices, not statistically estimated parameters. Scores above 70 are used only for descriptive counts, not a proven decision boundary.

All 3,948 observed primary-market wallets appear in `wallet_ranking.csv`. Ineligible wallets have a blank rank, zero score and an explicit reason. A zero means **not selected by this screen**, not innocent or low-risk with a known probability. Tied scores share a rank; address sorting merely makes presentation deterministic.

Wallet creation age, whole-account concentration, coordinated ownership, realized profits and repeated independent-event success are **not scored** because the required evidence is unavailable. A zero in the observed seven-day baseline is not a new-wallet claim. These exclusions are preferable to treating missing information as evidence.

## Ranked investigation leads

USDC amounts below are purchases, not profits. Prices are paid per YES share.

| Rank | Public wallet | Score | Window YES purchases | YES VWAP | Prior 7-day YES purchases |
| --- | --- | ---: | ---: | ---: | ---: |
| 1 | `0x31a56e9e690c621ed21de08cb559e9524cdb8ed9` | 94.96 | 26,215.00 | 0.07523 | 6,323.34 |
| 2 | `0x6baf05d193692bb208d616709e27442c910a94c5` | 92.75 | 10,000.00 | 0.11308 | 0.00 |
| 3 | `0xa72db1749e9ac2379d49a3c12708325ed17febd4` | 87.20 | 5,782.66 | 0.07160 | 0.00 |
| 4 | `0x858d551d073e9c647c17079ad9021de830201047` | 78.35 | 3,117.01 | 0.07538 | 0.00 |
| 5 | `0x9ed9fb24166d7aae9ec0f8eef267c46cb34ef365` | 65.50 | 1,499.19 | 0.10870 | 1,199.34 |
| 6 | `0x8204c2803f9b69e6a623ac70c92a049699ed56ea` | 60.43 | 899.99 | 0.06000 | 0.00 |
| 7 | `0x2577c59314e3efd45f9dd31067ea329d5a4ea5ec` | 58.10 | 779.68 | 0.07000 | 0.00 |
| 8 | `0xa1ffbb2952fcd18b3b4759ccddeb7fdf90f655bd` | 37.14 | 932.73 | 0.10938 | 1,050.00 |

The second wallet’s first observed primary-market trade is January 3 at 03:42:01 UTC. It also bought about 15,089.94 USDC of February-deadline YES shares before the cutoff. This broadens the documented exposure to the same event; it does not establish a second independent prediction.

Counter-evidence matters. Wallet four previously bought about 1,636.79 USDC of YES in the unsuccessful 2025-deadline market. This does not prove a realized loss because sales and hedges have not been reconstructed, but it contradicts a simple “only correctly timed predictions” narrative. Wallet six also has substantial earlier YES buying in unsuccessful 2025 deadlines. Wallet eight has heavily offsetting flows: its directionality is only 0.0319, materially reducing its score.

## Robustness and false-positive checks

| Check | Eligible wallets | Maximum score | Interpretation |
| --- | ---: | ---: | --- |
| Cutoff 04:00 UTC | 7 | 94.96 | Seven base candidates remain. |
| Main cutoff 05:00 UTC | 8 | 94.96 | Four scores exceed 70; three exceed 80. |
| Approximate strike boundary 06:00 UTC | 9 | 94.96 | Seven of the base eight remain. |
| Announcement 09:21 UTC | 90 | 94.96 | Includes reactions to an unfolding public operation; invalid as a clean pre-operation window. |
| Equal component weights | 8 | 95.24 | Same candidate set. |
| More weight on burst | 8 | 95.11 | Same candidate set. |
| Minimum purchase 100 USDC | 13 | 94.96 | Threshold-sensitive tail. |
| Minimum purchase 1,000 USDC | 5 | 94.96 | Retains larger buyers only. |

Seven daily placebo cutoffs from December 27 through January 2 produce maximum scores from 59.98 to 84.64. Four of these seven windows have at least one score above 70. The event-day maximum of 94.96 and three scores above 80 are comparatively unusual in this small sample, but the controls are few, related and subject to changing market conditions. No calibrated false-positive rate, p-value or causal inference is claimed.

## Earlier cutoffs and window lengths

The added checks in `results/news_boundary_sensitivity.csv` expose what changes when the uncertain information boundary moves:

| Cutoff / purchase window | Eligible wallets | Original top-three wallets still in top three |
| --- | ---: | ---: |
| 00:00 UTC / 24 hours | 8 | 2 |
| 03:00 UTC / 24 hours | 5 | 2 |
| 04:00 UTC / 24 hours | 7 | 3 |
| Main 05:00 UTC / 24 hours | 8 | 3 |
| 05:30 UTC / 24 hours | 9 | 3 |
| 06:00 UTC / 24 hours | 9 | 2 |
| 07:30 UTC / 24 hours | 52 | 2 |
| 05:00 UTC / 12 hours | 8 | 3 |
| 05:00 UTC / 48 hours | 18 | 3 |

The original three remain the leading group with 12-hour and 48-hour windows. They do not all remain when the cutoff is moved much earlier: wallet `0x6baf05...a94c5` bought at 03:42, so a 03:00 cutoff excludes that purchase. This is a real timing dependency, not a failed test to discard. The rise to 52 eligible wallets at 07:30 shows why a publicly unfolding operation should not be included in the main screen. Later cutoffs are comparison scenarios, not clean pre-news evidence. For each alternative window length, the seven-day baseline ends where that purchase window starts; it never overlaps the scored purchases.

## Relationship to the other Maduro submission

I compared the published report in [PR #1224](https://github.com/1712n/dn-institute/pull/1224), as available on October 7, 2026. It identifies the same three leading addresses, in a different order. This study does not claim to discover previously unreported wallets. Both analyses examine the same event, so agreement is not independent validation of insider activity.

The additional work here concerns interpretation: maker and taker trade-side coverage, signed YES/NO flows that discount offsetting activity, earlier-cutoff comparisons, and evidence of earlier YES buying on unsuccessful deadlines. The other submission adds wider wallet histories that this dataset does not contain. Those histories are a useful next step; I have not copied them into my results or inferred whole-wallet concentration from market-only history.

## Limits and next investigative steps

This is one event family, selected retrospectively. It cannot establish population-wide insider prevalence, repeatable trading skill or causation. Account linkage, transfers, full wallet histories, outside positions, fees and redemptions were not collected. Net directional *trade flow* is not inventory; purchases are not realized P&L. Market makers, hedgers, public-information specialists and lucky traders can trigger these heuristics.

The strongest next step is to reconstruct full histories and on-chain flows for the leading candidates, verify the earliest accessible public reports and compare additional independently selected events. Until then, the defensible conclusion is that **several wallets warrant closer examination for unusually timed directional exposure; this dataset alone does not establish insider trading**.

## Reproduction and provenance

Run `python3 -m unittest -v` and `python3 analyze.py`; see [README.md](README.md). Fourteen tests cover pagination, date boundaries, wrong-market data, future-data exclusion, offsetting flows, trade splitting, baseline effects and eligibility. The analysis executes hash/cursor/CSV reconciliation on real inputs. Synthetic test records never enter results.

API contract: [Polymarket Data API v2 trades](https://docs.polymarket.com/api-reference/feeds/list-trades). Market metadata: archived Gamma responses under `data/*/raw/event_000.json`. All record-level findings above are computed from the supplied snapshot, with candidate transactions in `results/top_wallet_window_trades.csv`. 
