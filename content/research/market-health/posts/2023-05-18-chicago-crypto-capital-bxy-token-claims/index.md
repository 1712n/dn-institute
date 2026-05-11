---
title: "Chicago Crypto Capital BXY Token Custody Claims"
date: 2023-05-18
entities:
  - Chicago Crypto Capital
  - Brian Amoah
  - Elbert Elliott
  - BXY
  - Beaxy Digital
  - Crypto Asset Securities
---

## Summary

This case study analyzes the SEC's Chicago Crypto Capital action as a market-health warning about token-distribution intermediaries that make custody, delivery, markup, account-statement, and issuer-health representations to retail investors. On May 18, 2023, the SEC announced default judgments against Chicago Crypto Capital LLC, its owner Brian Amoah, and former salesman Elbert Elliott.

According to the SEC's litigation release, from August 2018 through November 2019, Chicago Crypto Capital, Amoah, and Elliott acted as unregistered brokers and conducted an unregistered offering of BXY tokens. The release said they raised at least $1.5 million from approximately 100 individuals, many of whom had no experience investing in crypto assets.

The SEC complaint alleged materially false and misleading statements about BXY token custody and delivery, the markup charged by Chicago Crypto Capital, delivery of account statements, liquidation of one investor's BXY, defendants' personal investments in BXY, and financial and management problems at BXY issuer Beaxy Digital Ltd. in late 2019. The SEC also alleged that some investors never received their BXY tokens and that all investors paid an undisclosed markup.

The supporting dataset is available in [chicago-crypto-capital-summary.csv](chicago-crypto-capital-summary.csv).

## Token Distribution Pattern

The SEC release described Chicago Crypto Capital as an intermediary selling BXY tokens to retail investors. That role creates a chain of obligations between the investor, intermediary, custodian or wallet, token issuer, and any secondary-market venue.

For market-health review, a token sale through an intermediary should reconcile investor subscriptions to token allocations, wallet addresses, delivery confirmations, custody records, markup disclosures, account statements, and any issuer disclosures that affect token value. If delivery or custody claims are not independently verifiable, investors may see an account statement without actually controlling the token.

The SEC alleged that the defendants made misleading statements across several of those checkpoints. The result was not only an offering-registration issue; it was also an information-quality problem in the market for the token.

## False Market Signals

### Custody and delivery claim

The SEC alleged false and misleading statements about custody and delivery of BXY tokens and alleged that some investors never received tokens. Delivery should be verified through wallet records, transfer hashes, custodian statements, and investor-controlled addresses.

### Account-statement claim

The complaint alleged misleading statements about delivery of account statements. Account statements should be reconciled to wallet and custody records rather than treated as proof of ownership by themselves.

### Undisclosed markup

The SEC alleged that all investors paid an undisclosed markup on BXY tokens. Price transparency requires the intermediary's acquisition cost, resale price, spread, fees, and conflicts to be disclosed and reconciled.

### Liquidation representation

The complaint alleged misstatements about Chicago Crypto Capital's liquidation of an investor's BXY. Liquidation claims should be checked against executed transactions, venue records, realized price, fees, and proceeds distribution.

### Issuer-health signal

The SEC alleged misleading statements about financial and management problems at Beaxy Digital in late 2019. Intermediaries selling issuer-linked tokens should verify that material issuer-health risks are disclosed to purchasers.

## Event Timeline

| Date or period            | Event                                                                                               | Market-health signal                                                   |
| ------------------------- | --------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| August 2018-November 2019 | The SEC alleged Chicago Crypto Capital, Amoah, and Elliott sold BXY tokens as unregistered brokers. | Intermediary role required custody, delivery, and markup controls.     |
| Offering period           | The SEC alleged at least $1.5 million was raised from approximately 100 individuals.                | Retail scale required investor-level allocation and delivery records.  |
| Offering period           | The SEC alleged false statements about custody, delivery, account statements, and liquidation.      | Statements needed independent wallet and trading evidence.             |
| Offering period           | The SEC alleged all investors paid an undisclosed markup.                                           | Token pricing needed spread and fee transparency.                      |
| Late 2019                 | The SEC alleged misleading statements about Beaxy Digital financial and management problems.        | Issuer-health information was material to token purchasers.            |
| September 14, 2022        | The SEC filed the civil complaint in the Northern District of Illinois.                             | Legal action formalized the alleged token-distribution failures.       |
| May 10, 2023              | The court entered default judgments against Chicago Crypto Capital, Amoah, and Elliott.             | Judgment-stage outcome imposed injunctions, bars, and monetary relief. |
| May 18, 2023              | The SEC announced the default judgments.                                                            | Public enforcement summary documented final remedies.                  |

## Reconciliation Metrics

| Metric               | SEC allegation or judgment figure                                                     | Market-health interpretation                                                          |
| -------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Amount raised        | At least $1.5 million                                                                 | Investor funds needed allocation, custody, delivery, and pricing proof.               |
| Investor count       | Approximately 100 individuals                                                         | Retail scale required reliable investor-level records.                                |
| Token                | BXY                                                                                   | Token ownership needed wallet, custodian, and transfer verification.                  |
| Investor delivery    | Some investors allegedly never received BXY tokens                                    | Account records could diverge from token control.                                     |
| Markup               | All investors allegedly paid an undisclosed markup                                    | Token price required spread and conflict disclosure.                                  |
| Amoah and CCC remedy | $935,599.65 disgorgement plus $136,087.10 prejudgment interest, jointly and severally | Judgment imposed significant monetary relief.                                         |
| Elliott remedy       | $21,777.64 disgorgement plus $3,167.66 prejudgment interest                           | Salesperson-level remedy reflected offering conduct.                                  |
| Civil penalties      | $1,339,368 for CCC, $245,553 for Amoah, and $133,938 for Elliott                      | Penalties reflected default-judgment remedies.                                        |
| Legal posture        | Default judgments entered May 10, 2023                                                | Article can treat judgment entry as final while distinguishing complaint allegations. |

## Detection Checklist

1. Reconcile investor subscriptions to token allocations, wallet transfers, custodian records, and investor-controlled addresses.
2. Verify account statements against blockchain and custody evidence.
3. Compare intermediary acquisition cost, resale price, markup, fees, and conflict disclosures.
4. Reconcile any liquidation claim to executed trades, venue records, realized proceeds, and investor payouts.
5. Verify issuer-health statements against issuer disclosures, management changes, and financial records.
6. Confirm whether brokers or intermediaries are registered or exempt before relying on sales representations.
7. Preserve legal posture: this article relies on SEC allegations and default judgments, so alleged statements should remain clearly attributed to the SEC.

## Market-Health Lessons

Chicago Crypto Capital shows why token ownership is not just an account-statement question. Investors need evidence that tokens were actually delivered or held for them, and market-health reviewers need to connect those records to wallet or custodian data.

The case also shows why undisclosed markups distort token-market information. If retail buyers do not know the spread paid to the intermediary, the apparent token price can misrepresent both market demand and intermediary conflicts.

## References

- [SEC litigation release, Chicago Crypto Capital, May 18, 2023](https://www.sec.gov/enforcement-litigation/litigation-releases/lr-25729)
