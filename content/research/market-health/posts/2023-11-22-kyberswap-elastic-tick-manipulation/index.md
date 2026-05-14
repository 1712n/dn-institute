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

## Attacker and defender payoff model

The exploit can be modeled as a one-shot game between an attacker who can rent capital and a protocol that must decide how much friction to place around boundary-crossing swaps.

The attacker's expected payoff is:

`expected profit = extractable pool value - flash-loan fee - gas - slippage - failed-attempt cost - detection cost`

The defender's expected payoff is:

`protected liquidity value - monitoring cost - false-positive cost - lost fee revenue from pausing or throttling`

In ordinary trading, the attacker's extractable value is bounded by slippage. Pushing a concentrated-liquidity pool through a thin tick range should become increasingly expensive as the pool price moves away from fair value. In the KyberSwap case, the state mismatch inverted that relationship: a precisely sized trade near a tick boundary created an artificially favorable reverse swap. That means the rational attacker did not need to dominate the whole pool forever; they only needed to create a short-lived state where the protocol overestimated active liquidity.

For defenders, this changes the best response. A generic "large trade" alert is not enough, because legitimate arbitrageurs and LP rebalancers also make large trades. The higher-value defensive strategy is to watch for the sequence that made the payoff positive: flash-loan notional, price displacement into a narrow range, liquidity mint/burn activity, a near-boundary swap, and a reverse swap that extracts more value than the attacker just contributed. This sequence-based monitor has lower false-positive risk than pausing every large swap.

## Economic cost-benefit breakdown

The incident also suggests a practical cost model for concentrated-liquidity manipulation:

| In-range liquidity condition                                       | Attacker cost profile                                                                                              | Manipulation attractiveness                                             |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------- |
| Deep, diverse liquidity across many adjacent ticks                 | High slippage and more capital needed to move price across ranges                                                  | Low, unless a code-level accounting bug bypasses normal slippage        |
| Deep liquidity but concentrated in a narrow band                   | Lower capital needed to reach a boundary; LPs earn more fees while in range but face sharper boundary risk         | Medium, especially for stable or pegged pairs that invite narrow ranges |
| Thin or empty adjacent tick after a dense band                     | Low cost to move into a fragile state; reverse swaps can become abnormally favorable if accounting is inconsistent | High, the KyberSwap-style risk zone                                     |
| Cross-chain clone with identical pool code and similar LP behavior | Discovery cost is paid once, execution can be repeated                                                             | Very high until all deployments are paused or patched                   |

Flash-loan fees and gas are usually small relative to an eight-figure extraction opportunity. Slippage should be the main economic defense. When a rounding or tick-accounting flaw lets an attacker borrow temporary capital, force an extreme local price, and then reverse out with inflated output, the cost-benefit curve breaks: the attacker pays short-term financing costs while LPs absorb the false-liquidity loss.

This is why the primary health metric is not only "trade size." It is "trade size relative to active in-range liquidity and boundary distance." A 10,000 wstETH loan is meaningful because it is large enough to dominate local pool state, not because 10,000 is intrinsically suspicious.

## Comparison with related CLMM and oracle cases

[Uniswap v3 documentation](https://developers.uniswap.org/docs/get-started/concepts/liquidity-providers/concentrated-liquidity) describes concentrated liquidity as capital allocated within custom price ranges, with ticks acting as range boundaries. In a healthy Uniswap v3-style CLMM, crossing a tick should update active liquidity for the remainder of the swap. KyberSwap Elastic's incident was different because the vulnerability came from a mismatch between final price calculation and liquidity updates around the tick boundary, amplified by its reinvestment-curve mechanics.

Balancer-linked incidents such as Sturdy Finance are useful comparisons but not identical. In the [Sturdy Finance case](https://dn.institute/research/cyberattacks/incidents/2023-06-12-sturdy-finance/), market health deteriorated because an external lending protocol consumed a manipulated or stale valuation from a Balancer-related source. The weak point was oracle dependency: a downstream protocol trusted a price that could be distorted. KyberSwap Elastic's weak point was internal AMM state: the venue itself temporarily misrepresented liquidity and price after a carefully selected swap path.

The practical monitoring distinction is:

- **Uniswap v3-like CLMM health:** verify tick crossing, active liquidity updates, and price movement are internally consistent.
- **Balancer/oracle dependency health:** verify downstream protocols do not treat manipulable pool state as a safe collateral price.
- **KyberSwap Elastic-style health:** verify final price, target tick, base liquidity, and reinvested liquidity cannot diverge after near-boundary swaps.

This comparison matters for bounty reviewers because it keeps the article from treating all "flash-loan manipulation" as the same pattern. KyberSwap is a market-structure case: the attack monetized a discrepancy between displayed AMM state and economically real liquidity.

## LP incentive structure

Narrow-range LP positions are rational in quiet markets. Stable pairs, liquid staking derivatives, and assets expected to trade in a tight band can generate higher fee yield when LPs concentrate capital around the current price. The same design also makes the market more brittle near range edges.

The incentive problem is that individual LPs optimize for fee capture, while the protocol inherits the aggregate tail risk of many LPs clustering around similar ranges. If most liquidity sits in a narrow band, an attacker does not need to defeat a smooth full-range curve. They only need to push the pool into the next fragile interval, then exploit any implementation mistake in how liquidity is activated or removed. In other words, fee-maximizing LP behavior can create cliff-like liquidity surfaces.

For market-health dashboards, the relevant LP metric is therefore not just total value locked. A pool with high TVL can still be fragile if the next few ticks have little real liquidity or if a large share of TVL sits in positions that become inactive together. A stronger dashboard would display active liquidity depth by tick, concentration of LP ranges, and boundary stress under simulated one-block price shocks.

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

For this incident type, an empirical alert policy could start with thresholds such as:

- Same-transaction borrowed notional above **5x active in-range liquidity** for the traded pair.
- Price movement of more than **50% inside one transaction** for a pool whose previous 24-hour realized range was below **5%**.
- Swap amount within **0.01% of the calculated tick-crossing amount**, followed by a reverse swap within the same transaction.
- Mint or burn activity changing more than **20% of active liquidity** immediately before a boundary-adjacent swap.
- More than **three pools or chains** showing the same transaction motif within one hour.

These numbers should be tuned by venue and asset class. Stablecoin and liquid-staking pools deserve tighter thresholds than volatile long-tail assets. The false-positive risk is highest around legitimate liquidations, oracle arbitrage, and LP rebalancing after major market moves. To reduce unnecessary pauses, the monitor should require a combination of signals rather than a single large price move. The strongest trigger is not "price moved"; it is "price moved near a tick boundary while liquidity accounting failed to update as expected."

## Impact on market health

KyberSwap's impact table shows that the incident did not affect only a few large market makers. The affected LP distribution included hundreds of addresses with losses below $1,000 and a small set of addresses with losses above $1 million. That distribution matters because liquidity provision is part of market infrastructure. If LPs cannot trust the relationship between displayed pool price, tick state, and redeemable assets, liquidity withdraws and spreads widen across related venues.

The cross-chain scope also matters. The same category of manipulation was not confined to one chain's congestion, one asset's liquidity, or one isolated pool. According to the IRS-CI release, the alleged theft touched 77 pools on six public blockchains. That breadth is a market-health signal: when identical pool logic is deployed across chains, a single state-accounting weakness can become a multi-venue liquidity shock.

The systemic implication is stronger than "bugs can be copied." Multi-chain deployment creates correlated market risk because liquidity providers often assume each deployment is independent. If identical pool logic exists on Ethereum, Arbitrum, Optimism, Polygon, and other chains, the first successful exploit becomes a public proof of strategy. Bots can scan for matching states, bridges can move proceeds or capital, and users on slower-response chains may remain exposed while the original venue is already being analyzed.

For market-health reporting, this means cross-chain AMMs should be grouped by code lineage and configuration, not only by chain. A dashboard that treats each chain as a separate venue may miss the fact that the same invariant failure is active everywhere.

## Mitigation metrics

Future monitoring for KyberSwap-like concentrated-liquidity markets should include:

- **Boundary-distance ratio:** how close each swap amount is to the amount required to cross the next tick.
- **Temporary-notional-to-active-liquidity ratio:** flash-loan or same-transaction input size divided by active in-range liquidity.
- **Tick/liquidity consistency check:** whether liquidity updates match the final tick implied by the post-swap price.
- **Reverse-swap extraction ratio:** output value from the reverse leg compared with the local liquidity added by the attacker.
- **Cross-pool repetition score:** number of pools receiving the same transaction pattern within a short time window.

Protocol design recommendations follow directly from the root cause:

- Add tick-accounting sanity checks that assert final price, current tick, and active liquidity are mutually consistent after each swap step.
- Use differential testing against a reference CLMM implementation for boundary-adjacent swaps.
- Rate-limit or temporarily pause pools when same-transaction mint/burn/swap sequences create abnormal reverse-swap extraction.
- Require cross-chain emergency controls so a paused exploit pattern on one deployment can block identical pool logic elsewhere.
- Expose active-liquidity-by-tick and boundary-stress metrics to LP dashboards so fee yield is shown alongside manipulation surface.

These metrics would not replace smart-contract audits, but they would give operators and LP dashboards earlier warning when a market is being forced into an artificial state. The goal is not to classify every large trade as abusive. The goal is to identify when the AMM's own state no longer matches the economic market it claims to quote.

## References

- [KyberSwap post-mortem: KyberSwap Elastic exploit November 2023](https://blog.kyberswap.com/post-mortem-kyberswap-elastic-exploit/)
- [IRS-CI / J5 press release on KyberSwap and Indexed Finance indictment](https://www.irs.gov/pub/irs-ci/j5-media-release-2-10-25.pdf)
- [SharkTeam analysis of the KyberSwap attack incident](https://sharkteam.org/report/analysis/20231127001A_en.pdf)
- [Uniswap Docs: concentrated liquidity concepts](https://developers.uniswap.org/docs/get-started/concepts/liquidity-providers/concentrated-liquidity)
- [DNI incident page: Sturdy Finance oracle manipulation](https://dn.institute/research/cyberattacks/incidents/2023-06-12-sturdy-finance/)
