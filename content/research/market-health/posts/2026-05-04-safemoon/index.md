---
title: "🌰 SafeMoon — Insider Liquidity Drain and Token Price Manipulation in an $8B Market Cap Scheme"
date: 2026-05-04
entities:
  - SafeMoon
  - SFM
  - Braden John Karony
  - Kyle Nagy
  - Thomas Smith
  - PancakeSwap
  - BNB Chain
---

## Summary

1. **SafeMoon was a BNB Chain token** launched in March 2021 that reached a peak market capitalization of approximately $8 billion by April 2021, driven by social-media marketing and a tokenomics model that imposed a 10% tax on every transaction (5% redistributed to holders, 5% added to the liquidity pool).
2. **The SEC and DOJ charged SafeMoon's leadership** in November 2023. The SEC filed civil securities-fraud charges against SafeMoon LLC, SafeMoon US LLC, founder Kyle Nagy, CEO Braden John Karony, and CTO Thomas Smith, while the DOJ brought criminal securities-fraud, wire-fraud, and money-laundering conspiracy charges against Nagy, Karony, and Smith.
3. **Liquidity pool manipulation** was the primary fraud vector: SafeMoon's creators maintained undisclosed control over the project's PancakeSwap liquidity pools and systematically drained BNB from them while publicly claiming the funds were locked and inaccessible.
4. **Wash trading signals** were present in SafeMoon's on-chain trading data: abnormally uniform transaction sizes during high-volume periods, repetitive buy patterns from wallets linked to the development team, and volume spikes that coincided with promotional campaigns rather than organic demand.
5. **SafeMoon collapsed in stages**: the token lost 95% of its value from its April 2021 peak to early 2022, then suffered a final liquidity pool exploit in March 2023 that drained $8.9 million. SafeMoon US LLC filed for Chapter 7 bankruptcy in December 2023.

## Background

SafeMoon launched on March 8, 2021, on the Binance Smart Chain (now BNB Chain) as a "DeFi token" with an innovative tokenomics model. The project's central selling point was the 10% transaction tax:

- **5% reflection**: Redistributed proportionally to all existing token holders, incentivizing holding over selling
- **5% liquidity pool contribution**: Automatically added to the SafeMoon/BNB liquidity pool on PancakeSwap, supposedly ensuring permanent and growing liquidity

This mechanism was marketed as "anti-whale" and "deflationary," creating an economic model where selling was penalized and holding was rewarded. In reality, the 10% tax served primarily to:

1. **Discourage selling** by imposing a steep exit cost, trapping investors while insiders extracted value
2. **Generate a continuous flow of BNB** into liquidity pools that the team secretly controlled
3. **Create artificial price support** through the automatic liquidity addition, masking the underlying lack of organic demand

The token was initially launched with a supply of 1 quadrillion tokens (later migrated to SafeMoon V2 with a 1000:1 consolidation in December 2021).

## 🌰 Token Price Manipulation Mechanics

### Controlled Liquidity Pool Drain

The core of SafeMoon's manipulation was a discrepancy between what the team publicly claimed about liquidity and what they actually did with it.

**Public claim**: The 5% liquidity tax was permanently locked in the PancakeSwap liquidity pool, providing irreversible price support.

**Reality (per SEC complaint, Case 1:23-cv-08138)**: The team retained administrative access to the liquidity pool smart contracts through:

- **Owner-controlled `swapAndLiquify` function**: The SafeMoon contract's liquidity mechanism could be manually triggered by the contract owner, allowing selective timing of when BNB was added to or removed from the pool
- **Unlocked LP tokens**: Contrary to public statements, the liquidity provider tokens that control the SafeMoon/BNB pair were not locked in a time-locked contract. The team held the LP tokens in wallets they controlled.
- **Systematic BNB extraction**: Between 2021 and 2022, the team used these LP tokens to remove BNB from the liquidity pool in amounts that would not immediately crash the token price. Federal prosecutors documented multiple large withdrawals converted to personal use.

### Price-Volume Analysis During Key Periods

| Period | SFM Price | Market Cap | Daily Volume | Key Event |
|--------|----------|------------|-------------|-----------|
| Mar 2021 (launch) | $0.00000001 | <$1M | Minimal | Token deployed on BSC |
| Apr 12, 2021 | $0.00001399 (ATH) | ~$8B | $400M+ | Peak FOMO, Tiktok/Twitter campaigns |
| May 2021 | $0.000004 | ~$2.5B | $50-100M | First major correction; whale sells |
| Sep 2021 | $0.0000015 | ~$900M | $10-20M | Volume declining; reflections shrinking |
| Dec 2021 | V2 migration | ~$500M | N/A | 1000:1 consolidation to SFM V2 |
| Jan 2022 | $0.002 (V2) | ~$1.2B | $5-15M | Brief recovery post-migration |
| Jun 2022 | $0.0004 | ~$250M | $2-5M | Steady bleed; team still extracting |
| Mar 28, 2023 | $0.0002 → $0.00002 | <$20M | Exploited | LP exploit drains $8.9M in BNB |
| Nov 2023 | $0.00003 | <$10M | Minimal | SEC/DOJ charges filed |

The price trajectory reveals a classic pump-and-dump pattern:
- **Pump phase (March-April 2021)**: Aggressive social media marketing on TikTok, Twitter, and YouTube drove retail FOMO. The 10% tax created an artificial sense of scarcity while the auto-liquidity mechanism provided apparent price support.
- **Controlled dump (May 2021-March 2023)**: The team extracted value through LP drains while the token price gradually declined. The 10% tax on selling slowed the decline by penalizing retail exit, extending the extraction window.

### 🌰 Insider Wallet Analysis

The SEC's complaint identified several wallet patterns consistent with insider manipulation:

1. **Development wallet accumulation**: Wallets associated with the SafeMoon team received large token allocations at launch that were not disclosed in the token's purported "fair launch" marketing
2. **Coordinated buy-sell patterns**: On-chain analysis showed clusters of wallets executing identical-sized purchases during promotional periods, followed by sells through separate wallets to avoid triggering the reflection mechanism's whale detection
3. **Cross-chain fund movement**: Extracted BNB was bridged to Ethereum and other chains, then converted to stablecoins or fiat through centralized exchanges, making the fund trail more difficult to trace

## Wash Trading Evidence

### On-Chain Transaction Patterns

Analysis of SafeMoon's BNB Chain transaction data reveals several wash trading indicators:

**Transaction size clustering**: During high-volume promotional periods (particularly April 2021), a significant proportion of trades clustered around identical BNB amounts (0.1, 0.5, 1.0, 5.0 BNB), which is inconsistent with organic retail trading where trade sizes follow a power-law distribution.

**Time-of-trade regularity**: Blocks containing SafeMoon transactions showed periodic clustering inconsistent with human trading behavior. Groups of 3-5 transactions appeared at regular intervals during promotional campaigns, suggesting automated buy pressure generation.

**Reflection mechanism gaming**: The 5% reflection tax was designed to reward holders, but sophisticated actors could exploit it by:
- Creating many small wallets that accumulated reflections
- Executing wash trades between controlled wallets (paying the 10% tax but recovering a portion through reflections across the wallet network)
- The net cost of wash trading was reduced below the nominal 10% tax, making artificial volume generation economically viable for insiders who controlled enough wallets

### Volume Anomalies

SafeMoon's peak daily volume of over $400 million in April 2021 was highly anomalous for a token with:
- No underlying product or utility
- No significant exchange listings (traded primarily on PancakeSwap DEX)
- A 10% transaction tax that should suppress volume

The volume-to-market-cap ratio during peak periods exceeded 0.05 (5% daily turnover), which is abnormally high for a buy-and-hold token with a 10% sell penalty. For comparison, established large-cap tokens with no transaction tax typically show volume-to-market-cap ratios of 0.01-0.03 (1-3%).

## Social Media Manipulation

### Coordinated Promotional Campaigns

SafeMoon's price movements were tightly correlated with social media activity rather than fundamental developments:

- **#SAFEMOON** was one of the most-trending crypto hashtags on Twitter during March-April 2021
- The project employed a network of paid promoters and influencers across TikTok, YouTube, and Twitter who created coordinated content around specific price milestones
- "SafeMoon Army" became a self-reinforcing community where members were incentivized (through reflections) to recruit new buyers, creating pyramid-like dynamics
- The team organized "buy events" — coordinated mass-purchase campaigns at specific times — which artificially inflated transaction volume and price

### Information Asymmetry

While promoting the token publicly, the team withheld critical information:

1. **Liquidity lock status**: Publicly claimed as locked; actually accessible to the team
2. **Team wallet holdings**: Undisclosed insider allocations contradicted "fair launch" claims
3. **Development progress**: Promised products (SafeMoon Wallet, SafeMoon Exchange, SafeMoon Blockchain) were either significantly delayed, launched with critical vulnerabilities, or never materialized
4. **Token burns**: Announced token burns that were later found to be transfers to team-controlled wallets rather than actual burns to the dead address

## Regulatory and Legal Outcomes

### SEC Enforcement

- **November 1, 2023**: The SEC filed a complaint against SafeMoon LLC, SafeMoon US LLC, and executives Kyle Nagy, Braden John Karony, and Thomas Smith (Case 1:23-cv-08138, E.D.N.Y.) charging violations of Sections 5(a), 5(c), and 17(a) of the Securities Act, plus Sections 9(a)(2), 10(b), and 20(a) of the Exchange Act and Rule 10b-5
- The SEC alleged SafeMoon was an unregistered security and that executives engaged in fraud by misappropriating investor funds and making material misrepresentations

### DOJ Criminal Charges

- **November 1, 2023**: DOJ announced criminal charges against Karony, Smith, and Nagy
- **Karony**: Charged with securities fraud conspiracy, wire fraud conspiracy, and money laundering conspiracy. The indictment alleged he used misappropriated funds to purchase a custom Porsche, real estate in New Hampshire, and other luxury items
- **Smith**: Charged with securities fraud conspiracy, wire fraud conspiracy, and money laundering conspiracy
- **Nagy**: Charged with securities fraud conspiracy, wire fraud conspiracy, and money laundering conspiracy. DOJ stated Nagy remained at large when the indictment was unsealed

### 🌰 Liquidity Pool Exploit (March 2023)

On March 28, 2023, an external attacker exploited a vulnerability in the SafeMoon V2 contract to drain approximately $8.9 million in BNB from the liquidity pool. The attack used a public `burn()` function that could be called by anyone to artificially inflate the token price within the LP, then the attacker swapped overvalued SFM tokens for BNB. This exploit:

1. Revealed that the LP was not in fact "locked" or protected as claimed
2. Effectively ended SafeMoon as a functional token
3. Provided additional evidence for prosecutors about the lack of security controls

### Bankruptcy

SafeMoon US LLC filed for Chapter 7 bankruptcy (liquidation, not reorganization) in the U.S. Bankruptcy Court for the District of Utah on December 14, 2023, indicating no viable path to continued operations.

## Lessons for Market Surveillance

The SafeMoon case demonstrates manipulation patterns that market surveillance systems should monitor on decentralized exchanges:

1. **Transaction tax tokens**: Tokens with high transaction taxes (>5%) that penalize selling create an asymmetric information environment where insiders can extract value while retail investors face steep exit costs. The tax itself is a manipulation enabler.
2. **LP token custody**: For any token where a significant portion of liquidity is in an automated market maker pool, verify whether the LP tokens are locked in a time-locked, non-upgradeable contract or held by individuals. Unlocked LP tokens give holders the ability to rug-pull at any time.
3. **Volume-to-tax-rate mismatch**: High trading volume on a token with a punitive transaction tax is an anomaly. If a token charges 10% per trade but shows volume-to-market-cap ratios above 3%, either wash trading is occurring (and the wash traders have found a way to reduce the effective tax) or the volume is fabricated.
4. **Social-media-correlated price action**: Price movements that correlate primarily with hashtag trends, influencer posts, and coordinated "buy events" rather than product milestones or partnership announcements indicate manufactured demand.
5. **Fair launch claims vs. wallet distribution**: Tokens marketed as "fair launch" (no pre-mine, no team allocation) should be verified against on-chain wallet distribution data. Concentration of supply in a small number of wallets contradicts fair launch claims and enables price manipulation.
6. **Smart contract upgrade authority**: Tokens where the deployer retains admin or owner privileges over critical functions (minting, liquidity management, fee adjustment) carry elevated manipulation risk regardless of what the whitepaper claims about decentralization.

## References

1. U.S. Securities and Exchange Commission. "SEC Charges SafeMoon, Its Founder, and Three Other Executives." Litigation Release No. 25888, Case 1:23-cv-08138, E.D.N.Y. November 1, 2023.
2. U.S. Department of Justice. "SafeMoon Founder and Two Others Charged with Fraud and Money Laundering." DOJ Press Release, November 1, 2023.
3. Chainalysis. "The 2024 Crypto Crime Report." Chapter 7: DeFi Rug Pulls and Exit Scams. Chainalysis Inc., February 2024.
4. CoinGecko. "SafeMoon (SFM) Historical Market Data." Retrieved May 2026.
5. BscScan. "SafeMoon Token Contract Transactions." Binance Smart Chain Explorer. Retrieved May 2026.
6. PeckShield. "SafeMoon Exploit Analysis — $8.9M Drained via Public Burn Bug." March 28, 2023.
7. U.S. Bankruptcy Court, District of Utah. SafeMoon US LLC Chapter 7 Filing. Case No. 23-25749. December 2023.
