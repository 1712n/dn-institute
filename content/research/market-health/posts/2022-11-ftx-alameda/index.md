---
title: "FTX and Alameda Research: How a $65 Billion Exchange Collapsed Through Self-Dealing, FTT Token Manipulation, and Commingled Customer Funds"
date: "2019-01 -- 2022-11"
description: "FTX founder Sam Bankman-Fried used sister company Alameda Research to manipulate the FTT token price, borrowed billions in customer deposits, and created a web of self-dealing that ultimately destroyed the world's third-largest cryptocurrency exchange."
entities:
  - FTX
  - Alameda Research
  - FTT
---

## Summary

The collapse of FTX in November 2022 represented the largest fraud in cryptocurrency history, with customer losses estimated at $8 billion. FTX founder Sam Bankman-Fried operated a systematic scheme in which his trading firm Alameda Research received preferential treatment on the exchange, borrowed billions in customer deposits, and manipulated the price of FTX's native FTT token to inflate collateral values. The fraud was exposed when a leaked Alameda balance sheet revealed that the firm's assets were primarily composed of illiquid, self-issued tokens rather than independent assets. Bankman-Fried was convicted on seven counts of fraud and conspiracy in November 2023 and sentenced to 25 years in prison.

## The FTT Token Manipulation

At the center of the fraud was FTT, the native token of the FTX exchange. FTX created FTT with a total supply of 350 million tokens, retaining a significant portion for the company and Alameda Research. The token's value was supported by a periodic buy-and-burn mechanism funded by exchange trading fees, creating sustained demand.

The manipulation operated through circular reinforcement. FTX and Alameda held the majority of FTT's circulating supply, meaning the token's price was determined primarily by trades between related entities rather than genuine market demand. Alameda used its FTT holdings as collateral to borrow from FTX's customer deposits, and FTX used the inflated FTT valuation to report healthy balance sheets.

Because Alameda was both the largest holder and the most active trader of FTT, the token's price was effectively controlled by a single entity. Any independent selling pressure could be absorbed by Alameda's trading activity, maintaining the artificial floor needed to keep collateral values above borrowing thresholds.

## Customer Fund Misappropriation

FTX transferred approximately $8 billion in customer deposits to Alameda Research through a series of mechanisms that were hidden from customers, auditors, and regulators.

Alameda maintained a special account on FTX that was exempt from the exchange's auto-liquidation engine. This meant Alameda could maintain positions that would have triggered forced liquidation for any other user, effectively borrowing against customer deposits without the risk management constraints applied to other traders.

The transfers were facilitated by a backdoor in FTX's accounting system that allowed Alameda's liabilities to be hidden from standard balance sheet reports. Internal records used a hidden "fiat@" account that was excluded from customer-facing dashboards, concealing the scale of the deficit.

## Collapse Timeline

On November 2, 2022, CoinDesk published a report based on a leaked Alameda Research balance sheet showing that the firm's $14.6 billion in assets were heavily concentrated in FTT and other FTX-linked tokens. Of the reported assets, approximately $5.8 billion was in FTT, a token whose value was entirely dependent on the continued operation and credibility of FTX.

On November 6, Binance CEO Changpeng Zhao announced that Binance would liquidate its entire FTT holdings, valued at approximately $580 million. This triggered a cascade of customer withdrawals from FTX as confidence in the platform evaporated.

Within 72 hours, FTX faced approximately $6 billion in withdrawal requests that it could not fulfill because the customer deposits had been lent to Alameda. On November 11, FTX filed for Chapter 11 bankruptcy protection.

## Market Manipulation Detection Patterns

The FTX case illustrates manipulation patterns that market surveillance systems should flag:

- **Concentrated token ownership.** When an exchange's native token is primarily held and traded by the exchange itself and its affiliated entities, the reported market price does not reflect genuine price discovery. On-chain analysis of token holder distribution can identify this concentration.
- **Circular collateral.** Using self-issued tokens as collateral to borrow real assets creates systemic risk that is invisible to external observers but detectable through analyzing the composition of declared reserves relative to independent assets.
- **Exempted accounts.** Any trading account exempt from standard risk management rules represents a potential vector for hidden liabilities. Exchange transparency reports should disclose the existence of any accounts with modified liquidation parameters.
- **Volume-price divergence on native tokens.** High reported trading volume on an exchange's native token that does not correlate with independent exchange data or on-chain transfer activity suggests artificial volume generation.
