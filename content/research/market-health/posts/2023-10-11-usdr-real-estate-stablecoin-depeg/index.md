---
title: "USDR Real Estate Stablecoin Depeg and Liquid Reserve Run"
date: 2023-10-11
entities:
  - USDR
  - Tangible
  - DAI
  - Polygon
---

## Summary

On October 11, 2023, Tangible's Real USD (USDR) stablecoin lost its $1 peg after redemptions drained the protocol's liquid reserves. [CoinDesk reported](https://www.coindesk.com/markets/2023/10/11/real-estate-backed-stablecoin-usdr-de-pegs-after-treasury-was-drained-of-liquid-assets) that the Polygon-based, real-estate-backed stablecoin fell to nearly $0.51 after its treasury was drained of DAI. The same report described a treasury with zero DAI remaining and only about $6.2 million of liquid insurance-fund assets against roughly 45 million USDR in circulating supply.

The USDR case is a Market Health example of maturity and liquidity mismatch. The token was presented as stable because it was backed in part by real estate, but real estate cannot be liquidated as quickly as on-chain users can redeem or sell a token. [Open Dollar's stablecoin review](https://www.opendollar.com/blog/a-closer-look-at-stablecoins-usdr-depeg-design-mechanics) described the October 11 event as a sudden rush to redeem liquid DAI from the treasury, which triggered panic selling and sent USDR as low as $0.5040.

## Metrics Used

### Liquid reserve coverage

The most important market-health signal was not headline collateralization but immediately redeemable liquidity. A stablecoin can claim backing from valuable assets and still fail to defend its peg if the liquid slice of the treasury is exhausted before holders finish redeeming.

Useful reserve-health metrics include:

- liquid reserve value divided by circulating stablecoin supply;
- share of reserves in slow-to-liquidate real-world assets;
- daily redemption capacity versus circulating supply;
- insurance-fund composition and whether it is itself exposed to the depegging token;
- secondary-market depth if primary redemptions are paused or depleted.

### Run dynamics

USDR's depeg accelerated once holders saw that liquid DAI reserves were gone. The market then priced the stablecoin closer to the liquidity available today rather than the appraised value of real estate collateral that might be monetized later. That is a classic run signal: the first redeemers exit into liquid assets, while late redeemers are left with uncertain recovery claims.

This is why stablecoin health analysis should separate solvency from liquidity. Solvency asks whether assets might eventually cover liabilities. Liquidity asks whether holders can redeem at par under stress. USDR's visible market price showed that users cared about immediate liquidity.

### Secondary-market slippage

When redemption liquidity disappeared, USDR holders turned to decentralized exchanges. Thin or imbalanced DEX liquidity can amplify a peg break because every exit trade pushes the market price lower. A stablecoin whose primary redemption path is depleted and whose secondary liquidity is shallow can spiral from a small discount into a deep depeg within hours.

The same fields are summarized in [usdr-signals.csv](usdr-signals.csv) for dataset-based review.

| Signal                   | Observation                                                     | Market-health interpretation                                          |
| ------------------------ | --------------------------------------------------------------- | --------------------------------------------------------------------- |
| Peg low                  | USDR traded near $0.50-$0.51                                    | Market discounted the token once liquid reserves were exhausted       |
| Liquid reserve depletion | DAI reserves were reported as drained to zero                   | Real-time redemption capacity was insufficient for circulating supply |
| Circulating supply       | About 45 million USDR was outstanding                           | Liability scale exceeded immediately liquid assets                    |
| Insurance fund           | About $6.2 million of liquid insurance-fund assets remained     | Backstop size was small relative to par liabilities                   |
| Collateral mismatch      | Real estate backed much of the system but was slow to liquidate | Off-chain collateral did not provide instant peg defense              |

## Timeline

- **Before October 11, 2023:** USDR operated as a Polygon-based stablecoin backed by a mix of real estate and on-chain assets.
- **October 11, 2023:** A rush to redeem DAI from the treasury accelerated, draining the immediately liquid redemption asset.
- **October 11, 2023:** USDR fell to roughly $0.50-$0.51 as holders sold into thin secondary-market liquidity.
- **After the depeg:** Public coverage described Tangible's need to develop recovery options, including monetizing or restructuring the real-estate backing.

## Market Health Lessons

USDR shows that a stablecoin can fail at the peg even when it has claimed asset backing. The market-health question is whether the backing can become dollars quickly enough to satisfy redemptions. Real-world assets may support long-term recovery value, but they do not function like cash reserves during an on-chain run.

For stablecoin monitoring, liquid reserve coverage, redemption queue depth, reserve asset duration, DEX liquidity, and insurance-fund composition should be tracked separately from nominal collateral value. A stablecoin backed by slow assets needs larger liquid buffers, redemption throttles, or transparent liquidity gates so holders can understand whether the peg is defendable under stress.
