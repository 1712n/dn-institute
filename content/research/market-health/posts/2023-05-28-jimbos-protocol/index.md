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
[Rekt](https://rekt.news/jimbo-rekt) give the factual basis for this case. In
market-health terms, the attack can be read as a state-oracle failure: flash-loan
capital created temporary buying pressure, the JIMBO/WETH pool translated that
pressure into an inflated spot price, `shift()` treated the distorted venue as a
safe liquidity target, and the closing sell leg converted the protocol's
misplaced WETH depth into extractable value.

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
2. The borrowed ETH was swapped into the JIMBO/WETH pair, making the pool's
   current price look healthier than the surrounding liquidity could support.
3. A small amount of JIMBO was sent to the controller, and `shift()` was called,
   causing protocol logic to consume the manipulated spot state.
4. The liquidity move concentrated protocol-owned WETH where the attacker could
   trade against it with poor protection from slippage or stale-price checks.
5. The attacker reversed the position, sold JIMBO into the newly exposed WETH
   depth, repaid the loan, and left the market with lower usable liquidity and a
   broken price signal.

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

Use configurable thresholds rather than vague labels:

- `large_swap_liquidity_pct = X`: flag any `shift()` or rebalance call when the
  preceding swap is more than X% of pool liquidity, or when its notional value is
  more than `large_swap_sigma = N` standard deviations above the rolling
  `large_swap_window_blocks = M`-block swap-size baseline. Require the swap and
  rebalance to occur in the same block or within `rebalance_lag_blocks = K`.
- `slippage_pct` and `min_output_amount`: before moving protocol-owned
  liquidity, simulate the rebalance and fail the routine if expected slippage is
  greater than `slippage_pct` or if the output asset amount is less than
  `min_output_amount`.
- `twap_window_short = 5m`, `twap_window_long = 1h`,
  `spot_twap_deviation_pct = Y`, and `spot_twap_zscore = Z`: compare current
  spot price with short and long TWAPs or an independent reference price, then
  block liquidity management when spot price deviates by more than Y% or by a
  z-score greater than Z.
- `reversal_blocks = T` and `push_away_pct`: link the account, transaction path,
  or bundle that pushed price away from TWAP with any reverse trade after a
  protocol action. Alert when the push-away magnitude exceeds `push_away_pct`
  and the reversal lands within T blocks.
- `rapid_move_pct = A`, `rapid_move_blocks = B`, and
  `minimum_depth_delta`: treat a price increase greater than A% inside B blocks
  followed by a depth drop larger than `minimum_depth_delta` as a market
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
