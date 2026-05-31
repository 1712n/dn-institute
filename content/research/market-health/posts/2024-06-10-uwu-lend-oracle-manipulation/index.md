---
title: "UwU Lend transaction-local oracle manipulation"
date: 2024-06-10
entities:
  - UwU Lend
  - sUSDe
  - WETH
  - crvUSD
  - CRV
  - DAI
  - USDT
---

## Summary

On June 10, 2024, UwU Lend was exploited through a series of Ethereum transactions that public incident reports describe as an oracle price manipulation attack. The protocol's LendingPool proxy at `0x2409af0251dcb89ee3dee572629291f9b087c668` was an Aave V2 fork, and the attacker used transaction-local liquidity and Curve-pool state changes to alter how the market valued sUSDe-linked positions.

The on-chain evidence in this case shows a market-health failure, not only a contract-control failure:

- The three public attack transactions were all contract-creation transactions sent by `0x841ddf093f5188989fa1524e7b893de64b421f47`, producing fresh executor contracts in blocks `20061319`, `20061322`, and `20061352`.
- Those receipts landed within `6m36s`, used `53,192,379` gas in total, and emitted `1,670` logs, including `669` ERC-20 `Transfer` logs.
- Receipt-level transfer accounting across attacker-controlled addresses shows net liquid-token inflows of `4,907.443160` WETH, `840,627.852064` crvUSD, `498,960.112775` bLUSD, and `456,696.702201` sDAI.
- The same accounting records large UwU internal/accounting-token changes, including `131,155,184.389656` uSUSDE, `65,662,583.444679` variableDebtSUSDE, and `25,326,128.474128` variableDebtCRV.

This is a lower-bound receipt view. It uses ERC-20 logs only, excludes native ETH balance changes and execution traces, and separates liquid assets from lending-market accounting tokens so the output is not mistaken for a full USD loss valuation. The created-contract discovery uses `receipt.contractAddress`, so it captures top-level contract creations only; internal `CREATE`/`CREATE2` helper contracts would require trace data such as `debug_traceTransaction`.

## Reproducible Dataset

I generated the CSV files and SVG charts in this directory from Ethereum JSON-RPC receipts with `build-uwu-lend-onchain-evidence.js`. The script uses no third-party package and intentionally requires an explicit `ETH_RPC_URL`; use a reliable Ethereum endpoint because public RPC services can rate-limit historical receipt and metadata calls. It can be rerun with:

```bash
ETH_RPC_URL="$YOUR_ETH_RPC_URL" node content/research/market-health/posts/2024-06-10-uwu-lend-oracle-manipulation/build-uwu-lend-onchain-evidence.js
```

Primary evidence:

- [`uwu-lend-tx-summary.csv`](uwu-lend-tx-summary.csv): transaction sender, created executor contract, block, timestamp, gas, log count, and ERC-20 transfer count.
- [`uwu-lend-controlled-addresses.csv`](uwu-lend-controlled-addresses.csv): attacker-controlled addresses included in the net-flow set, with a discovery-method note for seeded addresses versus receipt-only top-level executor discovery.
- [`uwu-lend-attack-transactions.csv`](uwu-lend-attack-transactions.csv): per-transaction net ERC-20 flow to the controlled address set.
- [`uwu-lend-token-net.csv`](uwu-lend-token-net.csv): aggregate net flow by token, including lending-market accounting tokens.
- [`uwu-lend-liquid-token-net.csv`](uwu-lend-liquid-token-net.csv): liquid-token subset of the aggregate flow table.

The three attack transactions are:

- [`0x242a0fb4fde9de0dc2fd42e8db743cbc197ffa2bf6a036ba0bba303df296408b`](https://etherscan.io/tx/0x242a0fb4fde9de0dc2fd42e8db743cbc197ffa2bf6a036ba0bba303df296408b)
- [`0xb3f067618ce54bc26a960b660cfc28f9ea0315e2e9a1a855ede1508eb4017376`](https://etherscan.io/tx/0xb3f067618ce54bc26a960b660cfc28f9ea0315e2e9a1a855ede1508eb4017376)
- [`0xca1bbf3b320662c89232006f1ec6624b56242850f07e0f1dadbe4f69ba0d6ac3`](https://etherscan.io/tx/0xca1bbf3b320662c89232006f1ec6624b56242850f07e0f1dadbe4f69ba0d6ac3)

## Receipt Pattern

{{< figure src="uwu-lend-receipt-load.svg" alt="Log count and gas used by the three UwU Lend attack receipts" caption="Each attack transaction created a fresh executor contract from the same attacker EOA. Blue bars show receipt log count; green bars show gas used, normalized separately." >}}

The receipt timeline is compressed:

| Transaction | Block      | Timestamp              | Created executor                             | Gas used     | Logs  |
| ----------- | ---------- | ---------------------- | -------------------------------------------- | ------------ | ----- |
| attack-1    | `20061319` | `2024-06-10T12:05:59Z` | `0x21c58d8f816578b1193aef4683e8c64405a4312e` | `18,097,758` | `561` |
| attack-2    | `20061322` | `2024-06-10T12:06:35Z` | `0x4e48c46779b3b16d63375751467d7eee34d41c3d` | `17,428,770` | `572` |
| attack-3    | `20061352` | `2024-06-10T12:12:35Z` | `0x13f3fee69160162a78284c64c1100a3df476d890` | `17,665,851` | `537` |

The repeated shape matters. A normal user borrow, repay, or liquidation path should not need to create a new executor contract, issue hundreds of token transfers, and touch many accounting tokens in a single block window. The high log density is a useful monitoring signal because it can be observed from receipts without a full transaction trace.

Public writeups describe the attack as using multiple flash-loan sources, sUSDe/USDe-linked pool manipulation, and liquidation/borrowing paths through UwU's LendingPool. CUBE3's postmortem says the attack moved the sUSDe price used by the protocol from roughly `0.9882` to `1.0318` during the manipulation phase. The receipt-level pattern above is the execution footprint of that market-state dependency.

## Net Flow View

{{< figure src="uwu-lend-token-net.svg" alt="Net liquid-token inflow to UwU Lend attacker-controlled addresses" caption="Liquid-token net inflow to attacker-controlled addresses across the three sampled receipts. Bars are log-scaled because token units are not directly comparable." >}}

The liquid-token subset is intentionally small:

| Token  | Net amount       | Notes                                                            |
| ------ | ---------------- | ---------------------------------------------------------------- |
| WETH   | `4,907.443160`   | Residual WETH after flash-loan-sized in/out movement.            |
| crvUSD | `840,627.852064` | Net retained crvUSD after same-transaction inflows and outflows. |
| bLUSD  | `498,960.112775` | Liquid token retained in the third attack receipt.               |
| sDAI   | `456,696.702201` | Liquid token retained in the first attack receipt.               |

The full token table includes protocol accounting artifacts:

| Token             | Class              | Net amount           |
| ----------------- | ------------------ | -------------------- |
| uSUSDE            | uwu-interest-token | `131,155,184.389656` |
| variableDebtSUSDE | debt-accounting    | `65,662,583.444679`  |
| variableDebtCRV   | debt-accounting    | `25,326,128.474128`  |
| variableDebtUSDT  | debt-accounting    | `4,221,692.419481`   |
| variableDebtDAI   | debt-accounting    | `3,520,271.928241`   |

Those accounting-token rows should not be read as directly withdrawable assets. They are still useful because they show that the manipulated market state did not merely move through external DEX pools; it also created and reshaped UwU lending positions inside the same receipts. LlamaRisk's later crvUSD incident report highlights the knock-on risk of the exploited CRV position, including a large Curve Lend borrow opened from the UwU exploit flow.

## Market-Health Signals

This case gives several concrete rules for lending-market and oracle monitoring:

- **Executor creation plus immediate high-value protocol access:** alert when a fresh contract is created by a newly funded or low-history EOA and immediately enters a lending-pool path with hundreds of transfer logs.
- **Oracle-dependent accounting-token discontinuity:** treat large same-receipt changes in uTokens, variable-debt tokens, or collateral tokens as a market-state anomaly when they are paired with Curve or stable-pool manipulation.
- **Flash-loan-sized gross flow with small positive residuals:** compare gross ERC-20 in/out movement with net retained assets; a residual WETH gain after million-token round trips is a stronger signal than the net row alone.
- **Cross-market aftermath:** track whether extracted collateral is immediately used as collateral in another lending venue, as happened with the CRV/crvUSD path discussed by LlamaRisk.

UwU Lend shows why lending protocols should not treat transaction-local pool state as a reliable market-health input. When the oracle path can be moved and consumed inside the same execution window, the borrow and liquidation accounting becomes an output of the attack rather than an independent risk control.

## References

- CUBE3 incident analysis: https://blog.cube3.ai/2024/06/11/cube3-ai-detected-uwu-lend-attack-days-in-advance/
- SharkTeam incident analysis: https://medium.com/@sharkteam/sharkteam-analysis-of-the-uwu-lend-attack-423735b677a7
- LlamaRisk crvUSD incident report: https://llamarisk.com/research/crvusd-incident-report-20240612
- Etherscan attack transaction 1: https://etherscan.io/tx/0x242a0fb4fde9de0dc2fd42e8db743cbc197ffa2bf6a036ba0bba303df296408b
- Etherscan attack transaction 2: https://etherscan.io/tx/0xb3f067618ce54bc26a960b660cfc28f9ea0315e2e9a1a855ede1508eb4017376
- Etherscan attack transaction 3: https://etherscan.io/tx/0xca1bbf3b320662c89232006f1ec6624b56242850f07e0f1dadbe4f69ba0d6ac3
