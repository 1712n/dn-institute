---
date: 2026-05-05
entities:
  - id: atomic-wallet
    name: Atomic Wallet
    type: wallet
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
title: "Atomic Wallet suspected software compromise and $100M+ multi-chain wallet drain"
---

## 1. Introduction and incident overview

On 2 June 2023, users of the non-custodial desktop and mobile wallet application Atomic Wallet began reporting unauthorized outflows of cryptocurrency from their wallets. Over the following days and weeks, blockchain analysts identified more than 5,000 affected wallet addresses across multiple chains — including Bitcoin, Ethereum, Tron, BSC, XRP Ledger, Dogecoin, Litecoin, and Stellar. The aggregate loss, initially estimated around $35 million, was later reported by independent on-chain investigators and the FBI as exceeding $100 million as additional victim wallets surfaced.

Atomic Wallet is an Estonia-registered, non-custodial cryptocurrency wallet that supports hundreds of assets. Its core value proposition is that private keys are encrypted and stored locally on the user's device rather than held by Atomic Wallet as a custodian. This architecture normally places the custody responsibility — and much of the security perimeter — on the end user's device. The June 2023 incident challenged that assumption: the scale of affected wallets across multiple blockchains pointed to a systemic wallet-software, key-management, infrastructure, or user-environment compromise rather than a clearly isolated single-chain protocol issue.

## 2. Technical background

### 2.1 Atomic Wallet's key-management architecture

Atomic Wallet generates a 12-word BIP-39 mnemonic during onboarding. From this seed, the application derives chain-specific private keys using standard hierarchical deterministic (HD) wallet derivation paths (BIP-44). The seed and derived keys are encrypted with the user's locally chosen password using AES-256 encryption and stored in application data files on the device. The wallet's exchange features are powered by backend swap-aggregation services, and the application periodically communicates with Atomic Wallet's infrastructure for price feeds, transaction broadcasting, and in-app swap coordination.

### 2.2 Pre-existing security concerns

Security researchers had flagged potential vulnerabilities in Atomic Wallet before the June 2023 incident. In February 2022, the auditing firm Least Authority published a report identifying multiple issues in Atomic Wallet's design and implementation and warning that the wallet did not sufficiently demonstrate protection for user private keys and sensitive data. Public reporting after the 2023 drain frequently cited this audit as a red flag. However, because Atomic Wallet did not publish a definitive root-cause report for the June 2023 incident, the audit findings should be treated as relevant prior-risk context rather than proof of the exact exploited path.

### 2.3 Attack surface considerations

Several vectors could plausibly explain a compromise of locally encrypted seed phrases or derived keys at scale:

1. **Supply-chain or build compromise**: A malicious dependency, compromised build pipeline, or poisoned update artifact could embed key-exfiltration logic into a wallet application binary distributed to users.

2. **Server-side or telemetry exposure**: If an application transmits encrypted seed material, derived key material, logs, or material sufficient to assist reconstruction during backups, telemetry, or swap coordination, a compromise of related infrastructure could become high impact.

3. **Insufficient local encryption**: If the AES-256 encryption of local seed storage used a weak key-derivation function, short salt, or predictable initialization vector, an attacker who obtained the encrypted files (via malware, cloud sync, or another vulnerability) could brute-force passwords at scale.

4. **CDN or update-channel poisoning**: If an application's auto-update mechanism failed to verify cryptographic signatures on binaries, an attacker who compromised the update channel could distribute a trojanized version to users.

## 3. Attack execution and on-chain forensics

### 3.1 Timeline of the drain

The earliest widely reported unauthorized transactions appeared on-chain on 2 June 2023. Public analysis described the drain as occurring in waves:

- **Early wave (2-3 June)**: Higher-value wallets on major chains were drained quickly. Transactions were broadcast in rapid succession, suggesting automated tooling.

- **Follow-on wave (3-4 June)**: Additional wallets across BSC, XRP Ledger, Dogecoin, Litecoin, and other chains were emptied. The attacker appeared to work through chains and assets in batches, suggesting automated key-derivation and sweep processes.

- **Later sweeps (5-10 June and after)**: Residual wallets and less common assets were swept. Some victims reported funds disappearing after the initial wave, consistent with an attacker holding key material or access paths and sweeping balances opportunistically.

### 3.2 Laundering methodology

On-chain analysis, particularly by Elliptic and the pseudonymous researcher ZachXBT, mapped portions of the laundering pipeline:

1. **Initial consolidation**: Stolen ERC-20 tokens were swapped to ETH via decentralized exchanges such as Uniswap and 1inch. BTC and other UTXO-chain funds were consolidated into intermediate wallets.

2. **Mixer usage**: Ethereum-denominated and Bitcoin-denominated funds were linked by investigators to laundering paths that included Sinbad.io, a mixer later sanctioned by the U.S. Treasury's Office of Foreign Assets Control (OFAC) in November 2023.

3. **Cross-chain movement**: Portions of the stolen funds were bridged or swapped across chains to complicate tracing. Cross-chain protocols and centralized venues were used to convert between asset types.

4. **Exchange deposit**: Some later-stage funds were deposited into centralized exchanges, where incident-response partners and law enforcement attempted freezes where possible.

### 3.3 Attribution to the Lazarus Group

Multiple independent analysts, including Elliptic, attributed the Atomic Wallet attack to North Korea's Lazarus Group with high confidence. The FBI later publicly identified DPRK-linked actors in connection with Atomic Wallet stolen funds. The attribution rested on several converging indicators:

- **Laundering pattern overlap**: The mixer usage, peel-chain structure, and timing of consolidation transactions matched Lazarus Group's established playbook from the Harmony Horizon Bridge ($100M, June 2022) and Ronin Bridge ($625M, March 2022) hacks.

- **Sinbad.io association**: Elliptic's analysis showed that Atomic Wallet funds were laundered through infrastructure associated with prior DPRK-linked laundering, including Sinbad.io.

- **FBI attribution**: In an August 2023 statement, the FBI identified cryptocurrency stolen by DPRK actors and included Atomic Wallet among the affected incidents.

- **Operational consistency**: The multi-chain, multi-asset targeting pattern — draining many assets associated with compromised wallets rather than targeting one chain — was consistent with DPRK-linked operations that aim to maximize extraction per compromised target.

## 4. Atomic Wallet's response and transparency failures

### 4.1 Initial disclosure

Atomic Wallet's initial response drew criticism for both its pace and content. The company's first public acknowledgment came via a tweet on 3 June 2023, over 24 hours after the first unauthorized outflows, stating: "We have received reports of wallets being compromised. We are doing all we can to investigate and analyze the situation. As we have more information, we will share it accordingly."

### 4.2 Scope minimization

In subsequent communications, Atomic Wallet stated that "less than 1% of monthly active users" were affected. While this figure may have been numerically accurate relative to the total user base, critics noted that it obscured the severity of the financial impact: affected users collectively lost amounts later reported above $100 million. The framing was perceived by some observers as minimizing the incident's significance.

### 4.3 Root-cause opacity

Atomic Wallet did not publish a detailed technical post-mortem or definitive root-cause analysis. The company retained blockchain analytics support to assist with tracing stolen funds but did not publicly disclose which vulnerability was exploited, whether it had been patched, or what architectural changes were made to prevent recurrence. In a June 2023 blog post, the company listed possible causes under investigation — including network vulnerabilities, malware on user devices, man-in-the-middle attacks, and code injection — but did not narrow these down publicly.

This opacity left users unable to assess whether the wallet was safe to continue using. Security researchers noted that without a confirmed root cause, there was no basis to believe the vulnerability had been remediated.

### 4.4 No compensation program

Unlike some projects that have established recovery funds or user-compensation mechanisms after security incidents, Atomic Wallet did not announce a broad compensation or restitution program for affected users. The company stated that it was working with law enforcement and blockchain analytics firms to trace and recover funds, but public reporting did not show a full victim reimbursement process.

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

Atomic Wallet's desktop software architecture and third-party dependencies illustrate the supply-chain risk inherent in modern cryptocurrency wallet software. A single compromised package, a poisoned CI/CD pipeline, or a malicious pull request in an upstream dependency could inject key-exfiltration logic that persists through multiple wallet versions before detection. This risk is not unique to Atomic Wallet; it applies to any wallet built with extensive third-party dependencies.

The incident accelerated industry discussion about:

- **Reproducible builds**: Allowing users and auditors to verify that distributed binaries correspond to the published source code.
- **Dependency minimization**: Reducing the npm dependency tree to shrink the supply-chain attack surface.
- **Hardware wallet integration**: Encouraging users to use hardware wallets for high-value storage, keeping signing keys on dedicated secure elements rather than in software wallets.
- **Transparency reports**: Publishing regular security audits and incident-response procedures before incidents occur, not after.

### 6.3 DPRK cyber theft as a systemic market risk

The reported Lazarus Group / DPRK connection in the Atomic Wallet hack — alongside the Ronin Bridge, Harmony Horizon, and numerous other cryptocurrency thefts — positions DPRK-sponsored cyber operations as a systemic risk to the cryptocurrency market. The UN Panel of Experts estimated that DPRK-linked groups stole approximately $1.7 billion in cryptocurrency in 2022 alone. The Atomic Wallet attack added to the 2023 threat landscape.

For market health, the implications are:

- **Liquidity and price impact**: Large-scale thefts followed by laundering can inject sell pressure into markets when the attacker converts stolen assets to more liquid or fiat-usable forms. This can affect liquidity and prices of specific tokens, especially smaller assets.

- **Regulatory response**: Each major hack attributed to DPRK actors strengthens policy arguments for stricter security and incident-reporting expectations for cryptocurrency infrastructure.

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

The Atomic Wallet incident of June 2023 demonstrated that non-custodial wallet security is contingent on implementation, distribution, dependencies, and incident transparency, not merely on the cryptographic design of key storage. The attack, attributed by investigators and the FBI to DPRK-linked actors, affected more than 5,000 wallets across multiple blockchains and resulted in losses reported above $100 million. Atomic Wallet's response was criticized for limited root-cause transparency, leaving users and the broader ecosystem unable to independently determine whether the vulnerability was remediated.

The incident underscores the structural risk that software, dependency, update-channel, and key-management failures pose to cryptocurrency infrastructure and highlights the growing role of state-sponsored threat actors as a systemic concern for market health. For the ecosystem to mature, wallet developers should adopt reproducible builds, minimize dependencies, promptly address audit findings, and commit to transparency when incidents occur. Users, in turn, should treat software wallets as convenience tools rather than secure vaults, and allocate significant holdings to hardware wallets with isolated signing environments.
