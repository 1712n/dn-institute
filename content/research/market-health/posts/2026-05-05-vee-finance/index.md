---
date: 2026-05-05
entities:
  - id: vee-finance
    name: Vee Finance
    type: defi
  - id: avalanche
    name: Avalanche
    type: blockchain
  - id: pangolin
    name: Pangolin
    type: defi
  - id: augustus-swapper
    name: AugustusSwapper
    type: defi
title: "Vee Finance single-source oracle manipulation, leveraged-trading slippage bypass, and the $34 M Avalanche drain"
---

## 1. Introduction and incident overview

On 20 September 2021, Vee Finance, a lending and leveraged-trading protocol on Avalanche, was exploited for roughly $34 million. Public reporting from Rekt placed the stolen assets at about 8,804 WETH and 214 WBTC after the funds were bridged back to Ethereum. The exploit occurred during Avalanche's rapid DeFi expansion, shortly after other ecosystem losses such as Zabu Finance. It became one of the largest early security incidents on Avalanche and demonstrated how quickly borrowed liquidity, DEX price manipulation, and a single-source oracle can convert into protocol insolvency.

The core issue was Vee Finance's use of asset prices from Pangolin liquidity pools as a single source of truth inside leveraged-trading flows. During leveraged trading, the protocol used those pool prices as reference values. The attacker created and manipulated several pairs involving QI, XAVA, LINK.e, WETH.e, and WBTC.e, routed swaps through external swap infrastructure, and exploited how prices and decimals were handled. According to the Rekt summary of Vee Finance's post-mortems, price manipulation plus missing decimal processing allowed transactions to pass slippage checks that normally should have rejected them.

The incident was not a simple "send funds to attacker" bug. It was a market-infrastructure failure. Vee treated manipulable DEX spot prices as reliable collateral/trading references inside a leveraged protocol. The attacker made the market tell Vee the wrong story, then used Vee's own trading and withdrawal logic to extract real WETH and WBTC.

Vee Finance matters for market-health analysis because it captures a common risk pattern from the 2021 multi-chain DeFi boom: protocols expanded to fast, lower-fee chains and shipped lending/leverage features before oracle, slippage, and decimal handling were robust enough for adversarial liquidity. Avalanche's low fees and emerging liquidity made it attractive to users, but also reduced the friction for repeated setup transactions, pair creation, and exploit retries.

## 2. Background: Vee Finance and Avalanche DeFi

### 2.1 Vee Finance's product surface

Vee Finance offered lending and leveraged trading on Avalanche. A lending protocol is already sensitive to price correctness because collateral and debt values determine whether borrowing is safe. A leveraged-trading protocol is even more sensitive because it performs swaps, borrows, and position adjustments based on live market references. If those references can be manipulated, the protocol can approve trades that transfer value away from liquidity providers and lenders.

In a healthy design, a leveraged-trading route should answer several questions conservatively:

1. What is the current price of each asset?
2. Is the price source deep and manipulation-resistant?
3. Are token decimals normalized before comparing values?
4. Does the quoted output satisfy slippage limits after all fees and conversions?
5. Does the route create or use a pool that the attacker can control?
6. Can a single trade or short sequence move the price used by the protocol?

The Vee exploit showed weaknesses in these checks.

### 2.2 Avalanche's early liquidity environment

Avalanche C-Chain was growing quickly in 2021. Capital moved into AMMs, lending markets, and new farms because transaction costs were lower than Ethereum mainnet and incentives were high. That environment created both opportunity and fragility. Many assets were bridged representations such as WETH.e, WBTC.e, LINK.e, and USDT.e. Liquidity was fragmented across venues and newly created pools.

Fragmented liquidity matters for oracle design. If a protocol prices assets from one pool or a small set of pools, an attacker may only need to manipulate those pools rather than the broader market. The correct reference price for WETH or WBTC is not the price in an attacker-created or thin Pangolin pair. It is the market-wide price across deep venues and robust oracles.

### 2.3 Pangolin pool prices as a single source

Rekt's writeup states that during leveraged trading Vee Finance used a single-source price oracle: asset prices in Pangolin pools. DEX pool prices are useful for swaps, but using them directly as trusted reference prices inside a lending/leverage protocol is dangerous. AMM prices are endogenous. They are created by the current reserves in the pool. Anyone who can trade against the pool can move those reserves and therefore move the price.

A robust system can use DEX data as one input, but it should not treat a single live pool as an authoritative valuation source. It should aggregate, time-weight, cap deviations, and reject pools with insufficient depth or attacker-controlled creation history.

## 3. Vulnerability: manipulable spot pricing plus decimal/slippage failures

### 3.1 Single-source oracle risk

The first weakness was reliance on Pangolin pool prices without enough independent validation. The attacker created several swap pairs and used them in the exploit setup:

- QI/WETH.e
- XAVA/WETH.e
- LINK.e/WETH.e
- QI/LINK.e
- XAVA/LINK.e
- XAVA/WBTC.e
- LINK.e/WBTC.e

Creating or using thin pairs matters because a low-liquidity AMM can be moved cheaply. If the protocol reads prices from those pairs, the attacker can shape the protocol's view of value. A lending market or leveraged trader then becomes a price-taking victim of the attacker's temporary market.

### 3.2 Leveraged trading as the value-transfer path

The exploit path used Vee's leveraged-trading functionality. Leveraged trading typically combines borrowing and swapping. The protocol may borrow an asset, swap it into another asset, and treat the resulting position as collateral or exposure. If price and slippage checks are wrong, the attacker can cause the protocol to accept a route that is economically invalid.

In Vee's case, the attacker performed repeated swaps, including USDT.e to ETH.e routes through AugustusSwapper. The problem was not necessarily AugustusSwapper itself; external swap routers are common infrastructure. The risk was that Vee allowed the leveraged-trading flow to depend on manipulated pool references and insufficiently normalized price checks.

### 3.3 Decimal processing and slippage bypass

Rekt reports that the manipulation was combined with a price acquisition issue where decimals were not processed, allowing transactions to pass protocol slippage checks that would normally have failed. Decimal handling is a deceptively simple but critical part of DeFi accounting. Tokens may use 6, 8, 18, or other decimal precision. Wrapped and bridged assets can also differ in implementation details.

If a protocol compares raw token amounts without normalizing decimals, it may misjudge whether a trade is favorable, whether collateral is sufficient, or whether output satisfies slippage constraints. A slippage check that appears to protect users can become meaningless if it compares values on different scales.

This is why market-health analysis must treat decimals as part of the risk model. Incorrect decimal normalization is not a cosmetic bug. In a leveraged protocol, it can decide whether a value-destroying transaction is accepted.

### 3.4 Missing manipulation-resistance controls

The attack sequence involved pair creation, repeated setup transactions, failed attempts, new exploit contracts, and many transfers. A protocol with stronger manipulation-resistance controls could have flagged or blocked several points:

- newly created pairs being used as price sources;
- abnormal reserve movements in reference pools;
- large price deviation from global WETH/WBTC values;
- repeated failed exploit-like transactions;
- routes involving attacker-created liquidity;
- output values inconsistent after decimal normalization; and
- leveraged trades that moved or depended on thin pools.

Vee's design did not stop the sequence in time.

## 4. Attack preparation

### 4.1 Funding through Tornado Cash

The exploiter's Ethereum address was funded through Tornado Cash in three 10 ETH transactions. The funds were then bridged to Avalanche. This funding pattern is not proof of malicious intent by itself, but it is a common preparation step for attacks that require operational capital while obscuring the source of funds.

After reaching Avalanche, the attacker swapped 26.999006274904347875 WETH.e for 1,369.708 AVAX through Pangolin. AVAX was needed for gas, pair creation, and execution on Avalanche C-Chain.

### 4.2 Contract deployment and pair setup

The attacker deployed exploit contracts and used them to acquire target tokens and create the relevant Pangolin pairs. Rekt identifies at least three deployed exploit contracts and notes that the first attempt failed due to insufficient gas before later attempts succeeded.

This iterative behavior is important. The attacker was not simply clicking a single public function. They were testing the route, adjusting gas, deploying new contracts, creating market structure, and retrying until the exploit sequence cleared.

### 4.3 Funding multiple execution addresses

Once the attack contract was funded with 20 AVAX across five addresses, execution could begin. Multiple funded addresses gave the attacker operational flexibility and helped support repeated transactions. In low-fee environments, this kind of multi-address setup is cheap relative to the potential extraction.

## 5. Attack execution

### 5.1 Manipulating Pangolin reference prices

The attacker manipulated prices by swapping through the pairs created or targeted during setup. Because Vee used Pangolin pool prices as references in leveraged trading, these swaps influenced the values Vee saw. The attacker therefore attacked the protocol indirectly through its market inputs.

This is a fundamental oracle lesson: an AMM pool is not just a market; when a lending protocol reads it, the pool becomes part of the lending protocol's security boundary.

### 5.2 Using leveraged trading under manipulated prices

With manipulated references in place, the attacker used Vee's leveraged-trading flow. The protocol accepted transactions that should have failed under correct price and slippage handling. Rekt attributes this to manipulation plus missing decimal processing in price acquisition.

The result was that Vee's contracts allowed value to move out of the protocol under false assumptions about exchange rates and slippage. The attacker could repeatedly route trades and positions until WETH/WBTC liquidity was drained.

### 5.3 Repeated swaps through AugustusSwapper

Rekt specifically notes repeated swaps of USDT.e to ETH.e through AugustusSwapper. Swap aggregators can route through multiple pools and may be useful for ordinary execution, but they also make validation harder for the calling protocol. The protocol must ensure that:

- the route is authorized;
- the output is correctly valued;
- decimals are normalized;
- slippage checks are based on trusted prices;
- manipulated intermediate pools cannot define final value; and
- the swapper cannot be used to hide an economically invalid path.

If the protocol delegates route complexity to an external swapper without robust final checks, it can approve trades that look syntactically valid but are economically harmful.

### 5.4 Bridging stolen assets back to Ethereum

The stolen funds were sent back to Ethereum during and after the attack through more than 100 transactions. Rekt reported the exploiter's Ethereum wallet held about 214 WBTC and 8,804 WETH, corresponding to roughly $34 million at the time.

This cross-chain exit pattern matters. An exploit on Avalanche can quickly become an Ethereum custody problem once assets are bridged. Security teams must monitor not only the original chain but also bridge exits, Ethereum receipts, centralized exchange deposits, and mixer interactions.

## 6. Market and user impact

### 6.1 A top-ten Rekt event at the time

Rekt placed the Vee Finance loss in its top-ten leaderboard at the time, around number 7. That ranking reflected how large the exploit was relative to the then-young Avalanche DeFi ecosystem. A $34 million loss can damage user confidence across a chain, not only in the exploited protocol.

Avalanche was in a growth phase. Users were being encouraged to bridge assets, farm incentives, and explore new lending markets. A major lending/leverage exploit sends a clear market signal: the chain may be fast and cheap, but protocol maturity still varies widely.

### 6.2 WETH and WBTC liquidity loss

The stolen assets were highly liquid blue-chip wrappers: WETH and WBTC. This is different from an exploit that drains a protocol's native token. WETH and WBTC represent externally valuable assets and can be moved, bridged, and sold across many venues. Their loss directly reduces the protocol's ability to meet lender withdrawals.

For users who supplied WETH or WBTC, the exploit meant a direct loss of assets they expected to be among the safest in the market. The risk was not WETH or WBTC smart-contract failure. It was Vee's leverage/oracle layer.

### 6.3 Avalanche ecosystem contagion

Vee's loss followed the Zabu Finance exploit earlier in September 2021. Repeated incidents on a growing chain can create ecosystem-wide risk repricing:

- liquidity providers withdraw from unrelated protocols;
- users discount high APYs as compensation for unmeasured smart-contract risk;
- bridge inflows slow because users fear immature protocol security;
- auditors and monitoring teams focus on the ecosystem; and
- attackers scan similar protocols for copied oracle patterns.

The impact of a large exploit is therefore broader than the protocol's TVL.

## 7. Audit and process lessons

Rekt notes that Vee Finance had audits, including reports from SlowMist and CertiK, but the incident still occurred. It also states that Vee ignored recommendations in the SlowMist audit. The broader point is that audits do not eliminate economic-risk review. A lending and leveraged-trading protocol must be tested against adversarial market conditions, not only static code bugs.

Audit coverage should include:

- oracle-source manipulation;
- newly created pool usage;
- decimal normalization across all supported tokens;
- slippage checks under manipulated prices;
- external swapper route validation;
- bridge-wrapper assumptions;
- repeated failed transaction patterns; and
- whether audit recommendations were implemented before launch.

If a high-severity or economically meaningful recommendation is deferred, the protocol should treat the corresponding feature as unsafe until fixed.

## 8. Controls that would have reduced the loss

### 8.1 Multi-source oracle design

Vee should not have treated Pangolin spot prices as sufficient for leveraged-trading valuation. A safer design would combine multiple independent sources, use time-weighting, require minimum liquidity depth, and reject newly created or low-liquidity pairs as references. For WETH and WBTC, robust external price feeds and cross-market validation were especially important.

The protocol should also cap how far a local DEX price can deviate from a global reference before disabling leveraged trades.

### 8.2 Decimal normalization everywhere

All price, slippage, collateral, and output checks must normalize token decimals. This should be enforced in shared math libraries and tested with tokens using 6, 8, and 18 decimals. Tests should deliberately include bridged assets and routes where input and output tokens use different precision.

A good invariant is:

> A trade that is value-negative under normalized prices cannot pass slippage checks because of raw decimal differences.

If a protocol cannot prove that invariant, leveraged trading should not be enabled.

### 8.3 Reject attacker-created reference pools

Price sources should have age, liquidity, and provenance requirements. A pool created shortly before a transaction should not be eligible as a price oracle for leveraged trading. The protocol can require:

- minimum pool age;
- minimum time-weighted liquidity;
- minimum number of independent liquidity providers;
- no extreme reserve changes in the last N blocks;
- price agreement with other venues; and
- governance review before a pair becomes a reference.

These controls would not prevent all manipulation, but they would eliminate the most obvious attacker-created-pair path.

### 8.4 Route-level final value checks

When using a swap aggregator, the protocol should validate the final output against trusted prices after the route executes or through a pre-validated quote. It should not rely only on intermediate pool prices or aggregator output. Final value checks should be conservative and include protocol fees, expected slippage, and worst-case decimal handling.

If the route is too complex to validate, the protocol should not allow it for leveraged trading.

### 8.5 Emergency monitoring and pause logic

The Vee attack involved multiple visible warning signs: exploit contract deployments, failed attempts, pair creation, manipulated swaps, and repeated routes. A monitoring system could pause leveraged trading when it sees:

- newly created reference pairs;
- abnormal price deviation;
- repeated failed high-value leverage calls;
- sudden WETH/WBTC outflows;
- attacker-funded address clusters; and
- bridge exit flows beginning during protocol distress.

Emergency pause controls should be narrow but fast. Disabling leveraged trading for a short period is preferable to allowing a $34 million drain.

## 9. Market-health indicators

### 9.1 Oracle-source liquidity depth

For every asset a lending or leverage protocol supports, analysts should compare protocol exposure to the liquidity depth of the price source. If a protocol holds tens of millions in WETH/WBTC exposure but prices routes from thin or attacker-created pools, the risk is high.

The useful metric is not simply TVL. It is:

> maximum protocol value at risk ÷ cost to move the oracle source enough to pass a bad trade.

When that ratio is large, attackers have a positive expected value.

### 9.2 Decimal mismatch coverage

Protocols should publish or internally maintain a matrix of token decimals, wrappers, and pricing paths. Monitoring should flag any new asset or route where decimals differ and tests have not been run. Bridged assets such as WETH.e, WBTC.e, LINK.e, and USDT.e should receive extra scrutiny because their symbols can look familiar while contract details differ.

### 9.3 Cross-chain exit velocity

Large bridge exits during or immediately after abnormal protocol activity are a high-risk signal. In Vee's case, stolen funds were sent back to Ethereum through many transactions. Monitoring should connect Avalanche-side exploit activity with Ethereum-side receipts in near real time.

### 9.4 Failed exploit attempts

The attacker had failed attempts before success. Failed high-value interactions are often ignored as noise, but they can be reconnaissance or exploit debugging. Protocols should alert when failed transactions interact with sensitive functions, especially if followed by contract redeployments or modified calldata.

## 10. Broader implications

### 10.1 Leveraged protocols are oracle protocols

Any protocol that offers leverage is fundamentally an oracle protocol. It can only be safe if it knows asset values well enough to prevent undercollateralized or value-negative positions. If the price source is manipulable, the leverage engine will magnify the error.

Vee Finance shows that leverage turns a bad quote into a solvency event.

### 10.2 Multi-chain speed magnifies weak assumptions

Fast, low-cost chains reduce friction for users and attackers alike. An exploit that requires many setup transactions, pair creations, or retries is more practical when transaction costs are low. This does not make low-fee chains unsafe by default, but it means protocol-level defenses must assume attackers can iterate cheaply.

### 10.3 Blue-chip assets do not make the protocol safe

Users often treat WETH and WBTC markets as safer because the assets themselves are liquid and widely recognized. But when those assets are deposited into a vulnerable lending protocol, the protocol's accounting layer becomes the dominant risk. The underlying asset can be sound while the wrapper system drains it.

## 11. Timeline

- **Before 20 September 2021**: Vee Finance operates lending and leveraged trading on Avalanche, using Pangolin pool prices during leveraged-trading flows.
- **Pre-attack funding**: The attacker funds the Ethereum address through three 10 ETH Tornado Cash withdrawals, bridges funds to Avalanche, and swaps WETH.e for AVAX.
- **Setup**: The attacker deploys exploit contracts, acquires target tokens, and creates or uses pairs involving QI, XAVA, LINK.e, WETH.e, and WBTC.e.
- **Initial attempts**: At least one attempt fails due to insufficient gas; new exploit contracts are deployed.
- **Successful exploit**: The attacker manipulates Pangolin reference prices and uses Vee leveraged-trading paths, including repeated USDT.e-to-ETH.e swaps through AugustusSwapper, to bypass slippage checks and extract value.
- **Exit**: Stolen assets are bridged back to Ethereum across more than 100 transactions. The exploiter's Ethereum wallet holds roughly 214 WBTC and 8,804 WETH.
- **Response**: Vee Finance announces the incident, attempts to contact the attacker, and offers to discuss a bug bounty.

## 12. Lessons for market participants

For users, Vee Finance is a reminder that lending-market risk depends on oracle and route design, not only asset quality. Supplying WETH or WBTC to a young leveraged protocol can be risky if the protocol prices trades from manipulable local pools.

For builders, the controls are clear: never use a single DEX pool as an unbounded price source for leverage; normalize decimals everywhere; reject attacker-created reference pools; validate aggregator routes by final trusted value; and pause on abnormal setup patterns.

For analysts, the Vee exploit provides a monitoring template: track newly created pools used by protocols, compare oracle-source depth to value at risk, scan for decimal mismatch paths, flag failed exploit attempts, and link cross-chain exits to protocol distress.

The Vee Finance exploit was therefore not just an Avalanche lending hack. It was a failure to separate market execution from market truth. The protocol let an attacker manufacture the prices it trusted, and those manufactured prices were enough to turn leveraged trading into a $34 million drain.

## References

- Rekt, [Vee Finance - Rekt](https://rekt.news/vee-finance-rekt/)
- Vee Finance, [incident announcement cited by Rekt](https://veefi.medium.com/vee-finance-accident-announcement-5e75ff197da6)
- Vee Finance, [attack analysis cited by Rekt](https://veefi.medium.com/vee-finance-attack-analysis-a4839724e085)
- Vee Finance, [main-cause analysis cited by Rekt](https://veefi.medium.com/the-main-cause-of-vee-finance-attack-7a8475085ec5)
- Etherscan, [exploiter Ethereum address](https://etherscan.io/address/0xeeee458c3a5eaafcfd68681d405fb55ef80595ba)
