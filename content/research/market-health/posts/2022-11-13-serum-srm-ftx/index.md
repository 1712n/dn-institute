---
title: "Serum SRM: FTX-Linked Supply Concentration and Market Health Signals"
date: "2022-11-13"
description: "SRM's November 2022 collapse shows how concentrated exchange-linked token supply, admin-key dependency, and collapsing venue confidence can turn a governance token into a market health warning."
entities:
  - Serum
  - SRM
  - FTX
  - Alameda Research
  - OpenBook
  - Solana
---

## Summary

Serum's SRM token was a market-health warning during the FTX collapse because the token combined three fragile signals: large FTX/Alameda-linked inventory, an order-book protocol whose upgrade authority was no longer trusted, and a sharp public-market repricing after the FTX balance-sheet crisis became visible.

SRM was not just another liquid asset in the FTX ecosystem. It was the governance and fee token for Serum, a central limit order book used by Solana applications. When FTX failed in November 2022, market participants had to price both issuer concentration risk and protocol-control risk at the same time. The result was a rapid SRM drawdown and a community migration from Serum to OpenBook, making SRM a useful case study for surveillance teams monitoring exchange-linked tokens.

## Timeline

- **November 2, 2022:** CoinDesk published details from Alameda Research's balance sheet, reporting heavy exposure to FTX-associated tokens including FTT and SRM. That disclosure made the market focus on how much of Alameda's reported asset base was composed of illiquid ecosystem tokens rather than cash-like collateral.
- **November 8-11, 2022:** FTX entered a liquidity crisis and then Chapter 11 bankruptcy proceedings. SRM sold off alongside other FTX-linked assets.
- **November 13, 2022:** Solana developers publicly moved to fork Serum after concerns that Serum's upgrade path was no longer safe to rely on. OpenBook became the replacement order-book infrastructure.

## Price Signal

The supporting CSV in this folder samples DefiLlama's historical SRM price feed around the FTX collapse.

| Date       | SRM price, USD | Observation                                                            |
| ---------- | -------------: | ---------------------------------------------------------------------- |
| 2022-11-01 |         0.7681 | Before the public Alameda balance-sheet shock.                         |
| 2022-11-08 |         0.7451 | FTX liquidity concerns were spreading, but SRM had not fully repriced. |
| 2022-11-10 |         0.3204 | SRM had fallen about 57% from November 8.                              |
| 2022-11-29 |         0.2484 | The post-bankruptcy level stayed far below the pre-crisis range.       |

That price path is important because it was not only a broad market selloff. SRM had issuer-specific and infrastructure-specific risks: Alameda/FTX inventory created potential forced-seller pressure, while Serum's role in Solana DeFi meant that application developers had to evaluate whether the protocol itself remained safe to integrate.

## Market Health Signals

### 1. Exchange-linked token concentration

Exchange-affiliated tokens can be reflexive collateral. If a trading firm values a large internal token position at market price, the reported balance sheet may look solvent while public float is thin. Once confidence drops, that same token can become difficult to sell without moving the market.

SRM fit this pattern because FTX and Alameda were closely associated with Serum's launch and ecosystem. The useful surveillance signal is not "large token allocation" by itself. The warning appears when large insider-linked inventory, exchange solvency stress, and falling public liquidity appear together.

### 2. Control-plane risk

Serum's market-health problem was not limited to price. After FTX filed for bankruptcy, Solana developers worried that Serum's upgrade authority was compromised or no longer safe. Solana Foundation's status page described a community-led replacement build that used a separate verified program identifier. That emergency migration is a strong non-price signal: even if an order book still works technically, applications may abandon it when control of the upgrade path is unclear.

For surveillance purposes, this is similar to an exchange-reserve signal. A token venue can appear live while hidden authority or governance risk makes future market data less reliable.

### 3. Liquidity migration

Once OpenBook became the safer venue, SRM lost part of its infrastructure role. A governance or fee token can trade with a liquidity premium while applications depend on its protocol. If integrators migrate away, that premium can disappear quickly.

This makes migration announcements, deprecations, and emergency forks useful inputs for market-health monitoring. Price, depth, and trade-count metrics should be read together with repository, governance, and validator-ecosystem signals.

## Monitoring Rules

The SRM episode suggests several practical rules for exchange-linked or protocol-linked tokens:

- Track insider-linked token balances separately from circulating float, especially when the issuer or lead market maker is also a major exchange.
- Treat sudden exchange solvency stress as a liquidity shock for affiliated tokens, even before withdrawals or trading are officially halted.
- Flag tokens whose protocol depends on a privileged upgrade authority controlled by a distressed entity.
- Watch for emergency forks or migration recommendations; these can mark a loss of protocol trust before or alongside a token price collapse.
- Compare price declines with liquidity depth and venue availability. A large percentage move is more severe when supported markets are narrowing at the same time.

## References

- CoinDesk reported Alameda Research balance-sheet exposure to FTX-associated tokens, including SRM: [Divisions in Sam Bankman-Fried's Crypto Empire Blur on His Trading Titan Alameda's Balance Sheet](https://www.coindesk.com/business/2022/11/02/divisions-in-sam-bankman-frieds-crypto-empire-blur-on-his-trading-titan-alamedas-balance-sheet/)
- The Solana Foundation summarized ecosystem exposure and the Serum replacement-build context after the FTX bankruptcy, including its exposure to 134.54 million SRM tokens: [Solana Foundation Facts Related to FTX Bankruptcy](https://solana.com/news/solana-facts-ftx-bankruptcy)
- SRM historical prices sampled from DefiLlama's public coin price API: `https://coins.llama.fi/prices/historical/<timestamp>/coingecko:serum`
