---
title: "USDT Curve 3pool Imbalance Depeg"
date: 2023-06-15
entities:
  - Tether
  - USDT
  - Curve Finance
  - Uniswap
  - DAI
  - USDC
---

## Summary

On June 15, 2023, USDT traded slightly below its dollar peg as selling pressure pushed stablecoin pools out of balance. [CoinDesk reported](https://www.coindesk.com/markets/2023/06/15/usdt-selling-on-curve-uniswap-spooks-traders-amid-bitcoin-drop) that USDT holdings in Curve's 3pool rose above 72%, showing that traders preferred DAI and USDC over Tether in that moment.

[CoinMarketCap summarized](https://coinmarketcap.com/academy/article/tether-allows-disclosure-of-reserve-data-amidst-depeg-concerns) the same June episode as a Curve 3pool imbalance in which USDT reached about 70% or more of pool weight and traded around $0.996-$0.997. A similar pool-imbalance signal appeared again later in the summer: [CoinDesk reported](https://www.coindesk.com/markets/2023/08/03/traders-ditch-usdt-on-curve-uniswap-pushing-key-exchange-pools-into-imbalance) that traders again ditched USDT on Curve and Uniswap, pushing the Curve 3pool to roughly 62% USDT.

The market-health issue was stablecoin interchangeability risk. Curve 3pool assumes USDT, USDC, and DAI can usually trade near parity, but the pool composition itself becomes a stress indicator when traders aggressively sell one stablecoin into the other two.

## Manipulation Analysis

The first stress vector was pool composition. A stablecoin AMM can show market confidence earlier than the headline price. When USDT's share of the 3pool rises far above the target balance, the pool is absorbing sell pressure from users who prefer other stablecoins.

The second vector was cross-venue flow. CoinDesk reported selling pressure on both Curve and Uniswap, meaning the stress signal was not isolated to one pool. Stablecoin risk systems should watch multiple venues for synchronized imbalance.

The third vector was redemption confidence. If users believe direct redemption can absorb selling pressure, a small secondary-market discount may close quickly. If they doubt redemption depth or timing, the discount can feed more pool imbalance.

The fourth vector was reflexive routing. As USDT weight increases in a pool, swaps out of USDT can become more expensive or less attractive. That can route stress to other pools and venues, making stablecoin depth fragmented during the exact period when users need reliable exits.

## Metrics Used

### Curve 3pool balance

The primary signal is whether one stablecoin dominates a pool that is designed to stay balanced.

Useful metrics include:

- USDT share of Curve 3pool;
- USDC and DAI shares of Curve 3pool;
- deviation from equal-weight target;
- hourly change in pool composition;
- one-sided deposit and withdrawal volume.

### Stablecoin peg deviation

Price should be monitored together with liquidity and venue mix.

Useful metrics include:

- USDT price deviation from $1;
- discount duration below 99.9 cents and 99.5 cents;
- USDT/USDC and USDT/DAI swap slippage;
- arbitrage volume after the discount opens;
- exchange-order-book depth around $1.

### Cross-venue selling

Pool stress becomes more important when several venues show the same direction.

Useful metrics include:

- net USDT sold on Curve;
- net USDT sold on Uniswap;
- centralized exchange USDT order-flow imbalance;
- bridge inflows of USDT to major trading venues;
- stablecoin swap route concentration.

### Redemption and confidence signals

Secondary-market discounts need issuer and redemption context.

Useful metrics include:

- Tether redemption volume;
- reported redemption readiness;
- reserve-disclosure updates;
- time between public reassurance and price normalization;
- social and news sentiment around USDT reserves.

The same fields are summarized in [usdt-curve-3pool-signals.csv](usdt-curve-3pool-signals.csv) for dataset-based review.

| Signal                | Observation                                                         | Market-health interpretation                                       |
| --------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------ |
| 3pool USDT overweight | CoinDesk reported USDT holdings above 72% in Curve 3pool            | Pool composition can reveal stablecoin exit pressure               |
| Peg deviation         | CoinMarketCap summarized USDT trading around $0.996-$0.997          | Small peg breaks matter when paired with large pool imbalance      |
| Cross-venue selling   | CoinDesk reported USDT selling on Curve and Uniswap                 | Stress is more serious when multiple liquidity venues align        |
| Repeated imbalance    | CoinDesk later reported another USDT-heavy Curve/Uniswap imbalance  | Recurrent pool imbalance should be treated as a stablecoin signal  |
| Confidence monitoring | Public coverage tied the event to depeg concerns and reserve debate | Reserve confidence and AMM composition should be monitored jointly |

## Timeline

- **June 15, 2023:** USDT selling pushed Curve 3pool far from equal weight, with USDT becoming the dominant pool asset.
- **June 15-16, 2023:** Public coverage framed the move as a slight depeg and a stress signal rather than a full reserve failure.
- **August 3, 2023:** A similar USDT-heavy imbalance appeared again across Curve and Uniswap stablecoin pools.
- **After the imbalances:** The episodes remained useful examples of how stablecoin pool composition can warn of confidence stress even when a peg break is small.

## Market Health Lessons

USDT's Curve 3pool imbalance shows that stablecoin risk is not only about price. A token can trade close to $1 while pools reveal that users are trying to exit it into other stablecoins.

For Market Health, stablecoin dashboards should combine peg deviation, AMM composition, cross-venue flow, redemption signals, and issuer reserve communication. A pool that becomes heavily overweight one stablecoin is an early warning that traders no longer view the assets as interchangeable cash equivalents.
