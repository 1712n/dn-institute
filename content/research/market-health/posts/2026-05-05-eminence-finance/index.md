---
date: 2026-05-05
entities:
  - id: eminence-finance
    name: Eminence Finance
    type: defi
  - id: yearn-finance
    name: Yearn Finance
    type: defi
  - id: andre-cronje
    name: Andre Cronje
    type: individual
title: "Eminence Finance flash-loan bonding-curve exploit, $15 M user-deposited fund drain, and test-in-production risk"
---

## 1. Introduction and incident overview

On 29 September 2020, Eminence Finance — an unreleased, unaudited NFT gaming protocol created by Yearn Finance founder Andre Cronje — was exploited via a flash-loan attack that drained approximately $15 million in DAI from its smart contracts. The attacker used a flash loan from Uniswap to manipulate the protocol's bonding curve mechanism, minting EMN tokens at a low point on the curve, burning them for other protocol currencies at an inflated rate, and extracting the resulting DAI profits. After the exploit, the attacker returned $8 million in DAI to Andre Cronje's deployer address, retaining approximately $7 million.

The Eminence incident was distinctive not because of its technical sophistication (the flash-loan bonding-curve exploit was relatively straightforward) but because of the circumstances that created the vulnerability. The protocol's smart contracts were deployed to Ethereum mainnet as part of a "test in production" development approach — they were never intended for public use, had no audit, no official announcement, and no user interface. Despite this, DeFi users discovered the contracts on-chain, identified Andre Cronje's deployer address, speculated that the contracts represented an upcoming Yearn ecosystem product, and deposited $15 million in DAI within hours of discovery. The exploit highlighted the extreme risk of deploying unfinished smart contracts to production blockchains and the speculative behavior patterns that can emerge in DeFi when prominent developers are involved.

## 2. Technical background

### 2.1 Eminence and the Yearn ecosystem

Andre Cronje is the founder of Yearn Finance (YFI), one of the most prominent DeFi protocols focused on yield optimization. Cronje was known for his "test in production" development philosophy — deploying experimental smart contracts to Ethereum mainnet for testing, often before formal audits or public announcements. This approach was controversial within the DeFi community: supporters viewed it as rapid iteration in a permissionless environment, while critics warned that mainnet deployments of unaudited code created unacceptable risks.

Eminence Finance appeared to be a concept project combining DeFi mechanics with NFT gaming elements. The contracts deployed to mainnet included token mechanics inspired by gaming "factions" — users could mint an EMN governance token and then convert it into various "currency" tokens representing different game factions. The contracts had no associated user interface, documentation, or official announcement.

### 2.2 Bonding curves

A bonding curve is a mathematical function that determines the price of a token based on its current supply. As more tokens are minted (supply increases), the price increases along the curve; as tokens are burned (supply decreases), the price decreases. Bonding curves create an automated pricing mechanism where early buyers pay less than later buyers, and the total collateral locked in the curve backing the tokens increases as supply grows.

Eminence used a bonding curve to price EMN tokens against DAI. Users could deposit DAI to mint EMN (increasing the supply and price along the curve), or burn EMN to receive DAI back (decreasing the supply and price). The bonding curve also connected EMN to subsidiary "faction" tokens, allowing EMN to be burned and converted into faction-specific currencies.

### 2.3 Flash loans and bonding-curve manipulation

Flash loans — uncollateralized loans that must be borrowed and repaid within a single transaction — are a powerful tool for DeFi manipulation because they allow an attacker to temporarily control very large amounts of capital (often hundreds of millions) at zero cost. When combined with bonding curves, flash loans enable an attacker to:

1. Borrow a large amount of the backing asset (e.g., DAI).
2. Use the borrowed funds to buy along the bonding curve, increasing the token price.
3. Convert or sell tokens at the inflated price through a mechanism that does not properly account for the sudden price change.
4. Repay the flash loan with the profits.

The vulnerability arises when a bonding curve system has multiple exit paths with inconsistent pricing, allowing tokens bought at one price on the curve to be sold or converted at a different (higher) effective price through an alternative mechanism.

## 3. The vulnerability and exploit

### 3.1 Multi-currency conversion inconsistency

Eminence's smart contracts allowed EMN tokens to be converted into multiple "faction" currencies. The core vulnerability was a pricing inconsistency between the EMN bonding curve and the faction currency conversion mechanism. Specifically:

1. EMN could be minted by depositing DAI on the bonding curve (at a price determined by current supply).
2. EMN could be burned to mint faction currency tokens (at a rate determined by a separate calculation).
3. Faction currency tokens could be burned to recover DAI or other value.

The inconsistency allowed the attacker to mint EMN at one price point on the bonding curve, burn the EMN for faction currencies at a more favorable conversion rate, and then extract more DAI than was originally deposited. This price differential, when amplified by a large flash loan, produced significant profits per iteration.

### 3.2 Attack execution

The attacker executed the exploit through the following steps:

1. **Flash loan**: Borrowed 15 million DAI from Uniswap in a single transaction.
2. **Mint EMN**: Deposited DAI into the bonding curve to mint a large quantity of EMN tokens, pushing the price up along the curve.
3. **Convert to faction tokens**: Burned approximately half the EMN to mint faction currency tokens (such as eAAVE, eLINK, etc.), exploiting the conversion rate inconsistency.
4. **Extract DAI**: Burned the faction tokens and remaining EMN to extract more DAI from the bonding curve than was originally deposited.
5. **Repay flash loan**: Returned the 15 million DAI to Uniswap.
6. **Profit**: Retained the excess DAI extracted through the pricing inconsistency.

The attacker's profit came from the gap between the cost of minting EMN on the tight bonding curve and the value extractable by burning EMN through the faction conversion pathway. The flash loan provided the capital needed to exploit this gap at scale.

### 3.3 Partial fund return

After executing the exploit, the attacker sent approximately $8 million in DAI to the Ethereum address identified as Andre Cronje's deployer account. The remaining approximately $7 million was retained by the attacker. The partial return was unprecedented at the time (September 2020) and foreshadowed the pattern of negotiated partial returns that would become common in later DeFi exploits.

The attacker's motivation for the partial return was never definitively established. Speculation included: an attempt to deflect blame toward Cronje (by making it appear that Cronje might be the exploiter), a "white-hat" framing of the exploit (returning funds to the developer for redistribution to victims), or a negotiating gesture to reduce the perceived severity of the theft.

## 4. Context: the "ape-in" phenomenon

### 4.1 How $15M ended up in unreleased contracts

The $15 million deposited into Eminence's contracts was not invested through any official channel. The sequence of events that led to user deposits was:

1. Andre Cronje deployed several smart contracts to Ethereum mainnet from his known deployer address, without any announcement.
2. On-chain observers noticed the deployments and identified the deployer as Cronje's address.
3. DeFi-native users decompiled the contract bytecode, identified the bonding curve and gaming mechanics, and speculated that this was a new Yearn-adjacent project.
4. Word spread rapidly through DeFi social media (Twitter, Discord, Telegram) that "Andre's new project" was live on mainnet.
5. Speculative users ("degens") rushed to deposit DAI and mint EMN tokens, anticipating that early participation would be rewarded when the project officially launched.
6. Within hours, $15 million in DAI was deposited into the unaudited, unannounced, unfinished contracts.

This "ape-in" behavior — depositing large sums into unverified contracts based on social signals rather than technical due diligence — was characteristic of DeFi culture in mid-2020, during the "DeFi Summer" period of intense yield farming and speculation.

### 4.2 Developer responsibility and "test in prod"

The incident raised significant questions about developer responsibility when deploying experimental code to production blockchains:

- **Cronje's position**: He stated that the contracts were never meant for public use, were still in development, and that users who deposited funds did so at their own risk without any encouragement from him.
- **Community criticism**: Many community members argued that a prominent developer deploying token contracts to mainnet from a known address created an implicit signal that the contracts were safe to interact with, regardless of official announcements.
- **Legal ambiguity**: The incident highlighted the lack of clear legal frameworks for liability when users voluntarily interact with unfinished smart contracts on permissionless blockchains.

## 5. Response and aftermath

### 5.1 Community reaction

The exploit triggered intense debate within the DeFi community. Users who lost funds were divided between those who blamed the attacker, those who blamed Cronje for deploying unfinished contracts, and those who acknowledged personal responsibility for depositing funds into unannounced, unaudited contracts.

Andre Cronje reported receiving death threats following the incident and temporarily withdrew from public DeFi development. The incident contributed to a broader discussion about the sustainability of the "move fast and break things" development culture in DeFi.

### 5.2 Partial compensation

Andre Cronje facilitated partial compensation for affected users using the $8 million returned by the attacker. The returned funds were distributed proportionally to addresses that had deposited into the Eminence contracts. Users received approximately 53% of their lost funds back (8 million / 15 million), with the remaining 47% ($7 million) permanently lost.

### 5.3 EMN token aftermath

The EMN token's value collapsed to effectively zero following the exploit, as the bonding curve's DAI backing was drained. Users who held EMN tokens at the time of the exploit lost their entire position unless they were among the early depositors who were compensated from the returned funds. The Eminence project was never officially launched or continued in any form.

## 6. Market-health implications

### 6.1 Test-in-production as a systemic risk vector

The Eminence incident established "test in production" as a recognized DeFi risk vector. When developers deploy experimental contracts to mainnet — even without announcements — the permissionless nature of blockchain means that anyone can discover and interact with those contracts. If the developer is well-known, the social signaling effect can attract significant capital into unfinished and potentially vulnerable contracts.

This creates a systemic risk because:
- Mainnet contract deployments from known developers are immediately indexed and discoverable.
- DeFi-native users actively monitor deployer addresses for new contract activity.
- Social media amplifies discovery rapidly, creating FOMO-driven deposit rushes.
- Unfinished contracts lack the security measures (audits, bug bounties, gradual TVL caps) that protect production deployments.

For market surveillance, monitoring contract deployments from known developer addresses — particularly when those contracts include token minting or bonding curve mechanisms — can provide early warning of potential test-in-production risk situations.

### 6.2 Flash-loan bonding-curve attacks as a vulnerability class

The Eminence exploit was an early example of flash-loan attacks against bonding curve mechanisms. The general vulnerability pattern applies to any bonding curve system where:

1. Multiple entry/exit paths exist with inconsistent pricing.
2. Large capital can move the price significantly along the curve.
3. The price impact of a large operation is not correctly accounted for across all paths.

Subsequent bonding curve exploits (including attacks on various "fair launch" token mechanisms and liquidity bootstrapping pools) have followed similar patterns. The common defense is ensuring that all paths through the curve system produce consistent pricing and that no combination of operations can extract more value than was deposited.

### 6.3 Social signaling and herd behavior in DeFi

The $15 million deposit rush into Eminence's unannounced contracts demonstrated the power of social signaling in DeFi investment decisions. Users deposited funds not because of any fundamental analysis, documented roadmap, or security assurance, but because:

- A famous developer's address was associated with the contracts.
- Other users were depositing, creating fear of missing out (FOMO).
- The "DeFi Summer" environment had conditioned users to expect extreme returns from early participation.
- Social media amplification created a self-reinforcing cycle of discovery and deposits.

This herd behavior creates concentrated risk: when social signals drive rapid capital concentration into unvetted contracts, the potential loss from any vulnerability is amplified by the compressed timeline and large aggregate deposits. Market surveillance systems that track rapid TVL growth in new, unaudited contracts can flag these situations before they reach critical mass.

### 6.4 The "moral hazard" of partial fund returns

The attacker's decision to return $8 million (53% of stolen funds) created complex incentive dynamics:

- **For the attacker**: Returning partial funds reduced criminal liability risk while retaining significant profits ($7 million). This established a "profitable middle ground" between full theft and full return.
- **For users**: The partial return reduced individual losses but did not eliminate them. Users who deposited into unannounced, unaudited contracts still lost 47% of their funds.
- **For the ecosystem**: The partial return may have reduced the deterrent effect of the exploit, as future attackers could observe that returning a portion of funds appeared to reduce consequences while still being highly profitable.

### 6.5 Permissionless deployment and market-health implications

The Eminence incident highlighted a fundamental tension in permissionless blockchain systems: anyone can deploy any code to mainnet, and anyone can interact with any deployed code. There is no gatekeeper that prevents users from depositing funds into unfinished, unaudited, or intentionally malicious contracts. While this permissionlessness is a core feature of decentralized systems, it creates market-health challenges:

- Users may interact with contracts that are not designed, intended, or safe for holding funds.
- Deployed contract code may contain bugs that would be caught by audits or testing if the protocol were officially launched.
- The responsibility boundary between deployer and user is legally and ethically ambiguous.

For market surveillance, distinguishing between "officially launched" protocols (with documentation, audits, and announced deployments) and "discovered" contracts (deployed without announcement, potentially for testing) can help risk-assessment systems flag elevated-risk interactions.

## 7. Lessons learned and recommendations

### 7.1 For DeFi developers

1. **Never deploy fund-accepting contracts for testing**: Use testnets, local forks, or mainnet forks for testing. If mainnet testing is necessary, deploy contracts that cannot accept external deposits or use deployment addresses that are not publicly associated with the developer.

2. **Implement deposit caps on new deployments**: If deploying new contracts to mainnet, implement hard deposit caps that limit total funds at risk until the protocol has been audited and formally launched. This bounds potential losses even if users discover and interact with the contracts prematurely.

3. **Use anonymous deployer addresses for testing**: If mainnet testing is necessary, use fresh deployer addresses that are not publicly linked to the developer, reducing the social signaling effect.

### 7.2 For DeFi users

1. **Do not deposit into unannounced contracts**: Regardless of the deployer's reputation, contracts that have not been formally announced, documented, and audited should be treated as experimental and potentially dangerous. The association with a famous developer does not constitute a security guarantee.

2. **Evaluate contract audit and documentation status**: Before depositing funds, verify that the protocol has been formally announced, has published documentation, has undergone security audits, and has a functioning user interface. The absence of any of these should be a red flag.

3. **Resist FOMO-driven deposits**: The social pressure to "ape in" early to new protocols is a powerful behavioral driver that short-circuits risk assessment. Implement personal waiting periods (e.g., 48-72 hours) before depositing into any new protocol, regardless of social signals.

### 7.3 For market surveillance

1. **Monitor rapid TVL growth in new contracts**: Contracts that accumulate significant TVL within hours of deployment (particularly without associated documentation or announcements) represent elevated risk. Flag these situations for potential user warnings.

2. **Track known developer addresses**: Monitor contract deployments from addresses associated with prominent DeFi developers. New deployments from known addresses that lack documentation may attract speculative deposits into potentially unsafe contracts.

3. **Assess "social signal" risk**: When a new contract's TVL growth is primarily driven by social media FOMO rather than fundamental analysis or official announcements, the deposited capital is at elevated risk because the usual risk-assessment processes (audits, documentation review, community discussion) have been bypassed.

## 8. Conclusion

The Eminence Finance exploit of September 2020 demonstrated the catastrophic intersection of test-in-production development practices, social-signal-driven speculation, and flash-loan-enabled bonding-curve attacks. An unreleased, unaudited, unannounced protocol accumulated $15 million in user deposits within hours of discovery simply because it was deployed from a famous developer's address, and was immediately exploited for its full value by an attacker who identified a bonding-curve pricing inconsistency exploitable via flash loan.

The incident's market-health significance extends beyond the $15 million (net $7 million) loss. It established that permissionless blockchain environments create emergent risk when social signaling drives capital concentration into unvetted contracts, that flash-loan attacks against bonding curves represent a recurring vulnerability class whenever multiple conversion paths have inconsistent pricing, and that the "test in production" development philosophy creates unintended market-health consequences when prominent developers are involved. For the DeFi ecosystem, Eminence remains a cautionary example of how social dynamics (developer reputation, FOMO, herd behavior) can override individual risk assessment and concentrate capital in maximally vulnerable positions.
