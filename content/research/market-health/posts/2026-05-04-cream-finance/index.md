---
title: "🌰 Cream Finance — Flash Loan Price Oracle Exploit and $130M Lending Pool Drain"
date: 2026-05-04
entities:
  - Cream Finance
  - CREAM
  - Ethereum
  - Yearn Finance
  - Curve Finance
  - Aave
  - Iron Bank
  - yUSD
---

## Summary

1. **On October 27, 2021, the Cream Finance lending protocol suffered its third major exploit**, losing approximately $130 million in what was then one of the largest flash loan attacks in DeFi history. The attacker manipulated the price oracle for Yearn's yUSD vault token to inflate collateral value, then borrowed against this inflated collateral across Cream's lending pools.
2. **The core vulnerability was Cream's reliance on the internal exchange rate of yUSD** (a Yearn vault token representing a share of a Curve stablecoin pool) as a price oracle for collateral valuation. The attacker could manipulate this exchange rate by directly depositing tokens into the underlying Curve pool, inflating the per-share value that Cream used to assess collateral worth.
3. **The attack required approximately $1.5 billion in flash-loaned capital** sourced from multiple DeFi protocols including Aave and Cream itself (via its Iron Bank integration). This capital was used to simultaneously manipulate the yUSD price and borrow against the inflated collateral.
4. **The stolen funds were not returned**, and the attacker routed proceeds through Tornado Cash and various DeFi protocols. Unlike the Poly Network or Euler exploits, there was no negotiated recovery. Cream's depleted reserves meant that depositors in the affected pools suffered permanent losses.
5. **Cream Finance had been exploited twice before** — in February 2021 (~$37.5M via an Alpha Finance flash loan) and August 2021 (~$18.8M via a reentrancy bug in the AMP token). The October attack effectively ended Cream as a significant DeFi lending protocol, with TVL collapsing from hundreds of millions to near zero.

## Background

Cream Finance was a permissionless lending protocol forked from Compound Finance. It differentiated itself by listing a wide variety of tokens as collateral — including LP tokens, vault tokens, and long-tail assets that Aave and Compound would not accept. While this permissive listing policy attracted capital and users, it also expanded the protocol's attack surface by requiring price oracles for complex, composable DeFi tokens.

### Protocol Architecture

The key components relevant to the attack:

- **crTokens**: Cream's interest-bearing deposit tokens (equivalent to Compound's cTokens). Depositing USDC yielded crUSDC, representing a share of the USDC lending pool.
- **Collateral Markets**: Cream allowed a wide range of tokens to be used as collateral, including Yearn vault tokens (yTokens), Curve LP tokens, and other DeFi derivatives.
- **Price Oracle for Vault Tokens**: For Yearn vault tokens like yUSD, Cream calculated collateral value using the vault's `pricePerShare` — the internal exchange rate between the vault token and the underlying assets. This rate is determined by the vault's total assets divided by its total token supply.
- **Iron Bank**: A separate lending market within the Cream ecosystem designed for protocol-to-protocol lending, featuring higher leverage limits and whitelist-based access. Iron Bank shared infrastructure with Cream's main market.

### Key Design Parameters at Exploit Time

| Parameter | Value |
|-----------|-------|
| Protocol TVL | ~$300M across all markets |
| yUSD collateral factor | Varied; sufficient to allow significant borrowing |
| yUSD price oracle | Yearn vault `pricePerShare` (internal exchange rate) |
| Flash loan sources | Aave, dYdX, Cream/Iron Bank internal |
| Number of listed collateral types | 60+ tokens including LP tokens and vault tokens |
| Prior exploits | Feb 2021 (~$37.5M), Aug 2021 (~$18.8M) |

The vulnerability centered on using `pricePerShare` as a price oracle. This value represents the vault's net asset value per share, which can be manipulated by anyone who can change the vault's underlying asset balance — including through direct deposits into the underlying Curve pool.

## Technical Exploit Mechanics

### Attack Overview

The attack was executed in a single Ethereum transaction, orchestrated through a custom contract that coordinated flash loans, price manipulation, and borrowing across multiple protocols.

**Step 1 — Massive Flash Loan Acquisition**:

The attacker sourced approximately $1.5 billion in flash-loaned capital from multiple protocols:
- Flash loans from Aave (ETH, DAI, USDC)
- Flash loans from Cream/Iron Bank
- The total capital was needed both to manipulate the yUSD price and to establish collateral positions

The scale of the flash loan was remarkable — it required nearly all available flash loan liquidity across multiple major protocols simultaneously.

**Step 2 — yUSD Price Manipulation**:

The yUSD vault token's `pricePerShare` was calculated as:

```
pricePerShare = totalAssets / totalSupply
```

Where `totalAssets` is the value of the underlying Curve stablecoin pool position. The attacker manipulated this by:

1. Depositing a large amount of stablecoins directly into the underlying Curve pool that yUSD references
2. This increased the pool's total value, which increased yUSD's `totalAssets`
3. Since `totalSupply` (the number of yUSD tokens in circulation) did not change, the `pricePerShare` increased proportionally
4. Cream's oracle read this inflated `pricePerShare` as the current value of yUSD collateral

The manipulation was temporary — only lasting within the same transaction — but that was sufficient because the flash loan and the borrowing occurred in the same atomic transaction.

**Step 3 — Deposit Inflated Collateral and Borrow**:

With the yUSD price artificially inflated:
1. The attacker deposited yUSD tokens into Cream as collateral
2. Cream valued this collateral using the now-inflated `pricePerShare`
3. The attacker could borrow far more value than the yUSD was actually worth at normal prices
4. Borrowing was executed across multiple Cream lending pools — ETH, WBTC, stablecoins, and other assets

**Step 4 — Unwind and Extract Profit**:

1. The Curve pool deposit was unwound (or the manipulation was irrelevant post-borrow since the debt was already created)
2. The flash loans were repaid using a portion of the borrowed funds
3. The remaining borrowed funds were the attacker's profit — approximately $130M
4. The yUSD collateral left in Cream was now worth far less than the debt it was backing, creating bad debt across the protocol's lending pools

### Why the Oracle Was Vulnerable

The fundamental issue was using a composable token's internal exchange rate as a price oracle:

1. **`pricePerShare` is not a market price**: It represents the vault's accounting view of its assets, not an independently determined market price. Any mechanism that can change the vault's underlying asset balance can change the `pricePerShare`.

2. **Composability creates manipulation vectors**: The yUSD vault is composed of a Curve LP position. Anyone can deposit into the Curve pool, changing its total value and thus the vault's `pricePerShare`. This is by design for normal DeFi usage but becomes a vulnerability when a lending protocol treats this value as an oracle.

3. **Flash loans enable manipulation at scale**: Without flash loans, manipulating the yUSD price would require the attacker to commit their own capital, limiting the manipulation magnitude and creating financial risk. Flash loans removed this constraint, allowing manipulation with borrowed capital that was repaid in the same transaction.

4. **No time-weighted average**: The oracle read the instantaneous `pricePerShare`, making same-transaction manipulation possible. A TWAP or delayed oracle would have resisted single-transaction manipulation.

### Cream's Repeated Vulnerability to Flash Loans

| Exploit | Date | Amount | Vector |
|---------|------|--------|--------|
| Alpha Finance / Iron Bank | Feb 2021 | ~$37.5M | Flash loan leveraged borrowing via Iron Bank's protocol-to-protocol credit |
| AMP Token Reentrancy | Aug 2021 | ~$18.8M | ERC-777 reentrancy in AMP token's transfer hook during Cream liquidation |
| yUSD Oracle Manipulation | Oct 2021 | ~$130M | Flash loan manipulation of yUSD pricePerShare |

The pattern across all three exploits was consistent: Cream's permissive collateral listing policy outpaced its oracle and risk management infrastructure. Each new collateral type introduced novel attack surfaces that were not adequately addressed.

## Market Impact

### CREAM Token

| Metric | Pre-Exploit (Oct 27) | Post-Exploit (48h) |
|--------|---------------------|-------------------|
| CREAM price | ~$175 | ~$80 |
| Price decline | — | ~54% |

The CREAM token had already declined significantly from its early-2021 highs (~$400+) due to the two prior exploits. The October attack accelerated a downward trajectory that continued through 2022.

### Protocol TVL and Viability

- Pre-exploit TVL: ~$300M
- Post-exploit TVL: effectively collapsed to near zero as depositors withdrew remaining assets
- Cream continued operating in a limited capacity but never recovered meaningful TVL
- The Iron Bank product was eventually separated and continued independently under different management

### Depositor Losses

Unlike exploits where funds are returned (Poly Network, Euler), the Cream attack resulted in permanent losses for depositors:
- Depositors in the pools that the attacker borrowed from (ETH, WBTC, stablecoin pools) found their deposits partially or fully drained
- The bad debt created by the worthless yUSD collateral was socialized across affected pools
- There was no DAO treasury recovery plan of sufficient size to make depositors whole

## Vulnerability Pattern: Composable Token Price Oracles

### The Composability Oracle Problem

DeFi's composability means that tokens often represent claims on other tokens, which in turn represent claims on other tokens:
- yUSD = share of Yearn vault → which holds Curve LP tokens → which represent stablecoin pool positions
- Each layer in this composition introduces a potential oracle manipulation vector

When a lending protocol uses the internal accounting of a composable token as a price oracle, it inherits all the manipulation vectors of every layer in the composition chain.

### Comparison to Other Oracle Manipulation Attacks

| Protocol | Token Manipulated | Oracle Type | Manipulation Method |
|----------|------------------|-------------|-------------------|
| Cream Finance | yUSD (Yearn vault) | `pricePerShare` (internal) | Direct deposit into underlying Curve pool |
| Harvest Finance | USDC/USDT (Curve pool) | Curve spot price | Large swap to move AMM price |
| Mango Markets | MNGO (perp market) | On-chain perp mark price | Self-trading on illiquid perp |
| Compound (proposal 117) | Various | Uniswap V3 TWAP | Proposed migration that would have introduced risk |

The common thread is that any price feed derived from an on-chain mechanism (AMM spot price, vault exchange rate, perp mark price) can be manipulated by actors with sufficient capital — and flash loans provide that capital at zero cost.

### Mitigation Approaches

Post-Cream, the DeFi lending ecosystem adopted several approaches to address composable token oracle risk:

1. **External oracle feeds**: Using Chainlink or other off-chain oracle networks for composable token pricing, rather than relying on on-chain exchange rates
2. **Virtual price instead of spot price**: For Curve-based tokens, using Curve's `get_virtual_price` (which is manipulation-resistant) instead of spot calculations
3. **Supply caps and borrow caps**: Limiting the total amount of composable tokens that can be used as collateral or borrowed, reducing the maximum exploit size
4. **Collateral factor reductions**: Assigning lower collateral factors to composable tokens, requiring more collateral per unit of borrowing
5. **Monitoring and circuit breakers**: Implementing real-time monitoring for large `pricePerShare` changes and pausing markets when anomalies are detected

## Lessons for Market Surveillance

1. **Monitor composable token exchange rate spikes**: A sudden increase in the `pricePerShare` or equivalent metric of a vault/LP token used as collateral in a lending protocol is a strong oracle manipulation indicator. Surveillance systems should track these rates and alert on deviations that exceed normal yield-accumulation rates (e.g., a vault that normally appreciates 0.01% per day suddenly showing a 5% increase within a block).

2. **Flash loan volume correlation with lending protocol interactions**: The $1.5B flash loan coordinated across multiple protocols was unusual. Monitoring for transactions that originate flash loans from multiple sources simultaneously and then interact with lending protocol collateral/borrow functions should be a standard alert pattern.

3. **Repeated exploit patterns on the same protocol**: Cream was exploited three times in eight months, each time through a different vector but with a common theme (permissive collateral listing outpacing risk management). A protocol with one major exploit should be subject to elevated surveillance for subsequent attacks targeting different aspects of the same architectural weakness.

4. **Bad debt accumulation monitoring**: After the exploit, Cream's lending pools contained bad debt (undercollateralized positions that could not be liquidated profitably). Monitoring for the creation of bad debt — positions where collateral value falls below debt value and remains there — can detect both exploits and market-driven insolvency events.

5. **Cross-protocol dependency mapping**: The Cream exploit depended on the composition chain: Cream → Yearn → Curve. Mapping these dependencies and monitoring for unusual activity in downstream protocols (large Curve deposits) correlated with upstream protocol interactions (Cream deposits/borrows) can detect multi-protocol manipulation attacks.

6. **Permissionless listing as a risk amplifier**: Protocols that allow permissionless collateral listing inherently have a larger and less-predictable attack surface than those with curated listings. Surveillance should apply higher monitoring intensity to newly listed collateral types, especially composable tokens.

## References

1. Cream Finance. "Post-Mortem: October 27, 2021 Exploit." Cream Finance Blog, October 2021.
2. Rekt News. "Cream Finance — REKT 3." rekt.news, October 27, 2021.
3. Mudit Gupta (@Mudit__Gupta). "Cream Finance v3 exploit analysis." Twitter thread, October 27, 2021.
4. PeckShield. "Cream Finance Hack Analysis." PeckShield Alert, October 27, 2021.
5. Chainalysis. "The 2022 Crypto Crime Report." Chapter: DeFi Exploits. Chainalysis Inc., February 2022.
6. BlockSec. "Flash Loan Attack on Cream Finance." BlockSec Blog, October 2021.
7. Yearn Finance. "Yearn Vault Security." Yearn Finance Documentation, 2021.
