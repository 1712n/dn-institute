---
title: "Blizz Finance LUNA oracle-pause lending drain"
date: "2022-05-13"
description: "Blizz Finance was drained after a paused LUNA price feed left the lending market valuing collapsing collateral far above executable market prices."
entities:
  - Blizz Finance
  - LUNA
  - Chainlink
  - Avalanche
---

Blizz Finance, an Avalanche lending protocol, was drained during the May 2022
Terra collapse after its LUNA collateral market continued to use the last
Chainlink price-feed value while the external LUNA market kept falling. The
incident is a useful market-health case because the loss did not require a
manipulated AMM pool or a broken transfer function. The exploitable signal was a
paused oracle feed whose last value remained actionable inside a lending market.

Contemporaneous reports captured Blizz's public explanation that Chainlink had
paused the LUNA oracle, leaving LUNA worth 0.10 dollars according to the oracle
while attackers deposited large amounts of LUNA and borrowed the available
collateral. The same reports noted that Blizz was drained before the team could
pause the affected market because of a timelock. Galaxy's later Chainlink
research summarizes the same pattern as a LUNA oracle-pause case where Blizz
continued using a stale 0.10 dollar price. Halborn grouped Blizz with Venus
Protocol as a May 2022 LUNA price-discrepancy exploit and estimated Blizz's loss
at about 8.28 million dollars. DefiLlama's Blizz Finance history shows protocol
liquidity falling from about 9.6 million dollars on May 11 to about 8.3 million
dollars on May 12 and zero on May 13.

## Incident metrics

| Signal             | Observation                                                                      | Market-health interpretation                                                                             |
| ------------------ | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Oracle state       | LUNA feed was paused while Blizz still valued collateral at 0.10 dollars         | The lending market kept accepting a last-known oracle value after external market conditions had changed |
| Market condition   | LUNA was in an extreme collapse during the Terra failure                         | A volatile collateral asset required a liveness and divergence check, not only a latest-answer read      |
| Exploitable action | Attackers deposited large amounts of LUNA and borrowed available lendable assets | The stale quote turned depreciated collateral into a higher internal borrowing limit                     |
| Pause blocker      | Reports said Blizz could not pause before the drain because of a timelock        | Emergency controls were slower than the pace of oracle-driven borrowing pressure                         |
| Loss estimate      | Halborn estimated Blizz Finance likely lost about 8.28 million dollars           | The stale-oracle exposure was large enough to deplete the protocol                                       |
| Liquidity path     | DefiLlama shows Blizz Finance liquidity dropping to zero on May 13, 2022         | The exploit became visible as a complete lending-liquidity exit                                          |

The companion `blizz-luna-oracle-market-signals.csv` file separates the TVL,
oracle, loss-estimate, and operational signals for reuse in dashboards.

## Manipulation path

The core loop was:

1. LUNA's external market price kept falling during the Terra collapse.
2. The Chainlink LUNA feed stopped updating at its minimum circuit-breaker
   value.
3. Blizz Finance continued to treat the last oracle value as usable collateral
   pricing.
4. Attackers deposited LUNA at that internal value and borrowed assets whose
   market value was not similarly impaired.

That loop converts oracle liveness risk into market abuse. The attacker's edge
was not secret information; it was a public mismatch between a lending protocol
that accepted a stale 0.10 dollar LUNA quote and external markets where LUNA's
liquidation value had collapsed below that level. A market-health system should
therefore treat a feed pause as a separate risk state from a low-but-live price.

## Detection controls

Lending protocols should monitor at least three oracle health dimensions before
allowing collateral-backed borrowing:

- **Freshness:** reject or haircut collateral if the feed timestamp is older
  than the market's expected update interval during high volatility.
- **Circuit-breaker state:** treat minimum-answer or maximum-answer boundaries
  as emergency states, not as normal market prices.
- **Cross-market divergence:** compare oracle value with executable DEX/CEX
  prices and halt new borrows when divergence exceeds a preset threshold.

The Blizz incident shows why relying only on a reputable oracle network is not
enough. The consuming protocol still needs local rules for stale answers,
minimum-answer floors, and collateral-specific exposure caps. Aave forks and
other lending-market templates should surface these as first-class risk
parameters because copy-pasted oracle readers can inherit assumptions that are
reasonable in ordinary markets and dangerous during a collapse.

## Lessons for market health

Paused price feeds are market-health events. They should be rendered in
dashboards with the same urgency as a large trade-size anomaly, oracle-vs-spot
divergence, or liquidation cascade. A lending market that cannot distinguish
"the asset is worth 0.10 dollars" from "the feed stopped updating at 0.10
dollars" can continue creating solvency from a price that no longer exists.

For surveillance, the useful alert is the combination of a last-known oracle
answer, a large external price move, and rising borrow demand against the
affected collateral. Once those conditions appear together, the safer default is
to pause new borrows, reduce collateral factors, or set the collateral supply
cap to zero until the feed is live and the price is validated against external
markets again.

## References

- [CryptoNews: Blizz Finance depleted after LUNA feeds pause](https://cryptonews.net/news/altcoins/6473559/)
- [crypto.news: Terra LUNA fiasco affects Blizz Finance and Venus Protocol](https://crypto.news/terra-luna-defi-blizz-financend-venus-protocol/)
- [Galaxy: Chainlink oracle and price-feed risk cases](https://www.galaxy.com/insights/research/chainlink-oracle-ccip-price-feeds)
- [Halborn: Explained: The Luna price dip exploits](https://www.halborn.com/blog/post/explained-the-luna-price-dip-exploits-may-2022)
- [DefiLlama Blizz Finance protocol data](https://defillama.com/protocol/blizz-finance)
