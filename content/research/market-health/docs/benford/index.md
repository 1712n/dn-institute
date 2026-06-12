---
title: "Benford's Law"
bookToc: true
weight: 30
---

## Benford's Law

[Benford's Law](https://en.wikipedia.org/wiki/Benford%27s_law), or the First-Digit Law, is a principle used to evaluate the first digit distribution in sets of numerical data. Benford's Law asserts that in many naturally occurring datasets, the first digit is likely to be small. For example, the number 1 appears as the leading digit about 30% of the time, while 9 appears as the leading digit less than 5% of the time. In the context of cryptocurrency trading, adherence to Benford's Law can be used to scrutinize trading data for inconsistencies or abnormalities. 

### Mathematical Background

Benford's Law probabilities can be calculated using: 

{{< katex display >}}
P(d) = log_{10}(1 + \frac{1}{d})
{{< /katex >}}

Where d is the digit and P(d) is probability of d being the first digit.

 This formula can be used to generate a table of the expected frequencies of the leading digits in a data set that follows Benford's law:

Leading digit | Expected frequency
------- | --------
1 | 30.1% 
2 | 17.6%
3 | 12.5%
4 | 9.7%
5 | 7.9%
6 | 6.7% 
7 | 5.8%
8 | 5.1%
9 | 4.6%

### Metrics in the API Response

`firstdigitdist`: This metric represents the distribution of the first digits across the given dataset. It returns an object with the digit (1-9) as keys and the count of occurrences as values. This distribution is then compared against the expected distribution as per Benford's Law to detect anomalies.

`benfordlawtest`: This metric is the Kolmogorov-Smirnov (K-S) test statistic, which measures the maximum distance between the observed first-digit distribution and the expected distribution under Benford's Law. At the 5% significance level, compare the statistic with the critical value:

{{< katex display >}}
\text{critical value} = \frac{1.36}{\sqrt{\text{tradecount}}}
{{< /katex >}}

- If `benfordlawtest` is greater than the critical value, reject the null hypothesis that the data conforms to Benford's Law.
- If `benfordlawtest` is less than or equal to the critical value, there is insufficient evidence to reject the null hypothesis.

A statistically significant deviation does not by itself prove manipulation. Sample size, market structure, and whether Benford's assumptions are appropriate for the selected data must also be considered.

#### Example

```json
 {
        "timestamp": "2023-12-25T18:59:00.000Z",
        "marketvenueid": "okx",
        "pairid": "doge-usdt",
        "firstdigitdist": {
            "1": 8,
            "2": 6,
            "3": 7,
            "4": 2,
            "5": 2,
            "6": 1,
            "7": 2,
            "8": 3,
            "9": 3
        },
        "benfordlawtest": 0.0809
    }
    
```    

### Usage Example

The market surveillance data was analyzed for a 3 hour period on market `okx-doge-usdt`. The analysis focused on the `firstdigitdist` and `benfordlawtest` metrics.

Steps taken:

1. Aggregated the first digit frequencies from all records.
2. Compared the actual distribution with the expected Benford's Law distribution.
3. Evaluated the data's conformity to Benford's Law through the 'benfordlawtest' metric.
4. Interpreted the results.

Initial aggregation of first digit frequencies provided a foundational understanding of the distribution. The expected frequencies were then calculated based on Benford's Law, omitting the detailed formula here. A comparative analysis between expected and observed distributions was conducted, highlighting discrepancies.

| Digit | Expected Count (Benford's Law) | Observed Count |
|-------|--------------------------------|----------------|
| 1     | 1398                           | 1207           |
| 2     | 818                            | 981            |
| 3     | 580                            | 464            |
| 4     | 450                            | 455            |
| 5     | 368                            | 366            |
| 6     | 311                            | 277            |
| 7     | 269                            | 269            |
| 8     | 238                            | 175            |
| 9     | 213                            | 450            |

The average 'benfordlawtest' value across the data is approximately 0.208.

#### Interpretation

1. **First Digit Distribution:**
   - The digit '1' appears less frequently than expected, while '2' and '9' appear more frequently than expected according to Benford's Law.
   - Digits '3', '5', '6', '7', and '8' all show fewer occurrences than expected, with '8' having a notably lower frequency.
   - The digits '4' and '7' are quite close to their expected frequencies.

2. **Benford's Law Test:**
   - The reported average `benfordlawtest` value of approximately 0.208 should not be interpreted on its own. For each time window, compare the K-S statistic with `1.36 / sqrt(tradecount)` using that window's corresponding trade count.
   - Averaging K-S statistics across windows with different sample sizes obscures the relevant critical-value comparison. Inspect each window-level statistic and threshold instead.

#### Possible Reasons and Implications
- **Natural Variability:** Not all datasets strictly follow Benford's Law, especially if they are not large enough or don't cover a wide enough range of magnitudes.
- **Specific Domain Characteristics:** The nature of the data (financial market data in this case) might have inherent characteristics that cause deviations. For example, certain price ranges might be more common due to psychological pricing or market regulations.
- **Data Manipulation:** Significant deviations from Benford's Law are sometimes indicators of fabricated or manipulated data. However, this would require further investigation and domain-specific analysis to substantiate.

In conclusion, while Benford's Law provides an insightful tool for analyzing market data, it should be used in conjunction with other analysis methods to comprehensively understand market behavior and potential anomalies.

#### Visuals

Visual aids, such as a bar graph representing the expected and actual frequency distribution of leading digits, can help in better visualizing the adherence or deviation from Benford’s Law.

{{< figure src="benford.png" >}}

### Applications in Market Surveillance
- **Detecting Potential Manipulation**: Test values above their sample-size-dependent critical values indicate statistically significant deviations that may require further investigation. However, natural deviations can occur.
- **Identifying Suspicious Patterns**: Unusual first digit frequencies appearing concurrently across exchanges could indicate coordinated manipulation efforts. 
- **Combining With Other Metrics**: Benford's Law is best used alongside other metrics like volume, volatility, orders to substantiate manipulation hypotheses.
- **Establishing Expected Ranges**: Calculate historical test value ranges for a trading pair to better detect anomaly deviations.

### Considerations for Cryptocurrencies

- Market dynamics like high frequency algorithmic trading can naturally distort distributions.
- Psychologic price thresholds and market-specific regulations can influence numbers.
- Different cryptocurrencies demonstrate varying levels of adherence. 

### Key Takeaways

- Benford's Law analyzes if data conforms to expected first digit distribution.
- Deviations may indicate potential manipulation but require further substantiation.
- Naturally occurring distortions are possible.
- Works best with other metrics for robust surveillance.

## References and Further Reading

- [Testing Benford's Law](https://testingbenfordslaw.com/)
- [Benford’s Law and The Detection of Election Fraud](https://www.cambridge.org/core/journals/political-analysis/article/abs/benfords-law-and-the-detection-of-election-fraud/3B1D64E822371C461AF3C61CE91AAF6D)
- [Crypto Wash Trading by LW Cong et al. (2021)](https://arxiv.org/pdf/2108.10984.pdf)
