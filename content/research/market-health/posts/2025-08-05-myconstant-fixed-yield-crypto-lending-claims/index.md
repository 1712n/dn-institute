---
title: "MyConstant Fixed-Yield Crypto Lending Claims"
date: 2025-08-05
entities:
  - CONST LLC
  - MyConstant
  - Huynh Tran Quang Duy
  - TerraUSD
  - UST
---

## Summary

This case study analyzes MyConstant as a market-health warning about crypto lending platforms that advertise fixed returns, crypto-backed collateral, and low-risk pooled lending while customer funds are used in ways that do not match the product description. On August 5, 2025, the SEC issued an administrative order against Huynh Tran Quang Duy, founder and CEO of CONST LLC, which did business as MyConstant.

The SEC order said that from September 2020 through November 2022, MyConstant raised more than $20 million from more than 4,000 investors by offering and selling unregistered securities. MyConstant told investors their funds would be lent through crypto-backed loan products producing fixed returns of 6 percent to 10 percent, but the SEC found investor funds were pooled and that Huynh used some investor funds to buy TerraUSD, the algorithmic stablecoin that depegged and collapsed in May 2022.

For market-health review, MyConstant is useful because the marketed risk control was collateral. A crypto-backed loan platform should be able to reconcile customer deposits to borrower loans, collateral addresses, collateralization ratios, liquidations, interest receipts, reserve accounts, and withdrawal liquidity. If pooled funds are instead exposed to UST or other unrepresented assets, fixed-yield dashboards understate market and protocol risk.

The supporting dataset is available in [myconstant-summary.csv](myconstant-summary.csv).

## Trading Narrative

The California DFPI's December 2022 order said MyConstant operated an online platform offering peer-to-peer loan brokering, interest-bearing crypto asset accounts, and interest-bearing fiat accounts. The platform represented that peer-to-peer loans were secured by borrowers' crypto assets and that interest-bearing accounts paid fixed annual percentage yields.

The SEC order sharpened the fund-flow problem. MyConstant investors expected returns based on the company's effort to pool funds, lend them to borrowers, collect interest, and manage collateral. The SEC found MyConstant raised more than $20 million from more than 4,000 investors and used some investor money to buy UST rather than only making crypto-backed loans as represented.

UST exposure changed the risk profile. TerraUSD was marketed as a stablecoin, but it depegged and collapsed in May 2022. A lending product promising fixed returns from collateralized loans should not quietly become exposed to algorithmic-stablecoin risk without disclosure and reconciliation. The relevant market-health control is product-to-asset mapping: every source of yield must match the product description.

The final SEC order required Huynh to pay $8,364,508 in disgorgement, $1,575,238 in prejudgment interest, and a $750,000 civil penalty. The order also imposed a cease-and-desist obligation. Those amounts show the difference between advertised lending yield and the funds the regulator determined should be returned or penalized.

## False Market Signals

### Fixed lending yield

Fixed returns of 6 percent to 10 percent can look stable, but they require proof of borrower interest, collateral coverage, defaults, fees, reserves, and withdrawals.

### Crypto-backed collateral

Collateral claims should be verified on-chain and against borrower agreements. Collateralization should include price volatility, liquidation thresholds, and actual liquidation history.

### Peer-to-peer branding

Peer-to-peer language can make users think specific loans match specific deposits. If funds are pooled, users face platform-level risk rather than only borrower-level risk.

### Stablecoin exposure

UST exposure introduced protocol and depeg risk. A platform should disclose and mark that exposure instead of treating it as equivalent to secured lending.

### Interest-bearing fiat accounts

Fiat return claims can feel separate from crypto risk. If fiat funds are pooled into crypto or stablecoin exposures, the risk profile changes.

### Withdrawal confidence

Fixed-yield platforms often rely on smooth withdrawals to maintain confidence. Withdrawal capacity should be tested against actual liquid assets, not dashboard balances.

## Event Timeline

| Date or period    | Event                                                                                      | Market-health signal                                            |
| ----------------- | ------------------------------------------------------------------------------------------ | --------------------------------------------------------------- |
| September 2020    | SEC relevant period began.                                                                 | Product and fund-flow controls needed records from launch.      |
| 2020-2022         | MyConstant offered crypto-backed and interest-bearing products.                            | Fixed-yield claims needed loan and collateral reconciliation.   |
| May 2022          | TerraUSD depegged and collapsed.                                                           | UST exposure created protocol and liquidity risk.               |
| November 2022     | SEC relevant period ended.                                                                 | Final investor balances needed product-to-asset reconciliation. |
| December 21, 2022 | California DFPI ordered MyConstant to stop offering crypto-related products in California. | State order challenged product legality and disclosures.        |
| August 5, 2025    | SEC issued administrative order against Huynh.                                             | Federal order fixed disgorgement, interest, and penalty.        |

## Reconciliation Metrics

| Metric                    | Enforcement-record figure or claim                       | Market-health interpretation                                        |
| ------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------- |
| Investor count            | More than 4,000 investors                                | Scale required standardized ledgers and customer disclosures.       |
| Funds raised              | More than $20 million                                    | Deposit flows needed product-to-asset mapping.                      |
| Advertised fixed return   | 6 percent to 10 percent                                  | Yield needed borrower interest and collateral proof.                |
| SEC disgorgement          | $8,364,508                                               | Disgorgement measured improper gains to be returned.                |
| Prejudgment interest      | $1,575,238                                               | Interest captured time value of disgorged funds.                    |
| Civil penalty             | $750,000                                                 | Penalty added deterrence beyond disgorgement.                       |
| Product categories        | Peer-to-peer loans, crypto asset accounts, fiat accounts | Different products required separate risk and liquidity accounting. |
| Collateral representation | Borrowers' crypto assets securing loans                  | Collateral claims required on-chain and contract verification.      |
| Unrepresented asset risk  | TerraUSD purchases with investor funds                   | UST exposure changed product risk after pooling.                    |
| State enforcement posture | DFPI desist-and-refrain order                            | State regulator identified securities and consumer-law issues.      |

## Detection Checklist

1. Reconcile every fixed-yield product to borrower loans, collateral, interest receipts, defaults, and reserves.
2. Verify crypto collateral on-chain and compare it with loan balances and liquidation thresholds.
3. Identify whether deposits are matched to specific loans or pooled into platform-level exposures.
4. Require disclosure and marking of stablecoin and protocol exposures, especially algorithmic stablecoins.
5. Separate fiat-account yields from crypto-backed loan yields in accounting and risk reporting.
6. Test withdrawal liquidity against cash, stablecoin, loan maturities, and collateral liquidation capacity.
7. Preserve legal posture: this article relies on SEC administrative findings and California DFPI public orders.

## Market-Health Lessons

MyConstant shows why collateral language must be verified rather than assumed. A crypto-backed loan product sounds secured, but the security depends on actual collateral, custody, valuation, and liquidation mechanics.

The case also shows how pooling changes customer risk. If funds are pooled, a customer's return depends on the platform's whole asset book, including any undisclosed UST or other protocol exposure.

Finally, fixed-yield crypto products should be analyzed like balance-sheet products, not only like trading products. Yield, liquidity, collateral, and asset allocation all need to reconcile before a dashboard return can be trusted.

## References

- [SEC administrative order against Huynh Tran Quang Duy, August 5, 2025](https://www.sec.gov/files/litigation/admin/2025/33-11382.pdf)
- [California DFPI order announcement, December 21, 2022](https://dfpi.ca.gov/press_release/dfpi-orders-myconstant-to-cease-offering-crypto-related-products/)
