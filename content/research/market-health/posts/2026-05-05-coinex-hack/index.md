---
date: 2026-05-05
entities:
  - id: coinex
    name: CoinEx
    type: exchange
  - id: lazarus-group
    name: Lazarus Group
    type: threat-actor
  - id: fbi
    name: Federal Bureau of Investigation
    type: regulatory
  - id: tether
    name: Tether
    type: stablecoin-issuer
title: "CoinEx hot-wallet breach, $70 M multi-chain theft, and Lazarus Group attribution"
---

## 1. Introduction and incident overview

On 12 September 2023, the Hong Kong-based cryptocurrency exchange CoinEx disclosed that its hot wallets had been compromised, resulting in the theft of approximately $70 million in cryptocurrency across multiple blockchains. The stolen assets included ETH, BTC, TRON-based tokens, Polygon tokens, Solana tokens, and assets on several other networks. CoinEx detected the unauthorized outflows through its risk-control system and suspended deposit and withdrawal services shortly after the first unauthorized transfers.

The FBI subsequently attributed the CoinEx hack to North Korea's Lazarus Group (also tracked as TraderTraitor), linking it to a broader campaign of DPRK-sponsored cryptocurrency theft that included the Stake.com hack ($41M, also September 2023) and the Alphapo/CoinsPaid hacks (July 2023). The Lazarus Group attribution placed the CoinEx breach within a pattern of state-sponsored attacks targeting cryptocurrency exchanges and payment processors throughout 2023.

## 2. Technical background

### 2.1 CoinEx's market position

CoinEx is a cryptocurrency exchange that was founded in 2017 and is headquartered in Hong Kong. The exchange supports trading in hundreds of cryptocurrency pairs and serves a global user base. CoinEx operates both spot and derivatives markets and, like most centralized exchanges, maintains a multi-chain hot-wallet infrastructure to support withdrawals across the variety of blockchains it supports.

### 2.2 Hot-wallet architecture

CoinEx's hot wallets held assets on multiple blockchains, including Ethereum, Bitcoin, Tron, Polygon, Solana, BNB Chain, and others. Each chain's hot wallet required its own private key, and the security of the entire hot-wallet infrastructure depended on the protection of these keys and the monitoring systems that detect unauthorized outflows.

The specific key-management architecture — HSMs, key-management services, or software-based signing — was not publicly disclosed. CoinEx described the attack as a compromise of its hot-wallet private keys without providing technical detail on the attack vector.

## 3. Attack execution

### 3.1 Timeline

The unauthorized transfers began on 12 September 2023. CoinEx's risk-control system detected abnormal withdrawals from several hot-wallet addresses, prompting the exchange to suspend deposit and withdrawal services. The initial detection and suspension occurred within hours of the first unauthorized transfers.

### 3.2 Multi-chain drain

The attacker drained hot wallets across multiple blockchains simultaneously:

- **Ethereum**: Approximately $18.1 million in ETH and ERC-20 tokens.
- **Bitcoin**: Approximately $6.1 million in BTC.
- **Tron**: Approximately $11.5 million in TRX and TRC-20 tokens.
- **Polygon**: Tokens valued at several million dollars.
- **Solana**: SOL and SPL tokens.
- **BNB Chain, Bitcoin Cash, Ripple, and others**: Smaller amounts across additional chains.

The total theft was estimated at approximately $70 million based on asset values at the time of the unauthorized transfers.

### 3.3 Post-theft fund movement

The attacker followed established laundering patterns:

1. **Token-to-native swaps**: Stolen ERC-20 and other fungible tokens were rapidly swapped to ETH, BNB, and other native chain assets through Uniswap, PancakeSwap, and other DEXes. This step converted freezable tokens to non-freezable assets before issuers could respond.

2. **Consolidation**: Funds were moved to a smaller number of attacker-controlled addresses across multiple chains.

3. **Cross-chain bridging**: Portions of the stolen funds were bridged between chains to complicate tracing.

4. **Mixing and staging**: Consistent with DPRK-linked laundering patterns, the attacker staged funds across multiple addresses over time rather than immediately liquidating through centralized exchanges.

Blockchain analytics firm Elliptic and others tracked the fund flow and identified overlap with addresses and laundering infrastructure linked to prior Lazarus Group operations.

## 4. Attribution

### 4.1 FBI attribution

The FBI attributed the CoinEx hack to DPRK-linked cyber actors, specifically the group tracked as the Lazarus Group or TraderTraitor. The attribution was included in a broader advisory covering multiple DPRK cryptocurrency thefts in 2023.

The FBI's attribution was based on:

- **Shared laundering infrastructure**: Stolen CoinEx funds were traced to addresses and services previously associated with confirmed Lazarus Group operations.
- **Operational pattern consistency**: The multi-chain simultaneous drain, rapid DEX swap behavior, and staged laundering approach matched DPRK tradecraft observed in other 2023 attacks.
- **Temporal and target clustering**: The CoinEx hack occurred within days of the Stake.com hack ($41M) and within weeks of the Alphapo ($23M) and CoinsPaid ($37M) hacks — all attributed to the same DPRK threat cluster.

### 4.2 2023 DPRK campaign context

The CoinEx hack was part of a particularly active period of DPRK-linked cryptocurrency theft in 2023:

| Target | Date | Amount | Type |
|---|---|---|---|
| Alphapo | July 2023 | ~$23M | Payment processor |
| CoinsPaid | July 2023 | ~$37M | Payment processor |
| Stake.com | Sept 4, 2023 | ~$41M | Casino/exchange |
| CoinEx | Sept 12, 2023 | ~$70M | Exchange |

The clustering of these attacks within a two-month period suggested either a concentrated campaign by a single operational unit or coordinated operations by multiple DPRK-linked teams sharing tools, infrastructure, and intelligence. The total estimated DPRK-linked cryptocurrency theft in 2023 exceeded $600 million across all attributed incidents.

## 5. CoinEx's response

### 5.1 Detection and suspension

CoinEx detected the unauthorized transfers through its risk-control monitoring system and suspended deposit and withdrawal services. The detection occurred within hours of the first unauthorized outflows, which was faster than some historical exchange hacks but still provided sufficient time for the attacker to complete the multi-chain drain.

### 5.2 Public communication

CoinEx's initial public disclosure was relatively prompt, acknowledging the security incident and providing updates on the suspension and investigation. The exchange identified the affected hot-wallet addresses and published them to enable blockchain analytics firms and other exchanges to track and flag the stolen funds.

### 5.3 User compensation

CoinEx committed to fully compensating all affected users from its reserves and insurance fund. The exchange stated that user assets were "100% secure" and that the lost amount would be covered by the company. CoinEx did not disclose the specific size of its reserves or insurance fund.

### 5.4 Resumption of operations

CoinEx resumed deposit and withdrawal services in stages over the following weeks, starting with assets on chains where the hot-wallet infrastructure had been fully rebuilt and secured. The staged resumption reflected the complexity of rebuilding multi-chain hot-wallet infrastructure with new keys and security controls.

### 5.5 Root-cause disclosure

CoinEx attributed the breach to a compromise of its hot-wallet private keys but did not publish a detailed technical post-mortem or root-cause analysis. The specific attack vector — server compromise, key-management vulnerability, insider threat, social engineering, or other mechanism — was not publicly disclosed.

## 6. Market-health implications

### 6.1 DPRK threat escalation in 2023

The CoinEx hack, as part of the broader 2023 DPRK campaign, represented an escalation in both the pace and total value of state-sponsored cryptocurrency theft. The Lazarus Group's operational tempo in 2023 — multiple attacks per month targeting exchanges, payment processors, and DeFi protocols — demonstrated that DPRK cyber operations had industrialized their cryptocurrency-theft capabilities.

For market health, this escalation has several implications:

- **Systemic risk**: The aggregate value of DPRK-linked cryptocurrency theft is large enough to represent a material risk factor for the cryptocurrency market. The UN Panel of Experts estimated DPRK-linked cryptocurrency theft at approximately $1.7 billion in 2022 and potentially higher in 2023.

- **Insurance and reserve adequacy**: Exchanges must account for state-sponsored threat actors in their risk models. The probability and severity of a hot-wallet compromise is higher when the threat includes well-resourced state actors than when it includes only opportunistic criminals.

- **Regulatory pressure**: Each attributed DPRK theft strengthens the case for stricter exchange security requirements and sanctions compliance obligations, increasing the regulatory burden on the entire cryptocurrency industry.

### 6.2 Multi-chain attack surface

The CoinEx hack reinforced the structural vulnerability of centralized exchanges' multi-chain hot-wallet architectures. Each additional supported blockchain increases the number of private keys that must be managed and protected, and a compromise of the central key-management system cascades across all chains.

The progression of multi-chain exchange hacks — from KuCoin (2020, multi-chain) through CoinEx (2023, multi-chain) to BingX (2024, 8+ chains) — shows that the attack surface has grown as the number of supported chains has increased, but exchange key-management architectures have not uniformly kept pace with this expansion.

### 6.3 The DEX swap window

As with other exchange hacks, the CoinEx attacker used DEXes to rapidly swap stolen tokens for non-freezable native assets. The speed of this conversion — typically executed within minutes of the theft — continues to outpace the industry's ability to coordinate centralized freeze responses.

The structural challenge is that decentralized exchanges by design cannot implement the kind of address-screening, transaction-blocking, or fund-freezing capabilities that would close the DEX swap window. Proposals to address this tension include:

- **Faster freeze coordination**: Reducing the response time between theft detection and stablecoin/token freeze deployment through pre-established communication channels and automated alert systems.
- **Exchange-DEX monitoring integration**: Real-time monitoring of DEX swap activity from addresses flagged as exchange hot wallets, enabling faster detection of theft-in-progress.
- **Protocol-level screening**: Some DEX frontends have implemented address screening (using lists from Chainalysis, TRM Labs, etc.), though this does not prevent direct smart-contract interaction.

### 6.4 Payment processor targeting

The 2023 DPRK campaign targeted not only exchanges (CoinEx, Stake.com) but also payment processors (Alphapo, CoinsPaid). Payment processors manage hot wallets on behalf of merchants and platforms, and their key-management systems face similar risks to exchange hot wallets. The targeting of payment processors expanded the threat surface beyond exchanges, affecting the broader cryptocurrency payment infrastructure.

## 7. Lessons learned and recommendations

### 7.1 For exchanges

1. **Assume state-sponsored threat actors**: Design hot-wallet security under the assumption that attackers include well-resourced state actors with sophisticated capabilities. This implies higher security investments than would be justified against opportunistic criminals alone.

2. **Segment key management by chain**: Use separate key-management systems, HSMs, or enclaves for each chain's hot wallet. A single key-management compromise should not cascade across all supported chains.

3. **Minimize hot-wallet exposure**: Hold the minimum necessary balance in hot wallets on each chain. Implement automated, rate-limited cold-to-hot replenishment.

4. **Accelerate detection and response**: Invest in real-time monitoring across all supported chains, with automated withdrawal suspension when anomaly thresholds are breached. Every minute of response time saved reduces the attacker's extraction.

5. **Pre-arrange freeze coordination**: Maintain direct communication channels with Tether, Circle, and major token projects for emergency freeze requests. Rehearse freeze-request procedures regularly.

### 7.2 For market surveillance

1. **Track DPRK-attributed laundering infrastructure**: Maintain and regularly update databases of addresses, contracts, and services associated with confirmed DPRK laundering operations. Monitor these addresses for new inflows.

2. **Detect multi-chain simultaneous outflows**: Flag events where multiple hot-wallet addresses belonging to the same exchange show large outflows within a short timeframe across different chains.

3. **Monitor DEX swap patterns**: Watch for large token-to-native-asset swaps from newly funded addresses, especially immediately following detected exchange hot-wallet outflows.

### 7.3 For regulators

1. **Mandate security standards**: Require exchanges to implement specific security controls for hot-wallet management, including chain-segmented key management, cold-storage minimums, and real-time monitoring.

2. **Require incident reporting**: Establish mandatory incident-reporting timelines and disclosure requirements, including root-cause analysis obligations.

3. **Coordinate on DPRK threat intelligence**: Share threat intelligence about DPRK-linked operations across jurisdictions to enable faster identification and response.

## 8. Conclusion

The CoinEx hot-wallet breach of September 2023 resulted in the theft of approximately $70 million in cryptocurrency across multiple blockchains. The FBI's attribution of the attack to North Korea's Lazarus Group placed it within a broader 2023 campaign that also targeted Stake.com, Alphapo, and CoinsPaid, collectively representing hundreds of millions of dollars in state-sponsored cryptocurrency theft.

The incident reinforced several structural themes in exchange security: the expanding multi-chain attack surface that makes hot-wallet key management increasingly complex, the persistent DEX swap window that allows attackers to convert freezable tokens to non-freezable assets before industry response, and the need for exchange security models to account for state-sponsored threat actors with sophisticated and well-resourced capabilities.

CoinEx's response — including prompt detection, public disclosure of affected addresses, and commitment to full user compensation — represented improvements over some historical exchange-hack responses, though the lack of a detailed root-cause analysis limited the industry's ability to learn from the specific attack vector. For the broader cryptocurrency market, the CoinEx hack underscored that exchange security is not merely an operational concern for individual platforms but a systemic risk factor influenced by state-level geopolitical dynamics.
