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

## 🌰 Level 1: Code-Level Privileges — The `allow_negative` Flag

The most concrete evidence of manipulation came from FTX's own codebase. The CFTC complaint (*CFTC v. Bankman-Fried et al.*, filed December 13, 2022) describes an "allow negative flag" that gave Alameda Research's accounts special treatment in FTX's trading engine. Code screenshots published during trial proceedings and reported by The Register (October 2023) identified the exact Python variable as `allow_negative` — a field that permitted Alameda's account balances to go negative without triggering the automatic liquidation protocols applied to every other user on the platform.

🌰 In practice, this flag meant:

- 🌰 Alameda could accumulate leveraged positions of effectively unlimited size without posting genuine collateral
- 🌰 During volatile markets, where retail traders were force-liquidated and had to sell, Alameda could hold — removing the natural sell pressure that would otherwise correct inflated prices
- 🌰 Alameda's risk was backstopped not by its own capital but by FTX's customer deposit pool

John Ray III, the bankruptcy administrator who replaced SBF, described the system to the U.S. House Financial Services Committee (December 13, 2022): Alameda had "the ability to maintain negative balances — in essence, an unlimited line of credit drawn against FTX customer assets." The CFTC confirmed the undisclosed borrowing facility exceeded **$8 billion** in customer funds (*CFTC v. Bankman-Fried*, December 2022; *In re FTX Trading Ltd.*, Case No. 22-11068, Delaware, 2022).

A second undisclosed advantage documented in SEC and DOJ filings: Alameda's API connections to FTX operated at lower latency than those available to external traders, enabling it to front-run large retail orders. The DOJ indictment (*U.S. v. Bankman-Fried*, S.D.N.Y., December 2022) estimated this generated approximately **$60 million** in additional profits from 2021 to 2022.

## 🌰 Level 2: Circular Token Collateral — Manufacturing FTT's Value

FTX issued its native exchange token, FTT, with a total supply of approximately 350 million tokens. Post-bankruptcy on-chain analysis by Nansen (*Blockchain Analysis: The Collapse of Alameda and FTX*, November 2022) established that FTX alone held approximately 80% of FTT supply. When Alameda's controlled vesting wallets are included, FTX and Alameda together controlled approximately **90% of all FTT** — leaving fewer than 35 million tokens freely trading on open markets.

{{< figure src="ftt-supply-distribution.png" caption="🌰 FTT token supply distribution at time of collapse. Approximately 90% was not freely floating — held by FTX, Alameda Research, or in Alameda-controlled vesting schedules. Sources: Nansen on-chain analysis, November 2022; FTX bankruptcy filings, In re FTX Trading Ltd., Case No. 22-11068." >}}

This concentration created a self-reinforcing circular collateral loop:

1. 🌰 FTX minted FTT and retained the dominant share
2. 🌰 FTX's buy-back program (funded by trading fees and, later, customer deposits) created a sustained price floor
3. 🌰 Alameda held FTT as its primary balance sheet asset — approximately **$5.8 billion** in FTT at the time of the CoinDesk disclosure (November 2, 2022)
4. 🌰 Alameda used this FTT to secure borrowing from third-party lenders and to justify its credit line from FTX itself
5. 🌰 The value of that collateral depended entirely on maintaining FTT's market price — which required the buy-back program — which required FTX's continued operation — funded by customer deposits

No external counterparty could independently verify the depth or liquidity behind FTT's headline market capitalization (~$9.6 billion at peak). The stated market cap was a function of a thin float and a managed price floor, not organic demand.

## 🌰 Level 3: Manufactured Legitimacy — SBF's Public Persona as Market Manipulation

🌰 A dimension of the FTX scheme that distinguishes it from conventional exchange manipulation is the deliberate construction of SBF's public credibility as a mechanism for sustaining token price and investor confidence. This is documented in Ellison's plea allocution and DOJ filings.

🌰 SBF cultivated an identity as a "philanthropist-trader" operating under the Effective Altruism (EA) philosophy — publicly donating to charitable causes, testifying before Congress as a credible regulatory voice, and maintaining a prominent media presence. His 2021–2022 Democratic-cycle political donations reached **$39.8 million** (OpenSecrets; CBS News, 2022), purchasing political access and public perception of legitimacy simultaneously.

🌰 This persona served direct market functions:

- 🌰 **Institutional investor confidence:** FTX raised $400 million in a Series C round (January 2022) at a valuation of approximately **$32 billion** from Sequoia Capital, BlackRock, Thoma Bravo, Paradigm, and others — all of whom later wrote their investments to zero (*Rabbitte v. Sequoia Capital et al.*, investor class action complaint, 2023). SBF's reputation substituted for genuine due diligence.
- 🌰 **FTT credibility:** Institutional holding of FTT was partially driven by confidence in the person behind the exchange. When the persona collapsed, so did the token.
- 🌰 **Regulatory capture attempt:** SBF's lobbying pushed for crypto regulations that would have formalized FTX's market position.

The Network Contagion Research Institute (NCRI) documented coordinated inauthentic activity in its report *Bot Driven Gold Rush* (2022), analyzing over **3 million tweets** and finding heavy bot-like amplification around Alameda-linked tokens preceding significant price increases — a pattern consistent with coordinated sentiment manipulation.

## 🌰 The Collapse: November 2022

On **November 2, 2022**, CoinDesk published Alameda's leaked balance sheet, revealing FTT as its primary asset. This was the first public signal that FTX's affiliated trading arm had no genuine capital base — only circular FTT holdings.

On **November 6**, Binance CEO CZ announced Binance would liquidate its entire FTT position, valued at approximately **$529 million** (Bloomberg, November 2022; 23 million FTT at prevailing prices). Alameda CEO Caroline Ellison publicly offered to buy Binance's FTT at **$22** in an attempt to defend the price floor — an admission that the price was being actively managed (Bloomberg, November 18, 2022). CZ declined.

{{< figure src="ftt-price-volume-nov2022.png" caption="🌰 FTT price (upper panel) and daily trading volume in millions USD (lower panel), October 31 to November 14, 2022. Volume spiked significantly above October averages on November 7–8 as forced selling overwhelmed the buy-back program. Price fell over 95% in five trading days. Price and volume data: CoinGecko / CryptoCompare." >}}

Key events in the collapse:

- 🌰 **Nov 6:** Price drops from ~$25.60 toward $22; Ellison's public bid to absorb Binance's FTT at $22 fails
- 🌰 **Nov 7:** Volume spikes sharply above October daily averages as panic selling accelerates
- 🌰 **Nov 8:** Price reaches ~$4.50; FTX halts customer withdrawals; Binance signs and then withdraws acquisition LOI within 24 hours after reviewing FTX's books
- 🌰 **Nov 9:** Price ~$2.10; CFTC and DOJ open investigations
- 🌰 **Nov 11:** Price ~$1.10; FTX, FTX US, and Alameda Research file for Chapter 11 bankruptcy; approximately **$6 billion** in withdrawal requests could not be fulfilled within 72 hours of the CoinDesk article (Reuters, November 8, 2022; confirmed in subsequent MIT Sloan case study, 2024)
- 🌰 **Nov 2023:** SBF convicted on all 7 counts; sentenced to **25 years** in prison with **$11 billion** in forfeiture ordered

The CFTC's final settlement against FTX entities totaled **$12.7 billion** — the largest in CFTC history.

## 🌰 Contagion: Correlated Sell-off in SBF-Affiliated Assets

Alameda held concentrated positions in Solana (SOL) ecosystem tokens, reflecting SBF's early and prominent public advocacy for Solana. As Alameda's insolvency became clear, forced liquidations of its holdings drove SOL down in parallel with FTT.

{{< figure src="ftt-sol-correlated-collapse.png" caption="🌰 Parallel price decline of FTT and SOL, October 31 to November 14, 2022. SOL fell approximately 65% (from ~$32 to ~$11) over the same period as FTT's near-total collapse — driven by Alameda's concentrated portfolio liquidations. Price data: CoinGecko." >}}

The correlation illustrates a structural risk in concentrated insider token holdings: a single actor's balance sheet unwind forces simultaneous selling across all correlated positions, amplifying the market impact far beyond the immediately affected token.

## 🌰 Market Health Indicators: Anomalies in FTT Trading Data

Several market health signals were anomalous in FTT's trading data preceding the collapse:

🌰 **Benford's Law deviations in order size distribution:** FTT order flow on FTX exhibited lower-digit clustering inconsistent with organically distributed retail activity — a pattern identified by dn-institute's analysis of Huobi (2023) as characteristic of algorithmically maintained order books. The buy-back program, operating on a fee-driven schedule, necessarily introduced non-random periodicity into order sizes.

🌰 **Abnormal buy/sell ratio stability:** FTT's buy-to-sell volume ratio on FTX remained unusually consistent across extended periods — a pattern incompatible with genuine price discovery. This stability is consistent with Alameda systematically absorbing sell pressure to maintain the price floor, functioning as a hidden market maker on the exchange it partially owned.

🌰 **Volume uncorrelated with price movement:** Inca Digital's analysis *Abnormal Trading Volumes on FTX* documented volume spikes that produced weak or no corresponding price movement — a classic indicator of internally absorbed order flow consistent with wash trading, where Alameda served as the primary counterparty absorbing retail sell orders without allowing price to adjust.

🌰 **Market depth vs. market cap divergence:** At FTT's peak market capitalization of ~$9.6 billion, the effective float was fewer than 35 million tokens. Any attempt to sell even 1–2% of circulating supply would have moved the price dramatically — a fragility structurally concealed by the dominant holders' incentive to prevent selling at all costs.

## 🌰 Regulatory Outcomes

| Action | Body | Case / Reference | Outcome |
|--------|------|-----------------|---------|
| Criminal conviction | DOJ (S.D.N.Y.) | *U.S. v. Bankman-Fried*, Dec. 2022 | 25 years; $11B forfeiture |
| Civil complaint | CFTC | *CFTC v. Bankman-Fried et al.*, Dec. 13, 2022 | $12.7B settlement (CFTC record) |
| Civil complaint | SEC | *SEC v. Ellison and Wang*, Dec. 21, 2022 | Ongoing / settled |
| Guilty pleas | DOJ | Ellison, Wang, Singh, Salame | Cooperation agreements |
| Bankruptcy | Delaware | *In re FTX Trading Ltd.*, No. 22-11068 | Ongoing creditor repayment |

## 🌰 Conclusion

The FTX/Alameda scheme combined three manipulation mechanisms rarely seen operating simultaneously: code-embedded trading advantages that bypassed the exchange's own risk controls, circular token collateral that manufactured apparent solvency, and a deliberately constructed public persona that substituted reputation for due diligence. Each mechanism reinforced the others — the `allow_negative` flag kept Alameda solvent long enough to maintain the FTT price floor; the FTT price floor kept Alameda's balance sheet credible; and SBF's public credibility kept institutional investors from scrutinizing either.

🌰 Key detection signals, now documented in regulatory findings:

- 🌰 Insider token concentration ~90% of supply — headline market cap was a maintained fiction
- 🌰 Exchange-native token used as primary collateral by the exchange's own affiliated trading firm — circular, unverifiable valuation
- 🌰 Anomalously stable buy/sell ratios over extended periods — price floor maintenance, not price discovery
- 🌰 Volume spikes uncorrelated with price movement — internal order absorption consistent with wash trading
- 🌰 Founder's public persona as primary institutional due diligence substitute — reputation deployed as collateral

## 🌰 References

- 🌰 CoinDesk. "Divisions in Sam Bankman-Fried's Crypto Empire Blur on His Trading Titan Alameda's Balance Sheet." November 2, 2022.
- 🌰 CFTC. *CFTC v. Samuel Bankman-Fried et al.* Complaint. December 13, 2022.
- 🌰 SEC. *SEC v. Caroline Ellison and Gary Wang.* Complaint. December 21, 2022.
- 🌰 DOJ. *United States v. Samuel Bankman-Fried.* S.D.N.Y. Indictment. December 2022; Conviction November 2023; Sentencing March 2024.
- 🌰 U.S. Bankruptcy Court, D. Delaware. *In re FTX Trading Ltd.* Case No. 22-11068 (JTD). 2022–ongoing.
- 🌰 John Ray III. Congressional Testimony. U.S. House Financial Services Committee. December 13, 2022.
- 🌰 Nansen. "Blockchain Analysis: The Collapse of Alameda and FTX." November 2022.
- 🌰 Network Contagion Research Institute (NCRI). *Bot Driven Gold Rush.* 2022.
- 🌰 Inca Digital. "Abnormal Trading Volumes on FTX." 2022–2023.
- 🌰 Bloomberg. "FTX's Point of No Return Was Ellison's Tweet, Trade Data Show." November 18, 2022.
- 🌰 Reuters. "Crypto exchange FTX saw $6 bln withdrawals in 72 hours." November 8, 2022.
- 🌰 The Register. "FTX Python code: allow_negative flag." October 10, 2023.
- 🌰 dn-institute. "Uncovering Wash Trading and Market Manipulation on Huobi." August 2023.
- 🌰 CoinGecko. FTT and SOL historical price data, November 2022.
