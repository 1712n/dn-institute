---
title: "BUSD Paxos Mint Halt and Redemption Run"
date: 2023-02-13
entities:
  - Paxos
  - BUSD
  - Binance
  - NYDFS
  - USDP
---

## Summary

On February 13, 2023, Paxos announced that it would stop minting new BUSD tokens and end its relationship with Binance for the branded stablecoin. [Paxos said](https://www.paxos.com/newsroom/paxos-will-halt-minting-new-busd-tokens) the halt would take effect on February 21, that existing BUSD remained fully backed, and that customers could redeem BUSD for U.S. dollars or convert it to USDP.

[The New York Department of Financial Services said](https://www.dfs.ny.gov/consumers/alerts/Paxos_and_Binance) it ordered Paxos to cease minting Paxos-issued BUSD because of unresolved issues related to Paxos' oversight of its relationship with Binance. [Paxos later reported](https://www.paxos.com/newsroom/paxos-manages-the-safe-redemption-of-7-9b-busd-in-one-month-without-market-disruption) that it safely redeemed $7.9 billion of BUSD in one month without market disruption.

The market-health issue was not a reserve shortfall. It was issuance and redemption-path risk: once new minting ended, BUSD became a shrinking stablecoin whose market cap, exchange liquidity, and pool usage would only decline unless another issuer relationship replaced it.

## Manipulation Analysis

The first stress vector was regulatory issuance risk. Stablecoin users often focus on reserves, but the ability to mint new supply is also market infrastructure. When minting is halted, arbitrage and exchange liquidity have to adapt to a one-way redemption path.

The second vector was issuer-brand dependency. BUSD was issued by Paxos but carried Binance branding and distribution. NYDFS specifically highlighted Paxos' oversight relationship with Binance, making the stablecoin's market health dependent on legal, operational, and commercial links outside the token contract.

The third vector was redemption concentration. Paxos' redemption report shows that BUSD holders redeemed billions of dollars in a short period. That outcome was orderly, but the event still demonstrates why stablecoins need dashboards that track redemption velocity after issuer or regulator announcements.

The fourth vector was liquidity migration. As BUSD supply declines, trading pairs, liquidity pools, and collateral systems that rely on BUSD need replacement assets. Protocols that treat all dollar stablecoins as interchangeable can miss the risk that one token's issuance lifecycle has changed.

## Metrics Used

### Issuance-status risk

The primary signal is whether the stablecoin can still expand supply to meet demand.

Useful metrics include:

- minting enabled or halted;
- announced halt date;
- remaining redemption window;
- issuer relationship changes;
- stablecoin market cap after the announcement.

### Redemption velocity

Orderly redemption still needs capacity monitoring.

Useful metrics include:

- daily BUSD redemptions;
- cumulative redeemed amount;
- redemption queue or delay;
- BUSD converted into USDP;
- issuer liquidity and reserve disclosures.

### Market liquidity migration

A shrinking stablecoin changes venue liquidity.

Useful metrics include:

- BUSD trading volume by venue;
- BUSD pair delistings or conversion deadlines;
- stablecoin pool BUSD share;
- slippage for BUSD-to-USDT, BUSD-to-USDC, and BUSD-to-DAI exits;
- collateral systems still accepting BUSD.

### Regulatory and relationship signals

Stablecoin market health includes off-chain regulatory control points.

Useful metrics include:

- regulator orders and consumer notices;
- issuer statements about partner relationships;
- exam or oversight findings;
- public legal risk updates;
- changes in approved chain or token scope.

The same fields are summarized in [busd-paxos-mint-halt-signals.csv](busd-paxos-mint-halt-signals.csv) for dataset-based review.

| Signal                 | Observation                                                         | Market-health interpretation                                       |
| ---------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------ |
| Mint halt              | Paxos said it would stop issuing new BUSD on February 21, 2023      | Minting status is a core stablecoin liquidity signal               |
| NYDFS order            | NYDFS ordered Paxos to cease minting Paxos-issued BUSD              | Regulatory action can change stablecoin market structure quickly   |
| Redemption path        | Paxos said customers could redeem BUSD or convert it to USDP        | Redemption options determine whether a supply wind-down is orderly |
| One-month redemption   | Paxos reported $7.9 billion of BUSD redemptions in one month        | Redemption velocity should be tracked after issuer shocks          |
| Relationship oversight | NYDFS cited unresolved oversight issues involving Paxos and Binance | Brand and issuer dependencies are stablecoin risk factors          |

## Timeline

- **February 13, 2023:** Paxos announced that it would stop minting new BUSD and end its relationship with Binance for the branded stablecoin.
- **February 13, 2023:** NYDFS published a consumer notice explaining that it had ordered Paxos to cease minting Paxos-issued BUSD.
- **February 21, 2023:** Paxos' announced halt on new BUSD issuance took effect.
- **March 2023:** Paxos reported that it had redeemed $7.9 billion of BUSD in one month without market disruption.

## Market Health Lessons

BUSD's mint halt shows that stablecoin health is not only a question of whether reserves match supply. A stablecoin can be fully backed and still become structurally impaired if minting ends and the token enters a redemption-only lifecycle.

For Market Health, protocols should track stablecoin mint status, issuer partnerships, regulator notices, redemption velocity, and liquidity migration. A shrinking stablecoin can remain redeemable while becoming less suitable as trading-pair inventory, lending collateral, or AMM liquidity.
