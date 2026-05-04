---
date: 2026-05-05
entities:
  - id: compound-finance
    name: Compound Finance
    type: defi
  - id: golden-boys
    name: Golden Boys
    type: threat-actor
  - id: humpy
    name: Humpy
    type: threat-actor
title: "Compound Finance governance attack, Proposal 289 treasury diversion, and $24 M COMP allocation dispute"
---

## 1. Introduction and incident overview

On 28 July 2024, Compound Finance's decentralized autonomous organization (DAO) passed Proposal 289 by a narrow margin of 682,191 to 633,636 votes, allocating 499,000 COMP tokens (approximately $24 million) from the protocol's treasury to a yield-bearing vault called "goldCOMP" controlled by a group known as the "Golden Boys." The proposal was widely characterized as a governance attack — a situation in which a well-resourced actor or group accumulates sufficient governance tokens to push through proposals that serve their interests over those of the broader protocol community.

The Compound governance attack was not a smart-contract exploit in the traditional sense: no code was hacked, no funds were stolen through unauthorized transactions, and no private keys were compromised. Instead, the attack operated entirely within the protocol's legitimate governance mechanisms. The attacker (a pseudonymous DeFi whale known as "Humpy") accumulated enough COMP voting power to pass a proposal that the broader community opposed, exploiting the low voter participation that characterizes most DAO governance votes. The incident ultimately resolved through negotiation — Proposal 289 was canceled in exchange for a new staking product — but it exposed fundamental vulnerabilities in token-weighted governance systems.

## 2. Technical background

### 2.1 Compound Finance governance system

Compound Finance is a decentralized lending protocol on Ethereum that allows users to supply and borrow crypto assets. The protocol is governed by COMP token holders through an on-chain governance system known as Compound Governor. COMP holders can create proposals, delegate voting power, and vote on proposals that modify protocol parameters, allocate treasury funds, or make other governance decisions.

The Compound governance system operates with the following key parameters:

- **Proposal threshold**: A minimum amount of delegated COMP required to submit a proposal (65,000 COMP at the time of the incident).
- **Voting period**: A fixed period during which COMP holders can cast votes (typically 3 days).
- **Quorum**: A minimum number of votes required for a proposal to be valid (400,000 COMP at the time).
- **Timelock**: A delay between proposal passage and execution (typically 2 days), allowing the community to react to passed proposals.

Token-weighted governance systems like Compound's operate on the principle of one-token-one-vote: each COMP token represents one vote, and the outcome of any proposal is determined solely by the weight of tokens voting for and against it. This creates a direct relationship between token accumulation and governance power.

### 2.2 The "Golden Boys" and Humpy

The "Golden Boys" are a pseudonymous group in the DeFi ecosystem led by a whale known as "Humpy" (also identified by the handle @Titanium_32). Humpy has a documented history of governance manipulation across multiple DeFi protocols:

- **Balancer (2022)**: Humpy engaged in a prolonged governance conflict with Balancer from April to December 2022, accumulating sufficient veBAL voting power to unilaterally control governance decisions. The conflict forced an unprecedented "peace treaty" between Humpy and the Balancer protocol.
- **SushiSwap (2024)**: In March 2024, SushiSwap's "Head Chef" Jared Grey accused Humpy of attempting a governance attack to inflate SUSHI emissions and direct them to pools associated with his GOLD token.

The pattern across these incidents involves accumulating governance tokens (through purchases, yield farming, or borrowed voting power), proposing treasury allocations that benefit the attacker's controlled addresses, and leveraging low voter participation to pass proposals that the broader community opposes.

### 2.3 Governance attacks as a threat category

Governance attacks represent a distinct category of DeFi risk that operates at the intersection of economic incentives and protocol design. Unlike technical exploits that target code vulnerabilities, governance attacks exploit the economic and social dynamics of decentralized governance:

- **Economic**: If the cost of acquiring sufficient governance tokens is less than the value that can be extracted through governance proposals, a rational (if antisocial) actor has an incentive to execute the attack.
- **Social**: Low voter participation means that a relatively modest token position can determine outcomes, as most token holders do not actively participate in governance.
- **Temporal**: Token borrowing (through DeFi lending protocols) or flash delegations can provide temporary voting power sufficient to pass proposals without requiring permanent capital commitment.

## 3. Attack chronology

### 3.1 Early proposals and reconnaissance (April-May 2024)

The governance attack on Compound unfolded over approximately three months, with multiple failed proposals preceding the final successful one:

**April 29 - May 2, 2024**: Suspicious COMP delegations were identified from Bybit hot wallets. While not definitively linked to the Golden Boys, the timing coincided with increased governance activity from addresses associated with the group.

**May 6, 2024**: Humpy submitted Proposal 247, requesting that 5% of Compound's treasury (approximately 92,000 COMP) be invested in the goldCOMP vault — a yield-bearing product controlled by the Golden Boys' multisig wallet. The proposal was publicly discussed on Compound's governance forum.

**May 10, 2024**: Following community pushback and criticism of the proposal's trust structure, Humpy canceled Proposal 247 and promised to create a "Trust Setup" that would address concerns about the Golden Boys' control over deposited funds.

This initial proposal served as reconnaissance: it tested the community's response, identified the level of opposition, and revealed the voting power dynamics that the attacker would need to overcome in subsequent attempts.

### 3.2 Second attempt (July 2024)

**July 19, 2024**: Humpy submitted Proposal 279, incorporating a "Trust Setup" contract intended to provide governance controls over funds deposited in the goldCOMP vault. Despite the added trust mechanism, the community remained skeptical of the proposal's terms, and Proposal 279 also failed to pass.

The rejection of Proposal 279 demonstrated that community opposition remained strong, but the voting margins were narrow enough to suggest that additional voting power accumulation could tip the outcome.

### 3.3 Successful passage of Proposal 289 (July 28, 2024)

**July 28, 2024**: Humpy submitted Proposal 289, dramatically escalating the requested amount from the original 92,000 COMP (in Proposal 247) to 499,000 COMP — approximately $24 million and a significant portion of Compound's treasury. The proposal was structured to transfer the COMP tokens to the goldCOMP vault, a yield-bearing product where:

- COMP tokens would be deposited and wrapped as "goldCOMP."
- Yield would ostensibly be generated for all goldCOMP holders.
- The Golden Boys' multisig retained exclusive control over withdrawal functions, meaning the DAO could not recall the funds at its own discretion.

The proposal passed with 682,191 votes in favor and 633,636 votes against — a margin of only 48,555 votes (approximately 7% of the total votes cast). Only 57 unique addresses participated in the vote.

### 3.4 Critical governance dynamics

Several factors enabled the proposal's passage:

1. **Low voter participation**: With only 57 addresses voting on a proposal affecting $24 million in treasury funds, the practical quorum was far below what the theoretical token distribution would suggest. The vast majority of COMP holders did not vote.

2. **Vote concentration**: Humpy and allied addresses controlled a significant block of voting power. The narrow margin of 48,555 COMP suggests that Humpy's accumulated position was just barely sufficient to overcome opposition.

3. **Delegation from exchanges**: The earlier observation of delegations from Bybit hot wallets suggested that governance power was being assembled from exchange-held tokens, potentially including borrowed tokens.

4. **Proposal fatigue**: After multiple proposal attempts (247, 279, 289), community vigilance may have waned, particularly for addresses that had previously voted against and assumed their opposition was sufficient.

## 4. Community response and resolution

### 4.1 Immediate reaction

The passage of Proposal 289 triggered immediate backlash:

- **Michael Lewellen**, a security advisor for Compound, characterized the event as a "governance attack" on the protocol's treasury.
- **Wintermute Governance** highlighted the critical risk that withdrawal functions were "solely controlled by GoldenBoyzMultisig," meaning the DAO could not recall the allocated funds.
- **COMP token price declined approximately 6.7%** in the hours following the proposal's passage, reflecting market concern about treasury misappropriation.
- Community members submitted **Proposal 290**, which aimed to transfer the Timelock Admin to a community multisig that could cancel pending proposals — a defensive measure against the treasury transfer's execution.

### 4.2 Cross-protocol commentary

The incident prompted commentary from governance leaders across the DeFi ecosystem:

- **Michael Egorov (Curve Finance)** argued that vote-escrow tokenomics (veTokenomics) — which requires 4-year token locking for governance participation — would prevent such attacks by making governance power expensive to acquire temporarily.
- **Marc Zeller (Aave)** highlighted that Aave's active governance and community guardian veto mechanism provide structural defenses against governance attacks.

### 4.3 Negotiated resolution

On July 29-30, 2024, Compound community leaders negotiated directly with Humpy, reaching a compromise:

- Humpy agreed to cancel Proposal 289 (preventing the $24 million transfer).
- In exchange, Compound would implement a new staking product allocating 30% of current and future market reserves to staked COMP holders.
- The staking product would be controlled by the Compound DAO (not the Golden Boys' multisig).
- Proposal 290 (the defensive timelock transfer) was also canceled as part of the resolution.

Humpy publicly framed the outcome as a positive development: "Glad to have brought Compound to the limelight again. COMP finally becoming a yield bearing asset!" This framing — presenting a governance attack as "constructive disruption" — has become a recurring pattern in DeFi governance disputes.

## 5. Market-health implications

### 5.1 Token-weighted governance as an attack surface

The Compound governance attack demonstrated that token-weighted governance systems are fundamentally vulnerable to well-resourced actors who can accumulate sufficient voting power. The attack cost is bounded by the market price of governance tokens multiplied by the quantity needed to achieve a voting majority, while the potential payoff is the value of treasury assets that can be redirected.

For Compound specifically:

- Treasury value at risk: ~$24 million (499,000 COMP).
- Cost to accumulate decisive voting power: Significantly less than $24 million, given that the margin was only 48,555 COMP (worth approximately $2.3 million at the time).
- Return on attack: If successful, the attacker would extract approximately 10x the cost of the additional voting power needed.

This favorable cost-benefit ratio for the attacker represents a systemic vulnerability in any token-weighted governance system where:
1. Treasury value exceeds the cost of acquiring a governance majority.
2. Voter participation is low (reducing the required governance position).
3. Governance tokens can be borrowed or acquired temporarily.

### 5.2 Serial governance attackers

Humpy's documented pattern across Balancer, SushiSwap, and Compound demonstrates that governance attacks are not isolated incidents but can be conducted serially by the same actor against multiple protocols. This pattern is enabled by:

- **Portable methodology**: The same techniques (token accumulation, proposal submission, vote coordination) apply to any token-weighted governance system.
- **Impunity**: Governance attacks operate within the protocol's legitimate rules, making legal consequences uncertain and enforcement difficult.
- **Profitable resolution**: Even when attacks are detected and opposed, the attacker often negotiates favorable settlements (as in the Balancer "peace treaty" and Compound staking product).

For market surveillance, tracking the governance activity of known serial attackers across multiple protocols can provide early warning of coordinated governance campaigns.

### 5.3 Low voter participation as systemic risk

The fact that only 57 addresses voted on a $24 million treasury allocation highlights the fundamental challenge of voter apathy in DAO governance. Typical voter participation in DeFi governance ranges from 1-10% of circulating token supply, meaning that practical governance control requires far less capital than theoretical token-weighted models suggest.

| Protocol | Typical Voter Participation | Governance Treasury |
|---|---|---|
| Compound | ~5-8% of COMP supply | ~$100M+ |
| Uniswap | ~2-5% of UNI supply | ~$3B+ |
| Aave | ~3-7% of AAVE supply | ~$300M+ |

Low participation rates mean that governance attacks require acquiring only a fraction of the circulating token supply — often achievable through a combination of purchases, yield farming, and delegation from passive holders or exchanges.

### 5.4 Exchange-held tokens and delegation risk

The observation of COMP delegations from exchange hot wallets introduces a concerning vector: exchange-held tokens being used (deliberately or inadvertently) to influence governance outcomes. If an exchange delegates governance power for tokens in its custody, or if an attacker borrows tokens from exchanges and delegates them, the governance attack cost decreases significantly:

- The attacker does not need to permanently acquire governance tokens.
- Borrowed tokens can be returned after the vote completes.
- Flash loans or short-term lending can provide voting power at minimal cost.

Several DeFi protocols have experienced or narrowly avoided attacks exploiting borrowed governance power. The Beanstalk governance attack of April 2022 used a flash loan to acquire sufficient governance tokens to pass a malicious proposal in a single transaction. While Compound's governance system has a multi-day voting period that prevents single-transaction flash-loan attacks, multi-day token borrowing remains feasible.

### 5.5 COMP price impact and market signaling

The approximately 6.7% decline in COMP price following Proposal 289's passage demonstrated that governance attacks have direct market-price implications. Token holders who lack the sophistication or engagement to participate in governance votes may nonetheless be affected through:

- **Dilution**: Treasury token allocations to attacker-controlled addresses dilute the value of remaining treasury holdings.
- **Confidence loss**: Successful governance attacks signal that the protocol's treasury and parameters are not secure, reducing confidence in the protocol's long-term value proposition.
- **Precedent effects**: A successful attack encourages future attempts, creating an ongoing risk premium for the protocol's governance token.

For market surveillance, monitoring governance proposals for anomalous characteristics (large treasury allocations to new addresses, narrow passage margins, low voter counts, repeated resubmission after rejection) can provide signals of potential governance attacks before they impact token prices.

### 5.6 Defenses and their trade-offs

The Compound incident prompted discussion of various governance defense mechanisms:

| Defense | Mechanism | Trade-off |
|---|---|---|
| Vote-escrow (veTokenomics) | Lock tokens for 1-4 years to participate in governance | Reduces liquidity, increases committed capital cost for attackers, but also reduces participation from casual holders |
| Time-weighted voting | Weight votes by how long tokens have been held | Disadvantages new legitimate participants alongside attackers |
| Community guardian/veto | Designated security council can veto malicious proposals | Introduces centralization; guardian becomes a trust point |
| High quorum requirements | Require large percentage of supply to vote | Reduces governance throughput; legitimate proposals may fail to reach quorum |
| Proposal cooldown | Limit how quickly rejected proposals can be resubmitted | Slows legitimate governance iteration |
| Dual governance | Require approval from multiple stakeholder classes | Increases complexity; potential for deadlock |

No single defense is universally superior. The Compound incident demonstrated that the current common approach (simple token-weighted voting with low practical participation) is insufficient against motivated attackers with sufficient capital.

## 6. Lessons learned and recommendations

### 6.1 For DeFi protocols with token governance

1. **Implement governance guardian mechanisms**: Designate a security council or multisig with the power to veto proposals that meet specific risk criteria (e.g., treasury allocations exceeding a threshold, proposals that transfer control to new addresses). This introduces a safety layer without fully centralizing governance.

2. **Increase quorum requirements for treasury-sensitive proposals**: Proposals that allocate treasury funds above a threshold should require higher quorum levels than routine parameter changes, ensuring that significant decisions reflect broader community consensus.

3. **Monitor delegation patterns**: Implement monitoring for large delegation events, particularly from exchange addresses or newly active addresses, as these may signal governance attack preparation.

4. **Consider time-weighted or lock-based voting**: Systems that require tokens to be locked for extended periods before they confer voting power increase the cost of temporary governance attacks.

### 6.2 For COMP holders and DAO participants

1. **Delegate actively**: If you hold governance tokens but do not actively monitor proposals, delegate your voting power to a trusted representative who will participate in governance on your behalf.

2. **Monitor proposal velocity**: Multiple rejected proposals being resubmitted with increasing amounts or modified terms is a pattern that warrants scrutiny and active opposition.

3. **Evaluate multisig control structures**: Any proposal that allocates funds to a multisig should be scrutinized for who controls the multisig, what the recall mechanisms are, and whether the DAO retains ultimate control.

### 6.3 For market surveillance

1. **Track governance token accumulation patterns**: Monitor for addresses rapidly accumulating large positions in governance tokens, particularly when the cost of accumulation is small relative to the protocol's treasury.

2. **Flag low-participation high-value votes**: Proposals that pass with low absolute voter counts but large treasury impacts warrant immediate attention as potential governance attacks.

3. **Cross-protocol attacker tracking**: Maintain awareness of known governance attackers (like Humpy) and monitor their activity across multiple protocols. Serial attackers tend to reuse similar tactics and can be identified early.

4. **Monitor governance token borrowing**: Increased borrowing of governance tokens on lending platforms (Aave, Compound itself, etc.) prior to voting deadlines may indicate attack preparation.

## 7. Conclusion

The Compound Finance governance attack of July 2024 demonstrated that DeFi protocol security encompasses not only smart-contract integrity and private-key management but also the robustness of governance systems against well-resourced actors. By accumulating sufficient COMP voting power and exploiting low voter participation, the pseudonymous attacker "Humpy" and his "Golden Boys" group passed a proposal to redirect $24 million in treasury funds to a vault under their control. While the attack was ultimately resolved through negotiation rather than fund loss, it exposed the structural vulnerability of token-weighted governance systems to capital-driven manipulation.

For market health, the incident established several concerning precedents. The attack cost (acquiring marginal voting power) was dramatically lower than the potential payoff (treasury capture), creating favorable economics for governance attacks across the DeFi ecosystem. The serial nature of Humpy's attacks across Balancer, SushiSwap, and Compound demonstrated that governance vulnerabilities are portable and repeatable. And the resolution through negotiation — where the attacker received a favorable settlement (the staking product) in exchange for withdrawing the attack — risks creating incentives for future governance hostage-taking. Until DeFi governance systems evolve beyond simple token-weighted voting to incorporate mechanisms that increase attack costs and reduce the power of concentrated token positions, governance attacks will remain a persistent and potentially escalating threat to protocol treasuries and market stability.
