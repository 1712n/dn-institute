---
date: 2026-05-05
entities:
  - id: monox-finance
    name: MonoX Finance
    type: defi
title: "MonoX Finance single-token pool self-swap exploit, MONO price inflation, and $31 M multi-chain drain"
---

## 1. Introduction and incident overview

On 30 November 2021, MonoX Finance — a decentralized exchange (DEX) protocol offering single-token liquidity pools on Ethereum and Polygon — was exploited for approximately $31 million. The attacker exploited a critical logic flaw in the protocol's swap function that allowed the same token to be used as both the input and output of a swap. By repeatedly swapping the MONO governance token against itself, the attacker artificially inflated the MONO token's internal price within the protocol, then used the massively overvalued MONO to purchase real assets (WETH, MATIC, USDC, and other tokens) from MonoX's liquidity pools across both chains.

The MonoX exploit was notable for its conceptual simplicity. The underlying vulnerability — failing to prevent a swap where `tokenIn` equals `tokenOut` — was a basic input validation error that violated a fundamental invariant of automated market maker (AMM) design. The exploit did not require flash loans, oracle manipulation, or complex multi-step interactions; it simply exploited the fact that the protocol's price-update logic could be tricked into simultaneously recording a decrease in MONO supply (as if MONO were being sold) and an increase in MONO supply (as if MONO were being bought), resulting in a net price increase per swap iteration.

## 2. Technical background

### 2.1 MonoX and single-token liquidity pools

MonoX Finance was a DEX protocol that differentiated itself from traditional AMMs (like Uniswap and SushiSwap) through its single-token liquidity pool design. In a traditional AMM, liquidity providers must deposit a pair of tokens (e.g., ETH/USDC) in balanced proportions to create a trading pair. MonoX's innovation was allowing liquidity providers to deposit only a single token, with the protocol using a virtual counter-asset (vCASH) to price all tokens against a common unit.

In MonoX's design:
- Each token has a single-sided liquidity pool priced against vCASH.
- When a user swaps Token A for Token B, the protocol performs two internal operations: it sells Token A for vCASH (reducing the Token A pool and increasing its vCASH balance), then buys Token B with vCASH (reducing the vCASH balance and delivering Token B to the user).
- The price of each token is determined by its ratio to vCASH in its pool, following a constant-product-like pricing curve.

This architecture means that the price of any token within MonoX is determined solely by the protocol's internal accounting of that token's pool balance relative to vCASH. If the internal accounting can be manipulated, token prices can be artificially inflated or deflated.

### 2.2 The MONO governance token

MONO was MonoX Finance's governance token. Like many DeFi protocol tokens, MONO was tradeable within the protocol's own pools. MonoX maintained a MONO/vCASH liquidity pool that determined the MONO token's internal price. Users could swap MONO for other tokens (and vice versa) through this pool.

The MONO token's presence in MonoX's own pools created a reflexive relationship: the protocol's internal pricing of its own governance token could be manipulated through the same swap mechanisms that the protocol offered for all tokens. This self-referential pricing arrangement made MONO a particularly attractive target for price manipulation.

### 2.3 AMM invariant assumptions

All AMM designs rely on mathematical invariants that must be maintained across all operations. For constant-product AMMs (the most common design, used by Uniswap V2 and its forks), the fundamental invariant is:

```
x * y = k (constant)
```

Where `x` is the reserve of Token A, `y` is the reserve of Token B, and `k` is a constant that only changes when liquidity is added or removed (not during swaps).

A critical implication of this invariant is that any swap must reduce one reserve and increase the other. A swap where the same token is used as both input and output violates this assumption because the protocol's accounting must simultaneously increase and decrease the same reserve — creating an inconsistent state that the invariant was never designed to handle.

## 3. The vulnerability

### 3.1 Missing same-token check in swap function

The core vulnerability in MonoX's swap contract was the absence of a check preventing swaps where `tokenIn` and `tokenOut` are the same address. The swap function accepted two token addresses as parameters and processed the swap without verifying that they were different tokens.

In a properly implemented AMM, when a user swaps Token A for Token B:
1. The protocol receives Token A from the user (increasing Token A reserves).
2. The protocol updates Token A's price downward (more Token A in pool = lower price).
3. The protocol sends Token B to the user (decreasing Token B reserves).
4. The protocol updates Token B's price upward (less Token B in pool = higher price).

When `tokenIn` and `tokenOut` are the same token (MONO in this case), the protocol:
1. Receives MONO from the user (treating it as the input token).
2. Updates MONO's price downward (as if MONO supply increased).
3. Sends MONO to the user (treating it as the output token).
4. Updates MONO's price upward (as if MONO supply decreased).

The critical flaw was in the ordering and implementation of these price updates. Due to how MonoX's accounting handled the double update, the net effect was a price increase for MONO with each self-swap iteration. The price decrease from step 2 was effectively overwritten or offset by the price increase from step 4, because the contract updated the pool state for the "output" token after the "input" token update, and the output update used the already-modified state.

### 3.2 Accumulative price inflation

Because each self-swap produced a net increase in MONO's internal price, the attacker could iterate the self-swap many times to compound the price inflation exponentially. Each iteration used the inflated price from the previous iteration as the starting point, creating a multiplicative effect.

The attacker did not need to deposit significant initial capital because:
- The self-swap returned the MONO tokens to the attacker (minus the swap fee).
- The net effect on the attacker's MONO balance was minimal (only losing swap fees per iteration).
- The net effect on MONO's internal price was a significant increase per iteration.

After sufficient iterations, the MONO token's internal price within MonoX was inflated to astronomical levels relative to its actual market value, despite no change in external market conditions.

### 3.3 Conversion to real assets

Once MONO's internal price was sufficiently inflated, the attacker used the overvalued MONO to purchase real assets from MonoX's pools. Because MonoX's pools contained significant reserves of WETH, MATIC, USDC, and other tokens, the attacker could exchange a small amount of (internally overvalued) MONO for large quantities of these real assets.

The protocol's price oracle (which was entirely internal) "believed" that the MONO being offered was worth millions of dollars, and accordingly released commensurate amounts of real tokens from its pools. The protocol had no external oracle reference to detect that MONO's internal price was wildly divergent from its actual market price.

## 4. Attack execution

### 4.1 Multi-chain exploitation

The attacker exploited MonoX on both Ethereum and Polygon, where the protocol maintained separate deployments with independent liquidity pools. The same vulnerability existed in both deployments.

**Ethereum**: The attacker drained approximately $18.2 million in WETH and other tokens from MonoX's Ethereum deployment.

**Polygon**: The attacker drained approximately $10.5 million in MATIC-denominated tokens and other assets from MonoX's Polygon deployment.

Additional tokens stolen across both chains included USDC, USDT, various governance tokens, and wrapped assets, bringing the total to approximately $31 million.

### 4.2 Attack transactions

The attack was executed through multiple transactions on each chain. The attacker:

1. Obtained a modest initial quantity of MONO tokens (either through purchase or from existing holdings).
2. Executed multiple self-swap transactions (MONO → MONO) to inflate MONO's internal price.
3. Once the internal price was sufficiently inflated, executed swaps of MONO → WETH, MONO → MATIC, MONO → USDC, etc. to drain real assets from the pools.
4. Repeated the process across multiple pools on both chains until the pools were substantially depleted.

### 4.3 Stolen asset composition

The stolen assets included:

| Token | Chain | Approximate Value |
|---|---|---|
| WETH | Ethereum | ~$18.2M |
| MATIC | Polygon | ~$7.1M |
| Various ERC-20 tokens | Both | ~$5.7M |
| **Total** | | **~$31M** |

## 5. Response and aftermath

### 5.1 Detection and announcement

MonoX Finance detected the exploit and announced it via social media on 30 November 2021. The team confirmed that smart contracts on both Ethereum and Polygon had been exploited and that all staking pools had been drained. The protocol was immediately paused to prevent further exploitation.

### 5.2 Post-mortem

MonoX published a post-mortem acknowledging the self-swap vulnerability. The team confirmed that the swap function lacked a check for `tokenIn == tokenOut`, a basic validation that would have prevented the entire exploit. The vulnerability was present in the audited version of the code, raising questions about the audit's thoroughness.

### 5.3 Audit failure

MonoX's smart contracts had been audited prior to deployment. The audit failed to identify the missing same-token check — a relatively straightforward validation error that should be part of any AMM security review checklist. The audit failure highlighted a broader concern about audit quality in the DeFi space: not all audits are equally thorough, and an audit attestation does not guarantee that fundamental logic errors have been detected.

### 5.4 No fund recovery

Unlike some DeFi exploits where attackers returned portions of stolen funds, the MonoX attacker did not return any of the stolen assets. The funds were moved through various addresses and potentially mixed through privacy protocols, making recovery unlikely.

### 5.5 MONO token and protocol impact

Following the exploit, MONO's market price collapsed as the stolen tokens were sold on external markets and confidence in the protocol evaporated. MonoX's TVL (total value locked) dropped to effectively zero as remaining liquidity providers withdrew what little remained. The protocol did not recover its user base or TVL after the exploit.

## 6. Market-health implications

### 6.1 Self-referential token pricing risk

The MonoX exploit highlighted a systemic risk in DeFi protocols that price their own governance tokens within their own pools. When a protocol's internal pricing mechanism can be manipulated to inflate its native token's value, the entire pool system becomes vulnerable because the inflated native token can be exchanged for all other assets in the protocol.

This self-referential pricing risk is particularly acute in single-token liquidity pool designs (like MonoX) where:
- Each token is priced against a virtual counter-asset rather than another real token.
- The protocol's own governance token can be priced through the same mechanism as external tokens.
- No external oracle provides a reality check on the internal price.

The risk is not unique to MonoX. Any AMM that holds its own governance token in liquidity pools faces similar reflexivity risk, though traditional pair-based AMMs (like Uniswap) are somewhat more resistant because price manipulation in one pair does not directly affect other pairs' pricing.

### 6.2 Basic invariant violations as catastrophic bugs

The MonoX vulnerability — failing to check that input and output tokens are different — was arguably the simplest possible logical error in an AMM swap function. The fix was a single conditional check (`require(tokenIn != tokenOut)`). Yet this trivial oversight enabled a $31 million loss.

For market surveillance and risk assessment, this implies that basic invariant assumptions in AMM designs should be explicitly verified:

| Invariant | Check | Consequence of Violation |
|---|---|---|
| tokenIn ≠ tokenOut | Same-token check | Price inflation (MonoX) |
| Reserve product maintained | Post-swap invariant check | Arbitrary token extraction |
| Reserves ≥ 0 | Underflow protection | Pool bankruptcy |
| Swap amount ≤ reserve | Bounds check | Protocol insolvency |
| Fee correctly applied | Fee accounting check | Fee extraction bypass |

The simplicity of the MonoX bug relative to its catastrophic impact demonstrates that DeFi security assessment should prioritize basic invariant verification before complex vulnerability analysis.

### 6.3 Single-token liquidity pool model risks

MonoX's single-token liquidity pool model, while innovative in reducing impermanent loss for liquidity providers, introduced unique security risks compared to traditional pair-based AMMs:

1. **Virtual counter-asset manipulation**: Because vCASH exists only as an accounting unit (not as a real token with independent market value), its relationship to real tokens can be manipulated without affecting external markets. In a pair-based AMM, manipulating one token's price requires trading against a real counter-asset, creating a natural cost.

2. **Cross-pool contagion**: In single-token pool designs, all pools share a common pricing unit (vCASH). Manipulation of any token's vCASH ratio can potentially affect the perceived value of other tokens' pools through the shared accounting.

3. **No external arbitrage correction**: Traditional AMM price deviations from market prices are corrected by arbitrageurs who profit by buying underpriced or selling overpriced tokens. In the MonoX self-swap attack, the price inflation was entirely internal and could not be corrected by external arbitrage because no external market existed for MONO at the internally manipulated price.

### 6.4 Audit limitations and protocol risk

The MonoX audit failure illustrated a persistent challenge in DeFi security: the gap between audit attestation and actual security. The DeFi ecosystem has developed a pattern where protocols obtain audits as a marketing and credibility tool, but the quality and thoroughness of audits varies enormously. Users and liquidity providers often interpret "audited" as "secure," but this equivalence is not reliable.

For market surveillance, audit status should be treated as one input to risk assessment rather than a binary safe/unsafe indicator. Factors that affect audit reliability include:

- **Auditor reputation and specialization**: Well-known firms with DeFi-specific expertise tend to catch more issues.
- **Audit scope**: Some audits cover only a subset of the protocol's contracts.
- **Time and budget**: Rushed audits or audits with limited budgets may miss issues.
- **Post-audit code changes**: Protocols sometimes modify code after audit completion without re-auditing.

### 6.5 Multi-chain deployment amplification

MonoX's exploitation on both Ethereum and Polygon demonstrated how multi-chain deployments amplify exploit impact. The same vulnerability existed on both chains because the same contract code was deployed to both. The attacker could independently exploit each deployment, doubling the potential extraction.

For the growing multi-chain DeFi ecosystem, this means that:

- A single vulnerability in a multi-chain protocol produces losses proportional to the number of chains on which the protocol is deployed.
- Attackers who discover a vulnerability on one chain can immediately check for the same vulnerability on all other chains where the protocol is deployed.
- Multi-chain protocols face multiplicative security risk: the probability of exploitation remains the same, but the potential loss scales linearly with the number of deployments.

### 6.6 Comparison with other price manipulation exploits

The MonoX exploit belongs to a broader category of DeFi attacks that manipulate internal token pricing to drain protocol assets. Comparison with related incidents:

| Incident | Date | Mechanism | Loss |
|---|---|---|---|
| MonoX Finance | Nov 2021 | Self-swap same-token price inflation | ~$31M |
| Harvest Finance | Oct 2020 | Flash-loan curve manipulation of stablecoin pool | ~$34M |
| BonqDAO | Feb 2023 | Tellor oracle price report manipulation | ~$120M |
| Mango Markets | Oct 2022 | Spot price manipulation to inflate collateral | ~$114M |
| Warp Finance | Dec 2020 | LP token oracle manipulation via flash loan | ~$7.7M |

MonoX's self-swap exploit was distinctive in requiring no external capital (flash loans) and no oracle manipulation — the protocol's own internal accounting was sufficient to inflate prices when the basic same-token invariant was not enforced.

## 7. Lessons learned and recommendations

### 7.1 For AMM and DEX protocol developers

1. **Enforce basic swap invariants**: Implement explicit checks for fundamental AMM invariants, including `tokenIn != tokenOut`, as the first validation in any swap function. These checks should be non-removable and prominently documented.

2. **Implement internal price bounds**: Set maximum price change limits per transaction or per block to prevent catastrophic price inflation in a single operation or sequence of operations. If a swap would cause a token's price to change by more than a defined threshold, the transaction should revert.

3. **Consider circuit breakers**: Implement automated trading halts when pool ratios deviate significantly from recent historical norms or from external oracle prices. This provides a backstop against price manipulation even if specific invariant checks are missed.

4. **Test edge cases explicitly**: Include self-swap (tokenIn == tokenOut) and zero-amount swaps in standard test suites. These edge cases are simple to test but frequently overlooked.

### 7.2 For DeFi auditors

1. **Prioritize invariant verification**: Before examining complex interactions or attack paths, verify that basic mathematical and logical invariants are enforced in all core functions. Missing basic checks are often more catastrophic than subtle vulnerabilities.

2. **Test self-referential scenarios**: When a protocol includes its own governance token in its pools, explicitly test scenarios where the governance token's internal price is manipulated and the consequences for other pools.

3. **Multi-chain consistency review**: When auditing protocols deployed on multiple chains, verify that all deployments share the same security properties and that no chain-specific adaptations introduce new vulnerabilities.

### 7.3 For DeFi users and liquidity providers

1. **Assess protocol token reflexivity risk**: Before providing liquidity to a protocol that trades its own governance token within its pools, consider the risk that the governance token's price can be manipulated to drain pools. Protocols with strong separation between governance token pricing and pool operations present lower reflexivity risk.

2. **Evaluate audit quality beyond attestation**: Look for audits from reputable firms with DeFi-specific expertise, consider whether the audit scope covers the contracts you are interacting with, and check whether the deployed code matches the audited version.

### 7.4 For market surveillance

1. **Monitor for self-swap patterns**: Detect transactions where the same token appears as both input and output in swap operations. While most protocols correctly prevent this, new or unaudited protocols may contain the same vulnerability.

2. **Track internal price deviations**: Monitor AMM internal prices for tokens and flag significant deviations from external market prices. A token whose AMM internal price is dramatically higher than its market price may indicate ongoing price manipulation.

3. **Assess multi-chain exposure concentration**: When evaluating protocol risk, weight the potential loss by the number of chain deployments. A protocol deployed on five chains with $5M per chain has $25M in aggregate risk from a single vulnerability.

## 8. Conclusion

The MonoX Finance exploit of November 2021 demonstrated that DeFi protocols can be catastrophically compromised by the absence of basic input validation checks. By exploiting the missing `tokenIn != tokenOut` check in MonoX's swap function, the attacker inflated the MONO governance token's internal price through repeated self-swaps and then exchanged the overvalued MONO for $31 million in real assets across Ethereum and Polygon deployments.

The incident's significance for market health extends beyond its immediate $31 million impact. It established that single-token liquidity pool designs carry unique self-referential pricing risks not present in traditional pair-based AMMs, that multi-chain deployments amplify exploit impact linearly, and that even audited protocols can contain trivially exploitable bugs when basic invariant checks are not enforced. For the DeFi ecosystem, MonoX reinforced the principle that protocol security depends first on correct enforcement of fundamental mathematical invariants — and that no amount of architectural innovation can compensate for the absence of basic validation logic.
