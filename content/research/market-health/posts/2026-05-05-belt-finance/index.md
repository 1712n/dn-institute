---
title: "Belt Finance's 4Belt flash-loan exploit: strategy imbalance and incorrect share valuation"
date: "2026-05-05"
description: "The May 2021 Belt Finance exploit on BSC showed how stablecoin vaults can be drained when strategy allocation logic and share valuation fail under flash-loan-sized balance swings."
entities:
  - Belt Finance
  - 4Belt
  - beltBUSD
  - BUSD
  - USDT
  - Binance Smart Chain
  - PancakeSwap
  - Ellipsis
  - Venus
---

## Summary

On May 29, 2021, Belt Finance lost 6,234,753 BUSD in a flash-loan exploit against its Binance Smart Chain stablecoin infrastructure. The affected product was the 4Belt pool, which supported USDT, USDC, BUSD, and DAI, with the attacker specifically exploiting the beltBUSD vault and underlying strategy allocation logic. Belt Finance said the attacker used a smart contract that borrowed from PancakeSwap and executed the exploit eight times. Decrypt reported that the attack lasted about ten minutes before the team halted deposits and withdrawals and patched the vulnerability.

The exploit did not depend on a volatile token price pump. It targeted accounting. Belt's vault attempted to route deposits to the most undersubscribed strategy and withdrawals from the most oversubscribed strategy. By injecting hundreds of millions of flash-loaned BUSD, swapping large amounts through Ellipsis, and repeatedly changing which strategy appeared under- or over-subscribed, the attacker made Belt's share valuation and strategy accounting pay out more BUSD than the attacker was entitled to withdraw.

Rekt summarized the core issue as "incorrect share valuation." CryptoSlate and CryptoNews.net quoted Belt's postmortem: the attacker used PancakeSwap flash loans, exploited the beltBUSD pool and underlying strategies, and executed the contract eight times for 6,234,753 BUSD profit. Decrypt reported that beltBUSD vault users suffered a 21.36% loss and 4Belt pool users suffered a 5.51% loss. The combined attack cost was reported as 50,030,452 BUSD, with 43,795,699 BUSD used as transaction fees.

For market-health purposes, Belt Finance belongs in the same family as Harvest Finance and other strategy-accounting exploits. The protocol offered stablecoin optimization, so users reasonably expected low price volatility. But stablecoin pools can still be high-risk if their internal accounting assumes balances are smooth, strategies are balanced, or share prices cannot be manipulated atomically.

## What Belt Finance did

Belt Finance was a Binance Smart Chain yield optimizer and stablecoin-focused DeFi protocol. Its 4Belt pool let users interact with a basket of major stablecoins: BUSD, USDT, USDC, and DAI. The platform routed assets into yield strategies and attempted to manage allocations across those strategies.

This design promised convenience. Users could deposit stablecoins into a pool and let Belt allocate capital across yield sources. In a healthy system, vault shares should represent a proportional claim on underlying assets plus accrued yield. If a user deposits BUSD, receives vault shares, and later withdraws, the amount returned should reflect their share of real pool value.

The attack showed how difficult that accounting becomes when a vault spans multiple strategies and external liquidity venues. A stablecoin vault is not automatically simple just because the assets are meant to trade near $1. It still needs to value strategy positions, track imbalances, handle deposits and withdrawals, and resist atomic manipulation.

## The attacker's high-level strategy

Rekt published a concise step-by-step reconstruction of the exploit. The attacker used eight flash loans totaling approximately 385 million BUSD from PancakeSwap. In the first transaction, the attacker deposited 10 million BUSD into the bEllipsisBUSD strategy when it was the most undersubscribed strategy. Then the attacker deposited 187 million BUSD into the bVenusBUSD strategy, which was also treated as the most undersubscribed strategy.

The attacker then swapped 190 million BUSD into 169 million USDT through Ellipsis, withdrew more BUSD from the bVenusBUSD strategy when it became the most oversubscribed strategy, swapped 169 million USDT back into 189 million BUSD, and deposited BUSD back into bVenusBUSD. Rekt said the swap, withdraw, swap-back, and deposit loop was repeated seven times before the flash loans were repaid and profit withdrawn.

This flow matters because it attacked the vault's balancing assumptions. Belt's routing logic used relative strategy subscription levels to decide where new deposits and withdrawals should go. The attacker used huge temporary balances to push the system between states, causing withdrawals and share valuations to reflect distorted conditions.

The attack was not "stablecoin depegging" in the ordinary sense. The assets mostly remained stablecoins. The exploitable movement was inside the protocol's accounting and strategy allocation, amplified by large Ellipsis swaps and flash-loan capital.

## Incorrect share valuation

The phrase "incorrect share valuation" captures the core market failure. A vault share should price the user's claim on the underlying portfolio. If that price can be made inaccurate during one transaction, a flash-loan attacker can mint or redeem shares at favorable values and extract the difference.

In Belt's case, public summaries describe a strategy imbalance problem. The protocol assumed its strategy accounting could safely use current strategy states to value deposits and withdrawals. The attacker created extreme temporary imbalance:

- one strategy appeared undersubscribed and received a huge deposit,
- a large stablecoin swap changed external pool conditions,
- a strategy then appeared oversubscribed and became the withdrawal source,
- the attacker withdrew at an inflated or incorrect valuation,
- the loop repeated.

This is similar to other DeFi incidents where the accounting layer relied on a value that could be moved inside the same block. If share value, virtual price, pool balance, or strategy allocation can be manipulated by a single atomic sequence, then a vault can pay out more than it owns.

The fact that the exploit was repeated eight times shows the bug was not a one-off rounding edge case. The attacker could industrialize the sequence until the team halted the affected flows or the profit opportunity ended.

## Flash loans as amplifier, not root cause

Flash loans are often described as the "attack," but in incidents like Belt they are better understood as an amplifier. The root cause was that Belt's accounting and strategy routing did not remain safe under very large, atomic balance changes. Flash loans supplied the capital to create those changes without requiring the attacker to already own hundreds of millions of BUSD.

Decrypt explained that a flash loan lets a borrower take uncollateralized capital and repay it within one transaction; if repayment fails, the transaction reverts. This makes flash loans useful for attackers because they can borrow, manipulate a vulnerable protocol, extract profit, repay, and keep the remainder in seconds.

The Belt attacker used PancakeSwap to access enormous BUSD liquidity. Rekt put the flash-loan size at roughly 385 million BUSD. Decrypt reported that the attacker's smart contract executed the exploit eight times before developers became aware of the incident and halted withdrawals and deposits.

The lesson is not that protocols should simply "block flash loans." That is usually impractical. The lesson is that every accounting formula should be tested as if an attacker can temporarily control very large balances. In DeFi, they can.

## Why stablecoin users were still exposed

Stablecoin vaults can create a false sense of safety. Users may think their main risk is stablecoin depeg or protocol APY variation. Belt showed another risk: internal accounting loss.

The underlying assets were familiar stablecoins. The product was optimized for stablecoin transfers and yield. But the user-facing loss was still large. Decrypt reported beltBUSD vault users lost 21.36% of funds and 4Belt pool users lost 5.51%. These are severe losses for users who likely chose a stablecoin product to avoid volatile-token drawdowns.

The incident therefore belongs in market-health analysis because it undermined a key DeFi promise: that stablecoin yield aggregators provide relatively conservative exposure. The assets may be stable, but the strategy stack can be fragile.

## Timeline

**May 29, 2021:** The attacker initiated the flash-loan exploit against BSC's 4Belt pool. Belt later said the smart contract used PancakeSwap flash loans and exploited beltBUSD and its underlying strategy protocols.

**Attack execution:** The attacker ran the contract eight times. Rekt described deposits into bEllipsisBUSD and bVenusBUSD, repeated BUSD/USDT swaps through Ellipsis, withdrawals from bVenusBUSD, and repayment of flash loans.

**Detection and response:** Decrypt reported that the attack lasted about ten minutes before Belt developers became aware, halted withdrawals and deposits, and patched the vulnerability. CryptoSlate reported deposits and withdrawals from affected pools were suspended for 48 hours.

**Public postmortem:** Belt published an incident report and apologized for the delay, saying it wanted to make things right. CryptoSlate and CryptoNews.net quoted the report's 6,234,753 BUSD profit figure.

**Compensation planning:** Belt said it was creating a compensation plan and expected to publish details shortly after the incident. The team also reassured users that it had not sold its own tokens and said BSC ecosystem attacks were becoming a broader concern.

## BSC exploit season context

The Belt exploit happened during a cluster of Binance Smart Chain incidents. Decrypt noted that PancakeBunny had recently lost $45 million in a flash-loan attack, BurgerSwap had lost $7.2 million, and other BSC projects including Uranium Finance, bEarn, Spartan Protocol, Autoshark, and Merlin Labs had suffered exploits.

Rekt described the period as BSC's "flash loan exploit season." This context matters because Belt was not an isolated failure. It reflected a pattern: fast-growing BSC protocols forked or adapted complex DeFi designs, accumulated substantial total value locked, and then encountered attacks that stress-tested their accounting under conditions audits or developers had not fully modeled.

The market-health damage extended beyond Belt. Every new BSC exploit made users question whether high APYs were compensation for hidden implementation risk. It also pressured the ecosystem to improve monitoring, incident response, and audit standards.

## Similarity to Harvest Finance

Rekt explicitly compared Belt to the Harvest Finance exploit. Both incidents involved stablecoin or yield strategy accounting and large capital moving through external pools. In Harvest, the attacker manipulated Curve pool pricing and vault share accounting to withdraw more than their fair share. In Belt, the attacker used PancakeSwap flash loans and Ellipsis swaps to manipulate strategy allocation and share valuation.

The common theme is accounting that trusts a manipulable state:

- Harvest trusted pool conditions that could be moved atomically.
- Belt trusted strategy balance/valuation states that could be moved atomically.

The fix is not merely adding one check. Protocols need a design philosophy: vault shares should not be priced from values that can be cheaply manipulated within the same transaction, especially when withdrawals can immediately realize the manipulated price.

## Controls that would have reduced risk

### Manipulation-resistant share pricing

Vault share prices should avoid using instantly manipulable balances as the sole source of truth. If strategies depend on external pool states, protocols should use delayed accounting, conservative valuation, time-weighted measures, or withdrawal limits during imbalance.

### Strategy imbalance limits

If a strategy becomes suddenly under- or over-subscribed by hundreds of millions of dollars, the vault should not continue normal routing. Extreme changes should trigger circuit breakers, delayed settlement, or manual review.

### Withdrawal source constraints

Routing withdrawals from the most oversubscribed strategy can be useful for balancing, but it can also be gamed. Withdrawal routing should be resistant to attacker-created subscription states and should not let one transaction force the protocol to pay from a manipulated source.

### Flash-loan-scale testing

Tests should model attackers with access to hundreds of millions of temporary stablecoins. Unit tests with small deposits will not reveal failures that depend on strategy dominance or large pool imbalance.

### External protocol dependency review

Belt's exploit involved PancakeSwap for flash loans and Ellipsis for swaps. A vault using external liquidity venues should model how large swaps in those venues affect its own accounting. Composability means external state is part of the threat model.

### Real-time anomaly detection

Eight repeated exploit executions over about ten minutes gave some window for automated monitoring. Alerts on massive flash-loan deposits, repeated strategy flips, large BUSD/USDT loops, or abnormal vault share changes might have reduced the number of successful repetitions.

## User-side lessons

For users, the main lesson is that stablecoin APY products are not equivalent to holding stablecoins. A stablecoin vault adds smart-contract risk, strategy risk, external protocol risk, and accounting risk.

Before depositing into a stablecoin optimizer, users should ask:

1. How are vault shares priced?
2. Can share price be manipulated within one block?
3. Which external protocols are used for yield and swaps?
4. Are deposits and withdrawals routed through different strategies?
5. Are there caps on strategy imbalance?
6. Does the protocol have live monitoring and emergency pause authority?
7. What compensation plan exists if accounting fails?

High APY often means the protocol is doing more than passive holding. More moving parts mean more ways for an attacker to turn stable assets into unstable outcomes.

## Conclusion

Belt Finance's May 2021 exploit drained 6,234,753 BUSD from its BSC stablecoin infrastructure by combining PancakeSwap flash loans, Ellipsis swaps, and repeated manipulation of beltBUSD strategy accounting. The root cause was incorrect share valuation under extreme strategy imbalance. Users of beltBUSD and 4Belt suffered meaningful losses even though they were participating in a stablecoin-focused product.

The incident remains relevant because many DeFi products still rely on strategy allocation and vault share accounting. If that accounting assumes calm markets, balanced strategies, or limited capital, it will fail in an adversarial environment where attackers can borrow hundreds of millions for one transaction. Stablecoin vaults need manipulation-resistant accounting, not just stable assets.

## References

- Rekt, "Belt Finance" — https://rekt.news/belt-rekt/
- Decrypt, "Belt Finance Exploited for $6.2 Million in Flash Loan Attack" — https://decrypt.co/72358/belt-finance-exploited-6-2-million-flash-loan-attack
- CryptoSlate, "Flash loan attack on DeFi platform Belt Finance sees $6.2 million gone" — https://cryptoslate.com/flash-loan-attack-on-defi-platform-belt-finance-sees-6-2-million-gone/
- CryptoNews.net, "Flash loan attack on DeFi platform Belt Finance sees $6.2 million gone" — https://cryptonews.net/news/defi/731519/
- Vidma, "The Belt Finance Exploit: A $6.3M Flash Loan Attack on BSC" — https://www.vidma.io/blog/the-belt-finance-exploit-a-6-3m-flash-loan-attack-on-bsc
