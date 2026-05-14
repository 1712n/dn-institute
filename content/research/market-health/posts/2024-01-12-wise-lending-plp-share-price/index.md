---
title: "Wise Lending PLP share-price inflation market-health case"
date: "2024-01-12"
description: "Wise Lending was drained after a precision-loss and rounding-donation path inflated a nearly empty Pendle LP market's share price."
entities:
  - Wise Lending
  - PLP-stETH-Dec2025
  - Pendle
  - Ethereum
---

Wise Lending V1 was exploited on January 12, 2024 after an attacker used a
precision-loss path against a nearly empty Pendle LP market. The incident is a
useful market-health case because the exploitable signal was not simply a bad
line of arithmetic. It was a combination of thin market state, share-price
inflation, flash-loan funding, and lending-market exposure.

Public analyses describe the attacker targeting a PLP-stETH-Dec2025 market that
had been deployed shortly before the incident. By making strategic deposits,
withdrawals, and donation-like balance movements, the attacker inflated the
market's share price and then borrowed funds from the lending markets. Reported
loss estimates range from about 170 ETH to 178.19 ETH, or roughly 440,000 to
464,000 dollars. DefiLlama's protocol data shows Wise Lending TVL near 835,000
dollars on January 12 and about 439 dollars on January 13, making the market
health break visible as a near-total liquidity exit.

## Incident metrics

| Signal          | Observation                                                                              | Market-health interpretation                                                                         |
| --------------- | ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Market depth    | The exploited PLP-stETH-Dec2025 market was nearly empty                                  | Thin or newly deployed collateral markets should receive stricter caps and health checks             |
| Accounting path | The exploit relied on precision loss and donation-like balance manipulation              | Share accounting can become a market signal when lending limits depend on calculated share value     |
| Funding source  | Reports describe flash-loan involvement in the exploit path                              | Temporary capital can create abnormal share-price pressure without a durable position history        |
| Loss estimate   | Public summaries estimate roughly 440,000 to 464,000 dollars lost                        | A small collateral surface was able to create protocol-level loss                                    |
| Liquidity path  | DefiLlama shows Wise Lending TVL falling from about 835,000 dollars to about 439 dollars | The exploit produced an observable next-day protocol-liquidity collapse                              |
| Market age      | The affected market was described as deployed shortly before the incident                | New markets need delayed caps, minimum-liquidity thresholds, and manual review before full borrowing |

The companion `wise-lending-plp-market-signals.csv` file separates the TVL,
loss-estimate, mechanism, and market-depth signals for reuse in dashboards.

## Manipulation path

The core loop was:

1. A thin PLP-stETH-Dec2025 market gave the attacker a low-liquidity surface.
2. Flash-loan funding and repeated accounting operations changed the market's
   share-price state.
3. Precision loss and donation-like balance movements inflated the value that
   Wise Lending used for the position.
4. The attacker borrowed funds against the inflated share value.
5. Protocol liquidity collapsed after the exploit completed.

This is a market-health issue because the dangerous state was visible before it
became a full drain. A new market with little organic liquidity, sudden balance
movement, and rising borrow demand against a calculated share value should be
treated as a separate risk state from an established collateral market with deep
liquidity and stable share accounting.

## Detection controls

Wise Lending shows why lending protocols should connect accounting invariants to
market surveillance. Useful controls include:

- **Minimum-liquidity thresholds:** block or cap borrowing against newly deployed
  collateral markets until depth and usage history exceed a configured floor.
- **Share-price jump limits:** pause collateral use when a share price changes
  faster than the underlying asset and pool balance can justify.
- **Donation-delta monitoring:** flag balance increases that are not matched by
  ordinary deposit, withdrawal, or yield paths.
- **Flash-loan funding checks:** lower limits or pause borrow paths when the
  same transaction funds, reprices, and borrows against a position.
- **New-market exposure caps:** give new PLP or LP collateral types low initial
  debt ceilings that scale only after observation.

The key distinction is between accounting precision as an internal correctness
problem and accounting precision as an external market signal. If calculated
share value directly controls borrowing power, precision loss can become a
market-health failure.

## Lessons for market health

Thin markets need stricter borrowing defaults than mature collateral markets. A
single pool or share token can look ordinary in a static asset list while still
being too shallow to support immediate borrowing at full collateral value. The
Wise Lending exploit shows that dashboards should rank collateral not only by
token name and price, but also by market age, liquidity depth, share-price
volatility, donation deltas, and flash-loan-coupled borrow attempts.

For surveillance teams, the useful alert is the combined pattern: nearly empty
market, abrupt share-price movement, temporary funding, and borrowing against the
repriced collateral. That pattern should trigger a pause or severe haircut even
if each individual transaction step fits the protocol's nominal accounting
rules.

## References

- [SolidityScan: Wise Lending Hack Analysis](https://blog.solidityscan.com/wise-lending-hack-analysis-f652f389e397)
- [Smart Contract Hacking: Wise Lending V1 Hack (2024)](https://smartcontractshacking.com/hacks/wise-lending-v1-hack-2024)
- [FXStreet: Wise Lending market exploited for 177 ETH in a flash loan attack](https://www.fxstreet.com/cryptocurrencies/news/wise-lending-market-exploited-for-177-eth-in-a-flash-loan-attack-202401130252)
- [DefiLlama Wise Lending protocol data](https://defillama.com/protocol/wise-lending)
