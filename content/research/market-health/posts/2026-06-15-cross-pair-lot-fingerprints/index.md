---
title: "Cross-pair exact-lot fingerprints: a surveillance signal, not proof of wash trading"
date: 2026-06-15
description: "One week of Binance BOME and NEIRO spot data shows the same exact order-size fingerprints across USDT and USDC markets. The pattern identifies shared automation, but public aggregate trades alone cannot establish common beneficial ownership."
entities:
  - Binance
  - BOME
  - NEIRO
  - USDT
  - USDC
---

## Summary

This study examines 606,658 public Binance aggregate trades across BOME/USDT, BOME/USDC, NEIRO/USDT, and NEIRO/USDC from June 7 through June 13, 2026. Two exact quantities, 200,000 tokens and 14,748 tokens, recur across all four markets.

The 200,000-token quantity represents:

- 19.73% of BOME/USDT aggregate trades and 20.17% of quoted notional;
- 18.44% of BOME/USDC aggregate trades and 19.91% of quoted notional;
- 17.35% of NEIRO/USDT aggregate trades and 8.52% of quoted notional;
- 51.76% of NEIRO/USDC aggregate trades and 20.80% of quoted notional.

The persistence and cross-pair reuse identify a strong automated execution fingerprint. They do **not**, by themselves, establish wash trading. Binance's public aggregate-trade files contain no account, order-owner, or beneficial-owner identifiers. The data therefore cannot show whether the buyer and seller are controlled by the same party, which is central to a wash-trading determination.

The practical lesson is methodological: repeated exact sizes are useful for generating surveillance alerts, but an alert should be escalated only after tests for ownership, self-trade prevention, quote replenishment, price impact, and economic risk transfer.

## Data and method

The source is the official [Binance public data archive](https://github.com/binance/binance-public-data). Binance documents each spot `aggTrades` row as:

1. aggregate trade ID;
2. price;
3. quantity;
4. first underlying trade ID;
5. last underlying trade ID;
6. timestamp;
7. whether the buyer was the maker;
8. whether the trade was the best-price match.

For this 2026 sample, the timestamp column uses microsecond precision under the archive's documented post-2024 spot-data convention.

The analysis:

- downloads 28 daily archives directly from `data.binance.vision`;
- records a SHA-256 hash for every source archive;
- counts exact decimal quantities without floating-point rounding;
- calculates each quantity's share of aggregate-trade count and quote notional;
- separates buyer-initiated and seller-initiated aggregate trades using the buyer-maker flag;
- checks whether an aggregate row represents one underlying fill or several;
- checks whether the same timestamp contains the target quantity on both aggressor sides.

The full URLs and hashes are in [`source_manifest.csv`](source_manifest.csv). The calculations can be regenerated with:

```sh
python analyze.py
```

The script uses only the Python standard library. Generated results are stored in [`daily_metrics.csv`](daily_metrics.csv) and [`fingerprint_summary.csv`](fingerprint_summary.csv).

## Result 1: the 200,000-token lot persists across every market

{{< figure src="daily_200k_notional_share.svg" alt="Daily share of quote notional executed in aggregate trades of exactly 200,000 tokens across four Binance spot markets" caption="The 200,000-token exact lot persists on all seven days. Its share of daily notional is especially stable in both BOME markets and NEIRO/USDC." loading="lazy" >}}

For BOME/USDT, the 200,000-token quantity is the most common exact quantity on every day in the sample. It accounts for between 12.15% and 23.46% of daily aggregate-trade count, and between 13.91% and 26.10% of daily notional.

BOME/USDC has much lower total activity, but the same quantity remains prominent. It becomes the day's most common quantity on four of seven days and contributes between 14.44% and 27.16% of daily notional on those four days.

The same 200,000-token fingerprint also appears in both NEIRO markets. It is particularly dominant by trade count in NEIRO/USDC, where its daily share ranges from 43.32% to 59.76%.

This cross-token, cross-quote reuse is more informative than observing a round number in one market. It suggests that one or more automated systems use a shared sizing configuration.

## Result 2: a non-round fingerprint travels with the round one

{{< figure src="cross_pair_fingerprints.svg" alt="Aggregate-trade count shares for exact quantities of 200,000 and 14,748 tokens across BOME and NEIRO spot markets" caption="Both exact quantities occur in all four markets. The non-round 14,748-token fingerprint is concentrated in BOME, while the 200,000-token fingerprint is strong across both assets." loading="lazy" >}}

The exact quantity 14,748 is useful because ordinary decimal rounding is a weak explanation for it. It accounts for:

- 19.03% of BOME/USDT aggregate trades;
- 18.54% of BOME/USDC aggregate trades;
- 0.84% of NEIRO/USDT aggregate trades;
- 2.14% of NEIRO/USDC aggregate trades.

Across both BOME markets, the 200,000 and 14,748 quantities together represent roughly 38% of all aggregate-trade rows. Their similar count shares but very different notional shares are consistent with two configured execution sizes rather than a single broad "round-number preference."

The 14,748 quantity also appears in NEIRO, but much less often. That weaker reuse is still valuable for clustering execution behavior: a surveillance system could treat the pair of quantities as a fingerprint, while retaining the possibility that unrelated users or multiple bots independently use the same sizes.

## Result 3: side balance raises an alert but does not resolve ownership

For the 200,000-token quantity, buyer-initiated shares range from 43.74% to 50.47% across the four markets. The 14,748-token quantity is similarly balanced, with buyer-initiated shares between 46.43% and 49.89%.

Balanced aggressor flow can be compatible with:

- two-sided market making;
- inventory-rebalancing algorithms;
- execution services using fixed clip sizes;
- multiple unrelated strategies responding to the same liquidity;
- volume-generating or wash-trading activity.

The public rows do not distinguish among those explanations. Importantly, the timestamp test found almost no instances in which the target quantity appeared on both aggressor sides at the exact same microsecond: zero in both BOME markets and only three 200,000-token timestamps across the two NEIRO markets. There is therefore no simple public-data pattern of simultaneous matched opposite-side prints.

Most target rows also correspond to a single underlying fill. Depending on the market, 72.49% to 96.93% of the 200,000-token aggregate rows and more than 91% of the 14,748-token rows contain one underlying trade ID. The fingerprints are not merely an artifact of many differently sized fills being merged into the same aggregate row.

## What would turn the signal into stronger evidence?

Regulators treat wash trading as a question of intent, common control, and the absence of bona fide market risk. For example, the U.S. Commodity Futures Trading Commission's [Coinbase enforcement order](https://www.cftc.gov/PressRoom/PressReleases/8369-21) focused on transactions between programs operated by the same entity and the resulting misleading market information.

An exchange or regulator with account-level data could test the present alert by adding:

1. **Beneficial-ownership linkage:** determine whether the buyer and seller accounts share ownership, funding sources, API keys, devices, or withdrawal destinations.
2. **Self-trade prevention evidence:** inspect whether the trades bypassed, disabled, or repeatedly triggered self-trade controls.
3. **Position and risk transfer:** measure whether the participant's net position and economic exposure remain effectively unchanged after the repeated prints.
4. **Order-book response:** test whether displayed liquidity is replenished mechanically at the same sizes and prices.
5. **Price and volume impact:** compare the fingerprint's contribution to reported volume with its lasting effect on price, spread, and depth.
6. **Cross-market synchronization:** identify whether the same controller sends related orders across BOME and NEIRO markets within implausibly tight intervals.

These tests distinguish a useful anomaly detector from an unsupported accusation.

## Surveillance recommendation

Exact-lot concentration should be implemented as a multi-stage alert:

- calculate daily and rolling shares for each exact quantity by trade count and notional;
- compare the same quantity across quote currencies and unrelated base assets;
- retain non-round quantities as higher-information fingerprints;
- measure aggressor-side balance and timestamp clustering;
- require account-level ownership or risk-transfer evidence before classifying activity as wash trading.

The BOME and NEIRO sample would clearly pass the first-stage concentration and cross-pair tests. It would not pass a final wash-trading classification using public data alone.

## Limitations

- Aggregate trades are not order-book events and do not include canceled or unfilled orders.
- Public files contain no account identifiers or self-trade-prevention results.
- USDT and USDC notionals are reported in their native quote units and are not adjusted for small stablecoin price differences.
- The seven-day window establishes persistence, not a long-run baseline.
- Exact-size reuse can identify common software behavior without proving common ownership.

The analysis should therefore be read as a reproducible market-surveillance case study and a false-positive control, not as a finding that Binance, BOME, NEIRO, or any identifiable trader engaged in manipulation.
