---
title: "Jimbos Protocol JIMBO Liquidity-Shift Manipulation"
date: 2023-05-28
entities:
  - Jimbos Protocol
  - JIMBO
  - WETH
  - Arbitrum
---

## Summary

On May 28, 2023, Jimbos Protocol was drained for about 4,090 ETH, worth roughly
$7.5 million at the time. The incident is a useful Market Health case because
the profit path depended on a short-lived, attacker-created price imbalance in
the JIMBO/WETH pool rather than on ordinary directional demand for JIMBO.

Security analyses from [Halborn](https://www.halborn.com/blog/post/explained-the-jimbos-protocol-hack-may-2023),
[Numen Cyber](https://www.numencyber.com/jimbos-protocol-hack/), and
[Rekt](https://rekt.news/jimbo-rekt) describe the same core sequence: the
attacker borrowed ETH, bought a large amount of JIMBO, pushed the pool price
away from normal levels, triggered the protocol's `shift()` liquidity operation,
and then sold the remaining JIMBO back into WETH after the protocol had moved
liquidity into the manipulated range.

The market-health lesson is that an automated liquidity-management protocol can
convert a temporary pool distortion into a real solvency event when it trusts
the current pool state without slippage, delay, or independent price checks.

## Timeline

| Date         | Event                                                                                      | Market-health signal                                               |
| ------------ | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| May 2023     | Jimbos Protocol relaunched v2 after a problematic first launch.                            | New liquidity design with limited production history.              |
| May 28, 2023 | The attacker used a flash loan and large JIMBO buy to move the pool price.                 | Abrupt average transaction size and price-impact spike.            |
| May 28, 2023 | The attacker called `shift()` and forced protocol liquidity into the distorted pool state. | Protocol-owned liquidity followed the manipulated venue price.     |
| May 28, 2023 | The attacker sold JIMBO back into the pool and drained WETH liquidity.                     | Buy/sell flow reversed after the rebalance; JIMBO price collapsed. |
| May 29, 2023 | Jimbos Protocol offered an on-chain settlement proposal to recover funds.                  | Loss confirmed as a protocol solvency and user-confidence event.   |

## Manipulation Pattern

The JIMBO market did not show a gradual repricing event. It showed an atomic
liquidity distortion:

1. The attacker took a large flash loan, reported by Numen Cyber as 10,000 ETH.
2. The borrowed ETH was swapped into the JIMBO/WETH pair, creating a sharp
   JIMBO price increase in the pool.
3. A small amount of JIMBO was sent to the controller, and `shift()` was called.
4. Because the shift operation lacked adequate slippage controls, protocol funds
   were moved using the manipulated pool state.
5. The attacker reversed the trade, sold JIMBO into the now-exposed WETH
   liquidity, repaid the flash loan, and kept the difference.

That sequence matters because it separates real user demand from manufactured
venue state. A price series alone might show a spike and crash; the healthier
interpretation is to pair price action with pool depth, protocol-owned liquidity
movement, and same-block buy/sell reversal.

## Metrics To Monitor

### Average Transaction Size

The opening swap was abnormally large relative to normal retail activity. A
monitor should flag sudden jumps in average transaction size on the JIMBO/WETH
pool, especially when a single transaction both creates and consumes most of the
price impact.

### Buy/Sell Flow Reversal

The manipulation required a buy leg followed by a sell leg after protocol
liquidity had been repositioned. A sharp buy/sell ratio swing inside a short
block window is a stronger signal than raw volume alone, because the attacker's
goal was not accumulation. It was to alter the state used by `shift()`.

### Protocol-Owned Liquidity Movement

The highest-risk step was not the initial buy. It was the protocol moving WETH
liquidity in response to the distorted price. For liquidity-management systems,
pool price impact should be monitored together with protocol-owned-liquidity
transfers, current tick/range selection, and minimum-output checks.

### Post-Manipulation Depth

After the reverse swap, WETH liquidity was drained and JIMBO repriced sharply
lower. Thin post-event depth indicates that the prior price was not supported by
organic liquidity. A market-health dashboard should treat a same-transaction
depth collapse as a venue-quality alert.

## Detection Rules

- Flag any `shift()` or rebalance call that follows a large same-block swap in
  the relevant pool.
- Require slippage and minimum-output bounds before moving protocol-owned
  liquidity.
- Compare current pool price with a time-weighted price or an independent
  reference before executing liquidity management.
- Alert when one account or transaction path both pushes price away from normal
  levels and reverses the position after a protocol action.
- Treat a rapid price increase followed by liquidity exhaustion as a market
  integrity event, even if the contract call itself succeeds.

## Why This Belongs In Market Health

Jimbos Protocol shows that DeFi market health is not just an exchange-volume
problem. In automated liquidity systems, protocol actions can become the
counterparty to manipulated prices. The attacker did not need to convince
outside traders that JIMBO was worth more; the attacker only needed the protocol
to act as if the transient pool price was valid.

The practical lesson is to measure both market behavior and protocol behavior.
Average transaction size, buy/sell ratio, and depth changes identify the
distortion. Rebalance timing, slippage bounds, and liquidity destination explain
whether the distortion can become an extractable loss.

## References

- Halborn, [Explained: The Jimbos Protocol Hack (May 2023)](https://www.halborn.com/blog/post/explained-the-jimbos-protocol-hack-may-2023)
- Numen Cyber, [A Detailed Analysis of Arbitrum-based Jimbos Protocol's $7.5 Million Hack](https://www.numencyber.com/jimbos-protocol-hack/)
- Rekt, [Jimbo's Protocol - REKT](https://rekt.news/jimbo-rekt)
