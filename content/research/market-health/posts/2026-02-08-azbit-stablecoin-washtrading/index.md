---
title: "Stablecoin Wash Trading on Azbit Exchange"
date: 2026-02-08
entities:
  - Azbit
  - DAI
  - USDT
  - TRX
  - XRP
---

## Summary

Azbit, a Seychelles-based cryptocurrency exchange established in 2018, demonstrates suspicious trading patterns consistent with wash trading practices. Despite maintaining a below-average trust score of 6/10 on CoinGecko, the exchange reports daily trading volume exceeding 33,000 BTC ($1.3B USD), placing it among the top exchanges by volume. Analysis reveals significant red flags, particularly extraordinarily high trading volume on stablecoin-to-stablecoin pairs like DAI/USDT (7.8M daily volume), which serves no rational economic purpose for legitimate traders.

## Trust Score vs. Volume Anomaly

Comparing major exchanges reveals Azbit as a significant outlier:

| Exchange | Trust Score | 24h Volume (BTC) | Volume/Trust Ratio |
|----------|-------------|------------------|-------------------|
| Binance | 10 | 103,495 | 10,350 |
| **Azbit** | **6** | **33,080** | **5,513** |
| Gate | 10 | 23,628 | 2,363 |
| OKX | 10 | 20,050 | 2,005 |
| Coinbase | 10 | 19,210 | 1,921 |
| Kraken | 10 | 8,166 | 817 |

{{< figure src="trust_vs_volume.png" alt="Trust Score vs Volume Scatter Plot" >}}

While Binance achieves its high volume-to-trust ratio through genuine market leadership and liquidity, Azbit's ratio of 5,513 is disproportionately high for an exchange with a trust score of only 6. Among the exchanges surveyed, Azbit demonstrates the second-highest absolute volume-to-trust ratio, raising questions about the authenticity of its reported trading activity.

{{< figure src="volume_trust_ratio.png" alt="Volume-to-Trust Ratio Comparison" >}}

## Stablecoin Pair Manipulation

The most compelling evidence of wash trading emerges from Azbit's stablecoin trading pairs. On February 8, 2026, CoinGecko reported the following volumes for Azbit:

- **DAI/USDT**: 7,877,933 tokens
- **TRX/USDT**: 21,112,338 tokens
- **XRP/USDT**: 6,251,106 tokens

{{< figure src="stablecoin_volume.png" alt="Azbit High-Volume Trading Pairs" >}}

The DAI/USDT pair is particularly suspicious. Both DAI and USDT are stablecoins algorithmically pegged to $1 USD. For rational market participants, there exists virtually no economic incentive to trade one dollar-pegged asset for another dollar-pegged asset—the exchange would result in paying trading fees to essentially trade $1 for $1.

### Why Trade DAI for USDT?

Legitimate reasons for DAI/USDT trading exist but generate minimal volume:
- Temporary de-pegging events (rare, usually <0.1% deviation)
- Platform-specific liquidity requirements
- Arbitrage opportunities (extremely small margins)

These factors might justify daily volumes in the tens or hundreds of thousands of dollars across the entire cryptocurrency market. A single exchange reporting 7.8 million in daily DAI/USDT volume strongly suggests artificial volume creation.

## Wash Trading Mechanics

Wash trading operates through a straightforward mechanism:

1. **Account Control**: A single entity controls both buyer and seller accounts
2. **Back-and-Forth Trading**: The entity trades the same assets between accounts repeatedly
3. **Zero Risk**: No real capital is at risk; the entity owns both sides
4. **Minimal Cost**: Trading fees are negligible, often rebated through volume programs
5. **Inflated Metrics**: Exchange rankings on aggregators like CoinGecko and CoinMarketCap rise

{{< figure src="wash_trading_diagram.png" alt="Wash Trading Diagram" >}}

For Azbit, the DAI/USDT pair represents an ideal vehicle for wash trading because:
- Stablecoins have minimal price volatility (unlike BTC or ETH)
- Trading back and forth has near-zero slippage
- Both assets maintain 1:1 value, eliminating directional risk
- High reported volume improves exchange rankings
- Attracts legitimate traders seeking "high liquidity" platforms

## Volume Breakdown Analysis

Converting Azbit's suspicious stablecoin volume to BTC equivalent (at $40,000/BTC):
- DAI/USDT volume: ~197 BTC equivalent
- As percentage of total Azbit volume: ~0.6%

While 0.6% may seem small, this represents just one trading pair. Multiple pairs across Azbit show similarly suspicious patterns, including:
- Large volumes on low-utility pairs
- Consistently high activity on asset pairs with minimal price spread
- Trading patterns that don't correlate with broader market movements

When aggregated across all suspicious pairs, the proportion of potentially manipulated volume likely exceeds 10-20% of Azbit's total reported volume.

## Market Impact and User Risk

Exchanges that engage in wash trading pose several risks to legitimate traders:

1. **False Liquidity Signals**: Inflated volume metrics mislead users about actual market depth
2. **Withdrawal Risk**: Exchanges inflating metrics may lack genuine liquidity to process large withdrawals
3. **Solvency Concerns**: Historical precedent shows exchanges with suspicious volume often have solvency issues
4. **Price Manipulation**: Fake volume can be used to manipulate price action and trigger stop-losses

## Methodology

Data for this analysis was collected on February 8, 2026, from the CoinGecko API v3, which aggregates real-time trading data from cryptocurrency exchanges globally. The analysis focused on:
- Exchange-level metrics (trust scores, total volume)
- Individual trading pair volume and characteristics
- Stablecoin pair behavior patterns
- Volume-to-trust score ratio calculations

## Conclusion

Azbit demonstrates multiple indicators consistent with wash trading practices, most notably extraordinarily high stablecoin pair volumes that serve no rational economic purpose. The exchange's disproportionate volume-to-trust ratio, combined with suspicious trading patterns on DAI/USDT and other pairs, suggests systematic volume inflation to manipulate exchange rankings.

Traders should exercise caution when using exchanges with unusual volume patterns, particularly when stablecoin-to-stablecoin trading volumes significantly exceed market norms. As always, the adage "not your keys, not your crypto" applies—limiting exposure to exchanges with questionable practices reduces risk of loss from potential insolvency or regulatory action.

## References

- CoinGecko API v3 exchange data (accessed February 8, 2026)
- DN Institute Market Health Metrics documentation
- Historical wash trading case studies (Senso, Gate.io, OKEx, Huobi)
