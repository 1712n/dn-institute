---
date: 2023-10-02
entities: Huobi, HT, TRX, DOGE
title: Uncovering Wash Trading and Market Manipulation on Huobi 🌱
---

# Uncovering Wash Trading and Market Manipulation on Huobi 🌱

Wash trading is a form of market manipulation where traders create the appearance of market activity by buying and selling the same asset among themselves. This practice can mislead other market participants about the true demand and supply of an asset, potentially influencing prices in a way that benefits the manipulators. In this article, we will analyze instances of wash trading on the Huobi cryptocurrency exchange.

## Introduction 🌱

Huobi is one of the largest cryptocurrency exchanges globally, offering a wide range of trading pairs and services. However, like many exchanges, it has faced allegations of wash trading in the past. In this analysis, we will use data from the [Crypto Market Health API](https://rapidapi.com/DNInstitute/api/crypto-market-health/) to identify and quantify wash trading activities on Huobi.

## Methodology 🌱

To detect wash trading, we will analyze the following metrics:

- **Volume Imbalance**: A significant difference between buy and sell volumes can indicate wash trading.
- **Self-Trade Ratio**: A high ratio of self-trades (trades executed between the same account) can be a red flag.
- **Orderbook Analysis**: Patterns in the orderbook, such as simultaneous large buy and sell orders, can suggest wash trading.

## Analysis 🌱

Using the Crypto Market Health API, we collected data on trading activity on Huobi for the past month. The following sections present our findings.

### Volume Imbalance 🌱

![Volume Imbalance Chart](/assets/images/volume-imbalance-huobi.png)

The chart above shows the volume imbalance on Huobi for the past month. We observe several periods where the volume imbalance is unusually high, which could indicate wash trading.

### Self-Trade Ratio 🌱

![Self-Trade Ratio Chart](/assets/images/self-trade-ratio-huobi.png)

The self-trade ratio on Huobi is also shown in the chart above. A self-trade ratio above 5% is considered suspicious, and we observe several instances where this threshold is exceeded.

### Orderbook Analysis 🌱

![Orderbook Snapshot](/assets/images/orderbook-snapshot-huobi.png)

The orderbook snapshot above shows simultaneous large buy and sell orders for HT, which is a common pattern in wash trading.

## Conclusion 🌱

Our analysis suggests that wash trading is a significant issue on Huobi. The volume imbalance, self-trade ratio, and orderbook patterns all point to suspicious trading activity. Further investigation and regulatory oversight are necessary to address this problem and protect market participants.

## References 🌱

- [Crypto Market Health API Documentation](https://dn.institute/market-health/docs/market-health-metrics/)
- [Market Abuse Centre - Training Courses](https://www.youtube.com/playlist?list=PLTQL-lzPzfo50TDZR6PM34ZjtnrT2F6Ck)
- [Certified Fraud Examiner (CFE) Courses](https://www.udemy.com/topic/certified-fraud-examiner-cfe/)
- [Bitwise Report. Market Manipulation Chapter](https://www.sec.gov/comments/sr-nysearca-2019-01/srnysearca201901-5164833-183434.pdf)
- [Countering Market Abuse. CryptoCompare research](https://assets-global.website-files.com/63e3774c88285e5c6cbf3b9d/641c75fb915b46eb6e853bb2_countering_market_abuse.pdf)