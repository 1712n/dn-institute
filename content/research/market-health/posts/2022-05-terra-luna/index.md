---
title: "Terra/Luna Collapse: How a $40 Billion Algorithmic Stablecoin Failed Through Design Flaws and Market Manipulation"
date: "2022-05-07 -- 2022-05-13"
description: "The Terra/Luna ecosystem collapsed in May 2022 when the UST algorithmic stablecoin lost its peg, triggering a hyperinflationary death spiral in LUNA that wiped out approximately $40 billion in market value within a week."
entities:
  - Terra
  - Luna
  - UST
  - Anchor Protocol
---

## Summary

In May 2022, the Terra blockchain ecosystem experienced one of the largest collapses in cryptocurrency history when its algorithmic stablecoin UST lost its dollar peg, triggering a cascading failure that destroyed approximately $40 billion in combined market value. The collapse exposed fundamental design flaws in the algorithmic stabilization mechanism and raised questions about whether large withdrawals from the Anchor Protocol lending platform were coordinated to deliberately destabilize the peg. Terra founder Do Kwon was subsequently arrested in March 2023 and convicted of fraud in 2024.

## The Algorithmic Peg Mechanism

Unlike stablecoins backed by dollar reserves (USDC, USDT), UST maintained its peg through an algorithmic mint-and-burn mechanism with LUNA. Users could always exchange 1 UST for $1 worth of LUNA, and vice versa. When UST traded above $1, arbitrageurs would mint UST by burning LUNA, increasing UST supply and pushing the price down. When UST traded below $1, arbitrageurs would burn UST and mint LUNA, reducing UST supply and pushing the price up.

This mechanism worked in stable conditions but contained a critical vulnerability: it depended on continuous demand for LUNA to absorb the selling pressure generated when large amounts of UST were redeemed. If confidence in the system wavered and redemptions accelerated, each UST burned would mint more LUNA, diluting LUNA's value, which would further reduce confidence, triggering more UST redemptions in a self-reinforcing death spiral.

## The Anchor Protocol Dependency

Anchor Protocol, a lending platform on Terra, offered approximately 20% annual yield on UST deposits. This yield was subsidized by the Luna Foundation Guard (LFG) and was not sustainable through organic lending demand alone. By May 2022, approximately 75% of all UST in circulation was deposited in Anchor, meaning the stablecoin's demand was overwhelmingly driven by a single unsustainable yield source.

This concentration created a structural fragility: if Anchor's yield was reduced or confidence in its sustainability wavered, a large portion of UST's demand could evaporate simultaneously.

## The Collapse

On May 7, 2022, large withdrawals from Anchor Protocol began, with approximately $2 billion in UST removed over two days. The selling pressure pushed UST below its $1 peg. The Luna Foundation Guard deployed approximately $1.5 billion in Bitcoin reserves to defend the peg, but the intervention was insufficient.

As UST's price fell further below $1, the arbitrage mechanism kicked in, burning UST and minting massive quantities of LUNA. LUNA's circulating supply exploded from approximately 350 million to over 6.5 trillion tokens in days, causing its price to collapse from $80 to fractions of a cent.

By May 13, UST was trading at approximately $0.10 and LUNA was effectively worthless. The combined market value destruction was estimated at $40 billion.

## Manipulation Allegations

Significant debate exists over whether the initial Anchor withdrawals were coordinated to deliberately trigger the death spiral. Analysis of on-chain activity showed that several large wallets executed substantial UST sales on Curve Finance in a pattern consistent with an intentional attack on the peg rather than organic selling.

The Luna Foundation Guard's deployment of Bitcoin reserves to defend the peg was also criticized as potentially benefiting insiders who could front-run the known selling pressure. The transparency of the reserve deployment allowed observers to anticipate LFG's actions and position accordingly.

## Detection Patterns

The Terra/Luna collapse illustrates systemic risks that market health monitoring should address:

- **Unsustainable yield as a demand driver.** When a stablecoin's circulating supply is predominantly held in a single yield-generating protocol offering above-market returns, the stability of the peg is directly tied to the sustainability of that yield. Monitoring the concentration of stablecoin deposits in individual protocols can identify this vulnerability before it materializes.
- **Algorithmic peg stress testing.** The mint-and-burn mechanism had never been tested under conditions of sustained, large-scale redemption pressure. Monitoring the ratio of UST redemptions to LUNA market depth could have identified the threshold at which the stabilization mechanism would enter a death spiral.
- **Reserve deployment transparency.** When peg defense reserves are deployed publicly and predictably, the defense itself becomes front-runnable. Monitoring large reserve movements and correlated trading activity on secondary markets can detect whether defense mechanisms are being exploited.
