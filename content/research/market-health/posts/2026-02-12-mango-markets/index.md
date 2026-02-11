---
title: "Mango Markets: $110M Oracle Manipulation Attack, 'Legal Open Market Actions' Defense, and First DeFi Market Manipulation Conviction"
date: 2026-02-12
entities:
  - Mango Markets
  - MNGO
---

## Summary

1. **$110 million drained through oracle manipulation**: On October 11, 2022, Avraham Eisenberg used $10 million in initial capital to manipulate the MNGO perpetual futures price on Mango Markets by 1,300% in under 10 minutes, then used the artificially inflated collateral value to borrow $110 million in assets from the protocol's treasury — draining nearly all available liquidity.
2. **First-ever DeFi market manipulation conviction**: Eisenberg was arrested in Puerto Rico on December 26, 2022, and convicted by a federal jury on April 18, 2024, of commodities fraud and market manipulation — marking the first time a U.S. jury found someone guilty of manipulating a decentralized finance protocol.
3. **Publicly claimed "legal open market actions"**: Within hours of the exploit, Eisenberg identified himself on Twitter and described his actions as "a highly profitable trading strategy" using "legal open market actions" — a defense that the jury rejected after less than six hours of deliberation.
4. **DAO negotiated $47 million "bug bounty" return**: The Mango Markets DAO voted (98% approval) to allow Eisenberg to keep $47 million as a "bug bounty" in exchange for returning $67 million, an arrangement Eisenberg himself proposed by voting with his stolen governance tokens.
5. **Convictions overturned on venue grounds**: In May 2025, the Second Circuit Court of Appeals overturned Eisenberg's convictions, ruling that the Southern District of New York was not the proper venue — prosecutors filed a new indictment in the Western District of Texas in December 2025.

## Background

### Mango Markets and Solana DeFi

**Mango Markets** was a decentralized exchange (DEX) and lending platform built on the **Solana** blockchain, launched in **August 2021**. The protocol offered spot trading, perpetual futures, and borrowing/lending services, with governance controlled by holders of the **MNGO** token [1].

At the time of the exploit, Mango Markets had approximately **$116 million in total value locked (TVL)**, making it one of the largest DeFi protocols on Solana. The protocol used a **price oracle system** to determine asset values for collateral and margin calculations.

### Oracle-Based Collateral System

Mango Markets' lending system operated on a standard DeFi collateral model:

- Users deposited assets as collateral
- The protocol calculated collateral value using **oracle price feeds** (primarily Switchboard and Pyth oracles)
- Users could borrow against their collateral up to protocol-defined limits
- If collateral value fell below the borrowing threshold, positions would be liquidated

Critically, the protocol's collateral valuation for **MNGO token** perpetual futures positions used the **same oracle price** as the spot market — meaning that manipulating the spot price would directly inflate the collateral value of futures positions.

## The Attack (October 11, 2022)

### Setup and Execution

Avraham Eisenberg executed a meticulously planned oracle manipulation attack in under 10 minutes [2]:

**Phase 1 — Establishing Positions (Pre-attack):**
- Eisenberg funded **two separate accounts** on Mango Markets with approximately **$5 million USDC each** ($10 million total)
- From Account A, he placed a massive **long position** on MNGO perpetual futures
- From Account B, he simultaneously placed the corresponding **short position** — creating an artificially matched trade

**Phase 2 — Price Manipulation:**
- Eisenberg used a third account to **aggressively buy MNGO tokens** on multiple Solana DEXs and on Mango Markets' own order book
- MNGO token price surged from approximately **$0.038 to $0.54** — a **1,300% increase** — in under 10 minutes
- The thin liquidity of MNGO (market cap approximately $30 million) meant that relatively small purchases could move the price dramatically

**Phase 3 — Collateral Inflation:**
- Account A's long MNGO futures position was now valued at approximately **$423 million** in unrealized profit (at the manipulated price)
- Mango Markets' oracle system accepted this manipulated price as the collateral value

**Phase 4 — Treasury Drainage:**
- Using the inflated collateral value, Eisenberg **borrowed against Account A's position**, withdrawing approximately **$110 million** in assets from Mango Markets' treasury
- Withdrawn assets included: **SOL, USDC, USDT, BTC, ETH, SRM, MNGO**, and other tokens
- Account B's short position was liquidated (the loss was capped at the $5M deposit), while Account A extracted the full treasury

### Impact

| Metric | Value |
|--------|-------|
| Initial capital | ~$10 million |
| MNGO price manipulation | $0.038 → $0.54 (1,300%+) |
| Assets drained | ~$110 million |
| Protocol TVL before attack | ~$116 million |
| Protocol TVL after attack | ~$6 million |
| Time to execute | <10 minutes |

## The "Legal Open Market Actions" Defense

### Eisenberg's Public Identification

In a move unprecedented in DeFi exploits, Eisenberg **publicly identified himself on Twitter** within hours of the attack [3]:

- Tweeted: *"I was involved with a team that operated a highly profitable trading strategy last week"*
- Described the actions as *"legal open market actions, using the protocol as designed"*
- Argued he was simply an arbitrageur exploiting a market inefficiency
- Claimed: *"I believe all of our actions were legal open market actions, using the protocol as designed, even if the development team did not fully anticipate all the consequences of setting parameters the way they are"*

### Legal Theory

Eisenberg's defense rested on the argument that:
1. He made trades on an open, permissionless protocol
2. No terms of service prohibited his actions
3. Oracle prices reflected real market activity
4. "Code is law" — the protocol functioned as designed

This argument was ultimately rejected by the jury.

## DAO Negotiation and "Bug Bounty"

### The $47 Million Deal

After the exploit, the Mango Markets DAO conducted an extraordinary governance vote [4]:

1. Eisenberg proposed a deal through Mango's governance system: he would return $67 million if allowed to keep the remaining **$47 million** as a "bug bounty"
2. **Eisenberg voted in the proposal using stolen MNGO governance tokens** — approximately 32 million MNGO tokens he had taken from the treasury
3. The DAO voted **98% in favor** of the deal (with Eisenberg's own stolen tokens contributing to the majority)
4. The agreement included a provision that Mango Markets would not pursue criminal charges

**October 15, 2022**: Eisenberg returned approximately **$67 million** to the Mango Markets treasury per the agreement.

### Controversy

The DAO "bug bounty" arrangement was criticized for:
- Allowing a thief to vote on their own amnesty using stolen funds
- Setting a precedent that DeFi exploiters could negotiate to keep a portion of stolen funds
- Undermining the concept of governance by demonstrating that large token holders could unilaterally dictate outcomes
- The "no criminal charges" provision had no legal effect on DOJ prosecution authority

## Arrest and Trial

### Arrest (December 26, 2022)

Eisenberg was arrested by the FBI at a **condo in Condado, Puerto Rico** on December 26, 2022 — approximately 2.5 months after the exploit. He was charged with [5]:

- Commodities fraud
- Commodities manipulation
- Wire fraud

### Trial and Conviction (April 2024)

The trial took place in the **Southern District of New York** before Judge **Arun Subramanian** [6]:

- **Prosecution argument**: Eisenberg intentionally manipulated MNGO's price to artificially inflate his collateral, then drained the protocol — this constituted market manipulation regardless of whether the protocol was decentralized
- **Defense argument**: The trades were "legal open market actions" on a permissionless protocol with no terms of service prohibiting his strategy
- **April 18, 2024**: The jury convicted Eisenberg on all counts after approximately **six hours of deliberation**
- This was the **first-ever U.S. conviction for market manipulation of a decentralized finance protocol**

### Convictions Overturned (May 2025)

In **May 2025**, the **Second Circuit Court of Appeals** overturned Eisenberg's convictions [7]:

- The court ruled that the **Southern District of New York** was not the proper venue for the case
- The relevant conduct — the manipulation of MNGO tokens on Solana DEXs — did not have a sufficient nexus to New York
- The reversal was on **procedural grounds**, not on the merits of whether the conduct constituted market manipulation

### New Indictment (December 2025)

In **December 2025**, federal prosecutors filed a new indictment against Eisenberg in the **Western District of Texas** (Austin), where Mango Labs was headquartered. The case remains pending.

### Separate CSAM Conviction

In a separate case, Eisenberg was convicted and sentenced to **52 months in federal prison** for possession of child sexual abuse material (CSAM) found on devices seized during his arrest.

## SEC and Regulatory Actions

### SEC Settlement with Mango DAO (January 2025)

The SEC reached a settlement with Mango DAO and Mango Labs in **January 2025** [8]:

- Mango DAO agreed to pay a **$700,000 civil penalty**
- Mango DAO agreed to **destroy all MNGO tokens** in its treasury and request delisting from exchanges
- MNGO was deemed an unregistered security
- The settlement effectively ended the protocol

### Mango Markets Shutdown (January 2025)

Mango Markets **ceased operations** in January 2025 following the SEC settlement. The protocol had never fully recovered from the October 2022 exploit, with TVL remaining far below pre-attack levels.

## Market Manipulation Implications

The Mango Markets exploit represents a landmark case in DeFi market manipulation:

1. **Oracle manipulation as systemic DeFi risk**: The ability to manipulate a low-liquidity token's price and use the inflated value as collateral demonstrates that DeFi lending protocols are inherently vulnerable to oracle manipulation when they accept illiquid tokens as collateral
2. **"Code is law" defense rejected**: The jury's conviction established legal precedent that manipulating a DeFi protocol constitutes market manipulation under existing commodities law, regardless of whether the protocol is permissionless or whether the exploiter's transactions are technically valid on-chain
3. **Governance token capture**: Eisenberg's ability to vote on his own amnesty using stolen governance tokens exposed a fundamental weakness in token-weighted governance — that large token acquisitions (whether through purchase or theft) can be used to override community interests
4. **Thin liquidity as attack surface**: MNGO's approximately $30 million market cap meant that $10 million in capital could move the price 1,300% — demonstrating that the ratio of protocol TVL to collateral token liquidity is a critical security parameter

## Relevance to Market Health Metrics

Mango Markets' case demonstrates several indicators in the DN Institute [Market Health Metrics](https://dn.institute/research/market-health/docs/market-health-metrics/) framework:

- **Oracle integrity as health metric**: The gap between oracle-reported prices and actual executable market depth provides a measurable indicator of manipulation risk — protocols accepting collateral valued at oracle prices without liquidity-adjusted caps are structurally vulnerable
- **Token liquidity relative to protocol TVL**: The ratio of collateral token market depth to protocol TVL (here, ~$30M MNGO liquidity vs. ~$116M TVL) represents a quantifiable risk metric — low ratios indicate that the protocol can be drained through price manipulation
- **Governance concentration risk**: Token-weighted voting systems where a single entity can acquire controlling influence — whether through accumulation or exploitation — represent measurable governance centralization that should inform protocol health assessments
- **Post-exploit negotiation patterns**: The DAO "bug bounty" negotiation pattern — where attackers retain a percentage of stolen funds — creates perverse incentives that should be factored into risk assessment of protocols that have established such precedents

## References

1. Mango Markets, "Mango Markets Documentation." [docs.mango.markets](https://docs.mango.markets/)
2. CoinDesk, "How a Crypto Trader Drained $110M From DeFi Exchange Mango Markets," October 2022. [coindesk.com](https://www.coindesk.com/markets/2022/10/12/how-market-manipulation-led-to-a-100m-exploit-on-solana-defi-exchange-mango/)
3. Blockworks, "Avraham Eisenberg Reveals Himself as Mango Markets Exploiter," October 2022. [blockworks.co](https://blockworks.co/news/avraham-eisenberg-mango-markets-exploiter)
4. The Block, "Mango Markets Exploiter Eisenberg Proposes Resolution — Using Stolen Governance Tokens to Vote," October 2022. [theblock.co](https://www.theblock.co/post/176998/mango-markets-dao-approves-47-million-deal-with-exploiter)
5. DOJ, "Man Arrested for $110M Scheme to Defraud Decentralized Cryptocurrency Exchange," December 2022. [justice.gov](https://www.justice.gov/usao-sdny/pr/man-arrested-110-million-scheme-defraud-decentralized-cryptocurrency-exchange)
6. DOJ, "Avraham Eisenberg Convicted in First-Ever Cryptocurrency Open Market Manipulation Trial," April 2024. [justice.gov](https://www.justice.gov/usao-sdny/pr/avraham-eisenberg-convicted-first-ever-cryptocurrency-open-market-manipulation-trial)
7. Reuters, "Mango Markets manipulator Eisenberg's conviction overturned on venue grounds," May 2025. [reuters.com](https://www.reuters.com/legal/)
8. SEC, "SEC Settles With Mango DAO and Mango Labs for Offering Unregistered Crypto Asset Securities," January 2025. [sec.gov](https://www.sec.gov/newsroom/press-releases/2025-9)
