---
title: "Terra/Luna: $45 Billion Algorithmic Stablecoin Collapse, Anchor Protocol's Unsustainable Yields, and Industry-Wide Contagion"
date: 2026-02-12
entities:
  - Terraform Labs
  - LUNA
  - UST
---

## Summary

1. **$45 billion wiped out in one week**: Between May 7 and May 13, 2022, the combined market capitalization of LUNA and UST collapsed from approximately $45 billion to near zero, as the algorithmic stablecoin UST lost its dollar peg and LUNA entered a hyperinflationary death spiral.
2. **Algorithmic design failure**: UST maintained its peg through a mint-and-burn mechanism with LUNA — users could always redeem 1 UST for $1 of LUNA — but this reflexive design meant that once confidence broke, redemptions caused LUNA to hyperinflate from $87 to $0.0005 (a 99.9999% decline) in eight days.
3. **72% concentrated in one protocol**: At its peak, 72% of all circulating UST ($17.15 billion) was deposited in Anchor Protocol to earn ~19.5% APY — a yield subsidized by Terraform Labs that was being depleted at $6 million per day by April 2022.
4. **$4.47 billion SEC settlement**: A jury found Terraform Labs and Do Kwon liable for securities fraud in April 2024 after less than two hours of deliberation, resulting in a $4.47 billion consent judgment — though Terraform's January 2024 bankruptcy filing rendered the judgment largely uncollectable.
5. **15-year prison sentence**: Do Kwon was arrested in Montenegro in March 2023 on a forged Costa Rican passport, extradited to the United States in December 2024, pleaded guilty to fraud in August 2025, and was sentenced to 15 years in federal prison in December 2025.

## Background

### Terraform Labs and Founders

Terraform Labs was co-founded in **January 2018** in Singapore by **Do Kwon** (Kwon Do-hyeong) and **Daniel Shin**. Do Kwon held a B.S. in Computer Science from Stanford and had previously worked at Microsoft and Apple. Shin, a Wharton graduate, had founded Ticket Monster (acquired by Groupon in 2014 for $260 million) [1].

On May 11, 2022 — during the collapse — Do Kwon was revealed to have been a co-founder of the previously failed algorithmic stablecoin project **Basis Cash** under the pseudonym **"Rick Sanchez"**. Basis Cash launched on Ethereum in late 2020 and failed to maintain its dollar peg before being abandoned.

Terraform Labs raised over **$200 million** from investors including Arrington Capital, Coinbase Ventures, Galaxy Digital, and Lightspeed Venture Partners.

### The UST-LUNA Mechanism

TerraUSD (UST) was an **algorithmic stablecoin** with no dollar reserves. It maintained its peg through a two-token mint-and-burn mechanism [2]:

- **To mint 1 UST**: Burn $1 worth of LUNA (reducing LUNA supply)
- **To redeem 1 UST**: Burn 1 UST and receive $1 worth of LUNA (increasing LUNA supply)
- **Peg maintenance**: If UST dropped below $1, arbitrageurs could buy cheap UST, burn it for $1 of LUNA, sell the LUNA, and pocket the difference — buying pressure restored the peg

This system was **reflexive**: UST's stability depended on confidence in LUNA's value, and LUNA's value derived from demand for UST. There was no hard collateral backstop.

**LUNA** reached an all-time high of approximately **$119.18 on April 5, 2022**, with a market capitalization approaching $40 billion. UST's circulating supply peaked at approximately **$18.5 billion**, making it the third-largest stablecoin.

### Luna Foundation Guard (LFG)

In **February 2022**, Do Kwon established the **Luna Foundation Guard** to accumulate Bitcoin as an emergency reserve. By May 7, 2022, LFG held **80,394 BTC** worth approximately $3.5 billion [3].

## The Collapse: May 7–13, 2022

### Day-by-Day Timeline

**May 7, 2022 (Saturday):**
- Two large wallet addresses withdrew **375 million UST** from Anchor Protocol
- An **85 million UST** swap for 84.5 million USDC was detected on Curve Finance
- UST briefly depegged to **$0.985**
- LFG had earlier withdrawn **150 million UST** from the Curve 3pool to prepare a liquidity migration to a new 4pool, temporarily reducing pool depth

**May 8, 2022 (Sunday):**
- LFG announced it would loan **$750 million in BTC** to market makers to defend the peg, plus $750 million in UST to buy back BTC after stabilization
- LFG transferred over **50,000 BTC** to trading counterparties

**May 9, 2022 (Monday):**
- UST lost its peg decisively, falling as low as **$0.35**
- Anchor Protocol deposits collapsed from **$14 billion to below $9 billion**
- LUNA dropped from approximately $61 to under $30

**May 10–11, 2022:**
- UST hovered around $0.50–$0.60
- Massive UST-to-LUNA redemptions caused LUNA supply to explode through hyperinflationary minting

**May 12, 2022:**
- LUNA fell **96% in a single day**, dropping below $0.10
- The **Terra blockchain was halted** at block height 7,603,700 due to governance attack risks from the hyperinflating supply

**May 13, 2022:**
- LUNA fell to **$0.0005** (from $87 on May 5 — a decline of 99.9999%)
- Terra blockchain halted a second time
- **Binance suspended** trading of LUNA and UST
- UST traded at approximately $0.10

**LFG Bitcoin Reserve Depletion:**
- LFG's reserves were depleted from **80,394 BTC to just 313 BTC** in the failed peg defense
- Approximately **$3.5 billion** in Bitcoin was sold for nothing [3]

## Scale of Losses

- **$45 billion** in combined LUNA and UST market capitalization wiped out within one week
- **$28 billion** destroyed across Terra blockchain decentralized applications
- Over **$450 billion** vanished from the broader crypto market during May 2022 as Bitcoin fell from ~$36,000 to ~$26,000
- South Korea estimated **28,000 domestic citizens** lost funds directly
- Judge Paul Engelmayer estimated as many as **1 million victims** globally [4]

## Anchor Protocol: The 20% Yield Engine

Anchor Protocol was the DeFi lending platform built on Terra that offered approximately **19.5% APY** on UST deposits [5]:

- From June 2021 to May 2022, total UST deposits in Anchor increased by **3,826%**
- At its peak, Anchor's TVL reached **$17.15 billion** (May 5, 2022)
- **72% of all circulating UST** was deposited in Anchor — the protocol was effectively the sole demand driver for UST
- Borrowing demand never matched deposit growth; the protocol ran a persistent **yield deficit** requiring subsidies from Terraform Labs
- Anchor's yield reserve received a **$450 million injection** in February 2022 but was being depleted at approximately **$6 million per day** by April 2022
- On May 1, 2022, the Terra community approved a proposal to gradually reduce Anchor's rate, but it was too late
- Anchor TVL collapsed from $17.15 billion (May 5) to **below $30 million** by May 31

## The "Attacker" Theory and Nansen Analysis

A widely shared theory alleged that a single entity orchestrated the depeg by borrowing $1 billion in Bitcoin, accumulating a $350 million UST position, then dumping UST on Curve Finance when liquidity was thin, forcing LFG to sell its Bitcoin reserves and profiting from a Bitcoin short position.

**Nansen's on-chain forensic analysis (May 27, 2022)** debunked the single-attacker narrative [6]:

- **Seven wallet addresses** (not one) initiated the depeg by swapping significant UST on Curve
- These wallets had withdrawn UST from Anchor in the days and weeks prior
- Nansen could not confirm whether these entities coordinated off-chain
- The research suggested the depeg resulted from "investment decisions of several well-funded entities" responding to deteriorating macroeconomic conditions

Multiple analysts, including those at the **Richmond Federal Reserve**, argued that no coordinated attack was necessary — UST's collapse was an inevitable consequence of its flawed algorithmic design.

## Legal Consequences

### SEC Civil Action

The SEC filed its complaint against Terraform Labs and Do Kwon on **February 16, 2023** [7]:

- Alleged offering of **unregistered securities** (LUNA, wLUNA, UST, and Anchor's yield)
- Alleged deception about UST's stability and false claims about the **Chai payment app** using Terra's blockchain
- **April 5, 2024**: Jury returned a **unanimous guilty verdict** after less than two hours of deliberation
- **June 12, 2024**: Court approved a **$4.47 billion** consent judgment:
  - Terraform Labs: $3.59 billion in disgorgement + $467 million in prejudgment interest + $420 million civil penalty
  - Do Kwon: $110 million in disgorgement + $14.3 million in interest + $80 million penalty

Terraform had filed for **Chapter 11 bankruptcy on January 21, 2024**, rendering the judgment largely uncollectable.

### Do Kwon's Criminal Case

**March 23, 2023**: Do Kwon arrested at Podgorica Airport in Montenegro while traveling on a **forged Costa Rican passport** [8].

**Extradition battle**: Both the U.S. and South Korea filed competing extradition requests, resulting in 21 months of legal proceedings. On **December 27, 2024**, Montenegro's Justice Minister approved extradition to the United States. Kwon arrived in the U.S. on **December 31, 2024**.

**Indictment**: Nine counts including securities fraud, wire fraud, commodities fraud, and conspiracy.

**August 2025**: Do Kwon pleaded guilty to two counts — conspiracy to commit commodities fraud, securities fraud, and wire fraud, plus wire fraud [4].

**December 11, 2025**: Judge **Paul Engelmayer** sentenced Do Kwon to **15 years in federal prison** — exceeding the 12 years requested by prosecutors. Kwon was also ordered to forfeit over **$19 million**.

## Contagion: Industry-Wide Cascade

The Terra collapse triggered a cascading series of failures across the crypto industry [9]:

### Three Arrows Capital (3AC)
- Singapore-based hedge fund managing approximately $10 billion at peak
- Had invested over **$200 million** in LUNA as part of LFG's $1 billion Bitcoin raise
- Failed to meet margin calls after LUNA collapsed; **liquidated by BlockFi on June 15, 2022**
- Filed for bankruptcy in the British Virgin Islands in June 2022
- 3AC's liquidators later sought **$1.3 billion** from Terraform Labs

### Celsius Network
- Experienced **20% customer fund outflows** in the 11 days following Terra's collapse
- **June 12, 2022**: Froze all withdrawals citing "extreme market conditions"
- Filed for Chapter 11 bankruptcy on **July 13, 2022**

### Voyager Digital
- Had lent **$660 million** to Three Arrows Capital, which defaulted
- Filed for Chapter 11 bankruptcy on **July 5, 2022**

### BlockFi
- Survived initial contagion but was fatally weakened
- Entered a bailout deal with FTX, then filed for bankruptcy in **November 2022** after FTX collapsed

### FTX/Alameda Connection
- Alameda Research was one of the **largest UST-LUNA swappers** among Anchor depositors
- To cover Terra losses and repay lenders (including a $400 million loan recall from Genesis), Alameda began using FTX customer deposits — contributing to FTX's own collapse in November 2022

**Total 2022 contagion**: Cascading failures from Terra through FTX resulted in an estimated **$2 trillion** in lost crypto market capitalization.

## Regulatory Impact

The Terra collapse became the primary catalyst for stablecoin regulation [10]:

- **U.S. Treasury**: Secretary Janet Yellen urged Congress to approve federal stablecoin regulation by end of 2022
- **Lummis-Gillibrand Act** (June 2022): Bipartisan bill for comprehensive digital asset regulation
- **2023 House Draft Bill**: Proposed a **two-year moratorium on algorithmic stablecoins** like UST
- **EU MiCA Regulation**: The collapse accelerated finalization of the Markets in Crypto-Assets regulation, which includes specific provisions against unbacked stablecoins

## Market Manipulation Implications

The Terra/Luna collapse reveals fundamental risks in algorithmic stablecoin systems:

1. **Reflexive design as structural vulnerability**: The UST-LUNA mint/burn mechanism created a system where loss of confidence in either token automatically destroyed the other — a death spiral that no amount of reserves could prevent once it began
2. **Artificial yield as market distortion**: Anchor's ~20% APY, subsidized by Terraform Labs, concentrated 72% of UST in a single protocol and attracted deposits based on unsustainable returns — functioning as a growth subsidy that masked fundamental insolvency
3. **Liquidity pool exploitation**: The withdrawal of UST from Curve's 3pool during the migration to 4pool created a window of reduced depth that large sellers could exploit to break the peg
4. **Contagion as systemic risk**: The chain of failures from Terra → 3AC → Celsius → Voyager → BlockFi → FTX demonstrated that interconnected leverage across CeFi and DeFi can transmit a single protocol failure across the entire industry

## Relevance to Market Health Metrics

Terra's case demonstrates several indicators in the DN Institute [Market Health Metrics](https://dn.institute/research/market-health/docs/market-health-metrics/) framework:

- **Algorithmic stability as market health metric**: The absence of hard collateral backing for UST — in contrast to USDT or USDC — represents a fundamental design risk that should be weighted in any stablecoin assessment used for market health analysis
- **Yield sustainability analysis**: Returns of 19.5% APY on a stablecoin in a low-yield macro environment signal unsustainable economics that should be treated as a leading indicator of collapse risk
- **Protocol concentration risk**: 72% of a stablecoin's supply deposited in a single protocol represents extreme concentration that amplifies bank-run dynamics and should be monitored as a systemic risk metric
- **Cross-protocol contagion mapping**: The Terra → 3AC → Celsius → FTX chain demonstrates that market health assessment must account for interconnected exposure across protocols, exchanges, and lending platforms

## References

1. Wikipedia, "Do Kwon." [wikipedia.org](https://en.wikipedia.org/wiki/Do_Kwon)
2. Harvard Law School Forum on Corporate Governance, "Anatomy of a Run: The Terra-Luna Crash," May 2023. [harvard.edu](https://corpgov.law.harvard.edu/2023/05/22/anatomy-of-a-run-the-terra-luna-crash/)
3. Fortune, "Luna Foundation Guard dumps nearly all its Bitcoin reserves to save Terra's UST peg," May 2022. [fortune.com](https://fortune.com/2022/05/16/luna-foundation-guard-dumps-bitcoin-reserves-terra-usd-peg/)
4. U.S. Department of Justice, "Crypto-Enabled Fraudster Sentenced to Orchestrating $40 Billion Fraud," December 2025. [justice.gov](https://www.justice.gov/usao-sdny/pr/crypto-enabled-fraudster-sentenced-orchestrating-40-billion-fraud)
5. Seoul National University, "The Terra-Luna Collapse and the Role of the Anchor Protocol." [snu.ac.kr](https://snu.elsevierpure.com/en/publications/the-terra-luna-collapse-and-the-role-of-the-anchor-protocol-a-bir/)
6. Nansen, "On-Chain Forensics: Demystifying TerraUSD De-peg," May 2022. [nansen.ai](https://www.nansen.ai/research/on-chain-forensics-demystifying-terrausd-de-peg)
7. SEC, "Terraform and Kwon to Pay $4.5 Billion Following Jury Verdict," June 2024. [sec.gov](https://www.sec.gov/newsroom/press-releases/2024-73)
8. U.S. Department of Justice, "Do Kwon Extradited to the United States from Montenegro," December 2024. [justice.gov](https://www.justice.gov/usao-sdny/pr/do-kwon-extradited-united-states-montenegro-face-charges-relating-fraud-resulting-40)
9. Chicago Fed, "A Retrospective on the Crypto Runs of 2022," 2023. [chicagofed.org](https://www.chicagofed.org/publications/chicago-fed-letter/2023/479)
10. Baker Institute, "The Fall of Terra/LUNA: A Boost for Crypto Regulations," 2022. [bakerinstitute.org](https://www.bakerinstitute.org/research/the-fall-of-terraluna-a-boost-for-crypto-regulations)
