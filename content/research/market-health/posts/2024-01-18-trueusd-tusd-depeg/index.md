---
title: "TrueUSD TUSD Peg Stress During Binance Selling Pressure"
date: 2024-01-18
entities:
  - TrueUSD
  - TUSD
  - Binance
  - FDUSD
  - Techteryx
---

## Summary

In January 2024, TrueUSD (TUSD) traded below its intended $1 peg during a period of heavy selling, shifting exchange incentives, and public uncertainty about redemption and reserve transparency. [CoinDesk reported](https://www.coindesk.com/markets/2024/01/16/tusd-loses-1-peg-amid-binances-fdusd-focus-analyst) on January 16 that TUSD was trading around $0.988 while Binance trading activity was moving toward FDUSD after Binance promoted FDUSD for Launchpool participation. Two days later, [CoinDesk reported](https://www.coindesk.com/markets/2024/01/18/trueusd-wobbles-towards-1-peg-amid-reported-redemption-issues) that TUSD had traded as low as about $0.96 before recovering toward $0.99, amid claims that some redemption requests had been denied.

The issuer's public response framed the move as a market-structure event rather than a solvency failure. [CryptoSlate reported](https://cryptoslate.com/trueusd-attributes-binance-launchpool-activities-to-recent-stablecoin-price-deviation/) that TrueUSD attributed the price deviation to Binance Launchpool-linked activity, said redemption channels remained available, and said routine attestations were continuing.

The TUSD case is useful for Market Health because it shows how a fiat-backed stablecoin can face a peg discount even without an on-chain exploit. The stress came from confidence, redemption credibility, exchange-liquidity concentration, and incentive changes around a dominant trading venue. Those are measurable signals even when the underlying reserve assets are off-chain.

## Metrics Used

### Peg deviation and recovery speed

The direct market-health signal was the discount from $1. A move from roughly $0.988 to an intraday low near $0.96-$0.97 showed that market participants were willing to sell TUSD below par rather than wait for redemption, arbitrage, or issuer clarification. The recovery toward $0.99 was also important: it showed that the market did not price the event like a complete collateral failure, but it still did not immediately restore full confidence.

Useful peg metrics include:

- lowest observed spot price against USDT or USD;
- time spent below $0.99 and $0.98 thresholds;
- spread between Binance, other centralized exchanges, and decentralized venues;
- recovery speed after issuer statements or large buy-side flows;
- whether arbitrage closes the discount quickly or remains impaired.

### Exchange concentration and incentive shifts

TUSD had benefited from Binance support during 2023, including high-volume trading pairs and Launchpool usage. When Launchpool incentives shifted toward FDUSD, TUSD holders had a reason to rotate into another stablecoin that carried greater utility on the same exchange. That kind of utility shock matters for stablecoin health because a token's "cash-like" demand can depend on where it is accepted and rewarded.

Exchange-concentration metrics include:

- share of spot volume on the largest venue;
- net TUSD buying or selling on Binance during the depeg window;
- changes in Launchpool, fee, margin, or collateral eligibility;
- depth of TUSD-USDT and TUSD-FDUSD books;
- stablecoin supply changes after exchange incentive changes.

### Redemption confidence

For a fiat-backed stablecoin, the strongest peg defense is credible redemption at par. Public reports that some market participants could not redeem, even if disputed by the issuer, can weaken arbitrage incentives. Traders may avoid buying discounted TUSD if they are unsure they can redeem it for dollars quickly and reliably.

The key market-health question is not only whether redemptions are formally available, but whether a broad set of holders can use them under stress. Monitoring should distinguish official redemption availability from observed redemption latency, minimum sizes, bank coverage, queue depth, and user reports of failed or delayed processing.

### Reserve attestation continuity

Reserve attestations do not by themselves guarantee instant redemption, but interruption or confusion around attestations can still affect confidence. During a peg event, users want current, independently verifiable evidence that assets cover liabilities and that the issuer can meet redemptions through its banking network.

For off-chain stablecoins, reserve-health monitoring should track:

- latest attestation timestamp;
- attestation provider and scope;
- reserve asset composition and eligible cash equivalents;
- liabilities covered by the report;
- whether attestation publication continues during stress.

The same fields are summarized in [tusd-signals.csv](tusd-signals.csv) for dataset-based review.

| Signal                  | Observation                                                            | Market-health interpretation                                         |
| ----------------------- | ---------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Peg low                 | TUSD traded around $0.96-$0.97 during the January 18 stress window     | Market priced redemption and liquidity risk despite the $1 target    |
| Binance selling         | Reports described large TUSD selling and rotation toward other stables | Exchange-driven utility shifts can pressure stablecoin demand        |
| Launchpool incentive    | TUSD was no longer the favored Launchpool asset versus FDUSD           | Incentive removal reduced exchange-native reasons to hold TUSD       |
| Redemption uncertainty  | Public reporting cited disputed claims of denied redemption requests   | Arbitrage weakens when primary redemption credibility is questioned  |
| Attestation sensitivity | The issuer emphasized ongoing routine attestations                     | Reserve-report continuity matters during off-chain stablecoin stress |

## Timeline

- **Before January 2024:** TUSD had grown with significant Binance-related demand, including trading-pair support and Launchpool usage.
- **January 15-16, 2024:** Heavy selling on Binance pushed TUSD below $1, with public reports describing a price around $0.988 and market rotation toward FDUSD.
- **January 18, 2024:** TUSD traded lower, with reports citing prices around $0.96-$0.97 before a partial recovery toward $0.99.
- **January 18, 2024:** TrueUSD publicly attributed the volatility to Binance Launchpool-related activity and said minting, redemption, and attestations remained available.
- **After the event:** TUSD remained a useful case for monitoring exchange concentration, redemption confidence, and off-chain reserve transparency around stablecoins.

## Market Health Lessons

TUSD's January 2024 depeg shows that fiat-backed stablecoins need more than nominal backing to maintain market confidence. A token can face a discount when exchange utility changes, liquidity concentrates on one venue, redemption reliability is questioned, or reserve reporting is not persuasive enough during stress.

Market-health monitoring should combine price data with behavioral and operational signals. Peg price, order-book imbalance, exchange incentive changes, supply contraction, redemption reports, and attestation freshness all measure different parts of the same risk surface. When those signals move together, a stablecoin can break below par even before there is definitive proof of reserve impairment.
