---
title: "Polter Finance BOO Spot-Oracle Manipulation and Lending Pool Drain"
date: 2024-11-16
entities:
  - Polter Finance
  - BOO
  - SpookySwap
  - Fantom
---

## Summary

The November 2024 Polter Finance incident is a useful market-health case because the attacker did not need to break a price feed provider. The lending market accepted a spot-derived BOO price from thin SpookySwap pools, then let that price determine borrowing power across multiple Polter reserves.

Public incident reports describe the same core failure:

- Polter Finance was a Fantom lending protocol whose BOO market depended on SpookySwap V2/V3 pool state for pricing.
- The attacker used flash-loan and flash-swap liquidity to distort the BOO pool balances inside the transaction.
- The manipulated BOO price let the attacker deposit minimal BOO collateral and borrow large amounts from several lending pools.
- CertiK and Halborn place the direct exploit at about $8.7 million, while Cointelegraph reported a police-report loss figure of about $12 million.

This makes Polter a clean example of a cross-market oracle-liquidity mismatch: the protocol treated a low-depth spot market as if it could safely support protocol-wide borrowing capacity.

## Market-health surface

Polter's risk surface was created by the combination of a lending market, BOO collateral, and an oracle path tied to the same liquidity pools that could be moved by a single atomic trade. [Halborn's incident explanation](https://www.halborn.com/blog/post/explained-the-polter-finance-hack-november-2024) says the protocol used the spot price from SpookySwap V2/V3 for BOO rather than a more manipulation-resistant source, which made the lending decision vulnerable to flash-loan price movement.

[CertiK's incident analysis](https://www.certik.com/zh-CN/blog/polter-finance-incident-analysis) gives the most useful replay details. It identifies the exploiter, exploit contract, two SpookySwap pool addresses, Polter's ChainlinkUniV2Adapter and PriceFeedV2 contracts, and the affected Polter pool addresses. CertiK also describes the key oracle logic problem: the adapter's `getRoundData()` path returned the same spot-derived value as `latestRoundData()`, so the intended historical or fallback check did not provide an independent price anchor.

That matters for market-health monitoring because the failure was visible as a capacity mismatch before it became a solvency event. A collateral token priced from thin pool state should not unlock borrow power across several unrelated reserves unless the oracle is slow-moving, multi-source, capped, or quarantined.

## Attack mechanics

The public reports describe a short, atomic manipulation path:

1. The attacker drew BOO liquidity from the SpookySwap V3 and V2 pools. CertiK reports 269,042 BOO from the V3 pool and 1,154,788 BOO from the V2 pool, leaving each pair with only `1e6` wei of BOO.
2. With BOO reserves depleted, Polter's oracle read an inflated BOO price from the same pool state.
3. The attacker deposited a minimal BOO amount as collateral. Coinspect's replay summary describes the collateral setup as `1e18` BOO units.
4. Polter's lending pool then treated the manipulated BOO collateral as sufficient to borrow against multiple reserves.
5. After borrowing and swapping assets, the attacker repaid the flash liquidity and retained the drained value.

CertiK reports that the attacker borrowed 9,134,844 wFTM during the validation path and then drained multiple Polter pools. A Cointelegraph report republished by TradingView says Polter paused operations on November 17, 2024 after identifying the exploit and traced stolen funds to Binance-linked wallets.

The extreme indicator was the one-collateral-token valuation. CertiK states that the manipulated reserve balances led Polter to value the deposited BOO at about `$1.373e18`. The exact number is less important than the invariant failure: a single BOO collateral event should not generate borrowing power large enough to drain a multi-asset lending market.

## Evidence table

| Signal                                                                      | Source                                                                                                                                                                                                   | Market-health value                                                         |
| --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| Direct exploit estimate around $8.7 million                                 | [CertiK incident analysis](https://www.certik.com/zh-CN/blog/polter-finance-incident-analysis), [Halborn explanation](https://www.halborn.com/blog/post/explained-the-polter-finance-hack-november-2024) | Establishes on-chain loss scale for the drain.                              |
| Police-report loss figure around $12 million                                | [Cointelegraph report republished by TradingView](https://www.tradingview.com/news/cointelegraph%3A4d22dee57094b%3A0-crypto-lender-polter-finance-halts-operations-after-12m-hack/)                      | Captures the wider TVL or reported-loss view.                               |
| 269,042 BOO plus 1,154,788 BOO removed from SpookySwap pools                | [CertiK incident analysis](https://www.certik.com/zh-CN/blog/polter-finance-incident-analysis)                                                                                                           | Shows the source-market liquidity manipulation behind the collateral price. |
| 9,134,844 wFTM borrowed                                                     | [CertiK incident analysis](https://www.certik.com/zh-CN/blog/polter-finance-incident-analysis)                                                                                                           | Shows the borrow-side impact after the price read.                          |
| BOO market reportedly valued near $3,000 while enabling a $12 million event | [Cointelegraph report republished by TradingView](https://www.tradingview.com/news/cointelegraph%3A4d22dee57094b%3A0-crypto-lender-polter-finance-halts-operations-after-12m-hack/)                      | Shows collateral-market depth was not aligned with protocol exposure.       |

## Replay packet

A useful replay packet should collect `tx_hash`, `block_number`, `exploit_contract`, `borrower`, `collateral_asset`, `collateral_amount`, `oracle_contract`, `oracle_adapter`, `spot_pair_v2`, `spot_pair_v3`, `pair_boo_reserve_before`, `pair_boo_reserve_after`, `pair_quote_reserve_before`, `pair_quote_reserve_after`, `reported_collateral_value`, `borrowed_asset`, `borrowed_amount`, `reserve_a_token`, `reserve_liquidity_before`, `reserve_liquidity_after`, `flash_loan_source`, `flash_loan_amount`, and `post_swap_fund_flow`.

The important join is not only between Polter's borrow event and the oracle contract. It must also include the SpookySwap reserve state in the same block or transaction. Without that source-market state, the Polter borrow can look like a normal collateralized loan.

## Detection controls

### Collateral-market depth check

Before enabling a lending market, compare the maximum borrow capacity unlocked by the collateral factor with the executable depth of the market used by the oracle. A simple rule would have blocked or quarantined BOO:

- if `max_borrow_capacity_usd / oracle_source_depth_usd` is above a fixed threshold, cap the asset's collateral factor at zero;
- if the oracle source can be moved inside one block by available flash liquidity, require a TWAP or independent oracle before allowing borrowing;
- if the lending protocol's total borrowable reserves exceed the collateral token's source-market depth by orders of magnitude, treat the market as unsafe regardless of nominal TVL.

The Cointelegraph report republished by TradingView says the BOO market was valued near $3,000 while the incident reached the $12 million reported-loss range. That is a direct example of this mismatch.

### Same-block oracle-reserve divergence

The detector should alert when a price used for borrowing is read from a pool whose reserves changed materially in the same transaction. For a collateral token such as BOO, useful features include:

- same-transaction percentage change in BOO reserves on oracle source pools;
- ratio between current spot price and a prior-block or rolling TWAP price;
- whether `latestRoundData()` and historical round reads are backed by independent observations;
- number of borrow calls that depend on the manipulated collateral price before the flash liquidity is repaid.

CertiK's description of `getRoundData()` returning the same spot-dependent value as `latestRoundData()` is the core anti-pattern. A historical check that reads the same manipulated state is not a check.

### New-market quarantine

Newly listed collateral markets should start with restrictive borrow caps until enough independent liquidity and oracle history exists. Polter's BOO market was newly deployed, and the Cointelegraph/TradingView report describes that market as the one that enabled the event. A useful control is a staged launch rule:

1. collateral factor remains zero until at least two independent price sources are live;
2. borrow cap is initially bounded by a small multiple of source-market executable depth;
3. cap increases only after observed depth and volatility are stable across multiple days;
4. any same-block reserve drain in the oracle source pauses new borrowing while still allowing repayment.

### Cross-reserve drain guard

The final symptom was not just an abnormal BOO price. It was one collateral event being used to borrow across multiple reserves. A protocol-level market-health monitor should stop or rate-limit when:

- one borrower opens a new collateral position and immediately borrows the available balance of several reserves;
- borrow utilization jumps to near 100% for multiple assets in one transaction or block;
- the same collateral price read gates all of those borrow calls;
- collateral valuation falls back to spot pool state with no independent sanity bound.

This detector is intentionally behavior-based. It does not require proving intent. It flags the economic pattern: source-market reserves are distorted, collateral value becomes extreme, and reserve drains fan out across assets.

## Lessons

The Polter incident shows why market-health systems should treat oracle source liquidity as part of lending risk. A protocol can reuse familiar lending code and still become unsafe if the price feed, market depth, collateral factor, and borrow caps are not designed together.

For lending markets, the first useful response is not a post-incident attribution debate. It is a runtime invariant: no collateral token whose source market can be atomically moved should unlock more borrowing power than that source market can economically support. Polter's BOO market violated that invariant, and the result was a lending pool drain rather than a normal liquidation event.

## References

- CertiK, [Polter Finance Incident Analysis](https://www.certik.com/zh-CN/blog/polter-finance-incident-analysis), November 18, 2024.
- TradingView/Cointelegraph, [Crypto lender Polter Finance halts operations after $12M hack](https://www.tradingview.com/news/cointelegraph%3A4d22dee57094b%3A0-crypto-lender-polter-finance-halts-operations-after-12m-hack/), November 18, 2024.
- Halborn, [Explained: The Polter Finance Hack (November 2024)](https://www.halborn.com/blog/post/explained-the-polter-finance-hack-november-2024), November 25, 2024.
- Coinspect Security, [Polter Finance](https://www.coinspect.com/learn-evm-attacks/cases/polter-finance/).
