---
title: "BitGrail: $170M Nano Token Loss Through Client-Side-Only Validation, Italian Court Declares Operator Personally Bankrupt, and Landmark Cryptocurrency Property Ruling"
date: 2026-02-12
entities:
  - BitGrail
  - Nano
  - Francesco Firano
---

## Summary

1. **17 million Nano tokens ($170M) missing — 13% of total supply**: BitGrail, a small Italian cryptocurrency exchange, reported 17 million Nano (XRB) tokens missing on February 9, 2018, valued at approximately $170 million — representing roughly 13% of total Nano supply and making it the largest single-asset cryptocurrency exchange loss at the time.
2. **Client-side-only withdrawal validation enabled unlimited extraction**: BitGrail relied exclusively on JavaScript client-side validation for withdrawals with no server-side verification — users could bypass the validation locally, and a double-credit bug doubled deposited balances in BitGrail's database without corresponding blockchain entries, allowing systematic extraction of unbacked funds.
3. **Operator knew of insolvency for months but continued accepting customers**: Italian courts found that unauthorized withdrawals began as early as July 2017, but operator Francesco Firano ("The Bomber") continued accepting new customers — growing the user base from 70,000 to 217,000 during the breach period — while secretly aware the exchange was insolvent.
4. **Italian court declared both exchange and operator personally bankrupt**: In January 2019, the Court of Florence declared both BitGrail S.r.l. and Firano personally bankrupt in a landmark ruling that classified cryptocurrency as legal property and a "means of payment" under Italian law — one of the first European court decisions establishing a legal framework for exchange insolvency.
5. **Police accused Firano of hacking his own exchange**: In December 2020, Italy's Postal and Communications Police alleged Firano was responsible for the hacks and charged him with computer fraud, self-laundering, and fraudulent bankruptcy — citing evidence that he transferred 230 BTC ($1.8M) to a personal account at a Malta-based exchange he allegedly owned three days before disclosing the loss.

## Background

### BitGrail and the Nano Listing

**BitGrail** was a small Italian cryptocurrency exchange operated by **Francesco Firano**, known online as **"The Bomber."** The exchange was registered as **BitGrail S.r.l.** and operated from Florence, Italy. BitGrail gained prominence in late 2017 as one of the few exchanges listing **Nano** (then called RaiBlocks/XRB), a feeless, instant-confirmation cryptocurrency founded by **Colin LeMahieu** [1].

During the late 2017 cryptocurrency bull market, Nano's price surged from **$0.22 on December 1, 2017** to an all-time high of approximately **$33–37 on January 2, 2018**. As one of the primary exchanges offering Nano trading, BitGrail attracted a surge of new users — growing from approximately 70,000 to **217,000 registered accounts**.

### The Vulnerability: Client-Side-Only Validation

BitGrail's software contained multiple compounding flaws that enabled systematic fund extraction [2]:

**1. Client-side JavaScript validation only**: Withdrawal requests were validated exclusively by client-side JavaScript with **no server-side verification**. Users could bypass the JavaScript validation locally and submit withdrawal requests exceeding their account balance.

**2. Double-credit bug**: A bug in BitGrail's deposit processing system **doubled account balances** — any time a user deposited funds, there was a chance they would receive twice the amount in their BitGrail balance, with the excess reflected in the database but not on the blockchain.

**3. Cross-account withdrawal bug**: A second vulnerability allowed one user to request a withdrawal to their wallet address using another account's balance, generating negative balances for victim accounts.

**4. Lack of idempotence**: BitGrail sent multiple withdrawal requests to the Nano node for the same transaction. Because the communication mechanism lacked idempotence, the Nano nodes processed duplicate withdrawal requests — resulting in "double withdrawals."

**5. Hot wallet architecture**: BitGrail stored all of its Nano holdings in a single hot wallet, maximizing the exposure to any withdrawal exploit.

## The Breach (July 2017 – February 2018)

### Timeline of Unauthorized Withdrawals

Italian court documents and police investigations established that the losses occurred over several months [3]:

| Period | Event |
|--------|-------|
| June–July 2017 | First unauthorized withdrawals: approximately **2.5 million Nano** disappear from BitGrail |
| October 2017 | Second major tranche: approximately **7.5 million Nano** stolen; BitGrail was aware of an operational flaw since at least this date |
| December 2017 | Firano converts central wallet to "cold wallet" system; exchange activity becomes intermittent |
| Early January 2018 | Multiple users report negative balances; BitGrail halts all Nano withdrawals and deposits |
| January 28, 2018 | BitGrail closes Nano withdrawals permanently |
| February 2–5, 2018 | Firano deposits **230 BTC (~$1.8M)** to his personal account on The Rock Trading, a Malta-based exchange he allegedly owned |
| February 8, 2018 | Firano privately informs the Nano Core Team of the shortfall |
| February 9, 2018 | BitGrail publicly announces insolvency: "internal checks revealed unauthorized transactions which led to a 17 million Nano shortfall" |

### Exploitation Pattern

Malicious actors exploited the balance glitch to withdraw excess Nano, then **arbitraged those amounts on other exchanges** — particularly **Mercatox** — and repeated the cycle by re-depositing on BitGrail. The court determined that "it was the BitGrail exchange that [because of a software flaw] actually requested to the node multiple times to allow the funds to leave the wallet" [4].

## Firano's Response and the Hard Fork Demand

### Firano's Claims

- Blamed the Nano protocol for the loss, claiming a bug in Nano nodes failed to verify transactions properly
- Demanded the Nano development team perform a **hard fork** to recover the stolen funds (similar to Ethereum/Ethereum Classic after the 2016 DAO hack)
- Filed a police report presenting himself as a victim of hacking
- Stated the losses were only discovered through "internal checks" in February 2018

### Nano Foundation's Response

The Nano Core Team immediately launched an investigation and **refused** Firano's hard fork demand [5]:

- Published a statement that no double-spending was detected on the Nano ledger: "We have no reason to believe the loss was due to an issue in the Nano protocol"
- Released **private conversations** between Firano and Nano core team members (including developer **Zack Shapiro** and founder Colin LeMahieu) to demonstrate Firano's misleading behavior
- Stated: "Firano has been misleading the Nano Core Team and the community regarding the solvency of the BitGrail exchange for a significant period of time"
- Prepared blockchain entries, chat logs, and screenshots for law enforcement

### Legal Fund for Victims

- The Nano Foundation contacted **Espen Enger**, a representative of approximately 600 BitGrail victims
- On **April 9, 2018**, announced it would match victim donations to the legal fund **up to $1 million**, targeting a $2 million total
- Victims had already raised over **$300,000**; the Nano Foundation's match brought the fund to approximately $600,000
- Retained Italian law firm **BonelliErede** to file bankruptcy petitions [6]

## Italian Court Ruling (January 2019)

### Bankruptcy Declaration

The **Court of Florence, Bankruptcy Division**, issued its ruling on **January 21, 2019** [7]:

- Both **BitGrail S.r.l.** and **Francesco Firano personally** were declared bankrupt
- Firano was found personally liable because "the losses originated from Mr. Firano's conduct" and he failed to promptly report the loss to depositors
- The court determined the service agreement between BitGrail and users constituted a **deposito irregolare** (irregular deposit), making the exchange administrator the owner with obligation to return equivalent amounts

### Landmark Legal Precedent

The ruling established important legal precedent [8]:

- Cryptocurrencies were classified as **legal property** and a **"means of payment"** under Italian law, relying on anti-money laundering legislation
- Nano tokens were classified as **fungible assets** since all units are identical
- This was one of the **first European court rulings** to establish a comprehensive legal framework for cryptocurrency exchange insolvency

### Seized Assets

- Over **$1 million** in Firano's personal assets, including his car
- Millions of dollars in cryptocurrency from BitGrail exchange accounts
- Courts authorized blocking of platforms and seizure of cryptocurrency wallets
- Firano was barred from holding managerial positions or conducting business activities

## Criminal Investigation (December 2020)

Italy's **Postal and Communications Police** (Polizia Postale e delle Comunicazioni) formally alleged that Firano was responsible for the hacks [9]:

### Charges Against Firano

1. **Computer fraud** (frode informatica)
2. **Self-laundering** (auto-riciclaggio)
3. **Fraudulent bankruptcy** (bancarotta fraudolenta)

### Key Evidence

- Six search warrants issued against Firano and collaborators
- Multiple computers seized
- The 230 BTC transfer to his personal Malta-based exchange account was traced with assistance from the **Financial Information Unit of Italy's central bank**
- Authorities intervened before Firano could fully convert the cryptocurrency to fiat currency

**Ivano Gabrielli**, director of Italy's national cybercrime center, stated: *"It is not yet clear whether he participated actively in the theft or if he simply decided not to increase security measures after discovering it."*

The case was described as **"the biggest cyber-financial attack in Italy and one of the biggest in the world"** [10].

## Restitution Proceedings

In 2020, bankruptcy trustees invited creditors to file refund claims:

| Tranche | Details |
|---------|---------|
| Creditor claims | Options to receive restitution in euros or cryptocurrency, calculated based on holdings on the bankruptcy declaration date |
| Asset distribution | BitGrail's remaining assets exceeded EUR 16M+ in Bitcoin and EUR 20M+ in Nano coins |
| Rejection criteria | Some applications rejected for failure to complete identification procedures or lack of proof |
| Appeal rights | Approved and denied creditors could dispute claims of other creditors and appeal |

Full restitution for the largest losses was not achievable given the gap between total claims and remaining assets.

## Market Impact

- **NANO token**: Dropped from ~$11.50 to ~$9.12 on the day of announcement; eventually fell below $1 (95%+ decline from ATH), compounded by the 2018 bear market
- **Trading volume**: BitGrail had been one of the few Nano exchanges; volume declined from approximately $50 million; over 80% of Nano trades subsequently moved to Binance
- **Community impact**: Approximately **217,000–230,000 users** affected; victims organized as the **BitGrail Victims Group (BGVG)** on Medium
- **Investor confidence**: The incident severely damaged Nano's reputation despite the protocol itself being blameless

### Class Action Lawsuits

- **Silver Miller** law firm filed a class action in the **U.S. District Court, Eastern District of New York** against Nano, alleging violations of U.S. securities regulations and demanding Nano perform a hard fork
- A second class action was also filed against Nano [11]

## Timeline

| Date | Event |
|------|-------|
| June–July 2017 | First unauthorized withdrawals (~2.5 million Nano) |
| October 2017 | Second major tranche (~7.5 million Nano); Firano aware of operational flaw |
| January 2, 2018 | Nano (XRB) reaches ATH of ~$33–37 |
| January 28, 2018 | BitGrail permanently closes Nano withdrawals |
| February 2–5, 2018 | Firano transfers 230 BTC to personal Malta-based exchange account |
| February 9, 2018 | BitGrail announces insolvency; 17 million Nano shortfall disclosed |
| February 12, 2018 | Nano Foundation publishes official statement accusing Firano of misleading behavior |
| April 9, 2018 | Nano Foundation announces $1 million legal fund match |
| April 26, 2018 | BonelliErede files bankruptcy petitions; Florence Prosecutor's Office intervenes |
| January 21, 2019 | Court of Florence declares both BitGrail and Firano personally bankrupt |
| December 2020 | Italian police formally accuse Firano of computer fraud, self-laundering, and fraudulent bankruptcy |

## Market Manipulation Implications

The BitGrail incident reveals critical vulnerabilities in small exchange operations and their impact on market integrity:

1. **Client-side-only validation as catastrophic security failure**: BitGrail's reliance on JavaScript client-side validation with no server-side verification represents one of the most basic security failures in exchange history — demonstrating that even the most elementary web security oversights can lead to nine-figure losses when applied to custody of digital assets
2. **Single-exchange listing dependency as manipulation vector**: Nano's concentration on BitGrail as a primary trading venue meant that the exchange's insolvency directly impacted the token's price and reputation — a form of indirect market manipulation where exchange failure is indistinguishable from protocol failure from the perspective of retail investors
3. **Undisclosed insolvency as ongoing fraud**: Firano's continued acceptance of new customers — growing the user base from 70,000 to 217,000 — while knowing the exchange was insolvent constituted ongoing misrepresentation that deepened losses with each new deposit, demonstrating that exchange solvency transparency is a critical market integrity requirement
4. **Personal asset extraction during insolvency as red flag**: The transfer of 230 BTC to a personal account days before public disclosure follows a pattern seen in other exchange failures (QuadrigaCX, FTX) where operators attempt to extract personal value before collapse — making pre-disclosure personal transfers a detectable on-chain signal

## Relevance to Market Health Metrics

BitGrail's case demonstrates several indicators in the DN Institute [Market Health Metrics](https://dn.institute/research/market-health/docs/market-health-metrics/) framework:

- **Exchange technical infrastructure assessment**: BitGrail's client-side-only validation failure demonstrates that basic web security practices — server-side validation, idempotent API design, cold/hot wallet segregation — should be measurable components of exchange health scoring, particularly for smaller exchanges that may lack formal security audits
- **Listing concentration risk**: The ratio of a token's trading volume concentrated on a single exchange provides a measurable vulnerability indicator — tokens where >50% of volume occurs on a single small exchange face elevated risk of simultaneous price and liquidity collapse if that exchange fails
- **Operator transparency metrics**: The time gap between Firano's awareness of insolvency (October 2017) and public disclosure (February 2018) — approximately four months — demonstrates that operator disclosure timeliness is a critical health metric, and that prolonged withdrawal restrictions should be treated as a leading indicator of potential insolvency
- **Proof-of-reserves as minimum standard**: BitGrail's case predated the widespread adoption of proof-of-reserves attestations — the fundamental mismatch between database balances (inflated by the double-credit bug) and actual blockchain holdings would have been detectable through even basic reserve verification mechanisms

## References

1. TechCrunch, "Italian cryptocurrency exchange gets hacked for $170 million in Nano," February 2018. [techcrunch.com](https://techcrunch.com/2018/02/12/bitgrail-hack-nano/)
2. Hacker News, "BitGrail lost $170M because only client-side validation was used." [news.ycombinator.com](https://news.ycombinator.com/item?id=16353966)
3. Cointelegraph, "Owner of Hacked Crypto Exchange BitGrail Sentenced to Return Funds to Customers," January 2019. [cointelegraph.com](https://cointelegraph.com/news/owner-of-hacked-crypto-exchange-bitgrail-sentenced-to-return-funds-to-customers)
4. The Next Web, "Italian court forces BitGrail CEO to repay $170M in 'lost' cryptocurrency," January 2019. [thenextweb.com](https://thenextweb.com/news/bitgrail-court-cryptocurrency-nano)
5. Nano Foundation, "Official Statement Regarding BitGrail Insolvency," February 2018. [medium.com](https://medium.com/nanocurrency/official-statement-regrading-bitgrail-insolvency-ed4422bf274b)
6. Bitcoin Magazine, "Nano To Match $1M In Legal Fund Donations To Support BitGrail Hack Victims," April 2018. [bitcoinmagazine.com](https://bitcoinmagazine.com/culture/nano-match-1m-legal-fund-donations-support-bitgrail-hack-victims)
7. BitGrail Victims Group, "THE BITGRAIL EXCHANGE RULING: A WIN FOR CRYPTOCURRENCY EXCHANGE USERS," January 2019. [medium.com](https://medium.com/@bitgrailvictims/the-bitgrail-exchange-ruling-a-win-for-cryptocurrency-exchange-users-50df6c383571)
8. Clifford Chance, "Italian court rules that cryptocurrency is 'property' and a 'means of payment'." [cliffordchance.com](https://www.cliffordchance.com/insights/resources/blogs/talking-tech/en/articles/2019/10/italian-court-rules-that-cryptocurrency-is--property.html)
9. Decrypt, "Italian Police Accuse BitGrail CEO of Money Laundering," December 2020. [decrypt.co](https://decrypt.co/52145/bitgrail-hacker-who-stole-e120-million-has-been-caught)
10. CoinDesk, "BitGrail Operator May Have Hacked Own Exchange to Steal EUR 120M, Police Allege," December 2020. [coindesk.com](https://www.coindesk.com/markets/2020/12/21/bitgrail-operator-may-have-hacked-own-exchange-to-steal-120m-police-allege)
11. Finance Magnates, "$170 Million Mistake: BitGrail May Have Been Aware of Bug that Led to Hack," February 2018. [financemagnates.com](https://www.financemagnates.com/cryptocurrency/news/170-million-mistake-bitgrail-may-aware-bug-led-hack/)
