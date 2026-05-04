---
date: 2026-05-05
entities:
  - id: indodax
    name: Indodax
    type: exchange
  - id: slowmist
    name: SlowMist
    type: analytics
  - id: bappebti
    name: Bappebti
    type: regulatory
title: "Indodax hot-wallet compromise, $22 M multi-chain theft, and Indonesian exchange security gaps"
---

## 1. Introduction and incident overview

On 11 September 2024, Indonesia's largest cryptocurrency exchange by trading volume, Indodax (formerly Bitcoin.co.id), suffered a hot-wallet compromise that resulted in the theft of approximately $22 million in cryptocurrency. The stolen assets spanned multiple blockchains, including Ethereum, Bitcoin, Tron, Polygon, and Optimism. Indodax suspended all platform operations — including trading and withdrawals — while it investigated the breach and secured its remaining infrastructure.

The Indodax hack occurred within a broader wave of exchange compromises in mid-to-late 2024, following the WazirX breach ($230M+, July 2024) and preceding the BingX hack ($52M, September 2024) by just nine days. The clustering of these incidents raised questions about whether coordinated threat actors were targeting Asian-market exchanges specifically, and whether the regulatory and security maturity of exchanges in Southeast Asia lagged behind global standards.

## 2. Technical background

### 2.1 Indodax's market position

Indodax is Indonesia's oldest and largest cryptocurrency exchange, founded in 2014. The platform serves millions of registered users in Indonesia, a country where cryptocurrency adoption has grown rapidly despite evolving regulatory frameworks. Indodax is registered with Bappebti (the Commodity Futures Trading Regulatory Agency), Indonesia's commodities regulator, which oversees cryptocurrency trading platforms.

The exchange supports trading in hundreds of cryptocurrency pairs and maintains hot wallets across multiple blockchains to facilitate withdrawals. As with most centralized exchanges, the majority of user assets are held in cold storage, with hot wallets holding a smaller operational float.

### 2.2 Hot-wallet architecture

Indodax's hot-wallet infrastructure supported withdrawals across multiple chains, including Bitcoin, Ethereum, Tron, Polygon, Optimism, and several others. Each chain required its own hot-wallet address and corresponding private key. The specific key-management architecture — whether individual HSMs, a centralized signing service, or another mechanism — was not publicly disclosed.

The multi-chain hot-wallet design creates the same structural vulnerability seen in other exchange hacks: a compromise of the key-management layer can cascade across all supported chains, enabling the attacker to drain hot wallets on every network simultaneously.

## 3. Attack execution

### 3.1 Timeline

The unauthorized transfers began on 11 September 2024, with the first suspicious outflows detected by blockchain monitoring services. The stolen assets included:

- **Ethereum**: ETH and various ERC-20 tokens, including USDT.
- **Bitcoin**: BTC transferred from Indodax's Bitcoin hot wallet.
- **Tron**: TRX and TRC-20 tokens.
- **Polygon**: MATIC and Polygon-native tokens.
- **Optimism**: ETH and OP-chain tokens.
- **Other chains**: Smaller amounts from additional supported networks.

The total theft was estimated at approximately $22 million based on the value of assets at the time of the unauthorized transfers.

### 3.2 Attack vector

Indodax's public communications described the incident as a compromise of its "withdrawal system." The blockchain security firm SlowMist, which analyzed the attack, indicated that the attacker likely gained access to Indodax's hot-wallet signing infrastructure, enabling direct transfers from hot wallets to attacker-controlled addresses.

The specific root cause — whether the compromise originated from a server-level intrusion, compromised API credentials, a key-management system vulnerability, an insider threat, or another vector — was not publicly disclosed in detail. Indodax stated that it was cooperating with law enforcement and cybersecurity firms to investigate the breach.

### 3.3 Post-theft fund movement

After the theft, the attacker followed the now-standard playbook for exchange-hack laundering:

1. **Token-to-native swaps**: Stolen ERC-20 and other fungible tokens were swapped for ETH and other native chain assets through decentralized exchanges, particularly Uniswap and 1inch. This step was executed rapidly to convert freezable tokens (USDT, USDC) to non-freezable assets before issuers could deploy blacklist actions.

2. **Consolidation**: Funds were consolidated across chains into a smaller number of attacker-controlled addresses.

3. **Bridging**: Portions of the stolen funds were bridged between chains to add complexity to the tracing effort.

4. **Potential mixing**: Some funds appeared to be routed through addresses associated with privacy-enhancing protocols, though the full laundering path was not publicly detailed.

### 3.4 Tether freeze

Tether froze a portion of the stolen USDT at attacker-controlled addresses on Ethereum and Tron. The exact amount frozen was not publicly confirmed by Indodax, but blockchain analysts noted USDT blacklist transactions targeting addresses linked to the theft within hours of its detection.

## 4. Indodax's response

### 4.1 Operational suspension

Indodax suspended all trading and withdrawal operations immediately upon confirming the breach. The suspension affected all users on the platform, not just those whose wallets were directly compromised — because hot-wallet losses reduce the exchange's operational float and potentially its solvency margin.

### 4.2 User communication

Indodax communicated the incident through social media channels and the Indodax website. The exchange initially described the incident as "system maintenance" before confirming the security breach. This initial characterization drew criticism from users who argued that transparency should take precedence over reputational management during a security incident.

In subsequent communications, Indodax confirmed the breach, stated that user funds were safe (backed by the exchange's reserves), and provided updates on the timeline for resuming operations.

### 4.3 Resumption of operations

Indodax resumed trading and withdrawal operations within approximately one week of the incident, after implementing security upgrades to its wallet infrastructure. The exchange stated that all user balances would be honored in full, indicating that the $22 million loss was absorbed by the company's reserves rather than socialized across users.

### 4.4 Root-cause disclosure

As of early 2026, Indodax had not published a detailed technical post-mortem or root-cause analysis of the hot-wallet compromise. The lack of detailed disclosure is consistent with the broader pattern in centralized exchange incidents, where operational and legal considerations often override transparency.

## 5. Attribution considerations

### 5.1 Potential DPRK connection

Blockchain analytics firms noted behavioral similarities between the Indodax attack and operations attributed to North Korean threat actors:

- **Multi-chain simultaneous drain**: The attacker targeted hot wallets across multiple chains in a single operation, consistent with DPRK-linked campaigns that maximize extraction.
- **Rapid DEX swap pattern**: Immediate conversion of freezable tokens to native assets through DEXes matches the playbook observed in WazirX, BingX, and other 2024 exchange hacks attributed or suspected to be linked to DPRK actors.
- **Temporal clustering**: The Indodax hack occurred nine days before the BingX hack and two months after the WazirX hack, all of which shared similar attack patterns.

However, no official governmental attribution of the Indodax hack to DPRK-linked actors was publicly announced as of early 2026. The behavioral similarities are suggestive but insufficient for definitive attribution. Multiple threat actor groups have adopted similar multi-chain exploitation and DEX-laundering techniques.

## 6. Market-health implications

### 6.1 Southeast Asian exchange security maturity

The Indodax hack, combined with the WazirX breach earlier in 2024, highlighted concerns about the security maturity of cryptocurrency exchanges serving Southeast Asian markets. Both incidents involved hot-wallet compromises at major domestic exchanges, suggesting that the security infrastructure at these exchanges may not have kept pace with the increasing sophistication of threat actors targeting the cryptocurrency sector.

Factors that may contribute to a security gap include:

- **Rapid growth outpacing security investment**: Exchanges in fast-growing markets may prioritize feature development and user acquisition over security infrastructure investment.
- **Regulatory variability**: Cryptocurrency regulation in Southeast Asia varies significantly by jurisdiction, and some regulatory frameworks do not impose specific security requirements on exchange operators.
- **Talent and tooling access**: Security engineering talent and enterprise-grade security tooling may be less accessible in some markets compared to exchanges headquartered in the U.S., Europe, or Japan.

### 6.2 Initial communication and transparency

Indodax's initial characterization of the incident as "system maintenance" before confirming a security breach reflected a communication pattern that is common in the exchange industry but damaging to user trust. Users who were unable to withdraw their funds during the suspension were left uncertain about whether their assets were safe, and the delayed confirmation of a breach eroded confidence.

For market health, exchange incident-communication practices have implications for systemic stability: if users cannot trust that exchanges will disclose breaches promptly and honestly, the rational response is to minimize exchange exposure, which can reduce exchange liquidity and increase withdrawal pressure during periods of uncertainty.

### 6.3 Regulatory implications in Indonesia

The Indodax incident drew attention to Bappebti's oversight of cryptocurrency exchanges in Indonesia. While Bappebti had registered Indodax and other domestic exchanges, the regulatory framework's security requirements and incident-reporting obligations were not as detailed as those in some other jurisdictions (e.g., Japan's FSA, which imposed extensive security requirements on exchanges after the Coincheck hack in 2018).

The incident may contribute to the evolution of Indonesian cryptocurrency regulation toward more prescriptive security requirements for exchange operators, including:

- Mandatory security audits by independent firms.
- Incident-reporting timelines and disclosure requirements.
- Minimum custody-security standards (multisig, HSM usage, cold-storage ratios).
- User-compensation and insurance requirements.

### 6.4 Exchange-hack clustering in 2024

The WazirX–Indodax–BingX cluster of exchange hacks within a three-month period in 2024 raised systemic concerns:

| Exchange | Date | Amount | Region |
|---|---|---|---|
| WazirX | July 2024 | ~$230M | India |
| Indodax | Sept 11, 2024 | ~$22M | Indonesia |
| BingX | Sept 20, 2024 | ~$52M | Singapore |

Whether these incidents were conducted by the same threat actor, by related actors sharing tools and techniques, or by independent actors exploiting similar vulnerabilities is not definitively established. However, the clustering suggests either a coordinated campaign targeting Asian-market exchanges or a convergence of exploit techniques that makes exchanges in this region particularly vulnerable during this period.

For market surveillance, exchange-hack clustering patterns should be treated as a risk signal: when one exchange in a region or category is compromised, other exchanges with similar architectures and security profiles should be assessed for elevated risk.

## 7. Lessons learned and recommendations

### 7.1 For exchanges

1. **Transparent breach communication**: Describe incidents accurately from the first public statement. Characterizing a security breach as "maintenance" delays user decision-making and erodes trust.

2. **Hot-wallet minimization**: Reduce hot-wallet balances across all chains to the minimum needed for expected withdrawal volume. Automated, rate-limited cold-to-hot replenishment should be the standard.

3. **Key-management segmentation**: Separate key-management infrastructure by chain to limit the blast radius of a single compromise. Avoid shared signing servers or API credentials across chains.

4. **Real-time monitoring with automated response**: Implement monitoring that detects unusual outflows within minutes and automatically suspends withdrawals when thresholds are breached. The goal is to minimize the exploitation window.

5. **Publish post-mortem analyses**: Detailed root-cause disclosure enables the industry to learn from incidents. Exchanges should publish post-mortems within a reasonable timeframe, with sensitive details redacted as needed.

### 7.2 For regulators

1. **Prescriptive security requirements**: Move beyond registration-only frameworks to impose specific security standards on exchange operators, including cold-storage ratios, multisig or MPC custody requirements, and incident-reporting timelines.

2. **Independent security audits**: Require periodic independent security audits of exchange custody and key-management infrastructure.

3. **Regional coordination**: Given the clustering of exchange hacks targeting Asian-market exchanges, regional regulatory coordination on security standards and threat intelligence sharing could raise the baseline security level.

### 7.3 For users

1. **Self-custody for significant holdings**: The recurring pattern of exchange hot-wallet compromises reinforces the case for moving significant holdings to personal hardware wallets.

2. **Assess exchange communication practices**: Exchanges that are transparent about incidents, publish proof of reserves, and provide detailed post-mortems demonstrate a higher commitment to user trust.

## 8. Conclusion

The Indodax hot-wallet compromise of September 2024 resulted in the theft of approximately $22 million in cryptocurrency across multiple blockchains. The incident demonstrated the continued vulnerability of centralized exchange hot-wallet infrastructure to key-management compromises, and its timing — within a cluster of exchange hacks targeting Asian-market platforms in 2024 — raised questions about the security maturity of exchanges in the region and the potential for coordinated threat-actor campaigns.

Indodax's response — including a delayed breach confirmation, full user-loss coverage from reserves, and operational resumption within approximately one week — illustrated both the strengths (user compensation) and weaknesses (communication opacity, no root-cause disclosure) of the centralized exchange incident-response model. For the broader market, the Indodax case contributes to the growing evidence that exchange security must be assessed not only at the protocol level but also at the organizational, regulatory, and regional levels, with particular attention to the multi-chain attack surface that makes modern exchange hot-wallet infrastructure increasingly difficult to defend.
