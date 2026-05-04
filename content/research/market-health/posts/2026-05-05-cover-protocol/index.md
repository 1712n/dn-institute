---
title: "Cover Protocol, infinite minting, and the market risk of reward-contract mint authority"
date: 2026-05-05
entities:
  - Cover Protocol
  - COVER
  - Grap Finance
  - Binance
  - 1inch
  - Balancer
---

## Summary

1. On 28 December 2020, Cover Protocol's Blacksmith liquidity-mining contract was exploited through a reward-accounting bug that allowed attackers to mint an effectively unlimited amount of COVER.
2. Public writeups report that total COVER supply jumped from about **84,477 tokens** to more than **40 quintillion tokens** in one abuse path, collapsing the token price by roughly 90% within hours.
3. Grap Finance, the most visible exploiter, sold minted COVER, returned about **4,350 ETH**, burned remaining minted tokens, and left the message "Next time, take care of your own shit."
4. The return of funds did not erase the market damage: other exploiters kept proceeds, illegitimate COVER entered circulation, centralized exchanges halted trading, and users who bought or held during the collapse required compensation plans.
5. The incident is a market-health case study in why a reward contract should never have uncapped mint authority over a live token without hard supply limits, extreme-value tests, and real-time issuance monitoring.

## Why this incident matters

Cover Protocol was not just another DeFi farm token. It positioned itself as part of the decentralized insurance and coverage market. That made the exploit especially damaging for confidence. A protocol selling protection products suffered a failure in its own reward infrastructure, and the failure directly affected the market price and supply integrity of its token.

The affected component was Blacksmith, Cover's liquidity-mining and staking rewards contract. Blacksmith had authority to mint COVER rewards. That is a powerful capability. When reward logic is wrong, the failure mode is not a small accounting discrepancy. It can become arbitrary token issuance.

The December 2020 exploit showed how quickly token-market assumptions can break when a contract with mint authority has a calculation bug. A coverage token that had a finite circulating supply suddenly faced quadrillions of unauthorized units. DEX liquidity, centralized exchange books, arbitrage routes, and user balances all had to absorb the shock in real time.

This is why the event belongs in market-health research. It was not only a smart-contract bug; it was a failure of monetary integrity for a live token.

## The vulnerable surface: Blacksmith reward accounting

Blacksmith tracked reward distribution for approved liquidity pools. The broad pattern is familiar from liquidity-mining systems:

1. Users stake an LP token.
2. The contract tracks total pool deposits.
3. Rewards accumulate over time.
4. The contract calculates accumulated rewards per staked token.
5. Users claim rewards, and the reward token is minted or transferred.

The dangerous part was how Cover's Blacksmith contract cached and updated pool data. Technical analysis by Mudit Gupta described the core bug as a cache invalidation failure: the contract cached pool data in memory, updated pool data in storage, but later used stale cached data in reward calculations. The stale value prevented the usual writeoff from neutralizing an abnormally large `accRewardsPerToken` value.

That bug became exploitable when an approved Balancer pool had little or no remaining staked balance. If total token balance in a pool becomes tiny, a per-token reward calculation can become enormous. The attacker manipulated the pool state so that `accRewardsPerToken` shot up, while the writeoff value used to offset rewards remained based on the old, smaller value.

The result was a claimable reward that the contract treated as legitimate. Because Blacksmith had COVER mint authority, the inflated reward calculation became newly minted COVER tokens.

## A simplified attack flow

The most visible abuse path was not complicated from the outside:

```text
1. A new Balancer pool was approved for Blacksmith rewards.
2. The attacker deposited Balancer Pool Tokens into Blacksmith.
3. The attacker withdrew almost all of the position, leaving a tiny balance.
4. The attacker deposited again while the reward-per-token math was distorted.
5. The stale cached pool value caused the reward writeoff to be too small.
6. The attacker claimed rewards.
7. Blacksmith minted an astronomical amount of COVER.
8. The attacker sold minted COVER into market liquidity.
```

The Grap Finance sequence is the most widely quoted because it produced the largest theatrical moment. Rekt's timeline reports a deposit of about 15,255.55 BPT into the DAI/Basis pool, a withdrawal that left just 1 wei in the Blacksmith balance, a later redeposit, and then a reward claim that minted **40,796,131,214,802,500,000.212114436030863813 COVER**.

That number is absurd by design. It is the visible sign of a reward system that lost all connection to economic reality. The contract did not merely overpay a weekly reward. It minted enough supply to make existing token balances meaningless unless the market and protocol coordinated a rollback, burn, snapshot, or replacement.

## Why the bug became a market event

If an internal rewards ledger is wrong but cannot touch token supply, the damage may be bounded. Cover's Blacksmith contract could mint COVER. That converted a reward-accounting error into a circulating-supply crisis.

Once unauthorized COVER existed, attackers could sell it. Grap Finance sold minted COVER through 1inch, returned proceeds later, and burned remaining minted tokens. Other exploiters reportedly sold and retained proceeds. Rekt estimated **$9.4 million taken, $3.2 million recovered, and $6.2 million lost**. Mudit Gupta separately wrote that the original hacker had cashed out about **1,400 ETH, 1 million DAI, 3,000 LINK, and 90 WBTC**, about **$4.4 million** at the time.

The exact loss figure depends on whether the accounting includes returned ETH, retained proceeds, exchange-user compensation, token-holder losses, or market capitalization destruction. But for market-health analysis, the direction is unambiguous: supply integrity failed, the market repriced COVER violently, and the protocol had to plan a new-token or snapshot-based recovery.

This is a different loss profile from a vault drain. In a vault drain, assets leave a pool. In Cover's case, supply itself became untrustworthy. Holders had to ask whether their COVER represented the pre-exploit token, a contaminated post-exploit token, or a claim on a future replacement distribution.

## The Grap Finance "white hat" problem

Grap Finance became the public face of the exploit because it returned funds and framed the action as a white-hat intervention. Its message was blunt:

```text
Next time, take care of your own shit.
```

Crypto Briefing reported that Grap Finance said it had "No gains" and returned obtained LP funds to Cover. Rekt's timeline reports that Grap sent 4,351 ETH to Cover's deployer account and burned remaining minted COVER.

The return mattered. It reduced some direct losses and gave Cover a pool of assets for compensation. But it did not make the exploit harmless.

First, the market price had already collapsed. Traders who sold during the panic, bought contaminated tokens, provided liquidity, or held through exchange halts faced losses that were not cleanly reversed by the returned ETH.

Second, Grap Finance was not the only actor. Rekt identified six addresses that used the loophole. Some returned value; others did not. A white-hat label attached to one actor does not cover every copycat transaction.

Third, the publicity created a second market effect. GRAP itself received enormous attention, while COVER holders absorbed damage. Even if an actor returns proceeds, the event can still transfer value through reputation, attention, arbitrage, and token-market positioning.

For market health, "white hat returned funds" should never be treated as a sufficient resolution. The relevant question is whether users and markets are restored to a coherent pre-exploit state. In Cover's case, that required emergency warnings, trading halts, replacement-token planning, and exchange compensation.

## Exchange spillover and user losses

The exploit did not remain inside DeFi contracts. It spilled into centralized exchange markets.

As illegitimate COVER was sold and arbitraged, traders moved tokens across venues. Rekt observed a large increase in COVER deposits to Binance before trading was paused. Binance later announced an incident-resolution plan for affected users, with reporting at the time describing more than $10 million in compensation through its SAFU fund and a mix of replacement COVER, BUSD, and ETH handling depending on user timing.

This spillover is important. A DeFi mint bug can become a centralized-exchange user-protection problem within hours. The exchange may not be the source of the bug, but it still has to decide whether to halt trading, reverse or compensate trades, honor deposits, or coordinate with the issuer.

That creates a market-structure dependency. Users often assume that token balances can move freely between DEXs and CEXs. During an infinite-mint exploit, that assumption becomes dangerous. A token bought cheaply on a DEX may be illegitimate in economic terms but still technically transferable. If exchanges accept deposits before understanding the incident, losses can propagate into their order books.

The Cover incident therefore illustrates why exchanges need token-supply anomaly monitors, not just wallet risk filters. A sudden supply expansion from an authorized minter can be just as toxic as a stolen-token deposit.

## Insurance irony and confidence damage

Cover's product category made the optics worse. A DeFi coverage protocol is supposed to help users manage smart-contract and protocol risk. When its own token economics fail, the market reasonably questions whether the protocol can underwrite external risks.

This is not only reputational. Coverage markets depend on solvency, trust in claims processes, and confidence that governance and token incentives are intact. An infinite-mint event attacks all three. If the token used for incentives, governance, or coverage-market participation can be inflated by a reward contract, the entire protection model becomes suspect.

The market response showed that users understood this. COVER's price collapsed, trading venues paused activity, and the team had to discuss snapshots and replacement tokens. Even where funds were returned, the protocol's credibility was impaired.

For insurance-like DeFi products, internal control failures are especially costly because they contradict the product's core promise. The protocol does not merely lose assets; it loses the credibility needed to sell protection.

## The failed invariant

The core invariant should have been simple:

```text
COVER minted by rewards <= authorized emissions for the relevant pool and period
```

Blacksmith violated that invariant. A reward calculation tied to a tiny remaining LP-token balance and stale cached pool data allowed a claim far beyond intended emissions. The contract had no effective mint cap to stop the result.

This is the key design lesson. Reward systems should not rely on a single calculation to both determine and execute minting. If a contract can mint a token, it should have independent guardrails:

1. Maximum rewards per pool per block, day, or week.
2. Maximum total emission per epoch.
3. Sanity checks against configured reward schedules.
4. Pause triggers when issuance deviates from expected bands.
5. Separation between reward accounting and token mint authority.

Even if the reward calculation is wrong, hard caps should prevent astronomical issuance. A bug should be expensive and embarrassing, not existential.

## Why cache invalidation matters in financial contracts

The bug sounds mundane: cached pool data was stale. In ordinary software, stale cache bugs can show outdated UI, wrong recommendations, or inefficient behavior. In a financial contract, stale state can mint money.

Blacksmith used cached pool information to save gas and structure calculations. But when storage was updated and memory was not, later calculations referenced an outdated view of the pool. That outdated view interacted with the reward-per-token formula in a way that failed under an extreme pool-balance condition.

This is why DeFi code cannot treat "gas optimization" and "state correctness" as separate concerns. Caching storage reads into memory can be a valid optimization, but every cached variable becomes a second copy of financial truth. If the two copies diverge, the contract may settle value against the wrong one.

The Cover exploit is therefore a useful warning for forks and modified reward systems. A developer can copy a familiar pattern, adjust it for a new protocol, and accidentally invalidate one of the assumptions that made the original pattern safe. MasterChef-style accounting, reward debts, accumulated rewards per token, and LP-token balances are all fragile when modified without adversarial extreme-value tests.

## What monitoring should have caught

The on-chain signals were loud.

First, a newly approved Blacksmith pool saw a sequence of deposit, almost-full withdrawal, redeposit, and reward claim. That pattern is suspicious for any reward contract because it probes how per-token rewards behave at tiny pool balances.

Second, COVER mint volume exploded far beyond the expected emissions schedule. A supply monitor should have treated a mint of even a few times the configured reward rate as an emergency; a mint of quintillions of tokens should have stopped the system automatically if possible.

Third, DEX selling pressure followed the mint. Large newly minted balances moving into 1inch routes or other swap venues should have triggered exchange and liquidity-provider warnings.

Fourth, centralized exchange deposits rose as traders tried to exit or arbitrage. CEX monitoring should flag sudden deposits of a token that has just experienced abnormal minting from an official contract.

Finally, token-holder count and transfer activity spiked as opportunistic traders tried to catch the collapsing price. That behavior is not itself malicious, but it shows why a delayed public warning can increase secondary losses.

## Communication and containment

Rekt reported that Cover took about six hours to publicly acknowledge the attack and later warned users not to buy COVER and to remove liquidity from the COVER/ETH pool on SushiSwap. The team also said CLAIM/NOCLAIM Balancer pools were unaffected and later explored a new COVER token snapshot before the minting exploit was abused.

Those actions were directionally correct, but speed matters. In a live infinite-mint incident, every minute creates more room for arbitrage, exchange deposits, copycats, and uninformed trading. A protocol with token mint authority should have a prepared incident playbook:

1. Revoke or pause mint authority immediately.
2. Publish affected contracts and unaffected contracts separately.
3. Warn exchanges and major liquidity venues.
4. Announce whether the current token contract is considered contaminated.
5. Define snapshot logic before encouraging market participants to trade replacement claims.
6. Preserve transaction evidence for postmortem and compensation.

Cover removed minting access from Blacksmith once the issue was identified, but the market damage had already propagated. The incident shows that technical containment and public market containment must happen together.

## Compensation complexity

Compensation after an infinite mint is harder than compensation after a simple theft. A theft has a clearer before-and-after asset balance. An infinite mint contaminates trading history.

Who should be compensated?

1. Pre-exploit COVER holders whose token value was diluted.
2. LPs who absorbed toxic flow.
3. Users who bought after the exploit but before public warnings.
4. Centralized exchange users whose orders filled in a distorted market.
5. Protocol participants who held claims tied to COVER economics.

Each group has a different claim. A snapshot before the exploit helps pre-exploit holders, but it may not fully address traders who interacted during the chaos. Returned ETH helps, but it may not match every user's realized loss. Exchange-level compensation can protect exchange users, but it creates a different standard from DEX users.

This is why prevention matters. Once supply integrity fails, there is no clean repair that makes every participant whole without introducing new discretionary decisions.

## Lessons for token and rewards design

The Cover incident suggests several durable controls.

First, reward contracts should not have unlimited mint authority. If minting is necessary, the token should enforce caps at the token contract level, not only inside the reward contract.

Second, reward schedules should be independently observable. A monitor should be able to say, "This pool can mint at most X COVER this week," and compare actual mints against that bound.

Third, extreme states should be tested. Tiny pool balances, new pools, immediate deposit-withdraw cycles, one-wei residual balances, and very large LP deposits should all be part of the test suite.

Fourth, reward accounting should avoid stale cached state in any path that affects minting. If memory copies are used, developers should prove that every later calculation intentionally uses either the old state or the updated state.

Fifth, exchanges and DEX frontends should integrate supply-anomaly data. A token that just inflated by quadrillions of units should not be treated as an ordinary volatile asset.

Finally, insurance-like protocols need stricter internal controls than ordinary farms. Their product is trust in risk management. A basic emissions-control failure undermines the entire brand.

## Conclusion

The Cover Protocol exploit was an infinite-mint failure in a reward contract with excessive authority. A stale cached-pool accounting bug in Blacksmith allowed attackers to mint astronomical quantities of COVER, dump tokens into market liquidity, crash the price, force exchange halts, and trigger complicated compensation and replacement-token plans.

Grap Finance returned a large share of proceeds and burned remaining minted tokens, but the market-health damage was already done. Supply integrity is not restored simply because one exploiter returns funds. The deeper lesson is that token minting must be treated like a monetary policy operation with hard bounds, independent monitoring, and emergency controls. Without those controls, a reward bug can become a market-wide confidence crisis in a single morning.
