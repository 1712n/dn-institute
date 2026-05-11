---
title: "HAWK memecoin launch sniper concentration and crash signals"
date: 2026-05-11
entities:
  - HAWK
  - Haliey Welch
  - Solana
  - OverHere
---

## Summary

The December 2024 launch of the HAWK memecoin, associated with internet personality Haliey Welch, is a useful market-health case study because the token exhibited several measurable launch-risk signals within minutes: celebrity-driven demand, rapid price appreciation, concentrated early-wallet buying, a very large single-wallet snipe, and a steep drawdown before ordinary buyers could reasonably assess the market.

Public reporting describes the sequence as follows:

1. HAWK launched on Solana on December 4, 2024.
2. The token briefly reached a reported market capitalization near $490 million.
3. The price then fell by roughly 90% or more within hours, with several reports describing a 91% decline in less than three hours or a 95% decline shortly after launch.
4. Cointelegraph reported Solscan data showing that one wallet bought 17.5% of supply seconds after launch for 4,195 WSOL, worth about $993,000 at the time.
5. Bubblemaps analysis, as summarized by Know Your Meme and other outlets, reported that 96% of supply was held by one wallet cluster and that 285 investors participated in the presale.
6. Investors later filed litigation alleging deceptive practices around the token launch; Welch publicly said she was cooperating with legal counsel for affected investors.

This article does not determine legal liability. It treats the HAWK launch as a monitoring pattern for market-abuse and market-quality teams: a token can appear to have massive demand while price discovery is dominated by one or a few early actors with privileged speed, launch access, or presale exposure.

## Launch pattern

HAWK was promoted as a memecoin tied to a viral personality rather than as an asset with underlying cash flow. That is common in memecoin markets, but HAWK differed from ordinary speculative volatility because the market structure changed extremely quickly after launch. The token attracted public attention, moved to a high reported market capitalization, and then collapsed before a stable secondary market formed.

The important market-health signal is the compression of the full boom-and-bust cycle into a very short window. When a token reaches hundreds of millions of dollars in reported valuation and then loses most of that value in hours, surveillance should examine whether the visible price move was created by broad organic demand or by thin liquidity, concentrated early holders, and automated launch-sniping.

## Single-wallet snipe

Cointelegraph reported that one wallet bought 17.5% of HAWK supply seconds after launch for 4,195 WSOL, worth approximately $993,000 at the time. That type of trade should be treated as a severe launch-concentration alert.

The issue is not simply that a trader bought early. A wallet buying that much supply immediately after launch can distort every downstream market-health indicator:

- reported market capitalization can rise quickly from a small float;
- retail buyers can mistake one large early position for broad demand;
- the buyer can become a dominant source of sell pressure;
- price impact can be extreme because public liquidity is still shallow;
- later wallet profit-and-loss distribution becomes highly asymmetric.

For a monitoring system, this should trigger an "early supply capture" rule: if any wallet obtains more than a threshold share of supply within the first few blocks or minutes, the token should be flagged as high-risk even if volume and social attention look strong.

## Wallet-cluster concentration

Bubblemaps analysis, summarized in public reporting, found that 96% of HAWK supply was allegedly held by one cluster of wallets. That is a different but related concentration signal from the single-wallet snipe.

Wallet clusters matter because supply can appear decentralized across many addresses while still being economically coordinated. A cluster may share funding sources, transaction timing, transfer paths, or common counterparties. In a launch market, these links are especially important because early cluster behavior can determine whether later buyers are entering a genuine market or providing exit liquidity to coordinated holders.

Useful cluster checks include:

- common funding wallets before launch;
- repeated transfers between launch wallets;
- synchronized buys or sells within the first hour;
- common deposit addresses after exits;
- presale allocations moving into market-making or sale wallets.

HAWK's reported cluster concentration would have produced an immediate high-risk score under this framework.

## Presale and float opacity

Know Your Meme's summary of Bubblemaps reporting states that 285 investors participated in HAWK's presale. Presales are not inherently abusive, but they change the economics of a public launch. A public buyer needs to know how much supply can be sold, by whom, and under what lockup or vesting terms.

If presale participants receive liquid supply while public marketing begins, the launch can become a transfer from late public buyers to earlier private participants. The market-health concern increases when presale details are paired with fast sniping and wallet clustering.

An exchange, market monitor, or consumer-risk dashboard should therefore track:

- presale share of total supply;
- lockup and vesting terms;
- whether presale wallets sell during the launch window;
- whether public float is sufficient for stable price discovery;
- whether marketing statements clearly explain private allocation risk.

## Drawdown speed

Several public reports describe HAWK falling by roughly 90% or more shortly after launch. Cointelegraph reported a 90% dump amid backlash. BTCC reported that the token fell 91% in less than three hours after reaching a market cap near $490 million. CryptoTimes reported litigation after an alleged 95% crash.

Drawdown speed is a useful quality metric because it measures how quickly demand disappears after the first public wave. A token that collapses within hours may have been priced by transient social attention rather than durable liquidity. When that collapse is combined with early holder concentration, it suggests late buyers were exposed to a market where insiders, presale holders, or snipers could exit far more efficiently than ordinary participants.

## Litigation and public response

Investor litigation followed the HAWK crash. The complaint, filed in December 2024, alleged that buyers suffered losses after the token's launch and marketing. Litigation is not proof of the underlying claims, but it is relevant market-health context because it shows that the event produced real-world loss allegations and reputational risk around token promotion.

Welch later said publicly that she was cooperating with legal counsel representing affected investors. For market monitoring, the post-launch legal response is a lagging indicator. It is less useful for real-time prevention than the on-chain concentration and launch-window trading signals, but it helps validate that early warning rules would have identified a socially and financially significant event.

## Market-health indicators to track

The HAWK case suggests several indicators for celebrity memecoin launches.

### Early supply capture

Flag any wallet that acquires a large share of supply within seconds or minutes of launch. A 17.5% acquisition by one wallet is extreme enough to warrant an automatic high-risk alert.

### Clustered launch wallets

Calculate supply held by related wallet clusters, not only by individual addresses. Reported 96% cluster concentration is a stronger signal than a top-holder table alone.

### Presale-to-public imbalance

Track how much supply was available to private participants before public buyers arrived, and whether those wallets sell during the first trading window.

### Peak-to-crash compression

Measure the time between peak reported market capitalization and a 50%, 75%, or 90% decline. A 90% drawdown within hours should trigger a market-quality warning.

### Promotion-source dependency

Measure whether buying activity is tied to a celebrity announcement or influencer promotion rather than organic product usage. High promotion dependency makes a token more vulnerable to reflexive exits.

### Retail loss exposure

Estimate how many wallets bought after the peak or during the post-peak decline. This identifies whether losses are concentrated among late retail entrants.

## Why HAWK belongs in a market manipulation wiki

HAWK shows how a memecoin launch can combine legitimate-looking public hype with fragile market structure. The token's market risk was not hidden in complex smart-contract logic; it was visible in basic launch metrics:

- a celebrity-driven public attention spike;
- a huge early single-wallet position;
- alleged wallet-cluster concentration;
- opaque presale economics;
- rapid peak-to-crash timing.

Those signals are the same inputs a market-health system can use for earlier intervention. Even before legal claims are resolved, HAWK demonstrates why exchanges, retail dashboards, and analysts should treat launch concentration as a first-class risk metric.

## Sources

- [Cointelegraph: HAWK dumps 90% amid launch backlash](https://cointelegraph.com/news/hawk-tuah-memecoin-dumps-90-percent-outrage-token-launch-insider)
- [Know Your Meme: HAWK rug pull scandal summary and Bubblemaps supply-cluster reporting](https://knowyourmeme.com/memes/hawk-tuah-girls-hawk-meme-coin-rug-pull-scandal)
- [Halborn: explanation of the Hawk Tuah rug-pull allegations](https://www.halborn.com/blog/post/explained-the-hawk-tuah-rug-pull-december-2024)
- [BTCC: HAWK price crash and market-cap timeline](https://www.btcc.com/en-US/academy/research-analysis/hawk-tuah-crypto-scam-everything-you-need-to-know)
- [DL News: insiders, bots, and HAWK launch mechanics](https://www.dlnews.com/articles/markets/investors-angry-hawk-tuah-girl-haliey-welch-memecoin-crashes/)
- [CryptoTimes: investor lawsuit after HAWK crash](https://www.cryptotimes.io/2024/12/20/investors-sue-creators-of-hawk-tuah-memecoin-after-95-crash/)
- [Hawk Tuah token complaint](https://www.lawoftheledger.com/wp-content/uploads/sites/15/2024/12/Hawk-Thua-Token-Complaint.pdf)
