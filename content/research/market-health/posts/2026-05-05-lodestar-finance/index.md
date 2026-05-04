---
date: 2026-05-05
entities:
  - id: lodestar-finance
    name: Lodestar Finance
    type: defi-protocol
  - id: plutusdao
    name: PlutusDAO
    type: defi-protocol
  - id: arbitrum
    name: Arbitrum
    type: blockchain
title: "Lodestar Finance plvGLP oracle manipulation: exchange rate inflation and $6.5M Arbitrum lending drain"
---

## Introduction

Lodestar Finance was a decentralized lending and borrowing protocol on Arbitrum (an Ethereum Layer 2 rollup) that supported a variety of collateral types including standard tokens (ETH, USDC, ARB) and yield-bearing vault tokens from other Arbitrum DeFi protocols. Among its supported collateral assets was plvGLP — a liquid staking derivative of GLP (GMX Protocol's liquidity provider token) created by PlutusDAO. The plvGLP token represented a staked GLP position with auto-compounded rewards, and its value was derived from the underlying GLP's net asset value plus accumulated yield.

On December 10, 2022, an attacker exploited a vulnerability in how Lodestar Finance priced the plvGLP collateral token, manipulating its reported exchange rate to inflate the apparent value of deposited plvGLP collateral and borrow far more than the collateral was actually worth. The exploit drained approximately $6.5 million from Lodestar's lending pools on Arbitrum. The vulnerability was in the oracle mechanism that Lodestar used to determine plvGLP's value — rather than using an independent external price feed, the protocol derived plvGLP's price from an on-chain exchange rate function that could be manipulated through targeted interactions with the PlutusDAO vault.

## Background

### GLP and plvGLP Token Architecture

GLP is the liquidity provider token for GMX Protocol, a decentralized perpetual exchange on Arbitrum. GLP represents a proportional share of GMX's multi-asset pool (containing ETH, BTC, stablecoins, and other tokens), and GLP holders earn a share of GMX's trading fees plus esGMX (escrowed GMX) rewards. The value of one GLP token is determined by the total value of the assets in GMX's pool divided by the total GLP supply.

PlutusDAO created plvGLP (Plutus vault GLP) as a liquid staking wrapper for GLP. Users deposited GLP into PlutusDAO's vault and received plvGLP tokens in return. The vault auto-compounded GLP rewards (selling esGMX for more GLP), causing the exchange rate between plvGLP and GLP to increase over time. One plvGLP was always redeemable for more than one GLP (since it represented the original GLP plus accumulated compounded rewards).

The plvGLP/GLP exchange rate was tracked by the PlutusDAO vault contract through a function that reported how much GLP each plvGLP was worth. This exchange rate was the price input that Lodestar Finance used to value plvGLP collateral.

### Lodestar's plvGLP Oracle Design

Lodestar Finance priced plvGLP by reading the exchange rate from the PlutusDAO vault contract (how much GLP per plvGLP) and multiplying by GLP's price (obtained from a reliable source like Chainlink or GMX's own oracle). The formula was:

```
plvGLP_price = plvGLP_to_GLP_exchange_rate * GLP_price
```

The vulnerability was in how the `plvGLP_to_GLP_exchange_rate` was determined. If this exchange rate could be manipulated — for example, by depositing or withdrawing from the PlutusDAO vault in a way that temporarily inflated the rate — the resulting plvGLP price used by Lodestar would be artificially high, allowing the attacker to borrow more than their collateral's true value.

## The Attack

### Vulnerability: Manipulable Exchange Rate

The core vulnerability was that the PlutusDAO vault's reported exchange rate (plvGLP per GLP) could be temporarily inflated through specific interactions within a single transaction. The exchange rate was calculated based on the vault's total GLP holdings divided by the total plvGLP supply. If the attacker could increase the vault's GLP holdings without proportionally increasing the plvGLP supply (or decrease the plvGLP supply without proportionally decreasing the GLP), the exchange rate would spike upward.

The specific manipulation mechanism involved the vault's reward distribution: when rewards were compounded into the vault (increasing the GLP balance without minting new plvGLP), the exchange rate increased. The attacker found a way to trigger or simulate this reward compounding within the same transaction as their Lodestar operations, creating a momentary exchange rate spike that Lodestar's oracle reported as the current plvGLP value.

### Attack Execution

The attack on December 10, 2022, proceeded as follows:

**Step 1: Flash loan acquisition.** The attacker obtained flash loans of GLP and other assets to provide capital for the manipulation.

**Step 2: Exchange rate inflation.** The attacker interacted with the PlutusDAO vault in a way that temporarily inflated the plvGLP/GLP exchange rate. This may have involved depositing GLP directly into the vault contract (increasing the GLP balance without minting proportional plvGLP), triggering a reward compound that added GLP to the vault without minting new plvGLP shares, or exploiting a specific function that updated the vault's balance accounting in a manipulable way.

**Step 3: Collateral deposit at inflated value.** With the exchange rate temporarily inflated, the attacker deposited plvGLP tokens into Lodestar Finance as collateral. Lodestar queried the PlutusDAO vault for the current exchange rate, received the inflated rate, and valued the attacker's plvGLP at a much higher price than its true value.

**Step 4: Excessive borrowing.** The attacker borrowed the maximum possible amount of other assets (ETH, USDC, ARB, MAGIC, etc.) against their overvalued plvGLP collateral. Because Lodestar believed the collateral was worth far more than its actual value, it allowed borrows that exceeded the true collateral value.

**Step 5: Exchange rate restoration.** After the attacker's transactions completed, the PlutusDAO vault's exchange rate returned to its normal level (the manipulation was temporary). The attacker's plvGLP collateral was now worth its true (much lower) value, but the borrows had already been issued.

**Step 6: Flash loan repayment and profit extraction.** The attacker repaid flash loans and retained the profit: the borrowed assets minus the true value of the deposited collateral and flash loan fees. Total extraction: approximately $6.5 million.

## Impact

### Financial Losses

Lodestar Finance's lending pools lost approximately $6.5 million in various Arbitrum assets. The losses were distributed across all depositors in the affected pools (ETH, USDC, ARB, MAGIC, and others), whose deposits were used to fund the attacker's uncollateralized borrows. The protocol was left with bad debt: outstanding borrows backed by plvGLP collateral that was worth a fraction of the debt it secured.

### Protocol Shutdown

Following the exploit, Lodestar Finance halted all operations. The team published a post-mortem confirming the plvGLP exchange rate manipulation and announced that the protocol would not resume operations. Remaining depositors were allowed to withdraw whatever residual assets were available, receiving significantly less than their original deposits due to the bad debt.

### Impact on Arbitrum DeFi

The Lodestar exploit highlighted risks specific to the Arbitrum DeFi ecosystem: many Arbitrum lending protocols accepted yield-bearing vault tokens (plvGLP, GLP derivatives, auto-compound tokens) as collateral, and these tokens' prices were often derived from on-chain exchange rates rather than independent oracle feeds. The exploit prompted other Arbitrum lending protocols (Radiant Capital, Tender.fi, Silo Finance) to review their pricing mechanisms for yield-bearing collateral tokens.

## Response and Remediation

### Post-Mortem

Lodestar published a detailed post-mortem identifying the exchange rate manipulation vector and acknowledging that their oracle design was fundamentally flawed for yield-bearing tokens whose exchange rates could be manipulated within a single transaction.

### Industry Response

The Arbitrum DeFi community responded by developing best practices for pricing yield-bearing tokens as lending collateral. Key recommendations included using time-weighted exchange rates (averaging the rate over multiple blocks to prevent single-transaction manipulation), implementing exchange rate deviation bounds (rejecting price reads that deviate significantly from recent historical values), querying independent price sources rather than vault exchange rate functions, and implementing deposit-to-borrow delays that prevent collateral from being used for borrowing in the same block it is deposited.

## Technical Analysis

### Exchange Rate Oracle Manipulation Pattern

The Lodestar exploit exemplifies the "composable oracle manipulation" pattern specific to yield-bearing vault tokens in DeFi. The pattern arises when: a lending protocol prices a vault token using the vault's own exchange rate function, the exchange rate function reflects the vault's current state (live balance/supply ratio), and the vault's state can be temporarily manipulated within a single transaction.

This pattern is analogous to using a Uniswap pool's spot price as an oracle (manipulable via flash loans), but applied to yield-bearing vault tokens instead of AMM pools. The defense is the same: never use a live, manipulable state read as a price input for lending decisions.

### Yield-Bearing Token Pricing Challenges

Yield-bearing tokens (plvGLP, stETH, aTokens, cTokens, etc.) pose unique oracle challenges because their value is not a simple market price — it is derived from a combination of the underlying asset's price and a multiplier (the exchange rate representing accumulated yield). This two-component pricing creates two potential manipulation vectors: the underlying asset price (addressed by traditional oracle security measures) and the exchange rate (often read from the vault contract's own state, which may be manipulable).

For established tokens with deep liquidity (like stETH or wstETH), market-based pricing through decentralized exchanges may be feasible. For newer or less liquid yield-bearing tokens (like plvGLP), market-based pricing is insufficient and exchange rate reads are necessary — but must be protected against manipulation.

### Comparison with Similar Exchange Rate Exploits

The Lodestar exploit belongs to a growing category of attacks targeting yield-bearing token exchange rate manipulation in lending contexts. Similar incidents include the Sentiment Protocol exploit (April 2023, approximately $1 million on Arbitrum), which manipulated the value of Balancer LP tokens used as collateral through a similar exchange rate inflation mechanism; and the Euler Finance exploit (March 2023, approximately $197 million on Ethereum), which while mechanistically different (donation attack to inflate the exchange rate of eTokens), exploited the same fundamental concept: manipulating a share/exchange rate that feeds into a lending protocol's collateral valuation.

## Lessons Learned

### Never Use Live Vault Exchange Rates as Oracle Inputs

The most direct lesson is that lending protocols must not use a vault token's live exchange rate (read from the vault contract's current state) as the sole input for collateral valuation. Live exchange rates are vulnerable to same-transaction manipulation and should be treated with the same suspicion as spot AMM prices. Instead, use time-weighted exchange rates averaged over multiple blocks, implement exchange rate deviation checks with circuit breakers, maintain an independent exchange rate tracker that updates periodically rather than on-demand, or require a time delay between collateral deposit and borrow eligibility.

### Composability Creates Oracle Surface Area

DeFi composability — the ability for protocols to integrate with each other's tokens and contracts — creates an expanding oracle attack surface. Every new yield-bearing token accepted as collateral represents a new price feed that must be secured against manipulation. Lending protocols should treat each new collateral asset's pricing mechanism as a critical security component requiring dedicated analysis and testing.

### Arbitrum-Specific Considerations

Arbitrum's fast block times and low gas costs make exchange rate manipulation cheaper and faster than on Ethereum mainnet, reducing the practical cost of attacks. Arbitrum lending protocols should implement security measures calibrated to the L2's speed and cost characteristics, not simply copy Ethereum-designed protections that may be inadequate in the faster, cheaper L2 environment.

## Conclusion

The Lodestar Finance plvGLP exchange rate manipulation exploit of December 10, 2022, drained approximately $6.5 million from the Arbitrum lending protocol by temporarily inflating the PlutusDAO vault's reported exchange rate for plvGLP tokens, causing Lodestar to overvalue the attacker's collateral and issue borrows exceeding the collateral's true worth. The vulnerability was in using the vault's live exchange rate function as a price oracle input — a pattern vulnerable to same-transaction manipulation that parallels the well-known risks of using spot AMM prices for lending valuations. The incident reinforced that yield-bearing vault tokens require dedicated, manipulation-resistant pricing mechanisms in lending contexts, and that DeFi's composability expands the oracle attack surface with each new integrated asset type.
