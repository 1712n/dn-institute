---
title: "EmpiresX Fake Trading Platform and Synthetic Return Signals"
date: 2025-02-04
entities:
  - EmpiresX
  - Empires Consulting Corp.
  - Emerson Pires
  - Flavio Goncalves
  - Joshua Nicholas
---

## Summary

This case study analyzes EmpiresX as a market-health warning about fake trading-performance signals. The CFTC announced a February 2025 default judgment against Emerson Pires, Flavio Goncalves, and Joshua Nicholas for fraud in connection with the EmpiresX commodity pool scheme. The CFTC said the order required Pires and Goncalves to pay more than $32 million in disgorgement and more than $96 million in civil monetary penalties, while Nicholas was ordered to pay $289,000 in disgorgement and $867,000 in penalties.

The market-health problem was not simply that investors lost money. EmpiresX allegedly manufactured the evidence investors would normally use to evaluate trading quality: a purported trading bot, claimed daily profits, a supposed profitable account at a large electronic trading platform, and a fake website that mimicked that platform. Those signals made customers believe the pool was trading successfully when regulators later said the bot was fake, trading produced losses, and only a small portion of investor funds reached a brokerage account.

The supporting dataset is available in [empiresx-summary.csv](empiresx-summary.csv).

## Trading Narrative

According to the CFTC, the EmpiresX defendants began soliciting individuals around September 2020 to trade commodity futures, options, and other products through commodity interest pools. The solicitation used the EmpiresX website, online videos, social platforms, calls, and electronic messages. During the relevant period, Pires, Goncalves, and Empires Consulting accepted and pooled at least $41.6 million from more than 12,500 individuals.

The SEC's separate litigation release described the platform as a fake trading scheme. It said EmpiresX sold investments touting daily profits of one percent supposedly earned by a trading bot or by Nicholas' manual trading. The SEC alleged the bot was fake, Nicholas' trading generated significant losses, and only a small portion of investor funds was transferred to EmpiresX's brokerage account.

DOJ described the same core narrative in the criminal case. Nicholas pleaded guilty in September 2022 to conspiracy to commit securities fraud in connection with a cryptocurrency-based Ponzi scheme that took in approximately $100 million from investors. DOJ said EmpiresX promoted a purported proprietary trading bot and guaranteed returns, but paid earlier investors with money from later investors.

## False Market Signals

### One-percent daily profit claims

Daily return claims are market signals because they imply a repeatable source of edge, liquidity, and risk control. A one-percent daily profit narrative should be reconciled against trade-level executions, brokerage statements, account balances, fees, losses, and open positions. In EmpiresX, regulators said those claims were not supported by real trading performance.

### Trading bot credibility

Automated trading can be legitimate, but the existence of a bot is not evidence of profitable market activity. The useful market-health test is whether the strategy has auditable orders, fills, timestamps, balances, and risk limits. The SEC alleged the EmpiresX bot was fake, which turns a technology claim into a synthetic performance signal.

### Mimicked platform account pages

The CFTC said Nicholas showed participants an account page he identified as EmpiresX's profitable account with a large electronic trading platform, even though EmpiresX had no account with that platform. The order also found the defendants created a fake website that mimicked the platform's website to make participants believe their funds were being traded.

This is a different risk from wash trading on a public venue. The false venue interface itself becomes the market display. Customers see balances, profit history, and trading activity that look like market evidence but are controlled by the promoter.

### Withdrawal failure as a late signal

By November 2021, the CFTC said the defendants stopped honoring participant withdrawal requests. Withdrawal failure is often a lagging indicator: by the time customers cannot exit, the earlier false signals have already influenced deposits, reinvestment decisions, and referrals. Market-health reviews should treat delayed withdrawals as a trigger to recheck whether the advertised trading activity ever existed.

## Event Timeline

| Date or period        | Event                                                                                  | Market-health signal                                                                     |
| --------------------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| September 2020 onward | EmpiresX solicited participants for commodity pools through websites and social media. | Public marketing created a scale and performance narrative.                              |
| 2020 to 2021          | The platform promoted daily one-percent profits from a trading bot or manual trading.  | Return claims required independent trade and account verification.                       |
| Relevant CFTC period  | At least $41.6 million was pooled from more than 12,500 individuals.                   | Customer inflows far exceeded verified trading evidence described by regulators.         |
| November 2021         | Withdrawal requests stopped being honored, according to the CFTC.                      | Exit friction became a late-stage warning sign.                                          |
| June 30, 2022         | CFTC and SEC filed related civil actions.                                              | Regulators challenged the trading-performance narrative.                                 |
| September 8, 2022     | Nicholas pleaded guilty in the DOJ criminal case.                                      | Criminal resolution confirmed the false-bot and guaranteed-return narrative.             |
| May 12, 2023          | SEC announced final judgment against Nicholas.                                         | SEC said the bot was fake and trading generated losses.                                  |
| February 4, 2025      | CFTC announced default judgment against Pires, Goncalves, and Nicholas.                | Final CFTC order imposed monetary sanctions, injunctions, and trading-registration bans. |

## Detection Checklist

1. Require broker, exchange, or custodian records before accepting claimed account balances.
2. Match promoted daily returns to timestamped orders, fills, fees, and realized P&L.
3. Verify that any referenced trading venue confirms the account relationship directly.
4. Treat screenshots, dashboards, and account pages as untrusted until they can be reconciled to external records.
5. Separate bot existence from bot performance: code, logs, and deployment claims are not substitutes for trade records.
6. Monitor withdrawal delays, new fee demands, and tax-or-unlock demands as signs that displayed profits may be fabricated.
7. Compare customer inflows with actual brokerage deposits and trading-account balances.
8. Preserve legal posture: this article relies on CFTC order findings, SEC allegations and judgment materials, and DOJ plea-release statements.

## Market-Health Lessons

EmpiresX shows that market-health analysis must cover private trading displays, not only public order books. A fabricated exchange screen, bot dashboard, or account statement can influence investor behavior in the same way inflated exchange volume does: it makes the market appear deeper, more active, and more profitable than the underlying evidence supports.

The practical control is independent reconciliation. Claimed returns should reconcile to broker statements. Claimed venue accounts should be confirmed by the venue. Claimed automated strategies should reconcile to order logs and realized P&L. Claimed balances should reconcile to custodial or bank records. If those external checks fail, the displayed performance should be treated as marketing content rather than market data.

## References

- [CFTC press release 9045-25, February 4, 2025](https://www.cftc.gov/PressRoom/PressReleases/9045-25)
- [SEC litigation release 25722, May 12, 2023](https://www.sec.gov/enforcement-litigation/litigation-releases/lr-25722)
- [DOJ press release 22-951, September 8, 2022](https://www.justice.gov/archives/opa/pr/empiresx-head-trader-pleads-guilty-global-cryptocurrency-investment-fraud-scheme-amassed)
- [CFTC complaint, June 30, 2022](https://www.cftc.gov/media/7436/enfempirescomplaint063022/download)
