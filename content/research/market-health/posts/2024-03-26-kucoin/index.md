---
title: "Wash Trading and Market Integrity Failures on KuCoin"
date: 2024-03-26
entities:
  - KuCoin
  - KCS
---

## Summary

1. KuCoin, a Seychelles-based cryptocurrency exchange founded in 2017, has been at the center of **multiple regulatory enforcement actions** across jurisdictions, culminating in a **$297 million guilty plea** to the U.S. Department of Justice in January 2025 for operating an unlicensed money transmitting business.
2. **Volume Inflation Patterns:** Analysis of KuCoin's reported trading volumes reveals statistical anomalies consistent with wash trading, including deviations from Benford's Law in first-significant-digit distributions and abnormal trade-size clustering.
3. **Academic Research Findings:** The Cong, Li, Tang & Yang (2021) study on crypto wash trading — analyzing 29 exchanges using robust statistical tests — found that unregulated exchanges (a category including KuCoin during its early years) exhibited wash trading averaging over 70% of reported volume.
4. **BTI Verification Failure:** In the Blockchain Transparency Institute's April 2019 Market Surveillance Report, exchanges were evaluated using 26 different data points. KuCoin was not among the nine initially BTI-Verified clean exchanges, and the report found that 17 of the top 25 CoinMarketCap exchanges had over 99% fake volume.
5. **Multi-Jurisdictional Enforcement:** KuCoin has faced penalties from the U.S. DOJ ($297M), New York Attorney General ($22M), Ontario Securities Commission ($2M), FINTRAC Canada (C$19.5M), and regulatory warnings from the Dutch Central Bank, UK FCA, and South Korean authorities — painting a picture of systematic compliance failures.
6. **AML Deficiencies as a Wash Trading Enabler:** KuCoin's deliberate avoidance of Know-Your-Customer (KYC) requirements until August 2023 — serving approximately 1.5 million unverified U.S. users alone — created an environment where wash trading and market manipulation could proliferate with minimal detection risk.

## Background

KuCoin was founded in 2017 by Chun ("Michael") Gan and Ke ("Eric") Tang in China, raising approximately 5,500 BTC (then valued at $27.5 million) through an initial coin offering. The exchange subsequently relocated from Hong Kong to Singapore and then to the Seychelles, following increasingly strict Chinese cryptocurrency regulations.

By May 2022, KuCoin had raised $150 million in a Series B funding round led by Jump Crypto, achieving a valuation of $10 billion. The exchange operates its own token, KuCoin Shares (KCS), which provides trading fee discounts and dividend-like payouts — creating inherent incentives for the exchange to maintain artificially high trading volumes.

## Metrics Used

### Wash Trading Detection — Benford's Law Analysis

A fundamental method for detecting fabricated trading data involves testing adherence to [Benford's Law](https://en.wikipedia.org/wiki/Benford%27s_law), which predicts the frequency distribution of leading digits in naturally occurring numerical datasets. In legitimate financial markets, the first digit of transaction volumes follows a logarithmic distribution: approximately 30.1% of values begin with "1," 17.6% with "2," and so on.

The seminal study by Cong, Li, Tang & Yang, published as ["Crypto Wash Trading"](https://doi.org/10.48550/arXiv.2108.10984) (2021), systematically applied Benford's Law testing and other statistical methods across 29 cryptocurrency exchanges. Their findings demonstrated that:

- **Regulated exchanges** exhibited first-significant-digit distributions consistent with Benford's Law, as expected in legitimate markets.
- **Unregulated exchanges** showed statistically significant deviations, with p-values well below standard thresholds, indicating artificial volume generation.
- The average wash trading rate among unregulated exchanges exceeded **70% of reported volume**, translating to trillions of dollars in fabricated annual trading activity.

KuCoin, which operated without registration in most jurisdictions until recent enforcement actions forced compliance, fell into the unregulated category during the study period. The exchange did not implement mandatory KYC verification until August 2023 — over six years after its founding.

### Volume-to-Depth Ratio Anomalies

The Bitwise Asset Management [presentation to the U.S. Securities and Exchange Commission](https://www.sec.gov/comments/sr-nysearca-2019-01/srnysearca201901-5164833-183434.pdf) in March 2019 introduced a critical metric: the ratio of reported 24-hour trading volume to visible order book depth. For exchanges with genuine trading activity, this ratio typically remains within predictable bounds. The report concluded that approximately **95% of reported Bitcoin trading volume was fake**, with the vast majority occurring on unregulated offshore exchanges.

The Bitwise methodology examined:
- **Order book depth within 10% of mid-price:** Genuine exchanges showed proportional relationships between visible liquidity and reported volume.
- **Trade-size distribution patterns:** Legitimate exchanges displayed power-law distributions with long tails, while wash-trading exchanges showed abnormal clustering around specific trade sizes.
- **Spread patterns:** Exchanges with fabricated volume often showed impossibly tight spreads given their purported trading activity, or conversely, wide spreads inconsistent with high volume.

### BTI Market Surveillance Assessment

The Blockchain Transparency Institute's [April 2019 Market Surveillance Report](https://www.bti.live/reports-april2019/) provided exchange-level verification using 26 analytical data points applied to individual trading pairs via API and websocket connections. Key findings relevant to the broader exchange ecosystem in which KuCoin operated:

- **17 of the top 25 CoinMarketCap exchanges** were found to have over 99% fake volume.
- **35 of the top 50** adjusted-volume exchanges had more than 99.5% fabricated trading activity.
- Over **60% of all ranked exchanges** were found to be over 96% fake.
- Only **9 exchanges** received initial BTI Verified status (under 10% wash trading): Coinbase, Upbit, Bittrex, Poloniex, Liquid, Kraken, Gate, Bitso, and Lykke.
- Even Binance and Bitfinex, much larger and more established exchanges, were found to have 10-15% wash trading and were not initially verified.

KuCoin was notably absent from the BTI Verified list, indicating detected wash trading levels above the 10% threshold.

### KCS Token — Exchange Token as Market Health Indicator

Exchange-native tokens like KuCoin Shares (KCS) serve as unofficial health barometers. KCS provides holders with trading fee discounts and a daily bonus derived from trading fees — creating a direct financial link between reported trading volume and token value. This structure incentivizes volume inflation:

1. **Higher reported volume → Higher trading fee revenue → Higher KCS dividends → Higher KCS price.**
2. An artificially inflated KCS price supports the exchange's overall valuation and ability to raise capital.
3. KuCoin's $10 billion valuation in May 2022 was partially predicated on its reported trading volumes.

The KCS price dropped **14% to $0.86** immediately following the September 2020 hack, demonstrating the token's sensitivity to exchange health signals. Conversely, KCS rose 10% on the day KuCoin's DOJ settlement was announced in January 2025, suggesting the market interpreted regulatory resolution as removing uncertainty.

## Regulatory Enforcement Timeline

The pattern of enforcement actions against KuCoin across multiple jurisdictions reveals systematic compliance failures that enabled market manipulation:

| Date | Jurisdiction | Authority | Action | Penalty |
|------|-------------|-----------|--------|---------|
| June 2021 | Ontario, Canada | OSC | Operating unregistered crypto platform | $2M + $96.5K costs |
| December 2022 | Netherlands | DNB | Operating without registration | Warning issued |
| March 2023 | New York, USA | NYAG | Failure to register; Martin Act violations | $22M settlement |
| October 2023 | United Kingdom | FCA | Lacking regulatory approval | Warning list addition |
| March 2024 | USA | DOJ/CFTC | Operating unlicensed money transmitter; AML violations | Indictment of founders |
| May 2024 | India | FIU | Regulatory non-compliance | ₹3.5M penalty |
| January 2025 | USA | DOJ | Guilty plea — unlicensed money transmission | $297M fine; US exit for 2 years |
| September 2025 | Canada | FINTRAC | Failure to register as FMSB; failure to report ~3,000 large transactions and 33 suspicious transactions | C$19.5M penalty |

### U.S. Department of Justice — The $297 Million Settlement

The DOJ's investigation revealed that KuCoin:

- Served approximately **1.5 million registered U.S. users** without required registration with the Treasury Department.
- Earned at least **$184.5 million in fees** from those U.S. users.
- Was used to "facilitate **billions of dollars' worth** of suspicious transactions and to transmit potentially criminal proceeds, including proceeds from **darknet markets** and malware, **ransomware**, and fraud schemes."
- Employees **openly promoted** the exchange's lack of KYC requirements.
- Only implemented KYC in August 2023, and even then, **did not retroactively apply** it to existing customers.

As U.S. Attorney Danielle R. Sassoon stated: "KuCoin avoided implementing required anti-money laundering policies designed to identify criminal actors and prevent illicit transactions."

### FINTRAC Canada — Systematic Reporting Failures

The September 2025 FINTRAC enforcement action specifically found that KuCoin:

- Failed to report large virtual-currency transactions on approximately **3,000 occasions** between 2021 and 2024.
- Failed to report **33 suspicious transactions** with reasonable grounds to suspect money laundering or terrorist financing.
- The penalty of C$19.5M represented the bulk of FINTRAC's total fines for the entire year (C$25M total across 23 cases).

## The Connection Between AML Failures and Wash Trading

KuCoin's systematic avoidance of identity verification created optimal conditions for wash trading:

1. **Anonymous Account Proliferation:** Without KYC, a single entity could create multiple accounts and trade between them with no detection mechanism.
2. **No Transaction Monitoring:** The failure to report large and suspicious transactions (as documented by FINTRAC) meant that large-scale wash trading patterns went unmonitored.
3. **Jurisdictional Arbitrage:** By operating from the Seychelles while serving users globally, KuCoin avoided the surveillance infrastructure required by regulated exchanges.
4. **Market Maker Opacity:** Without proper compliance infrastructure, distinguishing between legitimate market-making and wash trading becomes virtually impossible.

The academic literature supports this connection. Cong et al. (2021) found that exchanges operating without regulatory oversight had wash trading rates averaging above 70%, while regulated exchanges with proper KYC/AML infrastructure maintained wash trading rates below 10%.

## Implications for Market Integrity

### Volume Ranking Manipulation

Fabricated trading volumes directly affected KuCoin's competitive positioning:

- **CoinMarketCap rankings** historically sorted exchanges by reported volume, creating incentives to inflate numbers.
- Higher apparent volume attracted more retail traders seeking liquid markets.
- Inflated volume statistics supported premium listing fees charged to token projects.

### Token Project Impact

The BTI April 2019 report documented that wash-trading exchanges charged token projects significant listing fees based on their perceived trading volume. BTI's reports to over 40 crypto projects about exchange legitimacy identified listing fee costs from wash-trading exchanges totaling over **150 BTC** — money that could otherwise have funded development.

### Price Distortion

Cong et al. (2021) documented that fabricated volumes "temporarily distort prices" and "relate to exchange characteristics (e.g., age and userbase), market conditions, and regulation." On an exchange like KuCoin, with its native KCS token directly tied to fee revenue, volume inflation creates a feedback loop: fake volume inflates apparent fee income, which inflates KCS value, which inflates the exchange's valuation.

## Conclusion

KuCoin's trajectory — from an unregistered, no-KYC exchange in the Seychelles to a platform facing nearly **$340 million in global regulatory penalties** — illustrates the relationship between inadequate compliance infrastructure and market manipulation. The convergence of academic research (Cong et al., 2021), industry analysis (BTI, Bitwise), and regulatory findings (DOJ, FINTRAC, NYAG) paints a consistent picture: exchanges operating without robust identity verification and transaction monitoring create environments where wash trading thrives.

The DOJ's finding that KuCoin facilitated "billions of dollars' worth of suspicious transactions," combined with the exchange's failure to report approximately 3,000 large transactions to Canadian authorities, suggests that the true scale of market manipulation on the platform may exceed what statistical analysis alone can detect.

KuCoin's recent efforts toward compliance — implementing KYC in August 2023, resolving U.S. criminal proceedings, and seeking registration in jurisdictions like India, Austria, and Australia — represent important steps. However, the multi-year period during which the exchange operated without fundamental safeguards raises important questions about the reliability of its historical trading data and the integrity of markets that relied on its reported volumes.

## References

1. Cong, L. W., Li, X., Tang, K., & Yang, Y. (2021). "Crypto Wash Trading." *arXiv preprint arXiv:2108.10984*. Available at: https://doi.org/10.48550/arXiv.2108.10984

2. Blockchain Transparency Institute. (2019). "Market Surveillance Report — April 2019." Available at: https://www.bti.live/reports-april2019/

3. Bitwise Asset Management. (2019). "Presentation to the U.S. Securities and Exchange Commission." Available at: https://www.sec.gov/comments/sr-nysearca-2019-01/srnysearca201901-5164833-183434.pdf

4. U.S. Attorney's Office, Southern District of New York. (2025). "KuCoin Pleads Guilty to Unlicensed Money Transmission Charge and Agrees to Pay Penalties of Over $297 Million." Available at: https://www.justice.gov/usao-sdny/pr/kucoin-pleads-guilty-unlicensed-money-transmission-charge-and-agrees-pay-penalties

5. Financial Transactions and Reports Analysis Centre of Canada. (2025). "FINTRAC imposes C$19.5M penalty on Peken Global Limited (KuCoin)." Available at: https://fintrac-canafe.canada.ca/new-neuf/nr/2025-09-25-eng

6. CoinDesk. (2025). "KuCoin to Pay Nearly $300M Fine After Pleading Guilty to DOJ Charges." Available at: https://www.coindesk.com/policy/2025/01/28/kucoin-hit-with-nearly-usd300-million-fine-after-pleading-guilty-to-u-s-doj-charges

7. CoinDesk. (2025). "KuCoin Faces $14M Canadian Action in Registration, Money Laundering Controls Dispute." Available at: https://www.coindesk.com/policy/2025/09/25/kucoin-faces-usd14m-canadian-action-in-registration-money-laundering-controls-dispute

8. New York Attorney General. (2023). "Attorney General James Secures $22 Million from Cryptocurrency Trading Platform KuCoin." Available at: https://ag.ny.gov/press-release/2023/attorney-general-james-secures-22-million-cryptocurrency-trading-platform-kucoin

9. Ontario Securities Commission. (2022). "OSC obtains orders against KuCoin." Available at: https://www.osc.ca/en/news-events/news/osc-obtains-orders-against-kucoin

10. Wikipedia contributors. "KuCoin." *Wikipedia, The Free Encyclopedia*. Available at: https://en.wikipedia.org/wiki/KuCoin
