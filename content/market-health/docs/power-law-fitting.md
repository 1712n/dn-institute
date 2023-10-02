---
title: "Power Law Fitting"
navShowPages: true
bookToc: true
weight: 40
---

## General Description

[Power Law](https://en.wikipedia.org/wiki/Power_law) Fitting explores the distributions of observed trade sizes in cryptocurrency markets. This methodology seeks to ascertain whether the trade size distributions have fat tails, a characteristic exhibited by power law distributions often observed in traditional financial markets and other economic settings. By determining the values of the exponent α in the fitted results within the Pareto–Lévy range, analysts can glean insights into market behavior and potential manipulation.

## Theory

In economic systems, a power law distribution indicates the presence of extreme events or values, such as massive trades in financial markets. Power law fitting helps in identifying these extreme events and understanding their frequency and impact.

## Mathematical Background

The Power Law is expressed mathematically as:

{{< katex display >}}
P(x) \propto x^{-\alpha}
{{< /katex >}}

Where _α_ is the exponent that often falls within the Pareto–Lévy range in the context of trade size distributions.

## Crypto Context

In cryptocurrency trading, Power Law Fitting assists in the identification and analysis of trade size distributions. The analysis of metrics such as kurtosis, mean, median, mode, skewness, and standard deviation aids in understanding the nature of the trade size distributions and detecting anomalies or manipulative activities.

## Usage Examples

Consider the API metrics:

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
