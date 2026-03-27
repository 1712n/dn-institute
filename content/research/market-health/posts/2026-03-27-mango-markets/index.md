---
title: "Mango Markets: Oracle Manipulation and the $114 Million DeFi Exploit"
date: 2026-03-27
entities:
  - Mango Markets
  - Avraham Eisenberg
  - MNGO
---

## Summary

1. **$114 Million Exploit:** On October 11, 2022, trader Avraham Eisenberg manipulated the price oracle of the Solana-based DeFi protocol Mango Markets, artificially inflating the price of MNGO token to borrow $114 million against his inflated collateral — effectively draining the protocol's treasury.
2. **Open Market Manipulation:** Eisenberg publicly claimed the exploit was a "highly profitable trading strategy" that was legal, making no attempt to conceal his identity. He engaged in public negotiations with the Mango DAO to return a portion of the funds.
3. **DOJ Criminal Conviction:** Eisenberg was arrested in December 2022 and charged with commodities fraud and market manipulation. In April 2024, a federal jury convicted him on all counts — the first conviction for oracle manipulation in a DeFi protocol.
4. **SEC and CFTC Parallel Actions:** Both the SEC and CFTC filed civil charges, with the SEC classifying MNGO as a security and the CFTC treating it as a commodity — creating overlapping jurisdiction claims.
5. **Sentencing:** Eisenberg was sentenced to 52 months in federal prison in August 2025.

## Background

Mango Markets was a decentralized exchange and lending protocol built on the Solana blockchain. Users could trade perpetual futures, lend and borrow assets, and use their token holdings as collateral. The protocol relied on oracle price feeds to determine the value of collateral — a dependency that became the attack vector.

Avraham Eisenberg, a 27-year-old trader from New York, executed the exploit openly, later stating on Twitter that he had conducted a "highly profitable trading strategy" and that "all of our actions were legal open market actions."

## Metrics used

### Oracle manipulation mechanism

The exploit followed a precise sequence:

1. **Position building:** Eisenberg funded two accounts on Mango Markets with approximately $5 million each (total $10 million).
2. **Perp position:** Using one account, he took a massive long position on MNGO-PERP (perpetual futures on the MNGO token). The other account took the opposite short position.
3. **Spot market manipulation:** Eisenberg then purchased large quantities of MNGO tokens on low-liquidity spot markets (primarily on Ascendex and FTX), driving the spot price from approximately $0.03 to $0.91 — a 30x increase.
4. **Oracle update:** The Mango Markets oracle (Pyth and Switchboard) updated to reflect the new spot price, which inflated the value of Eisenberg's long MNGO-PERP position.
5. **Borrowing against inflated collateral:** With his collateral now showing dramatically higher value, Eisenberg used the unrealized profit on his long position to borrow $114 million in various tokens (USDC, SOL, BTC, MSOL, and others) from the Mango Markets lending pools.
6. **Withdrawal:** He withdrew the borrowed funds, leaving the protocol insolvent.

### The "self-identified" aftermath

Unlike most DeFi exploiters, Eisenberg did not attempt anonymity:

- He publicly identified himself on Twitter within days of the exploit.
- He negotiated with the Mango DAO governance forum, eventually agreeing to return $67 million while retaining $47 million as a "bug bounty."
- He framed the exploit as legitimate market activity, arguing that manipulating price oracles through open-market purchases was not illegal.

## Regulatory actions and legal outcomes

### DOJ criminal charges — December 2022

Eisenberg was arrested on December 26, 2022 in Puerto Rico. He was charged with:

- Commodities fraud (18 U.S.C. § 1348)
- Commodities market manipulation (7 U.S.C. § 9(a)(2))

### Trial and conviction — April 2024

A federal jury in the Southern District of New York convicted Eisenberg on both counts after a two-week trial. The conviction established that manipulating DeFi oracle prices through coordinated spot market purchases constitutes market manipulation under federal law — even when conducted through "open market" transactions.

### Sentencing — August 2025

Eisenberg was sentenced to **52 months (approximately 4.3 years)** in federal prison.

### SEC civil action

The SEC filed a civil complaint classifying MNGO as a security and charging Eisenberg with securities fraud and market manipulation.

### CFTC civil action

The CFTC filed a parallel complaint treating MNGO perpetual futures as commodity swaps and charging Eisenberg with commodities fraud and manipulation.

## Timeline

| Date | Event |
|--|--|
| 2022-10-11 | Eisenberg exploits Mango Markets for $114M via oracle manipulation |
| 2022-10-15 | Mango DAO negotiation — Eisenberg returns $67M, keeps $47M |
| 2022-12-26 | Eisenberg arrested in Puerto Rico |
| 2023-01 | DOJ indictment filed (S.D.N.Y.) |
| 2023-01 | SEC and CFTC file parallel civil charges |
| 2024-04 | Federal jury convicts Eisenberg on all counts |
| 2025-08 | Sentenced to 52 months in federal prison |

## References

1. DOJ, "[Avraham Eisenberg Convicted of Commodities Fraud and Manipulation](https://www.justice.gov/usao-sdny/pr/avraham-eisenberg-convicted-commodities-fraud-and-manipulation)," April 2024.
2. SEC, "[SEC Charges Avraham Eisenberg with Manipulating Mango Markets](https://www.sec.gov/newsroom/press-releases/)," January 2023.
3. CFTC, "[CFTC Charges Avraham Eisenberg with Market Manipulation](https://www.cftc.gov/PressRoom/PressReleases/)," January 2023.
4. CoinDesk, "[Mango Markets Exploiter Avraham Eisenberg Arrested](https://www.coindesk.com/policy/2022/12/28/mango-markets-exploiter-avraham-eisenberg-arrested/)," December 28, 2022.
5. The Block, "[Avraham Eisenberg describes $114 million Mango Markets exploit as 'highly profitable trading strategy'](https://www.theblock.co/post/176937)," October 2022.
