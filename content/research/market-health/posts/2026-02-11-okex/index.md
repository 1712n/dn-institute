---
title: "OKEx: 93% Fabricated Volume, Founder Detention, and Five-Week Withdrawal Freeze"
date: 2026-02-11
entities:
  - OKEx
  - BTC
---

## Summary

1. **93% fabricated volume**: Independent researcher Sylvain Ribes estimated in March 2018 that over 93% of OKEx's reported trading volume was fake, making it the single largest source of fabricated volume among major exchanges at the time.
2. **Not among verified exchanges**: Bitwise Asset Management's March 2019 SEC presentation identified only 10 exchanges with genuine volume. OKEx — despite ranking among the top 3 by reported volume — was not among them.
3. **Founder detained**: In October 2020, OKEx founder Star Xu (Mingxing Xu) was detained by Chinese authorities, triggering an unprecedented five-week withdrawal freeze affecting all users.
4. **922% volume inflation (BTI)**: The Blockchain Transparency Institute's December 2018 report found OKEx inflating volume by 922%, reporting $182 million when estimated true volume was $19.7 million, with all top 30 traded tokens engaging in wash trading.
5. **$504M DOJ penalty**: In February 2025, OKX (rebranded from OKEx) pled guilty to violating U.S. anti-money laundering laws and agreed to pay over $504 million in penalties.

## Background

OKEx was founded in 2017 by Star Xu (Mingxing Xu), a former Yahoo China engineer who had previously founded OKCoin in 2013. Originally launched in Hong Kong, OKEx relocated its headquarters to Malta in 2018 and then to the Seychelles in 2022 as regulatory pressure on cryptocurrency exchanges intensified. The exchange offered spot trading, futures, perpetual swaps, and options across hundreds of trading pairs.

At its peak, OKEx consistently ranked among the top 3 exchanges globally by reported volume on CoinMarketCap. In January 2022, the exchange rebranded to OKX as part of a broader effort to distance itself from its earlier controversies and expand into Web3 services.

## Volume Fabrication Evidence

### Sylvain Ribes Study (March 2018)

In March 2018, independent cryptocurrency researcher Sylvain Ribes published a detailed statistical analysis of exchange volumes that specifically highlighted OKEx as the worst offender among major exchanges [1]:

- OKEx's real volume was estimated at approximately **$7 million** compared to reported volumes exceeding **$100 million** daily
- This represented over **93% fabricated volume**
- The methodology analyzed order book depth and slippage patterns — genuine exchanges showed consistent relationships between order book depth and volume, while OKEx showed extreme divergence
- Ribes noted that OKEx's order books were abnormally thin relative to the reported trading volume, a signature pattern of wash trading where trades are executed between controlled accounts without requiring actual market depth

### Bitwise Asset Management SEC Presentation (March 2019)

Bitwise's analysis for the SEC identified only **10 exchanges** with genuine, verifiable Bitcoin trading volume: Binance, Bitfinex, bitFlyer, Bitstamp, Bittrex, Coinbase Pro, Gemini, itBit, Kraken, and Poloniex [2].

OKEx — which at the time reported among the highest volumes globally — was conspicuously absent from this list. Bitwise's research demonstrated that OKEx exhibited the hallmark patterns of volume fabrication:

- Trade size distributions that deviated from expected power-law patterns
- Volume-to-visitor ratios far exceeding those of verified exchanges
- Suspicious trade timing patterns inconsistent with organic activity

### Blockchain Transparency Institute (December 2018)

BTI's December 2018 report provided specific quantification of OKEx's volume inflation [3]:

- OKEx was found to be **inflating its exchange volume by 922%**, reporting $182,301,294 when estimated true volume was $19,763,245
- **All of OKEx's top 30 traded tokens** were identified as engaging in wash trading
- BTI discovered four distinct bot strategies used by exchanges to inflate volumes, some set to alter volumes depending on the time of day and current market hype
- OKEx was identified as the single biggest offender among major crypto exchanges
- OKEx CEO publicly confronted BTI's findings, calling the allegations "inaccurate and misleading"
- BTI subsequently alleged that OKEx orchestrated a DDoS attack against their website following the report's publication

### The Tie Research

The Tie's social media and web traffic analysis corroborated the volume fabrication findings. Their methodology, which compared reported trading volumes against expected volumes derived from Twitter followers, web traffic, and other engagement metrics, showed OKEx's reported volume significantly exceeded what user activity indicators could support [4].

## Founder Detention and Withdrawal Freeze

### October 2020 Crisis

On October 16, 2020, OKEx suspended all cryptocurrency withdrawals, citing the inability to contact "a certain private key holder" required to authorize transactions [5]:

- OKEx founder **Star Xu was detained** by Chinese police for questioning in connection with an unspecified investigation
- Because Xu held the private keys required for withdrawal authorization, the entire exchange's withdrawal capability was frozen
- The freeze lasted approximately **five weeks**, from October 16 to November 26, 2020
- During this period, users could continue to trade but could not withdraw any assets
- OKB token (the exchange's native token) dropped over 15% immediately following the announcement

### Resolution

- On November 19, 2020, OKEx announced it would resume withdrawals within a week
- Withdrawals officially resumed on November 26, 2020
- Star Xu was reportedly released, though details of the investigation were not publicly disclosed
- The incident exposed critical centralization risks — a single individual's detention rendered the exchange's entire withdrawal infrastructure inoperable

## Regulatory Consequences

### DOJ Guilty Plea and $504M Penalty (February 2025)

In February 2025, OKX (the rebranded OKEx) pled guilty to one count of operating an unlicensed money transmitting business and agreed to pay penalties totaling over $504 million — comprising $420.3 million in criminal forfeiture and $84.4 million in fines [7]:

- OKX knowingly violated anti-money laundering laws for over **seven years**
- The exchange facilitated over **$5 billion** in suspicious transactions and criminal proceeds
- Employees advised U.S. customers to **falsify personal information**, such as inputting random country names and ID numbers to bypass KYC checks
- OKX did not implement commercially available software to monitor suspicious activity until approximately **May 2023**
- The exchange had no controls to determine whether transactions were linked to sanctioned regions

## Market Manipulation Implications

OKEx's case illustrates how volume fabrication persisted even at the highest-profile exchanges:

1. **Scale of deception**: As a consistently top-3 exchange by reported volume, OKEx's fabrication had outsized impact on market-wide volume statistics and CoinMarketCap rankings
2. **Listing fee revenue**: Inflated volume metrics attracted token projects willing to pay listing fees — reportedly $100,000–$1,000,000+ per listing — creating a direct financial incentive for maintaining artificial volume
3. **Derivatives market impact**: OKEx's position as a major futures and perpetual swap venue meant that fabricated spot volumes could distort index prices used for derivatives settlement
4. **Centralization risks**: The withdrawal freeze demonstrated that despite claims of decentralization and institutional-grade infrastructure, critical exchange operations depended on a single individual

## Relevance to Market Health Metrics

OKEx's volume patterns demonstrate several indicators documented in the DN Institute [Market Health Metrics](https://dn.institute/research/market-health/docs/market-health-metrics/) framework:

- **Order book depth divergence**: Abnormally thin order books relative to reported volume — a statistical signature identified by Ribes
- **Volume-traffic divergence**: Reported trading volume vastly exceeded what web traffic and social media metrics could support
- **Cross-validation failure**: Multiple independent analyses (Ribes, Bitwise, BTI, The Tie) all reached the same conclusion — reported volumes were not genuine
- **Centralization risk exposure**: Single points of failure in key management, exposed by the withdrawal freeze, represent operational risks that volume metrics alone do not capture
- **Regulatory vulnerability**: The founder's detention highlighted the exchange's exposure to jurisdictional risks despite nominal headquarters relocation

## References

1. Sylvain Ribes, "Chasing Fake Volume: A Crypto-plague," Medium, March 2018. [medium.com](https://medium.com/@sylvainartplayribes/chasing-fake-volume-a-crypto-plague-ea1a3c1e0b5e)
2. Bitwise Asset Management, "Analysis of Real Bitcoin Trade Volume," Presentation to the U.S. Securities and Exchange Commission, March 2019. [sec.gov](https://www.sec.gov/comments/sr-nysearca-2019-01/srnysearca201901-5164833-183434.pdf)
3. Blockchain Transparency Institute, "Market Surveillance Report," September 2019. [bti.live](https://www.bti.live/reports-april2019/)
4. The Tie, "Exchange Volume Analysis," 2019. [thetie.io](https://thetie.io)
5. Coindesk, "OKEx Suspends Crypto Withdrawals as Founder Reportedly Arrested," October 2020. [coindesk.com](https://www.coindesk.com/markets/2020/10/16/okex-suspends-crypto-withdrawals/)
6. Cointelegraph, "OKEx to Resume Withdrawals After Month-Long Freeze," November 2020. [cointelegraph.com](https://cointelegraph.com/news/okex-to-resume-unrestricted-crypto-withdrawals-on-nov-27)
7. U.S. Department of Justice, "OKX Pleads Guilty To Violating U.S. Anti-Money Laundering Laws," February 2025. [justice.gov](https://www.justice.gov/usao-sdny/pr/okx-pleads-guilty-violating-us-anti-money-laundering-laws-and-agrees-pay-penalties)
8. Cointelegraph, "OKEx Slams New Wash Trading Allegations as 'Inaccurate and Misleading,'" 2018. [cointelegraph.com](https://cointelegraph.com/news/okex-slams-new-wash-trading-allegations-as-inaccurate-and-misleading)
