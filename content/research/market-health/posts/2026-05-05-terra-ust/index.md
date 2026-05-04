---
title: "🌰 Terra UST — Algorithmic Stablecoin Death Spiral and Anchor Run"
date: 2026-05-05
entities:
  - Terra
  - TerraUSD
  - LUNA
  - Anchor Protocol
  - Terraform Labs
  - Do Kwon
---

## Summary

1. **In May 2022, TerraUSD (UST), one of the largest algorithmic stablecoins, lost its intended $1 peg and entered a reflexive death spiral with LUNA**, the volatile token used in Terra's mint-and-burn stabilization mechanism. Within days, UST traded far below $1 and LUNA hyperinflated toward near-zero market value.
2. **The collapse erased tens of billions of dollars in UST/LUNA market value and triggered wider crypto-market contagion**. The direct ecosystem loss is commonly estimated around $40-60 billion, while broader market drawdowns and follow-on insolvencies affected lenders, funds, exchanges, and retail investors across the industry.
3. **Anchor Protocol's high UST yield was central to the system's growth and fragility**. Anchor advertised roughly 20% APY on UST deposits for much of Terra's growth phase, attracting a large share of circulating UST. When confidence weakened and deposits fled, the same concentration amplified redemption pressure.
4. **The design combined a confidence-sensitive stablecoin with a reflexive collateral token**. When UST traded below peg, arbitrageurs could burn UST for $1 worth of LUNA, but heavy redemptions minted large amounts of LUNA, depressing LUNA's price and reducing confidence in the mechanism's ability to restore UST.
5. **The incident became a defining market-health case for algorithmic stablecoins, subsidized DeFi yields, reserve transparency, and run-risk surveillance**. It showed that peg stability, total value locked, and high yields can mask fragile liquidity if exit capacity depends on continued confidence in a volatile endogenous asset.

## Background

### Terra and UST

Terra was a Cosmos-SDK-based blockchain ecosystem developed by Terraform Labs. Its best-known product was TerraUSD (UST), an algorithmic stablecoin intended to maintain a value near $1 without being fully backed by dollar reserves. UST was paired with LUNA, the Terra network's volatile native asset.

The core mechanism was:

| UST market condition | Intended arbitrage |
|----------------------|-------------------|
| UST > $1 | Users could burn $1 worth of LUNA to mint 1 UST, increasing UST supply |
| UST < $1 | Users could burn 1 UST to mint $1 worth of LUNA, reducing UST supply |

In theory, arbitrage would pull UST back toward $1. In practice, the mechanism depended on market confidence that newly minted LUNA would retain enough value to absorb redemptions. That assumption failed under stress.

### Anchor Protocol

Anchor Protocol was a lending and savings application on Terra that became the primary source of UST demand. It offered a high target yield on UST deposits, often described around 19.5-20% APY. The yield was funded by borrower interest, staking rewards, and a yield reserve that required subsidies when natural revenue was insufficient.

Anchor's role created several market-health risks:

1. **Concentration risk**: A large fraction of UST supply sat in one yield venue.
2. **Subsidy risk**: A high target yield required external support when organic borrower demand was not enough.
3. **Run risk**: If depositors lost confidence, exits could happen quickly because deposits were liquid.
4. **Reflexive peg risk**: UST withdrawals increased sell pressure on UST and redemption pressure on LUNA.
5. **Narrative risk**: The stablecoin's adoption story depended heavily on yield rather than payments utility.

## Timeline

| Date | Event |
|------|-------|
| 2020 | Terra's algorithmic stablecoin model gains traction across Terra applications |
| 2021 | UST supply grows rapidly alongside Anchor Protocol deposits |
| Early 2022 | Luna Foundation Guard (LFG) accumulates Bitcoin and other reserves intended to support UST's peg |
| May 7-8, 2022 | Large UST withdrawals and swaps pressure the peg; UST begins trading below $1 |
| May 9-10, 2022 | UST depegs more severely; Anchor deposits fall sharply; LUNA issuance accelerates |
| May 11-12, 2022 | LUNA price collapses as supply expands; exchanges begin halting or restricting LUNA/UST markets |
| May 13, 2022 | Terra validators halt the chain during crisis conditions, then restart with restrictions |
| Late May 2022 | Terra community approves a new chain, while the original chain continues as Terra Classic |
| 2023 | SEC charges Terraform Labs and Do Kwon with fraud-related claims |
| 2024 | Terraform Labs and Do Kwon are found liable for fraud in a U.S. civil case; settlement and bankruptcy processes follow |

## Mechanism of the Collapse

### The UST/LUNA Reflexive Loop

UST's stabilizing mechanism relied on a conversion rule: 1 UST could be redeemed for $1 worth of LUNA. This created a stabilizing incentive under normal conditions but a destabilizing feedback loop under panic conditions.

When UST traded below $1:

1. Traders bought discounted UST.
2. They redeemed UST for $1 worth of newly minted LUNA.
3. They sold LUNA to realize the spread or hedge exposure.
4. LUNA selling pressure pushed LUNA's price down.
5. Lower LUNA price required minting more LUNA per UST redeemed.
6. Expanding LUNA supply weakened confidence further.
7. UST holders rushed to exit before the mechanism lost more capacity.

This is the classic algorithmic-stablecoin death spiral: the asset intended to absorb stablecoin redemptions falls in value precisely when redemption demand is highest.

### Anchor Withdrawal Pressure

Anchor made UST useful by giving holders a simple reason to buy and hold it: high yield. But that same concentration meant UST demand was highly sensitive to confidence in Anchor's yield and Terra's peg.

During the May 2022 stress:

- UST deposits left Anchor rapidly.
- Withdrawn UST moved to liquidity pools and exchanges.
- Curve and centralized-exchange liquidity became stress points.
- Peg-defense reserves were deployed but did not restore durable confidence.
- LUNA issuance accelerated as redemptions increased.

This dynamic resembled a bank run without deposit insurance, a lender of last resort, or a fully collateralized reserve backing each UST.

### Reserve Defense and LFG

In early 2022, Luna Foundation Guard accumulated reserves, including Bitcoin, intended to help defend UST's peg. These reserves changed the system from a purely algorithmic stablecoin toward a partially reserve-supported one, but the reserves were not large enough to cover all UST liabilities at par during a full run.

Reserve-design issues:

| Issue | Market-health concern |
|-------|----------------------|
| Reserve size | Reserves were smaller than total UST supply during peak stress |
| Asset volatility | BTC reserves could fall in value during crypto-wide panic |
| Transparency | Real-time reserve deployment and remaining balances were difficult for ordinary users to verify during the run |
| Execution | Selling reserves into stressed markets can worsen broader market pressure |
| Confidence | Partial reserves may slow a run but cannot guarantee par redemption if liabilities are larger |

The reserve episode illustrates why stablecoin surveillance should monitor not only collateral quantity but also collateral liquidity, volatility, governance, and redemption rules.

## Market Impact

### Direct Ecosystem Loss

UST and LUNA had reached very large market capitalizations before the collapse. The direct value destruction is commonly described in the tens of billions of dollars. Exact estimates vary depending on the date and method used:

| Component | Approximate impact |
|-----------|--------------------|
| LUNA market value | Collapsed from a top cryptoasset to near-zero on the original chain |
| UST market value | Fell from a large stablecoin supply at $1 target to deeply discounted levels |
| Direct Terra ecosystem loss | Commonly cited around $40-60B |
| Broader market drawdown | Hundreds of billions in crypto market value moved during the same period, though not all is attributable solely to Terra |

The safer interpretation is that Terra was a major catalyst in a broader deleveraging cycle, not the sole cause of every subsequent market loss.

### Contagion Channels

Terra's collapse propagated through several channels:

1. **Balance-sheet exposure**: Funds and lenders exposed to LUNA, UST, Anchor, or Terra ecosystem assets suffered direct losses.
2. **Leverage unwinds**: Falling prices triggered liquidations and forced selling across correlated crypto assets.
3. **Confidence shock**: Investors reassessed stablecoin risk, yield products, and DeFi collateral assumptions.
4. **Liquidity stress**: Exchanges and market makers had to manage volatile UST/LUNA order books and halted markets.
5. **Legal/regulatory response**: Stablecoin regulation and disclosure discussions accelerated after the collapse.

Several later failures in 2022 involved multiple causes, including Three Arrows Capital, Celsius, Voyager, BlockFi, and FTX/Alameda. Terra was an important early shock in that chain, but each later insolvency had its own risk-taking, leverage, governance, or fraud allegations.

## Legal and Regulatory Fallout

### SEC Action

In February 2023, the U.S. Securities and Exchange Commission charged Terraform Labs and Do Kwon, alleging a multi-billion-dollar cryptoasset securities fraud. The SEC's allegations included claims that investors were misled about UST's stability, LUNA, and use of Terra technology in payment applications.

In 2024, a U.S. jury found Terraform Labs and Do Kwon liable for fraud in a civil case. Terraform later reached a settlement with the SEC, and related bankruptcy and enforcement processes continued. Criminal and extradition proceedings involving Do Kwon also developed across jurisdictions.

For market-health analysis, the legal lesson is not simply that a peg failed. The key issue is whether public statements, risk disclosures, yield claims, and reserve representations matched the actual fragility of the system.

### Stablecoin Policy

Terra became a reference case in stablecoin policy debates:

- Fully reserved stablecoins were contrasted with algorithmic designs.
- Regulators focused on redemption rights, reserve quality, and disclosures.
- DeFi yield products drew scrutiny when advertised yields depended on subsidies or token incentives.
- Policymakers debated whether large stablecoins should face bank-like, money-market-fund-like, or payment-instrument regulation.

## Vulnerability Pattern: Endogenous Collateral

UST's central market-health flaw was endogenous collateral. The asset used to restore the peg, LUNA, was created by the same system and depended on confidence in that system.

| Design feature | Stress behavior |
|----------------|-----------------|
| UST redeemable for $1 worth of LUNA | Creates arbitrage in normal markets, but mints LUNA under redemptions |
| LUNA market value absorbs UST exits | Works only while LUNA market cap and liquidity remain credible |
| Anchor yield drives UST demand | High growth can be subsidy-driven rather than organic payment demand |
| Partial external reserves | Can slow panic but may be insufficient for full par redemption |
| Liquid deposits | Users can run quickly when confidence breaks |

Endogenous collateral systems can look overcollateralized during booms because the collateral asset appreciates with system growth. Under stress, collateral value and redemption demand move in opposite directions.

## Surveillance Signals

A market-health system should have flagged several Terra risk signals before and during the collapse:

1. **Stablecoin supply concentration in one yield venue**: A large share of UST parked in Anchor meant demand was not diversified.
2. **Yield-reserve depletion**: A high target APY requiring subsidies indicated that organic yield was insufficient.
3. **Peg deviations**: Even small deviations from $1 can matter when redemption reflexivity is high.
4. **Liquidity-pool imbalance**: UST leaving balanced pools and creating one-sided liquidity conditions was an early run signal.
5. **LUNA market-cap coverage**: The ratio of UST supply to LUNA market value and liquidity should have been monitored continuously.
6. **Reserve transparency and deployment**: Peg-defense reserve movements should be tracked in real time.
7. **Exchange halts and spread widening**: Fragmented prices and halted markets can indicate loss of arbitrage capacity.
8. **Social-risk acceleration**: Stablecoin runs are confidence events; public panic can become self-reinforcing.

## Comparison to Other Stablecoin Stress Events

| Incident | Year | Stablecoin type | Outcome |
|----------|------|-----------------|---------|
| Terra UST | 2022 | Algorithmic / endogenous collateral with partial reserves | Peg collapse and LUNA hyperinflation |
| Iron Finance TITAN | 2021 | Partially collateralized algorithmic stablecoin ecosystem | Death spiral and token collapse |
| Basis Cash | 2020-2021 | Algorithmic seigniorage-share model | Persistent failure to maintain peg |
| USDC Silicon Valley Bank stress | 2023 | Fully reserved fiat-backed stablecoin with bank exposure | Temporary depeg; peg restored after bank-deposit backstop |
| DAI collateral stress | 2020 | Overcollateralized crypto-backed stablecoin | Severe auction/liquidity stress; system survived after governance changes |

The comparison shows that not all depegs are equal. Reserve-backed and overcollateralized systems can still fail or depeg, but their failure modes differ from reflexive algorithmic designs that require a volatile endogenous token to absorb exits.

## Lessons for Market Health

1. **Yield is not the same as product-market fit**. UST demand was heavily supported by Anchor's high yield; when confidence in the yield and peg weakened, demand could disappear quickly.
2. **Stablecoin liabilities need credible exit capacity**. A stablecoin can trade at $1 for months, but the relevant question is whether all holders can exit near par during stress.
3. **Endogenous collateral is fragile**. If the backing asset is created by the same system and falls when redemptions rise, the stabilizing mechanism can become destabilizing.
4. **Partial reserves require clear rules**. Reserves must be large, liquid, transparent, and governed by predictable redemption or defense policies.
5. **Market cap is not liquidity**. LUNA's pre-collapse market capitalization did not mean the market could absorb mass UST redemptions.
6. **Run-risk metrics should be real time**. Peg deviations, Anchor withdrawals, Curve pool imbalance, reserve movements, and LUNA issuance were observable stress indicators.
7. **Disclosures matter**. Users need to understand whether a stablecoin is fully reserved, overcollateralized, algorithmic, subsidized, or dependent on a volatile collateral token.

## References

1. U.S. Securities and Exchange Commission. "SEC Charges Terraform and CEO Do Kwon with Defrauding Investors in Crypto Schemes." February 2023.
2. MIT Sloan Consumer Finance Initiative / NBER. "Anatomy of a Run: The Terra Luna Crash."
3. Luna Foundation Guard. Public reserve and post-event reporting statements, 2022.
4. Terraform Labs / Terra governance forum posts regarding Terra 2.0 and chain restart decisions, May 2022.
5. Anchor Protocol documentation and yield-reserve discussions.
6. Coin Metrics / Chainalysis / market-data reporting on UST peg, LUNA supply expansion, and Terra ecosystem losses.
7. Public exchange notices regarding LUNA/UST trading halts and delistings during May 2022.
