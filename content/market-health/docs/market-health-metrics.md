---
title: Market health metrics
bookToc: true
weight: 10
---

## Market Health Metrics Documentation

This documentation provides a guide on how to use and interpret market surveillance statistical metrics from the DNI [free API](https://rapidapi.com/DNInstitute/api/crypto-market-health) to identify anomalies and manipulations on cryptocurrency exchanges. Feel free to sumbit your analytical articles based on the API data here!

Indicator | Description | API metric
-- | -- | --
Volume-volatility correlation | Trading volumes usually spike when volatility in markets rise. Normally, high values of this metric indicate healthy market behavior. | `volume_volatility_correlation`
Benford's Law | The first significant digit distribution tends to fit Benford’s law for traditional financial markets and regulated exchanges. High deviation from this law may indicate potential anomalies, manipulation, or fraudulent activities in the market. | `first_digit_distribution`
Power law fitting | Power law appears to describe histograms of trading volume. The power laws observed in financial data arises when the trading behavior is performed in an optimal way. High values for this metric can indicate abnormal interest or attempts at market manipulation. | `volume_distribution_kurtosis`<br>`volume_distribution_mean`<br>`volume_distribution_median`<br>`volumedistribution_mode`<br>`volume_distribution_mode`<br>`volume_distribution_skewness`<br>`volume_distribution_std`
Time-of-trade | This indicator identifies abnormal accumulation of scheduled trades executed at the same time - minute/second. | `count_time_distribution`
Buy/sell ratio | Depending on whether the order taker is a buyer or seller, each trade is associated with a specific side of the trade. A consistent and large number of trades on one side of the book is a pattern that may signal automated activity. | `buy_sell_count_ratio`
VWAP | Volume weighted average price | `vwap`
