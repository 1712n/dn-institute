---
title: "Radiant Capital Liquidity Index Manipulation"
date: "2024-01-02"
description: "Radiant Capital's January 2024 Arbitrum incident shows how a newly opened lending market, flash-loan-amplified deposits, and precision-sensitive liquidity-index math can turn a small rounding edge into bad debt."
entities:
  - Radiant Capital
  - Arbitrum
  - USDC
  - WETH
  - ETH
  - Lending Markets
---

## Summary

Radiant Capital's Arbitrum deployment lost roughly $4.5 million to $4.6 million on January 2, 2024 after an attacker targeted its newly created native USDC market. Public writeups from Radiant's incident page in this repository, The Block, The Crypto Times, Blockchain News, Rekt, and Halborn describe the same core shape: flash-loan-sized liquidity changed a reserve or liquidity index, a precision or rounding edge compounded through repeated deposit and withdrawal operations, and the attacker borrowed WETH/ETH against an artificially improved accounting position.

For Market Health, the Radiant case is useful because the manipulation did not require an ordinary spot-price pump. The stressed market variable was the lending market's internal index. If a protocol allows a new pool's accounting index to move sharply under low organic liquidity, market-health monitoring has to treat that index like a price feed.

## Market Structure

The incident had four fragile ingredients:

- a new native USDC market on Arbitrum;
- flash-loan liquidity large enough to dominate the first accounting window;
- precision-sensitive index math inherited from familiar lending-market patterns;
- cross-asset borrowing capacity that converted the accounting distortion into extractable WETH/ETH.

This structure made the market look solvent while its accounting state was being pushed into an abnormal zone. The borrower did not need to convince outside traders that USDC was worth more than one dollar. They needed the protocol's index math to temporarily report that the manipulated position had more borrowing power than the pool should have allowed.

## Signal 1: New-Market Liquidity Dominance

The first warning signal is the share of a new lending market's effective liquidity that can arrive in one block or one short transaction bundle:

```text
new_market_liquidity_dominance =
  flash_loan_supplied_liquidity / organic_market_liquidity_before_bundle
```

When this ratio is above 1, the attacker can outsize normal market formation. Above 5, first-day pool accounting should be treated as adversarial until caps, cooldowns, or index-change limits prove otherwise. Radiant's affected USDC market was new enough that flash-loan liquidity could dominate the state transition the protocol used for borrowing decisions.

## Signal 2: Liquidity Index Jump

Lending markets often expose an internal index that tracks cumulative interest, reserves, or liquidity accounting. A market-health monitor should watch the index as a manipulated variable:

```text
liquidity_index_jump =
  abs(index_after_bundle - index_before_bundle) / index_before_bundle
```

Small index changes are normal. A large one-block jump in a newly launched pool is not. The Radiant exploit demonstrates that an index jump can be economically equivalent to an oracle deviation because it changes the collateral and borrowing math that downstream users and risk controls rely on.

## Signal 3: Rounding Amplification

The reported exploit path depended on cumulative precision error. A practical signal is how much value repeated deposit and withdrawal cycles can create relative to the cost of running them:

```text
rounding_amplification =
  value_created_by_repeated_cycles / transaction_and_flash_loan_cost
```

If this value is above 1, the market has an exploitable accounting loop. If it grows with each cycle, the protocol should pause the affected pool because the attack becomes more profitable as the position size increases.

## Signal 4: Borrow-Against-Distortion Ratio

The market-health consequence is not just the abnormal index. It is the amount borrowed from the protocol because of that abnormal state:

```text
borrow_against_distortion_ratio =
  assets_borrowed_after_index_shift / total_assets_available_to_borrow
```

The higher this ratio, the more a local accounting error becomes system bad debt. In Radiant's case, the manipulated USDC market was converted into WETH/ETH extraction, so the final risk was visible as bad debt and a temporary pause of Arbitrum markets.

## Counterfactual Stress Test

A newly opened lending market can be tested before launch by simulating large first-block deposits and withdrawals:

| Scenario             | Assumption                                           | Market-health response                                       |
| -------------------- | ---------------------------------------------------- | ------------------------------------------------------------ |
| Normal bootstrap     | First bundle is less than 25 percent of seeded depth | Watch index drift, but allow normal operation                |
| Whale bootstrap      | First bundle is 1x to 5x organic depth               | Apply borrow caps and alert on index movement                |
| Flash-loan dominance | First bundle is more than 5x organic depth           | Disable borrowing until index settles across multiple blocks |
| Amplifying precision | Repeated cycles increase claim value after each loop | Pause pool and fix math before allowing new borrows          |

The important control is sequencing. A market can accept deposits before it allows full borrowing, or it can cap borrowing until organic depth and index stability are proven.

## Detection Table

| Signal                         | What changed                                                 | Why it mattered                                               |
| ------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------- |
| New-market liquidity dominance | Flash-loan-sized liquidity hit a newly created USDC market   | One bundle could dominate the initial accounting state        |
| Liquidity index jump           | The reserve/liquidity index moved into an abnormal range     | Internal accounting became a manipulated market variable      |
| Rounding amplification         | Repeated cycles compounded a precision error                 | Small arithmetic error became economically extractable        |
| Borrow-against-distortion      | The attacker borrowed WETH/ETH against the manipulated state | Accounting distortion became protocol-level bad debt          |
| Market pause                   | Arbitrum markets were suspended while the incident was fixed | The manipulation affected confidence in live lending activity |

## Practical Alert Rules

1. Treat one-block liquidity-index movement like an oracle price move.
2. Cap borrowing in a new pool until the index has survived multiple blocks of deposits and withdrawals.
3. Alert when flash-loan-supplied liquidity exceeds organic seeded liquidity.
4. Run repeated deposit-withdraw simulations at maximum realistic flash-loan size before enabling borrowing.
5. Escalate if a small precision difference becomes profitable after transaction and flash-loan fees.
6. Separate deposit enablement from borrow enablement for thin or newly deployed markets.

## Lessons for Market Health

Radiant shows that lending markets can be manipulated through internal accounting, not only through external prices. A protocol may use a correct token price and still misprice risk if a liquidity index, reserve index, or exchange-rate accumulator can be shifted by a concentrated transaction bundle.

The broader lesson is that market-health tooling should monitor protocol state variables that behave like prices. Index jumps, exchange-rate jumps, and collateral-share inflation all deserve the same treatment as suspicious spot-market candles: compare them with organic liquidity, simulate adversarial flow, and block borrowing when the market is too young to prove that its accounting state is robust.

## Sources

- [Distributed Networks Institute: Radiant Capital suffers $4.6 million loss](https://dn.institute/research/cyberattacks/incidents/2024-01-03-radiant-capital/)
- [Halborn: Explained - The Radiant Capital Hack January 2024](https://www.halborn.com/blog/post/explained-the-radiant-capital-hack-january-2024)
- [Rekt: Radiant Capital Rekt](https://rekt.news/radiant-capital-rekt)
- [Blockchain News: Radiant Capital Suffers $4.5M Flash Loan Attack](https://blockchain.news/news/radiant-capital-suffers-45m-flash-loan-attack)
- [The Crypto Times: Radiant Capital Hacked for Over $4.5 Million in ETH](https://www.cryptotimes.io/2024/01/03/radiant-capital-hacked-for-over-4-5-million-in-eth/)
- [The Block: Radiant Capital reportedly hacked for $4.5 million worth of ETH](https://www.theblock.co/post/270080/radiant-capital-reportedly-hacked-eth)
