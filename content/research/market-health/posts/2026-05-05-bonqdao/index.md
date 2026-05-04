---
date: 2026-05-05
entities:
  - id: bonqdao
    name: BonqDAO
    type: defi-protocol
  - id: allianceblock
    name: AllianceBlock
    type: defi-protocol
  - id: polygon
    name: Polygon
    type: blockchain
title: "BonqDAO oracle manipulation exploit: Tellor price feed abuse and $120M ALBT/BEUR collateral drain on Polygon"
---

## Introduction

BonqDAO was a decentralized borrowing protocol on Polygon that allowed users to mint BEUR (a Euro-pegged stablecoin) by depositing collateral into individual debt positions called "troves" (adapted from Liquity Protocol's trove-based lending model). The protocol supported multiple collateral types, including ALBT (AllianceBlock's governance token) and wMATIC. Unlike many lending protocols that relied on Chainlink or other established oracle networks for price feeds, BonqDAO used Tellor Protocol — a decentralized oracle network where reporters stake TRB tokens to submit price data and can be disputed if they report incorrect values.

On February 1, 2023, an attacker exploited BonqDAO's integration with the Tellor oracle to manipulate the reported price of ALBT collateral, first inflating it to borrow massive amounts of BEUR, then deflating it to trigger liquidations of other users' ALBT troves at a fraction of their true value. The combined extraction was nominally valued at approximately $120 million based on the pre-exploit ALBT price, though the actual realizable value was significantly lower due to limited liquidity for ALBT. The attacker ultimately realized approximately $1-2 million in liquid assets after selling the extracted tokens.

## Background

### Liquity-Style Trove Model

BonqDAO's lending mechanism was adapted from Liquity Protocol, an Ethereum-based borrowing platform. In this model, each borrower creates a "trove" — an individual debt position with specific collateral deposited and a specific amount of stablecoin (BEUR) minted against it. The protocol enforces a minimum collateral ratio (MCR): if a trove's collateral value falls below the MCR due to price movements, the trove becomes eligible for liquidation.

Liquidations in the Liquity model work differently from Compound-style protocols: instead of partial liquidation with incentives, the entire trove's collateral is redistributed to other trove holders (in proportion to their collateral) or absorbed by a stability pool. This mechanism ensures the protocol remains solvent as long as the oracle accurately reports collateral prices.

### Tellor Oracle Integration

Tellor Protocol is a decentralized oracle where reporters submit data to on-chain contracts by staking TRB tokens as collateral. If a reporter submits inaccurate data, other participants can dispute the submission within a dispute window. If the dispute succeeds, the reporter's stake is slashed; if the dispute fails, the disputer's stake is slashed. This game-theoretic design incentivizes honest reporting — but the security guarantees depend on the staking cost being sufficient to deter manipulation.

BonqDAO integrated Tellor for ALBT price feeds on Polygon. The critical parameter was the stake required to submit a price report: at the time of the exploit, the staking requirement was approximately 10 TRB tokens (worth roughly $175 at the time). This meant that anyone willing to stake $175 could submit a price report for ALBT — a cost far below the value that could be extracted through price manipulation if the reported price was used by a protocol holding significant ALBT collateral.

### The Economic Mismatch

The fundamental vulnerability was an economic mismatch: the cost of submitting a manipulated price report ($175 in TRB stake) was vastly lower than the value at risk in BonqDAO's ALBT-collateralized troves (tens of millions in nominal ALBT value). Tellor's security model assumes that the cost of manipulation (staked TRB plus potential loss from dispute) exceeds the benefit an attacker could gain. But this assumption depends on the dispute mechanism being effective and the stake being proportional to the value secured — neither of which held in BonqDAO's case.

## The Attack

### Vulnerability: Low-Cost Oracle Manipulation

The core vulnerability was that BonqDAO's Tellor oracle integration allowed price reports for ALBT to be submitted by any party willing to stake the minimum TRB requirement (~10 TRB, ~$175). The dispute mechanism, while theoretically providing security, had a dispute window that was too long relative to the speed at which BonqDAO processed price updates — the protocol used the most recent price report for its calculations without waiting for the dispute window to expire.

### Attack Execution

The attack was executed in two phases on February 1, 2023:

**Phase 1: Price inflation and excessive borrowing.**

Step 1: The attacker staked 10 TRB tokens on the Tellor oracle network on Polygon, establishing themselves as an authorized price reporter for ALBT.

Step 2: The attacker submitted a price report for ALBT that dramatically inflated its value — reporting a price orders of magnitude higher than the actual market price.

Step 3: BonqDAO's smart contracts read the inflated ALBT price from the Tellor oracle and used it to evaluate the attacker's trove. With ALBT appearing to be worth far more than its actual value, the attacker's deposited ALBT collateral was grossly overvalued.

Step 4: The attacker minted a massive amount of BEUR against their now-overvalued collateral, borrowing far more BEUR than the true collateral value would support.

Step 5: The attacker sold the minted BEUR for other assets (USDC, MATIC, wETH) on Polygon DEXes, extracting real liquid value from the market.

**Phase 2: Price deflation and mass liquidation.**

Step 6: The attacker submitted a second Tellor price report for ALBT, this time reporting a price near zero.

Step 7: BonqDAO read the near-zero price and evaluated all existing ALBT troves against it. Every ALBT-collateralized trove in the system now appeared to be deeply undercollateralized.

Step 8: The attacker (and/or the protocol's stability pool mechanism) liquidated the undercollateralized troves, receiving their ALBT collateral at the deflated (near-zero) price. The attacker acquired large amounts of ALBT for essentially nothing.

Step 9: The attacker sold some of the acquired ALBT on DEXes, though the thin liquidity for ALBT on Polygon limited the realizable value.

### Realized vs. Nominal Value

While the nominal value of extracted ALBT was approximately $120 million at pre-exploit prices, the actual realizable value was dramatically lower. ALBT had limited liquidity on Polygon DEXes, and the exploit itself (combined with the subsequent selling pressure) crashed the ALBT price by over 90%. The attacker ultimately realized an estimated $1-2 million in liquid assets — a fraction of the headline number but still enormously profitable relative to the $175 oracle manipulation cost.

## Impact

### Financial Losses

The direct impact on BonqDAO was the complete collapse of the BEUR stablecoin (which lost its peg and became worthless as the protocol's collateral base was destroyed) and the liquidation of all ALBT troves in the system. BEUR holders who had not sold before the exploit lost their entire holdings. ALBT depositors lost their collateral through the manipulated liquidations.

The AllianceBlock project suffered severe reputational and market cap damage. The ALBT token price crashed by approximately 90% following the exploit, as the market priced in both the direct losses and the revelation that ALBT's primary DeFi use case (as collateral in BonqDAO) was fundamentally insecure.

### Tellor Oracle Trust Model Impact

The exploit raised significant questions about the Tellor oracle's security model for securing DeFi collateral. The core issue was that Tellor's per-submission stake ($175) was calibrated for general-purpose oracle reporting where the value of individual data points is moderate, not for securing billions in collateral where a single manipulated price report could drain the entire system.

Tellor responded by noting that their documentation explicitly warned integrators to implement adequate dispute buffers (waiting for the dispute window to expire before using reported data) and stake requirements proportional to the value secured. BonqDAO had not implemented either of these recommended safeguards.

### Broader Oracle Selection Implications

The BonqDAO exploit became a canonical case study in oracle selection for DeFi protocols. It demonstrated that the security of a decentralized oracle is not binary (decentralized = secure) but depends on specific economic parameters: the cost of submitting false data, the speed at which false data can be detected and disputed, and the relationship between these parameters and the value at risk in protocols consuming the data.

## Response and Remediation

### BonqDAO Response

BonqDAO published a post-mortem acknowledging the oracle manipulation attack and confirmed that the protocol had not implemented Tellor's recommended dispute buffer or proportional staking requirements. The protocol paused all operations and did not resume — the loss of all collateral and the collapse of BEUR made recovery infeasible without external capital injection.

### Tellor Protocol Response

The Tellor team published detailed guidance on secure oracle integration, emphasizing that protocols must implement dispute-window buffers (never using a price report that hasn't survived the full dispute window without challenges), proportional stake requirements (requiring reporters to stake an amount proportional to the value their reports secure), and multi-reporter consensus (requiring multiple independent reports before accepting a price update).

Tellor also began developing "TellorFlex" and updated oracle implementations with built-in dispute buffers that protocols could not bypass.

### AllianceBlock Response

AllianceBlock distanced itself from BonqDAO and confirmed that the ALBT token contract was not compromised. The team noted that the vulnerability was entirely in BonqDAO's oracle integration, not in the ALBT token itself. AllianceBlock offered no compensation to BonqDAO users, directing them to BonqDAO's team for recourse.

## Technical Analysis

### Oracle Security as Economic Game Theory

The BonqDAO exploit perfectly illustrates the game-theoretic nature of oracle security. The Tellor oracle's security rests on the assumption that: `cost_of_manipulation > benefit_of_manipulation`. The cost of manipulation is the TRB stake that would be slashed if the report is successfully disputed. The benefit of manipulation depends on the value at risk in protocols consuming the oracle's data.

In BonqDAO's case, the equation was catastrophically imbalanced: $175 (stake) << $120M (value at risk). Even accounting for the limited realizable value ($1-2M), the ratio was approximately 6,000:1 — making manipulation overwhelmingly profitable even if the attacker expected their stake to be slashed.

The fix requires rebalancing this equation: either increasing the cost of manipulation (higher staking requirements, longer dispute windows that delay usability) or decreasing the benefit (limiting the protocol's exposure to any single oracle report through rate limiting, diversified oracle sources, or price deviation bounds).

### Dispute Window Timing Vulnerability

BonqDAO's critical error was using Tellor price reports immediately upon submission, without waiting for the dispute window to expire. The dispute window exists precisely to allow honest participants to challenge false reports — but if the consuming protocol uses the report before the window expires, the dispute mechanism provides no protection.

The correct integration pattern is to impose a delay between report submission and report consumption, at minimum equal to the full dispute window. This means the protocol accepts staler prices (the most recent undisputed report from at least one dispute window ago) but gains the security guarantee that any report it uses has survived community scrutiny.

### Comparison with Other Oracle Manipulation Exploits

The BonqDAO exploit is similar in economic structure to the Mango Markets exploit (October 2022, approximately $100 million on Solana), where the attacker manipulated the reported price of MNGO token by trading in thin markets to inflate their collateral value on the platform, then borrowed against the inflated collateral. The key difference is the manipulation mechanism: Mango's attacker moved the actual market price through thin-market trading, while BonqDAO's attacker submitted false data to the oracle directly.

The Fortress Protocol exploit (May 2022, $3M) used governance to install a manipulable oracle — achieving the same end result (false price → inflated collateral → excessive borrowing) through a different access mechanism. BonqDAO's was more direct: no governance manipulation was needed because the oracle's own submission mechanism was insufficiently secured.

## Lessons Learned

### Oracle Cost Must Exceed Secured Value

The most fundamental lesson is that the cost of submitting false oracle data must significantly exceed the maximum value that can be extracted from protocols consuming that data. This requires oracle integrators to explicitly calculate the "maximum extractable value" from their protocol and ensure the oracle's manipulation cost exceeds it by a comfortable margin.

### Never Use Un-Disputed Oracle Reports

Price reports from decentralized oracle networks with dispute mechanisms must not be consumed until the dispute window has fully expired without challenges. Using a report before it has been "proven" (survived the dispute period) negates the oracle's primary security mechanism.

### Price Deviation Bounds

Protocols should implement price deviation checks that reject oracle reports deviating more than a threshold (e.g., 20%) from the last accepted price within a short time window. This bounds the maximum manipulation per report, even if the oracle's submission mechanism is compromised.

### Diversified Oracle Sources

Critical price feeds should aggregate data from multiple independent oracle sources. A single oracle source — regardless of how decentralized its internal mechanism — represents a single point of failure. Using Chainlink, Tellor, and a Uniswap TWAP together (requiring agreement within a tolerance) provides defense in depth against manipulation of any single source.

## Conclusion

The BonqDAO oracle manipulation exploit of February 1, 2023, extracted nominally $120 million (realistically $1-2 million in liquid value) from a Polygon lending protocol by submitting false ALBT price reports to the Tellor oracle for a cost of approximately $175 in staked TRB tokens. The attack proceeded in two phases: first inflating ALBT's reported price to borrow excessive BEUR, then deflating it to liquidate other users' troves at near-zero cost. The vulnerability was a catastrophic economic mismatch between the cost of oracle manipulation ($175) and the value at risk ($120M nominal), combined with BonqDAO's failure to implement Tellor's recommended security safeguards (dispute window buffers and proportional staking). The incident demonstrated that decentralized oracle security is fundamentally an economic game — the oracle is only as secure as the relationship between the cost of false reporting and the value of the data it provides — and that DeFi protocols bear responsibility for ensuring their oracle integration parameters match the economic value their systems secure.
