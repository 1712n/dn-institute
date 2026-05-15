---
title: "Mochi USDM Curve Gauge Governance Attack"
date: "2021-11-10"
description: "A Market Health case study on Mochi Inu's alleged attempt to use self-issued USDM liquidity and Curve/Convex voting power to redirect emissions toward its own pool."
entities:
  - Mochi Inu
  - USDM
  - Curve Finance
  - Convex Finance
  - CRV
  - CVX
---

## Summary

In November 2021, Mochi Inu's USDM pool on Curve became a useful example of **governance-power manipulation** in DeFi markets. The reported sequence was not a classic exchange wash-trading event or a price-oracle exploit. Instead, the concern was that value created around a self-issued asset could be recycled into governance and reward-voting power, steering incentives toward the same pool and attracting additional liquidity.

Key points:

1. Mochi Inu launched a Curve pool containing stablecoins and its USDM stablecoin; contemporary reports place peak liquidity at **$170.2 million**.
2. Curve and later security writeups said a large amount of USDM was used to acquire Curve/Convex governance exposure, including CVX or CRV-based voting power.
3. The concern was a reflexive loop: self-issued liquidity could fund governance-token accumulation, governance votes could increase rewards to the USDM pool, and higher rewards could attract more liquidity back into the same pool.
4. Curve's Emergency DAO cut off the USDM gauge rewards after characterizing the situation as a governance attack and a liquidity-provider risk.
5. Market surveillance should treat sudden liquidity growth, concentrated governance-token purchases, and fast reward-weight changes as correlated signals rather than isolated events.

## Mechanism

Curve gauges route token incentives to liquidity pools. Convex Finance builds on top of Curve by aggregating Curve voting power and distributing extra rewards to liquidity providers. In healthy conditions, this reward market can be competitive: projects acquire voting influence, vote for their gauges, and provide real liquidity or fees to justify incentives.

The Mochi case showed how that market can become fragile when the same project can rapidly create or route capital into the reward-voting system. A concise reconstruction from public reporting is: newly issued project value helped expand USDM exposure, that exposure was routed into CVX/Curve voting influence, and the resulting locked voting power could be pointed back at the project's own pool. Crypto Briefing reported Curve's concern that this sequence was meant to increase incentives for the USDM factory pool, while Halborn later categorized the episode as an attempted governance hack that used pool-linked liquidity to redirect rewards.

This created three market-health concerns:

- **Self-funded voting power:** governance-token buying pressure was linked to a project-controlled asset rather than independent market demand.
- **Incentive reflexivity:** if new rewards attracted more pool liquidity, the project could gain more capital to keep reinforcing the reward loop.
- **Exit and collateral risk:** liquidity providers could be exposed if the self-issued side of the pool became undercollateralized or if incentives disappeared suddenly. Public incident discussions treated this as central rather than incidental because USDM's oracle was reportedly set manually by a team-controlled address while about **99.5%** of circulating MOCHI supply was team-controlled, creating a direct manual-oracle plus supply-concentration undercollateralization risk.

## Market health indicators

The following thresholds are not proof of manipulation by themselves. They are practical alert heuristics that should trigger analyst review when multiple conditions appear in the same 24- to 72-hour window.

| Signal | Example alert rule | Measurement notes |
| --- | --- | --- |
| Pool composition drift | Flag when an issuer-linked asset is more than **35% of pool TVL for 12+ hours**, or rises by **20 percentage points in 24 hours**. | Use pool balances at hourly snapshots; denominator is total pool TVL in USD. |
| Issuer-linked swap bursts | Flag when wallets associated with the issuer swap more than **$5 million**, or more than **2% of pool depth**, into CRV, CVX, veCRV, or vlCVX in 24 hours. | Aggregate by labeled issuer wallets and obvious freshly funded intermediaries; compare trade size with pool depth before the swap. |
| Reward weight discontinuities | Flag when gauge vote weight increases by **50%+ in one voting epoch** while 7-day organic volume or fees grow by less than **10%**. | Compare gauge weights against volume, fee generation, and independent liquidity depth. |
| Wallet concentration | Flag when the top **5 wallets control more than 60%** of LP tokens, vote-escrow influence, or newly locked voting tokens. | Exclude known protocol contracts only when custody is genuinely dispersed. |
| Borrowed or minted-liquidity loops | Escalate when project-issued assets are minted, borrowed, swapped into voting tokens, and then used to support the same issuer's pool within **72 hours**. | Treat the loop as stronger when each leg is visible on-chain and amounts are material relative to TVL. |
| Emergency-governance actions | Label as severe when an emergency DAO removes a gauge, blocks emissions, or publicly states LPs are at risk. | Use these interventions as post-event labels for future detector training. |

A high-confidence alert should require at least two pre-event signals, for example issuer-linked swaps above the threshold plus a reward-weight jump in the same epoch. A severe alert should be raised if those signals are followed by an emergency governance action.

## Timeline

- **Early November 2021:** USDM pool liquidity rapidly expanded. An alerting system would flag this if issuer-linked assets exceeded **35% of TVL for 12+ hours** or grew by **20 percentage points in 24 hours**.
- **November 10, 2021:** Mochi's token launch and USDM pool growth quickly attracted nearly **$100 million** in liquidity, then later peaked at about **$170.2 million**. A detector would escalate if issuer-linked liquidity growth coincided with new voting-token accumulation.
- **November 10, 2021:** Public reports described USDM-funded swaps into governance or vote-escrow exposure, including converting USDM to DAI before purchasing Convex exposure. A detector would escalate if those swaps exceeded **$5 million** or **2% of pool depth** within a 24-hour window.
- **November 10–11, 2021:** Reward-routing risk increased as voting power could be directed toward the same pool; observers also traced unusual CVX price action to an address that had swapped roughly **46 million USDM** to DAI. Gauge monitors should compare the epoch's vote-weight change with 7-day volume and fee growth.
- **November 10–11, 2021:** Curve's Emergency DAO cut off the USDM gauge rewards after declaring liquidity providers at risk. This is the post-event severe label for the alert chain.
- **After the intervention:** Security and market observers framed the event as a governance attack or an aggressive exploitation of reward mechanics rather than a simple technical bug.

## Mitigations

- Require at least **two complete voting epochs** before newly launched pools with issuer-controlled assets can receive uncapped emissions.
- Cap gauge emissions when issuer-linked assets are above **35% of TVL** or when the top **5 wallets exceed 60%** of LP/vote influence.
- Rate-limit reward-weight increases, for example no more than **25% per epoch** unless 7-day organic volume, fees, and independent liquidity also rise.
- Add automatic review when issuer-linked wallets buy or lock more than **$5 million** of voting assets in 24 hours.
- Combine liquidity metrics with governance metrics; high TVL alone is not a proof of healthy, independent demand.
- Publish incident labels for emergency interventions so that future reward-market anomalies can be detected earlier.

## Sources

- [Halborn: Explained: The Mochi Inu Governance Hack (November 2021)](https://www.halborn.com/blog/post/explained-the-mochi-inu-governance-hack-november-2021)
- [Crypto Briefing: Curve Blocks Mochi After Alleged Attempted Governance Attack](https://cryptobriefing.com/curve-blocks-mochi-after-alleged-attempted-governance-attack/)
- [Curve Governance: The Curve Emergency DAO has killed the USDM gauge](https://gov.curve.finance/t/the-curve-emergency-dao-has-killed-the-usdm-gauge/2307)
