---
title: "🌰 Euler Finance — Donation Function Accounting Flaw and $197M Lending Protocol Drain"
date: 2026-05-04
entities:
  - Euler Finance
  - EUL
  - Ethereum
  - Aave
  - Balancer
  - DAI
  - USDC
  - WBTC
  - stETH
---

## Summary

1. **On March 13, 2023, the Euler Finance lending protocol was exploited for approximately $197 million** through a flash-loan-powered attack that abused a flaw in the protocol's donation function. The attacker leveraged an interaction between the `donateToReserves` function and the protocol's health factor calculation to create artificially undercollateralized positions that could be self-liquidated for profit.
2. **The root cause was that the `donateToReserves` function** allowed a borrower to reduce their own collateral (by donating their eTokens — Euler's interest-bearing deposit tokens — to the protocol reserves) without a corresponding health check. This meant a borrower could deliberately make their own position undercollateralized and then exploit the resulting liquidation opportunity.
3. **The attack was executed across multiple tokens**: the attacker drained DAI, USDC, WBTC, stETH, WETH, and related assets from Euler's lending pools. Flash loans from Aave provided the initial capital, and at least one MEV/front-running transaction copied part of the pattern as the exploit became visible on-chain.
4. **Euler later reported recovery of all recoverable exploited funds** after negotiations between Euler, the attacker, and on-chain intermediaries. Euler offered a $1 million bounty for information and engaged in direct on-chain communication before a sequence of returned-fund transactions.
5. **The Euler exploit highlighted a class of vulnerability specific to lending protocols**: accounting functions that modify a user's collateral or debt position without re-validating the health factor. The `donateToReserves` function had been audited multiple times but the interaction with the self-liquidation path was not caught.

## Background

Euler Finance was an Ethereum-based lending protocol. It differentiated itself from competitors like Aave and Compound through features including permissionless lending markets, reactive interest rates, and a tiered asset classification system (collateral, cross, isolated) that aimed to balance capital efficiency with risk management.

### Protocol Architecture

The key components relevant to the exploit:

- **eTokens**: Interest-bearing deposit tokens representing a user's share of a lending pool. When a user deposited DAI, they received eDAI proportional to their share of the pool.
- **dTokens**: Debt tokens representing a user's outstanding borrow. When a user borrowed USDC, dTokens tracked their debt including accrued interest.
- **Health Factor**: A ratio comparing the risk-adjusted value of a user's collateral (eTokens) to their debt (dTokens). A health factor below 1.0 made the position eligible for liquidation.
- **Liquidation**: When a position's health factor dropped below 1.0, liquidators could repay a portion of the borrower's debt and receive discounted collateral in return.
- **`donateToReserves`**: A function that allowed eToken holders to voluntarily transfer their eTokens to the protocol's reserve pool. This was intended as a mechanism for users to contribute to the protocol's insurance fund.
- **Leverage via `mint`**: Euler allowed users to create leveraged positions by minting eTokens and dTokens simultaneously — effectively depositing and borrowing in the same transaction to amplify exposure.

### Key Design Parameters at Exploit Time

| Parameter | Value |
|-----------|-------|
| Protocol TVL | ~$264M across all lending pools |
| Major affected assets | DAI, USDC, WBTC, WETH/stETH-related exposure |
| Health factor threshold | 1.0 (positions below this are liquidatable) |
| Liquidation discount | Varies by asset tier (typically 5-20%) |
| `donateToReserves` health check | **None** — this was the vulnerability |
| Self-liquidation | Allowed (a borrower could liquidate their own position) |
| Flash loan protection | None specific to the donation/liquidation interaction |

The critical vulnerability was that `donateToReserves` reduced the caller's eToken balance (collateral) without checking whether the resulting position was still healthy. Combined with the ability to self-liquidate, this created an exploit path.

## Technical Exploit Mechanics

### Attack Overview

The attack followed a repeated sequence designed to extract value from multiple lending pools. Public analyses describe variants of this pattern across DAI, USDC, WBTC, WETH, and stETH-related markets.

**Step 1 — Flash Loan Capital Acquisition**:
- The attacker flash-borrowed a large amount of the target token (e.g., 30 million DAI) from Aave
- This capital was needed to create the initial leveraged position on Euler

**Step 2 — Create Leveraged Position**:
- Deposited the flash-borrowed tokens into Euler, receiving eTokens
- Used Euler's `mint` function to create additional leveraged exposure: minting more eTokens and corresponding dTokens simultaneously
- This created a position with high collateral (eTokens) and high debt (dTokens), but with a health factor above 1.0 due to the overcollateralization

For example, in the DAI pool analyses:
- Flash-borrow tens of millions of DAI from Aave
- Deposit a portion into Euler, receiving eDAI collateral
- Use Euler's `mint` function to create a much larger same-asset eDAI/dDAI leveraged position
- Repay part of the debt and mint again, leaving a highly leveraged position that still passed normal checks before the donation step

**Step 3 — Donate Collateral to Destroy Health Factor**:
- Called `donateToReserves` to transfer a large portion of the eTokens to the protocol reserves
- This reduced the attacker's collateral without reducing their debt
- **Crucially, `donateToReserves` did not check the health factor after the donation**
- Result: the attacker's position became severely undercollateralized (health factor far below 1.0)

Continuing the example:
- Donate a large block of eDAI to reserves
- The account keeps its debt while its usable collateral falls sharply
- The position becomes deeply undercollateralized without the donation function enforcing the usual liquidity check

**Step 4 — Self-Liquidate for Profit**:
- Using a second account (also controlled by the attacker), liquidated the now-undercollateralized first account
- The liquidator account repaid a portion of the debt and received discounted collateral
- Because the position was so deeply undercollateralized, the liquidation transferred a significant amount of eTokens at a discount
- The attacker then redeemed the eTokens for the underlying asset

The profit came from the difference between:
- The value of collateral received through liquidation (at discount)
- The debt repaid during liquidation
- Plus: the liquidation and withdrawal path converted the deliberately created bad-debt state into withdrawable underlying assets from the affected pool

**Step 5 — Repay Flash Loan and Repeat**:
- Repaid the Aave flash loan
- Repeated the process for other lending pools (USDC, WBTC, stETH)

### Why the Donation Function Was Vulnerable

The `donateToReserves` function was conceptually simple: transfer eTokens from the caller's balance to the reserve pool. The implementation performed the transfer correctly, but it omitted a critical step that other balance-modifying functions included:

1. **`deposit`/`withdraw`**: These functions checked the health factor after modifying the user's eToken balance
2. **`borrow`/`repay`**: These functions checked the health factor after modifying the user's dToken balance
3. **`donateToReserves`**: This function modified the user's eToken balance **without** a subsequent health check

The omission was subtle because:
- The function was intended for voluntary, altruistic use — "why would someone donate their collateral if it would make them liquidatable?"
- In isolation, donating to reserves seems harmless — the donor loses value, and the protocol gains it
- The exploit required combining donation with self-liquidation and leveraged minting, a multi-step interaction that was not intuitive during auditing

### Multiple Audits Missed the Bug

Euler's contracts were audited by multiple firms. The `donateToReserves` function was present in the audited code, but the interaction between donation, health factor, and self-liquidation was not identified as a vulnerability. This highlights a limitation of manual code audits: they excel at finding individual function-level bugs but can miss emergent risks that arise from the interaction of multiple correct-in-isolation functions.

## MEV and Copycat Dynamics

As the exploit transactions became visible, other actors could inspect and attempt to copy or front-run parts of the pattern. Public incident writeups noted at least one MEV/front-running transaction that copied exploit logic and diverted DAI before later returning or transferring it onward.

The rapid visibility demonstrated that:
- The exploit was publicly visible on-chain once the first transactions were executed
- MEV bots and security researchers could reverse-engineer the attack pattern quickly
- Protocols with active exploits face a race condition: they must pause before copycats or opportunistic searchers amplify losses

Euler paused protocol activity after the attack was detected, but the incident still showed how quickly a transaction-level exploit recipe can spread.

## Fund Recovery Timeline

| Date | Event |
|------|-------|
| March 13 | Attack executed; Euler pauses protocol; approximately $197M drained |
| March 14 | Euler offers $1M bounty for information leading to attacker identification |
| March 15 | Euler sends on-chain message to attacker requesting fund return |
| March 16 | Attacker sends 100 ETH to a Ronin Bridge exploit victim address (possibly misdirected or a gesture) |
| March 18 | Attacker sends on-chain message to Euler: begins negotiation |
| March 20 | Attacker returns 3,000 ETH (~$5.4M) as initial gesture |
| March 25 | Attacker returns substantial portion of remaining funds |
| March 28 | Euler confirms that the bulk of stolen funds have been returned |
| April 4 | Euler says all recoverable exploited funds have been returned |

### Why the Attacker Returned Funds

Several factors likely contributed to the returned-fund outcome:

- **Blockchain analytics pressure**: Security researchers and analytics firms tracked the stolen funds and publicized address clusters and leads
- **Legal exposure**: Euler engaged law enforcement and legal counsel, creating credible threat of prosecution
- **On-chain communication**: Direct messaging between Euler and the attacker via Ethereum transaction calldata facilitated negotiation
- **Community pressure**: The Euler community and broader DeFi ecosystem publicly tracked the attacker's movements
- **Incomplete mixing**: A small amount was moved through Tornado Cash early in the incident, but the scale of the theft made full anonymization difficult

## Market Impact

### EUL Token

| Metric | Pre-Exploit | Post-Exploit (48h) | 1 Week Post |
|--------|-------------|-------------------|-------------|
| EUL price | Around mid-single digits | Sharp decline | Partial recovery on return news |
| Price impact | — | Reported as roughly 50% at the trough in some coverage | Still below pre-exploit levels |

### Protocol TVL

- Pre-exploit public TVL was reported around `$264M`
- Post-exploit TVL fell sharply as the protocol paused and assets were drained or withdrawn
- After fund recovery, Euler v1 did not immediately return to its prior operating scale

### Broader DeFi Lending Impact

- **Health check audit pattern**: The exploit reinforced an audit checklist item — every function that modifies a user's collateral or debt position must preserve or re-check the health-factor invariant.
- **Donation function scrutiny**: Several other lending protocols reviewed their own donation or reserve-contribution functions for similar missing health checks
- **Self-liquidation restrictions**: The incident pushed reviewers to scrutinize self-liquidation and related-account liquidation paths more closely

## Vulnerability Pattern: Missing Invariant Check on State-Modifying Functions

### The General Pattern

The Euler exploit belongs to a class of vulnerabilities where a state-modifying function omits a critical invariant check that other similar functions include:

1. **Identify a protocol invariant**: In lending protocols, the health factor invariant (collateral value > debt value, adjusted for risk) must hold for every non-liquidatable position
2. **Find a function that modifies state relevant to the invariant**: `donateToReserves` modifies eToken balance, which directly affects health factor
3. **Check whether the function re-validates the invariant after modification**: If not, the function can be used to break the invariant
4. **Combine with a profit-extraction mechanism**: Self-liquidation converts the broken invariant into extractable value

### Comparison to Other Lending Protocol Exploits

| Protocol | Date | Loss | Vulnerability |
|----------|------|------|--------------|
| Euler Finance | Mar 2023 | ~$197M | Missing health check on `donateToReserves` |
| Compound (cETH) | Sep-Oct 2021 | ~$147M | Incorrect reward distribution in `drip` function |
| Cream Finance | Oct 2021 | ~$130M | Flash loan oracle + self-referential token pricing |
| Mango Markets | Oct 2022 | ~$114M | Oracle manipulation via illiquid perp market |
| Aave (indirect) | Nov 2022 | ~$1.6M | CRV market manipulation attempt via Aave borrowing |

Each of these exploits targeted a different aspect of lending protocol accounting, but they share a common theme: the economic model assumed certain user behaviors (rational self-interest, no self-harm) that did not hold when combined with flash loans, self-liquidation, or cross-protocol interactions.

## Lessons for Market Surveillance

1. **Monitor donation and reserve-contribution functions**: Any lending protocol function that allows users to voluntarily reduce their own collateral should be flagged for health-check verification. Surveillance systems should alert on large donations to reserves, especially when followed by liquidation activity on the same or related addresses.

2. **Self-liquidation as an exploit signal**: A user liquidating their own position (same EOA or linked addresses as both borrower and liquidator) immediately after a donation or collateral reduction is a strong exploit indicator. This pattern should trigger real-time alerts.

3. **Leveraged position creation followed by collateral reduction**: The creation of a maximally leveraged position (repeated minting) followed by a large `donateToReserves` call in the same block or transaction sequence is the complete attack signature. Monitoring for this specific sequence can detect Euler-style attacks as they happen.

4. **Copycat/MEV speed**: Once an exploit recipe is public on-chain, copycats and searchers can arrive quickly. For protocols under active exploit, the time between initial attack detection and contract pause is the window during which opportunistic transactions can amplify losses.

5. **Flash loan origination correlation**: Large flash loan borrows from Aave or other flash loan providers, followed within the same transaction by interactions with a lending protocol's collateral-modifying functions, should be monitored as potential exploit transactions.

6. **Audit coverage gaps**: The Euler exploit was present in audited code but was missed because the vulnerability emerged from the interaction of multiple individually correct functions. Surveillance systems should maintain a database of known vulnerability patterns (missing health checks, self-referential pricing, etc.) and scan new protocol deployments for structural similarities.

## References

1. Euler Finance. "Euler Exploit Post-Mortem." Euler Finance Blog, March 2023.
2. Omniscia. "Euler Finance Incident Report." Omniscia Security, March 13, 2023.
3. BlockSec. "Euler Finance Exploit Analysis." BlockSec Blog, March 13, 2023.
4. Rekt News. "Euler Finance — REKT." rekt.news, March 13, 2023.
5. Chainalysis. "Inside the Euler Finance Exploit and Fund Recovery." Chainalysis Blog, April 2023.
6. Trail of Bits. "Lessons from the Euler Finance Exploit." Trail of Bits Blog, 2023.
7. Sherlock. "Euler Finance Exploit — Audit Retrospective." Sherlock Blog, March 2023.
