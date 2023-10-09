---
title: "Buy/Sell Ratio"
navShowPages: true
bookToc: true
weight: 60
---

## General Description

The Buy/Sell Ratio is an important metric used in trading analysis for various markets, including cryptocurrencies. It calculates the proportion of buy to sell orders in a given time period to determine the market’s sentiment. A balanced market generally observes a buy/sell ratio around 0.4-0.6, representing equivalent buy and sell activity.

Ratios significantly deviating from equilibrium time can hint at a market bias towards buying or selling, which may be caused by various factors, including automated trading systems that attempt to manipulate the market. However, an absence of any fluctuation of this metric and steady 0.5 value even for liquid market pairs is suspecious.

## Formula

{{< katex display >}}
{buy/sell~ratio} = \frac{n}{m},
{{< /katex >}}

where
{{< katex display >}}
n = \sum(volume_{id}) \text{ if } side_{id} = \text{buy}, m = \sum(volume_{id})
{{< /katex >}}

## Crypto Context

In cryptocurrency markets, where large volumes of trades are executed continuously, monitoring the Buy/Sell Ratio is crucial. Depending on the market context, both irregular and steady fluctuations in this ratio can be indicative of automated trading systems operating to influence the market.

## Usage Examples

Consider the API metric:

- `buy_sell_count_ratio`: An example value of `0.367` is provided. This number is lower than 0.5, showing a tilt towards sell orders. While not extremely far from the balanced point, continuous monitoring is necessary to ascertain if this is a trend or a one-time observation.

### How to Interpret

- A Buy/Sell Ratio significantly higher than 0.5 suggests a market bias towards buying. Such a scenario could lead to a price increase.
- A Buy/Sell Ratio significantly lower than 0.5 indicates a market bias towards selling, possibly leading to a price decrease.
- The example value of `0.367` suggests a moderate bias towards selling. It is crucial to observe this over time to ascertain if this is a consistent pattern or a brief occurrence.
- Use cross-exchange analysis to spot opposite Buy/Sell Ratio deviations of the same trading pair on different market venues.

## Visuals

Using line or bar graphs to plot the Buy/Sell Ratio over time can provide visual insights into market trends and potential manipulation. Sudden and unexplained spikes or drops in the ratio should be investigated further.

## References and Further Reading

- [Buy/Sell Ratio As a Predictor of Market Returns](https://www.aaii.com/journal/article/buy-sell-ratio-as-a-predictor-of-market-returns)
- [Analyzing Market Sentiment with the Put/Call Ratio](https://www.investopedia.com/articles/active-trading/051215/analyzing-market-sentiment-putcall-ratio.asp)
