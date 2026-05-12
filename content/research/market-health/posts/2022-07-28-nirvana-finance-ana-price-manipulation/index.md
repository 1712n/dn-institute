---
title: "Nirvana Finance ANA Price Manipulation and Treasury Drain"
date: 2022-07-28
entities:
  - Nirvana Finance
  - ANA
  - NIRV
  - Solend
  - Solana
---

## Summary

The July 2022 Nirvana Finance incident is a compact example of a protocol-internal market being treated as a safe price surface when it was not. The attacker used flash-loan liquidity from Solend to move Nirvana's ANA pricing curve, bought ANA below the protocol's intended economic floor, immediately resold ANA to Nirvana at the inflated curve price, and drained nearly all of the protocol's external reserves.

Public reports and the later criminal case describe the same economic pattern:

- Nirvana Finance was a Solana protocol built around the ANA token and the NIRV algorithmic stablecoin.
- The attacker used a large USDC flash loan to manipulate the ANA buy/sell path inside Nirvana's own contracts.
- CertiK reports that the attacker moved ANA from about $8 to about $24 during the transaction path, then swapped the inflated ANA claim for about $3.49 million in USDT.
- CoinDesk reported a roughly $3.5 million loss, an ANA price decline of almost 80%, and a NIRV peg collapse to about 8 cents shortly after the attack.
- In April 2024, the U.S. Department of Justice said Shakeeb Ahmed was sentenced to three years in prison for the Nirvana attack and another decentralized-exchange attack.

For market-health analysis, the useful lesson is not only that a smart contract had an exploitable pricing path. It is that protocol reserves, stablecoin backing, and redemption capacity were all exposed to a price that could be moved and monetized within one atomic trading sequence.

## Market-health surface

Nirvana's relevant surface was the coupling between ANA's pricing mechanism and the reserves backing the protocol. ANA was not simply a freely traded market token whose price movement hurt outside holders. The manipulated price became a claim on Nirvana's own liquidity, and NIRV's peg depended on confidence that those reserves and the ANA mechanism remained solvent.

[CertiK's incident analysis](https://www.certik.com/blog/nirvana-finance-incident-analysis) describes the attack as a flash-loan transaction that forced inaccurate ANA pricing. The attacker borrowed from Solend, bought ANA through Nirvana's program, moved the ANA price upward, sold ANA back into Nirvana's treasury, repaid the flash loan, and moved proceeds through Wormhole.

[CoinDesk's contemporaneous report](https://www.coindesk.com/tech/2022/07/28/solana-defi-protocol-nirvana-drained-of-liquidity-after-flash-loan-exploit) captured the market impact: ANA fell almost 80%, and NIRV lost its dollar peg. That makes the incident different from a pure arbitrage loss. The protocol's internal pricing curve, treasury liquidity, and stablecoin market confidence moved together.

The later DOJ case helps classify the event. In its April 2024 sentencing release, the DOJ said Ahmed used a Nirvana smart-contract exploit to purchase cryptocurrency from Nirvana below the intended price and immediately resell it to Nirvana at a higher price. That description maps cleanly to a protocol-market manipulation event: the trade path was not an outside market quote but an internal automated market that became the counterparty to the attacker.

## Attack mechanics

The public attack flow is short enough to express as a market-health replay:

1. The attacker borrowed a large amount of USDC from Solend. CertiK reports a $10.25 million USDC flash loan.
2. The attacker used the borrowed funds to buy ANA from Nirvana and invoke the path CertiK describes as the `Buy 3` command.
3. The ANA price moved from about $8 to about $24 inside the manipulated transaction sequence, according to CertiK.
4. The attacker sold ANA back into Nirvana's treasury, receiving about $3.49 million in USDT and additional USDC proceeds.
5. The Solend flash loan was repaid, and the retained funds were bridged from Solana to Ethereum through Wormhole.
6. ANA and NIRV then traded down sharply as the protocol's reserve backing and redemption credibility collapsed.

The transaction pattern is a warning sign for any protocol that lets one internal curve determine both entry price and redemption value. A market-health monitor should treat "same-transaction curve movement plus treasury redemption" as a solvency signal, not only as a trade anomaly.

## Evidence table

| Signal                                                     | Source                                                                                                                                                                                                   | Market-health value                                                                 |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Estimated Nirvana loss around $3.5 million                 | [CoinDesk](https://www.coindesk.com/tech/2022/07/28/solana-defi-protocol-nirvana-drained-of-liquidity-after-flash-loan-exploit), [CertiK](https://www.certik.com/blog/nirvana-finance-incident-analysis) | Establishes the direct reserve-drain scale.                                         |
| $10.25 million USDC borrowed from Solend                   | [CertiK](https://www.certik.com/blog/nirvana-finance-incident-analysis)                                                                                                                                  | Shows the temporary capital used to move the protocol market.                       |
| ANA moved from about $8 to about $24 during the attack     | [CertiK](https://www.certik.com/blog/nirvana-finance-incident-analysis)                                                                                                                                  | Shows the internal price path was manipulable inside the flash-loan sequence.       |
| About $3.49 million USDT received from Nirvana's treasury  | [CertiK](https://www.certik.com/blog/nirvana-finance-incident-analysis)                                                                                                                                  | Links the price manipulation to reserve extraction.                                 |
| ANA fell almost 80%; NIRV fell to about 8 cents            | [CoinDesk](https://www.coindesk.com/tech/2022/07/28/solana-defi-protocol-nirvana-drained-of-liquidity-after-flash-loan-exploit)                                                                          | Shows downstream market confidence and peg impact after the treasury drain.         |
| DOJ later described the buy-low, sell-high Nirvana exploit | [DOJ sentencing release](https://www.justice.gov/usao-sdny/pr/former-security-engineer-sentenced-three-years-prison-hacking-two-decentralized)                                                           | Confirms the economic mechanism in a law-enforcement record rather than only media. |

## Replay packet

A useful replay packet should include `tx_hash`, `slot`, `attacker`, `flash_loan_source`, `flash_loan_asset`, `flash_loan_amount`, `nirvana_program`, `ana_buy_instruction`, `ana_sell_instruction`, `ana_amount_bought`, `ana_curve_price_before`, `ana_curve_price_after`, `treasury_usdt_before`, `treasury_usdt_after`, `treasury_usdc_before`, `treasury_usdc_after`, `nirv_market_price_before`, `nirv_market_price_after`, `ana_market_price_before`, `ana_market_price_after`, `wormhole_bridge_tx`, and `ethereum_recipient`.

The important joins are between the Solend flash-loan leg, the ANA curve movement, the Nirvana treasury outflow, and the post-event ANA/NIRV market prices. Looking at only the loan or only the token price misses the core invariant failure: a short-lived curve state was allowed to determine a treasury redemption.

## Detection controls

### Curve-reserve exposure cap

Internal pricing curves should have an explicit cap on how much reserve value can be redeemed after a same-transaction price move. A detector can compare:

- current redemption value unlocked by the curve;
- protocol treasury depth in USDC, USDT, and other external assets;
- executable outside-market depth for ANA;
- size of flash liquidity available in the same ecosystem.

If `redemption_value_after_trade / external_reserve_depth` jumps above a fixed threshold in one transaction, the protocol should pause redemptions or force a delayed settlement path. The control is especially important when the counterparty to the trade is the protocol treasury rather than a third-party pool.

### Flash-loan-funded round-trip detector

The exploit path had a clean round trip: borrow, buy ANA, move curve price, sell ANA, repay. A generic market-health detector should flag when the same signer or transaction:

- receives large temporary liquidity;
- buys from a protocol-controlled curve;
- sells back into the same protocol before the temporary liquidity is repaid;
- exits with protocol reserve assets rather than only price exposure.

This signal does not require proving intent. It marks a structural risk: one atomic path can convert temporary liquidity into permanent treasury loss.

### Stablecoin backing stress signal

Because NIRV depended on Nirvana's reserve health and ANA mechanism, the treasury drain immediately became a stablecoin market event. A useful response would monitor:

- NIRV price deviation from $1 after large ANA curve trades;
- treasury reserve coverage before and after ANA buy/sell bursts;
- ANA price jumps that are not matched by external-market liquidity;
- social or governance pause events following abnormal reserve outflows.

The CoinDesk-reported NIRV drop to about 8 cents shows why stablecoin monitors should include protocol-reserve events, not only exchange order-book prices.

### Delayed settlement for self-priced assets

Assets whose price is defined by the protocol itself should not be instantly redeemable for all available reserve assets after a sharp in-transaction repricing. Safer designs include:

- redemption cooldowns after large curve movements;
- per-block treasury outflow caps;
- time-weighted or external reference checks for curve-based redemption;
- separate limits for buy-side price movement and sell-side treasury redemption.

Those controls would have turned the Nirvana event from an atomic drain into an observable stress event that could be rate-limited before reserves were exhausted.

## Lessons

Nirvana shows that market-health systems need to model the protocol as a trading venue when the protocol itself quotes prices and pays redemptions. The most important price was not a centralized-exchange ANA quote. It was the transient internal curve state that allowed an attacker to convert flash-loan liquidity into a treasury claim.

For surveillance, the key invariant is simple: a protocol-controlled price should not allow one transaction to both create an extreme valuation and redeem that valuation against most of the protocol's reserves. When that invariant is violated, token price, stablecoin peg, and treasury solvency become one risk surface.

## References

- CertiK, [Nirvana Finance Incident Analysis](https://www.certik.com/blog/nirvana-finance-incident-analysis), July 29, 2022.
- CoinDesk, [Solana DeFi Protocol Nirvana Drained of Liquidity After Flash Loan Exploit](https://www.coindesk.com/tech/2022/07/28/solana-defi-protocol-nirvana-drained-of-liquidity-after-flash-loan-exploit), July 28, 2022.
- U.S. Department of Justice, [Former Security Engineer Sentenced To Three Years In Prison For Hacking Two Decentralized Cryptocurrency Exchanges](https://www.justice.gov/usao-sdny/pr/former-security-engineer-sentenced-three-years-prison-hacking-two-decentralized), April 12, 2024.
- U.S. Department of Justice, [Former Security Engineer For International Technology Company Pleads Guilty To Hacking Two Decentralized Cryptocurrency Exchanges](https://www.justice.gov/usao-sdny/pr/former-security-engineer-international-technology-company-pleads-guilty-hacking-two), December 14, 2023.
