---
title: "USDC-USDT Sandwich Manipulation in a Uniswap v3 Stablecoin Pool"
date: 2025-03-12
description: "A receipt-level analysis of three March 2025 USDC/USDT sandwich attacks that converted nearly $495,000 of USDC into only $12,310 of USDT."
entities:
  - Uniswap v3
  - USDC
  - USDT
  - Ethereum
  - MEV
---

## Summary

On March 12, 2025, three Ethereum users sent large USDC-to-USDT swaps through the Uniswap v3 USDC/USDT 0.01% pool. Each victim transaction landed at transaction index 1 in its block. Each was bracketed by the same searcher account, `0x26ce7c1976c5eec83ea6ac22d83cb341b08850af`, through the same execution contract, `0x00000000003b3cc22af3ae1eac0440bcee416b40`.

The receipt data shows a repeatable three-step pattern:

1. The front-runner pushed roughly 18 million USDC through the stablecoin pool, draining roughly 17 million USDT and moving the pool far away from the expected stablecoin price.
2. The victim swap then executed at an extreme rate: the three victims received only 2.39% to 2.57% of the USDT expected from a near-1:1 stablecoin swap.
3. The back-run transaction reversed the pool back toward parity and paid a large direct transfer to the block fee recipient.

Across the three victim transactions, 494,719.034382 USDC was exchanged for only 12,310.021708 USDT. Measured against a simple 1:1 stablecoin baseline, the direct execution shortfall was 482,409.012674 dollars.

{{< figure src="stablecoin-sandwich-losses.svg" alt="Victim USDC input, received USDT, and implied loss in three stablecoin sandwich cases" caption="Victim execution outcomes in the three USDC/USDT sandwich cases. The green segment is the USDT received; the red segment is the gap versus a 1:1 stablecoin baseline." loading="lazy" >}}

## Dataset and Method

The companion dataset, [`stablecoin-sandwich-evidence.csv`](stablecoin-sandwich-evidence.csv), was built from Ethereum `eth_getTransactionReceipt` and `trace_transaction` calls for the front-run, victim, and back-run transactions in blocks 22029751, 22029756, and 22029771.

The analysis uses only on-chain evidence:

- Swap logs emitted by the Uniswap v3 pool `0x3416cf6c708da44db2624d63ea0aaef7113527c6`.
- ERC-20 transfer logs from the USDC contract `0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48` and the USDT contract `0xdac17f958d2ee523a2206206994597c13d831ec7`.
- Transaction ordering and timestamps from the Ethereum blocks.
- Internal ETH transfers from the back-run traces to the block fee recipient.

The three public victim transactions are:

- Case A: [`0xb403f921671c5f1494153f0b9543a0650ff1212a4b557f2ea53455107c94215c`](https://etherscan.io/tx/0xb403f921671c5f1494153f0b9543a0650ff1212a4b557f2ea53455107c94215c), block 22029751.
- Case B: [`0x636ca7a5f63a6698c82e860e610363e75d97184403fa06f9907243a84e25b68a`](https://etherscan.io/tx/0x636ca7a5f63a6698c82e860e610363e75d97184403fa06f9907243a84e25b68a), block 22029756.
- Case C: [`0xee9fcd2b9996e96b642cb4cda47fc140f98fdaf07ee02657743d4bfcc4670106`](https://etherscan.io/tx/0xee9fcd2b9996e96b642cb4cda47fc140f98fdaf07ee02657743d4bfcc4670106), block 22029771.

Etherscan marks the largest victim transaction as an MEV transaction, and [public reporting described the same event as a large sandwich attack](https://www.theblock.co/post/345977/crypto-trader-swaps-733000-for-just-19000-in-large-sandwich-attack). The raw receipts are more important than that label: the transaction order, pool tick movement, swap amounts, and back-run fee-recipient transfers are enough to reconstruct the manipulation path.

## Execution Evidence

The most useful market-health signal is the repeated block structure. In all three cases, the front-run transaction appears at index 0, the victim at index 1, and the back-run at index 2.

| Case |    Block | Front-run tx                                                                                                     | Victim tx                                                                                                       | Back-run tx                                                                                                     |
| ---- | -------: | ---------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| A    | 22029751 | [`0x14194b...a4266`](https://etherscan.io/tx/0x14194bc2f2daac35057c4d6f45c7fa86af2f7e2e941abd60b0bb26131fea4266) | [`0xb403f9...215c`](https://etherscan.io/tx/0xb403f921671c5f1494153f0b9543a0650ff1212a4b557f2ea53455107c94215c) | [`0x729c3a...61fd`](https://etherscan.io/tx/0x729c3a86c1bd2f144161d33bc3a1a75d1cf70cbb263bc6ec6437c7301a1a61fd) |
| B    | 22029756 | [`0x7fae57...7b40`](https://etherscan.io/tx/0x7fae574aac9a3cd8f0e82597f9424c55bd64fa98f7ca50f5cc0f7cd4de137b40)  | [`0x636ca7...b68a`](https://etherscan.io/tx/0x636ca7a5f63a6698c82e860e610363e75d97184403fa06f9907243a84e25b68a) | [`0x5b591b...cc4a`](https://etherscan.io/tx/0x5b591bca885d5e82a9ff89a24c41ec9f83ba01aa0ffc9101cfa5c742eeaacc4a) |
| C    | 22029771 | [`0xde5aa0...cd36`](https://etherscan.io/tx/0xde5aa0c1521d97a48496f10bb8aff364e490c8fc3a4f5d9d587538f15d80cd36)  | [`0xee9fcd...0106`](https://etherscan.io/tx/0xee9fcd2b9996e96b642cb4cda47fc140f98fdaf07ee02657743d4bfcc4670106) | [`0x3e72f3...943c`](https://etherscan.io/tx/0x3e72f3ad09d87149ce372e5f35eeb8012fed05f52bef45fb85fdacc0057a943c) |

The victim trades were not ordinary slippage events. A normal USDC/USDT stablecoin trade should clear close to one USDT per USDC in a healthy pool. These victims cleared at 0.025673, 0.025711, and 0.023881 USDT per USDC.

| Case  | Victim USDC in | Victim USDT out | USDT per USDC | Shortfall vs 1:1 |
| ----- | -------------: | --------------: | ------------: | ---------------: |
| A     | 142,514.609972 |    3,658.706929 |      0.025673 |   138,855.903043 |
| B     | 131,398.034741 |    3,378.316721 |      0.025711 |   128,019.718020 |
| C     | 220,806.389669 |    5,272.998058 |      0.023881 |   215,533.391611 |
| Total | 494,719.034382 |   12,310.021708 |      0.024883 |   482,409.012674 |

## Pool Price Distortion

The Uniswap v3 swap event includes the post-swap tick. Converting the tick with `1.0001^tick` gives a useful approximation of the pool's token1-per-token0 price after each swap. In this pool, token0 is USDC and token1 is USDT.

The pattern is stark: the front-run shifts the pool from parity into a roughly 2.7% to 2.8% USDT-per-USDC state, the victim pushes it down again, and the back-run restores the pool to about 1.0001.

{{< figure src="stablecoin-sandwich-tick-path.svg" alt="Tick-implied USDT per USDC after front-run, victim, and back-run swaps" caption="Tick-implied pool price after each swap. The back-run restores the USDC/USDT pool to parity after the victim has executed near the manipulated trough." loading="lazy" >}}

| Case | Front-run price after swap | Victim price after swap | Back-run price after swap |
| ---- | -------------------------: | ----------------------: | ------------------------: |
| A    |                   0.028136 |                0.023428 |                  1.000100 |
| B    |                   0.027978 |                0.023628 |                  1.000100 |
| C    |                   0.027383 |                0.020829 |                  1.000100 |

The evidence is stronger than a single bad fill. The same searcher repeats the same ordering pattern, with the same pool and the same execution contract, across three blocks separated by only four minutes.

## Builder Payment Signal

The back-run traces show direct ETH payments to the block fee recipient `0xd87f3d6c5624e8b02be13c2c92f8511b88b94d96`:

| Case | Block fee recipient payment in back-run | Approximate role                                   |
| ---- | --------------------------------------: | -------------------------------------------------- |
| A    |                     63.641261313491 ETH | Payment for transaction ordering in block 22029751 |
| B    |                     58.248347375831 ETH | Payment for transaction ordering in block 22029756 |
| C    |                    100.558534716115 ETH | Payment for transaction ordering in block 22029771 |

These transfers are economically consistent with a private-orderflow or builder-mediated sandwich. The largest case alone paid about 100.56 ETH to the fee recipient, while the victim lost about 215,533 stablecoin dollars versus a 1:1 execution baseline.

## Market Health Indicators

This incident suggests several surveillance rules that are more robust than looking for a single bad price:

1. **Index-0 / index-1 / index-2 bracketing.** A searcher transaction immediately before and after a retail-sized swap is a high-confidence sandwich candidate, especially when both searcher transactions share the same sender and executor.
2. **Stablecoin tick collapse.** A USDC/USDT pool moving from parity to below 0.03 USDT per USDC inside the same block is not ordinary stablecoin volatility.
3. **Back-run restoration.** The suspicious price move is not persistent; it is created before the victim and removed immediately afterward.
4. **Fee-recipient transfer.** A large internal ETH transfer to the block fee recipient in the back-run is evidence that transaction ordering itself was being purchased.
5. **Repeated victim structure.** Three similar victim swaps in four minutes indicate either repeated unsafe routing or a deliberate pipeline of highly sandwichable transactions.

The market-health lesson is that stablecoin pools can look healthy between blocks while still producing catastrophic execution quality inside a block. Block-level surveillance should therefore track not only daily volume and end-of-block pool state, but also intra-block tick paths, same-sender bracketing, and direct builder payments.

## Conclusion

The March 12 USDC/USDT sequence is a compact example of market manipulation rather than a protocol exploit. No pool contract needed to fail. The manipulation happened through ordering, temporary liquidity distortion, and an economically rational payment to the block producer path.

For users, the practical control is strict slippage protection and routing through MEV-protected submission paths. For market-health monitoring, the practical control is to score intra-block price paths rather than relying on end-of-block pool state. In this case, the pool ended each attack near parity, but the victims collectively lost more than 482,000 dollars of execution value during the manipulated intervals.
