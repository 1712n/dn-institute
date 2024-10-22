---
title: Market Health Metrics API
---

## Market Health Metrics Documentation

We're dedicated to enhancing the clarity and integrity within the cryptocurrency landscape. This documentation provides a guide on how to use and interpret market surveillance statistical metrics, made accessible through DNI's [free API](https://rapidapi.com/DNInstitute/api/crypto-market-health), aiding in the identification of possible market manipulation.

{{< market_widget >}}

Your insight is essential. We encourage submissions of analytical articles that utilize data from our API, offering a fresh perspective on the multifaceted dimensions of the cryptocurrency markets. All submissions are compensated, and noteworthy contributions could potentially open doors to a position as a Market Surveillance Analyst. Submit your articles via a pull request to our GitHub [repository](https://github.com/1712n/dn-institute/tree/main/content/market-health/posts). Join us in fostering a more transparent and healthy cryptocurrency ecosystem.

| Indicator | API metric | Description |
| ----------------------------- | --------------------------- | ------ |  
| [VWAP](/market-health/docs/vwap/_index.md)                            | `vwap` | The volume weighted average price, representing the average price of an asset as weighted by its trading volume over a specific time period. |
| [Trade Count](/market-health/docs/vwap/_index.md)                     | `tradecount` | Represents the total number of trades that have occurred within a specified timeframe, indicating market activity and liquidity. |   
| [Buy/Sell Ratio](/market-health/docs/buy-sell/_index.md)                  | `buysellratio`, `buysellratioabs` | Compares the volume of buy side trades to sell side trades, providing insights into market sentiment and potential price movements. | 
| [Time-of-trade Distribution](/market-health/docs/time-of-trade/_index.md)      | `timeoftrade` | This indicator identifies abnormal accumulation of scheduled trades executed at the same time - minute/second. |
| [First Digit Distribution](/market-health/docs/benford/_index.md)        | `firstdigitdist`, `benfordlawtest` | Measures how the first digits of trade values distribute, often used to detect anomalies or irregularities in data. The first significant digit distribution tends to fit Benford’s law for traditional financial markets and regulated exchanges. High deviation from this law may indicate potential anomalies, manipulation, or fraudulent activities in the market. |     
| [Volume Distribution](/market-health/docs/volumedist/_index.md)             | `volumedist` | Analyzes the distribution of trading volumes, helping to understand market depth and liquidity patterns. |

