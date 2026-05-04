---
date: 2026-05-05
entities:
  - id: radiant-capital
    name: Radiant Capital
    type: defi
  - id: mandiant
    name: Mandiant
    type: analytics
  - id: lazarus-group
    name: Lazarus Group
    type: threat-actor
  - id: arbitrum
    name: Arbitrum
    type: blockchain
  - id: bnb-chain
    name: BNB Chain
    type: blockchain
title: "Radiant Capital multisig signer compromise and $53 M cross-chain lending drain"
---

## 1. Introduction and incident overview

On 16 October 2024, the cross-chain lending protocol Radiant Capital suffered a coordinated attack that drained approximately $53 million in user funds from its deployments on Arbitrum and BNB Chain. The attacker compromised or manipulated the signing environment for enough Radiant multisig signers to obtain valid approvals for control-changing transactions. The incident was notable for the sophistication of the initial compromise vector — malware and social engineering against signer devices — and for the cross-chain scope of the resulting drain.

Radiant Capital engaged the incident-response firm Mandiant to investigate the breach. Mandiant's analysis attributed the attack with high confidence to a North Korean threat actor tracked as UNC4736, associated in public threat-intelligence reporting with DPRK cryptocurrency-theft operations. The attack followed the pattern of DPRK-linked campaigns that have targeted DeFi teams with social engineering, malicious files, and transaction-signing deception.

## 2. Technical background

### 2.1 Radiant Capital's architecture

Radiant Capital is a cross-chain lending protocol built on LayerZero's omnichain messaging infrastructure. It allows users to deposit assets on one chain and borrow against them on another. At the time of the exploit, Radiant had active deployments across multiple EVM networks, with the October drain centered on Arbitrum and BNB Chain and with approximately tens of millions of dollars in total value locked at risk.

The protocol's smart contracts were upgradeable, with administrative functions — including the ability to transfer ownership of lending pools and modify contract parameters — controlled by a multisig wallet. The multisig required 3-of-11 signatures to execute transactions, meaning that any attacker who could obtain three valid signer approvals could execute administrative actions.

### 2.2 Multisig security model

A 3-of-11 multisig provides a relatively low threshold relative to the total number of signers. While 11 signers distribute access broadly, requiring only 3 signatures means an attacker needs to compromise or deceive only 27% of the signer set to gain full control. Industry best practice for high-value DeFi protocols typically recommends higher thresholds (e.g., 5-of-9 or 7-of-11) to increase the number of independent approvals an attacker must obtain.

The security of the multisig ultimately depends on each signer's private key, signing device, and transaction-verification process. Hardware wallets and dedicated signing devices reduce key-extraction risk, but they do not fully solve transaction-deception risk if a compromised host, browser, or signing workflow can cause a signer to approve different calldata than the operation they believe they are approving. Software wallets on general-purpose, internet-connected devices expand the attack surface further to include malware, phishing, and remote-access exploits.

### 2.3 Safe (Gnosis Safe) multisig workflow

Radiant's multisig was implemented using Safe (formerly Gnosis Safe), the most widely used multisig framework in the Ethereum ecosystem. In the standard Safe workflow, one signer proposes a transaction through the Safe web interface, and other signers review and co-sign the transaction in the Safe UI. The transaction is displayed to each signer as a set of parameters (target contract, function call, value), and the signer's wallet signs the transaction data.

A critical aspect of this workflow is that signers rely on the Safe UI and their wallet's transaction-display capabilities to understand what they are signing. If an attacker can manipulate the transaction data displayed to signers — either by compromising the Safe frontend, intercepting the transaction at the device level, or replacing the legitimate transaction with a malicious one — signers may unknowingly approve a transaction that differs from what they intended.

## 3. Attack execution

### 3.1 Social-engineering and device compromise

According to Mandiant's investigation, the attack began with a social-engineering campaign targeting Radiant Capital team members. On approximately 11 September 2024, a Radiant developer received a Telegram message from what appeared to be a former contractor. The message requested feedback on a purported new project and included a link to a zipped PDF document. When the developer opened the file, it executed malware that established persistent access on the developer's device.

The malware and signing-workflow manipulation were identified by Mandiant as consistent with DPRK-linked tooling and tradecraft. Public disclosures indicate that the attacker ultimately obtained usable approvals from at least three signer environments, but they do not fully detail whether the additional exposure came from lateral movement, separate social-engineering messages, compromised communication channels, or some combination of those paths.

### 3.2 Transaction manipulation

With malicious access to, or influence over, at least three signer environments, the attacker was positioned to manipulate the signing workflow. According to Radiant's post-mortem, the attack exploited the gap between what signers saw in their Safe UI and what was actually submitted on-chain:

- When a legitimate routine transaction was proposed through the Safe workflow (such as a regular emissions adjustment), malware on affected devices manipulated the signing context.
- The signers' Safe frontends displayed the expected legitimate transaction, but the actual transaction data submitted to the blockchain was replaced with a malicious `transferOwnership` call.
- Each compromised signer believed they were approving a routine operational transaction but was actually signing an ownership-transfer transaction.

This transaction-deception vector is related to blind-signing risk: most wallet interfaces display a simplified representation of complex contract interactions, and users cannot easily verify raw calldata against the displayed description. Even when a hardware wallet is involved, the device may show only limited target/value information or hashes for arbitrary contract interactions unless signers independently decode and compare calldata.

### 3.3 Ownership transfer and fund drain

Once the attacker obtained three valid signatures on malicious control-changing transactions, they submitted them to the blockchain. The transactions shifted control of key Radiant contracts on Arbitrum and BNB Chain to attacker-controlled logic or addresses.

With privileged control over the lending-pool contracts, the attacker used malicious upgrades and administrative paths to drain a large portion of deposited assets. The drain proceeded rapidly across both chains:

- **Arbitrum**: Roughly $32 million in various assets (including stablecoins and wrapped major assets) was drained from Radiant's Arbitrum lending pools.
- **BNB Chain**: Roughly $21 million in assets was drained from BNB Chain pools.

The total extraction was approximately $53 million across both chains.

### 3.4 Post-drain fund movement

Public tracing showed post-drain movement patterns consistent with large DeFi theft laundering:

1. **Token consolidation**: Diverse stolen tokens were swapped to ETH and BNB via decentralized exchanges.
2. **Cross-chain movement**: Funds were moved between chains and addresses to complicate tracing.
3. **Routing through liquidity venues**: Portions were routed through decentralized exchanges and other on-chain services.
4. **Staged withdrawal**: Rather than liquidating everything immediately, the attacker staged funds across multiple addresses, consistent with cautious laundering after high-profile protocol thefts.

## 4. Attribution and investigation

### 4.1 Mandiant analysis

Radiant Capital engaged Mandiant (now part of Google Cloud) to conduct the incident investigation. Mandiant's analysis attributed the attack to UNC4736, a threat cluster associated with the DPRK's Reconnaissance General Bureau. The attribution was based on:

- **Malware signatures**: The malware reported on compromised devices matched DPRK tooling families previously used in cryptocurrency-targeting operations.
- **Operational patterns**: The social-engineering approach (Telegram-based initial contact, zipped file delivery, contractor impersonation) matched established DPRK tradecraft documented in prior incidents.
- **Laundering behavior**: Post-drain fund movement patterns were consistent with Lazarus Group / DPRK-linked laundering infrastructure.

### 4.2 Law-enforcement and interagency context

Radiant stated that law enforcement and blockchain-intelligence partners were engaged after the exploit. The Mandiant attribution also fits broader U.S. and allied warnings about DPRK cyber operations targeting cryptocurrency infrastructure, including social-engineering campaigns against developers and operations staff. Public law-enforcement statements should be treated as an attribution layer separate from the on-chain mechanics of the exploit.

### 4.3 Implications of the attribution

The DPRK attribution places the Radiant attack in a category of state-sponsored operations that are exceptionally difficult to deter through traditional security measures. DPRK-linked groups have demonstrated:

- **Long-duration reconnaissance**: The social-engineering campaign began over a month before the exploit, indicating patient operational planning.
- **Customized tooling**: Malware was tailored to the specific target's environment and workflow.
- **Operational persistence**: Even after initial access, the attacker waited until the malware was positioned on sufficient signer devices before executing the drain.

## 5. Radiant Capital's response

### 5.1 Immediate actions

Radiant detected the unauthorized transactions within minutes of execution and paused all protocol operations on affected chains. However, the drain was largely complete by the time the pause took effect — the attacker had executed the ownership transfer and fund extraction in rapid succession.

### 5.2 Post-mortem disclosure

Radiant published a detailed post-mortem in collaboration with Mandiant, disclosing the social-engineering vector, the device compromise, and the transaction-manipulation mechanism. This level of transparency was notable compared to many DeFi incidents where the root cause is either not disclosed or described in vague terms.

### 5.3 Security upgrades

Following the incident, Radiant announced several security improvements:

1. **Increased multisig threshold**: The signing threshold was increased so an attacker would need more signer approvals for a successful control change.
2. **Dedicated signing environments**: Signers were moved toward stricter hardware-wallet and clean-device practices.
3. **Transaction verification**: Additional verification steps were implemented to cross-check proposed transactions against expected behavior before signing.
4. **Timelock implementation**: Administrative functions were placed behind a timelock, introducing a delay between transaction proposal and execution that would allow the community to detect and respond to unauthorized transactions.
5. **Independent signature verification**: Signers were instructed to verify transaction calldata through independent channels rather than relying solely on the Safe UI.

### 5.4 Fund recovery efforts

Radiant stated that it was working with law enforcement and blockchain analytics firms to trace and potentially recover stolen funds. Given the attribution and the speed of post-exploit movement, recovery was uncertain and should not be assumed until funds are actually frozen, returned, or otherwise made claimable by affected users.

## 6. Market-health implications

### 6.1 Multisig threshold as a critical security parameter

The Radiant incident demonstrated that multisig security is only as strong as its weakest links — in this case, the individual signers' operational security and transaction-verification workflow. A 3-of-11 threshold meant the attacker needed to compromise or deceive only three signer environments to gain protocol control. For a protocol managing tens of millions of dollars in user funds, this represented a disproportionate concentration of risk.

The incident accelerated an industry discussion about appropriate multisig parameters:

- **Higher thresholds**: Requiring a majority (e.g., 6-of-11 or 7-of-11) of signers makes device-level compromise attacks significantly harder, as the attacker must successfully compromise more targets.
- **Signer diversity**: Distributing signers across different organizations, geographies, and device types reduces the probability that a single social-engineering campaign can reach enough signers.
- **Operational separation**: Requiring signers to use dedicated signing devices, clean hosts, and independent calldata verification limits the attack surface exposed to remote malware.

### 6.2 Social engineering as the primary DeFi attack vector

The Radiant attack reinforces a trend in which the most damaging DeFi exploits originate not from smart-contract vulnerabilities but from compromising the human and operational layers around the protocol. The progression from smart-contract bugs to social engineering reflects the maturation of DeFi security:

- **2020–2021**: Flash-loan oracle manipulations and reentrancy attacks dominated, targeting code-level vulnerabilities.
- **2022–2023**: Key compromises (Ronin, Harmony, Multichain) targeted the operational security of validator and multisig keys.
- **2024+**: Sophisticated social-engineering campaigns (Radiant, and similar patterns in other incidents) target individual team members' devices and trust relationships.

For market surveillance, this progression implies that code audits and formal verification, while necessary, are insufficient. The human and operational attack surface — employee security practices, device management, communication channel integrity — is increasingly the binding constraint on protocol security.

### 6.3 Blind-signing risk in multisig workflows

The transaction-manipulation technique used in the Radiant attack highlights a fundamental limitation of current multisig signing workflows. When signers approve transactions through a web interface (Safe UI) and a wallet (MetaMask, hardware wallet), they rely on those tools to accurately represent the transaction they are signing. If either the frontend or the device is compromised, the displayed transaction may differ from the actual on-chain transaction.

Mitigations for blind-signing risk include:

- **Calldata verification**: Signers independently decode and verify the raw transaction calldata against expected parameters before signing.
- **Simulation**: Using transaction simulation tools (Tenderly, Foundry) to preview the expected state changes of a transaction before signing.
- **Multi-channel confirmation**: Confirming transaction details through out-of-band channels (phone calls, in-person verification) rather than relying solely on digital interfaces.
- **Dedicated signing environments**: Using clean, dedicated devices for signing that are not used for general communication or web browsing, reducing the malware attack surface.

### 6.4 Cross-chain drain amplification

Radiant's cross-chain architecture meant that a single governance or ownership compromise could cascade across multiple chains. The attacker drained both Arbitrum and BNB Chain deployments through the compromised control path, extracting approximately $53 million rather than being limited to a single chain's liquidity.

For cross-chain protocols, this implies that the multisig (or governance mechanism) that controls administrative functions across all chain deployments is a single point of failure for the entire protocol. Chain-specific controls, independent multisigs per deployment, or chain-specific timelocks could limit the blast radius of a single compromise.

### 6.5 DPRK threat escalation

The Radiant attack contributes to a growing body of evidence that DPRK-linked groups are adapting their techniques to target increasingly sophisticated DeFi infrastructure. The progression from exchange hacks (2018–2020) to bridge attacks (2022) to social-engineering-based multisig compromises (2024) demonstrates operational learning and adaptation.

For the market as a whole, DPRK-sponsored theft represents a persistent, well-resourced threat that cannot be addressed through protocol-level security alone. Industry-wide coordination — including threat intelligence sharing, security standards for key management, and employee security training — is necessary to raise the cost of these attacks.

## 7. Lessons learned and recommendations

### 7.1 For DeFi protocols with multisig governance

1. **Set appropriate thresholds**: The multisig threshold should reflect the value under management. For protocols managing tens of millions or more, a majority threshold (>50% of signers) is appropriate.

2. **Enforce dedicated signing environments**: All multisig signers should use hardware wallets with clean, dedicated host devices not used for general communication, web browsing, or document handling.

3. **Implement timelocks**: Administrative functions should have timelocks that create a window for community detection and response before changes take effect.

4. **Verify transactions independently**: Establish procedures for signers to verify transaction calldata through independent channels and simulation tools before signing.

5. **Conduct social-engineering awareness training**: Regular security training for all team members with access to sensitive operations, including recognition of social-engineering patterns (impersonation, document-based malware, urgency pressure).

### 7.2 For multisig signers

1. **Use dedicated signing devices**: Maintain a separate device exclusively for multisig signing operations. Do not use this device for email, messaging, document viewing, or web browsing.

2. **Verify before signing**: Decode transaction calldata independently using tools like Etherscan's ABI decoder or local scripts. Do not rely solely on the Safe UI's transaction description.

3. **Be skeptical of unsolicited messages**: Treat requests for feedback, collaboration proposals, and document sharing from unknown or unexpected contacts as potential social-engineering vectors, especially if they involve downloading files.

### 7.3 For market surveillance

1. **Monitor multisig ownership changes**: Track ownership-transfer and administrative transactions on high-TVL DeFi protocols. Alert on unexpected ownership changes or parameter modifications.

2. **Watch for coordinated cross-chain drains**: Detect simultaneous large withdrawals across multiple chain deployments of the same protocol.

3. **Track DPRK-linked laundering patterns**: Monitor addresses associated with known DPRK laundering infrastructure for new inflows that may indicate fresh exploits.

## 8. Conclusion

The Radiant Capital exploit of October 2024 demonstrated the evolving sophistication of attacks targeting DeFi protocol governance infrastructure. By socially engineering access to multisig signer environments and manipulating the transaction-signing workflow, the attacker — attributed by Mandiant to a DPRK-linked threat group — compromised a 3-of-11 multisig control path and drained approximately $53 million across Arbitrum and BNB Chain deployments.

The incident underscored that DeFi protocol security extends far beyond smart-contract correctness. The human and operational security of multisig signers — their device hygiene, their ability to verify transactions independently, and their resistance to social engineering — is the binding constraint on protocol security for any system that relies on multisig governance. For the broader market, the Radiant attack reinforced the need for higher multisig thresholds, dedicated signing environments, timelock protections, and industry-wide coordination against state-sponsored threat actors whose capabilities continue to advance.
