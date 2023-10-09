---
title: "Benford's Law"
bookToc: true
weight: 30
---

## General Description

[Benford's Law](https://en.wikipedia.org/wiki/Benford%27s_law), or the First-Digit Law, is a principle used to evaluate the first digit distribution in sets of numerical data. Benford's Law asserts that in many naturally occurring datasets, the first digit is likely to be small. For example, the number 1 appears as the leading digit about 30% of the time, while 9 appears as the leading digit less than 5% of the time.

It is frequently employed in [accounting as a forensic tool](https://www.aabri.com/manuscripts/121125.pdf) to detect anomalies or potential fraud in financial statements, for example, by analyzing the frequency distribution of the first digits of the numbers in corporate expenses. In the infamous [Enron scandal](https://www.investopedia.com/updates/enron-scandal-summary/), where manipulated accounting practices were utilized to conceal debt and inflate profits, analysts and forensic accountants could employ Benford's Law to scrutinize the financial statements. 


## Mathematical Background

The following formula can be used to calculate the expected frequency of a given leading digit d in a data set that follows Benford's law:

{{< katex display >}}
P(d) = \log_{10} \left( 1 + \frac{1}{d} \right)
{{< /katex >}}
where _P(d)_ is the probability that the leading digit of a number in the data set will be _d_.

For example, to calculate the expected frequency of the leading digit 1, we would substitute _d=1_ into the formula:

{{< katex display >}}
P(1) = \log_{10} \left( 1 + \frac{1}{1} \right) = \log_{10} (2) = 0.301
{{< /katex >}}

This means that we expect the leading digit 1 to appear in about 30% of the numbers in a data set that follows Benford's law. This formula can be used to generate a table of the expected frequencies of the leading digits in a data set that follows Benford's law:

Leading digit | Expected frequency
------- | --------
1 | 0.301
2 | 0.176
3 | 0.125
4 | 0.097
5 | 0.079
6 | 0.067
7 | 0.058
8 | 0.051
9 | 0.046

## Crypto Context

In the context of cryptocurrency trading, adherence to Benford's Law can be used to scrutinize trading data for inconsistencies or abnormalities. Non-conformity to the expected digit distribution could suggest manipulation, such as wash trading or massive sell-offs, warranting further investigation.

## Usage Examples

Consider the given **Example Array Data: `[0, 636, 238, 489, 343, 148, 189, 75, 90, 125]`**. Each element of the array corresponds to the number of the occurrences of digits. 

The second value, representing the digit 1, is the highest (636 occurrences), aligning with Benford’s Law. However, the value for digit 3 (489 occurrences) is unexpectedly high compared to digit 2 (238 occurrences), which can be a red flag for potential data manipulation or anomalies. Use the percentage to conduct the hypothesis testing and the deviation estimation. 

## Visuals

Visual aids, such as a bar graph representing the expected and actual frequency distribution of leading digits, can help in better visualizing the adherence or deviation from Benford’s Law.

## References and Further Reading

- [Testing Benford's Law](https://testingbenfordslaw.com/)
- [Benford’s Law and The Detection of Election Fraud](https://www.cambridge.org/core/journals/political-analysis/article/abs/benfords-law-and-the-detection-of-election-fraud/3B1D64E822371C461AF3C61CE91AAF6D)
- [Crypto Wash Trading by LW Cong et al. (2021)](https://arxiv.org/pdf/2108.10984.pdf)
