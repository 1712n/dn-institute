---
title: "FBI Sting Operation Exposes Systematic Wash Trading by Gotbit, ZM Quant, CLS Global, and MyTrade"
date: 2024-10-09
entities:
  - Gotbit
  - ZM Quant
  - CLS Global
  - MyTrade
  - Lillian Finance
  - Saitama
  - Robo Inu Finance
  - VZZN
  - NexFundAI
---

## Summary

1. On October 9, 2024, the [U.S. Department of Justice](https://www.justice.gov/usao-ma/pr/eighteen-individuals-and-entities-charged-international-operation-targeting-widespread) and [SEC](https://www.sec.gov/newsroom/press-releases/2024-166) charged 18 individuals and entities in what prosecutors called the "first of its kind" cryptocurrency market manipulation crackdown, targeting professional **wash trading services** offered by market makers to artificially inflate token trading volumes.
2. **Four market maker firms** — [Gotbit](https://gotbit.io/) (Russia/Portugal), ZM Quant (China), CLS Global (UAE), and MyTrade (unspecified) — were charged with providing **wash trading as a service** to token issuers, using algorithmic bots to execute self-trades that created artificial volume and price movement on cryptocurrency exchanges.
3. **Four token companies** — Lillian Finance, Saitama, Robo Inu Finance, and VZZN — allegedly hired these market makers to pump their tokens' apparent trading volumes, then sold their holdings at inflated prices in classic [pump-and-dump schemes](https://www.investopedia.com/terms/p/pumpanddump.asp).
4. The FBI took the **unprecedented step** of creating its own token, [NexFundAI](https://etherscan.io/token/0x98833Af3CCb0BBf25E9EE5FF3C7B4261BB78e1C2), and deploying it on Ethereum to collect evidence — the token was actually traded on exchanges until law enforcement disabled its trading function.
5. Evidence from **private Telegram chats and videoconferences** showed defendants openly discussing wash trading mechanics, with one defendant [telling an FBI agent](https://www.arnoldporter.com/en/perspectives/blogs/enforcement-edge/2024/10/remaking-the-classics) his company's bots could "solve the cold start problem" through wash trading, and another admitting "I know it's wash trading and I know people might not be happy about it."

## Wash Trading Methodology

### Market Maker Bot Operations

The charged market makers operated automated **wash trading bots** designed to create the illusion of genuine market activity. According to court filings and [Chainalysis research](https://www.chainalysis.com/blog/crypto-market-manipulation-wash-trading-pump-and-dump-2025/), these operations typically involved:

- **Self-trading**: Bots executed trades where the same entity was simultaneously buyer and seller, generating artificial volume without any real change in beneficial ownership
- **Volume targeting**: Token issuers specified desired daily trading volumes (e.g., $1M/day), and market makers programmed bots to hit these targets through coordinated self-trades
- **Exchange manipulation**: Bots operated on multiple centralized exchanges to create the appearance of organic cross-exchange demand
- **Price manipulation**: By controlling buy/sell timing and volume, market makers could gradually inflate token prices to predetermined targets before insiders executed coordinated sell-offs

### Scale of Operations

- **Gotbit**, led by CEO Fedor Kedrov, was one of the most prominent operations, [publicly advertising](https://gotbit.io/) market-making services while allegedly providing wash trading to numerous token projects
- **ZM Quant**, run by Baijun Ou and Ruiqi Lau, operated from China and offered similar algorithmic wash trading services
- **CLS Global**, through employee Andrey Zhorzhes, operated from the UAE and was caught on recorded calls [explaining wash trading capabilities](https://www.arnoldporter.com/en/perspectives/blogs/enforcement-edge/2024/10/remaking-the-classics) to undercover FBI agents
- **MyTrade** was the fourth market maker charged in the scheme

### The NexFundAI Token Sting

In an unprecedented investigative technique, the FBI:

1. Created a real ERC-20 token called **NexFundAI** and deployed it on Ethereum at address [0x98833Af3CCb0BBf25E9EE5FF3C7B4261BB78e1C2](https://etherscan.io/token/0x98833Af3CCb0BBf25E9EE5FF3C7B4261BB78e1C2)
2. FBI agents posed as NexFundAI promoters seeking market-making services
3. Engaged the defendants in Telegram chats and videoconferences where they [openly discussed and demonstrated](https://www.arnoldporter.com/en/perspectives/blogs/enforcement-edge/2024/10/remaking-the-classics) their wash trading capabilities
4. The token was actually listed and traded on exchanges, with market makers executing wash trades on it, generating real on-chain evidence
5. Law enforcement ultimately disabled the token's trading function once sufficient evidence was collected

## Indicators of Wash Trading

Based on this case and related [Chainalysis research on wash trading patterns in 2024](https://www.chainalysis.com/blog/crypto-market-manipulation-wash-trading-pump-and-dump-2025/):

- **Matched buy-sell transactions**: Addresses executing buy and sell transactions of nearly identical USD value (within 1% difference) within 25 blocks (~5 minutes). Chainalysis identified approximately **$704 million** in suspected wash trading volume using this heuristic across Ethereum, BNB Chain, and Base in 2024.
- **Multi-sender dispersion patterns**: Controller addresses distributing funds to 5+ managed addresses via token multi-senders, with managed addresses then executing balanced buy/sell activity in the same liquidity pools. This pattern accounted for an estimated **$1.87 billion** in suspected wash trading volume in 2024.
- **Concentration in specific pools**: Suspected wash trading was concentrated in approximately 1,000–1,800 DEX pools per month (only 0.2–0.3% of active pools), suggesting a small number of actors driving the artificial volume.
- **Disproportionate volume from few actors**: A single controller address was responsible for approximately $143 million in suspected wash trading volume in January 2024 alone; one address executed over 54,000 matched buy-and-sell transactions throughout the year.

## Timeline

- **Pre-2024**: Gotbit, ZM Quant, CLS Global, and MyTrade establish market-making operations offering wash trading services to cryptocurrency token issuers
- **2024 (early)**: FBI launches undercover operation, creating the [NexFundAI token](https://etherscan.io/token/0x98833Af3CCb0BBf25E9EE5FF3C7B4261BB78e1C2) as a sting operation
- **2024**: Undercover FBI agents engage defendants in Telegram chats and videoconferences, collecting evidence of wash trading services offered and executed
- **October 9, 2024**: [DOJ announces charges](https://www.justice.gov/usao-ma/pr/eighteen-individuals-and-entities-charged-international-operation-targeting-widespread) against 18 individuals and entities for wire fraud, market manipulation, and conspiracy
- **October 9, 2024**: [SEC files parallel civil charges](https://www.sec.gov/newsroom/press-releases/2024-166) against Gotbit (Fedor Kedrov), ZM Quant (Baijun Ou, Ruiqi Lau), CLS Global (Andrey Zhorzhes), and others for manipulating markets by wash trading on crypto exchanges
- **October 9, 2024**: NexFundAI token trading function is disabled at the direction of law enforcement
- **October 9, 2024**: DOJ seizes over [$25 million in cryptocurrency](https://www.justice.gov/usao-ma/pr/eighteen-individuals-and-entities-charged-international-operation-targeting-widespread) and disables trading bots associated with the defendants
- **February 2025**: [Chainalysis publishes research](https://www.chainalysis.com/blog/crypto-market-manipulation-wash-trading-pump-and-dump-2025/) estimating up to $2.57 billion in suspected wash trading volume across major blockchains in 2024, providing broader context for the scale of manipulation in crypto markets

## Regulatory Significance

This case represents a watershed moment in cryptocurrency enforcement:

- **First criminal charges** specifically targeting wash trading market makers in crypto
- **First use of an FBI-created token** as an investigative tool, setting precedent for law enforcement operations in DeFi
- Demonstrates that **encrypted messaging platforms** (Telegram) do not provide immunity from prosecution — communications on these platforms formed the core evidence
- Establishes that traditional securities fraud statutes, particularly **wire fraud**, apply directly to cryptocurrency market manipulation
- Highlights the **professionalization of wash trading** as a paid service industry within crypto, where market makers openly marketed volume inflation capabilities
