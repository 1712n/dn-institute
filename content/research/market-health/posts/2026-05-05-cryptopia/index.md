---
title: "🌰 Cryptopia — Exchange Hack, Liquidation, and Multi-Year Creditor Recovery Process"
date: 2026-05-05
entities:
  - Cryptopia
  - New Zealand
  - Grant Thornton
  - Ethereum
  - Bitcoin
---

## Summary

1. **In January 2019, the New Zealand-based cryptocurrency exchange Cryptopia was hacked**, losing an estimated $16-30 million in various cryptocurrencies. The exchange went into liquidation in May 2019, and the subsequent creditor recovery process became one of the most complex and prolonged exchange insolvency proceedings in cryptocurrency history.
2. **The attack exploited Cryptopia's wallet infrastructure**, allowing the attacker to drain funds from thousands of individual wallet addresses across multiple blockchains. The specific vulnerability was not fully disclosed publicly, but blockchain analysis revealed that the attacker accessed private keys for a large number of Cryptopia's customer wallets.
3. **Cryptopia was a New Zealand exchange known for listing hundreds of small-capitalization tokens**, many of which were not available on larger exchanges. At its peak, the exchange listed over 500 trading pairs and served a global user base, though its total volume was modest compared to top-tier exchanges.
4. **The liquidation process, managed by Grant Thornton New Zealand, established legal precedents** for how cryptocurrency assets held by an exchange on behalf of customers should be treated in insolvency proceedings. In a landmark 2020 High Court ruling (Ruscoe v Cryptopia), the court determined that cryptocurrencies held by Cryptopia were property held on trust for customers — not general assets of the company — establishing an important principle for exchange insolvency proceedings globally.
5. **The recovery process extended over multiple years**, with Grant Thornton managing the identification of approximately 960,000 account holders, the tracing and securing of remaining assets, and the development of a claims and distribution process. The case illustrated the practical difficulties of exchange insolvency when dealing with hundreds of different cryptocurrency assets, anonymized accounts, and cross-jurisdictional claimants.

## Background

### Cryptopia Exchange

Cryptopia was founded in 2014 in Christchurch, New Zealand. The exchange carved out a niche by listing a very large number of small-capitalization and newly launched tokens that were not available on major exchanges like Binance or Coinbase:

- **Extensive listings**: Over 500 trading pairs at various points, covering tokens from small blockchain projects, newly launched ICOs, and niche cryptocurrencies
- **Global user base**: Despite being based in New Zealand, the exchange served customers worldwide
- **Trading volume**: Modest by industry standards — typically $1-5 million in daily volume, compared to billions for top-tier exchanges
- **Fee model**: Standard maker-taker fees with a focus on accessibility for small-cap token trading

### Exchange Infrastructure

| Parameter | Value |
|-----------|-------|
| Founded | 2014 |
| Location | Christchurch, New Zealand |
| Registered users | ~960,000 (as determined during liquidation) |
| Listed tokens | 500+ (varying over time) |
| Wallet architecture | Individual wallet addresses per user per coin |
| Cold/hot storage split | Details not publicly disclosed |
| KYC requirements | Limited (varied by jurisdiction and volume) |

The exchange's wallet architecture — maintaining individual addresses for each user for each listed token — meant that the infrastructure involved managing a very large number of private keys, expanding the attack surface relative to exchanges that used pooled wallets.

## The January 2019 Hack

### Attack Timeline

| Date | Event |
|------|-------|
| January 13, 2019 | Unauthorized transfers begin from Cryptopia wallets |
| January 14, 2019 | Cryptopia detects the breach and places the exchange in maintenance mode |
| January 15, 2019 | Cryptopia announces on Twitter: "We are currently experiencing an unscheduled maintenance, we are looking into the cause and will keep you updated" |
| January 15-16 | New Zealand Police notified; investigation begins |
| January 16 | Cryptopia confirms security breach; exchange remains offline |
| January 28 | A second wave of unauthorized transfers is detected from Cryptopia wallets (indicating the attacker still had access or had retained keys) |
| March 2019 | Cryptopia briefly reopens for limited trading and withdrawals |
| May 15, 2019 | Cryptopia enters liquidation; Grant Thornton appointed as liquidator |

### Attack Mechanics

The precise technical details of the hack were not comprehensively disclosed in public reporting. Based on available information from blockchain analysis, the New Zealand Police investigation, and Grant Thornton's reports:

1. **Wallet key compromise**: The attacker gained access to private keys for a large number of Cryptopia's customer wallet addresses. Unlike exchange hacks that drain a single hot wallet, the Cryptopia attack involved draining thousands of individual addresses.

2. **Multi-chain theft**: Funds were stolen across multiple blockchains, including Ethereum (ETH and ERC-20 tokens), Bitcoin, and various other chains where Cryptopia maintained wallets.

3. **Extended access**: The second wave of transfers on January 28 — two weeks after the initial breach was detected — suggested either that the attacker retained access to key material after the initial breach was discovered, or that the breach involved the compromise of key generation or storage systems rather than individual keys.

4. **Estimated losses**: Various sources estimate the total stolen amount at between $16 million and $30 million. The uncertainty in the figure reflects difficulty in valuing hundreds of small-cap tokens at the time of theft, many of which had limited liquidity.

### Blockchain Analysis Findings

Blockchain analytics firms tracked the stolen funds:

- **Ethereum-based assets**: The attacker's Ethereum addresses were identified and tracked. Stolen ERC-20 tokens were swapped on decentralized exchanges or sent to other platforms.
- **Bitcoin**: Stolen BTC was moved through multiple intermediate addresses.
- **Small-cap tokens**: Many of the stolen small-cap tokens were effectively illiquid — the attacker could not sell significant quantities without crashing the price, limiting the realizable value of the theft.
- **January 2020 arrest**: In a related development, a person was arrested in the United States in connection with laundering stolen Cryptopia funds through other exchanges. This arrest demonstrated that at least some of the stolen funds were traced to identifiable individuals.

## Liquidation and Legal Proceedings

### Grant Thornton Appointment

When Cryptopia entered liquidation in May 2019, Grant Thornton New Zealand was appointed as liquidator. The firm faced an unprecedented set of challenges:

1. **Account identification**: Identifying and contacting approximately 960,000 account holders, many of whom had limited KYC information on file
2. **Asset securing**: Locating and securing Cryptopia's remaining cryptocurrency assets across hundreds of different blockchains and tokens
3. **Legal framework**: Operating in uncharted legal territory regarding the treatment of cryptocurrency assets in insolvency
4. **Valuation**: Establishing fair valuation for hundreds of tokens, many of which had minimal or no market liquidity

### Ruscoe v Cryptopia: Landmark Ruling

In April 2020, the New Zealand High Court issued a landmark ruling in *Ruscoe v Cryptopia Ltd (in liquidation)* that established important principles for cryptocurrency and exchange insolvency:

**Key holdings**:

1. **Cryptocurrency is property**: The court confirmed that cryptocurrencies meet the legal definition of property — they are identifiable, have value, and are capable of being owned. This was significant because the legal status of cryptocurrency as property was not universally established in 2020.

2. **Trust relationship**: The court held that Cryptopia held customer cryptocurrency assets on trust for the customers. This meant that the crypto assets were not part of Cryptopia's general asset pool available to all creditors — they belonged to the customers who deposited them.

3. **Customer priority**: As trust property, customer cryptocurrency holdings took priority over claims by Cryptopia's general creditors (including trade creditors, tax authorities, and the company's own shareholders).

**Impact of the ruling**:

- Set a precedent that has been cited in cryptocurrency insolvency proceedings in other jurisdictions
- Provided clarity for exchange operators about their legal obligations regarding customer assets
- Influenced the development of cryptocurrency custody regulations in New Zealand and beyond
- Distinguished from the outcome in some other exchange insolvencies (such as Mt. Gox in Japan, where the treatment of customer assets was determined under different legal frameworks)

### Distribution Process

Grant Thornton developed a multi-phase distribution process:

1. **Claims portal**: A web-based portal where account holders could verify their identity and submit claims
2. **Account reconciliation**: Matching customer claims against Cryptopia's internal records and blockchain data
3. **Coin-by-coin approach**: Because hundreds of different tokens were involved, the liquidation had to handle each token type separately
4. **Conversion decisions**: For tokens with minimal liquidity, decisions had to be made about whether to attempt to sell them or distribute them directly to claimants
5. **Timeline**: The distribution process extended over multiple years, with initial distributions beginning in 2023 — approximately four years after the hack

## Market Impact

### Immediate Effects

The Cryptopia hack had limited impact on the broader cryptocurrency market, given the exchange's modest size:

- **BTC price**: No measurable impact attributable to the Cryptopia hack
- **Small-cap tokens**: Tokens primarily traded on Cryptopia experienced temporary price disruption on other exchanges, though many had limited alternative liquidity
- **NZD market**: The hack affected New Zealand's cryptocurrency ecosystem disproportionately, as Cryptopia was one of the country's primary cryptocurrency exchanges

### Long-Term Industry Impact

1. **Exchange security standards for small exchanges**: The hack highlighted that smaller exchanges with extensive token listings face a disproportionately large key management burden — hundreds of different blockchains, each requiring secure key management — that may exceed their security capabilities.

2. **Liquidation precedent**: The Ruscoe v Cryptopia ruling became a reference point for legal professionals and regulators dealing with exchange insolvency.

3. **Long-tail token risk**: The case demonstrated that exchanges listing hundreds of small-cap tokens expose customers to a unique risk — in a hack or insolvency, many of these tokens may be effectively worthless by the time recovery proceedings conclude.

4. **New Zealand regulatory evolution**: The incident contributed to New Zealand's development of a more comprehensive framework for cryptocurrency service providers.

## Vulnerability Pattern: Multi-Wallet Key Management at Scale

### The Small Exchange Security Challenge

Cryptopia's situation illustrates a security challenge specific to smaller exchanges that list many tokens:

| Security Dimension | Large Exchange | Small Exchange (Cryptopia-type) |
|-------------------|---------------|-------------------------------|
| Number of blockchains | 10-30 (curated) | 100+ (permissive listing) |
| Key management complexity | High but manageable | Extremely high relative to resources |
| Security team size | 50-200+ dedicated staff | Often single-digit |
| Cold storage implementation | Mature, audited | Variable quality |
| Monitoring per chain | Per-chain alerting | Potentially incomplete |
| Insurance coverage | Common for top-tier | Rarely available or affordable |

The mismatch between the security burden of managing hundreds of different cryptocurrencies and the resources available to a small exchange creates a structural vulnerability.

### Exchange Hack Comparison by Exchange Size

| Exchange | Date | Loss | Exchange Size (TVL) | Loss/TVL Ratio |
|----------|------|------|-------------------|---------------|
| Mt. Gox | 2014 | ~$473M | Largest (at the time) | Catastrophic (100%) |
| Bitfinex | 2016 | ~$72M | Top 5 | Significant (~15-20%) |
| Coincheck | 2018 | ~$530M | Large (Japan) | Very significant |
| Cryptopia | 2019 | ~$16-30M | Small-mid | Catastrophic (leading to liquidation) |
| KuCoin | 2020 | ~$280M | Top 10 | Significant but survivable |
| Bybit | 2025 | ~$1.5B | Top 3 | Significant but survivable |

The pattern shows that smaller exchanges are more likely to be existentially impacted by hacks — a $20M loss that a top-tier exchange can absorb may force a small exchange into liquidation.

## Lessons for Market Surveillance

1. **Small exchange disproportionate risk**: Exchanges with extensive token listings but limited resources present elevated security risk. Surveillance systems should weight exchange size and listing count as risk factors — a small exchange listing 500 tokens has a higher per-token security risk than a large exchange listing 50.

2. **Multi-chain wallet drain patterns**: The Cryptopia attack involved draining thousands of individual addresses across multiple chains, rather than a single hot wallet. Monitoring for coordinated, simultaneous small transfers from many addresses associated with a single exchange — particularly if directed to previously unseen addresses — should trigger alerts.

3. **Second-wave attack detection**: The January 28 second wave of transfers — two weeks after the initial breach — indicated persistent access. After an exchange breach is detected, surveillance should maintain elevated monitoring for follow-up transfers from the same exchange's addresses, as the attacker may retain key material.

4. **Liquidation process monitoring**: When an exchange enters liquidation, the remaining assets are managed by a liquidator. Surveillance should track liquidator-controlled addresses to ensure asset movements during the liquidation process are authorized and properly documented.

5. **Small-cap token liquidity risk in insolvency**: Tokens with limited liquidity outside a hacked exchange may become effectively worthless during a prolonged insolvency process. Surveillance and risk tools should assess what proportion of a token's liquidity depends on a single exchange.

6. **Trust vs. general asset treatment**: The Ruscoe v Cryptopia ruling determined that customer assets were held on trust, not as exchange property. This has implications for how surveillance systems model exchange insolvency risk — customers of exchanges in jurisdictions with trust treatment have different recovery expectations than those in general-creditor jurisdictions.

## References

1. Grant Thornton New Zealand. "Cryptopia Ltd (in liquidation) — Liquidators' Reports." Multiple reports, 2019-2024.
2. Ruscoe & Moore v Cryptopia Ltd (in liquidation) [2020] NZHC 728. New Zealand High Court, April 8, 2020.
3. New Zealand Police. "Operation Cryptopia — Investigation Updates." NZ Police, 2019-2020.
4. Chainalysis. "The 2020 Crypto Crime Report." Chapter: Exchange Hacks. Chainalysis Inc., February 2020.
5. CoinDesk. "Cryptopia Exchange Hacked, Puts Site in Maintenance Mode." CoinDesk, January 15, 2019.
6. Blockchain analysis by Elementus. "Cryptopia Hack Analysis." Elementus, January 2019.
