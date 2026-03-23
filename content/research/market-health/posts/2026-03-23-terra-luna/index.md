---
title: "Terra/Luna: The Algorithmic Stablecoin Collapse and Do Kwon's Fraud"
date: 2026-03-23
entities:
  - Terraform Labs
  - Do Kwon
  - UST
  - LUNA
---

## Summary

1. **$40 Billion Market Cap Destruction:** In May 2022, the algorithmic stablecoin UST lost its dollar peg, triggering a death spiral that wiped out approximately $40 billion in combined UST and LUNA market capitalization within a week — one of the largest single-event losses in crypto history.
2. **SEC Enforcement and $4.5 Billion Settlement:** The SEC charged Terraform Labs and Do Kwon with securities fraud. In June 2024, a federal jury found Terraform Labs liable, resulting in a $4.5 billion settlement — the largest SEC crypto enforcement outcome.
3. **Criminal Prosecution:** Do Kwon was arrested in Montenegro in March 2023 while traveling on a forged passport. He was extradited to the United States in December 2024 to face federal fraud charges.
4. **Manipulation of UST Peg:** The SEC alleged that Do Kwon secretly arranged for Jump Trading to purchase large quantities of UST during a prior de-peg event in May 2021, restoring the peg artificially and concealing a fundamental design flaw in the algorithmic stabilization mechanism.
5. **Systemic Contagion:** The Terra/Luna collapse triggered a cascading liquidity crisis that contributed to the bankruptcies of Three Arrows Capital, Celsius Network, Voyager Digital, and other firms, amplifying losses far beyond the Terra ecosystem.

## Background

Terraform Labs, founded in 2018 by Do Kwon and Daniel Shin in South Korea, created the Terra blockchain ecosystem centered on UST, an algorithmic stablecoin designed to maintain a 1:1 peg with the US dollar through a mint-and-burn mechanism with its sister token LUNA. Unlike collateralized stablecoins (USDT, USDC), UST had no reserve backing — its stability depended entirely on arbitrage incentives between UST and LUNA.

The Anchor Protocol, a DeFi lending platform built on Terra, offered approximately 20% APY on UST deposits, attracting over $17 billion in deposits and driving massive demand for UST. This yield was largely subsidized by Terraform Labs rather than generated organically.

## Metrics used

### The algorithmic stabilization mechanism

UST's peg mechanism worked as follows:

- To mint 1 UST, a user burned $1 worth of LUNA
- To redeem 1 UST, a user burned 1 UST and received $1 worth of LUNA
- Arbitrageurs were incentivized to restore the peg: if UST traded below $1, they could buy cheap UST and redeem it for $1 of LUNA at a profit

The fundamental vulnerability: this mechanism only worked when there was sufficient liquidity and market confidence in LUNA. A large enough sell-off of UST could overwhelm the redemption mechanism, causing LUNA to hyperinflate as more LUNA was minted to absorb UST redemptions.

### The May 2022 death spiral

The collapse unfolded over approximately one week:

- **May 7:** Large UST sell orders (reportedly $285 million) on Curve Finance depleted liquidity pools, pushing UST to $0.985.
- **May 8-9:** UST fell to $0.90. The Luna Foundation Guard (LFG) deployed $1.5 billion in Bitcoin reserves to defend the peg, but selling pressure overwhelmed the defense.
- **May 10:** UST dropped to $0.60. LUNA began its hyperinflationary spiral as the mint/burn mechanism generated billions of new LUNA tokens.
- **May 11-12:** UST fell below $0.20. LUNA's supply exploded from 340 million to over 6.5 trillion tokens. LUNA's price collapsed from $80 to effectively zero.
- **May 13:** The Terra blockchain was halted twice. Major exchanges delisted UST and LUNA.

### Concealment of prior de-peg event

The SEC's complaint alleged that during a prior UST de-peg in **May 2021**, Do Kwon secretly arranged for Jump Trading (operating through a subsidiary) to purchase over $20 million in UST to restore the peg. Kwon then publicly claimed the algorithmic mechanism had functioned as designed, when in reality a well-capitalized third party had manually intervened. This concealment attracted more investors who believed the stabilization mechanism was self-sustaining.

## Regulatory actions and legal outcomes

### SEC civil action — February 16, 2023

The SEC filed a complaint charging Terraform Labs and Do Kwon with securities fraud (*SEC v. Terraform Labs Pte Ltd. and Do Hyeong Kwon*, Case No. 1:23-cv-01346, S.D.N.Y.), alleging:

- UST, LUNA, wLUNA, and MIR constituted unregistered securities
- Kwon made false and misleading statements about UST's stability and the algorithmic mechanism
- Secret arrangement with Jump Trading to restore the peg in May 2021

### Jury verdict and settlement — April/June 2024

In April 2024, a federal jury found Terraform Labs and Do Kwon liable for securities fraud on all counts. In June 2024, the court approved a **$4.5 billion settlement** with Terraform Labs — the largest SEC crypto enforcement outcome. Terraform Labs agreed to wind down operations.

### Criminal arrest and extradition

- **March 23, 2023:** Do Kwon was arrested at Podgorica airport in Montenegro while attempting to travel using a forged Costa Rican passport.
- He was convicted in Montenegro of document forgery and sentenced to four months in prison.
- After competing extradition requests from the United States and South Korea, Montenegro approved extradition to the U.S.
- **December 2024:** Kwon was extradited to the United States to face federal fraud charges in the Southern District of New York.

### South Korean investigation

South Korean prosecutors issued an arrest warrant for Do Kwon in September 2022 and placed him on Interpol's Red Notice list. Co-founder Daniel Shin was also indicted in South Korea on related fraud charges.

## Timeline

| Date | Event |
|--|--|
| 2018 | Terraform Labs founded by Do Kwon and Daniel Shin |
| 2021-05 | First UST de-peg; secretly restored by Jump Trading |
| 2022-05-07 | Large UST sell-off begins on Curve Finance |
| 2022-05-09 | LFG deploys $1.5B Bitcoin reserves to defend peg |
| 2022-05-10 | UST falls to $0.60; LUNA hyperinflation begins |
| 2022-05-13 | Terra blockchain halted; ~$40B in value destroyed |
| 2022-09 | South Korea issues arrest warrant for Do Kwon |
| 2023-02-16 | SEC files civil fraud charges |
| 2023-03-23 | Do Kwon arrested in Montenegro with forged passport |
| 2024-04 | Jury finds Terraform Labs liable for fraud |
| 2024-06 | $4.5B SEC settlement approved |
| 2024-12 | Kwon extradited to the United States |

## References

1. SEC, "[SEC Charges Terraform Labs and Do Kwon with Defrauding Investors](https://www.sec.gov/newsroom/press-releases/2023-32)," February 16, 2023.
2. SEC, "[Terraform Labs and Do Kwon Found Liable for Securities Fraud](https://www.sec.gov/newsroom/press-releases/2024-49)," April 2024.
3. Reuters, "[Terra founder Do Kwon arrested in Montenegro](https://www.reuters.com/technology/terra-founder-do-kwon-arrested-montenegro-2023-03-23/)," March 23, 2023.
4. CoinDesk, "[Terra's UST Stablecoin Plunges, Triggering LUNA Death Spiral](https://www.coindesk.com/markets/2022/05/11/terras-ust-stablecoin-plunges/)," May 11, 2022.
5. Bloomberg, "[Jump Trading Helped Terraform Prop Up UST Stablecoin, SEC Says](https://www.bloomberg.com/news/articles/2023-02-16/jump-trading-helped-terraform-prop-up-ust-stablecoin-sec-says)," February 16, 2023.
6. DOJ, "United States v. Do Hyeong Kwon," S.D.N.Y., 2024.
