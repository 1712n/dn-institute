---
date: 2024-08-10
entities:
  - BitMEX
  - HDR Global Trading
  - Arthur Hayes
  - Benjamin Delo
  - Samuel Reed
title: "🌰 BitMEX: $100 Million Settlement for Unregistered Derivatives Trading and AML Failures"
---

## Summary 🌰

[BitMEX](https://www.bitmex.com/), operated by HDR Global Trading Limited and affiliated entities, was one of the largest cryptocurrency derivatives exchanges by volume from 2014 to 2020. In August 2021, the U.S. Commodity Futures Trading Commission ([CFTC](https://www.cftc.gov/PressRoom/PressReleases/8412-21)) secured a [$100 million civil monetary penalty](https://www.cftc.gov/PressRoom/PressReleases/8412-21) against BitMEX for illegally operating an unregistered trading platform, failing to implement Know-Your-Customer (KYC) procedures, and maintaining inadequate Anti-Money Laundering (AML) controls. Concurrently, the U.S. Department of Justice [indicted](https://www.justice.gov/usao-sdny/pr/founders-and-executives-cryptocurrency-derivatives-exchange-charged) BitMEX's three co-founders — Arthur Hayes, Benjamin Delo, and Samuel Reed — on Bank Secrecy Act violations. 🌰

BitMEX's business model relied on [100x leverage](https://blog.bitmex.com/the-history-of-leverage/) on Bitcoin perpetual swaps, attracting speculative traders globally while deliberately avoiding regulatory compliance. The platform processed over [$2 trillion in trading volume](https://www.reuters.com/technology/bitmex-pay-100-mln-resolve-us-cftc-fincen-charges-2021-08-10/) between 2014 and 2020 without implementing basic customer identification, enabling potential money laundering, market manipulation, and sanctions evasion at scale. 🌰

## Market Manipulation Indicators 🌰

### Wash Trading and Volume Inflation

BitMEX's market structure created conditions conducive to wash trading and artificial volume inflation:

- **No KYC requirements until 2020**: Users could create accounts with only an email address, enabling single entities to operate multiple accounts and trade against themselves without detection. The CFTC [found](https://www.cftc.gov/PressRoom/PressReleases/8412-21) that BitMEX failed to implement a Customer Information Program that would identify users. 🌰
- **Maker-taker fee structure with rebates**: BitMEX offered [negative maker fees](https://www.bitmex.com/app/fees) (rebates of -0.025%) for limit orders, incentivizing market makers to post and fill their own orders, profiting from the rebate while creating artificial volume signals.
- **Auto-deleveraging mechanism**: When liquidations exceeded the insurance fund, profitable traders were forcibly closed through [auto-deleveraging](https://www.bitmex.com/app/autoDeleveraging), creating cascading liquidation events that generated artificial volume spikes. During the March 2020 crash, over [$1.6 billion in positions were liquidated](https://www.coindesk.com/markets/2020/03/13/bitmex-liquidated-over-1b-in-crypto-futures-in-24-hours/) on BitMEX in 24 hours.
- **Insurance Fund opacity**: BitMEX's insurance fund grew to over [$350 million](https://www.coindesk.com/markets/2020/10/01/bitmex-insurance-fund-and-its-outsized-profits/) in Bitcoin by 2020, accumulated from trader liquidations. The fund's growth trajectory suggested systematic socialized losses from leveraged positions, where the exchange profited from the spread between liquidation and bankruptcy prices. 🌰

### Price Manipulation via Liquidation Cascades

BitMEX's 100x leverage combined with its liquidation engine created a feedback loop that amplified price movements:

- **Liquidation engine as market participant**: When a trader's margin fell below maintenance requirements, BitMEX's liquidation engine would submit a market order at the bankruptcy price, creating selling pressure that could trigger further liquidations. Academic research by [Carol Alexander and Daniel Heck (2020)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3353583) documented this cascade mechanism. 🌰
- **March 12-13, 2020 ("Black Thursday")**: Bitcoin's price fell from $7,900 to $3,600 in 24 hours. BitMEX experienced a [25-minute outage](https://blog.bitmex.com/the-13-march-downtime-and-its-causes/) during the crash (02:15-02:40 UTC, March 13), during which the price on other exchanges partially recovered. When BitMEX came back online, the price gap between BitMEX and other exchanges was over 10%, suggesting the exchange's liquidation engine was itself driving the broader market crash.
- **Overload protection or market manipulation?**: BitMEX attributed the outage to hardware failures. However, the timing — at the exact moment when cascading liquidations would have pushed the exchange-wide insurance fund into deficit — raised questions from [market participants](https://www.theblockcrypto.com/post/58744/traders-are-raising-questions-about-bitmexs-bitcoin-crash-outage) about whether the platform was selectively halting trading to protect its own fund. 🌰

### Spoofing and Order Book Manipulation

BitMEX's orderbook exhibited patterns consistent with spoofing:

- **Large wall orders**: Traders placed large limit orders (often 500-2,000 BTC notional) at key price levels to create artificial support or resistance, then cancelled them as price approached. BitMEX's API allowed high-frequency order placement and cancellation without any rate limiting penalties or surveillance.
- **Mark price vs. last price divergence**: BitMEX used a composite index ("mark price") from other exchanges for liquidation purposes, but the "last price" on BitMEX could deviate significantly. Traders could manipulate the last price to trigger stop-losses of other users while avoiding their own liquidation through the mark price mechanism. 🌰

## Regulatory Actions 🌰

### CFTC Civil Action (2020-2021)

- **October 1, 2020**: CFTC filed civil enforcement action against BitMEX entities and three founders (Case No. 20-cv-8132, SDNY).
- **Charges**: Operating an unregistered swap execution facility, acting as an unregistered futures commission merchant, failing to implement required KYC/AML programs.
- **August 10, 2021**: Consent order entered — [$100 million civil penalty](https://www.cftc.gov/PressRoom/PressReleases/8412-21). Up to $50 million could be offset by a concurrent FinCEN penalty. 🌰
- **Remedial measures**: BitMEX certified that all U.S. persons were blocked, all active users underwent verification, and U.S. operations ceased (except limited technical staff).

### DOJ Criminal Prosecution (2020-2022) 🌰

- **October 1, 2020**: DOJ/SDNY indicted Arthur Hayes, Benjamin Delo, Samuel Reed, and Gregory Dwyer for willful violation of the Bank Secrecy Act.
- **February 24, 2022**: Arthur Hayes [pleaded guilty](https://www.justice.gov/usao-sdny/pr/cryptocurrency-exchange-co-founder-pleads-guilty-bank-secrecy-act-violation) to one count of violating the BSA. Hayes was sentenced to [six months of home confinement](https://www.reuters.com/technology/bitmex-co-founder-hayes-sentenced-six-months-home-detention-2022-05-20/) and a $10 million fine.
- **March 2022**: Benjamin Delo pleaded guilty to the same charge, sentenced to [30 months probation](https://www.coindesk.com/policy/2022/06/15/bitmex-co-founder-benjamin-delo-sentenced-to-30-months-of-probation/) and a $10 million fine.
- **July 2022**: Samuel Reed pleaded guilty, sentenced to [probation](https://www.coindesk.com/policy/2022/08/10/bitmex-co-founder-samuel-reed-sentenced-to-probation/).
- **November 2022**: Gregory Dwyer pleaded guilty, sentenced to probation. 🌰

### FinCEN Action (2021) 🌰

The Financial Crimes Enforcement Network ([FinCEN](https://www.fincen.gov/)) assessed a $100 million civil monetary penalty against BitMEX for willful violations of the Bank Secrecy Act, running concurrently with the CFTC penalty structure. BitMEX was required to retain an independent compliance consultant and implement a comprehensive AML program.

## Market Health Detection Metrics 🌰

BitMEX's case offers several lessons for cryptocurrency market surveillance:

- **Volume anomalies during outages**: The March 2020 crash demonstrated how a single exchange's operational failures can distort the entire market's price. [Market Health API](https://rapidapi.com/DNInstitute/api/crypto-market-health/) volume distribution metrics would flag the extreme concentration of volume during liquidation cascades followed by zero volume during the outage.
- **Buy-sell ratio distortions**: During liquidation cascades, the buy-sell ratio becomes heavily skewed as the exchange's liquidation engine acts as a forced seller. BitMEX's auto-deleveraging mechanism created artificial one-sided order flow that would register as anomalous in [buy-sell ratio analysis](https://dn.institute/market-health/docs/buy-sell/).
- **Cross-exchange price divergence**: BitMEX's last price deviated by 10%+ from other exchanges during the March 2020 event, a pattern detectable through cross-venue price comparison and [VWAP analysis](https://dn.institute/market-health/docs/vwap/). 🌰
- **Insurance fund growth as manipulation proxy**: Consistent insurance fund growth indicates systematic extraction from traders through the liquidation mechanism. This metric, unique to derivatives exchanges, signals an exchange structure that profits from volatility-driven liquidations rather than fair trading. 🌰

## Total Penalties 🌰

| Entity | Agency | Penalty | Year |
|--------|--------|---------|------|
| BitMEX entities | CFTC | $100,000,000 | 2021 |
| BitMEX entities | FinCEN | $100,000,000 (concurrent with CFTC) | 2021 |
| Arthur Hayes | DOJ | $10,000,000 fine + 6 months home confinement | 2022 |
| Benjamin Delo | DOJ | $10,000,000 fine + 30 months probation | 2022 |
| Samuel Reed | DOJ | Probation | 2022 |
| Gregory Dwyer | DOJ | Probation | 2022 |
| **Combined** | | **$100,000,000+** (CFTC/FinCEN concurrent) **+ $20,000,000** (founder fines) | |

## References 🌰

- [CFTC Press Release 8412-21: Federal Court Orders BitMEX to Pay $100 Million](https://www.cftc.gov/PressRoom/PressReleases/8412-21) 🌰
- [CFTC Press Release 8270-20: Original Enforcement Action Filing](https://www.cftc.gov/PressRoom/PressReleases/8270-20)
- [Alexander, C., & Heck, D. (2020). Price discovery in Bitcoin: The impact of unregulated markets. Journal of Financial Stability](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3353583)
- [CoinDesk: BitMEX Liquidated Over $1B in Crypto Futures in 24 Hours](https://www.coindesk.com/markets/2020/03/13/bitmex-liquidated-over-1b-in-crypto-futures-in-24-hours/)
- [Reuters: BitMEX to pay $100 million to resolve U.S. CFTC, FinCEN charges](https://www.reuters.com/technology/bitmex-pay-100-mln-resolve-us-cftc-fincen-charges-2021-08-10/)
- [DOJ SDNY: Hayes Guilty Plea](https://www.justice.gov/usao-sdny/pr/cryptocurrency-exchange-co-founder-pleads-guilty-bank-secrecy-act-violation)
- [BitMEX Blog: The 13 March Downtime and its Causes](https://blog.bitmex.com/the-13-march-downtime-and-its-causes/) 🌰
- [Bitwise Report on Market Manipulation (SEC Filing)](https://www.sec.gov/comments/sr-nysearca-2019-01/srnysearca201901-5164833-183434.pdf)
