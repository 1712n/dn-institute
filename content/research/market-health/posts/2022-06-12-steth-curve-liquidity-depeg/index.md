---
title: "stETH Curve Liquidity Depeg and Contagion Stress"
date: 2022-06-12
entities:
  - Lido
  - stETH
  - ETH
  - Curve
  - Celsius
  - Three Arrows Capital
---

## Summary

In June 2022, staked ether (stETH) traded at a discount to ETH as large holders tried to exit through secondary markets before Ethereum withdrawals were enabled. [CoinDesk reported](https://www.coindesk.com/markets/2022/06/17/biggest-steth-pool-almost-empty-complicating-exit-for-would-be-sellers) that the largest stETH trading pool on Curve became heavily imbalanced, complicating exits for sellers and trapping liquidity-sensitive holders such as Celsius. [Web3 is Going Great recorded](https://www.web3isgoinggreat.com/?id=lido-staked-ether-steth-loses-peg) that the Curve pool was about 5% off peg and heavily imbalanced on June 12.

The core market-health issue was liquidity mismatch. stETH represented a claim on staked ETH, but it could not be redeemed directly for ETH at the time. Holders that needed immediate liquidity had to sell into secondary markets, especially Curve. As the pool skewed toward stETH, each additional sale pushed the discount wider and made the remaining exit capacity worse.

This case is useful for Market Health because it connects liquid-staking-token design, secondary-market depth, concentrated exit venues, leveraged collateral, and centralized-lender redemption pressure. It was not a smart-contract exploit, but it produced market stress that affected Celsius, Three Arrows Capital, DeFi lending positions, and retail stETH holders.

## Manipulation Analysis

The first stress vector was pool imbalance. A liquid-staking token can remain technically backed while still trading at a discount if immediate redemption is unavailable. Once the Curve stETH/ETH pool became dominated by stETH, the marginal price of a large exit fell below the nominal one-to-one relationship.

The second vector was forced selling by large holders. [CoinDesk reported on Nansen analysis](https://www.coindesk.com/business/2022/06/29/nansen-casts-blame-for-steth-de-peg-on-terra) that publicized stETH sales by 3AC, Celsius, and others helped push stETH below ETH, and that poor market conditions after Terra made the Curve pool imbalance hard to repair.

The third vector was redemption-liquidity mismatch at centralized lenders. [TechCrunch reported](https://techcrunch.com/2022/06/12/crypto-lender-celsius-pauses-withdrawals-transfers-citing-extreme-market-conditions/) that Celsius paused withdrawals, swaps, and transfers on June 12, citing extreme market conditions. If a lender owes liquid ETH to customers but holds a large illiquid stETH position, the stETH discount becomes a balance-sheet and run-risk signal.

The fourth vector was collateral contagion. [CoinMarketCap research](https://coinmarketcap.com/alexandria/article/coinmarketcap-research-liquidation-cascades-in-bear-markets) described Celsius's liquidity crunch and noted that 3AC liquidated more than 80,000 stETH into ETH and DAI to help close leveraged positions. This turned an exchange-rate discount into cross-platform stress.

## Metrics Used

### stETH/ETH discount

The primary signal is the discount between stETH and ETH on secondary markets.

Useful metrics include:

- stETH/ETH price ratio by venue;
- maximum intraday discount;
- duration of discount below 0.99, 0.97, and 0.95 ETH;
- spread between Curve price and centralized-exchange price;
- volume traded while below peg.

### Curve pool imbalance

The Curve pool was the main exit venue, so its composition mattered as much as the headline price.

Useful metrics include:

- percentage of pool reserves held as stETH;
- ETH available for same-block exits;
- slippage for 1,000, 10,000, and 50,000 stETH sales;
- net liquidity withdrawals by large wallets;
- pool rebalancing speed after major sales.

### Large-holder exit pressure

Market-health monitoring should separate broad retail selling from concentrated institutional exits.

Useful metrics include:

- stETH transfers from labeled Celsius, 3AC, Alameda, and other large wallets;
- sale size relative to Curve ETH depth;
- Aave collateral changes tied to stETH positions;
- debt repayments funded by stETH sales;
- wallet-level withdrawal timing around public solvency concerns.

### Redemption and lender stress

The stETH discount became more dangerous because some platforms owed users immediately liquid assets.

Useful metrics include:

- centralized-lender stETH balance versus customer ETH liabilities;
- withdrawal queue pressure;
- pause or withdrawal-limit announcements;
- borrowed stablecoin or ETH used to meet redemptions;
- collateral top-ups or debt repayments during the depeg.

The same fields are summarized in [steth-curve-liquidity-signals.csv](steth-curve-liquidity-signals.csv) for dataset-based review.

| Signal                  | Observation                                                       | Market-health interpretation                                         |
| ----------------------- | ----------------------------------------------------------------- | -------------------------------------------------------------------- |
| stETH discount          | Public reporting described a 2-5% stETH/ETH gap in June 2022      | Liquid-staking claims need secondary-market liquidity monitoring     |
| Curve pool imbalance    | CoinDesk reported the main stETH Curve pool was nearly drained    | Exit capacity can disappear before nominal backing changes           |
| Large-holder sales      | Nansen-linked reporting cited Celsius, 3AC, and other stETH sales | Concentrated exits can transmit stress across venues and lenders     |
| Celsius withdrawal halt | Celsius paused withdrawals on June 12                             | Lender redemption pressure can turn a market discount into run risk  |
| Leveraged unwind        | 3AC reportedly sold more than 80,000 stETH into ETH and DAI       | Collateral unwind can amplify depeg and liquidation-cascade dynamics |

## Timeline

- **May 2022:** Terra/UST stress and wider crypto-market declines increased demand for liquid collateral and stable liquidity.
- **June 9-12, 2022:** stETH selling pressure increased and the Curve stETH/ETH pool became heavily imbalanced.
- **June 12, 2022:** Celsius paused withdrawals, swaps, and transfers, citing extreme market conditions.
- **Mid-June 2022:** stETH traded at a sustained discount while large holders reduced positions and tried to protect leveraged loans.
- **Late June 2022:** Nansen-linked reporting connected the stETH depeg to Celsius, 3AC, Curve pool imbalance, and broader post-Terra contagion.

## Market Health Lessons

The stETH event shows that a token can be solvent in the long run while unhealthy in the short run. Market Health needs to measure whether a holder can exit now, not only whether the claim may redeem later.

For liquid-staking tokens and other receipt assets, dashboards should track secondary-market depth, pool composition, labeled large-holder exits, lender liability mismatch, and lending-market collateral exposure. When redemption is disabled or delayed, a pool imbalance can become the first public signal that a solvency story is turning into a liquidity crisis.
