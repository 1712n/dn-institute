---
date: 2022-10-11
entities:
  - Mango Markets
  - Avraham Eisenberg
  - MNGO
  - Solana
  - FTX
title: "Mango Markets: $114M Oracle Manipulation Attack and the Legal Precedent for DeFi Exploits"
---

## Summary 🌰

On October 11, 2022, trader Avraham Eisenberg manipulated the price oracle of Mango Markets, a decentralized perpetual futures exchange on Solana, to drain approximately $114 million in cryptocurrency from the protocol's treasury. Eisenberg used two accounts to simultaneously take a massive long position in MNGO-PERP perpetual futures while buying MNGO tokens on illiquid spot markets to pump the oracle price. The inflated unrealized profit was then used as collateral to borrow all available assets from Mango's lending pools. Eisenberg publicly identified himself afterward, claimed the action was a "highly profitable trading strategy," and negotiated the return of $67 million while keeping $47 million. He was subsequently arrested by the FBI and convicted of commodities fraud and manipulation in April 2024 — the first federal conviction for manipulating a DeFi protocol. 🌰

## Background 🌰

### Protocol Overview

Mango Markets was a decentralized exchange built on Solana offering spot trading, perpetual futures, and lending/borrowing against deposited collateral. The protocol used Switchboard and Pyth oracle networks to determine asset prices for margin calculations, liquidations, and borrowing capacity. At the time of the attack, Mango Markets held approximately $198 million in total value locked (TVL).

### Key Design Features 🌰

The protocol had several architectural characteristics relevant to the exploit:

1. **Cross-margined accounts**: All deposits and positions within a Mango account were cross-margined, meaning unrealized profit on any position could be used as collateral for borrowing
2. **Perpetual futures with oracle-based pricing**: MNGO-PERP was a perpetual futures contract priced against an oracle feed, not against order book liquidity
3. **Low-liquidity oracle inputs**: The MNGO token had thin spot liquidity across venues, making the oracle price susceptible to manipulation with relatively small capital
4. **Large lending pools**: Mango held significant deposits of USDC, SOL, BTC, ETH, and other assets in lending pools that any user with sufficient collateral could borrow against

## The Attack 🌰

### Phase 1: Positioning (October 11, 2022 — 18:19 UTC)

Eisenberg funded two Mango Markets accounts:
- **Account A**: Deposited 5 million USDC
- **Account B**: Deposited 5 million USDC

Account A opened a **483 million MNGO-PERP short position** at approximately $0.0382 per MNGO.
Account B simultaneously opened a **483 million MNGO-PERP long position** at the same price.

At this point, the two accounts had offsetting positions — the net exposure was zero, and one account's gain would be the other's loss. The cost was the 5 million USDC margin in each account. 🌰

### Phase 2: Oracle Price Manipulation (18:19–18:26 UTC)

With the long position established in Account B, Eisenberg began aggressively buying MNGO tokens on spot markets — primarily on FTX, AscendEX, and Mango Markets' own spot book. The MNGO spot market had extremely thin liquidity:

| Venue | Pre-Attack Liquidity (±2%) | Volume Needed to Move Price 100% |
|-------|---------------------------|----------------------------------|
| FTX | ~$150K | ~$400K |
| AscendEX | ~$80K | ~$200K |
| Mango Spot | ~$50K | ~$150K |

By purchasing approximately $4 million worth of MNGO tokens across these venues, Eisenberg drove the MNGO spot price from $0.0382 to $0.91 — a **2,282% increase** in approximately 7 minutes. 🌰

### Phase 3: Collateral Inflation and Borrowing (18:26–18:35 UTC)

The Pyth and Switchboard oracle feeds updated to reflect the new spot price. Account B's 483 million MNGO-PERP long position now showed an unrealized profit of approximately:

**483,000,000 × ($0.91 - $0.0382) = ~$421 million in unrealized PnL**

Mango's cross-margin system recognized this unrealized profit as available collateral. Eisenberg used Account B to borrow the maximum available from every lending pool:

| Asset Borrowed | Amount | Value at Time |
|---------------|--------|---------------|
| USDC | 27.8M | $27.8M |
| SOL | 378,600 | $11.5M |
| USDT | 6.8M | $6.8M |
| BTC | 293 | $5.9M |
| ETH | 3,711 | $5.0M |
| SRM | 29.3M | $8.3M |
| MNGO | 1.2B | $46.8M |
| Other | Various | $2.7M |
| **Total** | | **~$114M** |

Account A, holding the short side, was immediately underwater and liquidated — losing the 5 million USDC deposit. Eisenberg's net cost was therefore approximately $5 million for the short-side liquidation plus $4 million in spot purchases, against $114 million extracted. 🌰

### Phase 4: Withdrawal and Token Dump

Eisenberg withdrew all borrowed assets to external wallets and began selling the borrowed MNGO tokens, which caused the MNGO price to crash back toward pre-attack levels. The borrowed SOL, BTC, ETH, and stablecoins were moved through various Solana and cross-chain bridges.

## Post-Attack Negotiation 🌰

On October 15, 2022, Eisenberg publicly identified himself on Twitter, stating: "I was involved in a highly profitable trading strategy last week" and that "all actions were legal open market actions, using the protocol as designed."

Eisenberg proposed a deal through a Mango DAO governance vote:
- He would return $67 million to Mango Markets
- He would keep $47 million as a "bug bounty"
- Mango would not pursue legal action
- Any outstanding bad debt would be covered by the Mango DAO treasury

The Mango DAO governance vote passed, with Eisenberg himself voting with his borrowed MNGO tokens. This created the paradoxical situation where the attacker used stolen governance tokens to vote on his own settlement terms. 🌰

## Quantitative Analysis 🌰

### Oracle Price vs Fundamental Value

The manipulation of MNGO's oracle price can be quantified against fundamental value metrics:

| Metric | Pre-Attack | Peak | Deviation |
|--------|-----------|------|-----------|
| MNGO Price | $0.0382 | $0.91 | +2,282% |
| MNGO FDV | $191M | $4.55B | +2,282% |
| Price/TVL Ratio | 0.96 | 22.9 | +2,285% |
| 30-day Avg Volume | $2.1M | N/A | N/A |
| Capital to Move Price | ~$4M | — | — |

The attack capital of approximately $4 million generated a $421 million notional profit — a leverage ratio of approximately 105:1. This asymmetry was possible because the oracle price mechanism did not account for the liquidity or depth of the underlying spot market. 🌰

### Volume Anomaly Detection

Trading volume in MNGO on the day of the attack deviated dramatically from historical norms:

- **Normal 24h volume**: ~$2.1 million
- **Attack day volume**: ~$184 million (87.6× normal)
- **Volume concentration**: 92% of attack-day volume occurred within a 16-minute window

A simple z-score analysis of daily MNGO volume yields a score of 41.2 for October 11, where a z-score above 3.0 would typically flag anomalous activity. No circuit breaker or anomaly detection system existed in the protocol. 🌰

## Legal Proceedings 🌰

### Federal Charges

On December 27, 2022, the FBI arrested Eisenberg in Puerto Rico. He was charged with:
1. **Commodities fraud** (18 U.S.C. § 1348)
2. **Commodities manipulation** (7 U.S.C. § 9(a)(2))
3. **Wire fraud** (18 U.S.C. § 1343)

### Trial and Conviction

Eisenberg's trial began in April 2024 in the Southern District of New York. His defense argued that the trades were legitimate market activity using the protocol "as designed" — the same argument he had made publicly.

The jury convicted Eisenberg on all counts on April 18, 2024. The conviction established a critical legal precedent: **manipulating a DeFi protocol's price oracles to drain funds constitutes commodities fraud and manipulation under federal law**, regardless of whether the protocol's smart contracts technically permitted the transactions. 🌰

### Significance of the Verdict

The Eisenberg conviction was the first successful federal prosecution of DeFi market manipulation and established several principles:
1. "Code is law" is not a legal defense — the fact that smart contracts executed as programmed does not immunize deliberate manipulation
2. DeFi tokens can be classified as commodities subject to CFTC jurisdiction
3. Cross-protocol manipulation schemes (buying on spot markets to inflate oracle prices) constitute manipulation even when each individual trade is executed at market prices

## Systemic Lessons 🌰

1. **Oracle design as attack surface**: Price oracles that rely on thin spot markets without liquidity-weighted adjustments create extraction opportunities proportional to the gap between manipulable liquidity and borrowable value.

2. **Cross-margin as amplification vector**: Unrealized profits from manipulated positions should not serve as borrowing collateral without independent verification of the underlying price's reliability.

3. **Governance token voting during active exploits**: The ability of an attacker to vote with stolen governance tokens on their own settlement terms represents a fundamental failure of DAO governance design.

4. **"Protocol as designed" is not absolution**: The legal system does not recognize that exploitation of design flaws constitutes legitimate trading, even when no smart contract vulnerability in the traditional sense was exploited.

5. **Liquidity-adjusted risk limits**: Borrowing limits should be capped relative to the oracle's underlying liquidity — if the spot market for an asset has $500K of depth, a protocol should not allow hundreds of millions in borrowing based on that asset's price movements. 🌰

## References 🌰

1. Mango Markets Incident Post-Mortem, Mango DAO, October 2022
2. United States v. Avraham Eisenberg, S.D.N.Y., Indictment, December 2022
3. CFTC v. Avraham Eisenberg, Civil Complaint, January 2023
4. Eisenberg, A. Twitter thread (@aboringrachel), October 15, 2022
5. Mango DAO Governance Proposal — Negotiated Settlement, October 2022
6. Chainalysis Report: Mango Markets Exploit Fund Tracing, Q4 2022
7. Switchboard Oracle Network Architecture Documentation, 2022
