---
title: "Iron Finance TITAN Collapse and IRON Stablecoin Bank Run"
date: 2021-06-17
entities:
  - Iron Finance
  - IRON
  - TITAN
  - Polygon
  - USDC
---

## Summary

On June 16-17, 2021, Iron Finance's partially collateralized IRON stablecoin broke its $1 peg as the protocol's share token, TITAN, collapsed toward zero. [CoinDesk reported](https://www.coindesk.com/markets/2021/06/17/iron-finances-titan-token-falls-to-near-zero-in-defi-panic-selling) that TITAN fell from above $60 to near zero during panic selling, while IRON traded below its intended peg. The same report described a feedback loop in which large holders sold TITAN, IRON's mechanism minted more TITAN to defend the stablecoin, and falling TITAN prices further weakened confidence in the system.

[CoinDesk's postmortem coverage](https://www.coindesk.com/markets/2021/06/17/in-token-crash-postmortem-iron-finance-says-it-suffered-cryptos-first-large-scale-bank-run) said Iron Finance described the event as the world's first large-scale crypto bank run. Redemptions were disabled automatically when TITAN's price dropped too far, which meant the primary peg-restoration path became unreliable at the exact moment users most wanted to exit. A separate [CoinDesk analysis](https://www.coindesk.com/policy/2021/06/17/paying-the-iron-price-fractional-reserve-banking-on-a-blockchain) explained the design as roughly 75% USDC-backed and 25% backed by TITAN, making the final quarter of collateral highly reflexive.

The Iron Finance case is useful for Market Health because it combines stablecoin peg risk, share-token reflexivity, liquidity shock, and redemption-mechanism fragility. The protocol did not need a smart-contract exploit to fail. Its market design created a condition where selling pressure on the share token could rapidly impair stablecoin confidence.

## Metrics Used

### Peg deviation and redemption status

The core signal was IRON trading below $1 while users tried to redeem or exit. A stablecoin discount is more severe when the protocol's redemption path is paused, delayed, or dependent on a rapidly collapsing asset. Redemptions being disabled automatically during the run converted a market discount into a deeper confidence crisis.

Useful metrics include:

- IRON price versus $1 across DEX pools;
- time spent below $0.99, $0.95, and collateral-floor thresholds;
- whether redemptions are active, throttled, delayed, or disabled;
- redemption throughput versus circulating IRON supply;
- market price gap between IRON and the value of its redeemable backing.

### Share-token reflexivity

TITAN served as the volatile share token used by the stabilization mechanism. When users redeemed IRON, the system could mint or distribute TITAN as part of the process. That created reflexivity: falling TITAN reduced perceived backing, redemptions increased TITAN supply, and the extra TITAN supply created more sell pressure.

Market-health monitoring should treat share-token price, mint rate, circulating supply, and liquidity depth as stablecoin-risk metrics. A partially collateralized stablecoin cannot be assessed only by the value of its hard collateral when the remaining backing depends on a token that can be minted into a falling market.

### Liquidity-pool exit pressure

The run accelerated through liquidity pools. As TITAN and IRON holders exited, pool balances shifted and slippage increased. Thin liquidity or imbalanced pools can make a stablecoin appear to collapse faster than its nominal collateral value because every trade worsens the observable market price.

Useful pool metrics include:

- IRON-USDC and TITAN-USDC pool depth;
- pool imbalance during the run;
- large-wallet withdrawals from liquidity pools;
- slippage for a fixed IRON redemption or swap size;
- whether liquidity providers are removing depth faster than arbitrage can restore the peg.

### Collateral composition

The design used hard collateral and volatile protocol equity together. The USDC portion could support a floor, but the TITAN portion lost value during the same event that required it to defend the peg. That makes collateral composition a first-class market-health signal, not a footnote.

For partially collateralized stablecoins, monitoring should separate:

- hard collateral share;
- volatile share-token collateral share;
- current and stressed value of the volatile backing;
- mint or redemption formulas tied to the share token;
- emergency conditions that stop redemptions or change formula behavior.

The same fields are summarized in [iron-finance-signals.csv](iron-finance-signals.csv) for dataset-based review.

| Signal                 | Observation                                                      | Market-health interpretation                                       |
| ---------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------ |
| TITAN collapse         | TITAN fell from above $60 to near zero                           | Share-token collateral became unusable during peg stress           |
| IRON depeg             | IRON traded below its intended $1 peg                            | Stablecoin holders discounted redemption and backing reliability   |
| Redemption impairment  | Redemptions were disabled automatically during the run           | Primary peg-defense path failed under stress                       |
| Fractional collateral  | Design was roughly 75% USDC and 25% TITAN-backed                 | Hard-collateral floor did not protect the reflexive collateral leg |
| Liquidity exit dynamic | Large holders selling and liquidity withdrawal accelerated panic | Pool depth and whale exits were leading risk indicators            |

## Timeline

- **Before June 16, 2021:** IRON operated as a partially collateralized stablecoin backed by USDC and the TITAN share token.
- **June 16, 2021:** Large TITAN selling and liquidity exits began pressuring both TITAN and IRON markets.
- **June 16-17, 2021:** TITAN collapsed from above $60 to near zero, while IRON traded below peg.
- **June 17, 2021:** Iron Finance described the event as a large-scale crypto bank run and announced that redemptions would resume after an automatic disablement.
- **After the collapse:** The episode became a reference case for algorithmic and fractional-reserve stablecoin death spirals.

## Market Health Lessons

Iron Finance shows that stablecoin risk can come from market mechanics rather than a direct exploit. When a stablecoin's backing depends partly on a volatile share token, the share token's liquidity and mint dynamics become part of the stablecoin's solvency story.

Market-health monitoring should combine peg price, redemption status, hard-collateral ratio, share-token drawdown, liquidity-pool imbalance, and whale liquidity movements. If the volatile backing token can be minted into a falling market, small peg deviations can become self-reinforcing bank runs.
