---
date: 2026-05-05
entities:
  - id: indexed-finance
    name: Indexed Finance
    type: defi
  - id: defi5
    name: DEFI5
    type: index-token
  - id: cc10
    name: CC10
    type: index-token
  - id: ndx
    name: NDX
    type: token
title: "Indexed Finance reindex manipulation, single-token pool valuation, and the $16 M DEFI5/CC10 drain"
---

## 1. Introduction and incident overview

On 14 October 2021, Indexed Finance was exploited for roughly $16 million after an attacker manipulated the reindexing mechanics of its on-chain index pools. The attacker targeted the DEFI5 and CC10 pools, two tokenized crypto index products designed to give users basket exposure to DeFi and large-cap crypto assets. The exploit did not require stealing admin keys or compromising user wallets. It abused the protocol's own pool valuation and rebalancing logic during a reindex cycle, causing the pools to issue index tokens at a distorted price and then letting the attacker redeem those tokens for real underlying assets.

Indexed Finance was built to resemble an automated crypto ETF system. Each index token represented a proportional claim on a pool of assets. The pool used Balancer-style weighted-asset mechanics and controller logic to add, remove, and rebalance tokens over time. That design created a complex accounting surface: pool value, token weights, minimum balances, reindex scheduling, swap limits, and join/exit formulas all had to stay coherent while users and arbitrageurs interacted with the pool.

The vulnerability centered on the controller function used to update a newly added token's minimum balance. The controller estimated total pool value using the balance and target weight of a single reference token — the first fully initialized token with a positive target weight. During the DEFI5 exploit path, UNI became the reference token. The attacker used large flash-loaned positions and repeated swaps to drain the pool's UNI balance temporarily. Because the valuation formula extrapolated total pool value from that manipulated UNI balance while token weights updated slowly, the controller drastically underestimated the pool's value. Rekt reported that the controller valued the DEFI5 pool at only 29,851 SUSHI, roughly $300,000, despite the pool receiving more than $100 million worth of other assets during the attack sequence.

Once the minimum-balance calculation was distorted, the attacker could make a newly added token appear heavily overweighted, mint an outsized amount of DEFI5 or CC10 index tokens with relatively small input, and then burn those inflated index tokens to withdraw the real assets in the pool. The same mechanism was applied to both DEFI5 and CC10. The Future of Finance Fund was also affected because it held DEFI5 and CC10 as underlying assets.

The Indexed Finance incident matters for market-health analysis because it shows how composable index products can fail even when the visible assets are liquid blue-chip tokens. The failure was not in AAVE, UNI, COMP, MKR, CRV, SNX, LINK, YFI, BAT, or UMA themselves. It was in the index layer that turned those assets into pooled claims. When the claim-pricing logic was manipulated, diversified exposure became a single exploitable balance-sheet invariant.

## 2. Background: Indexed Finance and on-chain index pools

### 2.1 Crypto index products as pooled claims

Indexed Finance offered index pools such as DEFI5 and CC10. Each pool held a basket of tokens and issued an index token representing ownership of that basket. Users could buy, sell, join, or exit the pool without manually rebalancing every underlying asset. In theory, the index token's value should track the weighted net asset value of the pool.

This model is useful because it simplifies portfolio construction. Instead of buying multiple tokens separately, users can hold one index token. But it also introduces new risk. The index token is a claim on a smart-contract accounting system, not merely a wrapper around static assets. If the accounting system can be tricked into issuing too many index tokens, honest holders are diluted and the pool can be drained.

### 2.2 Balancer-style weighted pools

The Indexed pools were derived from Balancer-style pool logic. Weighted pools let tokens trade against each other according to balances and weights. They also support joining and exiting, where users deposit assets to mint pool tokens or burn pool tokens to withdraw underlying assets.

Balancer-style designs depend on careful math:

- token balances determine spot prices;
- token weights determine relative pool composition;
- join and exit formulas determine pool-token issuance and redemption;
- maximum input and output ratios limit extreme swaps; and
- reweighting logic gradually changes target exposures.

The Indexed exploit emerged from interactions among these components. The pool's swap limits slowed the attack but did not prevent it. The reweighting delay reduced ordinary slippage but created a temporary discrepancy that the attacker could manipulate.

### 2.3 Reindexing and minimum balances

Index products need to change composition when market conditions change. Indexed Finance used a controller to determine which tokens belonged in each index and to manage reindexing. When a new token was added to a pool, the system needed to establish a minimum balance and initialize the token's trading state before it could behave like an ordinary pool component.

The `updateMinimumBalance` function was intended to set that minimum based on the pool's estimated value. The key question was: how much of the newly added token should the pool require before treating it as initialized? If the estimate was too high, the pool might be hard to initialize. If the estimate was too low, an attacker could initialize it cheaply and distort weights.

Indexed calculated pool value using a function commonly described as `extrapolatePoolValueFromToken`. The simplified relationship was:

> total pool value = reference token balance × total pool weight ÷ reference token weight

This formula can be reasonable if the reference token balance and weight accurately represent the pool. It becomes dangerous if the reference token balance can be temporarily manipulated while the denominator and total weight remain slow-moving or externally determined.

## 3. Vulnerability: extrapolating pool value from a manipulable reference token

### 3.1 Single-reference-token valuation

The critical design weakness was using one token's liquidity to estimate the value of the entire pool. Rekt described the reference as the first token in the pool with target weight above zero and fully initialized. BlockSec similarly identified the `updateMinimumBalance` function and its pool-value calculation as the vulnerable component.

During the attack, the attacker targeted UNI as the reference token. By buying out or otherwise depleting UNI from the pool using flash-loaned assets, the attacker made the reference token balance far smaller than it should have been. The valuation formula then interpreted the shrunken UNI balance as evidence that the entire pool was worth much less.

This is a classic oracle-style failure, but inside a pool rather than in an external price feed. The manipulated signal was not a Chainlink price or DEX TWAP. It was the pool's own internal balance of a selected token.

### 3.2 Slow weight updates created a stale denominator

The formula also depended on token weights. Indexed limited the rate at which weights could change, reportedly by about 1% per hour. This was intended to control slippage and avoid abrupt rebalances. However, it created a mismatch: balances could be moved quickly through swaps, while weights could not react at the same speed.

The attacker exploited that mismatch. The UNI balance fell sharply, but the token weight used in the extrapolation did not adjust proportionally. The result was an artificially low total-pool-value estimate.

This is an important market-health lesson: controls designed to smooth one risk can create another. Gradual reweighting reduced normal rebalancing shock, but it also made the system vulnerable when a fast balance manipulation was combined with a slow accounting parameter.

### 3.3 Minimum-balance manipulation

Once the pool value was underestimated, the attacker called `updateMinimumBalance` for the newly added token, SUSHI in the DEFI5 path. Because the function used the manipulated pool value, the required minimum balance for SUSHI was set far below what a healthy pool value would imply.

This allowed the attacker to initialize and overweight the new token in a way that should not have been economically possible. The minimum-balance error became the bridge from temporary manipulation to permanent claim inflation.

### 3.4 Join and exit asymmetry

After manipulating the new token's balance and weight, the attacker used join and exit operations to mint and redeem pool tokens. BlockSec's analysis emphasizes that `exitPool` returned underlying tokens in equal proportion and did not account for the manipulated token weight in the way the attacker needed. Meanwhile, join operations with the now abnormal SUSHI state minted pool tokens at favorable terms.

The exploit therefore depended on more than one function. It required:

1. reindexing to add a token;
2. reference-token balance manipulation;
3. minimum-balance recalculation under manipulated value;
4. initialization of the newly added token at distorted weight;
5. pool-token minting under the distorted state; and
6. redemption of inflated pool-token claims against real assets.

Complex DeFi systems often fail at these function boundaries. Each function may look defensible in isolation, while their sequence creates an exploitable state machine.

## 4. Attack flow

### 4.1 Target selection: DEFI5 and CC10

The attacker targeted DEFI5 and CC10. DEFI5 held DeFi assets such as UNI, AAVE, COMP, SNX, CRV, and MKR before SUSHI was added in the attack path. CC10 held a broader set of large-cap crypto assets. Both pools shared the relevant reindex and valuation mechanics.

The attack also affected the Future of Finance Fund because it held DEFI5 and CC10 tokens. This illustrates index contagion: a fund that holds other index tokens inherits their smart-contract and valuation risk, not just their asset exposure.

### 4.2 Funding and flash loans

The attacker address was funded through Tornado Cash before the exploit. Public analysis also shows the use of large flash-loaned positions. Blockscope describes approximately $156 million in flash-loaned tokens used to manipulate pool state. Flash loans were not the bug, but they supplied the transaction-scale inventory needed to move multiple balances atomically and then repay lenders after extracting value.

Flash loans make this class of exploit especially dangerous because the attacker does not need to own the assets required to distort a pool. They only need enough transaction fees, code, and a profitable path through the protocol's state machine.

### 4.3 Triggering a reindex

In the DEFI5 transaction, the attacker invoked `reindexPool`, causing SUSHI to be bound as a new token in the pool. Before this step, the DEFI5 pool contained tokens including UNI, AAVE, COMP, SNX, CRV, and MKR. The reindex event created the window in which SUSHI needed initialization and a minimum balance.

This was not an unauthorized function call in the ordinary sense. Reindexing was a public mechanism of the protocol. The vulnerability was that a public reindex could be combined with balance manipulation and minimum-balance updates in the same transaction sequence.

### 4.4 Manipulating the reference token

The attacker used flash-loaned assets and repeated swaps to buy out UNI from the DEFI5 pool. The repeated swaps were necessary because the pool limited swap sizes. Rekt notes that swaps could not send more than half of the pool's existing balance in a token or purchase more than one-third of the pool's balance in a token. These limits slowed depletion but still allowed gradual manipulation through multiple operations.

As UNI balance decreased, `extrapolatePoolValueFromToken` returned a much lower pool value. The formula did not recognize that UNI had been deliberately depleted as part of an atomic exploit sequence.

### 4.5 Updating minimum balance under the false pool value

With UNI balance distorted, the attacker called `updateMinimumBalance` for SUSHI. The controller then set a minimum balance based on the false low pool value. BlockSec describes the vulnerable behavior as setting a not-yet-ready token's minimum balance to a fraction of pool value, where pool value itself had been manipulated.

This step converted a transient pool-balance distortion into a changed controller parameter. It was the point where the attack moved from price manipulation into protocol state corruption.

### 4.6 Creating abnormal SUSHI weight

The attacker then transferred or supplied a large amount of SUSHI to the pool and called `gulp`, causing SUSHI's status to become ready. Because the minimum-balance and value context had been manipulated, SUSHI's initial denormalized weight became abnormal.

Once SUSHI was ready under distorted conditions, the attacker could interact with the pool as though the new token state were legitimate. That made subsequent join operations highly favorable.

### 4.7 Minting inflated pool tokens and exiting

The attacker used `joinswapExternAmountIn` with SUSHI to mint pool tokens under the abnormal weight. Those pool tokens represented claims on the full pool. The attacker then called `exitPool` to redeem the inflated pool-token position for underlying assets.

The economic result was straightforward: the attacker minted claims too cheaply and redeemed them against assets supplied by honest users. DEFI5 and CC10 holders were diluted and drained.

## 5. Stolen assets and immediate impact

BlockSec reports two main attack transactions:

- In the DEFI5 transaction, the attacker gained approximately 6,226.8 AAVE, 15 ETH, 192,358.6 UNI, 5,459.5 COMP, 721,611.3 CRV, 16,680.6 SNX, and 406.5 MKR.
- In the CC10 transaction, the attacker gained approximately 109.6 MKR, 17,844 UMA, 1,002.4 COMP, 34,602.5 UNI, 131,645.4 BAT, 28,754.1 SNX, 1,273.6 AAVE, 124,194.2 CRV, 33,215.4 LINK, and 5.24 YFI.

The total value was about $16 million. The assets were not obscure, illiquid protocol tokens. They were widely traded DeFi and large-cap crypto assets. That made the drain immediately economically meaningful and also demonstrated that pooled blue-chip exposure can still be unsafe if the wrapper accounting is exploitable.

The attacker address remained publicly tracked, and Indexed Finance attempted to communicate with the exploiter on-chain. Rekt documented an on-chain message from Indexed asking to talk. The public aftermath later became notable because the team believed they could identify the attacker and pursued legal remedies. Regardless of legal status, the on-chain market damage was immediate: index holders lost underlying value, and confidence in the protocol's reindex model collapsed.

## 6. Market-health implications

### 6.1 Index tokens carry protocol-accounting risk

Index tokens are often marketed as diversified exposure. Diversification reduces idiosyncratic asset risk, but it does not reduce wrapper risk. If the index contract can over-issue claims, every underlying asset becomes drainable no matter how diversified the basket is.

This distinction is critical for market-health analysis. A user holding DEFI5 was not only exposed to the market prices of UNI, AAVE, COMP, SNX, CRV, MKR, and SUSHI. They were also exposed to:

- reindex logic;
- pool-value estimation;
- minimum-balance parameters;
- join and exit formulas;
- swap-ratio limits;
- controller permissions; and
- flash-loan manipulation of intermediate pool states.

Diversification at the asset layer can hide concentration at the contract-invariant layer.

### 6.2 Single-reference valuation is fragile

Estimating a whole pool from one token's balance is fragile when that balance can be moved during the same execution context in which the estimate is used. A robust index system should not allow any single token's temporarily depleted balance to define the entire pool's valuation for minting or initialization.

Market-health monitors should flag systems where:

1. pool value is extrapolated from a single component;
2. the reference component can be swapped in the same pool;
3. weights update slowly relative to balances;
4. new-token initialization depends on that value;
5. pool-token minting can immediately follow initialization; and
6. exit logic can redeem newly minted claims against the entire basket.

That pattern is dangerous even if the reference token is liquid under ordinary market conditions.

### 6.3 Flash loans expose atomic state-machine flaws

The Indexed exploit was not merely a "large trade." It was an atomic manipulation of a state machine. Flash loans let the attacker create a temporary world in which the pool's balances, weights, and minimum-balance calculations were inconsistent. The attacker then locked in the inconsistency by minting index tokens and redeemed before the world normalized.

Defenses that rely on the assumption that manipulators must hold capital over time are inadequate. Protocols must be safe under the condition that an attacker can borrow enormous amounts for one transaction.

### 6.4 Nested index contagion

FFF was affected because it held DEFI5 and CC10. This is an important structural point. Index products can hold other index products, yield tokens, LP tokens, or vault shares. If any underlying claim token becomes impaired, higher-level products inherit the impairment.

Market-health analysis should map these dependencies. A top-level index token may appear diversified, but if it holds claim tokens from vulnerable pools, its real exposure includes those pools' smart-contract risks.

## 7. Why existing limits failed

Indexed's pools had swap limits such as maximum input and output ratios. These controls are useful against simple one-shot pool drains, but they did not stop repeated manipulation. The attacker worked within the limits by performing multiple swaps. The limits increased the number of steps but did not address the core issue: pool value was recalculated from a reference balance that the attacker could still move enough.

This is a recurring DeFi defense failure. Rate limits and ratio limits are not substitutes for invariant protection. If a protocol's critical accounting formula can be biased by repeated legal operations, limiting each operation's size may only make the exploit longer, not impossible.

The design also relied on gradual weight changes. Again, this reduced normal rebalancing shock but did not protect against atomic balance manipulation. In fact, the slow weight update helped preserve the stale denominator used in the false pool-value estimate.

## 8. Controls that would have reduced the loss

### 8.1 Multi-asset pool valuation

Pool value should be calculated from multiple assets, not a single reference token. A valuation function can use all initialized tokens, external price feeds, liquidity-weighted medians, or conservative lower bounds. If one token's balance changes abnormally, the pool value should not collapse unless independent evidence confirms that the whole basket lost value.

For an index pool, a safer approach is to compute net asset value as the sum of verified component balances times robust component prices. If an asset lacks a reliable price, its contribution should be capped or excluded from minting calculations rather than allowing it to distort the whole pool.

### 8.2 Reindex isolation windows

Reindexing should not allow all sensitive operations in one atomic path. A protocol can separate:

- token binding;
- minimum-balance setting;
- token readiness;
- weight activation;
- joins;
- exits; and
- large swaps.

Delays or commit-reveal windows between these phases give monitoring systems and arbitrageurs time to detect manipulation. More importantly, they prevent an attacker from creating a false intermediate state and monetizing it before the transaction ends.

### 8.3 Conservative initialization of new tokens

Newly added tokens should be initialized with conservative caps. Until a token has stable balances and verified weights, joins and exits involving that token should be limited. Minimum balances should be based on robust pre-reindex snapshots, not live manipulated balances.

For example, a controller could snapshot pool value before reindexing begins and use that snapshot for all minimum-balance calculations. It could also reject minimum-balance updates if any reference token's balance has moved beyond a small threshold in the same block or recent window.

### 8.4 Invariant tests for join/exit cycles

The exploit demonstrates the need for property-based tests over sequences, not just individual functions. A useful invariant is:

> No sequence of swaps, reindexes, minimum-balance updates, gulps, joins, exits, and flash loans can let an account withdraw more net pool value than it supplied, except for ordinary market-making profit bounded by fees and price movement.

Testing should include manipulated balances, delayed weights, new-token initialization, maximum-ratio edge cases, and repeated legal operations within one transaction.

### 8.5 Emergency pause on abnormal reindex activity

Automated monitoring could detect the attack pattern:

- a reindex is triggered;
- a reference token balance is depleted through repeated swaps;
- `updateMinimumBalance` is called soon after;
- a new token is initialized with abnormal weight;
- large joins occur with the new token; and
- exits follow immediately.

Any one event may be legitimate. The sequence is not. A market-health-aware protocol should be able to pause joins or exits when this chain appears.

## 9. Monitoring signals

### 9.1 Reference-token depletion

If a pool uses a reference token for valuation, that token's balance should be monitored relative to historical and target-weight expectations. A sudden depletion of the reference token before a valuation update is a high-risk signal.

The monitor should not only watch price. It should watch the exact variable used by the protocol's formula. In Indexed's case, the exploitable signal was a pool balance used by `extrapolatePoolValueFromToken`.

### 9.2 Pool value discontinuities

A pool containing tens or hundreds of millions in assets should not suddenly be valued at a few hundred thousand dollars because one component's balance changed. Such a discontinuity should automatically disable minting and reindex updates until reviewed.

For index products, a net-asset-value floor can be computed from independent balances. If internal pool value diverges from that floor by an extreme amount, user-facing mint and exit operations should be restricted.

### 9.3 Newly added token overweight

A newly added token that becomes heavily overweight immediately after initialization is suspicious. In a controlled reindex, new weights should converge gradually. An immediate abnormal weight is a sign that minimum-balance or readiness logic has been manipulated.

### 9.4 Flash-loan-sized interaction clusters

The attack used large flash loans and many operations in a single transaction. Monitoring systems should flag clusters that combine:

- large inbound asset loans;
- repeated swaps around maximum-ratio limits;
- controller calls;
- pool-token minting;
- pool-token burning; and
- repayment at transaction end.

This cluster is often more informative than any single transfer.

## 10. Broader implications for DeFi index products

### 10.1 ETF-like UX can mask smart-contract leverage

Index tokens feel simple to users. They look like diversified portfolio shares. But on-chain index construction may involve complex active mechanisms that are much closer to automated market-making plus governance-controlled rebalancing than to a passive off-chain ETF.

Users and integrators should evaluate index products by reading the rebalancing and minting logic, not only the asset list. A basket of good assets can be unsafe if the basket wrapper can be gamed.

### 10.2 Open-source communication can be exploited

The Indexed aftermath included claims that the exploiter had asked detailed questions about oracle and reindex mechanics before the attack. Open-source collaboration is valuable and should not be abandoned, but protocols need a process for escalating unusually specific economic-invariant questions. If a user repeatedly asks how timing, weights, minimum balances, and reindexes interact, that may be a prompt for internal threat modeling.

The answer is not secrecy. The answer is to treat hard questions as potential security signals and run adversarial simulations before attackers do.

### 10.3 Legal recovery is not market recovery

Indexed Finance pursued legal remedies after the exploit, and later public reporting connected the case to a named individual. Legal action can matter for deterrence and possible restitution, but it does not restore on-chain solvency in real time. Markets price the immediate loss, uncertainty, and operational risk long before courts resolve responsibility.

For market-health purposes, prevention and rapid containment matter more than ex-post identification.

## 11. Timeline

- **Before 14 October 2021**: Indexed Finance operates DEFI5, CC10, and other index pools using Balancer-style pool mechanics and controller-driven reindexing.
- **Pre-attack**: The attacker address is funded through Tornado Cash. The attacker prepares contracts and flash-loan routes.
- **14 October 2021, around 18:37 UTC**: The attacker targets DEFI5, triggers reindexing, adds SUSHI, manipulates UNI balance, updates SUSHI minimum balance under a false pool valuation, mints inflated pool tokens, and exits for underlying assets.
- **Same attack window**: The attacker repeats the mechanism against CC10.
- **Aftermath**: Roughly $16 million in assets is stolen. Indexed Finance attempts on-chain communication with the exploiter. DEFI5, CC10, and dependent positions such as FFF suffer losses, and the protocol's reindex model faces severe trust damage.

## 12. Lessons for market participants

For users, Indexed Finance demonstrates that diversification does not eliminate smart-contract wrapper risk. An index token can hold high-quality assets and still be unsafe if its minting, reindexing, or redemption logic can over-issue claims.

For builders, the lesson is that pool valuation must be robust to adversarial state manipulation. Do not extrapolate total value from a single component whose balance can be moved in the same transaction. Do not allow new-token initialization, balance manipulation, pool-token minting, and redemption to occur in one atomic exploit path.

For analysts, the incident provides a monitoring template: track reference-token balances, pool-value discontinuities, newly added token weights, flash-loan-sized interaction clusters, and nested exposure through index-of-index products.

The Indexed Finance exploit was ultimately a claim-pricing failure. The attacker did not need to make the underlying assets worthless. They only needed to make the pool temporarily misprice its own shares. Once that happened, $16 million of diversified assets became withdrawable through inflated index-token claims.

## References

- Rekt, [Indexed Finance - Rekt](https://rekt.news/indexed-finance-rekt/)
- BlockSec, [The Analysis of Indexed Finance Security Incident](https://blocksec.com/blog/the-analysis-of-indexed-finance-security-incident)
- Blockscope, [The Indexed Finance Hack](https://research.blockscope.co/andean-medjovic-case-and-investigation/the-indexed-finance-hack)
- Etherscan, [DEFI5 attack transaction](https://etherscan.io/tx/0x44aad3b853866468161735496a5d9cc961ce5aa872924c5d78673076b1cd95aa)
- Etherscan, [CC10 attack transaction](https://etherscan.io/tx/0xbde4521c5ac08d0033019993b0e7e1d29b1457e80e7743d318a3c27649ca4417)
- Etherscan, [attacker address](https://etherscan.io/address/0xba5ed1488be60ba2facc6b66c6d6f0befba22ebe)
