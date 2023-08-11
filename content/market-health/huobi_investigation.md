---
date: 2023-06
target-entities: Huobi
entity-types: Exchange
attack-types: Market manipulation
title: "Uncovering Wash Trading and Market Manipulation on Huobi"
---

## Summary
1. Recent data reveals a surge in manipulative practices and liquidity issues within Huobi's trading volume since June.
2. Analysis of trade sizes pinpointed heightened activity from volume-generating trading algorithms, detected ahead of public concerns about exchange solvency.
3. Huobi's founder and exchange-linked tokens (HT, TRX) were manipulated, inflating trade volumes and token prices via transaction size adjustments long before.
4. Wash trading criteria comprising volume distribution skewness and fitting estimate show synchronized fluctuations across multiple spot markets (COMP, SOL, LINK, SUI, DOGE).


## Metrics used

### Abnormal activity indicator - Average transaction size

<gallery>
![doge-usdt volume metrics](img/huobi-investigation/tx-size-doge.png)
![ht-usdt volume metrics](img/huobi-investigation/tx-size-ht.png)
![sol-usdt volume metrics](img/huobi-investigation/tx-size-sol.png)
![sui-usdt volume metrics](img/huobi-investigation/tx-size-sui.png)

<p style="text-align: center;">Average transaction size, volume and trade count on multiple Huobi’s spot market over time, June - July 2023</p>

The main indicator, which signals about abnormal activity is huge jumps in average size of a transaction. Normally this value is always volatile. 
Low std values and rare but significant changes in average value of this metric strongly indicates dominating artificial trading activity.

![doge-usdt avg tx size comparison across multiple exchanges](img/huobi-investigation/doge-avg-tx-huobi-coinbase-binance-okx.jpg)

### Order printing bots – Volume distribution tail and skewness

Further analysis of the trading volume revealed even more interesting patterns. Typically, trading volume should adhere to a [power law](https://en.wikipedia.org/wiki/Power_law) 
heavy tail distribution, where small-sized trades are common and large-sized trades are rare. To estimate the power-law fitting we use a tail exponent. 
It is expected to be less than 3 on traditional financial markets.


![ht-usdt exponent](img/huobi-investigation/exponent-ht.png)

These metrics reveal the most obvious abnormalities in trade volume distribution. Despite the fact that it cannot be interpreted solely, 
it highlights the presence of individual traders placing high-volume orders as well as the trading bots printing dozens of trades of the same size. 

<gallery>
![comp-usdt exponent comparison between huobi and binance](img/huobi-investigation/exponent-comp-binance-huobi.png)
![doge-usdt exponent comparison between huobi and binance](img/huobi-investigation/exponent-doge-binance-huobi.png)
![sol-usdt exponent comparison between huobi and binance](img/huobi-investigation/exponent-sol-binance-huobi.png)

<p style="text-align: center;">Exponent comparison between Huobi and Binance for different spot markets over time, July 2023 </p>


Given that volume distribution in traditional financial markets is asymmetrical (with a predominance of trades of a small size), 
skewness of such distribution type should be greater than 1. This has nothing to do with the volume distribution built on Huobi’s market data. 

![skewness parameter of different markets](img/huobi-investigation/skewness.jpg)
![trx-usdt skewness comparison between huobi and binance](img/huobi-investigation/skewness_binance_huobi.png)

Below zero skewness values can be spotted visually. They indicate an artificially inflated volume.
![comp-usdt distribution comparison](img/huobi-investigation/comp-distribution-binance-huobi.png)
![comp-usdt distribution comparison](img/huobi-investigation/sol-distribution-binance-huobi.png)

### Real users presence – Spotting round-size trades
Recently published [research](https://twitter.com/adamscochran/status/1687959096316542976) suggests Huobi's insufficient funds to cover user obligations, 
prompting extreme actions like wash trading and manipulation to appear financially sound. There are several ways to match real retail users and reported volumes. 

![clustering student test with 100x rounding](img/huobi-investigation/sui-clustering-test-huobi-coinbase.png)
Assuming that retail investors often use round values for trading, the retail clustering indicator compares frequency of round volumes (100, 200, etc.) 
with the frequency of use of other trade sizes. Higher value of this metric represents higher probability of presence of real users. In the Huobi case 
this metric shows extremely low values.

![KS test for Benford's law, different markets'](img/huobi-investigation/ks-benford-huobi.jpg)

![sui-usdt KS test for Benford's law comparison between huobi and binance](img/huobi-investigation/sui-ks-benford-huobi-binance.jpg)
![trx-usdt KS test for Benford's law comparison between huobi and binance](img/huobi-investigation/trx-ks-benford-huobi-binance.jpg)
<p style="text-align: center;">KS test for first digit distribution comparison between Huobi and Binance for different spot markets over time, July 2023  </p>

This metric utilizes Benford's law, which claims that in many real-life sets of numerical data, the leading digit is likely to be small. In case of artificial 
volumes, first digits will be distributed uniformly, and KS test value will show higher values. In the Huobi case, this metric also indirectly confirms our 
hypothesis.

### Exchange native token as a proxy indicator

Another unofficial indicator of an exchange's health is the native token of the exchange. In Huobi's case such a token is HT. Previous metrics indicated about
artificial trading volume, but there is also evidence of Huobi attempts to influence the price. 
 

![ht-usdt buy/sell volume ratio comparison](img/huobi-investigation/ht-usdt-buy-sell-volume-multiple-exchange-comparison.jpg)

In normal conditions this metric is very volatile and looks like a stochastic process. In many ways, ratio of "buy" volume and "sell" volume determines 
price behavior and it furhther movements. However, in Huobi case this metrics often fluctuates in a very small range. It means that Huobi tries to controle
all price movements of their token price, and, basically, manipulates the market. It's worths nothing to mention that Huobi has information about all 
open orders at their platform, which makes manipulating the price much more dangerous. For Huobi users, of course. 