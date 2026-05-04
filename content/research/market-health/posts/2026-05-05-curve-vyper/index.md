---
title: "🌰 Curve Finance — Vyper Reentrancy Bug and CRV Contagion Risk"
date: 2026-05-05
entities:
  - Curve Finance
  - Vyper
  - CRV
  - Alchemix
  - JPEG'd
  - Metronome
  - Ethereum
---

## Summary

1. **On July 30, 2023, several Curve Finance liquidity pools and related ecosystem pools were exploited through a Vyper compiler reentrancy bug**, with public estimates placing gross affected value around $69-70 million and net losses lower after whitehat and exploiter returns.
2. **The root cause was not a normal application-level missing guard**. Contracts had used Vyper's `@nonreentrant` decorator, but Vyper compiler versions 0.2.15, 0.2.16, and 0.3.0 contained a latent bug that made the lock malfunction in affected contracts.
3. **The attack targeted ETH-paired pools where reentrancy could occur during liquidity removal and token transfer flows**, including JPEG'd's pETH/ETH pool, Alchemix's alETH/ETH pool, Metronome's msETH/ETH pool, and Curve's CRV/ETH pool.
4. **The market impact extended beyond the direct pool losses**. CRV price pressure, concerns over founder Michael Egorov's CRV-backed borrowing positions, and liquidity-provider withdrawals created a broader DeFi contagion scare even though the affected bug was limited to specific Vyper-compiled contracts.
5. **The incident became a toolchain-security case study**: source-code audits are incomplete when compiler behavior can invalidate security assumptions. Protocol surveillance should track compiler versions, dependency risk, pool liquidity, liquidation-sensitive collateral positions, and emergency withdrawal advisories.

## Background

### Curve Finance

Curve Finance is a decentralized exchange optimized for stable and correlated assets. Its pools are deeply integrated into DeFi: lending protocols, liquid staking derivatives, stablecoin issuers, yield aggregators, and collateral markets all depend on Curve pool pricing and liquidity.

Curve pools often hold large balances of assets that are intended to trade near each other, such as ETH and liquid staking derivatives, or stablecoins and their wrapped variants. That design makes Curve a core market-structure component rather than an isolated exchange.

### Vyper

Vyper is a Python-like smart contract language for the Ethereum Virtual Machine. Some Curve pools were written in Vyper rather than Solidity. Developers used Vyper features such as the `@nonreentrant` decorator to prevent a contract from being re-entered before a sensitive function completed.

In normal operation, a reentrancy guard works like a lock:

1. The protected function begins execution.
2. The contract sets a lock value.
3. If an external call tries to re-enter another protected function before the first call finishes, the lock check fails.
4. The original function completes and clears the lock.

The July 2023 incident occurred because this expected behavior was not reliably enforced for contracts compiled with specific Vyper versions.

## Timeline

| Date / Time | Event |
|------------|-------|
| July 2021 | Vyper 0.2.15 released; later identified as one of the vulnerable versions |
| December 2021 | Vyper 0.3.1 released; the later-known bug was no longer present after the vulnerable 0.2.15/0.2.16/0.3.0 range |
| July 30, 2023 | Exploits begin against Curve ecosystem pools using vulnerable Vyper-compiled contracts |
| July 30, 2023 | Vyper publicly warns that versions 0.2.15, 0.2.16, and 0.3.0 contain malfunctioning reentrancy locks |
| July 30-31, 2023 | JPEG'd, Alchemix, Metronome, and Curve-linked pools report losses or emergency responses |
| Early August 2023 | Portions of funds are returned by exploiters and whitehat / MEV actors |
| August 2023 | Curve posts a public bounty for information on unrecovered exploiter funds |

The key surveillance failure was that the compiler issue existed long before the exploit window, but the market only repriced the risk once attackers demonstrated the bug against live liquidity.

## Affected Pools and Loss Estimates

Public sources report different numbers depending on whether they measure gross drained value, unrecovered loss, or values after partial returns. A conservative way to frame the incident is:

| Metric | Approximate Public Figure |
|-------|---------------------------|
| Gross value affected / taken | ~$69-70M |
| CertiK reported net loss after returns | ~$52M |
| Chainalysis original estimate | Approximately $70M in losses, with final loss potentially lower after recoveries |
| Notable returned funds | Alchemix received 4,820 alETH and 2,258 ETH; JPEG'd confirmed most stolen funds returned; whitehat c0ffeebabe.eth returned funds to Curve/Metronome |

Affected pools and protocols included:

| Pool / Protocol | Role in Incident |
|----------------|------------------|
| JPEG'd pETH/ETH | Early exploit target; a front-running MEV transaction captured value before the original transaction in one reported path |
| Alchemix alETH/ETH | Large affected pool; later received a significant return of alETH and ETH |
| Metronome msETH/ETH | Affected by the same vulnerable Vyper compiler issue |
| Curve CRV/ETH | Direct Curve pool affected, creating CRV market stress |

The incident was therefore not a single-pool bug. It was a shared compiler-risk event that could propagate to deployed contracts with the vulnerable pattern and meaningful assets at risk.

## Technical Mechanism

### Reentrancy in Liquidity Pools

Reentrancy occurs when a contract makes an external call before updating or finalizing all internal accounting, and the called address uses that opportunity to call back into the original contract. If the original contract assumes the first operation has completed when it has not, balances can be miscomputed.

In liquidity pools, reentrancy can be especially dangerous because pool functions combine:

- token transfers;
- balance checks;
- virtual price calculations;
- liquidity-token minting or burning;
- invariant checks;
- external callbacks through ETH or token transfer mechanisms.

If an attacker can re-enter between those steps, the pool may calculate withdrawal amounts using stale or inconsistent state.

### The Vyper `@nonreentrant` Failure

The affected Curve ecosystem contracts were not obviously missing a reentrancy guard in source code. They used Vyper's `@nonreentrant` decorator. The problem was that affected Vyper compiler versions generated bytecode where the lock did not reliably protect the intended cross-function critical section.

Vyper's postmortem identified versions 0.2.15, 0.2.16, and 0.3.0 as vulnerable. Public analyses describe the bug as a storage-layout / lock-handling issue in which the reentrancy lock could be set and checked inconsistently. The result was that code which appeared protected at the source level could still be re-entered at runtime.

This distinction matters for audit methodology:

- A source-code reviewer could see `@nonreentrant` and reasonably expect protection.
- A protocol integrator could rely on the compiler to implement the decorator correctly.
- The deployed bytecode did not preserve that security property for the affected versions.

### Example Attack Flow

CertiK's analysis of the pETH/ETH path describes the attacker borrowing a large amount of WETH, adding liquidity to the Curve pool, removing liquidity, and using a fallback-triggered reentrant call to manipulate pool accounting during withdrawal. The attacker then repaid the flash liquidity and retained the difference.

At a high level:

1. Borrow a large temporary ETH/WETH amount.
2. Add liquidity to the vulnerable ETH-paired pool.
3. Begin removing liquidity.
4. Use the external transfer / fallback path to re-enter before accounting is safely finalized.
5. Add or remove liquidity again while the pool state is inconsistent.
6. Repay temporary liquidity and keep the excess assets.

The exact path varied by pool, but the common mechanism was reentrancy through a contract that developers believed was protected by `@nonreentrant`.

## Market Impact

### Direct Liquidity Shock

The first-order impact was loss of funds from affected pools. Liquidity providers in those pools were directly exposed because pool assets were removed faster than legitimate accounting allowed.

Curve and related teams responded by warning users to withdraw from affected or potentially affected Vyper-based pools. That created a second liquidity shock: even unaffected pools could see withdrawals because users needed to understand whether their specific pool was compiled with a vulnerable version.

### CRV Price and Collateral Pressure

The more systemic risk came from CRV market structure. After the exploit, CRV sold off and liquidity thinned. Market participants focused on Curve founder Michael Egorov's large CRV-backed loan positions across DeFi lending protocols. If CRV price fell far enough, liquidations could create forced selling into already stressed markets.

This turned a compiler bug into a market-health incident:

- CRV price declined after exploit news.
- Exploiters held or could sell CRV-related assets from the CRV/ETH pool.
- Lending protocols with CRV collateral exposure faced bad-debt concerns.
- Egorov conducted over-the-counter CRV sales to reduce loan pressure.
- DeFi users monitored Aave and other protocols for contagion risk.

The risk was not only the dollars drained from pools; it was the possibility that CRV collateral liquidation could propagate stress into lending markets.

### TVL and Confidence

Curve's TVL fell sharply after the incident as users withdrew or reassessed pool risk. Some reported figures show TVL dropping by roughly half during the stress window, though exact percentages depend on timestamp and data source.

For market surveillance, the precise TVL number is less important than the sequence:

1. Technical exploit.
2. Emergency withdrawal warnings.
3. Liquidity provider withdrawals.
4. Governance-token price decline.
5. Lending-collateral stress.
6. OTC balance-sheet stabilization.

This is a recognizable contagion chain for DeFi infrastructure protocols.

## Why the Incident Was Hard to Detect

### The Source Looked Protected

Many DeFi incidents involve missing checks, wrong constants, or explicit unsafe calls. The Curve-Vyper incident was harder because contracts appeared to use the correct source-level protection.

Auditors and integrators needed to ask a deeper question: did the compiled bytecode actually implement the expected guard?

### The Bug Was Version-Specific

The affected versions were specific: 0.2.15, 0.2.16, and 0.3.0. Other Vyper versions were not necessarily vulnerable. That meant risk could not be assessed by asking "is this written in Vyper?" The correct question was:

- Which exact compiler version built this deployed bytecode?
- Does the contract use `@nonreentrant` in a way affected by the bug?
- Does the contract hold assets and expose external-call paths where reentrancy matters?
- Are there ETH or callback-capable token flows that can trigger reentry?

### Pool Exposure Was Uneven

Not every Curve pool was equally exposed. Pools compiled with unaffected versions or not using the vulnerable reentrancy pattern were safer. The challenge during the incident was rapidly classifying pools by compiler version and runtime exploitability while public fear was spreading faster than technical triage.

## Surveillance Framework

### Pre-Incident Toolchain Inventory

Protocols should maintain a machine-readable inventory of deployed contracts:

| Field | Why It Matters |
|------|----------------|
| Source language | Identifies Vyper/Solidity/Huff/Yul risk classes |
| Compiler version | Allows fast matching against known compiler advisories |
| Optimization settings | Affects generated bytecode and audit reproducibility |
| Library dependencies | Identifies shared code and package-level blast radius |
| Security decorators/modifiers | Shows which safety properties depend on compiler output |
| Asset balances | Prioritizes contracts by economic exposure |

Without this inventory, teams are forced to reconstruct risk during an active exploit.

### Real-Time Signals

Useful live indicators for a Curve-Vyper-style event include:

| Signal | Interpretation |
|-------|----------------|
| Vyper or compiler security advisory | Immediate need to map affected bytecode |
| Large liquidity removals from ETH-paired pools | Possible exploit or panic withdrawal |
| Abnormal MEV rewards around pool transactions | Bots may be front-running exploit attempts |
| Sudden CRV/ETH pool imbalance | Direct market stress and possible token-price impact |
| Lending-protocol health factor changes for CRV-backed accounts | Contagion risk beyond Curve |
| Team withdrawal advisories | User-protection signal but also liquidity-flight trigger |

### Post-Incident Accounting

Loss accounting should separate:

- gross drained value;
- whitehat-captured value;
- exploiter-returned value;
- protocol-returned value;
- unrecovered user loss;
- market impact from token price movements and liquidation avoidance.

Combining all of these into a single "loss" number can mislead analysts. Chainalysis initially reported approximately $70 million in losses while noting final loss could be lower after recoveries; CertiK later reported approximately $69.3 million taken, $16.7 million returned, and $52 million remaining as loss.

## Comparison With Related Incidents

| Incident | Mechanism | Shared Lesson |
|---------|-----------|---------------|
| The DAO | Reentrancy in split function | External calls before final accounting can drain funds |
| bZx | Flash-loan price manipulation | Temporary state distortions can create durable losses |
| Parity Wallet | Shared library / initialization failure | Dependency architecture can freeze assets |
| Nomad Bridge | Upgrade initialization bug | A single initialization mistake can compromise many users |
| Curve-Vyper | Compiler-level reentrancy guard failure | Toolchain bugs can invalidate source-level security assumptions |

Curve-Vyper is especially important because the vulnerability sat below application code. It showed that "audited source" is not enough if the compiler or deployment pipeline is not also part of the security boundary.

## Defensive Checklist

Protocols with high-value pools or lending integrations should implement:

1. **Compiler-version allowlists** for production deployments.
2. **Bytecode-level verification** of critical security properties, not just source-level review.
3. **Dependency advisory monitoring** for compilers, libraries, and deployment tools.
4. **Emergency pool-classification scripts** that map all live contracts to compiler versions and balances.
5. **Withdrawal circuit breakers** for pools showing abnormal liquidity-removal patterns.
6. **Cross-protocol collateral monitoring** for governance tokens linked to exploited protocols.
7. **MEV-aware exploit detection** to identify front-running of malicious transactions and possible whitehat captures.
8. **Separate gross-loss and net-loss accounting** so recovered funds do not obscure initial blast radius.

## Key Takeaways

1. **Compiler bugs are protocol bugs when deployed contracts depend on compiler-generated safety logic.**
2. **Reentrancy risk remains relevant even after years of standard mitigations.**
3. **Exact compiler versions matter.** Broad language labels are not enough for risk assessment.
4. **Market impact can exceed direct exploit loss** when the affected protocol's governance token is collateral in lending markets.
5. **Whitehat and MEV activity can reduce final loss but complicate incident accounting.**
6. **DeFi surveillance should connect code risk, pool liquidity, token markets, and lending collateral.**

## References

- Chainalysis, "Curve Finance Liquidity Pool Hack" (August 2023).
- Vyper team and Omniscia, "Vyper Nonreentrancy Lock Vulnerability Technical Post-Mortem" (2023).
- LlamaRisk, "Curve Pool Reentrancy Exploit Postmortem" (2023).
- CertiK, "Vyper Incident Analysis" (2023).
- Public Curve, Alchemix, JPEG'd, and Vyper incident updates from July-August 2023.
