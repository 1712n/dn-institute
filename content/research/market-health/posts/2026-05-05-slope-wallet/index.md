---
title: "🌰 Slope Wallet — Private Key Logging Vulnerability and Solana Wallet Drain"
date: 2026-05-05
entities:
  - Slope Wallet
  - Solana
  - Phantom
  - Sentry
  - SOL
---

## Summary

1. **In early August 2022, approximately 9,231 Solana wallets were drained** of SOL, USDC, and other SPL tokens in an attack that initially appeared to affect the Solana blockchain itself. Investigation pointed to Slope Wallet, a third-party Solana mobile wallet, whose app had transmitted seed phrases or mnemonic material to a Sentry logging environment in plaintext.
2. **The root cause was an implementation error in Slope Wallet's mobile application**: the app included sensitive recovery material in telemetry sent to a Sentry-based application-monitoring system. This meant that wallets whose seed phrases had been created or imported in affected Slope flows could be exposed to anyone who obtained access to the relevant logs.
3. **The attack drained roughly $4-6 million** from affected wallets, primarily in SOL and USDC. While the dollar amount was modest compared to major DeFi exploits, the incident was significant because it affected thousands of individual non-custodial wallets — users who believed they were self-custodying their assets.
4. **Some Phantom Wallet users were also affected**, but the common link was prior use of the same recovery phrase with Slope Wallet. Phantom's own software was not identified as containing the logging vulnerability, but a seed phrase imported into both wallets could have been captured by Slope's telemetry.
5. **The incident demonstrated that non-custodial wallets are only as secure as their implementation**: the theoretical security guarantee of self-custody can be silently violated by wallet software that transmits recovery material to external or developer-controlled logging systems. Ordinary users had little practical visibility into whether this was happening.

## Background

### Solana Wallet Ecosystem (2022)

By mid-2022, the Solana ecosystem supported multiple wallet options:

- **Phantom**: The most popular Solana wallet, available as a browser extension and mobile app
- **Slope Wallet**: A mobile-first Solana wallet with a focus on user-friendly design
- **Solflare**: Another popular Solana wallet with browser and mobile versions
- **Hardware wallets**: Ledger and other hardware wallets supported Solana

Slope Wallet was a legitimate, publicly available wallet application on both iOS and Android app stores. It was not a scam or phishing application — it was a real wallet that happened to contain a severe implementation vulnerability.

### Sentry Error Monitoring

Sentry is a widely used application performance monitoring and error-tracking platform. Developers integrate Sentry into their applications to automatically capture and report errors, crashes, and performance issues. When an error occurs, the Sentry SDK collects contextual information (stack traces, variable states, user data) and transmits it to Sentry's servers for analysis.

The key issue: Sentry's data collection can inadvertently capture sensitive information if the application does not properly filter or redact sensitive variables before they are included in error reports.

### Key Parameters

| Parameter | Value |
|-----------|-------|
| Wallets drained | ~9,231 |
| Total loss | ~$4-6M reported |
| Primary assets stolen | SOL, USDC (SPL tokens) |
| Vulnerability | Seed phrases / mnemonic material logged to a Sentry environment in plaintext |
| Affected software | Slope Wallet mobile app |
| Secondarily affected | Phantom users who had imported seed into Slope |
| Detection | August 2-3, 2022 |

## Timeline of Events

| Date (August 2022) | Event |
|--------------------|-------|
| Aug 2 (evening) | Reports emerge on Twitter/Discord of Solana wallets being drained |
| Aug 2 (night) | Thousands of wallets affected; community initially suspects Solana protocol vulnerability |
| Aug 3 (early) | Solana Foundation, Phantom, and security researchers begin coordinated investigation |
| Aug 3 | Initial analysis rules out Solana protocol bug; focus shifts to wallet software |
| Aug 3 | Investigation identifies that affected wallets were overwhelmingly Slope Wallet users (or former users) |
| Aug 3 | Slope Wallet issues statement acknowledging the investigation |
| Aug 3-4 | Security researchers report that Slope's mobile app transmitted seed phrases to a Sentry logging environment |
| Aug 4 | Solana Foundation publishes preliminary findings pointing to Slope |
| Aug 4 | Slope confirms the vulnerability and advises users to create new wallets immediately |

### The Initial Panic

The first hours of the incident caused significant alarm in the Solana community because:
- Wallets were being drained without any user interaction (no transaction signing, no phishing)
- The affected wallets appeared to span multiple wallet providers (Phantom and Slope)
- The drain affected wallets that had not interacted with any suspicious dApps
- Some commentators speculated that a fundamental vulnerability in Solana's key derivation or transaction model had been discovered

This speculation was incorrect — the Solana protocol was not compromised. The confusion arose because Phantom users who had previously used Slope were also affected, making it appear that multiple wallet implementations were vulnerable.

## Technical Exploit Mechanics

### The Logging Vulnerability

Slope Wallet's mobile application integrated the Sentry SDK for error monitoring. The implementation error:

1. **Seed phrase in memory**: When a user created a wallet or imported a seed phrase, the seed phrase was held in the application's memory as part of normal wallet operation
2. **Sentry data capture**: The Sentry integration, when reporting errors or certain events, captured contextual data from the application's state — including, in Slope's implementation, sensitive recovery material
3. **Plaintext transmission**: The seed phrase or mnemonic material was transmitted to a Sentry logging environment as part of the telemetry payload, without application-level redaction
4. **Server-side storage**: The sensitive material was stored in Slope-controlled logs, accessible to anyone with access to that logging environment or credentials

The vulnerability was not in Sentry's core product itself — Sentry provides mechanisms for filtering sensitive data (data scrubbing, beforeSend hooks, deny lists). Slope's implementation failed to prevent seed phrases or mnemonic material from reaching the telemetry pipeline.

### From Logged Keys to Wallet Drain

The exact path from logged seed phrases to wallet drainage was:

1. **Attacker access**: Someone gained access to the seed phrases stored in Slope's Sentry project. Whether this was a Slope insider, an external attacker who compromised Sentry credentials, or another party has not been definitively established publicly.
2. **Key derivation**: From each seed phrase, the attacker derived the corresponding Solana private key(s) and wallet address(es)
3. **Balance check**: The attacker queried Solana RPC nodes to identify which addresses held assets worth draining
4. **Automated drain**: The attacker executed automated transactions from each compromised wallet, transferring SOL and SPL tokens to attacker-controlled addresses
5. **Scale**: Approximately 9,231 wallets were drained in a coordinated operation

### Why Phantom Users Were Affected

Phantom Wallet's own software did not contain the logging vulnerability. However:
- Some users had created their Solana wallet using Slope first, then later imported the same seed phrase into Phantom
- Some users had created a wallet in Phantom, then imported it into Slope for convenience
- In either case, the seed phrase had been entered into Slope at some point, triggering the Sentry logging

This meant the attack surface was not limited to current Slope users — anyone who had used Slope Wallet with a given seed phrase could have been affected, even if they had since switched entirely to Phantom.

## Impact Analysis

### Financial Losses

| Asset | Approximate Loss |
|-------|-----------------|
| SOL | Multi-million-dollar share of reported losses |
| USDC (SPL) | Material share of reported losses |
| Other SPL tokens | Smaller share of reported losses |
| **Total** | **~$4-6M reported** |

The relatively modest total loss likely reflected the demographic of Slope's user base — primarily retail users with smaller balances, rather than a large concentration of institutional wallets.

### Affected User Demographics

- **Individual retail users**: Affected wallets appear to have been heavily retail-oriented
- **Small balances**: Many drained wallets held relatively small amounts compared with institutional custody balances
- **Geographic distribution**: Global, reflecting Slope's availability on iOS and Android app stores worldwide
- **Non-technical users**: Mobile wallet users are typically less technically sophisticated than users of browser extension wallets or hardware wallets

### Psychological Impact

Beyond the financial losses, the incident had a significant psychological impact on the Solana ecosystem:
- **Erosion of self-custody trust**: Users who chose non-custodial wallets specifically for the security guarantee of self-custody discovered that their trust had been silently violated
- **Wallet switching**: Many users migrated to hardware wallets or re-evaluated their wallet choices
- **Community response**: The Solana community's rapid investigation and identification of the root cause was widely praised

## Vulnerability Pattern: Sensitive Data Leakage Through Telemetry

### How Telemetry Logging Creates Key Exposure

The Slope incident illustrates a class of vulnerability where legitimate monitoring tools inadvertently capture sensitive data:

1. **Telemetry SDKs are designed to capture context**: Error monitoring tools like Sentry capture broad contextual data to help developers diagnose issues. This data-hungry design is beneficial for debugging but dangerous when sensitive variables are in scope.

2. **Default capture is inclusive**: Unless explicitly configured to exclude certain data, telemetry SDKs may capture any variable in the application's state at the time of an event.

3. **Mobile app complexity**: Mobile wallet applications must manage the seed phrase during wallet creation, import, and signing operations. If the telemetry SDK is active during any of these operations, the seed phrase may be captured.

4. **Third-party server storage**: Telemetry data is stored on the monitoring provider's servers, introducing a new trust dependency. The user trusts the wallet developer, but may not be aware that their data is being sent to a third party.

### Comparison to Other Key Exposure Incidents

| Incident | Date | Exposure Vector | Impact |
|----------|------|----------------|--------|
| Slope Wallet | Aug 2022 | Seed phrases / mnemonic material logged to Sentry environment | ~$4-6M from ~9,231 wallets |
| Wintermute | Sep 2022 | Profanity vanity address generator (32-bit entropy) | ~$160M from 1 wallet |
| Atomic Wallet | Jun 2023 | Suspected key derivation or storage vulnerability | ~$100M from multiple wallets |
| Ledger Connect Kit | Dec 2023 | Supply chain attack injecting wallet-draining code | ~$600K from affected dApp users |
| Trust Wallet | Apr 2023 | Disclosed WASM vulnerability in key generation | Limited (patched before exploit) |

Each incident represents a different mechanism by which private keys can be compromised despite the user following standard security practices.

## Response and Remediation

### Slope Wallet Response

- Acknowledged the vulnerability and recommended users create new wallets with fresh seed phrases
- Stopped or changed the affected telemetry/logging path
- The wallet's future development and user base were severely impacted by the incident

### Solana Foundation Response

- Coordinated the multi-party investigation involving wallet providers and security researchers
- Published findings transparently, clarifying that the Solana protocol was not compromised
- Emphasized that affected users should immediately create new wallets and transfer remaining assets

### Community Investigation

The Solana community's investigation was notable for its speed and transparency:
- Multiple independent security researchers contributed to identifying the Slope/Sentry connection
- Analysis was published openly, allowing the community to verify findings
- The investigation process itself became a case study in collaborative incident response

## Lessons for Market Surveillance

1. **Telemetry-based key exposure as a vulnerability class**: Surveillance systems should recognize that wallet applications using third-party telemetry/monitoring services (Sentry, Datadog, New Relic, etc.) may inadvertently expose private keys. When a wallet application's data practices are audited, telemetry data flows should be explicitly reviewed.

2. **Multi-wallet drain pattern recognition**: Approximately 9,231 wallets drained in a coordinated operation creates a distinctive on-chain pattern — thousands of transfers from diverse source addresses to a smaller set of destination addresses within a short time window. Surveillance systems should alert on this pattern.

3. **Cross-wallet contamination**: The Phantom/Slope cross-contamination illustrates that a vulnerability in one wallet can affect users of other wallets if they share seed phrases. Risk assessment should consider whether a user has ever used a compromised wallet, not just whether they currently use it.

4. **Non-custodial wallet risk is not zero**: The self-custody model assumes that the wallet software faithfully generates, stores, and uses private keys without exposing them. Surveillance and risk assessment should incorporate wallet software implementation quality as a risk factor, not just the theoretical security model.

5. **App store presence does not guarantee security**: Slope was a legitimate app available on major app stores, passed standard app review processes, and was not flagged as malicious. Surveillance systems should not assume that app store listing implies adequate security for cryptocurrency management.

6. **Former user risk**: The fact that *former* Slope users were affected (people who had used Slope in the past and then switched to Phantom) creates a long-tail risk. When a wallet vulnerability is discovered, the risk population includes all *historical* users, not just current users. Surveillance should account for this temporal dimension.

## References

1. Solana Foundation. "8/3 Wallet Investigation Update." Solana Foundation Blog, August 3, 2022.
2. Phantom. "Phantom Wallet Statement on Solana Wallet Drain." Phantom Blog, August 2022.
3. Slope. "Slope Wallet Statement." Slope Finance, August 2022.
4. OtterSec. "Investigation into Solana Wallet Drain." OtterSec / Twitter, August 3, 2022.
5. CoinDesk. "Solana Wallet Drain Traced to Slope Wallet's Sentry Logging." CoinDesk, August 2022.
6. Rekt News. "Slope — REKT." rekt.news, August 2022.
