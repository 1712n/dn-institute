---
title: "KiloEx Oracle Price-Path Manipulation"
description: "A Market Health case study on how attacker-controlled oracle-price transitions let KiloEx positions open at artificial lows and close at artificial highs across multiple chains."
date: 2025-04-14
tags:
  - KiloEx
  - Oracle manipulation
  - Perpetuals
  - BNB Chain
  - Base
  - opBNB
---

## Key points

1. The April 2025 KiloEx exploit shows a market-health failure mode where a trading venue treated externally supplied oracle-price updates as executable position state.
2. SlowMist's incident recap says the attacker exploited a public `execute` path in `MinimalForwarder` to trigger `PositionKeeper.setPrices` and manipulate opening and closing prices on opBNB, Base, and BSC.
3. Halborn's analysis describes the price path as attacker-influenced low values for opening positions followed by inflated values for closing them, including examples such as opening ETH exposure around $100 and closing around $10,000.
4. Public reports put the initial loss near $7.5 million to $8.4 million. KiloEx later announced that all stolen funds had been recovered after coordination with security firms, exchanges, and ecosystem partners.
5. The surveillance lesson is not simply "protect the admin key." A market-health monitor should flag when an external forwarder, batch executor, or oracle relay can move executable prices far outside venue and reference-market bands during the same trading path.

The companion file [`kiloex-oracle-price-signals.csv`](kiloex-oracle-price-signals.csv) records the source-linked evidence points used below. The chart reconstructs the control path from public reporting rather than replaying each chain trace.

{{< figure src="kiloex-price-path.svg" alt="KiloEx oracle price manipulation control path" caption="Selected public evidence points from the April 2025 KiloEx oracle-price manipulation." loading="lazy" >}}

## The fragile market structure

KiloEx operated as an on-chain perpetual trading venue where position execution depended on oracle prices. That is normal for many derivatives venues, but it creates a hard market-health boundary: price inputs must be independent, timely, and bounded before they can define a trader's entry or exit value.

The incident exposed a failure at that boundary. SlowMist identifies the exposed route as the public `execute` function on `MinimalForwarder`. In that route, forwarded calls into `executeIncreasePositions` and `executeDecreasePositions` could reach `PositionKeeper.setPrices`, so the same execution flow that changed position size also supplied the price inputs used to value the trade. Once that separation failed, KiloEx's accounting could credit positions using one synthetic valuation on entry and a different synthetic valuation on exit, instead of checking both against independent market prices.

In market-health terms, the exploit converted an oracle relay into the market. The attack did not need broad external venues to clear ETH, BTC, or BNB at the manipulated prices. It needed KiloEx's own execution stack to treat the synthetic path as authoritative for position accounting.

## The price-path loop

Halborn's public analysis gives the clearest economic shape. It describes positions opened at artificially low prices and closed at artificially high prices. For example, Halborn says ETH positions were opened near $100 and closed near $10,000, BTC positions were opened near $1,000 and closed near $100,000, and BNB positions were opened near $10 and closed near $1,000.

Those values are not subtle market deviations. They are circuit-breaker signals. A derivatives venue whose oracle path accepts a 100x same-asset jump inside the execution lifecycle is no longer tracking the external market. It is honoring a manipulated accounting state.

SlowMist's timeline adds useful operational structure:

1. An Ethereum funding transaction occurred before the exploit sequence.
2. The attacker deployed operational contracts on BSC, Base, and opBNB.
3. The attacker used the public forwarder execution path to update prices while increasing and decreasing positions.
4. The same strategy was repeated across several assets and chains.
5. KiloEx suspended platform operations and later announced full fund recovery.

The multi-chain repetition matters because it turns a one-off logic flaw into a platform-wide market-health problem. Once the oracle relay path was exposed, every chain and asset route that trusted the same execution pattern inherited the same price-integrity failure.

## What the public signals show

The public evidence supports four monitorable signals:

1. **Forwarder-to-position coupling:** a public forwarder path reached price-setting logic that should have been tightly constrained.
2. **Same-path entry and exit manipulation:** the attack used artificial lows to enter and artificial highs to exit, so entry/exit price deltas were themselves the anomaly.
3. **Cross-chain reuse:** SlowMist lists deployments and attacks across BSC, Base, and opBNB, showing that the failure pattern was portable.
4. **Loss-to-recovery separation:** recovery after the incident does not change the pre-incident market-health failure. The useful detection window sits before the manipulated positions close.

The loss estimates vary by source because different reports measure different assets, chains, and recovery states. SlowMist summarizes KiloEx's official root-cause framing and says all stolen funds were recovered. Cointelegraph reported a compensation plan for users affected by a $7 million-plus hack and later reported the return of the stolen funds. The Block reported a compensation plan after an estimated $7.5 million price exploit. Those figures all point to the same economic materiality: this was not a low-severity accounting bug.

## Surveillance indicators

### Oracle-price excursion bands

- Reject or pause any position execution where the open or close price falls outside an independent reference band for the same asset.
- Treat 10x or 100x same-asset moves inside a single execution path as a hard-fail condition, even before final profit is known.
- Compare submitted oracle values against multiple external venues and the venue's own recent fills before position accounting is finalized.

### Entry-exit asymmetry

- Monitor for positions opened at extreme discounts and closed at extreme premiums within a short lifecycle.
- Score open/close price deltas by asset volatility, not by a static absolute threshold.
- Escalate if the same account or contract repeatedly realizes profit from the same low-entry/high-exit structure.

### Forwarder and relay reachability

- Inventory every public function or trusted-forwarder path that can reach price-setting or position-execution logic.
- Require signed, bounded, and replay-protected price updates before a forwarder can trigger market execution.
- Alert when a non-oracle account submits price payloads that directly affect trading outcomes.

### Multi-chain blast radius

- Apply incident controls across all deployments that share the same execution stack.
- If one chain reports abnormal oracle-price deltas, pause equivalent routes on sibling deployments until the shared relay path is reviewed.
- Track whether attacker contracts are redeployed across chains within the same response window.

## Controls that would have changed the outcome

1. A hard separation between public forwarder execution and oracle price-setting authority.
2. Independent price-band checks on every open and close path, with fail-closed behavior for out-of-band values.
3. Position lifecycle checks that reject impossible open-to-close price deltas for the same asset and account.
4. Per-chain kill switches that propagate to sibling deployments when a shared executor or oracle relay fails.
5. An execution simulator that tests whether arbitrary forwarded calls can reach price-critical state.
6. Real-time monitoring for repeated low-entry/high-exit profit loops across assets.

## Why this belongs in a market manipulation wiki

KiloEx is useful for a Market Health wiki because the core harm is price-state manipulation. The exploit used a smart-contract path, but the economic outcome came from making the venue accept fake market prices for real position accounting. A market observer would see artificial entry prices, artificial exit prices, repeated cross-chain execution, and large realized gains without corresponding external-market movement.

That makes the case transferable. Any venue that depends on signed price updates, relayers, keepers, or trusted forwarders should treat price authority as part of market integrity. The right control is not only "fix the forwarding bug." It is to prove that no execution path can convert a private or attacker-chosen price into a public venue quote without independent validation.

## References

- SlowMist, "SlowMist Assists KiloEx in Recovering All Stolen Funds: Incident Recap", April 23, 2025: https://slowmist.medium.com/slowmist-assists-kiloex-in-recovering-all-stolen-funds-incident-recap-273d10f6d466
- Halborn, "Explained: The KiloEx Hack (April 2025)", April 28, 2025: https://www.halborn.com/blog/post/explained-the-kiloex-hack-april-2025
- Cointelegraph, "KiloEx compensation plan after $7M hack", April 16, 2025: https://cointelegraph.com/news/kiloex-compensation-plan-7-million-hack-april
- Cointelegraph, "KiloEx hacker returns all stolen funds", April 18, 2025: https://cointelegraph.com/news/kiloex-hacker-returns-all-stolen-funds
- The Block, "KiloEx price exploit compensation", April 16, 2025: https://www.theblock.co/post/351839/kiloex-price-exploit-compensation
- KiloEx docs, "Trading Rules": https://docs.kiloex.io/kiloex-docs/trading/trading-rules
