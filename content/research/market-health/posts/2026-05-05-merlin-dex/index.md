---
date: 2026-05-05
entities:
  - id: merlin-dex
    name: Merlin DEX
    type: defi-protocol
  - id: zksync-era
    name: zkSync Era
    type: blockchain
  - id: certik
    name: CertiK
    type: security-firm
title: "Merlin DEX rug pull on zkSync Era: privileged back-door drain and the limits of audit certification"
---

## Introduction

Merlin DEX was a decentralized exchange launched on zkSync Era, a zero-knowledge rollup (zk-rollup) scaling solution for Ethereum that went live on mainnet in March 2023. Positioned as an early mover in the zkSync DeFi ecosystem, Merlin DEX offered automated market maker (AMM) functionality for token swaps and liquidity provision, attracting users who wanted to participate in the emerging zkSync ecosystem during its early high-growth phase. The project had undergone a security audit by CertiK, one of the most prominent blockchain security auditing firms, and displayed the CertiK audit badge on its website and marketing materials as a signal of trustworthiness.

On April 25, 2023, approximately two days after the protocol's public launch and initial liquidity event, the Merlin DEX team executed a rug pull — a deliberate insider theft — draining approximately $1.82 million from the protocol's liquidity pools. The drain was facilitated by a privileged function in the smart contract that allowed addresses with a specific admin role to withdraw all tokens from the liquidity pools without going through the standard withdrawal process. This back-door function had been identified during the CertiK audit as a centralization risk, but the finding was classified as informational rather than critical, and the Merlin team had acknowledged but not addressed it before launch.

The Merlin DEX rug pull became a landmark incident not because of its size — $1.82 million was modest by DeFi rug pull standards — but because it occurred on a CertiK-audited protocol, forcing a public reckoning about the meaning, limitations, and potential misuse of security audit certifications in the DeFi industry.

## Background

### zkSync Era Launch and Early Ecosystem

zkSync Era, developed by Matter Labs, launched its mainnet alpha in March 2023 after a prolonged testnet period. The launch generated significant excitement in the Ethereum community because zkSync was one of the first general-purpose zk-rollups to support full EVM compatibility (via the zkEVM), promising Ethereum-level security with dramatically lower transaction costs. The prospect of a zkSync token airdrop (widely anticipated but not yet confirmed at the time) drove a rush of users and protocols to the network, creating a gold-rush atmosphere where new projects launched daily.

This environment was fertile ground for both legitimate projects and scams. Users eager to establish on-chain activity for a potential airdrop were willing to deposit funds into newly launched protocols with limited track records. The combination of high user demand, low barrier to protocol deployment, and limited due diligence created ideal conditions for rug pulls — projects designed from the outset to attract deposits and then steal them.

### CertiK Audit Ecosystem

CertiK had established itself as one of the largest blockchain security auditing firms by volume, having audited thousands of projects across multiple chains. The firm offered a range of audit services, from comprehensive smart contract reviews to more limited "quick audit" assessments. CertiK also operated a public "Skynet" platform that displayed audit results, security scores, and risk assessments for audited projects, which users and investors frequently consulted when evaluating DeFi protocols.

The CertiK audit badge had become a de facto trust signal in the DeFi industry — many users interpreted the presence of a CertiK audit as an endorsement of a protocol's safety and legitimacy. This interpretation significantly exceeded what a smart contract audit actually provides: a technical review of the code's behavior against its specification, which explicitly does not cover the intentions of the development team, the economic viability of the protocol, or the risk of intentional insider theft (rug pulls).

### Merlin DEX Pre-Launch

Merlin DEX launched with a standard AMM implementation on zkSync Era, allowing users to provide liquidity in paired token pools and earn trading fees. The protocol conducted a liquidity generation event (LGE) where users deposited tokens (primarily ETH and stablecoins) to bootstrap the initial liquidity pools. The LGE attracted approximately $1.82 million in deposits within the first 48 hours, driven in part by the general enthusiasm for zkSync ecosystem participation and the visible CertiK audit badge on the project's website.

The project's smart contracts were relatively simple — a standard Uniswap V2-style AMM with the addition of a farming rewards system for liquidity providers. However, the contracts included several privileged functions accessible only to addresses holding specific admin roles. These functions were standard for DeFi protocols that need operational flexibility (e.g., adjusting fee parameters, pausing the protocol in emergencies), but one particular function — the ability for the admin to directly transfer tokens from the liquidity pool contracts — went beyond normal operational requirements and constituted a back door.

## The Attack

### Privileged Withdrawal Function

The core mechanism of the rug pull was a function in the Merlin DEX liquidity pool contracts that allowed addresses with the contract's admin role to call a withdrawal function that bypassed the standard liquidity removal process. In a legitimate AMM, liquidity can only be removed by LP token holders who burn their LP tokens in proportion to their share of the pool. The admin withdrawal function in Merlin's contracts allowed the admin to transfer arbitrary amounts of any token held in the pool contracts without burning any LP tokens — effectively allowing the admin to drain the pools at will.

This function was not hidden in obfuscated code or implemented through a subtle backdoor — it was a straightforward `transferFrom` or `withdraw` function protected only by an access control modifier (e.g., `onlyOwner` or a role-based access control check). The function was visible in the contract source code and had been identified by CertiK during their audit.

### Execution

On April 25, 2023, approximately 48 hours after the LGE concluded and the initial liquidity pools were established, the Merlin DEX team executed the drain:

**Step 1: Admin access.** The team used the admin wallet (which held the privileged role on the pool contracts) to call the admin withdrawal function on each liquidity pool.

**Step 2: Pool drain.** The admin function transferred all tokens from the liquidity pool contracts to the admin wallet. This included ETH, USDC, and other tokens that users had deposited during the LGE and subsequent trading activity. The total extraction was approximately $1.82 million.

**Step 3: Token conversion.** The team converted the stolen tokens to ETH through various DEXes on zkSync Era and Ethereum mainnet. Portions of the funds were bridged from zkSync to Ethereum through the official bridge and third-party bridges.

**Step 4: Fund laundering.** The team moved the ETH through multiple intermediary wallets and eventually into mixing services (primarily Tornado Cash) to obfuscate the trail of funds. On-chain investigators tracked portions of the funds through these movements, but the mixing step made full recovery unlikely.

### Timeline

The entire rug pull was executed within minutes. From the first admin withdrawal transaction to the last pool being drained, the process took approximately 15 minutes. Users who noticed the TVL dropping to zero and attempted to withdraw their funds found that the pools were already empty. The speed of execution was enabled by the direct admin withdrawal function — no complex exploit or multi-step attack was required. The team simply called the function they had built into the contracts from the beginning.

## Impact

### Financial Losses

The direct financial impact was approximately $1.82 million in stolen tokens, distributed across all users who had deposited into Merlin DEX's liquidity pools. Losses were proportional to each user's deposit — those who had contributed more to the LGE or added liquidity after launch lost more. Because the pools were completely drained, every liquidity provider lost 100% of their deposited funds.

The Merlin token (MAGE) collapsed to zero following the rug pull, adding additional losses for users who had purchased the governance token on the open market. The total economic damage including MAGE token losses exceeded $2 million, though the exact figure depends on the timing and price at which MAGE holders purchased their tokens.

### Impact on CertiK's Credibility

The most significant and lasting impact of the Merlin DEX rug pull was on the credibility of CertiK's audit certifications. The fact that a CertiK-audited protocol had been designed as a rug pull from the beginning — with the drain function present in the audited code — raised fundamental questions about the value and interpretation of security audits.

CertiK's post-incident response revealed that their audit had indeed flagged the centralization risk associated with the admin withdrawal function. The finding was classified as "informational" or "centralization" rather than "critical" or "high," and the recommended mitigation was to implement a timelock or multi-sig for admin functions. The Merlin team had acknowledged the finding but stated they would address it post-launch — a commitment they obviously had no intention of fulfilling.

This disclosure sparked a broader debate about the audit industry's responsibility. Critics argued that CertiK should have classified the admin drain function as a critical risk (since it enabled complete fund theft), should have refused to issue an audit report or security score for a protocol with such an obvious back door, and should have clearly communicated to users that the audit did not assess the team's intentions or trustworthiness.

Defenders of CertiK argued that the firm correctly identified the centralization risk, that audits are explicitly scoped to technical code review rather than team trustworthiness assessment, and that users who interpreted a CertiK badge as a guarantee of safety were misunderstanding the purpose of audits.

### Impact on zkSync Ecosystem

The Merlin DEX rug pull was one of the earliest high-profile security incidents on zkSync Era, occurring within the first month of the network's mainnet launch. The incident raised concerns about the quality of projects deploying on the new network and the adequacy of user protections in the early-stage ecosystem.

The zkSync community and Matter Labs (the development team behind zkSync) responded by encouraging users to exercise greater caution when interacting with new protocols, and several community-driven initiatives emerged to provide additional due diligence resources beyond audit badges. However, the fundamental challenge remained: in a permissionless ecosystem, anyone could deploy contracts and attract users, and no amount of community warnings could fully prevent users from depositing into malicious protocols.

## Response and Remediation

### CertiK's Response

CertiK published a detailed response to the incident, confirming that their audit had identified the centralization risk and that the Merlin team had acknowledged but not resolved it. CertiK stated that their audit process was designed to identify technical vulnerabilities and centralization risks, not to assess the intentions of project teams. The firm noted that the centralization finding was visible on their Skynet platform for anyone who reviewed the full audit report.

CertiK also announced several improvements to their audit reporting and Skynet platform in response to the incident. These included more prominent display of centralization and privileged function warnings on project pages, a new "rug pull risk" indicator that would flag protocols with admin functions capable of draining user funds, enhanced post-audit monitoring that would alert the community if audited contracts were modified or if suspicious transactions were detected, and clearer communication about what audits do and do not cover, including explicit disclaimers that audits do not assess team trustworthiness.

### Community Response

The DeFi community's response was a mix of sympathy for affected users and frustration with the audit certification ecosystem. Security researchers published analyses demonstrating that Merlin DEX's admin drain function was visible in the contract code and could have been identified by any user who reviewed the contracts independently. This raised the question of user responsibility — in a decentralized ecosystem, should users rely on audit badges as a substitute for their own due diligence?

Several community members launched on-chain investigations to track the stolen funds, identifying intermediary wallets and flagging them on blockchain analytics platforms. While some funds were traced to centralized exchange deposits (where they could potentially be frozen by exchange compliance teams), the majority was routed through mixing services and remained unrecovered.

### No Recovery for Users

Unlike many DeFi exploits where the protocol team works to compensate affected users, the Merlin DEX rug pull was perpetrated by the team itself, leaving no entity with the motivation or resources to provide compensation. Users who lost funds had no recourse beyond pursuing legal action against the anonymous development team — a practically impossible task given the pseudonymous nature of DeFi project teams.

This outcome underscored a fundamental asymmetry in DeFi security: while technical exploits by external attackers are often partially remediable (through bug bounties, whitehat negotiations, or protocol treasury compensation), insider theft (rug pulls) by project teams is almost never recoverable because the perpetrators control the only resources that could fund compensation.

## Technical Analysis

### Privileged Function Patterns in DeFi Contracts

The admin withdrawal function in Merlin DEX's contracts represents one of the most direct rug pull mechanisms: a function that allows a privileged address to transfer tokens from the contract to an arbitrary destination. While the most blatant versions (a literal `rugPull` function) are easy to identify, the same capability can be disguised in several ways.

The most common patterns include the direct drain function, where a function protected by `onlyOwner` or similar modifiers calls `token.transfer(owner, balance)` to transfer all tokens; the proxy upgrade pattern, where the contract uses a transparent or UUPS proxy pattern and the admin can upgrade the implementation to a new contract that includes a drain function; the migration function pattern, where a function ostensibly designed for protocol migration allows the admin to move all funds to a new contract address that the admin controls; and the emergency withdrawal pattern, where a function designed for emergency situations (pausing the protocol and returning funds to a treasury address) can be abused if the treasury address is controlled by the team.

All of these patterns share a common characteristic: they give a single address (or small set of addresses) the unilateral ability to move user funds. In legitimate protocols, these functions are typically protected by timelocks (requiring a 24-48 hour delay between initiating and executing an admin action), multi-signature wallets (requiring multiple independent parties to approve the action), and governance votes (requiring token holder approval for admin actions).

Merlin DEX implemented none of these safeguards. The admin could call the drain function at any time, without delay, without multi-sig approval, and without governance oversight. This was the centralization risk that CertiK identified and the Merlin team declined to mitigate.

### Audit Scope and Limitations

Smart contract audits are technical code reviews, not comprehensive security assessments. A standard audit scope includes verifying that the contract's code correctly implements its specified behavior, identifying vulnerabilities that could allow external attackers to exploit the contract, flagging centralization risks where admin functions could be abused, reviewing access control implementations for correctness, and checking for common vulnerability patterns (reentrancy, integer overflow, etc.).

A standard audit scope does not include assessing whether the project team intends to use admin functions maliciously, evaluating the economic viability or sustainability of the protocol's tokenomics, verifying the identity or trustworthiness of the development team, monitoring post-audit contract deployments to ensure the audited code is actually deployed (rather than a modified version), or providing ongoing security monitoring of the deployed protocol.

This scope limitation means that a project can receive a clean audit (no critical or high-severity vulnerabilities in the code) while still being a designed rug pull — the code works exactly as intended, and the intention is theft. The Merlin DEX case demonstrated this gap clearly: the audit correctly identified that the code allowed the admin to drain funds, but the audit process did not (and was not designed to) assess whether the admin would do so.

### Rug Pull Detection Heuristics

The DeFi security community has developed several heuristics for identifying potential rug pulls before they occur. Key indicators include unrenounced contract ownership (the deployer retains admin control with no timelock or multi-sig), the presence of admin functions capable of draining user funds, anonymous development teams with no verifiable track record, recently deployed contracts with no prior testnet history, aggressive marketing focused on APY and returns rather than technical innovation, and liquidity pools where the team controls a majority of the LP tokens (enabling a liquidity rug where the team removes their liquidity, crashing the token price).

Merlin DEX exhibited several of these indicators: unrenounced ownership, admin drain functions, an anonymous team, and aggressive marketing of yield farming returns. However, many legitimate early-stage DeFi projects also exhibit some of these characteristics (particularly unrenounced ownership and anonymous teams), making it difficult to definitively identify rug pulls based on heuristics alone.

Tools like Token Sniffer, RugDoc, and GoPlus Security have automated some of these checks, providing quick risk assessments for new tokens and protocols. However, false positive rates remain high (many legitimate projects trigger alerts), and sophisticated rug pull teams can design contracts that pass automated checks while retaining the ability to drain funds through more subtle mechanisms.

### Post-Audit Contract Modification Risk

A related risk that the Merlin case highlighted (though it was not the specific mechanism used) is the possibility that a project deploys a different version of the contract than the one that was audited. If the audited code is secure but the deployed code contains additional admin functions or backdoors, the audit badge provides false assurance to users.

Some audit firms address this by including a "deployment verification" step where they confirm that the deployed bytecode matches the audited source code. CertiK's Skynet platform included this feature for some projects, but verification was not consistently applied across all audited protocols. The Merlin case reinforced the importance of deployment verification as a standard audit deliverable.

### Comparison with Other Rug Pulls

The Merlin DEX rug pull fits into a broader pattern of DeFi insider theft that peaked during 2021-2023. Notable comparisons include the Thodex exchange rug pull (April 2021, approximately $2 billion), where the Turkish crypto exchange's CEO absconded with user funds — a centralized exchange rug pull rather than a DeFi smart contract drain; the Squid Game Token rug pull (November 2021), where a meme token on BSC was designed with a sell-restriction mechanism that prevented holders from selling while the team drained the liquidity pool; and the AnubisDAO rug pull (October 2021, approximately $60 million), where the team conducted a liquidity bootstrapping auction and then drained the collected ETH through a multi-sig wallet they controlled.

The common thread across these incidents is that the theft mechanism was built into the protocol from the beginning — these were not exploits of unintentional vulnerabilities but deliberate designs by project insiders. This distinguishes rug pulls from the vast majority of DeFi exploits, where external attackers discover and exploit unintentional vulnerabilities.

## Lessons Learned

### Audits Are Not Endorsements

The most important lesson from the Merlin DEX rug pull is that a security audit is a technical code review, not an endorsement of a protocol's safety, legitimacy, or trustworthiness. Users must understand that an audit badge means "the code was reviewed for technical vulnerabilities," not "this protocol is safe to use." The DeFi industry has a collective responsibility to educate users about this distinction and to develop more comprehensive trust frameworks that go beyond code audits to include team verification, economic modeling, and ongoing monitoring.

### Centralization Risks Are Critical Risks

Audit firms should treat admin functions capable of draining user funds as critical-severity findings, not informational observations. The ability for a single address to steal all user funds is the highest possible risk in a DeFi protocol — it is more dangerous than any technical vulnerability because it requires no attacker ingenuity and has a 100% success rate. Audit reports should clearly flag these capabilities with the strongest possible warning language, and audit firms should consider withholding favorable security scores from protocols that retain unmitigated drain capabilities.

### Timelock and Multi-Sig as Minimum Standards

DeFi protocols that hold user funds should implement timelocks and multi-signature requirements on all admin functions as a baseline security standard. A 24-48 hour timelock on admin actions gives users time to withdraw funds if a malicious transaction is queued, effectively transforming an instant rug pull into a detectable and preventable threat. Multi-signature requirements ensure that no single party can unilaterally drain funds. Together, these measures do not eliminate the risk of insider theft but dramatically reduce it by introducing delays and requiring collusion.

### Due Diligence Beyond Audit Badges

Users should not rely solely on audit badges when evaluating DeFi protocols. A more comprehensive due diligence process includes reading the full audit report (not just the badge) to understand what risks were identified, checking whether identified risks (especially centralization risks) have been mitigated, verifying that the deployed contract matches the audited code, researching the development team's track record and public identity, starting with small deposits and increasing exposure only after the protocol has demonstrated stability over time, and monitoring on-chain activity for suspicious admin transactions.

## Conclusion

The Merlin DEX rug pull of April 25, 2023, resulted in the theft of approximately $1.82 million from liquidity providers on zkSync Era through a privileged admin withdrawal function that allowed the development team to drain all pool assets without restriction. The incident's significance extends far beyond its financial impact to the fundamental questions it raised about the DeFi audit certification ecosystem: a CertiK-audited protocol was designed as a rug pull from inception, with the drain function present in the audited code and flagged as a centralization risk in the audit report — yet the CertiK badge was presented to and interpreted by users as a signal of safety. The Merlin case demonstrated that the gap between what audits provide (technical code review) and what users expect (a guarantee of safety) represents one of the most significant unaddressed risks in the DeFi industry. Closing this gap requires concurrent action by audit firms (treating admin drain capabilities as critical findings), protocol developers (implementing timelocks and multi-sig as baseline standards), and users (conducting due diligence beyond audit badges). Until these systemic improvements are achieved, rug pulls will continue to exploit the trust gap that audit certifications inadvertently create.
