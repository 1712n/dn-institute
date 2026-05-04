---
date: 2026-05-05
entities:
  - id: three-arrows-capital
    name: Three Arrows Capital
    type: fund
  - id: su-zhu
    name: Su Zhu
    type: person
  - id: kyle-davies
    name: Kyle Davies
    type: person
  - id: teneo
    name: Teneo
    type: trustee
  - id: terra
    name: Terra
    type: protocol
title: "Three Arrows Capital leverage collapse and the 2022 crypto credit contagion"
---

## 1. Introduction and incident overview

Three Arrows Capital (3AC) was one of the most prominent crypto hedge funds of the 2020-2021 bull market. Founded by Su Zhu and Kyle Davies, the fund became known for large directional bets, close relationships with crypto lenders and trading desks, and an aggressively bullish public posture on Bitcoin, Ether, Layer 1 tokens, and structured crypto products. By mid-2022, that reputation had reversed. 3AC failed to meet margin calls, a British Virgin Islands court ordered liquidation, and liquidators began trying to locate assets and records across jurisdictions.

The collapse was not a single smart-contract exploit. It was a leverage, liquidity, and counterparty-risk failure that propagated through centralized crypto credit markets. 3AC had exposures to the Terra/LUNA ecosystem, Grayscale Bitcoin Trust (GBTC), staked Ether (stETH), directional token positions, and loans from major crypto lenders. When market prices fell and liquidity thinned, the fund could not satisfy creditor demands. Its failure helped transmit stress to Voyager Digital, Genesis, BlockFi, Blockchain.com, Deribit, and other counterparties, contributing to the broader 2022 crypto credit crisis.

For market-health analysis, 3AC is important because it showed how crypto leverage can hide outside the protocol layer. On-chain positions may be visible, but bilateral loans, over-the-counter derivatives, exchange margin, token side letters, and fund-level liabilities can remain opaque until defaults begin. A market can appear decentralized at the asset layer while still depending on a small number of highly levered centralized funds and lenders.

## 2. Background: from macro fund to crypto credit hub

### 2.1 Fund profile

Three Arrows Capital began as a trading firm with roots in traditional foreign-exchange and macro markets before becoming deeply associated with crypto. During the bull market, it grew into a large borrower, investor, and liquidity taker across digital-asset venues. The fund's founders were influential on social media and in private deal networks, which helped 3AC obtain access to lending relationships and token allocations.

3AC's strategy was not one narrow trade. It combined:

1. **Directional crypto exposure**: large long positions in Bitcoin, Ether, and alternative Layer 1 tokens.

2. **Structured product exposure**: investments in vehicles such as GBTC whose shares could trade at a premium or discount to underlying Bitcoin.

3. **DeFi and liquid-staking exposure**: positions involving stETH and other yield-bearing or derivative assets.

4. **Venture and token investments**: allocations to private token rounds and early-stage crypto projects.

5. **Borrowed capital**: loans from centralized crypto lenders and trading counterparties.

This mix made the fund highly sensitive to a broad market drawdown. If prices fell, collateral values declined; if liquidity disappeared, positions could not be exited without large slippage; if lenders demanded repayment at the same time, the fund needed cash precisely when its assets were hardest to monetize.

### 2.2 The crypto lending environment

During 2020 and 2021, centralized crypto lending grew quickly. Lenders offered yield to depositors and made loans to market makers, funds, miners, and trading firms. Some lending was overcollateralized and margin-monitored. Other lending depended heavily on reputation, relationship history, or limited disclosure. Large borrowers could receive credit because they were perceived as sophisticated, profitable, and systemically important.

This environment created hidden concentration risk. Multiple lenders could believe their exposure to 3AC was manageable without seeing the fund's total liabilities to everyone else. Each lender might know its own collateral package and loan terms, but not the full creditor stack. When the same borrower pledges correlated assets to many counterparties, the system is more levered than any one lender's bilateral view implies.

### 2.3 Reflexive confidence

3AC benefited from reflexive confidence. Its visible success attracted deal flow; deal flow improved perceived access; perceived access supported credit; credit allowed larger positions; larger positions reinforced market influence during rising prices. This loop worked while collateral values rose. In a downturn, the loop reversed. Creditors became less willing to roll loans, market participants questioned the fund's solvency, and illiquid positions became harder to finance.

The market-health lesson is that reputation is not collateral. A fund's public confidence, founder access, or prior returns cannot substitute for verified asset, liability, and liquidity information.

## 3. Major risk exposures

### 3.1 Terra/LUNA and UST

The May 2022 Terra collapse destroyed tens of billions of dollars of market value across UST and LUNA. 3AC had meaningful exposure to the Terra ecosystem, and reporting after the collapse indicated that the fund suffered large losses when LUNA hyperinflated and UST failed to maintain its dollar peg.

Terra mattered for 3AC beyond the direct loss amount. It damaged the fund's balance sheet at the same time that confidence in crypto credit was weakening. It also reduced lenders' willingness to accept optimistic valuations of other illiquid assets. A fund can sometimes survive one large loss if it can raise liquidity or maintain creditor confidence. Terra made both more difficult.

### 3.2 GBTC premium-to-discount reversal

The Grayscale Bitcoin Trust trade was one of the defining structured trades of the prior cycle. For years, GBTC shares often traded at a premium to the value of underlying Bitcoin. Accredited investors could create shares through private placements, wait through a lock-up period, and sell into the public market. When the premium was large, the trade looked attractive.

As competition from other Bitcoin products increased and market conditions changed, GBTC moved from a premium to a persistent discount. That harmed investors who had treated the premium as a repeatable yield source. For levered holders, the discount created a double problem: Bitcoin's price fell, and the vehicle traded below net asset value. If financed with borrowed money, the position became difficult to use as liquidity without realizing losses.

3AC was associated with large GBTC exposure. The trade's reversal showed how a market-structure arbitrage can become a balance-sheet trap when the exit depends on secondary-market demand and regulatory expectations that do not materialize on schedule.

### 3.3 stETH and liquidity mismatch

Staked Ether derivative tokens such as Lido's stETH represent claims related to staked ETH. Before Ethereum withdrawals were enabled, stETH was not directly redeemable for ETH at par on demand. Its market price depended on liquidity pools, arbitrage expectations, and confidence in eventual redemption. During 2022 stress, stETH traded at a discount to ETH as holders sought liquidity.

The stETH discount was not itself a protocol insolvency event, but it created mark-to-market and collateral stress for levered holders. If a borrower used stETH as collateral or held it as a liquidity reserve, a discount during market stress meant the asset was less useful exactly when liquidity was needed. 3AC was linked to stETH selling and related liquidity pressure during the crisis.

This is a general market-health lesson: liquid-staking tokens and other derivative claims can be economically sound over long horizons but still create short-term liquidity risk if they are financed with demand liabilities.

### 3.4 Venture and locked-token exposure

Crypto funds often hold private-round tokens, equity stakes, or locked allocations that may not be immediately liquid. These positions can be valuable in a bull market but are difficult to sell during a crisis. Marking them at recent round prices can overstate near-term solvency if creditors demand cash.

3AC's portfolio included venture-style assets and token allocations. In a liquidation, such assets are harder to value and recover than exchange-traded coins. Creditors need realizable value, not theoretical marks. The mismatch between reported portfolio value and cash liquidity can be fatal when margin calls accelerate.

## 4. Collapse timeline

### 4.1 May 2022: Terra breaks the credit cycle

The Terra ecosystem collapsed in May 2022. UST lost its peg, LUNA supply expanded rapidly, and crypto markets repriced risk across stablecoins, DeFi, and levered funds. 3AC's Terra exposure became a visible concern. At the same time, Bitcoin and Ether prices remained under pressure, and lenders began reassessing counterparty risk.

The key transition was from price loss to credit loss. Market participants can absorb volatile asset prices if financing remains available. Once creditors doubt a borrower's solvency, they demand margin, reduce credit lines, or liquidate collateral. That transforms market volatility into a liquidity crisis.

### 4.2 June 2022: margin calls and default notices

In June 2022, reports emerged that 3AC had failed to meet margin calls from counterparties. Several venues liquidated or moved to liquidate positions. Voyager Digital disclosed large exposure to 3AC and issued a notice of default after the fund failed to repay loans. Other firms later disclosed losses or impairments connected to 3AC.

The situation revealed how concentrated crypto credit had become. A single fund's failure could affect lenders with retail deposit programs, institutional trading venues, and other funds. Because many exposures were private, the market learned about them in fragments: a default notice here, a trading-desk loss there, a withdrawal freeze somewhere else.

### 4.3 BVI liquidation and Chapter 15 filing

In late June 2022, a British Virgin Islands court ordered the liquidation of Three Arrows Capital, and Teneo was appointed to manage the process. The fund also entered Chapter 15 proceedings in the United States to recognize and support the foreign liquidation. Liquidators sought records, asset access, and cooperation from the founders.

The liquidation process was complicated by jurisdictional spread, incomplete records, and disputes over founder cooperation. Liquidators later pursued subpoenas and asset-recovery efforts around the world. The process underscored that crypto funds can operate globally while leaving creditors dependent on slow, multi-jurisdictional insolvency tools when something goes wrong.

### 4.4 Contagion through lenders and counterparties

3AC's default contributed to a cascade across centralized crypto finance:

1. **Voyager Digital**: disclosed exposure to 3AC and later filed for bankruptcy.

2. **BlockFi**: suffered losses and liquidity stress, later receiving emergency support before ultimately filing for bankruptcy after the FTX collapse.

3. **Genesis**: had large exposure to 3AC and later became central to the post-FTX credit crisis.

4. **Blockchain.com and other counterparties**: disclosed or were reported to have exposure or claims.

5. **Deribit and trading venues**: pursued claims and collateral recovery related to 3AC obligations.

Not every later failure was caused solely by 3AC. The 2022 market included Terra, Celsius, FTX, falling asset prices, and broader liquidity contraction. But 3AC was one of the major transmission nodes between asset-price losses and centralized-credit losses.

## 5. Mechanics of the failure

### 5.1 Leverage on correlated collateral

Leverage is most dangerous when collateral is correlated with the borrower's strategy. A crypto fund borrowing against crypto assets to buy more crypto is exposed to a common shock: when the market falls, both collateral value and portfolio value fall together. Lenders may call margin at the same time that asset sales push prices lower.

3AC appears to have been exposed to this dynamic across several assets. Terra, GBTC, stETH, Bitcoin, Ether, and venture tokens were not independent safe havens. In a crypto-wide deleveraging, they all became harder to finance.

### 5.2 Illiquidity disguised as wealth

Bull markets can make illiquid positions look like cash. Locked tokens, private investments, and thinly traded derivatives can be marked at high prices, creating apparent net worth. But if creditors demand repayment in stablecoins, fiat, BTC, or ETH, illiquid assets cannot necessarily be sold quickly.

The distinction between mark-to-market value and liquidation value became central in 3AC's collapse. A portfolio can be large on paper and still unable to meet immediate liabilities. Market-health systems should therefore track liquidity-adjusted assets, not only nominal exposure.

### 5.3 Cross-creditor blind spots

Each creditor may have seen 3AC as a high-quality borrower. The systemic problem was that creditors could not easily see one another. Without a shared view of total fund leverage, every bilateral loan underestimated the borrower's aggregate stress.

Traditional prime brokerage can mitigate this through centralized margining, reporting, and capital rules. Crypto credit in 2021-2022 often lacked comparable transparency. That allowed leverage to build in overlapping private relationships.

### 5.4 Social signaling and delayed repricing

Crypto markets are unusually influenced by public narratives and founder signaling. 3AC's founders were prominent voices, and bullish public commentary may have delayed some counterparties' risk repricing. When confidence finally shifted, it shifted abruptly.

This does not mean public optimism caused the collapse. It means that social credibility can become part of a credit model without being explicitly acknowledged. Lenders may treat reputation as evidence of solvency until hard withdrawal or margin data contradicts it.

## 6. Legal and recovery process

### 6.1 Liquidator mandate

Teneo's mandate as liquidator involved identifying assets, preserving value, communicating with creditors, and pursuing recovery through courts where necessary. In crypto, that includes tracing wallets, identifying exchange accounts, reviewing token allocations, and seeking cooperation from counterparties.

The process is difficult because crypto assets can move quickly, while legal authority moves slowly. Liquidators may know that assets passed through certain wallets or venues but still need subpoenas, recognition orders, and cooperation to recover them. If records are incomplete, even identifying the estate's property can be contested.

### 6.2 Founder cooperation disputes

Liquidators and courts repeatedly addressed the question of founder cooperation. Public reports and court filings described difficulty obtaining information from Su Zhu and Kyle Davies during parts of the process. The founders later disputed elements of the liquidators' characterization and gave their own explanations of the collapse.

For market-health purposes, the key issue is not only personal blame. It is operational dependency. A fund with billions in claims should have records and governance that allow liquidation without relying primarily on founders' voluntary memory, devices, or social-media statements.

### 6.3 Creditor claims

Creditor claims were reported in the billions of dollars, with major claims from crypto lenders and trading firms. Genesis Asia Pacific was reported to have one of the largest claims. Voyager's exposure was especially important because Voyager served retail customers and later entered bankruptcy, demonstrating how a hedge-fund default could affect retail depositors indirectly through lending intermediaries.

Claims figures in large insolvencies can change as valuation dates, collateral offsets, and legal disputes evolve. The stable conclusion is that 3AC was a multi-billion-dollar credit event for the crypto market, not a contained fund loss.

## 7. Market-health warning signals

### 7.1 Borrower concentration across lenders

The most important signal was concentration. If many lenders depend on the same borrower, the system is fragile even if each lender believes its own loan is well managed. Market-health monitoring should track repeated appearances of the same funds across lender disclosures, court filings, on-chain credit venues, and OTC market rumors.

### 7.2 Large illiquid positions financed by short-term credit

Illiquid or locked assets can be legitimate investments, but they should not be financed primarily by short-term callable debt. Warning signs include funds borrowing against GBTC-like structured products, locked tokens, or liquid-staking derivatives while promising lenders quick repayment.

### 7.3 Public confidence inconsistent with market behavior

A gap between confident public messaging and deteriorating withdrawal, margin, or collateral signals should be treated as a risk marker. Markets should not rely on founder social presence as a solvency signal. In stressed conditions, verifiable collateral and liability data matter more than narrative.

### 7.4 stETH and derivative-token liquidity stress

Derivative tokens can introduce liquidity risk without protocol failure. A widening discount between stETH and ETH did not mean stETH was worthless, but it did mean immediate liquidity was expensive. Similar discounts in liquid-staking, bridge, wrapped, or yield-bearing assets can indicate deleveraging pressure.

### 7.5 Contagion disclosures

After a major borrower defaults, the next signal is which lenders disclose exposure. If disclosures are slow, incomplete, or forced by bankruptcy filings, market confidence deteriorates. Healthy lenders should be able to quantify exposure, collateral status, and expected losses quickly.

## 8. Comparison with other 2022 failures

### 8.1 Terra as asset-level collapse

Terra was primarily an asset and mechanism failure: UST's peg broke, LUNA hyperinflated, and the stabilization design failed under a run. 3AC was different. Terra was one of the shocks that damaged 3AC, but 3AC's collapse was a balance-sheet and credit-network failure. It translated asset losses into lender losses.

### 8.2 Celsius as maturity mismatch

Celsius promised retail users yield and liquidity while deploying assets into loans, DeFi, and other strategies. 3AC was not a retail lender, but it was connected to the same credit system. Celsius represented depositor-to-lender maturity mismatch; 3AC represented borrower leverage and fund-level opacity. Together, they showed both sides of the same fragile market.

### 8.3 FTX/Alameda as exchange-affiliate commingling

FTX and Alameda involved exchange customer assets, affiliate privileges, and internal controls at a much larger public scale. 3AC did not operate a major retail exchange. Its risk came from borrowing and investment leverage. Both cases, however, demonstrate that off-chain liabilities can overwhelm on-chain transparency. Users and counterparties need balance-sheet visibility, not just wallet monitoring.

### 8.4 QuadrigaCX as founder-control fraud

QuadrigaCX was a founder-control and custody-fraud case. 3AC was a fund leverage case. The overlap is operational opacity: creditors and customers could not independently assess real assets, liabilities, or controls until after failure. Both incidents argue for records that survive founder absence and for independent verification of balances.

## 9. Lessons for crypto credit markets

### 9.1 Relationship lending needs hard limits

Crypto lenders should not extend large unsecured or undercollateralized credit based primarily on founder reputation, prior profitability, or market influence. Relationship lending can exist, but it needs exposure caps, collateral haircuts, audit rights, and real-time risk monitoring.

### 9.2 Collateral should be stress-tested for liquidity

Collateral value should be discounted for liquidity, lock-ups, and correlation with the borrower. GBTC at a discount, stETH under stress, and locked venture tokens are not equivalent to cash or short-duration Treasury collateral. Haircuts should widen automatically when market depth deteriorates.

### 9.3 Liabilities should be mapped across counterparties

No single lender can fully solve cross-creditor opacity alone, but markets can improve through shared credit registries, attestations, prime-brokerage structures, or audited borrower reporting. The goal is to prevent every lender from believing it is senior, well-collateralized, or uniquely protected when aggregate leverage says otherwise.

### 9.4 Fund records should be liquidation-ready

Investment funds that borrow at scale should maintain records that liquidators and creditors can use if the fund fails. Wallet inventories, exchange accounts, side letters, token vesting schedules, OTC confirmations, and collateral agreements should not depend on founders' voluntary cooperation after a crisis.

### 9.5 Contagion planning matters

Lenders should model not only direct borrower default but also simultaneous default by correlated borrowers and asset-price shocks. 3AC's default occurred in a market already damaged by Terra and broader deleveraging. Stress tests that assume isolated defaults are too optimistic for crypto.

## 10. Conclusion

Three Arrows Capital was a defining failure of the 2022 crypto credit cycle. It did not collapse because of one exploitable smart contract or one hacked private key. It collapsed because large, correlated, partly illiquid exposures were financed through opaque credit relationships that depended heavily on confidence. When Terra failed, GBTC traded at a discount, stETH liquidity weakened, and lenders demanded repayment, the balance sheet could not withstand the pressure.

The incident's broader significance lies in contagion. 3AC connected hedge-fund losses to lenders, retail-facing platforms, trading venues, and bankruptcy estates. It showed that crypto market health cannot be measured only by protocol code or visible exchange prices. Hidden leverage, private credit, collateral quality, and borrower concentration can be just as important.

For future surveillance, the 3AC pattern is clear: monitor concentrated borrowers, derivative-token discounts, large illiquid positions financed with short-term debt, inconsistent counterparty disclosures, and credit exposure to funds whose public confidence is not matched by verifiable balance-sheet data. Crypto markets can recover from price volatility; they struggle when nobody knows who owes what to whom until after the defaults begin.
