---
title: "Mosaic Exchange Trading-Performance Claims and False Liquidity Signals"
date: 2025-01-13
entities:
  - Mosaic Exchange
  - Sean Michael
  - Bitcoin
  - BTC
---

## Summary

This case study analyzes the CFTC's Mosaic Exchange enforcement action as a market-health warning about unverified trading-performance claims. The CFTC filed its complaint in September 2023, and on January 13, 2025, announced final default judgment orders against Mosaic Exchange Ltd. and its owner and CEO, Sean Michael. The court ordered approximately $468,600 in restitution, $60,980 in disgorgement, and a $660,000 civil monetary penalty.

The market-health problem was not a public order-book manipulation allegation. It was a private trading platform narrative that used false claims about assets under management, proprietary trading accuracy, monthly profit margins, and exchange partnerships to induce customers to transfer bitcoin and other funds. The CFTC said Mosaic did not have the represented AUM, did not generate the represented win rates, lost money trading for customers, and did not have the advertised partnership or broker agreements with cryptocurrency exchanges.

The supporting dataset is available in [mosaic-exchange-summary.csv](mosaic-exchange-summary.csv).

## Trading Narrative

According to the CFTC's September 2023 complaint summary, from approximately February 2019 through June 2021 Mosaic solicited at least 17 people in the United States and other countries to provide bitcoin or other funds for trading. Mosaic allegedly advertised itself as a cryptocurrency trading platform with tens of millions of dollars in assets under management and a proprietary algorithm that was 82% accurate.

The solicitation also allegedly used extreme monthly performance claims. The CFTC said Mosaic represented profit margins at various times ranging from 20% to 60% per month and 10% to more than 50% per month. By January 2025, the default judgment order found the win-rate claims were not actual trading results but hypothetical projections, and that Mosaic's trading accounts did not generate the profits represented.

## Market-Health Indicators

### AUM claims without custody proof

Assets under management can create a false liquidity signal. A platform that claims tens of millions of dollars in AUM appears more credible, more liquid, and more operationally mature than a small unverified operation. Market-health reviews should require custody records, independent administrator records, bank or wallet attestations, and audited reporting before treating AUM claims as evidence of real scale.

### Algorithmic win rates

An 82% trading-algorithm accuracy claim is a performance statistic, not a market fact. It should be checked against trade-level records, realized P&L, benchmark selection, fees, slippage, and drawdowns. The CFTC's final order found Mosaic did not generate the represented win rates but instead used hypothetical projections. That distinction is critical: hypothetical backtests can be useful, but presenting them as realized trading performance can mislead customers about risk and liquidity.

### Monthly profit ranges

Monthly return claims of 20% to 60%, or 10% to more than 50%, should trigger immediate scrutiny. The higher the claimed return, the more important it is to verify position history, venue execution, realized gains, and capital at risk. Market-health systems should not treat promised or advertised returns as evidence of trading skill without external records.

### Exchange partnership claims

The CFTC said Mosaic advertised partnership or broker agreements with cryptocurrency exchanges that it did not have. Exchange relationships can imply privileged liquidity, better execution, lower fees, or institutional-grade access. Verification should come from the named exchange or written agreements, not from the promoter's marketing material.

## Detection Checklist

1. Verify AUM using custody, bank, wallet, administrator, or auditor records.
2. Reconcile advertised strategy performance against trade-level realized P&L.
3. Separate hypothetical projections, backtests, and demo results from live customer-account performance.
4. Require named exchanges to confirm partnership, broker, or liquidity-provider claims.
5. Compare customer deposit flows with actual trading-account funding and realized trading losses.
6. Treat extreme monthly return claims as a risk signal requiring independent evidence.
7. Preserve enforcement posture: this article relies on CFTC complaint allegations and the January 2025 final default judgment order.

## Market-Health Lessons

Mosaic shows how market-health analysis must extend beyond public trade feeds. Private trading platforms and commodity pools can manufacture credibility through performance statistics, AUM numbers, and exchange-affiliation claims. Those claims influence customer behavior in the same way exchange volume or order-book depth might influence a trader: they create an impression of scale, competence, and liquidity.

The core test is external verifiability. If a platform claims large AUM, high strategy accuracy, major exchange relationships, and extraordinary monthly returns, each claim should be independently testable. If the platform cannot produce reliable custody records, trade logs, exchange confirmations, and realized P&L, the claimed market signal should not be treated as market evidence.

## References

- [CFTC press release 8789-23, September 27, 2023](https://www.cftc.gov/PressRoom/PressReleases/8789-23)
- [CFTC press release 9032-25, January 13, 2025](https://www.cftc.gov/PressRoom/PressReleases/9032-25)
