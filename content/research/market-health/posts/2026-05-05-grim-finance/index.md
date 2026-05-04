---
date: 2026-05-05
entities:
  - id: grim-finance
    name: Grim Finance
    type: defi
  - id: fantom
    name: Fantom
    type: blockchain
  - id: spirit-swap
    name: SpiritSwap
    type: defi
title: "Grim Finance vault reentrancy, fake deposit accounting, and the $30 M Fantom yield-aggregator drain"
---

## 1. Introduction and incident overview

On 18 December 2021, Grim Finance, a Fantom-based yield optimizer, was exploited for roughly $30 million after an attacker used a reentrancy flaw in the protocol's vault deposit path to mint far more vault shares than their real liquidity contribution justified. Grim was part of the auto-compounding vault ecosystem: users deposited LP tokens into vaults, the protocol harvested rewards, compounded positions, and issued vault receipt tokens representing claims on the pooled assets. That model made internal share accounting the core trust surface. If a depositor could cause the vault to over-issue receipt tokens, they could redeem a disproportionate share of everyone else's LP inventory.

The exploit targeted the `depositFor()` logic in Grim's boost vaults. The function let callers specify the token used in the deposit flow. The attacker supplied a malicious token contract and used the vault's external token-transfer call as the reentrancy entry point. During the transfer, the malicious token reentered the same deposit function repeatedly before the original call completed. Each nested call caused the vault to calculate and mint additional Grim boost-vault shares, even though the attacker had not provided equivalent real underlying LP assets at every accounting layer. In the final reentrant frame, the attacker deposited legitimate SpiritSwap LP tokens, exited the recursive call chain, withdrew the inflated vault-token balance, removed liquidity, repaid flash-loaned capital, and kept the excess assets drained from Grim depositors.

The incident was not a subtle oracle manipulation or a cross-chain consensus failure. It was a classic vault-accounting failure triggered by a modern DeFi integration pattern: user-selectable tokens, forked yield-aggregator code, flash-loan-sized liquidity, and share issuance that trusted external contract calls too early. The market impact was immediate. Rekt reported that GRIM fell about 80% after the attack, and Grim's reputation as a yield optimizer collapsed because the exploit struck the custody layer that users relied on to represent their pooled positions honestly.

Grim Finance matters for market-health analysis because it shows how a single missing reentrancy guard in a vault deposit route can convert passive LP deposits into attacker-withdrawable inventory across many assets. The exploit also highlighted a recurring risk in 2021 DeFi: protocols forked successful vault templates faster than they could deeply audit all modified code paths. A bug in a deposit convenience function became a system-wide solvency event.

## 2. Background: Grim Finance and Fantom yield optimization

### 2.1 Yield optimizers as balance-sheet intermediaries

Yield optimizers aggregate user deposits into strategy vaults. A typical vault accepts LP tokens or single-sided assets, deposits those assets into external protocols, periodically harvests incentive tokens, sells or compounds rewards, and issues receipt tokens representing ownership in the vault. Users do not directly control the underlying farming positions while their funds are deposited. Instead, they trust the vault contract to maintain a correct ratio between:

1. the underlying assets held or controlled by the strategy;
2. the total supply of vault shares;
3. each user's individual share balance; and
4. the withdrawal function that converts shares back into underlying assets.

That accounting ratio is the vault's solvency boundary. If the vault mints too many shares for one party, the loss is socialized across all other depositors because the excess shares can be redeemed against the same finite pool of underlying LP assets.

Grim Finance offered this auto-compounding model on Fantom, a chain that in late 2021 had fast growth in lower-fee DeFi, high nominal yields, and many forks of Ethereum and BNB Chain designs. Fantom's low transaction cost made compounding vaults attractive, but it also made recursive exploit transactions and repeated trial execution inexpensive.

### 2.2 Boost vaults and receipt-token trust

The exploited Grim contracts were boost vaults. Users deposited LP tokens and received Grim boost-vault tokens, often denoted with a `GB-` prefix, which represented a claim on the LP inventory inside the vault. The attacker did not need to compromise user wallets one by one. They needed only to inflate their own receipt-token balance and then redeem those inflated receipts against the shared pool.

In a healthy vault, the deposit flow is conceptually simple:

1. receive the exact underlying token amount from the depositor;
2. measure the vault's prior asset balance and total share supply;
3. calculate the correct number of new shares;
4. mint shares only after the real asset transfer is complete; and
5. prevent any nested call from observing or manipulating intermediate state.

The Grim exploit violated the last requirement. The token-transfer step invoked an external contract selected by the attacker, and the function had no effective reentrancy barrier preventing that contract from calling back into the vault.

### 2.3 Why deposit functions need reentrancy protection

Reentrancy is often discussed in the context of withdrawals because the canonical DAO exploit involved recursive withdrawal before balance reduction. Grim demonstrates that deposits can be just as dangerous. A deposit function often looks safer because it appears to move assets into a protocol, not out of it. But when deposit accounting mints transferable claims, a false or duplicated deposit is economically equivalent to theft. The attacker can mint claims first and withdraw later.

Any function that performs an external call before all accounting invariants are fixed must be treated as reentrancy-sensitive. ERC-20 transfers are not always inert balance updates. They may involve non-standard tokens, malicious contracts, hooks, callbacks, or proxy behavior. Even if the intended underlying LP token is benign, allowing the caller to choose an arbitrary `token` parameter expands the trust boundary from "known LP token" to "any contract implementing enough of the token interface to be called."

## 3. The vulnerability

### 3.1 User-selectable token input

The core design error was that Grim's `depositFor()` path let a caller pass in a token address used in the transfer flow. According to the Rekt reconstruction, the attacker called `depositFor()` with `token == ATTACKER` and `user == ATTACKER`, causing the vault to call `safeTransferFrom()` on the attacker's malicious token contract. That malicious contract then recursively called `depositFor()` again.

The function therefore trusted an attacker-controlled contract at exactly the point where it needed to be most conservative. The vault should have accepted only the known underlying LP token for that vault, or it should have normalized all external inputs before any share-minting path could be reached. Instead, the user-selectable token acted as a programmable callback surface.

### 3.2 Missing reentrancy guard

The deposit function was not protected by a `nonReentrant` guard. A reentrancy guard would have blocked the second nested call as soon as the first call entered the function. Without it, every recursive frame could execute enough deposit logic to affect share accounting.

This distinction is important because checks-effects-interactions discipline alone can be difficult in deposit functions that must first confirm receipt of assets. A robust vault commonly combines:

- token whitelisting or immutable underlying-token constraints;
- balance-difference accounting based on actual received tokens;
- reentrancy guards on deposit and withdrawal functions;
- share issuance after real transfer validation;
- rejection of fee-on-transfer or non-standard tokens unless explicitly supported; and
- invariant tests proving that recursive calls cannot inflate `totalSupply` relative to `totalAssets`.

Grim's vulnerable path lacked the effective combination needed for an arbitrary-token external call.

### 3.3 Share inflation rather than direct asset transfer

The attacker did not simply call a function that sent them user funds. The exploit worked by inflating the attacker's vault-token balance. That made the theft indirect:

1. recursive calls caused extra `GB-` receipt tokens to be minted or credited;
2. those receipt tokens represented ownership of the real vault inventory;
3. the attacker redeemed the inflated balance;
4. the withdrawal pulled out more LP tokens than the attacker had contributed; and
5. the LP tokens were broken back into the underlying assets.

This is why vault-share accounting bugs are severe. The protocol's own redemption logic completes the drain once the attacker has a false claim.

## 4. Attack flow

### 4.1 Flash-loan setup and LP creation

The attacker began with flash-loaned assets, using pairs such as WBTC and FTM in the public reconstruction. They added liquidity on SpiritSwap and minted legitimate SpiritSwap LP tokens. This step gave the attacker enough real LP inventory to make the final deposit and withdrawal path executable.

Flash loans were not the root cause, but they made the attack capital-efficient. A well-funded attacker could have performed the same accounting exploit with their own capital, but flash loans removed the need to hold a large starting inventory. The protocol's security therefore had to be safe against temporary, transaction-scoped liquidity.

### 4.2 First `depositFor()` call with the malicious token

The attacker called Grim's `depositFor()` function and supplied their malicious token contract as the token parameter. The vault attempted to transfer tokens from the attacker. In a normal ERC-20 flow, this would move balances and return a boolean success value. In the attack flow, the malicious token's transfer logic became executable code controlled by the attacker.

When Grim called `safeTransferFrom()` on the malicious token, control moved out of Grim and into the attacker's contract. That external call happened before the entire deposit operation was safely finalized.

### 4.3 Recursive deposits

Inside the malicious token's transfer logic, the attacker reentered `depositFor()` multiple times. Rekt's workflow describes repeated loops where the malicious token reentered the same function, increasing the amount of minted Grim boost-vault tokens at every level. Because the outer calls had not finished, the vault treated each nested interaction as a valid additional deposit context.

The exact internal arithmetic depends on the specific vault implementation, but the economic effect was clear: the attacker accumulated a much larger vault-share balance than their real net asset contribution supported. The vulnerability was therefore not merely "reentrancy exists" but "reentrancy exists at a point where share issuance can be duplicated."

### 4.4 Final legitimate LP deposit

In the last recursive step, the attacker called `depositFor()` with the legitimate SpiritSwap LP token. This converted the attack path from fake-token recursion into a real deposit context tied to actual vault inventory. The nested calls then unwound, leaving the attacker with an inflated `GB-` vault-token position.

This final real-token step is why the exploit could drain real assets even though the reentrancy entry token was attacker-controlled. The malicious token opened the recursive accounting window; the legitimate LP token anchored the final vault position; the inflated receipt-token balance bridged the two.

### 4.5 Withdrawal and liquidity removal

After the attacker held inflated Grim boost-vault tokens, they withdrew from the vault. The withdrawal logic redeemed the attacker's excessive shares for more SpiritSwap LP tokens than they had actually earned. The attacker then removed liquidity from SpiritSwap, recovered the underlying assets, repaid the flash loan, and retained the surplus.

From users' perspective, this looked like a vault drain. From the contract's perspective, it was a sequence of apparently valid share redemptions. That difference matters: downstream integrations and dashboards that only watch for direct unauthorized transfers may miss the significance of share-supply inflation until the withdrawal has already consumed the vault.

## 5. Market and user impact

### 5.1 Approximately $30 million stolen

Public reporting places the loss at approximately $30 million. The attack entered Rekt's leaderboard at number 18 at the time, reflecting the size of the loss relative to other DeFi incidents. The stolen assets came from vault users, not from a treasury allocation that could be isolated from customer balances.

For a yield optimizer, this is the worst category of failure: the product's value proposition is custody, automation, and pooled optimization. When the vault accounting fails, the protocol cannot plausibly claim that the exploit was peripheral to its core service.

### 5.2 GRIM token price collapse

Rekt reported that the GRIM token fell about 80% after the attack. That price reaction was not just speculative panic. Governance and utility tokens for yield optimizers derive much of their value from confidence that users will continue to deposit assets, strategies will continue to earn fees, and the protocol will be able to maintain TVL. A $30 million vault exploit damages all three assumptions simultaneously:

- TVL leaves because users withdraw what remains;
- future fee revenue falls because fewer users trust the vaults;
- token holders face dilution or treasury pressure if compensation is attempted; and
- integration partners reassess whether the protocol is safe to list or route into.

The token-price collapse therefore represented a market repricing of future protocol credibility, not merely a reaction to a single balance-sheet event.

### 5.3 Fantom ecosystem trust effects

The exploit occurred during a period when Fantom DeFi was rapidly expanding. Many users allocated capital based on high annualized yields and fast-moving vault launches. Grim's failure showed that forked yield infrastructure could carry hidden systemic risk even when the underlying AMMs and chains continued operating normally.

Because vault strategies often sit on top of other protocols, an exploit can produce second-order effects:

1. sudden LP removal can affect DEX liquidity;
2. reward-token selling can pressure farm incentives;
3. bridge or exchange flows may increase as attackers exit stolen assets;
4. competing vaults using similar code may suffer withdrawals; and
5. users may withdraw from unrelated Fantom protocols because they cannot easily distinguish isolated contract risk from ecosystem-wide code reuse.

In this sense, the Grim event was both a protocol exploit and a market-confidence shock.

## 6. Relationship to the Charge DeFi incident

Rekt noted that Charge DeFi lost 1,849 CHARGE to the same attack vector only hours before Grim was exploited. Charge DeFi later said it had reached out to projects using the same code to warn them about the vulnerability. Whether or not that warning reached Grim in time, the sequence illustrates a recurring DeFi incident pattern: once a vulnerability in a forked codebase is demonstrated publicly, every unpatched fork becomes an immediate target.

This creates a "race condition" at the ecosystem level. Attackers can scan for similar code and execute quickly, while projects must identify exposure, pause contracts, communicate with users, and deploy fixes. Forked protocols that lack real-time security monitoring or emergency pause discipline are disadvantaged in that race.

The Charge-to-Grim sequence also undermines a common risk heuristic: users often assume that a protocol is safer if it is based on a widely used codebase. Forking can reduce design risk when the fork is exact and the original has been battle-tested, but it can increase implementation risk when teams modify small parts of the system without re-auditing the new trust boundaries. A convenience function or parameter change can invalidate the assumptions that made the original safe.

## 7. Why audits did not prevent the exploit

Grim Finance had been audited before the exploit, yet the reentrancy flaw remained. The lesson is not that audits are useless. It is that audits are point-in-time reviews, and their effectiveness depends on scope, reviewer expertise, code complexity, test coverage, and whether the deployed bytecode exactly matches the reviewed system.

Deposit-path reentrancy is especially easy to underestimate because it does not look like a direct outflow. Reviewers may focus on withdrawal paths, owner privileges, strategy permissions, or oracle assumptions while treating token transfers into the vault as low risk. But once arbitrary tokens can be passed into a deposit function, every token transfer becomes an untrusted external call.

An audit that misses this issue should prompt stronger process controls:

- require independent review of all external-call sites, not just withdrawal functions;
- add property-based tests for share-inflation invariants;
- run malicious-token harnesses against deposit routes;
- diff forked code against upstream and review every deviation;
- bind vaults to immutable underlying tokens where possible; and
- require emergency pause drills for newly disclosed fork vulnerabilities.

The Grim exploit shows that "audited" is not a binary security state. Market participants need to know what was audited, what changed afterward, and whether the test suite covered adversarial token behavior.

## 8. Market-health indicators and warning signs

### 8.1 Rapid TVL growth in unaudited or lightly modified forks

High TVL growth can be a vulnerability amplifier when code maturity lags capital inflow. Grim's model attracted assets because auto-compounding yields were attractive. But every new dollar in the vault increased the payoff for exploiting share accounting. For market-health monitoring, large and fast TVL inflows into forked vault systems should trigger deeper inspection of:

- whether deployed contracts match audited commits;
- whether vaults use known, immutable underlying tokens;
- whether deposits and withdrawals are reentrancy-guarded;
- whether strategies support arbitrary token parameters;
- whether a public bug bounty exists; and
- whether emergency pausing is fast and multisig-controlled.

Yield alone is not a health signal. High yield with weak vault invariants is often compensation for unpriced technical risk.

### 8.2 Arbitrary-token surfaces

Any vault function that accepts a user-supplied token address should be treated as high risk. A protocol may intend to support flexible deposit routing, zap functionality, or multi-token strategies, but that flexibility turns every token contract into a potential control-flow adversary. Market-health tooling can flag these surfaces by scanning ABI and source code for functions that combine:

1. token address parameters;
2. `transfer`, `transferFrom`, or `safeTransferFrom` calls;
3. share minting or balance-crediting logic; and
4. missing `nonReentrant` modifiers.

This pattern is not specific to Grim. It appears in vaults, routers, zaps, staking contracts, and reward distributors.

### 8.3 Receipt-token supply anomalies

The most direct on-chain signal for this class of exploit is an abnormal increase in receipt-token supply relative to underlying assets. A healthy vault's share supply may grow as deposits arrive, but the ratio between total shares and total assets should remain within expected bounds. A reentrancy-induced share inflation event can cause:

- sudden receipt-token minting to a new or low-history address;
- repeated nested calls in a single transaction;
- receipt-token supply increasing faster than underlying token balance;
- large withdrawal immediately after receipt-token minting; and
- flash-loan funding and repayment in the same transaction.

Real-time monitoring should compute vault price-per-share before and after major transactions. If price-per-share falls sharply during a deposit or if share supply expands without proportional underlying asset growth, the system should alert or pause.

### 8.4 Same-code exploit propagation

The Charge DeFi and Grim sequence shows that exploitability can propagate through code families. Once one protocol using a shared pattern is attacked, others become higher-risk even if they have not yet shown abnormal on-chain behavior. A market-health monitor should maintain clusters of protocols by code lineage and alert on:

- shared contract names and bytecode hashes;
- common upstream forks;
- identical vulnerable functions;
- audit reports from the same code family; and
- attacks on related deployments within a short time window.

In fast-moving DeFi ecosystems, "a similar project was just exploited" is itself a market-health signal.

## 9. Controls that would have reduced the loss

### 9.1 Reentrancy guards on deposit and withdrawal functions

The simplest control is to apply a reentrancy guard to every function that moves assets, mints shares, burns shares, or calls untrusted external contracts. This includes deposits. A guard would have blocked the nested `depositFor()` calls and prevented the recursive share inflation.

Reentrancy guards are not a substitute for correct accounting, but they are a low-cost defense-in-depth layer. Their absence in a vault function that accepts arbitrary tokens should be considered a critical issue.

### 9.2 Immutable underlying-token validation

Vault contracts should know their underlying asset. If a vault is designed for a specific SpiritSwap LP token, the deposit path should not accept a caller-selected token that can differ from the vault's configured underlying. If zap or router convenience is needed, it should happen in a separate contract that converts inputs into the exact underlying token before interacting with the vault.

Separating zaps from vault accounting narrows the vault's trust boundary. The vault receives only the known LP token, and the zap contract can be independently reviewed as a routing component rather than a custody ledger.

### 9.3 Balance-difference accounting

Instead of trusting the requested deposit amount, vaults should measure actual token balances before and after transfer. Shares should be minted based on the verified balance increase, not on caller-supplied amounts or assumptions about successful transfer behavior. This helps defend against fee-on-transfer tokens, tokens that return false success values, and malicious contracts that do not behave like standard ERC-20s.

Balance-difference accounting alone would not necessarily stop all reentrancy if nested calls can still alter shared state, but it reduces the ability to mint shares for assets that were not actually received.

### 9.4 Invariant and adversarial-token testing

Vault test suites should include malicious token contracts that attempt to reenter every external-call site. A strong invariant for this incident class is:

> No sequence of deposits, callbacks, withdrawals, or transfers can allow an account to withdraw more underlying assets than its proportional share of actual net deposits and earned yield.

This invariant should be tested under nested calls, fee-on-transfer behavior, failing transfers, zero-amount transfers, and flash-loan-scale balances. Traditional unit tests using only well-behaved mock ERC-20 tokens are insufficient.

### 9.5 Emergency response to fork-family warnings

When Charge DeFi was exploited using the same vector, every related fork should have immediately paused vulnerable vaults or disabled affected functions until review. Emergency pause mechanisms are controversial because they introduce centralization risk, but yield vaults already custody user funds. A narrow, time-limited pause controlled by a multisig can be preferable to leaving a known critical vulnerability open while analysis proceeds.

The key is transparency: protocols should publish what was paused, why, what code paths are affected, and how users can withdraw safely once patched.

## 10. Broader implications for DeFi market structure

### 10.1 Composability amplifies small accounting mistakes

Grim's exploit path touched flash loans, DEX liquidity, LP tokens, vault shares, and auto-compounding strategy logic. None of those components was necessarily broken in isolation. The failure came from how they were composed. This is a recurring DeFi market-structure theme: a small accounting mistake at one layer can become a multi-protocol drain because assets are tokenized, pledged, wrapped, and redeemed across layers.

Market-health analysis must therefore examine claim hierarchies, not only spot prices or TVL. A vault receipt token is a claim on LP tokens; LP tokens are claims on AMM reserves; AMM reserves are claims on underlying assets. If any layer can over-issue claims, the higher-level market can appear liquid until redemptions reveal the shortfall.

### 10.2 Fork velocity versus security maturity

The 2021 DeFi cycle rewarded rapid launches and high yields. Forking established protocols made deployment faster, but it also encouraged teams to treat inherited code as a commodity rather than a system with fragile invariants. Grim's failure shows that even small deviations in deposit routing can require a full security review.

Investors and users should evaluate forked protocols by asking:

- What changed from the upstream codebase?
- Were the changes audited independently?
- Are vault share invariants formally or property tested?
- Do deployed contracts include the same protections as upstream?
- Has the team rehearsed emergency response?

Forking can be a strength only if it preserves the upstream security assumptions. Otherwise, it creates a false sense of familiarity.

### 10.3 Token prices as confidence indicators

The GRIM token's reported 80% decline after the exploit illustrates how governance or utility tokens price operational credibility. For protocols whose revenue depends on TVL, a vault exploit reduces expected future cash flows even if the token itself is not directly drained. Token markets therefore act as rough confidence indicators for protocol security.

However, token price alone is a lagging signal. By the time GRIM collapsed, user funds had already been lost. Better market-health monitoring should combine token price, TVL movement, share-supply anomalies, and exploit propagation across related codebases.

## 11. Timeline

- **Before 18 December 2021**: Grim Finance operates Fantom yield-optimizer vaults, including boost vaults that issue receipt tokens for deposited LP assets.
- **Hours before Grim exploit**: Charge DeFi suffers a smaller loss using the same attack vector and says it warned projects using similar code.
- **18 December 2021**: The Grim attacker uses flash-loaned assets, creates SpiritSwap LP tokens, calls `depositFor()` with a malicious token, reenters the deposit path repeatedly, inflates Grim boost-vault shares, withdraws excess LP tokens, removes liquidity, and repays the flash loan.
- **Immediately afterward**: Grim publicly announces the exploit, investigates attacker fund movement, and users rush to withdraw remaining funds.
- **After disclosure**: Public reporting estimates the loss at about $30 million, and Rekt reports an approximately 80% GRIM token price decline.

## 12. Lessons for market participants

For users, Grim Finance is a reminder that vault APY is not the same as vault safety. A high-yield auto-compounder can fail because of a single accounting bug unrelated to the strategy's nominal yield source. Users should treat new vaults, heavily modified forks, and arbitrary-token deposit surfaces as higher risk even when the protocol has an audit badge.

For builders, the main lesson is that vault shares are money-like liabilities. Minting them must be protected with the same rigor as direct asset transfers. Every external call in a share-minting path is a potential control-flow break. Reentrancy protection, immutable asset validation, balance-difference accounting, and malicious-token tests should be baseline requirements.

For analysts, the incident provides a concrete monitoring template: watch vault price-per-share, receipt-token supply, underlying asset balances, flash-loan-funded deposits, and repeated nested calls. Combine those signals with code-lineage mapping so that an exploit in one fork automatically raises the risk score of related deployments.

The Grim Finance exploit was not simply a $30 million hack. It was a market-health failure in how DeFi priced forked custody risk. Users paid for yield while underpricing the possibility that the vault receipt tokens themselves could be fraudulently inflated. Once that invariant failed, the protocol's market, token, and reputation collapsed together.

## References

- Rekt, [Grim Finance - Rekt](https://rekt.news/grim-finance-rekt/)
- FTMScan, [example exploit transaction](https://ftmscan.com/tx/0x19315e5b150d0a83e797203bb9c957ec1fa8a6f404f4f761d970cb29a74a5dd6)
- OpenZeppelin, [ReentrancyGuard documentation](https://docs.openzeppelin.com/contracts/4.x/api/security#ReentrancyGuard)
- Solidity documentation, [security considerations: reentrancy and checks-effects-interactions](https://docs.soliditylang.org/en/latest/security-considerations.html)
