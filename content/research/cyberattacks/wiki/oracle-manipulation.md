---
title: "Oracle Manipulation"
description: "A deep dive into how DeFi protocols are exploited by manipulating price oracles, often using flash loans to create undercollateralized loans and drain liquidity."
---

Price oracles are the backbone of DeFi, providing the external data that lending protocols, derivatives, and other dApps need to function. When these oracles are insecure, they become the Achilles' heel of the protocol they serve.

## The Mechanism of Oracle Manipulation

The vulnerability arises when a protocol relies on a price feed that can be easily and cheaply manipulated. The most common target is an oracle that sources its price directly from a single, low-liquidity spot market (e.g., a Uniswap V2 pool).

*   **Spot Price Manipulation:** An attacker uses a flash loan to execute a massive trade on the target DEX pool. For example, they might swap millions of USDC for Asset A. This huge, temporary buying pressure drives the spot price of Asset A to an artificially high level.
*   **Borrowing Against Inflated Collateral:** The attacker then deposits the now-inflated Asset A as collateral into a lending protocol. The protocol's oracle reads the manipulated spot price and assigns an excessively high value to the collateral.
*   **Draining the Protocol:** The attacker proceeds to borrow every other available asset (like stablecoins, ETH, etc.) against their super-valued collateral, effectively draining the protocol of its liquidity before paying back the initial flash loan.

## Case Studies

### 1. Mango Markets ($116M) - Spot Price Manipulation

*   **Vector:** The attacker used two accounts to first establish a large perpetual futures position in the native MNGO token. They then used funds to aggressively buy MNGO on the spot market, driving its price up by over 1000%.
*   **Impact:** The protocol's oracle used this manipulated spot price, which massively increased the value of the attacker's collateral. They then borrowed against this value, draining the protocol of $116M.
*   **Lesson:** Relying on the spot price of a low-liquidity native token as an oracle is a critical vulnerability.

### 2. Cream Finance ($130M) - Composable Exploit

*   **Vector:** The attacker used a series of complex flash loans and interactions within the Yearn ecosystem to manipulate the price of the yUSD token on a Curve pool.
*   **Impact:** This manipulated price was fed into Cream Finance, which accepted the inflated yUSD as collateral, allowing the attacker to borrow and steal $130M.
*   **Lesson:** Composability is a double-edged sword. When protocols rely on each other, vulnerabilities can cascade through the ecosystem in unforeseen ways.

### 3. BonqDAO ($120M) - Oracle Update Flaw

*   **Vector:** The attacker found a vulnerability in an oracle for the ALBT token. They were able to manipulate the price on a DEX and then trigger an update in the BonqDAO contract before anyone could react.
*   **Impact:** They used the manipulated price to mint over 100 million BEUR (a euro-pegged stablecoin) with virtually worthless collateral, then swapped it for other assets.
*   **Lesson:** Oracles must not only be sourced from manipulation-resistant feeds (like TWAPs or Chainlink) but must also have built-in safeguards, like circuit breakers, that halt protocol activity if the price changes too dramatically in a short period.
