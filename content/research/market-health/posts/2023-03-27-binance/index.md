---
title: "Binance: Wash Trading, Regulatory Evasion, and the $4.3 Billion Settlement"
date: 2023-03-27 — 2023-12-18
entities:
  - Binance
  - Changpeng Zhao
  - BNB
  - Sigma Chain
  - Merit Peak
  - BAM Trading
---

## Summary 🌰

1. The CFTC filed a complaint on March 27, 2023, alleging that Binance — the world's largest cryptocurrency exchange — knowingly operated an illegal derivatives exchange while actively helping U.S. customers evade compliance controls using VPNs and shell companies. 🌰
2. The SEC's June 2023 complaint revealed that **Sigma Chain**, a trading firm secretly owned by CZ, conducted **wash trading on Binance.US** to artificially inflate volume during the platform's early days, while another CZ-controlled entity, **Merit Peak**, commingled **billions of dollars** in customer funds. 🌰
3. CZ pleaded guilty to federal charges on November 21, 2023, resulting in a combined **$4.3 billion settlement** — comprising $2.85 billion to the CFTC (including $1.35 billion in disgorgement and a $150 million personal penalty for CZ) and $1.8 billion in criminal fines to the DOJ. 🌰
4. BNB trading volume declined **47%** after the SEC charges (from $16.4M to $8.7M average daily volume), but recovered to $19.9M after the settlement — indicating that regulatory resolution restored market confidence despite the severity of the violations. 🌰
5. The case established a precedent as the **largest criminal resolution** in the history of the U.S. Treasury Department, with parallel enforcement actions from the CFTC, SEC, DOJ, FinCEN, and OFAC. 🌰

## Background 🌰

### Binance's Corporate Structure

Binance was founded by Changpeng Zhao (CZ) in 2017 and rapidly grew to become the world's largest cryptocurrency exchange by trading volume. Unlike traditional financial institutions, Binance deliberately avoided establishing a formal headquarters, operating through a web of affiliated entities across multiple jurisdictions.

In 2019, Binance launched Binance.US through BAM Trading Services, ostensibly as an independent, U.S.-compliant platform. The SEC later alleged that this separation was illusory — CZ maintained control over both platforms, and Binance.US served primarily as a regulatory shield while Binance continued to serve U.S. customers on its main platform.

### Key Entities

| Entity | Role | Control |
|--------|------|---------|
| Binance Holdings Ltd. | Global exchange operator | CZ (CEO) |
| BAM Trading Services | Binance.US operator | Nominally independent; SEC alleges CZ control |
| Sigma Chain AG | Market maker on Binance.US | Secretly owned by CZ |
| Merit Peak Ltd. | Fund management | CZ-controlled; commingled customer funds |

## Wash Trading: The Sigma Chain Operation 🌰

### SEC Allegations

The SEC's complaint (Case 1:23-cv-01599, S.D.N.Y., June 5, 2023) detailed how Sigma Chain AG — a Swiss-registered trading firm secretly owned by CZ — served as the primary market maker on Binance.US and engaged in wash trading to create the illusion of liquid, active markets.

According to the complaint, Sigma Chain:
- Was onboarded as a market maker on Binance.US at CZ's direct instruction
- Engaged in **wash trading** by simultaneously placing buy and sell orders that matched against each other
- Artificially inflated trading volumes during Binance.US's critical early growth period
- Operated without disclosure of its relationship to CZ or Binance

The wash trading was strategically targeted: it concentrated on trading pairs where Binance.US needed to demonstrate sufficient liquidity to attract retail customers and compete with established U.S. exchanges.

### Customer Fund Commingling 🌰

The SEC further alleged that Merit Peak Ltd., another CZ-controlled entity, received **billions of dollars** in transfers from accounts holding Binance.US customer funds. These funds were commingled in accounts at Silvergate Bank, violating U.S. regulations requiring segregation of customer assets.

Reuters independently confirmed through bank records that CZ's head of back office was the primary operator for five Binance.US bank accounts, including one holding American customer funds.

## Regulatory Evasion: VPNs and Shell Companies 🌰

### CFTC Findings

The CFTC complaint (Case 1:23-cv-01887, N.D. Ill.) documented a systematic effort to evade U.S. regulations while retaining access to U.S. customers and their capital:

- **VPN Instructions**: Binance employees instructed U.S. customers to use virtual private networks to mask their location and continue trading on the global platform
- **Shell Company Accounts**: VIP customers with U.S.-based beneficial owners were directed to open accounts under newly incorporated offshore shell companies
- **Compliance Theater**: CZ acknowledged internally that compliance controls were performative. In one communication, he stated the need to "word [the popup] very carefully so that we let people know what they need to do, including using a VPN, without explicitly stating it"
- **Deliberate Sabotage**: The CFTC found that CZ and senior management "intentionally sabotaged and subverted Binance's superficial compliance controls"

A senior compliance officer wrote internally: "If US users get on .com, we become subjected to the following US regulators, FinCEN, OFAC and SEC… we try to ask our US users to use VPN / or ask them to provide (if they are an entity) non-US documents / On the surface we cannot be seen to have US users but in reality, we should get them through other creative means."

## On-Chain Volume Analysis 🌰

To quantify the market impact of the regulatory actions against Binance, we analyzed BNB daily trading volume data from CryptoCompare across four regulatory periods in 2023.

### Price and Volume Overview

{{< figure src="bnb-price-volume.png" alt="BNB Price and Trading Volume with Regulatory Event Markers" caption="BNB daily price and trading volume, January 2022 – January 2024. Red dashed lines mark the CFTC complaint (March 27), SEC charges (June 5), and CZ guilty plea (November 21)." loading="lazy" >}}

The chart reveals a clear pattern of regulatory impact on BNB trading activity. Each enforcement action created a distinct volume spike followed by a period of reduced baseline activity, with the SEC's 13 charges producing the most sustained volume depression.

### Volume Comparison by Regulatory Period 🌰

{{< figure src="bnb-volume-comparison.png" alt="BNB Average Daily Volume by Regulatory Period" caption="Average daily BNB trading volume across four regulatory periods in 2023, showing the impact of successive enforcement actions." loading="lazy" >}}

| Period | Avg Daily Volume | Change from Baseline |
|--------|-----------------|---------------------|
| Pre-CFTC (Jan–Mar 2023) | $16.4M | Baseline |
| CFTC–SEC gap (Mar–Jun 2023) | $13.8M | −16% |
| Post-SEC (Jun–Nov 2023) | $8.7M | −47% |
| Post-Settlement (Nov–Dec 2023) | $19.9M | +21% |

The **47% volume decline** after the SEC charges represents the market's assessment of existential regulatory risk. The subsequent **recovery to $19.9M** after CZ's guilty plea and settlement demonstrates that regulatory certainty — even negative certainty — is preferable to uncertainty for market participants.

### Settlement Week Detail 🌰

{{< figure src="bnb-settlement-detail.png" alt="BNB Price and Volume During CZ Guilty Plea" caption="BNB price and volume during November–December 2023, showing the market reaction to CZ's guilty plea and the $4.3 billion settlement." loading="lazy" >}}

On November 21, 2023 — the day CZ pleaded guilty — BNB daily volume spiked to **$88.9M**, a 10× increase over the preceding week's average. Despite the severity of the charges, BNB price stabilized around $230 and subsequently recovered, reflecting the market's view that the settlement removed the worst-case scenario of a forced shutdown.

## Legal Proceedings and Outcomes 🌰

### Multi-Agency Enforcement

The Binance case is unprecedented in involving **five U.S. agencies** simultaneously:

| Agency | Action | Outcome |
|--------|--------|---------|
| CFTC | Civil complaint (Mar 2023) | $2.85B settlement ($1.35B disgorgement + $150M CZ penalty) |
| SEC | 13 charges (Jun 2023) | Majority of claims allowed to proceed; ongoing |
| DOJ | Criminal charges | CZ guilty plea; $1.8B criminal fine |
| FinCEN | AML violations | $3.4B penalty (largest in FinCEN history) |
| OFAC | Sanctions violations | $968M settlement |

Note: The DOJ, FinCEN, and OFAC penalties overlap and are partially concurrent, resulting in a combined total of approximately **$4.3 billion**.

### CZ's Sentence

CZ was sentenced to **four months in prison** in April 2024 — significantly less than the 18 months prosecutors requested. He also stepped down as Binance CEO, replaced by Richard Teng. CZ was released in September 2024.

### Binance Remediation

As part of the settlement, Binance agreed to:
- Appoint an independent compliance monitor for three years
- Complete offboarding of all U.S. users from the global platform
- Implement enhanced KYC/AML controls including blockchain monitoring
- Conduct annual enterprise-wide risk assessments
- Cooperate with ongoing law enforcement investigations

## Market Manipulation Indicators 🌰

The Binance case reveals several manipulation patterns relevant to market surveillance:

### Wash Trading Through Affiliated Market Makers

Sigma Chain's wash trading on Binance.US demonstrates how exchange operators can use secretly affiliated entities to inflate volume. Unlike independent wash trading by third parties, exchange-affiliated wash trading is particularly dangerous because:
- The exchange controls order matching and can ensure wash trades execute efficiently
- The affiliated entity has access to privileged information about order flow
- The artificial volume directly benefits the exchange's business metrics

### Volume as a Regulatory Signal

Our analysis shows that BNB trading volume served as a real-time indicator of regulatory risk perception:
- The **47% post-SEC decline** quantifies the market's assessment of existential risk
- The **post-settlement recovery** demonstrates that resolution — even with $4.3B in penalties — was preferable to uncertainty
- This pattern contrasts sharply with FTX, where volume collapsed permanently because the exchange ceased to exist

## Conclusion 🌰

The Binance enforcement action represents the most comprehensive multi-agency regulatory response to cryptocurrency market manipulation to date. The case documented three distinct categories of misconduct: wash trading through the secretly affiliated Sigma Chain, customer fund commingling through Merit Peak, and systematic regulatory evasion through VPN instructions and shell company structures. 🌰

Our volume analysis quantifies the market impact: the **47% decline in BNB trading volume** after the SEC charges demonstrates that regulatory action materially affects market participation. The subsequent **recovery after settlement** illustrates a key difference from the FTX collapse — Binance survived because its underlying business was operational, whereas FTX's volume was largely artificial. 🌰

Key lessons for market surveillance: 🌰
1. **Affiliated market makers** require mandatory disclosure and monitoring — Sigma Chain's undisclosed relationship to CZ enabled wash trading that would have been flagged under standard conflict-of-interest rules 🌰
2. **Cross-entity fund flows** between exchange operators and affiliated entities are a leading indicator of customer fund misappropriation 🌰
3. **Volume response to regulatory events** provides a quantitative measure of how much reported activity is genuine versus artificial 🌰
4. **Internal communications** remain the most powerful evidence — CZ's VPN instructions and compliance officers' candid assessments proved more damaging than any quantitative analysis 🌰

## References

1. CFTC Complaint, Case 1:23-cv-01887 (N.D. Ill., March 27, 2023). [PDF](https://www.cftc.gov/media/8351/enfbinancecomplaint032723/download)
2. SEC Complaint, Case 1:23-cv-01599 (S.D.N.Y., June 5, 2023). [PDF](https://www.sec.gov/files/litigation/complaints/2023/comp-pr2023-101.pdf)
3. CFTC Press Release: "Binance and Zhao Agree to Pay $2.85 Billion." [Link](https://www.cftc.gov/PressRoom/PressReleases/8825-23)
4. CFTC Press Release: "Federal Court Enters Order Against Binance and Former CEO." [Link](https://www.cftc.gov/PressRoom/PressReleases/8837-23)
5. SEC Press Release 2023-101: "SEC Files 13 Charges Against Binance." [Link](https://www.sec.gov/newsroom/press-releases/2023-101-sec-files-13-charges-against-binance-entities-founder-changpeng-zhao)
6. OFAC Settlement with Binance Holdings, Ltd. (November 21, 2023). [PDF](https://ofac.treasury.gov/system/files/2023-11/20231121_binance.pdf)
7. CryptoCompare Historical Data API — BNB/USD daily OHLCV data. [Link](https://min-api.cryptocompare.com/)

