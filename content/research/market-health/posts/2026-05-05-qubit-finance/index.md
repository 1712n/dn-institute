---
title: "Qubit Finance, fake bridge collateral, and the market risk of event-driven cross-chain lending"
date: 2026-05-05
entities:
  - Qubit Finance
  - QBridge
  - BNB Chain
  - Ethereum
  - qXETH
  - PancakeBunny
---

## Summary

1. On 27-28 January 2022, Qubit Finance's QBridge was exploited for roughly **$80 million** after an attacker minted unbacked qXETH on BNB Chain and used it as collateral to borrow real assets.
2. The exploit did not require breaking the lending market's collateral math directly. It attacked the bridge layer that told the lending market what collateral existed.
3. A legacy `deposit()` path for ERC-20 tokens remained callable after QBridge added a native-ETH `depositETH()` path. Both paths emitted the same bridge deposit event.
4. Because ETH was represented by the zero address and that address was whitelisted, `safeTransferFrom()` did not revert even though no ETH moved. The bridge event was emitted anyway, and relayer logic minted qXETH on BNB Chain.
5. The incident is a market-health case study in cross-chain collateral risk: when a bridge can mint unbacked assets, every lending pool that accepts those assets becomes exposed, even if its own local accounting is correct.

## Why Qubit matters

Qubit Finance was a BNB Chain lending and borrowing protocol built by Mound, the team also associated with PancakeBunny. Qubit offered cross-chain collateral through QBridge: users could deposit assets on Ethereum and receive corresponding qTokens on BNB Chain. Those qTokens could then be supplied as collateral in Qubit's lending markets.

This design is powerful because it lets assets move across chains and become productive collateral. It is also dangerous because the lending market is only as safe as the bridge's proof that collateral was actually locked. If the bridge mints qTokens without a real source-chain deposit, the lending market sees collateral that does not exist.

That is what happened to Qubit. The attacker created qXETH on BNB Chain without locking ETH on Ethereum. The qXETH then functioned as fake collateral. Qubit's lending contracts did what lending contracts are supposed to do: they accepted collateral and allowed borrowing. The problem was upstream. The collateral token was not backed.

For market health, this is an important distinction. A lending protocol can have apparently sound loan-to-value math and still be drained if the collateral issuer is compromised or fooled.

## The bridge design flaw

QBridge had two deposit paths relevant to ETH:

1. `depositETH()`, intended for native ETH deposits and requiring actual ETH value.
2. `deposit()`, a more generic ERC-20 deposit function that used `safeTransferFrom()`.

Both paths could emit the same kind of `Deposit` event. That event was used by cross-chain processing to mint the corresponding qToken on BNB Chain.

The dangerous overlap came from the way ETH was represented. Native ETH does not have an ERC-20 contract address, so QBridge used the zero address as a placeholder. The zero address was whitelisted. When the attacker called the generic `deposit()` path with ETH-related data, the contract resolved the token address to the zero address and attempted `safeTransferFrom()`.

Calling a function on an address with no contract code can return successfully at the low-level EVM call layer. No token moved, but the call path did not fail. The contract then emitted a deposit event that relayer logic treated like a legitimate ETH-backed deposit.

In simple terms:

```text
no ETH locked on Ethereum
        +
Deposit event emitted anyway
        =
qXETH minted on BNB Chain
```

The bridge turned an event into collateral. The event was false.

## Attack flow

The exploit sequence can be summarized as follows:

```text
1. The attacker funded an Ethereum address shortly before the exploit.
2. The attacker called QBridge's generic deposit() function with ETH-related resource data.
3. The zero address was used as the token address for ETH.
4. safeTransferFrom() did not revert, despite no real ETH being transferred.
5. QBridge emitted a Deposit event.
6. Cross-chain processing minted qXETH on BNB Chain.
7. The attacker repeated the process to accumulate a large qXETH balance.
8. The attacker supplied unbacked qXETH as collateral in Qubit's lending markets.
9. The attacker borrowed real assets and converted them, ultimately draining about $80 million.
```

Rekt reported that the attacker gained access to **77,162 qXETH**, described as worth about **$185 million**, and then borrowed WETH, BTC-B, USD stablecoins, CAKE, BUNNY, and MDX before converting assets into roughly **200,000 BNB**. Merkle Science described the attacker as draining **206,809 BNB** and minting more than **216,000 qXETH**, with stolen assets including WETH, BTCB, BNB, MATIC, CAKE, BUSD, and others.

The exact accounting varies by source and by whether it tracks collateral minted, assets borrowed, or final converted proceeds. The market-health point is consistent: unbacked qXETH became the key that unlocked real lending-pool liquidity.

## The lending market was downstream of the bridge

Qubit's lending market did not need to misprice ETH for the exploit to work. It needed to trust qXETH.

This is the core composability risk. A market can correctly value a collateral token based on its assumed peg or backing and still be wrong if the token's supply is illegitimate. The risk is not price oracle manipulation in the usual sense. It is collateral provenance failure.

When a bridge mints wrapped or synthetic assets, it creates claims. Lending markets, AMMs, and other protocols may then treat those claims as assets. If the bridge's minting path is compromised, every protocol that accepts the wrapped asset becomes exposed to the bridge bug.

In Qubit, the fake collateral entered a lending system. In another protocol, the same pattern could contaminate AMM pools, stablecoin collateral, derivatives margin, or governance voting. Bridges are not just transport infrastructure; they are asset issuers.

## Why identical events were dangerous

The event layer is often treated as a neutral log of what happened. Cross-chain systems frequently rely on events because they are easy for relayers to watch and prove. But an event is only as trustworthy as the contract path that emitted it.

QBridge's generic token deposit path and native ETH deposit path emitted events that downstream logic could not distinguish adequately. The relayer saw "Deposit" and minted qXETH. It did not know that the event came from a path where no ETH had actually moved.

That is a design flaw. Cross-chain events should encode enough information for downstream validators to verify what happened:

1. Which function path emitted the event.
2. Which token address was transferred.
3. Whether native value was attached.
4. The exact amount received by the contract.
5. Whether the source-chain balance increased by the emitted amount.
6. A deposit nonce or ID that cannot be replayed or spoofed.

If two economically different actions produce the same event, the bridge is asking off-chain systems to make a distinction that the log does not contain. In Qubit, that ambiguity became an $80 million loss.

## The zero-address trap

The zero address is often used as a placeholder for native ETH. That convention is convenient, but it is dangerous when mixed with ERC-20 transfer logic.

An ERC-20 token address should point to a contract with code. Native ETH is not an ERC-20 token. If a contract accepts `address(0)` in a token-transfer path, it must explicitly branch into native-asset handling and require `msg.value` or a balance delta. It should not pass the zero address into a generic token transfer helper and treat lack of revert as proof of payment.

The Qubit exploit shows why:

```text
zero address whitelisted
       +
generic ERC-20 deposit path
       +
same Deposit event as native ETH path
       =
unbacked bridge mint
```

This is not merely a coding gotcha. It is a collateral-control failure. The bridge must prove that locked assets exist before it mints claims. A placeholder address cannot be allowed to bypass that proof.

## Market impact

The immediate loss was approximately **$80 million**. Qubit's native token QBT reportedly fell sharply after the exploit. Borrowing, supplying, repaying, bridge operations, and some redemption functions were disabled while the team responded.

The broader impact was confidence damage across BNB Chain lending and cross-chain collateral systems. Users who supplied real assets to Qubit lending pools were exposed not because they borrowed recklessly, but because another user could mint fake collateral and drain shared liquidity.

That is a different risk profile from a normal liquidation or bad-debt event. In a normal lending loss, collateral prices move, liquidators fail, or oracle data lags. In Qubit, collateral creation itself was fraudulent. The system's solvency assumptions were violated before any LTV calculation started.

The loss also reinforced the market's concern that bridges were becoming DeFi's largest attack surface. By early 2022, cross-chain systems were accumulating significant value, but many had immature verification models, complex relayer assumptions, and large downstream integrations. Qubit was one of several bridge-related incidents that made this risk visible.

## Team-history and repetition risk

Qubit was built by the team behind PancakeBunny, which had already suffered a major exploit in May 2021. Rekt highlighted that history directly. For users, repeated incidents by related teams are not just reputation issues. They are process signals.

A single exploit can happen even to careful teams. Repeated severe losses suggest deeper problems: rushed launches, insufficient change management, weak threat modeling, inadequate review of legacy code, or a culture that underestimates adversarial conditions.

Qubit also reportedly had its cross-chain collateral feature audited in December 2021. An audit did not prevent the exploit. That does not mean audits are useless. It means users should ask what the audit covered, whether the exact deployed configuration matched the reviewed code, and whether legacy functions were explicitly tested under adversarial event-relayer conditions.

For protocols that issue collateral across chains, the audit scope must include:

1. Native-token and ERC-20 deposit paths.
2. Event semantics.
3. Relayer assumptions.
4. Zero-address handling.
5. Resource-ID mapping changes.
6. Owner-only configuration changes.
7. Downstream lending-market exposure.

If the audit only checks local contract syntax or common ERC-20 transfer behavior, it may miss the actual bridge risk.

## Governance and configuration risk

Community technical summaries later emphasized another important angle: resource-ID mappings and zero-address configuration. Qubit documentation and post-incident analysis described how ETH was represented by the zero address, and a community-run Qubit incident wiki alleges that a prior owner-only mapping change replaced WETH's contract address with the zero address without a public explanation.

That claim should be handled cautiously unless independently verified in every detail, but the risk category is real. Bridge configuration is critical infrastructure. A mapping from a resource ID to a token address determines what asset the bridge thinks it is handling. If that mapping can be changed without a timelock, public notice, or validation, the bridge can be moved into a dangerous state quickly.

For market health, this means bridge configuration should be treated like protocol code:

1. Changes should be timelocked where possible.
2. Users and integrators should be alerted before asset mappings change.
3. Zero-address mappings should be restricted to explicitly native-token functions.
4. Relayers should reject events that do not match expected function paths.
5. Lending markets should pause collateral acceptance when bridge mappings change.

Bridges fail not only through code bugs but through unsafe configuration states.

## Why no direct deposit was needed

One of the most unintuitive aspects of the exploit is that the attacker did not need to deposit ETH to get qXETH. That breaks the mental model users have for bridges.

Users assume:

```text
locked ETH on Ethereum -> qXETH on BNB Chain
```

The exploit created:

```text
event pretending ETH was locked -> qXETH on BNB Chain
```

The difference is everything. A bridge token is supposed to be a receipt. In Qubit, the receipt could be printed without the deposit. Once printed, it entered a lending market that could not distinguish fake receipts from legitimate ones.

This is why bridges need balance-based validation, not only event-based validation. The source contract should verify actual received value before emitting an event that can mint destination-chain assets. Relayers should also verify that value, not merely watch for a log.

## What monitoring should have caught

Several real-time signals could have reduced the loss.

First, a bridge monitor should compare emitted deposit amounts to actual source-chain balance changes. A large ETH deposit event with no corresponding ETH received should be impossible.

Second, relayers should classify deposit events by function selector. A native-ETH mint on BNB Chain should not be triggered by a generic ERC-20 deposit path unless the token contract and balance delta are valid.

Third, lending markets should monitor sudden collateral supply expansion for bridge-issued assets. qXETH supply increasing by tens or hundreds of thousands of ETH-equivalent units should trigger a pause before borrowing is allowed.

Fourth, borrowing against newly minted bridge collateral should be rate-limited. A short delay or staged credit limit can turn a bridge-mint anomaly from an $80 million immediate drain into a containable incident.

Fifth, protocols should monitor destination-chain borrow concentration. One address using freshly minted collateral to borrow across many assets is a high-risk pattern.

These controls are not theoretical. They target the exact bridge-to-lending failure path that Qubit exposed.

## User-facing lessons

For users, the Qubit exploit is a warning about cross-chain collateral. A lending market may advertise overcollateralized borrowing, but the quality of collateral depends on who issued it and how.

Before supplying assets to a market that accepts bridge-issued collateral, users should ask:

1. Who controls the bridge minting path?
2. Are relayers permissioned, audited, and monitored?
3. Does the bridge verify source-chain balance changes or only events?
4. Can token mappings be changed instantly by an owner?
5. Are newly minted bridge assets subject to borrow caps?
6. Has the same team suffered prior severe exploits?

High yield in a lending pool may be compensation for risk that users cannot see directly. If a pool lends against fragile bridge collateral, every supplier is indirectly underwriting that bridge.

## Broader market implications

Qubit helped define the 2022 bridge-risk cycle. Bridges attracted massive value because they connected liquidity across chains. They also became attractive targets because a single validation bug could create unbacked assets or unlock locked funds.

The incident showed that bridge losses do not stay inside bridges. They spill into lending protocols, DEX liquidity, token prices, user confidence, and chain-level reputation. A fake-mint bug can become a solvency event for every market that accepts the bridged token.

This has a clear market-health implication: cross-chain assets should not be treated as identical to native assets without a risk premium. qXETH was not ETH. It was a claim issued by QBridge. When QBridge failed, qXETH's collateral meaning failed.

## Conclusion

The Qubit Finance exploit was an $80 million failure of cross-chain collateral validation. A legacy ERC-20 `deposit()` path, zero-address ETH representation, indistinguishable deposit events, and relayer trust combined to mint unbacked qXETH on BNB Chain. That fake qXETH was then used as collateral to borrow real assets from Qubit's lending pools.

The enduring lesson is that bridge tokens are not automatically assets; they are claims. Lending markets that accept those claims must understand and monitor the bridge that issues them. If an event can mint collateral without a deposit, the lending market's own solvency math becomes irrelevant.
