---
title: "Uranium Finance, AMM invariant drift, and the market risk of unsafe forked-code migrations"
date: 2026-05-05
entities:
  - Uranium Finance
  - BNB Chain
  - WBNB
  - BUSD
  - USDT
  - U92
---

## Summary

1. On 28 April 2021, Uranium Finance, a BNB Chain decentralized exchange forked from Uniswap V2, was exploited for roughly **$57.2 million** during its v2 liquidity-migration period.
2. The bug was a small but fatal change to the pair contract's swap invariant check: constants were changed from **1,000** to **10,000** in parts of the fee-adjusted balance calculation, but not consistently throughout the final product check.
3. That mismatch broke the AMM's constant-product protection and allowed an attacker to swap a minimal input amount for about **98% of the output reserve**.
4. The stolen assets included about **34,000 WBNB**, **17.9 million BUSD**, **1,800 ETH**, **80 BTC**, **5.7 million USDT**, **638,000 ADA**, **26,500 DOT**, and **112,000 U92**.
5. Uranium is a market-health case study because it shows how a one-line arithmetic inconsistency in forked AMM code can turn a liquidity migration into a full reserve drain, cross-chain laundering event, and permanent collapse of user confidence.

## Why this incident matters

Automated market makers are only as safe as their invariants. A Uniswap-style pair contract holds two reserves and enforces a rule that, after a swap and fee adjustment, the product of the reserves should not decrease. Traders can change the composition of the pool, but they should not be able to remove value without paying the corresponding input.

Uranium Finance broke that guarantee. The protocol was a BNB Chain exchange forked from Uniswap V2, but the team modified the fee logic while moving to a new version. The modification was tiny in code terms and catastrophic in market terms. A few constants were adjusted to reflect different fee scaling, but the final invariant check still used an inconsistent denominator. That mismatch let the attacker satisfy the contract's check while taking nearly all of the output token from each pair.

The result was not a theoretical bug report. It was a multi-asset liquidity drain. Pools that users treated as market infrastructure were emptied because the contract that defined valid swaps no longer matched the economics of valid swaps.

## The invariant that failed

In a Uniswap V2-style pair, the swap function does not simply trust a caller's requested output. It checks that the balances after the swap still satisfy the fee-adjusted constant-product rule. In simplified form:

```text
adjusted_balance_0 * adjusted_balance_1 >= reserve_0 * reserve_1 * scale^2
```

The exact code uses integer math and fee multipliers, but the economic idea is straightforward: after accounting for the input token and fee, the pool should not be poorer.

Uranium changed part of this logic. Rekt summarized the error as follows: **1,000 was changed to 10,000 in two places but not at the end**. That means the contract was no longer comparing like with like. Two pieces of the calculation were scaled as if the denominator had changed, while the final invariant comparison still reflected the old scaling.

The bug created a false pass. The attacker could send a minimal amount of input token to a pair, request almost all of the output token, and still satisfy the broken check. In practice, public writeups describe the exploit as allowing a swap of 1 wei or similarly tiny input for about 98% of a pair's output reserve.

An AMM invariant is supposed to be the last line of defense. It should not matter whether the caller is trusted, the frontend is honest, or the trade is unusual. If the invariant is correct, invalid swaps fail. In Uranium's v2 pair contracts, invalid swaps could pass.

## The attack path

The attack was direct and devastating.

Before calling `swap()`, the attacker sent minimal amounts of each input token to the vulnerable pair contracts. Then the attacker used the low-level swap function to request very large output amounts from those pairs. Because the fee-adjusted invariant check was broken, the pairs accepted the swaps.

The funds removed were spread across the exchange's main liquid assets:

1. About **34,000 WBNB**, valued around **$18 million**.
2. About **17.9 million BUSD**, valued around **$17.9 million**.
3. About **1,800 ETH**, valued around **$4.7 million**.
4. About **80 BTC**, valued around **$4.3 million**.
5. About **5.7 million USDT**, valued around **$5.7 million**.
6. About **638,000 ADA**, valued around **$0.8 million**.
7. About **26,500 DOT**, valued around **$0.8 million**.
8. About **112,000 U92**.

The total reported loss was about **$57.2 million**. That number placed Uranium among the largest BNB Chain DeFi losses of the period and showed how much liquidity had accumulated behind a contract that had not preserved the forked invariant correctly.

## Migration timing made the risk worse

The timing made the incident more damaging and more suspicious to observers.

Uranium migrated to v2 about ten days before the exploit. That v2 deployment introduced the vulnerable pair logic. The team was then preparing a v2.1 update that would fix the issue, with liquidity migration expected around the time of the attack. Rekt highlighted the uncomfortable sequence: the bug was added in v2, left in place while TVL accumulated, and exploited on the day it was expected to be fixed.

The project's own postmortem language, quoted in the repo's cyberattack incident entry, said the team became concerned that a potential critical exploit existed while reviewing low-level risks identified by a BSC Gemz audit. The code had reportedly been running for about ten days without incident while accumulating more than $80 million in TVL.

That is the core market-health failure. Once the team suspected a critical pair-contract issue, every minute with live liquidity in the vulnerable contracts mattered. Users were still exposed while the team evaluated options such as contacting BSC or considering a white-hat-style intervention. The attacker moved faster than mitigation.

For migrations, the lesson is clear: if the core invariant of a live AMM may be broken, ordinary upgrade planning is too slow. Liquidity should be paused, capped, or emergency-migrated under a clear incident protocol before the vulnerability becomes public or exploitable.

## Forked code is not automatically safe

Uranium Finance was a fork of Uniswap V2. That fact may have reassured users. Uniswap V2 was battle-tested, widely reviewed, and deeply studied. But a fork inherits safety only to the extent that it preserves the assumptions that made the original code safe.

The Uranium bug came from modification. A constant changed in some places but not others. That is exactly the kind of change that makes forked code dangerous. Developers often copy a proven contract, adjust fees, add incentives, change tokenomics, and assume that the base security properties still hold. They may not.

In an AMM, constants are not cosmetic. Fee multipliers, denominators, reserve updates, and invariant checks form one mathematical system. If one part changes, every dependent comparison must change with it. A mismatch can make the protocol accept trades that the original system would reject.

This is why "fork of Uniswap" should never be treated as a sufficient safety claim. A better disclosure would say:

1. Which lines differ from upstream.
2. Which invariants are affected by those changes.
3. Which tests prove the modified invariant still holds.
4. Whether independent reviewers checked the exact deployed bytecode.
5. Whether any live migration changes the risk profile.

Without that information, users cannot know whether they are using battle-tested code or a fragile variant with a familiar name.

## The AMM math was the market

Traditional exchanges separate matching logic, custody, and settlement across multiple systems. In an AMM, the pair contract is the market. It holds reserves, prices trades, enforces the invariant, and settles output.

That means an arithmetic bug is not just a code bug. It is a market-structure failure. If the contract's definition of a valid trade is wrong, the market itself is wrong.

Uranium's pairs appeared to offer liquidity. Users deposited assets into pools because they expected swaps to obey constant-product economics. The attacker instead interacted with the pair contracts at the level where the market's rules were enforced and found that the rules no longer protected the reserves.

This distinction matters for risk monitoring. Price charts, TVL, and trade volume do not reveal whether the invariant is implemented correctly. An AMM can look liquid until the first adversarial swap drains it. Market health therefore depends on formal or property-based testing of the trading rule, not only observation of normal user flow.

## Cross-chain exit risk

The stolen assets did not remain neatly inside one venue. Rekt reported that at least **2,200 ETH** from the incident had been mixed through Tornado Cash. The attacker also held a liquid basket of BNB Chain assets and bridged representations of assets such as BTC, ETH, DOT, ADA, USDT, and BUSD.

This was an early sign of a pattern that later became common: a BNB Chain DeFi exploit could quickly become a cross-chain laundering problem. Even if Binance-linked infrastructure had some ability to monitor or freeze assets on BNB Chain, bridges and Ethereum-side mixers gave attackers additional exits.

For market health, cross-chain liquidity increases both usefulness and blast radius. It lets users move assets efficiently, but it also lets exploit proceeds seek the path of least resistance. A DEX exploit on one chain can produce ETH-side mixer flows, CEX deposit risk, and wrapped-asset issuer response problems.

Uranium showed that BNB Chain's ecosystem was no longer isolated. Once a protocol accumulated major liquidity, attackers could drain it and route value through multiple systems before users or developers could coordinate a response.

## Insider-risk questions

Public commentary raised suspicions because the exploit happened shortly before the planned v2.1 fix and because the Uranium contracts repository was reportedly removed from GitHub. It is important to separate suspicion from proof. The public record supports the following cautious framing:

1. The bug existed in v2 for roughly ten days.
2. The team was preparing a fix.
3. The exploit occurred before that fix could protect users.
4. The repository removal and timing created suspicion.
5. Suspicion is not the same as confirmed insider involvement.

From a market-health perspective, the important point is not to prove insider action. It is to recognize that opaque upgrade processes create insider-risk narratives even when no insider attack is proven. If users cannot inspect the code, compare versions, track deployed bytecode, or understand migration timing, they are forced to rely on trust.

DeFi protocols should reduce that trust surface. Public diffs, verified deployed contracts, reproducible builds, formal migration windows, and pre-announced emergency procedures all help prevent ambiguity. When a large exploit occurs during an opaque migration, trust collapses regardless of whether the attacker had inside knowledge.

## What monitoring should have caught

The most direct prevention would have been invariant testing before deployment, but runtime monitoring could still have helped.

First, every pair contract should have been tested against adversarial swaps that request extreme output amounts for tiny inputs. For a Uniswap-style AMM, a property test should assert that no swap can reduce the fee-adjusted product below the expected bound.

Second, any fork that changes fee denominators should run differential tests against upstream behavior. If the only intended change is fee rate, then the tests should show that reserve-draining swaps still revert.

Third, migration periods should include TVL caps until new contracts have survived enough review and monitoring. Uranium's v2 accumulated tens of millions of dollars before the flaw was exploited. A staged rollout could have reduced maximum loss.

Fourth, live swap monitoring should flag output-to-input ratios that are impossible under normal pricing. A trade extracting 98% of a reserve for minimal input is not a bad price; it is a broken market.

Fifth, if a team becomes aware of a potential critical vulnerability, the protocol should have a public emergency mode. Quietly preparing a fix while liquidity remains exposed leaves users blind and gives attackers a target.

## Audits and missed severity

The incident also illustrates the limits of audits when teams modify core primitives. The repo's incident entry notes that Uranium's postmortem said the bug had not been recognized as critical during multiple audits, and that the team later became concerned while reviewing risks identified by BSC Gemz audit work.

Audits are not magic. They are bounded reviews. A reviewer can miss a small constant mismatch, especially if the surrounding code resembles familiar Uniswap V2 logic. But in AMM code, a small constant mismatch can be the entire security boundary.

The right response is not to dismiss audits. It is to supplement them with invariant-focused tests and deployment controls:

1. Unit tests for ordinary swaps.
2. Fuzz tests for extreme swaps.
3. Invariant tests for reserve products.
4. Differential tests against upstream Uniswap V2.
5. Independent review of every changed line in pair contracts.
6. Formal pause or migration plans for suspected critical issues.

The more a protocol markets itself as a fork of battle-tested code, the more it should document the exact ways it is not that code.

## User-facing lessons

For liquidity providers, Uranium is a warning about chasing yield on forked AMMs. High returns often come from new deployments, new tokens, and new incentives. Those are exactly the environments where modified contracts, rushed migrations, and incomplete testing are common.

Users cannot personally audit every pair contract. But they can ask practical questions:

1. Is the pair contract verified on-chain?
2. Are the changes from upstream Uniswap or PancakeSwap documented?
3. Has the exact deployed version been live long enough to accumulate confidence?
4. Are TVL caps or staged migrations used?
5. Does the team have a credible emergency pause path?
6. Is there a history of prior exploits or rushed fixes?

Uranium had already suffered a prior rewards-contract exploit earlier in April 2021. That history should have increased caution. A second major failure in the same month suggested process weakness, not merely bad luck.

## Market implications

The Uranium exploit contributed to a broader lesson about BNB Chain DeFi in 2021. Cheap transactions and fast deployment made it easy to launch forks and attract liquidity. They also made it easy for small teams to deploy high-risk code changes at large scale.

The market did not always price that risk correctly. TVL could move into protocols faster than security processes matured. Users often treated forks as if they inherited the reputation of the original protocol, while attackers treated forks as new attack surfaces with familiar patterns and hurried modifications.

This mismatch is a recurring market-health problem. Liquidity is mobile and yield-seeking. Security review is slower. When TVL outruns assurance, a single bug can become a multi-million-dollar drain before the market has time to adapt.

## Conclusion

The Uranium Finance exploit was a $57.2 million failure of AMM invariant preservation. A forked Uniswap V2 pair contract changed fee-scaling constants inconsistently, allowing minimal-input swaps to pass the contract's check while draining almost all output reserves.

The incident's lasting lesson is that AMM math is market infrastructure. Forking battle-tested code does not preserve safety when the invariant is changed. Migrations, fee modifications, and emergency fixes must be treated as high-risk financial events, not routine deployments. If the pair contract's arithmetic is wrong, the market can be emptied in a single transaction.
