---
title: "Market Manipulation and Wash Trading on FTX: The Role of Alameda Research"
date: 2026-03-19
entities:
  - FTX
  - Alameda Research
  - FTT
  - SBF
---

## Summary

1. **Structural Conflict of Interest:** Alameda Research, the affiliated trading firm, operated with special privileges on FTX, including exemption from the exchange's auto-liquidation engine and a hidden $65 billion line of credit funded by customer deposits.
2. **FTT Token Manipulation:** FTX's native token FTT was used as collateral despite being created and controlled by FTX itself. The SEC charged that Alameda purchased large quantities of FTT on the open market to artificially inflate its price, a practice confirmed through on-chain analysis.
3. **Wash Trading Indicators:** Abnormal bitcoin volume spikes on FTX were detected during periods of low price volatility — a hallmark of wash trading. Volume spikes were uncorrelated with price movement, indicating recursive buy-sell activity by a single entity.
4. **Social Media Bot Amplification:** A study by the Network Contagion Research Institute (NCRI) analyzing over 3 million tweets found that bot-driven activity preceded 11–30% single-day price jumps in tokens held by Alameda before their listing on FTX.
5. **Collapse and $8 Billion Gap:** When CoinDesk revealed Alameda's FTT-heavy balance sheet in November 2022, a bank run ensued, exposing an $8 billion shortfall between customer deposits and available assets, leading to the largest fraud case in crypto history.

## Background

FTX was founded in 2019 by Sam Bankman-Fried (SBF) and became the third-largest cryptocurrency exchange by volume, reaching a $32 billion valuation at its peak. Alameda Research, a quantitative trading firm also founded by SBF, served as the primary market maker on FTX. This dual role — exchange operator and dominant market maker — created a structural conflict of interest at the core of FTX's operations.

## Metrics used

### Alameda's special trading privileges

Unlike other market participants, Alameda Research operated under a fundamentally different set of rules on FTX. Court testimony from former FTX engineering director Nishad Singh and CEO of Alameda Research Caroline Ellison revealed that:

- Alameda was **exempt from FTX's auto-liquidation engine**, the risk management system that automatically closes positions when a trader's margin falls below required thresholds.
- A backdoor in FTX's codebase — coded as `allow_negative = 0` by co-founder Gary Wang shortly after FTX's 2019 launch — permitted Alameda to maintain a negative balance of up to **$65 billion**, effectively giving it unlimited borrowing power from the pool of FTX customer deposits. A LedgerX engineer discovered this backdoor on May 5, 2022; the employee was fired that summer.
- Alameda had **faster API access** to FTX than other traders, enabling front-running opportunities.

These privileges were not disclosed to FTX customers or investors. By mid-June 2022, Alameda had borrowed **$9.9 billion from FTX customer accounts** — 77% of the $13 billion in customer USD deposits, according to Caroline Ellison's trial testimony. Ellison also testified that she prepared **seven alternative balance sheets** on SBF's direction to hide the borrowed-funds line from lenders.

### FTT token — Self-referential collateral and price manipulation

FTX created FTT as its native exchange token in 2019. The token was used to offer trading fee discounts, but critically, it also served as **collateral on Alameda's balance sheet**. This created a circular dependency:

1. FTX minted FTT tokens, retaining a majority of the supply.
2. Alameda used FTT as collateral to borrow from FTX (i.e., from customer funds).
3. Alameda purchased FTT on the open market to support its price, using borrowed customer funds.
4. The inflated FTT price was reported as a balance sheet asset, justifying further borrowing.

The SEC's complaint filed on December 13, 2022 (SEC v. Bankman-Fried, Case No. 22-cv-10501) explicitly charged that Alameda "purchased large quantities [of FTT] on the open market to prop up its price." On-chain analysis by [Nansen Research](https://www.nansen.ai/research/blockchain-analysis-the-collapse-of-alameda-and-ftx) identified approximately **$4.1 billion in FTT transfers** from Alameda to FTX wallets between September 28 and November 1, 2022, along with $388 million in stablecoins flowing in the opposite direction.

At the time of CoinDesk's November 2, 2022 report, Alameda's balance sheet showed $14.6 billion in assets — of which over **$5 billion was in FTT**, a token with limited liquidity that could not be sold without crashing its own price.

### Abnormal volume patterns — Wash trading signals

Analysis by [Inca Digital](https://inca.digital/intelligence/abnormal-volumes-ftx/) identified suspicious trading volume patterns on FTX's bitcoin markets:

- **Volume spikes with minimal price impact**: Large 1-minute volume peaks were detected during periods when the difference between open and close prices was negligible. In normally functioning markets, volume spikes of this magnitude would produce measurable price movement.
- **Volume exceeding statistical distribution norms**: During March 2020, abnormal bitcoin volumes on FTX "greatly exceeded the distribution during even minute price shifts." Such patterns — high volume with no corresponding price change — are consistent with an entity recursively buying and selling the same asset (wash trading).
- **Cross-exchange comparison anomalies**: When compared to exchanges with established surveillance programs (Coinbase, Kraken), FTX's volume distribution showed statistically significant deviations from the power-law heavy tail distribution expected in legitimate markets.

Academic research published in the *Journal of International Financial Markets, Institutions and Money* (["FTX's downfall and Binance's consolidation"](https://www.sciencedirect.com/science/article/pii/S037843712300599X), arXiv:2302.11371) noted that FTT demonstrated "superior performance compared to BTC and BNB" throughout 2022 — a pattern consistent with active price manipulation rather than organic market dynamics.

### Social media manipulation — Coordinated bot campaigns

A 2023 study by the **Network Contagion Research Institute (NCRI)**, [reported by CNBC](https://www.cnbc.com/amp/2023/08/02/elon-musk-tweets-twitter-bots-boosted-ftx-listed-crypto-researchers.html), analyzed over **3 million tweets** mentioning 18 cryptocurrencies listed on FTX between January 2019 and January 2023:

- Alameda held at least **five tokens before they were listed on FTX**, creating a pump opportunity.
- Bot-like social media activity preceded significant price increases. For the RNDR token specifically, inauthentic post spikes **preceded 11–30% single-day price jumps** on four separate occasions in 2022–2023.
- The study concluded that "the intensification of social media activity was not merely an organic outcome of the coins' popularity, but potentially a strategic ploy to influence market sentiment."

This represents a multi-channel manipulation strategy: artificial volume (wash trading) combined with artificial sentiment (bot amplification) to inflate prices of tokens already held by the affiliated trading firm.

## Collapse timeline

| Date | Event |
|--|--|
| 2022-11-02 | CoinDesk publishes Alameda's balance sheet showing $5B+ in FTT exposure |
| 2022-11-06 | Binance CEO CZ announces sale of 23M FTT ($529M); $1B withdrawn from FTX in 24h |
| 2022-11-07 | Additional $4B in withdrawals; FTX liquidity crisis becomes acute |
| 2022-11-08 | FTT falls below $22; Binance signs non-binding LOI to acquire FTX; FTX halts withdrawals |
| 2022-11-09 | Binance withdraws acquisition offer after due diligence reveals "mishandled customer funds" |
| 2022-11-10 | Alameda Research winds down trading operations |
| 2022-11-11 | FTX, Alameda, and 130+ entities file for Chapter 11 bankruptcy; $477M stolen by hackers |
| 2022-11-12 | Reuters reports $1B+ in customer funds unaccounted for |
| 2022-12-12 | SBF arrested in Nassau, Bahamas |
| 2022-12-13 | DOJ, SEC, and CFTC file simultaneous charges |

## Regulatory actions and legal outcomes

### Department of Justice

Sam Bankman-Fried was indicted on **seven counts of fraud and conspiracy**. His trial concluded on November 2, 2023 with a guilty verdict on all counts. On March 28, 2024, he was sentenced to **25 years in federal prison** and ordered to **forfeit $11 billion**.

Three former executives pleaded guilty and cooperated with prosecutors:

- **Caroline Ellison** (CEO, Alameda Research): sentenced September 24, 2024 to **2 years** in prison and $11 billion forfeiture.
- **Gary Wang** (CTO, FTX): key prosecution witness, cooperated extensively.
- **Nishad Singh** (Engineering Director, FTX): pleaded guilty; CFTC filed additional fraud charges on February 28, 2023.

Their testimony confirmed that Bankman-Fried knowingly directed the use of FTX customer funds to cover Alameda's trading losses, venture investments, real estate purchases, and political donations.

Federal prosecutors described the case as "one of the biggest financial frauds in American history."

### Securities and Exchange Commission

The SEC filed its complaint on December 13, 2022, charging Bankman-Fried with orchestrating a scheme to defraud FTX equity investors. The SEC's complaint specifically alleged manipulation of FTT's price through coordinated open-market purchases by Alameda Research.

### Commodity Futures Trading Commission

The CFTC filed a parallel complaint on December 13, 2022, charging FTX and Alameda with fraud and material misrepresentations in connection with the sale of digital commodities. In August 2024, a consent order established a **$12.7 billion judgment** — the largest in CFTC history — comprising $8.7 billion in restitution and $4 billion in disgorgement.

### Customer recovery

Under the bankruptcy plan approved in October 2024, most FTX customers are expected to receive **100–118% of their November 2022 account balances** in cash. However, these repayments are based on cryptocurrency prices at the time of the bankruptcy filing — meaning customers do not benefit from the substantial price appreciation that occurred in 2023–2024.

## References

1. CoinDesk, "[Divisions in Sam Bankman-Fried's Crypto Empire Blur on His Trading Titan Alameda's Balance Sheet](https://www.coindesk.com/business/2022/11/02/divisions-in-sam-bankman-frieds-crypto-empire-blur-on-his-trading-titan-alamedas-balance-sheet/)," November 2, 2022.
2. CoinDesk, "[The Epic Collapse of Sam Bankman-Fried's FTX Exchange: A Crypto Markets Timeline](https://www.coindesk.com/markets/2022/11/12/the-epic-collapse-of-sam-bankman-frieds-ftx-exchange-a-crypto-markets-timeline)," November 12, 2022.
3. Nansen Research, "[Blockchain Analysis: The Collapse of Alameda and FTX](https://www.nansen.ai/research/blockchain-analysis-the-collapse-of-alameda-and-ftx)," November 2022.
4. Inca Digital, "[Abnormal Trading Volumes on FTX](https://inca.digital/intelligence/abnormal-volumes-ftx/)," 2022.
5. SEC, "SEC Charges Samuel Bankman-Fried with Defrauding Investors," Case No. 22-cv-10501, December 13, 2022.
6. CFTC, "CFTC Charges Sam Bankman-Fried, FTX Trading and Alameda Research," Case No. 22-cv-10503, December 13, 2022.
7. Bao et al., "[FTX's downfall and Binance's consolidation](https://www.sciencedirect.com/science/article/pii/S037843712300599X)," *Journal of International Financial Markets, Institutions and Money*, 2023.
8. NCRI / CNBC, "[Elon Musk tweets, Twitter bots boosted FTX-listed crypto](https://www.cnbc.com/amp/2023/08/02/elon-musk-tweets-twitter-bots-boosted-ftx-listed-crypto-researchers.html)," August 2, 2023.
9. DOJ, "United States v. Samuel Bankman-Fried," sentencing memorandum, March 28, 2024.
10. Seven Pillars Institute, "[Case Study: FTX and Sam Bankman-Fried](https://www.sevenpillarsinstitute-org.sevenpillarsconsulting.com/case-study-ftx-and-sam-bankman-fried/)."
