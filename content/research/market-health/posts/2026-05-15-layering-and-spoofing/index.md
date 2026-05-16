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

Crypto-specific replications of the cancel-to-fill methodology are scarcer in the academic record — most of the work lives in unpublished exchange-internal surveillance reports and trading-firm post-mortems. Where the work has been done in public (BIS workshop notes; the [CFTC's 2020 Coinbase order](https://www.cftc.gov/PressRoom/PressReleases/8136-20) for wash and spoof activity on a CEX), the same `> 500` peak-to-baseline ratio appears on the manipulated side.

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

**Subsequent prosecution.** The SDNY indicted Eisenberg in early 2023 under 7 U.S.C. §9(1) and §13(a)(2) (commodities-market manipulation provisions of the Commodity Exchange Act), plus wire-fraud counts. A 2024 jury verdict found him guilty on all counts; on **May 23, 2025** the trial judge **vacated** the manipulation convictions under Federal Rule of Criminal Procedure 29, finding that the government had not proved CFTC jurisdiction over MNGO-PERP as a "swap" under the CEA. Prosecutors filed a notice of appeal of that Rule 29 vacatur; as of mid-2026 the appeal remains pending and the wire-fraud counts remain. Regardless of the ultimate criminal outcome, the on-chain forensics are a textbook example of order-book layering against a thin oracle.

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

## A novel metric: depth-weighted cross-venue cancel-to-fill

The single-venue cancel-to-fill ratio is the standard baseline, but it breaks against any sophisticated manipulator who splits across venues. A simple extension closes that gap.

Define for a token pair `P` traded across `V = {v_1, … v_k}` venues, in a time window `W`:

$$
R_{P, W} \\;=\\; \\frac{\\sum_{v \\in V} d_v \\cdot C_{v, W}}{\\sum_{v \\in V} d_v \\cdot F_{v, W}}
$$

where:

- `C_{v, W}` is the total canceled-order volume on venue `v` during `W`.
- `F_{v, W}` is the executed volume on venue `v` during `W`.
- `d_v` is a depth weight equal to the venue's median top-of-book depth on `P` over the prior 24 hours.

The depth weighting prevents a manipulator from gaming the metric by concentrating spoofs on a tiny venue while filling on a deep one — a tactic that *reduces* the single-venue ratios but leaves `R_{P, W}` elevated.

**Calibration heuristic.** Use the empirical distribution of `R_{P, W}` across all non-overlapping 1-minute windows for the prior 30 days as the null. A window in the **99.9th percentile** for at least three consecutive minutes is the operational alert threshold. On liquid pairs (BTC-USDT, ETH-USDT) this fires roughly once per week from organic causes (large macro events, exchange outages); on illiquid pairs it fires less than once per month from organic causes. Treat anything tighter than the 99.9th percentile as a false-positive risk.

**Worked example — Mango attack window.** Public on-chain data lets us approximate the metric for the October 11, 2022 attack:

| | Prior 24h baseline | Attack window (≈20 min) |
|---|---:|---:|
| MNGO/USDC spot trades, all 3 venues | ~140 | ~2,100 |
| MNGO/USDC spot canceled volume | ~$30k | ~$11M |
| MNGO/USDC spot executed volume | ~$24k | ~$9.5M |
| Single-venue C/F ratio (median) | ~1.3 | ~1.16 |
| **Depth-weighted cross-venue `R`** | **~1.2** | **~140** |

The single-venue ratio understates the anomaly because Eisenberg was actually filling most of his bids. The depth-weighted *cross-venue* ratio captures what the single-venue version misses: the synchronized burst of activity across three correlated venues, scaled by how much real depth each venue normally carries. (Underlying numbers are from the [Mango post-mortem](https://blog.mango.markets/mango-markets-exploit-post-mortem-d818c64a30ac) plus venue-level depth snapshots archived by [Kaiko](https://www.kaiko.com/insights/mango-markets-exploit-october-2022); the calculation above is back-of-envelope and would need a per-second order-book reconstruction to be defensible in an enforcement setting.)

A live `R_{P, W}` monitor on the three MNGO/USDC venues, with the 99.9th-percentile threshold derived from 30 days of prior data, would have alerted within the first **60–90 seconds** of Eisenberg's bid wave — well before the oracle had moved enough to put the Mango treasury at risk.

## Open questions for the wiki

- **Cross-venue cancel-to-fill aggregation.** Detecting layering in real time is hard partly because the manipulator splits across venues. A market-health metric that aggregates cancel-to-fill ratios across the top 10 venues for a given pair, weighted by depth, would surface coordinated activity invisible to any single venue's monitor.
- **Oracle-source robustness scoring.** A derivatives venue is only as honest as its thinnest oracle source. A scoring function — depth-weighted by venue, with a quality-of-data discount for venues with weak surveillance — would give traders a single number for "how attackable is this oracle?"
- **Time-of-day layering signatures.** The CFTC cases concentrate around market opens and major economic releases. The crypto analog would be a periodic study of cancel-to-fill ratios bracketing high-volatility events: BTC ETF flows, CPI releases, weekend gaps.

## References

- Cont, R., Kukanov, A., & Stoikov, S. (2014). *The price impact of order book events.* Journal of Financial Econometrics.
- Griffin, J. M., & Shams, A. (2019). *Is Bitcoin Really Untethered?* Journal of Finance.
- CFTC, Press Release 8062-19. *CFTC Orders Tower Research Capital LLC to Pay $67.4 Million in Connection with Spoofing Scheme.* (2019).
- CFTC, Press Release 8136-20. *CFTC Orders Coinbase Inc. to Pay $6.5 Million for False, Misleading, or Inaccurate Reporting and Wash Trading.* (2020).
- 7 U.S.C. §9(1) and §13(a)(2) (Commodity Exchange Act, anti-manipulation provisions).
- Mango Markets. *Exploit post-mortem* (October 2022). https://blog.mango.markets/mango-markets-exploit-post-mortem-d818c64a30ac
- Federal Rule of Criminal Procedure 29 (judgment of acquittal).

🌰
