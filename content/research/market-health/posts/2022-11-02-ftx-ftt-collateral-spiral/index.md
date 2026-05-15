---
title: "FTX FTT Collateral Spiral"
date: 2022-11-02
entities:
  - FTX
  - Alameda Research
  - FTT
  - Binance
  - Sam Bankman-Fried
---

## Summary

In November 2022, FTX and Alameda Research became a market-health stress case when the market learned how much of Alameda's reported balance sheet depended on FTX's own exchange token, FTT. [CoinDesk reported](https://www.coindesk.com/business/2022/11/02/divisions-in-sam-bankman-frieds-crypto-empire-blur-on-his-trading-titan-alamedas-balance-sheet) that a private Alameda balance sheet showed $3.66 billion of unlocked FTT and $2.16 billion of FTT collateral among $14.6 billion of assets.

The risk was not only that FTT could fall. The risk was reflexive: a token issued by FTX was being treated as a major asset and collateral input for Alameda, while market confidence in FTX also depended on Alameda's solvency. When confidence broke, FTT price pressure, exchange withdrawals, and collateral-quality concerns reinforced each other.

On November 6, 2022, [CoinDesk reported](https://www.coindesk.com/business/2022/11/06/binance-sells-holdings-of-ftx-token-as-alameda-ceo-defends-firms-financial-condition) that Binance planned to sell its remaining FTT holdings after receiving roughly $2.1 billion in BUSD and FTT as part of its FTX equity exit. [TechCrunch also summarized](https://techcrunch.com/2022/11/07/heres-the-rundown-on-the-binance-and-ftx-fiasco/) Binance's public sale announcement and Alameda's response as the dispute became a market confidence event.

The market-health issue was exchange-token collateral concentration. A venue token can support incentives, fee discounts, and treasury accounting, but it becomes fragile collateral when issuer solvency, token liquidity, market-maker balance sheets, and customer withdrawals all depend on the same confidence loop.

## Risk Transmission Analysis

The first vector was balance-sheet concentration in a related-party asset. CoinDesk's balance-sheet reporting made the concentration visible: Alameda's listed FTT exposure was large enough that the market could no longer treat the token as a normal liquid reserve. A collateral pool backed by an affiliated issuer token has correlated default risk. If the exchange is questioned, the token weakens; if the token weakens, the trading firm's collateral weakens; if the trading firm's collateral weakens, the exchange is questioned again.

The second vector was float and liquidity mismatch. Reported FTT balances were measured in notional dollars, but the tradable market depth available during a confidence shock was much smaller than the headline asset value. That made the marked value sensitive to selling pressure. A large holder publicly planning to sell added a market-depth shock at the same time that counterparties were rechecking Alameda's collateral quality.

The third vector was withdrawal contagion. FTX customers did not need to model every internal loan or balance-sheet line. Once FTT-linked solvency concerns became public, rational customers had an incentive to withdraw before other customers. That turns a token-collateral concern into a platform-liquidity run. [Ars Technica later summarized](https://arstechnica.com/tech-policy/2022/11/ftx-on-brink-of-collapse-after-binance-abandons-rescue/) the sequence as a confidence shock that quickly turned into liquidity stress and an attempted rescue.

The fourth vector was alleged price support. [The CFTC later alleged](https://www.cftc.gov/PressRoom/PressReleases/8638-22) that FTX-linked actors used Alameda privileges and customer funds in a broader fraudulent scheme, while [SEC/CFTC coverage also highlighted](https://www.securities.io/sec-and-cftc-charge-co-conspirators-in-ftx-collapse-ftt-labeled-crypto-security-token/) regulator focus on FTT's role in the collapse. For market-health monitoring, the important lesson is that thinly traded related-party tokens should be treated as impaired collateral unless their price can survive unaffiliated selling, exchange outflows, and disclosure shocks.

## Metrics Used

### Affiliated-token collateral share

The core indicator is the share of reported assets, collateral, or borrow capacity tied to a token issued by the same corporate group. CoinDesk's reported figures put unlocked FTT and FTT collateral at $5.82 billion combined. Against $14.6 billion of reported assets, that was roughly 39.9% of Alameda's reported asset base tied to FTT exposure.

Useful metrics include:

- affiliated-token exposure as a share of total assets;
- affiliated-token exposure as a share of borrow collateral;
- unlocked versus locked token balance;
- token issuer relationship to the borrower or venue;
- collateral haircut applied to affiliated tokens.

### Market depth versus marked collateral value

Market-health systems should compare marked token value with realistic liquidation capacity. If the market can absorb only a fraction of the marked collateral before price impact becomes severe, then book value should not be treated as executable liquidity.

Useful metrics include:

- order-book depth within 2%, 5%, and 10%;
- daily spot volume versus collateral notional;
- largest holder sell overhang;
- OTC bid availability;
- exchange concentration for token liquidity.

### Withdrawal-run pressure

The FTX episode shows that collateral doubts can become exchange-liquidity pressure within days. Withdrawal velocity is therefore a direct market-health signal, not only an operations metric.

Useful metrics include:

- customer withdrawal requests by hour;
- net exchange reserves by asset;
- withdrawal processing delay;
- suspended asset or chain count;
- changes in stablecoin, BTC, and ETH hot-wallet balances.

### Public confidence triggers

Public disclosures can change collateral quality even before on-chain flows move. CoinDesk's balance-sheet report and Binance's FTT-sale announcement were both narrative events that changed market assumptions about solvency, liquidity, and liquidation pressure.

Useful metrics include:

- major holder sale announcements;
- balance-sheet leak or disclosure timing;
- issuer, affiliate, or executive response latency;
- spread between token spot price and internal collateral value;
- social and news velocity around solvency terms.

The same fields are summarized in [ftx-ftt-collateral-signals.csv](ftx-ftt-collateral-signals.csv) for dataset-based review.

| Signal                     | Observation                                                                                                           | Market-health interpretation                                                      |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| ftt_balance_sheet_exposure | CoinDesk reported $3.66 billion unlocked FTT and $2.16 billion FTT collateral on Alameda's balance sheet              | Track affiliated-token concentration inside reported assets and borrow collateral |
| related_party_collateral   | FTT was issued by FTX while Alameda and FTX were both controlled by Sam Bankman-Fried                                 | Apply steep haircuts to collateral that is correlated with issuer solvency        |
| holder_sale_overhang       | Binance said it would sell remaining FTT holdings after receiving BUSD and FTT from its FTX equity exit               | Watch large-holder liquidation intent as a depth and confidence shock             |
| withdrawal_run_pressure    | FTT uncertainty preceded large customer withdrawals from FTX                                                          | Escalate token-collateral stress when it becomes venue-liquidity stress           |
| alleged_price_support      | U.S. regulator allegations later described Alameda manipulation of FTT's market price to inflate collateral value     | Treat thin related-party token prices as unreliable collateral inputs             |
| reflexive_confidence_loop  | FTX confidence depended on Alameda solvency, while Alameda collateral quality depended on FTT and therefore FTX trust | Flag circular solvency dependencies between venue, market maker, and token        |

## Timeline

- **November 2, 2022:** CoinDesk reported that Alameda's balance sheet was heavily exposed to FTT, including $3.66 billion of unlocked FTT and $2.16 billion of FTT collateral.
- **November 6, 2022:** Binance said it would sell remaining FTT holdings. CoinDesk and TechCrunch both reported the announcement and the stated post-exit risk-management rationale.
- **November 7-8, 2022:** Market confidence weakened as FTT collateral concerns met customer withdrawal incentives. Alameda's public response did not remove the core related-party collateral concern.
- **November 9-11, 2022:** Binance walked away from an FTX rescue process, and [The Guardian reported](https://www.theguardian.com/technology/2022/nov/11/cryptocurrency-exchange-ftx-files-for-bankruptcy-protection-in-us) that FTX filed for U.S. bankruptcy protection shortly afterward. The token-collateral concern had become a full exchange-solvency event.
- **December 2022 and after:** U.S. regulators alleged that FTX-linked actors manipulated FTT's market price, reinforcing the market-health lesson that issuer-affiliated tokens should not be valued like independent liquid collateral.

## Market Health Lessons

FTX's FTT spiral shows why affiliated exchange tokens need special collateral treatment. The risk is not just price volatility. It is circularity: the same confidence variable can support the venue, the token, the market maker, and the borrow book.

A useful control is an affiliated-token haircut rule. If a borrower, exchange, issuer, market maker, or major creditor is economically tied to the token, then the collateral system should discount that token far more aggressively than an independent liquid asset. The haircut should become stricter when the token's marked collateral value exceeds realistic market depth.

A second control is a withdrawal-run escalation rule. Once token-collateral stress coincides with exchange outflows, the incident has moved from balance-sheet risk to platform-liquidity risk. At that point, proof-of-reserves, withdrawal latency, hot-wallet balances, and large-holder overhang should be monitored together.

For Market Health, the event is a template for detecting circular collateral. If a venue token props up a related trading firm, and that firm's perceived solvency props up the venue, then price support can mask fragility until a disclosure or large-holder sale forces the loop to unwind.
