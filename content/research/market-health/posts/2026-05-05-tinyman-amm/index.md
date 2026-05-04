---
title: "Tinyman's Algorand AMM exploit: how a pool-token burn bug drained high-value ASAs"
date: "2026-05-05"
description: "The January 2022 Tinyman exploit on Algorand showed how a small redemption bug in immutable AMM contracts can become a market-wide liquidity emergency when attackers can burn pool tokens and withdraw two copies of the same valuable asset."
entities:
  - Tinyman
  - Algorand
  - ALGO
  - goBTC
  - goETH
  - ASA
---

## Summary

Tinyman, an Algorand-based decentralized exchange and automated market maker, suffered one of the first major DeFi exploits of 2022. The attack began around January 1-2 and exploited a previously unknown vulnerability in Tinyman's liquidity-pool smart contracts. Instead of burning pool tokens and receiving the expected proportional share of two different pool assets, the attacker could receive two units of the same asset. In pools where one asset was far more valuable than the other, especially goBTC and goETH pools, that mistake let the attacker extract disproportionate value and repeat the process.

Public reports from TRM Labs, AMBCrypto, CryptoPotato, CryptoNews Australia, and FXEmpire all describe the same basic pattern: the attacker funded wallets, targeted selected pools, swapped into assets and minted pool tokens, then abused the burn path to receive duplicate high-value assets. Tinyman warned users to remove liquidity because the protocol used immutable, permissionless contracts and could not simply pause or upgrade the vulnerable code. TRM reported more than $3 million in goETH and goBTC removed from liquidity pools, while Tinyman communications quoted by media reported roughly $3 million stolen and continued risk to remaining liquidity.

The incident is important for market-health analysis because it was not only a loss event. It was a liquidity confidence shock for an emerging Algorand DeFi venue. Tinyman's remaining liquidity reportedly fell sharply after the warning, and the team had to block routes in the web app, ask liquidity providers to withdraw, and work on compensation plans. That combination turned a contract bug into a market-structure event: prices became volatile, pools thinned, and users had to make urgent risk decisions while the exploit was still copyable.

The lesson is simple but durable. AMM pool-token accounting is custody accounting. If the burn path does not strictly enforce asset uniqueness and proportional redemption, LP shares stop representing a claim on a balanced basket and become an extraction tool.

## Tinyman's role in Algorand DeFi

Tinyman was a prominent decentralized trading platform on Algorand. It allowed users to swap Algorand Standard Assets and provide liquidity to pools, receiving pool tokens that represented their proportional ownership. The design served the same economic role as AMMs on Ethereum and other chains: liquidity providers deposited two assets, traders swapped against pool reserves, and the pool token was the accounting object tying LP ownership to reserves.

That pool-token relationship is the heart of the exploit. In a normal AMM, burning LP tokens should return a proportional amount of each asset in the pair. If a pool contains ALGO and goBTC, the LP burn should return some ALGO and some goBTC according to the user's share. It should never let the redeemer receive the valuable side twice while skipping the lower-value side. Once that invariant breaks, the LP token no longer represents a neutral share of the pool. It becomes a way to choose which reserve to drain.

Tinyman's importance to Algorand amplified the incident. A vulnerability in a small isolated pool would still harm LPs, but a vulnerability in the shared pool contract pattern created risk across many pools. Because the vulnerable contracts were immutable and permissionless, Tinyman could not patch the live pools in place or block all transactions at the protocol layer. The emergency response therefore shifted to user warnings, front-end changes, and liquidity removal.

## Exploit mechanics

The exploit sequence can be summarized in five steps.

1. The attacker activated and funded wallets.
2. The attacker targeted pools with a favorable value imbalance, especially pools involving goBTC or goETH.
3. The attacker swapped some assets and minted pool tokens.
4. The attacker burned those pool tokens through a vulnerable path.
5. The burn returned two copies of the same high-value asset instead of one unit of each pool asset, allowing the attacker to drain value and repeat.

AMBCrypto, citing Tinyman's own explanation, reported that attackers began by activating wallet addresses and depositing seed funds. They then interacted with targeted pools, swapped tokens, and minted pool tokens. The bug was exploited when pool tokens were burned: the attackers could receive two of the same assets instead of two different assets. The report said the attackers continued to burn and swap over 17 transactions until they had stolen roughly $3 million at the time of withdrawal.

CryptoNews Australia quoted Tinyman's explanation that the unknown bug in the burning of pool tokens let the attacker receive two of the same assets rather than two different assets. This worked in the attacker's favor because goBTC was significantly more valuable than ALGO; the attacker immediately swapped against ALGO to continue the attack. FXEmpire and CryptoPotato reported the same mechanism and noted that stablecoin pools were used to extract value and move assets to other wallets or centralized exchanges.

TRM Labs added forensic context. According to TRM, the attacker pre-funded a wallet from a centralized exchange. The exploit removed more than $3 million in goETH and goBTC from liquidity pools, with flows showing the same wallet that received a centralized-exchange deposit also receiving the goETH and goBTC removed from pools across 17 transactions. As of January 6, 2022, TRM reported that the attacker's primary wallet still held approximately 21 goBTC.

The economically important detail is not the exact transaction choreography of every swap. It is that a burn function, which should have been a conservative redemption path, became a selective-withdrawal primitive. AMM designs often focus on swap pricing and fee logic, but the LP mint and burn paths are equally critical because they define who owns reserves.

## Why duplicate-asset redemption breaks an AMM

Consider a simplified pool with ALGO and goBTC. A liquidity provider owns 1% of the pool. If the pool has 10,000 ALGO and 10 goBTC, burning the LP tokens should return 100 ALGO and 0.1 goBTC. That preserves proportional ownership. The pool loses 1% of each reserve, and the remaining LPs still own the same balanced basket.

If a bug lets the user receive two units of the same asset, the attacker can choose the valuable side. Instead of receiving 100 ALGO and 0.1 goBTC, the attacker may receive an amount equivalent to two claims on goBTC. The pool loses too much of the scarce reserve and too little of the cheaper reserve. The remaining pool becomes distorted, its price becomes unstable, and future swaps inherit the damage.

That kind of error is especially severe when assets have very different prices. A duplicate ALGO redemption in an ALGO/goBTC pool might be less profitable. A duplicate goBTC redemption is highly profitable because goBTC represents Bitcoin exposure on Algorand. The attacker's incentive is therefore to target pools where the duplicated asset is the most valuable component.

This is why the reported targeting of goBTC and goETH pools makes sense. Those assets were more valuable than ALGO, so the burn bug could be converted into immediate profit. After extracting high-value assets, the attacker could swap through stablecoin pools or other routes to lock in value and continue funding the exploit.

## Timeline

**January 1-2, 2022:** Tinyman pools were attacked. Tinyman publicly stated that an attack occurred on January 1/2 and that it exploited a previously unknown contract bug, allowing the attacker to withdraw assets from a pool they were not entitled to.

**Early attack hours:** Certain Algorand Standard Assets were drained, creating immediate volatility. Attackers funded wallets, targeted pools, swapped assets, minted pool tokens, and exploited the burn bug.

**Public warnings:** Tinyman urged liquidity providers to withdraw liquidity from all Tinyman-related contracts. Because the contracts were trustless and immutable, the team said it could not reverse or pause transactions at the protocol layer. CryptoNews Australia quoted Tinyman warning that losses after 9:00 UTC on January 4 would become the responsibility of users because there was nothing the team could do to stop the event.

**Front-end mitigation:** Tinyman blocked liquidity routes in the web app and replaced them with warning signs. This did not fix the immutable contracts, but it reduced the likelihood that ordinary users would continue interacting through the official interface.

**Continuing risk:** CryptoPotato reported that the exploit was still ongoing and that around $2 million in various digital assets remained at risk in pools. Tinyman again advised all users to remove liquidity as soon as possible.

**Compensation planning:** Tinyman stated that affected users would be reimbursed and that the team was working on compensation plans. Later public discussion around compensation appears to have been more complicated, but the immediate incident response included a commitment to reimburse affected users.

## Market-health impact

The direct reported loss was around $3 million, but the market-health impact was larger than a single loss figure.

First, the exploit undermined confidence in Tinyman's pool-token accounting. LPs had to assume that any pool using the vulnerable contracts could be attacked. That converts a local pool bug into a platform-wide withdrawal race. Rational LPs remove liquidity quickly, even from pools not yet exploited, because the first users to withdraw can preserve more value than those who wait.

Second, liquidity removal can amplify volatility. AMBCrypto reported that remaining liquidity stood around $5 million, down from about $43 million earlier. When pool depth collapses, trades move prices more aggressively, arbitrage becomes noisier, and users can suffer slippage even outside the original exploit path.

Third, immutable contracts changed the response options. On one hand, immutability supports decentralization because no administrator can arbitrarily seize assets or change rules. On the other hand, when a critical bug exists, immutability prevents a quick contract-level pause. Tinyman had to rely on warnings and front-end restrictions while attackers and copycats could still interact directly with contracts.

Fourth, the exploit targeted wrapped or bridged high-value assets on Algorand, such as goBTC and goETH. When an AMM incident affects wrapped Bitcoin and Ether representations, it can weaken confidence in cross-asset liquidity across the chain. Users do not need to believe the bridge itself failed to become concerned about the safety of trading and LP venues for bridged assets.

Finally, the exploit became an ecosystem reputational event. TRM described it as the first DeFi exploit of 2022. For Algorand DeFi, that timing mattered: the new year began with a visible warning that alternative-chain AMMs faced the same contract-accounting risks as Ethereum DeFi.

## Why immutability made the emergency harder

Tinyman's response repeatedly emphasized that the team could not stop transactions on the blockchain. This is a central tradeoff in DeFi security. Immutable contracts reduce governance and admin-key risk, but they make emergency remediation difficult. If the contracts cannot be upgraded or paused, the only immediate options are:

- warn users,
- remove or disable official front-end routes,
- coordinate with wallets, explorers, and community channels,
- ask LPs to withdraw,
- trace funds and coordinate with exchanges,
- deploy a patched replacement protocol later,
- compensate users if funds are available.

Those measures are slower and less deterministic than a pause switch. But a pause switch creates its own trust assumptions. A good market-health framework should not simply say "immutability is bad" or "pausability is good." Instead, it should ask whether the protocol's risk model matches its maturity and audit depth. If contracts are immutable from day one, the testing, formal verification, and audit requirements need to be higher, because bugs cannot be contained after deployment.

For Tinyman, the lack of an immediate fix meant that every hour of public knowledge increased copycat risk. AMBCrypto reported that other wallets were exploiting the bug and that Tinyman warned those actors could be held culpable. Once the exploit pattern is known, the opportunity shifts from one attacker to a public race against vulnerable pools.

## Audit and invariant lessons

The exploit highlights several invariants that AMM audits should treat as mandatory.

### Burn outputs must map to distinct pool assets

The burn path must prove that returned assets are exactly the pool's two distinct assets and that the same asset cannot be selected twice. This should be enforced by code, not assumed from user input, transaction ordering, or front-end behavior.

### Redemption must be proportional

Burning x% of LP supply should redeem x% of each reserve, minus any documented fees or rounding rules. Tests should verify that no burn path can overdraw one reserve while underdrawing the other.

### Asset identifiers require strict validation

On Algorand, assets are identified as Algorand Standard Assets. Any smart-contract logic that accepts asset IDs must ensure they match the pool's configured assets and cannot be duplicated or substituted. Identifier validation is not a cosmetic check; it is the boundary between ownership and theft.

### Value imbalance must be part of testing

The bug was more profitable when one side of the pool was much more valuable. Test suites should include high-imbalance scenarios such as ALGO/goBTC, stablecoin/volatile pairs, and low-decimal or high-decimal asset combinations. A path that looks harmless with equal-value test tokens may be catastrophic with wrapped BTC.

### Copycat resistance matters

Once a pool-level bug is public, every vulnerable pool becomes an open target. Protocols should have preplanned emergency communication and migration flows. Even immutable protocols can prepare user-facing tools to withdraw safely, publish affected pool lists, and monitor exploit transactions in real time.

## User and LP risk management

For liquidity providers, the Tinyman incident shows why LP risk is not limited to impermanent loss. LPs are also exposed to implementation risk in mint and burn paths. A pool can have healthy trading volume and still be unsafe if the accounting contract is flawed.

LPs evaluating an AMM should ask:

1. Is the pool contract audited, and is the audit specific to the deployed version?
2. Can contracts be paused or upgraded, and who controls that ability?
3. If immutable, what was the verification standard before launch?
4. Are mint and burn invariants tested under high-value asset imbalance?
5. Does the protocol publish emergency withdrawal instructions?
6. Are official front ends the only safe interaction path, or can users verify contract calls independently?
7. Does the protocol have a compensation fund or insurance mechanism?

Users should also be careful with post-exploit liquidity. When a protocol tells LPs to withdraw because an exploit is ongoing, the apparent high fees or arbitrage opportunities in damaged pools may be misleading. The risk is not merely price movement; it may be that the pool accounting itself no longer protects LP claims.

## Response quality

Tinyman's immediate response included public warnings, front-end route blocking, liquidity-withdrawal instructions, and a compensation commitment. Those steps were appropriate for an immutable-contract emergency. The most important warning was direct: users needed to remove liquidity because Tinyman could not stop the exploit at the contract layer.

The response also reveals a hard truth for DeFi teams. Once an exploit exists in immutable contracts, communications become part of the defense. The team must convince users to act before attackers drain remaining value. Delay, ambiguity, or overly technical wording can cost users money. Clear warnings, repeated across official channels, are a security control when code can no longer be changed.

At the same time, compensation promises should be precise. Affected-user reimbursement can restore trust, but only if eligibility, timing, funding source, and claim process are transparent. If compensation is incomplete or unclear, it can become a second reputational incident after the technical exploit.

## Comparison with Ethereum AMM exploits

Tinyman was on Algorand, not Ethereum, but the underlying lesson is chain-agnostic. AMMs are accounting systems. Every chain has a different smart-contract language and execution model, but LP shares still need to represent a proportional claim on reserves.

Ethereum AMM exploits often involve reserve manipulation, oracle misuse, or token behavior such as fee-on-transfer and reentrancy. Tinyman's exploit instead centered on asset-selection and burn validation. That difference matters because it reminds auditors not to overfit to one ecosystem's common bugs. On Algorand, TEAL and ASA mechanics produce their own failure modes.

For cross-chain DeFi, this is especially important. A user may see goBTC or goETH and assume the main risk is bridge custody. The Tinyman incident shows an additional layer: even if the wrapped asset itself is valid, the AMM holding it can lose value through local pool-accounting bugs.

## What a safer design would require

A safer AMM design for this failure mode would include:

- hardcoded or immutably stored pair asset IDs,
- explicit assertion that withdrawal asset A and withdrawal asset B are different,
- proportional reserve calculations based on total LP supply,
- rejection of any burn transaction that repeats an asset ID,
- test vectors covering duplicate-asset attempts,
- high-value imbalance simulations,
- independent audit of mint and burn paths, not only swap math,
- emergency migration tooling for immutable deployments,
- real-time monitoring for abnormal reserve changes.

In a non-upgradable protocol, these controls must be correct before launch. In an upgradable or pausable protocol, governance controls must protect users from admin abuse while still enabling emergency mitigation. Neither model is free; each moves risk to a different layer.

## Conclusion

The Tinyman exploit was a compact but severe AMM accounting failure. A pool-token burn path that should have returned two different assets could instead return two copies of the same valuable asset. Attackers used that bug against high-value Algorand Standard Asset pools, especially goBTC and goETH, removing roughly $3 million and forcing Tinyman to tell all users to withdraw liquidity from vulnerable contracts.

For market-health purposes, the key point is that the exploit damaged more than balances. It drained liquidity, increased volatility, exposed the limits of immutable contract response, and weakened trust in an early Algorand DeFi venue. It also reinforced a broader AMM rule: LP redemption logic is as critical as swap pricing. If the burn path is wrong, pool tokens stop being ownership receipts and become attack instruments.

## References

- TRM Labs, "Tinyman: The First DeFi Exploit of 2022?" — https://www.trmlabs.com/resources/blog/first-defi-liquidity-pool-exploited-in-2022
- AMBCrypto, "Another year, another hack: Algorand's DeFi platform Tinyman exploited for $3M" — https://ambcrypto.com/another-year-another-hack-algorands-defi-platform-tinyman-exploited-for-3m/
- CryptoPotato, "$3 Million Lost as an Algorand-Based Decentralized Trading Platform Exploited" — https://cryptopotato.com/3-million-lost-as-an-algorand-based-decentralized-trading-platform-exploited/
- CryptoNews Australia, "Algorand-Based DeFi Platform Tinyman Exploited for $3 Million" — https://cryptonews.com.au/news/algorand-based-defi-platform-tinyman-exploited-for-3-million-93270/
- FXEmpire, "DeFi Platform Tinyman Lost $3 Million During an Exploit" — https://www.fxempire.com/news/article/defi-platform-tinyman-lost-3-million-during-an-exploit-855009
- Halborn, "Explained: The Tinyman Hack (January 2022)" — https://www.halborn.com/blog/post/explained-the-tinyman-hack-january-2022
