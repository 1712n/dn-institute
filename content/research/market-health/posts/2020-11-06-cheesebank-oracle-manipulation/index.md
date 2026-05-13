---
title: "Cheese Bank Oracle Manipulation on Uniswap"
date: 2020-11-06
entities:
  - Cheese Bank
  - CHEESE
  - Uniswap
  - dYdX
  - USDC
  - USDT
  - DAI
---

## Summary

Cheese Bank was drained for about $3.3 million on November 6, 2020 after an attacker used a dYdX flash loan to manipulate the Uniswap market that Cheese Bank used as an on-chain price source. The incident is useful for market-health monitoring because the loss was not caused by a long-lived organic repricing of CHEESE. It was a one-transaction reserve shock that became a credit limit inside a lending protocol.

The attacker borrowed 21,000 ETH, used part of it to acquire CHEESE and create CHEESE-ETH LP collateral, then pushed the Uniswap pool into a temporarily distorted state. Cheese Bank's oracle refresh used the manipulated pool balance to value the LP token. With that inflated collateral value, the attacker borrowed the stablecoins held by the protocol, unwound the market move, repaid the flash loan, and kept the drained assets.

The clearest warning signs were:

1. a collateral valuation tied to a single AMM pool,
2. an oracle refresh callable inside the same atomic transaction as the market move,
3. a flash-loan-funded trade size far larger than ordinary pool depth,
4. stablecoin borrowing that consumed nearly the full balances available in Cheese Bank,
5. a price move that reverted once the attacker completed the round trip.

## Incident Metrics

The supporting dataset is stored in [`cheesebank-attack-metrics.csv`](cheesebank-attack-metrics.csv). It normalizes the public incident numbers into market-health fields that can be checked against future lending markets.

| Metric                   |                                      Value | Market-health interpretation                                                                                         |
| ------------------------ | -----------------------------------------: | -------------------------------------------------------------------------------------------------------------------- |
| Flash loan principal     |                                 21,000 ETH | Temporary capital large enough to dominate the referenced pool should be treated differently from durable liquidity. |
| Initial CHEESE purchase  |                  50 ETH for 107,232 CHEESE | The attacker first prepared collateral inventory before inflating the pool.                                          |
| LP collateral seed       |               107,232 CHEESE plus 78.8 ETH | The collateral token was tied directly to the pool that would later be distorted.                                    |
| Price-impact leg         |                     20,000 ETH into CHEESE | A single transaction changed the observable reserve state used by the oracle.                                        |
| Reported LP value change |                                 about 300x | A collateral value jump of this size should trigger a circuit breaker or manual review.                              |
| Borrowed stablecoins     | 2,000,000 USDC, 1,230,000 USDT, 87,000 DAI | The borrow flow consumed the protocol's stablecoin liquidity rather than reflecting normal demand.                   |
| Estimated loss           |                         about $3.3 million | Stablecoin losses show the manipulated collateral value was accepted as borrowable value.                            |

## Attack Flow

PeckShield traced the exploit to one transaction at `19:22:21 UTC` on November 6, 2020. The transaction was initialized by a malicious contract and funded with a 21,000 ETH flash loan from dYdX.

The attacker first swapped 50 ETH for roughly 107,232 CHEESE on Uniswap V2. They then paired those CHEESE tokens with 78.8 ETH to mint CHEESE-ETH LP tokens and used that LP position as Cheese Bank collateral.

The manipulation leg came next. The attacker swapped 20,000 ETH into CHEESE, forcing the CHEESE-ETH Uniswap pool into an abnormal reserve state. Cheese Bank's oracle was then refreshed while that state was active. The relevant LP pricing logic derived the LP value from the WETH balance in the Uniswap CHEESE-ETH pair, the ETH price, and LP token supply. This meant a temporary increase in the pool's WETH side could be converted into a higher reported LP-token price.

Once the LP collateral was overvalued, the attacker borrowed the protocol's stablecoin balances. PeckShield reported the drained amounts as about 2 million USDC, 1.23 million USDT, 87,000 DAI, and a small ETH remainder. The attacker then sold the CHEESE back for almost 20,000 ETH, converted 58,812 USDC to 132 ETH to cover execution costs, consolidated the proceeds, and repaid the flash loan.

The market signal is important: the apparent CHEESE and LP repricing did not survive the transaction. It was an atomic manipulation of the measurement venue, not a broad repricing across independent venues.

## Why The Price Feed Failed

Cheese Bank used an AMM-derived oracle for a lending decision. That makes the referenced pool a control surface. If the price feed observes a reserve state that an attacker can reshape with borrowed capital, the lending protocol inherits the AMM's weakest moment.

The risky pattern was not simply "using Uniswap." The risky pattern was accepting a fresh, manipulable spot state as collateral value without enough friction:

- no time-weighted average price window,
- no independent price source,
- no delay between oracle refresh and borrowing,
- no liquidity-adjusted haircut for LP collateral,
- no cap on the amount of stablecoins borrowable immediately after a sharp collateral repricing.

The ProMutator paper classifies Cheese Bank as a 2020 oracle manipulation case involving dYdX, Uniswap V2, the `balanceOf`-style measurement of the CHEESE-WETH LP, and a $3.3 million loss. It also notes why this case is more subtle than some single-call oracle failures: Cheese Bank updated token prices through stored state, so the exploit depended on calling refresh at the right point in the transaction.

## Market-Health Indicators

### 1. Same-block price shock

A collateral price that moves hundreds of percent or more within one transaction should be separated from normal price discovery. The Cheese Bank move was created by a large temporary ETH inflow and then unwound. Monitoring should flag reserve changes where the input capital is returned or nearly returned before transaction end.

### 2. Pool depth mismatch

The attack used 20,000 ETH to move the CHEESE market after seeding LP collateral with only 78.8 ETH and 107,232 CHEESE. That mismatch between collateral seed size and manipulation notional is a signal that the pool is being used as a measuring instrument rather than as a durable liquidity venue.

### 3. Full-balance borrowing

The attacker borrowed the exact available balances of USDC, USDT, and DAI. Full-utilization borrowing immediately after an oracle refresh is a strong sign that the borrower is exploiting a transient valuation rather than taking a risk-managed loan.

### 4. Round-trip recovery

After the stablecoins were borrowed, the attacker swapped the manipulated CHEESE inventory back to ETH and repaid the 21,000 ETH flash loan. A reserve shock followed by same-transaction reversion is a concise signature for flash-loan oracle manipulation.

## Controls That Would Have Reduced The Risk

Cheese Bank's loss points to several controls that lending protocols can apply before listing thin or reflexive collateral:

- Use TWAP oracles with a window long enough to make manipulation expensive across blocks.
- Require independent prices from more than one venue for collateral that can be borrowed against.
- Add a cooldown between a large oracle update and high-value borrowing.
- Cap borrow amounts after abrupt reserve changes, especially for assets with shallow liquidity.
- Haircut LP collateral using exit liquidity, slippage, and pool concentration rather than only an instantaneous reserve-derived value.
- Alert when a transaction both changes the referenced AMM reserves and borrows against the changed valuation.

## References

- [PeckShield: Cheese Bank Incident Root Cause Analysis](https://peckshield.medium.com/cheese-bank-incident-root-cause-analysis-d076bf87a1e7)
- [Cheese Bank Detailed Statement](https://cheesebank2020.medium.com/cheese-bank-detailed-statement-a765372dd84f)
- [ImmuneBytes: Cheese Bank Hack Detailed Analysis](https://immunebytes.com/blog/cheese-bank-hack-nov-6-2020-detailed-analysis/)
- [Etherscan attack transaction](https://etherscan.io/tx/0x600a869aa3a259158310a233b815ff67ca41eab8961a49918c2031297a02f1cc)
- [ProMutator: Detecting Vulnerable Price Oracles in DeFi by Mutated Transactions](https://www.csie.ntu.edu.tw/~hchsiao/pub/2021_IEEE_SB_ProMutator.pdf)
