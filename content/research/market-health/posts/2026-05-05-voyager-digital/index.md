---
date: 2026-05-05
entities:
  - id: voyager-digital
    name: Voyager Digital
    type: cefi
  - id: stephen-ehrlich
    name: Stephen Ehrlich
    type: person
  - id: three-arrows-capital
    name: Three Arrows Capital
    type: fund
  - id: cftc
    name: Commodity Futures Trading Commission
    type: regulatory
  - id: ftc
    name: Federal Trade Commission
    type: regulatory
title: "Voyager Digital yield-platform collapse and the unsecured 3AC credit failure"
---

## 1. Introduction and incident overview

Voyager Digital was a retail-facing crypto brokerage and yield platform that marketed easy access to digital assets, commission-free trading, and rewards on customer balances. In 2021 and early 2022, it presented itself as a safer and more regulated alternative to offshore crypto venues, emphasizing public-company status, security, and the ability for users to earn yield while holding assets on the platform.

That perception collapsed in June and July 2022. Voyager disclosed that Three Arrows Capital (3AC), one of its largest institutional borrowers, had failed to repay a loan of 15,250 BTC and 350 million USDC — worth roughly $650 million at the time. Voyager issued a notice of default, suspended trading, deposits, withdrawals, and loyalty rewards, and filed for Chapter 11 bankruptcy protection on 5 July 2022. The company later became entangled in failed asset-sale attempts to FTX and then Binance.US, while regulators accused Voyager and former CEO Stephen Ehrlich of misleading customers about the safety of their assets.

Voyager is a market-health case study because it sat between retail customers and opaque institutional credit. Customers saw a consumer app and account balances. Behind the app, Voyager was pooling customer assets and lending large amounts to high-risk counterparties to generate yield. The core failure was not a smart-contract exploit or an external wallet hack. It was a centralized credit, disclosure, and risk-management failure that transformed a hedge-fund default into retail customer losses.

## 2. Business model and trust assumptions

### 2.1 Brokerage interface

Voyager's user interface resembled a brokerage app. Customers could buy and sell crypto assets, track portfolio values, and earn rewards on selected holdings. Voyager routed trades through connected market makers and exchanges rather than operating as a conventional order-book exchange for all activity. For users, the product felt simple: deposit cash or crypto, trade in the app, and withdraw when needed.

This simplicity hid a complex custody and credit model. Customer assets were not merely sitting in segregated wallets waiting for withdrawals. To support yield programs and platform economics, Voyager transferred customer digital assets to third-party borrowers. That meant customers were exposed not only to Voyager's own operational controls but also to the solvency and trading behavior of institutional counterparties they could not see.

### 2.2 Yield generation

Voyager advertised rewards on certain crypto balances. Like other centralized crypto lenders, it needed a source of income to pay those rewards. One source was lending customer assets to counterparties that promised returns. This is economically similar to securities lending, prime brokerage, or bank-like maturity transformation, but Voyager's disclosures and controls did not give customers a clear bank-level or broker-dealer-level risk picture.

The CFTC later alleged that Voyager pooled customer assets and transferred billions of dollars' worth of digital asset commodities as loans to high-risk third parties. It also alleged that Voyager operated a commodity pool without required registration. Voyager and Ehrlich contested regulatory allegations in public statements, but the bankruptcy facts showed that customer recoveries depended heavily on the fate of large institutional loans.

### 2.3 Customer-safety messaging

Voyager publicly emphasized safety, trust, and rigor. The CFTC alleged that Voyager and Ehrlich represented the platform as a "safe haven" and said it operated with the "same level of rigor and trust" as a traditional financial institution. The FTC separately alleged that Voyager misled consumers about the safety and availability of deposits.

The market-health issue is the gap between user-facing safety language and balance-sheet reality. A platform can be public, app-based, and compliance-branded while still making concentrated unsecured loans. Customers evaluating such platforms need to know whether their assets are held in reserve, lent out, rehypothecated, or exposed to specific borrowers.

## 3. Exposure to Three Arrows Capital

### 3.1 Loan size and structure

Voyager's exposure to 3AC was the central trigger for its collapse. The loan consisted of 15,250 BTC and 350 million USDC. At June 2022 market prices, Voyager described the exposure as more than $650 million. The scale was enormous relative to Voyager's ability to absorb losses. It was also highly concentrated: one borrower represented a decisive share of the platform's credit risk.

The loan was widely described as unsecured or undercollateralized. That meant Voyager did not hold sufficient liquid collateral that could be sold quickly to recover the amount due if 3AC defaulted. In a volatile crypto market, unsecured credit to a hedge fund holding correlated crypto assets is especially dangerous because borrower solvency, collateral values, and market liquidity all deteriorate together.

### 3.2 3AC's market stress

3AC suffered severe losses during the 2022 market downturn, including exposure to Terra/LUNA, GBTC discount dynamics, stETH liquidity stress, and broad crypto price declines. As creditors demanded repayment or margin, the fund became unable to satisfy obligations. Voyager was one of the most visible victims because it had a large public-company disclosure trail and a retail customer base.

The 3AC default showed how private hedge-fund leverage can transmit to retail users through centralized lenders. Voyager customers did not lend directly to 3AC. They deposited with Voyager. Voyager's risk-management choices created the link.

### 3.3 Notice of default

In late June 2022, Voyager issued a notice of default to 3AC after the fund failed to repay the BTC and USDC loan. Voyager said it intended to pursue recovery from 3AC, but the default immediately created liquidity pressure. A platform that owes customers withdrawable balances cannot easily survive the sudden impairment of a major loan if it lacks enough liquid reserves.

This is the classic maturity-mismatch problem in a crypto wrapper. Customers expect app balances to be withdrawable on demand. The platform's assets include loans to distressed borrowers. When many customers try to withdraw and a major borrower defaults, the mismatch becomes visible.

## 4. Collapse timeline

### 4.1 June 2022: credit line and default

As market stress intensified, Voyager announced a credit facility with Alameda Research that included cash and USDC components and Bitcoin availability. The facility was presented as a liquidity backstop. Shortly afterward, Voyager disclosed 3AC's default. The sequence reflected the platform's deteriorating liquidity position: it needed external support while trying to recover a massive borrower exposure.

Alameda's role later became ironic because FTX and Alameda themselves collapsed in November 2022. In June, however, Alameda appeared to be a potential stabilizing counterparty for Voyager. The episode showed how interconnected the 2022 crypto credit system had become: the failure of one borrower pushed a lender toward support from another trading empire that would later fail.

### 4.2 Withdrawal and trading suspension

On 1 July 2022, Voyager suspended trading, deposits, withdrawals, and loyalty rewards. This was the point at which the user-interface promise broke. Customers who believed they held liquid crypto balances discovered that access depended on Voyager's solvency and restructuring process.

Withdrawal suspension is a critical market-health signal. It converts suspected credit impairment into confirmed customer harm. Even if a platform later resumes partial distributions, the suspension itself means customers no longer control assets they expected to be available.

### 4.3 Chapter 11 bankruptcy

Voyager filed for Chapter 11 bankruptcy protection on 5 July 2022 in the Southern District of New York. The filing sought to reorganize the company, preserve value, and create a process for customer recovery. Bankruptcy materials showed that Voyager had a large customer liability base and that recovery depended on asset sales, remaining crypto holdings, claims against 3AC, and market prices.

Chapter 11 placed customers into a legal claims process. Instead of withdrawing coins directly, users became creditors whose distributions depended on court-approved plans. That shift from wallet balance to bankruptcy claim is one of the most important practical risks of centralized crypto platforms.

### 4.4 Failed FTX sale

In September 2022, FTX US won an auction to acquire Voyager assets in a deal often described around $1.4 billion in headline value, depending on customer-asset values. The proposed sale was meant to provide a path for customers to regain access through FTX. In November 2022, FTX collapsed and filed for bankruptcy, eliminating that path and adding another layer of uncertainty.

The failed FTX sale demonstrated contagion inside contagion. Voyager failed partly because of 3AC. Its proposed rescue failed because FTX failed. Customers were exposed not only to Voyager's own credit decisions but also to the solvency of potential rescuers.

### 4.5 Binance.US sale attempt and wind-down

After the FTX deal failed, Voyager pursued a sale to Binance.US. That transaction faced regulatory objections and uncertainty. Binance.US eventually terminated the deal, citing the hostile and uncertain regulatory climate in the United States. Voyager then proceeded with a self-liquidation plan and distributions to creditors.

The sequence showed that bankruptcy recovery in crypto can depend on market structure and regulatory approvals as much as on remaining assets. A platform's customers can wait months while proposed rescue transactions fail for reasons outside their control.

## 5. Regulatory allegations

### 5.1 CFTC action

In October 2023, the CFTC filed a complaint against Stephen Ehrlich, former CEO of Voyager entities. The complaint charged fraud and registration failures connected to the Voyager platform and alleged operation of an unregistered commodity pool. The CFTC alleged that Voyager falsely touted itself as a safe haven, promised high-yield returns up to 12%, and transferred customer assets to high-risk third parties.

The CFTC also alleged that in early 2022 Voyager transferred more than $650 million in customer digital assets to a hedge fund on an unsecured basis after grossly inadequate due diligence. The agency said that when the borrower defaulted, Voyager experienced dire liquidity issues, while Ehrlich continued to publicly assert that customer assets were safe. These are allegations in ongoing litigation, but they map directly onto the market-health concerns revealed by the bankruptcy.

### 5.2 FTC action

The Federal Trade Commission separately charged Voyager and Ehrlich in October 2023. The FTC's public framing focused on alleged deceptive claims about the safety of consumer deposits and the availability of FDIC insurance. Voyager had marketed USD holdings in ways that many customers interpreted as bank-like protection. In reality, FDIC insurance did not protect customers from Voyager's failure, crypto-asset losses, or lending losses.

The FDIC issue is important because consumer apps often borrow trust language from regulated finance. A customer may see "USD," "safe," "insured," or bank-partner references and infer that the full account relationship is protected. In crypto platforms, those inferences can be wrong. Market-health monitoring should treat ambiguous insurance claims as high-risk when platform assets are being lent or rehypothecated.

### 5.3 Disclosure gap

Regulatory actions emphasized a central disclosure gap: customers were not given a clear, real-time picture of how their assets were used, which counterparties borrowed them, what collateral existed, and what would happen in bankruptcy. Even sophisticated users could not easily infer that a massive 3AC default would freeze the platform.

This gap is not solved by saying users should read terms of service. If a platform markets itself as safe and simple while operating a credit fund behind the scenes, market-health disclosures need to be prominent, specific, and quantitative.

## 6. Mechanics of customer harm

### 6.1 Account balance versus property right

Before the collapse, Voyager users saw account balances denominated in crypto and dollars. After bankruptcy, those balances became claims subject to legal treatment. The difference matters. A displayed BTC balance is not equivalent to a self-custodied BTC UTXO. It is a claim against a platform whose assets may include loans, claims against bankrupt borrowers, and illiquid recoveries.

This transformation is a recurring CeFi failure mode. Customers think in wallet terms; bankruptcy courts think in estate, claims, and distribution terms.

### 6.2 Yield as hidden credit risk

Yield is never free. If a platform pays rewards on customer assets, it must generate revenue through lending, staking, market making, fees, or subsidies. Voyager's rewards exposed customers to borrower risk. The advertised yield did not come with an equally prominent disclosure that a single hedge-fund default could impair access to assets.

For market surveillance, high advertised yield should trigger the question: who is paying it, with what collateral, and under what stress scenario?

### 6.3 Liquidity mismatch

Voyager offered a liquid user experience while holding assets that were not equally liquid. Loans to 3AC could not be instantly recalled once 3AC was distressed. Customer withdrawals, by contrast, could arrive immediately. This mismatch is manageable only with conservative liquidity reserves, diversified borrowers, strong collateral, and stress tests. Voyager's exposure failed that test.

### 6.4 Counterparty opacity

Retail customers generally did not know the size and terms of Voyager's loans to specific counterparties before the crisis. Without that information, they could not price the risk of keeping assets on the platform. Counterparty opacity is especially dangerous in crypto because the same names can appear across many lenders. A fund like 3AC could be a borrower from multiple platforms, creating system-wide fragility invisible to any one retail user.

## 7. Market-health warning signals

### 7.1 Large single-borrower exposure

The clearest warning signal was borrower concentration. A retail-facing platform should not be existentially dependent on repayment from one hedge fund. Any disclosure showing a large percentage of assets lent to one borrower should trigger severe risk marking, especially if the loan is unsecured.

### 7.2 Vague "safe haven" language

Safety claims should be tested against actual asset use. If a platform says assets are safe while lending them to high-risk trading firms, the claim is at best incomplete. Market-health systems should flag generic safety language that is not accompanied by reserve, collateral, and counterparty detail.

### 7.3 Yield above transparent sources

When advertised yield exceeds what can be explained by transparent staking rewards or fee revenue, the missing source is often credit risk. The higher the yield, the more important it is to identify borrowers, collateral, duration, and loss waterfall.

### 7.4 Emergency credit facilities

An emergency credit facility can stabilize a platform, but it can also reveal stress. Voyager's Alameda facility indicated liquidity pressure before the bankruptcy filing. Surveillance should distinguish between ordinary treasury management and rescue financing announced during market turmoil.

### 7.5 Withdrawal suspension

Withdrawal suspension is not a warning signal; it is the failure event. The market-health goal is to detect the preceding signals early enough for users and counterparties to reduce exposure. Once withdrawals stop, customers are already in a loss-allocation process.

## 8. Comparison with related failures

### 8.1 Three Arrows Capital

3AC was the borrower whose default triggered Voyager's collapse. The fund represented hidden leverage and illiquid collateral. Voyager represented the retail-facing lender that transmitted that fund failure to app users. Together, they show both sides of centralized crypto credit contagion.

### 8.2 Celsius

Celsius and Voyager both offered yield products and suspended withdrawals in 2022. Celsius had a broader set of asset-deployment and governance issues, while Voyager's collapse was especially tied to one large 3AC exposure. The common lesson is that retail yield platforms need bank-like transparency if they are going to take bank-like maturity and credit risk.

### 8.3 BlockFi

BlockFi also had 3AC-related losses and later depended on support from FTX before filing for bankruptcy after FTX collapsed. Voyager and BlockFi illustrate how attempted rescues can create new dependencies. A platform that survives one credit event by relying on another fragile crypto institution may still fail when the rescuer fails.

### 8.4 FTX

FTX appears twice in Voyager's story: first as a proposed buyer, then as another bankrupt estate. FTX's collapse prevented the sale path that Voyager customers had expected. The connection shows how concentrated the 2022 crypto market was around a few large firms. A failure at one node could repeatedly disrupt recovery efforts elsewhere.

## 9. Lessons for platform design

### 9.1 Segregate customer assets or disclose lending clearly

If customer assets are lent, users should know that they are taking credit risk. If a platform wants to market custody-like safety, it should maintain custody-like reserves and segregation. Mixing the two creates false expectations.

### 9.2 Limit counterparty concentration

No retail platform should be able to lose solvency because one borrower defaults. Exposure limits, collateral requirements, and borrower diversification are basic controls. In crypto, these controls need to account for correlated market crashes, not just normal volatility.

### 9.3 Make yield sources auditable

Users and regulators should be able to trace yield to specific sources: staking rewards, trading fees, secured lending, unsecured lending, or promotional subsidies. If yield sources are opaque, users cannot evaluate whether they are being compensated for the risk.

### 9.4 Match liquidity promises to asset liquidity

Platforms should not offer demand withdrawals against assets deployed into illiquid or callable-only-under-good-conditions loans unless they maintain enough liquid reserves for stress scenarios. Liquidity terms should match asset duration.

### 9.5 Avoid misleading insurance language

References to bank partners, FDIC insurance, or "safe" cash management must be narrow and precise. Customers need to understand exactly what is insured, by whom, under what failure scenario, and what is not protected.

## 10. Conclusion

Voyager Digital's collapse was one of the clearest examples of retail crypto users being exposed to institutional credit risk they could not see. The app interface looked like a brokerage. The yield program looked like a passive reward. The risk engine behind it included a massive loan to Three Arrows Capital. When 3AC defaulted, Voyager's liquidity failed, withdrawals stopped, and users became creditors in bankruptcy.

The incident remains relevant because centralized crypto platforms still compete on simplicity, yield, and trust branding. Those features can be valuable, but only if matched by transparent asset use, conservative counterparty limits, and honest disclosure. Voyager showed that a platform can appear consumer-friendly while functioning economically like an under-disclosed credit fund.

For market-health monitoring, the Voyager pattern is clear: flag high retail yields, vague safety language, large undisclosed borrowers, emergency credit lines, and any mismatch between instant-withdrawal promises and illiquid lending. Crypto investors can choose to take credit risk, but they cannot price a risk that the platform hides behind an app balance.
