---
date: 2026-05-05
entities:
  - id: dodo
    name: DODO
    type: defi
  - id: dodo-v2
    name: DODO V2
    type: defi
  - id: crowdpooling
    name: Crowdpooling
    type: defi
  - id: ethereum
    name: Ethereum
    type: blockchain
title: "DODO V2 Crowdpooling reinitialization bug, fake-token flash-loan bypass, and the $3.8 M pool drain"
---

## 1. Introduction and incident overview

On 8 March 2021, DODO's V2 Crowdpooling contracts were exploited after attackers abused an initialization bug that allowed vulnerable pool contracts to be initialized more than once. By first initializing a pool with a counterfeit token, manipulating reserve accounting, then reinitializing with real pool tokens, attackers bypassed the flash-loan return check and drained several DODO V2 Crowdpools.

Public reports put the total drained value around $3.8 million. The affected pools included WSZO, WCRES, ETHA, and FUSI Crowdpooling pools. DODO stated that V1 pools, non-Crowdpool V2 pools, user wallet approvals, and the trading module were unaffected. The damage was concentrated in project-team-provided Crowdpooling liquidity rather than ordinary user wallets.

The incident had an unusual "Dark Forest" aftermath. Multiple actors interacted with the exploit path. DODO's preliminary report described Individual A and Individual B, while later reporting used animal names such as Hippo, Gazelle, Leopard, and Skunk to describe attackers, frontrunning bots, and recovery participants. Within 24 hours, DODO said it recovered $3.1 million of the $3.8 million stolen, had roughly $200,000 frozen on an exchange, and paid a $300,000 special bounty.

The DODO exploit is important for market-health analysis because it was not a typical AMM price-manipulation incident. It was an initialization and permission-management failure. The pool creation contract could be reinitialized by outsiders, letting attackers alter which token the pool thought it was managing and use counterfeit assets to satisfy accounting checks. In DeFi, initialization is a one-time trust boundary. If it can be crossed twice, the pool's identity can be rewritten.

## 2. Background: DODO and Crowdpooling

### 2.1 DODO's AMM model

DODO is a decentralized exchange protocol known for its Proactive Market Maker model. Rather than using a simple constant-product curve in every context, DODO's design aims to provide capital-efficient liquidity with pricing curves informed by external or configured reference prices. Like many AMM and launch/liquidity protocols, DODO expanded beyond simple trading pools into tools for token launches and initial liquidity formation.

The March 2021 exploit targeted DODO V2 Crowdpooling contracts. Crowdpooling was designed to help projects distribute tokens and establish liquidity. Project teams could work with DODO to create pools in which users participate in early liquidity events.

This feature created a specialized pool lifecycle:

- pool creation;
- initialization;
- parameter setup;
- token deposit;
- crowd participation;
- trading or settlement; and
- post-event liquidity management.

Each lifecycle step needs strict permissions. The first time a pool is initialized, it defines the pool's asset identity and accounting assumptions. A second initialization should not be possible.

### 2.2 Why initialization functions are dangerous

Initialization functions are common in proxy contracts, factory-created pools, and clone deployments. They replace constructors in cases where code is deployed once and configured later. But an initializer must be protected with a one-time guard. If anyone can call it repeatedly, the contract's identity can be reset.

In a pool, reinitialization can affect:

- base token address;
- quote token address;
- reserve variables;
- owner or maintainer parameters;
- flash-loan accounting;
- pricing logic;
- pool status; and
- permission boundaries.

The DODO exploit abused this exact class of risk. The vulnerable Crowdpooling contract could have its `init()` function called multiple times. That let attackers move the contract through a malicious configuration sequence rather than simply trade against it.

### 2.3 Flash loans and pool accounting

Flash loans are not inherently malicious. They allow an actor to borrow assets and return them in one transaction. A pool that offers or interacts with flash-loan-like flows must verify that borrowed assets are returned by the end of the transaction.

The DODO bug let attackers bypass that check by changing the pool's token identity and reserve accounting. If a pool thinks counterfeit tokens satisfy its return condition, real tokens can leave while fake tokens come back. This is not a liquidity-pricing failure; it is an asset-identity failure.

## 3. Vulnerability: repeated `init()` and counterfeit token substitution

### 3.1 The repeatable initializer

Rekt and Quadriga both summarize the root cause: the DODO V2 Crowdpooling smart contract had a bug allowing `init()` to be called multiple times. DODO's own quoted explanation in Quadriga states that after an audit, code changes were merged to simplify logic before going live, and a critical permission-management step was missed.

That means the bug was not an exotic compiler issue or an unknown EVM behavior. It was a basic lifecycle invariant failure:

> A pool initializer must be callable exactly once by the authorized creation path.

If an attacker can initialize the same pool once with fake parameters and again with real parameters, all downstream accounting becomes suspect.

### 3.2 Counterfeit token setup

The attack began with a counterfeit token. The exploiter initialized the vulnerable smart contract with a token under their control. This gave the attacker a way to shape the pool's internal reserve/accounting state around an asset that did not represent the real liquidity they intended to drain.

Counterfeit tokens are powerful in smart-contract exploits because they can be designed to satisfy interface expectations while having no economic value. A protocol that checks only "did a token transfer happen?" without anchoring the exact expected token identity can be fooled.

### 3.3 `sync()` and reserve zeroing

The exploiter then called `sync()` to set the reserve variable, representing token balance, to zero. In AMM and pool contracts, a `sync()` function usually aligns internal reserves with observed balances. That can be safe when token identity and pool state are fixed. It is dangerous if an attacker can manipulate token identity or initialization state around it.

In the DODO exploit sequence, `sync()` helped prepare reserve accounting so the later reinitialization/flash-loan path would accept the attacker's state.

### 3.4 Reinitialization with real tokens

After setting up the fake-token state, the exploiter called `init()` again, this time using a real token from DODO's pools. Because the initializer was not one-time protected, the pool accepted the new configuration. The attacker could now interact with real pool assets while retaining manipulated accounting conditions from the earlier steps.

This is the core conceptual failure: the pool's asset identity was not immutable after setup.

### 3.5 Flash-loan check bypass

Finally, the exploiter used a flash loan to transfer real tokens from the pools and bypass the flash-loan check. Public summaries describe the attacker returning counterfeit tokens in place of the original tokens, causing the contract's return-check logic to pass even though real assets had been removed.

This is an asset-substitution attack. The contract accepted "something" as satisfying the return condition because its initialization and reserve state had been manipulated. But economically, the pool lost real tokens.

## 4. Attack flow

### 4.1 Select vulnerable Crowdpooling pools

The attacks targeted several DODO V2 Crowdpools, including WSZO, WCRES, ETHA, and FUSI. DODO and public reports emphasized that V1 pools and non-Crowdpool V2 pools remained safe. That matters because it narrows the vulnerability to a specific contract family and lifecycle, not the entire DODO exchange.

Market-health analysis should always separate protocol-wide failure from module-specific failure. In this case, the affected module was Crowdpooling pool creation/initialization.

### 4.2 Initialize with counterfeit token

The attacker created a fake token and initialized the vulnerable contract with it. This gave the attacker control over the initial asset environment. A fake token can be minted, moved, or structured to support the exploit without representing real external value.

### 4.3 Manipulate reserves with `sync()`

The attacker called `sync()` and set the reserve variable to zero. This step manipulated the pool's internal belief about token balances. In a correctly initialized pool, reserve synchronization should reflect reality. In a reinitializable pool, it can become part of state confusion.

### 4.4 Reinitialize with real pool token

The attacker called `init()` again, now pointing the pool at a real token held in DODO's Crowdpooling liquidity. Because repeat initialization was possible, the pool accepted the new identity.

The distinction between fake and real tokens is central. The exploit did not need to break cryptography or forge a real token. It needed the pool to switch which token it considered authoritative at the wrong time.

### 4.5 Drain via flash-loan path

With the pool state prepared, the attacker used a flash-loan-like path to transfer real tokens out and return counterfeit tokens or otherwise satisfy the manipulated return check. This drained the pools while leaving the contract's check logic fooled.

Public reports estimate the total drained value at $3.8 million.

## 5. Multi-actor "Dark Forest" dynamics

### 5.1 Two initial individuals

Rekt's account describes two individuals: Individual A and Individual B. Individual B showed signs of being a frontrunning bot, including a contract address with several leading zeroes, CHI gas token usage, and extremely high gas prices. Individual B's exploits reportedly preceded Individual A's successful exploits by roughly ten minutes.

This is a critical DeFi market-health theme. Once an exploit transaction enters the mempool, searchers and bots can copy, frontrun, or mutate it. The first exploiter may not be the final recipient of funds.

### 5.2 Hippo, Gazelle, Leopard, and Skunk

Quadriga's summary of DODO's later postmortem describes a more complicated recovery narrative. It says DODO later referred to addresses as Hippo and Gazelle, with other actors such as Leopard and Skunk involved in frontrunning, bot capture, and recovery. The story included a honeypot-like trap that captured vETH from a bot and negotiations through samczsun and other whitehat contacts.

The exact naming is less important than the market structure it reveals: public mempools are adversarial. Exploit execution, bot frontrunning, whitehat interception, and negotiation can happen within minutes.

### 5.3 Recovery outcome

DODO reported recovering $3.1 million of the $3.8 million stolen within 24 hours, having another roughly $200,000 frozen on an exchange, and giving $300,000 as a special bounty. Hippo reportedly netted around $200,000 from smaller successful attacks, while much of the rest was intercepted or returned.

This recovery reduced user/project losses, but it does not reduce the severity of the bug. A protocol should not depend on bots and whitehats to correct initialization mistakes.

## 6. Market and user impact

### 6.1 Affected project teams

DODO stated that only project teams that worked with DODO during pool creation and provided liquidity for those pools saw losses. Ordinary DODO users' wallet assets were untouched, and wallet approvals were not affected. This distinction matters for risk communication.

However, project-team liquidity is still market infrastructure. If launch pools can be drained, token distribution and early liquidity formation are compromised. Projects using the platform face reputational and treasury losses.

### 6.2 Trading module unaffected

DODO also stated that the trading module was unaffected and that trading on the DODO platform continued. That helped contain panic. But the incident still raised questions about development and release processes, especially because DODO's quoted explanation said code changes were merged after an audit and missed the permission step.

For market participants, the lesson is that an audited module can become unsafe after post-audit changes. Audit status must be tied to the exact deployed code.

### 6.3 Crowdpooling trust shock

Crowdpooling is a trust-sensitive product. Projects and users rely on the protocol to handle launch liquidity and token accounting correctly. A pool-initialization exploit directly affects confidence in using that launch mechanism.

DODO disabled the pool creation portal, identified exposed pools, rescued roughly $80,000 still at risk, and later reported strengthened audits before re-enabling Crowdpooling. These steps were necessary to restore confidence.

## 7. Why the bug was preventable

### 7.1 One-time initializer guards

The simplest control is a one-time initializer guard. A contract should store an `initialized` flag and reject any second initialization. The initializer should also be restricted to the authorized factory or deployer path.

The invariant:

> Once a pool's token addresses and core parameters are set, no external caller can reset them.

This is now standard practice in proxy and clone patterns, but DODO's incident shows why it is essential.

### 7.2 Immutable asset identity after launch

Pool token addresses should be immutable after initialization. If a protocol needs migration or upgradeability, that process should use explicit governance/admin paths, timelocks, event logging, and user-visible migration steps. It should not be possible through the public pool interface.

Asset identity is not a minor parameter. It defines what economic object the pool holds.

### 7.3 Post-audit diff review

Quadriga quotes DODO as saying that code changes were merged after the PeckShield audit to simplify logic before going live, and the critical permission-management step was missed. This is a direct process lesson.

Any code change after an audit must be reviewed with the same seriousness as pre-audit code. A small simplification can remove a guard, change a permission path, or reopen an initialization function.

Release controls should include:

- audited commit hash pinned in deployment records;
- diff review from audited commit to deployed commit;
- automated checks for initializer guards;
- deployment dry runs;
- independent sign-off for permission changes; and
- monitoring for public initializer calls after deployment.

### 7.4 Invariant tests for fake-token substitution

Pool contracts should be tested against fake tokens and malicious tokens. Useful invariants include:

- a pool cannot be initialized twice;
- token addresses cannot change after initialization;
- `sync()` cannot create a state that allows asset substitution;
- flash-loan return checks require the exact borrowed token;
- counterfeit tokens cannot satisfy real-token obligations;
- reserve variables match actual balances for the configured token; and
- reinitialization attempts revert before any state change.

The DODO exploit is a textbook case where a fake-token test would have exposed the issue.

### 7.5 Mempool-aware incident response

DODO's recovery involved bots, frontrunning, and whitehat coordination. Protocols should assume that once an exploit is visible, mempool actors will compete to extract, copy, or intercept it.

Incident response should include:

- immediate vulnerable-function pause or frontend disablement where possible;
- on-chain monitoring of exposed pools;
- private transaction submission for rescue actions;
- security contact paths for whitehats;
- exchange-freeze coordination where applicable; and
- clear public communication about affected modules.

## 8. Market-health indicators

### 8.1 Public `init()` after deployment

Any deployed contract with a public initializer that can be called after setup is a high-risk signal. Market-health scanners can look for:

- callable `init()` or `initialize()` functions;
- missing initialized flag;
- mutable token-address storage;
- public factory bypass paths;
- repeated initialization events; and
- initialization after nonzero liquidity exists.

### 8.2 Pool identity drift

A pool should not change its base/quote token addresses after launch. Monitoring should flag any transaction that changes token identity, reserve token references, or key pool parameters outside a known migration path.

Identity drift is especially dangerous in systems with flash loans, because a token substitution can bypass repayment checks.

### 8.3 Post-audit deployment drift

Audits often reference a commit hash. If deployed bytecode differs materially from audited code, risk rises. DODO's incident highlights the importance of tracking post-audit changes.

Market-health dashboards should distinguish:

- audited source;
- deployed source;
- post-audit diffs;
- unaudited hotfixes; and
- deployment-time configuration.

### 8.4 Bot interception as a symptom

Frontrunning bots and whitehat interception can reduce losses, but their presence indicates the exploit was publicly reproducible. If a mempool bot can copy an attack within minutes, the vulnerability is mechanically simple enough that many actors can exploit it once seen.

Protocols should treat bot involvement as a severity amplifier, not a lucky detail.

## 9. Broader implications for DeFi launch infrastructure

### 9.1 Launch contracts hold concentrated trust

Crowdpooling and launchpool contracts often hold concentrated liquidity during sensitive launch windows. A bug in those contracts can damage both the protocol hosting the launch and the projects using it.

Unlike mature AMM pools with distributed liquidity, launch pools may have a small set of project-team deposits. That can make losses more targeted but still severe.

### 9.2 Initialization is part of security design

Smart-contract security discussions often focus on reentrancy, oracle manipulation, and access control after deployment. DODO shows that initialization is equally important. A pool's first configuration is the root of its security model.

If initialization can be repeated, the contract does not have a stable identity.

### 9.3 Recovery stories can obscure root causes

DODO's recovery story was dramatic and relatively successful. But the core lesson should not be "bots saved the day." The core lesson is that a missing permission-management step let attackers rewrite pool identity and drain liquidity. Recovery is an operational success; the bug was a preventive failure.

## 10. Timeline

- **Before March 2021**: DODO develops and launches V2 Crowdpooling contracts. Some code changes are merged after audit to simplify logic.
- **8 March 2021**: Attackers exploit the repeatable `init()` bug in DODO V2 Crowdpooling contracts.
- **Exploit sequence**: Fake token initialization, `sync()` reserve manipulation, reinitialization with real token, and flash-loan drain/bypass.
- **Immediate response**: DODO identifies exposed pools within minutes, rescues roughly $80,000 still at risk, disables the pool creation portal, and communicates with affected project teams.
- **Recovery**: DODO reports $3.1 million of $3.8 million recovered within 24 hours, around $200,000 frozen on an exchange, and $300,000 paid as a special bounty.
- **Aftermath**: DODO strengthens audit practices and re-enables Crowdpooling after additional reviews.

## 11. Lessons for builders, users, and analysts

For builders, the DODO exploit reinforces that initializers are critical security functions. They must be one-time, permissioned, tested, and monitored. Pool token identity must be immutable after launch.

For users and project teams, the lesson is that launch infrastructure risk is different from ordinary trading risk. A protocol's trading module can remain safe while its pool-creation module fails. Teams should ask whether launch contracts are separately audited and whether deployed code matches audited code.

For analysts, the DODO incident provides a durable checklist: scan for repeatable initializers, mutable token identity, post-audit diffs, fake-token substitution paths, `sync()` reserve manipulation, and flash-loan repayment checks that can be satisfied by the wrong asset.

The DODO V2 Crowdpooling exploit was therefore not just a $3.8 million hack. It was a reminder that a pool is only as safe as its initialization boundary. Once that boundary failed, fake tokens could stand in for real liquidity.

## References

- Rekt, [DODO - REKT](https://rekt.news/au-dodo-rekt)
- Quadriga Initiative, [DODO Finance Initialization Vulnerability](https://www.quadrigainitiative.com/casestudy/dodofinancehack.php)
- Halborn, [Explained: The DODO DEX Hack (March 2021)](https://www.halborn.com/blog/post/explained-the-dodo-dex-hack-march-2021)
- DODO, [Pool Incident Postmortem: With a Little Help from Our Friends](https://blog.dodoex.io/dodo-pool-incident-postmortem-with-a-little-help-from-our-friends-327e66872d42)
- Etherscan, [ETHA-USDT exploit transaction referenced by Rekt](https://etherscan.io/tx/0x0b062361e16a2ea0942cc1b4462b6584208c8c864609ff73aaa640aaa2d92428)
- Etherscan, [WSZO-USDT exploit transaction referenced by Rekt](https://etherscan.io/tx/0xff9b3b2cb09d149762fcffc56ef71362bec1ef6a7d68727155c2d68f395ac1e8)
