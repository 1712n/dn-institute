---
title: "Aave V2 CRV Borrow-and-Sell Squeeze"
date: 2022-11-22
entities:
  - Aave
  - Curve
  - CRV
  - USDC
  - OKX
---

## Summary

1. Aave V2's CRV market showed how a lending protocol can turn a concentrated borrow-and-sell campaign into protocol-level bad debt when borrowable supply is large relative to spot and liquidation liquidity.
2. Aave governance recorded that the 0x57e0 account deposited $38.9 million USDC on November 13, borrowed roughly 17 million CRV from November 13 to November 21, then added about $24 million more USDC and borrowed 55 million CRV on November 22.
3. The CRV spot price fell from about $0.61 to $0.4096, then rebounded sharply as Curve published crvUSD/LLAMMA material and liquidation demand began to buy CRV back into a thin market.
4. Aave governance recorded about $63 million USDC liquidated and about $1.7 million of bad debt. Blockworks separately reported 385 mini-liquidation transactions over about 50 minutes and 2.64 million CRV of excess debt.
5. The incident was not only a failed short. It was a market-health failure mode: one visible account, one thin borrow market, one large opposing CRV supplier, delayed governance controls, and liquidation flow that became a forced market order.

The companion file [`aave-crv-event-ledger.csv`](aave-crv-event-ledger.csv) records the source-linked evidence points used below. The SVG chart is a compact reconstruction from those public data points rather than exchange tick data.

{{< figure src="aave-crv-stress-path.svg" alt="Aave CRV stress path chart" caption="Selected public evidence points from the November 2022 Aave V2 CRV short and liquidation cycle." loading="lazy" >}}

## Why the market became fragile

CRV was an especially fragile lending asset in November 2022 because much of the token's economic supply was not freely available on short notice. Aave governance later summarized the market as a long-tail-asset risk case, and the sequence shows why that label mattered.

The 0x57e0 account started with stable collateral and repeatedly borrowed CRV. Aave governance recorded a $38.9 million USDC deposit on November 13. Over the next eight days, the account borrowed about 17 million CRV and sold through 1inch and centralized exchanges while CRV fell from $0.61 to as low as $0.41.

That first phase created two surveillance signals:

1. Borrowed CRV was leaving the lending market rather than being held for ordinary hedging or liquidity.
2. The borrow account was large enough that a price rebound could turn liquidation into a market-impact event.

The second phase was sharper. On November 22, Aave governance recorded four additional deposits totaling about $24 million USDC, a 55 million CRV borrow valued around $36 million, a 30 million CRV transfer to centralized exchanges, and additional 1inch swaps. The same governance recap cited $0.4096 as the local price low.

This is the useful market-health distinction: price pressure and protocol solvency were coupled. The borrower did not need to break Aave's code. The position only needed to be large enough that liquidation had to buy back more CRV than the market could absorb smoothly.

## Concentration around opposing accounts

The event also depended on visible concentration on the other side. Aave governance cited a CRV supplier with 174 million CRV, worth about $110 million, in the CRV liquidity pool and representing 27% of circulating supply. ChainCatcher/Foresight News reported that the same 0x7a16 address supplied 41 million CRV on November 20, then redeemed 45 million CRV later that day.

The 0x7a16 account does not need to be treated as manipulative to matter. Its size made the market path reflexive:

1. A large CRV holder on Aave made liquidation thresholds easy to discuss and monitor.
2. The short account's sales pushed CRV down toward stress levels.
3. CRV's rebound turned the short account's own debt into the stressed position.
4. Liquidators had to source CRV while the market was already moving upward.

That combination is closer to a crowded position unwind than a normal lending-market liquidation.

## Liquidation as market impact

Aave governance recorded the first liquidation at 13:31 UTC on November 22 and said the USDC collateral position was fully liquidated within the day. It put the total liquidated USDC at approximately $63 million and the remaining protocol bad debt at about $1.7 million.

Blockworks reported a more granular liquidation path: 385 mini-liquidation transactions over about 50 minutes, leaving 2.64 million CRV of bad debt. ChainCatcher/Foresight News cited EigenPhi data showing more than $5.65 million liquidated in an eight-minute burst from 21:31 to 21:38 after CRV rebounded from around $0.40 to $0.64.

The number of liquidation transactions is important because it shows why the insolvency was a market-structure issue. Many small liquidations can still have one aggregate effect: forced CRV buying into limited liquidity. A liquidator that receives USDC collateral and must close CRV debt becomes a buyer, and all buyers compete with each other when the collateral is one-sided and the debt asset is thin.

## Indicators for surveillance teams

### Borrow-utilization concentration

- Alert when one account borrows a double-digit share of a long-tail market's available debt liquidity or increases debt by tens of millions of tokens over a few days.
- Escalate faster when the borrowed asset is a governance token with large locked, founder-held, or strategic positions that can make float smaller than headline supply.
- Compare the borrower's debt growth with protocol-wide utilization so analysts can distinguish ordinary demand from a position that can dominate the liquidation path.

### Debt-asset liquidity gap

- Check collateral value against executable depth in the debt asset, not only against oracle value. In this case, stablecoin collateral did not remove the need to buy CRV into limited liquidity.
- Stress-test whether liquidators could close the debt asset within an internal slippage limit during a rebound rather than assuming the collateral asset can be sold cleanly.
- Raise the liquidation buffer or tighten borrowing when debt-token depth falls while account-level debt keeps rising.

### Exchange-transfer amplification

- Escalate borrowed-token transfers to centralized exchanges when the flow reaches millions of tokens or a meaningful share of the market's available borrow liquidity.
- Track whether exchange inflows coincide with price declines, additional protocol borrowing, or rising utilization in the same debt asset.
- Treat large borrowed-supply transfers as a potential bridge between protocol debt and external spot-market pressure, even when the transfer itself is not proof of intent.

### Reflexive collateral narrative

- Flag public narratives around named large leveraged positions when the debt asset, collateral asset, and liquidation thresholds are easy for outside traders to model.
- Stress-test whether pressure on one visible position would force liquidators to trade the same thin asset in the opposite direction.
- Separate intent analysis from risk response: the surveillance alert should fire when the reflexive setup is visible, even before manipulation is proven.

### Governance-response latency

- Track open risk-forum discussions against market movement and require pre-defined emergency actions when utilization, account concentration, and exchange-transfer alerts stack together.
- Maintain response-time targets for parameter freezes, borrow caps, or liquidation-threshold changes in long-tail markets under active stress.
- Log whether governance remediation happens before liquidation stress, during liquidation, or only after bad debt appears; that timing is the operational control being tested.

## Remediation and residual lesson

Aave ultimately cleaned up the excess CRV debt through governance. In January 2023, an Aave governance update said the AIP-144 repayment contract acquired 2.7 million CRV and cleared the remaining excess debt in about 15 hours and roughly a dozen transactions.

That cleanup was successful, but it is also the lesson. The protocol needed treasury action and governance execution after liquidation because the market could not settle the position cleanly at the moment of stress.

For similar lending markets, the useful controls are operational:

1. Borrow caps that decline as utilization and external liquidity worsen.
2. Debt-asset liquidity checks, not only collateral-value checks.
3. Automatic alerts when borrowed assets leave the protocol for centralized exchanges.
4. Lower liquidation thresholds or frozen borrowing for long-tail assets during market-wide liquidity shocks.
5. Exposure dashboards that combine account-level borrow concentration, debt-token depth, and known large collateral positions.
6. Post-liquidation accounting that separates "bad price move" from "insufficient liquidation liquidity" so future parameter changes target the real failure.

## Why this belongs in a market manipulation wiki

The Aave CRV incident is useful because it sits between market manipulation and protocol risk. The short account's borrowed CRV sales were observable market pressure; the rebound and liquidations were the mechanical counterpressure. Both sides were amplified by protocol design.

A surveillance team would not need to prove intent to flag the event. The red flags were measurable before the final liquidation: concentrated borrowing, stressed long-tail liquidity, exchange transfers of borrowed supply, visible opposing collateral, and liquidation demand that could not be executed without moving the market.

## References

- Aave Governance, "Q4-2022 Risk-Off Measures", December 1, 2022: https://governance.aave.com/t/q4-2022-risk-off-measures/10898
- Aave Governance, "Discussion: Reducing Long Tail Asset Risk", November 22, 2022: https://governance.aave.com/t/discussion-reducing-long-tail-asset-risk/10748
- Aave Governance, "[ARFC] Repay Excess CRV Debt on Ethereum v2", January 2023 update: https://governance.aave.com/t/arfc-repay-excess-crv-debt-on-ethereum-v2/10955
- Blockworks, "Feature or Flaw? Aave Left With $1.7M in Bad Debt", November 22, 2022: https://blockworks.co/news/aave-curve-bad-debt
- ChainCatcher/Foresight News, "Review of the CRV Bull-Bear Battle: The Largest Short with $63 Million in Collateral Liquidated", November 23, 2022: https://www.chaincatcher.com/en/article/2083417
