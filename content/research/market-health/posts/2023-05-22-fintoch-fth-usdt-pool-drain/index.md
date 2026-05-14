---
title: "Fintoch FTH/USDT pool-drain market-health case"
date: "2023-05-22"
description: "Fintoch combined false institutional affiliation, unrealistic return promises, concentrated FTH inventory, and a final FTH/USDT sale that drained more than 31 million USDT from investors."
entities:
  - Fintoch
  - FTH
  - USDT
  - BNB Chain
  - Morgan Stanley
---

Fintoch collapsed on May 22, 2023 after the project accumulated investor USDT
in a BNB Chain fundraising contract and then drained the paired liquidity by
selling a large amount of FTH into the FTH/USDT pool. DN Institute records the
loss at 31,697,984 USDT, while the related rug-pull explainer records the final
pool-drain transaction at 31,666,317 USDT.

This is a useful market-health case because the final loss was not an isolated
website exit. The observable warning signs joined off-chain credibility claims
with on-chain token and liquidity structure: a fake Morgan Stanley affiliation,
a one percent daily return promise, regulator warning-list exposure,
concentrated FTH holdings, and a large stablecoin drain from a thin internal
market.

## Incident metrics

| Signal                  | Observation                                                                           | Market-health interpretation                                                      |
| ----------------------- | ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| Regulator warning       | MAS listed Fintoch on its investor alert list before the drain                        | Warning-list matches should be treated as venue and issuer risk inputs            |
| False affiliation       | Morgan Stanley published a notice rejecting any Fintoch affiliation                   | Unsupported institutional backing claims are high-priority credibility signals    |
| Return promise          | DN Institute records an advertised one percent daily return                           | Fixed high daily returns are incompatible with normal market-risk disclosure      |
| Loss amount             | DN Institute records 31,697,984 USDT stolen from investors                            | Loss scale shows the fundraising pool had become a material stablecoin exposure   |
| Final sale transaction  | The drain transaction exchanged FTH against USDT and removed about 31.7 million USDT  | Large issuer-side sells against project-held liquidity are immediate shock events |
| Concentrated token flow | The rug-pull explainer records 34,341 FTH moving to the scammer before the final sale | Privileged or concentrated token inventory can turn into direct pool-drain risk   |
| Fund movement afterward | DN Institute says funds were bridged to Ethereum and Tron after the BNB Chain drain   | Cross-chain movement is a post-event recovery and attribution signal              |

The companion `fintoch-fth-usdt-signals.csv` file records the warning,
credibility, return-promise, token-flow, loss, drain-transaction, and
post-drain movement signals for reuse.

## Manipulation path

The Fintoch pattern linked investor acquisition to a token-market exit:

1. The project presented itself as a peer-to-peer financial platform and
   claimed a Morgan Stanley relationship that Morgan Stanley later rejected.
2. It promoted a fixed daily return that created a strong user-acquisition
   signal but did not match a transparent source of market yield.
3. MAS added Fintoch to its investor alert list before the loss event.
4. Investor USDT accumulated inside the Fintoch STO contract on BNB Chain.
5. FTH token supply and FTH/USDT liquidity were structured so that insider
   token concentration could be sold into the pool.
6. The final transaction sold FTH and removed more than 31 million USDT,
   leaving investors exposed to a collapsed project token.
7. The drained funds were later bridged across chains, reducing the chance of
   fast recovery.

The market-health lesson is that a project-controlled token sale can behave
like a manipulated market even when there is no ordinary exchange order book.
When investor stablecoins are pooled against an issuer-controlled token, the
issuer's token inventory, transfer timing, pool depth, and final sell size are
the market.

## Detection controls

Fintoch points to controls that can be applied before the final drain:

- **Affiliation verification:** match public institutional backing claims
  against denials, warnings, and domain-controlled announcements.
- **Return-promise scoring:** flag fixed high-yield promises, especially when
  they are paired with token-sale or fundraising contracts.
- **Warning-list enrichment:** join issuer names, domains, and token symbols to
  regulator alert lists before allowing the asset to appear as normal market
  exposure.
- **Concentration monitoring:** track privileged transfers of issuer tokens to
  deployer, treasury, or newly active wallets near fundraising milestones.
- **Pool-drain thresholds:** alert when a single token sale can remove a large
  fraction of pooled stablecoin liquidity.
- **Cross-chain exit tracing:** separate the initial market shock from later
  bridge movements so recovery and attribution analysis do not obscure the
  original drain.

These controls are practical because they rely on visible statements,
regulatory lists, token transfers, and pool outflows. They do not require
knowing the scammers' identities before the event.

## Lessons for market health

Fintoch shows why market-health monitoring should cover fundraising pools and
project-native liquidity, not only centralized exchange trades. The same asset
can carry several risk layers at once: marketing claims that attract deposits,
issuer-side token concentration that enables price collapse, and stablecoin
liquidity that can be removed in one transaction.

The strongest signal bundle is an unsupported institutional claim, fixed daily
return promise, regulator warning, concentrated project-token transfer, and
large issuer-side sell against pooled USDT. When those signals appear together,
the project should be treated as a market-integrity risk before the final drain
is visible in loss reporting.

## References

- [DN Institute cyberattack incident: Fintoch](https://dn.institute/research/cyberattacks/incidents/2023-05-22-fintoch/)
- [Halborn: Explained - The Fintoch Rug Pull](https://www.halborn.com/blog/post/explained-the-fintoch-rug-pull-may-2023)
- [Morgan Stanley: Important notice regarding Fintoch](https://www.morganstanley.com/content/dam/msdotcom/global-offices/pdf/Indonesia/Indonesia_Fintoch_Important_Notice.pdf)
- [Monetary Authority of Singapore investor alert list search for Fintoch](https://www.mas.gov.sg/investor-alert-list?q=Fintoch)
- [BscScan: Fintoch drain transaction](https://bscscan.com/tx/0xa5e64161928ee40f6af02a32fc5c1fb9efa05cca6b91d88326279329b71c7ea2)
