---
title: "My Big Coin Fictitious Trading Data and Synthetic Token Price Discovery"
date: 2025-06-11
entities:
  - My Big Coin
  - My Big Coin Pay
  - MBC
  - Randall Crater
  - Mark Gillespie
  - John Roche
---

## Summary

This case study documents the My Big Coin digital-asset fraud scheme, focusing on the market-health signals created by fictitious trading status and fabricated daily price information. The CFTC filed its original enforcement action in January 2018, and on June 11, 2025, announced that the U.S. District Court for the District of Massachusetts entered a final default judgment against Mark Gillespie, John Roche, My Big Coin Pay, Inc., and My Big Coin, Inc. The order required more than $25 million in penalties and restitution. A separate February 2025 consent order against Randall Crater required more than $7.6 million in restitution.

The market-health lesson is that a token can create a false impression of market activity without operating a real liquid market. According to the CFTC, My Big Coin materials misrepresented that MBC was actively traded on several currency exchanges, reported daily trading prices even though no price existed because MBC was not trading, and claimed MBC was backed by gold. Those claims converted a non-trading asset into a synthetic market story that customers could monitor through account balances and price claims but could not verify through independent exchange activity.

The supporting dataset is available in [my-big-coin-summary.csv](my-big-coin-summary.csv).

## Fictitious Market Structure

The CFTC alleged that from at least January 2014 through January 2018, the defendants solicited customers by misrepresenting MBC's value, use, trade status, and gold backing. The My Big Coin website allegedly displayed solicitation materials, trade data, and other materials that made MBC appear active and valuable. The CFTC said those materials represented that MBC was actively traded on multiple currency exchanges, including the MBC Exchange website, when it was not.

This is not a normal low-liquidity token case. Low-liquidity assets may trade rarely but still have a verifiable market. In My Big Coin, the alleged market-health failure was more fundamental: daily prices and trade status were represented to customers despite the absence of trading. That makes the incident useful as a synthetic price-discovery case.

## Market-Health Indicators

### Claimed exchange listings without independent volume

The first signal is the gap between claimed exchange access and externally verifiable trading. A token issuer or promoter can claim that a market exists on one or more exchanges, but market-health analysis should verify whether those venues publish independent order books, trade histories, custody paths, and withdrawal functions. If the only source for the listing claim is the promoter's own website, the trading status should be treated as unverified.

### Daily price reports with no trading basis

The CFTC said the defendants misrepresented daily trading prices even though no price existed because MBC was not trading. A daily token quote can look like market data, but it is not a market price unless it comes from arms-length transactions or a transparent pricing methodology. Synthetic quotes should be flagged when prices update without corresponding trade prints, venue volume, or independent market-maker quotes.

### Account balances without redemption

The scheme used account views and coin balances to maintain the appearance of ownership. The CFTC alleged that when customers raised questions about accounts, defendants issued additional coins and encouraged customers not to redeem holdings until a supposed new exchange became active. This is a key market-health risk: internal balances can delay detection by making customers believe value exists while redemption remains blocked or postponed.

### Collateral and partnership claims

The CFTC also alleged that defendants falsely represented MBC was backed by gold and had a MasterCard partnership. Collateral and payment-network claims can support a token's perceived value even when trading evidence is missing. Market-health reviews should treat backing claims and payment-network claims as separate verification tasks, not as substitutes for proof of trading.

## Detection Checklist

1. Verify claimed exchange listings against independent venue data, not promoter-hosted pages.
2. Reconcile daily token prices against actual trade prints, trade IDs, and public order-book activity.
3. Flag assets where account balances increase but withdrawals or redemptions are unavailable or repeatedly delayed.
4. Test collateral claims, such as gold backing, against custody records, auditor reports, and redemption rights.
5. Treat claims of payment-network partnerships as unverified unless the named partner confirms them publicly.
6. Separate real low-liquidity markets from non-trading assets with promoter-supplied prices.
7. Preserve enforcement posture: the June 2025 and February 2025 CFTC announcements describe court orders resolving the agency's enforcement action, while the January 2018 press release summarizes allegations from the complaint.

## Market-Health Lessons

My Big Coin shows that fake market data can be more basic than wash trading. Wash trading uses real or simulated trades to inflate volume, but a fictitious-token scheme can skip the order book entirely and publish a price narrative directly. The resulting risk is similar: customers and observers may see apparent price discovery, apparent exchange access, and apparent account value that do not reflect executable liquidity.

For crypto market-health systems, the case supports a simple hierarchy. A quoted price is weaker than a trade print. A trade print is weaker than a trade print tied to a public venue with withdrawals. A promoter-hosted balance is weakest of all unless it can be redeemed or externally verified. When those layers are missing, the appropriate market-health label is not merely thin liquidity; it may be no verifiable market.

## References

- [CFTC press release 7678-18, January 24, 2018](https://www.cftc.gov/PressRoom/PressReleases/7678-18)
- [CFTC press release 9051-25, February 10, 2025](https://www.cftc.gov/PressRoom/PressReleases/9051-25)
- [CFTC press release 9084-25, June 11, 2025](https://www.cftc.gov/PressRoom/PressReleases/9084-25)
