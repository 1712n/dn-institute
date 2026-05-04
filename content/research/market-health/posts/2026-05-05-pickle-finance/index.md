---
date: 2026-05-05
entities:
  - id: pickle-finance
    name: Pickle Finance
    type: protocol
  - id: dai
    name: DAI
    type: stablecoin
  - id: compound
    name: Compound
    type: protocol
  - id: ethereum
    name: Ethereum
    type: blockchain
  - id: yearn-finance
    name: Yearn Finance
    type: protocol
title: "Pickle Finance Evil Jar exploit, pDAI vault drain, and DeFi vault-accounting risk"
---

## 1. Introduction and incident overview

On 21 November 2020, Pickle Finance was exploited for roughly 19.7 million DAI from its pDAI Jar, a yield-aggregating vault on Ethereum. The attack became known as the "Evil Jar" exploit because the attacker deployed malicious Jar-like contracts that looked valid enough to interact with Pickle's controller. By combining fake Jar contracts, a vulnerable Jar-swap path, delegated converter logic, and Compound cDAI accounting, the attacker moved user deposits through protocol-controlled paths and ultimately redeemed cDAI for DAI.

The incident was one of the early DeFi vault failures that showed how composability can create hidden control-flow risk. Pickle's Jars were forked and modified versions of Yearn v1 vaults. The added flexibility of direct Jar-to-Jar swaps created a powerful generalized function, `swapExactJarForJar()`. That function did not adequately verify that supplied Jar contracts were genuine Pickle Jars. It also allowed attacker-controlled converter call data to reach logic that could trigger harmful calls in the context of the controller.

For market health, the Pickle exploit matters because vault shares and stablecoin deposits were treated as low-volatility yield instruments by users. A single composability and validation failure turned a stablecoin vault into a nearly $20 million loss. It demonstrated that yield aggregators are not just passive wrappers around assets; they are active accounting systems whose controllers, converters, strategies, and share tokens must be analyzed as one security boundary.

## 2. Pickle Finance and the pDAI Jar

### 2.1 Pickle Jars

Pickle Finance was a yield-optimization protocol. Users deposited assets into "Jars," which functioned like vaults: a user deposited an underlying token, received a Jar share token, and the protocol strategy attempted to earn yield by deploying the underlying token into other DeFi protocols.

The pDAI Jar accepted DAI and used a Compound DAI strategy. In simplified terms:

1. Users deposited DAI into the pDAI Jar.
2. The Jar issued pDAI shares.
3. The controller and strategy moved DAI into Compound.
4. Compound returned cDAI, a tokenized claim on supplied DAI.
5. Yield accrued through the Compound position.

This design is common in DeFi yield aggregators. It creates several layers of accounting: user shares, Jar balances, controller balances, strategy balances, and external-protocol receipt tokens.

### 2.2 Why vault accounting is fragile

Vault systems are sensitive because users do not hold the underlying asset directly after depositing. They hold a claim on a moving set of assets. If the vault strategy holds cDAI instead of DAI, or LP tokens instead of stablecoins, the controller must know exactly which tokens are legitimate strategy assets and which are incidental "dust."

The Pickle exploit abused this complexity. It was not enough for a contract to say "do not withdraw the want token." The strategy held cDAI as the economically meaningful asset, while DAI was the user's underlying deposit token. A dust-withdrawal protection that did not understand cDAI's role left room for the attacker to seize the receipt token and redeem it into DAI.

### 2.3 Added Jar-swap functionality

Pickle's ControllerV4 introduced direct swaps between Jars. The intent was flexibility: a user or protocol flow could move from one Jar position to another. The relevant function signature included `_fromJar`, `_toJar`, an amount, a minimum output, converter targets, and arbitrary data.

Flexibility was the problem. The controller accepted Jar-like contracts supplied by the caller. If the controller did not verify that those addresses were sanctioned Pickle Jars, a malicious contract could mimic the required interface and then behave differently inside functions such as `deposit()`.

## 3. The exploit mechanics

### 3.1 Fake Jar contracts

The attacker deployed fake Jar contracts that implemented enough of the Jar interface to pass the controller's expectations. The Evil Jar post-mortem lists functions such as `token`, `getRatio`, `decimals`, `transfer`, `transferFrom`, `approve`, `allowance`, `balanceOf`, `withdraw`, and `deposit` as sufficient for a malicious Jar to interoperate with the controller path.

The dangerous function was `deposit()`. In a real Jar, deposit should move the underlying asset into the vault and mint shares. In the Evil Jar, `deposit()` could instead transfer tokens from the controller to the attacker's address or contract.

This is the core validation lesson: matching an interface is not the same as being a trusted contract. In DeFi, interface compatibility can be malicious if the caller assumes semantic trust from syntactic compatibility.

### 3.2 First phase: moving DAI through the pDAI system

The attacker first used fake Jars and `swapExactJarForJar()` to manipulate the pDAI strategy state. Public technical analyses describe the attacker querying `StrategyCmpdDaiV2.getSuppliedUnleveraged()` and finding about 19.7 million DAI available through the strategy path.

The attacker then invoked `swapExactJarForJar()` with fake Jar addresses. This caused the strategy to deleverage and move DAI back through the pDAI Jar path. The attacker also called `pDAI.earn()` multiple times, causing the strategy to deposit into Compound and receive cDAI.

At this stage, the attacker was not simply calling "withdraw all DAI." They were shaping the protocol's internal accounting so that the value became represented as cDAI in a location and form the second stage could seize.

### 3.3 Second phase: converter delegatecall and cDAI extraction

The second phase used fake Jars, a fake underlying contract, and the approved Curve converter logic. The Evil Jar post-mortem explains that the controller delegate-called approved Jar converters with caller-supplied data. One approved converter, `CurveProxyLogic`, could be used in a way that let crafted inputs influence a call to a target contract.

The attacker used this path to trigger a `withdraw(address)`-style call on the strategy, moving cDAI out of the strategy and into the controller. Because the strategy's protection focused on the "want" token rather than treating cDAI as protected economic principal, cDAI could be treated as withdrawable dust.

Once the cDAI reached the controller, the controller's later deposit into the attacker-controlled Evil Jar transferred the cDAI to the attacker's contract. The attacker then redeemed cDAI through Compound for DAI and transferred the DAI away.

### 3.4 Why the attack required multiple flaws

The exploit was not a single-line bug. It required several design flaws to compose:

1. The controller did not whitelist or strictly validate Jar addresses supplied to `swapExactJarForJar()`.
2. Fake Jar contracts could implement the expected interface while redirecting `deposit()` behavior.
3. The controller accepted converter targets and data in a way that enabled dangerous delegated control flow.
4. The approved Curve converter path could be used for call injection.
5. The strategy's dust-withdrawal protection did not treat cDAI as protected principal for the pDAI strategy.
6. Compound receipt tokens could be redeemed into DAI after extraction.

Each flaw narrowed the gap between "flexible Jar swap" and "full vault drain." Together they enabled the attacker to convert user stablecoin deposits into attacker-controlled DAI.

## 4. Timeline

### 4.1 Attack date

The exploit occurred on Saturday, 21 November 2020. Public technical analyses identify the main exploit transaction as `0xe72d4e7ba9b5af0cf2a8cfb1e30fd9f388df0ab3da79790be842bfbed11087b0`.

### 4.2 Discovery and public analysis

The attack was rapidly reverse-engineered by DeFi security researchers. A public "Evil Jar" technical post-mortem by banteg, samczsun, and other contributors documented the fake Jar construction, the vulnerable controller flow, the converter path, the cDAI movement, and the mitigation steps.

BlockApex later published an accessible step-by-step analysis that summarized the fake Jar deployments, the query of the strategy's available DAI, the repeated `earn()` calls, the crafted Curve-proxy call, and the final cDAI redemption into DAI.

### 4.3 Immediate mitigation

The Evil Jar post-mortem describes immediate mitigation steps including setting the DAI PickleJar minimum to zero to prevent further deposits and revoking vulnerable converter logic. These were emergency containment actions aimed at preventing the same path from being reused while the team and community investigated.

## 5. Market impact

### 5.1 Stablecoin vault loss

The stolen amount was roughly 19.7 million DAI, close to $20 million. Because DAI is a stablecoin, the loss did not require token-price assumptions to understand. It was a direct loss of stablecoin principal from a yield vault.

Stablecoin vault losses are especially damaging for market confidence because users often perceive stablecoin strategies as lower volatility than volatile-asset farming. The Pickle exploit showed that a stable asset inside a complex protocol can carry high smart-contract and controller risk.

### 5.2 Vault-share repricing

Vault share tokens depend on the underlying assets remaining in the strategy. Once the pDAI Jar was drained, pDAI claims no longer represented the expected DAI backing. This forced the market to reprice not only Pickle's governance token and reputation, but also the risk premium for yield-aggregator vault shares more broadly.

The event therefore affected two layers:

1. Direct victims who lost DAI in the pDAI Jar.
2. The broader DeFi market, which had to reassess the safety of vault forks, strategy controllers, and generalized asset-moving functions.

### 5.3 Composability confidence shock

Pickle used Compound as an external yield venue and Yearn-like vault architecture as a design base. The exploit did not mean Compound failed, and it did not mean every Yearn-style vault was unsafe. It did show that forked or modified composable systems can introduce new risks at integration boundaries.

The market-health lesson is that each added layer changes the trust model. A strategy can be safe in isolation, a receipt token can be safe in isolation, and a controller can appear functional in ordinary use. But if a generalized controller function allows fake contracts and delegated converter calls, the combined system can fail.

## 6. Compensation and recovery context

Pickle Finance pursued a compensation framework after the exploit. Public summaries describe CORNICHON as an IOU-style token distributed to affected pDAI users, representing a claim on potential recoveries or future repayment funds. The important accounting point is that such tokens are not immediate full recovery unless they become redeemable for actual assets.

For strict income or loss accounting, there is a difference between:

1. Funds actually recovered from the attacker.
2. Assets allocated by the protocol or DAO for compensation.
3. IOU tokens representing possible future recovery.
4. Market-value changes in governance tokens.

The Pickle case illustrates why incident response should clearly distinguish realized recovery from claims, proposals, or reputational commitments.

## 7. Root-cause analysis

### 7.1 No trusted-Jar registry enforcement

The most direct root cause was that `swapExactJarForJar()` accepted attacker-supplied Jar-like contracts without enforcing that they were legitimate Pickle Jars. A trusted registry or whitelist would have constrained the function to known vault contracts.

The general rule is simple: if a protocol core function moves user funds, the counterparties it interacts with cannot be arbitrary contracts just because they implement the same interface.

### 7.2 Untrusted delegated execution

The controller's converter mechanism created another critical boundary. Delegating to approved converter logic with user-controlled data can be safe only if the converter strictly constrains target addresses, function selectors, and argument semantics. In this exploit, crafted data and a fake underlying contract helped produce a harmful call sequence.

Delegatecall-style patterns are especially risky because code executes in the caller's context. If an attacker can influence what code runs or what calls are made while the protocol context holds valuable approvals or balances, ordinary validation assumptions break down.

### 7.3 Misclassified receipt tokens

The pDAI strategy's economically important position was cDAI. Treating non-DAI tokens as potential dust did not account for the fact that cDAI represented the vault's principal. This is a recurring DeFi accounting problem: receipt tokens, LP tokens, and wrapped assets can be the actual asset, not incidental leftovers.

Strategies should explicitly mark protected assets, including derivative or receipt tokens, and reject emergency or dust-withdrawal calls that move them outside approved accounting paths.

### 7.4 Flexible design without invariant coverage

The Jar-swap feature was designed for flexibility. But flexible asset-moving functions need stronger invariants:

1. Total assets before and after the operation should reconcile.
2. Only approved Jars should be valid endpoints.
3. Strategy principal should not leave approved strategy paths.
4. Receipt-token balances should be protected.
5. User-supplied calls should not execute arbitrary target logic.

If those invariants are not enforced on-chain or thoroughly tested, flexibility becomes attack surface.

## 8. Detection and monitoring

### 8.1 Vault movement monitors

Yield protocols should monitor:

1. Large strategy withdrawals.
2. Sudden receipt-token movements from strategy contracts.
3. Controller balances spiking during complex operations.
4. New or unrecognized Jar-like contracts interacting with controllers.
5. Use of generalized swap or migration functions with unknown endpoints.

In the Pickle case, a monitor that alerted on unrecognized Jars passed into `swapExactJarForJar()` could have detected the attack path before the final extraction completed.

### 8.2 Receipt-token protection

Monitoring should treat receipt tokens as first-class assets. For pDAI, cDAI was principal. For other vaults, the protected assets might be yTokens, Curve LP tokens, Uniswap LP tokens, Aave aTokens, or staking derivatives.

A useful monitoring rule is: if a strategy's primary position token leaves the strategy outside an approved harvest, rebalance, migration, or withdrawal path, alert immediately.

### 8.3 Controller balance anomaly detection

Controllers should not unexpectedly accumulate large balances of strategy receipt tokens. If funds briefly pass through a controller, the destination should be deterministic and approved. A large cDAI balance appearing in the controller during a Jar swap should be treated as high-risk.

### 8.4 Converter-call restrictions

For protocols that use converter targets, monitoring should record:

1. Which converter was called.
2. Which final target address was reached.
3. Which function selector was used.
4. Whether the target belongs to an approved protocol.
5. Whether the call moved protected assets.

Converters should not be opaque execution tunnels.

## 9. Prevention controls

### 9.1 Whitelist all vault endpoints

Every externally callable function that moves funds between vaults should require both source and destination vaults to be approved in a trusted registry. Interface checks are insufficient.

### 9.2 Avoid user-controlled delegatecall paths

Delegatecall and generalized proxy logic should be minimized in core accounting paths. Where proxy logic is necessary, target addresses and function selectors should be hard-coded, allowlisted, or derived from trusted registries rather than supplied freely by callers.

### 9.3 Explicit protected-asset lists

Each strategy should maintain a protected-asset list that includes underlying tokens and receipt tokens. Emergency withdrawal or "recover stuck token" functions should refuse to move any token that represents current strategy principal.

### 9.4 Invariant tests for strategy migrations and swaps

Protocols should test invariants across the full controller-strategy-vault stack:

1. Total user assets cannot decrease except by documented fees or market movement.
2. A vault swap cannot introduce unknown contracts.
3. Receipt tokens cannot be reclassified as dust.
4. Controller approvals cannot be used by attacker-deployed contracts.
5. Converter calls cannot reach arbitrary strategy functions.

These tests should include malicious mock contracts, not only friendly integrations.

### 9.5 Timelocks or circuit breakers for new generalized functions

High-risk features like direct vault swaps should be deployed with conservative limits, timelocks, and circuit breakers. If a new function can move all user assets through composable paths, it should be treated as a major security boundary and rolled out gradually.

## 10. Lessons for DeFi users

Users often evaluate vaults by APY, token incentives, and brand. The Pickle exploit shows that vault risk also depends on:

1. Whether the protocol is a fork with modifications.
2. How controllers validate strategy and vault endpoints.
3. Whether receipt tokens are protected.
4. Whether external integrations use delegatecall or arbitrary calldata.
5. Whether emergency controls are tested and governed.

Stablecoin yield is not risk-free. A DAI vault can lose principal if the controller moves cDAI incorrectly or allows malicious contracts into the accounting path.

## 11. Conclusion

The Pickle Finance Evil Jar exploit was a landmark DeFi vault-accounting failure. By deploying fake Jar contracts, abusing `swapExactJarForJar()`, leveraging converter logic, and extracting cDAI from the pDAI strategy, the attacker drained roughly 19.7 million DAI from users.

The broader lesson is that DeFi vaults are accounting systems, not simple wallets. Controllers, strategies, receipt tokens, converters, and vault shares form one security boundary. To protect market integrity, protocols must whitelist vault endpoints, restrict delegated execution, classify receipt tokens as protected principal, monitor controller balance anomalies, and test malicious composability paths before generalized asset-moving functions hold real user funds.
