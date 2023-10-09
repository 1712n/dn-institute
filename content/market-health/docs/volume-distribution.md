---
title: "Volume distribution analysis"
navShowPages: true
bookToc: true
weight: 40
---

## General Description

The trade size distribution is a straightforward way to visually represent the sizes of executed transactions and the number of occurences in a histogram. To gain insights into these distributions and identify any unusual or manipulative activities, various statistical metrics like kurtosis, mean, median, mode, skewness, and standard deviation are analyzed.

Another approach involves using the [power law](https://en.wikipedia.org/wiki/Power_law) to describe a phenomenon where a small number of items are concentrated at the top of a distribution. In simpler terms, this suggests that medium to small retail transactions are frequent, while large "whale" orders are rare. 

The Power Law is expressed mathematically as:

{{< katex display >}}
P(x) \propto x^{-\alpha}
{{< /katex >}}

Where _α_ is the exponent that often falls within the Pareto–Lévy range in the context of trade size distributions.

The power law fitting aims to determine whether trade size distributions exhibit fat tails, a characteristic often observed in traditional financial markets and described by power law distributions.

## Crypto Context

In cases of potential wash trading, certain trading patterns, such as an unusually high volume of trades, may occur more frequently than expected according to the power law distribution. Analysts can identify possible manipulative trading practices by detecting deviations from the anticipated trading patterns outlined by the power law.

## Usage Examples

Consider the API metrics:

- `volume_distribution`: The provided data structure will help building the histogram and conducting the visual analysis. 
- `volume_distribution_kurtosis`: A value of `3.58703` signals a heavy-tailed distribution, indicating a higher likelihood of extreme values.
- `volume_distribution_mean`: A value of `0.38137`, being less than the `volume_distribution_median` of `0.64753`, points to a right-skewed distribution.
- `volume_distribution_skewness`: A value of `1.02254` indicates a moderate positive skewness, meaning more small trades than large ones, but the large trades can be very large.
- `volume_distribution_mode`: A value of `0.39749` highlights that the most frequent trade sizes are relatively small.
- `volume_distribution_std`: A value of `0.31331` implies a moderate level of dispersion around the mean trade size, emphasizing the impact of the fat tails on the overall distribution.

## Visuals

Using visual aids, such as a histogram or a log-log plot, can better illustrate the trade size distribution and its adherence or deviation from the expected power law distribution.

## References and Further Reading

- [Power-law distributions in empirical data](https://epjdatascience.springeropen.com/articles/10.1140/epjds6)
- [A Brief History of Generative Models for Power Law and Lognormal Distributions](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.142.4520&rep=rep1&type=pdf)
- [On the Power Law of Large Numbers](https://arxiv.org/abs/1401.6358)
