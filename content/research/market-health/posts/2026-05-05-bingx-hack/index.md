---
date: 2026-05-05
entities:
  - id: bingx
    name: BingX
    type: exchange
  - id: lazarus-group
    name: Lazarus Group
    type: threat-actor
  - id: tether
    name: Tether
    type: stablecoin-issuer
title: "BingX hot-wallet breach, $52 M multi-chain theft, and exchange incident-response case study"
---

## 1. Introduction and incident overview

On 20 September 2024, the Singapore-based cryptocurrency exchange BingX disclosed that its hot wallets had been compromised, resulting in the theft of approximately $52 million in cryptocurrency across multiple blockchains. The stolen assets spanned Ethereum, BNB Chain, Polygon, Arbitrum, Optimism, Base, Avalanche, and other EVM-compatible networks. BingX detected the unauthorized outflows through its risk-management monitoring system and suspended withdrawals within approximately one hour of the first detected unauthorized transfers.

The incident was notable for three reasons: the multi-chain breadth of the theft (affecting hot wallets across at least eight networks), the exchange's relatively rapid detection and public acknowledgment, and the attacker's use of decentralized exchanges to swap stolen tokens to native chain assets before the exchange could coordinate freeze responses. BingX committed to covering all user losses from its own reserves and resumed normal operations within several days.

## 2. Technical background

### 2.1 BingX's wallet architecture

BingX, like most centralized exchanges, maintained a tiered wallet architecture separating hot wallets (internet-connected, used for routine withdrawals) from cold storage (offline, holding the majority of assets). The exchange operated hot wallets on multiple EVM-compatible blockchains to support its multi-chain trading and withdrawal infrastructure.

The multi-chain hot-wallet architecture required BingX to manage private keys for hot wallets on each supported network. The security of this architecture depended on the isolation and protection of each chain's hot-wallet keys, as well as the monitoring systems that detect unauthorized outflows.

### 2.2 Multi-chain EVM hot-wallet exposure

The proliferation of EVM-compatible Layer 1 and Layer 2 networks (Ethereum, BNB Chain, Polygon, Arbitrum, Optimism, Base, Avalanche, and others) has expanded the attack surface for centralized exchanges. Each additional chain requires its own hot-wallet address and private key, and a compromise of the key-management system can cascade across all supported chains simultaneously. This is the same structural risk demonstrated in the KuCoin hack of 2020, now amplified by the growth of the multi-chain ecosystem.

## 3. Attack execution

### 3.1 Initial detection and timeline

On 20 September 2024, BingX's risk-management team detected unusual outflows from its hot wallets at approximately 04:00 UTC. The unauthorized transfers had begun shortly before detection, with the attacker executing withdrawals from hot wallets across multiple chains in rapid succession.

BingX suspended all withdrawals at approximately 05:00 UTC — roughly one hour after the first detected unauthorized transfer. The exchange published a public notification via social media shortly thereafter, acknowledging "abnormal network access" and confirming the withdrawal suspension.

### 3.2 Multi-chain drain pattern

The attacker drained hot wallets across at least eight blockchain networks:

- **Ethereum**: ETH and various ERC-20 tokens.
- **BNB Chain**: BNB and BEP-20 tokens.
- **Polygon**: MATIC and associated tokens.
- **Arbitrum**: ETH and ARB-chain tokens.
- **Optimism**: ETH and OP-chain tokens.
- **Base**: ETH and Base-chain tokens.
- **Avalanche**: AVAX and associated tokens.
- **Additional chains**: Smaller amounts from other supported networks.

The simultaneous multi-chain drain pattern suggested that the attacker had compromised a centralized key-management system or signing infrastructure rather than individual chain-specific wallets, enabling rapid, automated sweeps across all supported networks.

### 3.3 Immediate token swaps

Following the established pattern seen in other exchange hacks (notably KuCoin 2020), the attacker immediately began swapping stolen ERC-20 and other tokens for native chain assets (ETH, BNB, MATIC, etc.) through decentralized exchanges. This step was taken to convert freezable tokens (centralized stablecoins like USDT and USDC, as well as tokens with admin-controlled blacklist functions) into non-freezable native assets before token issuers could respond.

Blockchain analytics firms tracking the attack in real time observed rapid swaps through Uniswap, PancakeSwap, and other DEXes across multiple chains. The speed of these conversions — executed within minutes of the initial theft — reflected the attacker's awareness of the centralized freeze capabilities available to stablecoin issuers and their urgency to convert before those capabilities were deployed.

### 3.4 Fund consolidation

After converting stolen tokens to native chain assets, the attacker consolidated funds across chains. Portions of the stolen funds were bridged between networks and aggregated into a smaller number of addresses. The consolidation pattern was consistent with preparation for further laundering through mixers, cross-chain bridges, or OTC channels.

## 4. BingX's response

### 4.1 Detection and suspension

BingX's detection of the unauthorized transfers within approximately one hour represented a faster response time than many historical exchange hacks. The exchange's risk-management monitoring system flagged the unusual outflow patterns, triggering the withdrawal suspension.

However, the one-hour window was sufficient for the attacker to execute the multi-chain drain and begin token swaps. The challenge of real-time detection in a multi-chain environment is that monitoring must cover all supported networks simultaneously, and the latency between unauthorized transfer and detection creates an irreducible exploitation window.

### 4.2 Public communication

BingX's initial public statement described the incident as "minor asset losses" and emphasized that the majority of user assets were in cold storage. The exchange was criticized for the "minor" characterization, as $52 million is significant in absolute terms, though it may have represented a small percentage of BingX's total assets under management.

In subsequent communications, BingX provided more detailed information about the incident and confirmed its commitment to full user-loss coverage.

### 4.3 User compensation

BingX stated that all user losses would be covered from the exchange's own reserves. The exchange did not disclose specific details about its insurance fund or reserve structure, but committed to making affected users whole. Withdrawals were resumed within several days of the incident.

### 4.4 Root-cause disclosure

BingX did not publish a detailed technical post-mortem or root-cause analysis of the hot-wallet compromise. The specific mechanism by which the attacker obtained access to hot-wallet private keys — whether through a server compromise, key-management system vulnerability, insider access, or other vector — was not publicly disclosed as of early 2026.

This opacity is common in exchange security incidents but limits the industry's ability to learn from the breach and assess whether similar vulnerabilities exist at other exchanges.

## 5. Attribution considerations

### 5.1 Lazarus Group pattern

Blockchain analytics firms noted similarities between the BingX attack pattern and operations attributed to North Korea's Lazarus Group:

- **Multi-chain simultaneous drain**: Targeting all available chains in a single operation to maximize extraction before response.
- **Rapid DEX swaps**: Immediately converting freezable tokens to non-freezable native assets.
- **Consolidation and bridging patterns**: Moving funds through cross-chain bridges and aggregation addresses consistent with known DPRK laundering infrastructure.

However, no official governmental attribution of the BingX hack to Lazarus Group or DPRK-linked actors was publicly announced as of early 2026. The behavioral similarities are suggestive but not dispositive, as the multi-chain drain and DEX-swap pattern has been adopted by multiple threat actors, not exclusively DPRK-linked groups.

### 5.2 Broader threat landscape

The BingX hack occurred in a period of intensified exchange-targeting activity in September 2024, coinciding with the Indodax hack ($22M, also September 2024) and following closely after the WazirX breach ($230M+, July 2024). This clustering of exchange hacks within a short period may reflect coordinated campaigns by one or more threat actors, or it may reflect the broader expansion of the multi-chain attack surface that has made exchange hot wallets more vulnerable.

## 6. Market-health implications

### 6.1 Multi-chain attack surface expansion

The BingX incident demonstrated that the proliferation of EVM-compatible networks has expanded the attack surface for centralized exchanges in a way that is difficult to defend against. Each additional supported chain adds:

- Another hot-wallet address to fund and monitor.
- Another private key to manage and protect.
- Another network to monitor for unauthorized outflows.
- Another set of DEXes through which stolen funds can be laundered.

For exchange operators, this creates a scaling challenge: security costs and operational complexity grow with each additional supported chain, but competitive pressure and user demand drive exchanges to support as many chains as possible.

### 6.2 The DEX swap race

The BingX attack, like KuCoin before it, highlighted the race condition between attacker DEX swaps and centralized freeze responses. The attacker's ability to convert freezable tokens (USDT, USDC, project tokens with admin controls) to non-freezable native assets (ETH, BNB) within minutes of the theft undermines the effectiveness of centralized freeze capabilities.

Potential mitigations for this race condition include:

- **Faster detection and freeze coordination**: Reducing the time between theft detection and centralized freeze deployment, potentially through automated alert-and-freeze protocols between exchanges and stablecoin issuers.
- **On-chain monitoring services**: Third-party monitoring services that detect large, unusual outflows from exchange hot wallets in real time and automatically notify relevant parties.
- **DEX-level cooperation**: Although controversial from a decentralization perspective, some proposals have suggested that major DEX frontends could implement screening of addresses flagged in real-time theft alerts, though this would not prevent interaction with DEX contracts directly.

### 6.3 Exchange transparency deficit

BingX's decision not to publish a detailed root-cause analysis is typical of the cryptocurrency exchange industry but problematic for market health. Without understanding how hot-wallet keys were compromised, the broader industry cannot assess whether similar vulnerabilities exist at other exchanges, and users cannot make informed decisions about which exchanges to trust.

The transparency deficit is partly driven by legal and competitive concerns (exchanges may fear that disclosing vulnerabilities invites further attacks or undermines user confidence) but comes at the cost of systemic learning. The contrast with DeFi protocols — which typically publish detailed post-mortems, given the public nature of their smart-contract code — highlights an area where centralized exchange practices lag.

### 6.4 User-loss coverage and reserve adequacy

BingX's ability to cover user losses from its own reserves, without disclosing reserve details, illustrates the "trust me" model of exchange solvency. Users relied on BingX's representation that it had sufficient reserves, without independent verification. The development of proof-of-reserves practices in the wake of FTX's collapse has improved transparency at some exchanges, but adoption remains uneven, and many exchanges (including BingX at the time) did not publish regular proof-of-reserves attestations.

## 7. Comparative context

The BingX hack falls within a cluster of exchange hot-wallet compromises in 2024:

| Exchange | Date | Amount stolen | Chains affected | Attribution |
|---|---|---|---|---|
| WazirX | July 2024 | ~$230M | Ethereum | Lazarus Group (attributed) |
| BingX | Sept 2024 | ~$52M | 8+ EVM chains | Unconfirmed (Lazarus pattern) |
| Indodax | Sept 2024 | ~$22M | Multi-chain | Unconfirmed |

The clustering of these incidents within a two-month period raises questions about whether the attacks were conducted by the same threat actor or reflected a broader trend of increased exchange targeting during this period.

## 8. Lessons learned and recommendations

### 8.1 For exchanges

1. **Segment hot-wallet infrastructure by chain**: Use separate key-management systems, servers, or HSMs for each chain's hot wallet. A compromise of one chain's infrastructure should not cascade to others.

2. **Minimize hot-wallet balances**: Implement automated, rate-limited cold-to-hot replenishment. The hot-wallet balance on each chain should be the minimum needed for expected withdrawal volume.

3. **Reduce detection latency**: Invest in real-time monitoring across all supported chains, with automated alerts for outflows exceeding expected parameters. The goal should be detection within minutes, not hours.

4. **Pre-arrange freeze coordination**: Establish direct communication channels with stablecoin issuers (Tether, Circle) and major token projects for emergency freeze requests. Minutes matter in the DEX swap race.

5. **Publish root-cause post-mortems**: Detailed technical disclosure — even with sensitive details redacted — enables the industry to learn from incidents and assess systemic risks.

### 8.2 For users

1. **Minimize exchange holdings**: Hold only the assets needed for active trading on exchanges. Move long-term holdings to personal hardware wallets.

2. **Evaluate exchange transparency**: Prefer exchanges that publish proof-of-reserves attestations and have a track record of transparent incident disclosure.

3. **Diversify exchange exposure**: Avoid concentrating all exchange-based assets on a single platform. Splitting holdings across multiple exchanges limits the impact of any single breach.

### 8.3 For market surveillance

1. **Monitor multi-chain hot-wallet outflows**: Track known exchange hot-wallet addresses across all supported chains. Flag simultaneous outflows from the same exchange on multiple chains.

2. **Track rapid DEX swap patterns**: Detect large, sudden token-to-native-asset swaps on DEXes from addresses that were recently funded from known exchange hot wallets.

3. **Cluster analysis for coordinated campaigns**: When multiple exchange hacks occur within a short period, analyze whether on-chain behavior patterns (laundering infrastructure, timing, target selection) suggest a common threat actor.

## 9. Conclusion

The BingX hot-wallet breach of September 2024 demonstrated the expanded attack surface created by the multi-chain EVM ecosystem and the persistent challenge of the DEX swap race — the window between theft and centralized freeze response during which attackers convert freezable tokens to non-freezable native assets. The $52 million theft across at least eight blockchain networks was detected within approximately one hour, and BingX committed to full user-loss coverage from its reserves.

The incident's market-health implications center on the scaling challenge of multi-chain security for centralized exchanges, the transparency deficit in exchange incident disclosure, and the ongoing race between attacker speed and industry response coordination. As the number of supported chains continues to grow, exchange operators face increasing pressure to segment their hot-wallet infrastructure, minimize exposure on each chain, and reduce detection latency to limit the irreducible exploitation window that multi-chain architectures create.
