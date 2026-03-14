---
date: 2023-10-02
entities: Huobi, HT, TRX, DOGE
title: Uncovering Wash Trading and Market Manipulation on Huobi 🌱
---

# Uncovering Wash Trading and Market Manipulation on Huobi 🌱

Wash trading is a form of market manipulation where traders create the appearance of market activity by buying and selling the same asset among themselves. This practice can mislead other market participants about the true demand and supply of an asset, potentially influencing prices in a way that benefits the manipulators. In this article, we will analyze instances of wash trading on the Huobi cryptocurrency exchange.

## Introduction 🌱

Huobi is one of the largest cryptocurrency exchanges globally, offering a wide range of trading pairs and services. However, like many exchanges, it has faced allegations of wash trading. In this analysis, we will use data from the [Crypto Market Health API](https://rapidapi.com/DNInstitute/api/crypto-market-health/) to identify and quantify wash trading activities on Huobi.

## Methodology 🌱

To detect wash trading, we analyzed the order book snapshots and executed order feeds provided by the Crypto Market Health API. Specifically, we looked for patterns where large volumes of trades occurred between two or more accounts with no net change in the overall market position.

## Findings 🌱

Our analysis revealed several instances of wash trading on Huobi, particularly involving the HT, TRX, and DOGE trading pairs. Here are some key findings:

- **High Frequency of Self-Trades:** We observed a significant number of self-trades, where the same account placed both buy and sell orders at nearly the same time.
- **No Net Volume Change:** Despite the high volume of trades, there was no corresponding change in the overall market position, indicating that these trades were likely wash trades.
- **Pattern Recognition:** We identified specific patterns in the order book snapshots that were indicative of wash trading activities.

## Visualizations 🌱

![Wash Trading Pattern on Huobi](/assets/images/wash-trading-huobi.png)

## Conclusion 🌱

Our analysis provides evidence of wash trading activities on the Huobi cryptocurrency exchange. These findings highlight the importance of robust monitoring and regulatory measures to prevent market manipulation and protect investors.

## References 🌱

- [Crypto Market Health API Documentation](https://dn.institute/market-health/docs/market-health-metrics/)
- [Market Abuse Centre - Training Courses](https://www.youtube.com/playlist?list=PLTQL-lzPzfo50TDZR6PM34ZjtnrT2F6Ck)
- [Certified Fraud Examiner (CFE) Courses](https://www.udemy.com/topic/certified-fraud-examiner-cfe/)
- [Bitwise Report. Market Manipulation Chapter](https://www.sec.gov/comments/sr-nysearca-2019-01/srnysearca201901-5164833-183434.pdf)
- [Countering Market Abuse. CryptoCompare research](https://assets-global.website-files.com/63e3774c88285e5c6cbf3b9d/641c75fb915b46eb6e853bb2_countering_market_abuse.pdf)

## Images 🌱

![Wash Trading Pattern on Huobi](/assets/images/wash-trading-huobi.png)

*Figure 1: Example of a wash trading pattern detected on Huobi.*

## Datasets 🌱

- [Huobi Order Book Snapshots](/datasets/huobi-order-book-snapshots.csv)
- [Huobi Executed Order Feeds](/datasets/huobi-executed-order-feeds.csv)

*Note: Datasets are available upon request and may be subject to licensing restrictions.*