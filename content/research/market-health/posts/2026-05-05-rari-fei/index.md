---
date: 2026-05-05
entities:
  - id: rari-capital
    name: Rari Capital
    type: defi
  - id: fei-protocol
    name: Fei Protocol
    type: defi
  - id: compound
    name: Compound
    type: defi
title: "Rari Capital Fuse pool reentrancy exploit, $80 M drain, and Fei Protocol contagion"
---

## 1. Introduction and incident overview

On 30 April 2022, multiple Rari Capital Fuse lending pools were exploited through a reentrancy vulnerability, resulting in the theft of approximately $80 million in cryptocurrency. The exploit targeted Fuse pools — permissionless, isolated lending markets built on a fork of Compound V2's cToken architecture. The attacker used a classic reentrancy attack vector to manipulate borrowing and collateral accounting within the Fuse pool contracts, enabling them to borrow in excess of their collateral and extract the surplus.

The incident had significant contagion effects because Rari Capital had recently merged with Fei Protocol, an algorithmic stablecoin project. Fei's protocol-controlled value (PCV) — the treasury reserves backing the FEI stablecoin — was partially deployed in Rari Fuse pools as a yield-generation strategy. The exploit drained a portion of Fei's PCV along with other depositors' funds, contributing to a governance crisis that ultimately led to Fei Protocol's shutdown and the unwinding of the Rari-Fei merger.

## 2. Technical background

### 2.1 Rari Capital and Fuse pools

Rari Capital was a DeFi protocol that offered permissionless lending pool creation through its Fuse platform. Fuse allowed anyone to create a customized lending pool with chosen collateral types, interest-rate models, and risk parameters — similar to Compound or Aave but without the governance-curated asset listing process.

Fuse pools were built on a fork of Compound V2's cToken architecture. Each pool contained multiple cToken markets (e.g., cETH, cUSDC, cDAI), and users could deposit assets to earn interest or borrow against their deposits. The fork preserved Compound V2's core accounting logic — supply/borrow balances, exchange rates, collateral factors — with modifications to support the permissionless pool-creation model.

### 2.2 The Compound V2 reentrancy surface

Compound V2's original cToken implementation was designed primarily for ERC-20 tokens with standard transfer behavior. When Compound V2 was extended to support ETH (via cETH), the contract needed to handle ETH's native transfer mechanism, which includes a fallback/receive function call to the recipient. This ETH transfer callback creates a potential reentrancy vector: when the cETH contract sends ETH to a borrower (during a borrow or withdrawal), the recipient can execute arbitrary code in their fallback function before the cETH contract has updated its internal state.

Compound V2 itself mitigated this risk through careful ordering of state updates and, in some cases, reentrancy guards. However, forks of Compound V2 — including Rari's Fuse — did not always preserve these mitigations, particularly when the fork modified the original code or added new features.

### 2.3 Fei Protocol's PCV deployment in Fuse

Fei Protocol maintained protocol-controlled value (PCV) — a treasury of assets that backed the FEI stablecoin's peg. To generate yield on its PCV, Fei deployed portions of its treasury into various DeFi strategies, including Rari Fuse pools. This deployment meant that Fei's treasury was directly exposed to the smart-contract risk of the Fuse pool contracts.

The Rari-Fei merger, completed in late 2021, made this exposure a formal relationship: Fei Protocol acquired Rari Capital's governance tokens and integrated Fuse into its broader protocol strategy. The merger was intended to create synergies between Fei's stablecoin and Rari's lending infrastructure, but it also concentrated Fei's risk exposure in Rari's codebase.

## 3. The vulnerability

### 3.1 Reentrancy in cETH borrow/withdraw

The vulnerability was a reentrancy bug in the Fuse pool's cETH implementation. When a user called the borrow or withdraw function on the cETH market, the contract:

1. Checked the user's collateral and borrowing limits.
2. Transferred ETH to the user.
3. Updated the user's borrow balance in the contract's internal accounting.

The critical issue was that step 2 (ETH transfer) occurred before step 3 (state update). When the ETH transfer triggered the recipient's fallback function, the recipient could re-enter the cETH contract (or a related Fuse pool contract) before the borrow balance was updated. Because the state still reflected the pre-borrow balances, the reentrancy call could:

- Execute another borrow, effectively double-borrowing against the same collateral.
- Withdraw collateral that should have been locked by the outstanding borrow.
- Manipulate other related pool state in the window before the first borrow's accounting was finalized.

### 3.2 Violation of checks-effects-interactions

The vulnerability was a textbook violation of the checks-effects-interactions pattern — a fundamental Solidity security practice where:

1. **Checks**: Verify that the operation is valid (collateral sufficient, borrow limit not exceeded).
2. **Effects**: Update the contract's internal state (record the borrow, reduce available collateral).
3. **Interactions**: Perform external calls (transfer ETH to the borrower).

By performing the interaction (ETH transfer) before the effect (state update), the contract left a window for reentrancy. This pattern had been identified as a risk in Compound V2 forks by security researchers before the Rari exploit, but the specific Fuse pool implementation had not been remediated.

## 4. Attack execution

### 4.1 Exploit sequence

The attacker deployed a smart contract that interacted with vulnerable Fuse pools. The exploit sequence for each targeted pool was:

1. **Deposit collateral**: The attacker deposited tokens into the Fuse pool as collateral.
2. **Borrow ETH**: The attacker called the cETH borrow function, which transferred ETH to the attacker's contract.
3. **Reenter on callback**: In the attacker's contract's receive/fallback function (triggered by the ETH transfer), the contract re-entered the Fuse pool to execute additional borrows or withdraw the original collateral.
4. **Extract excess**: Because the pool's state had not been updated to reflect the first borrow, the reentrancy calls succeeded in borrowing or withdrawing more than the attacker's actual collateral justified.
5. **Repeat**: The attacker repeated this pattern across multiple Fuse pools, draining each one.

### 4.2 Multiple pools affected

The reentrancy vulnerability existed in multiple Fuse pools that supported cETH markets. The attacker systematically exploited pools with significant ETH and token deposits, extracting funds from each. The total extraction across all affected pools was approximately $80 million.

### 4.3 Fund movement

The attacker moved the stolen funds through a series of Ethereum addresses and used Tornado Cash to launder portions of the proceeds. The rapid use of Tornado Cash — within hours of the exploit — was consistent with an attacker who was aware of the tracing capabilities available to law enforcement and blockchain analytics firms.

## 5. Response and aftermath

### 5.1 Immediate response

Rari Capital and Fei Protocol's joint team detected the exploit within hours and paused the affected Fuse pool contracts to prevent further extraction. However, because Fuse pools were permissionless and numerous, the team needed to identify and pause each affected pool individually, which took time.

### 5.2 Fei Protocol governance crisis

The exploit triggered a governance crisis within the merged Rari-Fei entity:

- **PCV losses**: Fei Protocol's PCV suffered losses from its Fuse pool deposits, directly impacting the reserves backing the FEI stablecoin.
- **Victim-compensation debate**: The Fei community debated whether to use remaining PCV to compensate Fuse pool depositors. This created a conflict between FEI holders (whose stablecoin backing would be further reduced by compensation payments) and Fuse depositors (who had lost funds).
- **Governance vote**: A contentious governance vote was held on whether to allocate PCV to compensate victims. The proposal narrowly passed, but the debate exposed deep divisions within the community and eroded confidence in the merged entity's governance.

### 5.3 Fei Protocol shutdown

The combination of PCV losses, governance discord, and loss of community confidence ultimately led to Fei Protocol's decision to wind down operations. In August 2022, Fei Protocol announced that it would redeem all FEI stablecoins at par ($1) using remaining PCV and cease operations. The shutdown represented the effective end of both Fei Protocol and Rari Capital as active projects.

The Rari-Fei merger, originally intended to create a powerful DeFi conglomerate combining stablecoin and lending infrastructure, had instead created a concentrated risk that amplified the exploit's impact and destroyed both projects.

### 5.4 No fund recovery

The attacker's use of Tornado Cash made fund recovery extremely difficult. No significant recovery of the stolen $80 million was reported. The losses were borne by Fuse pool depositors (partially compensated from Fei's PCV) and, ultimately, by FEI stablecoin holders whose backing was reduced.

## 6. Market-health implications

### 6.1 Compound V2 fork risk

The Rari exploit highlighted a systemic risk in the DeFi ecosystem: the widespread use of Compound V2 forks as the basis for new lending protocols. Compound V2's cToken architecture is one of the most-forked codebases in DeFi, and each fork inherits not only the original code's features but also its potential vulnerabilities — particularly when the fork modifies the original code without fully understanding the security implications.

The reentrancy issue in cETH handling was a known risk in Compound V2 forks that had been documented by security researchers. However, the permissionless nature of Rari's Fuse platform meant that pools could be created and funded without individual security review, creating a large attack surface of potentially vulnerable contracts holding user funds.

For market surveillance, the proliferation of Compound V2 forks means that a vulnerability discovered in one fork may be exploitable across multiple protocols:

| Fork | Date | Loss | Vector |
|---|---|---|---|
| Rari Capital (Fuse) | Apr 2022 | ~$80M | cETH reentrancy |
| Hundred Finance | Apr 2023 | ~$7M | hToken exchange-rate manipulation |
| Midas Capital | Jan 2023 | ~$660K | Flash-loan collateral manipulation |

### 6.2 Permissionless pool creation as a risk amplifier

Rari's Fuse model — allowing anyone to create a lending pool with arbitrary parameters — democratized lending-pool creation but also distributed security responsibility to pool creators who may not have the expertise to assess smart-contract risks. Pool depositors relied on the underlying Fuse contract code being secure, but the permissionless model meant there was no curated review of pool parameters or asset compatibility.

This model amplifies risk because:

- **No human review**: Unlike Aave or Compound, where new assets are added through governance proposals with risk assessment, Fuse pools could include any ERC-20 token without review.
- **Fragmented liquidity**: Funds are spread across many pools, making it harder to coordinate security responses.
- **Heterogeneous risk profiles**: Each pool has different assets, parameters, and risk levels, making it difficult for depositors to assess the aggregate risk of the platform.

### 6.3 Protocol merger as a contagion channel

The Rari-Fei merger created a direct contagion channel: Fei's stablecoin treasury was exposed to Rari's smart-contract risk. When the Fuse pool exploit occurred, the damage cascaded from Rari's lending platform to Fei's stablecoin, ultimately destabilizing both protocols.

This contagion pattern is relevant for market health because DeFi protocol mergers and treasury deployments create hidden dependencies:

- When Protocol A deploys its treasury into Protocol B's yield strategies, Protocol A's solvency becomes dependent on Protocol B's security.
- Users of Protocol A (e.g., FEI stablecoin holders) may not be aware of this dependency or the smart-contract risks it introduces.
- A security failure in Protocol B can trigger a governance crisis and potential wind-down of Protocol A.

### 6.4 Governance under stress

The Fei community's contentious debate over victim compensation illustrated the challenges of DAO governance during crisis:

- **Competing stakeholder interests**: FEI holders and Fuse depositors had conflicting interests regarding the use of PCV for compensation.
- **Time pressure**: The governance process, designed for deliberative decision-making, was poorly suited to the urgency of a security incident response.
- **Confidence erosion**: The public debate eroded confidence in the merged entity's ability to manage risk, accelerating the project's decline.

For DeFi governance design, the Rari-Fei experience suggests that incident-response procedures — including pre-approved compensation frameworks and emergency action authorities — should be established before incidents occur, not debated during them.

## 7. Lessons learned and recommendations

### 7.1 For DeFi lending protocols

1. **Apply reentrancy guards to all ETH-handling functions**: Any function that transfers ETH must either use a reentrancy guard (`nonReentrant`) or strictly follow the checks-effects-interactions pattern (update state before transferring ETH).

2. **Audit fork-specific modifications**: When forking Compound V2 or other base protocols, conduct security audits that specifically examine modifications to the original code and their interaction with the original security assumptions.

3. **Review permissionless pool risks**: If offering permissionless pool creation, implement contract-level protections against known vulnerability classes (reentrancy, oracle manipulation, flash-loan attacks) that do not depend on pool creators' security expertise.

### 7.2 For protocol mergers and treasury management

1. **Assess smart-contract risk of deployment targets**: Before deploying protocol treasury into another protocol's yield strategies, conduct or commission a security review of the target protocol's contracts.

2. **Limit single-protocol exposure**: Cap the proportion of treasury deployed in any single protocol to limit contagion from a single exploit.

3. **Establish pre-incident compensation frameworks**: Define in advance how losses from deployment-target exploits will be handled, including whether and how treasury funds will be used for victim compensation.

### 7.3 For market surveillance

1. **Track Compound V2 fork deployments**: Maintain awareness of protocols built on Compound V2 forks, as they share a common vulnerability surface.

2. **Monitor permissionless lending pool TVL**: Track value locked in permissionless lending platforms where pool-level security review may be absent.

3. **Detect treasury deployment dependencies**: Map where major protocol treasuries are deployed and monitor those deployment targets for security incidents.

## 8. Conclusion

The Rari Capital Fuse pool exploit of April 2022 demonstrated how a known vulnerability class — cETH reentrancy in a Compound V2 fork — could result in an $80 million loss when deployed at scale in a permissionless lending platform. The exploit's contagion through the Rari-Fei merger destroyed Fei Protocol's stablecoin reserves and triggered a governance crisis that led to both projects' shutdown.

The incident underscored three structural DeFi risks: the proliferation of Compound V2 fork vulnerabilities across multiple protocols, the risk amplification of permissionless pool creation without per-pool security review, and the contagion channel created when protocol treasuries are deployed into other protocols' smart contracts. For the broader market, the Rari-Fei case demonstrated that DeFi protocol mergers can concentrate risk rather than diversify it, and that governance mechanisms designed for routine operations may fail under the stress of a major security incident.
