---
title: "BitForex: Systematic Wash Trading and the $56.5 Million Exit Scam"
date: 2024-02-23
entities:
  - BitForex
  - BF Token
  - OMI
  - TRB
---

## Summary

1. **Years of inflated trading volumes:** Multiple independent analyses — including reports from [Chainalysis](https://www.chainalysis.com/blog/fake-trade-volume-cryptocurrency-exchanges/), the [Blockchain Transparency Institute](https://www.einnews.com/pr_news/477521233/bitforex-the-biggest-wash-trading-crypto-exchange-in-the-world), and [Kaiko](https://blog.kaiko.com/how-to-spot-artificial-volume-766283f23fbe) — found that BitForex fabricated the vast majority of its reported trading volume, with estimates suggesting approximately **93% of volume was fake**.
2. **Regulatory warnings ignored:** Japan's Financial Services Agency (FSA) [flagged BitForex in March 2023](https://www.coindesk.com/policy/2023/04/03/japan-regulator-flags-four-crypto-exchanges-including-bybit-for-operating-without-registration) for operating without registration, alongside Bybit, Bitget, and MEXC Global.
3. **Suspicious CEO departure:** BitForex CEO Jason Luo abruptly stepped down on January 31, 2024, weeks before the exchange collapsed.
4. **$56.5 million exit:** On February 23, 2024, on-chain investigator [ZachXBT identified](https://twitter.com/zachxbt/status/1762028433574650347) approximately $56.5 million in outflows from BitForex hot wallets across multiple chains, after which withdrawals were halted and the platform went dark.
5. **Significant token supply risk:** BitForex held approximately 18% of the Tellor (TRB) supply and 7% of the Ecomi (OMI) supply. OMI crashed approximately 88% following the incident.

## Background

BitForex was founded in 2017 and registered in the Republic of Seychelles, with operations primarily based in Hong Kong. The exchange marketed itself as a "world's leading digital asset trading platform" and, at its peak in January 2024, reported daily trading volumes exceeding [$4.2 billion](https://www.coingecko.com/en/exchanges/bitforex). Its first CEO, Garrett Jin, led the exchange from 2017 to 2020, followed by Jason Luo.

Despite its claimed volumes, BitForex consistently ranked among the worst offenders for fake trading activity across multiple independent analyses conducted between 2018 and 2023.

## Evidence of Wash Trading

### Chainalysis Trade-to-On-Chain Volume Analysis

In a November 2019 report, blockchain analytics firm Chainalysis examined the ratio of reported trade volume to actual on-chain transaction volume for dozens of cryptocurrency exchanges. Using the methodology established by the [Bitwise Asset Management report to the SEC](https://www.sec.gov/comments/sr-nysearca-2019-01/srnysearca201901-5164833-183434.pdf), Chainalysis established a baseline ratio from ten exchanges identified by Bitwise as having legitimate volume (the "Bitwise 10").

BitForex's reported trade-to-on-chain volume ratio **dramatically exceeded this baseline**, indicating that the vast majority of its reported trading activity did not correspond to real asset movements on the blockchain. Chainalysis concluded that "a substantial amount of its trade volume has been faked."

### Blockchain Transparency Institute Findings

The Blockchain Transparency Institute (BTI), a non-profit organization of cryptocurrency researchers, conducted systematic analyses of exchange trading volumes. In its 2019 report, BTI identified BitForex as one of the worst offenders globally, estimating that **approximately 93% of its reported trading volume was fabricated** through wash trading. On January 29, 2019, BTI calculated that of BitForex's reported $242 million daily volume, only approximately $17 million represented genuine trading activity.

BTI's methodology examined order book depth, web traffic relative to trading volume, and trade pattern anomalies to distinguish real trading from artificial volume generation.

### Kaiko Market Data Analysis

Crypto market data provider Kaiko independently identified anomalous trading patterns on BitForex consistent with wash trading. Their analysis highlighted irregularities in order flow, trade size distribution, and timing patterns that are characteristic of algorithmic volume generation rather than organic market activity.

## Regulatory Actions

### Japan FSA Warning (March 2023)

On March 31, 2023, Japan's Financial Services Agency issued a formal [warning letter](https://www.coindesk.com/policy/2023/04/03/japan-regulator-flags-four-crypto-exchanges-including-bybit-for-operating-without-registration) to BitForex for soliciting Japanese customers without holding the required registration under Japan's Payment Services Act. The FSA instructed BitForex to cease providing services to Japanese citizens. BitForex was named alongside Bybit, Bitget, and MEXC Global in this enforcement action.

Despite the regulatory warning, BitForex continued operations without making significant compliance changes.

## The Exit Scam (February 2024)

### Timeline of Events

- **January 31, 2024:** CEO Jason Luo [steps down](https://support.bitforex.com/hc/en-us/articles/28260960127385-Jason-Stepped-Down-as-CEO-of-BitForex) from BitForex. No successor is announced.
- **February 21, 2024:** BitForex's Telegram and social media accounts stop posting and responding to users.
- **February 23, 2024:** Approximately [$56.5 million](https://twitter.com/zachxbt/status/1762028433574650347) in cryptocurrency is withdrawn from BitForex's hot wallets across multiple blockchains, as identified by on-chain investigator ZachXBT.
- **February 24, 2024:** Users report that all tokens on the exchange are trading at prices 60-80% below market rates, and withdrawal processing has ceased entirely.
- **February 26, 2024:** ZachXBT publicly flags the suspicious outflows. The exchange's website becomes inaccessible, displaying a Cloudflare DDoS protection error page.
- **February 27, 2024:** Reports emerge that BitForex team members were detained by Chinese authorities for investigation.

### On-Chain Evidence

ZachXBT's on-chain analysis revealed coordinated outflows of approximately $56.5 million from BitForex's hot wallets on February 23, 2024. The withdrawals occurred across multiple blockchain networks simultaneously, suggesting a deliberate and planned extraction of assets rather than routine operations.

Following the outflows, no further deposits or withdrawals were processed by the exchange. Trading volume dropped to zero according to both CoinMarketCap and CoinGecko data.

### Impact on Token Markets

BitForex's collapse had outsized effects on specific token markets due to the exchange's concentrated holdings:

- **Ecomi (OMI):** BitForex held approximately 7% of total OMI supply. OMI serves as the utility token for the VeVe ecosystem, a marketplace for licensed NFTs from brands including Marvel and Disney. Following the BitForex shutdown, OMI crashed approximately 88%, from $0.0069 to $0.00078.
- **Tellor (TRB):** BitForex reportedly held approximately 18% of the TRB token supply, creating significant overhang risk for TRB holders.

### User Response

A Telegram group named "[Scammed by BitForex](https://t.me/scammedByBitForex)" rapidly grew to over 150 members as affected users organized to share information and pursue collective action. Users filed complaints with Hong Kong's Securities and Futures Commission (SFC) and attempted to raise awareness through cryptocurrency media and influencers.

## Connection to Former CEO Garrett Jin

In October 2025, on-chain analytics firm EyeOnChain [reportedly traced](https://news.shib.io/2025/10/14/ex-bitforex-ceo-denies-ties-to-100k-btc-whale-in-fraud-scandal/) a Hyperliquid whale account holding over 100,000 BTC to wallet addresses associated with Garrett Jin, who served as BitForex's CEO from 2017 to 2020. Jin publicly denied the connection, stating "the fund isn't mine." The allegations remain unresolved and under investigation.

## Conclusion

The BitForex case illustrates how persistent wash trading can serve as both a revenue-generating strategy and a cover for more serious malfeasance. For years, multiple independent analyses flagged BitForex's trading volumes as overwhelmingly artificial, yet the exchange continued to operate and attract depositors. The combination of fabricated volumes, regulatory non-compliance, and an eventual exit scam resulting in $56.5 million in losses demonstrates the risks that wash trading poses not merely as a form of market deception but as an indicator of deeper operational and ethical failures at cryptocurrency exchanges.

## References

1. Chainalysis. "Can On-chain Data Help Us Spot Fake Exchange Trading Volumes?" November 2019. https://www.chainalysis.com/blog/fake-trade-volume-cryptocurrency-exchanges/
2. Blockchain Transparency Institute. "Bitforex — The Biggest Wash Trading Crypto Exchange in the World." EIN Presswire, October 2019. https://www.einnews.com/pr_news/477521233/bitforex-the-biggest-wash-trading-crypto-exchange-in-the-world
3. Bitwise Asset Management. "Analysis of Real Bitcoin Trade Volume." Presented to the SEC, March 2019. https://www.sec.gov/comments/sr-nysearca-2019-01/srnysearca201901-5164833-183434.pdf
4. CoinDesk. "Japan Regulator Flags Four Crypto Exchanges Including Bybit for Operating Without Registration." April 3, 2023. https://www.coindesk.com/policy/2023/04/03/japan-regulator-flags-four-crypto-exchanges-including-bybit-for-operating-without-registration
5. ZachXBT. Twitter post identifying BitForex suspicious outflows. February 26, 2024. https://twitter.com/zachxbt/status/1762028433574650347
6. Decrypt. "Exit Scam? Bitcoin Exchange BitForex Shutters After $57M Mysteriously Withdrawn." February 26, 2024. https://decrypt.co/219012/exit-scam-bitforex-shutters-after-57-million-withdrawn
7. Halborn. "Explained: The BitForex Rug Pull (February 2024)." February 29, 2024. https://www.halborn.com/blog/post/explained-the-bitforex-rug-pull-february-2024
8. CoinGecko. BitForex exchange data. https://www.coingecko.com/en/exchanges/bitforex
9. Kaiko. "How to Spot Artificial Volume." https://blog.kaiko.com/how-to-spot-artificial-volume-766283f23fbe
10. The Shib Daily. "Ex-BitForex CEO Denies Ties to 100K BTC Whale in Fraud Scandal." October 14, 2025. https://news.shib.io/2025/10/14/ex-bitforex-ceo-denies-ties-to-100k-btc-whale-in-fraud-scandal/
