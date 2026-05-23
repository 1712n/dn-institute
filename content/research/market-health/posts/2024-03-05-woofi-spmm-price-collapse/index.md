---
title: "WOOFi WOO sPMM Price-Collapse Manipulation"
description: "A Market Health case study on how repeated low-liquidity WOO trades pushed WOOFi's synthetic PMM price state close to zero and created a narrow automated-response window."
date: 2024-03-05
tags:
  - WOOFi
  - WOO
  - Arbitrum
  - Synthetic PMM
  - Price manipulation
---

## Key points

1. WOOFi's March 2024 exploit shows a market-health failure mode where a synthetic market maker converts one account's temporary low-liquidity trade path into an extreme internal price.
2. WOOFi's postmortem says the exploiter borrowed about 7.7 million WOO plus other assets, sold WOO into WOOFi, drove the sPMM price adjustment close to zero, then swapped out 10 million WOO at nearly no cost.
3. The same pattern repeated three times within minutes and produced about $8.75 million in profit after flash loans were returned.
4. The fallback control did not cover WOO because the WOO token price was not checked against Chainlink in that path. WOOFi reported the extreme adjusted price as $0.00000009.
5. Forta's public timeline shows a useful detection window: first attack transaction at 15:42:06 UTC, first alert at 15:42:22 UTC, second attack at 15:49:29 UTC, third attack at 15:53:58 UTC, and WOOFi pause capability later used during the incident.

The companion file [`woofi-spmm-exploit-signals.csv`](woofi-spmm-exploit-signals.csv) records the source-linked transaction, alert, and postmortem signals used below. The chart compresses those signals into a response-window view rather than a full Arbitrum trace replay.

{{< figure src="woofi-spmm-response-window.svg" alt="WOOFi sPMM price manipulation response window" caption="Selected public evidence points from the March 2024 WOOFi WOO sPMM manipulation sequence." loading="lazy" >}}

## The fragile market structure

WOOFi's synthetic proactive market maker was designed to simulate centralized-exchange order-book depth. Instead of using a constant-product pool alone, WOOFi's sPMM adjusted price, spread, and depth around oracle-informed state.

That design is useful when the reference state is bounded and liquidity assumptions remain realistic. The March 2024 incident exposed the other side of the design: when a newly feasible WOO borrow route appeared on Arbitrum and WOO liquidity was thin, the sPMM adjustment itself became the market that could be manipulated.

WOOFi's postmortem says the attacker sold borrowed WOO into WOOFi and caused the sPMM to adjust WOO to an extreme near-zero price. The same account could then buy a much larger WOO amount at almost no cost in the same transaction path. This is different from a normal market loss caused by adverse flow. The protocol's internal pricing state moved outside a usable range and then honored that state for the next leg.

## The price-collapse path

The public postmortem and Arbiscan-linked transactions give a compact signal chain:

1. Flash liquidity funded WOO inventory and other assets.
2. The attacker sold WOO into WOOFi during a period of limited Arbitrum-side WOO liquidity.
3. WOOFi's sPMM adjustment pushed the internal WOO price to a value WOOFi later reported as $0.00000009.
4. The fallback check did not stop the trade because WOO did not have the Chainlink-covered fallback in that path.
5. The attacker swapped out 10 million WOO at nearly no cost.
6. The sequence repeated three times within roughly twelve minutes from the first to the third attack transaction.

Forta's transaction links provide useful cadence data. The first attack transaction occurred at 15:42:06 UTC and triggered the first Forta alert at 15:42:22 UTC. The second and third attack transactions followed at 15:49:29 UTC and 15:53:58 UTC. That means the first public alert arrived about seven minutes before the second transaction and more than eleven minutes before the third.

The market-health lesson is that the critical signal was not just "large swap." It was the combination of large same-asset trade, abnormal sPMM price displacement, missing independent price fallback, and repeated near-identical execution before the venue could pause.

## What the transaction signals show

Arbiscan labels all three transactions as calls by "WooFi Exploiter 1." The pages expose three useful, source-level signals:

1. Repetition: three successful attack transactions in one short window.
2. Complexity growth: 45 logs and 24 ERC-20 transfers in the first transaction; 51 logs and 28 ERC-20 transfers in the second; 54 logs and 30 ERC-20 transfers in the third.
3. ETH-scale value movement: each transaction page shows about 559 to 561 ETH in internal transfers.

Those figures do not by themselves prove profit. The profit estimate comes from WOOFi's postmortem, which reported about $8.75 million after flash loans were returned. The transaction figures matter because they are the raw cadence and complexity evidence that a monitor could have acted on before the sequence finished.

## Surveillance indicators

### Synthetic price displacement

- Alert when a synthetic PMM price adjustment moves an asset far outside the range implied by independent venues.
- Treat near-zero internal prices for a live collateral or trading asset as a circuit-breaker condition, not as a tradeable quote.
- Measure the gap between pre-trade oracle state, adjusted sPMM state, and fallback price coverage.

### Borrowed-inventory dominance

- Compare borrowed WOO inventory against Arbitrum-side liquidity and recent executed depth.
- Flag transactions where borrowed inventory is immediately sold into the venue that recalculates the next leg's price.
- Require stricter limits when a newly listed lending market makes a token's inventory easier to source than the venue's available depth.

### Repeated execution cadence

- Escalate after the first abnormal WOO price displacement rather than waiting for cumulative loss.
- Watch for repeated same-account, same-method, same-asset flows within minutes.
- Combine transaction-log count, ERC-20 transfer count, and net pool value movement into a single response score.

### Fallback coverage failure

- Inventory every token whose sPMM price can override oracle state.
- Verify that each token has a live independent fallback before it can be traded through a high-notional path.
- Fail closed when the adjusted price moves outside a configured band and the fallback source is absent.

## Controls that would have changed the outcome

1. A hard price band around WOO's adjusted sPMM price, with automatic pause when the adjustment implies a near-zero live asset price.
2. A per-token fallback coverage requirement before the asset can be listed in an sPMM route.
3. A same-transaction limit that prevents selling a large borrowed inventory into the model and then buying a larger WOO amount from the distorted model.
4. A low-liquidity listing review tied to external borrow availability, not only to WOOFi's own pool balances.
5. An automated response hook that can pause the affected route after the first abnormal transaction or first external alert.
6. A repetition guard that blocks a second same-pattern transaction by the same account before manual review.

## Why this belongs in a market manipulation wiki

The WOOFi exploit is a useful Market Health case because it turns price manipulation into a venue-design problem. The attack did not need a broad public market to believe WOO was worthless. It only needed WOOFi's own pricing model to accept a temporary, attacker-created flow state as a valid executable quote.

That makes the incident transferable to other synthetic or oracle-assisted venues. Any venue that models price from external data plus recent trade notional should monitor whether the model can be driven outside real liquidity. The warning signs were concrete: low WOO liquidity on the target network, large borrowed inventory, a missing fallback check, an internal price near zero, repeated transactions within minutes, and a pause window that existed before the full sequence ended.

## References

- WOOFi, "WOOFi sPMM exploit post-mortem", March 5, 2024: https://woox.io/blog/woofi-spmm-exploit-post-mortem
- Forta, "WooTrade Hack Detected in Advance by Forta ($4.8M)", March 14, 2024: https://www.forta.org/blog/wootrade-hack-detected-in-advance-by-forta-4-8m
- Arbiscan, first attack transaction `0x57e555328b7def90e1fc2a0f7aa6df8d601a8f15803800a5aaf0a20382f21fbd`: https://arbiscan.io/tx/0x57e555328b7def90e1fc2a0f7aa6df8d601a8f15803800a5aaf0a20382f21fbd
- Arbiscan, second attack transaction `0x40e1b8c78083fc666cb7598efcecd0ae0af313fc41441386e4db716c2808ce07`: https://arbiscan.io/tx/0x40e1b8c78083fc666cb7598efcecd0ae0af313fc41441386e4db716c2808ce07
- Arbiscan, third attack transaction `0xe80a16678b5008d5be1484ec6e9e77dc6307632030553405863ffb38c1f94266`: https://arbiscan.io/tx/0xe80a16678b5008d5be1484ec6e9e77dc6307632030553405863ffb38c1f94266
- Distributed Networks Institute, "The WOOFi suffered a flash loan exploit on Arbitrum": https://dn.institute/research/cyberattacks/incidents/2024-03-05-woofi/
