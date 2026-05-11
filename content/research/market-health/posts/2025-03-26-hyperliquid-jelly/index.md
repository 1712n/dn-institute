---
title: "Hyperliquid's JELLYJELLY Incident: Perpetual Market Manipulation Against a Protocol Vault"
date: 2025-03-26
description: "A market-health case study of the JELLYJELLY manipulation incident on Hyperliquid, focusing on liquidation routing, HLP vault exposure, and depth-adjusted perp risk."
entities:
  - Hyperliquid
  - JELLYJELLY
  - HLP
  - HYPE
  - Binance
  - OKX
---

## Summary

1. The March 2025 JELLYJELLY incident on Hyperliquid was not a typical exchange hack. It was a market-structure stress test in which leveraged perpetual positions, thin spot liquidity, and protocol-owned liquidation exposure interacted in a way that could turn a small token into a large venue-level liability.
2. Public postmortems describe a strategy built around concentrated accounts: large JELLYJELLY short exposure, offsetting long exposure, and forced liquidation that transferred risk to Hyperliquid's liquidity provider vault, HLP.
3. The signal quality was high before governance intervention: outsized open interest versus market depth, rapid spot price expansion, cross-venue listing pressure, a liquidation path that made HLP the counterparty, and a governance vote to delist the market.
4. The event is useful for market-health monitoring because it connects trade-level indicators to venue solvency indicators. A token can look locally small while still threatening an exchange vault if leverage, liquidation mechanics, and oracle sensitivity are misaligned.
5. The strongest practical controls are not only better liquidation thresholds. Venues should track open-interest-to-depth ratios, account concentration, vault-inherited position limits, cross-venue price divergence, and emergency-settlement governance events as one combined risk surface.

## Incident overview

Hyperliquid listed perpetual markets through an on-chain order book design where positions can be liquidated into a protocol liquidity provider vault. In ordinary market conditions, this creates a venue-native backstop for liquidations. In the JELLYJELLY event, that design became the target.

Several independent writeups describe the same core pattern: the attacker opened large JELLYJELLY positions, forced liquidation on a short leg, and left HLP holding a short position while spot and perpetual prices moved sharply higher. Halborn's incident review reported that the actor used several wallets and that JELLYJELLY moved hundreds of percent during the attack window. Other market reports described the HLP vault facing approximately eight-figure unrealized losses before Hyperliquid validators voted to delist and settle the market.

The public numbers are directionally consistent even when they differ in final PnL accounting. Reports tied the setup to a short of roughly several million dollars and offsetting long positions, followed by a rapid token move that made the inherited HLP short dangerous. This is enough to frame the event as a surveillance problem: the important ratio was not token market capitalization in isolation, but concentrated perp exposure versus usable depth and the vault's ability to unwind.

The minimum preventive rule would have been a depth-adjusted margin gate. Before accepting additional JELLYJELLY exposure, the venue could estimate the larger of (a) expected liquidation slippage if the position had to be auctioned into visible depth and (b) the mark-to-market loss from a stress move equal to the token's recent intraday range. If that stress loss exceeded the user's posted margin plus a vault-safe liquidation buffer, the position should have been rejected or forced to reduce. In simplified terms:

```text
required_margin >= max(depth_slippage_loss, stress_price_move_loss) + vault_transfer_buffer
```

The attack became systemic because the residual loss was not bounded to the initiating account. Once liquidation routed the short to HLP, the relevant comparison changed from "can this trader survive?" to "can a shared vault absorb and exit this token without becoming the market?" That is a stricter standard than ordinary user margining and should be measured before liquidations occur.

The market was later delisted by validator vote. Hyperliquid's own documentation describes delisting as a validator-governed process where positions are settled and open orders are cancelled. Media and security reports said the JELLYJELLY response also involved an emergency settlement price decision. That matters because the response was not only an exchange operations decision; it was a governance-controlled market-structure intervention.

The event also arrived just after another Hyperliquid liquidity stress episode. A large ETH long liquidation had reportedly produced a multi-million-dollar HLP loss days earlier. JELLYJELLY therefore exposed a repeated stress point: concentrated positions can convert liquidation mechanics into protocol-level balance-sheet risk.

## Quantitative stress framing

The JELLYJELLY incident is useful because the public numbers are large enough to create a practical risk desk checklist even without full private order book data. Reports vary on exact position accounting, but the common anchors are consistent: a JELLY short in the low single-digit millions of dollars, a token market capitalization in the tens of millions, a several-hundred-percent price move, and a protocol vault that could have inherited an eight-figure loss.

| Input                               | Publicly reported range or anchor                          | Market-health interpretation                                                                  |
| ----------------------------------- | ---------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Attacker short position             | Roughly $4.1 million to $6 million                         | A single account cluster could create a venue-level risk event in a low-cap perp market.      |
| JELLY market capitalization context | Roughly $10 million to $25 million in public reports       | The short was not small relative to the token's economic float or attention-driven liquidity. |
| JELLY price move                    | About 385% to 429% during the attack window                | Stress moves should be calibrated to intraday realized ranges, not normal volatility.         |
| Potential HLP loss                  | About $12 million to $13 million in several reports        | The inherited position could become material even if the token itself looked niche.           |
| HLP vault size context              | About $220 million to $230 million in public reporting     | A $12 million loss would be roughly 5% of the vault, before considering confidence effects.   |
| Prior March 2025 HLP stress         | About $4 million loss from a large ETH liquidation episode | Repeated losses suggest a structural liquidation-routing weakness, not an isolated oddity.    |

Those anchors imply three risk ratios that should have been watched together:

```text
position_to_market_cap = inherited_or_liquidatable_position / token_market_cap
vault_loss_at_risk = stressed_unwind_loss / vault_equity
repeat_stress_load = recent_vault_losses / vault_equity
```

Using only the public ranges, a $4.1 million short against a $25 million token market cap is already a 16.4% position-to-market-cap ratio. A $6 million short against a $10 million market cap is a 60% ratio. Both values are too high for a market where the backstop vault can inherit the position. Even if the true effective float was higher than the headline market cap estimate, the risk gate should compare the position to executable depth, which would usually be smaller than market capitalization.

The vault-loss-at-risk ratio tells the same story from the venue side. A $12 million potential loss against a $230 million HLP vault is about 5.2% of vault equity; against a $220 million vault it is about 5.5%. Adding the earlier reported $4 million ETH liquidation stress would bring recent March stress to roughly $16 million, or about 7.0% to 7.3% of a $220 million-$230 million vault. This does not mean HLP was insolvent. It means the liquidation engine was able to route concentrated trader risk into a shared pool quickly enough that governance had to intervene.

The emergency settlement price makes the monitoring lesson sharper. Halborn reports that Hyperliquid settled the market around $0.0095 rather than the much higher displayed JELLY price near the intervention window. That gap is evidence of an oracle and settlement problem, not merely a trader-level liquidation. When the fair settlement price has to be chosen manually after the fact, the automated system has already lost the ability to express a reliable executable exit price.

An ex ante rule can be simple: if a single cluster's position is greater than 10% of the token's market capitalization, greater than 3x two-percent executable depth, or can create a vault loss above 1% of vault equity under an observed intraday price move, the market should enter reduce-only mode until depth normalizes. JELLYJELLY appears to have crossed at least the position-size and vault-loss criteria under conservative public assumptions.

## Timeline and observable signals

| Date            | Event                                                                                           | Market-health signal                                                                                                          |
| --------------- | ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| March 2025      | JELLYJELLY was a comparatively small and thinly traded token before the event.                  | Low depth makes the perp market easier to move with spot buys or venue-to-venue price pressure.                               |
| March 26, 2025  | Public reports describe concentrated JELLYJELLY short and long exposure across related wallets. | Account concentration and offsetting exposures are red flags when liquidation routes risk to a venue-owned vault.             |
| March 26, 2025  | The short leg was liquidated, transferring a large short position to HLP.                       | Liquidation beneficiary analysis should flag when the backstop vault inherits a position larger than normal depth can absorb. |
| March 26, 2025  | JELLYJELLY's price moved sharply higher while HLP carried the short.                            | Open-interest-to-depth and price-impact ratios become more informative than nominal market capitalization.                    |
| March 26, 2025  | Hyperliquid validators voted to delist the market and settle it.                                | Emergency governance settlement is a late-stage market-health signal, similar to a circuit breaker.                           |
| After delisting | Hyperliquid said most affected users would be reimbursed, according to media reports.           | User reimbursement reduces direct customer harm but does not remove the need for ex ante manipulation controls.               |

## Manipulation pattern

The incident can be viewed as a three-part manipulation pattern rather than a single exploit.

First, the attacker appears to have chosen a token where a meaningful price move could be created with limited capital. Market surveillance should treat a token's market capitalization as secondary to live order book depth, especially when a leveraged perp market exists. If one percent depth is tiny compared with open interest, the market can become a lever on the venue's own liquidation system.

Second, the attacker used liquidation routing as part of the strategy. A liquidation engine is supposed to reduce counterparty risk by transferring or closing unhealthy positions. But if a protocol vault accepts the residual position, then a manipulator can intentionally manufacture a position that the vault would not have chosen at that size or at that entry price.

Third, the attacker benefited from reflexive price pressure. Once HLP was short and the token's price was rising, every further price increase threatened the vault. This created a feedback loop: higher price, larger HLP mark-to-market loss, stronger pressure for emergency action, and greater public attention on the token.

That combination makes the event different from ordinary pump-and-dump activity. A pump-and-dump normally extracts value from later retail buyers. The JELLYJELLY incident targeted a venue mechanism: forced counterparty assignment and emergency settlement.

## Metrics used

### Open interest versus available depth

The first risk metric is the ratio between perp open interest and spot/perp market depth. If a position can be many times larger than the available liquidity near the current price, liquidation becomes uncertain even before price manipulation begins.

For small tokens, a practical indicator is:

```text
position_pressure = absolute_open_interest / one_percent_order_book_depth
```

The numerator should be calculated after grouping related accounts where possible. The denominator should include live depth on the venue plus reliable external spot liquidity only if that liquidity is actually usable by the oracle or liquidation engine.

When this ratio rises above a defined threshold, the venue should reduce max leverage, tighten position limits, widen margin requirements, or pause new risk-increasing positions. Waiting until the liquidation begins is too late; the harmful trade is the creation of a vault-sized position in a thin market.

### Vault-inherited position exposure

HLP's role makes the second metric venue-specific:

```text
vault_inherited_exposure = position_size_transferred_to_vault / vault_equity
```

The more useful version is not only equity-based. It should also compare the inherited position with the token's market depth and recent realized volume. A vault can appear solvent in aggregate while still being unable to exit a particular token without moving the market against itself.

For surveillance, inherited exposure should trigger separate alerts from normal trader open interest. A trader's losing position is not the same as a backstop vault's losing position. The first is a user risk. The second can become a venue solvency and governance risk.

### Account concentration and offsetting legs

Public postmortems describe multiple wallets participating in the setup. A venue should monitor whether several accounts are economically linked by timing, funding paths, or mirrored exposures.

Useful warning signs include:

- One cluster opening a large short while related accounts hold long exposure or spot inventory.
- Position changes arriving in a short time window before a thin market price move.
- Repeated transfer of liquidation risk from the same account cluster to the protocol backstop.
- New accounts that rapidly become a dominant share of a token's open interest.

These signals do not prove manipulation by themselves. They do, however, justify higher margin requirements and manual risk review before liquidation transfers exposure to a shared vault.

### Cross-venue price and listing pressure

The incident also had cross-venue dynamics. Media coverage reported that major venues announced or supported JELLYJELLY derivatives around the same window. That made external pricing and attention part of the risk surface.

Cross-venue surveillance should compare:

- Hyperliquid mark price versus external spot prices.
- External perp funding and premium versus Hyperliquid funding and premium.
- Listing announcements and sudden volume spikes on other exchanges.
- Whether oracle inputs are robust enough when the external market is shallow or newly listed.

The key question is not whether other exchanges caused the move. The question is whether the venue's risk engine assumed more external liquidity and price stability than actually existed.

### Governance intervention as a late indicator

Validator delisting and settlement worked as a circuit breaker. It limited further mark-to-market damage but also confirmed that automatic market controls had already failed to contain the position.

For market-health reporting, an emergency delisting should be treated like an exchange outage or withdrawal freeze: it is a severe late-stage signal. It may be the least harmful remaining option, but it should not be the first effective defense.

## Why this matters for market manipulation analysis

Traditional wash trading metrics focus on trade size distributions, repeated round lots, Benford deviations, and stable buy/sell ratios. Those are still relevant. JELLYJELLY adds another category: liquidation-route manipulation.

The economic victim is not necessarily the last buyer. The victim can be a shared venue vault or insurance fund. This changes the right surveillance questions:

- Who becomes the counterparty after liquidation?
- Is the backstop allowed to inherit concentrated exposure in a token with shallow depth?
- Does the market allow a trader to create risk larger than the venue can unwind?
- Are external price references liquid enough to support liquidation and settlement?
- Can governance intervention be anticipated by measurable risk thresholds?

If these questions are not monitored together, a venue can pass ordinary trade-count and price-change checks while still accumulating a dangerous structural exposure.

## Suggested monitoring rules

1. **Depth-adjusted open interest cap:** reduce max position size when open interest exceeds a multiple of one percent depth across reliable venues.
2. **Backstop inheritance cap:** prevent the protocol vault from inheriting a position above a per-token percentage of vault equity, recent volume, or live order book depth.
3. **Account-cluster risk scoring:** group accounts by timing, funding, and mirrored exposure before calculating concentration limits.
4. **Liquidation path simulation:** simulate worst-case vault exposure before accepting new positions in thin markets.
5. **External listing watch:** raise margin requirements around new CEX listings, perp listings, or sudden external volume changes.
6. **Emergency-governance reporting:** publish a post-event market health report whenever validators delist or manually settle a market.

## Data limitations

This article relies on public postmortems, media reporting, and protocol documentation rather than a full private order book reconstruction. Exact account ownership, realized PnL, and liquidation engine state are not fully public. The analysis therefore treats the incident as a market-structure case study: the signal set is strong enough to design monitoring rules, but it should not be read as a legal attribution of identity or intent.

The most important missing dataset is a minute-by-minute combination of order book snapshots, funding rate histories, account-level open interest, margin state, oracle input timelines, liquidator action logs, HLP maker inventory changes, and on-chain vault position deltas. Even partial publication of these datasets would let future researchers reconstruct the liquidation threshold, estimate the slippage curve, and convert the monitoring rules above into a reproducible benchmark.

## References

- [Halborn: Explained - The Hyperliquid Hack, March 2025](https://www.halborn.com/blog/post/explained-the-hyperliquid-hack-march-2025)
- [Hyperliquid Docs: Delisting](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/delisting)
- [Hyperliquid Docs: Liquidations](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/liquidations)
- [Arkham: JELLYJELLY Exploit on Hyperliquid](https://info.arkm.com/research/jellyjelly-exploit-on-hyperliquid)
- [The Block: Hyperliquid delists JELLYJELLY memecoin amid whale manipulation fiasco](https://www.theblock.co/post/348314/hyperliquid-delists-jellyjelly-memecoin-amid-whale-manipulation-fiasco)
- [CoinDesk: HyperLiquid delists JELLY after vault squeezed in $13M tussle](https://www.coindesk.com/markets/2025/03/26/hyperliquid-delists-jellyjelly-after-vault-squeezed-in-usd13m-tussle)
- [Cointelegraph: Hyperliquid delists JELLY perps, citing suspicious activity](https://cointelegraph.com/news/hyperliquid-delists-jelly-perps-citing-suspicious-activity)
- [web3 is going just great: Hyperliquid suffers market manipulation attack](https://www.web3isgoinggreat.com/single/hyperliquid-manipulation)
