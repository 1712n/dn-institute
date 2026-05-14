---
title: "KyberSwap Elastic Tick Manipulation and Concentrated-Liquidity Market Health"
date: "2023-11-22"
description: "KyberSwap Elastic's November 2023 exploit shows how precise tick-boundary swaps, flash-loan notional, and liquidity-state mismatch can create artificial AMM prices and broad LP losses."
entities:
  - KyberSwap
  - KyberSwap Elastic
  - KNC
  - WETH
  - wstETH
  - USDC
  - Arbitrum
  - Ethereum
---

## Summary

On November 22, 2023, KyberSwap Elastic pools were manipulated through a highly precise concentrated-liquidity exploit. The incident is already documented as a security event in the cyberattacks section, but it also belongs in Market Health because the loss mechanism depended on artificial AMM prices, tick-boundary movement, flash-loan notional, and incorrect liquidity accounting.

KyberSwap's post-mortem estimated 2,367 affected liquidity providers and approximately $56.2 million in affected assets. The team attributed about $48.7 million to the primary exploiter and another $6.6 million to mimicking bots. A later IRS-CI announcement alleged that the KyberSwap exploit drained approximately $48.8 million from 77 pools across six public blockchains.

The main market-health lesson is that concentrated-liquidity markets need monitoring beyond ordinary price and volume charts. A pool can show a technically valid sequence of swaps while its internal tick and liquidity state becomes economically false. That creates a temporary market where the quoted price, the effective liquidity, and the true redeemable assets no longer describe the same venue.

## Why this is a market manipulation case

KyberSwap Elastic was a concentrated-liquidity automated market maker. Liquidity providers could place capital in price ranges, and pool state changed as swaps crossed tick boundaries. The attacker used borrowed assets and carefully sized swaps to move a pool into a state where the code treated liquidity as available when the economically correct state should have reduced or removed it.

In market-health terms, the exploit combined four warning signs:

1. **Large temporary notional:** SharkTeam described an analyzed transaction where the attacker borrowed 10,000 wstETH before manipulating a pool.
2. **Extreme local price displacement:** In that transaction, SharkTeam reported the wstETH price moving from about 1.05 ETH to 0.000015257 during setup.
3. **Near-boundary precision:** KyberSwap's post-mortem describes a calculated swap amount that landed around a tick-boundary rounding inconsistency.
4. **Liquidity-state mismatch:** After the tick manipulation, the pool behaved as though more liquidity existed than should have been available.

This differs from simple wash trading. The exploiter did not merely print fake volume to impress an external ranking site. The manipulation changed the local AMM state so later swaps could extract assets from liquidity providers at distorted effective prices.

## Signal table

The companion CSV file, [`kyberswap-elastic-market-signals.csv`](kyberswap-elastic-market-signals.csv), summarizes the main observable signals:

| Signal                     | Observation                                              | Market-health interpretation                            |
| -------------------------- | -------------------------------------------------------- | ------------------------------------------------------- |
| Affected users             | 2,367 LP addresses identified by KyberSwap               | Broad LP impact rather than a bilateral failed trade    |
| Affected assets            | About $56.2 million in affected assets                   | Economic loss after market-state distortion             |
| Primary exploiter amount   | About $48.7 million attributed to the original exploiter | Main manipulation separated from copycat flow           |
| Mimicking bots amount      | About $6.6 million attributed to mimicking bots          | Publicly observable venue weakness was quickly repeated |
| Pool and chain breadth     | IRS-CI alleged 77 pools across six chains                | Systemic concentrated-liquidity risk across deployments |
| Flash-loan notional        | 10,000 wstETH borrowed in SharkTeam's example            | Temporary capital overwhelmed local pool state          |
| Extreme price displacement | wstETH moved from about 1.05 ETH to 0.000015257          | Price action inconsistent with normal market-making     |
| Tick-boundary precision    | Swap amount selected near a rounding boundary            | Boundary-focused CLMM manipulation indicator            |

## Detection approach

For concentrated-liquidity venues, a monitoring system should treat the following as higher-risk combinations:

- **Large flash-loan-funded swaps followed by liquidity mints and burns** in the same block or transaction bundle.
- **Price movement into a narrow or empty tick range** before a reverse-direction swap.
- **Swap amounts close to the amount required to cross a tick boundary**, especially when the amount is one unit below a calculated threshold.
- **Liquidity changes that do not match tick movement**, where the pool price crosses or appears to cross a range boundary but base liquidity is not reduced as expected.
- **Copycat extraction shortly after the first exploit**, because a vulnerable pool state can become visible to bots before the protocol is paused.

These checks are venue-specific. A central-limit-order-book exchange might watch order-book spoofing, cancellation bursts, and trade self-matching. A concentrated-liquidity AMM also needs invariant checks over tick state, local liquidity, reinvested liquidity, and price movement.

## Impact on market health

KyberSwap's impact table shows that the incident did not affect only a few large market makers. The affected LP distribution included hundreds of addresses with losses below $1,000 and a small set of addresses with losses above $1 million. That distribution matters because liquidity provision is part of market infrastructure. If LPs cannot trust the relationship between displayed pool price, tick state, and redeemable assets, liquidity withdraws and spreads widen across related venues.

The cross-chain scope also matters. The same category of manipulation was not confined to one chain's congestion, one asset's liquidity, or one isolated pool. According to the IRS-CI release, the alleged theft touched 77 pools on six public blockchains. That breadth is a market-health signal: when identical pool logic is deployed across chains, a single state-accounting weakness can become a multi-venue liquidity shock.

## Mitigation metrics

Future monitoring for KyberSwap-like concentrated-liquidity markets should include:

- **Boundary-distance ratio:** how close each swap amount is to the amount required to cross the next tick.
- **Temporary-notional-to-active-liquidity ratio:** flash-loan or same-transaction input size divided by active in-range liquidity.
- **Tick/liquidity consistency check:** whether liquidity updates match the final tick implied by the post-swap price.
- **Reverse-swap extraction ratio:** output value from the reverse leg compared with the local liquidity added by the attacker.
- **Cross-pool repetition score:** number of pools receiving the same transaction pattern within a short time window.

These metrics would not replace smart-contract audits, but they would give operators and LP dashboards earlier warning when a market is being forced into an artificial state.

## References

- [KyberSwap post-mortem: KyberSwap Elastic exploit November 2023](https://blog.kyberswap.com/post-mortem-kyberswap-elastic-exploit/)
- [IRS-CI / J5 press release on KyberSwap and Indexed Finance indictment](https://www.irs.gov/pub/irs-ci/j5-media-release-2-10-25.pdf)
- [SharkTeam analysis of the KyberSwap attack incident](https://sharkteam.org/report/analysis/20231127001A_en.pdf)
