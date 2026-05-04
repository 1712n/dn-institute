---
title: "🌰 KyberSwap — Elastic Liquidity Tick Manipulation and $48.8M Multi-Chain DEX Drain"
date: 2026-05-05
entities:
  - KyberSwap
  - KyberNetwork
  - KNC
  - Ethereum
  - Arbitrum
  - Optimism
  - Polygon
  - Base
  - Avalanche
---

## Summary

1. **On November 22, 2023, the KyberSwap Elastic decentralized exchange was exploited for approximately $47-48.8 million** across multiple chains including Ethereum, Arbitrum, Optimism, Polygon, Base, and Avalanche. The attacker exploited a vulnerability in the concentrated liquidity tick-boundary calculation logic.
2. **The root cause was a precision/rounding error in KyberSwap Elastic's reinvestment curve and tick-crossing calculations**. Under carefully constructed swap conditions near tick boundaries, the contract's internal accounting could double-count or overstate available liquidity, allowing the attacker to withdraw more value from pools than should have been possible.
3. **The attacker executed a sophisticated, multi-step attack** that required precise manipulation of pool prices around specific tick boundaries, combined with flash-loaned liquidity. The attack was replicated across several KyberSwap Elastic deployments, suggesting the attacker had developed and tested the exploit before executing it across chains.
4. **The attacker sent an on-chain message to KyberSwap** demanding negotiation and claiming they would be willing to return funds under certain conditions, including a proposed arrangement where the attacker would receive a portion of the funds. The attacker also demanded authority over KyberSwap's governance. Negotiations were contentious and ultimately the full amount was not returned.
5. **The exploit demonstrated that concentrated liquidity implementations** — which allow liquidity providers to specify price ranges rather than providing liquidity across the entire price curve — introduce complex mathematical edge cases at tick boundaries that can be exploitable if not handled with sufficient precision.

## Background

### KyberSwap and KyberNetwork

KyberNetwork is a decentralized exchange (DEX) aggregation and liquidity protocol that has operated since 2018. KyberSwap is the user-facing DEX component, which includes:

- **KyberSwap Classic**: An earlier AMM design with standard constant-product liquidity pools
- **KyberSwap Elastic**: A concentrated liquidity AMM (similar to Uniswap V3) that allows liquidity providers to concentrate their liquidity within specific price ranges
- **DEX aggregation**: KyberSwap also functions as a DEX aggregator, routing trades through multiple liquidity sources

The exploit targeted KyberSwap Elastic specifically, across all chains where it was deployed.

### Concentrated Liquidity Mechanics

Concentrated liquidity, pioneered by Uniswap V3, divides the price curve into discrete "ticks." Liquidity providers choose a price range (defined by an upper and lower tick) within which their liquidity is active:

- **Ticks**: Discrete price points that divide the continuous price space. Each tick represents a specific price ratio.
- **Active liquidity**: Only liquidity within the range containing the current price is used for swaps. As the price moves, liquidity from different ranges activates and deactivates.
- **Tick crossing**: When a swap moves the price across a tick boundary, the protocol must activate new liquidity and deactivate old liquidity, updating internal accounting accordingly.

This tick-crossing logic is mathematically complex and is the area where KyberSwap's vulnerability existed.

### Key Parameters at Exploit Time

| Parameter | Value |
|-----------|-------|
| KyberSwap Elastic TVL | Tens of millions of dollars across chains |
| Chains deployed | Ethereum, Arbitrum, Optimism, Polygon, Base, Avalanche, others |
| Concentrated liquidity model | Similar to Uniswap V3 with modifications (reinvestment curve) |
| Tick spacing | Variable per pool |
| Total drained | ~$47-48.8M across multiple chains |

## Technical Exploit Mechanics

### The Reinvestment Curve Vulnerability

KyberSwap Elastic differed from Uniswap V3 in several ways, including its handling of fee reinvestment. The protocol included a "reinvestment curve" mechanism that automatically reinvested accumulated trading fees back into the pool. This reinvestment curve interacted with the tick-boundary calculations in a way that created a precision vulnerability.

**The core issue**: When carefully structured swaps moved pool prices around tick boundaries, the reinvestment curve's contribution to total liquidity could be calculated with a precision error. Specifically:

1. The protocol computed the amount of liquidity available at a tick boundary by combining the base liquidity (from LPs) with the reinvestment liquidity (from accumulated fees)
2. At certain tick boundaries, the rounding in this combination could produce a result that was slightly different from the mathematically correct value
3. The attacker could exploit this by constructing a sequence of swaps that repeatedly crossed tick boundaries in a way that accumulated these rounding errors
4. Repeated boundary-crossing operations amplified the discrepancy between the protocol's internal accounting and the actual token balances

### Attack Sequence

The attacker's approach across each targeted chain:

**Step 1 — Flash Loan**: Borrowed large amounts of tokens from flash loan providers to fund the attack

**Step 2 — Liquidity Provision**: Added concentrated liquidity at carefully chosen tick ranges in the target pool, specifically designed to create the conditions for the precision error

**Step 3 — Price Manipulation Around Tick Boundary**: Executed swaps that moved the pool price to carefully selected boundary conditions where the reinvestment curve calculation could produce the precision error

**Step 4 — Exploit the Precision Error**: Around the tick boundary, the protocol's internal accounting could overstate available liquidity. The attacker exploited this discrepancy by extracting tokens that should have remained in the pool.

**Step 5 — Repeat and Extract**: The attacker repeated this process across multiple pools and tick ranges, extracting value from each precision error

**Step 6 — Cross-Chain Execution**: The same exploit was executed on Ethereum, Arbitrum, Optimism, Polygon, Base, and Avalanche, suggesting pre-deployment testing and automation

### Losses by Chain

| Chain | Approximate Loss |
|-------|-----------------|
| Arbitrum | Largest reported share, around tens of millions |
| Optimism | Major reported share |
| Ethereum | Multi-million-dollar reported share |
| Polygon | Low-single-digit millions reported |
| Base | Low-single-digit millions reported |
| Avalanche | Low-single-digit millions reported |
| **Total** | **~$47-48.8M reported** |

The concentration of losses on Arbitrum and Optimism broadly reflected where vulnerable KyberSwap Elastic liquidity was available at the time.

### Why This Vulnerability Was Difficult to Detect

1. **Mathematical complexity**: Concentrated liquidity tick calculations involve complex fixed-point arithmetic. The precision error only manifested at specific tick boundaries under specific conditions, making it difficult to detect through standard testing.

2. **Interaction between components**: The vulnerability arose from the interaction between the reinvestment curve (a KyberSwap-specific feature) and the standard tick-crossing logic. Each component might be correct in isolation, but their interaction at boundary conditions produced the error.

3. **Small per-transaction discrepancy**: Each individual tick-boundary crossing produced a small discrepancy. The attack's profitability came from amplifying these discrepancies through repeated, carefully constructed swap sequences.

4. **Multi-chain deployment**: Similar vulnerable code was deployed across multiple chains, meaning the same class of bug could be exploited in parallel wherever affected pools had sufficient liquidity.

## Post-Exploit Events

### Attacker Communication

The KyberSwap exploit was notable for the attacker's confrontational communication style:

- **On-chain messages**: The attacker sent messages demanding negotiation and proposing terms
- **Governance and company-control demands**: The attacker demanded extraordinary authority over KyberSwap/KyberNetwork assets, governance, and company operations
- **Bounty framing**: The attacker framed their demands as compensation for identifying the vulnerability
- **Contentious tone**: Unlike the relatively cooperative communications in the Euler Finance or Poly Network cases, the KyberSwap attacker's demands were widely perceived as extortionate

### KyberSwap Response

- **November 22**: KyberSwap confirmed the exploit and advised users to withdraw remaining funds
- **November 23**: KyberSwap offered a 10% bounty for fund return
- **Negotiations**: Extended back-and-forth between KyberSwap and the attacker, with the attacker's demands widely criticized
- **Treasury impact**: KyberSwap/KyberNetwork reported significant treasury impact and later workforce reductions

### Partial Recovery

As of public reporting, the full amount was not returned. Some funds were recovered through various channels, but the exact final recovery amount was not publicly confirmed as matching the full $48.8M.

## Market Impact

### KNC Token

| Metric | Pre-Exploit | Post-Exploit (48h) |
|--------|-------------|-------------------|
| KNC price | ~$0.75 | ~$0.62 |
| Price decline | — | ~17% |

### KyberSwap TVL and Operations

- Pre-exploit TVL: tens of millions of dollars across chains
- Post-exploit TVL: dropped sharply as remaining users withdrew
- KyberSwap/KyberNetwork announced significant workforce reductions in the weeks following
- The protocol continued operating but with reduced TVL and activity

### Broader DEX Impact

- **Concentrated liquidity scrutiny**: The exploit intensified scrutiny of concentrated liquidity implementations, particularly custom modifications to the Uniswap V3 model
- **Audit focus on tick boundaries**: Security firms added tick-boundary precision testing as a standard audit item for concentrated liquidity protocols
- **Fork risk assessment**: Protocols that forked or modified Uniswap V3's concentrated liquidity were flagged for additional review

## Vulnerability Pattern: Concentrated Liquidity Tick-Boundary Precision

### The Tick-Boundary Risk in Concentrated Liquidity

Concentrated liquidity protocols divide the continuous price space into discrete ticks. At each tick boundary, the protocol must:

1. Calculate the exact amount of liquidity entering or exiting the active range
2. Update internal accounting for fee accumulation and distribution
3. Handle the transition between different liquidity positions

Each of these calculations involves fixed-point arithmetic with limited precision. At boundary conditions (exactly at a tick), the mathematical behavior can differ from the general case, creating potential for precision errors.

### Comparison to Other DEX Exploits

| Protocol | Date | Loss | Vulnerability Type |
|----------|------|------|--------------------|
| KyberSwap Elastic | Nov 2023 | ~$47-48.8M | Tick-boundary precision in reinvestment curve |
| Curve/Vyper | Jul 2023 | ~$70M | Compiler-level reentrancy lock bug |
| Balancer | Aug 2023 | ~$2M | Rate provider manipulation |
| Platypus | Feb 2023 | ~$8.5M | Logic error in stablecoin AMM |
| SushiSwap (RouteProcessor) | Apr 2023 | ~$3.3M | Approval vulnerability in router contract |

The KyberSwap exploit was distinctive in targeting the mathematical precision of tick-boundary calculations rather than exploiting reentrancy, oracle manipulation, or access control flaws.

### Why Custom Concentrated Liquidity Implementations Are Risky

Uniswap V3's concentrated liquidity code has been extensively audited, battle-tested, and mathematically verified. Protocols that fork and modify this code face risks:

1. **Modified invariants**: Changes to the fee model, reinvestment mechanism, or tick calculation can break invariants that the original code relied upon
2. **Edge case divergence**: The original code may handle edge cases (like exact tick boundaries) correctly, but modifications can inadvertently break these handlers
3. **Reduced testing coverage**: Modified code has less real-world testing than the original, and the modifications may create new edge cases not covered by existing tests
4. **Audit scope limitations**: Auditors reviewing a fork may focus on the modifications and miss subtle interactions between modified and unmodified code

## Lessons for Market Surveillance

1. **Tick-boundary transaction monitoring**: Swaps that repeatedly move pool prices to exact tick boundaries in concentrated liquidity pools should be flagged as potentially exploitative. Normal trading rarely targets exact tick prices — this pattern indicates deliberate manipulation.

2. **Cross-chain simultaneous exploit detection**: The KyberSwap attacker hit multiple chains within a short timeframe. Surveillance systems should correlate exploit-like transactions across chains for protocols deployed on multiple networks, as a confirmed exploit on one chain may imply related deployments are vulnerable.

3. **Concentrated liquidity fork risk assessment**: Protocols that fork Uniswap V3's concentrated liquidity with custom modifications (fee models, reinvestment curves, tick spacing) should be flagged for elevated scrutiny. The more extensive the modifications, the higher the risk of introduced vulnerabilities.

4. **Precision error amplification patterns**: The attack involved repeated tick-boundary crossings to amplify small precision errors. Monitoring for transactions that execute many small swaps crossing the same tick boundaries in rapid succession can identify this attack pattern.

5. **Attacker communication as intelligence**: The KyberSwap attacker's on-chain messages provided early intelligence about their intentions and demands. Monitoring for UTF-8 encoded messages in transaction calldata from flagged addresses provides insight into attacker behavior.

6. **Post-exploit TVL flight monitoring**: After a DEX exploit, remaining TVL typically exits rapidly. Monitoring withdrawal rates from exploited protocols provides real-time data on the extent of confidence loss and potential secondary market impacts.

## References

1. KyberSwap. "KyberSwap Elastic Exploit — Post-Incident Update." KyberSwap Blog, November 2023.
2. BlockSec. "KyberSwap Elastic Exploit Analysis." BlockSec Blog, November 2023.
3. Rekt News. "KyberSwap — REKT." rekt.news, November 22, 2023.
4. Ambient Finance (@CrocSwap). "Technical Analysis of KyberSwap Exploit." Twitter thread, November 2023.
5. Chainalysis. "The 2024 Crypto Crime Report." Chapter: DEX Exploits. Chainalysis Inc., February 2024.
6. DeFi Llama. "KyberSwap TVL Data." defillama.com, 2023.
