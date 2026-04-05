---
title: "FTX and Alameda Research: Circular Collateral, Code-Level Privileges, and the Manufactured Legitimacy of FTT"
date: "2026-04-05"
description: "Comprehensive analysis of how FTX and Alameda Research sustained a multi-billion dollar market manipulation scheme through circular token collateral, hidden code-level trading advantages, and deliberate public persona construction — culminating in the largest crypto exchange collapse on record."
entities:
  - "FTX"
  - "Alameda Research"
  - FTT
  - SOL
---

## 🌰 Background

FTX was a centralized cryptocurrency exchange founded in 2019 by Sam Bankman-Fried (SBF). Its sister company, Alameda Research, was a quantitative trading firm also controlled by SBF that traded on FTX with a set of undisclosed structural advantages over all other market participants. This conflict of interest — an exchange operating as referee while its affiliated trading desk played with a stacked deck — was the foundation of one of the most sophisticated market manipulation schemes in financial history.

The manipulation operated on three simultaneous levels: **technical** (code embedded in the trading engine), **financial** (circular token collateral), and **social** (constructed public legitimacy). Each layer reinforced the others.

## 🌰 Level 1: Code-Level Privileges — The "allow_negative" Flag

The most concrete evidence of manipulation came from FTX's own codebase. Bankruptcy administrators and the CFTC established that FTX's trading engine contained a hardcoded exception for Alameda Research's accounts: a flag called `allow_negative` that permitted Alameda's balances to go negative without triggering the automatic liquidation engine applied to every other user on the platform.

🌰 In practice, this meant:

- 🌰 Alameda could accumulate leveraged positions of effectively unlimited size without posting real collateral
- 🌰 During volatile markets, where retail traders would be force-liquidated, Alameda could hold — removing natural sell pressure that would otherwise correct inflated prices
- 🌰 Alameda's risk was backstopped not by its own capital but by FTX's customer deposit pool

John Ray III, the bankruptcy administrator appointed to replace SBF, described the system to the U.S. House Financial Services Committee (December 2022) as one where "Alameda had the ability to maintain negative balances — in essence, an unlimited line of credit drawn against FTX customer assets." The CFTC's December 2022 complaint confirmed the same: Alameda received an undisclosed borrowing facility ultimately exceeding **$8 billion** in customer funds.

A separate undisclosed advantage documented in SEC and DOJ filings: Alameda's API connections to FTX operated at a lower latency than those available to external traders, enabling it to systematically front-run large retail orders — a practice that generated an estimated **$60 million** in additional profits from 2021 to 2022 (DOJ indictment, December 2022).

## 🌰 Level 2: Circular Token Collateral — Manufacturing FTT's Value

FTX issued its native exchange token, FTT, with a total supply of approximately 336 million tokens. At the time of collapse, on-chain analysis by Nansen (November 2022) and post-bankruptcy forensic accounting established that FTX and Alameda together held approximately **88% of all FTT** — leaving fewer than 40 million tokens freely trading on open markets.

{{< figure src="ftt-supply-distribution.png" caption="🌰 FTT token supply distribution at time of collapse. Approximately 88% was held by FTX, Alameda Research, or locked in vesting schedules — leaving a thin float that could be priced far above genuine liquidity. Sources: FTX bankruptcy filings; Nansen on-chain analysis, November 2022." >}}

This concentration created a feedback loop of circular collateral:

1. 🌰 FTX minted FTT and retained the dominant share
2. 🌰 FTX's buy-back program (funded by trading fees) created a sustained price floor
3. 🌰 Alameda held FTT as its primary balance sheet asset — carrying ~$5.8 billion in FTT at the time of the CoinDesk disclosure (November 2, 2022)
4. 🌰 Alameda used this FTT to secure borrowing from third-party lenders and justify its credit line from FTX itself
5. 🌰 The value of that collateral depended entirely on maintaining FTT's market price — which required the buy-back program — which required FTX's continued operation — funded by customer deposits

No external counterparty could independently verify the depth or liquidity behind FTT's headline market capitalization (~$9.6 billion at peak). The stated market cap was a function of a thin float and a managed price floor, not organic demand.

## 🌰 Level 3: Manufactured Legitimacy — SBF's Public Persona as Market Manipulation

🌰 A dimension of the FTX scheme that distinguishes it from conventional exchange manipulation is the deliberate construction of SBF's public credibility as a mechanism for sustaining token price and investor confidence. This is not speculation — it is documented in Ellison's plea allocution and DOJ filings.

🌰 SBF cultivated an identity as a "philanthropist-trader" operating under the Effective Altruism (EA) philosophy — publicly donating to charitable causes, testifying before Congress as a credible regulatory voice, and maintaining a prominent media presence in major outlets (Forbes, Fortune, NYT). He became the second-largest donor to the 2022 U.S. Democratic Party midterm campaigns, contributing **$39.8 million** — a sum that purchased political access and perception of legitimacy simultaneously.

🌰 This persona served direct market functions:

- 🌰 **Institutional investor confidence:** FTX raised $400 million in Series C funding (January 2022) at a $32 billion valuation from Sequoia Capital, BlackRock, and others — all of whom later wrote investments to zero. SBF's reputation was the primary due diligence substitute.
- 🌰 **FTT credibility:** Institutional holding of FTT was partially driven by confidence in the person behind the exchange. When the persona collapsed, so did the token.
- 🌰 **Regulatory capture attempt:** SBF's lobbying pushed for crypto regulations that would have formalized FTX's market position and potentially legitimized its practices.

The NCRI (Network Contagion Research Institute) documented coordinated social media activity — across 3 million+ tweets — showing bot-driven amplification of SBF's public appearances preceding 11–30% price increases in FTT and affiliated tokens, a pattern consistent with coordinated sentiment manipulation (NCRI, 2022).

## 🌰 The Collapse: November 2022

On **November 2, 2022**, CoinDesk published Alameda's leaked balance sheet, revealing FTT as its primary asset. This was the first public signal that FTX's affiliated trading arm had no genuine capital base — only circular FTT holdings.

On **November 6**, Binance CEO CZ announced Binance would liquidate its entire FTT position, valued at approximately **$529 million**. Alameda CEO Caroline Ellison publicly offered to buy Binance's FTT at $22 in an attempt to defend the price floor — publicly admitting the price was being actively managed. CZ declined.

{{< figure src="ftt-price-volume-nov2022.png" caption="🌰 FTT price (upper) and daily trading volume in millions USD (lower), October 31 to November 14, 2022. Volume spiked 14x above October averages on November 7–8 as forced selling overwhelmed the buy-back program. Price fell over 95% in five trading days. Price and volume data: CoinGecko / CryptoCompare." >}}

Key events:

- 🌰 **Nov 6:** Price drops from $25.60 → $22; Ellison's public bid fails
- 🌰 **Nov 7:** Volume spikes to ~$480M (11× October daily average of ~$43M)
- 🌰 **Nov 8:** $4.50; trading volume peaks at ~$604M; FTX halts withdrawals; Binance signs then withdraws acquisition LOI within 24 hours after reviewing FTX's books
- 🌰 **Nov 9:** $2.10; CFTC and DOJ open investigations
- 🌰 **Nov 11:** $1.10; FTX, FTX US, and Alameda Research file for Chapter 11 bankruptcy; $6B+ in withdrawal requests could not be fulfilled
- 🌰 **Nov 2023:** SBF convicted on all 7 counts; sentenced to **25 years** in prison; **$11 billion** in forfeiture ordered

The CFTC's final settlement against FTX entities totaled **$12.7 billion** — the largest in CFTC history.

## 🌰 Contagion: Correlated Sell-off in SBF-Affiliated Assets

Alameda held concentrated positions in Solana (SOL) ecosystem tokens, reflecting SBF's early and public advocacy for Solana as the preferred chain for FTX's ecosystem. As Alameda's insolvency became clear, forced liquidations of its crypto holdings drove SOL down in tandem with FTT.

{{< figure src="ftt-sol-correlated-collapse.png" caption="🌰 Parallel price decline of FTT and SOL, October 31 to November 14, 2022. SOL fell from ~$32 to ~$11 (65% decline) over the same period as FTT's near-total collapse, driven by Alameda's concentrated portfolio liquidations. Price data: CoinGecko." >}}

The correlation illustrates a structural risk in concentrated insider token holdings: a single actor's balance sheet unwind forces simultaneous selling across all correlated positions, amplifying the market impact far beyond the immediately affected token.

## 🌰 Market Health Indicators: Anomalies Preceding the Collapse

Several market health signals were anomalous in FTT's trading data in the months before the collapse:

🌰 **Benford's Law deviations in order size distribution:** FTT order flow on FTX showed lower-digit clustering inconsistent with organically distributed retail activity — a pattern documented in dn-institute's analysis of Huobi (2023) as characteristic of algorithmically maintained order books. The buy-back program, operating on a fee-driven schedule, necessarily introduced non-random periodicity into order sizes.

🌰 **Abnormal buy/sell ratio stability:** FTT's buy-to-sell volume ratio on FTX remained unusually consistent across months — a pattern incompatible with genuine price discovery, where buy/sell ratios fluctuate significantly with market sentiment. This stability is consistent with Alameda systematically absorbing sell-side pressure to maintain the price floor.

🌰 **Market depth vs. market cap divergence:** At FTT's peak market capitalization of ~$9.6 billion, order book depth data showed that a sale of 2% of circulating supply could move the price by 10%+. This illiquidity was structurally hidden by the fact that the dominant holders (FTX/Alameda) had no incentive to sell and every incentive to stabilize — until they couldn't.

🌰 **Volume uncorrelated with price movement:** Inca Digital's analysis of FTX BTC trading (cited in subsequent regulatory proceedings) showed large-volume periods that did not produce corresponding price movements — a classic indicator of wash trading or internally absorbed order flow, where Alameda served as the counterparty absorbing retail sell orders without allowing price to adjust.

## 🌰 Regulatory Outcomes

| Action | Body | Outcome |
|--------|------|---------|
| Criminal conviction | DOJ (S.D.N.Y.) | SBF: 25 years, $11B forfeiture |
| Civil charges | CFTC | $12.7B settlement (record) |
| Civil charges | SEC | Multiple defendants |
| Guilty pleas | DOJ | Ellison, Wang, Singh, Salame |

## 🌰 Conclusion

The FTX/Alameda scheme combined three manipulation mechanisms rarely seen operating simultaneously: code-embedded trading advantages that bypassed the exchange's own risk controls, circular token collateral that manufactured apparent solvency from thin air, and a deliberately constructed public persona that substituted reputation for genuine due diligence. Each mechanism reinforced the others — the "allow_negative" flag kept Alameda solvent long enough to maintain the FTT price floor; the FTT price floor kept Alameda's balance sheet credible; and SBF's public credibility kept institutional investors from scrutinizing either.

🌰 Key detection signals, now documented in regulatory findings:

- 🌰 Insider token concentration >88% of supply — headline market cap is a maintained fiction
- 🌰 Exchange-native token used as primary collateral by exchange's affiliated trading firm — circular, unverifiable valuation
- 🌰 Anomalously stable buy/sell ratios over extended periods — price floor maintenance, not price discovery
- 🌰 Volume spikes uncorrelated with price movement — internal order absorption
- 🌰 Founder's public persona as primary institutional due diligence substitute — credibility as collateral

## 🌰 References

- 🌰 CoinDesk. "Divisions in Sam Bankman-Fried's Crypto Empire Blur on His Trading Titan Alameda's Balance Sheet." November 2, 2022.
- 🌰 U.S. CFTC v. Samuel Bankman-Fried et al. Complaint and $12.7B Settlement Order. December 2022.
- 🌰 United States v. Samuel Bankman-Fried. S.D.N.Y. Indictment and Jury Verdict. December 2022; November 2023.
- 🌰 Caroline Ellison Plea Agreement and Allocution. S.D.N.Y., December 19, 2022.
- 🌰 John Ray III. Congressional Testimony, U.S. House Financial Services Committee. December 13, 2022.
- 🌰 Nansen Research. "FTX Collapse: On-Chain Analysis." November 2022.
- 🌰 Network Contagion Research Institute (NCRI). "Coordinated Inauthentic Behavior and Crypto Markets." 2022.
- 🌰 Inca Digital. FTX BTC wash trading volume analysis. Referenced in CFTC proceedings, 2022–2023.
- 🌰 FTX Bankruptcy Filing. Debtors' Schedules of Assets and Liabilities. Delaware, January 2023.
- 🌰 SEC v. Samuel Bankman-Fried. Civil Complaint. December 13, 2022.
- 🌰 dn-institute. "Uncovering Wash Trading and Market Manipulation on Huobi." August 2023.
- 🌰 CoinGecko / CryptoCompare. FTT and SOL historical price and volume data, November 2022.
