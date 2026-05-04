---
title: "🌰 Multichain — MPC Key Compromise and $126M Cross-Chain Bridge Collapse"
date: 2026-05-05
entities:
  - Multichain
  - Anyswap
  - Fantom
  - Ethereum
  - Binance Smart Chain
  - Moonriver
  - Dogecoin
---

## Summary

1. **In July 2023, the Multichain (formerly Anyswap) cross-chain bridge suffered abnormal outflows totaling over $126 million**, with large unauthorized transfers from its MPC-controlled bridge addresses across multiple chains. The incident followed weeks of operational disruptions and communication failures from the Multichain team.
2. **The root cause was reportedly the compromise or misuse of the MPC (Multi-Party Computation) key system** that secured the bridge's cross-chain asset custody. According to statements released after the incident, Multichain's CEO Zhaojun He had exclusive control over critical server infrastructure and MPC key shares, and he was detained by Chinese authorities in late May 2023 — leaving the protocol without operational access to its own security infrastructure.
3. **The largest outflows affected the Fantom bridge**, which lost approximately $130 million in assets including WBTC, USDC, DAI, and various other tokens. Additional outflows were observed from Multichain's Moonriver and Dogecoin bridge addresses.
4. **Multichain officially ceased operations on July 14, 2023**, announcing that the protocol could not continue due to force majeure circumstances related to the CEO's detention and the resulting inability to maintain the MPC network. The team recommended that all users stop using Multichain services.
5. **The incident exposed critical centralization risks in bridge infrastructure**: despite marketing itself as a decentralized cross-chain protocol with MPC-based security, Multichain's operational security depended heavily on a single individual who controlled access to the MPC key server infrastructure. When that individual became unavailable, the entire protocol's security collapsed.

## Background

### Multichain Protocol

Multichain, originally launched as Anyswap in 2020, was one of the largest cross-chain bridge protocols by total value locked (TVL). The protocol facilitated token transfers between dozens of blockchains and at its peak secured over $1.5 billion in bridged assets. Multichain was particularly important for the Fantom ecosystem, serving as the primary bridge for bringing Ethereum-native assets to the Fantom network.

### MPC-Based Bridge Architecture

Multichain used a Multi-Party Computation (MPC) approach for cross-chain asset custody, which was marketed as more decentralized and secure than simple multi-signature wallets:

- **MPC Network**: A set of nodes that collectively held shares of the private keys controlling bridge addresses. No single node held a complete private key.
- **Threshold Signing**: To authorize a cross-chain transfer, a threshold number of MPC nodes had to cooperate in a distributed signing protocol to produce a valid signature.
- **Bridge Addresses**: On each supported chain, Multichain maintained addresses controlled by the MPC network. Users' bridged assets were locked in these addresses.

### Operational Reality vs. Marketing

While MPC technology is sound in principle, Multichain's implementation had critical centralization weaknesses:

| Aspect | Marketed Claim | Reported Reality |
|--------|---------------|-----------------|
| Key management | Distributed MPC across independent nodes | CEO reportedly had access to all key shares and controlled critical infrastructure |
| Server infrastructure | Decentralized node operators | Core MPC servers reportedly under CEO's personal control |
| Operational continuity | Protocol-level resilience | Single point of failure: CEO's availability |
| Governance | Community-driven DAO | Critical operational decisions concentrated in founding team |

The gap between Multichain's marketed decentralization and its operational centralization was the fundamental vulnerability that the July 2023 incident exploited.

## Timeline of Events

### Pre-Incident Warning Signs

| Date | Event |
|------|-------|
| Late May 2023 | Multichain CEO Zhaojun He reportedly detained by Chinese police in Kunming |
| May 21-25 | Users begin reporting delayed or failed cross-chain transactions |
| May 25 | Multichain acknowledges "technical issues" affecting some cross-chain routes |
| June 2023 | Multiple cross-chain routes remain suspended; team communication becomes sporadic |
| Late June | Binance and other exchanges suspend Multichain-bridged token deposits |
| July 6 | Large unauthorized outflows begin from Multichain bridge addresses |
| July 7 | Multichain confirms "abnormal" transfers; Fantom Foundation acknowledges situation |
| July 10 | Multichain team reveals CEO's detention and explains operational breakdown |
| July 14 | Multichain officially ceases operations |

### The Critical Gap: May 25 to July 6

The approximately six-week period between the first operational disruptions and the large unauthorized outflows was a warning period during which:
- Cross-chain transactions were delayed or failing, indicating backend infrastructure problems
- The Multichain team provided minimal and opaque communication
- Users and protocols that depended on Multichain had limited information to assess risk
- TVL remained high because many users were unable to bridge assets out (the very mechanism that would protect them was broken)

This period illustrated a failure mode specific to bridge protocols: when the bridge itself is degraded, users who need to exit are trapped in the destination chain with wrapped tokens whose backing is at risk.

## Technical Analysis

### How the MPC System Failed

Based on post-incident disclosures and analysis:

1. **Centralized infrastructure control**: The MPC nodes required server infrastructure to operate. The CEO reportedly controlled the cloud accounts and access credentials for these servers. When the CEO was detained, the remaining team could not access or operate the MPC network.

2. **Key share concentration**: While MPC distributes key shares across multiple nodes, the security guarantee depends on the shares being held by genuinely independent parties. If one individual has access to enough shares (directly or through infrastructure control), the MPC system degenerates to single-key security.

3. **No operational succession plan**: There was no documented or tested procedure for maintaining the MPC network if the CEO became unavailable. No other team member had sufficient access to the infrastructure to maintain operations or execute an emergency shutdown.

4. **Unauthorized access**: Once the MPC infrastructure was compromised (whether through the detained CEO's credentials, through the authorities who detained him, or through an external attacker exploiting the operational chaos), the bridge addresses could be drained.

### Outflow Analysis

The unauthorized outflows occurred across multiple chains:

| Chain | Approximate Outflow | Major Tokens |
|-------|-------------------|--------------|
| Fantom | ~$130M | WBTC, USDC, DAI, LINK, CRV, YFI, and others |
| Moonriver | ~$6.8M | Various bridged tokens |
| Dogecoin | ~$666K | DOGE |
| **Total** | **~$137M+** | |

Note: Estimates vary across sources. Some analyses count only the abnormal July outflows; others include assets that became irrecoverable due to the protocol shutdown. The commonly cited figure of $126M refers to the initial wave of abnormal transfers.

The Fantom bridge was disproportionately affected because:
- Fantom relied heavily on Multichain as its primary bridge from Ethereum
- A large volume of assets had been bridged to Fantom through Multichain
- Fantom's DeFi ecosystem had significant TVL denominated in Multichain-bridged tokens

### Impact on Bridged Token Backing

When the Multichain bridge addresses were drained, the wrapped tokens on destination chains (e.g., multiUSDC on Fantom) lost their backing:

- **multiUSDC** (Multichain-bridged USDC on Fantom): Became unbacked when the corresponding USDC was removed from the Ethereum bridge address. The token was no longer redeemable 1:1 for native USDC.
- **multiWBTC**, **multiDAI**, **multiLINK**, etc.: Same pattern — wrapped versions on Fantom became worth less than the native tokens they were supposed to represent.
- **Depegging**: Multichain-bridged tokens on Fantom rapidly depegged on DEXs, with some falling to a fraction of their intended value within hours.

## Fantom Ecosystem Impact

### Immediate Effects

The Multichain collapse had a devastating impact on the Fantom ecosystem:

| Metric | Pre-Incident | Post-Incident (1 week) |
|--------|-------------|----------------------|
| Fantom DeFi TVL | ~$300M | ~$100-150M |
| multiUSDC peg | ~$1.00 | $0.10-0.30 |
| FTM price | ~$0.30 | ~$0.22 |

Many Fantom DeFi protocols had accepted Multichain-bridged tokens as collateral or liquidity:
- **Lending protocols**: Positions collateralized by Multichain-bridged tokens faced immediate insolvency
- **DEXs**: Liquidity pools containing Multichain-bridged tokens experienced massive impermanent loss
- **Yield farms**: Strategies involving Multichain-bridged tokens collapsed

### Fantom Foundation Response

The Fantom Foundation:
- Acknowledged the situation and clarified that Multichain was an independent entity
- Worked to establish alternative bridging routes (Axelar, LayerZero, Celer)
- Engaged in community discussions about the future of wrapped assets on Fantom
- Eventually migrated key ecosystem infrastructure to new bridge providers

### Long-Term Ecosystem Damage

The Multichain collapse permanently impaired Fantom's DeFi ecosystem:
- Many users who held Multichain-bridged tokens on Fantom suffered total losses on those positions
- Developer and user confidence in Fantom's infrastructure was damaged
- The incident demonstrated the risk of ecosystem-level dependency on a single bridge provider

## Vulnerability Pattern: Bridge Centralization Risk

### The "Bus Factor" Problem

Multichain's failure exemplifies the "bus factor" problem in cryptocurrency infrastructure: what happens when a critical individual becomes unavailable? For Multichain:

- **Bus factor = 1**: The entire protocol's security and operation depended on a single person
- **No key escrow or recovery mechanism**: There was no dead-man's switch, timelock, or multi-party recovery process for the MPC infrastructure
- **No transparency about operational structure**: Users and integrating protocols were not informed about the degree of centralization

### Comparison to Other Bridge Centralization Incidents

| Incident | Date | Root Cause | Centralization Failure |
|----------|------|-----------|----------------------|
| Multichain | Jul 2023 | CEO detention → MPC infrastructure inaccessible | Single individual controlled all critical infrastructure |
| Harmony Horizon | Jun 2022 | 2-of-5 validator key compromise | Low threshold with potentially concentrated validators |
| Ronin Bridge | Mar 2022 | 5-of-9 keys compromised via social engineering | Axie Sky Mavis controlled 4 of 9 validators |
| Wormhole | Feb 2022 | Smart contract vulnerability | Not a centralization issue, but Jump Crypto's bailout illustrated concentration of bridge oversight |

The pattern across these incidents is consistent: bridge security degrades when the operational reality is more centralized than the stated architecture. Whether the centralization is in key management (Multichain), validator sets (Harmony, Ronin), or smart contract upgrade authority, the result is that a smaller attack surface than expected can compromise all bridged assets.

### Red Flags for Bridge Centralization

Based on the Multichain case, the following should be treated as warning signs:

1. **Opaque operator structure**: If the identity and independence of MPC node operators or bridge validators is not publicly verifiable, assume concentration risk
2. **Single-entity infrastructure**: If one organization (or individual) controls the server infrastructure for the entire MPC network, the MPC provides weaker security than its threshold suggests
3. **Communication failures during outages**: Multichain's sporadic and opaque communication during the May-June disruption period was a strong signal that something was fundamentally wrong with the protocol's operational structure
4. **No documented succession or recovery plan**: Protocols that cannot demonstrate how they would maintain operations if key personnel become unavailable have a single point of failure

## Market Impact

### Broader Market Effects

The Multichain collapse had limited impact on the broader crypto market but significant impact on specific ecosystems:

- **FTM token**: Declined roughly 25-30% in the weeks surrounding the incident, from approximately $0.30 to ~$0.22
- **Fantom DeFi**: TVL declined substantially as users exited positions denominated in Multichain-bridged tokens
- **Bridge sector**: Accelerated the shift toward bridges with more transparent and decentralized security models
- **Regulatory attention**: The incident, involving a CEO detained by Chinese authorities and resulting in user losses, added to the regulatory narrative around cryptocurrency operational risks

### Bridge Design Evolution

Post-Multichain, the bridge sector evolved in several directions:

1. **Canonical bridges**: L2 rollups (Arbitrum, Optimism, Base) promoted their canonical bridges, which inherit security from the underlying L1
2. **Light client bridges**: Bridges using on-chain light clients to verify cross-chain state (e.g., IBC for Cosmos) gained adoption as a more trustless alternative
3. **Multiple bridge standards**: Ecosystems began supporting multiple bridge providers rather than depending on a single bridge, reducing single-provider risk
4. **Transparency requirements**: Integration decisions increasingly required disclosure of bridge operator identity, key management practices, and emergency procedures

## Lessons for Market Surveillance

1. **Bridge operational disruption as an early warning**: The six-week period of degraded Multichain operations before the large outflows was a clear warning signal. Surveillance systems should monitor cross-chain bridge transaction success rates, confirmation times, and user-reported failures as leading indicators of bridge infrastructure problems.

2. **Communication pattern analysis**: A bridge team that shifts from regular communication to sporadic, opaque updates during an operational disruption is exhibiting a red-flag pattern. Tracking team communication frequency and transparency during incidents can distinguish between routine maintenance and systemic problems.

3. **Wrapped token peg monitoring**: Multichain-bridged tokens depegged rapidly once the outflows were detected. Real-time monitoring of wrapped token prices on DEXs versus their intended peg can provide early detection of bridge compromise — depeg precedes official announcements.

4. **TVL concentration risk**: Ecosystems that route a majority of bridged assets through a single bridge provider have concentrated risk. Surveillance should track the market share of bridge providers within each ecosystem and flag ecosystems where one bridge controls more than 50% of bridged TVL.

5. **MPC transparency verification**: Claimed MPC security should be verified against the operational reality. Surveillance and risk assessment should probe whether MPC node operators are genuinely independent and whether the infrastructure is resilient to single-entity failure.

6. **Jurisdiction risk for bridge operators**: The CEO's detention by Chinese authorities introduced a jurisdiction risk that was not priced in by users. Bridge operators' jurisdictional exposure — including the legal environments of key personnel — should be part of risk assessment.

## References

1. Multichain. "Multichain Operation Ceased." Multichain Blog / Twitter, July 14, 2023.
2. Fantom Foundation. "Fantom Foundation Statement on Multichain." Fantom Blog, July 2023.
3. Chainalysis. "The 2024 Crypto Crime Report." Chapter: Bridge Exploits. Chainalysis Inc., February 2024.
4. Rekt News. "Multichain — REKT." rekt.news, July 2023.
5. Elliptic. "Multichain Exploit Analysis." Elliptic Research, July 2023.
6. CoinDesk. "Multichain CEO's Arrest Triggered Protocol's Collapse." CoinDesk, July 2023.
7. The Block. "Multichain Shuts Down After $126M Exploit." The Block, July 14, 2023.
