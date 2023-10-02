---
title: "VWAP"
navShowPages: true
bookToc: true
weight: 60
---

## General Description

VWAP, or Volume Weighted Average Price, is a trading benchmark used by traders that gives the average price a security has traded at throughout the day, based on both volume and price. It is important because it provides traders with insight into both the trend and value of a security.

## Theory

The idea behind the VWAP is simple: it gives an average price of a security over a particular time frame that is adjusted based on volume. This means more weight is given to the price levels where a lot of trading activity has occurred, giving a more realistic average price that is less susceptible to manipulation.

## Crypto Context

In cryptocurrency markets, the VWAP can be used to understand the true average price of a coin, adjusted for volume. This is especially useful in these markets, which can be more volatile and less liquid compared to traditional financial markets.

## Usage Examples

Consider the API metric:

- `vwap`: An example value of `1624.164163150681200000` is provided. This value represents the average price, adjusted for volume, at which trades have been executed over a defined period.

## How to Interpret

- A significant difference between the VWAP and the current price may indicate manipulation or that the price is moving in a particular direction. For instance, if the current price is much higher than the VWAP, it may be considered overvalued, as it has been trading at a price higher than the average volume-weighted price.
- It's essential to monitor the VWAP value in relation to the current price to detect potential anomalies. Consistently observing the VWAP can provide insight into potential price manipulation, as large orders or high-frequency trading can skew the current price away from the VWAP.

## Visuals

A line chart plotting the VWAP and the current price over time can provide a clear visual representation of price trends and potential anomalies. A consistent gap between the VWAP and the current price should be a red flag for traders and analysts.

## References and Further Reading

- [Volume Weighted Average Price (VWAP)](https://www.investopedia.com/terms/v/vwap.asp)
- [Using VWAP to Understand Volume and Control Your Execution](https://www.traderhq.com/using-vwap-understand-volume-control-execution/)
- [A Closer Look at VWAP as a Trend Tool](https://tickertape.tdameritrade.com/trading/vwap-volume-weighted-average-price-trend-17328)
