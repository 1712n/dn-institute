---
title: "Movement MOVE market-maker sell pressure after token launch"
date: "2025-03-25"
description: "A case study of one-sided market-making activity around MOVE after its token launch, the resulting 38 million USDT recovery plan, and market-health signals that can detect similar launch-liquidity failures."
entities:
  - Movement Network Foundation
  - Movement Labs
  - MOVE
  - Binance
  - Web3Port
---

## Summary

In March 2025, Binance alerted Movement Network Foundation and Movement Labs that a market maker connected to the MOVE token had been under investigation for irregular activity. Movement's own statement says the market maker sold a substantial amount of MOVE shortly after the December 2024 token generation event without completing meaningful buy orders, breaching an agreement that required liquidity on both sides of the MOVE/USDT pair.

Public reporting attributed the affected flow to roughly 66 million MOVE sold after listing and a 38 million USDT profit before Binance offboarded the market maker on March 18, 2025. Movement Network Foundation responded by cutting ties with the market maker, informing other exchanges, and committing recovered cash proceeds to a 38 million USDT buyback program on Binance over three months.

The case is useful for market-health monitoring because the alleged misconduct did not require a complex on-chain exploit. The observable pattern was a launch-liquidity imbalance: inventory allocated for market making became concentrated sell pressure while buy-side support was weak. Similar cases can be screened with trade-side balance, VWAP slippage, order-book depth, and trade-size distribution checks during the first days after listing.

## Event timeline

| Date           | Event                                                                                                                                                     | Market-health relevance                                                                                                                 |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| December 2024  | MOVE launched, and the market maker sold a substantial amount of MOVE shortly after the token generation event, according to Movement Network Foundation. | Launch windows should have stricter surveillance because market makers often control inventory before broad price discovery stabilizes. |
| March 11, 2025 | Binance informed Movement Network Foundation of an ongoing investigation involving the market maker.                                                      | Exchange surveillance can detect abnormal behavior before public remediation begins.                                                    |
| March 18, 2025 | Binance offboarded the market maker, according to public reporting.                                                                                       | Venue-level sanctions are a strong signal that the activity violated liquidity-provider expectations.                                   |
| March 25, 2025 | Movement Network Foundation published its incident statement and announced the Movement Strategic Reserve buyback plan.                                   | Remediation shifted recovered proceeds into public-market buybacks intended to restore liquidity to the ecosystem.                      |

## Market-health signals

### One-sided market making

The central red flag is inventory being distributed as sell orders without comparable buy-side support. A legitimate market maker should usually quote both sides of the book and recycle inventory to maintain liquidity. In this case, Movement said the agreement required two-sided liquidity on the MOVE/USDT pair, while the actual activity was substantial selling without meaningful buys.

Useful checks:

- Compare sell volume and buy volume over short launch windows.
- Flag periods where a known liquidity provider's net inventory transfer is overwhelmingly one-directional.
- Monitor whether quoted bid depth remains near expected levels while inventory is being sold.

### VWAP and price impact

If market-maker inventory is sold into thin post-listing liquidity, execution prices can pull the market VWAP below normal launch expectations. The direct signal is not just a falling price; it is falling price combined with concentrated sell-side volume and weak replenishment of bids.

Useful checks:

- Compare intraday VWAP drift with cumulative net sell volume.
- Identify large sell bursts that account for a disproportionate share of total traded volume.
- Measure whether price recovers after the market maker's selling stops or after remediation begins.

### Trade-size and volume distribution

The reported sale size, roughly 66 million MOVE, indicates that a small number of actors may have dominated early trading. Volume distribution analysis can help separate broad retail price discovery from a launch dominated by institutional inventory liquidation.

Useful checks:

- Track concentration of large trades during the first 24-72 hours after listing.
- Compare trade-size distribution against peer launches with similar circulating supply.
- Flag distribution tails where a small number of large trades explain most volume.

### Governance and control risk

This case also highlights non-trading controls. A token project can create market risk before listing if contracts, intermediaries, or market-maker mandates allow a third party to control too much launch inventory without enforceable quoting constraints. The trading pattern is the symptom; weak allocation governance is the root risk.

Useful controls:

- Require pre-listing market-maker agreements to specify minimum bid/ask obligations, inventory limits, and venue-level reporting.
- Escrow market-maker inventory with staged releases tied to liquidity obligations.
- Monitor affiliated intermediaries and disclose market-maker roles before listing.

## Why this matters

Market-maker misconduct can look similar to a pump-and-dump or insider distribution event from the user's perspective: a token launches, early liquidity appears deep enough to trade, and then concentrated inventory sale overwhelms demand. The MOVE case shows why market-health tooling should combine exchange trade data with governance metadata, including known market-maker allocations and contractual obligations.

The practical monitoring lesson is that launch surveillance should turn vague "sell pressure" into thresholds that can be tested before public remediation is needed. A conservative rule set for a newly listed token would flag a designated market maker when:

- its first-72-hour sell volume is more than 3x its buy volume,
- its net sold inventory exceeds the 90th percentile of comparable launches after normalizing by circulating supply,
- its execution-weighted VWAP drifts more than 10% below the launch-window median while bid replenishment stays below the peer-launch median,
- one entity or affiliated cluster accounts for more than 25% of large sell trades during the initial listing window.

Those thresholds should be calibrated against a peer sample of token launches rather than a single project. For example, a surveillance desk can maintain a rolling benchmark table with median and 90th-percentile values for sell-side concentration, large-trade concentration, bid-depth replenishment, and three-day VWAP drift across similar listings. MOVE's reported pattern, roughly 66 million tokens sold with little buy-side support and 38 million USDT in proceeds, would then be tested against the peer median and tail percentiles instead of judged only after the price impact became public.

The root-cause model is equally important. The trading imbalance was possible because market-maker inventory appears to have been controlled by a third party without an enforceable, real-time constraint tying that allocation to two-sided quoting. The agreement required liquidity on both sides of the MOVE/USDT pair, but the observable market result described by Movement and Binance was one-sided distribution. That gap turns a governance decision into a market-health risk: inventory grants, intermediary relationships, and venue reporting should be monitored as first-class data, not only as legal documents reviewed after an incident.

On detection lead time, the public facts suggest the anomaly could have been escalated long before the March 2025 remediation. Binance's reported misconduct date was December 12, 2024; Movement said Binance notified it on March 11, 2025; Movement announced the buyback on March 25, 2025. A launch-window rule that triggered within the first 72 hours would have produced an alert around December 15, roughly 86 days before Movement's Binance notice and roughly 100 days before the public buyback announcement. Even if a team required a full week of post-listing data, the alert would still have arrived months before public remediation.

For new token listings, the strongest warning signs are:

- high sell-side concentration immediately after listing,
- weak or missing buy-side replenishment by the designated market maker,
- fast VWAP deterioration during concentrated inventory sales,
- delayed disclosure of who controlled launch liquidity,
- remediation that relies on post-event buybacks rather than preventive controls.

The recommended control loop is therefore: publish market-maker allocation metadata before listing, monitor the first 24-72 hours against peer-launch thresholds, require venue-level reporting when a liquidity provider breaches the sell/buy ratio or bid-depth floor, and escrow remaining inventory until two-sided quoting recovers. That turns the MOVE lesson from an after-the-fact case study into a pre-listing checklist.

## References

- Movement Network Foundation, [Movement Network Foundation Statement](https://www.movementnetwork.xyz/article/movement-network-foundation-statement), March 25, 2025.
- Blockworks, [Movement Labs draws scrutiny following Binance's market maker investigation](https://blockworks.com/news/binance-movement-market-maker-investigation), March 25, 2025.
- CoinDesk, [Movement's MOVE Token Soars 25% as Strategic Reserve Is Unveiled After Malicious Market Maker Activity](https://www.coindesk.com/markets/2025/03/26/movement-s-move-token-up-over-25-after-binance-offboards-market-maker), March 26, 2025.
- CoinDesk, [Inside Movement's Token-Dump Scandal: Secret Contracts, Shadow Advisers and Hidden Middlemen](https://www.coindesk.com/tech/2025/04/30/inside-movement-s-token-dump-scandal-secret-contracts-shadow-advisors-and-hidden-middlemen), April 30, 2025.
