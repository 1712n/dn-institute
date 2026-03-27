---
title: "FTX and Alameda Research: How Code-Level Privileges Enabled Billions in Market Manipulation"
date: "2019-05 -- 2022-11"
description: "Alameda Research exploited hidden code privileges on FTX to trade with unlimited leverage using customer funds, front-run token listings, and manipulate markets while operating as the exchange's primary market maker."
entities:
  - FTX
  - Alameda Research
  - FTT
---

## Summary

Between May 2019 and November 2022, Alameda Research operated as the primary market maker on FTX while secretly exploiting code-level privileges that gave it effectively unlimited access to customer funds. FTX engineers implemented an "allow negative" flag in Alameda's account that permitted the firm to withdraw billions of dollars beyond its own deposits, funded by customer assets. Alameda used this advantage to front-run token listings, manipulate FTT token price, and trade with leverage unavailable to any other market participant. When the scheme collapsed in November 2022, approximately $8 billion in customer funds were missing. FTX founder Sam Bankman-Fried was convicted of wire fraud, conspiracy, and money laundering in November 2023 and sentenced to 25 years in prison.

## Code-Level Market Manipulation

The FTX-Alameda manipulation was unique in that it was embedded directly in the exchange's source code. At Bankman-Fried's direction, FTX engineers created a special account flag for Alameda that bypassed the exchange's standard risk checks. This flag allowed Alameda to execute trades and withdrawals even when its account balance was negative by billions of dollars, with the deficit covered automatically by customer deposits held on FTX.

This gave Alameda capabilities that no other trader on the platform had: effectively unlimited leverage, no liquidation risk, and the ability to absorb losses that would have bankrupted any other account. The asymmetry between Alameda's hidden privileges and the standard trading conditions presented to retail users constituted a structural form of market manipulation, as other traders were competing against a counterparty with fundamentally different rules.

## Token Listing Front-Running

Between early 2021 and March 2022, Alameda Research accumulated approximately $60 million worth of cryptocurrency tokens on Ethereum ahead of those tokens being listed for trading on FTX. Because Alameda had advance knowledge of upcoming FTX listings through its relationship with Bankman-Fried, it could purchase tokens at lower prices before the listing announcement drove prices up.

This front-running pattern exploited material non-public information about exchange listing decisions, which reliably cause price increases as new tokens become accessible to FTX's user base. The practice transferred value from FTX users who bought at post-listing prices to Alameda, which had accumulated positions at pre-listing levels.

## FTT Token Price Support

FTX's native FTT token served as a critical component of the manipulation scheme. Alameda held large quantities of FTT on its balance sheet and used these holdings as collateral for borrowing on FTX. Maintaining an elevated FTT price was essential because a decline would reduce Alameda's collateral value and expose its insolvency.

The circular dependency between FTT price and Alameda's solvency created incentives for active price manipulation. Evidence presented at trial showed that Alameda engaged in strategic trading of FTT to support its price during periods of selling pressure, using customer funds to finance purchases that benefited Alameda's balance sheet rather than protecting customer interests.

## Collapse and Detection

The scheme began unraveling in November 2022 when reporting by CoinDesk revealed that Alameda's balance sheet was heavily concentrated in illiquid FTT tokens. The revelation triggered a bank run on FTX as customers attempted to withdraw funds, exposing that the exchange lacked sufficient reserves to honor customer balances. On November 11, 2022, FTX filed for Chapter 11 bankruptcy.

## Detection Indicators

The FTX-Alameda case illustrates manipulation patterns that market surveillance should flag:

- **Asymmetric trading behavior.** One market maker consistently taking larger positions and absorbing larger losses than its visible balance should support indicates hidden funding sources or privilege asymmetries.
- **Pre-listing accumulation patterns.** Entities with exchange relationships accumulating tokens before listing announcements suggests information leakage.
- **Native token price stability.** Abnormally stable prices for exchange-native tokens during broader market downturns may indicate active price support, particularly when the token serves as collateral for significant borrowing.
- **Counterparty concentration.** A single market maker accounting for a disproportionate share of exchange volume, especially when that maker has a financial relationship with the exchange operator, creates conflicts of interest that enable manipulation.
