---
title: "FTX and Alameda Research: Anatomy of a $8 Billion Market Manipulation and Fraud Scheme"
date: 2022-11-02 — 2022-11-12
entities:
  - FTX
  - Alameda Research
  - Sam Bankman-Fried
  - FTT
  - Caroline Ellison
---

## Summary 🌰

1. FTX, once the world's third-largest cryptocurrency exchange, collapsed in November 2022 after it was revealed that its affiliated trading firm **Alameda Research** had been using **$8 billion in customer deposits** as its personal trading fund, enabled by a secret "allow negative" flag in FTX's codebase. 🌰
2. Alameda held an estimated **$5.82 billion in FTT tokens** (representing ~88% of circulating supply) on its balance sheet, using these self-issued tokens as collateral to borrow customer funds — a circular scheme that inflated FTT's apparent value while masking insolvency. 🌰
3. FTT price collapsed **77.5% in 48 hours** (from $24.10 on November 5 to $5.43 on November 8, 2022), with daily trading volume spiking from a $10.4M October average to **$603.5M on November 8** — a 58× increase that overwhelmed the artificial liquidity structure. 🌰
4. The CFTC's complaint documented that Alameda received **preferential treatment** on FTX including exemption from the exchange's auto-liquidation protocol, faster API access, and a virtually unlimited line of credit funded by customer deposits. 🌰
5. Sam Bankman-Fried was convicted on **seven federal charges** including wire fraud and conspiracy, and sentenced to **25 years in prison**. The FTX estate reached a **$12.7 billion settlement** with the CFTC — the largest in the agency's history. 🌰

## Background 🌰

### The FTX-Alameda Structure

FTX Trading Ltd. was a cryptocurrency derivatives exchange founded by Sam Bankman-Fried (SBF) and Gary Wang in 2019. Alameda Research, a quantitative trading firm founded by SBF in 2017, served as FTX's primary market maker. Despite public claims of separation, the two entities shared office space, personnel, and — critically — financial infrastructure.

FTT was FTX's native exchange token, launched in 2019. FTX promoted FTT through a "buy and burn" mechanism, using a portion of exchange revenue to purchase and destroy FTT tokens, theoretically creating deflationary pressure. By 2022, FTT had a reported market capitalization exceeding $3 billion.

### The Catalyst

On November 2, 2022, CoinDesk published a report revealing that Alameda Research's balance sheet was heavily concentrated in FTT tokens — not independent assets. This triggered a cascade of events:

- **November 6**: Binance CEO Changpeng Zhao (CZ) announced Binance would liquidate its FTT holdings (~$580M)
- **November 7**: FTX experienced $6 billion in withdrawal requests within 72 hours
- **November 8**: FTX halted withdrawals; Binance signed a non-binding acquisition letter, then withdrew
- **November 11**: FTX, Alameda Research, and 130 affiliated entities filed for Chapter 11 bankruptcy

## Market Manipulation: The FTT Circular Collateral Scheme 🌰

### The "Allow Negative" Flag

According to the CFTC complaint (Case 1:22-cv-10503, S.D.N.Y.), FTX's codebase contained a special flag for Alameda Research's account that allowed it to maintain a **negative balance** — effectively granting unlimited withdrawal privileges funded by other customers' deposits. No other FTX customer had this capability.

The CFTC documented that this arrangement enabled Alameda to:
- Withdraw customer funds without posting adequate collateral
- Avoid FTX's automatic liquidation engine that applied to all other traders
- Access a **virtually unlimited line of credit** backed by customer deposits

### FTT as Artificial Collateral 🌰

The SEC's complaint (Case 1:23-cv-01599) detailed how FTT tokens were used in a circular collateral scheme:

| Component | Detail |
|-----------|--------|
| FTT on Alameda's balance sheet | ~$5.82B (per CoinDesk report) |
| FTT circulating supply held by Alameda | ~88% |
| FTT used as collateral on FTX | Valued at market price |
| Actual liquidation value | Near zero (no independent buyers at scale) |

The scheme operated as follows:
1. FTX issued FTT tokens at minimal cost
2. Alameda accumulated the majority of FTT supply
3. Alameda posted FTT as collateral on FTX at inflated market prices
4. FTX accepted this collateral and extended credit (from customer deposits) to Alameda
5. Alameda used the borrowed funds for trading, venture investments, and political donations

This created a **reflexive loop**: FTT's price was sustained by limited circulating supply (since Alameda held most of it), and the inflated price justified larger collateral values, enabling more borrowing.

## On-Chain Volume Analysis 🌰

To quantify the market impact of FTX's collapse, we analyzed FTT daily trading volume data from CryptoCompare across three periods: pre-crisis (October 2022), crisis (November 1–14, 2022), and post-collapse (November 15 – December 31, 2022).

### Price and Volume Overview

{{< figure src="ftt-price-volume.png" alt="FTT Price and Trading Volume from January 2021 to January 2023" caption="FTT daily price (top) and trading volume (bottom), January 2021 – January 2023. The red-shaded region marks the November 2022 collapse." loading="lazy" >}}

The chart reveals several structural patterns:

- FTT reached its all-time high of **$79.70 on September 9, 2021**, during the broader crypto bull market
- Trading volume remained relatively stable throughout 2022 until the November crisis
- The volume spike during the collapse dwarfs all prior trading activity, indicating a complete breakdown of the artificial liquidity structure

### Crash Week Detail 🌰

{{< figure src="ftt-crash-detail.png" alt="FTT Price and Volume During November 2022 Crash" caption="Hour-by-hour view of FTT's collapse, November 1–15, 2022. The price dropped 77.5% in 48 hours while volume spiked 58×." loading="lazy" >}}

| Date | Close Price | Daily Volume | Event |
|------|------------|-------------|-------|
| Nov 1 | $25.85 | $10.8M | CoinDesk balance sheet report |
| Nov 5 | $24.10 | $17.9M | Pre-crash baseline |
| Nov 6 | $22.29 | $104.4M | CZ announces FTT liquidation |
| Nov 7 | $22.14 | $111.3M | $6B withdrawal requests |
| Nov 8 | $5.43 | $603.5M | FTX halts withdrawals |
| Nov 9 | $1.52 | $204.9M | Binance withdraws acquisition |
| Nov 10 | $3.73 | $32.5M | SBF apologizes on Twitter |
| Nov 11 | $2.60 | $14.5M | Chapter 11 bankruptcy filed |

The **November 8 volume spike to $603.5M** represents a 58× increase over the October average ($10.4M). This extreme volume concentration on a single day — coinciding with the withdrawal halt — indicates that the prior "normal" trading volumes were largely sustained by Alameda's market-making activity rather than genuine market participation.

### Volume Comparison by Period 🌰

{{< figure src="ftt-volume-comparison.png" alt="FTT Average Daily Volume Comparison by Period" caption="Average daily trading volume across three periods, showing the collapse of genuine liquidity after FTX's bankruptcy." loading="lazy" >}}

| Period | Avg Daily Volume | Relative to Pre-Crisis |
|--------|-----------------|----------------------|
| Pre-crisis (Oct 2022) | $10.4M | 1.00× (baseline) |
| Crisis (Nov 1–14) | $83.3M | 8.0× |
| Post-collapse (Nov 15–Dec 31) | $0.1M | 0.01× |

The post-collapse volume of **$0.1M per day** — a 99% decline from the pre-crisis level — reveals the true extent of artificial volume. When Alameda's market-making ceased, virtually all trading activity disappeared. This 100× volume ratio between pre-crisis and post-collapse periods is among the most extreme ever documented for a major exchange token.

## Market Manipulation Indicators 🌰

### Volume-Authenticity Disconnect

The 100× volume decline after Alameda ceased operations provides direct evidence that the majority of FTT's reported trading volume was generated by a single market maker with privileged access. In organic markets, the removal of one participant — even a major one — does not eliminate 99% of volume.

### Concentration Risk and Reflexivity

Alameda's ~88% control of FTT circulating supply created a market structure where:
- **Price discovery was illusory**: With one entity controlling supply, the "market price" reflected Alameda's willingness to sell, not genuine supply-demand equilibrium
- **Collateral values were circular**: FTT's price depended on Alameda not selling, but Alameda's solvency depended on FTT's price
- **Liquidation was impossible**: Any attempt to liquidate FTT holdings at scale would collapse the price, destroying the collateral value — exactly what occurred in November 2022

### Cross-Exchange Impact 🌰

FTX's collapse triggered contagion across the cryptocurrency market:
- Bitcoin fell 22% in the week following FTX's bankruptcy filing
- Total crypto market capitalization declined by approximately $200 billion
- Multiple FTX-linked entities (BlockFi, Genesis, Voyager) subsequently filed for bankruptcy
- The event accelerated regulatory action globally, including the EU's MiCA framework implementation

## Legal Proceedings and Outcomes 🌰

### Criminal Convictions

| Defendant | Role | Outcome |
|-----------|------|---------|
| Sam Bankman-Fried | FTX CEO, Alameda founder | Convicted on 7 charges, **25 years** prison (March 2024) |
| Caroline Ellison | Alameda CEO | Pled guilty, **2 years** prison (September 2024) |
| Gary Wang | FTX CTO | Pled guilty, no prison (cooperation) |
| Nishad Singh | FTX Engineering Director | Pled guilty, no prison (cooperation) |
| Ryan Salame | FTX co-CEO | Pled guilty, **7.5 years** prison |

### Regulatory Actions

- **CFTC**: Filed complaint November 2022; reached **$12.7 billion settlement** (largest in CFTC history) with the FTX estate in 2024
- **SEC**: Filed complaint December 2022 charging SBF with securities fraud; case resolved through criminal proceedings
- **DOJ**: Secured convictions against all five defendants between 2023–2024

### Creditor Recovery

The FTX bankruptcy estate, under CEO John J. Ray III, recovered sufficient assets to propose **full repayment** of customer claims at petition-date values (November 2022 prices), with distributions beginning in 2024. However, customers do not receive the appreciation in crypto prices since the bankruptcy filing.

## Conclusion 🌰

The FTX-Alameda collapse represents the largest documented case of market manipulation and fraud in cryptocurrency history. The scheme's core mechanism — using a self-issued token (FTT) as collateral to borrow customer funds through a privileged account flag — created a fragile structure that collapsed within days once external pressure (the CoinDesk report and CZ's liquidation announcement) disrupted the reflexive loop. 🌰

Our volume analysis quantifies the manipulation's scale: the **99% decline in FTT trading volume** after Alameda ceased operations demonstrates that virtually all prior market activity was artificial. The **58× volume spike on November 8** — the day withdrawals were halted — represents the moment when genuine sell pressure overwhelmed the artificial liquidity structure. 🌰

Key lessons for market surveillance: 🌰
1. **Single-entity volume dominance** is detectable through post-disruption volume analysis — genuine markets do not lose 99% of volume when one participant exits 🌰
2. **Circular collateral schemes** (issuing tokens → using as collateral → borrowing against them) create reflexive fragility that standard risk models fail to capture 🌰
3. **Privileged account access** (the "allow negative" flag) represents a systemic risk that exchange audits should specifically test for 🌰
4. **Token supply concentration** (88% held by one entity) is a leading indicator of price manipulation potential, detectable through on-chain analysis 🌰

## References

1. CFTC Complaint, Case 1:22-cv-10503 (S.D.N.Y., December 13, 2022). [PDF](https://www.cftc.gov/media/8076/enfftxtradingcomplaint121322/download)
2. SEC Complaint, Case 1:23-cv-01599 (S.D.N.Y., February 28, 2023). [PDF](https://www.sec.gov/files/litigation/complaints/2023/comp-pr2023-41.pdf)
3. DOJ Press Release: "Samuel Bankman-Fried Sentenced to 25 Years" (March 28, 2024). [Link](https://www.justice.gov/usao-sdny/pr/samuel-bankman-fried-sentenced-25-years-his-orchestration-multiple-fraudulent-schemes)
4. CoinDesk, "Divisions in Sam Bankman-Fried's Crypto Empire Blur on His Trading Titan Alameda's Balance Sheet" (November 2, 2022).
5. CFTC Press Release: "$12.7 Billion in Relief for FTX Customers" (2024). [Link](https://www.cftc.gov/PressRoom/PressReleases/8956-24)
6. CryptoCompare Historical Data API — FTT/USD daily OHLCV data. [Link](https://min-api.cryptocompare.com/)
