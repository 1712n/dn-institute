---
date: 2026-05-05
entities:
  - id: alpha-homora
    name: Alpha Homora
    type: defi
  - id: cream-finance
    name: Cream Finance (Iron Bank)
    type: defi
  - id: yearn-finance
    name: Yearn Finance
    type: defi
title: "Alpha Homora V2 — Iron Bank uncollateralized credit-line exploit and $37 M DeFi lending drain"
---

## 1. Introduction and incident overview

On 13 February 2021, the leveraged yield-farming protocol Alpha Homora V2 was exploited through a complex interaction with Cream Finance's Iron Bank lending pool, resulting in a loss of approximately $37.5 million. The attacker manipulated the accounting of Alpha Homora's integration with Iron Bank — a protocol-to-protocol uncollateralized credit line — to borrow far more than the protocol's actual collateral justified, ultimately extracting the excess as profit.

The exploit was significant for several reasons: it involved a vulnerability not in a single protocol but in the trust relationship between two interacting protocols (Alpha Homora and Iron Bank), it exploited an uncollateralized lending arrangement that existed between whitelisted DeFi protocols, and it demonstrated how the composability of DeFi systems creates attack surfaces at the interfaces between protocols rather than within any single protocol's code.

## 2. Technical background

### 2.1 Alpha Homora V2

Alpha Homora was a leveraged yield-farming protocol built by Alpha Finance Lab. It allowed users to take leveraged positions in yield-farming strategies — for example, providing leveraged liquidity to Uniswap or Curve pools. Users deposited collateral and borrowed additional capital from lending pools to amplify their yield-farming positions.

Alpha Homora V2 (launched in early 2021) introduced integration with Cream Finance's Iron Bank to source borrowing liquidity. Rather than maintaining its own isolated lending pool, Alpha Homora V2 borrowed from Iron Bank to fund users' leveraged positions.

### 2.2 Iron Bank and uncollateralized protocol-to-protocol lending

Iron Bank was a lending platform operated by Cream Finance (with close ties to Yearn Finance) that introduced the concept of protocol-to-protocol uncollateralized credit lines. Unlike standard DeFi lending (where borrowers must deposit collateral exceeding their loan value), Iron Bank allowed whitelisted protocols to borrow without posting full collateral, based on the assessment that these protocols were trustworthy and would repay.

Alpha Homora V2 was one of Iron Bank's whitelisted protocols. This meant Alpha Homora could borrow from Iron Bank up to a credit limit without depositing equivalent collateral into Iron Bank's contracts. The credit line was intended to be repaid as Alpha Homora users closed their leveraged positions and returned the borrowed capital.

This trust-based, uncollateralized lending arrangement created a fundamentally different risk profile from standard overcollateralized DeFi lending: the security of Iron Bank's funds depended not on on-chain collateral but on the correctness and security of Alpha Homora's smart-contract logic. If Alpha Homora's accounting could be manipulated to borrow more than its users' positions justified, the excess would be unbacked debt.

### 2.3 The HomoraBank contract

Alpha Homora V2's core contract, HomoraBank, managed users' leveraged positions. Each position tracked the user's collateral, the borrowed amount from Iron Bank, and the yield-farming strategy being employed. When a user opened a leveraged position, HomoraBank would borrow from Iron Bank on behalf of the user and deploy the combined (collateral + borrowed) capital into the specified yield-farming strategy.

The critical function for the exploit was the interaction between HomoraBank's position accounting and its calls to Iron Bank's lending functions. The attacker identified a way to manipulate the state of HomoraBank's position tracking in a way that allowed borrowing from Iron Bank without a corresponding legitimate position to back it.

## 3. Attack execution

### 3.1 Vulnerability: sUSD pool custom spell interaction

The exploit centered on Alpha Homora V2's integration with Curve's sUSD pool through a custom "spell" contract. Spells in Alpha Homora were adapter contracts that defined how to interact with specific yield-farming strategies (Uniswap, Curve, Sushi, etc.).

The attacker discovered that the sUSD Curve pool spell allowed a specific sequence of operations that manipulated the accounting of a position within HomoraBank:

1. The attacker could create a position in the sUSD Curve pool spell.
2. Through a series of operations involving adding and removing liquidity, the attacker could inflate the apparent value of their position as tracked by HomoraBank.
3. With an inflated position value, the attacker could borrow additional funds from Iron Bank through Alpha Homora's credit line, because HomoraBank's accounting believed the position justified the borrowing.

### 3.2 The double-counting mechanism

The specific mechanism involved a double-counting bug in how HomoraBank tracked the value of collateral within certain Curve pool positions. When the attacker performed specific operations through the sUSD spell:

- The collateral was counted once as the LP tokens held in the position.
- The same value was counted again through the underlying pool's reserve accounting.

This double-counting inflated the apparent collateral value, allowing the attacker to borrow from Iron Bank in excess of the actual collateral's true value. The difference between the inflated accounting value and the actual collateral value was extractable as profit.

### 3.3 Extraction

The attacker repeated the inflate-and-borrow cycle multiple times within a series of transactions, each time borrowing more from Iron Bank than the position's actual value justified. The borrowed funds (stablecoins and ETH) were extracted from Iron Bank's lending pools, while the inflated but actually underbacked position remained in Alpha Homora.

The total extraction was approximately $37.5 million, representing the gap between what Iron Bank lent to Alpha Homora (based on inflated position accounting) and the actual value of the positions backing those loans.

### 3.4 Fund disposition

The attacker deposited portions of the extracted funds into various DeFi protocols, including Aave and Compound, and moved other portions through multiple addresses. Some funds were later returned through negotiation (see Section 5).

## 4. Root-cause analysis

### 4.1 Uncollateralized trust as a systemic risk

The fundamental enabler of the exploit was the uncollateralized credit line between Alpha Homora and Iron Bank. In standard overcollateralized DeFi lending, a borrower's maximum extraction is limited by their posted collateral — even if accounting bugs exist, the protocol holds the collateral as a backstop. In the uncollateralized model, there is no on-chain collateral backstop: if the whitelisted protocol's accounting is manipulated, the lender (Iron Bank) has no collateral to seize.

This transforms accounting bugs — which in a standard lending protocol might allow slightly unfavorable liquidation prices but not net extraction — into direct extraction vectors. The uncollateralized credit line eliminated the safety margin that overcollateralization normally provides.

### 4.2 Position accounting complexity

Alpha Homora V2's support for multiple yield-farming strategies across multiple protocols (Uniswap, Curve, Sushi, etc.) required complex position-accounting logic that tracked the value of diverse LP tokens and farming positions. This complexity expanded the attack surface: each new spell/strategy integration introduced new accounting logic that could potentially be manipulated.

The sUSD Curve pool spell's double-counting bug was specific to the interaction between Curve pool mechanics (which involve adding/removing liquidity with specific token compositions) and Alpha Homora's position-valuation logic. The bug did not exist in isolation in either Curve's contracts or Alpha Homora's core logic — it emerged from the specific interaction between them.

### 4.3 Insufficient integration testing

The exploit path involved a specific sequence of operations through the sUSD spell that had not been adequately tested or audited. The combination of operations — creating a position, manipulating reserves through add/remove liquidity calls, and then borrowing against the inflated position — represented an adversarial interaction path that standard testing may not have covered.

## 5. Response and aftermath

### 5.1 Immediate response

Alpha Finance Lab detected the exploit and paused Alpha Homora V2's borrowing functionality to prevent further extraction. The team published a preliminary analysis and began working with Iron Bank/Cream Finance to assess the damage.

### 5.2 Dispute between Alpha and Iron Bank

The aftermath of the exploit created a significant dispute between Alpha Finance Lab and Cream Finance/Iron Bank regarding responsibility for the losses:

- **Alpha Finance's position**: The vulnerability was in Alpha Homora's spell interaction, and the loss ultimately came from Iron Bank's lending pools. Alpha committed to repaying the bad debt over time through a portion of protocol revenue.
- **Iron Bank/Cream's position**: The uncollateralized credit line was extended based on trust in Alpha Homora's smart-contract security, and the failure of that security should be Alpha's responsibility to make whole.

The dispute highlighted the unclear liability framework in protocol-to-protocol DeFi arrangements. Unlike traditional finance, where credit agreements include legal recourse mechanisms, the uncollateralized DeFi credit line had no established dispute-resolution procedure.

### 5.3 Partial resolution

Over subsequent months, Alpha Finance Lab allocated a portion of protocol revenue toward repaying the bad debt. However, the full $37.5 million was not immediately repaid, and the outstanding debt became a persistent point of contention within the DeFi community. The incident contributed to Cream Finance's own financial difficulties (Cream suffered additional separate exploits later in 2021) and to broader skepticism about uncollateralized protocol-to-protocol lending arrangements.

### 5.4 Industry impact on uncollateralized lending

The Alpha Homora exploit significantly dampened enthusiasm for uncollateralized protocol-to-protocol lending in DeFi. The concept — which had been promoted as a way to improve capital efficiency by allowing trusted protocols to borrow without tying up collateral — was revealed to shift risk from the borrower to the lender without adequate safeguards.

Following the exploit, Iron Bank and other lending protocols that had experimented with uncollateralized credit lines became more conservative in extending such arrangements, and the DeFi community became more skeptical of trust-based lending models that lacked on-chain collateral backstops.

## 6. Market-health implications

### 6.1 Protocol-to-protocol trust as a hidden risk layer

The Alpha Homora exploit revealed a risk layer that is largely invisible to end users: the trust relationships between DeFi protocols. When a user deposited funds into Iron Bank's lending pools, they were exposed not only to Iron Bank's smart-contract risk but also to the smart-contract risk of every protocol that had an uncollateralized credit line with Iron Bank. This risk was not typically disclosed or understood by depositors.

For market surveillance, protocol-to-protocol credit relationships represent hidden dependencies that can transmit losses across the DeFi ecosystem:

- A bug in Protocol A (the borrower) can cause losses in Protocol B (the lender).
- Depositors in Protocol B may not be aware of their exposure to Protocol A's security.
- The magnitude of potential loss is determined by the credit limit, not by any collateral backstop.

### 6.2 Composability at the interface level

Unlike exploits that target a single protocol's internal logic, the Alpha Homora exploit targeted the interface between two protocols — the accounting of how Alpha Homora's positions mapped to borrowing from Iron Bank. This interface-level vulnerability pattern is particularly concerning because:

- **Auditing gaps**: Audits typically focus on individual protocol contracts. The interface between protocols — how one protocol's state is interpreted by another — may fall between audit scopes.
- **Upgrade risk**: If either protocol upgrades its contracts, the interface assumptions may be invalidated, potentially introducing new vulnerabilities.
- **Complexity multiplication**: Each new integration (new spell, new lending partner, new strategy) multiplies the number of interfaces that must be secured, creating a combinatorial expansion of the attack surface.

### 6.3 The capital-efficiency vs. security trade-off

Uncollateralized lending was motivated by the desire for capital efficiency — protocols should not need to lock up collateral when their counterparties are "trusted." The Alpha Homora exploit demonstrated that this trade-off shifts risk rather than eliminating it. The capital saved by the borrower (Alpha Homora, which didn't need to post collateral) became risk borne by the lender (Iron Bank depositors, who had no collateral to seize in the event of default).

For the DeFi ecosystem, this implies that overcollateralization, while capital-inefficient, provides a crucial safety property: it bounds the maximum loss from any single protocol's accounting failure to the value of the posted collateral. Removing this bound in the name of efficiency creates tail-risk exposure that may not be adequately priced.

### 6.4 Precedent for inter-protocol dispute resolution

The Alpha Homora/Iron Bank dispute highlighted the absence of established dispute-resolution mechanisms for DeFi protocol-to-protocol arrangements. In traditional finance, credit agreements include covenants, default procedures, and legal enforcement mechanisms. In DeFi's uncollateralized credit model, there was no clear procedure for:

- Determining liability when a whitelisted protocol is exploited.
- Establishing repayment timelines and enforcement.
- Allocating losses between the borrowing protocol, the lending protocol, and end-user depositors.

The lack of resolution mechanisms meant that the dispute was managed through informal negotiation and community pressure rather than any formal procedure.

## 7. Lessons learned and recommendations

### 7.1 For DeFi protocols

1. **Prefer overcollateralization**: Maintain overcollateralized lending as the default model. The capital efficiency of uncollateralized lending does not justify the tail-risk exposure it creates for lenders.

2. **If extending credit lines, bound exposure**: If uncollateralized or undercollateralized lending is used between protocols, implement hard caps on total exposure and real-time monitoring of the borrower's position health.

3. **Audit interface interactions**: When integrating with other protocols, audit not only the individual contracts but the interface logic — how one protocol's state is read and interpreted by the other. Adversarial interaction paths should be explicitly tested.

4. **Conduct economic simulations**: Before deploying new integrations, simulate adversarial scenarios where an attacker attempts to manipulate position accounting through the specific operations available in the new integration.

### 7.2 For DeFi depositors

1. **Understand counterparty exposure**: When depositing into lending pools that extend credit to other protocols, understand that your deposit is exposed to the smart-contract risk of those counterparty protocols, not just the lending pool's own contracts.

2. **Assess credit-line risk**: Check whether a lending protocol extends uncollateralized credit lines, and to whom. The protocols receiving credit lines represent additional risk factors for depositors.

### 7.3 For market surveillance

1. **Map protocol-to-protocol credit relationships**: Maintain awareness of which protocols extend uncollateralized or undercollateralized credit to other protocols. These relationships represent hidden contagion paths.

2. **Monitor borrowing against whitelisted credit lines**: Track borrowing activity on uncollateralized credit lines for unusual patterns — rapid increases in borrowing, borrowing against new or unusual position types, or borrowing that approaches credit limits.

3. **Track inter-protocol disputes**: Unresolved disputes between DeFi protocols can indicate bad debt, potential insolvency, or governance failures that may affect depositors.

## 8. Conclusion

The Alpha Homora V2 exploit of February 2021 demonstrated the risks of uncollateralized protocol-to-protocol lending in DeFi. By exploiting a double-counting vulnerability in Alpha Homora's Curve sUSD spell, the attacker was able to inflate position accounting and borrow approximately $37.5 million from Iron Bank in excess of actual collateral. The loss was borne by Iron Bank depositors, who had no on-chain collateral backstop to limit their exposure.

The incident's broader significance lies in its illumination of three DeFi structural risks: the hidden counterparty exposure created by protocol-to-protocol credit relationships, the vulnerability of interface-level interactions between composable protocols, and the absence of dispute-resolution mechanisms for inter-protocol credit arrangements. The DeFi industry's subsequent retreat from uncollateralized lending models reflects a recognition that the capital efficiency gained by removing collateral requirements does not compensate for the tail-risk exposure it creates for lenders and depositors.
