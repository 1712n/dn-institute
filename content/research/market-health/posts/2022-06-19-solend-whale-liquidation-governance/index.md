---
title: "Solend Whale Liquidation Governance Stress"
date: 2022-06-19
entities:
  - Solend
  - Solana
  - SOL
  - USDC
  - USDT
---

## Summary

On June 19-21, 2022, Solend faced a market-health crisis around one very large borrowing account. [CoinDesk reported](https://www.coindesk.com/tech/2022/06/19/solana-defi-platform-votes-to-control-whale-account-in-bid-to-avoid-liquidation-chaos) that Solend users voted on a proposal to give Solend Labs emergency authority over the account so the position could be liquidated over the counter instead of through normal on-chain liquidation.

[Decrypt summarized](https://decrypt.co/103489/solend-whale-108m-loan-nearly-crashed-solana) that the account had borrowed about $108 million in USDC and USDT against a very large SOL deposit, creating liquidation risk that could have strained Solend's SOL market. [The Crypto Times reported](https://www.cryptotimes.io/2022/06/20/solanas-defi-platform-invalidates-whale-account-takeover-proposal/) that a later governance proposal invalidated the emergency takeover plan after user backlash.

The core market-health issue was not a smart-contract theft. It was a concentration and liquidation-design problem: one account's collateral and borrow size were large enough to force the protocol to choose between normal liquidation mechanics, emergency governance intervention, and user trust in account-level sovereignty.

## Manipulation Analysis

The first stress vector was collateral concentration. A lending market can appear solvent in aggregate while one whale account dominates liquidation risk. If that account moves toward liquidation, market depth and oracle prices matter more than headline total value locked.

The second vector was liquidation venue mismatch. On-chain liquidation works best when collateral can be absorbed by liquidators and surrounding markets. In the Solend episode, public reporting focused on the risk that a large SOL liquidation could overwhelm market liquidity and create bad debt or network congestion.

The third vector was governance speed. SLND1 and the follow-up proposal showed how emergency governance can become part of market structure. Fast votes may reduce short-term risk, but they also create governance capture and legitimacy questions if one voter or a small group can decide emergency account controls.

The fourth vector was user-exit pressure. Once users see a protocol considering emergency intervention around one account, the market-health question expands from liquidation math to confidence in withdrawals, borrow caps, and future governance boundaries.

## Metrics Used

### Whale account concentration

The primary signal is whether one account can dominate liquidation outcomes for a whole lending market.

Useful metrics include:

- largest borrower share of total borrows;
- largest collateral depositor share of total supplied collateral;
- borrow concentration by asset;
- collateral concentration by asset;
- distance between current collateral value and liquidation threshold.

### Liquidation capacity

Normal liquidation mechanics need to be compared against available market depth.

Useful metrics include:

- liquidation size at each price threshold;
- spot depth for SOL within 2%, 5%, and 10% of mid price;
- expected slippage for full liquidation;
- protocol bad-debt estimate under stressed execution;
- liquidator wallet capacity and realized liquidation pace.

### Governance intervention risk

Emergency governance can be a market-health risk when it changes user account assumptions.

Useful metrics include:

- proposal voting period length;
- turnout concentration by voter;
- share of voting power controlled by the largest voter;
- time between proposal creation and execution;
- whether the proposal grants account-specific emergency authority.

### Confidence and withdrawal pressure

The incident also affected user confidence in the lending venue.

Useful metrics include:

- supply withdrawals after proposal publication;
- stablecoin utilization in Solend markets;
- borrow-rate changes during the event;
- change in available USDC and USDT liquidity;
- social and governance sentiment around account control.

The same fields are summarized in [solend-whale-liquidation-signals.csv](solend-whale-liquidation-signals.csv) for dataset-based review.

| Signal                | Observation                                                   | Market-health interpretation                                      |
| --------------------- | ------------------------------------------------------------- | ----------------------------------------------------------------- |
| Whale borrow exposure | Reporting described about $108 million borrowed against SOL   | One account can dominate protocol-level liquidation risk          |
| Liquidation threshold | Public coverage focused on SOL price levels near liquidation  | Collateral depth should be tracked against specific price bands   |
| Emergency governance  | SLND1 sought emergency authority over the account             | Governance controls can become market-structure risk              |
| Reversal vote         | A later vote invalidated the emergency takeover proposal      | Emergency actions need legitimacy and rollback monitoring         |
| Fund movement         | Follow-up reporting said the whale account began moving funds | Risk can be reduced by position migration before forced execution |

## Timeline

- **June 19, 2022:** Solend users voted on SLND1, an emergency proposal intended to mitigate liquidation risk from a large whale account.
- **June 20, 2022:** Public backlash followed the account-control plan, and a later proposal invalidated the emergency takeover approach.
- **June 21, 2022:** [The Crypto Times reported](https://www.cryptotimes.io/2022/06/21/solend-protocol-whale-account-starts-moving-funds/) that the whale account began moving funds, reducing immediate liquidation pressure.
- **After the reversal:** Solend's episode remained a useful case study in borrower concentration, liquidation depth, and governance authority under market stress.

## Market Health Lessons

Solend shows that lending protocols need dashboards that join account concentration, asset depth, oracle distance, liquidation mechanics, and governance powers. These should not be monitored as separate domains. A governance proposal can be a direct signal that normal market controls are no longer sufficient.

For Market Health, the practical lesson is to model the largest-account liquidation path before a price shock forces action. If a single borrower can push the protocol into emergency account controls, then the market already has a concentration problem even before liquidation begins.
