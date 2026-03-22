---
title: "Market Manipulation and Algorithmic Stablecoin Fraud: The $40 Billion Terra/LUNA Collapse"
date: 2022-05-07
entities:
  - Terraform Labs
  - LUNA
  - UST
  - Do Kwon
  - Jump Trading
  - Anchor Protocol
---

## Summary

1. Between May 7 and May 13, 2022, the Terra/LUNA ecosystem suffered a **catastrophic collapse that destroyed approximately $40 billion in market value**, triggered by the de-pegging of the TerraUSD (UST) algorithmic stablecoin from its $1 target and the subsequent hyperinflationary death spiral of the LUNA token.
2. SEC enforcement actions and court proceedings revealed that **UST's algorithmic peg mechanism had been secretly propped up by Jump Trading** during a prior de-peg event in May 2021, with Jump purchasing over 62 million UST across multiple exchanges to restore the peg — an intervention that Terraform Labs and CEO Do Kwon then **falsely characterized as the algorithm self-healing**.
3. In compensation for restoring the peg, Terraform Labs **sold 61.4 million LUNA tokens to Jump Trading at a fixed price of $0.40 per token** under a private agreement, while LUNA traded at up to $90 on the open market — **yielding Jump approximately $1.28 billion in profit** from a coordinated market manipulation arrangement.
4. Terraform Labs and Do Kwon **fabricated usage metrics for the Terra blockchain**, misrepresenting that the Korean payment application Chai was processing transactions on-chain, when in reality Terraform was replicating Chai transactions to simulate genuine blockchain adoption.
5. A **jury found Terraform Labs and Do Kwon liable for civil fraud** in April 2024 after deliberating for less than two hours, resulting in a **$4.5 billion settlement** with the SEC — including $3.59 billion in disgorgement, $467 million in prejudgment interest, and $500 million in civil penalties.
6. Do Kwon **pleaded guilty to conspiracy and wire fraud** in August 2025 following extradition from Montenegro and was **sentenced to 15 years in federal prison** in December 2025, with the sentencing judge stating that "in the history of federal prosecutions, there are few frauds that have caused as much harm."

## Background

Terraform Labs was founded in 2018 by Do Kwon and Daniel Shin in Seoul, South Korea. The company developed the Terra blockchain, which supported an ecosystem of algorithmic stablecoins pegged to various fiat currencies. The flagship product was TerraUSD (UST), an algorithmic stablecoin designed to maintain a $1 peg through a mint-and-burn mechanism with LUNA, Terra's native governance and staking token.

The peg mechanism worked as follows: when UST traded above $1, arbitrageurs could mint new UST by burning $1 worth of LUNA, increasing UST supply and pushing its price down. When UST traded below $1, holders could burn UST to mint $1 worth of LUNA, reducing UST supply and pushing its price back up. This mechanism created a reflexive relationship where UST demand drove LUNA value (through burning), and LUNA value underpinned confidence in UST's peg stability.

Anchor Protocol, a lending and borrowing platform on Terra, offered approximately 20% annual percentage yield (APY) on UST deposits, attracting massive capital inflows. At its peak, Anchor held over $14 billion in UST deposits, representing the majority of all UST in circulation and creating a concentration risk that would prove critical during the collapse.

By April 2022, LUNA reached a peak price of $119.18 with a market capitalization of approximately $40 billion, ranking among the top 10 cryptocurrencies. UST's market capitalization exceeded $18 billion, making it the third-largest stablecoin by market cap.

## The May 2021 De-Peg and Secret Market Intervention

### First De-Peg Event

On May 19, 2021, UST experienced an unexpected de-peg, falling approximately 10% below its $1 target. This was the first significant stress test of the algorithmic mechanism under real market conditions.

### Jump Trading's Secret Intervention

According to the SEC's complaint against Terraform Labs and Do Kwon, the peg was not restored by the algorithmic mechanism as publicly claimed. Instead, between May 23 and May 27, 2021, Jump Trading — identified in court documents as the unnamed "third party" — purchased over 62 million UST tokens across multiple cryptocurrency exchanges to artificially restore the peg.

The purchases were deliberately spread across multiple venues to conceal Jump's role as a single coordinated buyer. This cross-exchange buying pressure pushed UST back to $1, creating the appearance that the algorithmic mint-and-burn mechanism had functioned as designed.

### Compensation and Profit

In exchange for the market intervention, Terraform Labs entered into a private agreement with Jump Trading in July 2021 to sell 61.4 million LUNA tokens at a fixed price of $0.40 per token. At the time of transfer, LUNA was trading at prices as high as $90 on the open market, yielding Jump Trading approximately $1.28 billion in profit from the arrangement.

### False Public Statements

Following the peg restoration, Do Kwon and Terraform Labs publicly claimed that UST had proven its algorithmic resilience under stress. According to the SEC complaint, Terraform publicly boasted that it had "purportedly proven the reliability of the UST $1.00 peg" in what it described as a "black swan" event and "as intense of a stress test in live conditions as can ever be expected."

These statements were materially misleading. The peg had not been restored by the algorithm but by a secretly funded market intervention. Investors who relied on these representations to assess UST's stability were making decisions based on fabricated evidence of algorithmic robustness.

## Fabrication of Blockchain Usage Metrics

### The Chai Deception

Beyond the peg manipulation, the SEC alleged that Terraform Labs systematically fabricated usage metrics for the Terra blockchain. Do Kwon and Terraform publicly represented that Chai, a popular Korean electronic mobile payment application with millions of users, was processing transactions on the Terra blockchain, providing real-world utility that would drive organic demand for UST and LUNA.

According to the SEC's investigation, Chai was not actually using the Terra blockchain for payment processing. Instead, Terraform Labs was replicating Chai's transaction data onto the blockchain to simulate genuine commercial adoption. This created a false impression of real-world utility that inflated investor confidence in the Terra ecosystem's fundamentals.

## The May 2022 Collapse

### Trigger Events (May 7-8)

On May 7, 2022, two large addresses withdrew approximately $375 million in UST from Anchor Protocol. This was followed by large-scale UST selling on the Curve Finance stablecoin exchange, where UST was traded against other stablecoins in a liquidity pool.

The sell pressure pushed UST below $1, dropping to approximately $0.98 on May 7. While minor de-pegs had occurred before, the scale of the withdrawals and the speed of the selling created uncertainty about whether the peg would hold.

### Death Spiral Activation (May 9-11)

On May 9, UST began a rapid de-peg that would prove irreversible:

| Date | UST Price | LUNA Price | LUNA Supply |
|------|-----------|------------|-------------|
| May 7 | $0.98 | ~$80 | ~1 billion |
| May 9 | $0.75 | ~$30 | ~1.5 billion |
| May 10 | $0.67 | ~$5 | ~3 billion |
| May 11 | $0.23 | ~$0.10 | ~6 billion |
| May 12 | $0.10 | ~$0.0001 | ~6.5 trillion |
| May 13 | $0.04 | ~$0.00001 | ~6.5 trillion |

The death spiral operated through the following mechanism: as UST fell below $1, holders burned UST to mint LUNA for arbitrage profit. This massively increased LUNA supply, crashing LUNA's price. As LUNA's price fell, more LUNA needed to be minted per UST burned, further diluting LUNA. The collapsing LUNA price reduced confidence in UST's backing, triggering more UST selling, which triggered more LUNA minting in a self-reinforcing loop.

Over three days, LUNA's supply increased from approximately 1 billion to 6.5 trillion tokens — a 6,500x dilution — while its price fell from $80 to effectively zero.

### Anchor Protocol Bank Run

Anchor Protocol experienced a classic bank run as UST depositors rushed to withdraw before the peg collapsed further. Anchor's total value locked fell from over $14 billion to under $2 billion within 48 hours. The 20% APY that had attracted deposits became irrelevant as the underlying asset (UST) lost over 90% of its value.

### Luna Foundation Guard's Failed Defense

The Luna Foundation Guard (LFG), a nonprofit established to defend UST's peg, deployed its Bitcoin reserves (approximately $3.5 billion at peak) in an attempt to stabilize UST. The BTC sales from LFG's reserves contributed to broader cryptocurrency market selling pressure, with Bitcoin falling from approximately $36,000 to $26,000 during the same period. The defense failed, and the LFG's reserves were depleted without restoring the peg.

## Metrics Analysis

### Volume Distribution Anomaly During Collapse

During the collapse window, UST trading volume on major exchanges exhibited extreme deviation from normal patterns. Daily UST volume on Binance, the largest trading venue, spiked from a typical $500 million to over $15 billion on May 10-11 — a 30x increase. The volume distribution was dominated by large, uniformly-sized sell orders consistent with algorithmic liquidations and coordinated unwinding by institutional holders, rather than the power law distribution expected in organic trading.

### Price Oracle Feedback Loop

The UST/LUNA exchange rate oracle was central to the death spiral. As UST depegged, the oracle-reported exchange rate created a reflexive feedback loop: lower UST prices meant more LUNA minting per redemption, which meant lower LUNA prices, which meant lower implied backing for UST, which meant more UST selling. The oracle faithfully reported accurate prices, but the mechanism design meant accurate price reporting accelerated the collapse rather than stabilizing it.

### Concentration Risk in Anchor Deposits

Analysis of on-chain data revealed that a small number of large depositors accounted for a disproportionate share of Anchor Protocol's total value locked. The May 7 trigger event — two addresses withdrawing $375 million — represented less than 3% of Anchor's TVL but was sufficient to destabilize the entire ecosystem. This concentration was obscured by aggregate TVL metrics that suggested broad-based adoption.

### Cross-Market Contagion

The Terra collapse triggered cascading liquidations and bankruptcies across the cryptocurrency ecosystem:

| Entity | Impact | Amount |
|--------|--------|--------|
| Three Arrows Capital | Bankruptcy (July 2022) | $3.5 billion in losses |
| Voyager Digital | Bankruptcy (July 2022) | $1.3 billion exposure |
| Celsius Network | Bankruptcy (July 2022) | $4.7 billion in liabilities |
| BlockFi | Bankruptcy (November 2022) | Significant Terra exposure |
| Total crypto market cap decline (May 2022) | Market-wide drawdown | ~$500 billion |

## Regulatory and Legal Consequences

### SEC Civil Action

The SEC filed a civil complaint against Terraform Labs and Do Kwon in February 2023, alleging violations of securities anti-fraud and registration provisions. The complaint charged that LUNA and UST were unregistered securities, that the algorithmic peg was misrepresented, and that blockchain usage metrics were fabricated.

In April 2024, after a nine-day trial, a seven-person jury deliberated for less than two hours before finding Terraform Labs and Do Kwon liable on all counts. The $4.5 billion settlement included:

- **Terraform Labs**: $3.587 billion in disgorgement + $467 million in prejudgment interest + $420 million civil penalty
- **Do Kwon**: $110 million in disgorgement + $14.3 million in prejudgment interest + $80 million civil penalty

### Criminal Prosecution

Do Kwon was arrested in Montenegro in March 2023 using a fraudulent passport and sentenced to several months in Montenegrin prison for passport forgery. After a prolonged extradition battle, Montenegro approved his transfer to the United States in December 2024.

In August 2025, Do Kwon pleaded guilty to conspiracy and wire fraud. In December 2025, he was sentenced to 15 years in federal prison. Judge Paul Engelmayer stated during sentencing: "In the history of federal prosecutions, there are few frauds that have caused as much harm as you have, Mr. Kwon."

### Jump Trading's Role

The Terraform Labs bankruptcy estate filed a $4 billion lawsuit against Jump Trading for its role in the May 2021 peg manipulation. The SEC separately charged Jump Crypto's subsidiary Tai Mo Shan Limited, resulting in a $123 million settlement for its involvement in manipulating UST's peg. While Jump Trading has argued it engaged in legitimate market-making, the coordinated nature of the intervention, the concealment across multiple exchanges, and the below-market compensation arrangement have been characterized by regulators as market manipulation.

## Implications for Market Integrity

1. **Algorithmic stablecoin risk**: The Terra collapse demonstrated that algorithmic peg mechanisms can fail catastrophically under sufficient sell pressure, and that the reflexive relationship between a stablecoin and its backing token creates systemic fragility that is difficult to assess from external metrics alone.
2. **Hidden market interventions**: The secret Jump Trading intervention in May 2021 shows that apparently algorithmic or decentralized mechanisms may be secretly propped up by undisclosed market participants, creating false confidence in system robustness.
3. **Yield as an attack vector**: Anchor Protocol's unsustainable 20% APY attracted deposits that created the concentration risk enabling the collapse. Artificially high yields can function as a mechanism to draw capital into fragile systems.
4. **Cascading systemic risk**: A single protocol failure triggered a chain of bankruptcies across apparently independent entities, demonstrating the interconnected counterparty risk within the cryptocurrency ecosystem.
5. **Fabricated on-chain metrics**: The Chai transaction fabrication demonstrates that on-chain data, often considered a transparency advantage over traditional finance, can be manipulated to simulate organic adoption.

## References

1. "Anatomy of a Run: The Terra Luna Crash." Harvard Law School Forum on Corporate Governance, May 22, 2023.
2. "SEC Charges Terraform Labs and Do Kwon with Defrauding Investors in Crypto Schemes." SEC Litigation Release, February 16, 2023.
3. "Statement on Jury's Verdict in Trial of Terraform Labs PTE Ltd. and Do Kwon." SEC, April 4, 2024.
4. "Terraform and Kwon to Pay $4.5 Billion Following Fraud Verdict." SEC Press Release 2024-73, June 12, 2024.
5. "Jump Trading Made $1.28B Propping Up Terra: Court Records." Fortune, May 15, 2023.
6. "Jump Crypto Is Unnamed Firm That Made $1.28B From Do Kwon's Doomed Terra Ecosystem." CoinDesk, February 17, 2023.
7. "Do Kwon Gets 15 Years in Prison for $40 Billion Terraform Fraud." Bloomberg, December 11, 2025.
8. "Anatomy of a Run: The Terra Luna Crash." NBER Working Paper Series, Working Paper 31160, 2023.
9. "Oracle Manipulation Attacks Rising: A Unique Concern for DeFi." Chainalysis, 2023.
10. "How Market Manipulation Led to a $100M Exploit on Solana DeFi Exchange Mango." CoinDesk, October 12, 2022.
11. "SEC Charges Jump Crypto Subsidiary $123 Million for Manipulating Terra Luna UST Peg." CryptoSlate, December 2024.
12. "Terraform Labs and Founder Do Kwon Found Liable in US Civil Fraud Trial." CNN Business, April 5, 2024.
