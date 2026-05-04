---
date: 2026-05-05
entities:
  - id: ledger
    name: Ledger
    type: infrastructure
  - id: ledger-connect-kit
    name: Ledger Connect Kit
    type: defi
  - id: npmjs
    name: npm (NPMJS)
    type: infrastructure
title: "Ledger Connect Kit supply-chain compromise, wallet-drainer injection, and $600 K cross-dApp theft"
---

## 1. Introduction and incident overview

On 14 December 2023, the Ledger Connect Kit — an npm JavaScript library used by decentralized applications (dApps) to enable users to connect their Ledger hardware wallets — was compromised through a supply-chain attack. An attacker who gained access to a former Ledger employee's npm account published three malicious versions (1.1.5, 1.1.6, and 1.1.7) of the `@ledgerhq/connect-kit` package. The malicious code injected a wallet-drainer payload into every dApp that loaded the compromised library, redirecting users' funds to the attacker's wallets when they signed transactions. The attack resulted in approximately $600,000 in stolen funds before the malicious package was removed and a clean version was deployed.

The Ledger Connect Kit incident was a high-profile example of a software supply-chain attack targeting the cryptocurrency ecosystem. Unlike exploits that target a single smart contract or protocol, supply-chain attacks compromise a shared dependency — in this case, a widely used JavaScript library — which then propagates malicious code to every application that uses that dependency. The incident demonstrated that the security of DeFi front ends depends not only on the protocols' own code but also on the security of their entire software dependency chain, including third-party libraries hosted on public package registries.

## 2. Technical background

### 2.1 Ledger Connect Kit

Ledger Connect Kit is an open-source JavaScript library published by Ledger on the npm (Node Package Manager) registry under the scope `@ledgerhq/connect-kit`. The library provides a standardized interface for dApps to detect, connect to, and interact with Ledger hardware wallets. When a user visits a dApp that integrates Ledger Connect Kit, the library handles the communication between the web browser and the Ledger device, enabling the user to review and sign transactions on their hardware wallet's secure display.

Ledger Connect Kit was integrated into numerous DeFi front ends, including SushiSwap, Zapper, Revoke.cash, and other prominent dApps. The library was typically loaded dynamically from a CDN (Content Delivery Network) or installed as an npm dependency, meaning that updates to the library would automatically propagate to all dApps that referenced it without requiring each dApp to explicitly update their code.

### 2.2 npm and the JavaScript supply chain

npm (NPMJS) is the world's largest software registry, hosting over two million JavaScript packages. It is the standard package manager for Node.js and is widely used by web applications, including DeFi front ends. When a developer publishes a package to npm, any application that depends on that package can automatically receive updates (depending on the version pinning strategy).

The npm ecosystem's trust model is based on account authentication: only the account holder for a given package scope can publish new versions. If an attacker gains access to a maintainer's npm account, they can publish arbitrary code under that package's name, and any application that loads the package (either directly or via a CDN that mirrors npm) will execute the attacker's code. This creates a single-point-of-failure security model where the compromise of a single npm account can affect thousands or millions of downstream applications.

### 2.3 Supply-chain attacks in the software ecosystem

Software supply-chain attacks — where an attacker compromises a dependency rather than the target application itself — have become an increasingly common attack vector across the software industry. Notable supply-chain incidents include the SolarWinds compromise (2020), the ua-parser-js npm package hijack (2021), the event-stream npm package backdoor (2018), and the Codecov bash uploader compromise (2021). In the cryptocurrency space, supply-chain attacks are particularly dangerous because the target applications handle financial transactions, meaning that injected malicious code can directly steal funds.

## 3. The attack

### 3.1 Initial compromise: phishing the npm account

The attack began when a former Ledger employee fell victim to a phishing attack that captured their npm session token. The phishing attack bypassed the employee's two-factor authentication (2FA) because it captured the active session token rather than attempting to authenticate with credentials. With the session token, the attacker gained access to the former employee's NPMJS account, which retained publish permissions for the `@ledgerhq/connect-kit` package.

The fact that a former employee retained npm publish permissions for a critical Ledger package indicated a gap in Ledger's access-management procedures. Offboarding processes should revoke all access to production systems and package registries, but the former employee's npm account credentials had not been rotated or the account's publish permissions had not been removed after their departure.

### 3.2 Malicious package publication

On 14 December 2023, beginning at approximately 09:49 CET, the attacker used the compromised npm account to publish three successive malicious versions of Ledger Connect Kit:

- **Version 1.1.5** (published ~09:49 CET)
- **Version 1.1.6** (published ~10:44 CET)
- **Version 1.1.7** (published ~11:37 CET)

The malicious versions contained injected code that loaded a wallet-drainer payload. The drainer used a rogue WalletConnect project to redirect users' funds. When a user interacted with any dApp that loaded one of the compromised versions of Ledger Connect Kit, the injected code presented a transaction that, if signed, would transfer the user's assets to the attacker's wallet.

The multiple version publications (three within approximately two hours) likely represented the attacker refining the malicious payload or attempting to evade detection by replacing earlier versions with updated ones.

### 3.3 Propagation via CDN

The attack's impact was amplified by the CDN distribution model used by many dApps. Rather than bundling a specific version of Ledger Connect Kit at build time, some dApps loaded the library dynamically from a CDN that served the latest published version from npm. When the attacker published the malicious versions to npm, the CDN automatically began serving the compromised code to any dApp that requested the library.

This CDN propagation model meant that dApps were affected without any action by their developers — the malicious code was injected automatically through the dependency chain. Conversely, even after Ledger published a clean version of the library to npm, the CDN's caching behavior meant that some edge servers continued to serve the malicious version until their caches expired and were refreshed with the clean version.

### 3.4 Attack window and impact

The malicious library was available on npm for approximately five hours. However, the window during which user assets were actively being drained was estimated at less than two hours. The discrepancy reflects the time required for CDN propagation (both for the malicious code to reach all edge servers and for the clean replacement to fully propagate).

During the active attack window, users who visited affected dApps and signed transactions had their funds redirected to the attacker. The total losses were approximately $600,000 across multiple users and chains (primarily Ethereum and EVM-compatible networks). The relatively modest total — compared to the potential blast radius of a library used by dozens of major dApps — reflected the narrow time window and the fact that the attack required users to actively sign transactions during the compromised period.

## 4. Affected ecosystem

### 4.1 Scope of affected dApps

Any dApp that loaded one of the compromised versions (1.1.5, 1.1.6, or 1.1.7) of `@ledgerhq/connect-kit` during the attack window was potentially affected. The library's integration into multiple DeFi front ends meant that the attack surface included:

- **SushiSwap**: A major decentralized exchange.
- **Zapper**: A DeFi portfolio management and interaction platform.
- **Revoke.cash**: Ironically, a tool specifically designed to help users revoke token approvals and manage wallet security.
- Numerous other dApps that integrated Ledger Connect Kit for hardware wallet support.

The compromise of Revoke.cash was particularly noteworthy because users specifically visit Revoke.cash to improve their wallet security. During the attack window, users attempting to revoke token approvals (a security best practice) were instead exposed to the wallet-drainer payload.

### 4.2 Interaction model

The wallet-drainer payload required user interaction to steal funds. The malicious code could not bypass the hardware wallet's transaction-signing requirement — users still needed to physically confirm transactions on their Ledger device. However, the injected code modified the transaction parameters that were presented to users, replacing legitimate dApp transactions with transfers to the attacker's address. Users who did not carefully verify the transaction details on their Ledger device's screen before confirming would unknowingly sign the malicious transaction.

This highlights an important security property of hardware wallets: even during a supply-chain attack that compromises the software interface, the hardware wallet's trusted display provides a last line of defense. Users who verified the transaction details shown on their Ledger device (rather than relying on the software interface's representation) could have detected the discrepancy and rejected the malicious transaction.

### 4.3 Hardware wallet security model preserved

The attack did not compromise Ledger's hardware wallet firmware, secure element, or private-key storage. Users' seed phrases and private keys were never exposed. The attack operated entirely at the software layer — compromising the JavaScript library that facilitates communication between the web browser and the hardware wallet. The hardware wallet's core security guarantees (private keys never leave the secure element, transactions must be confirmed on the device's display) remained intact.

This distinction is significant for understanding the attack's scope: users who did not interact with any dApp during the attack window were not affected, regardless of whether they owned a Ledger device. The attack targeted the software bridge between dApps and hardware wallets, not the hardware wallets themselves.

## 5. Response and aftermath

### 5.1 Detection

The attack was first detected by Blockaid, a web3 security firm, which identified the malicious payload in the Ledger Connect Kit library and alerted Ledger at approximately 13:45 CET. The community also rapidly identified and disseminated warnings through social media and developer communication channels.

### 5.2 Remediation

Ledger's technology and security teams deployed a clean version of the Connect Kit library within approximately 40 minutes of being alerted (at approximately 14:18 CET). The clean version removed the malicious code and restored legitimate functionality. However, due to CDN caching, the malicious version remained accessible from some CDN edge servers for a period after the clean version was published to npm.

To accelerate the remediation, Ledger coordinated with WalletConnect to disable the rogue WalletConnect project that the malicious code used to redirect funds. This effectively broke the malicious payload's fund-redirection mechanism even for users still loading the cached malicious library version.

### 5.3 Fund recovery efforts

On the same day as the attack, Tether froze the USDT held in the attacker's address at approximately 14:55 CET. This freezing prevented the attacker from moving or exchanging the USDT portion of the stolen funds. Ledger worked with law enforcement and blockchain analytics firms to trace the attacker's fund-movement activity across chains.

Ledger announced that it would make affected users whole, committing to compensate the approximately $600,000 in stolen funds. This compensation commitment was notable as an acknowledgment that the supply-chain compromise was Ledger's responsibility, since it resulted from inadequate access controls on the npm package.

### 5.4 Post-incident security measures

Following the incident, Ledger implemented several security improvements:

1. **npm account access revocation**: All former employees' access to Ledger's npm packages was revoked, and publish permissions were restricted to current, authorized personnel with enhanced authentication requirements.

2. **Package signing and integrity verification**: Ledger enhanced the integrity verification mechanisms for its published packages, including exploring npm package provenance (supply-chain attestation) to allow consumers to verify that published packages originate from authorized build pipelines.

3. **CDN and distribution review**: Ledger reviewed its library distribution model to reduce reliance on automatic CDN propagation of latest versions, encouraging dApp developers to pin specific verified versions rather than loading the latest version dynamically.

4. **Clear signing initiative**: Ledger accelerated its initiative to promote "clear signing" — the practice of displaying human-readable transaction details on hardware wallet screens — which helps users detect malicious transaction modifications even when the software interface is compromised.

## 6. Market-health implications

### 6.1 Software supply-chain risk in DeFi

The Ledger Connect Kit incident highlighted a systemic risk in the DeFi ecosystem: the dependence of DeFi front ends on shared JavaScript libraries distributed through public package registries. The npm ecosystem hosts thousands of packages used by DeFi front ends, and each package represents a potential supply-chain attack vector. A single compromised package can affect every dApp that depends on it, creating a one-to-many amplification effect.

This supply-chain risk is distinct from and orthogonal to smart-contract security. A DeFi protocol can have perfectly secure smart contracts, thoroughly audited by multiple firms, and still be compromised through a supply-chain attack on its front-end dependencies. The Ledger Connect Kit attack did not exploit any smart-contract vulnerability — it compromised the user interface layer, modifying the transactions that users were asked to sign.

| Supply-Chain Incident | Date | Vector | Loss |
|---|---|---|---|
| event-stream npm backdoor | Nov 2018 | Compromised maintainer added malicious dependency targeting Copay wallet | ~$0 (detected early) |
| Ledger Connect Kit | Dec 2023 | Phished npm account, wallet-drainer injected into @ledgerhq/connect-kit | ~$600K |
| Atomic Wallet | Jun 2023 | Suspected supply-chain or infrastructure compromise | ~$100M+ |
| Solana web3.js | Dec 2023 | Compromised npm account, backdoor in @solana/web3.js | ~$160K |

### 6.2 npm account security as critical infrastructure

The incident demonstrated that npm account credentials for widely used packages are effectively critical infrastructure in the DeFi ecosystem. The compromise of a single npm account — belonging to a former employee, no less — was sufficient to inject malicious code into dozens of major DeFi applications. This places npm account security on par with smart-contract deployer key security and bridge validator key security in terms of its potential impact on user funds.

For market surveillance, monitoring npm package publications for high-impact DeFi-related packages can provide early warning of supply-chain compromises. Tools that detect anomalous package updates (unexpected publishers, unusual code changes, new dependencies) can complement on-chain monitoring to provide a more complete view of DeFi ecosystem risk.

### 6.3 CDN-based distribution as a risk amplifier

The CDN distribution model used by many dApps amplified the attack's reach. When a dApp loads a library from a CDN that automatically serves the latest npm version, any update to the npm package immediately affects the dApp's users — without the dApp developer reviewing or approving the update. This "auto-update" model prioritizes convenience and ease of integration over security, creating a risk that is invisible to most dApp users and many dApp developers.

The alternative — pinning specific library versions and loading them from first-party infrastructure — provides better security but requires more maintenance overhead and delays the propagation of security patches. The Ledger incident illustrated the tension between these approaches: the same CDN mechanism that allowed the malicious code to propagate quickly also made remediation slower (due to caching).

### 6.4 Hardware wallet security model under front-end compromise

The incident provided a real-world test of the hardware wallet security model under front-end compromise conditions. The core hardware wallet guarantee — that private keys never leave the secure element and transactions must be confirmed on the device's trusted display — remained intact. Users who carefully verified the transaction details on their Ledger device's screen could have detected and rejected the malicious transactions.

However, the incident also revealed practical limitations of this security model:

- **Transaction readability**: Many DeFi transactions produce complex, encoded data on the hardware wallet display that is difficult for users to interpret. The gap between what the hardware wallet displays and what a user can realistically verify is a practical weakness that attackers can exploit.
- **User behavior**: Most users develop habits of quickly confirming transactions on their hardware wallets without carefully reviewing each field, particularly for routine operations like token swaps. The supply-chain attack exploited this behavioral pattern.
- **Clear signing adoption**: The "clear signing" approach — which translates encoded transaction data into human-readable descriptions on the hardware wallet display — addresses the readability gap but was not universally implemented at the time of the attack.

### 6.5 Broader implications for DeFi front-end security

The Ledger Connect Kit compromise, combined with other front-end attacks in 2022-2023 (BadgerDAO Cloudflare compromise, Celer cBridge BGP hijack, Curve Finance DNS hijack), established front-end security as a critical and under-addressed layer in the DeFi security stack. While the DeFi industry has invested heavily in smart-contract auditing, oracle security, and validator/multisig key management, front-end security — encompassing supply-chain integrity, DNS security, CDN security, and browser-environment security — has received comparatively less attention.

For market health, this front-end security gap represents a systemic risk because:

- Front-end attacks can affect multiple protocols simultaneously (through shared dependencies like Ledger Connect Kit).
- Front-end security is largely invisible to on-chain monitoring tools.
- The attack surface is vast (npm hosts millions of packages, any of which could be compromised).
- Users have limited ability to independently verify front-end integrity.

## 7. Lessons learned and recommendations

### 7.1 For library publishers and DeFi infrastructure providers

1. **Rigorous offboarding**: Immediately revoke all access to package registries, CI/CD systems, and production infrastructure when employees leave the organization. This includes revoking active sessions and rotating any credentials the departing employee may have had access to.

2. **Enforce hardware-key 2FA for package publishing**: Session-token phishing (as used in this attack) can bypass TOTP-based 2FA. Hardware security keys (e.g., FIDO2/WebAuthn) are resistant to phishing attacks and should be mandatory for accounts with package publish permissions.

3. **Implement npm package provenance**: npm's package provenance feature (launched in 2023) allows package consumers to verify that a published package was built from a specific source repository and build pipeline. Publishers should enable provenance attestation to allow consumers to detect unauthorized publications.

4. **Minimize publish permissions**: Restrict npm publish permissions to the minimum set of accounts necessary, using automated CI/CD pipelines (rather than human accounts) for package publication where possible.

### 7.2 For dApp developers

1. **Pin dependency versions**: Load dependencies from specific, verified versions rather than dynamically fetching the latest version from a CDN. This prevents automatic propagation of compromised updates.

2. **Use Subresource Integrity (SRI)**: When loading scripts from external sources, use SRI hashes to ensure that the loaded script matches a known-good version. This prevents CDN-served content from being silently modified.

3. **Monitor dependency updates**: Implement automated monitoring for updates to critical dependencies, reviewing changes before incorporating them. Tools like Socket.dev, Snyk, and npm audit can help identify suspicious package changes.

4. **Bundle dependencies at build time**: Rather than loading dependencies from external CDNs at runtime, bundle them into the dApp's build artifacts. This ensures that the dApp serves a known, verified version of each dependency.

### 7.3 For DeFi users

1. **Verify transactions on hardware wallet displays**: Always verify the recipient address, amount, and other transaction details on your hardware wallet's trusted display before confirming. If the displayed details do not match your intended transaction, reject it.

2. **Be cautious with dApp interactions during incident reports**: If a supply-chain compromise is reported for a library used by DeFi front ends, avoid interacting with dApps until the incident is resolved and confirmed safe.

3. **Use separate wallets for dApp interactions**: Maintain separate wallets for dApp interaction (with limited funds) and long-term storage (with larger holdings), reducing the potential loss from any single front-end compromise.

### 7.4 For market surveillance

1. **Monitor npm publications for DeFi-critical packages**: Track publication events for widely used DeFi-related npm packages. Anomalous publications (unexpected publisher accounts, unusual timing, significant code changes) warrant immediate investigation.

2. **Integrate front-end security monitoring with on-chain surveillance**: Combine on-chain transaction monitoring with off-chain signals (npm publications, DNS changes, CDN behavior, TLS certificate issuance) to provide comprehensive coverage of both smart-contract and front-end attack vectors.

3. **Track DeFi front-end dependency maps**: Maintain awareness of which major DeFi protocols depend on which shared libraries, to assess the blast radius of a supply-chain compromise affecting a specific package.

## 8. Conclusion

The Ledger Connect Kit supply-chain compromise of December 2023 demonstrated that DeFi ecosystem security extends beyond smart contracts to encompass the entire software supply chain that delivers front-end interfaces to users. By phishing a former employee's npm session token and publishing malicious versions of a widely used JavaScript library, the attacker injected a wallet-drainer payload into dozens of major DeFi applications simultaneously, stealing approximately $600,000 from users who signed transactions during the approximately two-hour active attack window.

The incident underscored three structural risks for DeFi market health. First, shared JavaScript dependencies distributed through public package registries create one-to-many amplification vectors where a single compromised account can affect the entire ecosystem. Second, CDN-based distribution models that automatically propagate the latest package version trade security for convenience, enabling both rapid attack propagation and delayed remediation. Third, the gap between the hardware wallet's theoretical security guarantee (trusted display for transaction verification) and users' practical behavior (habitual confirmation without careful review) remains a exploitable weakness that supply-chain attacks can target. For the DeFi ecosystem, the Ledger Connect Kit incident established software supply-chain security as a critical area requiring the same level of investment and attention that the industry has applied to smart-contract auditing and on-chain monitoring.
