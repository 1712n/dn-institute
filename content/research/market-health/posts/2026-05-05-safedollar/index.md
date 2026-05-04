---
date: 2026-05-05
entities:
  - id: safedollar
    name: SafeDollar
    type: defi-protocol
  - id: polygon
    name: Polygon
    type: blockchain
title: "SafeDollar stablecoin exploit on Polygon: reward pool drain and algorithmic peg collapse"
---

## Introduction

SafeDollar was an algorithmic stablecoin protocol operating on Polygon (formerly Matic Network) that aimed to maintain a $1.00 peg for its SDO (SafeDollar) stablecoin through a seigniorage-based monetary expansion and contraction mechanism. Following the design pattern pioneered by Basis Cash and its derivatives, SafeDollar used a three-token system: SDO (the stablecoin), SDS (SafeDollar Shares, representing seigniorage rights), and SDB (SafeDollar Bonds, used for contraction-phase buybacks). Liquidity providers who staked SDO in designated farming pools earned SDS rewards, while the protocol's monetary policy was governed by an automated expansion and contraction cycle based on the time-weighted average price (TWAP) of SDO relative to its $1.00 target.

On June 28, 2021, an attacker exploited a vulnerability in SafeDollar's reward pool contract, draining approximately $248,000 in USDC and USDT from the pool. While the direct financial extraction was relatively modest, the exploit's second-order effect was catastrophic: the attack caused the SDO stablecoin to lose its peg entirely, crashing from $1.00 to $0.00 — a total and permanent loss of value for all SDO holders. The incident represented one of the starkest examples of how a vulnerability in a peripheral contract (the reward pool) can cascade through an algorithmic stablecoin's economic model to destroy the entire system.

## Background

### Algorithmic Stablecoin Design: Basis Cash Model

Algorithmic stablecoins of the Basis Cash lineage operated on a seigniorage model where the protocol expanded the money supply when the stablecoin traded above its peg and contracted it when the stablecoin traded below. During expansion phases (SDO price > $1.00), new SDO tokens were minted and distributed to SDS stakers (the "boardroom"), increasing supply and theoretically pushing the price back toward $1.00. During contraction phases (SDO price < $1.00), users could purchase SDB bonds at a discount, burning SDO tokens to reduce supply. When the peg was eventually restored, bond holders could redeem SDB for SDO at a premium, incentivizing participation in the contraction mechanism.

This model was inherently fragile: it depended on continued confidence in the protocol's ability to restore the peg. If confidence broke — due to a large sell-off, a smart contract exploit, or any event that dramatically moved SDO below its peg — the contraction mechanism could enter a death spiral where falling prices reduced participation in bond purchases, which failed to reduce supply sufficiently, which led to further price declines. The fragility was well-documented by the time SafeDollar launched, as numerous Basis Cash forks on Ethereum and BSC had already experienced peg failures and death spirals.

### SafeDollar's Polygon Deployment

SafeDollar launched on Polygon during a period of rapid growth for the network's DeFi ecosystem. Polygon's low transaction fees (fractions of a cent compared to Ethereum's multi-dollar gas costs) and fast block times made it attractive for yield farming and algorithmic stablecoin experiments, as the low transaction costs allowed users to claim rewards, compound yields, and rebalance positions frequently without incurring prohibitive gas costs.

The protocol's farming pools accepted deposits of various tokens (including USDC, USDT, and SDO-paired liquidity pool tokens) and distributed SDS rewards to stakers. These farming pools were the primary mechanism for bootstrapping liquidity and maintaining user engagement with the protocol — they were functionally the protocol's growth engine and its most critical infrastructure.

### Reward Pool Architecture

SafeDollar's reward pool contract managed the distribution of SDS tokens to liquidity providers who staked their LP tokens or stablecoins. The contract tracked each staker's share of the total pool, calculated pending rewards based on the time since the last claim and the staker's proportional share, and distributed rewards when stakers called the `claim` or `withdraw` functions.

The pool contract also held reserves of the reward token (SDS) and, in some configurations, other tokens that were part of the farming incentive structure. The vulnerability that the attacker exploited was in this reward calculation and distribution mechanism, where an edge case in the staking/unstaking logic allowed the attacker to extract more value than they were entitled to.

## The Attack

### Vulnerability: Reward Calculation Manipulation

The vulnerability in SafeDollar's reward pool was related to the interaction between the staking mechanics and the reward distribution formula. The specific flaw involved the way the contract calculated a staker's reward entitlement when the staker's balance was modified.

The reward pool used a "reward per share" accumulator pattern, a common design in DeFi staking contracts. In this pattern, the contract maintains a global `accRewardPerShare` variable that tracks the cumulative rewards distributed per unit of staked tokens. When rewards are added to the pool, `accRewardPerShare` increases by `newRewards / totalStaked`. Each staker's pending reward is calculated as `(staker.amount * accRewardPerShare) - staker.rewardDebt`, where `rewardDebt` is set at the time of deposit to the staker's initial `amount * accRewardPerShare`, ensuring the staker only earns rewards from the point of their deposit onward.

The vulnerability was in the handling of a specific token type that had transfer fees or a deflationary mechanism. When the attacker deposited tokens into the reward pool, the pool contract recorded the full deposit amount (the amount specified in the transaction), but the actual tokens received by the pool were less than the recorded amount due to the transfer fee. This discrepancy between the recorded stake and the actual tokens held by the contract created a mismatch that the attacker could exploit.

By repeatedly depositing and withdrawing, the attacker could accumulate a recorded stake that exceeded the actual tokens in the pool, and then claim rewards based on the inflated recorded stake. The reward calculation used the recorded stake (not the actual token balance) to determine the staker's share of distributed rewards, allowing the attacker to extract a disproportionately large share of the reward pool.

### Attack Execution

The attack was executed through a series of transactions on June 28, 2021:

**Step 1: Initial positioning.** The attacker acquired a quantity of the fee-on-transfer tokens that were accepted by SafeDollar's reward pool. The attacker also acquired USDC and USDT to provide as liquidity.

**Step 2: Deposit with inflated accounting.** The attacker deposited the fee-on-transfer tokens into the reward pool. The pool contract recorded the full deposit amount (e.g., 1,000 tokens), but due to the transfer fee, only a reduced amount (e.g., 950 tokens) actually arrived in the contract. The attacker's recorded stake was now 1,000, but the pool only held 950 tokens from this deposit.

**Step 3: Repeated deposit/withdraw cycles.** The attacker repeated the deposit-withdraw cycle multiple times. Each cycle further widened the gap between the recorded stakes across all deposits and the actual tokens held by the pool. The attacker accumulated reward entitlements based on the inflated recorded stakes.

**Step 4: Reward extraction.** The attacker claimed rewards from the pool. Because the reward calculation was based on the inflated recorded stake rather than the actual token balance, the attacker received a disproportionately large share of the distributed rewards. The attacker drained the pool's USDC and USDT reserves (approximately $248,000) through this inflated reward claim.

**Step 5: Market impact.** After draining the reward pool, the attacker sold the extracted SDS tokens on Polygon DEXes. The large sell pressure, combined with the news of the exploit, triggered panic selling of both SDS and SDO tokens. The SDO stablecoin's peg broke immediately and irreversibly as confidence in the protocol collapsed.

### SDO Price Collapse

The immediate aftermath of the exploit saw the SDO stablecoin's price fall from approximately $1.00 to effectively $0.00 within hours. The collapse sequence followed a predictable pattern for algorithmic stablecoins under stress. First, the exploit drained the reward pool, eliminating the farming incentive that attracted liquidity providers. Second, without farming rewards, liquidity providers began withdrawing from SDO pools, reducing the stablecoin's market depth. Third, the reduced liquidity amplified price impact for any selling, causing the SDO price to drop below $1.00. Fourth, the sub-peg price triggered the contraction mechanism, but with confidence shattered, few users were willing to purchase SDB bonds. Fifth, the failure of the contraction mechanism confirmed the death spiral, and remaining holders sold SDO at any price, driving the token to zero.

## Impact

### Financial Losses

The direct financial extraction was approximately $248,000 in USDC and USDT from the reward pool. However, the total economic impact was orders of magnitude larger: the complete collapse of the SDO stablecoin from $1.00 to $0.00 destroyed the entire market capitalization of SDO, which was estimated at several million dollars at the time. SDS (SafeDollar Shares) tokens also collapsed to zero, as their value derived from the expectation of future seigniorage revenues that would never materialize.

The total losses including the direct extraction and the cascading token value destruction were estimated at $10-15 million, though the exact figure depends on assumptions about the liquidity available for SDO and SDS holders to exit their positions as the collapse progressed. Most holders were unable to sell at pre-exploit prices, meaning their effective losses were closer to the full value of their holdings.

### Impact on Polygon DeFi

The SafeDollar exploit contributed to a broader narrative of security concerns in Polygon's rapidly growing DeFi ecosystem. In the weeks surrounding the attack, several other Polygon protocols experienced exploits or rug pulls, reinforcing perceptions that the chain's low barrier to deployment (minimal gas costs for contract deployment and testing) attracted both legitimate projects and poorly audited or outright malicious ones.

The incident also highlighted the specific risk of algorithmic stablecoins on low-cost chains: the low gas fees that made these protocols attractive for yield farming also made it cheap for attackers to execute the rapid deposit-withdraw cycles needed for the exploit. On Ethereum mainnet, where each transaction costs several dollars in gas, the same attack would have been less capital-efficient due to the gas overhead of each cycle.

### Algorithmic Stablecoin Systemic Risk

The SafeDollar collapse provided another data point in the growing evidence that seigniorage-based algorithmic stablecoins were inherently fragile systems prone to catastrophic failure. The incident predated the much larger collapse of Terra/UST (May 2022, approximately $40 billion in value destroyed) but demonstrated the same fundamental dynamic: algorithmic stablecoins that depend on confidence and incentive mechanisms to maintain their peg can collapse entirely when a single shock (an exploit, a large sell-off, or a crisis of confidence) disrupts the incentive equilibrium.

The SafeDollar case was particularly illustrative because the triggering shock was relatively small ($248,000 in extracted value) relative to the total destruction it caused. This amplification — a modest exploit cascading into total protocol failure — demonstrated the extreme fragility of seigniorage-based systems where the stability mechanism depends on continued voluntary participation.

## Response and Remediation

### Immediate Response

The SafeDollar team acknowledged the exploit within hours and confirmed that the reward pool had been drained. They advised users to withdraw their remaining assets from all SafeDollar contracts and refrain from purchasing SDO or SDS tokens. The team published a brief post-mortem identifying the fee-on-transfer token accounting mismatch as the root cause and noted that they had paused the affected reward pool contract.

### Protocol Discontinuation

Unlike many exploited protocols that attempted recovery through contract upgrades and rebrands, the SafeDollar team effectively discontinued the protocol following the exploit. The combination of the drained reward pool and the total collapse of the SDO peg meant that there was no viable path to recovery — the protocol's economic model required a functioning stablecoin peg to generate seigniorage revenue, and the peg could not be restored without incentives that required the reward pool to be funded.

The team did not announce a successor protocol or a token migration plan, and the project's social media channels and documentation were eventually abandoned. This outcome was consistent with the general pattern of algorithmic stablecoin projects that experienced fatal peg failures: once the confidence equilibrium broke, it was virtually impossible to rebuild without external capital injection, and the small-scale projects typical of the Basis Cash fork ecosystem lacked the resources or investor backing to attempt such a recovery.

### Community Response

The SafeDollar exploit prompted several DeFi security researchers to publish analyses of the fee-on-transfer token vulnerability pattern, noting that it was a known risk that had been documented in multiple audit reports but continued to appear in unaudited contracts. The Polygon community established informal security advisory channels to warn about similar vulnerabilities in other yield farming protocols, though the decentralized nature of the ecosystem meant that comprehensive coverage was difficult to achieve.

## Technical Analysis

### Fee-on-Transfer Token Accounting Risks

Fee-on-transfer (also called deflationary or tax) tokens are ERC-20 tokens that automatically deduct a percentage of every transfer as a fee, which is typically burned or redistributed to holders. When a user transfers 1,000 fee-on-transfer tokens with a 5% fee, only 950 tokens arrive at the destination, with 50 tokens being burned or redistributed.

DeFi protocols that accept fee-on-transfer tokens must account for this discrepancy by measuring the actual tokens received (comparing the contract's balance before and after the transfer) rather than trusting the amount specified in the transfer call. The standard pattern is:

```
uint256 balanceBefore = token.balanceOf(address(this));
token.transferFrom(msg.sender, address(this), amount);
uint256 actualReceived = token.balanceOf(address(this)) - balanceBefore;
// Use actualReceived, NOT amount, for all accounting
```

SafeDollar's reward pool contract failed to implement this pattern, using the specified `amount` rather than the actual received amount for staking calculations. This is a well-documented vulnerability pattern that has been identified in multiple smart contract audit frameworks (including Slither's `token-with-fee` detector and OpenZeppelin's fee-on-transfer checklist).

### Reward Per Share Accumulator Pattern Risks

The reward-per-share accumulator pattern used by SafeDollar (and hundreds of other yield farming contracts) is generally secure when the staked token and the pool's accounting are in agreement. The pattern breaks down when there is a discrepancy between the staked amount recorded in the contract and the actual tokens held, because the accumulator's share calculation divides rewards by the recorded total stake, and each staker's entitlement is proportional to their recorded individual stake.

When an attacker can inflate their recorded stake without a corresponding increase in actual tokens (through fee-on-transfer accounting errors, or through other mechanisms that create accounting discrepancies), they can claim a larger share of rewards than their actual contribution warrants. If the inflation is large enough, the attacker can drain the entire reward reserve.

The defense is straightforward: always use actual received amounts (measured by pre/post-transfer balance comparison) for all accounting, and validate that the total recorded stakes never exceed the actual token balance held by the contract. Any discrepancy between recorded stakes and actual balance indicates a potential accounting error that should trigger a circuit breaker.

### Algorithmic Stablecoin Fragility Analysis

The SafeDollar collapse illustrates a structural property of seigniorage-based algorithmic stablecoins: they have no floor. Unlike collateralized stablecoins (USDC, DAI, FRAX) where the stablecoin's value is backed by reserves that can be redeemed, algorithmic stablecoins backed only by seigniorage expectations have no guaranteed redemption value. When the expectation of future seigniorage drops to zero (as happens in a death spiral), the stablecoin's fundamental value drops to zero as well.

This means that any event that sufficiently undermines confidence — an exploit, a governance attack, or simply a large sell-off that triggers cascading liquidations — can drive the stablecoin to zero. The SafeDollar case demonstrated this with a triggering event ($248,000 exploit) that was tiny relative to the total destruction (millions in market cap), highlighting the nonlinear amplification inherent in confidence-based monetary systems.

The comparison to traditional bank runs is apt: algorithmic stablecoins, like fractional-reserve banks, maintain stability through the collective belief that the system will remain stable. When that belief is shaken, the self-reinforcing dynamics of withdrawal and price decline can destroy the system regardless of its fundamental design quality.

### Comparison with Similar Incidents

Several other algorithmic stablecoin projects on various chains suffered similar exploits or confidence collapses during the same period. Iron Finance (June 2021, Polygon) experienced a death spiral triggered by large whale sell-offs rather than a smart contract exploit — the IRON stablecoin collapsed from $1.00 to near $0.00 through pure economic dynamics, demonstrating that algorithmic stablecoins were fragile even without code vulnerabilities.

Basis Cash (December 2020 - March 2021, Ethereum) gradually lost its peg and entered a prolonged death spiral as the expansion/contraction mechanism failed to maintain equilibrium, ultimately stabilizing near $0.00. Dynamic Set Dollar (DSD) and Empty Set Dollar (ESD) followed similar trajectories.

The SafeDollar case was distinctive in that the trigger was a smart contract exploit rather than a pure economic collapse, but the end result was identical: total and permanent peg failure. This convergence of outcomes — regardless of whether the trigger is technical (exploit) or economic (sell pressure) — underscores the fundamental fragility of the seigniorage model.

## Lessons Learned

### Always Measure Actual Received Amounts

The most direct technical lesson is that DeFi contracts must never trust the `amount` parameter of a token transfer for accounting purposes when dealing with arbitrary ERC-20 tokens. The only reliable method for determining how many tokens a contract received is to measure the balance before and after the transfer. This applies to all contracts that accept deposits, including staking pools, liquidity pools, vaults, and lending contracts. Failing to account for fee-on-transfer mechanics is a well-known vulnerability pattern with a simple, well-documented fix.

### Peripheral Contract Exploits Can Be Fatal

The SafeDollar exploit drained a reward pool — a peripheral component of the protocol, not the core stablecoin minting or redemption mechanism. Yet this peripheral exploit was sufficient to destroy the entire protocol. The lesson is that in tightly coupled DeFi systems (especially algorithmic stablecoins where every component contributes to the confidence equilibrium), there are no truly peripheral contracts. Every contract that holds value, distributes incentives, or maintains liquidity is a potential single point of failure for the entire system.

### Algorithmic Stablecoin Risk Disclosure

Protocols launching algorithmic stablecoins have a responsibility to clearly disclose the systemic risks inherent in their design — specifically, the risk that the stablecoin can go to zero if confidence is sufficiently disrupted. Users who deposit into farming pools or hold the stablecoin should understand that they are exposed not just to smart contract risk (the specific contracts they interact with) but to the systemic risk of the entire economic model failing. The SafeDollar case, where a $248,000 exploit caused millions in losses, demonstrates that even modest technical failures can trigger total systemic collapse.

### Audit Coverage for Yield Farming Contracts

The SafeDollar reward pool was not subject to a formal security audit before deployment. Given that the vulnerability it contained (fee-on-transfer accounting) was a well-known pattern detectable by automated tools, even a basic automated scan (using Slither or similar) would have flagged the issue before launch. The lesson reinforces a consistent theme across DeFi exploits: the vast majority of exploited vulnerabilities are well-documented patterns that would be caught by standard audit processes, and the decision to deploy without auditing is a false economy that consistently results in losses orders of magnitude larger than the cost of an audit.

## Conclusion

The SafeDollar exploit of June 28, 2021, drained approximately $248,000 from the protocol's reward pool on Polygon through a fee-on-transfer token accounting vulnerability, but its cascading impact destroyed the entire SDO stablecoin, driving it from $1.00 to $0.00 and wiping out millions in total market capitalization. The attack exploited a well-documented vulnerability pattern — the failure to measure actual received token amounts when dealing with fee-on-transfer tokens — in an unaudited staking contract. The disproportionate impact ($248,000 extracted, millions destroyed) demonstrated the extreme fragility of seigniorage-based algorithmic stablecoins, where any sufficiently disruptive shock to the incentive equilibrium can trigger an irreversible death spiral. The incident serves as both a technical lesson about fee-on-transfer token handling and a systemic lesson about the structural risks of algorithmic stablecoin designs, contributing to the growing body of evidence that ultimately culminated in the May 2022 Terra/UST collapse as the defining failure of the algorithmic stablecoin model.
