---
title: "Bybit: $1.5 Billion Lazarus Group Heist, Safe{Wallet} Supply Chain Attack, and 72-Hour Reserve Recovery"
date: 2026-02-12
entities:
  - Bybit
  - ETH
---

## Summary

1. **$1.5 billion stolen — largest crypto heist in history**: On February 21, 2025, North Korea's Lazarus Group stole approximately $1.5 billion in Ethereum and Ethereum-based tokens from Bybit's cold wallet, surpassing the Ronin Network hack ($625 million) as the largest single cryptocurrency theft ever recorded.
2. **Supply chain attack via Safe{Wallet}**: The hack was not a direct breach of Bybit's systems — attackers compromised a Safe{Wallet} developer's macOS workstation on February 4, 2025 via a malicious Docker project, then injected JavaScript into Safe{Wallet}'s AWS infrastructure that specifically targeted Bybit's cold wallet transactions.
3. **FBI attribution to North Korea**: On February 26, 2025, the FBI issued a Public Service Announcement officially attributing the attack to North Korea's "TraderTraitor" threat actor (Lazarus Group), publishing 51 Ethereum addresses associated with the stolen funds.
4. **$5 billion withdrawal run survived**: Bybit processed over $5 billion in withdrawals in the days following the hack without halting operations, replenishing its reserves within 72 hours through bridge loans and OTC purchases of approximately 447,000 ETH.
5. **86% of stolen ETH converted to BTC**: By March 20, 2025, the attackers had converted 86.29% of the stolen ETH to Bitcoin primarily through THORChain, with 27.59% of funds going completely dark through mixers and P2P networks by April 2025.

## Background

Bybit is a cryptocurrency exchange founded in 2018 by **Ben Zhou**, a former forex executive. Headquartered in Dubai, UAE, Bybit grew to become one of the world's largest crypto exchanges by trading volume, with over **$17 billion in total assets** under management as of February 2025.

Bybit used **Safe{Wallet}** (formerly Gnosis Safe), an industry-standard multi-signature wallet solution, to manage its Ethereum cold storage. The exchange had been publishing regular **Proof of Reserves reports since June 2024**, with independent audits confirming reserve ratios above 100%.

## The Attack: Supply Chain Compromise

### Phase 1 — Developer Machine Compromise (February 4, 2025)

The attack began 17 days before the actual theft. Security firm **Sygnia** and Safe{Wallet}'s own investigation revealed the following attack chain [1]:

- A Safe{Wallet} developer (designated "Developer1") had their **Apple macOS workstation compromised** on February 4, 2025
- The developer downloaded a malicious Docker project named **"MC-Based-Stock-Invest-Simulator-main"**, likely delivered through social engineering
- The Docker project initiated network traffic to the domain `getstockprice[.]com`
- The malware harvested the developer's **AWS session tokens**, allowing the attackers to bypass multi-factor authentication and access Safe{Wallet}'s cloud infrastructure

### Phase 2 — JavaScript Injection

With access to Safe{Wallet}'s AWS environment, the attackers:

- Injected **malicious JavaScript** into Safe{Wallet}'s web UI files hosted on an **AWS S3 bucket** serving `app.safe.global`
- The malicious code was designed to activate **only when Bybit's specific cold wallet initiated a transaction** — all other users saw unaltered, normal behavior
- This targeted approach avoided detection during the 17-day dormancy period

### Phase 3 — The Theft (February 21, 2025)

On February 21, 2025, at approximately **14:13 UTC** [2]:

- Bybit's authorized signers initiated a routine transfer from their Ethereum cold wallet to a warm wallet
- The malicious JavaScript **altered the transaction payload** displayed to the signers while showing a normal-looking interface
- The signers connected their **Ledger hardware devices** and signed what appeared to be a legitimate transfer
- The actual transaction changed the operation type to `delegatecall`, handing control of the cold wallet smart contract to the attackers
- **Within two minutes** of the malicious transaction executing, the attackers uploaded clean JavaScript back to the S3 bucket, removing all traces

### Assets Stolen

| Asset | Amount | Approximate USD Value |
|-------|--------|-----------------------|
| ETH (Ether) | ~401,347 ETH | ~$1.12 billion |
| stETH (Lido Staked Ether) | ~90,376 stETH | ~$253 million |
| cmETH (Mantle Staked ETH) | ~15,000 cmETH | ~$44 million |
| mETH (Mantle ETH) | ~8,000 mETH | ~$23 million |
| **Total** | | **~$1.5 billion** |

## Attribution: Lazarus Group / TraderTraitor

The FBI issued **Public Service Announcement #250226** on February 26, 2025, officially attributing the attack to **North Korea**, using the designation **"TraderTraitor"** [3]:

- TraderTraitor is also known as Lazarus Group, APT38, BlueNoroff, and Stardust Chollima
- The group operates under North Korea's **Reconnaissance General Bureau (RGB)**, the country's primary intelligence agency
- Blockchain analytics firms **Elliptic**, **Chainalysis**, **TRM Labs**, and on-chain investigator **ZachXBT** independently confirmed the Lazarus Group attribution within hours of the incident
- Lazarus Group has stolen at least **$3.4 billion** in cryptocurrency since 2007, with **$1.34 billion** stolen in 2024 alone across 47 separate heists

## Money Laundering

The Lazarus Group employed a multi-layered laundering strategy with exceptional speed [4]:

**Stage 1 — Initial Dispersion (Hours 1–48):**
- Staked ETH derivatives were immediately swapped to native ETH via decentralized exchanges
- ETH was dispersed across dozens of intermediary wallets
- Approximately **$160 million** was laundered within the first 48 hours

**Stage 2 — Cross-Chain Conversion:**
- The primary laundering route converted ETH to BTC via **THORChain**, a decentralized cross-chain protocol — approximately **$1.2 billion** passed through THORChain
- By **March 20, 2025**, **86.29% of stolen ETH had been converted to BTC**
- Other platforms used included **eXch** (an anonymous swap service that refused to freeze stolen funds), Lombard, LiFi, Stargate, and SunSwap

**Stage 3 — Mixing and Obfuscation:**
- Converted BTC was dispersed across thousands of addresses
- Funds were processed through **Wasabi Wallet** and other Bitcoin mixers
- Eventually moved to OTC and P2P fiat exchange services

**Status as of April 21, 2025** (per Ben Zhou):
- **68.57%** of stolen funds remain **traceable**
- **27.59%** have **gone dark** (passed through mixers/P2P networks)
- **3.84%** have been **frozen** (~$54 million)

## Bybit's Response

### Immediate Crisis Management

Bybit CEO **Ben Zhou** went live on X (Twitter) within **30 minutes** of the hack being detected [5]:

- Zhou confirmed the breach and stated: "Even if this hack loss is not recovered, Bybit is solvent. All client assets are 1:1 backed"
- Bybit **did not halt withdrawals** — all withdrawal requests continued to be processed
- In the days following the hack, **over $5 billion in withdrawals** were processed (a "bank run" of approximately $4 billion plus the $1.5 billion stolen)

### Reserve Replenishment (72 Hours)

Bybit secured emergency funding to cover the ETH shortfall [6]:

- **Bridge loans** from undisclosed partners covered approximately 80% of the lost ETH within hours
- Key firms facilitating recovery included **Galaxy Digital**, **FalconX**, and **Wintermute** (OTC trading)
- **Mirana Ventures** deposited approximately **$600 million in ETH** to Bybit
- Within **72 hours** (by February 24, 2025), Bybit announced it had fully replenished reserves with approximately **447,000 ETH**
- A **Hacken** audit on February 26, 2025 verified that Bybit's reserve ratio exceeded 100% across all major assets

### LazarusBounty Program

On February 25, 2025, Ben Zhou declared **"war on Lazarus"** and launched the LazarusBounty program [7]:

- The bounty offered up to **10% of recovered funds** (potentially $140 million)
- **5%** to entities that successfully freeze stolen funds; **5%** to the first reporter providing verifiable evidence
- Approximately **$4.2 million** was awarded to bounty participants including Binance, ZachXBT, and the Mantle network

## Market Impact

The hack caused significant market disruption [8]:

- **ETH** dropped approximately 2–4% immediately (from ~$2,840 to ~$2,620), with a broader **~24% decline** over the following days
- **BTC** fell below **$90,000**, its lowest since November 2024
- Combined **1% market depth** for BTC, ETH, and top 50 altcoins **plunged 59%** between 1 PM and 10 PM UTC on February 21, from $68 million to $28 million

## Comparison to Major Crypto Hacks

| Rank | Incident | Date | Amount | Attribution |
|------|----------|------|--------|-------------|
| **1** | **Bybit** | **Feb 2025** | **~$1.5B** | **Lazarus Group** |
| 2 | Ronin Network / Axie Infinity | Mar 2022 | ~$625M | Lazarus Group |
| 3 | Poly Network | Aug 2021 | ~$611M | Unknown (returned) |
| 4 | Coincheck | Jan 2018 | ~$534M | Unknown |
| 5 | Mt. Gox | 2011–2014 | ~$473M | Unknown |

## Market Manipulation Implications

The Bybit hack reveals critical vulnerabilities in cryptocurrency exchange security:

1. **Supply chain as attack surface**: The attack targeted not Bybit's own infrastructure but a third-party dependency (Safe{Wallet}), demonstrating that exchanges are only as secure as their weakest vendor — a risk invisible to traditional exchange-level analysis
2. **Social engineering over technical exploits**: The entire $1.5 billion theft originated from a single developer downloading a malicious Docker project, highlighting that human factors remain the primary vulnerability in even the most technically sophisticated custody systems
3. **DeFi infrastructure as laundering channel**: The use of THORChain to launder $1.2 billion demonstrates that permissionless cross-chain protocols function as money laundering infrastructure when they lack compliance controls
4. **State-sponsored threats**: The Lazarus Group attribution — with the FBI confirming North Korea funds its weapons program through crypto theft — establishes that exchanges face nation-state adversaries whose capabilities and resources exceed those of conventional cybercriminals

## Relevance to Market Health Metrics

The Bybit hack demonstrates several indicators in the DN Institute [Market Health Metrics](https://dn.institute/research/market-health/docs/market-health-metrics/) framework:

- **Third-party dependency risk**: The Safe{Wallet} supply chain compromise demonstrates that exchange security assessments must extend to wallet providers, custody infrastructure, and software dependencies — not just the exchange's own systems
- **Proof of reserves as crisis metric**: Bybit's pre-existing PoR practice (since June 2024) enabled rapid verification of solvency post-hack, demonstrating the value of continuous reserve attestation as a market confidence mechanism
- **Market depth as vulnerability indicator**: The 59% collapse in market depth within hours shows that hack disclosures create acute liquidity crises whose severity can be measured through real-time depth monitoring
- **Cross-chain flow analysis**: The THORChain laundering pattern provides a template for detecting state-sponsored fund movements through permissionless bridge protocols

## References

1. Sygnia, "Sygnia's Investigation into the Bybit Hack: What We Know So Far," February 2025. [sygnia.co](https://www.sygnia.co/blog/sygnia-investigation-bybit-hack/)
2. NCC Group, "Bybit Hack: In-Depth Technical Analysis," February 2025. [nccgroup.com](https://www.nccgroup.com/research-blog/in-depth-technical-analysis-of-the-bybit-hack/)
3. FBI, "North Korea Responsible for $1.5 Billion Bybit Hack," February 2025. [fbi.gov](https://www.fbi.gov/investigate/cyber/alerts/2025/north-korea-responsible-for-1-5-billion-bybit-hack)
4. TRM Labs, "Bybit Hack Update: North Korea Moves to Next Stage of Laundering," 2025. [trmlabs.com](https://www.trmlabs.com/resources/blog/bybit-hack-update-north-korea-moves-to-next-stage-of-laundering)
5. CNBC, "Hackers steal $1.5 billion from exchange Bybit in biggest crypto heist ever," February 2025. [cnbc.com](https://www.cnbc.com/2025/02/21/hackers-steal-1point5-billion-from-exchange-bybit-biggest-crypto-heist.html)
6. CNBC, "Crypto exchange Bybit says it has fully replenished reserves after record-breaking $1.5 billion hack," February 2025. [cnbc.com](https://www.cnbc.com/2025/02/24/bybit-replenished-reserves-after-record-breaking-1point5-billion-hack.html)
7. CoinDesk, "Bybit Declares 'War on Lazarus' as It Crowdsources Effort to Freeze Stolen Funds," February 2025. [coindesk.com](https://www.coindesk.com/markets/2025/02/25/bybit-declares-war-on-lazarus-as-it-crowdsources-effort-to-freeze-stolen-funds)
8. Kaiko Research, "Bybit Hack by the Numbers," February 2025. [kaiko.com](https://research.kaiko.com/insights/bybit-hack-by-the-numbers)
