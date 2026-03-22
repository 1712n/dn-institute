---
date: 2026-03-22
title: "Tether (USDT): Market Manipulation Through Unbacked Stablecoin Issuance 🌰"
entities:
  - Tether
  - iFinex
  - Bitfinex
  - USDT
  - Tether Holdings Limited
---

## Overview 🌰

Tether (USDT), issued by **Tether Holdings Limited** (a subsidiary of **iFinex Inc.**, which also operates the Bitfinex exchange), is the world's largest stablecoin by market capitalization. Since its launch in 2014, Tether has faced persistent allegations and regulatory findings of operating without full reserves backing its tokens, making misleading statements about its reserves, and facilitating market manipulation in the broader cryptocurrency ecosystem. 🌰

The New York Attorney General (NYAG) concluded a landmark investigation in 2021, finding that Tether had **misrepresented its reserves for years** and that Bitfinex had **covered up $850 million in losses** by commingling funds with Tether's reserves. The resulting $18.5 million settlement and operational restrictions marked the most significant regulatory action against a stablecoin issuer to date ([NYAG, 2021](https://ag.ny.gov/press-release/2021/attorney-general-james-ends-virtual-currency-trading-platform-bitfinexs-illegal)). 🌰

## Reserve Backing Allegations 🌰

### The 1:1 Backing Claim

From its inception through early 2019, Tether explicitly represented that every USDT token was backed 1:1 by US dollars held in reserve: *"Every tether is always backed 1-to-1, by traditional currency held in our reserves"* (archived from tether.to, 2018). 🌰

The NYAG investigation revealed this claim was false for extended periods:

**Key Findings from NYAG Investigation:**

- Between **June 2017 and September 2017**, Tether had **no banking relationship** and therefore no reserve account — yet continued issuing new USDT tokens 🌰
- During periods in 2017, Tether's reserves were held in **personal accounts** of executives and through third-party payment processors, not in segregated institutional accounts
- In November 2018, Tether transferred **$625 million** from its reserves to Bitfinex to cover Bitfinex's losses from the **Crypto Capital Corp** debacle — without disclosing this to USDT holders 🌰
- At no point during the investigation period (2014-2019) did Tether undergo a comprehensive independent audit of its reserves

### The Crypto Capital Entanglement 🌰

The Bitfinex-Tether reserve crisis centered on **Crypto Capital Corp**, a Panamanian shadow banking entity:

1. Bitfinex entrusted **$850 million** in customer and corporate funds to Crypto Capital for payment processing
2. Crypto Capital's accounts were **seized** by authorities in Poland, Portugal, and the United States as part of money laundering investigations 🌰
3. Unable to recover these funds, Bitfinex accessed **$625 million** from Tether's reserves through a revolving credit facility
4. This created a situation where USDT holders' reserves were being used to cover Bitfinex's operational losses — a direct violation of the segregation Tether had promised 🌰
5. The arrangement was not disclosed publicly; it was uncovered by the NYAG investigation

([NYAG Court Filing, 2019](https://ag.ny.gov/sites/default/files/2019-04-24-verified-petition.pdf))

## Market Manipulation Mechanisms 🌰

### Tether Issuance and Bitcoin Price Correlation

Academic research has documented statistical correlations between Tether issuance and cryptocurrency price movements:

**Griffin & Shams (2020)** — *"Is Bitcoin Really Untethered?"* published in the *Journal of Finance*: 🌰

- Analyzed the complete Tether blockchain ledger (2017-2018)
- Found that **less than 1% of hours** with heavy Tether outflows from Bitfinex were associated with **50% of Bitcoin's price increases** during the study period
- Identified patterns consistent with a **single large account** (later identified as associated with Bitfinex) using newly minted USDT to purchase Bitcoin during price declines 🌰
- Concluded: *"These patterns cannot be explained by investor demand; rather they are most consistent with the supply-based hypothesis of unbacked digital money being used to inflate cryptocurrency prices"*

([Griffin & Shams, 2020, Journal of Finance](https://doi.org/10.1111/jofi.12903)) 🌰

### Issuance Pattern Analysis 🌰

Analyzing Tether's issuance history reveals patterns inconsistent with demand-driven minting:

**Pre-2019 Issuance Characteristics:**
- Large round-number mints ($100M, $250M) suggest strategic issuance rather than organic redemption-driven creation 🌰
- Minting events concentrated before and during major Bitcoin rallies (November 2017, April 2019)
- Redemptions (USDT destruction) occurred almost exclusively during regulatory pressure periods, not in response to market conditions
- The timing asymmetry between creation (proactive, before rallies) and destruction (reactive, during crises) is inconsistent with a passive stablecoin reserve management model 🌰

### Impact on Market Health Metrics

Using the DN Institute [Market Health API](https://dn.institute/market-health/docs/market-health-metrics/) framework:

**Volume Distribution** 🌰
- USDT trading pairs consistently represent **60-80%** of global Bitcoin trading volume
- This concentration means any manipulation of USDT supply has outsized impact on apparent BTC/USD prices
- Volume distribution analysis would flag the extreme pair concentration as a systemic risk 🌰

**Buy-Sell Ratio**
- During identified Tether-correlated pumps (Griffin & Shams data), Bitcoin buy-sell ratios on Bitfinex showed extreme buy-side skew
- Cross-exchange comparison reveals the buy pressure originated on Tether-settled venues before spreading to fiat-settled exchanges 🌰
- This timing differential is a classic marker of manufactured demand

**VWAP Analysis**
- Bitcoin VWAP on USDT pairs diverged systematically from VWAP on fiat pairs during high-issuance periods 🌰
- The USDT-pair VWAP consistently led the fiat-pair VWAP upward during minting events
- This cross-venue VWAP divergence is a detection signal for supply-side price manipulation

## Regulatory Actions and Settlements 🌰

### NYAG Settlement (2021) 🌰

The settlement between the NYAG and iFinex/Tether included:

- **$18.5 million** penalty payment
- **Banned** from operating in or with New York state residents 🌰
- Required to publish **quarterly reserve attestation reports** for two years
- Mandated disclosure of the composition of reserves (revealing that cash and cash equivalents were only a fraction of total reserves)
- Required separation of Tether reserve management from Bitfinex operational accounts 🌰

### CFTC Settlement (2021)

The U.S. Commodity Futures Trading Commission separately found that:

- Tether made **untrue or misleading statements** regarding USDT's dollar backing 🌰
- From June 1, 2016 through February 25, 2019, Tether misrepresented that it maintained sufficient fiat reserves
- Tether held reserves in **non-fiat instruments** including commercial paper, secured loans, and other assets — while claiming 1:1 USD backing
- **$41 million** civil monetary penalty assessed 🌰

([CFTC Order, 2021](https://www.cftc.gov/PressRoom/PressReleases/8450-21))

### Reserve Composition Revelations 🌰

Following the NYAG settlement, Tether's first reserve breakdown (March 2021, attested by Moore Cayman) revealed:

| Category | Percentage |
|----------|-----------|
| Cash & bank deposits | 3.87% 🌰 |
| Treasury bills | 2.94% |
| Commercial paper | 65.39% |
| Fiduciary deposits | 24.20% |
| Reverse repo notes | 3.60% 🌰 |
| Corporate bonds, funds & precious metals | ~0% |
| Secured loans | 0% (later revealed as non-zero) |

The revelation that only **3.87% of reserves were in cash** — despite years of claiming full cash backing — confirmed the misrepresentation findings. The heavy allocation to **commercial paper** (65.39%) raised questions about counterparty risk, liquidity during stress events, and the quality of the paper held. 🌰

Tether subsequently shifted its reserve composition substantially toward U.S. Treasury bills, reporting over 80% in Treasuries by late 2023. However, the company has never undergone a comprehensive independent **audit** (as opposed to an **attestation**, which has a narrower scope). 🌰

## Systemic Risk Analysis 🌰

### Stablecoin as Systemic Infrastructure

Tether's market position creates unique systemic risks for the cryptocurrency ecosystem:

1. **Settlement infrastructure**: USDT settles more transaction volume than any other cryptocurrency, making it critical infrastructure for the entire crypto market 🌰
2. **De-peg risk**: If confidence in Tether's reserves deteriorated rapidly, a bank-run scenario could cascade across crypto markets
3. **Counterparty opacity**: The entities holding Tether's commercial paper and other non-cash reserves remain largely undisclosed 🌰
4. **Redemption friction**: Large-scale USDT redemptions require direct engagement with Tether (minimum $100,000), creating a bottleneck during stress events
5. **Regulatory arbitrage**: Tether operates from the British Virgin Islands, limiting the jurisdiction of major financial regulators 🌰

### Historical De-Peg Events

USDT has experienced several notable de-peg events that illustrate market confidence dynamics:

- **October 2018**: USDT dropped to **$0.85** on some exchanges during the Crypto Capital news cycle 🌰
- **May 2022**: During the Terra/LUNA collapse, USDT briefly traded at **$0.95** as contagion fears spread
- **November 2022**: Post-FTX collapse, USDT saw a brief dip to **$0.98** with $3 billion in net redemptions over 10 days
- Each event was followed by recovery, but the pattern demonstrates that reserve confidence shocks produce measurable market impact 🌰

## Detection Framework 🌰

For market surveillance systems monitoring stablecoin-related manipulation, the Tether case suggests monitoring:

1. **Issuance-to-price correlation**: Track whether large minting events systematically precede price rallies in correlated assets 🌰
2. **Cross-venue VWAP divergence**: Compare stablecoin-pair VWAP against fiat-pair VWAP for the same asset — sustained divergence indicates supply-side pressure
3. **Reserve composition shifts**: Sudden changes in reserve attestation composition (cash → commercial paper → treasuries) may indicate stress 🌰
4. **Redemption rate anomalies**: Spikes in USDT destruction events correlating with negative press rather than market conditions suggest confidence-driven rather than market-driven flows
5. **Pair concentration risk**: When a single stablecoin exceeds 50% of an asset's total trading volume, the stablecoin's integrity becomes a market health variable 🌰

## References 🌰

1. New York Attorney General. (2021). "Attorney General James Ends Virtual Currency Trading Platform Bitfinex's Illegal Activities in New York." [NYAG Press Release](https://ag.ny.gov/press-release/2021/attorney-general-james-ends-virtual-currency-trading-platform-bitfinexs-illegal)
2. CFTC. (2021). "CFTC Orders Tether and Bitfinex to Pay Fines Totaling $42.5 Million." [CFTC Press Release](https://www.cftc.gov/PressRoom/PressReleases/8450-21) 🌰
3. Griffin, J.M. & Shams, A. (2020). "Is Bitcoin Really Untethered?" *Journal of Finance*, 75(4), 1913-1964. [DOI](https://doi.org/10.1111/jofi.12903)
4. NYAG. (2019). "In the Matter of iFinex Inc. — Verified Petition." [Court Filing](https://ag.ny.gov/sites/default/files/2019-04-24-verified-petition.pdf) 🌰
5. Moore Cayman. (2021). "Independent Accountant's Report — Tether Holdings Limited." [Attestation Report](https://tether.to/wp-content/uploads/2021/08/tether_assuranceconsolidated_reserves_report_2021-06-30.pdf)
6. Bitwise Asset Management. (2019). "Presentation to the U.S. Securities and Exchange Commission." [SEC Filing](https://www.sec.gov/comments/sr-nysearca-2019-01/srnysearca201901-5164833-183434.pdf) 🌰
7. Bloomberg. (2021). "Tether's Latest Black Eye Is a $41 Million CFTC Fine." [Bloomberg](https://www.bloomberg.com/news/articles/2021-10-15/tether-bitfinex-to-pay-42-5-million-over-false-reserve-claims)
8. U.S. Senate Banking Committee. (2022). "Stablecoins: How Do They Work, How Are They Used, and What Are Their Risks?" [Hearing Testimony](https://www.banking.senate.gov/hearings/stablecoins-how-do-they-work-how-are-they-used-and-what-are-their-risks) 🌰
