---
title: "Coincheck: $534M NEM Hack, Hot Wallet Negligence, and Japan's Regulatory Transformation"
date: 2026-02-12
entities:
  - Coincheck
  - NEM
---

## Summary

1. **$534 million stolen — largest crypto hack at the time**: On January 26, 2018, hackers stole 523 million NEM (XEM) tokens worth approximately $534 million (58 billion yen) from Coincheck's hot wallet, surpassing even Mt. Gox as the largest cryptocurrency theft in nominal dollar terms at that time.
2. **Entire balance in a single hot wallet**: Coincheck stored its entire NEM holdings in a single internet-connected hot wallet with no multi-signature security, with CEO Koichiro Wada citing "difficulty of the technology and a lack of staff" as the reason for not implementing cold storage.
3. **260,000 users compensated at $0.81 per NEM**: Coincheck announced compensation of 88.549 JPY (~$0.81) per NEM token — approximately 20% below the value at the time of theft — paying a total of 46.3 billion yen (~$426 million) from its own reserves beginning March 12, 2018.
4. **40% laundered on dark web**: Despite the NEM Foundation's automated tagging system that marked all stolen tokens as "tainted," hackers laundered approximately 40% of the stolen NEM through dark web exchanges at a 15% discount before the tracking system ceased operations.
5. **Catalyst for Japan's crypto regulatory framework**: The hack directly triggered the creation of the Japan Virtual Currency Exchange Association (JVCEA), FSA business improvement orders against seven exchanges, and the 2019 Payment Services Act amendment mandating 95% cold storage for customer assets.

## Background

Coincheck was originally incorporated as **ResuPress, Inc.** in 2012 by **Koichiro Wada** and **Yusuke Otsuka**. The Coincheck exchange launched approximately in 2014, growing to become one of Japan's largest cryptocurrency trading platforms. By January 2018, the exchange served hundreds of thousands of users trading Bitcoin, Ethereum, NEM, and other cryptocurrencies against the Japanese yen.

At the time of the hack, Coincheck was operating as a **"quasi-operator"** — it had applied for but not yet received a full license from Japan's Financial Services Agency (FSA) under the Payment Services Act. Despite handling hundreds of millions in customer funds, the exchange had not implemented industry-standard security measures for its NEM holdings.

## The Hack

### Attack Vector: Phishing and Malware (January 26, 2018)

On January 26, 2018, at approximately **3:00 AM JST**, hackers executed one of the largest cryptocurrency thefts in history [1]:

- Attackers used **phishing emails** to trick a Coincheck employee into downloading malware
- The malware included **Mokes** and **Netwire** — remote access trojans previously associated with Russian cybercriminal groups
- Once installed, the malware provided unauthorized access to the employee's computer
- The attackers stole the **private key** to Coincheck's NEM hot wallet
- **523 million NEM tokens** (worth ~$534 million / 58 billion yen) were transferred to multiple external addresses
- Coincheck later identified and published **11 addresses** where the stolen funds were sent

### Why a Hot Wallet?

Coincheck's decision to store its entire NEM balance in a single hot wallet represented a catastrophic deviation from industry best practices [2]:

- **No cold storage**: All 523 million NEM tokens were held in an internet-connected wallet
- **No multi-signature security**: Coincheck had not implemented NEM's built-in multi-signature wallet feature
- At a press conference on January 27, CEO Wada stated the exchange failed to implement these measures due to **"the difficulty of the technology and a lack of staff able to carry out the task"**
- The NEM Foundation responded: **"Had Coincheck used the NEM multi-signature wallet, this could not have happened"**
- For comparison, industry best practice (e.g., Coinbase) required approximately 98% of holdings in cold storage

## NEM Foundation Tracking

The NEM Foundation created an **automated tagging system** using NEM's mosaic feature to trace stolen funds in real time [3]:

- All funds associated with the theft were marked with a tag identifying them as **"tainted"**
- Any cryptocurrency exchange could verify whether NEM tokens being deposited originated from the hack
- The NEM protocol's flexibility enabled real-time tracing, making stolen tokens theoretically unusable on regulated platforms

**However, the system had critical limitations:**

- The tagging process required approximately **2–3 minutes per address**, meaning hackers could move funds faster than they could be tagged
- Hackers laundered approximately **40% of the stolen tokens** by selling them on the **dark web at a 15% discount**, converting primarily to Bitcoin
- On **March 18, 2018**, the NEM Foundation **ceased tracking operations** — the balance of the account believed to belong to the hackers had reached zero

## Coincheck's Response and User Compensation

### Press Conference (January 26–27, 2018)

Coincheck held a **90-minute press conference** at the Tokyo Stock Exchange headquarters, with CEO Wada and COO Otsuka appearing and bowing in apology. The exchange announced it would **compensate all 260,000 affected users using its own capital** [4].

### Compensation Details

| Detail | Value |
|--------|-------|
| Compensation rate | 88.549 JPY per NEM (~$0.81 USD) |
| Calculation method | Weighted average trading price on Zaif XEM/JPY exchange |
| Total compensation | ~46.3 billion yen (~$426 million USD) |
| Affected users | ~260,000 |
| Refunds began | March 12, 2018 |
| Refunds completed | March 12, 2019 |
| Funding source | Coincheck's own capital reserves |

The compensation rate of 88.549 JPY was approximately **20% below** the ~58 billion yen value of the stolen tokens at the time of theft, as it reflected the weighted average price rather than the peak price.

### Lawsuits

Despite the compensation commitment, affected users filed legal action:
- **February 15, 2018**: 7 plaintiffs sued at the Tokyo District Court
- **February 27, 2018**: 132 plaintiffs sued for 228 million yen (~$2 million)

## Monex Group Acquisition

On **April 6, 2018**, Japanese online brokerage **Monex Group** announced its acquisition of Coincheck [5]:

- **Purchase price**: 3.6 billion yen (~$33.5 million) for 100% of shares
- **Execution date**: April 16, 2018
- Co-founders Wada and Otsuka stepped down as CEO/Director but remained as operating officers
- **Toshihiko Katsuya** (Monex Group Managing Director) became Coincheck's new Representative Director
- **January 11, 2019**: Coincheck received its official FSA license, becoming fully registered approximately 12 months after the hack

## Arrests and Recovery

### Original Hackers

The perpetrators of the hack have **never been identified or arrested**. Attribution remains unclear — a 2018 investigation pointed toward North Korea, while a 2019 follow-up implicated Russian developers based on the Mokes and Netwire malware variants [6].

### Money Laundering Arrests

- **March 11, 2020**: Tokyo Metropolitan Police arrested **two men** (one from Osaka, one from Hokkaido) suspected of illegally exchanging stolen NEM tokens
- The Osaka suspect was accused of transacting approximately **24 million NEM coins** and potentially accessing approximately 200 accounts
- Both were arrested under the Punishment of Organized Crimes and Proceeds of Crime Control Act
- By 2021, **more than 30 individuals** had been charged for exchanging stolen NEM tokens, accounting for approximately one-third of the stolen value

### Fund Recovery

**No significant amount of the original stolen NEM was recovered.** The laundering was accomplished primarily through dark web exchanges before the NEM Foundation's tracking system could prevent conversion.

## Japanese Regulatory Response

### Immediate Actions (January–March 2018)

The FSA responded aggressively to the Coincheck hack [7]:

- **January 29, 2018**: Kanto Local Finance Bureau issued a **business improvement order** to Coincheck
- **January 30, 2018**: FSA ordered **all cryptocurrency exchange operators** to review system-risk management and report results
- **March 8, 2018**: Business improvement orders issued to **seven exchanges**:
  - **Two suspended** (Bit Station and FSHO)
  - **Five ordered to improve** (Tech Bureau/Zaif, GMO Coin, Bicrements, Mr. Exchange, and Coincheck)
- **No new exchange licenses** were granted in all of 2018

### JVCEA Creation (2018)

The hack was the direct catalyst for the **Japan Virtual Currency Exchange Association (JVCEA)** [8]:

- Established in March–April 2018 by **16 licensed exchanges**
- **October 24, 2018**: FSA accredited JVCEA as a **Certified Self-Regulatory Organization** under the Payment Services Act
- Authority to set rules for customer asset protection, AML/CTF standards, and operational guidelines
- Power to conduct inspections and impose sanctions on member exchanges

### 2019 Payment Services Act Amendment

The legislative response, passed in May 2019 and enforced May 1, 2020, directly addressed the exact failures that enabled the Coincheck hack [9]:

- **Cold storage mandate**: Exchanges must store at least **95% of customers' crypto assets in cold wallets** (offline)
- **Hot wallet matching**: For any amount in hot wallets (up to 5%), the exchange must hold an equivalent amount of its own crypto assets in cold storage as a "Redemption Guarantee"
- **Customer fund separation**: Exchanges must manage customer crypto assets **separately from their own assets**, with statutory preference rights
- **Custody regulation**: Crypto asset custody services brought under the PSA, requiring custodian registration
- **Terminology change**: "Virtual currency" renamed to **"crypto assets" (暗号資産)** to align with international standards

## Market Manipulation Implications

The Coincheck hack illustrates fundamental exchange security failures:

1. **Hot wallet negligence as systemic risk**: Storing $534 million in a single internet-connected wallet without multi-signature security represents the most basic custody failure — one that no amount of market monitoring can detect externally
2. **Unregulated operator risk**: Coincheck was operating as an unlicensed "quasi-operator" at the time of the hack, demonstrating that regulatory status is a prerequisite indicator for exchange reliability
3. **Malware-based private key theft**: The phishing → malware → key extraction attack chain demonstrated that exchange security depends on employee-level security hygiene — a factor invisible to market participants
4. **Tagging limitations**: The NEM Foundation's tracking system, despite being technically innovative, could not prevent 40% of stolen funds from being laundered through dark web channels, demonstrating that blockchain-level tracing is insufficient without exchange-level compliance enforcement

## Relevance to Market Health Metrics

Coincheck's case demonstrates several indicators in the DN Institute [Market Health Metrics](https://dn.institute/research/market-health/docs/market-health-metrics/) framework:

- **Custody infrastructure as health indicator**: The absence of cold storage and multi-signature security at Japan's largest exchange by NEM volume demonstrates that custody practices must be assessed independently of trading volume or market share
- **Regulatory status as prerequisite**: Coincheck's "quasi-operator" status — handling hundreds of millions without a license — represents a regulatory red flag that should inform exchange risk assessments
- **Compensation capacity as resilience metric**: Coincheck's ability to compensate 260,000 users from its own reserves ($426 million) — and the Monex acquisition that followed — provides a benchmark for evaluating exchange resilience after security failures
- **Regulatory response as market structure improvement**: The direct chain from Coincheck hack → JVCEA creation → 95% cold storage mandate demonstrates how individual exchange failures can produce systemic security improvements

## References

1. CNBC, "Japanese cryptocurrency exchange loses more than $500 million to hackers," January 2018. [cnbc.com](https://www.cnbc.com/2018/01/26/japanese-cryptocurrency-exchange-loses-more-than-500-million-to-hackers.html)
2. Fortune, "Coincheck Hack: How to Steal $500 Million in Cryptocurrency," January 2018. [fortune.com](https://fortune.com/2018/01/31/coincheck-hack-how/)
3. Cointelegraph, "$530 Mln in XEM Stolen From Coincheck Can Be Traced, NEM Team Confirms," January 2018. [cointelegraph.com](https://cointelegraph.com/news/530-million-in-xem-stolen-from-coincheck-can-be-traced-nem-team-confirms)
4. NBC News, "Hacked Japanese cryptocurrency exchange Coincheck to repay $425 million," January 2018. [nbcnews.com](https://www.nbcnews.com/news/world/hacked-japanese-cryptocurrency-exchange-coincheck-repay-425-million-n841761)
5. Bloomberg, "Hacked Crypto Exchange Sold for $34 Million to Japan's Monex," April 2018. [bloomberg.com](https://www.bloomberg.com/news/articles/2018-04-06/hacked-crypto-exchange-sold-for-34-million-to-japan-s-monex)
6. Cointelegraph, "Two Japanese Men Arrested for 'Fencing' NEM From Coincheck Hack," March 2020. [cointelegraph.com](https://cointelegraph.com/news/two-japanese-men-arrested-for-fencing-nem-from-coincheck-hack)
7. Library of Congress, "Regulation of Cryptocurrency: Japan." [loc.gov](https://maint.loc.gov/law/help/cryptocurrency/japan.php)
8. Baker McKenzie, "Japanese FSA accredits JVCEA as self-regulatory organization," November 2018. [bakermckenzie.com](https://blockchain.bakermckenzie.com/2018/11/13/japanese-financial-services-agency-accredits-the-japan-virtual-currency-exchange-association-as-a-self-regulatory-organization/)
9. K&L Gates, "Japan's New Crypto Regulation: 2019 Amendments to Payment Services Act," November 2019. [klgates.com](https://www.klgates.com/Japans-New-Crypto-Regulation-2019-Amendments-to-Payment-Services-Act-and-Financial-Instruments-and-Exchange-Act-of-Japan-11-26-2019)
