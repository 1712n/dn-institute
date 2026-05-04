---
date: 2026-05-05
entities:
  - id: deus-finance
    name: Deus Finance
    type: defi
  - id: dei
    name: DEI
    type: stablecoin
  - id: muon
    name: Muon
    type: oracle
  - id: solidly
    name: Solidly
    type: defi
title: "Deus Finance Muon/Solidly oracle manipulation, DEI collateral inflation, and the $13.4 M Fantom lending drain"
---

## 1. Introduction and incident overview

On 28 April 2022, Deus Finance suffered a roughly $13.4 million exploit on Fantom after an attacker manipulated both the off-chain Muon oracle path and the on-chain Solidly USDC/DEI pool used by the lending system. The attacker inflated the apparent value of DEI collateral, deposited a small amount of DEI, borrowed far more DEI than that collateral could justify, and converted the proceeds into approximately 5,446 ETH before moving funds back to Ethereum and onward to Tornado Cash.

This was the second Deus oracle incident in two months. On 15 March 2022, Deus users had been liquidated for roughly $3 million after an earlier oracle manipulation. After that first event, Deus integrated Muon's off-chain volume-weighted-average-price oracle, which was described as protection against exactly this class of attack. The April exploit showed that the new system was still too narrow: Muon watched the same Solidly USDC/DEI market, did not filter the relevant flash-swap behavior properly, and still allowed an attacker to prepare a manipulated price state before the main borrow transaction.

The exploit is important for market-health analysis because it demonstrates a deeper failure than "use an oracle." Deus added an oracle layer after an earlier incident, but the oracle's data sources and filtering were still insufficient. The protocol treated a synthetic price signal from a manipulable market as a lending truth. Once that happened, a small amount of DEI collateral could unlock a much larger protocol liability.

## 2. Background: Deus, DEI, Muon, and Solidly

### 2.1 Deus Finance and DEI

Deus Finance was a DeFi protocol with a native ecosystem around DEUS and DEI. DEI was a stablecoin intended to track the U.S. dollar. Like many algorithmic or partially collateralized stablecoin systems, DEI depended on a combination of market liquidity, protocol mechanisms, and confidence that redemptions and collateral valuation were sound.

In the affected lending design, DEI could be used as collateral or borrowed through protocol contracts. That made DEI's price especially sensitive. If DEI was valued too high, the protocol could lend out more than the real collateral base justified. If DEI lost peg after an exploit, the perceived solvency and stability of the entire system could weaken.

### 2.2 Solidly USDC/DEI pool

Solidly was a Fantom AMM used for liquidity between USDC and DEI. A stablecoin pool such as USDC/DEI might appear safe because both assets are intended to trade near $1. However, AMM pool state is not the same as a robust reference price. Pool balances can be manipulated with large trades, flash swaps, and short-term liquidity effects. If a lending protocol reads that pool as a price source, the pool becomes part of the lending protocol's security boundary.

The Deus incident depended on the Solidly USDC/DEI pool twice:

1. Muon's off-chain VWAP oracle monitored transactions in that pool.
2. The lending contract used the same pool as an on-chain oracle during the main attack.

That meant one market became a common dependency for both the off-chain and on-chain validation layers.

### 2.3 Muon oracle integration

After the March 2022 incident, Deus integrated Muon's off-chain VWAP oracle. The intent was to resist simple on-chain spot manipulation by calculating a volume-weighted average price from observed pool transactions. In principle, an off-chain oracle can improve safety by filtering noise, aggregating over time, and using independent data collection.

In practice, the April exploit showed that Muon was still too dependent on the same Solidly price environment. Rekt quotes Lafayette Tabor explaining that Muon's implementation used Solidly as a price source and that a flash-swap path was not filtered properly. That allowed a short-term VWAP price glitch to become part of the oracle response.

This is a crucial distinction: adding an oracle does not automatically create independent truth. If the oracle watches the same manipulable venue and lacks adversarial filtering, it can simply formalize the manipulated market state.

## 3. Vulnerability: one market controlled both oracle layers

### 3.1 Shared dependency between off-chain and on-chain prices

The most important design failure was shared dependency. Both the off-chain Muon VWAP and the on-chain lending price path depended on the Solidly USDC/DEI pool. The attacker therefore did not have to fool independent systems. They had to manipulate one market in two compatible ways.

Oracle diversity is not about having multiple components. It is about having independent components. If two oracle layers observe the same thin or manipulable source, their agreement is not strong evidence. It may only mean they are both seeing the same attacker's distortion.

### 3.2 Flash-swap data not filtered out

The attacker prepared Muon's price by using a transaction that Rekt describes as able to "fake" a swap of roughly 2 million USDC to 100,000 DEI about four minutes before the main attack. Tabor later attributed this to a Solidly flash-swap behavior that the Muon oracle did not filter correctly.

That mattered because VWAP systems are only as good as the transactions they include. If the oracle treats abnormal flash-swap artifacts as genuine market volume, it can compute a price that looks averaged and legitimate while still reflecting a synthetic manipulation.

### 3.3 On-chain DEI price manipulation during the main transaction

After the Muon setup, the attacker performed the main attack against the lending contract's on-chain oracle source. According to PeckShield's reconstruction quoted by Rekt:

1. The attacker flash-loaned 143,200,000 USDC.
2. The attacker swapped 143,200,000 USDC into 9,547,716 DEI through the Solidly USDC/DEI pool, making DEI extremely expensive.
3. With only 71,436 DEI as collateral, the attacker borrowed 17,246,885 DEI from the DeiLenderSolidex contract due to the manipulated price.
4. The attacker repaid the flash loan and kept roughly $13 million of profit.

This sequence shows how short-term price manipulation turned into long-term bad debt. The flash-loan capital was temporary, but the borrowed protocol assets were real.

### 3.4 Stablecoin reflexivity

The target asset was DEI, a stablecoin. Stablecoins create reflexive risk when their own market price is used inside the credit system that supports them. If the system overvalues DEI, it can issue too much debt or allow unsafe borrowing. If the exploit weakens confidence, DEI can trade under peg, which further damages the system's credibility.

In Deus's case, Rekt reported that DEI traded under peg after the exploit but appeared to stabilize over time. The key market-health point is that oracle manipulation can become a stablecoin-confidence event, not merely a lending-market loss.

## 4. Attack preparation

### 4.1 Funding through Tornado Cash and Multichain

The funds used to finance the manipulation were initially withdrawn from Tornado Cash on Ethereum. The attacker then swapped for about $2 million USDC and bridged funds to Fantom through Multichain. This provided the capital needed for the Muon manipulation setup before the larger flash-loan transaction.

Cross-chain funding made the attack harder to detect from a single-chain perspective. Ethereum-side funding, bridge transfer, Fantom-side oracle preparation, and Fantom-side execution were all parts of one campaign.

### 4.2 Four-minute oracle preparation window

About four minutes before the main attack, the attacker executed the transaction that influenced Muon's VWAP calculation. This timing matters. The oracle manipulation was not necessarily in the same transaction as the final exploit. It was staged. A monitor that only watches the main lending contract transaction would miss the preparatory manipulation that made the later borrow possible.

For market-health monitoring, this means oracle consumers should watch the input markets continuously. The dangerous event may occur minutes before the exploit transaction that drains funds.

## 5. Main attack flow

### 5.1 Flash-loan capital

The attacker borrowed 143.2 million USDC through a flash loan. Flash loans were not the vulnerability by themselves. They were the capital source that made the manipulation large enough. The protocol needed to be safe even if an attacker could temporarily command hundreds of millions of dollars within one transaction.

The existence of flash loans means collateral and oracle designs must be robust against transaction-scale liquidity, not just organic market volume.

### 5.2 DEI price inflation

The attacker swapped the 143.2 million USDC into 9,547,716 DEI through the Solidly USDC/DEI pool. This made DEI appear extremely expensive in the pool used by the lending contract's price path. Because the protocol interpreted that price as meaningful, DEI collateral appeared much more valuable than it really was.

The economic trick was straightforward: spend temporary capital to make a collateral asset look expensive, borrow against the inflated value, then unwind or repay the temporary capital while retaining the borrowed funds.

### 5.3 Borrowing against inflated collateral

With the price manipulated, the attacker posted 71,436 DEI as collateral and borrowed 17,246,885 DEI. Under normal stablecoin assumptions, that ratio should be impossible: collateral worth about $71,436 should not unlock more than $17 million of borrowing. The manipulated price collapsed that sanity check.

The ratio itself should have been a circuit-breaker signal. Any stablecoin collateral valuation that implies hundreds of dollars per DEI should be rejected unless multiple independent sources confirm a real market event. For a dollar-targeted asset, extreme appreciation is not a bullish signal; it is likely an oracle failure.

### 5.4 Profit extraction and exit

After borrowing, the attacker repaid the flash loan and kept roughly $13 million in profit. Rekt reports that the loot, including funds used to finance Muon manipulation, amounted to 5,446 ETH and was moved from Fantom to Ethereum before entering Tornado Cash.

This exit path matters because once funds move through bridge and mixer infrastructure, recovery becomes harder. Protocols need pre-exit detection and pause controls, not only post-hoc tracing.

## 6. Market impact

### 6.1 $13.4 million protocol loss

The immediate reported loss was $13.4 million. Deus stated user funds were safe, no users were liquidated, DEI lending was temporarily halted, and the DEI peg was restored. Even if user balances were protected directly, protocol-level losses still matter because they affect treasury resources, insurance capacity, future yields, and market confidence.

The exploit also followed a $3 million incident only weeks earlier. Repeated incidents compound reputational damage. Market participants may tolerate one unexpected attack; a second similar oracle failure raises questions about whether the root cause was truly addressed.

### 6.2 DEI peg stress

DEI traded under peg after the exploit. Stablecoin peg stress is a market-health signal because it reflects confidence in redemption, backing, and governance response. A lending exploit against DEI collateral can create uncertainty around:

- whether borrowed DEI is fully backed;
- whether the treasury can absorb losses;
- whether future borrowing will be disabled or constrained;
- whether integrations should keep accepting DEI; and
- whether users should exit before recovery plans are finalized.

The market does not wait for a full technical post-mortem before repricing stablecoin risk.

### 6.3 DEUS price reaction

Rekt reported an initial roughly 20% DEUS price drop, followed by a recovery near pre-hack prices. That recovery does not mean the exploit was harmless. Token prices can rebound on expectations of treasury coverage, community support, or broader market appetite. But the protocol's security credibility still weakens when a new oracle layer fails shortly after being introduced.

## 7. Why the new oracle did not solve the old problem

After the March incident, Deus added Muon. The failure was not that Muon existed; it was that the implementation still relied on a narrow data path and insufficient filtering. The April attack fooled both the off-chain VWAP layer and the on-chain pool price.

This highlights three common oracle mistakes:

1. **Confusing off-chain computation with independent data**: If the off-chain system reads the same manipulated source, moving computation off-chain does not fix manipulation.
2. **Treating VWAP as inherently safe**: VWAP can be manipulated if fake, flash, or obscure swaps are included.
3. **Ignoring asset semantics**: DEI was designed to be a stablecoin. Extreme price appreciation should have been capped or rejected by domain-specific logic.

Robust oracle design requires source diversity, filtering, deviation caps, and domain-aware sanity checks.

## 8. Controls that would have reduced the loss

### 8.1 Independent price sources

Muon should not have relied only on Solidly for DEI pricing. A safer design would use multiple sources, including deep pools, redemption mechanisms, centralized or decentralized reference prices where appropriate, and conservative fallback values. If independent sources disagree, the lending system should reduce collateral value or halt borrowing rather than pick the most favorable value.

For a stablecoin, a maximum usable price near the target peg is also reasonable. If DEI trades at $20, $200, or more in one pool, the protocol should not treat that as increased collateral power.

### 8.2 Flash-swap filtering

VWAP oracles must filter abnormal transactions that do not represent genuine market-clearing volume. Flash swaps, self-referential routes, atomic distortions, and same-block reserve artifacts should be excluded or heavily discounted. The oracle should know the difference between durable liquidity and temporary accounting states.

This filtering must be tested adversarially. It is not enough to assume ordinary trades behave well.

### 8.3 Borrow caps and isolation mode

Even if DEI collateral remained enabled, the protocol could cap maximum borrowing against DEI during the rollout of a new oracle. Isolation mode would have limited the blast radius. New oracle integrations should start with conservative caps and expand only after observing production behavior under stress.

The first Deus incident should have triggered stricter limits until the replacement oracle proved itself.

### 8.4 Stablecoin-specific price bounds

For a dollar-pegged stablecoin, upward deviations are not a reason to increase borrow power dramatically. A simple rule could be:

> If DEI price exceeds a modest upper bound, cap collateral value at the peg or pause borrowing.

This would have prevented a manipulated over-peg price from turning 71,436 DEI into collateral for 17,246,885 DEI of borrowing.

### 8.5 Pre-attack oracle-input monitoring

The Muon preparation transaction occurred about four minutes before the main attack. Monitoring could have flagged abnormal Solidly USDC/DEI activity before the lending transaction executed. Protocols that depend on oracle input markets should monitor those markets continuously and pause borrowing when anomalies appear.

Useful alerts include:

- sudden large swaps in oracle source pools;
- flash-swap patterns included in oracle windows;
- VWAP deviation from peg;
- bridge-funded address activity before oracle updates;
- short-window price changes incompatible with stablecoin design; and
- main lending calls shortly after oracle anomalies.

## 9. Broader implications

### 9.1 Oracle upgrades can create false confidence

Adding a new oracle after an exploit can reassure users, but only if the new oracle changes the security model materially. If it still watches the same market and lacks filtering, it may create false confidence. The second Deus incident is a cautionary example: the team believed the new Muon integration was designed to prevent the prior issue, but the attacker found a path through the combined oracle system.

### 9.2 Stablecoin lending requires conservative asymmetry

Stablecoin collateral should be treated asymmetrically. Price drops may indicate depeg risk and should reduce borrowing power. Price spikes above peg should not increase borrowing power without strong independent confirmation, because a stablecoin's purpose is not to appreciate. Over-peg readings are often liquidity artifacts.

Protocols that lend against their own or closely associated stablecoins must be especially conservative because losses can feed back into peg confidence.

### 9.3 Cross-chain attack paths complicate defense

The Deus exploit used Ethereum-side funding, Multichain bridging, Fantom execution, and Ethereum/Tornado exit. This kind of cross-chain path requires defense teams to monitor multiple environments. A protocol operating on Fantom cannot ignore Ethereum funding and bridge flows when the attacker can stage capital elsewhere.

## 10. Market-health indicators

### 10.1 Repeated oracle incidents

Two similar incidents within two months is itself a market-health signal. Analysts should downgrade confidence when a protocol suffers one oracle manipulation and then quickly suffers another after a mitigation. The second event suggests either incomplete root-cause analysis or insufficiently conservative deployment.

### 10.2 Stablecoin price above peg in collateral systems

Stablecoin overpricing in a collateral oracle should trigger alerts. For a dollar-targeted asset, a price far above $1 is not a legitimate reason to expand borrowing capacity. It is a likely manipulation or liquidity anomaly.

### 10.3 Oracle source overlap

If an off-chain oracle and an on-chain oracle both depend on the same pool, their agreement is weak. Market-health tooling should map oracle dependencies and identify shared sources. Systems that appear to have multiple checks may still have one economic point of failure.

### 10.4 Bridge-funded setup transactions

The attacker funded manipulation from Ethereum, bridged to Fantom, prepared the oracle, and executed shortly afterward. Monitoring systems should connect bridge arrivals, large swaps in oracle pools, and lending activity in a single risk score.

## 11. Timeline

- **15 March 2022**: Deus users are liquidated for roughly $3 million in an earlier oracle manipulation incident.
- **19 March 2022**: Deus communicates that Muon oracles are ready and implemented.
- **Before 28 April 2022**: The attacker sources capital from Tornado Cash on Ethereum, swaps into USDC, and bridges funds to Fantom through Multichain.
- **Four minutes before main attack**: A transaction influences Muon's VWAP by creating a false-looking swap of roughly 2 million USDC to 100,000 DEI in the Solidly USDC/DEI pool.
- **28 April 2022, 02:40 UTC**: The attacker flash-loans 143.2 million USDC, manipulates the Solidly USDC/DEI pool, posts 71,436 DEI as collateral, and borrows 17,246,885 DEI from DeiLenderSolidex.
- **After execution**: The attacker repays the flash loan, keeps roughly $13 million profit, bridges funds to Ethereum, and sends proceeds to Tornado Cash.
- **Post-incident**: Deus halts DEI lending, states that no users were liquidated, and works on covering losses through veDEUS funds.

## 12. Lessons for market participants

For users, the Deus exploit shows that a stablecoin's peg promise is not enough. The safety of lending against that stablecoin depends on the oracle path, source diversity, and whether the protocol caps abnormal prices. A stablecoin can be both under peg in the market and overvalued in a vulnerable collateral system.

For builders, the lesson is to avoid shared oracle dependencies, filter flash-swap artifacts, cap stablecoin collateral values near peg, isolate new oracle deployments, and monitor oracle input markets before main protocol calls occur.

For analysts, the incident provides a monitoring template: look for repeated oracle failures, map source overlap between off-chain and on-chain price checks, alert on stablecoin over-peg readings that increase borrowing power, and link bridge-funded setup transactions to oracle-pool anomalies.

The April 2022 Deus Finance exploit was therefore not just another flash-loan attack. It was an oracle-composition failure. A new oracle layer was added after a prior exploit, but because it still depended on the same manipulable market and failed to filter abnormal swaps, the protocol again converted a temporary price fiction into permanent losses.

## References

- Rekt, [Deus DAO - Rekt 2](https://rekt.news/deus-dao-rekt-2/)
- Rekt, [Deus DAO - Rekt](https://rekt.news/deus-dao-rekt/)
- PeckShield, [Deus exploit reconstruction cited by Rekt](https://twitter.com/peckshield/status/1519533378529562624)
- FTMScan, [Muon oracle manipulation transaction](https://ftmscan.com/tx/0x8589e136e6ad927096d07baa16852d16f11456c0446efb8f1ecd467ce0d4cb10)
- FTMScan, [main flash-loan attack transaction](https://ftmscan.com/tx/0x39825ff84b44d9c9983b4cff464d4746d1ae5432977b9a65a92ab47edac9c9b5)
- Etherscan, [attacker address](https://etherscan.io/address/0x701428525cbac59dae7af833f19d9c3aaa2a37cb)
