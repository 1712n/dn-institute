---
title: Market health metrics
bookToc: true
---

Indicator | Description | API metric
-- | -- | --
Volume-volatility correlation | Trading volumes usually spike when volatility in markets rise. Normally, high values of this metric indicate healthy market behavior. | `volume_volatility_correlation`
Benford's Law | The first significant digit distribution tends to fit Benford’s law for traditional financial markets and regulated exchanges. High deviation from this law may indicate potential anomalies, manipulation, or fraudulent activities in the market. | `first_digit_distribution`
Power law fitting | Power law appears to describe histograms of trading volume. The power laws observed in financial data arises when the trading behavior is performed in an optimal way. High values for this metric can indicate abnormal interest or attempts at market manipulation. | `volume_distribution_kurtosis`<br>`volume_distribution_mean`<br>`volume_distribution_median`<br>`volumedistribution_mode`<br>`volume_distribution_mode`<br>`volume_distribution_skewness`<br>`volume_distribution_std`
Time-of-trade | This indicator identifies abnormal accumulation of scheduled trades executed at the same time - minute/second. | `count_time_distribution`
Buy/sell ratio | Depending on whether the order taker is a buyer or seller, each trade is associated with a specific side of the trade. A consistent and large number of trades on one side of the book is a pattern that may signal automated activity. | `buy_sell_count_ratio`
VWAP | Volume weighted average price | `vwap`

## Market Health Metrics Documentation

This documentation provides a guide on how to use and interpret market surveillance statistical metrics from the API to identify anomalies and manipulations on cryptocurrency exchanges.

### 1. **Volume-Volatility Correlation**

- **Description**: Measures the relationship between trading volume and market volatility. 
- **API Metric**: `volume_volatility_correlation`
- **How to Interpret**:
  - **Example Value**: `0.52781`
  - Trading volumes typically spike when volatility in markets rise, i.e. a value close to 1 indicates a strong positive correlation, signaling healthy market behavior. A value near -1 may indicate potential market manipulation.
  - In this case, a moderate positive correlation is observed.

### 2. **Benford's Law**

- **Description**: Evaluates the first digit distribution to detect anomalies or potential market manipulation.
- **API Metric**: `first_digit_distribution`
- **Example Array Data**: `[0, 636, 238, 489, 343, 148, 189, 75, 90, 125]`
- **How to Interpret**:
  - According to [Benford's Law](https://en.wikipedia.org/wiki/Benford%27s_law), we expect more numbers to start with 1 (about 30%), followed by 2 (about 18%), and so on, in decreasing order.
  - In the provided data example, the second value (representing the digit 1) is the highest, which is expected. However, the value for digit 3 is unexpectedly high compared to digit 2, which might need further investigation.
- **Reference**: [Testing Benford's Law](https://testingbenfordslaw.com/)

### 3. **Power Law Fitting**

- **Description**: Explores whether the distributions of observed trade size have fat tails characterized by the power law as seen in traditional financial markets and other economic settings; values of exponent α in the fitted results fall within the Pareto–Lévy range.
- **API Metrics**:
  - `volume_distribution_kurtosis`
  - `volume_distribution_mean`
  - `volume_distribution_median`
  - `volume_distribution_mode`
  - `volume_distribution_skewness`
  - `volume_distribution_std`
- **How to interpret**:
  - For a proper analysis of the Power Law Fitting, it is essential to visualize the distribution, fit the power-law model, and compute goodness-of-fit metrics. Such analysis cannot be fully performed without additional tools.
  - `volume_distribution_kurtosis`: Higher values (>3) indicate abnormal interest or attempts at market manipulation. The value of `3.58703` indicates a heavy-tailed distribution, as it's greater than `3`, signaling a higher likelihood of extreme values, which is characteristic of power-law distributions. 
  - The `volume_distribution_mean` of `0.38137` being less than the `volume_distribution_median` of `0.64753` suggests that the distribution is skewed to the right. This is further confirmed by a `volume_distribution_skewness` value of `1.02254`, indicating a moderate positive skewness. This means that there are more small trades than large ones, but the large trades can be very large.
  - The `volume_distribution_mode` of `0.39749` further supports this, indicating that the most frequent trade sizes are relatively small.
  - The `volume_distribution_std` value of `0.31331` implies a moderate level of dispersion around the mean trade size. In the context of power-law distribution, this further emphasizes the impact of the fat tails on the overall distribution, showing that there can be substantial variation in trade sizes, including the presence of extreme values.

- **Reference**: [Power-law distributions in empirical data](https://arxiv.org/abs/0706.1062)

### 4. **Time-of-Trade**

- **Description**: Identifies abnormal accumulation of scheduled trades executed at the same time - minute/second. This accumulation of trades indicate bot activity and can be an indication of wash trading.
- **API Metric**: `count_time_distribution`
- **Array Data**: `[7, 0, 14, ..., 9, 6, 19]`
- **How to Interpret**:
  - A comparatively big count in a specific time slot, such as `217`, could suggest abnormal trading activity during that period and should be further investigated on larger time windows.

### 5. **Buy/Sell Ratio**

- **Description**: Analyzes the proportion of buy to sell orders to detect automated trading.
- **API Metric**: `buy_sell_count_ratio`
- **Example Value**: `0.367`
- **How to Interpret**:
  - Values significantly higher or lower than 0.5 may suggest biased trading activity.
  - The given value slightly lower than 0.5, indicating a bias towards sell orders.

### 6. **VWAP (Volume Weighted Average Price)**

- **Description**: Represents the average price based on trading volume.
- **API Metric**: `vwap`
- **Value**: `1624.164163150681200000`
- **How to Interpret**:
  - A significant difference between the VWAP and the current price may indicate manipulation.
  - Monitor the VWAP value in relation to the current price for potential anomalies.

### Summary:

Each metric provides insights into different aspects of market behavior:

- **Volume-Volatility Correlation**: Observes volume and volatility relationships.
- **Benford’s Law**: Checks first digit distribution for conformity with expected patterns.
- **Power Law Fitting**: Analyzes trading volume histograms for abnormal behavior.
- **Time-of-Trade**: Monitors time slots for unexpected trade accumulations.
- **Buy/Sell Ratio**: Evaluates order book balance to spot potential automated trading.
- **VWAP**: Watches average price and volume to identify significant price deviations.

By analyzing these metrics in conjunction and investigating unusual patterns or values, users can more effectively spot potential market anomalies or manipulative activities. Further analysis with statistical software and visualization tools is recommended for more accurate assessments and insights.