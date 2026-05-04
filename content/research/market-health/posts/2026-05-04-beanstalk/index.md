---
title: "🌰 Beanstalk Farms — Flash Loan Governance Attack and $182M Protocol Drain"
date: 2026-05-04
entities:
  - Beanstalk
  - BEAN
  - Aave
  - Uniswap
  - SushiSwap
  - Curve
  - Ethereum
---

## Summary

1. **On April 17, 2022, the Beanstalk Farms protocol was exploited for approximately $182 million** through a governance attack that used flash-loaned tokens to pass and execute malicious governance actions. Public analyses estimate the attacker's net profit at roughly $76-80 million after flash-loan repayment and swaps.
2. **The attack exploited Beanstalk's governance mechanism**, which allowed temporary voting power to trigger emergency execution after the malicious proposals had been staged. The attacker flash-loaned roughly $1 billion in liquidity, accumulated sufficient governance power (Stalk tokens) through Curve pool deposits, voted to pass malicious proposals, and drained the protocol — all within a single Ethereum transaction.
3. **The governance design flaw** was that Beanstalk's voting power was determined by current token holdings (specifically, Stalk accumulated from depositing assets into the Silo), with no time-lock, snapshot mechanism, or multi-block voting requirement. This meant temporarily held tokens could exercise permanent governance authority.
4. **BEAN, the protocol's algorithmic stablecoin, lost its $1 peg sharply** immediately after the exploit as the protocol's backing was drained. Reports placed post-exploit lows in a wide range, and Beanstalk's TVL collapsed as Silo liquidity was removed.
5. **Beanstalk Farms relaunched ("Beanstalk Replanted") in August 2022** with redesigned governance and recapitalization efforts, though the original exploit left a large unrecovered loss.

## Background

Beanstalk was a credit-based algorithmic stablecoin protocol on Ethereum, launched in August 2021. Unlike collateral-backed stablecoins (USDC, DAI), Beanstalk maintained BEAN's $1 peg through:

- **Silo deposits**: Users deposited BEAN and BEAN-paired LP tokens (BEAN:3CRV, BEAN:ETH) into the "Silo," earning Stalk (governance power) and Seeds (future Stalk accrual)
- **Field mechanism**: When BEAN traded below $1, the protocol offered "Pods" (debt instruments) at premium interest rates, incentivizing buying and depositing BEAN
- **Seasons**: Regular intervals (~1 hour) when the protocol evaluated its peg and adjusted incentives

The governance token was Stalk, which was earned by depositing assets in the Silo. Stalk holders could propose and vote on Beanstalk Improvement Proposals (BIPs). The critical governance parameters at the time of the attack:

| Parameter | Value |
|-----------|-------|
| Voting power | Stalk balance at time of vote |
| Proposal threshold | Majority of participating Stalk |
| Voting period | Proposals executable after 1 day and sufficient votes |
| Execution mechanism | On-chain, callable by anyone after passing |
| Snapshot mechanism | None — live balance used |

## 🌰 Technical Exploit Mechanics

### Attack Transaction Overview

The entire attack was executed in a single Ethereum transaction (block 14602790), consisting of the following sequence:

**Step 1 — Flash-loan acquisition (roughly $1 billion)**:
- Borrowed 350M DAI, 500M USDC, 150M USDT from Aave V2 flash loans
- Borrowed additional BEAN and LUSD from other sources

**Step 2 — Liquidity pool manipulation**:
- Deposited the borrowed stablecoins into Curve's 3CRV pool and the BEAN:3CRV Curve metapool
- This gave the attacker a massive position in BEAN:3CRV LP tokens

**Step 3 — Governance power acquisition**:
- Deposited the BEAN:3CRV LP tokens into Beanstalk's Silo
- This immediately granted Stalk (governance voting power) proportional to the deposit size
- The flash-loaned position was large enough to constitute a supermajority of all Stalk

**Step 4 — Malicious proposal execution**:
- The attacker had submitted BIP-18 and BIP-19 (malicious governance proposals) in advance, during the normal proposal period
- BIP-18 contained the malicious logic that transferred Silo assets to the attacker's wallet
- A related proposal/action sent $250,000 to the Ukraine crypto donation address, widely interpreted as a publicity or obfuscation element
- With supermajority Stalk, the attacker called `emergencyCommit()` to instantly pass and execute BIP-18

**Step 5 — Asset extraction**:
- BIP-18 execution drained the Silo of all deposited assets
- The attacker received BEAN, 3CRV, BEAN:3CRV LP, BEAN:ETH LP, and LUSD tokens
- Converted all assets to ETH and stablecoins

**Step 6 — Flash loan repayment**:
- Repaid all Aave flash loans plus fees
- Net profit: roughly $76-80 million in ETH and stablecoins, depending on accounting methodology

### Why the Attack Worked

The fundamental issue was a **governance design that treated temporarily held tokens identically to long-term holdings**:

1. **No snapshot voting**: Stalk balances were checked at the moment of voting, not at a historical block. Flash-loaned tokens that existed for a single block had the same voting power as tokens held for months.
2. **No time-lock on governance power**: Newly deposited assets immediately received full Stalk. There was no vesting period or minimum holding duration before governance rights activated.
3. **`emergencyCommit()` allowed same-transaction execution**: While regular BIPs required a waiting period, the `emergencyCommit()` function allowed proposals to be passed and executed in the same transaction if they achieved a supermajority — enabling flash-loan-based governance capture.

## 🌰 Market Impact

### BEAN Stablecoin Collapse

| Metric | Pre-Exploit | Post-Exploit |
|--------|-------------|-------------|
| BEAN price | ~$1.00 | Severe depeg reported |
| Protocol TVL | ~$150M | Collapsed after Silo drain |
| BEAN:3CRV pool | ~$75M liquidity | Drained |
| BEAN:ETH pool | ~$25M liquidity | Drained |

The collapse was immediate and severe. With the protocol's backing assets drained, BEAN had no effective mechanism to maintain its peg during the crisis.

### Broader DeFi Impact

- **Algorithmic stablecoin confidence**: The Beanstalk exploit, occurring just one month before the Terra/Luna collapse (May 2022), contributed to growing skepticism about algorithmic stablecoin designs
- **Governance security awareness**: The attack became a reference case for "flash loan governance attacks," prompting multiple DeFi protocols to audit their governance mechanisms
- **Curve pool impact**: The BEAN:3CRV pool on Curve was drained, but broader Curve operations were unaffected as the pool was isolated

## On-Chain Fund Flow

### Attacker's Post-Exploit Movement

The attacker's primary Ethereum address processed the stolen funds as follows:

1. **Immediate conversion**: All non-ETH tokens were swapped to ETH via DEX aggregators
2. **Tornado Cash deposits**: A large share of the ETH proceeds was deposited into Tornado Cash after the exploit
3. **Tracing challenge**: The mixer flow made recovery and attribution materially harder, even though the source transaction and initial swaps remained visible on-chain

### Protocol Response

- **April 17**: Beanstalk Farms governance paused
- **April 18**: Beanstalk Farms published post-mortem and announced community recovery plan
- **June 2022**: "Barn Raise" community funding campaign to recapitalize the protocol
- **August 2022**: "Beanstalk Replanted" launched with redesigned governance
- The relaunched protocol introduced governance and security changes intended to reduce single-transaction governance-capture risk

## Governance Vulnerability Analysis

### Flash Loan Governance Attack Pattern

The Beanstalk exploit established a template for flash loan governance attacks:

1. **Identify a protocol where governance power is derived from current token holdings** rather than historical snapshots
2. **Verify that an already-staged proposal can be executed in the same transaction as temporary voting power is acquired**
3. **Submit a malicious proposal** during a normal proposal window and wait for the voting period to become active
4. **Flash loan sufficient tokens** to achieve the required voting threshold
5. **Vote and execute the already-staged proposal** within a single transaction, before the flash loan must be repaid
6. **Drain the protocol's assets** through the governance-approved proposal

This pattern is only possible when all three conditions are met: live-balance voting, same-transaction execution, and sufficient flash loan liquidity. Removing any one condition prevents the attack.

### Comparison to Traditional Governance Attacks

| Aspect | Traditional 51% Attack | Flash Loan Governance |
|--------|----------------------|---------------------|
| Capital required | Must buy and hold tokens | Temporary borrowed capital plus fees/slippage |
| Duration of control | Persistent | Single transaction |
| Detection window | Days to weeks | Seconds (single block) |
| Economic cost to attacker | Market impact of accumulation | Flash-loan fees, gas, slippage, and execution risk |
| Reversibility | Difficult (tokens held) | Automatic (flash loan repaid) |

The flash-loan governance attack is particularly dangerous because the attacker does not need to permanently acquire governance power and the detection window can compress to a single block.

## Lessons for Market Surveillance

1. **Governance snapshot requirements**: Any DeFi protocol where governance power is determined by live token balances rather than historical snapshots is vulnerable to flash loan governance capture. Surveillance systems should flag protocols lacking time-weighted or snapshot-based voting.

2. **Emergency execution functions**: Functions like `emergencyCommit()` that allow same-transaction proposal execution create attack surface. These functions should require multi-block or multi-transaction confirmation, even in emergency scenarios.

3. **Flash loan volume monitoring**: Unusually large flash loans, particularly those involving governance-relevant tokens, should trigger real-time alerts. The Beanstalk attacker's $1 billion flash loan was orders of magnitude larger than typical flash loan activity.

4. **Proposal content analysis**: Governance proposals that transfer protocol assets to external addresses should receive heightened scrutiny. BIP-18's payload — draining the entire Silo — was a transparent theft mechanism that could have been flagged by automated proposal content analysis.

5. **Governance participation anomalies**: A sudden spike in governance participation from a previously inactive address, particularly at levels sufficient to reach the required threshold, is an anomaly worth alerting on. The attacker's Stalk holdings went from zero to supermajority within a single block.

6. **Time-lock enforcement**: Governance changes affecting treasury or protocol-owned assets should have mandatory time-locks that cannot be bypassed by emergency functions. Multi-day execution delays provide a window for community review and intervention.

## References

1. Beanstalk Farms. "Beanstalk Governance Exploit — Post-Mortem." Beanstalk Farms Blog, April 18, 2022.
2. PeckShield. "Beanstalk Exploit Analysis — Flash Loan Governance Attack." PeckShield Alert, April 17, 2022.
3. CertiK. "Beanstalk Farms Deep Dive: Understanding the Flash Loan Governance Exploit." CertiK Research, April 2022.
4. Chainalysis. "The 2023 Crypto Crime Report." Chapter 4: DeFi Exploits. Chainalysis Inc., January 2023.
5. Rekt News. "Beanstalk — REKT." rekt.news, April 17, 2022.
6. Etherscan. "Transaction 0xcd314668aaa9bbfebaf1a0bd2b6553d01dd58899c508d4729fa7311dc5d33ad7." Ethereum Mainnet Block 14602790.
7. Aave. "Flash Loans V2 Documentation." Aave Protocol, 2022.
