---
title: "FTX and Alameda Research: Circular Token Manipulation and the Collapse of FTT"
date: "2026-04-05"
description: "Analysis of how FTX and its affiliated trading firm Alameda Research used the FTT token as circular collateral to inflate balance sheet valuations, manipulate market prices, and sustain an $8B+ fraud — culminating in one of the largest exchange collapses in crypto history."
entities:
  - "FTX"
  - "Alameda Research"
  - FTT
  - SOL
---

## 🌰 Background

FTX was a centralized cryptocurrency exchange founded in 2019 by Sam Bankman-Fried (SBF). Its sister company, Alameda Research, was a quantitative trading firm — also controlled by SBF — that enjoyed undisclosed privileges on the FTX platform: an effectively unlimited line of credit drawn from customer deposits, exemption from automatic liquidation, and access to client order flow data. This structural conflict of interest was the foundation for the largest market manipulation scheme in crypto history.

## 🌰 The FTT Token as Circular Collateral

FTX issued its native exchange token, FTT, with a total supply of approximately 336 million tokens. At the time of collapse, fewer than 33 million tokens (~10%) were freely trading on the open market. FTX and Alameda together held the dominant share — estimated at 60% of total supply by post-bankruptcy on-chain analysis (Nansen, 2022) — while the remainder was locked in vesting schedules for team and early investors.

{{< figure src="ftt-supply-distribution.png" caption="🌰 Approximate FTT token distribution at time of collapse. FTX and Alameda collectively controlled the majority of supply, making open-market pricing a poor reflection of true value. Sources: FTX bankruptcy filings; Nansen on-chain analysis, November 2022." >}}

This concentration created a feedback loop: FTX used FTT as collateral to justify Alameda's multi-billion dollar line of credit, while Alameda's trading activity and buy-back programs artificially maintained the token's price. A November 2, 2022 CoinDesk report revealed that Alameda's balance sheet carried approximately **$5.8 billion in FTT** as its primary asset — a token largely created by, and held by, the same entities using it as collateral. True market depth for FTT was far shallower than the headline market capitalization implied.

## 🌰 Market Manipulation Mechanisms

Three mechanisms sustained the artificial valuation:

🌰 **1. Buy-back program as price floor.** FTX committed to repurchasing FTT from trading fee revenue, creating a synthetic price floor. This removed genuine price discovery and conditioned the market to treat FTT as a stable store of value.

🌰 **2. Exemption from liquidation.** Unlike retail traders, Alameda's positions on FTX were not subject to the platform's automatic liquidation engine, per internal FTX code reviewed by bankruptcy administrators (John Ray III testimony, 2023). This allowed Alameda to hold leveraged FTT positions that would have triggered forced selling for any other participant, suppressing artificial sell pressure.

🌰 **3. Cross-platform collateral inflation.** FTT was accepted as collateral on multiple third-party lending platforms and by FTX's own internal credit system. Because FTX and Alameda jointly held so much of the supply, they could credibly claim FTT's market cap (~$9.6B at peak) as an asset, despite that market cap being circular and illiquid.

## 🌰 The Collapse: November 2022

On **November 2, 2022**, CoinDesk published Alameda's balance sheet. The document showed FTT constituted the largest single asset. Within days, Binance CEO Changpeng Zhao (CZ) announced plans to liquidate Binance's entire FTT position — approximately **$529 million** — citing "risk management" concerns following "recent revelations."

Alameda CEO Caroline Ellison publicly offered to purchase all of Binance's FTT at $22 — a transparent attempt to defend the price floor. The offer was refused. On **November 6**, CZ confirmed Binance would sell. The price cascade that followed was severe:

{{< figure src="ftt-price-collapse-nov2022.png" caption="🌰 FTT price (USD) from October 31 to November 14, 2022. The token lost over 95% of its value in five trading days following public disclosure of Alameda's balance sheet and Binance's decision to liquidate holdings. Key events annotated. Price data: CoinGecko." >}}

- **Nov 6:** $22 → price begins collapse as sell pressure overwhelms buy-back capacity
- **Nov 8:** $4.50 → FTX halts customer withdrawals; Binance signs and then withdraws acquisition LOI
- **Nov 9:** $2.10 → CFTC and DOJ begin investigations
- **Nov 11:** $1.10 → FTX, FTX US, and Alameda Research file for Chapter 11 bankruptcy

Customer withdrawals that could not be fulfilled exceeded **$6 billion** within 72 hours of the CoinDesk article — consistent with an institution that had been re-hypothecating customer assets to fund trading operations.

## 🌰 Correlated Sell-off: Contagion to Related Assets

Alameda had accumulated large positions in SOL (Solana) — SBF was an early and prominent Solana backer, and multiple Solana ecosystem investments were held on FTX balance sheets. As Alameda's insolvency became clear, forced liquidation of its crypto holdings drove SOL down in tandem with FTT.

{{< figure src="ftt-sol-correlated-collapse.png" caption="🌰 Parallel price decline of FTT and SOL during November 2022. Both assets were heavily concentrated in Alameda Research's portfolio. SOL fell from ~$32 to ~$11 over the same period, reflecting market-wide revaluation of SBF-affiliated assets. Price data: CoinGecko." >}}

The correlation illustrates a key feature of manipulation concentrated in affiliated entities: when a single actor's balance sheet unravels, all correlated positions unwind simultaneously, amplifying market impact beyond the immediate token.

## 🌰 Regulatory Findings and Criminal Convictions

The CFTC's December 2022 complaint against FTX and SBF detailed the following violations relevant to market manipulation:

- 🌰 Alameda received an undisclosed "borrowing facility" from FTX customer funds in excess of **$8 billion**, enabling it to take outsized market positions without genuine capital backing
- 🌰 FTX software was modified to exempt Alameda from liquidation protocols applied to all other users
- 🌰 FTX co-mingled customer funds with operational accounts, using them to fund Alameda's trading losses and venture investments

In November 2023, Sam Bankman-Fried was convicted on all seven counts of fraud, conspiracy, and money laundering. Caroline Ellison, Ryan Salame, and other senior executives entered guilty pleas and cooperated with prosecutors. The DOJ described the scheme as "one of the biggest financial frauds in American history."

## 🌰 Market Health Indicators: What the Data Revealed

Several market health metrics were anomalous in FTT trading data preceding the collapse:

🌰 **Unusually stable buy/sell ratio:** FTT's buy-to-sell volume ratio on FTX remained remarkably consistent across extended periods — a pattern inconsistent with organic price discovery and consistent with algorithmic maintenance of a price floor (see Huobi analysis methodology, dn-institute, 2023).

🌰 **Low retail participation:** FTT trading was dominated by large round-lot transactions. Clustering analysis of order sizes showed minimal small-retail footprint relative to other exchange tokens of comparable market cap, indicating the volume was institutionally driven rather than reflecting genuine retail demand.

🌰 **Market depth illusion:** FTT's stated market capitalization (~$9.6B at peak) was not supported by actual liquidity. Order book analysis consistently showed that any attempt to sell 1–2% of the circulating supply would move the price by 10%+, revealing the visible price as a maintained fiction rather than a market equilibrium.

## 🌰 Conclusion

The FTX/Alameda manipulation of FTT exemplifies a category of exchange-native token fraud that evades standard market health detection: the manipulator is the exchange itself. The token's price was maintained not through wash trading in the traditional sense, but through structural insider advantages, circular collateral accounting, and buy-back programs funded by customer deposits. The result — a $9.6B asset that evaporated to near-zero in five days — represents the largest single instance of exchange-driven token price manipulation on record.

🌰 Key signals that preceded and accompanied the collapse:
- 🌰 Disproportionate insider token concentration (>90% not freely floating)
- 🌰 Anomalously stable price behavior inconsistent with organic trading
- 🌰 Undisclosed related-party loans collateralized by the same token
- 🌰 Asymmetric liquidation rules favoring the exchange's affiliated trading desk

## 🌰 References

- 🌰 CoinDesk. "Divisions in Sam Bankman-Fried's Crypto Empire Blur on His Trading Titan Alameda's Balance Sheet." November 2, 2022.
- 🌰 U.S. Commodity Futures Trading Commission v. Samuel Bankman-Fried et al. CFTC Complaint, December 13, 2022.
- 🌰 United States v. Samuel Bankman-Fried. S.D.N.Y. Indictment, December 9, 2022.
- 🌰 Nansen Research. "FTX Collapse: On-Chain Analysis." November 2022.
- 🌰 FTX Bankruptcy Filing. Debtors' Schedules of Assets and Liabilities. Delaware, January 2023.
- 🌰 John Ray III. Congressional Testimony. U.S. House Financial Services Committee, December 13, 2022.
- 🌰 Caroline Ellison Plea Agreement. S.D.N.Y., December 19, 2022.
- 🌰 dn-institute. "Uncovering Wash Trading and Market Manipulation on Huobi." August 2023.
- 🌰 CoinGecko. FTT and SOL historical price data, November 2022.
