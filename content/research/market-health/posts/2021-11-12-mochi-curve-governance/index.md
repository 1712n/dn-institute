---
title: "Mochi USDM Curve Gauge Governance Attack"
date: "2021-11-12"
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

1. Mochi Inu launched a Curve pool containing stablecoins and its USDM stablecoin; reports place peak liquidity around $100 million to $170 million.
2. Curve and later security writeups said a large amount of USDM was used to acquire Curve/Convex governance exposure, including CVX or CRV-based voting power.
3. The concern was a reflexive loop: self-issued liquidity could fund governance-token accumulation, governance votes could increase rewards to the USDM pool, and higher rewards could attract more liquidity back into the same pool.
4. Curve's Emergency DAO cut off the USDM gauge rewards after characterizing the situation as a governance attack and a liquidity-provider risk.
5. Market surveillance should treat sudden liquidity growth, concentrated governance-token purchases, and fast reward-weight changes as correlated signals rather than isolated events.

## Mechanism

Curve gauges route token incentives to liquidity pools. Convex Finance builds on top of Curve by aggregating Curve voting power and distributing extra rewards to liquidity providers. In healthy conditions, this reward market can be competitive: projects acquire voting influence, vote for their gauges, and provide real liquidity or fees to justify incentives.

The Mochi case showed how that market can become fragile when the same project can rapidly create or route capital into the reward-voting system. According to Crypto Briefing's account of Curve's position, Mochi minted a large amount of MOCHI, used it to mint USDM, bought a large number of CVX tokens, and locked those tokens despite warnings, seemingly to increase incentives to its own USDM factory pool. Halborn describes the same incident as a governance hack attempt in which Mochi's USDM pool liquidity was used to acquire Curve governance influence and redirect rewards toward the pool.

This created three market-health concerns:

- **Self-funded voting power:** governance-token buying pressure was linked to a project-controlled asset rather than independent market demand.
- **Incentive reflexivity:** if new rewards attracted more pool liquidity, the project could gain more capital to keep reinforcing the reward loop.
- **Exit and collateral risk:** liquidity providers could be exposed if the self-issued side of the pool became undercollateralized or if incentives disappeared suddenly.

## Market health indicators

Useful monitoring signals for similar cases include:

- **Pool composition drift:** track how much of a pool's liquidity is made up of project-issued or project-controlled assets versus neutral assets such as USDC, USDT, DAI, or ETH.
- **Issuer-linked swap bursts:** flag large swaps from a project stablecoin or governance token into voting assets such as CRV, CVX, veCRV, or vlCVX, especially soon after pool launch.
- **Reward weight discontinuities:** compare a gauge's new vote weight and reward APR against its organic trading volume, fee generation, and independent liquidity depth.
- **Borrowed or minted-liquidity loops:** identify whether the same entity can mint, borrow, or route assets that are then used to buy voting power for the pool it controls.
- **Emergency-governance actions:** treat gauge removals, blocked emissions, or emergency-DAO interventions as post-event labels for training risk rules.

## Timeline

- **November 2021:** Mochi Inu set up a Curve pool for USDM and other stablecoins. Public reports cite roughly $100 million to $170 million in pool liquidity.
- **November 2021:** Reports describe large USDM-funded swaps into governance or vote-escrow exposure, with the apparent goal of increasing rewards to the Mochi/USDM pool.
- **November 2021:** Curve's Emergency DAO cut off the USDM gauge rewards after declaring liquidity providers at risk.
- **After the intervention:** Security and market observers framed the event as a governance attack or an aggressive exploitation of reward mechanics rather than a simple technical bug.

## Mitigations

- Require longer observation windows before newly launched pools with issuer-controlled assets can receive large emissions.
- Cap reward weight or gauge emissions when liquidity is dominated by a single issuer-linked asset.
- Monitor governance-token purchases and vote-lock events from wallets associated with newly listed pools.
- Combine liquidity metrics with governance metrics; high TVL alone is not a proof of healthy, independent demand.
- Publish incident labels for emergency interventions so that future reward-market anomalies can be detected earlier.

## Sources

- [Halborn: Explained: The Mochi Inu Governance Hack (November 2021)](https://www.halborn.com/blog/post/explained-the-mochi-inu-governance-hack-november-2021)
- [Crypto Briefing: Curve Blocks Mochi After Alleged Attempted Governance Attack](https://cryptobriefing.com/curve-blocks-mochi-after-alleged-attempted-governance-attack/)
- [Chainlink: Market Manipulation vs. Oracle Exploits](https://chain.link/education-hub/market-manipulation-vs-oracle-exploits)
