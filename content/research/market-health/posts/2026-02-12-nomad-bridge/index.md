---
title: "Nomad Bridge: $190M 'Crowd-Looting' Exploit via Zero-Validation Initialization Bug, 300+ Copycat Addresses, and FTC Enforcement Action"
date: 2026-02-12
entities:
  - Nomad Bridge
  - Illusory Systems
  - Moonbeam
  - Evmos
---

## Summary

1. **$190 million drained in history's first "crowd-looting" DeFi exploit**: On August 1, 2022, a routine smart contract upgrade to the Nomad cross-chain bridge set the trusted message root to `0x00`, which — because all uninitialized Solidity mapping entries default to zero — caused every fraudulent message to be automatically validated, allowing anyone to drain funds by simply copying a successful exploit transaction and replacing the recipient address.
2. **300+ addresses participated — zero technical knowledge required**: Unlike typical DeFi exploits executed by a single attacker, the Nomad hack became a mass free-for-all where over 300 unique addresses drained funds through 960 transactions — 88% of exploiting addresses were copycats who simply found a working transaction on Etherscan, replaced the recipient address with their own, and rebroadcast it.
3. **41 addresses took 80% of stolen funds**: While hundreds of addresses participated, just 41 addresses extracted $152 million (80% of total), with the largest single exploiter draining approximately $47 million — demonstrating extreme concentration even in a "crowd-looting" event.
4. **Moonbeam and Evmos ecosystems devastated**: As the primary bridge for both chains, the hack caused Moonbeam's TVL to drop from $322 million to $88 million (72% decline) and Evmos TVL to fall 76.7%, while all Nomad-minted wrapped tokens (madUSDC, madUSDT, madWBTC) became effectively unbacked.
5. **FTC enforcement action and criminal arrest**: The Federal Trade Commission proposed a $37.5 million settlement against Nomad's operator Illusory Systems for misleading users about security, while alleged exploiter Alexander Gurevich was arrested at Ben-Gurion Airport in May 2025 after attempting to flee to Russia under a legally changed name.

## Background

### Nomad Bridge Overview

**Nomad** was a cross-chain messaging and token bridge connecting **Ethereum, Moonbeam, Avalanche, Evmos, and Milkomeda C1**. It was operated by **Illusory Systems, Inc.**, led by CEO **Pranay Mohan**. The bridge used an optimistic verification model inspired by optimistic rollups — messages were assumed valid unless challenged within a fraud-proof window [1].

Before the exploit, Nomad held approximately **$190.74 million in TVL** across its bridge contracts.

### The Initialization Bug

The vulnerability was introduced during a **routine smart contract upgrade on June 21, 2022**, to the **Replica** proxy contract (address: `0xB92336759618F55bd0F8313bd843604592E27bd8` on Ethereum). The Replica contract validates cross-chain messages on the destination chain [2].

**How the bug was introduced:**

1. During the upgrade, the `_committedRoot` initialization parameter was set to `0x00` (zero bytes32)
2. This value was stored in the `confirmAt` mapping, marking `0x00` as a trusted/confirmed root with a timestamp value of `1`
3. In the EVM, all storage slots are initialized to zero by default — any key not present in a Solidity mapping returns `0x00`
4. The `process()` function validated messages by checking if the associated root was acceptable via the `acceptableRoot()` function
5. When a message hash was **not present** in the `messages` mapping, the lookup returned `0x00`
6. Since `0x00` had been set as a trusted root, `acceptableRoot()` returned `true` for **every unproven message**

**Result**: Every message was automatically treated as proven and valid, regardless of whether it had been legitimately relayed through Nomad's off-chain agents.

**Initialization transaction**: `0x53fd92771d2084a9bf39a6477015ef53b7f116c79d98a21be723d06d79024cad`

As **samczsun** (Head of Security at Paradigm) summarized: *"A routine upgrade marked the zero hash as a valid root, which had the effect of allowing messages to be spoofed on Nomad. Attackers abused this to copy/paste transactions and quickly drained the bridge in a frenzied free-for-all."* [3]

## The Exploit (August 1–2, 2022)

### The "Crowd-Looting" Pattern

Beginning at approximately **21:32 UTC on August 1, 2022**, the first exploit transaction drained **100 WBTC** (~$2.3 million). What happened next was unprecedented in DeFi history [4]:

- The exploit required **zero technical knowledge** of Solidity or Merkle trees
- Anyone could find a successful exploit transaction on Etherscan, **replace the recipient address with their own**, and rebroadcast it
- The drain involved **960 transactions** containing **1,175 individual withdrawals**
- By **05:49 UTC on August 2**, the bridge balance had been reduced from $190.74 million to **$1,794**

### Participation Statistics

| Metric | Value |
|--------|-------|
| Total unique addresses | 300+ |
| Copycat addresses (per Coinbase analysis) | 88% of exploiting addresses |
| Copycats' collective theft | ~$88 million |
| Addresses taking 80% of funds | 41 |
| Amount taken by top 41 addresses | $152 million |

### Top Exploiter Addresses

| Address | Amount |
|---------|--------|
| `0x56D8B635A7C88Fd1104D23d632AF40c1C3Aac4e3` | ~$47M |
| `0xBF293D5138a2a1BA407B43672643434C43827179` | ~$40M |
| `0xB5C55f76f90Cc528B2609109Ca14d8d84593590E` | ~$8M |

First exploit transaction: `0xa5fe9d044e4f3e5aa5bc4c0709333cd2190cba0f4e7f16bcf73f49f83e4a5460` [5]

### Stolen Assets Breakdown

| Token | Amount |
|-------|--------|
| USDC | ~87,459,362 |
| WETH | ~22,876 |
| WBTC | ~1,028 |
| USDT | ~8,625,217 |
| DAI | ~4,533,633 |
| CQT | ~113,403,733 |
| FXS | ~119,088 |
| Additional | FRAX, HBOT, IAG, GERO, CARDS, SDL, C3 |

## Impact on Dependent Ecosystems

Nomad served as the **primary bridge** for Moonbeam and Evmos ecosystems. The hack caused catastrophic downstream effects [6]:

| Chain/Project | TVL Impact |
|---------------|------------|
| **Moonbeam** | TVL dropped from $322M to ~$88M (72% decline); GLMR token fell from $0.84 to $0.64 (23% drop) |
| **Evmos** | TVL dropped 76.7% to ~$5M |
| **Milkomeda** | TVL dropped 45.45% to ~$12.4M |

**Wrapped token crisis**: All Nomad-minted wrapped tokens (madUSDC, madUSDT, madWBTC, madWETH) on Moonbeam, Milkomeda, and Evmos became **effectively unbacked** — the underlying assets on Ethereum had been stolen. These tokens lost their peg, causing cascading losses across lending and DEX protocols on those chains.

## Fund Tracing and Laundering

### Mandiant/Google Cloud Analysis

Mandiant partnered with **CT6** using their **CryptoVoyant** blockchain investigative software and identified four distinct clusters among addresses that stole over $2 million [7]:

- **Group A (White Hat)**: Three addresses that returned some funds (one returned 77.6%, others returned just 1.7% and 3.4%)
- **Group C (Black Hat)**: Stole ~$5.2M, routed through Uniswap swaps, then Tornado Cash
- **Group D (Largest Actor)**: Stole ~$54.5M, used OrionPool, Uniswap, and Curve for token swaps before further laundering

### TRM Labs Investigation

**TRM Labs** partnered directly with Nomad and traced approximately **$88 million** to wallets engaging in active laundering, including movement through Tornado Cash, conversion to privacy coins (Monero, Dash), non-custodial exchanges, and OTC brokers [8].

## Recovery Efforts

On **August 3, 2022**, Nomad announced a **10% bounty**: exploiters could keep 10% and face no legal action if they returned 90%+ of stolen funds. A recovery wallet was established for whitehat returns [9].

- **~$36–37 million** was returned (approximately 19–20% of total stolen)
- Returns were primarily stablecoins: $3.78M USDC, $2M USDT, $1.38M CQT, $1.2M FRAX
- Whitehats who returned 90%+ received a **Whitehat NFT** from Metagame and 100 FF tokens from Forefront

## Audit History

| Auditor | Period | Key Finding |
|---------|--------|-------------|
| **Quantstamp** | May–June 2022 (final report June 9, 2022) | 40 issues identified; QSP-19 specifically foreshadowed a similar vulnerability; auditor noted "the Nomad team has misunderstood the issue" |

**Critical audit gap ("Audit Drift")**: The buggy code responsible for the hack was introduced on **June 21, 2022** — 12 days **after** the Quantstamp audit was finalized. The deployed code differed from the audited code, a phenomenon security firm Zellic termed **"audit drift"** [10].

## Legal and Regulatory Response

### Criminal Case: Alexander Gurevich

| Detail | Information |
|--------|-------------|
| Suspect | Alexander Gurevich, Russian-Israeli dual national |
| Alleged theft | ~$2.89 million in tokens |
| Indictment | 8-count federal indictment (August 16, 2023), US District Court, Northern District of California |
| Charges | Wire fraud, money laundering, transportation of stolen property (up to 20 years) |
| Investigation | FBI San Francisco field office |
| Name change | Legally changed name to "Alexander Block" in Israeli Population Registry (April 29, 2025) |
| Arrest | May 1, 2025, at Ben-Gurion Airport while attempting to fly to Russia; coordinated by DOJ, FBI, and Interpol |
| Extradition | US formal request submitted December 2024; Israeli authorities approved [11] |

### Civil Lawsuit: Singh v. Illusory Systems

A class action (*Singh v. Illusory Systems, Inc.*, Case No. 1:23-cv-00183, D. Delaware) was filed by Manu Singh (Canadian citizen, lost ~$172,000) and Iagon AS (blockchain company, lost ~$4.2 million) alleging RICO violations. The **RICO claims were dismissed on March 29, 2024** — the court found "a series of intervening, non-racketeering acts" broke the causal chain [12].

### FTC Enforcement Action (December 2025)

The **Federal Trade Commission** alleged Nomad/Illusory Systems misled users about security and pushed an update containing "inadequately tested code." The proposed settlement requires [13]:

- Repayment of **~$37.5 million** to affected users
- Implementation of a comprehensive security program
- Assignment of a dedicated security employee
- Regular third-party security assessments
- Prohibition on further misrepresentations about product security

## Timeline

| Date | Event |
|------|-------|
| April 21, 2022 | Nomad deploys Replica proxy contract |
| June 9, 2022 | Quantstamp audit final report delivered |
| June 21, 2022 | Routine upgrade introduces 0x00 trusted root bug |
| August 1, 2022 ~21:32 UTC | First exploit transaction: 100 WBTC (~$2.3M) drained |
| August 1, 2022 ~23:25 GMT | Nomad acknowledges the hack on Twitter |
| August 2, 2022 ~05:49 UTC | Bridge balance reduced from $190.74M to $1,794 |
| August 3, 2022 | Nomad announces 10% whitehat bounty |
| By August 9, 2022 | ~$36–37M returned (17–20% of stolen) |
| August 16, 2023 | 8-count federal indictment against Alexander Gurevich |
| March 29, 2024 | RICO class action dismissed |
| May 1, 2025 | Gurevich arrested at Ben-Gurion Airport |
| December 2025 | FTC proposes $37.5M settlement against Illusory Systems |

## Market Manipulation Implications

The Nomad Bridge exploit reveals critical vulnerabilities in cross-chain bridge security and DeFi infrastructure:

1. **Initialization parameter as critical attack vector**: A single misconfigured initialization value (`0x00` as trusted root) in a routine upgrade destroyed $190 million in bridge security — demonstrating that proxy contract upgrade procedures represent one of the highest-risk operations in DeFi and that initialization parameter verification should be a mandatory pre-deployment check
2. **"Crowd-looting" as novel attack pattern**: The zero-knowledge exploit barrier transformed a sophisticated bridge hack into a mass looting event with 300+ participants — creating a new category of DeFi exploit where the attack transaction itself becomes a template that anyone can copy, fundamentally changing the speed and scale of fund extraction
3. **Bridge dependency as ecosystem single point of failure**: Nomad's role as the primary bridge for Moonbeam and Evmos meant that a single bridge failure caused 72% and 76.7% TVL collapses respectively — demonstrating that bridge dependency concentration represents measurable systemic risk for entire blockchain ecosystems
4. **Audit drift as systemic vulnerability**: The 12-day gap between audit completion and the introduction of vulnerable code demonstrates that point-in-time audits provide a false sense of security when code continues to change after audit — continuous audit coverage or mandatory re-audit requirements for post-audit code changes would address this gap

## Relevance to Market Health Metrics

Nomad Bridge's case demonstrates several indicators in the DN Institute [Market Health Metrics](https://dn.institute/research/market-health/docs/market-health-metrics/) framework:

- **Bridge TVL concentration as ecosystem risk metric**: The direct correlation between Nomad's bridge failure and Moonbeam/Evmos TVL collapse (72% and 76.7% respectively) demonstrates that the ratio of bridge-dependent TVL to total ecosystem TVL provides a measurable indicator of systemic fragility — ecosystems with high bridge concentration face elevated exploit-cascade risk
- **Upgrade-to-exploit time window**: The 41-day gap between the June 21 upgrade and August 1 exploit — during which the vulnerability sat in production undetected — represents a measurable metric for upgrade security monitoring, where longer windows of undetected vulnerabilities indicate weaker continuous security practices
- **Exploit participation dispersion**: The "crowd-looting" pattern with 300+ addresses provides a novel metric — the number of unique exploiting addresses per incident indicates the replicability of the exploit, which correlates with the speed and completeness of fund extraction
- **Regulatory response as market signal**: The FTC's $37.5M enforcement action — the first time the FTC targeted a DeFi bridge operator — establishes a regulatory precedent that bridge security failures may trigger government enforcement, representing a new category of regulatory risk for bridge-dependent protocols

## References

1. Nomad, "Root Cause Analysis." [medium.com](https://medium.com/nomad-xyz-blog/nomad-bridge-hack-root-cause-analysis-875ad2e5aacd)
2. Immunefi, "Hack Analysis: Nomad Bridge, August 2022." [medium.com](https://medium.com/immunefi/hack-analysis-nomad-bridge-august-2022-5aa63d53814a)
3. Halborn, "Explained: The Nomad Hack (August 2022)." [halborn.com](https://www.halborn.com/blog/post/explained-the-nomad-hack-august-2022)
4. The Block, "Nomad's $190 million bridge exploit drew hacking feeding frenzy of 300 addresses." [theblock.co](https://www.theblock.co/post/160851/nomads-190-million-bridge-exploit-drew-hacking-feeding-frenzy-of-300-addresses)
5. Coinbase, "Nomad Bridge Incident Analysis." [coinbase.com](https://www.coinbase.com/blog/nomad-bridge-incident-analysis)
6. Rekt News, "Nomad Bridge REKT." [rekt.news](https://rekt.news/nomad-rekt)
7. Mandiant/Google Cloud, "Dissecting the Nomad Bridge Hack and Following the Money." [cloud.google.com](https://cloud.google.com/blog/topics/threat-intelligence/dissecting-nomad-bridge-hack)
8. TRM Labs, "Key Suspect in $190M Nomad Bridge Exploit Extradited to the United States." [trmlabs.com](https://www.trmlabs.com/resources/blog/key-suspect-in-190m-nomad-bridge-exploit-extradited-to-the-united-states)
9. CNBC, "Hacked crypto startup Nomad offers a 10% bounty," August 2022. [cnbc.com](https://www.cnbc.com/2022/08/05/crypto-startup-nomad-offers-10percent-bounty-after-190-million-hack.html)
10. Zellic, "Audit Drift: You Could Have Found the Nomad Hack." [zellic.io](https://www.zellic.io/blog/audit-drift/)
11. Decrypt, "FTC Compels Nomad Operator to Repay Users After $186M Crypto Bridge Hack." [decrypt.co](https://decrypt.co/352621/ftc-nomad-operator-repay-users-186m-crypto-bridge-hack-2022)
12. Baker McKenzie, "U.S. Court Dismisses RICO Lawsuit in Connection with Nomad Bridge Hack," April 2024. [bakermckenzie.com](https://blockchain.bakermckenzie.com/2024/04/08/u-s-court-dismisses-rico-lawsuit-brought-in-connection-with-nomad-bridge-hack/)
13. National Law Review, "FTC Action Targets Crypto Bridge Security Failures." [natlawreview.com](https://natlawreview.com/article/privacy-tip-472-ftc-issues-proposed-order-against-illusory-systems-over-allegations)
