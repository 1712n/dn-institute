---
title: "TRX Wash Trading and Paid Promotion as a Market-Activity Inflation Pattern"
date: 2026-03-09
entities:
  - Justin Sun
  - Tron Foundation
  - BitTorrent Foundation
  - Rainberry
  - TRX
  - BTT
---

## Summary

This case study documents the market-health signals in the SEC's civil action against Justin Sun, Tron Foundation, BitTorrent Foundation, and Rainberry. The SEC filed the original complaint on March 22, 2023, alleging unregistered TRX and BTT distributions, undisclosed celebrity promotion, and TRX secondary-market wash trading. The court entered final judgment on March 9, 2026, ordering Rainberry to pay a $10 million civil penalty while dismissing the remaining claims against the Tron defendants with prejudice. Rainberry did not admit or deny the allegations.

The market-abuse pattern is useful because it joins three signals that often appear separately:

1. A token issuer or issuer-linked group controls a large token inventory.
2. Related accounts trade with each other to print volume without a change in beneficial ownership.
3. Public promotion and exchange-listing messaging convert artificial volume into a retail-facing liquidity signal.

The supporting dataset is available in [trx-wash-trading-summary.csv](trx-wash-trading-summary.csv).

## Enforcement Timeline

On March 22, 2023, the SEC announced charges against Justin Sun, Tron Foundation Limited, BitTorrent Foundation Ltd., and Rainberry Inc. The SEC said it had charged Sun and his companies with manipulating the secondary market for TRX through wash trading and with undisclosed promotion of TRX and BTT by celebrities. The SEC press release also stated that the complaint alleged more than 600,000 TRX wash trades between accounts Sun controlled, with 4.5 million to 7.4 million TRX wash traded daily from at least April 2018 through February 2019.

The complaint describes wash trading as trades without a change in beneficial ownership that create a false perception of market activity. It alleges that Sun's team conducted TRX wash trading on a U.S.-based trading platform and that the trading was intended to create the appearance of active legitimate demand, support TRX price stability, and make it easier for Sun and the Tron Foundation to sell TRX into the market.

On March 5, 2026, the SEC filed a proposed settlement. The SEC litigation release says the proposed final judgment would settle the Commission's Section 17(a)(3) claim against Rainberry related to TRX wash trading, dismiss the remaining claims against Rainberry and all claims against the other Tron defendants, and order Rainberry to pay a $10 million civil penalty if approved. A public docket copy of the March 9, 2026 final judgment records that the court signed the judgment and ordered Rainberry to pay the $10 million penalty.

## Manipulation Pattern

The alleged wash-trading scheme relied on controlled accounts, controlled inventory, and repeated back-and-forth execution. The SEC complaint states that Sun directed employees to open nominee accounts on multiple trading platforms, including a U.S.-based platform. Two accounts, identified in the complaint as Accounts 16 and 17, were opened in March 2018. Another account, the Activity Account, was opened in August 2018 in the name of a U.S.-based Rainberry employee. A Bancor Account also appears in the complaint's examples.

The scale is material for market monitoring. Between April 18, 2018 and February 11, 2019, the complaint says Accounts 16 and 17 generated at least 609,790 wash trades over 249 active days, or about 2,449 wash trades per day. A second account pair, the Activity and Bancor Accounts, allegedly generated at least 5,426 wash trades between September 26 and October 18, 2018, or about 236 per day. The complaint includes sample rows from October 1 and October 7, 2018 where the buying and selling account alternates while quantities and prices remain tightly patterned.

Market-health systems should treat this as an account-pair and beneficial-ownership problem, not just an exchange-volume problem. The reported volume can look continuous and liquid, but the economic ownership is unchanged. The risk is that external users, data vendors, ranking sites, and listing venues observe the volume without seeing the common controller behind the accounts.

## Market-Health Indicators

### Beneficial-ownership reversals

The strongest signal is repeated matched activity between accounts ultimately controlled by the same person or affiliated entities. In public exchange data, this may appear as alternating maker-taker account pairs, identical trade sizes, or price increments that do not correspond to broad market depth. Investigators should track whether the same account cluster appears on both sides of a market over short windows.

### Stable volume without organic depth

The alleged 4.5 million to 7.4 million TRX wash-traded daily is a reminder that high trade count and high volume do not prove real liquidity. A venue can show frequent prints while actual executable depth available to unaffiliated traders is thin. Useful checks include volume-to-order-book-depth ratios, concentration of prints by account cluster, and the share of trades that reverse across the same pair of accounts.

### Issuer inventory flowing into visible liquidity

The SEC complaint alleges the scheme required significant TRX supply that Sun provided. When an issuer or affiliated treasury supplies inventory for market-making activity, monitors should separate legitimate inventory distribution from circular trading. A simple test is whether inventory movement precedes high reported volume without corresponding increases in independent wallet or account participation.

### Promotion synchronized with activity signals

The SEC action also alleged paid celebrity promotion of TRX and BTT without disclosure. Undisclosed promotion does not itself prove wash trading, but in market-health analysis it raises the risk that artificial liquidity and public attention are working together. Monitoring rules should flag bursts of social promotion when they coincide with abnormal trade-count concentration, stable buy-sell ratios, or repetitive account-pair reversals.

## Detection Checklist

1. Group trades by suspected common control, shared funding source, or repeated withdrawal/deposit path.
2. Measure two-way trade recurrence between account pairs over short windows.
3. Compare reported volume with unaffiliated market depth and price impact.
4. Track whether issuer-linked wallets or treasury accounts fund both sides of visible market activity.
5. Compare social-promotion windows with abnormal account-pair recurrence and volume-depth divergence.
6. Preserve the distinction between allegations, settlements without admissions, and adjudicated findings when using enforcement actions as training data.

## References

- [SEC press release, March 22, 2023: SEC Charges Crypto Entrepreneur Justin Sun and His Companies for Fraud and Other Securities Law Violations](https://www.sec.gov/newsroom/press-releases/2023-59)
- [SEC complaint, SEC v. Justin Sun et al., filed March 22, 2023](https://www.sec.gov/files/litigation/complaints/2023/comp-pr2023-59.pdf)
- [SEC Litigation Release No. 26496, March 5, 2026](https://www.sec.gov/enforcement-litigation/litigation-releases/lr-26496)
- [Public docket copy of final judgment, March 9, 2026](https://law.justia.com/cases/federal/district-courts/new-york/nysdce/1%3A2023cv02433/596044/98/)
