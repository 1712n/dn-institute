---
title: "🌰 bZx Flash-Loan Attacks — Single-Block Price Manipulation and the Birth of DeFi Oracle Risk"
date: 2026-05-04
entities:
  - bZx
  - Fulcrum
  - dYdX
  - Uniswap
  - Kyber Network
  - Compound
  - Synthetix
  - WBTC
  - sUSD
---

## Summary

1. **In February 2020, bZx/Fulcrum was hit by two flash-loan-assisted market manipulation attacks within four days**, causing roughly $954,000 in protocol losses. The first attack manipulated WBTC/ETH execution through shallow Uniswap/Kyber liquidity; the second manipulated sUSD pricing used for collateral/borrowing.
2. **The attacks did not require a traditional private-key compromise or smart-contract drain.** They exploited bZx's dependence on single-block on-chain liquidity and price discovery, using flash loans to make manipulated spot prices look valid long enough for bZx to execute against them.
3. **The first attack borrowed 10,000 ETH from dYdX**, used part of the capital to create an oversized 5x WBTC short on Fulcrum, pushed bZx execution through a low-liquidity Uniswap WBTC pool, then sold borrowed WBTC into the inflated price. bZx absorbed the bad execution while the attacker exited with profit.
4. **The second attack manipulated the sUSD price used in bZx lending calculations**, allowing inflated collateral value to support undercollateralized borrowing. Both incidents showed that composability can turn small liquidity pools into system-wide pricing inputs.
5. **These attacks became canonical DeFi oracle-manipulation case studies.** They demonstrated why lending, margin, and derivatives protocols cannot safely rely on a single DEX spot price or a single-block execution path for collateral valuation.

## Background

bZx was an early DeFi margin-trading and lending protocol. Its Fulcrum product allowed users to open leveraged positions and borrow assets through smart contracts. Like many early DeFi protocols, bZx integrated with other protocols for liquidity and execution:

- **dYdX** supplied flash-loan liquidity.
- **Compound** supplied collateralized borrowing markets.
- **Kyber Network** routed trades across available liquidity sources.
- **Uniswap v1** provided automated market-maker liquidity, often with shallow reserves for long-tail pairs.
- **Synthetix sUSD** served as a synthetic stablecoin asset in one of the affected price paths.

This composability was the point of DeFi: protocols could be stitched together in a single transaction. But it also created a new manipulation surface. If a protocol used the output of another protocol as a price signal, an attacker could temporarily move that signal with borrowed capital and unwind the manipulation before the block ended.

The bZx incidents were not simply "hacks" in the traditional sense. They were adversarial trades that exploited a mismatch between **market price** and **oracle price**.

## 🌰 Attack 1 — WBTC/ETH Slippage and Price Manipulation

### Transaction Structure

Public post-mortems describe the first February 2020 attack as a single-transaction strategy roughly following this sequence:

1. Borrow **10,000 ETH** through a dYdX flash loan.
2. Deposit part of the ETH into Compound as collateral and borrow approximately **112 WBTC**.
3. Use bZx/Fulcrum to open a leveraged short position on WBTC/ETH.
4. bZx routes a large WBTC purchase through Kyber, which ultimately consumes shallow Uniswap WBTC liquidity.
5. The Uniswap WBTC price becomes temporarily inflated because the pool cannot absorb the trade without extreme slippage.
6. The attacker sells the borrowed WBTC into the inflated pool, receiving more ETH than the WBTC would have been worth under normal market conditions.
7. The flash loan is repaid inside the same transaction, leaving bZx with the loss from bad execution.

### Why the Trade Worked

The exploit worked because bZx treated a thin-liquidity execution path as if it reflected an economically valid market price. In a liquid market, buying or selling 112 WBTC should not drastically move price. In a shallow Uniswap v1 pool, the same trade could move the marginal price enough to make the trade profitable for the attacker and toxic for bZx.

| Component | Intended Role | Manipulation Failure |
|---|---|---|
| dYdX flash loan | Temporary capital source | Enabled a huge trade with no upfront capital |
| Compound WBTC borrow | Source of WBTC inventory | Let attacker sell WBTC after inflating price |
| bZx/Fulcrum short | Leveraged position/execution path | Absorbed manipulated trade execution |
| Kyber routing | Liquidity aggregator | Routed into shallow Uniswap liquidity |
| Uniswap WBTC pool | AMM liquidity | Spot price moved sharply in one block |

The attacker did not need to hold the manipulation for more than one block. The entire point was to borrow, distort, execute, sell, and repay atomically.

### Economic Result

Reported analyses estimate bZx's first-attack loss at roughly **$620,000**, while the attacker retained a lower but still material profit after the transaction settled. The exact attacker profit varies by accounting methodology because part of the gain was embedded in remaining Compound equity and position value.

## Attack 2 — sUSD Collateral Price Manipulation

The second attack occurred days later and targeted bZx's handling of sUSD pricing. The pattern was similar:

1. Borrow large temporary capital through a flash loan.
2. Move the sUSD price upward through low-liquidity on-chain venues used in the price path.
3. Deposit or reference the inflated sUSD value in bZx.
4. Borrow assets against collateral valued at the manipulated price.
5. Repay the flash loan and leave bZx with an undercollateralized position.

This incident reinforced the same lesson: if collateral valuation can be moved within the same block as borrowing, the lending protocol is accepting a manipulable price rather than a robust oracle.

## Market Manipulation Characteristics

### Single-Block Price Distortion

Traditional market manipulation often requires sustained wash trading, spoofing, or false information. The bZx attacks compressed manipulation into a single block. The attacker used flash-loan capital to create temporary price impact, then used that price impact as an input to another protocol before arbitrage could normalize the market.

### Oracle/Execution Coupling

bZx's failure was not only an "oracle bug." It was a coupling problem:

- execution routes were allowed to consume shallow liquidity,
- spot prices from those routes influenced trade/collateral outcomes,
- no time-weighted averaging or multi-source sanity check stopped the manipulation,
- and the entire loop could complete atomically.

This is why the bZx incidents are still cited in oracle-design discussions: an oracle can be technically "on-chain" and still be economically unsafe.

### Composability as Leverage

Flash loans did not create the vulnerability, but they amplified it. Without flash loans, the attacker would have needed substantial capital and inventory. With flash loans, the attack became a capital-free arbitrage against a pricing weakness.

| Primitive | Benefit to Honest Users | Abuse in bZx Attacks |
|---|---|---|
| Flash loans | Capital-efficient arbitrage/liquidation | Temporary massive buying power |
| AMMs | Permissionless liquidity | Thin pools became manipulable price signals |
| Aggregators | Best-route execution | Routed toxic flow into fragile liquidity |
| Margin protocols | Leverage | Converted bad prices into protocol losses |
| Lending markets | Capital access | Supplied borrowed inventory and exit value |

## Surveillance Signals

### 1. Same-Block Price Impact Before Borrowing

Any transaction that moves a DEX price and then immediately borrows against that moved price should be considered high risk.

**Trigger:** collateral price changes >5% inside the same transaction that opens a borrow or leveraged position.

### 2. Flash-Loan-Sized Execution Through Thin Pools

If a protocol routes a trade through a pool whose depth is small relative to trade size, the execution should be capped or rejected.

**Trigger:** trade size exceeds 10% of pool reserves for an asset used in oracle or collateral logic.

### 3. Single-Source Oracle Dependency

Protocols should flag any asset whose risk engine depends on one venue, one route, or a spot price without a time-weighted component.

**Trigger:** collateral valuation source count <3 or no TWAP/medianization.

### 4. Atomic Manipulation Loops

Mempool and transaction simulation can detect loops where borrowed funds manipulate price, execute against the manipulated price, then repay within one transaction.

**Trigger:** flash loan + DEX price movement + borrow/leverage action + repayment in one transaction.

### 5. Toxic Route Detection

Aggregators should not route protocol-owned or leveraged flow into pools where expected slippage exceeds a risk limit, even if the route is technically executable.

**Trigger:** projected slippage >2% on a route involving collateral or liquidation-sensitive assets.

### 6. Post-Incident Parameter Lockdown

After an oracle or execution incident, protocols should freeze high-risk markets until oracle sources, slippage caps, and liquidation parameters are reviewed.

**Trigger:** protocol loss from price manipulation or oracle deviation >0.1% of TVL.

## Lessons for DeFi Market Health

The bZx attacks marked a transition in DeFi security thinking. Before 2020, many teams focused on reentrancy, access control, and arithmetic bugs. bZx showed that **correct code can still lose money when it trusts manipulable market structure**.

Key lessons:

1. **Spot prices are not oracles.** A price that can be moved by the same transaction that consumes it is not a reliable risk input.
2. **Flash loans make capital assumptions obsolete.** Any price path that is safe only because manipulation would be expensive is unsafe in a flash-loan environment.
3. **Liquidity depth is a security parameter.** If a market is shallow, it should not be used to value collateral or execute leveraged protocol flow.
4. **Atomic composability requires atomic risk checks.** Protocols must simulate full transaction effects, not only individual function calls.
5. **Oracle design is market design.** The question is not merely whether data is cryptographically signed, but whether the economic process generating the data can be manipulated.

🌰 The practical surveillance lesson: if a protocol lets borrowed money move a price and then treats that moved price as truth, it has already sold the attacker an option on its own balance sheet.

## References

1. Coinbase. "Around the Block #3: Analysis on the bZx Attack." Coinbase Blog, February 2020.
2. The Block. "bZx exploit: Former Google engineer explains how an attacker made $350K in single transaction." February 2020.
3. bZx Network. "Incident Report and Post-Mortem." February 2020.
4. PeckShield. "bZx Hack Analysis." PeckShield Alert, February 2020.
5. Palkeo. "The bZx attacks explained." Technical analysis, 2020.
6. Eduard Stal. "bZx got rekt: what flash loan attacks teach developers." March 2020.
7. Chainlink. "What Is a Flash Loan Attack?" Oracle security education, 2020.
8. ConsenSys Diligence. "DeFi Oracle Best Practices and Price Manipulation Risks." 2020.
