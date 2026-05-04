---
date: 2026-05-05
entities:
  - id: wazirx
    name: WazirX
    type: exchange
  - id: liminal-custody
    name: Liminal Custody
    type: custodian
  - id: lazarus-group
    name: Lazarus Group
    type: threat-actor
  - id: ethereum
    name: Ethereum
    type: blockchain
  - id: india
    name: India
    type: jurisdiction
title: "WazirX multisig wallet breach and the $230 M exchange-custody loss"
---

## 1. Introduction and incident overview

On 18 July 2024, Indian cryptocurrency exchange WazirX disclosed that one of its multisig wallets had suffered a security breach. More than $230 million in cryptoassets was removed from the wallet, making the incident one of the largest exchange-custody failures in India and one of the largest global exchange hacks of 2024. Elliptic estimated the loss at approximately $235 million across more than 200 assets, including large positions in SHIB, ETH, MATIC, PEPE, and other ERC-20 tokens.

The affected wallet was operated using Liminal's digital-asset custody and wallet infrastructure. WazirX's preliminary report described a six-signatory configuration: five WazirX signatories and one Liminal signatory, with ordinary transactions requiring three WazirX approvals followed by Liminal approval. WazirX stated that signers saw one set of transaction information on Liminal's interface while the transaction actually signed appeared to contain a different payload. WazirX suspected that the payload had been replaced to transfer wallet control to an attacker.

The incident was not a public smart-contract bug in the exchange's trading engine. It was a custody-workflow failure: a Safe-style multisig, third-party custody interface, hardware-wallet signing process, whitelisting policy, and contract-control path were all part of the trust boundary. The market-health lesson is that exchange solvency can be damaged even when the core matching engine and user interface remain online, because customer assets ultimately depend on the integrity of wallet operations.

## 2. WazirX and custody architecture

### 2.1 Exchange custody model

Centralized exchanges aggregate user deposits into wallets controlled by the exchange or its custody partners. Users see account balances in an exchange database, but the underlying assets are held in on-chain wallets, bank accounts, or custodial arrangements. If a wallet holding customer crypto is drained, the exchange account balances become claims against a depleted pool rather than direct ownership of assets.

WazirX's affected wallet held Ethereum and ERC-20 tokens. According to public reporting, the stolen value represented a substantial portion of WazirX's reported crypto holdings. That scale matters: this was not a hot-wallet incident limited to daily withdrawal liquidity. It affected a wallet large enough that the exchange had to pause INR and crypto withdrawals and later deal with user-balance, restructuring, and recovery questions.

### 2.2 Liminal custody arrangement

The wallet was operated using Liminal's infrastructure from February 2023. WazirX said that Liminal's interface facilitated whitelisted destination addresses and that WazirX signatories could initiate transactions to those whitelisted addresses. Liminal, for its part, publicly disputed responsibility and argued that its infrastructure was not compromised. The result was a public custody dispute about where the trust boundary failed.

For market-health analysis, the blame dispute is less important than the architecture it exposes. A third-party custody arrangement can reduce some internal key-management risk, but it can also create interface and responsibility gaps:

1. **Who verifies what is displayed?** Signers rely on a web or custody interface to describe the transaction.
2. **Who verifies raw payloads?** Hardware wallets may not decode complex smart-contract upgrades in a human-readable way.
3. **Who controls policy?** Whitelisting and approval rules may be enforced by one party while signing authority is split across several parties.
4. **Who is liable after failure?** Users generally have a relationship with the exchange, not direct contractual visibility into every custody component.

When a loss occurs, these gaps can delay remediation, complicate litigation, and make users bear uncertainty while counterparties debate root cause.

### 2.3 Multisig security model

The affected setup reportedly involved six signatories: five controlled by WazirX personnel and one by Liminal. WazirX said a transaction normally required three WazirX signatories using Ledger hardware wallets plus final approval from Liminal. A design like this is intended to prevent a single compromised key from moving funds.

Multisig does not, however, eliminate transaction-deception risk. If attackers can cause signers to approve a malicious smart-contract upgrade or control transfer while the interface displays a benign transaction, the multisig threshold can be satisfied without the signers understanding the true effect. In that scenario, the attack is not "one stolen key"; it is compromise or manipulation of the signing workflow.

## 3. Attack mechanics

### 3.1 Displayed transaction versus signed payload

WazirX's preliminary report stated that the attack stemmed from a discrepancy between data displayed on Liminal's interface and the transaction's actual contents. The key phrase was that there was a mismatch between "what was actually signed" and what signers saw on the interface. WazirX suspected that the payload was replaced to transfer wallet control to an attacker.

This pattern is similar to other high-end crypto thefts where attackers target the human-signing layer rather than the cryptography itself. The private keys do not need to be mathematically broken. The attacker needs valid signatures on a malicious transaction. If a compromised browser, custody platform, signing bridge, transaction-building service, or operator workstation can alter the payload while preserving a benign display, the signatures become valid approvals for the attacker's transaction.

### 3.2 Malicious contract-control change

Technical analyses described the incident as involving a malicious smart-contract upgrade or control transfer. Once the attacker obtained enough approvals, the wallet control path was changed so assets could be drained to attacker-controlled addresses. The effect was that the attacker did not need to defeat every future withdrawal policy; after the control change, the wallet could be emptied under the attacker's logic.

This is a crucial distinction from a simple unauthorized transfer. In a simple transfer theft, the attacker signs a transaction moving assets from wallet A to wallet B. In a contract-control attack, the attacker changes who controls the wallet or how it executes transfers, then drains the wallet. That makes transaction review harder because the dangerous action may appear as an administrative operation rather than a visible list of outbound token transfers.

### 3.3 Whitelisting limitations

WazirX said a destination-address whitelist was in place. Whitelisting is valuable for ordinary transfers because it restricts where funds can be sent. But whitelisting can fail if the approved transaction is not a simple transfer to a destination address. If the malicious payload changes wallet control, upgrades implementation logic, or delegates authority, the ultimate asset movement can occur after the policy check that signers thought they were approving.

This limitation appears across custody systems. Controls designed for one transaction type may not protect against meta-transactions, smart-contract upgrades, delegate calls, module changes, or ownership transfers. Exchange wallet policies must therefore classify administrative transactions as high risk even if they do not immediately move tokens.

### 3.4 Hardware-wallet limitations

WazirX highlighted that the WazirX signatories used Ledger hardware wallets. Hardware wallets reduce key-extraction risk: malware on a laptop should not be able to read the private key directly. But hardware wallets cannot protect users who approve a transaction they do not understand. If the device displays incomplete or opaque calldata, or if signers rely on a custody interface for semantic meaning, they can still approve malicious operations.

The WazirX incident therefore fits a broader lesson: hardware wallets are necessary but not sufficient for institutional custody. Secure custody also requires clean signing hosts, independent transaction decoding, out-of-band verification, role separation, and pre-execution simulation.

## 4. Stolen assets and laundering

### 4.1 Asset composition

Elliptic reported that approximately $235 million in cryptoassets was lost, made up of more than 200 different assets. The largest reported components included:

| Asset | Approximate value reported by Elliptic |
|---|---:|
| SHIB | $96.7 million |
| ETH | $52.6 million |
| MATIC | $11 million |
| PEPE | $7.6 million |

The SHIB-heavy composition created immediate market impact because a large token inventory had to be converted into more liquid assets. Attackers typically prefer ETH or stablecoins for laundering because they have deeper liquidity, more routing options, and more established mixing or cross-chain paths.

### 4.2 Conversion to Ether

Elliptic observed that the thief had already swapped a number of stolen tokens for Ether using decentralized services soon after the breach. This is a standard first step after multi-asset theft: consolidate thinly traded or easily blacklisted tokens into a more liquid base asset, then fragment and route funds through additional addresses and services.

The conversion phase also creates observable market stress. Large sales of protocol or meme tokens can move prices, alert liquidity providers, and expose the theft before all assets are fully laundered. For exchanges and analytics firms, large post-breach swaps are useful tracing points; for users, they represent proof that the screen balance on the exchange no longer maps to recoverable assets.

### 4.3 North Korea attribution

Elliptic stated shortly after the incident that on-chain analysis and other information indicated hackers affiliated with North Korea perpetrated the breach. In January 2025, reporting on a joint statement by the United States, South Korea, and Japan described the WazirX hack as one of several cryptocurrency thefts attributed to DPRK-linked actors, alongside incidents involving DMM Bitcoin, Upbit, and Rain Management.

Attribution should be separated from mechanics. The on-chain mechanics show that a wallet-control path failed and assets were drained. Attribution addresses who likely operated or benefited from the attack. For market health, both matter: DPRK-linked groups have demonstrated patience, social-engineering capability, and laundering infrastructure, which increases the threat level for exchanges with large pooled wallets.

## 5. Immediate response and user impact

### 5.1 Withdrawal pause

WazirX paused INR and crypto withdrawals after disclosing the breach. A withdrawal pause is understandable during incident response, because the exchange must prevent additional losses and reconcile balances. But for users, it turns an exchange account into a frozen claim. Until withdrawals resume, the user cannot independently verify whether their account balance is backed by assets they can control.

This is why exchange hacks become solvency events. A breach that removes pooled assets creates a mismatch between user liabilities and remaining assets. Even if the exchange intends to make users whole, the immediate effect is the same as any custodial failure: users lose liquidity exactly when they most need it.

### 5.2 Balance snapshots and loss allocation

After the breach, WazirX had to determine how user balances would be treated. Public reporting discussed snapshots, reversals of post-incident activity, and proposals for spreading losses or recovering through restructuring. Those decisions are market-health issues, not just customer-support issues.

If losses are socialized across all users, customers whose specific assets were not directly in the drained wallet may still suffer. If losses are assigned only to users whose assets were in the wallet, similarly situated users may receive different treatment based on internal custody allocation they could not observe. Either approach can be contested because exchange users generally do not know which wallet backs their account balance at any moment.

### 5.3 Custody dispute

The public dispute between WazirX and Liminal added uncertainty. WazirX pointed to a mismatch between Liminal's interface and the signed transaction. Liminal argued that its infrastructure was not compromised and that responsibility lay elsewhere in the wallet or signing environment. For users, the practical problem was that assets were gone while the responsible parties disputed the failure boundary.

This is a recurring issue in outsourced custody. The exchange may advertise institutional custody as a trust signal, but users may have no direct recourse against the custodian. The custodian may provide infrastructure but not guarantee exchange solvency. If contracts do not clearly allocate operational, interface, and signing risk, the public dispute can delay recovery.

### 5.4 Secondary scams

CloudSEK reported that scammers quickly created lookalike domains and refund-related schemes targeting distressed WazirX users. This is common after large exchange hacks. Victims are searching for recovery information, support links, and compensation forms; attackers exploit that urgency with phishing pages, fake claim portals, and impersonated social accounts.

Incident response therefore has to include user-protection communications. A hacked exchange should not only announce the breach; it should maintain a verified communication hub, list fake domains, warn users not to sign recovery transactions, and coordinate takedowns with registrars and platforms.

## 6. Market-health implications

### 6.1 Exchange proof of reserves is incomplete

Proof of reserves can show that wallets held assets at a point in time, but it cannot guarantee that wallet controls are safe. WazirX reportedly held around $503 million in assets before the incident, and the stolen amount represented close to half of that figure. A reserve proof does not prevent a later wallet-control compromise.

For exchange users, reserve proof should be treated as one input, not a complete assurance. The stronger standard combines proof of reserves, proof of liabilities, segregation of client assets, wallet-control audits, incident-response capital, and transparent custody contracts.

### 6.2 Multisig threshold is not enough

The WazirX wallet required multiple approvals, but the approvals were only as good as the information signers verified. Multisig protects against unilateral action; it does not protect against coordinated deception of several signers or compromise of the transaction-building workflow.

For high-value exchange wallets, signers should verify:

1. Raw calldata through an independent decoder.
2. Target contracts and implementation addresses against an allowlist.
3. Expected state changes through simulation.
4. Administrative operations through out-of-band approval.
5. Transaction hashes across multiple independent devices.

If all signers rely on the same interface, the multisig can become a multi-person rubber stamp for a compromised transaction builder.

### 6.3 Custody vendors need explicit failure boundaries

Third-party custody is often presented as a security upgrade, but users and regulators need to understand the exact boundary:

1. Does the custodian control any signing key?
2. Does the custodian build transactions or merely approve them?
3. Does the custodian enforce whitelists on-chain, off-chain, or both?
4. Who verifies smart-contract upgrade payloads?
5. Who indemnifies users if the interface displays incorrect transaction details?

Without clear answers, "institutional custody" can become a vague trust label rather than a measurable security control.

### 6.4 Administrative operations deserve higher friction

The dangerous transaction in a wallet-control incident may not look like a withdrawal. It may be an upgrade, module change, delegate call, owner change, or policy update. These operations should require more friction than routine asset transfers:

1. Longer timelocks.
2. Higher signature thresholds.
3. Independent security-team review.
4. Public pre-announcement for non-emergency changes.
5. Automatic alerts to users and analytics providers.

Fast execution is useful for operations, but high-speed administrative changes create a catastrophic failure mode when the transaction is malicious.

### 6.5 User claims are not the same as wallet assets

The WazirX incident also illustrates the difference between exchange balances and on-chain assets. A user may believe they own a specific amount of ETH, SHIB, MATIC, or USDT. In practice, they own a claim against the exchange. If the exchange's pooled wallet loses assets, the user becomes part of a recovery process, not an on-chain owner able to move funds.

This distinction is central to crypto market health. Exchanges can provide convenience, liquidity, and fiat rails, but they reintroduce custodial credit risk that self-custody was designed to avoid.

## 7. Detection and prevention framework

### 7.1 Controls for exchanges

Exchanges holding large customer balances should implement:

1. **Independent transaction decoding**: Every signer verifies raw calldata outside the custody interface.
2. **Administrative-operation timelocks**: Wallet upgrades and owner changes cannot execute immediately after signing.
3. **Multi-vendor verification**: A second system reconstructs the transaction from source intent and compares hashes.
4. **Signer device isolation**: Signing devices and hosts are not used for email, browsing, messaging, or file downloads.
5. **Custody runbooks**: Vendor responsibilities and emergency contacts are documented before an incident.
6. **Circuit breakers**: Large or unusual asset movements trigger automatic pauses and public alerts.

### 7.2 Controls for custodians

Custody vendors should provide:

1. Verifiable transaction previews with raw calldata and decoded state changes.
2. Tamper-evident signing logs that can be independently audited.
3. On-chain enforcement of critical policies where possible, not only interface-level controls.
4. Clear client guidance for smart-contract upgrade and Safe module transactions.
5. Liability and escalation terms that users, exchanges, and regulators can understand.

### 7.3 Controls for users and institutions

Users and institutions cannot inspect every exchange wallet, but they can reduce exposure:

1. Keep only active trading balances on exchanges.
2. Prefer venues that publish wallet lists, reserve attestations, liability proofs, and custody architecture.
3. Diversify custody across venues and self-custody where operationally feasible.
4. Treat withdrawal pauses as credit events, not routine maintenance.
5. Watch for post-hack phishing and recovery scams before signing any transaction.

### 7.4 Market surveillance signals

Analytics teams should monitor:

1. Large token outflows from known exchange multisigs.
2. Safe owner changes, module additions, implementation upgrades, or policy changes on exchange wallets.
3. Sudden swaps from diverse stolen-token baskets into ETH.
4. Movement from exchange-linked wallets to newly created addresses.
5. Fake recovery domains and impersonation campaigns after high-profile incidents.

The faster these signals are detected and broadcast, the greater the chance that exchanges, bridges, stablecoin issuers, and law enforcement can freeze or trace funds before laundering is complete.

## 8. Lessons learned

The WazirX breach demonstrates that exchange security depends on the full custody workflow, not just on private-key storage. Hardware wallets, multisig thresholds, whitelisted addresses, third-party custody, and proof of reserves each reduce some risks, but none is sufficient if signers approve a malicious control-changing payload.

The incident also shows that users bear the consequences of architectural ambiguity. They did not choose the exact wallet design, custody vendor, or signing interface, yet they faced withdrawal pauses and uncertain recovery after the breach. When an exchange pools customer assets, every internal custody decision becomes a user-risk decision.

## 9. Conclusion

WazirX's July 2024 multisig-wallet breach was a market-health failure at the intersection of exchange custody, third-party wallet infrastructure, signer verification, and state-sponsored crypto theft. More than $230 million in assets was removed from a wallet whose controls were supposed to require multiple independent approvals. The attacker appears to have exploited the gap between displayed transaction intent and signed transaction payload, turning valid multisig approvals into a wallet-control compromise.

For the broader market, the lesson is clear: institutional custody must be verifiable, not merely branded. Signers need independent payload verification; administrative wallet operations need timelocks and higher thresholds; custody vendors need explicit failure boundaries; and users need to understand that an exchange balance is a claim on a custody system they cannot directly control. Without those controls, a multisig can fail not because cryptography breaks, but because the humans and interfaces around it sign the wrong thing.
