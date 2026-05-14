---
title: "Neutrino USDN Peg Breaks Across Waves Liquidity Stress"
date: 2022-04-04
entities:
  - Neutrino
  - USDN
  - Waves
  - WAVES
  - Vires Finance
---

## Summary

On April 4, 2022, Neutrino USD (USDN), an algorithmic stablecoin in the Waves ecosystem, lost its dollar peg during a sharp selloff in WAVES and a market-wide dispute over leverage, liquidity, and alleged manipulation around Vires Finance. [CoinDesk reported](https://www.coindesk.com/markets/2022/04/04/waves-usdn-stablecoin-loses-peg-drops-15-amid-manipulation-scare) that USDN dropped roughly 15% amid accusations that activity around Waves and Vires had distorted the WAVES market. [The Motley Fool reported](https://www.fool.com/investing/2022/04/05/why-waves-plunged-on-monday/) that the WAVES token fell more than 28% over 24 hours as the USDN peg unraveled.

USDN did not stabilize after a single isolated break. [CoinDesk reported](https://www.coindesk.com/markets/2022/05/11/crisis-in-terras-ust-stablecoin-spreads-to-neutrino-usd-on-waves-protocol) in May 2022 that USDN slipped below its peg again while TerraUSD was collapsing, and explained that the system relied on users locking WAVES to mint USDN and redeeming USDN to unlock WAVES. [CoinDesk later reported](https://www.coindesk.com/business/2022/08/26/algorithmic-stablecoin-usdn-falls-from-dollar-peg-as-liquidity-slumps) that USDN traded around $0.91 in August 2022, with analysts describing a fragile backing ratio and reduced liquidity.

The USDN case is a Market Health example of reflexive collateral and venue-linked liquidity risk. The stablecoin's peg depended on confidence in WAVES, but WAVES itself was exposed to the stablecoin's health, lending-market incentives, and forced unwind dynamics. When confidence weakened, the market priced USDN as a risky claim on a volatile collateral loop rather than as a cash-equivalent dollar.

## Metrics Used

### Peg deviation persistence

The most visible signal was repeated deviation from $1. A one-time intraday discount can reflect temporary liquidity pressure. Repeated discounts across April, May, and August 2022 showed that market confidence had not fully recovered and that arbitrage or protocol recapitalization was not reliably restoring the peg.

Useful peg metrics include:

- lowest USDN price during each stress window;
- number of hours or days spent below $0.99, $0.95, and $0.90;
- spread between USDN markets on Waves, centralized venues, and cross-chain venues;
- recovery speed after governance changes or issuer statements;
- whether each recovery required external liquidity or new incentive programs.

### Reflexive collateral exposure

USDN was backed through the WAVES ecosystem, so the peg relied on the market value and liquidity of the same asset whose price could be pressured by a peg break. If USDN holders redeem into WAVES while WAVES is falling, each redemption can add sell pressure to the collateral token. That is a reflexive loop: stablecoin weakness harms collateral confidence, and collateral weakness harms stablecoin confidence.

Market-health monitoring should separate nominal collateral value from stress collateral value. A collateral ratio based on a volatile token can look adequate before a selloff and then become inadequate quickly when the market tries to exit both the stablecoin and the backing token at the same time.

### Lending-market concentration

Vires Finance mattered because it concentrated leverage, stablecoin deposits, and borrowing activity inside the same ecosystem. Lending markets can make a stablecoin look liquid during expansion, but under stress they can also trap liquidity, concentrate bad debt, or incentivize users to unwind positions into thin markets.

Relevant lending-market metrics include:

- USDN deposits and borrow utilization on Vires;
- WAVES collateral concentration among large borrowers;
- liquidation thresholds and liquidation throughput;
- protocol bad debt or withdrawal queue depth;
- stablecoin APYs that may signal subsidized or fragile demand.

### Backing-ratio transparency

By August 2022, CoinDesk cited analysts who said USDN's backing through WAVES was around 14%. Whether that number was disputed or later changed, the market-health lesson is that algorithmic stablecoins require clear, current backing-ratio reporting. If users cannot independently understand the effective reserve buffer, peg defense depends on trust at the exact moment trust is under stress.

The same fields are summarized in [usdn-signals.csv](usdn-signals.csv) for dataset-based review.

| Signal                 | Observation                                                              | Market-health interpretation                                      |
| ---------------------- | ------------------------------------------------------------------------ | ----------------------------------------------------------------- |
| April peg break        | USDN dropped sharply below $1 as WAVES sold off                          | Stablecoin confidence weakened alongside collateral-token stress  |
| Repeated depegs        | USDN slipped again during the May UST crisis and August liquidity stress | Peg recovery was not durable across market regimes                |
| Reflexive collateral   | USDN mint/redeem mechanics depended on WAVES                             | A falling collateral token can amplify stablecoin redemption risk |
| Lending concentration  | Vires Finance was central to accusations and liquidity concerns          | Lending markets can concentrate leverage and exit pressure        |
| Backing-ratio concerns | Analysts later cited a low effective backing ratio                       | Reserve transparency and stress collateral value require tracking |

## Timeline

- **March 31-April 4, 2022:** USDN began wobbling below peg and then dropped sharply while WAVES sold off and market participants debated activity around Vires Finance.
- **April 5, 2022:** Public coverage connected the WAVES selloff to the USDN peg break and renewed concern about algorithmic stablecoin design.
- **May 11, 2022:** USDN slipped below peg again during the TerraUSD collapse, showing sensitivity to broader algorithmic-stablecoin confidence shocks.
- **August 26, 2022:** USDN traded around $0.91 as liquidity weakened and analysts questioned the stability of the backing model.
- **After 2022:** USDN remained a reference case for reflexive collateral, lending-market concentration, and repeated depeg monitoring.

## Market Health Lessons

USDN shows that algorithmic stablecoins can fail gradually through repeated confidence breaks rather than one final collapse. Each depeg made the next one easier because the market had evidence that peg defense depended on volatile collateral, thin liquidity, and changing governance responses.

For market-health analysis, the important signals are peg duration, collateral-token drawdown, backing-ratio sensitivity, lending-market utilization, and redemption throughput. A stablecoin that relies on a volatile ecosystem token needs stronger buffers and clearer reporting than a fiat-backed token, because the collateral can lose value at the same time users are trying to exit the stablecoin.
