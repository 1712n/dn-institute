---
date: 2026-05-05
entities:
  - id: cashio
    name: Cashio
    type: defi
  - id: saber
    name: Saber
    type: defi
  - id: wormhole
    name: Wormhole
    type: defi
  - id: solana
    name: Solana
    type: blockchain
title: "Cashio CASH stablecoin — collateral validation bypass and infinite-mint exploit on Solana"
---

## 1. Introduction and incident overview

On 23 March 2022, the Solana-based stablecoin protocol Cashio suffered a catastrophic exploit that allowed an attacker to mint an effectively unlimited quantity of CASH stablecoins without depositing legitimate collateral. The attacker minted approximately 2 billion CASH tokens and redeemed them against the protocol's collateral reserves, draining approximately $52 million in stablecoins (USDC and USDT) and LP tokens from Cashio's backing pools. The CASH stablecoin's price collapsed from its intended $1 peg to near zero.

The vulnerability was a collateral-validation bypass: the Cashio protocol's minting function accepted a collateral deposit account without adequately verifying that the account contained legitimate collateral tokens. The attacker created a fake collateral account that passed the protocol's insufficient validation checks, enabling unbacked minting. The exploit demonstrated a class of vulnerability specific to Solana's account-model architecture, where programs must explicitly validate the accounts passed to them in each transaction.

## 2. Technical background

### 2.1 Cashio's stablecoin design

Cashio was a decentralized stablecoin protocol on Solana that issued the CASH token, intended to maintain a 1:1 peg with the U.S. dollar. The peg mechanism worked through collateral-backed minting and redemption:

- **Minting**: Users deposited eligible collateral tokens (primarily Saber LP tokens representing stablecoin liquidity pool positions) into Cashio's vault and received CASH tokens in return, at a 1:1 ratio to the dollar value of the collateral.
- **Redemption**: Users burned CASH tokens and received the corresponding collateral from the vault.

The collateral pool consisted of Saber LP tokens from stablecoin pools (e.g., USDC-USDT pools). Saber was a Solana-based stableswap AMM (similar to Curve on Ethereum), and its LP tokens represented claims on pooled stablecoin liquidity. The use of LP tokens as collateral meant that CASH was indirectly backed by USDC and USDT held in Saber pools.

### 2.2 Solana's account model and program validation

Solana's programming model differs fundamentally from Ethereum's. On Ethereum, smart contracts store their own state internally. On Solana, programs (smart contracts) are stateless — all data is stored in accounts, and programs receive references to accounts as inputs to each instruction. This means that every Solana program must validate the accounts passed to it: verifying that accounts are owned by the expected programs, contain the expected data format, and have the expected relationships to other accounts.

This validation requirement is a critical security surface for Solana programs. If a program does not adequately validate the accounts it receives, an attacker can pass fake or manipulated accounts that the program mistakenly treats as legitimate, leading to incorrect state transitions.

### 2.3 The collateral validation chain

Cashio's minting function required the caller to pass several accounts representing the collateral being deposited:

1. **The collateral token account**: Containing the Saber LP tokens being deposited.
2. **The Saber pool account**: Identifying which Saber pool the LP tokens came from.
3. **The underlying token mint accounts**: Identifying the stablecoins (USDC, USDT) that the Saber pool held.

For the minting to be secure, Cashio needed to verify the entire chain: that the LP tokens were from a legitimate Saber pool, that the Saber pool held genuine stablecoins, and that the stablecoins were the real USDC/USDT token mints (not fake tokens with the same name).

### 2.4 Wormhole-wrapped tokens

Complicating the collateral validation, some of the accepted collateral involved Wormhole-wrapped tokens. Wormhole is a cross-chain bridge that creates wrapped versions of tokens from other chains on Solana. Wormhole-wrapped USDC on Solana is a different token mint from native Solana USDC (issued by Circle). Cashio accepted both native and Wormhole-wrapped stablecoin LP tokens as collateral, which added another layer to the validation chain: the protocol needed to verify not only that LP tokens were from legitimate Saber pools but also that the underlying stablecoins were genuine (either native or from legitimate Wormhole wrapping).

## 3. The vulnerability

### 3.1 Incomplete account validation

The critical vulnerability was in Cashio's `print_cash` (minting) instruction. The function received a chain of accounts representing the collateral, but it did not fully validate the relationships between these accounts. Specifically:

- The function verified that the collateral token account existed and contained tokens.
- It checked that the token account's mint matched a known LP token type.
- However, it did not fully verify that the LP tokens' underlying Saber pool actually held legitimate stablecoins.

The gap was in the verification of the Wormhole-wrapped token chain. The function checked that an account was present representing the Wormhole-wrapped collateral, but it did not verify that this account was actually a legitimate Wormhole-wrapped token. The attacker could pass any account that had the expected structure, regardless of whether it was actually issued by the Wormhole bridge program.

### 3.2 The fake collateral chain

The attacker exploited this gap by constructing a fake collateral chain:

1. Created a fake token mint (not a real stablecoin).
2. Created a fake Saber pool account containing the fake token.
3. Created LP tokens for the fake pool.
4. Created a fake Wormhole-wrapper account that appeared to wrap the fake token.
5. Passed this entire fake chain to Cashio's minting function.

Because Cashio's validation only checked the structure and types of the accounts but not their provenance (whether they were actually created by the Saber or Wormhole programs), the fake chain passed validation. The minting function treated the fake LP tokens as legitimate collateral and minted CASH tokens against them.

### 3.3 Root cause: missing owner checks

In Solana's account model, every account has an "owner" field indicating which program created and controls it. A legitimate Saber pool account is owned by the Saber program; a legitimate Wormhole-wrapped token account is owned by the Wormhole program. By checking the owner field of each account in the collateral chain, Cashio could have verified that the accounts were created by the expected programs rather than by the attacker.

The missing owner checks were the root cause. Without these checks, the attacker could create accounts with arbitrary data that mimicked the expected format, and Cashio's program would accept them as legitimate.

## 4. Attack execution

### 4.1 Minting phase

On 23 March 2022, the attacker called Cashio's `print_cash` instruction with the fake collateral chain described above. Because the validation was insufficient, the instruction succeeded, minting approximately 2 billion CASH tokens to the attacker's account.

The minting was unbacked: no legitimate collateral (no real USDC, USDT, or Saber LP tokens) was deposited. The attacker had created CASH out of nothing.

### 4.2 Redemption and extraction

With 2 billion CASH tokens in hand, the attacker redeemed portions of them against Cashio's collateral vault. The vault held legitimate Saber LP tokens (backed by real USDC and USDT) deposited by prior CASH minters. The redemption function allowed the attacker to burn CASH tokens and receive the corresponding collateral from the vault.

The attacker redeemed CASH for the LP tokens, then withdrew the underlying USDC and USDT from the Saber pools. The total extraction was approximately $52 million in stablecoins.

### 4.3 CASH price collapse

The massive unbacked minting and subsequent selling pressure caused the CASH stablecoin to lose its peg entirely. Users who held CASH tokens found them worthless, as the collateral vault had been drained by the attacker's redemptions. CASH's price fell to effectively zero.

### 4.4 Partial return and message

In an unusual development, the attacker subsequently returned approximately $8 million to what appeared to be smaller affected accounts. The attacker included a message in a transaction suggesting that accounts holding less than $100,000 would be refunded, while larger holders would not. This "Robin Hood" messaging attracted attention but did not reverse the majority of the damage.

## 5. Cashio's response

### 5.1 Immediate shutdown

The Cashio protocol was effectively destroyed by the exploit. The collateral vault was drained, CASH tokens were worthless, and there was no mechanism to restore the protocol's backing. The development team acknowledged the exploit and shut down the protocol.

### 5.2 Post-mortem

The development team published a brief post-mortem identifying the missing account-validation checks as the root cause. The post-mortem acknowledged that the minting function should have verified the owner fields of all accounts in the collateral chain, ensuring they were created by the expected programs (Saber, Wormhole).

### 5.3 No recovery

Beyond the attacker's voluntary partial return (~$8M to small holders), there was no organized recovery effort. The protocol had no insurance fund, no backing entity with reserves to cover losses, and no governance mechanism that could coordinate a response. The $44 million that was not returned represented a permanent loss for affected users.

## 6. Market-health implications

### 6.1 Solana account-validation as a systemic risk surface

The Cashio exploit highlighted a class of vulnerability that is specific to Solana's account-model architecture. Because Solana programs receive accounts as external inputs rather than reading their own internal state, every program must implement comprehensive validation of every account it processes. This validation burden is:

- **Ubiquitous**: Every instruction in every Solana program faces this requirement.
- **Easy to get wrong**: Missing a single validation check (e.g., not verifying an account's owner) can create a critical vulnerability.
- **Invisible to users**: Users have no way to assess whether a Solana program's account validation is comprehensive.

The Cashio case is not isolated — several other Solana DeFi exploits in 2022–2023 involved similar account-validation failures, though Cashio's was among the most damaging. The pattern prompted the Solana development community to create frameworks and best practices (including the Anchor framework's account constraints) to reduce the likelihood of validation oversights.

### 6.2 Stablecoin protocol fragility

CASH was an algorithmic/collateral-backed stablecoin with a relatively small market capitalization and a simple design. The exploit demonstrated that stablecoin protocols — which users rely on to maintain a stable value — can fail catastrophically when their minting mechanism is bypassed. Unlike a DeFi lending protocol where an exploit drains the attacker's target pool, a stablecoin mint exploit creates unbacked tokens that dilute the value of all existing holders' positions.

For market-health surveillance, stablecoin protocols present a specific risk profile:

- **Minting function as the critical trust boundary**: If the minting function can be called with invalid collateral, the entire stablecoin's value proposition collapses.
- **Collateral verification chain depth**: The more layers of indirection in the collateral chain (LP tokens wrapping wrapped tokens wrapping stablecoins), the more opportunities for validation gaps.
- **Peg collapse as a contagion vector**: When a stablecoin loses its peg, protocols that use it as collateral or in liquidity pools suffer collateral damage.

### 6.3 Wormhole/cross-chain token complexity

The involvement of Wormhole-wrapped tokens in the collateral chain added complexity that contributed to the validation gap. Cross-chain bridge tokens add an additional layer of indirection: a Wormhole-wrapped USDC on Solana is not the same token as Circle's native USDC on Solana, and verifying the legitimacy of wrapped tokens requires checking the wrapping program's ownership, not just the token's metadata.

This complexity is a general concern for DeFi protocols that accept bridge-wrapped tokens as collateral. Each bridge introduces its own trust assumptions and account structures, and protocols must validate collateral against the specific bridge's program IDs rather than relying on generic token-format checks.

### 6.4 Audit and testing coverage for account validation

The Cashio exploit raises questions about the adequacy of security audits and testing practices for Solana programs. Account-validation vulnerabilities can be detected through:

- **Automated account-check analysis**: Tools that verify that every account passed to a program instruction has its owner, mint, and key fields validated.
- **Fuzz testing with fake accounts**: Testing frameworks that pass invalid or attacker-created accounts to program instructions and verify that they are rejected.
- **Anchor framework constraints**: The Anchor framework for Solana development provides declarative account constraints that automatically enforce common validation checks, reducing the surface for manual validation errors.

Whether Cashio underwent a security audit, and whether an audit examined the account-validation chain in the minting function, was not clearly disclosed.

## 7. Comparative context

The Cashio exploit belongs to a category of Solana-specific account-validation attacks:

| Protocol | Date | Loss | Validation gap |
|---|---|---|---|
| Cashio | Mar 2022 | ~$52M | Missing owner checks on collateral chain accounts |
| Wormhole | Feb 2022 | ~$320M | Missing signer validation on guardian set |
| Crema Finance | July 2022 | ~$8.8M | Fake price oracle account |
| Mango Markets | Oct 2022 | ~$114M | Oracle price manipulation (economic, not validation) |

While the specific mechanics differ, the Cashio, Wormhole, and Crema exploits share the common pattern of insufficient account validation — failing to verify that accounts passed to a program instruction were created by the expected programs and contain legitimate data.

## 8. Lessons learned and recommendations

### 8.1 For Solana program developers

1. **Validate account owners for every account**: Every account passed to a program instruction should have its owner field verified against the expected program. This is the single most important validation check and would have prevented the Cashio exploit.

2. **Use the Anchor framework's account constraints**: Anchor's `#[account]` macros provide declarative constraints that automatically verify account owners, seeds, and relationships, reducing the surface for manual validation errors.

3. **Verify the full collateral chain**: When accepting collateral that involves multiple layers (LP tokens, wrapped tokens, bridge tokens), verify every link in the chain — not just the top-level token account.

4. **Fuzz test with adversarial accounts**: Include test cases that pass fake accounts (with correct structures but wrong owners) to every instruction. These tests should verify that the program rejects the fake accounts.

### 8.2 For stablecoin protocol users

1. **Assess minting-function security**: Before holding a stablecoin, understand how the minting function validates collateral. Stablecoins with complex collateral chains (LP tokens, wrapped tokens) have more validation surface area.

2. **Evaluate audit coverage**: Check whether the stablecoin protocol has been audited and whether the audit specifically covered account validation in the minting path.

3. **Diversify stablecoin exposure**: Avoid concentrating holdings in a single stablecoin protocol, especially smaller or newer ones. The peg collapse of a single stablecoin can cause total loss for holders.

### 8.3 For market surveillance

1. **Monitor stablecoin supply changes**: Alert on sudden, large increases in a stablecoin's total supply that are inconsistent with normal minting activity.

2. **Track collateral ratios**: Monitor the ratio of a stablecoin's circulating supply to its backing collateral. A divergence between supply and collateral indicates either unbacked minting or collateral loss.

3. **Watch for new minter addresses**: Flag minting activity from addresses that have not previously interacted with the protocol, especially when accompanied by large mint amounts.

## 9. Conclusion

The Cashio exploit of March 2022 demonstrated the critical importance of comprehensive account validation in Solana's program architecture. By passing a chain of fake collateral accounts that mimicked the expected structure but were not created by the legitimate programs (Saber, Wormhole), the attacker bypassed the minting function's validation and created approximately 2 billion unbacked CASH tokens. The subsequent redemption of these tokens against the protocol's legitimate collateral reserves resulted in a loss of approximately $52 million, the complete collapse of the CASH stablecoin peg, and the effective destruction of the protocol.

The incident underscored a Solana-specific risk surface — the burden on every program to validate every account it processes — and reinforced the importance of owner-field verification, framework-level constraints, and adversarial testing for programs that handle value. For the stablecoin ecosystem, the Cashio case demonstrated that the minting function is the critical trust boundary: if it can be bypassed, the stablecoin's value is destroyed for all holders.
