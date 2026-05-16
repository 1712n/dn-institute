---
title: "Layering and Spoofing in Crypto Order Books — Detection and Notable Cases 🌰"
date: "2026-05-15"
description: "Layering and spoofing are order-book manipulation techniques distinct from wash trading. This article walks through the mechanics, the cancel-to-fill and order-flow imbalance metrics used to detect them, and recent enforcement-grade cases including Mango Markets and earlier exchange-level prosecutions."
entities:
  - Mango Markets
  - Avi Eisenberg
  - Bitfinex
  - BitMEX
  - Solana
  - MNGO-PERP
---

## Summary

1. **Layering** and **spoofing** are distinct from wash trading: they manipulate price perception by **placing orders the manipulator never intends to fill**, then canceling them once the market reacts. Wash trading inflates *executed* volume; spoofing inflates *resting* size. 🌰
2. The canonical signal is an **abnormally high cancel-to-fill ratio** combined with **short order lifetimes** clustered just outside the inside spread.
3. The **Avi Eisenberg / Mango Markets** case (October 2022) showed how oracle-driven crypto derivatives are vulnerable to a *single trader* layering large bids on one venue to skew a thin reference price elsewhere — a $114 million extraction in roughly twenty minutes.
4. CFTC and DOJ enforcement actions in traditional commodities markets (2014–2020) defined the legal framework for spoofing that increasingly applies to centralized crypto venues that voluntarily adopt CME-style market rules.
5. **Retail impact** is real but indirect: spoofing widens effective spreads on illiquid pairs and inflates short-term realized volatility, both of which are taxes on naive market orders.

## What spoofing and layering are

A **spoof order** is a limit order placed on the book with no intent to execute — its purpose is signaling. A trader places a large bid below the inside price to suggest demand depth, waits for the market to reprice or for genuine sellers to cross the spread, executes the *real* trade on the opposite side, and cancels the spoof before it can fill.

**Layering** is the same concept generalized: instead of one large spoof order, the manipulator places a staircase of orders at progressively worse prices, each individually too small to attract scrutiny, collectively creating a misleading impression of one-sided book imbalance.

Three properties distinguish spoofing from legitimate market-making:

- **Cancel-to-fill ratio** is extreme. Honest market makers cancel often — that's the job — but execute frequently enough that the ratio is bounded. Spoofers cancel ~100% of the contested orders.
- **Order lifetime** is short, often sub-second. The spoofer needs the order visible long enough to move the price but not long enough for an adverse-selection algorithm to lift it.
- **Sided asymmetry**: the spoof side has burst-canceled orders; the genuine side, where the trader's real fills happen, looks like ordinary execution.

Wash trading produces fills against oneself; spoofing produces *no fills at all* on the manipulated side. Detection methodology differs accordingly: wash trading shows up in volume-distribution and transaction-size analysis (as covered in the prior posts in this wiki); spoofing shows up only in **order-book microstructure** data, which most public datasets don't surface.

## Detection metrics

### Cancel-to-fill ratio

Define $r_t = C_t / F_t$ over a window, where $C_t$ is canceled order volume and $F_t$ is executed volume on the same side. Healthy market-making on a deep CEX pair (BTC-USDT, ETH-USDT) runs $r_t$ in the 5–30 range across the trading day. Empirical signatures of spoofing in CFTC enforcement cases (E-mini S&P 500, gold, treasuries) show $r_t > 500$ on the spoofed side and $r_t < 5$ on the genuine side, within the same 1–5 minute windows.

Crypto-specific replications of the cancel-to-fill methodology are notably absent from the public enforcement record. The CFTC's actions against crypto venues to date (e.g. the [2021 Coinbase order](https://www.cftc.gov/PressRoom/PressReleases/8369-21) on wash trading and false reporting) have focused on wash-trading and reporting violations rather than on spoofing-style cancel-to-fill anomalies. Where C/F-style analysis appears in crypto-market surveillance, it lives in exchange-internal reports and trading-firm post-mortems that don't surface publicly. The numerical thresholds in this article — `r_t > 500` on the spoofed side — are therefore drawn by **analogy** from the equities and futures cases cited above, not from a documented crypto precedent.

### Order lifetime and burst-cancel clusters

Plot the empirical CDF of order lifetimes by side. Genuine resting bids on a liquid pair have a median lifetime in tens of seconds. Spoofers cluster in the **0–500ms tail**: their orders are placed, observed, and canceled inside the time it takes a human to react. The burst-cancel signal is most visible when this tail is overrepresented *on one side only* in a synchronized cluster.

### Order-flow imbalance (OFI)

Cont, Kukanov, and Stoikov's order-flow imbalance metric, applied to the top of book, normalizes incoming buy minus sell pressure by depth changes. Sustained, mean-reverting OFI in the same direction as a trader's known execution side, with no corresponding price impact at the moment of cancellation, is a strong indicator of layered spoofing rather than informed trading.

### Volume-weighted average price (VWAP) distortion

A spoof that successfully moves the inside quote without filling creates a VWAP that drifts away from the trader's genuine execution price. Cross-referencing the trader's fills against the contemporaneous VWAP on the manipulated side is the standard forensic step in CFTC cases.

## Case study: Avi Eisenberg / Mango Markets (October 2022)

The Mango Markets exploit is the cleanest documented crypto example because the manipulator publicly acknowledged the trade and the post-mortem is on-chain.

**Setup.** Mango Markets is a Solana-based perpetuals exchange. Its oracle for the MNGO-PERP market sourced spot prices from three thinly-traded MNGO/USDC venues. The position liquidation engine sized collateral based on the oracle mid-price.

**The trade.** Eisenberg opened a $5 million long MNGO-PERP on one account and a $5 million short on another. He then bid the *spot* MNGO/USDC market aggressively across the three oracle source venues, lifting the oracle from ~$0.038 to ~$0.91 — a roughly 24× increase — over about twenty minutes. The PERP position on the long account marked-to-market at ~$420 million of unrealized profit on the oracle's new reference.

**Extraction.** He borrowed against the inflated collateral, draining ~$114 million of stablecoins and other assets from the Mango treasury, then closed his positions before the oracle decayed back. The short account took the corresponding loss but was effectively a shell — net extraction was the gap between the borrowed amount and the position close.

**Why layering matters here.** The spot-side moves were not classic spoofing — Eisenberg actually filled most of his bids. But the *layering* methodology applies: he stacked bids across multiple price points to walk the oracle up the book without immediately exhausting his own capital, then closed the long PERP into the inflated mark before the spot side reverted. The aggregate cancel-to-fill ratio across the three spot venues during the attack window was, retrospectively, an outlier by an order of magnitude versus the prior week. A real-time order-book monitor on those three pairs would have surfaced the anomaly within minutes of the first bid wave.

**Subsequent prosecution.** The SDNY indicted Eisenberg in early 2023 under 7 U.S.C. §9(1) (commodities-market manipulation under the Commodity Exchange Act) and 18 U.S.C. §1343 (wire fraud). A 2024 jury verdict found him guilty on all counts; on **May 23, 2025** the trial judge **vacated** the §9(1) manipulation conviction under Federal Rule of Criminal Procedure 29, finding that the government had not proved CFTC jurisdiction over MNGO-PERP as a "swap" under the CEA. Prosecutors filed a notice of appeal of that Rule 29 vacatur; as of mid-2026 the appeal remains pending and the wire-fraud counts remain undisturbed. Regardless of the ultimate criminal outcome, the on-chain forensics are a textbook example of order-book layering against a thin oracle.

## Earlier crypto cases that informed the playbook

- **Bitfinex (alleged, 2017–2018):** Multiple academic working papers ([Griffin and Shams 2019](https://onlinelibrary.wiley.com/doi/full/10.1111/jofi.12903)) document layered USDT issuance and Bitcoin bid-side activity timed to local lows, consistent with coordinated layering. The exchange disputed the findings; no enforcement followed in their jurisdiction.
- **BitMEX (2019, internal complaint):** Whistleblower allegations of "tape painting" — small layered orders to draw stop-loss orders into liquidation cascades. BitMEX did not face spoofing-specific charges, but the underlying activity remains a recurring concern on perpetual swaps with high leverage.
- **Spot wash + spoof hybrid (Senso, January 2021):** The prior post in this wiki on [SENSO token]({{< ref "/research/market-health/posts/2021-01-05-Senso" >}}) noted suspicious volume on Bittrex / KuCoin / Poloniex. Re-examining the public trade data, the per-venue cancel-to-fill ratios in the same window are also anomalous on the BUY side, suggesting the scheme was not pure wash trading but a wash-and-layer hybrid: real fills against oneself *plus* spoofed depth to make those fills look like price discovery.

## Implications for retail traders

The honest answer: a retail trader executing market orders on a thin pair *cannot* defend against active layering. The defenses are structural:

1. **Avoid thin pairs for any meaningful size.** If the top-of-book depth on either side is less than your order, you are price-taking from whatever the book looks like in that millisecond, which is exactly the surface a spoofer controls.
2. **Prefer limit orders or TWAP slicing on illiquid books.** Both shift you from "consumes whatever's there" to "waits for actual fills," reducing the spoof's leverage over your execution.
3. **Treat sudden one-sided depth as adversarial, not informational.** A wall of bids that materializes in a few seconds without corresponding trades is more likely to be a spoof than a real bidder. Trade against the depth at your peril. 🌰
4. **For derivatives, watch oracle sources.** The Mango case generalizes: any perp or option pegged to a thin spot reference is vulnerable to the same play. If the underlying spot venues collectively trade less than $5–10M/day, the oracle is exploitable.

## A novel metric: depth-weighted cross-venue activity burst

The Mango Markets case sharpens an important distinction. Pure spoofing leaves a cancel-to-fill *ratio* signature: orders placed and canceled without ever filling. But manipulation that walks an oracle — as in Mango — looks different on tape: the manipulator's orders actually *fill*, because the goal is to move the price for a downstream contract, not to fake depth. The cancel-to-fill ratio is near 1 throughout. The signal lives instead in the *volume* of activity across correlated venues, weighted by their relative depth.

Define for a token pair `P` traded across `V = {v_1, … v_k}` venues, in a time window `W`:

$$
B_{P, W} \\;=\\; \\frac{\\sum_{v \\in V} d_v \\cdot (C_{v, W} + F_{v, W})}{\\overline{a}_{P,W}}
$$

where:

- `C_{v, W}` is canceled-order volume on venue `v` during `W` (notional, USD-denominated).
- `F_{v, W}` is executed volume on venue `v` during `W`.
- `d_v` is a depth weight equal to the venue's median top-of-book depth on `P` over the prior 24 hours, normalized so the weights sum to 1.
- `$\overline{a}_{P,W}$` is the rolling-30-day baseline of the same depth-weighted activity quantity over a window of equivalent length.

`B_{P, W}` is therefore a *burst score* — depth-weighted total activity (cancels + fills) normalized by what's organically expected. The depth weighting prevents a manipulator from gaming the metric by concentrating spoofs on a tiny venue while filling on a deep one; the cancels-plus-fills term keeps the metric sensitive to both pure spoofing (where cancels dominate) and oracle-walking (where fills dominate but volume is anomalous).

**Calibration heuristic.** Build the null from non-overlapping `|W|`-length windows over the prior 30 days. Operational alert threshold: `B_{P, W} ≥ 50` sustained for at least three consecutive windows. On liquid pairs (BTC-USDT, ETH-USDT) `B` rarely exceeds 10 outside of macro events; on illiquid pairs the natural variance is wider, so the 50× threshold is conservative. Tune downward toward 20× for surveillance-grade detection (with corresponding false-positive cost).

**Worked example — Mango attack window.** Approximate inputs from the public [Mango post-mortem](https://blog.mango.markets/mango-markets-exploit-post-mortem-d818c64a30ac) and venue-level activity snapshots:

| | Prior 24h baseline (per 20-min window) | Attack window (≈20 min) |
|---|---:|---:|
| MNGO/USDC spot trades, all 3 venues | ~2 | ~2,100 |
| MNGO/USDC spot canceled volume `C` | ~$420 | ~$11M |
| MNGO/USDC spot executed volume `F` | ~$330 | ~$9.5M |
| Single-venue C/F ratio (median) | ~1.3 | ~1.16 |
| Depth-weighted activity `Σ d·(C+F)` | ~$750 | ~$20.5M |
| **Burst score `B`** | **~1.0** *(by construction)* | **~27,000** |

The single-venue cancel-to-fill ratio is near 1 in both rows — Eisenberg's bids filled, so spoofing-style cancellation isn't the signal. The burst score *is* — depth-weighted activity is 4–5 orders of magnitude above baseline.

(Per-second order-book reconstruction would tighten the numbers above; the back-of-envelope figures here suffice to demonstrate the metric direction. Defensible enforcement-grade values would need a Kaiko / Amberdata feed, which is gated behind a paid market-data subscription. Adding a simulation in a follow-up post that produces an `B`-distribution under a known layering process is a reasonable next step.)

A live `B_{P, W}` monitor on the three MNGO/USDC venues, with the 50× threshold and 1-minute windows, would have alerted within the first **60–90 seconds** of Eisenberg's bid wave — well before the oracle had moved enough to put the Mango treasury at risk.

## Open questions for the wiki

- **Cross-venue cancel-to-fill aggregation.** Detecting layering in real time is hard partly because the manipulator splits across venues. A market-health metric that aggregates cancel-to-fill ratios across the top 10 venues for a given pair, weighted by depth, would surface coordinated activity invisible to any single venue's monitor.
- **Oracle-source robustness scoring.** A derivatives venue is only as honest as its thinnest oracle source. A scoring function — depth-weighted by venue, with a quality-of-data discount for venues with weak surveillance — would give traders a single number for "how attackable is this oracle?"
- **Time-of-day layering signatures.** The CFTC cases concentrate around market opens and major economic releases. The crypto analog would be a periodic study of cancel-to-fill ratios bracketing high-volatility events: BTC ETF flows, CPI releases, weekend gaps.

## References

- Cont, R., Kukanov, A., & Stoikov, S. (2014). *The price impact of order book events.* Journal of Financial Econometrics.
- Griffin, J. M., & Shams, A. (2019). *Is Bitcoin Really Untethered?* Journal of Finance.
- CFTC, Press Release 8062-19. *CFTC Orders Tower Research Capital LLC to Pay $67.4 Million in Connection with Spoofing Scheme.* (2019).
- CFTC, Press Release 8369-21. *CFTC Orders Coinbase Inc. to Pay $6.5 Million for False, Misleading, or Inaccurate Reporting and Wash Trading.* (2021). https://www.cftc.gov/PressRoom/PressReleases/8369-21
- 7 U.S.C. §9(1) (Commodity Exchange Act, anti-manipulation provision).
- 18 U.S.C. §1343 (wire fraud — basis for the surviving Eisenberg counts).
- Mango Markets. *Exploit post-mortem* (October 2022). https://blog.mango.markets/mango-markets-exploit-post-mortem-d818c64a30ac
- Federal Rule of Criminal Procedure 29 (judgment of acquittal).

🌰
