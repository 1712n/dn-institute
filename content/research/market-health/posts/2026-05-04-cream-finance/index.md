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

1. **On October 27, 2021, the Cream Finance lending protocol suffered a major exploit**, losing roughly $130 million in what was then one of the largest flash-loan-assisted DeFi lending attacks. The attacker manipulated the value Cream assigned to Yearn's yUSD vault token, then borrowed against the inflated collateral across Cream's lending pools.
2. **The core vulnerability was Cream's reliance on the internal exchange rate of yUSDVault shares** (a Yearn vault token tied to yUSD/Curve stablecoin exposure) as collateral valuation. Public analyses describe the attacker shrinking the yUSDVault share supply, then donating yUSD into the vault so `pricePerShare` jumped atomically.
3. **The attack used very large borrowed capital and recursive lending loops** sourced from protocols including Maker/Aave-style liquidity and Cream markets. This capital was used to build yUSDVault/crYUSD positions, inflate yUSDVault share value, and borrow against the inflated collateral.
4. **The stolen funds were not broadly returned**, and public tracing showed proceeds moving through DeFi, renBridge/BTC routes, and privacy-linked funding paths. Unlike the Poly Network or Euler exploits, there was no public negotiated recovery that made affected depositors whole.
5. **Cream and its surrounding lending ecosystem had suffered earlier major incidents** — including the February 2021 Alpha/Iron Bank incident and the August 2021 AMP reentrancy exploit. The October attack severely damaged Cream's viability as a major lending venue, with TVL and confidence falling sharply.

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
| Protocol TVL | Reported in the hundreds of millions before the exploit |
| yUSD collateral factor | Varied; sufficient to allow significant borrowing |
| yUSD price oracle | Yearn vault `pricePerShare` (internal exchange rate) |
| Large liquidity sources | Maker-style DAI liquidity, Aave ETH liquidity, and Cream market loops |
| Number of listed collateral types | 60+ tokens including LP tokens and vault tokens |
| Prior incidents | Feb 2021 Alpha/Iron Bank incident, Aug 2021 AMP exploit |

The vulnerability centered on using `pricePerShare` as a price oracle. This value represents the vault's net asset value per share, which can change abruptly when vault share supply and vault asset balance are manipulated in the same transaction sequence.

## Technical Exploit Mechanics

### Attack Overview

The attack was executed through a coordinated transaction sequence, with the bulk of the exploit occurring in a main Ethereum transaction that combined borrowed liquidity, vault manipulation, and Cream borrowing.

**Step 1 — Massive Flash Loan Acquisition**:

The attacker used extremely large borrowed liquidity across multiple protocols:
- Hundreds of millions of DAI were used to create yUSD/yUSDVault exposure
- A very large ETH borrow was used as collateral in Cream
- Cream markets were then used recursively to build crYUSD/yUSDVault exposure

The scale was remarkable — public writeups described roughly billion-dollar-scale temporary liquidity being coordinated across protocols.

**Step 2 — yUSD Price Manipulation**:

The yUSDVault token's `pricePerShare` was calculated as:

```
pricePerShare = totalAssets / totalSupply
```

Where `totalAssets` is the vault's yUSD balance and `totalSupply` is outstanding yUSDVault shares. The attacker manipulated this by:

1. Accumulating a large amount of yUSDVault exposure through Cream lending loops
2. Redeeming most yUSDVault shares for underlying yUSD, reducing outstanding share supply sharply
3. Donating yUSD back into the vault while share supply stayed low
4. Causing `pricePerShare` to jump atomically, which made Cream value crYUSD/yUSDVault-linked collateral much higher

The manipulation was temporary — only lasting within the same transaction — but that was sufficient because the flash loan and the borrowing occurred in the same atomic transaction.

**Step 3 — Deposit Inflated Collateral and Borrow**:

With the yUSDVault-linked collateral artificially inflated:
1. The attacker held large crYUSD/yUSDVault-linked collateral positions in Cream
2. Cream valued those positions using the now-inflated `pricePerShare`
3. The attacker could borrow far more value than the collateral would support under normal vault conditions
4. Borrowing was executed across multiple Cream lending pools — ETH, WBTC, stablecoins, and other assets

**Step 4 — Unwind and Extract Profit**:

1. The attacker used borrowed assets and redeemed yUSD/yUSDVault exposure to repay the temporary liquidity
2. The inflated-collateral debt remained in Cream after the transaction sequence
3. The remaining borrowed funds were the attacker's profit — approximately $130M
4. The yUSDVault-linked collateral left in Cream no longer supported the debt it had enabled, creating bad debt across the protocol's lending pools

### Why the Oracle Was Vulnerable

The fundamental issue was using a composable token's internal exchange rate as a price oracle:

1. **`pricePerShare` is not a market price**: It represents the vault's accounting view of assets per share, not an independently determined market price. If an attacker can alter vault asset balance relative to share supply, they can move `pricePerShare`.

2. **Composability creates manipulation vectors**: yUSD/yUSDVault exposure sits on top of Curve/Yearn mechanics. Actions that are valid in the lower-layer protocols can create abrupt accounting changes when a lending market treats the composed token as collateral.

3. **Flash loans enable manipulation at scale**: Without flash loans, manipulating the yUSD price would require the attacker to commit their own capital, limiting the manipulation magnitude and creating financial risk. Flash loans and temporary borrows reduced this upfront-capital constraint because most borrowed liquidity could be repaid in the same transaction sequence.

4. **No time-weighted average**: The oracle read the instantaneous `pricePerShare`, making same-transaction manipulation possible. A TWAP or delayed oracle would have resisted single-transaction manipulation.

### Cream's Repeated Vulnerability to Flash Loans

| Exploit | Date | Amount | Vector |
|---------|------|--------|--------|
| Alpha Finance / Iron Bank | Feb 2021 | ~$37.5M | Flash-loan leveraged borrowing via Iron Bank's protocol-to-protocol credit |
| AMP Token Reentrancy | Aug 2021 | ~$18.8M | Reentrancy in AMP token transfer hook during Cream borrowing/liquidation flow |
| yUSD Oracle Manipulation | Oct 2021 | ~$130M | Flash loan manipulation of yUSD pricePerShare |

The repeated pattern was that permissive or complex collateral integration outpaced oracle and risk-management controls. Each new collateral type introduced novel attack surfaces that were not fully contained.

## Market Impact

### CREAM Token

| Metric | Pre-Exploit (Oct 27) | Post-Exploit (48h) |
|--------|---------------------|-------------------|
| CREAM price | Triple digits pre-exploit | Sharp decline |
| Price decline | — | Reported around 50% in some windows |

The CREAM token had already declined significantly from early-2021 highs after prior incidents. The October attack accelerated a downward trajectory that continued through 2022.

### Protocol TVL and Viability

- Pre-exploit TVL was reported in the hundreds of millions
- Post-exploit TVL fell sharply as depositors withdrew remaining assets and confidence collapsed
- Cream continued operating in a limited capacity but did not recover its prior scale
- Iron Bank later became a separate product path rather than a simple continuation of Cream's original market

### Depositor Losses

Unlike exploits where recoverable funds were returned (Poly Network, Euler), the Cream attack resulted in lasting losses for many depositors:
- Depositors in the pools that the attacker borrowed from (ETH, WBTC, stablecoin pools) found their deposits partially or fully drained
- The bad debt created by the worthless yUSD collateral was socialized across affected pools
- No public recovery plan restored affected depositors to their pre-exploit position

## Vulnerability Pattern: Composable Token Price Oracles

### The Composability Oracle Problem

DeFi's composability means that tokens often represent claims on other tokens, which in turn represent claims on other tokens:
- yUSD = share of Yearn vault → which holds Curve LP tokens → which represent stablecoin pool positions
- Each layer in this composition introduces a potential oracle manipulation vector

When a lending protocol uses the internal accounting of a composable token as a price oracle, it inherits all the manipulation vectors of every layer in the composition chain.

### Comparison to Other Oracle Manipulation Attacks

| Protocol | Token Manipulated | Oracle Type | Manipulation Method |
|----------|------------------|-------------|-------------------|
| Cream Finance | yUSDVault / crYUSD exposure | `pricePerShare` (internal) | Vault share-supply and asset-balance manipulation |
| Harvest Finance | USDC/USDT (Curve pool) | Curve spot price | Large swap to move AMM price |
| Mango Markets | MNGO (perp market) | On-chain perp mark price | Self-trading on illiquid perp |
| Compound (proposal 117) | Various | Uniswap V3 TWAP | Proposed migration that would have introduced risk |

The common thread is that any price feed derived from an on-chain mechanism (AMM spot price, vault exchange rate, perp mark price) can be manipulated by actors with sufficient temporary capital — and flash loans make that capital available without long-term inventory risk.

### Mitigation Approaches

Post-Cream, DeFi risk reviewers increasingly emphasized several approaches to composable-token oracle risk:

1. **External oracle feeds**: Using Chainlink or other off-chain oracle networks for composable token pricing, rather than relying on on-chain exchange rates
2. **Less manipulable pool accounting where appropriate**: For Curve-based tokens, reviewers often prefer accounting values such as virtual price over raw spot calculations, while still checking whether the chosen value can move abruptly
3. **Supply caps and borrow caps**: Limiting the total amount of composable tokens that can be used as collateral or borrowed, reducing the maximum exploit size
4. **Collateral factor reductions**: Assigning lower collateral factors to composable tokens, requiring more collateral per unit of borrowing
5. **Monitoring and circuit breakers**: Implementing real-time monitoring for large `pricePerShare` changes and pausing markets when anomalies are detected

## Lessons for Market Surveillance

1. **Monitor composable token exchange rate spikes**: A sudden increase in the `pricePerShare` or equivalent metric of a vault/LP token used as collateral in a lending protocol is a strong oracle manipulation indicator. Surveillance systems should track these rates and alert on deviations that exceed normal yield-accumulation rates (e.g., a vault that normally appreciates 0.01% per day suddenly showing a 5% increase within a block).

2. **Large temporary-liquidity correlation with lending protocol interactions**: The billion-dollar-scale temporary liquidity coordinated across protocols was unusual. Monitoring for transactions that originate large flash loans or temporary borrows from multiple sources and then interact with lending protocol collateral/borrow functions should be a standard alert pattern.

3. **Repeated exploit patterns on the same protocol**: Cream was exploited three times in eight months, each time through a different vector but with a common theme (permissive collateral listing outpacing risk management). A protocol with one major exploit should be subject to elevated surveillance for subsequent attacks targeting different aspects of the same architectural weakness.

4. **Bad debt accumulation monitoring**: After the exploit, Cream's lending pools contained bad debt (undercollateralized positions that could not be liquidated profitably). Monitoring for the creation of bad debt — positions where collateral value falls below debt value and remains there — can detect both exploits and market-driven insolvency events.

5. **Cross-protocol dependency mapping**: The Cream exploit depended on the composition chain: Cream → Yearn/yUSDVault → Curve/yUSD. Mapping these dependencies and monitoring for unusual lower-layer vault/share-supply changes correlated with upstream protocol interactions (Cream deposits/borrows) can detect multi-protocol manipulation attacks.

6. **Permissionless listing as a risk amplifier**: Protocols that allow permissionless collateral listing inherently have a larger and less-predictable attack surface than those with curated listings. Surveillance should apply higher monitoring intensity to newly listed collateral types, especially composable tokens.

## References

1. Cream Finance. "Post-Mortem: October 27, 2021 Exploit." Cream Finance Blog, October 2021.
2. Rekt News. "Cream Finance — REKT 3." rekt.news, October 27, 2021.
3. Mudit Gupta (@Mudit__Gupta). "Cream Finance v3 exploit analysis." Twitter thread, October 27, 2021.
4. PeckShield. "Cream Finance Hack Analysis." PeckShield Alert, October 27, 2021.
5. Chainalysis. "The 2022 Crypto Crime Report." Chapter: DeFi Exploits. Chainalysis Inc., February 2022.
6. BlockSec. "Flash Loan Attack on Cream Finance." BlockSec Blog, October 2021.
7. Yearn Finance. "Yearn Vault Security." Yearn Finance Documentation, 2021.
