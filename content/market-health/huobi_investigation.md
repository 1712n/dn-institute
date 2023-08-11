---
date: 2023-06
entities: 
- Huobi
- HT
- TRX
- DOGE
title: "Uncovering Wash Trading and Market Manipulation on Huobi"
---

## Summary
1. Recent data reveals a surge in manipulative practices and liquidity issues within Huobi's trading volume since June.
2. Analysis of trade sizes pinpointed heightened activity from volume-generating trading algorithms, detected ahead of public concerns about exchange solvency.
3. Huobi's founder and exchange-linked tokens (HT, TRX) were manipulated, inflating trade volumes and token prices via transaction size adjustments long before.
4. Wash trading criteria comprising volume distribution skewness and fitting estimate show synchronized fluctuations across multiple spot markets (COMP, SOL, LINK, SUI, DOGE).
5. Absence of retail transaction clustering underscores Huobi's artificial trading volume, pointing to a distinct lack of genuine retail presence.
6. Huobi's potential market manipulation of its native token (HT) through order book insights raises user risks and emphasizes the need for caution.

## Metrics used

### Abnormal activity indicator - Average transaction size

Every minute, buyers and sellers generate numerous transactions across various crypto market platforms. The size of each transaction serves as a key parameter that provides insights into market participants, including liquidity providers, retail traders, and the exchanges themselves.

![doge-usdt volume metrics](img/huobi-investigation/tx-size-doge.png)
![ht-usdt volume metrics](img/huobi-investigation/tx-size-ht.png)
![sol-usdt volume metrics](img/huobi-investigation/tx-size-sol.png)
![sui-usdt volume metrics](img/huobi-investigation/tx-size-sui.png)

<p style="text-align: center;">Average transaction size, volume, and trade count on multiple Huobi spot market over time, June - July 2023</p>

The primary indicator signaling abnormal activity is the occurrence of significant spikes in the average transaction size. Typically, this value exhibits inherent volatility. Low standard deviation values found across multiple Huobi's spot markets, coupled with infrequent yet substantial fluctuations in the average transaction size, strongly indicate the prevalence of dominant artificial trading activity of the following tokens - DOGE, HT, SOL, SUI.

![doge-usdt avg tx size comparison across multiple exchanges](img/huobi-investigation/doge-avg-tx-huobi-coinbase-binance-okx.jpg)
<p style="text-align: center;">Average transaction size on DOGE/USDT spot market across multiple exchanges, May - July 2023</p>

### Order printing bots - Volume distribution tail and skewness

Further analysis of the trading volume revealed even more interesting patterns. Typically, trading volume should adhere to a [power law](https://en.wikipedia.org/wiki/Power_law) heavy tail distribution, where small-sized trades are common and large-sized trades are rare.

![comp-usdt distribution comparison](img/huobi-investigation/comp-distribution-binance-huobi.png)
![comp-usdt distribution comparison](img/huobi-investigation/sol-distribution-binance-huobi.png)
<p style="text-align: center;">Trade volume distribution samples comparison, COMP and SOL tokens on Huobi and Binance, July 2023</p>

To estimate the power-law fitting we use a tail exponent. It is expected to be less than 3 in traditional financial markets.

![ht-usdt exponent](img/huobi-investigation/exponent-ht.png)
<p style="text-align: center;">Volume distribution fitting indicator, HT/USDT spot market on Huobi, July 2023</p>

Despite the fact that a tail exponent cannot be considered solely, it highlights the presence of individual traders placing high-volume orders as well as the trading bots printing dozens of trades of the same size. 

![comp-usdt exponent comparison between huobi and binance](img/huobi-investigation/exponent-comp-binance-huobi.png)
![doge-usdt exponent comparison between huobi and binance](img/huobi-investigation/exponent-doge-binance-huobi.png)
![sol-usdt exponent comparison between huobi and binance](img/huobi-investigation/exponent-sol-binance-huobi.png)

<p style="text-align: center;">Volume distribution fitting indicator, various spot markets on Huobi and Binance over time, July 2023 </p>

Given that volume distribution in traditional financial markets is asymmetrical (with a predominance of trades of a small size), 
skewness of such distribution type should be greater than 1. However, this characteristic does not apply to the volume distribution observed in the market data from Huobi.

![skewness parameter of different markets](img/huobi-investigation/skewness-huobi.jpg)
<p style="text-align: center;">Skewness of trade volume distribution for different Huobi spot markets over time, June - July 2023 </p>

![trx-usdt skewness comparison between huobi and binance](img/huobi-investigation/skewness_binance_huobi.png)
<p style="text-align: center;">Skewness comparison between Huobi and Binance for TRX/USDT spot market over time, May - July 2023 </p>

Below zero skewness values can be spotted visually. They indicate volume manipulation practicies.


### Real users presence - Spotting round-size trades

Recently published [research](https://twitter.com/adamscochran/status/1687959096316542976) suggests Huobi's insufficient funds to cover user obligations, prompting extreme actions like wash trading and manipulation to appear financially sound. There are several ways to match real retail users and reported volumes. 

![clustering student test with 100x rounding](img/huobi-investigation/sui-clustering-test-huobi-coinbase.png)
<p style="text-align: center;">Student's clustering test for 100x rounding, sui-usdt spot market, comparison between Huobi and Coinbase, July 2023</p>

Taking into consideration the common practice among retail investors to favor round values for trading, the retail clustering indicator assesses the prevalence of round volumes (e.g., 100, 200) compared to other trade sizes. A higher value of this metric indicates an increased likelihood of actual user involvement. However, in the context of Huobi's data, this metric demonstrates exceptionally low values.


### Huobi Token - Unveiling Huobi's controlled price dynamics

An exchange's native token, like Huobi's HT, serves as an unofficial indicator of its health. As each exchange is particularly interested in boosting an affiliated token to attract more of customers' attention, its price is more likely to be a subject of manipulation.
 

![ht-usdt buy/sell volume ratio comparison](img/huobi-investigation/ht-usdt-buy-sell-volume-multiple-exchange-comparison.jpg)

<p style="text-align: center;">Buy/sell ratio of Huobi Token on Huobi, Poloniex and Gate.io, May - July 2023  </p>

The ratio of "buy" volume and "sell" volume determines price behavior and its furhther movements. In normal conditions this metric is very volatile and looks like a random process (see Gate.io). On the contrary, Huobi Token demonstrates abnormal buy-sell ratio stability that fluctuates within a narrow range.

This suggests potential manipulation, as Huobi may seek to exert control over token price movements. Notably, Huobi's possession of user order data further raises concerns about market manipulation, impacting its users.