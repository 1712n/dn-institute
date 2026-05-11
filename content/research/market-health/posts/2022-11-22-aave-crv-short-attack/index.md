---
title: "Aave CRV Short Attack and Lending-Market Bad Debt"
date: "2022-11-22"
description: "A large CRV short position on Aave attempted to pressure Curve DAO Token markets, failed through liquidation, and still left Aave with excess CRV debt."
entities:
  - Aave
  - Curve DAO Token
  - CRV
  - Avraham Eisenberg
---

In November 2022, Aave faced a market-manipulation attempt built around borrowing and selling Curve DAO Token (CRV). Aave governance contributors later identified the relevant wallet as `0x57e04786e231af3343562c062e0d058f25dace9e`. The position reached a peak short exposure of roughly 92 million CRV, about $60 million at the time, using USDC as collateral.

The trade failed for the short seller, but it still created protocol-level damage. Llama and Gauntlet wrote that the user was fully liquidated and lost roughly $10 million through liquidations, while Aave accrued about $1.6 million of CRV bad debt. A later Aave proposal quantified the excess debt at approximately 2.66 million CRV, worth about $1.76 million at the proposal's reference price.

## Manipulation signal

This event was not a conventional exchange wash-trading episode. It was a lending-market manipulation attempt in which borrowed inventory was used to pressure the public price of a low-liquidity governance token. The attack surface was created by the connection between three markets:

1. Aave supplied borrowable CRV liquidity.
2. CRV could be sold on centralized and decentralized venues.
3. Aave liquidations and collateral accounting depended on the same market price the short seller was trying to pressure.

The market-health signal was the concentration and speed of borrow-driven sell pressure. Public reports and Aave governance posts describe tens of millions of CRV being borrowed, transferred, and sold. If the CRV price had continued falling, the trade could have created profitable external short exposure while shifting part of the liquidation cost to Aave suppliers and the DAO treasury.

| Indicator                        | Observed value                                                            | Market-health interpretation                                                    |
| -------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| Peak short exposure              | About 92 million CRV, roughly $60 million                                 | Borrowed inventory became large enough to stress the token's external liquidity |
| Initial borrow-and-transfer path | 40 million CRV, worth about $20 million, reported as sent to OKX          | Borrowed protocol liquidity was routed toward external price pressure           |
| Liquidation result               | User fully liquidated after CRV price rallied                             | Price defense and liquidations stopped the short seller from profiting          |
| Protocol loss                    | About $1.6 million bad debt initially reported by Aave contributors       | A failed manipulation attempt still externalized cost to the lending market     |
| Final debt sizing                | About 2.66 million CRV excess debt, valued near $1.76 million in the ARFC | Debt repayment required governance and treasury action                          |

## Failure chain

The position was possible because Aave V2 let users borrow large quantities of volatile, lower-liquidity assets without the tighter controls later used in Aave V3, such as borrow caps, supply caps, isolation mode, and more granular risk controls. When a single wallet could borrow a large share of available CRV and then sell into outside markets, Aave's own CRV reserve became exposed to a feedback loop:

- borrowed CRV increased short inventory;
- external selling pushed on CRV's market price;
- lower CRV prices changed liquidation incentives and reserve solvency;
- liquidation slippage left residual bad debt when the position was closed.

The attacker did not need to compromise Aave contracts. The pressure came from using normal protocol functions at a size that exceeded the market's ability to absorb the trade cleanly.

## Governance response

After the liquidation, Llama and Gauntlet proposed repaying the CRV excess debt using Gauntlet's insolvency refund and Aave treasury resources. Aave governance also considered wider risk-off changes. The community discussion noted that the affected CRV bad debt was isolated, but the incident still showed that lending markets can inherit manipulation risk from external spot liquidity.

Aave later moved to freeze multiple low-liquidity markets on Ethereum V2 out of caution. The risk proposal listed CRV alongside other assets such as YFI, ZRX, MANA, 1INCH, BAT, ENJ, GUSD, AMPL, RAI, USDP, LUSD, xSUSHI, DPI, renFIL, and MKR. The policy response shifted attention from single-market liquidation logic to the broader question of whether long-tail assets should remain borrowable without caps during volatile market conditions.

## Why this matters for market health

The Aave/CRV episode is a useful case study because the manipulation attempt was observable before and after liquidation. A monitoring system could flag the same pattern with a few practical metrics:

- borrow concentration by wallet relative to total available token liquidity;
- transfer of borrowed assets to centralized exchanges shortly after borrowing;
- sharp divergence between borrow growth and organic demand for the asset;
- liquidation slippage risk under stressed order-book depth;
- residual bad debt after a large liquidation cycle.

For DeFi lending venues, market health cannot be judged only by whether liquidations execute. In this case liquidations worked, but the protocol still accrued excess debt. The better signal is whether a large borrower can create a price-pressure loop that is profitable externally while leaving the protocol with tail losses internally.

## Source dataset

The supporting event timeline is included in `timeline.csv`. It records the date, reported metric, and source used for each key fact.

## References

- [Aave governance: Repay excess debt in CRV market](https://governance.aave.com/t/arc-repay-excess-debt-in-crv-market-for-aave-v2-eth/10779)
- [Aave governance: ARFC repay excess CRV debt](https://governance.aave.com/t/arfc-repay-excess-crv-debt-on-ethereum-v2/10955)
- [Aave governance: Risk parameter recommendations for Aave V2 ETH](https://governance.aave.com/t/arc-risk-parameter-recommendations-for-aave-v2-eth-2022-11-22/10757)
- [CoinDesk report on CRV borrow and liquidation](https://www.coindesk.com/markets/2022/11/22/mango-exploiter-gets-liquidated-after-roiling-aave-using-20m-of-borrowed-curve-tokens)
- [Heimbach, Schertenleib, and Wattenhofer: Short Squeeze in DeFi Lending Market](https://ideas.repec.org/p/arx/papers/2302.04068.html)
