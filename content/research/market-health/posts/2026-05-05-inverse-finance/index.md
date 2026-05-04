---
date: 2026-05-05
entities:
  - id: inverse-finance
    name: Inverse Finance
    type: defi
  - id: anchor
    name: Inverse Finance Anchor
    type: defi
  - id: inv
    name: INV
    type: token
  - id: dola
    name: DOLA
    type: stablecoin
title: "Inverse Finance oracle manipulation, INV collateral inflation, and the $15.6 M Anchor bad-debt event"
---

## 1. Introduction and incident overview

On 2 April 2022, Inverse Finance's Anchor lending market was exploited for approximately $15.6 million after an attacker manipulated the on-chain price of INV, deposited the inflated INV as collateral, and borrowed real assets against a valuation that the market could not support. Public reporting from Rekt lists the extracted assets as 1,588 ETH, 94 WBTC, 4 million DOLA, and 39.3 YFI. The key mechanism was not a private-key compromise or a direct smart-contract transfer bug. It was a market-structure failure: a thin INV-WETH liquidity pool on SushiSwap became the input for a time-weighted-average-price oracle used by Inverse's lending market, and an MEV-aware attacker held that price high long enough for the protocol to accept overvalued collateral.

The attack was unusually sophisticated because it combined capital sourcing, address preparation, pool manipulation, oracle update timing, transaction spam, and borrowing in a coordinated sequence. Rekt reported that the exploiter withdrew 901 ETH from Tornado Cash, distributed 1.5 ETH across 241 clean addresses via Disperse, deployed several contracts, swapped 500 ETH into roughly 1,700 INV through the INV-WETH SushiSwap pair, and then used the manipulated price to borrow permanently from Inverse Finance. Flash-loan oracle attacks are often single-transaction events. The Inverse event was more deliberate: the attacker manipulated a thin market, defended the manipulated oracle state against arbitrage and generalized frontrunners, and then converted an inflated collateral mark into protocol bad debt.

The exploit matters for market-health analysis because it shows how a low-liquidity governance token can become a dangerous collateral asset when a lending market accepts it at oracle prices that are too easy to move. The protocol did not need to lose control of contracts. The market simply believed the wrong price for long enough to lend out scarce assets. Once the borrowed ETH, WBTC, YFI, and DOLA left the system, the remaining INV collateral no longer covered the debt.

## 2. Background: Inverse Finance, Anchor, INV, and DOLA

### 2.1 Inverse Finance and DOLA

Inverse Finance is a decentralized finance protocol associated with DOLA, a debt-backed stablecoin. In a lending-market model, users can deposit collateral and borrow other assets. If the collateral value falls too far relative to debt, liquidations should restore solvency by selling collateral before the loan becomes undercollateralized.

That mechanism depends on reliable collateral prices. If a protocol overvalues collateral at the moment of borrowing, it can issue loans that are already economically insolvent. Liquidation after the fact cannot fully repair the loss if the true market value of the collateral is far below the borrowed value.

DOLA adds an additional market-health dimension. A stablecoin issuer's solvency depends on the quality of backing assets and the collectability of debt. If a lending market creates uncollectable debt, the stablecoin's credibility can be affected even if the immediate exploit also drains non-stablecoin assets.

### 2.2 Anchor as the affected money market

Anchor was Inverse Finance's lending market. Users supplied collateral and borrowed assets from the protocol. In April 2022, INV itself was accepted as collateral. That created a reflexive risk: the protocol's own governance token became a credit instrument. If its price could be temporarily inflated, the protocol could be made to lend out real assets against a collateral base that would not survive normal market pricing.

Governance-token collateral is especially sensitive because:

1. liquidity is often shallow compared with blue-chip assets;
2. token supply may be concentrated among protocol-aligned holders;
3. spot markets can move sharply under concentrated trades;
4. lending protocols may set loan-to-value parameters based on assumed liquidity rather than stress-tested exit liquidity; and
5. price feeds may be built before a mature, independent oracle market exists.

The Inverse exploit hit that exact weakness: a thin traded token was accepted as collateral, and its oracle could be moved by an attacker with enough capital and transaction-control awareness.

### 2.3 INV-WETH SushiSwap liquidity as an oracle input

The vulnerable price path used the INV-WETH pair on SushiSwap. In general, a DEX-based TWAP oracle reads a pair's cumulative price over time and computes an average over a window. TWAPs are safer than using a single spot quote, but they are not automatically safe. Their manipulation resistance depends on:

- depth of the underlying pool;
- length of the averaging window;
- frequency and timing of updates;
- whether the oracle uses multiple independent markets;
- whether the lending protocol caps sudden price changes; and
- whether arbitrage can restore the pool before the oracle value is used.

In this incident, the INV-WETH market was thin enough that a 500 ETH swap could move the INV price dramatically. Rekt described the manipulation as changing the price by roughly 50x. That price then flowed through the Keeper/Keep3r oracle path into Inverse's collateral valuation.

## 3. Vulnerability: thin-pool TWAP as a high-value collateral oracle

### 3.1 TWAPs reduce but do not eliminate manipulation risk

A time-weighted average price smooths short-lived price spikes, but a TWAP based on a single low-liquidity pair can still be manipulated if the attacker can hold or repeatedly refresh the manipulated price through the relevant sampling window. The cost of manipulation is not the nominal value borrowed. It is the capital required to move and defend the reference pool long enough for the oracle to record the distorted price.

That cost was economically viable in Inverse's case because the prize was the protocol's borrowable liquidity: ETH, WBTC, YFI, and DOLA. A $15.6 million extraction justified significant spending on price movement, gas, contract deployment, address preparation, and transaction-ordering competition.

### 3.2 Single-source price dependency

The attack's most important structural weakness was dependence on a single thin DEX market. A robust collateral oracle for a volatile governance token should not treat one AMM pair as sufficient truth for a lending market that can issue millions in debt. If the token has no deep, independent, manipulation-resistant price sources, the safer conclusion is not "use a weaker oracle." It is "do not accept the asset as high-LTV collateral."

Single-source oracle dependency creates a direct path from AMM reserves to lending solvency:

1. the attacker moves the AMM price;
2. the oracle observes the moved price;
3. the lending market values collateral at the moved price;
4. the attacker borrows against the moved price;
5. the AMM price normalizes; and
6. the lending market is left with debt backed by collateral worth far less than recorded.

The protocol's accounting may remain internally consistent while its economic assumptions fail.

### 3.3 No sufficient circuit breaker on sudden collateral repricing

A lending market that accepts volatile collateral should treat sudden price appreciation with suspicion. If a collateral token rises 50x in the oracle path without corresponding deep-market confirmation, the safest behavior is to freeze new borrowing, cap the effective price, or require a long delay before the higher valuation can support debt.

In the Inverse event, the attack path succeeded because the manipulated INV price became usable collateral quickly enough for the attacker to borrow before the market could normalize. A circuit breaker could have rejected or damped the new price until multiple independent sources confirmed it.

### 3.4 MEV-aware attack execution

The exploit also demonstrated that oracle security cannot ignore MEV. Rekt quoted Flashbots researcher Bert Miller describing it as one of the most MEV-aware hacks he had seen, noting that the attacker held an oracle price at an extreme level across multiple blocks, prevented arbitrage bots from bringing prices back in line, and protected against generalized frontrunners.

That detail matters because many oracle-risk models assume arbitrage will quickly correct manipulated AMM prices. In a competitive block-building environment, attackers can use gas pricing, private transactions, address splitting, spam, and contract design to shape who gets into the next blocks. If the protocol only needs a few manipulated observations, the attacker does not need to defeat arbitrage forever. They only need to control the window that matters.

## 4. Attack flow

### 4.1 Funding and address preparation

Public analysis reported that the exploiter withdrew 901 ETH from Tornado Cash before the attack. They then sent 1.5 ETH to 241 clean addresses through Disperse. This preparation served several purposes:

- separating operational addresses from the funding origin;
- enabling distributed transaction submission;
- making mempool and block-inclusion behavior harder to interpret;
- creating noise around the real exploit contract; and
- giving the attacker flexibility in transaction ordering.

The attacker also deployed five smart contracts, only one of which was real according to Rekt's summary. Decoy contracts and distributed addresses can make it harder for generalized frontrunners or defenders to identify the critical path before execution.

### 4.2 Manipulating the INV-WETH pool

The attacker swapped 500 ETH into roughly 1,700 INV through the INV-WETH pair on SushiSwap. Because the pool was thin, that trade dramatically increased the apparent INV price. Rekt reports the price impact as roughly 50x.

This step created a distorted market state. The important point is not that the attacker bought INV at a bad price in isolation. That purchase was the cost of manufacturing a collateral mark. If the inflated mark allowed the attacker to borrow much more value than the manipulation cost, the trade was profitable even though the attacker overpaid for INV.

### 4.3 Capturing the manipulated TWAP

At the same time as the pool manipulation, the attacker spammed transactions to ensure their exploit sequence reached the next block before other participants could neutralize the opportunity. The Keeper/Keep3r oracle path used the SushiSwap TWAP and returned an inflated INV price to Inverse Finance.

The oracle therefore did what it was programmed to do: read from its configured source. The failure was that the configured source and update design were not robust enough for a lending market that could issue millions in debt against the result.

### 4.4 Depositing inflated INV collateral

The attacker deposited approximately 1,700 INV into Inverse as collateral. At fair value, Rekt estimated this INV at about $644,000. Under the manipulated oracle price, it was treated as vastly more valuable. That difference between fair value and oracle value became the exploitable credit line.

Collateral deposits are often thought of as safe because they add assets to the protocol. But if the protocol records the collateral at a false price, the deposit becomes a liability trigger. The dangerous action is not the deposit itself; it is the borrow limit created by the deposit.

### 4.5 Borrowing real assets

With the inflated collateral value accepted, the attacker borrowed approximately $15.6 million in assets, including 1,588 ETH, 94 WBTC, 4 million DOLA, and 39.3 YFI. These were real borrowable assets leaving the protocol. Once borrowed, the attacker had no economic reason to repay because the collateral would not cover the debt after INV normalized.

The result was bad debt: the protocol held collateral worth far less than the obligations created by the borrow. In a lending market, bad debt is not just an accounting entry. It represents losses that must be absorbed by reserves, future revenue, token holders, stablecoin backing, or users depending on the protocol's design and recovery plan.

## 5. Market impact

### 5.1 $15.6 million extraction and bad debt

The immediate loss was approximately $15.6 million. The asset mix mattered:

- **ETH and WBTC** were liquid blue-chip assets that could be moved or sold quickly.
- **YFI** was a higher-volatility governance token but still had external liquidity and market value.
- **DOLA** was Inverse's own stablecoin, linking the exploit directly to the protocol's stablecoin credibility.

Bad debt in a lending market changes user expectations. Suppliers and stablecoin holders must ask whether future revenue is sufficient to refill the hole, whether governance will socialize losses, and whether the protocol can prevent repeat incidents.

### 5.2 DOLA credibility risk

DOLA is designed to maintain stable value through the protocol's credit system. If the credit system issues uncollectable debt, the stablecoin's perceived backing weakens. The April exploit did not necessarily mean every DOLA was immediately unbacked, but it introduced a concrete solvency question: who absorbs the deficit created by bad borrowing?

Stablecoin markets are confidence-sensitive. A security incident can become a liquidity incident if holders rush to exit, liquidity providers pull pools, or integrations reduce exposure. Even when the peg survives, the risk premium rises because users must price recovery execution, governance response, and future oracle controls.

### 5.3 Governance-token collateral repricing

The exploit also changed how markets viewed INV as collateral. A governance token can have legitimate utility and market value, but it is not automatically suitable as high-capacity collateral. The ability to manipulate its price with 500 ETH of trading showed that the token's effective liquidation depth was not compatible with the borrowable liquidity it supported.

The broader market lesson is that collateral eligibility should depend on stressed exit liquidity, not market capitalization alone. A token can display a large fully diluted value while still having shallow on-chain liquidity. Lending against such a token creates a mismatch between quoted value and realizable value.

## 6. Why the attack attracted expert attention

The Inverse exploit drew attention because it was not a simple "push price, borrow, dump" transaction. It involved:

1. pre-funded addresses from a mixer;
2. distribution of ETH across many clean addresses;
3. multiple contract deployments;
4. a targeted manipulation of a known oracle source;
5. transaction spam to control block timing;
6. awareness of arbitrage and frontrunning threats; and
7. a borrowing sequence that converted temporary price control into permanent protocol debt.

This sophistication matters for defensive design. Protocols cannot assume attackers are naive, capital-constrained, or unable to understand oracle update mechanics. If a price feed's security relies on arbitrage correcting a pool before the next critical read, then the protocol is implicitly depending on a competitive MEV environment it does not control.

## 7. Controls that would have reduced the loss

### 7.1 Use deeper, independent oracle sources

The strongest mitigation is to avoid using a single thin AMM pair as the sole price source for borrow-limit calculations. A safer oracle can combine:

- Chainlink-style decentralized price feeds where available;
- multiple DEX pools across venues;
- centralized exchange references for liquid assets;
- liquidity-weighted medians;
- stale-price and deviation checks; and
- fallback logic that reduces collateral value rather than increasing it during uncertainty.

If an asset lacks deep independent price sources, the protocol should cap its collateral factor aggressively or exclude it from borrowing entirely.

### 7.2 Longer windows and manipulation-cost analysis

TWAP windows should be selected based on manipulation cost relative to protocol exposure. A short TWAP over a thin pool can be cheaper to manipulate than the amount that can be borrowed. Oracle designers should ask:

1. How much capital is required to move the price by 2x, 5x, or 50x?
2. How long must the price be held to affect the oracle?
3. What borrow limit can the resulting price unlock?
4. Can an attacker recover part of the manipulation cost?
5. Can transaction ordering prevent arbitrage during the window?

If the maximum borrowable value exceeds the cost of manipulation by a large margin, the oracle is unsafe for lending.

### 7.3 Borrow caps and isolation mode

Even if INV remained eligible as collateral, the protocol could have limited damage through per-asset borrow caps or isolation mode. An isolated collateral asset can only support borrowing of limited assets or limited amounts. That prevents a low-liquidity token from draining the entire market.

Borrow caps should be based on real exit liquidity and oracle robustness. For governance tokens, caps may need to be far lower than headline market capitalization suggests.

### 7.4 Price-change circuit breakers

If a collateral price rises too quickly, the protocol can delay using the higher value for new borrowing while still allowing liquidations or withdrawals under conservative assumptions. A circuit breaker could have detected the 50x INV move and frozen borrowing against the new price until a governance or oracle review completed.

Useful circuit-breaker rules include:

- maximum accepted price increase per hour;
- maximum accepted deviation between DEX and external feeds;
- automatic collateral-factor reduction after abnormal volatility;
- temporary borrow disablement after oracle source liquidity drops; and
- mandatory review when token price moves without corresponding volume across independent markets.

The goal is asymmetric caution: price increases that expand borrowing power should be harder to accept than price decreases that protect lenders.

### 7.5 MEV-aware oracle design

Oracle designers must assume attackers can influence block ordering. Mitigations include:

- longer averaging windows;
- delayed activation of higher prices;
- multi-block commit/reveal updates where appropriate;
- protected oracle update transactions;
- monitoring for transaction spam around oracle reads; and
- avoiding dependency on arbitrage to correct prices within a short window.

The Inverse incident shows that "arbitrage will fix it" is not a complete security model. Arbitrage is a market process, not a protocol guarantee.

## 8. Market-health indicators

### 8.1 Collateral liquidity versus borrowable liquidity

A simple monitoring metric is the ratio between borrowable value enabled by an asset and the cost to manipulate that asset's oracle source. If a 500 ETH trade can move a token's oracle price enough to unlock millions in borrowing, the market is unhealthy. Analysts should compare:

- total borrowable liquidity;
- asset collateral factor;
- DEX pool depth;
- price impact for large trades;
- oracle window length; and
- historical volatility.

When borrowable liquidity greatly exceeds manipulation cost, the protocol is subsidizing attackers.

### 8.2 Sudden collateral-price expansion

The attack required a dramatic INV price increase. Monitoring systems should alert when an accepted collateral asset experiences extreme price appreciation in the exact pool used by an oracle, especially if the move is not reflected across deeper markets. The alert should be tied to protocol action: pause new borrowing, reduce collateral factor, or route to governance emergency review.

### 8.3 Address and transaction-pattern signals

The attack's preparation created observable patterns:

- mixer-sourced funding;
- dispersion of ETH to many addresses;
- multiple contract deployments shortly before exploit execution;
- large trade through a thin oracle pair;
- mempool spam near oracle update timing; and
- immediate borrow of multiple assets after collateral deposit.

No single signal proves an exploit, but the combination should raise the risk score. Protocols can monitor for this pattern and preemptively disable borrowing if an oracle pair is being manipulated.

### 8.4 Stablecoin exposure to lending-market bad debt

For stablecoin protocols, market-health monitoring should connect lending-market incidents to stablecoin backing. If a protocol-issued stablecoin like DOLA is borrowed during an exploit, analysts should track:

- amount of stablecoin borrowed by the attacker;
- reserves or surplus available to absorb bad debt;
- governance-approved repayment plans;
- liquidity pool depth after the incident;
- peg deviations; and
- whether integrations maintain or reduce exposure.

Stablecoin solvency is not only about current peg price. It is also about confidence that the backing system can absorb losses.

## 9. Broader implications

### 9.1 Governance tokens are dangerous collateral without deep liquidity

The Inverse exploit is a case study in why protocol-native tokens require special caution as collateral. They may be valuable to the community, but they are also correlated with protocol risk. When the protocol is attacked, the governance token can fall, making it a poor backstop for protocol debt. If the same token's price is also manipulable, it can create bad debt before the market even reacts.

This is a double weakness:

1. the token can be overvalued by an oracle before borrowing; and
2. the token can lose market confidence after the exploit, reducing recovery value.

Collateral frameworks should penalize this reflexivity.

### 9.2 Oracle risk is market risk

Oracles are often treated as infrastructure, but in lending they are market-risk engines. A protocol's solvency can be destroyed by a price that is technically valid under the oracle's rules but economically invalid under real liquidity conditions. The distinction between "oracle worked as coded" and "oracle was safe" is critical.

Market-health research should therefore treat oracle configuration as part of the market's balance sheet. The question is not only where the price comes from. It is whether that price can support the amount of credit the protocol extends.

### 9.3 MEV changes the threat model

The attacker's ability to control a multi-block window shows why protocols must design around adversarial block ordering. Public mempools, private relays, searchers, builders, and gas auctions all affect whether a manipulated price can be maintained long enough to matter. Oracle designs that were marginally safe under simple arbitrage assumptions may fail under MEV-aware execution.

Defenses must be robust even when attackers can pay for priority, use private order flow, and confuse generalized frontrunners.

## 10. Timeline

- **Before 2 April 2022**: Inverse Finance Anchor accepts INV as collateral and uses an oracle path drawing from the INV-WETH SushiSwap market through Keeper/Keep3r TWAP infrastructure.
- **Pre-attack preparation**: The attacker withdraws 901 ETH from Tornado Cash, distributes 1.5 ETH across 241 clean addresses using Disperse, and deploys multiple smart contracts.
- **Price manipulation**: The attacker swaps 500 ETH into roughly 1,700 INV through the thin INV-WETH SushiSwap pair, raising the apparent INV price dramatically.
- **Oracle capture**: Transaction spam and MEV-aware execution help ensure the manipulated price is reflected in the next relevant oracle update before arbitrage can fully restore the pool.
- **Collateral deposit and borrowing**: The attacker deposits the inflated INV as collateral and borrows 1,588 ETH, 94 WBTC, 4 million DOLA, and 39.3 YFI.
- **Aftermath**: Inverse Finance acknowledges the exploit, lending-market operations are restricted, and the protocol faces bad debt and oracle-hardening requirements.

## 11. Lessons for market participants

For users, the lesson is that lending-market collateral lists matter as much as headline APYs. If a protocol accepts thinly traded governance tokens as collateral, users supplying assets to that market are implicitly exposed to oracle manipulation risk. The risk can materialize even when the smart contracts are not directly drained by an admin or key compromise.

For builders, the lesson is that TWAPs are not magic. They are only as strong as their source liquidity, update design, and manipulation-cost assumptions. Lending markets should use conservative collateral factors, independent price sources, borrow caps, and circuit breakers, especially for native governance tokens.

For analysts, the Inverse Finance exploit provides a repeatable monitoring model: compare oracle-source liquidity to borrowable liquidity, watch for sudden collateral-price appreciation in oracle pools, flag mixer-funded address dispersion and contract deployment before oracle updates, and track stablecoin backing after bad-debt events.

The $15.6 million Inverse Finance event was therefore not only an oracle exploit. It was a failure to align credit capacity with real market liquidity. The protocol treated a manipulable price as a lending truth, and the attacker converted that temporary truth into permanent bad debt.

## References

- Rekt, [Inverse Finance - Rekt](https://rekt.news/inverse-finance-rekt/)
- Inverse Finance, [official exploit acknowledgement](https://twitter.com/InverseFinance/status/1510282040809299972)
- PeckShield, [Inverse Finance exploit analysis](https://twitter.com/peckshield/status/1510232640338608131)
- PeckShield, [asset-flow visualization](https://twitter.com/peckshield/status/1510235343160676359)
- ChainlinkGod, [TWAP oracle risk comment cited during incident response](https://twitter.com/ChainLinkGod/status/1510298134202572800)
- Solidity and DeFi security practice, [OpenZeppelin oracle and lending-market risk references](https://blog.openzeppelin.com/)
