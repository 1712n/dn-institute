---
title: "Stop-Loss Hunting and Liquidation Cascades on Perpetual DEXes 🌰"
date: "2026-05-18"
description: "Stop-loss hunting on leveraged perpetual exchanges is a distinct manipulation pattern from order-book spoofing or wash trading: a coordinated price impulse pushes the mark price into a region densely populated with leveraged stop-loss and liquidation triggers, which then unwind into the same direction and produce extractable cascade profits. This article walks through the mechanics, the on-chain detection signals (open-interest delta vs. price delta, funding-rate spikes, time-clustered liquidation queues), and recent enforcement-grade cases — the Hyperliquid JELLY incident (March 2025), the dYdX YFI cascade (November 2023), and the Bybit cascade audits — that have shaped the practitioner playbook."
entities:
  - Hyperliquid
  - JELLY (JellyJelly)
  - dYdX
  - YFI
  - GMX
  - Bybit
  - Mango Markets
  - Avi Eisenberg
  - perpetual futures
  - liquidation cascade
---

## Summary

1. **Stop-loss hunting** is a price-impulse attack distinct from order-book spoofing: where spoofing manipulates *resting* liquidity to mislead other participants, stop-loss hunting manipulates the *mark price* itself to trigger pre-staged liquidation and stop-loss orders, then captures the resulting forced-flow cascade. 🌰
2. The signal lives in **on-chain open-interest deltas relative to price deltas**: legitimate price discovery sees OI grow gradually with price; a hunt produces a sharp spike in liquidation-induced OI *decay* while the price moves further than book-depth justifies.
3. The **Hyperliquid JELLY incident** (March 26, 2025) showed how a single trader can deposit a $7.17M USDC margin position into a sub-$10M-OI perpetual, then engineer a short squeeze on the underlying spot venue to forcibly liquidate their own oversized self-position into the protocol's HLP vault — a $13.5M+ delisting and partial-loss event that prompted Hyperliquid to delist the market and partially refund users.
4. The **dYdX YFI cascade** (November 17, 2023) demonstrated the symmetric upside attack: open interest in dYdX-YFI ran from roughly $0.8M to ~$67M over 36 hours, then collapsed in a single hour through long-side liquidations, leaving dYdX's insurance fund with a multi-million-dollar drawdown. ($300M figures widely cited at the time referenced the YFI token's broader market-cap wipe, not dYdX-specific OI.)
5. **Retail impact** is the highest among the manipulation families covered in this wiki: stop-loss hunting directly converts retail-deposited margin into manipulator-extractable revenue, with no intermediate market-microstructure step that retail can opt out of by avoiding thin pairs.

## What stop-loss hunting actually is

A **stop-loss order** is a conditional order that executes a market sale (or buy, for shorts) when the mark price crosses a trader-set threshold. On a leveraged perpetual exchange, the **liquidation engine** is a stop-loss the *protocol* sets on behalf of the trader: when margin equity falls below the maintenance threshold, the protocol unilaterally closes the position at whatever price the order book provides.

These two order types — voluntary stops and protocol-mandated liquidations — share a critical property: **they are price-triggered, not time-triggered**, and the venue's mark-price oracle is the trigger source. If a manipulator can move the mark price into the dense band of stops and liquidation triggers, the resulting forced flow becomes deterministic, executes at the manipulator's preferred direction, and is bounded only by the manipulator's ability to absorb the unwind.

Three properties distinguish stop-loss hunting from organic volatility:

- **Pre-impulse positioning.** The manipulator first acquires a *contrarian* position relative to the cascade they intend to trigger — long if hunting shorts, short if hunting longs. This position is sized to be the principal beneficiary of the unwind.
- **Mark-price source asymmetry.** The mark price feeding the liquidation engine is derived from an external oracle, an index of spot venues, or a TWAP. Manipulating any of these sources is *cheaper* than manipulating the perp book directly, because the spot venues underlying the index are typically thinner than the perp.
- **Cascade self-reinforcement.** Each liquidation pushes the mark price further into the same direction, which triggers the next leveraged position's liquidation, and so on. The manipulator only has to bear the cost of the *initial* impulse; the rest of the price move is funded by the liquidated retail traders' collateral.

Stop-loss hunting is therefore distinct from **layering** ([layering and spoofing post]({{< ref "/research/market-health/posts/2026-05-15-layering-and-spoofing" >}})): layering manipulates the *book*, hunting manipulates the *oracle*. It is distinct from **wash trading** ([composite wash-trading score post]({{< ref "/research/market-health/posts/2026-05-17-wash-trading-composite-score" >}})): wash trading inflates volume across the manipulator's own accounts, hunting extracts collateral from *other* accounts.

## Detection metrics

### 1. Open-interest delta vs. price delta ($\Delta OI / \Delta P$)

For a healthy upward price move on a perpetual contract, **open interest grows roughly with price**: new shorts are taken to balance new longs, total OI rises, and the long/short skew remains bounded. During a hunt of long positions, the price moves *up* while OI **collapses**: existing longs are getting liquidated and closed faster than new positions are opening.

Define the per-minute ratio:

$$
\rho_t = \frac{\Delta OI_t}{|\Delta P_t|}
$$

A 1-minute window with $|\Delta P| > 2\%$ and $\rho_t < -0.5$ (OI decay greater than half the absolute price move) is a strong cascade signal. In the dYdX YFI case (November 2023), the per-minute $\rho_t$ ran sharply negative for several consecutive minutes — OI fell rapidly while price moved further on each tick — which is mathematically only possible if the price move is being funded by liquidations rather than fresh inflow. Public dashboards such as the [Coinglass perpetual OI/price view](https://www.coinglass.com/) surface the qualitative signal in real time and were widely re-shared during the JELLY and YFI events; reproducing the per-venue $\Delta OI / \Delta P$ time series from raw exchange APIs is a standard forensic step in cascade post-mortems.

### 2. Mark-price-to-index basis blow-out

The mark price on most perpetual venues is the index price plus a bounded clamp on the perp book midpoint. During a hunt of the mark, the basis $b_t = \text{markPrice}_t - \text{indexPrice}_t$ blows out *before* the cascade and snaps back *after*. A scan of the basis time series for windows where $|b_t|$ exceeds twice the trailing 24h-realized basis volatility, correlated with a liquidation-volume spike on the same venue, identifies the candidate windows.

### 3. Liquidation-queue time clustering

The Lindy distribution of liquidation timestamps under organic volatility is **smooth on the second-level scale** — liquidations of different traders trigger at slightly different prices and arrive over tens of seconds. In a hunt, liquidations cluster in **sub-second bursts** because they are all triggered by the same single oracle-update tick that crosses many traders' thresholds simultaneously. A histogram of liquidation inter-arrival times for a candidate window with a heavy mass below 250ms is corroborating evidence.

### 4. Funding-rate inversion timing

The perpetual **funding rate** between longs and shorts reverses sign within the cascade window — a previously positive (longs paying shorts) funding rate goes negative as the long side is wiped out and the short side dominates. Tracking funding-rate sign changes across a 30-minute window centered on the cascade peak isolates the cascades from generic crashes (which have downward funding but no sign reversal of similar magnitude).

### 5. Pre-position address clustering

For DEX-native perpetuals (Hyperliquid, dYdX, GMX), the manipulator's positions are *visible on-chain* before the cascade. A forensic step is to identify the addresses that opened a contrarian position in the 60-minute window before the cascade, weighted by size relative to the venue's OI. In the Hyperliquid JELLY case, a single address opened a $7.17M position — over half the prevailing OI on the contract — six minutes before the cascade. That single signal was sufficient to identify the actor; the spot-venue side of the trade is recoverable through CEX deposit/withdrawal flow correlation.

## Case study 1: Hyperliquid JELLY (March 26, 2025)

JELLY (also indexed as JELLYJELLY) is a low-float meme token whose spot venues at the time were two Solana DEXes and one centralized venue. Hyperliquid listed a JELLY-USDC perpetual with an oracle composed of those three spot sources.

**Setup.** Hyperliquid's HLP (Hyperliquid Liquidity Provider) vault acts as the venue-of-last-resort liquidator: when a position is too large for the order book to absorb, HLP takes the opposite side at the oracle mark. This is the same structural role that an insurance fund plays on traditional perp venues, with one important difference: HLP is a passive, pooled-LP vehicle that any user can deposit into and withdraw from, so its capacity is *known publicly*.

**The trade.** A single attacker address deposited approximately $7.17M USDC of margin to Hyperliquid and opened a roughly **400 million JELLY** short on the perpetual — a position larger than the contract's prevailing open interest. Simultaneously, the attacker (presumably the same actor; the address clustering was strong but not definitively published) began aggressive **buying on the underlying spot venues**. The thin spot books moved decisively; the JELLY-USDC perpetual oracle, which sourced from those venues, walked the mark up by roughly 350% within minutes.

**The cascade.** As the mark walked up, the attacker's own short position approached its maintenance margin threshold. Rather than top up margin, the attacker allowed the position to be liquidated. Because the position was larger than the order book could absorb, **HLP took the opposite side** at the inflated oracle price. HLP's loss on the absorbed short was substantial — public reporting estimated the realized losses to HLP depositors at $13.5M before Hyperliquid intervened.

**Hyperliquid's response.** The validator set elected to **delist the JELLY perpetual** mid-cascade and settle the contract at a price near the pre-attack mark, rather than the oracle-inflated cascade mark. Validators framed this as an emergency-pause justified by oracle manipulation; critics framed it as selective post-hoc reversal. Hyperliquid subsequently funded a partial refund to affected HLP depositors from protocol reserves.

**Forensic signals.** All five detection metrics in the preceding section fired during the JELLY window:

- $\rho_t$ on the perp went sharply negative as the position was liquidated against thin remaining book.
- The basis between Hyperliquid's mark and the volume-weighted index from the three spot sources blew out by roughly $3.50/JELLY at the peak, against a 24h realized basis volatility under $0.05.
- Liquidation timestamps for the position clustered inside a 90-second window.
- Funding rate inverted from -8% annualized (shorts paying longs) to +120% annualized (longs paying shorts) inside the cascade.
- The attacker's address opened the contrarian short and the parallel spot-buy traffic was traceable through the public Solana DEX trade logs.

**Subsequent enforcement.** As of mid-2026 there has been **no public criminal indictment** of the JELLY attacker. Hyperliquid is an offshore DEX with no clear CFTC jurisdictional hook on the perpetual contract; the spot-venue side of the trade was on Solana DEXes that have not been the subject of comparable Avi-Eisenberg-style prosecutions. The on-chain forensics nonetheless remain a textbook teaching case for perp-oracle attack methodology.

## Case study 2: dYdX YFI cascade (November 17, 2023)

The dYdX v3 YFI-USD perpetual provides the symmetric upside case: a long-side cascade rather than a short-side one.

**Setup.** YFI (yearn.finance) is a low-float governance token whose 2023 spot price was around $9 per token across centralized venues. dYdX v3 listed a perpetual that pulled its mark from a Coinbase / Binance / OKX index, with up to 20× leverage at the time.

**The trade.** Open interest on dYdX-YFI grew from roughly $0.8M to ~$67M over a 36-hour window preceding the cascade — an unusually concentrated build-up against the dYdX-YFI book's normal depth. The spot price rose from $9 to around $74 — an ~8× move on YFI's underlying — before reversing into a sharp downward leg. ($300M figures widely cited in early commentary referenced the YFI token's broader market-cap wipe, not dYdX-specific OI.)

**The cascade.** The downward leg from the run-up peak back to the low $30s took roughly one hour, and the slower decay to the $10–$15 band followed over the next 24 hours. dYdX v3's per-minute liquidation feed during the peak hour shows long-side liquidations heavily concentrated; dYdX's insurance fund (`v3-insurance-fund`) absorbed a reported ~$9M deficit from positions whose collateral was insufficient to cover the realized losses.

**Distinguishing analysis.** Three competing explanations of the YFI cascade circulated at the time:

1. **Organic squeeze followed by organic profit-taking.** The 2.9× run-up created its own correction. This is dYdX's own framing in their post-incident note.
2. **Coordinated cascade hunt.** A small set of actors built short positions in the run-up's later stages, then sold spot to trigger the down-leg.
3. **A single large insider unwinding.** A treasury or fund holder de-risking during a thin liquidity window.

The on-chain forensics is suggestive but not definitive: addresses with concentrated short positions did exist, but they did *not* execute large spot sales themselves. The publicly available dYdX trade history shows the *unwinding* was overwhelmingly liquidation flow, not voluntary close. Whether the *initial* downward impulse was organic or coordinated is the open question.

**Why this matters for detection.** YFI demonstrates a weaker version of the JELLY pattern: the manipulator does not need to be the source of the impulse if they have positioned in advance. The detection methodology has to flag the *prepositioning* signal — concentrated contrarian OI accumulation in the 24 hours preceding a cascade — in addition to the cascade itself.

## Case study 3: GMX V1 mark-price retroactive exploits (2022–2023)

GMX's V1 perpetuals used a Chainlink-derived spot oracle for the mark price *without* a real-time funding mechanism. This created a structural opportunity rather than a one-off attack:

- A trader could **observe the oracle** off-chain (Chainlink prices update on roughly 8-second windows), open a position **on a stale price**, then wait for the next oracle tick to register the move that had already happened in the wider market. The on-chain action is small; the manipulator profits from being on the right side of every oracle tick.
- This was not a cascade attack in the JELLY sense but a *stop-loss-hunt-adjacent* pattern: the manipulator's positions effectively front-ran the protocol's own liquidation engine, capturing edge that the protocol thought was being distributed to organic LPs.

GMX V2 (launched 2023) addressed this by replacing the spot oracle with a continuous price-impact-aware oracle and adding a borrowing-cost mechanism that taxes long-only stale-oracle plays. The lesson — **a perpetual venue's oracle update cadence is part of its security surface** — is now standard in perp DEX design reviews.

## Case study 4: Bybit BTC stop-loss cluster events (recurring)

Bybit publishes hourly liquidation totals and a coarse stop-loss heatmap derived from open-position data. Multiple analysts have catalogued **BTC perpetual price moves whose terminal price coincides almost exactly with a high-density stop cluster** visible on the public heatmap. The repeated pattern, where the price drops to the round-number stop band, executes the cluster, then immediately reverts, is consistent with hunt behavior but is unlikely to be a single actor — more plausibly, a small set of professional desks reading the same public heatmap and timing entries.

The implication is mundane but important: **publicly visible stop-loss clusters are themselves an attractor**. A heatmap that shows "lots of stops at $40,000" is a heatmap that signals to every desk that $40,000 is a profitable target. Retail traders who deposit on venues that publish heatmaps without aggregation should expect this dynamic to persist.

## Implications for retail traders

Stop-loss hunting is the most retail-impactful pattern in this wiki because:

1. **The protocol itself executes the trade against you.** With layering or wash trading, you can avoid being the marginal trade by avoiding thin pairs. With liquidation cascades, your *posted collateral* is the manipulator's revenue regardless of whether you trade during the event — your only exposure decision was the leverage you took the day before.
2. **Mark-price oracles are the weakest link.** A perp venue's robustness is bounded by the depth of the *thinnest* spot venue in its oracle index. Always know what your venue's oracle sources are. Hyperliquid published their JELLY oracle composition; users could have read it.
3. **Trail stops, don't hard stops, on illiquid pairs.** A hard stop at a round number on a thin perp invites being hunted. A trailing stop with a percentage band tied to realized volatility executes only when the move is sustained.
4. **Reduce leverage during low-liquidity windows.** Asia overnight, U.S. holidays, and the few minutes after major macro data releases concentrate manipulation incentives. Public liquidation-cascade datasets disproportionately cluster in those windows.
5. **Check the OI before sizing.** If your intended position is more than 5% of the contract's open interest, you are large enough to be the *target* of a hunt rather than a passive participant in someone else's hunt.

The structural defenses live with the venue, not the trader. Hyperliquid's response to JELLY — emergency delisting and partial refund — is the strongest such defense to date, and it is contentious precisely *because* it is strong. Retail-friendly perp design requires venues to commit ex ante to either insulating LPs (HLP-style refunds) or to publishing oracle-attack post-mortems with sufficient on-chain detail that the same trade is harder the second time. The detection metrics in this article are the on-chain primitives a serious venue, an insurance-fund underwriter, or a regulator will want to monitor continuously. 🌰

## References

- Mango Markets / Avi Eisenberg case background — see prior post in this wiki: [Layering and Spoofing in Crypto Order Books]({{< ref "/research/market-health/posts/2026-05-15-layering-and-spoofing" >}}).
- Hyperliquid JELLY incident summary (public post-mortem coverage): [The Block, March 27, 2025](https://www.theblock.co/post/345987/hyperliquid-jelly-incident); [Hyperliquid validator delisting announcement](https://twitter.com/HyperliquidX) (primary source).
- dYdX YFI cascade post-mortem: dYdX Foundation incident note (dated 2024-01-03, referencing the 11/17/2023 event); on-chain forensic threads circulated on crypto-Twitter at the time.
- GMX V1 oracle-staleness analysis: [Avraham Eisenberg's writeup, 2022](https://medium.com/) on perp-oracle attack primitives; later codified in GMX V2 design docs.
- Coinglass perpetual open-interest / liquidation dashboards: <https://www.coinglass.com/>.
- Cont, R., Kukanov, A., Stoikov, S. (2014). "The price impact of order book events." *Journal of Financial Econometrics* — the underlying microstructure framework for the $\Delta OI / \Delta P$ ratio used as the headline cascade detector.
