---
date: 2026-05-05
entities:
  - id: level-finance
    name: Level Finance
    type: defi
  - id: bnb-chain
    name: BNB Chain
    type: blockchain
title: "Level Finance referral-reward exploit and $1.1 M protocol drain on BNB Chain"
---

## 1. Introduction and incident overview

On 1 May 2023, the decentralized perpetual-futures exchange Level Finance, deployed on BNB Chain, was exploited through a logic flaw in its referral-reward contract. The attacker repeatedly called the referral claim function to extract approximately 214,000 LVL tokens from the protocol's referral-reward pool. The LVL tokens were subsequently swapped for approximately 3,345 BNB (worth roughly $1.1 million at the time) through PancakeSwap. The exploit was executed through a smart-contract vulnerability rather than a key compromise or social-engineering attack.

Level Finance was a decentralized leveraged-trading platform that allowed users to trade perpetual contracts on BNB Chain. The protocol used a referral system to incentivize user acquisition: referring users earned LVL token rewards based on the trading activity of their referred accounts. The vulnerability exploited a flaw in how the referral contract tracked claimed rewards, allowing the attacker to claim the same referral rewards multiple times within the same transaction.

## 2. Technical background

### 2.1 Level Finance's perpetual-trading architecture

Level Finance operated as a decentralized perpetual-futures exchange on BNB Chain, similar in concept to GMX (Arbitrum) and GNS (Polygon). Traders could open leveraged long or short positions on cryptocurrency pairs, with the protocol's liquidity pool (LLP) serving as the counterparty. Liquidity providers deposited assets into the LLP and earned a share of trading fees.

The protocol's token economy included:

- **LVL**: The governance and utility token. LVL could be staked for additional rewards and was used in various protocol incentive mechanisms.
- **LLP**: Liquidity provider tokens representing a share of the protocol's trading-liquidity pool.
- **LGO**: Level Governance tokens used for DAO voting.

### 2.2 The referral system

Level Finance's referral system was designed to incentivize user growth. The mechanics were:

1. A user creates a referral code through the referral contract.
2. New users register using the referral code when they begin trading.
3. When referred users trade (open/close positions, pay fees), a portion of the trading fees is allocated to the referral-reward pool as LVL tokens.
4. The referrer can periodically claim their accumulated LVL rewards from the referral contract.

The referral contract maintained an accounting of each referrer's accumulated rewards and claimed rewards, with the claimable amount being the difference between total accumulated and previously claimed.

### 2.3 The LevelReferralControllerV2 contract

The vulnerable contract was `LevelReferralControllerV2`, which managed the referral-reward distribution. The contract's `claim` function was responsible for:

1. Calculating the claimable reward for the caller (accumulated minus already claimed).
2. Transferring the claimable LVL tokens to the caller.
3. Updating the internal accounting to reflect the claim.

The critical vulnerability was in the order and logic of these operations within the claim function.

## 3. Vulnerability analysis

### 3.1 The repeated-claim bug

The `LevelReferralControllerV2` contract's `claim` function contained a logic flaw that allowed a referrer to claim rewards multiple times for the same accumulated balance. The specific issue was related to how the contract tracked claim epochs and reward tiers.

The referral system used an epoch-based reward structure where rewards accumulated per epoch (time period). The `claim` function iterated over unclaimed epochs and calculated rewards for each. However, the function did not properly update the "last claimed epoch" marker in a way that prevented re-entry or re-invocation within the same transaction.

The attacker exploited this by calling the `claim` function multiple times within a single transaction (via a custom exploit contract). Each call to `claim` would recalculate and pay out rewards for the same epochs because the state update that should have marked those epochs as claimed was insufficient to prevent subsequent claims in the same transaction context.

### 3.2 Missing reentrancy or claim-status guard

The vulnerability was not a classic reentrancy bug (where an external call re-enters the same function during execution) but rather a logic error where repeated external calls to the same function produced duplicate payouts. The contract lacked:

1. **A reentrancy guard** (`nonReentrant` modifier) that would have prevented the function from being called while a previous call was still executing.
2. **A per-transaction claim limit** that would have restricted each address to one claim per block or transaction.
3. **Proper epoch-marking logic** that atomically recorded which epochs had been claimed before distributing rewards.

Any one of these protections would have been sufficient to prevent the exploit.

### 3.3 Exploit contract pattern

The attacker deployed a custom smart contract that:

1. Registered as a referrer in the Level Finance referral system.
2. Generated trading activity (possibly through self-referral or accomplice accounts) to accumulate referral rewards.
3. Called the `LevelReferralControllerV2.claim()` function repeatedly in a loop within a single transaction, extracting rewards multiple times for each claimed epoch.

The loop executed enough iterations to drain approximately 214,000 LVL from the referral-reward pool before the pool was exhausted.

## 4. Attack execution and fund movement

### 4.1 On-chain execution

The exploit was executed on 1 May 2023 on BNB Chain. The attacker's contract made multiple calls to the referral `claim` function, each extracting LVL tokens. The total extraction was approximately 214,000 LVL tokens from the referral-reward reserve.

### 4.2 Token swap

Immediately after extraction, the attacker swapped the 214,000 LVL tokens for BNB through PancakeSwap's LVL/BNB liquidity pool. The swap yielded approximately 3,345 BNB, worth roughly $1.1 million at prevailing prices. The large sale depressed the LVL token price on PancakeSwap due to the concentrated sell pressure against the pool's liquidity.

### 4.3 Fund bridging

The attacker subsequently bridged the BNB to other chains and moved the funds through several addresses to complicate tracing. The full disposition of funds was not publicly tracked in detail, and no fund recovery was reported.

## 5. Level Finance's response

### 5.1 Immediate actions

Level Finance detected the exploit shortly after execution and paused the referral contract to prevent further claims. The protocol's core trading and liquidity-pool contracts were not directly affected — the vulnerability was isolated to the referral-reward controller — so trading operations continued.

### 5.2 Post-mortem

Level Finance published a post-mortem confirming the repeated-claim vulnerability in `LevelReferralControllerV2`. The team acknowledged the logic flaw and the absence of reentrancy/claim guards that would have prevented the exploit.

### 5.3 Contract remediation

The referral controller was redesigned with:

1. A reentrancy guard on the claim function.
2. Updated epoch-tracking logic that properly marks claimed epochs before distributing rewards.
3. Per-address claim cooldowns to prevent rapid repeated claims.

The updated contract was audited before redeployment.

### 5.4 Impact assessment

The $1.1 million loss was borne by the referral-reward reserve, not directly by traders or liquidity providers. However, the LVL token price decline from the attacker's large sale affected all LVL holders, and the reputational damage reduced TVL and trading volume on the platform in subsequent weeks.

## 6. Market-health implications

### 6.1 Peripheral contract risk

The Level Finance exploit illustrates a pattern where the vulnerability is not in the protocol's core functionality (trading, settlement, liquidity management) but in a peripheral incentive mechanism (referral rewards). Peripheral contracts often receive less auditing attention and less rigorous design review than core contracts, because they are perceived as lower risk. However, as the Level Finance case demonstrates, peripheral contracts can hold significant token reserves and, when exploited, can cause material financial and reputational damage.

This pattern has been observed in other DeFi incidents:

| Protocol | Date | Vulnerable component | Loss |
|---|---|---|---|
| Level Finance | May 2023 | Referral reward controller | ~$1.1M |
| Beanstalk Farms | Apr 2022 | Governance voting module | ~$182M |
| Ankr | Dec 2022 | Deployer key (admin function) | ~$5M |
| BadgerDAO | Dec 2021 | Frontend injection (non-contract) | ~$120M |

The common lesson is that the security perimeter of a DeFi protocol includes all contracts and systems that hold value or can be used to extract value, not just the core trading or lending logic.

### 6.2 Incentive-mechanism attack surface

Referral systems, reward programs, and governance-token incentive mechanisms introduce attack surfaces that are qualitatively different from trading or lending vulnerabilities:

- **Self-referral**: Attackers can create both referrer and referred accounts, generating the trading activity needed to accumulate referral rewards without relying on genuine users.
- **Reward amplification**: Logic flaws in reward calculation or distribution (as in Level Finance) can amplify payouts beyond intended levels.
- **Gaming**: Even without explicit bugs, incentive mechanisms can be gamed through wash trading, circular referrals, or other economically rational but protocol-unintended behaviors.

For market surveillance, monitoring incentive-mechanism contracts for unusual claim patterns — rapid repeated claims, abnormally large claims relative to trading activity, and claims from contracts rather than EOAs — can provide early indicators of exploitation.

### 6.3 BNB Chain DeFi security landscape

The Level Finance exploit was one of several DeFi security incidents on BNB Chain during 2023, contributing to an environment where BNB Chain protocols faced elevated security scrutiny. Other BNB Chain incidents in the same period included the Ankr aBNBc exploit (December 2022), the BonqDAO oracle manipulation (February 2023), and several smaller protocol exploits.

BNB Chain's comparatively lower gas costs and faster block times (compared to Ethereum mainnet) make it an attractive deployment target for DeFi protocols but also lower the cost of executing repeated-call exploits like the Level Finance attack. On Ethereum mainnet, the gas cost of executing hundreds of claim calls in a single transaction would be substantial; on BNB Chain, the cost is a fraction of the potential profit.

### 6.4 Token-price impact of exploit-driven sales

The attacker's sale of 214,000 LVL tokens through PancakeSwap caused immediate price impact due to the concentrated sell pressure. For LVL holders who were not involved in the exploit, the token-price decline represented a direct financial loss — a form of dilution where the attacker's extracted tokens depressed the value of all outstanding tokens.

This price-impact channel is common in DeFi exploits where the attacker extracts protocol-native tokens rather than stablecoins or ETH. The attacker's need to liquidate the tokens creates a predictable sell event, and the lack of deep liquidity for many DeFi governance tokens amplifies the price impact.

For market surveillance, monitoring for sudden large sells of protocol-native tokens through DEXes — especially when the seller is a contract address rather than a known market maker — can serve as an exploit-detection signal.

## 7. Lessons learned and recommendations

### 7.1 For DeFi protocol developers

1. **Apply reentrancy guards universally**: The `nonReentrant` modifier should be applied to all external functions that modify state and distribute value, including peripheral contracts like referral controllers. The cost of adding a reentrancy guard is minimal, and the protection is broad.

2. **Audit peripheral contracts with the same rigor as core contracts**: Referral systems, reward distributors, governance modules, and other peripheral contracts hold value and should receive comprehensive security review.

3. **Implement claim-rate limiting**: Functions that distribute token rewards should include per-address, per-block, or per-epoch claim limits. A single address should not be able to claim rewards multiple times for the same period in the same transaction.

4. **Update state before distributing value (checks-effects-interactions)**: The claim function should mark epochs as claimed before transferring tokens. This standard pattern (checks-effects-interactions) prevents both reentrancy and repeated-call exploits.

5. **Test for repeated-call scenarios**: In addition to standard unit tests, write test cases that simulate an attacker calling the claim function multiple times in rapid succession. Fuzz testing tools can automate the discovery of such issues.

### 7.2 For users and token holders

1. **Evaluate the full contract set**: When assessing a DeFi protocol's security, consider not just the core trading or lending contracts but also peripheral systems (referrals, rewards, governance) that hold or distribute tokens.

2. **Monitor referral-system activity**: Unusual patterns in referral claims — large claims, frequent claims from the same address, claims from contract addresses — may indicate exploitation.

### 7.3 For market surveillance

1. **Flag rapid repeated function calls**: Monitor for transactions containing multiple calls to the same token-distribution function within a single transaction, especially from contract addresses.

2. **Track large token sales post-claim**: Detect patterns where a large claim of protocol tokens is immediately followed by a large sale on a DEX, which is the typical exploit-to-profit conversion path.

3. **Monitor peripheral contract reserves**: Track the token balances of referral, reward, and incentive contracts. Unexpected rapid depletion of these reserves may indicate exploitation.

## 8. Conclusion

The Level Finance exploit of May 2023 demonstrated that peripheral incentive contracts — in this case, a referral-reward controller — can be a significant source of protocol risk when they contain logic flaws. The attacker exploited a repeated-claim vulnerability in `LevelReferralControllerV2` to extract approximately 214,000 LVL tokens (~$1.1 million in BNB) from the referral-reward reserve. The vulnerability was a straightforward logic error: the claim function did not properly prevent the same rewards from being claimed multiple times in rapid succession.

The incident reinforced the importance of applying standard security patterns — reentrancy guards, checks-effects-interactions ordering, claim-rate limiting, and comprehensive testing — to all value-bearing contracts, not just the core protocol logic. For the broader DeFi ecosystem, the Level Finance case contributes to the evidence that peripheral contracts represent a systematically underprotected attack surface, and that security audits and testing should encompass the full scope of a protocol's deployed contracts.
