---
date: 2026-05-05
entities:
  - id: bearn-fi
    name: bEarn Fi
    type: defi
  - id: alpaca-finance
    name: Alpaca Finance
    type: defi
  - id: busd
    name: BUSD
    type: stablecoin
  - id: ibbusd
    name: ibBUSD
    type: token
title: "bEarn Fi BUSD vault denomination mismatch, ibBUSD strategy accounting, and the $18 M BSC yield-vault drain"
---

## 1. Introduction and incident overview

On 16 May 2021, bEarn Fi's BUSD vault on Binance Smart Chain was exploited after its vault and strategy contracts treated two economically different assets as if they were the same unit. The BvaultsBank contract handled user deposits and withdrawals in BUSD, while the associated BvaultsStrategy interacted with Alpaca Finance's interest-bearing ibBUSD token. The strategy reused BUSD-denominated amounts as if they were ibBUSD-denominated amounts, even though ibBUSD was worth more than one BUSD because it accrued yield.

That denomination mismatch let the attacker loop deposits and withdrawals with flash-loaned capital, causing the strategy to withdraw more BUSD-equivalent value from Alpaca than the bank expected and then leave the excess inside the strategy contract. On the next deposit, the leftover BUSD was reinvested and counted as apparent strategy yield. Repeating the loop inflated the attacker's share of the vault until the pool was drained.

Public loss estimates differ by methodology. Rekt described approximately $18 million drained from bEarn Fi, while other incident trackers commonly report roughly $11 million in net user loss. Both figures refer to the same core incident: the BUSD vault's accounting treated BUSD and ibBUSD as interchangeable and allowed flash-loan-sized loops to turn internal accounting error into withdrawable funds.

The bEarn Fi exploit matters for market-health analysis because it shows how stablecoin vaults can fail without any stablecoin depeg, oracle collapse, or private-key compromise. The assets were dollar-denominated, the yield source was a separate BSC protocol, and the exploit was created by a unit-conversion error between a vault token and its interest-bearing strategy token. In yield aggregators, "one share" and "one underlying token" are rarely the same thing. Treating them as equal can make a vault insolvent.

## 2. Background: bEarn Fi, bVaults, Alpaca, and ibBUSD

### 2.1 bEarn Fi and BSC yield aggregation

bEarn Fi was part of the 2021 Binance Smart Chain yield-aggregation wave. Users deposited assets into vaults, and the protocol routed those assets into external strategies to earn yield. This model promised convenience: users did not need to manually manage positions in Alpaca Finance or other protocols. The vault contract would deposit, harvest, reinvest, and track each user's share.

Yield aggregation creates a custody-accounting problem. The vault owes users an accurate claim on strategy assets, but those assets may be held as other tokens, staked in reward contracts, or represented by interest-bearing receipts. The accounting must consistently convert between user-facing assets and strategy-facing assets. If the conversion is wrong, the vault may report false yield, over-credit shares, or pay withdrawals from other users' capital.

### 2.2 Alpaca Finance ibBUSD

Alpaca Finance's ibBUSD is an interest-bearing receipt token. A user deposits BUSD into Alpaca and receives ibBUSD. Over time, ibBUSD appreciates relative to BUSD as interest accrues. That means 1 ibBUSD should not be assumed to equal 1 BUSD. The exchange rate is a core part of the token's design.

Interest-bearing tokens are common across DeFi:

- Compound uses cTokens.
- Aave uses interest-accruing/rebasing representations.
- Yearn vaults issue shares whose value changes over time.
- Alpaca issues ibTokens such as ibBUSD.

Every integration with such tokens must handle exchange rates explicitly. If a strategy deposits BUSD into Alpaca, receives ibBUSD, stakes ibBUSD, and later withdraws, it must know whether a function argument is denominated in BUSD or ibBUSD.

### 2.3 BvaultsBank and BvaultsStrategy split

The bEarn architecture separated the user-facing bank from the strategy implementation. The bank accepted BUSD deposits and withdrawals. The strategy invested the vault's BUSD into Alpaca, received ibBUSD, farmed with that ibBUSD, and redeemed ibBUSD back to BUSD when necessary.

This separation is normal. But it creates a contract boundary where units must be clear. The bank can pass "withdraw 7,804,239 BUSD" to the strategy. The strategy must then calculate how much ibBUSD needs to be withdrawn and redeemed to produce that BUSD amount. bEarn's strategy instead treated the same raw amount as ibBUSD in key internal operations.

That was the root of the exploit.

## 3. Vulnerability: inconsistent asset denomination

### 3.1 One amount, two meanings

Rekt summarized the bug as an inconsistent reading of the same input amount between BvaultsBank and BvaultsStrategy. The bank's withdrawal logic assumed the amount was BUSD. The strategy's withdrawal logic assumed the amount was ibBUSD.

Because ibBUSD was worth more than BUSD, withdrawing 7.8 million ibBUSD from Alpaca returned more than 7.8 million BUSD. The bank only sent the requested BUSD amount back to the attacker. The excess BUSD stayed in the strategy contract. The next deposit then swept that leftover into Alpaca and treated it as newly generated yield.

This is not a price manipulation bug in the usual sense. It is a denomination bug. The price of ibBUSD relative to BUSD was supposed to be greater than one. The problem was that bEarn's strategy failed to convert between the two units before using the amount.

### 3.2 False yield from leftover balances

The strategy's total value tracking was not resilient to unexpected leftovers. Instead of computing value purely from live balances and correct exchange rates, it could treat extra BUSD remaining in the contract as yield attributable to the strategy. When that "yield" was reinvested, the attacker's credited balance increased.

The exploit loop therefore converted an accounting mismatch into repeated apparent gains:

1. withdraw too much ibBUSD because a BUSD amount is treated as ibBUSD;
2. redeem excess BUSD;
3. return only the requested amount to the bank/user;
4. leave the excess in the strategy;
5. reinvest the excess on the next deposit; and
6. credit the strategy as though it earned yield.

When repeated with millions of flash-loaned BUSD, small percentage mismatches became a major drain.

### 3.3 Silent adjustment hid internal inconsistency

The Origin Protocol incident note on the bEarn exploit highlights another contributing factor: the contracts could switch to using actual available amounts when balances did not match accounting expectations rather than reverting. This made internal errors less visible. A system that silently adapts to inconsistent balances can continue appearing to work while its accounting drifts farther from reality.

For vault systems, failing closed is often safer than "helpfully" proceeding with a smaller or actual balance. If the contract believes it should have one amount and actually has another, that mismatch is a red-alert condition. Continuing can convert an accounting bug into exploitable state.

## 4. Attack flow

### 4.1 Flash-loan funding

The attacker used a flash loan from Cream with approximately 7,804,239 BUSD, according to the Rekt/PeckShield reconstruction. Flash loans provided the scale needed to make each loop profitable. The attacker did not need to own millions of BUSD; they only needed to repay the flash loan at the end.

This matters because a vault strategy must be safe against transient, transaction-scoped capital. If an exploit loop produces profit proportional to deposit size, flash loans turn it into a high-severity incident immediately.

### 4.2 Deposit into BvaultsBank

The attacker deposited the borrowed BUSD into BvaultsBank. The bank sent the funds to the associated BvaultsStrategy. The strategy deposited BUSD into Alpaca's BUSD vault and received ibBUSD. Rekt reports that a deposit of 7,804,239.111784605253208456 BUSD resulted in 7,598,066.589501626344403426 ibBUSD minted to the strategy.

This conversion already showed the important fact: ibBUSD and BUSD were not 1:1. Fewer ibBUSD represented the deposited BUSD because each ibBUSD was worth more than one BUSD.

### 4.3 Farming ibBUSD

The strategy farmed with the received ibBUSD through Alpaca FairLaunch. This step was part of the yield strategy. It also meant the strategy had to manage staked ibBUSD positions, not just liquid BUSD balances.

When a withdrawal came in, the strategy needed to know how much ibBUSD to unstake and redeem to produce a target amount of BUSD. That conversion was mishandled.

### 4.4 Withdrawal using the wrong unit

The attacker requested a withdrawal from BvaultsBank. The bank interpreted the withdrawal amount in BUSD. The strategy interpreted the raw withdrawal amount as ibBUSD. Rekt's example states that withdrawing 7,804,239.111784605253208533 BUSD was interpreted as withdrawing 7,804,239.111784605253208533 ibBUSD, equivalent to 8,016,006.09792806917101481 BUSD.

The bank then returned the requested BUSD to the attacker, while the extra BUSD remained in the strategy.

### 4.5 Reinvestment of leftovers as apparent yield

On the next round, the attacker deposited a similar amount into BvaultsBank. The strategy then had the new deposit plus leftover BUSD from the prior incorrect withdrawal. It invested all of that BUSD into Alpaca. Because the strategy's accounting treated the extra as yield, the attacker's withdrawable balance increased.

Each loop therefore ratcheted the accounting upward. The exploit did not depend on a single enormous miscalculation. It depended on repeated legal-looking deposit and withdrawal cycles that gradually converted denominator error into vault loss.

### 4.6 Exit and flash-loan repayment

After repeating the loop enough times, the attacker exited by draining the pool and repaid the flash loan. Rekt reports a flash-loan repayment of 7,806,580.383518140634784418 BUSD after fees. The remaining funds represented exploit profit.

The attack wallet identified in public reporting was `0x47f341d896b08daacb344d9021f955247e50d089`.

## 5. Market and user impact

### 5.1 Stablecoin vault losses

The affected users thought they were in a BUSD yield vault. A stablecoin vault can feel lower risk than volatile-token farming because the underlying asset is dollar-pegged. But stablecoin vault risk often comes from strategy accounting, not asset volatility. Here, BUSD itself did not fail. Alpaca's ibBUSD was behaving as an interest-bearing token. The loss came from bEarn's integration.

This is why "stablecoin APY" can be misleading. A stablecoin vault can still contain:

- smart-contract integration risk;
- share-token exchange-rate risk;
- strategy accounting risk;
- flash-loan exploitability;
- access-control and harvest risk; and
- cross-protocol dependency risk.

Users were exposed to all of those through a product marketed as yield aggregation.

### 5.2 BSC copy-code risk

The incident occurred during a period when BSC DeFi protocols were launching quickly and copying patterns from other ecosystems. Rekt framed the exploit as part of a broader wave of BSC protocols falling to hackers who exploited copied or insufficiently reviewed code.

The broader market-health issue is launch velocity. When protocols combine forked vault logic, external yield sources, interest-bearing tokens, and weak testing, they create hidden accounting assumptions. Those assumptions may survive normal use but fail under adversarial flash-loan loops.

### 5.3 Trust shock to yield aggregators

Yield aggregators depend on trust that their accounting is more reliable than a user managing strategies manually. A vault exploit undermines the core product. Even if a compensation plan exists, users must ask:

- Were all strategy integrations reviewed?
- Are other vaults using similar denomination assumptions?
- Does the protocol verify exchange rates for every interest-bearing token?
- Can internal accounting drift silently?
- Are emergency pauses fast enough?

The loss therefore affects more than one pool. It changes the perceived safety of the entire vault suite.

## 6. Controls that would have reduced the loss

### 6.1 Explicit unit types

The most direct control is to make units explicit in code. A value denominated in BUSD should not be passed into a function that expects ibBUSD without conversion. Contracts can enforce this with clear naming, internal libraries, and separate function signatures:

- `amountBusd`
- `amountIbBusd`
- `busdToIbBusd(amountBusd)`
- `ibBusdToBusd(amountIbBusd)`

While Solidity does not have native dependent types, disciplined naming and conversion boundaries reduce the risk of raw integer reuse.

### 6.2 Live exchange-rate conversion

Every deposit and withdrawal involving ibBUSD should query or compute the current exchange rate. The strategy should calculate how much ibBUSD is needed to redeem a target BUSD amount, including rounding and fees. It should also test edge cases where exchange rate changes between deposit and withdrawal.

For interest-bearing tokens, exchange-rate conversion is not optional. It is the accounting core.

### 6.3 Balance reconciliation and fail-closed behavior

If a strategy expects to receive exactly one amount and receives another, it should reconcile explicitly or revert. Unexpected leftover balances should not automatically become yield. A robust strategy can compute total value from live balances plus exchange rates, but it should not let arbitrary leftovers change user shares without a controlled harvest/reconciliation step.

Failing closed would have exposed the mismatch early. Silent adjustment allowed the exploit loop to continue.

### 6.4 Invariant tests over deposit/withdraw loops

The exploit was a loop, so testing should be loop-aware. A useful invariant is:

> Repeated deposit and withdrawal cycles with no real external yield cannot increase an attacker's net withdrawable balance, even when strategy tokens accrue value and flash-loan-sized deposits are used.

Tests should include:

- interest-bearing token exchange rates above 1;
- repeated deposit/withdraw cycles;
- leftover balances in strategy contracts;
- staking and unstaking receipt tokens;
- flash-loan-sized amounts;
- rounding edge cases; and
- scenarios where actual balances differ from accounting balances.

Unit tests that only check one deposit and one withdrawal at a 1:1 exchange rate would miss the bug.

### 6.5 Strategy isolation

Vaults should isolate strategy failures. If one strategy produces impossible yield or abnormal accounting deltas, the vault should pause that strategy and prevent reinvestment. A monitor could detect that a strategy generated hundreds of thousands of BUSD of "yield" immediately after a user deposit/withdraw loop with no corresponding external reward event.

The correct response to impossible yield is not to distribute it. It is to halt and investigate.

## 7. Market-health indicators

### 7.1 Interest-bearing token mismatch

Protocols integrating receipt tokens should be scanned for raw amount reuse. If a strategy passes an underlying amount into a receipt-token withdrawal function without exchange-rate conversion, the risk is high. This applies to ibTokens, cTokens, vault shares, LP tokens, and other wrapper assets.

### 7.2 Apparent yield spikes after user loops

A vault's yield should not spike because one user repeatedly deposits and withdraws. Monitoring should flag:

- large deposits followed by immediate withdrawals;
- strategy yield increases during those loops;
- leftover underlying balances in strategy contracts;
- repeated loops in one transaction; and
- flash-loan funding.

These are strong signs of accounting exploitation.

### 7.3 Internal accounting divergence

If `wantLockedTotal` or similar internal totals diverge from live strategy value, the vault should pause. Market-health tooling should compare internal totals against:

- underlying token balances;
- receipt-token balances multiplied by exchange rate;
- staked receipt-token balances;
- pending rewards; and
- debt or fees.

Any unexplained divergence is potential false yield.

### 7.4 Weekend and low-monitoring windows

Rekt noted the recurring weekend pattern in DeFi exploits. Whether or not attackers deliberately prefer weekends, protocols should assume monitoring coverage will be tested during low-attention periods. Automated controls must be strong enough to act without manual review.

## 8. Broader implications for yield vaults

### 8.1 Strategy tokens are not underlying tokens

The central lesson is simple: a strategy token is not the underlying token unless the protocol explicitly guarantees 1:1 redemption at all times. ibBUSD was designed to appreciate. Treating it as BUSD erased the very yield mechanism the strategy relied on.

Yield vaults often integrate multiple assets with similar symbols and different denominations. The more layers a vault uses, the more dangerous raw integer accounting becomes.

### 8.2 False yield is a solvency risk

False yield is worse than no yield. If a vault reports yield that does not exist, it can overpay withdrawals, overmint shares, or distribute other users' principal. The bEarn exploit repeatedly created apparent yield from leftover balances generated by the denomination mismatch. That apparent yield became the attacker's profit.

Protocols should treat unexpected yield with skepticism. Yield should be traceable to rewards, interest accrual, trading fees, or other legitimate sources.

### 8.3 External strategy integrations require adversarial review

Integrating Alpaca was not inherently unsafe. The unsafe part was failing to model Alpaca's ibBUSD denomination correctly. Every external strategy integration should be reviewed as a new accounting system, not just a token transfer destination.

Questions to ask:

- What token does the strategy receive?
- What token does it return?
- Does the receipt token appreciate or rebase?
- Are exchange rates queried correctly?
- Can leftovers accumulate?
- How is total value computed?
- What happens if withdrawal returns more or less than expected?

The bEarn incident shows that missing one of these answers can drain an entire vault.

## 9. Timeline

- **Before 16 May 2021**: bEarn Fi operates BSC bVaults, including a BUSD vault strategy that deposits into Alpaca and handles ibBUSD.
- **16 May 2021, 10:36:20 UTC**: The attacker begins exploiting BvaultsBank and BvaultsStrategy.
- **Attack loop**: The attacker flash-borrows about 7.8 million BUSD from Cream, deposits into BvaultsBank, receives ibBUSD through Alpaca, withdraws with a BUSD amount misinterpreted as ibBUSD, leaves excess BUSD in the strategy, and repeats the cycle.
- **Exit**: The attacker drains the pool and repays the Cream flash loan with fees.
- **Aftermath**: Public reports estimate the loss at roughly $11 million to $18 million depending on measurement. bEarn pauses vaults, investigates, and announces compensation plans.

## 10. Lessons for market participants

For users, bEarn Fi shows that stablecoin vaults can fail because of strategy accounting even when the stablecoin and yield source remain functional. A high APY on BUSD does not eliminate smart-contract denomination risk.

For builders, the lesson is to treat every wrapper token as a separate unit with an exchange rate. Never pass underlying-token amounts into receipt-token functions without conversion. Reconcile live balances, fail closed on accounting mismatches, and test repeated flash-loan-sized deposit/withdraw loops.

For analysts, the incident provides a monitoring template: scan for 1:1 assumptions around interest-bearing tokens, compare strategy internal totals with live exchange-rate-adjusted balances, flag apparent yield spikes after user loops, and watch for leftover balances being reinvested as if they were earned yield.

The bEarn Fi exploit was therefore not just a BSC flash-loan attack. It was a unit-accounting failure. The vault confused BUSD with ibBUSD, and that small conceptual error was enough to turn yield aggregation into a multimillion-dollar drain.

## References

- Rekt, [bEarn - Rekt](https://rekt.news/bearn-rekt)
- Origin Protocol Security, [2021-05-16 BearnFi Vault Attack](https://github.com/OriginProtocol/security/blob/master/incidents/2021-05-16-BearnFi.md)
- BscScan, [publicly reported bEarn attack transaction](https://bscscan.com/tx/0x6bf610ecaf2f89f41bcad7aca4646199430839e7cf979fbcafa896e5126361d1)
- BscScan, [Origin Protocol referenced bEarn attack transaction](https://bscscan.com/tx/0x603b2bbe2a7d0877b22531735ff686a7caad866f6c0435c37b7b49e4bfd9a36c)
- BscScan, [attacker wallet](https://bscscan.com/address/0x47f341d896b08daacb344d9021f955247e50d089)
- BscScan, [Alpaca ibBUSD token](https://bscscan.com/token/0x7c9e73d4c71dae564d41f78d56439bb4ba87592f)
