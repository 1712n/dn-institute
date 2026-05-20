---
title: "UwU Lend sUSDe Oracle Manipulation and crvUSD Cascade"
date: "2024-06-10"
description: "UwU Lend's June 2024 exploit shows how a manipulable lending oracle can turn temporary pool-price pressure into protocol losses and then propagate into crvUSD liquidation stress."
entities:
  - UwU Lend
  - sUSDe
  - crvUSD
  - CRV
  - Curve Lend
---

On June 10, 2024, the UwU Lend exploit turned a short-lived sUSDe pool-price distortion into a lending-market drain. The same incident then fed a second market-health problem: stolen CRV was used as Curve Lend collateral to borrow crvUSD, and the extra CRV supply helped set up the June 12 liquidation stress described by LlamaRisk.

The useful signal is not only that a lending protocol lost funds. It is that the manipulated price was a market input reused by a credit system. A price source that can be moved during a flash-loan transaction becomes a way to manufacture borrowing capacity, force liquidations, and export stress to connected lending markets.

{{< figure src="uwu-lend-oracle-cascade.svg" caption="Selected public metrics from the UwU Lend oracle manipulation and follow-on crvUSD stress. Source rows are in the companion CSV." >}}

## Evidence Snapshot

The companion file [`uwu-lend-oracle-cascade-events.csv`](uwu-lend-oracle-cascade-events.csv) records the event-level data used for this article. The strongest quantitative rows are:

- CUBE3 split the first UwU attack into three malicious transactions worth approximately $7.15m, $6.72m, and $4.14m.
- CUBE3 measured the manipulated sUSDe price path from $0.98821237 to $1.03183659 during the exploit flow, a roughly 4.4% intratransaction swing.
- LlamaRisk identified 23.6m CRV used as Curve Lend collateral to borrow about 8.1m crvUSD in one exploit-linked transaction.
- LlamaRisk later observed nearly 200m CRV supplied in the CRV-long Curve Lend market and peak debt of about $55m during the June 12 stress window.
- The Block reported a second UwU Lend exploit of about $3.7m on June 13, after the protocol had said the original sUSDe oracle vulnerability was resolved.

## Manipulation Mechanism

UwU Lend used a custom price path for sUSDe. Verichains traced the root cause to the `sUSDePriceProviderBUniCatch` oracle path and noted that the oracle mixed external price feeds with pool-derived prices. CUBE3's transaction analysis shows why that design was fragile: the attacker sourced large flash liquidity, moved the Curve pool state that the oracle path observed, borrowed against the resulting valuation, and then used liquidation calls to convert the temporary mark into durable assets.

This is a market-manipulation pattern even though the immediate victim was a lending protocol. The trade sequence created a price that was not representative of normal clearing conditions, then used the manipulated mark as a collateral-accounting input. The critical threshold was not a persistent depeg; it was a temporary price excursion large enough to change health factors and liquidation economics inside one block-level execution path.

## Contagion Path

LlamaRisk's crvUSD report is the key second-stage evidence. The UwU exploiter did not simply dump all stolen CRV into DEX liquidity. Instead, the attacker used 23,617,586.248 CRV as collateral to borrow 8,123,821.056 crvUSD. That choice transferred exploit inventory into another credit market.

The June 12 CRV drawdown then interacted with a much larger CRV-long Curve Lend market. LlamaRisk reported nearly 200m CRV supplied and peak debt of roughly $55m in that market. The crvUSD upward depeg was a liquidity-response failure during liquidation pressure, not a simple stablecoin demand story. In market-health terms, the initial oracle manipulation created an inventory shock, and the credit system amplified it through collateral concentration and liquidation mechanics.

## Monitoring Lessons

For Market Health, the incident suggests four practical indicators:

1. Lending markets that price collateral from manipulable pool spot values should be tagged as high-risk venues, especially when the pool is thin relative to borrowable liquidity.
2. A stablecoin or LSD pair does not need to depeg for hours to be exploitable. An intratransaction swing of a few percent can be enough if a lending market reads the manipulated value synchronously.
3. Post-exploit collateral movement matters. Large stolen positions moved into lending markets can create delayed stress even after the original exploit transaction is over.
4. "Vulnerability fixed" claims should be treated as unverified until the remaining inventory, bad debt, and downstream pool exposure are reduced. The June 13 second exploit is a reminder that the first incident can leave reusable state or assets behind.

## Sources

- CUBE3.AI, [Days in Advance, CUBE3.AI Detected Sophisticated $18M UwU Lend Attack](https://blog.cube3.ai/2024/06/11/cube3-ai-detected-uwu-lend-attack-days-in-advance/)
- Verichains, [UwU hacked cause by price oracle manipulated](https://blog.verichains.io/p/uwu-hacked-cause-by-price-oracle)
- LlamaRisk, [crvUSD Upward Depeg (June 12, 2024) Incident Report](https://research.llamarisk.com/research/crvusd-incident-report-20240612)
- The Block, [UwU Lend drained for $3.7 million in second exploit this week](https://www.theblock.co/post/299901/uwu-lend-second-hack-this-week)
