---
title: "Plouto Vault YPool Liquidity Manipulation"
date: 2020-12-16
entities:
  - Plouto
  - Plouto Vault
  - Curve YPool
  - Aave
  - Uniswap V2
  - USDC
  - USDT
  - DAI
---

## Summary

Plouto Vault was hit by a flash-loan-funded liquidity manipulation that turned a temporary Curve YPool imbalance into vault profit extraction. BlockSec reported that its monitoring system detected a series of malicious transactions on December 16, 2020. Across eight transactions, the attacker extracted about $698,775.32, with the largest single transaction producing about 175,669.88 USD of profit.

The attack is a useful market-health case because the manipulated signal was not an order-book quote or a long-lived token price. It was a temporary pool-composition change. Plouto Vault's minted-token amount depended on the corresponding token amount in YPool, so a one-transaction liquidity imbalance could change the accounting result seen by the vault.

The main warning signs were:

1. vault accounting dependent on a manipulable AMM pool state,
2. large flash-loan inputs compared with the profit target,
3. same-transaction borrowing, pool distortion, repayment, and profit extraction,
4. repeated transactions from the same attacker address and malicious contract,
5. profit realized in stablecoins after the pool state was used by the vault.

## Incident Metrics

The supporting dataset is stored in [`plouto-attack-metrics.csv`](plouto-attack-metrics.csv). It separates funding, manipulated venue, repayment, and profit signals so the case can be compared against other liquidity-manipulation incidents.

| Metric                     |                      Value | Market-health interpretation                                                           |
| -------------------------- | -------------------------: | -------------------------------------------------------------------------------------- |
| Aave flash loan            |             9,000,000 USDC | Temporary same-transaction liquidity funded the market move.                           |
| Uniswap V2 flash loan      |             2,000,000 USDT | A second venue supplied additional stablecoin notional.                                |
| Manipulated venue          | Curve YPool USDT liquidity | The accounting dependency was a pool composition variable, not an external price feed. |
| Largest transaction profit |             175,669.88 USD | The largest cycle converted a transient pool state into DAI profit.                    |
| Total extracted value      |             698,775.32 USD | BlockSec counted eight transactions using the same attack pattern.                     |
| Affected assets            |            USDC, USDT, DAI | The protocol's stablecoin vaults were the loss surface.                                |

## Attack Flow

BlockSec describes one representative transaction as a ten-step sequence. The attacker first borrowed 9,000,000 USDC from Aave, then borrowed 2,000,000 USDT from Uniswap V2. The attacker used that capital to manipulate USDT liquidity in Curve's YPool, interacted with Plouto Vault while the manipulated pool state was active, and then repaid the flash loans.

In the transaction BlockSec highlighted, the attacker repaid 2,006,200 USDT to Uniswap V2, swapped 17,298 USDT for 17,320 USDC to help repay the Aave leg, repaid 9,008,100 USDC to Aave, and finally swapped 177,533 USDC for 175,669 DAI that was sent to the attacker's externally owned account.

Plouto's public statement, published after its investigation, said the protocol's USDC, USDT, and DAI vaults lost more than $700,000 and identified the attacker address as `0x43c16293f319f424A6B277115A4A9Eb2Dbc327d1`. BlockSec's later analysis identified the same attacker prefix, one malicious contract, and eight transactions matching the liquidity-manipulation pattern.

## Why The Market Signal Failed

The root problem was treating a pool state that could be changed with temporary capital as if it were a reliable valuation input. In the ProMutator paper's taxonomy, Plouto Finance is grouped with 2020 price-oracle attacks that used flash loans and AMM price-related functions. The paper classifies the Plouto case as involving Aave, Uniswap V2, Curve, the `calc_withdraw_one_coin` function, DAI as the target asset, and about $700,000 of loss.

For market-health analysis, the important detail is the dependency chain:

1. flash-loan capital changed Curve YPool composition,
2. Plouto Vault logic read or depended on the manipulated pool state,
3. vault minting/accounting produced a favorable result for the attacker,
4. the attacker unwound the funding legs and kept the stablecoin profit.

This is different from ordinary arbitrage. Healthy arbitrage usually narrows a price discrepancy between venues and leaves a durable market correction. Here, the pool state was deliberately bent to influence another protocol's accounting, then the transaction exited with the accounting victim holding the loss.

## Market-Health Indicators

### 1. Pool-composition dependency

The manipulated variable was USDT liquidity in YPool. Any vault that mints or redeems shares based on a single pool's current balance should be treated as exposed to pool-composition manipulation, even if the assets involved are all stablecoins.

Curve-style stable pools are especially subtle because a balanced pool can make all assets look close to par while still allowing the balance vector and one-coin withdrawal quotes to move sharply under temporary capital. A monitor for this class of vault should therefore watch pool composition, `calc_withdraw_one_coin` output, and vault mint/redeem output together. A rule that only checks whether USDC, USDT, and DAI are near 1 USD can miss the real failure mode.

Monitoring should also vary by pool design. A deep, high-amplification stable pool can tolerate small balance shifts without making vault accounting unsafe, but a vault that reads the current pool state should still flag any same-block balance move that changes the dependent mint/redeem quote by more than 0.5% or that changes one stablecoin's pool share by more than 5 percentage points before the vault action executes. Lower-liquidity or lower-amplification pools should use tighter thresholds because the same borrowed notional creates a larger quote displacement.

### 2. Flash-loan notional concentration

The representative transaction used 9,000,000 USDC from Aave and 2,000,000 USDT from Uniswap V2. A monitoring rule should compare the notional used to change the pool with normal pool volume and with the profit or mint amount obtained from the dependent vault.

The representative transaction used about 11,000,000 USD of temporary funding to extract 175,669.88 USD of profit, or about 1.6% of the borrowed notional. The explicit flash-loan repayment premium was much smaller: 8,100 USDC to Aave and 6,200 USDT to Uniswap V2, about 14,300 USD before the repayment-supporting swap. Profit that is more than 10x the visible flash-loan premium after a same-transaction vault interaction is a practical alert threshold because it indicates the vault, not ordinary stablecoin routing, is paying the spread.

A conservative production rule would flag a vault interaction when all three conditions are true in one transaction: borrowed notional exceeds 10x the user's recent median vault interaction size, the dependent pool quote changes by more than 0.5% before the vault call, and realized profit exceeds 0.5% of temporary notional after repayments. Plouto's representative transaction would satisfy that pattern even without knowing the attacker's intent.

### 3. Same-transaction lifecycle

The transaction contained the whole lifecycle: borrow, distort, interact with the victim vault, restore enough liquidity to repay lenders, and convert the remaining value to DAI. This compact lifecycle is a strong indicator of manipulation rather than user-driven liquidity migration.

### 4. Repeated attacker pattern

BlockSec reported eight transactions launched by the same attacker address through one malicious contract. Repeated successful extraction from the same accounting dependency suggests the first transaction should have triggered an emergency pause or at least a vault-specific circuit breaker.

The eight-transaction series implies a failure in response granularity as well as in price validation. After transaction one, a vault-specific circuit breaker could have paused new mint/redeem paths for the affected USDC, USDT, and DAI vaults while leaving unrelated vaults alone. After transaction two, even a slower off-chain monitor should have been able to identify the same malicious contract, the same borrowed-liquidity pattern, and the same final stablecoin profit realization.

The likely failure modes are common in early vault designs: no per-vault loss or profit-outlier threshold, no automatic pause tied to pool-balance displacement, no same-block flash-loan heuristic, and governance or operator latency that was longer than the attacker's repeat cycle. The immediate mitigation would have been to stop only the affected vault adapters, freeze minting against the manipulated YPool dependency, and require manual review before re-enabling the strategy.

### 5. Profit realization in stablecoins

The warning-sign list ends with profit realized in stablecoins because that is where the extraction becomes measurable. In the representative transaction, the attacker converted 177,533 USDC into 175,669 DAI after repaying the funding legs. A stablecoin-denominated terminal balance is a strong post-condition for this incident type: the attacker is not holding directional risk in PLT or another volatile token, but has converted the accounting error into portable value.

On-chain monitors should therefore link the whole path rather than alert on the vault call alone. The sequence of borrowed stablecoins, YPool composition change, Plouto interaction, flash-loan repayment, and final DAI transfer to the attacker's externally owned account is more specific than any single step. That pattern separates malicious extraction from a benign user who deposits or withdraws during a volatile stablecoin pool rebalance.

## Controls That Would Have Reduced The Risk

Plouto's case points to controls that apply to stablecoin vaults and asset managers that depend on AMM pools:

- Use delayed or time-weighted accounting inputs instead of immediate pool balances.
- Add per-block and per-transaction caps on vault minting or redemption when pool composition changes abruptly.
- Treat stablecoin pool imbalances as risk events, not just price-neutral swaps.
- Require a cooldown between large pool changes and vault interactions that rely on the changed pool.
- Monitor for transactions that borrow from Aave or Uniswap V2 and interact with the same vault before repayment.
- Pause vault strategies when a single address repeats profitable manipulation cycles.

## References

- [BlockSec: Flash Loan Attack on Plouto Vault](https://blocksec.com/blog/flash-loan-attack-on-plouto-vault)
- [Plouto: Plouto Was Attacked By Flashloan](https://ploutoprotocol.medium.com/plouto-was-attacked-by-flashloan-c309161c6281)
- [Etherscan attacker address](https://etherscan.io/address/0x43c16293f319f424A6B277115A4A9Eb2Dbc327d1)
- [Etherscan transaction from Plouto statement](https://etherscan.io/tx/0xb4dd46d5d85a1b04fa4af30efaa57fab98ea03ae19de46aaf215706fd120af44)
- [ProMutator: Detecting Vulnerable Price Oracles in DeFi by Mutated Transactions](https://www.csie.ntu.edu.tw/~hchsiao/pub/2021_IEEE_SB_ProMutator.pdf)
