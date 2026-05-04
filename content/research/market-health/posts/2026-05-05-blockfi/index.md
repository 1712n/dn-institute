---
date: 2026-05-05
entities:
  - id: blockfi
    name: BlockFi
    type: cefi
  - id: ftx
    name: FTX
    type: exchange
  - id: alameda-research
    name: Alameda Research
    type: trading-firm
  - id: sec
    name: Securities and Exchange Commission
    type: regulatory
  - id: zac-prince
    name: Zac Prince
    type: person
title: "BlockFi interest-account collapse and the FTX-Alameda credit dependency"
---

## 1. Introduction and incident overview

BlockFi was one of the best-known centralized crypto lending platforms of the 2020-2021 cycle. It offered retail customers interest accounts, crypto-backed loans, credit-card products, and institutional services. Its flagship product, the BlockFi Interest Account (BIA), let customers deposit crypto assets and earn variable yield. BlockFi then used deposited assets in lending and other revenue-generating activities.

The company entered 2022 already under regulatory pressure. In February, the U.S. Securities and Exchange Commission announced a settlement with BlockFi Lending LLC over unregistered offers and sales of BIAs, including a $50 million SEC penalty and an additional $50 million in state settlements. Later that year, BlockFi suffered market losses and exposure to Three Arrows Capital, accepted a rescue credit facility from FTX US, became increasingly dependent on FTX and Alameda Research, paused withdrawals after FTX collapsed, and filed for Chapter 11 bankruptcy on 28 November 2022.

BlockFi is a market-health case study because it demonstrates rescue dependency. A lending platform weakened by one market shock can appear stabilized by a larger counterparty, only for that rescue counterparty to become the next failure node. Customers who thought they were earning passive yield were ultimately exposed to institutional lending, collateral quality, FTX exchange custody, Alameda credit risk, regulatory constraints, and bankruptcy claim treatment.

## 2. Business model and regulatory background

### 2.1 BlockFi Interest Accounts

BIAs allowed customers to lend crypto assets to BlockFi in exchange for monthly interest. Economically, the customer gave BlockFi control over deposited assets, and BlockFi sought yield by deploying those assets through institutional lending and related activities. This differed from self-custody and from fully reserved exchange balances. Customers were taking BlockFi credit risk, even if the app experience felt like a savings product.

The SEC's February 2022 order stated that from March 2019 onward, BlockFi offered and sold BIAs to the public without registering them as securities or qualifying for an exemption. The SEC also said BlockFi operated for more than 18 months as an unregistered investment company because it issued securities and held more than 40 percent of its total assets, excluding cash, in investment securities including crypto-asset loans to institutional borrowers. BlockFi settled without admitting or denying the SEC's findings.

### 2.2 Yield source opacity

The SEC also found that BlockFi made a false and misleading website statement for more than two years concerning the level of risk in its loan portfolio and lending activity. That finding is central to the market-health lesson. In crypto lending, yield comes from somewhere: borrower demand, staking rewards, trading strategies, market-making returns, subsidies, or token incentives. If users cannot evaluate where yield comes from and what risks support it, the product can look safer than it is.

BlockFi's customer base included retail users who may not have understood that their deposited crypto could be lent to institutional borrowers or that losses in those loans could affect withdrawals. Interest-account products are therefore not only technical products; they are disclosure products. The risk disclosure needs to be as visible as the yield number.

### 2.3 Institutional lending risk

BlockFi's institutional lending business involved extending credit to trading firms, funds, and market participants. In strong markets, this can generate yield. In stressed markets, collateral values fall, borrowers default, and lenders may discover that collateral is illiquid, correlated, or legally difficult to seize.

Crypto collateral is especially reflexive. Borrowers often pledge crypto assets to borrow stablecoins or other crypto assets. If the market falls, collateral values decline at the same time that borrowers' trading books lose money. If collateral includes exchange tokens, locked tokens, or claims on related parties, the lender may be exposed to the same ecosystem shock through multiple paths.

## 3. The 2022 stress sequence

### 3.1 Three Arrows Capital shock

The collapse of Three Arrows Capital in mid-2022 damaged several crypto lenders. BlockFi was among firms reported to have exposure to 3AC. The 3AC event forced lenders to reassess borrower risk, liquidity reserves, and collateral assumptions. Even if a lender survived the immediate shock, the market understood that centralized crypto credit was more fragile than advertised.

BlockFi responded by reducing headcount and seeking external support. The company framed its risk management as stronger than some peers, but the need for support showed that the credit cycle had changed. The easy-yield environment of 2021 had become a survival test.

### 3.2 FTX US credit facility

In July 2022, BlockFi announced a deal with FTX US that included a $400 million revolving credit facility and an option for FTX US to acquire BlockFi, with the acquisition price dependent on performance triggers. At the time, FTX and Sam Bankman-Fried were widely portrayed as rescuers of distressed crypto firms. For BlockFi, the facility provided liquidity and confidence after the 3AC shock.

The facility also created dependency. A rescue line is only as good as the rescuer's solvency and willingness to fund. By tying its survival narrative to FTX, BlockFi became exposed to FTX's reputation, balance sheet, and affiliated trading firm Alameda Research. This was not obvious to all retail users at the time because FTX still appeared liquid and powerful.

### 3.3 Alameda and FTX exposure

By the time BlockFi filed for bankruptcy, its filings and later recovery efforts showed major exposure to FTX and Alameda. BlockFi had assets on the FTX platform and loan exposure to Alameda, with claims that were later addressed through the FTX and Alameda bankruptcy estates. Some of the Alameda-related exposure was reportedly collateralized by assets linked to the FTX ecosystem, including FTT, making collateral quality highly correlated with the borrower's affiliated exchange.

This structure created wrong-way risk. If Alameda was under stress because FTX-linked assets were losing value, collateral tied to FTX or FTT would also deteriorate. A lender does not receive true protection when the collateral is most valuable only in the world where the borrower remains healthy.

### 3.4 FTX collapse and withdrawal pause

In November 2022, FTX experienced a rapid liquidity crisis and filed for bankruptcy. BlockFi paused withdrawals shortly after FTX's distress became public, citing significant exposure to FTX and associated corporate entities. The pause was the point at which BlockFi's rescue dependency became customer harm.

On 28 November 2022, BlockFi and several affiliates filed for Chapter 11 bankruptcy in New Jersey. The company listed large assets and liabilities and more than 100,000 creditors. The filing moved customers from an app-based withdrawal model into a court-supervised claims and distribution process.

## 4. Mechanics of the failure

### 4.1 Maturity mismatch

BlockFi's retail product offered customers a liquid account experience. Customers expected to withdraw assets, subject to platform terms and operational limits. BlockFi's asset side included loans, claims, and exchange balances that were not equally liquid during a crisis. When FTX failed and customer confidence dropped, liquidity demand rose exactly when asset liquidity fell.

This is the same structural mismatch seen across 2022 CeFi failures. Demand-like liabilities were supported by risky or illiquid assets. The mismatch can remain hidden in a bull market because withdrawals are manageable and collateral values rise. It becomes visible when many users want out at once.

### 4.2 Counterparty concentration

BlockFi's story shows that counterparty concentration can migrate over time. In June 2022, the market focused on 3AC exposure. After the FTX rescue facility, the more important risk became FTX and Alameda. A platform can reduce one exposure while creating another.

Market-health monitoring should therefore track not just whether a distressed platform has received a rescue, but who provided it and what new dependencies the rescue creates. If a lender's recovery depends on one exchange group, customer risk has not disappeared; it has moved.

### 4.3 Collateral quality and wrong-way risk

Collateral should protect a lender from borrower default. It fails when collateral value is tightly linked to the borrower's own solvency. FTT and FTX-linked assets were poor protection against Alameda or FTX-group stress because their value depended on market confidence in the same ecosystem.

This is a general rule for crypto credit: exchange tokens, affiliated tokens, locked allocations, and thinly traded assets need severe haircuts when used as collateral for loans to related or highly correlated borrowers.

### 4.4 Custody and exchange exposure

Holding assets on an exchange creates exchange-credit and operational risk. If a lender keeps customer-related assets on a trading venue that later freezes or enters bankruptcy, those assets become claims against that venue rather than liquid reserves. BlockFi's exposure to FTX included assets stuck in the FTX bankruptcy process.

Proof of reserves by the lender would not automatically solve this if reserves are themselves claims on another insolvent platform. Market-health analysis needs to distinguish between self-custodied liquid assets, pledged collateral, exchange balances, and bankruptcy claims.

## 5. Bankruptcy and recovery

### 5.1 Customer claim treatment

In bankruptcy, different account types can receive different treatment. BlockFi wallet customers, interest-account customers, loan customers, and other creditors did not all occupy the same legal position. Interest-account terms were especially important because customers had lent assets to BlockFi rather than keeping them in a pure custody arrangement.

This distinction is central for users. A product called an "account" can create a property relationship very different from a wallet. Users need to know whether they own specific assets, hold a contractual claim, or have lent assets to the platform.

### 5.2 FTX and Alameda recoveries

BlockFi's recovery prospects depended heavily on claims against FTX and Alameda. In 2024, BlockFi reached a settlement framework with the FTX and Alameda estates reported at up to approximately $874.5 million, including claims related to assets on FTX and loans to Alameda. The exact economic effect for customers depended on bankruptcy approvals, claim treatment, and distribution mechanics.

The recovery process showed how interconnected bankruptcies can delay user outcomes. BlockFi customers were not only waiting for BlockFi's estate; they were indirectly waiting on FTX and Alameda's estates too. Crypto credit contagion therefore creates nested insolvencies.

### 5.3 Regulatory creditor position

The SEC was listed among BlockFi's creditors because part of the February 2022 settlement remained unpaid at bankruptcy. This created an unusual juxtaposition: a platform that had already settled a major crypto-lending registration action still failed months later due to market and counterparty exposure.

The lesson is not that regulation alone guarantees solvency. Registration, disclosure, and enforcement can reduce information asymmetry, but they do not replace conservative liquidity management, collateral discipline, or counterparty limits.

## 6. Market-health warning signals

### 6.1 High retail yield after regulatory action

When a yield platform faces major regulatory action, its ability to continue the same business model may be impaired. If the platform remains dependent on lending income while its product set is restricted, margins and liquidity can change quickly. A February regulatory settlement followed by a November bankruptcy is a reminder that compliance remediation and solvency remediation are different tasks.

### 6.2 Rescue financing from a correlated crypto firm

A rescue from a traditional bank, insurer, or well-capitalized external investor is different from a rescue by another crypto trading group exposed to the same market cycle. FTX's facility helped BlockFi survive immediate stress but made BlockFi's fate more dependent on FTX. Surveillance should mark correlated rescues as temporary stabilization, not proof of safety.

### 6.3 Exchange-token collateral

Loans collateralized by exchange tokens or affiliate-linked assets should be treated as high wrong-way risk. If the borrower or rescuer is connected to the token issuer, collateral value may collapse exactly when needed.

### 6.4 Withdrawal pauses by peer platforms

When similar platforms pause withdrawals, the risk to remaining platforms rises. Customers often compare Celsius, Voyager, BlockFi, and others as a sector. Stress at one platform can trigger withdrawals at another, forcing asset sales and revealing hidden exposures.

### 6.5 Unclear account ownership

If customers cannot easily tell whether they are using custody, lending, brokerage, or collateral accounts, the platform has a disclosure problem. Legal treatment in bankruptcy may not match customer intuition. Market-health monitoring should flag ambiguous account terminology, especially when yield is involved.

## 7. Comparison with other 2022 failures

### 7.1 Celsius

Celsius and BlockFi both offered yield products and both exposed retail users to institutional or strategy risk. Celsius had broader alleged governance and asset-deployment issues, while BlockFi's final collapse was more directly tied to FTX/Alameda after surviving the earlier 3AC wave. Both cases show that retail yield platforms can transform user deposits into unsecured credit exposure.

### 7.2 Voyager Digital

Voyager was more visibly impaired by a single 3AC loan default. BlockFi's path involved both 3AC stress and later FTX/Alameda dependency. Voyager's failed FTX sale and BlockFi's FTX credit facility are parallel examples of rescue-risk: a distressed platform can become tied to a rescuer that later fails.

### 7.3 FTX/Alameda

FTX and Alameda were the final shock for BlockFi. Their collapse impaired assets, credit expectations, and confidence. BlockFi demonstrates how FTX's failure propagated beyond exchange customers to firms that had treated FTX and Alameda as counterparties, lenders, borrowers, custodians, or rescuers.

### 7.4 Genesis

Genesis, like BlockFi, was part of the institutional crypto credit network. Both had exposure to 3AC and later stress connected to FTX-era market conditions. Genesis was more institutionally focused, while BlockFi was more retail-facing. The shared lesson is that opaque credit networks can transmit losses across firms with different user bases.

## 8. Lessons for platform design

### 8.1 Separate custody from lending

Platforms should make a hard distinction between assets held in custody and assets lent for yield. The distinction should not be buried in terms of service. Users should see it at deposit time, in account labels, and in risk disclosures.

### 8.2 Publish counterparty and collateral risk

If a platform's solvency depends on institutional borrowers, users need aggregate exposure data. This does not require publishing every trade in real time, but it does require meaningful concentration limits, collateral categories, loan-to-value ranges, and stress-test disclosures.

### 8.3 Treat rescue facilities as risk events

A rescue facility should trigger heightened monitoring. Analysts should ask: Who is the rescuer? What collateral or options did they receive? Is the rescuer exposed to the same assets? Does the facility create new custody or credit dependencies?

### 8.4 Avoid wrong-way collateral

Collateral policy should prohibit or heavily discount assets whose value depends on the borrower, affiliate, or rescuer. Exchange tokens are especially risky because they can collapse quickly when confidence in the issuing exchange fails.

### 8.5 Keep bankruptcy records customer-readable

If a platform has multiple account types, it should maintain records that let customers and courts distinguish wallet assets, interest-account assets, collateral, loans, and institutional claims. Good records do not prevent failure, but they reduce confusion and recovery delays.

## 9. Conclusion

BlockFi's collapse was not a simple story of one bad loan or one failed exchange. It was the result of a lending business model that exposed retail users to institutional credit risk, a regulatory settlement that highlighted disclosure problems, a market crash that damaged borrowers, a rescue facility that tied BlockFi more closely to FTX, and the final failure of FTX and Alameda.

The market-health lesson is that yield platforms are credit intermediaries even when they look like consumer apps. Their risk cannot be evaluated only by brand, app design, or headline interest rate. Users and counterparties need to know where assets go, who borrows them, what collateral backs them, where reserves are held, and what legal claim the user has if the platform fails.

For surveillance, the BlockFi pattern is clear: monitor high retail yields, regulatory settlements, emergency credit facilities, exposure to exchange-affiliated borrowers, exchange-token collateral, and account terms that transfer ownership to the platform. A platform can survive one contagion wave and still fail in the next if the rescue introduces a new single point of failure.
