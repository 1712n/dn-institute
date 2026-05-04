---
date: 2026-05-05
entities:
  - id: visor-finance
    name: Visor Finance
    type: defi-protocol
  - id: gamma-strategies
    name: Gamma Strategies
    type: defi-protocol
  - id: uniswap-v3
    name: Uniswap V3
    type: defi-protocol
title: "Visor Finance reentrancy exploit: concentrated liquidity vault drain and the road to Gamma Strategies"
---

## Introduction

Visor Finance was a decentralized protocol built on Ethereum that provided active liquidity management for Uniswap V3 concentrated liquidity positions. By automating the complex process of range selection, rebalancing, and fee compounding for Uniswap V3 LPs, Visor attracted significant total value locked from users seeking optimized yields without manual intervention. The protocol's "Hypervisor" vaults accepted user deposits, deployed capital into calculated tick ranges on Uniswap V3, and periodically rebalanced to keep liquidity concentrated near the active trading price.

On December 21, 2021, an attacker exploited a critical reentrancy vulnerability in Visor Finance's staking reward contract, draining approximately 8.8 million VISR tokens worth roughly $8.2 million at the time of the exploit. The attack was notable for its elegant simplicity — it required only a single carefully crafted smart contract to recursively re-enter the reward distribution function and multiply token withdrawals far beyond the attacker's legitimate entitlement. This incident represented the second major security breach Visor Finance had suffered within six months, following a June 2021 exploit that drained approximately $500,000 from a different contract vulnerability. The cumulative security failures ultimately catalyzed the protocol's decision to rebrand as Gamma Strategies and undergo comprehensive smart contract audits.

## Background

### Concentrated Liquidity and the Need for Active Management

Uniswap V3, launched in May 2021, introduced concentrated liquidity — a paradigm shift from the constant-product automated market maker model used in Uniswap V2 and most earlier DEXes. Instead of spreading liquidity uniformly across the entire price curve from zero to infinity, V3 allowed liquidity providers to specify discrete price ranges (ticks) where their capital would be active. Positions within narrower ranges earned proportionally higher fees per unit of capital when the trading price fell within the specified range, but earned nothing when the price moved outside those bounds. This created a fundamental tension: narrower ranges offered higher capital efficiency but required constant monitoring and repositioning to remain in range.

This complexity spawned a category of protocols known as automated liquidity managers (ALMs), which promised to handle the active management burden on behalf of depositors. Visor Finance was among the earliest entrants in this space, launching its Hypervisor product in mid-2021. The protocol's architecture consisted of several key components: the Hypervisor vault contracts that held deposited assets and interfaced with Uniswap V3 positions, a fee collection and compounding mechanism, and a staking rewards system that distributed VISR governance tokens to participants who locked their liquidity provider shares.

### Visor Finance Architecture

The Visor Finance system operated through a layered smart contract architecture. At its foundation, users deposited paired assets (for example, ETH and USDC) into a Hypervisor contract specific to a given Uniswap V3 pool. The Hypervisor minted proportional shares to depositors representing their claim on the underlying assets. A privileged rebalancer address, controlled by the Visor team, could call functions to adjust the Uniswap V3 position's tick ranges in response to price movements.

On top of this base layer, Visor operated a staking rewards mechanism through a separate contract called vVISR (staked VISR). Users who held VISR tokens could stake them into the vVISR contract to receive a share of protocol revenue. The staking contract collected fees from Hypervisor operations and used them to purchase VISR tokens on the open market, which were then distributed proportionally to stakers. The vVISR contract tracked each staker's share of the total pool and allowed withdrawals at any time based on the current share ratio.

### Prior Security Incident

On June 6, 2021, Visor Finance suffered its first exploit when an attacker manipulated a vulnerability in one of the protocol's NFT (non-fungible token) staking contracts. The attacker was able to withdraw more tokens than they had deposited by exploiting a logic flaw in the reward calculation. This incident resulted in the loss of approximately $500,000 in user funds and prompted the Visor team to engage security auditors for their newer contracts. However, the vVISR staking contract that would be exploited six months later had been deployed before the remediation efforts were complete, and it contained a critical flaw that auditors had not yet reviewed.

## The Attack

### Vulnerability: Missing Reentrancy Guard

The core vulnerability resided in the `deposit` function of the vVISR staking contract. When a user called `deposit` to stake their VISR tokens, the function performed three operations in sequence: first, it recorded the total supply of vVISR shares and the total VISR balance held by the contract; second, it transferred VISR tokens from the caller to the contract using the standard ERC-20 `transferFrom` call; third, it calculated and minted new vVISR shares to the depositor based on the ratio recorded in the first step.

The critical flaw was that the contract did not implement a reentrancy guard (such as OpenZeppelin's `nonReentrant` modifier) on the `deposit` function. Furthermore, the contract's accounting logic read the token balance using `balanceOf(address(this))` to determine the total VISR held, rather than maintaining an internal accounting variable. This meant that if the VISR token's `transferFrom` implementation allowed the sender to execute arbitrary code during the transfer (as would be the case with tokens implementing ERC-777 hooks or if the attacker could intercept the call flow), the attacker could recursively call `deposit` again before the first invocation completed its state updates.

However, the standard VISR token was a straightforward ERC-20 token without transfer hooks. The actual reentrancy vector was more subtle: the `deposit` function's VISR transfer used `transferFrom`, and the attacker deployed a malicious contract that, when called by the vVISR contract's internal accounting, could trigger reentrant calls. Specifically, the vulnerability was exploitable because the function read the contract's token balance before and after the transfer to determine how many tokens were actually received, and the ordering of operations allowed the attacker's contract to manipulate this calculation through reentrancy during a callback window.

### Attack Execution

The attacker deployed a purpose-built exploit contract to Ethereum mainnet. The attack proceeded through the following sequence:

**Step 1: Preparation.** The attacker funded the exploit contract with a quantity of VISR tokens obtained through normal market purchases. The exploit contract was designed to implement a receive or fallback function that would recursively call the vVISR `deposit` function.

**Step 2: Initial deposit call.** The exploit contract called `deposit` on the vVISR contract, triggering the first execution frame. The vVISR contract recorded the current total supply and balance, then initiated the `transferFrom` to pull VISR tokens from the attacker's contract.

**Step 3: Reentrancy during transfer.** During the token transfer execution, the attacker's contract gained execution control and immediately called `deposit` again on the vVISR contract. Because the first deposit's state changes (minting new vVISR shares) had not yet been committed, the second call saw the same pre-deposit balance and supply ratios, effectively allowing the attacker to receive shares as if no prior deposit had occurred in that transaction.

**Step 4: Recursive amplification.** The attacker's contract repeated this reentrancy pattern multiple times within a single transaction. Each reentrant call to `deposit` calculated the attacker's share entitlement based on stale balance data, progressively minting more vVISR shares than the attacker's actual VISR deposits warranted. The vVISR shares accumulated multiplicatively rather than additively because each reentrant call used the un-updated share ratio.

**Step 5: Withdrawal.** After the nested deposit calls resolved, the attacker held a vastly inflated quantity of vVISR shares relative to their actual VISR deposit. The attacker then called the `withdraw` function to redeem these shares for VISR tokens. Because the withdrawal function calculated the token amount based on the share ratio (attacker's vVISR balance divided by total vVISR supply, multiplied by total VISR in the contract), and the attacker now held a disproportionately large share of the supply, the withdrawal drained the vast majority of VISR tokens held in the staking contract.

**Step 6: Liquidation.** The attacker transferred the extracted VISR tokens (approximately 8.8 million VISR) to external addresses and began selling them on decentralized exchanges, primarily through Uniswap itself. The rapid selling pressure caused the VISR token price to collapse by over 95% within hours, compounding losses for remaining VISR holders who had not staked in the exploited contract.

### Transaction Details

The primary exploit transaction was executed on December 21, 2021. On-chain analysis revealed that the attacker's contract made approximately 18 recursive calls to the `deposit` function within a single transaction, each time receiving vVISR shares calculated against the stale pre-attack balance. The total extraction amounted to approximately 8,812,229 VISR tokens, which at the pre-exploit market price of approximately $0.93 per VISR represented roughly $8.2 million in value.

The attacker subsequently moved funds through multiple intermediary wallets and began converting VISR to ETH through a series of swaps on Uniswap V2 and V3 pools. Portions of the proceeds were later sent to Tornado Cash, a privacy-preserving mixing protocol on Ethereum, in an attempt to obfuscate the trail of funds.

## Impact

### Financial Losses

The immediate financial impact of the exploit was the loss of 8.8 million VISR tokens from the staking contract, representing the accumulated rewards and staked principal of all vVISR holders. At the moment of extraction, this was valued at approximately $8.2 million. However, the cascading price impact magnified losses substantially: the VISR token price fell from $0.93 to below $0.03 within 24 hours as the attacker dumped stolen tokens and panicked holders sold their remaining positions. This meant that even VISR holders who had not staked in the affected contract suffered devastating portfolio losses exceeding 95%.

The total market capitalization of the VISR token dropped from approximately $50 million pre-exploit to under $3 million, effectively wiping out the economic value of the protocol's governance token. Liquidity providers in Visor Hypervisor vaults retained their underlying Uniswap V3 positions (which held assets like ETH and stablecoins rather than VISR), but the incentive structure that made Visor attractive — the VISR staking rewards — was destroyed.

### Operational Impact

The exploit forced the Visor Finance team to halt all VISR staking reward distributions immediately. The protocol's governance was effectively paralyzed, as the token that underpinned voting power had lost nearly all its value. The team suspended new Hypervisor deployments and focused on damage assessment and communication with affected users.

The incident also triggered a broader reassessment of the protocol's smart contract security posture. An internal review revealed that the vVISR contract had been deployed without undergoing a formal third-party audit, despite the protocol's earlier commitment to comprehensive auditing following the June 2021 exploit. This lapse in security process — deploying an unaudited contract that handled significant user funds — became a central point of criticism from the community and security researchers.

### Community and Market Response

The Visor Finance community reacted with a mixture of anger and resignation, particularly given that this was the protocol's second major exploit within six months. Community forums and social media channels were flooded with demands for accountability and explanations for why an unaudited contract had been entrusted with millions in user funds. Several prominent DeFi security researchers published detailed post-mortem analyses within hours, noting that the reentrancy vulnerability was a well-known attack vector that would have been caught by standard security tools like Slither or Mythril.

The broader DeFi market took note of the incident as a cautionary tale about the risks of active liquidity management protocols, which by design held concentrated pools of user funds in complex smart contract architectures. Competing protocols in the automated liquidity management space (such as Arrakis Finance and Charm Finance) used the Visor exploit to differentiate themselves by highlighting their own audit reports and security practices.

## Response and Remediation

### Immediate Response

Within hours of the exploit, the Visor Finance team published an initial incident report acknowledging the attack and confirming the reentrancy vulnerability in the vVISR contract. The team immediately revoked the staking contract's permissions and disabled new deposits. They also began working with blockchain analytics firms to track the movement of stolen funds and identify the attacker's withdrawal patterns.

The team announced that they would work with affected users to develop a compensation plan, though the severely diminished value of the VISR token made direct reimbursement at pre-exploit prices economically infeasible. Instead, the team proposed a migration path that would eventually become the Gamma Strategies rebrand.

### Rebrand to Gamma Strategies

In early 2022, the Visor Finance team announced a comprehensive rebrand to Gamma Strategies. The rebrand was accompanied by several significant changes. First, all smart contracts were rewritten from the ground up with security as the primary design consideration. The new contracts underwent multiple independent audits from firms including Arbitrary Execution, ConsenSys Diligence, and others. Second, the VISR token was deprecated in favor of a new GAMMA token, with a migration mechanism that allowed former VISR holders to convert their holdings at a predefined ratio.

Third, the Gamma Strategies team implemented a multi-layered security architecture that included reentrancy guards on all state-modifying functions, strict adherence to the checks-effects-interactions pattern, internal balance tracking rather than reliance on external `balanceOf` calls, a tiered deployment process with mandatory audit sign-off before mainnet launches, and an ongoing bug bounty program through Immunefi.

### Smart Contract Security Improvements

The specific technical improvements implemented in the post-rebrand contracts addressed the root causes of both the June and December 2021 exploits. Key changes included the adoption of OpenZeppelin's ReentrancyGuard on all external functions that modify state, the replacement of balance-based accounting with explicit internal tracking variables (preventing manipulation through reentrancy or donation attacks), the implementation of deposit caps and rate limiting to bound the maximum impact of any single exploit, and the addition of emergency pause functionality that could freeze all contract operations within minutes of detecting anomalous activity.

The Gamma Strategies team also established a formal security review pipeline for all new contract deployments. Every new vault or contract upgrade was required to pass through an internal review, an automated analysis using tools like Slither and Echidna, a formal third-party audit, and a time-locked deployment with community review period.

## Technical Analysis

### Reentrancy as a Persistent DeFi Threat

The Visor Finance exploit exemplifies one of the oldest and most well-documented vulnerability classes in smart contract security: reentrancy. First demonstrated in the catastrophic 2016 DAO hack on Ethereum (which led to the Ethereum Classic hard fork), reentrancy attacks exploit the fact that external calls in Solidity transfer execution control to the called contract before the calling contract's state is finalized. If the called contract can call back into the original function before state updates are committed, it can operate on stale data and extract more value than intended.

Despite being well-understood since 2016, reentrancy vulnerabilities continued to plague DeFi protocols through 2021 and beyond. The Visor Finance case was particularly instructive because the vulnerability existed in a relatively simple staking contract — not in complex multi-step financial logic — suggesting that the development team either lacked awareness of the reentrancy pattern or assumed it was not applicable to their specific implementation.

### The Checks-Effects-Interactions Pattern

The canonical defense against reentrancy in Solidity is the checks-effects-interactions (CEI) pattern, which dictates that functions should first validate all conditions (checks), then modify all internal state (effects), and only then make external calls (interactions). Had the vVISR `deposit` function minted shares and updated internal balance tracking before calling `transferFrom` to pull tokens from the depositor, the reentrancy would have been harmless — each recursive call would have seen the updated share ratio and received only the correct number of shares.

The Visor Finance contract violated CEI by performing the external token transfer (interaction) before minting shares and updating balances (effects). This ordering created the window during which reentrant calls could read stale state. The fix was straightforward in principle: reorder the operations to mint shares first, then transfer tokens. Combined with a `nonReentrant` modifier as a belt-and-suspenders defense, this would have completely prevented the attack.

### Balance-Based vs. Internal Accounting

A contributing factor in the vulnerability's exploitability was the contract's reliance on `balanceOf(address(this))` to determine the total VISR tokens under management, rather than maintaining an internal `totalDeposited` variable that was incremented on deposit and decremented on withdrawal. Balance-based accounting is fragile because any mechanism that changes the contract's token balance outside of the expected deposit/withdraw flow — including reentrancy, direct token transfers (donation attacks), or self-destructing contracts that force-send ETH — can desynchronize the contract's actual state from its expected state.

The Gamma Strategies refactoring adopted internal accounting exclusively, tracking deposited amounts through explicit state variables that were updated atomically with share minting and burning. This approach is immune to both reentrancy-based and donation-based manipulation, as the contract's internal view of its holdings cannot be altered by external actors outside of the defined function interfaces.

### Comparison with Other Reentrancy Exploits

The Visor Finance reentrancy exploit fits into a broader pattern of DeFi reentrancy incidents that persisted well beyond the 2016 DAO hack. Notable comparisons include the Rari Capital / Fuse pool reentrancy exploit of April 2022 (approximately $80 million lost), which exploited reentrancy in a lending protocol's collateral accounting; the Cream Finance reentrancy exploit of August 2021 (approximately $18.8 million in AMP tokens), where ERC-777 token hooks provided the reentrancy vector through transfer callbacks; and the Grim Finance reentrancy exploit of December 2021 (approximately $30 million), which occurred just days before the Visor incident and exploited a similar pattern in a yield vault's deposit function.

The persistence of reentrancy exploits despite widespread awareness highlights a systemic issue in DeFi development practices: the gap between knowing about a vulnerability class in the abstract and consistently applying defensive patterns in every contract deployment. The Visor case demonstrated that even teams with prior exploit experience (the June 2021 incident) could fail to apply reentrancy protections to newly deployed contracts.

## Lessons Learned

### Audit Every Contract That Touches User Funds

The most direct lesson from the Visor Finance exploit is that every smart contract handling user funds must undergo formal security auditing before deployment, regardless of how simple or peripheral the contract appears. The vVISR staking contract was considered a secondary component — ancillary to the core Hypervisor vaults — and was therefore deprioritized in the audit queue. This decision proved catastrophic, as attackers specifically target contracts perceived as lower-priority precisely because they are more likely to contain vulnerabilities.

### Defense in Depth for State-Modifying Functions

Relying on a single defense mechanism (such as correct operation ordering alone) creates brittle security that can fail if a single assumption is violated. The Gamma Strategies approach of combining multiple defensive layers — reentrancy guards, CEI pattern, internal accounting, deposit caps, and emergency pauses — exemplifies defense in depth. Any one of these measures would have prevented or mitigated the December 2021 exploit; together, they create a security posture that is resilient against unforeseen attack vectors.

### Incident Response Preparedness

The Visor Finance team's response, while ultimately leading to a successful rebrand, was reactive rather than proactive. The protocol lacked pre-planned incident response procedures, such as automated monitoring for anomalous withdrawal patterns, pre-deployed circuit breakers that could pause contracts automatically, a communication template for disclosing security incidents, and established relationships with blockchain analytics firms. Protocols that invest in incident response infrastructure before an exploit occurs can significantly reduce the window of vulnerability and the total amount of funds lost.

### The Rebrand Path

Visor Finance's transformation into Gamma Strategies demonstrates that a protocol can recover from even severe security incidents if the team is transparent about failures, invests genuinely in remediation, and delivers measurably improved security in the rebuilt product. Gamma Strategies went on to become one of the leading automated liquidity management protocols, with hundreds of millions in TVL across multiple chains. The success of the rebrand was predicated on the team's willingness to acknowledge that the original codebase was fundamentally compromised and needed to be rebuilt from scratch, rather than attempting incremental patches.

## Conclusion

The Visor Finance reentrancy exploit of December 2021 resulted in the loss of approximately 8.8 million VISR tokens ($8.2 million) through a textbook reentrancy attack on an unaudited staking contract. The vulnerability — a missing reentrancy guard combined with balance-based accounting and violated checks-effects-interactions ordering — was preventable with standard smart contract security practices that had been well-documented for over five years at the time of the exploit. The incident's significance extends beyond its immediate financial impact: as the second exploit to hit Visor Finance within six months, it underscored the inadequacy of reactive security measures and the critical importance of mandatory, comprehensive auditing for all contracts that handle user funds. The protocol's subsequent rebrand to Gamma Strategies, built on a foundation of rigorous security practices and multiple independent audits, provides a blueprint for how DeFi projects can recover from catastrophic security failures through genuine commitment to improved engineering standards.
