---
title: "QuadrigaCX: Fake Trades, Phantom Balances, and the Exchange That Lost $190M When Its Founder Died"
date: "2014-01 -- 2019-01"
description: "Canadian cryptocurrency exchange QuadrigaCX was revealed as a fraud after founder Gerald Cotten's death in India, with forensic investigation showing the exchange had been trading against its own customers using fabricated deposits and phantom balances for years."
entities:
  - QuadrigaCX
---

## Summary

QuadrigaCX, once Canada's largest cryptocurrency exchange, collapsed in early 2019 after founder Gerald Cotten reportedly died in India in December 2018, taking sole access to the exchange's cold wallets with him. Subsequent investigation by the Ontario Securities Commission revealed the exchange had been insolvent for years, with Cotten operating what amounted to a Ponzi scheme. He created fictitious deposits, traded against his own customers using fabricated balances, and transferred customer funds to personal accounts and competing exchanges for margin trading. Total losses were approximately CAD $215 million ($169 million USD at the time), affecting over 76,000 customers.

## Trading Against Customers With Fake Balances

The OSC investigation revealed that Cotten created accounts on QuadrigaCX under aliases -- including "Chris Fartko" and "Sceptre Gerry" -- and credited them with fabricated cryptocurrency balances that did not correspond to any actual deposits. He used these phantom funds to trade against real customers on the platform.

When Cotten's fake accounts "sold" cryptocurrency to real users, those users believed they had purchased genuine assets. In reality, the exchange's reserves decreased because real cryptocurrency had to be delivered to settle these trades, while Cotten's side of the transaction was backed by nothing. Over time, this one-sided extraction created a growing deficit between customer balances and actual reserves.

The practice was effectively invisible to customers because the exchange's internal ledger showed correct balances -- the discrepancy only existed between what the database reported and what the cold wallets actually held.

## Customer Funds Used for Margin Trading

Beyond direct extraction through fake trading, Cotten transferred substantial amounts of customer cryptocurrency to his personal accounts on other exchanges, where he used the funds for leveraged trading. These trades frequently resulted in significant losses, further depleting the reserves that QuadrigaCX customers believed were safely held.

The OSC found that Cotten lost approximately CAD $115 million through these external trading activities. The losses were not disclosed to customers or to QuadrigaCX's other staff, who were largely unaware of the exchange's true financial condition.

## Collapse and Death

When Cotten died on December 9, 2018, reportedly from complications of Crohn's disease while traveling in India, the exchange initially continued operating normally. In January 2019, QuadrigaCX announced it could not access approximately CAD $190 million in cryptocurrency because Cotten had been the sole holder of the cold wallet private keys.

The exchange filed for creditor protection in February 2019. Ernst & Young was appointed as monitor and discovered that most of the cold wallets had been empty for months before Cotten's death -- the funds had already been spent or lost through trading.

## Investigation Findings

The OSC's forensic investigation concluded that QuadrigaCX operated as a fraud from at least 2016 onward. Key findings included:

- Cotten created and used at least five fictitious accounts on the platform to trade with fabricated balances
- Approximately CAD $115 million was lost through Cotten's personal margin trading on other exchanges
- Customer funds were transferred to Cotten's personal bank accounts
- The exchange's internal controls were non-existent, with Cotten maintaining sole access to critical systems
- Other QuadrigaCX staff had no knowledge of or access to the exchange's actual reserves

## Detection Patterns

The QuadrigaCX case highlights manipulation patterns specific to exchanges operated by insiders:

- **Reserve opacity.** The fundamental vulnerability was that no independent verification of reserves existed. Customers trusted the exchange's reported balances without any mechanism to verify that corresponding assets existed in wallets. Proof-of-reserves audits, while imperfect, would have detected the discrepancy.
- **Single-person key management.** Sole custody of private keys by one individual represents both a security risk and a fraud risk. Multi-signature wallet arrangements with independent keyholders would have prevented unilateral fund extraction.
- **Internal account activity anomalies.** Accounts with large balances that appeared without corresponding on-chain deposits should have been flagged by any transaction monitoring system. The fictitious accounts traded actively against real customers for years.
