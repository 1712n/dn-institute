---
title: "BitMEX: Market Manipulation Through Liquidation Cascades and Trading Against Customers"
date: "2016-01 -- 2020-10"
description: "BitMEX, once the world's largest Bitcoin derivatives exchange, was charged by the CFTC and DOJ for operating an unregistered trading platform, facilitating money laundering, and allegedly engaging in practices that systematically disadvantaged its own customers through its liquidation engine design."
entities:
  - BitMEX
  - Arthur Hayes
---

## Summary

In October 2020, the U.S. Commodity Futures Trading Commission and Department of Justice simultaneously filed civil and criminal charges against BitMEX and its founders, including CEO Arthur Hayes. The charges centered on operating an unregistered trading platform and willfully violating Bank Secrecy Act requirements. Beyond the regulatory violations, extensive analysis by researchers and traders had documented patterns suggesting BitMEX's liquidation engine and system design systematically extracted value from leveraged traders through cascading liquidations, server overloads during volatile periods, and order execution practices that benefited the exchange's insurance fund at the expense of customers.

## The Liquidation Engine

BitMEX's core business was high-leverage Bitcoin perpetual futures, offering up to 100x leverage. The exchange's liquidation engine operated on a socialized loss model where positions that fell below maintenance margin were automatically liquidated and closed at the bankruptcy price rather than the current market price.

When a position was liquidated, if the closing price was better than the bankruptcy price, the difference went to BitMEX's insurance fund rather than being returned to the liquidated trader. This created a direct financial incentive for the exchange to trigger liquidations and close them at favorable prices.

During periods of high volatility, cascading liquidations became self-reinforcing. One trader's liquidation would push the price further, triggering additional liquidations in a chain reaction. BitMEX's insurance fund grew substantially during these cascades, suggesting the exchange benefited more from volatile liquidation events than from normal trading fee revenue.

## System Overloads During Volatility

Traders documented repeated instances where the BitMEX trading engine became unresponsive or severely degraded during periods of high volatility, precisely when traders most needed to manage their positions. The pattern was consistent: prices would move sharply, the interface would freeze or return errors, and by the time traders could interact with the platform again, their positions had been liquidated.

While BitMEX attributed these issues to traffic spikes, the timing raised questions about whether the degradation disproportionately affected position management (closing or reducing positions) relative to the liquidation engine (which continued operating during the same periods).

## Regulatory Action

The CFTC charged BitMEX with operating a facility for trading commodity futures and options without proper registration and violating multiple customer protection regulations. The DOJ filed parallel criminal charges against founders Arthur Hayes, Benjamin Delo, and Samuel Reed for willfully failing to establish an adequate anti-money laundering program.

Hayes pleaded guilty to violating the Bank Secrecy Act in February 2022 and was sentenced to two years of probation and a $10 million fine. BitMEX paid $100 million in penalties to settle with the CFTC and FinCEN.

## Detection Patterns

BitMEX's practices illustrate manipulation patterns relevant to derivatives exchange monitoring:

- **Insurance fund growth correlation with liquidation volume.** An insurance fund that grows disproportionately during high-volatility events suggests the liquidation mechanism is extracting excess value from traders beyond what is necessary for platform risk management.
- **System availability asymmetry.** If trading interface degradation correlates with volatile market conditions but the liquidation engine continues operating normally, the asymmetry creates conditions where customers cannot protect their positions while the exchange continues to process forced closures.
- **Liquidation cascade frequency.** Markets with very high leverage (50-100x) are structurally prone to cascading liquidations. Monitoring the frequency and depth of liquidation cascades relative to underlying market volatility can distinguish between organic market moves and amplified cascade events.
