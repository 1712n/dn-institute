---
title: "Mango MNGO Perpetual Oracle Manipulation"
description: "A Market Health case study on how thin MNGO spot markets, matched perpetual positions, and oracle-priced collateral let one trader borrow nearly all available Mango Markets liquidity."
date: 2022-10-11
tags:
  - Mango Markets
  - MNGO
  - Oracle manipulation
  - Perpetual futures
  - Solana
---

## Key points

1. Mango Markets shows a market-health failure mode where a thin spot market, a large self-matched perpetual position, and oracle-priced borrowing were connected tightly enough to turn short-lived price pressure into withdrawable collateral value.
2. The CFTC complaint says two Mango accounts were funded with $5 million USDC each, then used to create matched long and short positions of more than 400 million MNGO-USDC swaps at about $0.04.
3. During the manipulation window, large MNGO purchases on oracle exchanges moved reported MNGO prices from about $0.04 to as high as $0.91 on one exchange, while the Mango MNGO-USDC swap price rose to about $0.54.
4. The inflated long perpetual position rose from roughly $19 million to more than $200 million in marked value, enabling roughly $114 million to $116 million of borrowing and withdrawal from Mango's available liquidity.
5. The useful monitor is not "price up." It is the compound signal: same-actor matched open interest, thin external spot liquidity, oracle-source concentration, sudden collateral revaluation, and cross-asset borrowout before price persistence can be proven.

The companion file [`mango-mngo-oracle-signals.csv`](mango-mngo-oracle-signals.csv) records the source-linked evidence points used below. The chart reconstructs the market-control path from public reports rather than replaying every Solana trade.

{{< figure src="mango-mngo-oracle-path.svg" alt="Mango MNGO perpetual oracle manipulation control path" caption="Selected public evidence points from the October 2022 Mango Markets MNGO manipulation." loading="lazy" >}}

## The fragile market structure

Mango Markets combined spot trading, perpetual futures, margin, and borrowing inside one venue. That architecture made collateral value depend on market marks. For major assets, that dependency can be manageable when oracle inputs are deep and hard to move. For MNGO, the risk was different: the token was thin enough that concentrated buying could move the oracle sources quickly.

The CFTC described Mango's oracle as using prices from three external exchanges. That means the relevant market was not only Mango's own order book. A trader who could move the oracle-source markets could move the value of a Mango perpetual position, and that position could then affect borrowing capacity inside Mango.

The dangerous bridge was therefore:

1. build a large MNGO-USDC perpetual exposure on Mango,
2. move MNGO prices on the external oracle exchanges,
3. let the oracle mark the long perpetual at the inflated price,
4. borrow unrelated liquid assets against the mark, and
5. withdraw those assets before the MNGO price reverted.

In market-health terms, Mango converted a temporary external spot imbalance into internal credit. The protocol did not need a smart-contract authorization bug for this to become a liquidity drain.

## Matched exposure before the spot pump

The CFTC complaint says the trader created two anonymous Mango accounts and funded each with $5 million USDC. One account opened a leveraged long position of more than 400 million MNGO-USDC swaps at about $0.04, while the second account opened the matching short side.

That setup is important because the long account was the one whose marked value could become collateral. The short account's loss was bounded by its starting collateral, while the long account's artificial mark could scale with the oracle print.

Solidus Labs' order-book reconstruction gives the operational shape. It identifies a 483 million MNGO-PERP buy at 18:25 EST, followed by spot MNGO buying on Mango, AscendEX, and FTX during the next few minutes. DNI's incident timeline similarly anchors the Mango accounts at 10:19 PM UTC, the large MNGO-SOL perp order at 10:25 PM UTC, the external MNGO buying at 10:26 PM UTC, and the loan at 10:45 PM UTC.

The market-health issue was not merely that the position was large. It was large relative to MNGO's external liquidity and tied to borrowing in other assets. A surveillance system should treat that as one cross-venue event, not as separate spot, perpetual, and lending events.

## The oracle-window price shock

The CFTC complaint reports that MNGO traded around $0.04 between October 1 and October 10. During the incident window, one oracle exchange saw more than 1 million MNGO bought in about 30 minutes, versus historical volume averaging about 120,000 MNGO per hour. MNGO rose on that venue from about $0.04 to $0.45. The same complaint says simultaneous purchases moved the price to about $0.13 on another oracle exchange and about $0.91 on a third.

Mango's internal swap mark did not need to reach the highest external print. The CFTC says the MNGO-USDC swap price rose from about $0.04 to about $0.54. That was enough to revalue the long swap position from about $19 million to more than $200 million.

Solidus Labs frames the same window as a 10x to 30x price move relative to the previous day, with a peak of $0.91. That spread between venues is itself a signal. A market-health system should not only ask whether an oracle median or average is fresh. It should ask whether the input venues are being dominated by one account, whether the move is executable in size, and whether a dependent credit system is about to accept the mark.

## Borrowout as the loss event

Once the long perpetual position was marked higher, the trader used it as collateral. The CFTC complaint says the trader borrowed $114 million in USDC, USDT, and other digital assets, comprising all available lending liquidity on the platform. The SEC press release describes approximately $116 million withdrawn and says the transactions effectively drained all available Mango assets. DNI's incident page also records approximately $116 million lost and $67 million returned.

Those figures should be separated:

1. the artificial collateral value was above $200 million,
2. the borrowout was roughly $114 million to $116 million,
3. the negotiated return was about $67 million, and
4. the retained amount after the governance settlement was lower than the peak reported platform loss.

For market-health monitoring, the important point is timing. The borrowed assets left before the market could prove the new MNGO price was durable. After the purchases stopped, the CFTC complaint says MNGO quickly dropped to about $0.02, below the pre-manipulation level. The collateral mark therefore existed during the exact interval when Mango's lending system accepted it.

## Surveillance indicators

### Matched perpetual concentration

- Alert when one account opens a very large long position while another fresh account opens the matched short side in the same thin underlying asset.
- Combine the signal with account funding age, common funding sources, and size relative to normal market depth.
- Treat self-matched or closely timed offsetting exposure as higher risk when one side can become borrowable collateral.

### Oracle-source venue pressure

- Monitor the external venues that feed the oracle, not only the destination protocol.
- Compare the incident-window MNGO buy volume with historical hourly volume on each oracle source.
- Quarantine oracle updates when one trader's spot flow explains a large share of the input movement.

### Perpetual mark versus executable depth

- Compare the marked value of a perpetual position with the amount of spot liquidity that could unwind the underlying asset.
- Apply haircuts when a thin governance token produces a large unrealized gain without broad venue agreement.
- Prevent the unrealized gain from becoming borrowable collateral until the mark survives multiple independent price intervals.

### Cross-asset borrowout after a mark shock

- Escalate when one collateral mark shock is followed by borrowing across unrelated assets such as USDC, USDT, BTC, and ETH.
- Track reserve utilization in real time and pause new borrowing when available liquidity is being depleted by one account cluster.
- Require additional risk checks before allowing borrowed assets to leave the venue after a thin-token oracle shock.

## Controls that would have changed the outcome

1. A per-asset cap on how much unrealized MNGO perpetual profit could count toward borrowing capacity.
2. A stricter collateral haircut for thin governance-token derivatives whose oracle sources had shallow depth.
3. A velocity guard that delayed borrowability when MNGO moved several multiples inside one oracle window.
4. A cross-account wash-trade detector for matched long and short perpetual exposure.
5. A borrowout circuit breaker when one account cluster attempted to withdraw most available liquidity across unrelated assets.
6. An oracle-source surveillance layer that flagged concentrated spot buying on the exact venues feeding Mango's mark.

## Why this belongs in a market manipulation wiki

The Mango incident is useful because it connects market manipulation to credit-system design. The manipulated object was not only a spot token price. It was a spot token price that fed a perpetual mark, which fed collateral value, which fed borrowing across the platform's liquid reserves.

That chain is reusable. Any venue that accepts unrealized gains or thin-token marks as collateral should monitor whether the price move is externally executable, whether the trader is on both sides of the derivative exposure, and whether borrowable value is rising faster than market depth. The core market-health lesson is to bind collateral value to durable, executable liquidity rather than to a short-lived oracle print.

## References

- CFTC, "Commodity Futures Trading Commission v. Avraham Eisenberg", complaint filed January 9, 2023: https://www.cftc.gov/media/8046/enfeisenbergcomplaint010923/download
- SEC, "SEC Charges Avraham Eisenberg with Manipulating Mango Markets' Governance Token to Steal $116 Million of Crypto Assets", January 20, 2023: https://www.sec.gov/newsroom/press-releases/2023-13
- Solidus Labs, "The Mango Markets Exploit: An Order Book Analysis", October 2022: https://www.soliduslabs.com/post/mango-hack
- Distributed Networks Institute, "Mango Markets Exploited for $116 Million": https://dn.institute/research/cyberattacks/incidents/2022-10-11-mango-markets/
- CoinDesk, "How Market Manipulation Led to a $100M Exploit on Solana DeFi Exchange Mango", October 12, 2022: https://www.coindesk.com/markets/2022/10/12/how-market-manipulation-led-to-a-100m-exploit-on-solana-defi-exchange-mango/
