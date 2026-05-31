---
title: "Aave CRV short squeeze and collateral liquidation"
date: 2022-11-22
entities:
  - Aave
  - CRV
  - Curve
  - USDC
---

## Summary

In November 2022, wallet `0x57e04786e231af3343562c062e0d058f25dace9e` built a large short position against CRV on Aave V2 Ethereum by depositing USDC collateral, borrowing CRV, and selling the borrowed CRV back into USDC. The position became a market-health event when CRV liquidity and price action moved against the trade: the wallet was liquidated in hundreds of transactions on November 22, and Aave governance later moved to recapitalize the remaining CRV debt.

The on-chain evidence here shows the position as a complete flow rather than a headline number:

- Aave V2 emitted `14` CRV `Borrow` events for the wallet, totaling `92,000,000` CRV between November 14 and November 22, 2022.
- The same wallet transferred out `91,999,999.997087` CRV and received `63,974,581.892838` USDC across wallet-level ERC-20 transfer logs in the same block window.
- The wallet deposited `63,596,139.363797` USDC to Aave V2, while later Aave `LiquidationCall` events seized `63,605,103.124042` USDC collateral against `89,544,317.443850` CRV of covered debt.
- Liquidations were concentrated between `2022-11-22T13:31:23Z` and `2022-11-22T18:09:23Z`, not distributed across the whole build-up period.

The market-health failure was not that one wallet lost money on a directional short. The stress came from allowing one borrowable asset to accumulate a short position whose unwind depended on secondary-market CRV liquidity and an oracle path that could move faster than liquidation could fully remove protocol exposure.

## Reproducible Dataset

The CSV files and SVG charts in this directory are generated from Ethereum JSON-RPC logs with `build-aave-crv-onchain-evidence.js`. The script uses no third-party package and can be rerun with:

```bash
ETH_RPC_URL=https://ethereum-rpc.publicnode.com node content/research/market-health/posts/2022-11-22-aave-crv-short-squeeze/build-aave-crv-onchain-evidence.js
```

Primary evidence files:

- [`aave-crv-borrows.csv`](aave-crv-borrows.csv): CRV `Borrow` events from the Aave V2 Lending Pool for the wallet.
- [`aave-crv-usdc-deposits.csv`](aave-crv-usdc-deposits.csv): USDC `Deposit` events into Aave V2 by the wallet.
- [`aave-crv-wallet-transfers.csv`](aave-crv-wallet-transfers.csv): CRV and USDC ERC-20 transfers to and from the wallet.
- [`aave-crv-sale-transfers.csv`](aave-crv-sale-transfers.csv): transactions where the wallet sent CRV out and received USDC in the same transaction.
- [`aave-crv-liquidations.csv`](aave-crv-liquidations.csv): Aave V2 `LiquidationCall` events covering the wallet's CRV debt with USDC collateral.
- [`aave-crv-summary.csv`](aave-crv-summary.csv): aggregate counts and amounts used in this article.

The log range is Ethereum blocks `15,950,000` through `16,030,000`, covering the build-up, sell-down, and liquidation period. The script filters on Aave V2 Lending Pool `0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9`, CRV `0xD533a949740bb3306d119CC777fa900bA034cd52`, USDC `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`, and the wallet above.

## Borrow and Sell-Down Flow

{{< figure src="aave-crv-cumulative-crv-flow.svg" alt="Cumulative CRV borrowed from Aave, transferred out by the wallet, and covered by liquidation" caption="Cumulative CRV borrowed, transferred out by the wallet, and later covered by Aave liquidation events. Values are in millions of CRV." >}}

The cumulative CRV chart separates three stages:

1. **Position build-up:** the wallet borrowed in discrete Aave transactions. The first CRV borrow in this dataset is transaction [`0xc91b35211c5beca48daa4dab3169001b8ff1473674c80316a288dbaecd729b99`](https://etherscan.io/tx/0xc91b35211c5beca48daa4dab3169001b8ff1473674c80316a288dbaecd729b99) at block `15,966,378`.
2. **Market selling:** after borrowing, the wallet repeatedly transferred CRV out while receiving USDC back. The generated sale-transfer table contains `143` transactions with both sides visible at the wallet level.
3. **Liquidation wave:** Aave liquidation events began after the final borrow transaction [`0x95c2f5164f5e17f95cd75fbb209b9aa66f52d00261d64f1e8ec8efe7b0cec2da`](https://etherscan.io/tx/0x95c2f5164f5e17f95cd75fbb209b9aa66f52d00261d64f1e8ec8efe7b0cec2da), which occurred at block `16,025,172` on `2022-11-22T11:12:11Z`.

The amount borrowed and the wallet's outgoing CRV transfers almost match: `92,000,000` CRV borrowed versus `91,999,999.997087` CRV transferred out. That near-match is important. It indicates that the risk was not a hidden accounting artifact inside Aave; the borrowed asset left the wallet and was converted through market infrastructure.

The USDC side reinforces the same reading. The wallet received `63,974,581.892838` USDC and deposited `63,596,139.363797` USDC into Aave V2. In other words, the short position was repeatedly recycled through collateral and debt, with the wallet using sale proceeds to maintain borrowing capacity while continuing to sell CRV.

## Collateral Liquidation

{{< figure src="aave-crv-cumulative-usdc-flow.svg" alt="Cumulative USDC received by the wallet, deposited to Aave, and liquidated" caption="Cumulative wallet-level USDC receipts, Aave USDC deposits, and USDC collateral liquidated. Values are in millions of USDC." >}}

The liquidation wave shows why this belongs in a market-health library. The protocol had enough automation and third-party liquidator participation to seize almost all of the posted USDC collateral, but it still had residual exposure after the stressed market move.

The first liquidation event in the dataset is transaction [`0x6d75ebed779d6d2309ffbd45c4a9e0bb7f1f6a9b466463f1d77bd7ae650687fe`](https://etherscan.io/tx/0x6d75ebed779d6d2309ffbd45c4a9e0bb7f1f6a9b466463f1d77bd7ae650687fe), at block `16,025,860`. From there, `385` `LiquidationCall` events arrived in roughly four and a half hours. The log totals are:

| Metric                           |                   Amount |
| -------------------------------- | -----------------------: |
| CRV borrowed from Aave V2        |         `92,000,000` CRV |
| CRV transferred out by wallet    |  `91,999,999.997087` CRV |
| USDC transferred to wallet       | `63,974,581.892838` USDC |
| USDC deposited into Aave V2      | `63,596,139.363797` USDC |
| CRV debt covered by liquidations |  `89,544,317.443850` CRV |
| USDC collateral liquidated       | `63,605,103.124042` USDC |

Aave governance later described the same wallet as having opened a short position that peaked around `92M` CRV, with liquidation leaving a smaller bad-debt position isolated to the CRV market. A subsequent governance proposal set the repayment address to this same wallet and specified `2,570,639.04` CRV as the total excess debt to repay. Those governance records match the log-level structure here: the trade was mostly liquidated, but the liquidation sequence did not fully close the borrowed CRV exposure.

## Market-Health Interpretation

The case has a different shape from a flash-loan AMM reserve attack. There is no single transaction-local price deformation. The stress is instead a slow build-up followed by a fast unwind:

- **Borrow-side concentration:** one wallet accumulated a short that reached protocol-level relevance for a single borrowed asset.
- **Collateral/debt asymmetry:** the collateral was a deep stablecoin, while the debt was CRV, whose market depth and volatility determined whether liquidations could close exposure cleanly.
- **Reflexive liquidity risk:** selling borrowed CRV can pressure the same market needed for liquidators to acquire CRV later.
- **Liquidation throughput risk:** hundreds of successful liquidation events still did not guarantee a zero residual debt outcome.

For lending protocols, this suggests several monitoring rules:

- Alert when one borrower or cluster controls a large fraction of borrowable liquidity for a long-tail asset.
- Track the ratio between borrowed units and visible spot/DEX depth, not just collateral health factor.
- Watch for repeated borrow-sell-deposit loops that recycle sale proceeds into fresh collateral.
- Stress-test whether liquidators can acquire enough debt asset during a fast reversal without moving the market further against the protocol.

Aave V3 borrow caps and isolation-style controls are relevant because they limit the maximum size of this path before it reaches liquidation. The November 2022 CRV event shows why caps are not merely user-level risk settings; they are market-health limits on how much directional exposure a lending market can safely absorb.

## References

- Aave governance ARC: https://governance.aave.com/t/arc-repay-excess-debt-in-crv-market-for-aave-v2-eth/10779
- Aave governance proposal 146: https://governance-v2.aave.com/governance/proposal/146/
- Aave V2 Lending Pool on Etherscan: https://etherscan.io/address/0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9
- Wallet on Etherscan: https://etherscan.io/address/0x57e04786e231af3343562c062e0d058f25dace9e
- CRV token on Etherscan: https://etherscan.io/token/0xD533a949740bb3306d119CC777fa900bA034cd52
- USDC token on Etherscan: https://etherscan.io/token/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
