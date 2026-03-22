---
title: "Oracle Manipulation and Market Abuse on Mango Markets: $116 Million DeFi Exploit"
date: 2022-10-11
entities:
  - Mango Markets
  - MNGO
  - Solana
  - AscendEX
  - FTX
---

## Summary

1. On October 11, 2022, trader Avraham Eisenberg executed a **cross-market oracle manipulation attack** on Mango Markets, a Solana-based decentralized exchange, **extracting approximately $116 million** in digital assets within a 40-minute window.
2. The attack exploited **thin liquidity in the MNGO governance token**, which averaged under $100,000 in daily trading volume, enabling a **2,394% artificial price increase** from $0.038 to $0.91 through coordinated spot purchases across multiple exchanges.
3. By taking **offsetting perpetual futures positions** (483 million MNGO-PERPs) across two wallets he controlled, Eisenberg inflated the value of his long position through oracle price manipulation, then **borrowed against the artificially inflated collateral** to drain all available assets from the platform.
4. The exploit triggered **coordinated enforcement actions from the DOJ, SEC, and CFTC** — the CFTC's first-ever enforcement action involving oracle manipulation on a decentralized platform — resulting in criminal charges for commodities fraud, commodities manipulation, and wire fraud.
5. After the exploit, a **controversial DAO governance vote** allowed Eisenberg to retain $47 million as a "bug bounty" in exchange for returning $67 million, raising fundamental questions about the enforceability of DeFi governance resolutions under duress.
6. The case culminated in Mango Markets **shutting down operations in January 2025** following an SEC settlement requiring destruction of MNGO tokens, $700,000 in civil penalties, and delisting from all exchanges — effectively ending the platform that once held over $200 million in total value locked.

## Background

Mango Markets was a decentralized exchange and lending platform built on the Solana blockchain, launched in August 2021 by a team led by co-founders Maximilian Schneider and Daffy Durairaj. The platform offered spot trading, perpetual futures, and lending/borrowing services through a hybrid model combining an automated market maker (AMM) with a central limit order book (CLOB). This design was intended to provide both the capital efficiency of AMMs and the price discovery mechanism of traditional order books. At its peak in late 2021, Mango Markets held over $200 million in total value locked (TVL) and was one of the leading DeFi protocols in the Solana ecosystem.

The platform's governance token, MNGO, had a total supply of approximately 10 billion tokens, with approximately 1.56 billion in circulating supply at the time of the exploit. The initial token offering in August 2021 raised over $70 million. MNGO holders could participate in governance proposals through a DAO structure managed via the Realms governance framework on Solana, including proposals that would later play a controversial role in the aftermath of the exploit.

Critically, Mango Markets relied on a Pyth Network oracle to determine the price of MNGO for collateral valuation and perpetual futures settlement. The oracle aggregated price data from multiple exchanges where MNGO was traded, using a confidence-weighted average price that updated approximately every 400 milliseconds on Solana. This dependency on external price feeds, combined with the token's thin liquidity across trading venues, created a vulnerability that would prove catastrophic.

### Attacker Background

Avraham Eisenberg was not a first-time DeFi exploiter. Prior to the Mango Markets attack, he was linked to a series of governance and protocol exploits, including involvement in exploiting a governance vulnerability in Fortress Protocol in October 2021. His Twitter account (@avi_eisen) contained posts arguing that exploiting economic design flaws in DeFi protocols constituted legitimate market activity rather than fraud — a legal theory he would later assert in court. In a series of tweets on October 15, 2022, four days after the exploit, Eisenberg publicly identified himself as the attacker and described his actions as "a highly profitable trading strategy" that was "legal open market actions, using the protocol as designed."

## Attack Methodology

### Phase 1: Position Setup (6:07-6:25 PM ET)

Eisenberg funded two wallets on Mango Markets with $5 million USDC each, totaling $10 million in initial capital. The wallets were:

| Wallet | Solana Address | Role |
|--------|---------------|------|
| Wallet A | `CQvKSNnYtPTZfQRQ5jkHq8q2swJyRsdQLcFcj3EmKFfX` | Short position (sell side) |
| Wallet B | `4ND8FVPjUGGjx9VuGFuJefDWpg3THb58c277hbVRnjNa` | Long position (buy side) |

At approximately 6:25 PM ET, Wallet A placed a sell order for 483 million MNGO perpetual futures contracts at $0.0382 per unit. Wallet B simultaneously purchased the entirety of this order. This created a market-neutral hedge: Wallet A held a massive short position, and Wallet B held an equally massive long position in MNGO perpetual futures.

The notional value of these positions at the entry price was approximately $18.5 million — nearly double the $10 million in deposited capital. This was possible because Mango Markets permitted leverage on perpetual futures positions without adequate position-size limits relative to the underlying token's liquidity.

### Phase 2: Oracle Price Manipulation (6:25-6:30 PM ET)

Immediately after establishing the futures positions, Eisenberg began purchasing spot MNGO tokens across multiple exchanges that served as price inputs for Mango Markets' Pyth oracle:

| Time (ET) | Exchange | Action | Estimated Amount |
|-----------|----------|--------|-----------------|
| 6:26 PM | Mango Markets | Spot MNGO purchase | ~$1.44M |
| 6:27 PM | AscendEX | Spot MNGO purchase | ~$1.0M |
| 6:25-6:30 PM | FTX | Spot MNGO purchase | ~$1.6M |

The total approximately $4 million in coordinated spot purchases across these three venues caused the oracle-reported price of MNGO to spike from $0.038 to $0.91 — a **2,394% increase** — within approximately 30 minutes. The thin liquidity of MNGO, which typically saw under $100,000 in daily volume across all venues combined, meant that relatively modest capital could move the price dramatically.

The Pyth oracle's confidence interval widened significantly during the manipulation period, indicating abnormal price activity, but Mango Markets' protocol did not implement circuit breakers or confidence-interval-based position freezes that would have paused borrowing during periods of extreme price uncertainty.

### Phase 3: Collateral Exploitation and Asset Drainage (6:29-6:45 PM ET)

With the oracle now reporting a MNGO price of $0.91, the notional value of Wallet B's 483 million MNGO-PERP long position surged to approximately $439 million on paper. Mango Markets' lending protocol allowed users to borrow against their unrealized perpetual futures profits. Eisenberg used this artificially inflated collateral to borrow and withdraw virtually all available assets from the platform:

| Asset | Amount Withdrawn |
|-------|-----------------|
| USDC | $53.7 million |
| SOL | $18.3 million |
| MSOL | $11.5 million |
| MNGO | $10.5 million |
| BTC | $6.8 million |
| SRM | $5.4 million |
| USDT | $3.2 million |
| Other tokens (RAY, ADA, FTT, AVAX) | ~$6.6 million |
| **Total** | **~$116 million** |

After Eisenberg's withdrawals drained the platform's liquidity, the MNGO price collapsed as there was no organic demand to sustain it. Wallet B's long position was liquidated due to the collateral value dropping, but by this point, the borrowed assets had already been removed from the platform. Wallet A's short position profited from the price collapse, but the key damage — the extraction of $116 million from other users' deposits — was irreversible.

The entire attack, from the first USDC deposit to the final withdrawal, took approximately 40 minutes.

## Metrics Analysis

### Average Transaction Size Anomaly

The attack produced extreme anomalies in average transaction size on MNGO spot markets. Under normal conditions, MNGO spot trading on Mango Markets and other venues exhibited relatively small average transaction sizes consistent with the token's low liquidity profile. During the attack window, average transaction sizes spiked by orders of magnitude as Eisenberg's large coordinated purchases dominated all organic trading activity.

On AscendEX, approximately $1 million in MNGO purchases represented a volume spike of over 10x the exchange's typical daily MNGO volume, concentrated within minutes rather than spread across a full trading day. On FTX, the $1.6 million in purchases occurred across a similarly compressed timeframe, creating average transaction sizes approximately 50-100x normal levels.

The following table summarizes pre-attack vs. attack-window average transaction sizes across the three target exchanges:

| Exchange | Normal Avg Tx Size (MNGO/USD) | Attack Window Avg Tx Size | Multiple |
|----------|------------------------------|--------------------------|----------|
| Mango Markets | ~$200-$500 | ~$50,000-$100,000 | 100-500x |
| AscendEX | ~$100-$300 | ~$30,000-$80,000 | 100-800x |
| FTX | ~$300-$800 | ~$40,000-$120,000 | 50-400x |

### Volume Distribution Deviation

The attack fundamentally violated expected trade volume distribution patterns. In normal markets, trading volume follows a power law heavy tail distribution where small trades are common and large trades are rare. The tail exponent of this distribution typically falls between 1.5 and 3.0 in healthy markets.

During the manipulation window, the volume distribution was dominated by several large, uniformly-sized purchases — a signature consistent with a single entity executing a coordinated buying strategy rather than organic market activity. The tail exponent during the attack window approached or exceeded 5.0 on all three exchanges, indicating an extreme concentration of trade sizes that deviates sharply from natural market behavior.

This pattern is analogous to the volume distribution anomalies documented in wash trading detection research: when a single actor dominates trading activity, the natural power law distribution collapses into a narrow band of similarly-sized trades.

### Oracle Price vs. Fair Value Divergence

The most striking metric was the divergence between oracle-reported MNGO prices and any reasonable fair value estimate. MNGO's market capitalization prior to the attack was approximately $60 million at $0.038 per token (based on ~1.56 billion circulating supply). The manipulated price of $0.91 implied a market capitalization of approximately $1.4 billion — a 23x increase with no corresponding change in fundamentals, partnerships, or protocol development.

The oracle's confidence-weighted average price calculation could not adequately filter this manipulation because the coordinated purchases across multiple input exchanges shifted the genuine market price on those venues. The manipulation was not a simple oracle attack with falsified data; it was a genuine (if artificial) movement of the spot market price to corrupt the oracle's output.

The Pyth oracle did report widening confidence intervals during the manipulation, indicating abnormal price uncertainty. A robust implementation would have treated these widening intervals as a risk signal to temporarily freeze new borrowing — a safeguard that Mango Markets had not implemented.

### Liquidity Depth Analysis

The success of the manipulation was directly enabled by MNGO's extremely thin order book depth. Analysis of the order books across the three target exchanges prior to the attack showed:

- **Mango Markets MNGO/USDC**: Less than $500,000 in total ask liquidity within 50% of the mid-price
- **AscendEX MNGO/USDT**: Less than $200,000 in total ask liquidity
- **FTX MNGO/USDT**: Less than $300,000 in total ask liquidity
- **Combined ask liquidity across all three venues**: Under $1 million

This meant that Eisenberg's $4 million in total spot purchases was sufficient to consume virtually all available sell-side liquidity across all three venues, enabling the extreme price dislocation required for the exploit.

A key observation is the ratio between the attack capital deployed for manipulation ($4M in spot purchases) and the value extracted ($116M) — a **29x leverage ratio** that demonstrates the extreme efficiency of oracle manipulation attacks on thin-liquidity tokens. For comparison, Eisenberg's total initial capital was $10M and he extracted 11.6x that amount.

### Cross-Exchange Timing Correlation

The timing of Eisenberg's spot purchases across all three exchanges was highly correlated, with purchases on Mango Markets, AscendEX, and FTX occurring within a 1-5 minute window. This cross-exchange timing correlation is a strong indicator of coordinated manipulation. In organic markets, price movements on one exchange propagate to others through arbitrage with a typical latency of seconds to minutes. The near-simultaneous purchasing across all three venues — each representing a Pyth oracle input — shows deliberate targeting of the oracle's price aggregation mechanism rather than normal market activity.

## DAO Governance Manipulation

Following the exploit, Eisenberg submitted a governance proposal to Mango Markets' DAO via the Realms governance framework, effectively using the platform's own decentralized governance mechanism as a negotiation tool. The proposal (Proposal #65) offered to return $46 million in exchange for retaining approximately $70 million and a promise that the DAO would not pursue criminal charges.

Eisenberg voted on his own proposal using MNGO tokens acquired during the exploit, casting over 33 million votes (approximately 2.1% of circulating supply). This proposal failed to achieve quorum. A counter-proposal (Proposal #66) submitted by Mango Markets' team subsequently passed with over 98% approval, under which Eisenberg returned approximately $67 million and retained approximately $47 million as a so-called "bug bounty."

The enforceability of this settlement was immediately contested. Mango Labs co-founder Daffy Durairaj filed a lawsuit against Eisenberg in California Superior Court, arguing that the DAO was coerced into the agreement under duress, as users' funds were being held hostage as leverage in the negotiation. The case raised fundamental questions about whether DAO governance votes conducted while an attacker holds stolen assets can constitute valid contractual agreements.

The $67 million returned by Eisenberg was distributed pro-rata to affected depositors through a subsequent governance proposal, but this only covered approximately 58% of total losses, leaving depositors with an aggregate shortfall of approximately $49 million.

## Regulatory Response

The Mango Markets case prompted an unprecedented coordinated regulatory response, with three federal agencies bringing separate actions based on the same underlying conduct:

### Department of Justice (Criminal)

Eisenberg was arrested at an apartment in San Juan, Puerto Rico on December 26, 2022, and charged with commodities fraud, commodities manipulation, and wire fraud. The indictment alleged that he intentionally manipulated the MNGO oracle price to fraudulently obtain over $100 million in cryptocurrency from Mango Markets' depositors.

After a nine-day jury trial in the Southern District of New York in April 2024, Eisenberg was convicted on all three counts: commodities fraud (18 U.S.C. 1348), commodities manipulation (7 U.S.C. 9(1)), and wire fraud (18 U.S.C. 1343).

However, in May 2025, Judge Arun Subramanian vacated all convictions in a detailed opinion, finding that: (1) the government failed to prove proper venue in the Southern District of New York since all transactions were executed from Puerto Rico and the Solana blockchain has no geographic locus, and (2) Mango Markets had no terms of service, user agreements, or rules prohibiting the conduct, meaning there was no material misrepresentation sufficient to establish the "scheme to defraud" element of wire fraud or the deceptive conduct element of commodities fraud.

Prosecutors filed a notice of appeal to the Second Circuit Court of Appeals. The appeal remains pending and has significant implications for whether DeFi protocol exploits can be prosecuted under existing federal fraud statutes.

### Securities and Exchange Commission (Civil)

The SEC charged Eisenberg in January 2023, alleging that MNGO was an unregistered security under the Howey test and that his manipulation violated anti-fraud and market manipulation provisions of securities laws (Section 10(b) of the Exchange Act and Section 17(a) of the Securities Act).

Separately, in September 2024, the SEC charged Mango DAO, Mango Labs, and the Blockworks Foundation for conducting unregistered securities offerings when selling MNGO tokens through the initial token sale. The settlement required Mango DAO to:

- Destroy all remaining MNGO tokens held by the DAO treasury
- Request all exchanges to delist and halt trading in MNGO
- Remove MNGO from the Mango Markets platform
- Pay $700,000 in civil penalties

This was notable as one of the first SEC enforcement actions treating a DAO itself as an entity subject to securities law obligations, despite the DAO's decentralized structure.

### Commodity Futures Trading Commission (Civil)

The CFTC filed its complaint against Eisenberg in January 2023, marking the agency's **first-ever enforcement action involving oracle manipulation on a decentralized platform**. The CFTC alleged that the MNGO perpetual futures constituted commodity swaps subject to the Commodity Exchange Act and that Eisenberg's coordinated trading across spot markets to influence the oracle price constituted market manipulation under 7 U.S.C. 9(1).

Mango DAO separately paid $500,000 to settle with the CFTC for operating an unregistered trading facility. The CFTC settlement explicitly characterized the MNGO-PERP instruments as "swaps" — a classification with broad implications for how decentralized perpetual futures protocols are regulated.

## Platform Shutdown

The cumulative impact of the exploit, regulatory actions, and loss of user confidence led to Mango Markets announcing the discontinuation of operations in January 2025. The DAO approved proposals to make borrowing economically unviable by setting interest rates to extreme levels and reducing collateral factors to zero, effectively forcing remaining users off the platform. Co-founder Maximilian Schneider confirmed on Discord that contributors wanted to discontinue work on the project.

The platform's TVL, which had already collapsed from over $200 million pre-exploit to approximately $30 million immediately after, continued to decline through 2023 and 2024. By the time of the shutdown announcement, TVL was under $5 million.

| Period | TVL (approximate) | Event |
|--------|-------------------|-------|
| Late 2021 (peak) | $200M+ | Platform at full operation |
| October 10, 2022 (pre-exploit) | $183M | Day before the attack |
| October 12, 2022 (post-exploit) | ~$30M | Immediately after attack |
| October 15, 2022 (partial return) | ~$97M | $67M returned by Eisenberg |
| December 2023 | ~$20M | Ongoing user exodus |
| September 2024 | ~$10M | SEC settlement announced |
| January 2025 | <$5M | Shutdown announced |

The shutdown represented a complete collapse of a platform that had once been a flagship DeFi protocol on Solana, demonstrating how a single oracle manipulation event can trigger a cascade of regulatory, legal, and operational consequences that ultimately destroy a protocol.

## Comparison with Other Oracle Manipulation Exploits

The Mango Markets exploit belongs to a broader category of oracle manipulation attacks that have collectively drained hundreds of millions from DeFi protocols:

| Exploit | Date | Amount | Method |
|---------|------|--------|--------|
| Beanstalk | Apr 2022 | $182M | Flash loan governance attack |
| Cream Finance (v2) | Oct 2021 | $130M | Flash loan oracle manipulation |
| **Mango Markets** | **Oct 2022** | **$116M** | **Cross-exchange spot manipulation to inflate PERP collateral** |
| BonqDAO | Feb 2023 | $120M | Direct oracle price feed manipulation |
| Harvest Finance | Oct 2020 | $34M | Flash loan USDC/USDT oracle manipulation |

What distinguished the Mango Markets attack from flash loan-based exploits was its use of permanent capital ($10M in USDC) rather than borrowed flash loan funds, and its cross-exchange coordination across three separate trading venues to influence the oracle. This made the manipulation harder to detect in real-time because the spot purchases constituted genuine (if artificial) market activity on each individual exchange.

## Implications for DeFi Market Integrity

The Mango Markets case established several precedents and highlighted critical vulnerabilities in DeFi protocol design:

1. **Oracle dependency risk**: Protocols that use oracle-reported prices for collateral valuation are vulnerable to cross-market manipulation when the underlying tokens have thin liquidity. The Mango Markets case demonstrated that as little as $4 million in coordinated spot purchases can manipulate an oracle to extract 29x that amount.
2. **Position size limits**: Mango Markets had no effective limit on the ratio between a user's perpetual futures position size and the underlying token's total liquidity. A position of 483 million MNGO-PERPs on a token with under $100,000 daily volume should have triggered automated risk controls.
3. **Confidence interval circuit breakers**: The Pyth oracle reported widening confidence intervals during the manipulation, but Mango Markets did not implement automated responses to this signal. Protocols should freeze new borrowing when oracle confidence intervals exceed defined thresholds.
4. **DAO governance under duress**: The case demonstrated that attackers can leverage stolen assets to influence governance votes, undermining the assumption that decentralized governance provides adequate protection.
5. **Regulatory classification uncertainty**: The overlapping SEC, CFTC, and DOJ actions, each applying different legal frameworks to the same conduct, highlighted the fractured regulatory landscape for DeFi protocols.
6. **"Code is law" limitations**: Judge Subramanian's acquittal ruling — finding no fraud where there were no rules to violate — raised fundamental questions about whether exploiting protocol vulnerabilities constitutes market manipulation under existing law.
7. **Cross-venue surveillance**: The attack underscores the need for cross-exchange trade surveillance systems in DeFi. Monitoring a single venue would not have detected the coordinated manipulation across Mango Markets, AscendEX, and FTX.

## References

1. "The Mango Markets Exploit: An Order Book Analysis." Solidus Labs, October 2022.
2. "SEC Charges Avraham Eisenberg with Manipulating Mango Markets' Governance Token to Steal $116 Million of Crypto Assets." SEC Press Release 2023-13, January 20, 2023.
3. "CFTC Charges Avraham Eisenberg with Manipulative and Deceptive Scheme to Misappropriate Over $110 Million from Mango Markets." CFTC Press Release 8647-23, January 9, 2023.
4. "How Market Manipulation Led to a $100M Exploit on Solana DeFi Exchange Mango." CoinDesk, October 12, 2022.
5. "DeFi Exchange Mango's $114M Exploit Was Market Manipulation, Not a Hack, Ex-FBI Special Agent Says." CoinDesk, October 20, 2022.
6. "SEC Charges Entities Operating Crypto Asset Trading Platform Mango Markets for Unregistered Offers and Sales of MNGO Governance Tokens." SEC Press Release 2024-154, September 27, 2024.
7. "Mango Markets to Wind Down Operations After $110 Million Exploit and SEC Settlement." Yahoo Finance, January 13, 2025.
8. "Oracle Manipulation Attacks Rising: A Unique Concern for DeFi." Chainalysis, 2023.
9. "Federal Judge Overturns All Criminal Convictions in Mango Markets Case Against Avraham Eisenberg." TRM Labs, May 23, 2025.
10. "Mango Markets Exploiter Thought a DAO Protected Him. Then US Courts Showed Up." CoinDesk, January 31, 2023.
11. "United States v. Eisenberg, No. 23-cr-00077 (S.D.N.Y.)." Court Listener, Federal Criminal Docket.
12. "CFTC v. Eisenberg, No. 23-cv-00168 (S.D.N.Y.)." CFTC Enforcement Action, January 2023.
13. "Mango Markets Governance Proposal #65 and #66." Realms Governance, Solana, October 2022.
14. "An Empirical Study of DeFi Liquidations: Incentives, Risks, and Instabilities." Qin et al., IMC 2021.
15. "Attacking the DeFi Ecosystem with Flash Loans for Fun and Profit." Qin et al., Financial Cryptography 2021.
