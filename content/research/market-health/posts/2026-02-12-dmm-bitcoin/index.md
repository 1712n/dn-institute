---
title: "DMM Bitcoin: $308M North Korean Heist via LinkedIn Social Engineering of Wallet Provider, Japan FSA Shutdown Order, and Lazarus Group Attribution"
date: 2026-02-12
entities:
  - DMM Bitcoin
  - Ginco
  - TraderTraitor
---

## Summary

1. **$308 million stolen — largest crypto hack of 2024**: On May 31, 2024, hackers stole 4,502.9 BTC (~$308 million / 48.2 billion yen) from Japanese cryptocurrency exchange DMM Bitcoin through a supply-chain social engineering attack that compromised a third-party wallet software provider rather than the exchange itself.
2. **Supply-chain attack via LinkedIn targeting Ginco employee**: North Korean hackers posing as a LinkedIn recruiter sent a malicious Python script disguised as a pre-employment coding test to an employee at Ginco, DMM Bitcoin's wallet management provider — compromising session cookies that were then used to manipulate a legitimate DMM Bitcoin transaction request.
3. **FBI/NPA attributed to North Korea's TraderTraitor**: On December 23, 2024, the FBI, Department of Defense Cyber Crime Center (DC3), and Japan's National Police Agency jointly attributed the hack to TraderTraitor (also known as Jade Sleet/UNC4899), a North Korean state-sponsored cyber threat group operating under the Lazarus Group umbrella.
4. **Exchange shut down entirely**: After the Japan FSA issued a business improvement order citing severe security deficiencies, DMM Bitcoin announced on December 2, 2024 that it would cease all operations and transfer customer accounts to SBI VC Trade — becoming the first major Japanese exchange to shut down due to a hack since Coincheck's near-closure in 2018.
5. **$55 billion yen emergency fundraising**: DMM Bitcoin's parent company DMM Group provided 48 billion yen in capital plus additional loans totaling approximately 55 billion yen (~$367 million) to guarantee full customer compensation, despite the exchange ultimately being unable to continue operations.

## Background

### DMM Bitcoin and DMM Group

**DMM Bitcoin** (officially Bitcoin.DMM.com) was a Japanese cryptocurrency exchange launched in **January 2018** as a subsidiary of **DMM Group** (DMM.com), a major Japanese e-commerce and internet conglomerate founded in 1999 and headquartered in Minato City, Tokyo. DMM Group, led by billionaire **Keishi Kameyama**, operated across digital entertainment, e-commerce, and financial services including DMM FX (forex trading) and DMM.com Securities [1].

DMM Bitcoin was licensed by Japan's **Financial Services Agency (FSA)** under the Payment Services Act as a registered crypto-asset exchange. The platform offered spot trading and leverage/margin trading across approximately **38 cryptocurrency types**.

### Ginco — The Wallet Infrastructure Provider

**Ginco** is a Japan-based enterprise cryptocurrency wallet software company that provided wallet management infrastructure to DMM Bitcoin. Ginco employees maintained access to the wallet management system used to process DMM Bitcoin's cryptocurrency transactions — making the company a critical link in DMM Bitcoin's custody chain.

## The Attack: LinkedIn to Transaction Manipulation

### Phase 1 — Social Engineering via LinkedIn (Late March 2024)

The attack began in **late March 2024** when a North Korean cyber actor contacted an employee at Ginco through LinkedIn [2]:

1. The attacker **posed as a recruiter** on LinkedIn
2. The target was a Ginco employee who **maintained access to Ginco's wallet management system**
3. The attacker sent a URL to a **malicious Python script hosted on GitHub**, disguised as a **pre-employment coding test**
4. The victim **copied the Python code to their personal GitHub page**, executing the malicious payload and compromising their system

### Phase 2 — Session Cookie Exploitation (Mid-May 2024)

After the initial compromise:

1. The attackers **exploited session cookie information** stolen from the compromised Ginco employee's system
2. Using these session cookies, they **impersonated the compromised employee**
3. They **gained access to Ginco's unencrypted communications system**
4. This provided visibility into how DMM Bitcoin transaction requests were processed through Ginco's infrastructure

### Phase 3 — Transaction Manipulation (May 31, 2024)

Using their access to Ginco's systems:

1. The attackers **intercepted and manipulated a legitimate transaction request** initiated by a DMM Bitcoin employee
2. The manipulation redirected **4,502.9 BTC** to wallets controlled by the attackers
3. Because the transaction originated from a legitimate request through Ginco's system, it bypassed DMM Bitcoin's internal controls

### Stolen Amount

| Detail | Value |
|--------|-------|
| Bitcoin stolen | 4,502.9 BTC |
| USD value | ~$305–$308 million |
| JPY value | ~48.2 billion yen |
| Ranking | Largest cryptocurrency hack of 2024 |

## Attribution: TraderTraitor / Lazarus Group

On **December 23, 2024**, three agencies jointly published the attribution [3]:

- **Federal Bureau of Investigation (FBI)**
- **Department of Defense Cyber Crime Center (DC3)**
- **Japan National Police Agency (NPA)**

The hack was attributed to **TraderTraitor**, a North Korean state-sponsored cyber threat group also tracked as:
- **Jade Sleet** (Microsoft)
- **UNC4899** (Mandiant/Google)
- **Slow Pisces**

TraderTraitor operates under the broader **Lazarus Group / APT38** umbrella, linked to the Democratic People's Republic of Korea (DPRK). The FBI noted that TraderTraitor "is often characterized by targeted social engineering directed at multiple employees of the same company simultaneously."

## Money Laundering: Peel Chains to Huione Guarantee

The stolen funds were laundered through a sophisticated multi-stage process [4]:

1. **Peel chains**: Stolen BTC was broken into progressively smaller amounts — starting at 499 BTC per hop, decreasing to 39 BTC by the third hop, and eventually distributed in increments of 10–20 BTC
2. **CoinJoin mixing**: Funds were passed through Bitcoin CoinJoin mixing services
3. **Cross-chain bridging**: After mixing, funds were bridged from Bitcoin to other blockchains
4. **Conversion to USDT**: Funds were swapped for Tether (USDT)
5. **Bridging to Tron**: USDT was moved to the Tron blockchain
6. **Huione Guarantee**: Funds were funneled to **Huione Guarantee**, a Cambodia-based online marketplace tied to the Huione Group, identified as a significant facilitator of cybercrime and money laundering

### Tracking and Interdiction Efforts

- **On-chain investigator ZachXBT** (citing Elliptic data) reported over **$35 million** laundered through Huione Guarantee
- ZachXBT disclosed **538 wallet addresses** linked to Lazarus Group and Huione
- **July 12, 2024**: Tether **blacklisted a Tron wallet address**, blocking approximately **$28.2 million** in stolen funds from reaching Huione
- **Chainalysis** corroborated the Lazarus Group attribution based on laundering patterns

No significant recovery of the stolen funds has been publicly reported.

## DMM Bitcoin's Response

### Emergency Fundraising

DMM Bitcoin moved quickly to secure funds from its parent group [5]:

| Date | Amount | Type |
|------|--------|------|
| June 3, 2024 | 5 billion yen (~$32M) | Loans |
| June 7, 2024 | 48 billion yen (~$308M) | Capital increase from DMM.com |
| June 10, 2024 | 2 billion yen (~$12.8M) | Subordinated debt financing |
| **Total** | **~55 billion yen (~$367M)** | |

DMM Bitcoin pledged to **guarantee the full amount of customer Bitcoin** by procuring equivalent BTC from DMM.com. Following the hack, the exchange restricted services including suspending spot purchase orders and delaying Japanese yen withdrawals.

### Japan FSA Business Improvement Order (September 26, 2024)

The **Kanto Local Finance Bureau** (under the FSA) issued an administrative business improvement order to DMM Bitcoin, citing [6]:

1. **Concentration of authority**: A single team managed both system operations and security oversight
2. **Lack of independent audits**: Departments were auditing themselves with no independent security reviews
3. **Inadequate transaction controls**: Violations of rules governing cryptocurrency transfer handling
4. **Poor logging practices**: Insufficient logs to support the theft investigation
5. **Inadequate private key management**: Centralized control over system operations and private key handling
6. **Insufficient risk management**: Severe shortcomings in overall risk management and security practices

DMM Bitcoin was given until **October 28, 2024** to submit remediation plans.

### Shutdown and Transfer to SBI VC Trade

On **December 2, 2024**, DMM Bitcoin announced it would **cease all operations** and liquidate the exchange, unable to recover operationally from the hack [7].

**Transfer to SBI VC Trade:**
- **SBI VC Trade**, a subsidiary of Japan's SBI Group financial conglomerate, agreed to absorb all DMM Bitcoin customers
- **Transfer date**: March 8, 2025
- All customer accounts and assets (both yen deposits and cryptocurrency) transferred automatically
- SBI VC Trade added **14 new cryptocurrencies** to accommodate DMM Bitcoin's supported assets
- Margin/leverage positions were not transferred — customers had to settle before the transfer date

## Comparison to Other Lazarus Group / TraderTraitor Hacks

| Incident | Date | Amount | Attack Method | Target |
|----------|------|--------|---------------|--------|
| Ronin Bridge | March 2022 | ~$625M | Fake LinkedIn job offer → malicious PDF | Sky Mavis engineer |
| Harmony Horizon | June 2022 | ~$100M | Compromised private keys | Bridge validators |
| Atomic Wallet | June 2023 | ~$100M | Supply chain / wallet compromise | Wallet users |
| Stake.com | September 2023 | ~$41M | Private key compromise | Exchange hot wallet |
| CoinsPaid | July 2023 | ~$37M | Social engineering | Payment processor |
| **DMM Bitcoin** | **May 2024** | **~$308M** | **LinkedIn → Ginco wallet provider** | **Third-party infrastructure** |
| WazirX | July 2024 | ~$235M | Transaction manipulation | Exchange multisig |
| Bybit | February 2025 | ~$1.5B | Docker project → Safe{Wallet} developer | Third-party infrastructure |

**Key pattern**: DMM Bitcoin and Bybit represent an evolution in Lazarus Group tactics — rather than attacking exchanges directly, they **compromise third-party infrastructure providers** (Ginco for DMM, Safe{Wallet} for Bybit) to manipulate legitimate transaction flows from the inside.

## Timeline

| Date | Event |
|------|-------|
| January 2018 | DMM Bitcoin launched |
| Late March 2024 | North Korean actor contacts Ginco employee via LinkedIn with malicious Python script |
| Mid-May 2024 | Attackers exploit stolen session cookies to access Ginco communications |
| May 31, 2024 | 4,502.9 BTC (~$308M) stolen via manipulated transaction request |
| June 3–10, 2024 | DMM Bitcoin raises ~55 billion yen from parent group for customer compensation |
| July 2024 | ZachXBT/Elliptic report $35M+ laundered through Huione Guarantee |
| July 12, 2024 | Tether blacklists Tron address, blocking ~$28.2M |
| September 26, 2024 | Japan FSA issues business improvement order |
| December 2, 2024 | DMM Bitcoin announces shutdown; transfer to SBI VC Trade |
| December 23, 2024 | FBI/DC3/NPA jointly attribute hack to TraderTraitor (North Korea) |
| March 8, 2025 | Customer accounts transferred to SBI VC Trade |

## Market Manipulation Implications

The DMM Bitcoin hack reveals critical supply-chain vulnerabilities in cryptocurrency exchange infrastructure:

1. **Third-party infrastructure as primary attack surface**: The attackers never directly compromised DMM Bitcoin's systems — instead targeting Ginco, DMM Bitcoin's wallet management provider, demonstrating that exchange security extends to every vendor in the custody chain
2. **Social engineering scalability**: A single LinkedIn message containing a malicious Python script ultimately led to the theft of $308 million, showing that state-sponsored groups can breach major financial institutions through the most basic social engineering vector
3. **Session cookie exploitation as credential theft**: The attackers did not need to crack passwords or bypass 2FA — stolen session cookies from a single compromised employee provided sufficient access to manipulate production transactions
4. **Regulatory response as market signal**: The FSA's business improvement order, followed by DMM Bitcoin's shutdown, demonstrates that regulatory action post-hack can serve as an indicator of exchange viability for market health assessment

## Relevance to Market Health Metrics

DMM Bitcoin's case demonstrates several indicators in the DN Institute [Market Health Metrics](https://dn.institute/research/market-health/docs/market-health-metrics/) framework:

- **Supply-chain security as exchange health metric**: The Ginco compromise demonstrates that exchange security cannot be assessed in isolation — the security posture of wallet providers, custodians, and other infrastructure partners must be included in any comprehensive exchange health evaluation
- **Third-party dependency mapping**: Identifying which external service providers have access to an exchange's transaction signing infrastructure provides a measurable risk surface — exchanges with fewer external dependencies in their signing chain present lower supply-chain risk
- **Parent company backing as resilience indicator**: DMM Group's ability to inject 55 billion yen within 10 days demonstrates that exchange backing by well-capitalized parent companies provides meaningful protection for customer funds — a factor assessable through corporate structure analysis
- **Regulatory compliance depth**: The FSA's findings — single-team operations, self-auditing, inadequate logging — represent measurable governance failures that should be detectable through regulatory disclosure analysis before an incident occurs

## References

1. CryptoNinjas, "Japan's DMM Group sets up bitcoin exchange," January 2018. [cryptoninjas.net](https://www.cryptoninjas.net/2018/01/11/japans-dmm-group-sets-bitcoin-exchange/)
2. FBI, "FBI, DC3, and NPA Identification of North Korean Cyber Actors Tracked as TraderTraitor Responsible for Theft of $308 Million from Bitcoin.DMM.com," December 2024. [fbi.gov](https://www.fbi.gov/news/press-releases/fbi-dc3-and-npa-identification-of-north-korean-cyber-actors-tracked-as-tradertraitor-responsible-for-theft-of-308-million-from-bitcoindmmcom)
3. The Hacker News, "North Korean Hackers Pull Off $308M Bitcoin Heist from DMM Bitcoin Exchange," December 2024. [thehackernews.com](https://thehackernews.com/2024/12/north-korean-hackers-pull-off-308m.html)
4. Cointelegraph, "Lazarus is moving millions from $305M DMM Bitcoin hack — ZachXBT," July 2024. [cointelegraph.com](https://cointelegraph.com/news/lazarus-group-suspected-moving-stolen-funds-dmm-bitcoin-hack)
5. Cointelegraph, "Japanese crypto exchange raises $320M to recover funds after hack," June 2024. [cointelegraph.com](https://cointelegraph.com/news/dmm-bitcoin-raises-320m-recover-funds-hack-crypto-exchange-raises-320-m-to-recover-funds-after-major-hack)
6. Regulation Asia, "Japan FSA Issues Business Improvement Order on DMM Bitcoin," September 2024. [regulationasia.com](https://www.regulationasia.com/japan-fsa-issues-business-improvement-order-on-dmm-bitcoin/)
7. CoinDesk, "DMM Bitcoin to Shut Down After $305M Hack," December 2024. [coindesk.com](https://www.coindesk.com/business/2024/12/02/japanese-crypto-exchange-dmm-bitcoin-to-shut-down-after-305-m-hack)
