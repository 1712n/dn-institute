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
3. **The attack was executed across multiple tokens**: the attacker drained DAI, USDC, WBTC, stETH, and other assets from Euler's lending pools. Flash loans from Aave provided the initial capital, and the attack was replicated by several copycat attackers within hours.
4. **The attacker returned all stolen funds** over the following three weeks after negotiations between Euler, the attacker, and on-chain intermediaries. Euler offered a $1 million bounty for information and engaged in direct on-chain communication. The attacker ultimately returned the full amount, reportedly citing personal security concerns after blockchain analysis firms published leads.
5. **The Euler exploit highlighted a class of vulnerability specific to lending protocols**: accounting functions that modify a user's collateral or debt position without re-validating the health factor. The `donateToReserves` function had been audited multiple times but the interaction with the self-liquidation path was not caught.

## Background

Euler Finance was an Ethereum-based lending protocol that launched in December 2022 (v2 of the protocol). It differentiated itself from competitors like Aave and Compound through features including permissionless lending markets (any ERC-20 token could be listed), reactive interest rates, and a tiered asset classification system (collateral, cross, isolated) that aimed to balance capital efficiency with risk management.

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
| Largest pools | DAI (~$80M), USDC (~$50M), WBTC (~$40M), stETH (~$30M) |
| Health factor threshold | 1.0 (positions below this are liquidatable) |
| Liquidation discount | Varies by asset tier (typically 5-20%) |
| `donateToReserves` health check | **None** — this was the vulnerability |
| Self-liquidation | Allowed (a borrower could liquidate their own position) |
| Flash loan protection | None specific to the donation/liquidation interaction |

The critical vulnerability was that `donateToReserves` reduced the caller's eToken balance (collateral) without checking whether the resulting position was still healthy. Combined with the ability to self-liquidate, this created an exploit path.

## Technical Exploit Mechanics

### Attack Overview

The attack followed a precise sequence designed to extract maximum value from each lending pool. The attacker repeated this pattern for DAI, USDC, WBTC, and stETH pools.

**Step 1 — Flash Loan Capital Acquisition**:
- The attacker flash-borrowed a large amount of the target token (e.g., 30 million DAI) from Aave
- This capital was needed to create the initial leveraged position on Euler

**Step 2 — Create Leveraged Position**:
- Deposited the flash-borrowed tokens into Euler, receiving eTokens
- Used Euler's `mint` function to create additional leveraged exposure: minting more eTokens and corresponding dTokens simultaneously
- This created a position with high collateral (eTokens) and high debt (dTokens), but with a health factor above 1.0 due to the overcollateralization

For example, with the DAI pool:
- Deposit 30M DAI → receive ~30M eDAI
- Mint 195M eDAI + 195M dDAI (10x leverage via repeated minting)
- Position: ~225M eDAI collateral, ~195M dDAI debt, health factor > 1.0

**Step 3 — Donate Collateral to Destroy Health Factor**:
- Called `donateToReserves` to transfer a large portion of the eTokens to the protocol reserves
- This reduced the attacker's collateral without reducing their debt
- **Crucially, `donateToReserves` did not check the health factor after the donation**
- Result: the attacker's position became severely undercollateralized (health factor far below 1.0)

Continuing the example:
- Donate ~100M eDAI to reserves
- Position: ~125M eDAI collateral, ~195M dDAI debt → health factor well below 1.0

**Step 4 — Self-Liquidate for Profit**:
- Using a second account (also controlled by the attacker), liquidated the now-undercollateralized first account
- The liquidator account repaid a portion of the debt and received discounted collateral
- Because the position was so deeply undercollateralized, the liquidation transferred a significant amount of eTokens at a discount
- The attacker then redeemed the eTokens for the underlying asset

The profit came from the difference between:
- The value of collateral received through liquidation (at discount)
- The debt repaid during liquidation
- Plus: the donated eTokens effectively came from the protocol's reserves, meaning the attacker extracted value that belonged to other depositors

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

## Copycat Attacks

Within hours of the initial exploit, additional attackers replicated the same technique against Euler pools that the original attacker had not yet drained. These copycat attacks extracted additional funds, though the amounts were smaller because the original attacker had already targeted the largest pools.

The rapid replication demonstrated that:
- The exploit was publicly visible on-chain once the first transactions were executed
- MEV bots and security researchers could reverse-engineer the attack pattern quickly
- Protocols with active exploits face a race condition: they must pause before copycats arrive

Euler paused the protocol contracts after the original attack was detected, but some copycat transactions had already succeeded.

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
| April 4 | Euler confirms full recovery of all exploited funds |

### Why the Attacker Returned Funds

Several factors reportedly contributed to the full fund return:

- **Blockchain analytics pressure**: Firms including Chainalysis tracked the stolen funds and published leads connecting on-chain activity to potential real-world identities
- **Legal exposure**: Euler engaged law enforcement and legal counsel, creating credible threat of prosecution
- **On-chain communication**: Direct messaging between Euler and the attacker via Ethereum transaction calldata facilitated negotiation
- **Community pressure**: The Euler community and broader DeFi ecosystem publicly tracked the attacker's movements
- **Incomplete mixing**: The attacker used Tornado Cash for some funds, but the scale of the theft ($197M) made full anonymization extremely difficult

## Market Impact

### EUL Token

| Metric | Pre-Exploit | Post-Exploit (48h) | 1 Week Post |
|--------|-------------|-------------------|-------------|
| EUL price | ~$5.50 | ~$2.80 | ~$3.20 |
| Price decline | — | ~49% | ~42% (partial recovery on return news) |

### Protocol TVL

- Pre-exploit: ~$264M
- Post-exploit: effectively $0 (protocol paused)
- After fund recovery: Euler v1 remained paused; the team later launched Euler v2 with redesigned architecture

### Broader DeFi Lending Impact

- **Health check audit pattern**: The exploit established a new audit checklist item — every function that modifies a user's collateral or debt position must include a health factor check. This became a standard finding category in subsequent lending protocol audits.
- **Donation function scrutiny**: Several other lending protocols reviewed their own donation or reserve-contribution functions for similar missing health checks
- **Self-liquidation restrictions**: Some protocols implemented restrictions on self-liquidation or added additional checks when the liquidator and borrower share common ownership signals

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

4. **Copycat attack speed**: The Euler copycats arrived within hours. For protocols under active exploit, the time between initial attack detection and contract pause is the window during which copycat attacks succeed. Surveillance systems that can detect the first attack transaction and alert protocol operators within minutes provide significant value.

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
