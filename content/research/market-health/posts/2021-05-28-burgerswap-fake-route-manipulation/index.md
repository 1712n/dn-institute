---
title: "BurgerSwap fake-route reserve manipulation"
date: 2021-05-28
entities:
  - BurgerSwap
  - BURGER
  - WBNB
  - USDT
  - xBURGER
  - ROCKI
---

## Summary

On May 28, 2021, BurgerSwap's BNB Smart Chain AMM was exploited with a flash-loan-funded route that used an attacker-controlled token pair to distort the BURGER/WBNB market state inside a single transaction. Public incident writeups describe a wider 14-transaction loss cluster; the on-chain sample here focuses on 13 high-log extraction transactions sent by the same attacker wallet to the same exploit contract, starting with the first documented attack transaction.

The evidence shows a market-health failure rather than just a generic contract drain:

- The first attack transaction moved the BURGER/WBNB reserve-implied price from roughly `0.195` WBNB per BURGER to `0.000936` WBNB per BURGER inside one receipt, a more than `200x` reserve-price swing before partial recovery.
- The same receipt contains a fake-token pair swap that emits `45,452.972395` BURGER out with zero observable token input in the pair's `Swap` log, immediately before that BURGER is sold into the real BURGER/WBNB pool.
- Across the sampled extraction transactions, receipt-level transfer accounting shows net inflows to the attacker contract and funding wallet of `4,411.393180` WBNB, `1,431,761.031031` USDT, `432,874.621429` BURGER, `142,129.706547` xBURGER, `22,163.839969` BUSD, `95,168.833050` ROCKI, and `2.594824` ETH.

This is the pattern market-health monitoring should flag: spot reserve state is not merely volatile; it is being manufactured by a controlled route and then consumed as if it were a normal market price.

## Reproducible Dataset

I generated the CSV files and SVG charts in this directory from BNB Smart Chain JSON-RPC receipts with `build-burgerswap-onchain-evidence.js`. The script uses no third-party package and can be rerun with:

```bash
BSC_RPC_URL=https://bsc-dataseed.binance.org/ node content/research/market-health/posts/2021-05-28-burgerswap-fake-route-manipulation/build-burgerswap-onchain-evidence.js
```

Primary evidence:

- [`burgerswap-first-transaction-sync.csv`](burgerswap-first-transaction-sync.csv): BURGER/WBNB `Sync` reserve snapshots from the first attack receipt.
- [`burgerswap-first-transaction-swaps.csv`](burgerswap-first-transaction-swaps.csv): decoded `Swap` logs from the first attack receipt.
- [`burgerswap-attack-transactions.csv`](burgerswap-attack-transactions.csv): per-transaction net token movement to the attacker contract and funding wallet.
- [`burgerswap-attack-token-net.csv`](burgerswap-attack-token-net.csv): aggregate net token movement across the sampled transactions.

The first transaction is [`0xac8a739c1f668b13d065d56a03c37a686e0aa1c9339e79fcbc5a2d0a6311e333`](https://bscscan.com/tx/0xac8a739c1f668b13d065d56a03c37a686e0aa1c9339e79fcbc5a2d0a6311e333). Halborn's public incident summary describes the fake-token route and WBNB/BURGER manipulation path, while the LearnBlockchain reconstruction lists the same attacker wallet, exploit contract, platform contract, pair contract, and first transaction used by this dataset.

## Reserve-Price Collapse Inside One Receipt

{{< figure src="burgerswap-reserve-price.svg" alt="BURGER WBNB reserve-implied price through the first BurgerSwap attack transaction" caption="BURGER/WBNB reserve-implied price from Sync events in the first attack receipt. The x-axis is receipt log index, not wall-clock time." >}}

The reserve snapshots show three distinct states:

1. Before the fake-route cycle is consumed by the real pool, the pair's reserve-implied price sits near `0.194-0.195` WBNB per BURGER.
2. After the attacker sells BURGER through the real BURGER/WBNB pair, the reserve-implied price falls to `0.050114`.
3. After the fake pair emits another `45,452.972395` BURGER and that amount is sold into the real pair, the reserve-implied price collapses to `0.000936`.

This is not a normal slippage sequence. The fake-token leg gives the attacker a transaction-internal BURGER source, then the real pool pays WBNB against that manufactured state. The final swap in the same receipt uses only `491.799457` WBNB to buy `108,791.137767` BURGER after the reserve price has been crushed.

The decoded first-transaction swaps show the sequence:

| Log | Pair        | In                     | Out                     | Effective price           |
| --- | ----------- | ---------------------- | ----------------------- | ------------------------- |
| 29  | BURGER/WBNB | `6,028.990833` WBNB    | `92,677.046404` BURGER  | `0.065053765` WBNB/BURGER |
| 72  | BURGER/WBNB | `45,316.613933` BURGER | `4,478.616993` WBNB     | `0.098829471` WBNB/BURGER |
| 90  | FAKE/BURGER | no token input in log  | `45,452.972395` BURGER  | route-manipulation leg    |
| 94  | BURGER/WBNB | `45,452.972395` BURGER | `4,478.616970` WBNB     | `0.098532983` WBNB/BURGER |
| 123 | BURGER/WBNB | `491.799457` WBNB      | `108,791.137767` BURGER | `0.004520584` WBNB/BURGER |

The same receipt ends with a PancakeSwap USDT/WBNB pair movement that repays `6,062.287950` WBNB against `6,047.132230` WBNB out from the flash-swap pair. The attacker contract plus funding wallet still net `2,401.666781` WBNB and `110,562.238462` BURGER in that first transaction alone.

## Multi-Asset Extraction Pattern

{{< figure src="burgerswap-token-net.svg" alt="Net token inflow to the BurgerSwap attacker contract and wallet" caption="Net transfer amounts to the attacker contract and funding wallet across 13 high-log extraction transactions. Bars are log-scaled because token units are not comparable." >}}

The net-transfer table is not a full USD loss valuation. It is a receipt-level market-flow view: for each ERC-20 `Transfer` event in the sampled transactions, the script adds transfers into the attacker contract or funding wallet and subtracts transfers out of those same addresses.

That accounting exposes a repeated extraction structure:

- Some transactions use the same BURGER manipulation pattern to obtain WBNB directly.
- Other transactions end with large net inflows of third-party assets such as USDT, xBURGER, ROCKI, BUSD, and ETH.
- Several zero-net `BLP` entries are intentionally excluded from the chart because they were minted and burned as temporary liquidity-position artifacts rather than retained assets.

The high-level totals line up with the public post-mortem pattern: a flash-loan route creates artificial BURGER movement, then the altered state is used to pull out other pool assets. The important market-health signal is not just the final token list; it is the repeated use of transaction-local reserve deformation as an input to pricing.

## Detection Signals

This case gives several concrete monitoring rules for AMM and lending markets:

- **Transaction-local reserve discontinuity:** alert when a pool's `Sync`-derived reserve price changes by orders of magnitude inside one transaction and then partially reverts before the transaction ends.
- **Zero-input swap leg:** flag swap logs where a pair emits a large output without a corresponding input in the same pair log, especially when the output is immediately routed to a major liquidity pair.
- **Controlled-route dependency:** treat newly created or low-history intermediary pairs as untrusted pricing inputs when they appear in the same transaction as a large flash loan.
- **Cross-pool extraction after manipulated price:** combine reserve-price anomalies with net-transfer accounting to catch when the same contract converts a manipulated leg into WBNB, stablecoins, or other liquid assets.

BurgerSwap's exploit shows why spot AMM state should be treated as an execution artifact, not as a market-health metric, unless the data window is long enough and the route is independent enough to survive transaction-local manipulation.

## References

- First attack transaction on BscScan: https://bscscan.com/tx/0xac8a739c1f668b13d065d56a03c37a686e0aa1c9339e79fcbc5a2d0a6311e333
- Halborn incident summary: https://www.halborn.com/blog/post/explained-the-burgerswap-hack-may-2021
- LearnBlockchain incident reconstruction: https://learnblockchain.cn/article/2604
- Decrypt incident report: https://decrypt.co/72194/burgerswap-explains-7-2-million-flash-loan-attack-in-post-mortem
