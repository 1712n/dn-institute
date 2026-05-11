---
title: "Forcount Trader Systems Membership Return Claims"
date: 2022-12-14
entities:
  - Forcount Trader Systems
  - Forcount
  - Weltsys
  - Mindexcoin
  - Francisley Valdevino Da Silva
  - Juan Antonio Tacuri Fajardo
---

## Summary

This case study analyzes Forcount Trader Systems as a market-health warning about membership products that convert claimed crypto trading and mining profits into referral-driven return displays. On December 14, 2022, the SEC charged Francisley Valdevino Da Silva, Juan Antonio Tacuri Fajardo, Ramon Antonio Perez Arias, and Jose Ramiro Coronado Reyes for roles in creating and promoting Forcount, which the SEC described as a fraudulent crypto asset pyramid scheme that raised more than $8.4 million from hundreds of retail investors.

The SEC said Forcount memberships supposedly gave investors an interest in profits from crypto asset trading and mining operations. It also said the defendants knew, or were reckless in not knowing, that Forcount had no crypto asset trading and mining operations and that the scheme could continue only by expanding its investor base. DOJ's parallel release described the related withdrawal-failure pattern and said Forcount later offered Mindexcoin as a proprietary token that was essentially worthless.

The supporting dataset is available in [forcount-summary.csv](forcount-summary.csv).

## Trading Narrative

Forcount can be tested with a membership-to-market model. A membership that claims exposure to crypto trading and mining should reconcile to trading accounts, mining payouts, wallet flows, member-level allocations, and withdrawal capacity. The SEC's public release breaks that model at the source: it says there were no crypto asset trading and mining operations, and that new investor recruitment was the mechanism needed to continue the scheme.

The referral layer is part of the market-health problem. When returns depend on recruitment economics rather than trading or mining output, member dashboards can display growth while the underlying system becomes more fragile. The SEC said Forcount's referral program incentivized recruiting new victims, and DOJ said promoters held events, displayed wealth, and sold investment products through cash, checks, wires, and cryptocurrency. Those channels created the appearance of a growing crypto business without proving market activity.

The Mindexcoin phase shows a familiar liquidity-substitution pattern. DOJ said that as complaints mounted, Forcount began offering proprietary crypto-tokens called Mindexcoin, with promoters claiming they would become valuable when accepted for payment. DOJ said that was false and that the tokens were essentially worthless. In market terms, the scheme moved from claimed mining/trading returns to claimed token utility when redemption pressure increased.

## False Market Signals

### Membership exposure to trading and mining

Forcount memberships were promoted as interests in profits from supposed crypto asset trading and mining. A real product would need member-level allocation records, venue statements, mining-pool payouts, wallet flows, and expense reconciliation.

### Guaranteed return framing

DOJ said Forcount promised guaranteed daily returns and doubling of investments within six months. Such return framing conflicts with volatile crypto trading and mining economics unless actual losses, fees, and capacity limits are visible.

### Referral-program growth

The SEC said the referral program incentivized recruiting new victims. Recruitment can increase deposits and apparent activity, but it does not prove trading profits. Referral-driven growth should be separated from market-generated returns.

### Withdrawal difficulty

DOJ said withdrawal problems appeared around April 2018 for Forcount, with excuses, delays, and hidden fees. Withdrawal failure is an immediate signal that portal balances may not represent realizable value.

### Mindexcoin liquidity story

Mindexcoin converted redemption stress into a future token-utility claim. A token created during withdrawal pressure requires independent market-depth, wallet, merchant-acceptance, and redemption-history checks.

## Event Timeline

| Date or period          | Event                                                                                           | Market-health signal                                                    |
| ----------------------- | ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| July 2017 onward        | SEC said Forcount memberships were sold with claimed crypto trading and mining profit exposure. | Member returns required proof of actual trading and mining operations.  |
| April 2018              | DOJ said Forcount victims attempting withdrawals had difficulty.                                | Redemption friction undermined displayed return balances.               |
| July 2017-November 2020 | SEC said the defendants raised more than $8.4 million from hundreds of retail investors.        | Deposit growth needed to be separated from market-generated returns.    |
| 2018-2021               | DOJ said Forcount promoted investment products through events and presentations.                | Social proof did not verify underlying trading or mining.               |
| 2018-2021               | DOJ said Forcount offered Mindexcoin as complaints mounted.                                     | Proprietary token issuance reframed liquidity stress as future utility. |
| 2021                    | DOJ said Forcount had stopped making payments to victims by about 2021.                         | The return system failed when redemption pressure persisted.            |
| December 14, 2022       | SEC announced civil charges tied to Forcount's $8.4 million fraud.                              | Civil enforcement challenged membership, referral, and return claims.   |
| December 14, 2022       | DOJ announced parallel criminal charges involving Forcount and IcomTech.                        | Criminal allegations connected return portals, withdrawals, and tokens. |

## Reconciliation Metrics

| Metric                          | Enforcement-record figure                                           | Market-health interpretation                                        |
| ------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| SEC-described fundraising       | More than $8.4 million from hundreds of retail investors            | Scale required proof of trading, mining, and member allocations.    |
| Claimed source of returns       | Crypto asset trading and mining operations                          | Must reconcile to exchanges, mining pools, wallets, costs, and P&L. |
| SEC-described operations        | No crypto asset trading and mining operations                       | Claimed market source did not exist, according to the SEC.          |
| Referral program                | Incentivized recruiting new victims                                 | Deposit growth risked being confused with investment performance.   |
| DOJ-described withdrawal issues | Difficulty around April 2018, with delays, excuses, and hidden fees | Withdrawal problems undermined the meaning of displayed balances.   |
| Mindexcoin outcome              | DOJ said the token was essentially worthless                        | Token utility did not solve redemption or market-value gaps.        |
| Payment-stop period             | Payments stopped by about 2021                                      | Return displays failed the cash-out test.                           |

## Detection Checklist

1. Reconcile membership returns to actual trading accounts, mining-pool payouts, wallet flows, fees, and realized P&L.
2. Separate referral commissions and recruitment-driven deposits from market-generated profits.
3. Treat guaranteed daily returns or six-month doubling claims as high-risk until actual loss periods and capacity limits are shown.
4. Test member dashboard balances against successful withdrawal history.
5. Review whether new proprietary tokens are introduced after withdrawal complaints.
6. Verify token utility with independent merchants, exchange liquidity, issuer-wallet analysis, and redemption records.
7. Track whether promotional events and wealth displays are substituting for market evidence.
8. Preserve legal posture: this article relies on SEC and DOJ public statements and complaint allegations.

## Market-Health Lessons

Forcount shows how a membership product can blur three different signals: recruitment, displayed returns, and actual market performance. The safest review order is to verify trading and mining records first, then member allocations, then withdrawal capacity, and only then promotional or referral metrics.

Mindexcoin adds the second lesson. A proprietary token introduced after withdrawal problems should be treated as a liquidity-risk signal, not as an independent solution. Without real market depth and redemption utility, the token can extend the dashboard narrative while investor cash-out remains blocked.

## References

- [SEC press release 2022-227, December 14, 2022](https://www.sec.gov/newsroom/press-releases/2022-227)
- [DOJ IcomTech and Forcount charging release, December 14, 2022](https://www.justice.gov/usao-sdny/pr/us-attorney-announces-fraud-and-money-laundering-charges-against-founders-and-promoters)
- [SEC complaint against Forcount defendants](https://www.sec.gov/file/sec-complaint-2242)
