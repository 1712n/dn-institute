---
date: 2019-02-05
entities:
  - QuadrigaCX
  - Gerald Cotten
  - Jennifer Robertson
title: "🌰 QuadrigaCX: $190 Million in Customer Funds Lost After Founder's Alleged Death"
---

## Summary 🌰

[QuadrigaCX](https://en.wikipedia.org/wiki/QuadrigaCX) was Canada's largest cryptocurrency exchange by reported volume until its collapse in early 2019. Following the reported death of founder and sole operator [Gerald Cotten](https://en.wikipedia.org/wiki/Gerald_Cotten) on December 9, 2018, in Jaipur, India, approximately [$190 million CAD ($145 million USD)](https://www.bbc.com/news/world-us-canada-47203706) in customer funds were found to be inaccessible. An investigation by the Ontario Securities Commission (OSC) revealed that QuadrigaCX had operated as a [fraud from its inception](https://www.osc.ca/sites/default/files/2020-06/20200611_quadrigacx-a-review-by-staff-of-the-osc.pdf), with Cotten misappropriating the majority of customer deposits, trading against customers using fictitious balances, and running the exchange as an effective Ponzi scheme. 🌰

## Market Manipulation Methods 🌰

### Fictitious Balances and Internal Trading 🌰

The [OSC Staff Notice 21-329](https://www.osc.ca/sites/default/files/2020-06/20200611_quadrigacx-a-review-by-staff-of-the-osc.pdf) (published June 2020) revealed the core manipulation mechanism:

- **Phantom balances**: Cotten created multiple internal accounts under aliases (including "Chris Markay," "Aretwo Deetwo," and others) and credited them with [fictitious cryptocurrency and fiat balances](https://www.nytimes.com/2022/02/17/technology/quadrigacx-gerald-cotten.html) that did not correspond to actual assets held by the exchange. 🌰
- **Trading against customers**: Using these phantom-funded accounts, Cotten traded directly against real QuadrigaCX users. When his aliases "purchased" cryptocurrency from real users, customers received fiat credits on the platform, but the corresponding crypto was transferred to Cotten's personal wallets rather than held in exchange reserves.
- **Scale of internal trading**: The OSC found that Cotten's alias accounts executed trades totaling approximately [$115 million CAD](https://www.osc.ca/sites/default/files/2020-06/20200611_quadrigacx-a-review-by-staff-of-the-osc.pdf) against real customers. These trades were visible on the order book and contributed to reported volume, but represented one-sided extraction rather than genuine market activity. 🌰
- **External exchange losses**: Cotten also used customer funds to trade on other exchanges (Poloniex, Kraken, Bitfinex), losing approximately [$28 million CAD](https://www.osc.ca/sites/default/files/2020-06/20200611_quadrigacx-a-review-by-staff-of-the-osc.pdf) through speculative leveraged positions.

### Volume Fabrication 🌰

QuadrigaCX's reported trading volume was significantly inflated by Cotten's internal trading:

- **Alias account volume**: The OSC identified that Cotten's personal accounts contributed a substantial portion of all trades on the platform, artificially inflating QuadrigaCX's volume rankings and making the exchange appear more liquid and legitimate than it was.
- **Wash trading dynamics**: By controlling both sides of many trades (alias accounts buying from and selling to each other), Cotten created the appearance of an active market. This attracted real depositors who saw an exchange with high volume and tight spreads, not realizing the volume was manufactured. 🌰
- **No independent audits**: QuadrigaCX never underwent a third-party audit of its reserves. The exchange operated for five years (2013-2019) without any verification that customer deposits matched exchange holdings.

### Cold Wallet Deception 🌰

After Cotten's death, the exchange claimed customer funds were locked in cold wallets accessible only to the deceased founder:

- **Ernst & Young investigation**: Court-appointed monitor [Ernst & Young (EY)](https://documentcentre.ey.com/api/Document/download?docId=25728&language=EN) discovered that QuadrigaCX's supposed cold wallets were either empty or had been drained months before Cotten's death.
- **Bitcoin cold wallets**: EY identified [six Bitcoin cold wallet addresses](https://documentcentre.ey.com/api/Document/download?docId=25728&language=EN) associated with QuadrigaCX. Five of the six had been emptied in April 2018 — eight months before Cotten's death — with funds transferred to external exchanges. 🌰
- **Hot wallet as cold wallet**: The exchange had been operating in a fractional-reserve manner, with far fewer assets on hand than customer liabilities, for at least its final year of operation.
- **$46 million shortfall at death**: By the time of Cotten's death, the total identified assets were approximately [$46 million CAD short](https://www.theglobeandmail.com/business/article-how-did-quadrigacx-lose-its-customers-crypto-its-a-complicated-story/) of total customer claims, even assuming recovery of all identifiable wallets.

## Regulatory Investigation 🌰

### OSC Staff Notice 21-329 (June 2020) 🌰

The Ontario Securities Commission's comprehensive review concluded:

- QuadrigaCX operated as a **fraud** — not simply a mismanaged business
- Cotten was the **sole operator** with exclusive access to all wallets and systems
- The exchange had **no proper books or records**, no segregation of customer funds, and no independent oversight
- Customer deposits were **commingled with personal funds** and used for personal expenses including luxury real estate, travel, and personal investments 🌰

### CCAA Proceedings (2019-2020)

- **January 28, 2019**: QuadrigaCX applied for creditor protection under the Companies' Creditors Arrangement Act (CCAA) in the Nova Scotia Supreme Court
- **February 5, 2019**: Court granted initial CCAA order and appointed EY as monitor
- **June 2019**: EY's [Fifth Report](https://documentcentre.ey.com/api/Document/download?docId=25996&language=EN) detailed the extent of missing funds and Cotten's personal enrichment 🌰
- **76,319 affected creditors** filed claims totaling approximately $214.6 million CAD
- EY recovered approximately **$46 million CAD** from Jennifer Robertson (Cotten's widow), who returned assets including real estate, a yacht, and a private aircraft

### RCMP Investigation

- The Royal Canadian Mounted Police (RCMP) opened a criminal investigation but as of 2023 had not filed charges, partly because the primary suspect (Cotten) was deceased
- Conspiracy theories about Cotten faking his death persisted, fueled by the fact that he died in India (a country where death certificates can be obtained fraudulently), that he had updated his will 12 days before departing, and that he had a documented history of [online fraud prior to founding QuadrigaCX](https://vanity-fair.com/news/2019/11/the-strange-tale-of-quadriga-gerald-cotten) 🌰

## Market Health Detection Metrics 🌰

The QuadrigaCX case highlights several detection signals relevant to the [DN Institute Market Health framework](https://dn.institute/market-health/):

- **Volume-to-reserve ratio anomalies**: QuadrigaCX's reported volume was high relative to what its actual reserves could support. [Volume distribution analysis](https://dn.institute/market-health/docs/volumedist/) comparing reported volume against known on-chain reserves would have revealed the mismatch. 🌰
- **Benford's Law violations**: Trading data generated partly by a single operator's internal accounts would likely deviate from [Benford's Law](https://dn.institute/market-health/docs/benford/) distributions, particularly in trade sizes and frequencies, since human-generated trading patterns differ systematically from natural market activity.
- **Buy-sell ratio consistency**: With Cotten's alias accounts consistently buying real crypto from customers (one-directional extraction), the [buy-sell ratio](https://dn.institute/market-health/docs/buy-sell/) would show persistent asymmetry compared to genuine two-sided markets. 🌰
- **Withdrawal delays as leading indicator**: In the months before collapse, QuadrigaCX customers reported increasing withdrawal delays — a classic signal of fractional-reserve operation. Monitoring withdrawal processing times as a market health metric could provide early warning for similar future cases.

## Losses 🌰

| Category | Amount (CAD) | Amount (USD) |
|----------|-------------|-------------|
| Total customer claims | $214,600,000 | ~$164,000,000 |
| Identified missing funds | $190,000,000 | ~$145,000,000 |
| Cotten's internal trading | $115,000,000 | ~$88,000,000 |
| External exchange losses | $28,000,000 | ~$21,000,000 |
| Recovered by EY | $46,000,000 | ~$35,000,000 |
| **Net customer losses** | **~$168,600,000** | **~$129,000,000** |

## References 🌰

- [OSC Staff Notice 21-329: QuadrigaCX — A Review by Staff of the Ontario Securities Commission (June 2020)](https://www.osc.ca/sites/default/files/2020-06/20200611_quadrigacx-a-review-by-staff-of-the-osc.pdf) 🌰
- [Ernst & Young — QuadrigaCX Court Monitor Reports](https://documentcentre.ey.com/api/Document/download?docId=25728&language=EN)
- [BBC News: QuadrigaCX: Cryptocurrency exchange customers unable to access $190m](https://www.bbc.com/news/world-us-canada-47203706)
- [New York Times: How a Crypto King Abused Users' Trust (February 2022)](https://www.nytimes.com/2022/02/17/technology/quadrigacx-gerald-cotten.html) 🌰
- [The Globe and Mail: How did QuadrigaCX lose its customers' crypto?](https://www.theglobeandmail.com/business/article-how-did-quadrigacx-lose-its-customers-crypto-its-a-complicated-story/)
- [Netflix Documentary: Trust No One: The Hunt for the Crypto King (2022)](https://www.netflix.com/title/81349029)
- [Vanity Fair: The Strange Tale of Quadriga (November 2019)](https://www.vanityfair.com/news/2019/11/the-strange-tale-of-quadriga-gerald-cotten) 🌰
