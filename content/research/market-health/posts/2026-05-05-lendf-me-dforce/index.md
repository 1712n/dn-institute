---
date: 2026-05-05
entities:
  - id: dforce
    name: dForce
    type: defi
  - id: lendf-me
    name: Lendf.Me
    type: defi
  - id: imbtc
    name: imBTC
    type: token
  - id: erc777
    name: ERC-777
    type: token-standard
title: "Lendf.Me imBTC reentrancy exploit, ERC-777 callback risk, and the $25 M dForce lending-market drain"
---

## 1. Introduction and incident overview

On 19 April 2020, dForce's Lendf.Me lending protocol was drained of roughly $25 million in crypto assets after an attacker exploited an interaction between the protocol's Compound V1-style accounting and imBTC, an ERC-777 Bitcoin-backed token. The attack used ERC-777 callback behavior to reenter Lendf.Me before internal balances were safely updated, creating inflated collateral/accounting state and allowing the attacker to borrow or withdraw assets far beyond legitimate limits.

The incident became one of the defining early DeFi reentrancy events after The DAO. It was not caused by a price oracle manipulation, a governance takeover, or a compromised private key. It was caused by a protocol listing an asset with callback semantics that its lending-market accounting was not designed to handle.

The loss was severe: public reconstructions describe Lendf.Me's pools as being nearly completely drained across multiple assets, including ETH, USDT, USDC, imBTC, WBTC/HBTC variants, stablecoins, and other supported tokens. The unusual aftermath was that nearly all funds were later returned after intense tracing and pressure, reportedly following attacker operational-security mistakes. Even with recovery, the incident remains a market-health warning: integrations can invalidate assumptions inherited from forked code.

Lendf.Me's exploit matters because it sits at the intersection of three systemic risks:

- forked lending-protocol code reused outside its original asset assumptions;
- callback-capable token standards integrated as if they were plain ERC-20 tokens; and
- external token transfers occurring before final internal accounting.

Any one of those risks can be manageable. Combined, they drained a lending market.

## 2. Background: dForce, Lendf.Me, and imBTC

### 2.1 dForce and Lendf.Me

dForce was a DeFi ecosystem that included Lendf.Me, a lending protocol inspired by or forked from Compound V1-style money-market architecture. Users could supply supported assets, earn interest, borrow against collateral, and withdraw positions subject to collateral constraints.

In a multi-asset lending market, the central invariant is that internal user balances, total supply, collateral values, and actual token balances remain aligned. If a user supplies one asset, the system credits collateral. If the user withdraws or borrows, the system must verify solvency based on already-finalized state. If internal accounting can be observed or reused mid-update, the protocol can be tricked into believing collateral exists when it does not.

This is why lending markets are especially sensitive to reentrancy. A reentrant call can occur at a point where one part of the protocol believes an operation is complete while another part has not yet updated balances. That intermediate state can become exploitable collateral.

### 2.2 imBTC and ERC-777 hooks

imBTC was a Bitcoin-pegged Ethereum token issued by Tokenlon/imToken. Unlike a simple ERC-20 token, imBTC used ERC-777 behavior. ERC-777 is designed to improve token composability by allowing hooks such as:

- `tokensToSend`, called on the sender side; and
- `tokensReceived`, called on the recipient side.

Those hooks let contracts react during token transfers. This can be useful for richer token workflows, but it also means a token transfer is not just a passive balance movement. It can execute code in another contract while the calling protocol is still partway through its own state transition.

For protocols that assume token transfers are inert, ERC-777 hooks are dangerous. A contract that calls `transferFrom` may believe it is simply pulling tokens. In reality, the token may invoke a callback that can reenter the protocol before the original function completes.

### 2.3 The inherited assumption problem

Lendf.Me inherited or reused lending-market patterns from earlier code. Forking audited or battle-tested code can accelerate development, but inherited assumptions matter. Compound-style markets were originally designed around assets with certain transfer behavior. Adding a callback-capable token changes the threat model.

The key market-health question is not "Was the code forked from a known protocol?" It is:

> Does the fork's current asset list preserve the assumptions under which the code was safe?

In Lendf.Me's case, imBTC introduced a callback surface that the protocol's accounting flow did not safely absorb.

## 3. Root cause: callback reentrancy before final accounting

### 3.1 Checks-effects-interactions violation

The classic defense against reentrancy is checks-effects-interactions:

1. Check permissions and conditions.
2. Update internal state.
3. Interact with external contracts.

Lendf.Me's vulnerable path effectively interacted with an external token contract before all relevant accounting effects were finalized. When imBTC's transfer hook fired, the attacker could reenter Lendf.Me while balances were in a transitional state.

That ordering turned a token transfer into a control-flow handoff. Instead of completing a supply/withdrawal operation atomically, the protocol gave the token and attacker-controlled callback a chance to run nested lending-market operations.

### 3.2 ERC-777 sender-side callback risk

Some simplified summaries describe the vulnerability as `tokensReceived` reentrancy. More detailed reconstructions often focus on ERC-777 sender-side `tokensToSend` behavior during `transferFrom`. The exact hook name is less important than the design lesson: ERC-777 transfer hooks allow code execution during token movement, and a lending protocol must treat token transfers as external calls.

When a lending protocol calls into a token contract, it must assume the token can call back. If state is not already safe, reentrancy can observe or manipulate partially updated accounting.

### 3.3 False collateral from repeated state observation

The exploit did not require imBTC itself to lose its peg or malfunction. imBTC's callback features were part of the token standard. The lending protocol's problem was that the callback allowed the attacker to interact with Lendf.Me before the protocol's view of collateral and balances had stabilized.

By reentering during supply/withdrawal-related flows, the attacker could make the protocol overestimate supplied collateral or permit operations based on state that should not have been externally visible. Once collateral accounting was inflated, the attacker could borrow assets from other markets and drain the protocol's liquidity.

This is the lending-market equivalent of a double-counted deposit.

## 4. Attack flow

### 4.1 Prepare an imBTC position

The attacker used imBTC because it provided ERC-777 callback behavior. The attack required a contract capable of responding to token-transfer hooks and reentering Lendf.Me at the vulnerable point.

This was not a social-engineering attack or an administrator compromise. It was a contract-level interaction between a listed token and lending-market code.

### 4.2 Trigger a vulnerable supply/transfer path

The attacker initiated Lendf.Me operations involving imBTC. During token transfer, the ERC-777 hook gave the attack contract control before the original Lendf.Me operation had fully finalized its accounting.

The critical failure was not merely that a callback happened. Callbacks can be safe if internal state is already protected. The failure was that the callback happened while Lendf.Me still had exploitable intermediate state.

### 4.3 Reenter lending-market functions

Inside the callback, the attacker reentered Lendf.Me. Public reconstructions describe repeated recursive use of supply/withdrawal and borrowing paths to create inflated collateral and then draw assets from the protocol's markets.

The defensive way to frame this is:

- the protocol should have treated token transfer as untrusted external execution;
- the protocol should have finalized internal balances before that execution; and
- the protocol should have blocked nested calls into sensitive money-market functions.

Because those conditions were not enforced, a single listed token's callback behavior compromised the entire market.

### 4.4 Drain multiple assets

Once the protocol credited or accepted inflated collateral state, the attacker borrowed or withdrew assets across markets. Public summaries list a broad set of affected assets, including ETH, imBTC, USDT, USDC, HUSD, PAX, TUSD, BUSD, CHAI, WBTC/HBTC variants, and other supported tokens. The total loss was widely reported around $25 million.

This multi-asset blast radius is typical for lending markets. A bug in one collateral asset can become a loss in every borrowable asset because the lending protocol treats collateral as shared solvency support.

### 4.5 Funds returned

The aftermath was unusual. The attacker began returning assets within days, and public reporting states that nearly all funds were returned. Several incident summaries attribute the reversal to attacker operational-security failures and pressure from tracing, exchanges, and law-enforcement-adjacent escalation.

For users, recovery mattered. For market-health analysis, the exploit still counts as a severe protocol failure. A returned exploit demonstrates incident-response luck or pressure, not that the original system was safe.

## 5. Why the incident was systemic

### 5.1 Asset-listing risk

Lending protocols often focus on price, liquidity, volatility, and oracle availability when listing assets. Lendf.Me showed that token implementation behavior is just as important. A token can be liquid and valuable while still being unsafe to list if it executes callbacks during transfer.

Asset-listing review should include:

- token standard and extensions;
- transfer hooks;
- fee-on-transfer behavior;
- rebasing behavior;
- blacklist/pause powers;
- nonstandard return values;
- proxy upgradeability;
- ERC-1820 registry usage for ERC-777;
- known interactions with AMMs and lending protocols; and
- whether the protocol's code assumes inert ERC-20 transfers.

Listing imBTC without isolating ERC-777 callback risk turned one asset decision into a protocol-wide loss.

### 5.2 Forked-code risk

Forking saves time but transfers only code, not context. The original code's security properties depend on assumptions about assets, governance, parameters, integrations, and threat models. If a fork changes those assumptions, prior audits may no longer apply.

Lendf.Me was not merely "a Compound-like protocol." It was a Compound-like protocol with its own listed assets and operational choices. Those choices needed their own review.

### 5.3 Composability cuts both ways

ERC-777 was designed to improve token composability. DeFi markets were designed to compose assets and protocols. But composability increases the number of control-flow paths. A token transfer can become a function call. A function call can become a reentrant borrow. A collateral position can become a cross-market drain.

The incident illustrates adversarial composability: features that are useful in one context become attack surfaces in another.

## 6. Market impact

### 6.1 Immediate liquidity loss

The immediate effect was a near-total drain of Lendf.Me liquidity. Users who deposited assets into the lending market temporarily lost access to funds. Even though funds were later returned, the market experienced a full solvency shock.

In DeFi, a temporary full drain can still be catastrophic:

- users cannot withdraw during the incident;
- liquidations and borrowing markets freeze;
- governance and teams must coordinate under pressure;
- token prices may react before facts are known;
- integrators may halt connections; and
- confidence in similar forks declines.

### 6.2 imBTC and ERC-777 repricing

The exploit damaged confidence in imBTC integrations and ERC-777-style tokens in DeFi. The token standard's hooks were not inherently malicious, but the incident made clear that many protocols were not prepared to handle them.

After Lendf.Me, many protocols treated callback-capable tokens as high risk unless explicitly supported. This was a rational market response. The cost of one unsafe listing could exceed the benefits of supporting a new collateral type.

### 6.3 Early DeFi risk perception

In April 2020, DeFi was still small relative to later cycles. A $25 million loss was large enough to shape market perception. The incident reinforced several themes that would recur for years:

- forked protocols can inherit hidden fragility;
- integrations are security-critical;
- auditors must review live configuration, not just generic code;
- token standards can create non-obvious attack paths; and
- recovery is not the same as prevention.

## 7. Controls that would have reduced the loss

### 7.1 Reentrancy guards on market entry points

Sensitive functions such as supply, withdraw, borrow, repay, and liquidate should be protected against nested calls. A reentrancy guard would prevent a callback during one market operation from entering another operation before the first one completes.

This is especially important in multi-asset lending markets because reentrancy through one asset can affect solvency checks for other assets.

### 7.2 Checks-effects-interactions discipline

Internal accounting should be updated before external token transfers whenever safe and appropriate. If external calls must happen before final state changes, the protocol needs a stronger design that prevents intermediate state from being used in solvency checks.

For lending markets, the core invariant is:

> No external call may expose a state in which a user's collateral, debt, or total market balances can be interpreted inconsistently.

### 7.3 Callback-aware token admission

Protocols should classify tokens before listing:

- plain ERC-20;
- ERC-20 with nonstandard return values;
- fee-on-transfer token;
- rebasing token;
- ERC-777 or ERC-1363 callback token;
- upgradeable proxy token;
- pausable/blacklistable token; and
- wrapper/bridge token with external dependencies.

Callback tokens should either be rejected or handled through isolated adapters that are explicitly designed and tested for callbacks.

### 7.4 Invariant testing against malicious token mocks

Testing only with vanilla ERC-20 mocks is insufficient. Lending protocols should test with malicious or adversarial token mocks:

- token that calls back before transfer;
- token that calls back after transfer;
- token that reenters supply/withdraw/borrow;
- token that returns false;
- token that charges transfer fees;
- token that rebases during operation; and
- token that changes balance between checks.

The Lendf.Me exploit would be much easier to detect with a malicious ERC-777-style test token.

### 7.5 Per-asset isolation and caps

New collateral assets should be introduced with caps. If Lendf.Me's imBTC market had strict supply and borrow caps, the maximum cross-market loss could have been lower. Isolation modes and collateral caps are now common because they limit blast radius when a single asset has unexpected behavior.

The correct question is not whether an asset is safe enough to list forever at unlimited size. It is how much loss the protocol can tolerate while learning whether the asset behaves safely in production.

## 8. Market-health indicators

### 8.1 Callback-capable collateral

Any protocol accepting ERC-777, ERC-1363, or other callback-capable tokens should receive extra scrutiny. The monitoring question is whether callbacks can enter sensitive protocol functions before balances are final.

Indicators include:

- ERC-1820 registry usage;
- token contracts with sender/recipient hooks;
- lending markets without reentrancy guards;
- external token transfers before balance updates;
- forked Compound V1-style code; and
- lack of malicious-token tests.

### 8.2 Fork plus new asset class

A forked protocol listing an asset class not present in the original audited deployment is a high-risk combination. The fork may be safe for vanilla assets but unsafe for callback, rebasing, or fee-on-transfer tokens.

Analysts should compare the live asset list with the assumptions of the forked code and any cited audits.

### 8.3 Cross-market drain potential

In a lending market, a bug in one collateral asset can drain all borrowable assets. Health analysis should model the blast radius of each listed collateral:

- How much can be borrowed against it?
- Which markets can be drained?
- Are borrow caps active?
- Is the asset isolated?
- Are price or transfer semantics unusual?
- Can one asset's callback reach global accounting?

The Lendf.Me exploit was not limited to imBTC holders because the collateral system connected all markets.

### 8.4 Recovery-dependent solvency

If a protocol's survival depends on the attacker returning funds, the protocol has already failed from a market-health perspective. Recovery should be recorded separately from exploit severity. Lendf.Me's users benefited from returned funds, but the protocol's preventive controls did not stop the attack.

## 9. Broader implications for DeFi

### 9.1 Token standards are security boundaries

Token standards are not interchangeable implementation details. ERC-20, ERC-777, rebasing tokens, and fee-on-transfer tokens all create different integration requirements. A protocol that treats all tokens as "ERC-20-like enough" will eventually meet a token that breaks its assumptions.

The market-health lesson is to treat token standards as security boundaries. Crossing a boundary requires explicit review.

### 9.2 Asset onboarding is protocol development

Adding a new collateral asset is not merely a governance or business decision. It is a code-path expansion. The protocol is now executing against a new external contract with its own semantics. Asset onboarding should be treated like deploying a new feature.

That means reviews, tests, caps, monitoring, and rollback plans.

### 9.3 Early warnings existed

ERC-777 reentrancy risk was known before Lendf.Me. OpenZeppelin and others had written about ERC-777 hooks and reentrancy in AMMs such as Uniswap V1. The problem was not a completely unknown class of vulnerability. The failure was translating known risk into asset-listing controls.

This is common in DeFi security: the warning exists, but it is not operationalized where it matters.

## 10. Timeline

- **Before April 2020**: Lendf.Me operates as a dForce lending protocol with multiple supported assets, including imBTC.
- **18 April 2020**: Uniswap V1's imBTC pool is affected by a related ERC-777 reentrancy pattern, demonstrating callback risk in production.
- **19 April 2020**: Lendf.Me is drained through imBTC/ERC-777 reentrancy. Public reconstructions place the loss at roughly $25 million across many assets.
- **19-20 April 2020**: Security firms and the DeFi community identify the callback/reentrancy root cause; dForce pauses and coordinates response.
- **21-22 April 2020**: The attacker returns nearly all assets after tracing and pressure.
- **Aftermath**: dForce commits to distribution/recovery steps; the broader DeFi market becomes more cautious about ERC-777/callback-capable collateral.

## 11. Lessons for builders, users, and analysts

For builders, the lesson is to never assume a token transfer is inert. Treat every token as an external contract call, especially if it uses ERC-777 or any callback mechanism. Protect market entry points, update state before external calls, and test with malicious tokens.

For users, the lesson is that lending-protocol risk depends on every listed asset. Depositing USDC into a market can still expose a user to imBTC integration risk if the protocol allows imBTC collateral to borrow USDC.

For analysts, Lendf.Me provides a durable checklist: identify callback-capable assets, inspect transfer-before-accounting paths, check for reentrancy guards, compare asset lists with audit scope, and model cross-market blast radius.

The Lendf.Me exploit was not just a historical $25 million reentrancy incident. It was a demonstration that DeFi composability is only safe when every integration preserves the assumptions of the system it joins.

## References

- wheatli web3-knowledge, [Lendf.Me ERC777 reentrancy incident summary](https://github.com/wheatli/web3-knowledge/blob/e281721c33f7d07337c85481fa3cd709b18a97f8/08-security-incidents/defi-protocol/2020-lendfme-reentrancy.md)
- 0x-Shashi WEB3-AUDIT-SKILLS, [Lendf.Me forensic summary](https://github.com/0x-Shashi/WEB3-AUDIT-SKILLS/blob/4c0e3b9d17436fa2f7ae709ba1c78c075a20c301/skills/exploit-forensics/lendf-2020.md)
- OpenZeppelin, [Exploiting Uniswap: from reentrancy to actual profit](https://blog.openzeppelin.com/exploiting-uniswap-from-reentrancy-to-actual-profit)
- Etherscan, [publicly referenced Lendf.Me attack transaction](https://etherscan.io/tx/0xae7d664bdfcc54220df4f18d339005c6faf6e62c9ca79c56387bc0389274363b)
- SlowMist, [SlowMist analysis of the dForce hack](https://slowmist.medium.com/slowmist-analysis-of-the-dforce-hack-d6082e2e5111)
- PeckShield, [Uniswap/Lendf.Me root-cause and loss analysis](https://peckshield.medium.com/uniswap-lendf-me-hacks-root-cause-and-loss-analysis-50f3263dcc09)
