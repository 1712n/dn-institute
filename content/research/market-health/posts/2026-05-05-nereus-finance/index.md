---
date: 2026-05-05
entities:
  - id: nereus-finance
    name: Nereus Finance
    type: defi-protocol
  - id: avalanche
    name: Avalanche
    type: blockchain
title: "Nereus Finance NXUSD depeg: flash-loan price manipulation and $3.5M bad debt on Avalanche"
---

## Introduction

Nereus Finance was a decentralized lending and borrowing protocol on the Avalanche blockchain, forked from Aave and adapted for the Avalanche ecosystem. The protocol allowed users to deposit various crypto assets as collateral and borrow against them, including the protocol's native stablecoin NXUSD. Nereus Finance differentiated itself by integrating Avalanche-specific assets and optimizing for the chain's faster finality and lower gas costs compared to Ethereum mainnet.

On September 6, 2022, an attacker exploited Nereus Finance's price oracle mechanism through flash-loan-assisted price manipulation, creating approximately $3.5 million in bad debt on the protocol and triggering a severe depeg of NXUSD. The attack targeted the protocol's use of a spot price oracle for certain collateral types within the Trader Joe DEX liquidity pools, allowing the attacker to temporarily inflate the value of collateral tokens, borrow NXUSD against the inflated valuation, and leave the protocol with undercollateralized positions that could not be profitably liquidated.

## Background

### Nereus Finance Protocol Design

Nereus Finance operated as an Aave V2 fork with modifications for the Avalanche ecosystem. The protocol's core functions included lending markets where users deposited assets (AVAX, USDC, WETH, etc.) to earn yield, borrowing facilities where depositors could borrow other assets against their collateral, and NXUSD minting where users could mint the protocol's native stablecoin against their deposited collateral.

The protocol maintained several key parameters for each lending market: loan-to-value (LTV) ratios determining maximum borrowing capacity, liquidation thresholds triggering position liquidation when collateral value declined, and liquidation bonuses incentivizing liquidators to close undercollateralized positions. These parameters, combined with accurate price oracles, were designed to ensure the protocol remained solvent — that total collateral value always exceeded total outstanding borrows.

### Trader Joe LP Token Collateral

The critical vulnerability involved Nereus Finance's acceptance of Trader Joe LP tokens as collateral. Trader Joe is Avalanche's largest decentralized exchange, and its LP tokens represent liquidity provider positions in various trading pools. When Nereus accepted Trader Joe LP tokens as collateral, it needed to determine the USD value of these LP positions to calculate borrowing capacity.

LP token pricing is inherently more complex than pricing simple tokens like AVAX or USDC. An LP token's value depends on the underlying token quantities in the pool and their respective market prices. The standard approach is to calculate the total value of the pool's reserves and divide by the LP token supply. However, the pool's reserve quantities are directly affected by swaps — large swaps can temporarily alter reserve ratios and thus the apparent per-LP-token value.

### Oracle Architecture

Nereus Finance's oracle for Trader Joe LP tokens calculated their value based on the current reserve ratios in the liquidity pool. This created a dependency on the spot state of the pool — if an attacker could manipulate the pool's reserves (through a large flash-loan-funded swap), they could temporarily inflate the LP token's apparent value as reported by the oracle.

More robust LP token oracle designs exist, such as Chainlink's LP token price feeds that use time-weighted average prices (TWAPs) or "fair LP pricing" formulas that calculate LP token value based on external price feeds for the underlying assets rather than the pool's current reserve ratios. Nereus Finance did not use these more robust approaches for all of its LP token collateral markets.

## The Attack

### Oracle Manipulation via Flash Loan

The attack exploited the connection between Trader Joe pool reserves and Nereus Finance's LP token valuation oracle. By executing a large swap through a Trader Joe pool (funded by a flash loan), the attacker could temporarily shift the pool's reserves to a state where one token's reserve was much smaller than normal, inflating the per-LP-token value as calculated by Nereus's oracle.

The mechanism works as follows: in a constant-product AMM (x * y = k), a large swap that buys most of token X from the pool pushes X's spot price very high (due to reserve depletion) while simultaneously increasing Y's reserves. The LP token, representing a claim on both reserves, sees its computed value spike because the oracle values the reserves at current prices — and the price of X has been artificially inflated by the swap.

### Step-by-Step Attack Flow

**Step 1: Flash loan.** The attacker borrowed a large amount of tokens (several million USD worth) through Avalanche flash loan providers.

**Step 2: Pool manipulation.** The attacker executed a massive swap through the target Trader Joe pool, drastically altering the reserve ratio. This temporarily inflated the spot price of one of the pool's tokens and, consequently, the LP token's value as computed by Nereus's oracle.

**Step 3: Collateral deposit.** During the same transaction, while the LP token oracle reported the inflated value, the attacker deposited LP tokens (acquired separately or through the same transaction) into Nereus Finance as collateral.

**Step 4: Maximum borrowing.** With the LP tokens valued at the inflated price, the attacker borrowed the maximum amount of NXUSD and other assets allowed by the LTV ratio. Because the collateral appeared to be worth much more than its true value, the borrowing amount far exceeded what the collateral could actually support.

**Step 5: Flash loan repayment and exit.** The attacker reversed the large swap (or repaid the flash loan through other means), returning the pool's reserves to near their original state. The LP token oracle now reported the token's true (much lower) value. The attacker's Nereus position was now deeply undercollateralized, but the borrowed funds had already been extracted.

**Step 6: Bad debt creation.** Because the attacker's position was now undercollateralized (the collateral's true value was far below the borrowed amount), the position could not be profitably liquidated. Liquidators would need to repay the attacker's debt to receive the collateral, but the collateral was worth less than the debt — creating a net loss for any would-be liquidator. This "bad debt" remained on the protocol's books, backed by insufficient collateral.

### NXUSD Depeg Cascade

The $3.5 million in bad debt created by the attack had cascading effects on NXUSD's stability:

1. The bad debt meant the protocol's total collateral no longer fully backed all outstanding NXUSD
2. Market participants recognized this undercollateralization and lost confidence in NXUSD's peg
3. NXUSD holders rushed to swap their tokens for other stablecoins, creating heavy sell pressure
4. NXUSD's price on DEXes dropped significantly below $1 (trading as low as $0.50-$0.60 at times)
5. The depeg further discouraged new depositors and borrowers, reducing the protocol's ability to earn revenue to cover the bad debt

## Impact

### Protocol-Level Damage

The $3.5 million in bad debt represented a significant portion of Nereus Finance's total assets. The protocol was forced to socialize the losses across its user base, either through reduced yields for lenders, increased fees, or direct write-downs of depositor claims. The NXUSD depeg made it difficult for the protocol to attract new deposits, creating a negative feedback loop.

### NXUSD Stablecoin Impact

NXUSD's peg was severely compromised, with the token trading well below $1 for an extended period following the attack. This damaged the stablecoin's utility as a medium of exchange and store of value, as users could not rely on redeeming it at face value. The depeg also affected other DeFi protocols on Avalanche that had integrated NXUSD in their liquidity pools or lending markets.

### User Losses

NXUSD holders suffered losses proportional to the depeg — a holder of 10,000 NXUSD that was worth $10,000 pre-exploit found their position worth $5,000-$6,000 at the worst of the depeg. Lenders who had deposited assets into Nereus Finance faced reduced returns and potential principal losses due to the bad debt socialization.

### Protocol Outcome

Nereus Finance struggled to recover from the exploit. The combination of bad debt, NXUSD depeg, and reduced confidence made it difficult to attract new capital. The protocol eventually wound down its operations, with remaining assets distributed to creditors through a structured closure process.

## Technical Analysis

### LP Token Oracle Manipulation Vector

The fundamental vulnerability is using spot reserve data from AMM pools to price LP tokens used as collateral in lending protocols. This creates a direct manipulation path: any agent who can temporarily alter pool reserves (which is trivially achievable with flash loans) can inflate LP token valuations in the lending protocol.

The mathematical relationship in a constant-product pool is:

Pool value = reserve_X * price_X + reserve_Y * price_Y

If the oracle uses the pool's internal spot prices to value reserves (rather than external price feeds), a large swap inflates one token's spot price while depleting its reserve. The net effect on total pool value depends on the specific manipulation, but the per-LP-token value can be inflated because the "expensive" token's reserve, while smaller, is valued at the inflated price.

### Fair LP Token Pricing

The correct approach to LP token pricing uses external (manipulation-resistant) price feeds for the underlying tokens, rather than the pool's internal spot prices. The "fair LP token pricing" formula, popularized by Alpha Homora's team, values an LP token as:

Fair LP value = 2 * sqrt(reserve_X * reserve_Y) * sqrt(price_X * price_Y) / LP_supply

This formula is resistant to reserve manipulation because it uses the geometric mean of reserves (which is invariant under constant-product swaps — any swap that maintains x*y=k also maintains sqrt(x*y)=sqrt(k)) combined with external price feeds that the attacker cannot manipulate within a single transaction.

If Nereus Finance had used this fair pricing formula with Chainlink feeds for the underlying token prices, the LP token valuation would not have been affected by the attacker's swap, and the borrowing attempt would have been limited to the LP token's true value.

### Bad Debt as a Protocol Solvency Risk

The concept of "bad debt" in DeFi lending occurs when a borrower's position is undercollateralized but cannot be profitably liquidated. This happens when:
- The collateral value drops below the debt value
- The liquidation bonus (typically 5-15%) is insufficient to make liquidation profitable
- The position was created with artificially inflated collateral that reverted to true value

Bad debt represents a direct loss to the protocol because the outstanding loan can never be recovered through normal liquidation. The protocol must either absorb the loss from its insurance fund/reserves, socialize it across depositors, or raise new capital to cover the shortfall.

For stablecoin protocols like Nereus (where NXUSD was minted against collateral), bad debt directly undermines the stablecoin's backing. If total collateral no longer exceeds total NXUSD supply, the stablecoin is partially unbacked and cannot maintain its peg under redemption pressure.

### Comparison with Similar Oracle Manipulation Exploits

**Mango Markets (October 2022, ~$114M)**: Avraham Eisenberg manipulated the price of MNGO tokens on Mango Markets' own platform through large purchases, inflated his MNGO collateral's value, and borrowed against it. While the manipulation mechanism was different (open market buying vs. flash loan pool manipulation), the pattern is identical: inflate collateral value, borrow against inflated value, leave bad debt.

**Inverse Finance (April 2022, ~$15.6M)**: The attacker manipulated the SushiSwap TWAP oracle for INV tokens through a series of swaps, inflated INV's price as reported to Inverse Finance's lending contracts, and borrowed against the inflated valuation. The use of an on-chain TWAP rather than a spot price made the attack more complex (requiring sustained manipulation over multiple blocks) but the underlying pattern was the same.

**Harvest Finance (October 2020, ~$34M)**: The attacker manipulated Curve pool prices through large flash-loan-funded swaps, causing Harvest's vault to buy assets at inflated prices, then reversed the manipulation. While Harvest was a yield vault rather than a lending protocol, the flash-loan oracle manipulation vector is mechanistically identical.

### Defense: Collateral Type Risk Assessment

Not all collateral types carry equal oracle manipulation risk. Simple tokens with deep, multi-exchange liquidity (AVAX, USDC, WETH) are difficult to manipulate because their Chainlink feeds aggregate prices across many sources. LP tokens, yield-bearing tokens, and low-liquidity tokens are inherently higher risk because their prices depend on on-chain state that can be manipulated within transactions.

Lending protocols should assign higher collateralization requirements (lower LTV ratios) to collateral types with higher oracle manipulation risk, or implement additional safeguards such as supply caps, borrowing limits, and manipulation-resistant pricing formulas.

## Lessons Learned

### Never Use Spot Pool State for Collateral Pricing

LP tokens and other pool-derived assets must be priced using manipulation-resistant methods — either fair LP pricing formulas with external price feeds or time-weighted averages that span multiple blocks. Spot reserve data from AMM pools is trivially manipulable with flash loans and should never be used as the sole input for collateral valuation in lending protocols.

### Supply Caps and Borrowing Limits for High-Risk Collateral

Lending protocols should impose strict supply caps on collateral types with higher manipulation risk. If the maximum allowed LP token collateral is $500,000, the maximum possible bad debt from oracle manipulation is capped at a fraction of that amount — far less than the protocol-threatening $3.5 million that occurred without caps.

### Bad Debt Insurance and Recovery Mechanisms

Protocols should maintain insurance funds sized to cover worst-case bad debt scenarios for each collateral type. Additionally, automatic bad debt socialization mechanisms (such as aToken value haircuts in Aave-style systems) should be transparent and pre-defined, rather than ad-hoc responses to crises.

### Real-Time Oracle Integrity Monitoring

Automated monitoring that compares oracle-reported LP token values against independent calculations using external price feeds can detect manipulation in real-time. If the oracle value deviates from the independently calculated fair value by more than a threshold, new deposits of that collateral type should be automatically paused.

## Conclusion

The Nereus Finance NXUSD depeg exploit of September 6, 2022, created approximately $3.5 million in bad debt through flash-loan-assisted LP token oracle manipulation on Avalanche. The attacker temporarily inflated Trader Joe LP token valuations by manipulating pool reserves with flash-loan-funded swaps, deposited LP tokens as collateral at the inflated price, borrowed NXUSD against the artificial valuation, and left undercollateralized positions that could not be profitably liquidated. The resulting bad debt undermined NXUSD's backing, causing a severe stablecoin depeg and ultimately contributing to the protocol's wind-down. This incident demonstrates the critical importance of manipulation-resistant oracle design for LP tokens and other pool-derived collateral, the necessity of supply caps and borrowing limits for high-risk collateral types, and the catastrophic impact that bad debt can have on stablecoin-issuing protocols where undercollateralization directly threatens the stablecoin's peg.
