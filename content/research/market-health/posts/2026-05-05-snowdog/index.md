---
title: "Snowdog's Avalanche buyback collapse: hidden AMM design, privileged timing, and a 90% SDOG crash"
date: "2026-05-05"
description: "Snowdog's November 2021 buyback event on Avalanche showed how an opaque custom AMM and under-disclosed sellability constraints can convert a promised treasury buyback into a liquidity extraction event for the first addresses through the door."
entities:
  - Snowdog
  - Snowbank
  - SDOG
  - MIM
  - Avalanche
  - Trader Joe
---

## Summary

Snowdog was an Avalanche-based "decentralized reserve meme coin" launched by the Snowbank team during the 2021 wave of OlympusDAO forks. The project advertised an eight-day accumulation phase followed by a treasury-funded buyback. Users could acquire SDOG through minting, staking, or market purchases, then compete to sell into a large Magic Internet Money treasury. By the end of the short campaign, public reports put the buyback treasury around $44 million.

The buyback did not behave like a broad redemption event for holders. The Snowdog team moved liquidity away from Trader Joe and into a custom AMM built specifically for the buyback. The front end was password-protected until the event began, and the contract included a challenge mechanism intended to block bots. When liquidity was added, the new pool's ratio implied a massive SDOG price jump, with Rekt reporting a new price around $70,000 compared with a pre-buyback market price near $1,350. The first few transactions captured a large share of the treasury, while most holders were left selling below the pre-buyback market price or holding through a collapse.

Rekt reported that the first two transactions sold 403 SDOG for roughly $18 million in MIM, even though that SDOG would have been worth about $500,000 at pre-buyback prices. CryptoNews Australia reported that three wallets drained roughly $10 million, $7.7 million, and $3.3 million respectively using similar timing and strategy. CryptoBriefing reported that SDOG fell more than 90% after the buyback and that the team later said only the first 7% of supply sold could receive an above-market price. Many community members called the incident a rug pull. The team described it as a failed game-theory experiment.

This article treats the Snowdog collapse as a market-health incident rather than trying to prove criminal intent. The mechanics are enough: opaque execution rules, a custom AMM, privileged timing, hidden or poorly communicated constraints, and a treasury-backed price event created conditions where a tiny number of early sellers captured the value while ordinary holders absorbed the crash.

## What Snowdog promised

Snowdog's pitch combined several narratives that were powerful in late 2021:

- OlympusDAO-style reserve currency mechanics,
- meme-coin speculation,
- Avalanche ecosystem growth,
- protocol-owned liquidity,
- and a short, theatrical buyback event.

According to Rekt, Snowdog ran an eight-day accumulation phase where users could stock up on SDOG through minting, staking, or market buying. After that phase, the project planned to use treasury funds to buy back SDOG, burn proceeds, reduce staking rewards, and renounce contract ownership. The stated ambition was to turn SDOG into a meme currency of Avalanche.

The buyback framing was crucial. A treasury-funded buyback can create an expectation that holders will have a path to exit into deep project-owned liquidity. That expectation changes market behavior before the event. Users may mint more, buy more, or hold longer because they expect the treasury to become a buyer.

CryptoBriefing reported that many holders accumulated SDOG in anticipation of a substantial price increase. CryptoNews Australia wrote that the treasury's market value had grown to $44 million in eight days, letting holders compete for a portion of those funds during the buyback. The event therefore became the focal point of the entire project.

The risk was that the buyback was not a simple, transparent market operation. Its success depended on rules controlled by the team: where liquidity would be placed, how swaps would work, who could access the interface, what timing information was available, and how much supply could actually be sold above market.

## The custom AMM decision

Before the buyback, SDOG traded on Trader Joe, a major Avalanche decentralized exchange. Rekt reported that SDOG had been trading near $1,350 before the event. Instead of executing the buyback on Trader Joe, Snowdog decided to create a new AMM with an SDOG-MIM pool solely for the buyback.

The team justified the custom AMM as a defense against bots and MEV searchers. Rekt quoted the team explaining that they added a mathematical challenge to the AMM, making it nearly impossible for bots to quickly adapt and understand how the swap worked, so only users using the front end could swap. The front end was password-protected until the buyback went live.

On paper, bot protection can be a legitimate concern. A public buyback with large treasury funds is an obvious target for snipers, MEV, and automated execution. But the Snowdog implementation replaced one risk with another. A custom, opaque AMM narrowed who understood the execution path. If a small group had earlier access to the contract, challenge key, or exact pool mechanics, they would have an enormous timing advantage.

The new AMM also changed price formation. Rekt reported that once liquidity migrated from Trader Joe and was added to the custom pool, the pooled ratios created an implied SDOG price around $70,000. That price was not an organic market consensus. It was a mechanical result of the new pool setup. Whoever could sell first into that pool could monetize the artificial price before it collapsed.

## What happened in the first minutes

The earliest buyback transactions determined the outcome. Rekt reported that the first two transactions captured around 40% of the spoils:

- one address sold 187.8 SDOG for 10.4 million MIM, implying a price around $55,000 per SDOG,
- a second address sold 215.1 SDOG for 7.7 million MIM, implying a price around $36,000 per SDOG.

Together, those two addresses sold 403 SDOG for about $18 million. At pre-buyback prices, the same SDOG would have been worth roughly $500,000. Rekt noted that both addresses were new and had been funded via FTX the day before. It also reported that the accounts did not appear to have prepared Trader Joe approvals but approved the custom pool as soon as it was published, which fueled suspicion that they knew the buyback would happen on a new DEX.

CryptoNews Australia reported a similar pattern in broader terms. It said a single address made almost $10 million, removing about a quarter of the treasury's buyback power, and that two other wallets drained $7.7 million and $3.3 million using the same strategy. It also reported that the first wallet bought around $180,000 worth of SDOG with MIM before the buyback in $10,000 batches and later extracted more than $10 million worth of MIM.

CryptoBriefing reported the user-facing result: SDOG plummeted more than 90% after the buyback began. The team's postmortem said that for SDOG to stay above the pre-buyback market price of around $1,200, sellers needed their SDOG to be part of the first 7% of supply sold. Once that early slice passed, many holders had to sell below market or face further losses.

## The 7% constraint

The 7% supply constraint is central to the incident. A buyback marketed as a major treasury event can be interpreted by holders as broad support for price. But if only the first 7% of supply sold can receive above-market prices, then the event is closer to a race than a redemption.

CryptoBriefing quoted Snowdog's postmortem: "For the $SDOG price to be above market price before buyback (~$1200), sellers needed their $SDOG to be part of the first 7% of the supply being sold." CryptoNews Australia reported that developers failed to clarify that only 7% of the SDOG supply was eligible to be sold above market before the buyback.

That disclosure problem matters even if every line of code behaved as written. Market participants price events based on what they understand. If users believed a $44 million treasury buyback would broadly support SDOG, but the mechanics only favored the first few sellers, then the market was operating on incomplete information.

The result was predictable once the constraint was visible. Early sellers drained high-priced MIM liquidity. Later sellers faced a lower price and worsening panic. Holders who could not access or understand the custom AMM quickly were left with falling SDOG and little practical chance to realize the advertised benefit.

## Rug pull or failed experiment?

Many community members described Snowdog as a rug pull. The Snowdog/Snowbank team framed it as a failed experiment and an entertainment-oriented game-theory event. This article does not need to prove intent to classify the market-health failure.

The objective facts are sufficient:

- the team created a short-lived speculative token with a scheduled buyback,
- the treasury grew to tens of millions of dollars,
- liquidity moved from a known DEX to a custom buyback AMM,
- the front end was hidden until launch,
- the AMM included a challenge mechanism,
- early sellers captured a disproportionate share of MIM,
- the wider holder base experienced a price collapse,
- the most important sellability constraint was not clearly understood by the market.

Rekt asked whether the event was a "game theory experiment" or a new breed of rug pull. That framing is appropriate. The incident sits in the gray area where a project can claim rules were known or technically available while ordinary participants were economically disadvantaged by opacity and timing.

For market-health purposes, the safest wording is "gamed buyback" or "suspected rug-pull-like collapse." The evidence strongly supports that the structure favored a few early sellers. Public reports also show suspicion of inside information. But unless identities and intent are proven, the core lesson should focus on mechanism, not accusation.

## Market-health impact

The direct holder impact was severe. CryptoBriefing reported a more than 90% SDOG crash. CryptoNews Australia reported up to $30 million in investments lost, while web-search summaries and some secondary coverage cite losses around $30 million to $40 million. Rekt reported that two early transactions alone extracted approximately $18 million in MIM.

The collapse also affected Snowbank, the related OlympusDAO fork whose team launched Snowdog. Rekt wrote that Snowdog's failed experiment affected Snowbank's token price and described the result as "two projects rekt by the same team." That spillover is important because launch experiments are often used to market parent protocols. When an experiment fails, reputational damage can feed back into the original project.

The incident also damaged trust in Avalanche DeFi. Rekt called Snowdog the first incident it had investigated on Avalanche. Avalanche itself and MIM were not responsible for the custom AMM design, but users often associate ecosystem incidents with the chain and liquidity venues where they occur.

The broader market-health harm came from the precedent:

- treasury buybacks can be gamified in ways that punish ordinary holders,
- bot-protection language can mask asymmetric access,
- custom AMMs can hide economically critical rules,
- short-lived OHM forks can accumulate large treasuries before controls are tested,
- "game theory" branding can be used to normalize extreme participant risk.

## Why the custom AMM increased asymmetry

Using a standard DEX does not eliminate MEV or sniping, but it gives the market a familiar execution model. Traders can inspect pools, simulate swaps, use existing routers, and understand approval flow. Moving to a custom AMM changes the information landscape.

In Snowdog's case, Rekt identified three asymmetry points.

First, the front end was password-protected until the event began. That limited public testing and simulation.

Second, the contract used a challenge key or mathematical challenge. The team said this was anti-bot logic. Critics argued that anyone with privileged knowledge of the mechanism would have an advantage.

Third, the buyback pool's initial ratio created a huge artificial price. Early sellers needed not only SDOG but also the ability to interact quickly with the exact custom pool.

The first transactions' profitability suggests that speed and knowledge were decisive. A fair treasury buyback should minimize information asymmetry. Snowdog's structure amplified it.

## Liquidity migration risk

Snowdog also demonstrates the danger of liquidity migration around major events. If a token trades on a public DEX and then liquidity is migrated to a custom pool for a one-time event, the pricing environment changes completely. Holders who understand the old market may not understand the new one.

Liquidity migration can be legitimate when projects upgrade pools or move to better venues. But it becomes dangerous when:

- migration happens immediately before a major treasury event,
- the new pool is custom and unaudited by the public,
- access rules are hidden,
- initial pool ratios create extreme prices,
- and the project has not clearly explained who can profit and in what order.

Snowdog included all of these risk factors. The custom AMM was not merely a different trading venue. It was the mechanism through which the treasury would be distributed. That made its design the core financial instrument of the buyback.

## Disclosure failures

The team later apologized for failing to clearly state how the buyback would likely affect prices. CryptoBriefing's quoted postmortem excerpt is important because it admits that only the first 7% of supply could sell above market. If that condition was not understood before the event, many holders were making decisions under a false impression.

Good disclosure for a buyback event should include:

1. the exact venue,
2. pool addresses,
3. AMM formula,
4. anti-bot mechanism,
5. initial liquidity amounts,
6. expected price curve,
7. maximum profitable sellable supply,
8. whether ordinary holders can interact directly without the front end,
9. timing of liquidity migration,
10. risks of being late.

Snowdog's event turned on precisely those details. A broad claim of a "massive buyback" was not enough. The economically decisive fact was that profitability was limited to the first small slice of sellers.

## Lessons for users

Users evaluating buyback or treasury-backed meme/reserve projects should treat event mechanics as more important than treasury size. A large treasury does not help ordinary holders if the distribution mechanism is a winner-take-most race.

Important warning signs include:

- anonymous team control over event mechanics,
- custom DEX or AMM created only for the event,
- hidden front end or password-protected access,
- anti-bot mechanisms not independently reviewed,
- vague "game theory" explanations,
- unclear sellability limits,
- large treasury paired with tiny profitable exit window,
- liquidity migration immediately before launch,
- no public simulations of price impact.

The Snowdog incident is also a reminder that "anti-bot" features are not automatically pro-user. If anti-bot logic is opaque, it may simply replace public MEV competition with private information advantage.

## Lessons for protocol teams

If a team wants to run a treasury buyback fairly, it should design the event to reduce timing privilege.

Better patterns include:

- pro-rata redemption windows,
- commit-reveal participation,
- Dutch auction mechanisms with published rules,
- time-weighted buybacks on established venues,
- maximum per-wallet sell caps,
- delayed settlement to reduce first-block advantage,
- audited contracts and public dry runs,
- no hidden pool addresses,
- no last-minute custom AMM migration.

The key design goal is that users should know before the event whether they are participating in a pro-rata buyback, an auction, or a speed race. Snowdog's problem was not only that prices crashed. It was that many holders appeared to discover the true race conditions after the race had already been won.

## Conclusion

Snowdog's November 2021 buyback collapse was one of Avalanche DeFi's most visible early market-health failures. A project that promised an eight-day accumulation phase and a large MIM-backed buyback moved liquidity into a custom AMM, hid access until launch, and created a structure where the first few sellers captured a large share of the treasury. SDOG then crashed more than 90%, leaving ordinary holders with losses and a debate over whether the event was a rug pull or a failed experiment.

The safest lesson is not about intent. It is about design. Treasury buybacks must be transparent, independently inspectable, and fair across participants. If the mechanics reward only the first wallets with privileged timing, the buyback is not market support. It is a value-transfer race.

## References

- Rekt, "Snowdog" — https://rekt.news/snowdog-rekt/
- CryptoBriefing, "OlympusDAO Fork Snowdog Hit By 90% Crash" — https://cryptobriefing.com/olympus-dao-fork-snowdog-hit-by-90-crash/
- CryptoNews Australia, "SnowdogDAO Potentially Rugged for $30 Million" — https://cryptonews.com.au/news/snowdogdao-potentially-rugged-for-30-million-92932/
- CryptoNews.net, "Snowdog loses 90%, investors call it a rug pull" — https://cryptonews.net/news/security/2803019/
- Snowdog first early-seller transaction referenced by Rekt — https://snowtrace.io/tx/0x9207a13689617db6f4f88b3f512f2c7dbcfa87205a410556932f2d383cb38277
- Snowdog second early-seller transaction referenced by Rekt — https://snowtrace.io/tx/0x9e189624e41b3927cee86409084af93610af081fb1f46abff3018c1df9b606f6
