---
title: "🌰 PancakeBunny — Flash-Loan LP Oracle Manipulation and BUNNY Collapse"
date: 2026-05-05
entities:
  - PancakeBunny
  - BUNNY
  - PancakeSwap
  - Binance Smart Chain
  - WBNB
  - USDT
---

## Summary

1. **On May 19, 2021, PancakeBunny suffered a flash-loan-driven oracle manipulation on Binance Smart Chain**, allowing an attacker to exploit the protocol's reward minting logic and extract roughly $40-45 million in value.
2. **The exploit manipulated PancakeSwap pool reserves used by PancakeBunny's LP-token price calculation**, especially WBNB/USDT and BUNNY/BNB paths. The protocol treated a short-lived AMM reserve distortion as if it were durable value.
3. **The attacker used multiple flash loans to temporarily reshape pool balances**, then called `VaultFlipToFlip.getReward()` so the `BunnyMinterV2` logic minted an excessive amount of BUNNY. Public technical writeups report approximately 6.97 million BUNNY minted in the attack path.
4. **The market impact was rapid and severe**: the attacker sold newly minted BUNNY into the market, and BUNNY's price dropped from triple-digit levels to single digits in a short window. PancakeBunny's total value locked and user confidence also fell sharply.
5. **The incident is a useful market-health case because it linked AMM spot-price manipulation, LP valuation, protocol reward minting, flash loans, and governance-token reflexivity.** The direct exploit was a smart-contract/oracle bug, but the economic damage was transmitted through token supply inflation and market selling pressure.

## Background

### PancakeBunny

PancakeBunny was a yield aggregator on Binance Smart Chain. Users deposited assets and PancakeSwap LP tokens into vaults, and the protocol optimized farming strategies on their behalf. PancakeBunny charged performance fees on profits, and part of the incentive model rewarded users with the protocol's native BUNNY token.

The key design feature was that reward minting depended on the protocol's estimate of value. If the protocol believed a vault had generated fees worth a large amount of BNB, the minter could issue BUNNY tokens proportional to that value.

### Why LP Pricing Was Dangerous

PancakeBunny needed to value PancakeSwap LP tokens. A common but risky approach is to infer LP value from AMM reserves:

| Input | Why It Is Risky |
|------|-----------------|
| Pool reserves | Can be moved temporarily by large swaps |
| Spot price | Can be manipulated within a single transaction |
| LP total supply | May not reflect manipulated reserve composition safely |
| Single-venue liquidity | Gives attackers a clear market to manipulate |
| Reward minting tied to value | Converts temporary price distortion into token inflation |

Flash loans make this especially dangerous. They let an attacker borrow very large amounts of capital for one transaction, move AMM reserves, trigger the vulnerable calculation, unwind enough to repay the loan, and keep the extracted value.

## Timeline

| Date / Time | Event |
|------------|-------|
| May 19, 2021 | Attacker executes the exploit transaction on Binance Smart Chain |
| May 19, 2021 | Multiple flash loans are taken from PancakeSwap pools and ForTube Bank |
| May 19, 2021 | WBNB/USDT and BUNNY-related pool prices are manipulated during the transaction |
| May 19, 2021 | `VaultFlipToFlip.getReward()` triggers excessive BUNNY minting through `BunnyMinterV2` |
| May 19, 2021 | Newly minted BUNNY is sold into the market, causing a rapid price collapse |
| May 19-21, 2021 | PancakeBunny pauses and later restores vault deposit/withdrawal functionality |

DN Institute's incident page records the exploit transaction at 10:34 PM UTC on May 19, 2021, official confirmation around 11:18 PM UTC, and vault functionality restored on May 21.

## Attack Mechanics

### Step 1: Assemble Temporary Capital

Public writeups describe the attacker using eight flash loans: seven from PancakeSwap pools and one from ForTube Bank. Rekt lists large WBNB loans from multiple PancakeSwap pairs plus a USDT loan from ForTube.

This capital was not long-term risk capital. It existed only inside the exploit transaction and was used to distort the pools that PancakeBunny trusted for valuation.

### Step 2: Distort PancakeSwap Reserves

The attacker manipulated reserves in WBNB/USDT and related pools. The important effect was that PancakeBunny's price calculator saw LP tokens as far more valuable than they would be under normal market conditions.

cmichel's technical postmortem describes the core weakness as a wrong PancakeSwap LP price computation in `PriceCalculatorBSCV1`. The vulnerable calculation valued LP tokens using reserve balances that could be manipulated during the same transaction.

### Step 3: Trigger Reward Minting

The attacker had a small existing position in the relevant vault and then called `VaultFlipToFlip.getReward()`. That function calculated a performance fee and called into `BunnyMinterV2.mintForV2()`.

The reward minting path depended on valuing LP tokens and converting that value into BUNNY issuance. Once the manipulated LP price entered the calculation, the minter produced a huge number of BUNNY tokens for the attacker.

Public reports differ slightly in formatting, but the common figure is approximately 6.97 million BUNNY minted. Rekt also noted a separate developer-team mint in the same flow; for market-health analysis, the key point is that the attacker-induced value calculation created sudden BUNNY supply far beyond normal emissions.

### Step 4: Dump BUNNY and Repay Loans

After receiving the newly minted BUNNY, the attacker sold it into the market for WBNB/BNB. The flash loans were repaid, and the attacker retained the profit.

This final sale transformed an oracle/accounting exploit into visible market damage:

- BUNNY supply increased abruptly.
- Sell pressure hit relatively thin BUNNY liquidity.
- The BUNNY/BNB price fell sharply.
- Users who held or farmed BUNNY absorbed the market impact.

## Root Cause

### Manipulable LP Valuation

The core failure was not simply "flash loans are dangerous." Flash loans were the funding mechanism. The root vulnerability was that PancakeBunny used a manipulable on-chain AMM reserve state to price LP assets for reward minting.

cmichel highlights the relevant `PriceCalculatorBSCV1.valueOfAsset()` pattern: for LP tokens, value was derived from token reserves and LP total supply. If an attacker could distort the reserve side of that formula, the protocol would overestimate the LP token's value.

The same design class appears in other DeFi incidents:

| Design Pattern | Risk |
|---------------|------|
| LP value = reserves / total supply | Reserves can be manipulated temporarily |
| Spot AMM price as oracle | One transaction can move it |
| Reward issuance based on spot value | Temporary manipulation becomes permanent token inflation |
| No TWAP / external price check | No dampening of short-lived reserve distortion |
| Minting before settlement checks | Protocol cannot claw back after price normalizes |

### Reflexive Governance Token Emissions

BUNNY was both a reward token and a market-traded asset. That made the exploit reflexive:

1. Manipulated LP value caused excessive BUNNY minting.
2. Excessive BUNNY minting increased circulating supply.
3. The attacker sold BUNNY for WBNB/BNB.
4. BUNNY price fell sharply.
5. Lower BUNNY price reduced confidence and damaged the protocol's incentive model.

This is different from a pure vault drain. The attack damaged the market instrument that represented protocol incentives and governance.

## Market Impact

### BUNNY Price Collapse

Rekt reports BUNNY falling from about $146 to about $6 after the attacker sold the minted tokens. Other summaries describe a drop of more than 90-95%. Exact price snapshots vary by source and timestamp, but public accounts consistently describe a rapid token-price collapse.

For market-health purposes, the important signal is the path:

- supply shock from unauthorized minting;
- rapid market sell pressure;
- loss of confidence in reward-token economics;
- liquidity provider and vault user withdrawals;
- reduced protocol TVL.

### TVL and Confidence

Rekt reported PancakeBunny had previously reached more than $10 billion in TVL and was near $1 billion at the time of its writeup after the exploit. Those numbers should be treated as approximate, but the direction was clear: the exploit caused a major confidence shock.

Because yield aggregators depend on trust in strategy accounting and token incentives, a reward-token collapse can be as damaging as a direct pool loss. Users may withdraw even if their specific vault assets were not directly drained, because future rewards and protocol solvency assumptions have changed.

### Binance Smart Chain Context

The incident occurred during a period of intense DeFi growth on Binance Smart Chain. BSC protocols offered high yields, fast transactions, and lower fees than Ethereum, but many protocols reused AMM/oracle patterns that were vulnerable to flash-loan manipulation.

PancakeBunny's exploit became one of the clearest examples of BSC's 2021 flash-loan/oracle-manipulation wave: attackers could use low-cost, high-throughput execution and large AMM liquidity to manipulate local pricing assumptions inside a single transaction.

## Why the Attack Was Hard to Resist

### Flash Loans Removed Capital Constraints

Traditional market manipulation requires capital at risk. Flash loans change that. The attacker only needed the transaction to be profitable after fees and loan repayment. If the transaction failed, the whole transaction reverted.

This makes protocols that trust same-block AMM prices especially fragile:

- the attacker can borrow huge size;
- move the oracle-relevant pool;
- trigger the vulnerable function;
- unwind or repay;
- keep profit if the protocol minted or transferred durable value.

### Reward Logic Amplified the Price Error

The exploit was not just "price too high." The wrong price entered a formula that minted BUNNY at scale. A temporary valuation error became a permanent token-supply event.

This amplification is a key surveillance point. Protocols should rank oracle risk higher when manipulated prices feed:

- token minting;
- borrowing capacity;
- liquidation thresholds;
- performance fee payouts;
- share-price accounting;
- governance-token emissions.

### Single-Transaction Atomicity Hid the Risk

Outside observers could see the attack only after it executed. Inside one atomic transaction, the attacker could create, exploit, and remove much of the manipulated state. This compresses the detection window to milliseconds.

That is why prevention matters more than reactive monitoring for this class of exploit.

## Surveillance Framework

### Pre-Exploit Design Metrics

| Metric | Warning Signal |
|-------|----------------|
| Reward minting depends on AMM spot price | High risk |
| LP pricing uses current reserves directly | High risk |
| No TWAP or external oracle | High risk |
| Flash-loan accessible liquidity exceeds pool depth | High risk |
| Reward token liquidity is thin relative to possible mint size | High market-impact risk |
| Performance fees trigger token emissions | Mint amplification risk |

### Real-Time Signals

| Signal | Interpretation |
|-------|----------------|
| Multiple large flash loans in one transaction | Possible manipulation setup |
| Large reserve skew in oracle-referenced pools | Spot-price distortion |
| Reward claim soon after reserve skew | Oracle exploit path |
| Sudden protocol-token mint | Supply shock |
| Large sell of newly minted protocol token | Market-impact realization |
| Vault pause announcement | Incident confirmation or mitigation |

### Post-Incident Accounting

Analysts should separate:

- attacker profit in WBNB/BNB;
- number of BUNNY minted;
- value of BUNNY at pre-attack spot price;
- realized sale proceeds;
- BUNNY holder mark-to-market loss;
- vault user direct loss;
- TVL withdrawals caused by confidence loss.

This distinction matters because "loss" figures vary. Some sources quote $40M+, others around $45M, while technical writeups may describe 114,631 WBNB profit and millions of BUNNY minted. These are related but not identical measurements.

## Comparison With Related Incidents

| Incident | Manipulated Input | Durable Output |
|---------|-------------------|----------------|
| PancakeBunny | PancakeSwap LP reserve-derived value | Excess BUNNY mint and sale |
| Warp Finance | LP-token valuation from manipulable reserves | Under-collateralized borrowing |
| Harvest Finance | Curve pool state | Vault withdrawal profit |
| bZx | DEX spot price | Bad loan / arbitrage extraction |
| Mango Markets | MNGO oracle price | Borrowing against inflated perp PnL |

The common theme is that protocols accepted a temporary market state as durable economic value. PancakeBunny's version was especially reflexive because the durable output was new supply of the protocol's own token.

## Defensive Checklist

Protocols that mint rewards or calculate fees from LP values should implement:

1. **TWAP or time-delayed pricing** instead of same-block AMM spot reserves.
2. **External oracle cross-checks** for major assets such as BNB, USDT, and protocol tokens.
3. **Mint caps per block / per transaction** for governance and reward tokens.
4. **Circuit breakers** when reward claims imply abnormal token issuance.
5. **Flash-loan-resistance tests** that simulate reserve manipulation inside one transaction.
6. **Liquidity-aware token emission limits** so mint size cannot exceed plausible market absorption.
7. **Separate fee accounting from reward minting** where possible.
8. **Post-mint sell monitoring** for newly minted protocol-token supply.

## Key Takeaways

1. **Flash loans are accelerants, not root causes.** The vulnerable design is trusting manipulable same-block market state.
2. **LP tokens are hard to price safely.** Reserve-based formulas can be wrong when reserves are temporarily distorted.
3. **Reward minting turns oracle errors into supply shocks.**
4. **Protocol-token liquidity matters.** A mint exploit becomes a market crash when the attacker sells into thin liquidity.
5. **Gross exploit value, token-holder losses, and attacker profit are different measurements.**
6. **Market surveillance should connect flash loans, pool reserve changes, token mint events, and rapid sell pressure.**

## References

- Rekt, "PancakeBunny" (May 2021).
- cmichel, "BSC PancakeBunny Exploit Post Mortem" (May 2021).
- DN Institute incident page, "PancakeBunny" (2021-05-19).
- PeckShield, "PancakeBunny Incident: Root Cause Analysis" (May 2021).
- PancakeBunny team incident updates, May 2021.
