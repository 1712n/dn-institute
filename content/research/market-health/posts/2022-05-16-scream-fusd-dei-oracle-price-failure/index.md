---
title: "Scream's fUSD and DEI fixed-price collateral failure"
date: "2022-05-16"
description: "A Fantom lending market kept depegged stablecoins priced at one dollar, allowing borrowers to transform discounted fUSD and DEI collateral into protocol bad debt."
entities:
  - Scream
  - fUSD
  - DEI
  - Fantom
  - SCREAM
---

In May 2022, Scream, a Compound-style lending protocol on Fantom, showed how a
stablecoin depeg can become a market-manipulation channel when collateral
prices are fixed by policy rather than refreshed from executable markets.
During the post-Terra stablecoin stress, Fantom USD (fUSD) and DEI traded below
their dollar targets while Scream continued to value them at one dollar in its
lending markets. Users could therefore acquire or hold discounted fUSD and DEI,
deposit them as if they were worth par, and borrow other stablecoins against the
inflated collateral value.

The public loss estimates converged around 35 million dollars of bad debt.
CryptoSlate reported that Scream had hardcoded fUSD and DEI at one dollar, that
DEI traded as low as 0.52 dollars and fUSD as low as 0.69 dollars, and that
borrowers drained stablecoins such as FRAX, Fantom USDT, USDC, and MIM from the
protocol while posting the depegged assets as collateral. Crypto.news reported
the same 35 million dollar bad-debt estimate and noted that fUSD's Scream
deposit limit was set to infinity rather than zero. DefiLlama's Scream protocol
history shows total liquidity falling from 184.4 million dollars on May 13,
2022 to 98.3 million dollars on May 16, 65.8 million dollars on May 17, and
33.8 million dollars by May 20.

This was not a conventional smart-contract drain in which the attacker directly
breaks an invariant and transfers funds. The exploitable surface was the
market-health layer between an external traded price and an internal collateral
price. Once the internal price failed to move with the market, the lending
engine created artificial solvency for accounts backed by below-par collateral.
The protocol's accounting still saw one dollar of fUSD or DEI; secondary
markets saw a much lower liquidation value.

## Incident metrics

| Signal                    | Observation                                                                                                         | Market-health interpretation                                                                              |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Internal collateral price | fUSD and DEI were quoted at one dollar inside Scream while trading below peg                                        | A fixed collateral quote disconnected borrower health from liquidation value                              |
| Reported external lows    | fUSD around 0.69 dollars and DEI around 0.52 dollars in public reports                                              | The haircut required to keep loans solvent was materially larger than a normal stablecoin basis           |
| Reported bad debt         | Approximately 35 million dollars                                                                                    | The pricing gap was large enough to turn collateral-price risk into protocol insolvency                   |
| Liquidity drop            | DefiLlama shows Scream TVL/liquidity falling from 184.4 million dollars on May 13 to 33.8 million dollars on May 20 | Liquidity flight compounded the accounting loss and reduced remaining user exit capacity                  |
| Limit configuration       | Public reports said the fUSD deposit limit was effectively unlimited                                                | Exposure caps failed at the exact point where the oracle/input price was least reliable                   |
| Remediation signal        | Scream said it would work with Fantom Foundation liquidation support and move toward Chainlink oracle pricing       | The corrective action shifted from manual fixed prices toward live price feeds and liquidation automation |

The same data is separated into `scream-fusd-dei-market-signals.csv` for reuse
in incident dashboards or cross-protocol comparison.

## Manipulation path

The useful surveillance model is a three-step loop:

1. A supposedly stable collateral asset loses peg in executable markets.
2. The lending protocol continues to mark that asset at par, either through a
   hardcoded price, stale oracle, or governance-maintained assumption.
3. Borrowers convert the spread into extraction by borrowing assets that still
   trade near par.

The strategy does not require the borrower to manipulate the external price
directly. The market manipulation is the use of the internal misquote as a
synthetic exchange rate. When fUSD or DEI collateral was accepted at one dollar
inside Scream while available market evidence implied lower realizable value,
the lending pool became an off-market venue where discounted collateral could be
monetized at par.

This pattern is especially dangerous for algorithmic or protocol-native
stablecoins because their peg can fail exactly when correlated collateral,
liquidity depth, and user confidence deteriorate. During a broad stablecoin
shock, governance teams and protocol operators may also be slower to cut limits
because reducing a collateral asset to market price can immediately crystallize
bad debt and liquidations. That delay is itself a market-health signal.

## Detection controls

Lending markets should treat stablecoin parity as an assumption that expires
quickly, not as a constant. For every collateral asset that is expected to trade
at one dollar, the risk engine should track a minimum set of real-time and
delayed controls:

- Compare internal collateral price with executable DEX/CEX prices, pool
  redemption rates, and deep-liquidity stablecoin pairs.
- Trigger a collateral-factor reduction or borrow pause when a stablecoin
  trades outside a narrow band, such as 0.98 to 1.02 dollars, for more than a
  short observation window.
- Cap deposits and borrows for newly listed or recently stressed stablecoins
  until the peg, redemption path, and liquidity depth are proven in live market
  conditions.
- Monitor borrow concentration against the questionable collateral, especially
  when users borrow more liquid stablecoins or assets with better redemption
  quality.
- Separate emergency liquidation logic from the same governance path that
  listed the collateral, so operators can reduce exposure without waiting for a
  full governance cycle.
- Publish outstanding bad debt by collateral type after a depeg so depositors
  can distinguish ordinary utilization from insolvency.

The critical metric is not only the collateral price itself. A protocol can see
early warning by combining oracle-vs-market divergence, collateral deposit
velocity, stablecoin borrow outflows, and remaining pool liquidity. In Scream's
case, the useful alarm would have been the joint movement: below-peg fUSD and
DEI, unchanged one-dollar internal collateral valuation, high borrowing demand
for stronger stablecoins, and a rapid drop in Scream liquidity.

## Lessons for market health

Stablecoin lending markets need a market-health rule that is stricter than
"stablecoins equal one dollar." A better rule is: a stablecoin counts as one
dollar only while observable markets, redemption mechanics, and liquidity depth
continue to support that value. When those signals break, the protocol should
assume the asset is volatile collateral and apply haircuts, limits, or a pause.

The Scream incident also shows why exchange and protocol surveillance should
watch internal pricing venues, not only public markets. If a public market says
an asset is worth 0.52 to 0.69 dollars while a lending market lets it borrow at
one dollar, the lending market is effectively offering a subsidized exit path.
That spread can be extracted until the borrowable assets are gone or until the
operator updates the price. A market-health dashboard should therefore surface
protocol-level mispricing as an abuse opportunity even before a transaction is
classified as an exploit.

## References

- [CryptoSlate: Scream protocol loses millions to stablecoin depeg](https://cryptoslate.com/scream-protocol-losses-millions-to-stablecoin-depeg/)
- [Crypto.news: Fantom's Scream DeFi Protocol incurs $35M bad debt](https://crypto.news/fantoms-scream-defi-protocol-incurs-35m-bad-debt-as-two-more-stablecoins-lose-usd-peg/)
- [Smart Contract Hacking incident page for Scream](https://smartcontractshacking.com/hacks/scream-hack-2022)
- [DefiLlama Scream protocol data](https://defillama.com/protocol/scream)
