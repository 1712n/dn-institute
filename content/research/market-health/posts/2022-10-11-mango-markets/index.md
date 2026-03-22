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

Mango Markets was a decentralized exchange and lending platform built on the Solana blockchain, launched in August 2021. The platform offered spot trading, perpetual futures, and lending/borrowing services through an automated market maker (AMM) model. At its peak, Mango Markets held over $200 million in total value locked (TVL) and was one of the leading DeFi protocols in the Solana ecosystem.

The platform's governance token, MNGO, was sold through an initial token offering that raised over $70 million. MNGO holders could participate in governance proposals through a DAO structure, including proposals that would later play a controversial role in the aftermath of the exploit.

Critically, Mango Markets relied on a Pyth Network oracle to determine the price of MNGO for collateral valuation and perpetual futures settlement. The oracle aggregated price data from multiple exchanges where MNGO was traded. This dependency on external price feeds, combined with the token's thin liquidity across trading venues, created a vulnerability that would prove catastrophic.

## Attack Methodology

### Phase 1: Position Setup (6:07-6:25 PM ET)

Eisenberg funded two wallets on Mango Markets with $5 million USDC each, totaling $10 million in initial capital. At approximately 6:25 PM ET, Wallet A placed a sell order for 483 million MNGO perpetual futures contracts at $0.0382 per unit. Wallet B simultaneously purchased the entirety of this order. This created a market-neutral hedge: Wallet A held a massive short position, and Wallet B held an equally massive long position in MNGO perpetual futures.

### Phase 2: Oracle Price Manipulation (6:25-6:30 PM ET)

Immediately after establishing the futures positions, Eisenberg began purchasing spot MNGO tokens across multiple exchanges that served as price inputs for Mango Markets' oracle:

| Time (ET) | Exchange | Action | Amount |
|-----------|----------|--------|--------|
| 6:26 PM | Mango Markets | Spot MNGO purchase | ~$1.44M |
| 6:27 PM | AscendEX | Spot MNGO purchase | ~$1.0M |
| 6:25-6:30 PM | FTX | Spot MNGO purchase | ~$1.6M |

The total approximately $4 million in coordinated spot purchases across these three venues caused the oracle-reported price of MNGO to spike from $0.038 to $0.91 — a **2,394% increase** — within approximately 30 minutes. The thin liquidity of MNGO, which typically saw under $100,000 in daily volume across all venues, meant that relatively modest capital could move the price dramatically.

### Phase 3: Collateral Exploitation and Asset Drainage (6:29-6:45 PM ET)

With the oracle now reporting a MNGO price of $0.91, the notional value of Wallet B's 483 million MNGO-PERP long position surged to approximately $439 million on paper. Mango Markets' lending protocol allowed users to borrow against their unrealized perpetual futures profits. Eisenberg used this artificially inflated collateral to borrow and withdraw virtually all available assets from the platform:

| Asset | Amount Withdrawn |
|-------|-----------------|
| USDC | $53.7 million |
| USDT | $3.2 million |
| SOL | Various amounts |
| Other tokens | Various amounts |
| **Total** | **~$116 million** |

After Eisenberg's withdrawals drained the platform's liquidity, the MNGO price collapsed as there was no organic demand to sustain it. Wallet B's long position was liquidated due to the collateral value dropping, but by this point, the borrowed assets had already been removed from the platform. Wallet A's short position profited from the price collapse, but the key damage — the extraction of $116 million from other users' deposits — was irreversible.

## Metrics Analysis

### Average Transaction Size Anomaly

The attack produced extreme anomalies in average transaction size on MNGO spot markets. Under normal conditions, MNGO spot trading on Mango Markets and other venues exhibited relatively small average transaction sizes consistent with the token's low liquidity profile. During the attack window, average transaction sizes spiked by orders of magnitude as Eisenberg's large coordinated purchases dominated all organic trading activity.

On AscendEX, approximately $1 million in MNGO purchases represented a volume spike of over 10x the exchange's typical daily MNGO volume, concentrated within minutes rather than spread across a full trading day.

### Volume Distribution Deviation

The attack fundamentally violated expected trade volume distribution patterns. In normal markets, trading volume follows a power law heavy tail distribution where small trades are common and large trades are rare. During the manipulation window, the volume distribution was dominated by several large, uniformly-sized purchases — a signature consistent with a single entity executing a coordinated buying strategy rather than organic market activity.

### Oracle Price vs. Fair Value Divergence

The most striking metric was the divergence between oracle-reported MNGO prices and any reasonable fair value estimate. MNGO's market capitalization prior to the attack was approximately $60 million at $0.038 per token. The manipulated price of $0.91 implied a market capitalization of approximately $1.4 billion — a 23x increase with no corresponding change in fundamentals, partnerships, or protocol development.

The oracle's 30-minute weighted average price calculation could not adequately filter this manipulation because the coordinated purchases across multiple input exchanges shifted the genuine market price on those venues. The manipulation was not a simple oracle attack with falsified data; it was a genuine (if artificial) movement of the spot market price to corrupt the oracle's output.

### Liquidity Depth Analysis

The success of the manipulation was directly enabled by MNGO's extremely thin order book depth. Analysis of the order books across the three target exchanges prior to the attack showed:

- **Mango Markets MNGO/USDC**: Less than $500,000 in total ask liquidity within 50% of the mid-price
- **AscendEX MNGO/USDT**: Less than $200,000 in total ask liquidity
- **FTX MNGO/USDT**: Less than $300,000 in total ask liquidity

This meant that Eisenberg's $4 million in total spot purchases was sufficient to consume virtually all available sell-side liquidity across all three venues, enabling the extreme price dislocation required for the exploit.

## DAO Governance Manipulation

Following the exploit, Eisenberg submitted a governance proposal to Mango Markets' DAO, effectively using the platform's own decentralized governance mechanism as a negotiation tool. The proposal offered to return $46 million in exchange for retaining approximately $70 million and a promise that the DAO would not pursue criminal charges.

Eisenberg voted on his own proposal using MNGO tokens acquired during the exploit, casting over 33 million votes. This proposal failed to achieve quorum. A counter-proposal submitted by Mango Markets' team subsequently passed, under which Eisenberg returned approximately $67 million and retained approximately $47 million.

The enforceability of this settlement was immediately contested. Mango Labs co-founder Daffy Durairaj filed a lawsuit against Eisenberg arguing that the DAO was coerced into the agreement under duress, as users' funds were being held hostage as leverage in the negotiation.

## Regulatory Response

The Mango Markets case prompted an unprecedented coordinated regulatory response, with three federal agencies bringing separate actions based on the same underlying conduct:

### Department of Justice (Criminal)

Eisenberg was arrested in Puerto Rico in December 2022 and charged with commodities fraud, commodities manipulation, and wire fraud. After a nine-day jury trial in April 2024, he was convicted on all counts. However, in May 2025, Judge Arun Subramanian vacated all convictions, finding that (1) the government failed to prove proper venue in the Southern District of New York since all transactions were executed from Puerto Rico, and (2) Mango Markets had no terms of service or rules prohibiting the conduct, meaning there was no material misrepresentation sufficient for wire fraud. Prosecutors have appealed this acquittal.

### Securities and Exchange Commission (Civil)

The SEC charged Eisenberg in January 2023, alleging that MNGO was an unregistered security and that his manipulation violated anti-fraud and market manipulation provisions of securities laws. Separately, in September 2024, the SEC charged Mango DAO itself for conducting unregistered securities offerings when selling MNGO tokens. The settlement required Mango DAO to destroy remaining MNGO tokens, delist from all exchanges, and pay $700,000 in civil penalties.

### Commodity Futures Trading Commission (Civil)

The CFTC filed its complaint against Eisenberg in January 2023, marking the agency's first-ever enforcement action involving oracle manipulation on a decentralized platform. The CFTC alleged that the MNGO perpetual futures constituted commodity swaps and that Eisenberg's coordinated trading constituted market manipulation. Mango DAO separately paid $500,000 to settle with the CFTC.

## Platform Shutdown

The cumulative impact of the exploit, regulatory actions, and loss of user confidence led to Mango Markets announcing the discontinuation of operations in January 2025. The DAO approved proposals to make borrowing economically unviable by altering interest rates and collateral requirements, effectively forcing remaining users off the platform. Co-founder Maximilian Schneider confirmed on Discord that contributors wanted to discontinue work on the project.

The shutdown represented a complete collapse of a platform that had once been a flagship DeFi protocol on Solana, demonstrating how a single oracle manipulation event can trigger a cascade of regulatory, legal, and operational consequences that ultimately destroy a protocol.

## Implications for DeFi Market Integrity

The Mango Markets case established several precedents and highlighted critical vulnerabilities in DeFi protocol design:

1. **Oracle dependency risk**: Protocols that use oracle-reported prices for collateral valuation are vulnerable to cross-market manipulation when the underlying tokens have thin liquidity.
2. **DAO governance under duress**: The case demonstrated that attackers can leverage stolen assets to influence governance votes, undermining the assumption that decentralized governance provides adequate protection.
3. **Regulatory classification uncertainty**: The overlapping SEC, CFTC, and DOJ actions, each applying different legal frameworks to the same conduct, highlighted the fractured regulatory landscape for DeFi protocols.
4. **"Code is law" limitations**: Judge Subramanian's acquittal ruling — finding no fraud where there were no rules to violate — raised fundamental questions about whether exploiting protocol vulnerabilities constitutes market manipulation under existing law.

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
