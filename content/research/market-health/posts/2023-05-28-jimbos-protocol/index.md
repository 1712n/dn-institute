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

## On-Chain Evidence

I reproduced the exploit transaction receipt from Arbitrum block `95144408` and
decoded WETH `Transfer` events from transaction
`0x44a0f5650a038ab522087c02f734b80e6c748afb207995e757ed67ca037a5eda`. The
supporting files in this directory are:

- `build-jimbos-onchain-evidence.py`: fetches the receipt from Arbitrum RPC and
  regenerates the CSV and SVG artifacts.
- `jimbos-exploit-weth-transfers.csv`: every decoded WETH transfer in receipt
  order, with log index, labeled sender, labeled receiver, raw addresses, and
  WETH amount.
- `jimbos-exploit-weth-actors.csv`: actor-level gross inflow, gross outflow,
  net transfer delta, and maximum/minimum transfer-implied balance delta.

{{< figure src="jimbos-exploit-weth-flow.svg" alt="WETH transfer-implied balance deltas for the Jimbos exploit transaction" caption="WETH transfer-implied balance deltas across the exploit receipt. The chart starts each actor at zero and plots only deltas produced by decoded WETH Transfer logs, not full historical balances." >}}

Three receipt-derived findings matter for Market Health analysis:

1. The exploit did not just contain a large swap; it contained a fast liquidity
   feedback loop. The Jimbos controller received `14,402.122913` WETH from the
   liquidity-book token and sent the same amount back out during the same
   receipt. That is `28,804.245826` WETH of gross controller/liquidity-book
   movement inside one transaction.
2. The attack contract received `10,000` WETH from the Aave Arbitrum WETH source
   at log index 1 and repaid `10,005` WETH at log index 358. The receipt-level
   transfer trail therefore shows the flash-loan principal and fee boundary.
3. The attack contract's WETH transfer-implied delta ended at `625.999746` WETH
   after repayment, while public incident reports estimate the broader protocol
   loss at about `4,090` ETH. The gap is important: market-health monitoring
   should not look only at attacker wallet profit. It should also track gross
   liquidity churn, protocol-owned liquidity exposure, and post-trade venue
   depth.

## Manipulation Pattern

The JIMBO market did not show a gradual repricing event. The receipt evidence
shows a single-transaction liquidity distortion bounded by a visible funding leg
and repayment leg:

1. Log index `1` moves `10,000` WETH from the Aave Arbitrum WETH source into
   `attack_contract`, while log index `358` returns `10,005` WETH to the same
   source. Those two rows define the transaction's temporary-capital boundary
   without relying on a prose description of the attack.
2. Between those boundary rows, the attack contract's transfer-implied WETH
   delta rises to `10,630.999746` WETH before falling back to `625.999746` WETH
   after repayment. The useful market-health signal is therefore not just a
   large trade; it is a large temporary inventory swing that appears and unwinds
   inside one receipt.
3. The controller and liquidity-book actor rows show `28,804.245826` WETH of
   gross controller/liquidity-book churn. That gross flow is the evidence that
   protocol-owned liquidity migrated during the distorted state rather than
   remaining passive background depth.
4. The liquidity-book actor ends the receipt at `-630.999746` WETH on a
   transfer-implied basis. That links the temporary push-away period to a
   measurable depletion of venue-side WETH depth.
5. The market-health pattern is the joint condition: temporary capital enters,
   protocol liquidity moves while the venue state is distorted, and the same
   transaction closes with repayment plus residual attacker-side WETH.

That receipt-derived pattern matters because it separates real user demand from
manufactured venue state. A price series alone might show a spike and crash; the
healthier interpretation is to pair price action with pool depth,
protocol-owned-liquidity movement, and same-transaction reversal boundaries.

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
transfers, current tick/range selection, and minimum-output checks. In this
transaction, decoded WETH transfers show the controller cycling more gross WETH
through the liquidity book than the attacker's reported `10,000` WETH flash-loan
principal. That makes controller/liquidity-book gross flow a direct risk metric,
not just an accounting detail.

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
