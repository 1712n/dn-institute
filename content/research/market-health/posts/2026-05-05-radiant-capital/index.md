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

On 16 October 2024, the cross-chain lending protocol Radiant Capital suffered a coordinated attack that drained approximately $53 million in user funds from its deployments on Arbitrum and BNB Chain. The attacker compromised multiple private keys belonging to signers of Radiant's multisig wallet, gaining sufficient control to execute ownership-transfer transactions that redirected protocol funds. The incident was notable for the sophistication of the initial compromise vector — the signers' devices were infected with malware through a social-engineering campaign — and for the cross-chain scope of the resulting drain.

Radiant Capital had engaged the incident-response firm Mandiant to investigate the breach. Mandiant's analysis, along with statements from the FBI and other agencies, attributed the attack with high confidence to a North Korean threat actor tracked as UNC4736 (also known as AppleJeus/Citrine Sleet), associated with the DPRK's Reconnaissance General Bureau. The attack followed the pattern of DPRK-linked cryptocurrency thefts that have targeted DeFi protocols with increasing frequency and sophistication since 2022.

## 2. Technical background

### 2.1 Radiant Capital's architecture

Radiant Capital is a cross-chain lending protocol built on LayerZero's omnichain messaging infrastructure. It allows users to deposit assets on one chain and borrow against them on another. At the time of the exploit, Radiant had active deployments on Arbitrum (Ethereum Layer 2), BNB Chain, and Ethereum mainnet, with approximately $75 million in total value locked across all deployments.

The protocol's smart contracts were upgradeable, with administrative functions — including the ability to transfer ownership of lending pools and modify contract parameters — controlled by a multisig wallet. The multisig required 3-of-11 signatures to execute transactions, meaning that any party who controlled three signer keys could unilaterally execute administrative actions.

### 2.2 Multisig security model

A 3-of-11 multisig provides a relatively low threshold relative to the total number of signers. While 11 signers distribute access broadly, requiring only 3 signatures means an attacker needs to compromise only 27% of the signer set to gain full control. Industry best practice for high-value DeFi protocols typically recommends higher thresholds (e.g., 5-of-9 or 7-of-11) to increase the number of signers an attacker must compromise.

The security of the multisig ultimately depends on the security of each individual signer's private key and the device on which it is stored. If signers use hardware wallets (Ledger, Trezor) with air-gapped signing, the attack surface is limited to physical device compromise or supply-chain attacks on the hardware wallet firmware. If signers use software wallets on internet-connected devices, the attack surface expands to include malware, phishing, and remote-access exploits on those devices.

### 2.3 Safe (Gnosis Safe) multisig workflow

Radiant's multisig was implemented using Safe (formerly Gnosis Safe), the most widely used multisig framework in the Ethereum ecosystem. In the standard Safe workflow, one signer proposes a transaction through the Safe web interface, and other signers review and co-sign the transaction in the Safe UI. The transaction is displayed to each signer as a set of parameters (target contract, function call, value), and the signer's wallet signs the transaction data.

A critical aspect of this workflow is that signers rely on the Safe UI and their wallet's transaction-display capabilities to understand what they are signing. If an attacker can manipulate the transaction data displayed to signers — either by compromising the Safe frontend, intercepting the transaction at the device level, or replacing the legitimate transaction with a malicious one — signers may unknowingly approve a transaction that differs from what they intended.

## 3. Attack execution

### 3.1 Social-engineering and device compromise

According to Mandiant's investigation, the attack began with a social-engineering campaign targeting Radiant Capital team members. On approximately 11 September 2024, a Radiant developer received a Telegram message from what appeared to be a former contractor. The message requested feedback on a purported new project and included a link to a zipped PDF document. When the developer opened the file, it executed malware that established persistent access on the developer's device.

The malware, identified by Mandiant as consistent with DPRK-linked tooling, subsequently spread to or was independently deployed on the devices of at least two additional multisig signers. The specifics of how additional signers were compromised — whether through lateral movement within Radiant's communications infrastructure, separate social-engineering messages, or other vectors — were not fully detailed in public disclosures.

### 3.2 Transaction manipulation

With malware present on at least three signers' devices, the attacker was positioned to manipulate the signing workflow. According to Radiant's post-mortem, the attack exploited the gap between what signers saw in their Safe UI and what was actually submitted on-chain:

- When a legitimate routine transaction was proposed through the Safe workflow (such as a regular emissions adjustment), the malware on infected devices intercepted the transaction data.
- The signers' Safe frontends displayed the expected legitimate transaction, but the actual transaction data submitted to the blockchain was replaced with a malicious `transferOwnership` call.
- Each compromised signer believed they were approving a routine operational transaction but was actually signing an ownership-transfer transaction.

This attack vector — sometimes called "blind signing" exploitation — takes advantage of the fact that most wallet interfaces display a simplified representation of complex contract interactions, and users cannot easily verify the raw calldata against the displayed description. Even hardware wallets, which display transaction details on their screens, typically show only basic information (target address, value) rather than decoded function calls for arbitrary contract interactions.

### 3.3 Ownership transfer and fund drain

Once the attacker obtained three valid signatures on the malicious `transferOwnership` transaction, they submitted it to the blockchain. The transaction transferred ownership of Radiant's lending pool contracts on both Arbitrum and BNB Chain to an attacker-controlled address.

With ownership of the lending pools, the attacker called administrative functions to drain all deposited assets. The drain proceeded rapidly across both chains:

- **Arbitrum**: Approximately $32 million in various assets (USDC, USDT, WBTC, WETH, ARB) was drained from Radiant's Arbitrum lending pools.
- **BNB Chain**: Approximately $21 million in assets (USDC, USDT, WBNB, ETH) was drained from BNB Chain pools.

The total extraction was approximately $53 million across both chains.

### 3.4 Post-drain fund movement

The attacker moved the stolen funds through standard laundering patterns associated with DPRK-linked operations:

1. **Token consolidation**: Diverse stolen tokens were swapped to ETH and BNB via decentralized exchanges.
2. **Cross-chain bridging**: Funds were bridged between chains to complicate tracing.
3. **Mixer and privacy tool usage**: Portions were routed through mixing services and privacy protocols.
4. **Staged withdrawal**: Rather than liquidating immediately, the attacker staged funds across multiple addresses, consistent with DPRK laundering patterns that prioritize extraction security over speed.

## 4. Attribution and investigation

### 4.1 Mandiant analysis

Radiant Capital engaged Mandiant (now part of Google Cloud) to conduct the incident investigation. Mandiant's analysis attributed the attack to UNC4736, a threat cluster associated with the DPRK's Reconnaissance General Bureau. The attribution was based on:

- **Malware signatures**: The malware deployed on compromised devices matched known DPRK tooling families previously used in cryptocurrency-targeting operations.
- **Operational patterns**: The social-engineering approach (Telegram-based initial contact, zipped file delivery, contractor impersonation) matched established DPRK tradecraft documented in prior incidents.
- **Laundering behavior**: Post-drain fund movement patterns were consistent with Lazarus Group / DPRK-linked laundering infrastructure.

### 4.2 FBI and interagency involvement

The FBI, in coordination with other U.S. agencies, confirmed the DPRK attribution. The Radiant Capital attack was included in broader advisories about DPRK cyber operations targeting cryptocurrency infrastructure, alongside the Atomic Wallet, Harmony Horizon, and other attributed incidents.

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

1. **Increased multisig threshold**: The signing threshold was increased to reduce the number of signers needed to be compromised for a successful attack.
2. **Hardware wallet enforcement**: All multisig signers were required to use hardware wallets with fresh, dedicated devices.
3. **Transaction verification**: Additional verification steps were implemented to cross-check proposed transactions against expected behavior before signing.
4. **Timelock implementation**: Administrative functions were placed behind a timelock, introducing a delay between transaction proposal and execution that would allow the community to detect and respond to unauthorized transactions.
5. **Independent signature verification**: Signers were instructed to verify transaction calldata through independent channels rather than relying solely on the Safe UI.

### 5.4 Fund recovery efforts

Radiant stated that it was working with law enforcement and blockchain analytics firms to trace and potentially recover stolen funds. Given the DPRK attribution, significant recovery was considered unlikely — DPRK-linked groups have historically been highly effective at laundering stolen cryptocurrency through mixers, OTC desks, and decentralized exchanges, and diplomatic channels for asset recovery with North Korea are effectively nonexistent.

## 6. Market-health implications

### 6.1 Multisig threshold as a critical security parameter

The Radiant incident demonstrated that multisig security is only as strong as its weakest links — in this case, the individual signers' operational security. A 3-of-11 threshold meant the attacker needed to compromise only three devices to gain full protocol control. For a protocol managing $75 million in user funds, this represented a disproportionate concentration of risk.

The incident accelerated an industry discussion about appropriate multisig parameters:

- **Higher thresholds**: Requiring a majority (e.g., 6-of-11 or 7-of-11) of signers makes device-level compromise attacks significantly harder, as the attacker must successfully compromise more targets.
- **Signer diversity**: Distributing signers across different organizations, geographies, and device types reduces the probability that a single social-engineering campaign can reach enough signers.
- **Operational separation**: Requiring signers to use dedicated, air-gapped devices for signing operations limits the attack surface to physical access rather than remote malware.

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

Radiant's cross-chain architecture meant that a single ownership compromise cascaded across multiple chains simultaneously. The attacker drained both Arbitrum and BNB Chain deployments using the same compromised multisig, extracting $53 million rather than being limited to a single chain's liquidity.

For cross-chain protocols, this implies that the multisig (or governance mechanism) that controls administrative functions across all chain deployments is a single point of failure for the entire protocol. Chain-specific controls, independent multisigs per deployment, or chain-specific timelocks could limit the blast radius of a single compromise.

### 6.5 DPRK threat escalation

The Radiant attack contributes to a growing body of evidence that DPRK-linked groups are adapting their techniques to target increasingly sophisticated DeFi infrastructure. The progression from exchange hacks (2018–2020) to bridge attacks (2022) to social-engineering-based multisig compromises (2024) demonstrates operational learning and adaptation.

For the market as a whole, DPRK-sponsored theft represents a persistent, well-resourced threat that cannot be addressed through protocol-level security alone. Industry-wide coordination — including threat intelligence sharing, security standards for key management, and employee security training — is necessary to raise the cost of these attacks.

## 7. Lessons learned and recommendations

### 7.1 For DeFi protocols with multisig governance

1. **Set appropriate thresholds**: The multisig threshold should reflect the value under management. For protocols managing tens of millions or more, a majority threshold (>50% of signers) is appropriate.

2. **Enforce hardware wallet usage**: All multisig signers should use hardware wallets on dedicated devices not used for general communication, web browsing, or document handling.

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

The Radiant Capital exploit of October 2024 demonstrated the evolving sophistication of attacks targeting DeFi protocol governance infrastructure. By socially engineering access to multiple multisig signers' devices and manipulating the transaction-signing workflow, the attacker — attributed to a DPRK-linked threat group — compromised a 3-of-11 multisig and drained approximately $53 million across Arbitrum and BNB Chain deployments.

The incident underscored that DeFi protocol security extends far beyond smart-contract correctness. The human and operational security of multisig signers — their device hygiene, their ability to verify transactions independently, and their resistance to social engineering — is the binding constraint on protocol security for any system that relies on multisig governance. For the broader market, the Radiant attack reinforced the need for higher multisig thresholds, hardware-wallet enforcement, timelock protections, and industry-wide coordination against state-sponsored threat actors whose capabilities continue to advance.
