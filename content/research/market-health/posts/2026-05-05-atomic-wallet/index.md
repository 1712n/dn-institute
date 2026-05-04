---
date: 2026-05-05
entities:
  - id: atomic-wallet
    name: Atomic Wallet
    type: exchange
  - id: elliptic
    name: Elliptic
    type: analytics
  - id: lazarus-group
    name: Lazarus Group
    type: threat-actor
  - id: fbi
    name: Federal Bureau of Investigation
    type: regulatory
  - id: ofac
    name: Office of Foreign Assets Control
    type: regulatory
title: "Atomic Wallet supply-chain compromise and $100 M+ multi-chain private-key drain"
---

## 1. Introduction and incident overview

On 2 June 2023, users of the non-custodial desktop and mobile wallet application Atomic Wallet began reporting unauthorized outflows of cryptocurrency from their wallets. Over the following 72 hours, blockchain analysts established that at least 5,500 individual wallet addresses across multiple chains — including Bitcoin, Ethereum, Tron, BSC, Ripple, Dogecoin, Litecoin, and Stellar — had been compromised. The aggregate loss, initially estimated at $35 million, was revised upward by independent on-chain investigators to exceed $100 million within two weeks as additional victim wallets surfaced.

Atomic Wallet is an Estonia-registered, non-custodial cryptocurrency wallet that supports over 500 assets. Its core value proposition is that private keys are encrypted and stored locally on the user's device, never transmitted to Atomic Wallet servers. This architecture normally places the custody responsibility — and the security perimeter — entirely on the end user's device. The June 2023 incident challenged that assumption: the sheer scale of affected wallets, spanning multiple blockchains and device types simultaneously, pointed to a systemic compromise rather than a series of individual phishing or malware attacks.

## 2. Technical background

### 2.1 Atomic Wallet's key-management architecture

Atomic Wallet generates a 12-word BIP-39 mnemonic during onboarding. From this seed, the application derives chain-specific private keys using standard hierarchical deterministic (HD) wallet derivation paths (BIP-44). The seed and derived keys are encrypted with the user's locally chosen password using AES-256 encryption and stored in application data files on the device. The wallet's exchange features are powered by backend swap-aggregation services, and the application periodically communicates with Atomic Wallet's infrastructure for price feeds, transaction broadcasting, and in-app swap coordination.

### 2.2 Pre-existing security concerns

Security researchers had flagged potential vulnerabilities in Atomic Wallet before the June 2023 incident. In February 2022, the auditing firm Least Authority published a report identifying several issues in Atomic Wallet's codebase, including: inadequate encryption of private keys in local storage, the use of an outdated and potentially vulnerable version of Electron (the cross-platform desktop framework), insufficient cryptographic randomness in certain key-derivation paths, and the lack of proper code-signing mechanisms for updates. Least Authority concluded that the design "does not sufficiently protect user private keys and sensitive data" and recommended remediation steps. Atomic Wallet acknowledged the audit but provided limited public evidence that all findings were addressed prior to the June 2023 attack.

### 2.3 Attack surface considerations

Several vectors could explain a compromise of locally encrypted seed phrases at scale:

1. **Supply-chain injection**: A malicious dependency or compromised build pipeline could embed key-exfiltration logic into the wallet application binary distributed to users. Because Atomic Wallet is built on Electron and bundles hundreds of npm dependencies, its supply chain surface is broad.

2. **Server-side interception**: If the application transmits encrypted seed material (or material sufficient to reconstruct seeds) to Atomic Wallet infrastructure — during backups, telemetry, or swap coordination — a compromise of that infrastructure could yield seeds in bulk.

3. **Insufficient local encryption**: If the AES-256 encryption of local seed storage used a weak key-derivation function, short salt, or predictable initialization vector, an attacker who obtained the encrypted files (via malware, cloud sync, or another vulnerability) could brute-force passwords at scale.

4. **CDN or update-channel poisoning**: If the application's auto-update mechanism did not verify cryptographic signatures on binaries, an attacker who compromised the update CDN could distribute a trojanized version to all users.

## 3. Attack execution and on-chain forensics

### 3.1 Timeline of the drain

The earliest confirmed unauthorized transactions appeared on-chain on 2 June 2023, starting around 21:45 UTC. The drain proceeded in waves:

- **Wave 1 (2 June 21:45–3 June 06:00 UTC)**: High-value wallets targeted first. Ethereum, Bitcoin, and Tron wallets with balances exceeding $100,000 were drained systematically. Transactions were broadcast in rapid succession, suggesting automated tooling.

- **Wave 2 (3–4 June)**: Medium-value wallets across BSC, Ripple, Dogecoin, and Litecoin were emptied. The attacker appeared to work through chains sequentially, suggesting a batched key-derivation and sweep process.

- **Wave 3 (5–10 June)**: Residual low-value wallets and wallets on less common chains (Stellar, Cosmos, Algorand) were swept. Some victims reported funds disappearing days after the initial wave, indicating the attacker held derived keys and swept wallets opportunistically as balances appeared.

### 3.2 Laundering methodology

On-chain analysis, particularly by Elliptic and the pseudonymous researcher ZachXBT, mapped the laundering pipeline:

1. **Initial consolidation**: Stolen ERC-20 tokens were swapped to ETH via decentralized exchanges (Uniswap, 1inch) within minutes of the theft. BTC and other UTXO-chain funds were consolidated into intermediate wallets.

2. **OFAC-sanctioned mixer usage**: Ethereum-denominated funds were routed through the Sinbad.io mixer, a service the U.S. Treasury's Office of Foreign Assets Control (OFAC) later sanctioned in November 2023. Bitcoin funds passed through a combination of peel chains and the Sinbad mixer.

3. **Cross-chain bridging**: Portions of the stolen funds were bridged across chains to complicate tracing. THORChain and other cross-chain protocols were used to convert between asset types.

4. **Exchange deposit**: Final-stage funds were deposited into centralized exchanges — some of which froze portions upon notification by Atomic Wallet's incident-response partners and law enforcement.

### 3.3 Attribution to the Lazarus Group

Multiple independent analysts, including Elliptic, attributed the Atomic Wallet attack to North Korea's Lazarus Group with high confidence. The attribution rested on several converging indicators:

- **Laundering pattern overlap**: The mixer usage, peel-chain structure, and timing of consolidation transactions matched Lazarus Group's established playbook from the Harmony Horizon Bridge ($100M, June 2022) and Ronin Bridge ($625M, March 2022) hacks.

- **Sinbad.io association**: Elliptic's analysis showed that the stolen Atomic Wallet funds were laundered through the same Sinbad.io mixer addresses used to process proceeds from confirmed Lazarus Group operations, including the Harmony and Ronin thefts.

- **FBI confirmation**: In a January 2024 statement, the FBI confirmed that the Lazarus Group was responsible for the Atomic Wallet compromise, as part of a broader advisory on DPRK cyber theft targeting cryptocurrency infrastructure.

- **Operational consistency**: The multi-chain, multi-asset targeting pattern — draining all supported chains from a single seed compromise rather than targeting one chain — is characteristic of Lazarus Group operations that aim to maximize extraction per compromised target.

## 4. Atomic Wallet's response and transparency failures

### 4.1 Initial disclosure

Atomic Wallet's initial response drew criticism for both its pace and content. The company's first public acknowledgment came via a tweet on 3 June 2023, over 24 hours after the first unauthorized outflows, stating: "We have received reports of wallets being compromised. We are doing all we can to investigate and analyze the situation. As we have more information, we will share it accordingly."

### 4.2 Scope minimization

In subsequent communications, Atomic Wallet stated that "less than 1% of monthly active users" were affected. While this figure may have been numerically accurate relative to the total user base (reported at over 5 million downloads), critics noted that it obscured the severity of the financial impact: the affected 1% collectively lost over $100 million. The framing was perceived as an attempt to minimize the incident's significance.

### 4.3 Root-cause opacity

Atomic Wallet never published a detailed post-mortem or root-cause analysis. The company retained the blockchain analytics firm Chainalysis to assist with tracing stolen funds but did not publicly disclose which vulnerability was exploited, whether it had been patched, or what architectural changes were made to prevent recurrence. In a June 2023 blog post, the company listed four possible causes under investigation — network vulnerabilities, malware on user devices, man-in-the-middle attacks, and code injection — but did not narrow these down publicly.

This opacity left users unable to assess whether the wallet was safe to continue using. Security researchers noted that without a confirmed root cause, there was no basis to believe the vulnerability had been remediated.

### 4.4 No compensation program

Unlike some projects that have established recovery funds or user-compensation mechanisms after security incidents, Atomic Wallet did not announce any compensation or restitution program for affected users. The company stated that it was working with law enforcement and blockchain analytics firms to trace and recover funds, but no recovered funds were reported distributed to victims as of early 2026.

## 5. Legal proceedings

### 5.1 Class-action litigation

In August 2023, a class-action lawsuit was filed against Atomic Wallet in the U.S. District Court for the District of Colorado by affected users. The complaint alleged negligence, breach of implied warranty, and violations of consumer protection statutes. Key claims included:

- Atomic Wallet failed to address known vulnerabilities identified in the Least Authority audit.
- The company's marketing representations about security ("bank-level encryption," "your keys, your crypto") constituted misleading statements given the known and unaddressed vulnerabilities.
- The lack of a post-incident root-cause disclosure prevented users from mitigating ongoing risk.

Atomic Wallet moved to dismiss on jurisdictional grounds, arguing that as an Estonian entity with no U.S. office, the court lacked personal jurisdiction. The jurisdictional question highlighted a broader challenge in cryptocurrency security litigation: non-custodial wallet providers often operate across multiple jurisdictions with minimal physical presence in any single one, complicating users' ability to seek legal recourse.

## 6. Broader market-health implications

### 6.1 Non-custodial wallet trust model

The Atomic Wallet incident exposed a gap in the non-custodial wallet trust model. The theoretical security guarantee of non-custodial wallets — "not your keys, not your coins; your keys, your coins" — assumes that the wallet software faithfully generates, encrypts, and isolates private keys without leaking them. When the wallet software itself becomes the attack vector, the non-custodial model offers no recourse mechanism comparable to the insurance, reserves, or regulatory protections that (in theory) backstop custodial services.

This does not argue for custodial solutions, which carry their own well-documented risks (exchange hacks, insolvency, fraud). Rather, it highlights that non-custodial security is only as strong as the software supply chain, update mechanisms, and local encryption implementations — all of which are under the control of the wallet developer, not the user.

### 6.2 Supply-chain risk in cryptocurrency software

Atomic Wallet's Electron-based architecture, with its large dependency tree, illustrates the supply-chain risk inherent in modern cryptocurrency wallet software. A single compromised npm package, a poisoned CI/CD pipeline, or a malicious pull request in an upstream dependency could inject key-exfiltration logic that persists through multiple wallet versions before detection. This risk is not unique to Atomic Wallet; it applies to any wallet built on JavaScript/TypeScript frameworks with extensive third-party dependencies.

The incident accelerated industry discussion about:

- **Reproducible builds**: Allowing users and auditors to verify that distributed binaries correspond to the published source code.
- **Dependency minimization**: Reducing the npm dependency tree to shrink the supply-chain attack surface.
- **Hardware wallet integration**: Encouraging users to use hardware wallets for high-value storage, keeping signing keys on dedicated secure elements rather than in software wallets.
- **Transparency reports**: Publishing regular security audits and incident-response procedures before incidents occur, not after.

### 6.3 DPRK cyber theft as a systemic market risk

The Lazarus Group's involvement in the Atomic Wallet hack — alongside the Ronin Bridge, Harmony Horizon, and numerous other cryptocurrency thefts — positions DPRK-sponsored cyber operations as a systemic risk to the cryptocurrency market. The UN Panel of Experts estimated that DPRK-linked groups stole approximately $1.7 billion in cryptocurrency in 2022 alone. The Atomic Wallet attack added to this total in 2023.

For market health, the implications are:

- **Liquidity and price impact**: Large-scale thefts followed by mixer laundering inject sell pressure into markets when the attacker converts stolen assets to fiat-usable forms, typically through OTC desks or exchanges with weak KYC. This can depress prices of the specific tokens stolen.

- **Regulatory response**: Each major hack attributed to DPRK actors strengthens the case for stricter regulation of cryptocurrency infrastructure, including potential requirements for wallet-provider licensing, mandatory security audits, and incident-reporting obligations.

- **Sanctions compliance burden**: OFAC's November 2023 sanctioning of Sinbad.io (the mixer used to launder Atomic Wallet proceeds) created compliance obligations for all U.S.-nexus entities interacting with addresses associated with Sinbad. This pattern — hack, launder, sanction — increases the operational cost and legal risk for legitimate DeFi protocols and exchanges that inadvertently process tainted funds.

## 7. Lessons learned and structural recommendations

### 7.1 For wallet developers

1. **Address audit findings promptly and publicly**: The Least Authority audit identified issues over a year before the attack. Publicly tracking remediation of audit findings builds user trust and reduces exposure.

2. **Minimize the dependency supply chain**: Audit and pin all third-party dependencies. Use tools like `npm audit`, Snyk, or Socket to detect malicious or vulnerable packages. Consider alternative frameworks with smaller dependency surfaces for security-critical applications.

3. **Implement reproducible builds**: Enable independent verification that distributed binaries correspond to audited source code. This allows the community to detect supply-chain injections.

4. **Enforce code-signed auto-updates**: Ensure that the update mechanism cryptographically verifies binaries against a public key controlled by the development team, preventing CDN poisoning attacks.

5. **Publish incident-response post-mortems**: Full root-cause disclosure, even if it reveals embarrassing vulnerabilities, is essential for maintaining user trust and enabling the ecosystem to learn from incidents.

### 7.2 For users

1. **Use hardware wallets for significant holdings**: Software wallets, regardless of their non-custodial design, are only as secure as the device and software stack they run on. Hardware wallets isolate signing keys on dedicated secure elements.

2. **Diversify wallet providers**: Avoid storing all assets in a single wallet application. Spreading holdings across multiple wallets with different codebases limits exposure to any single supply-chain compromise.

3. **Monitor audit reports**: Before trusting a wallet with significant funds, check whether independent security audits have been conducted and whether identified issues were addressed.

### 7.3 For regulators and industry bodies

1. **Mandate security disclosures**: Require wallet providers above a certain user threshold to publish annual security audits and incident-response plans.

2. **Establish vulnerability-coordination mechanisms**: Create industry-wide frameworks for responsible disclosure and coordinated response to wallet vulnerabilities, analogous to CERT/CC in traditional software.

3. **Strengthen sanctions enforcement**: Continue targeting mixer and laundering infrastructure used by state-sponsored actors, while providing clear compliance guidance for legitimate DeFi protocols.

## 8. Conclusion

The Atomic Wallet incident of June 2023 demonstrated that non-custodial wallet security is contingent on the integrity of the entire software supply chain, not merely on the cryptographic design of key storage. The attack, attributed to North Korea's Lazarus Group, compromised at least 5,500 wallets across multiple blockchains, resulting in losses exceeding $100 million. Atomic Wallet's response was marked by delayed disclosure, scope minimization, and a persistent refusal to publish a root-cause analysis — leaving users and the broader ecosystem unable to determine whether the vulnerability was remediated.

The incident underscores the structural risk that software supply-chain attacks pose to cryptocurrency infrastructure and highlights the growing role of state-sponsored threat actors as a systemic concern for market health. For the ecosystem to mature, wallet developers must adopt reproducible builds, minimize dependencies, promptly address audit findings, and commit to transparency when incidents occur. Users, in turn, must treat software wallets as convenience tools rather than secure vaults, and allocate significant holdings to hardware wallets with isolated signing environments.
