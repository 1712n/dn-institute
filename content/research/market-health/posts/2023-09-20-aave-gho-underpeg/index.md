---
title: "Aave GHO Underpeg and Borrow-Rate Peg Restoration"
date: 2023-09-20
entities:
  - Aave
  - GHO
  - AAVE
  - Ethereum
---

## Summary

After Aave launched GHO, its overcollateralized native stablecoin, the asset traded below its intended $1 peg for an extended period. The underpeg was not presented as a hack. It was a market-health problem created by the relationship between GHO supply, borrow demand, secondary-market liquidity, and the governance-set borrow rate.

Aave describes [GHO](https://aave.com/gho) as a decentralized, overcollateralized stablecoin native to the Aave Protocol. Borrowers mint GHO against supplied collateral, while Aave Governance controls parameters including facilitators and interest rates. That governance control became the main peg-restoration tool after GHO's launch.

On September 20, 2023, Aave governance proposal [AIP-323](https://governance-v2.aave.com/governance/proposal/323/) increased the GHO borrow rate and stated that GHO's borrow rate had been set below the market price of stablecoin borrows. The proposal also noted that GHO's peg deviation, around $0.975 at the time, was affecting growth and market trust. Later proposals continued the same peg-restoration path by raising the borrow rate again.

## Metrics Used

### Borrow-rate differential

GHO's peg stress was closely tied to its borrow-rate setting. If GHO is cheaper to borrow than comparable stablecoins, borrowers can mint and sell it while secondary-market buyers demand a discount. AIP-323 described this explicitly: the rate was below market, which supported growth but contributed to peg pressure.

Market-health monitoring should compare:

- GHO borrow rate versus USDC, USDT, DAI and other stablecoin borrow rates;
- monthly average GHO price versus the governance target band;
- newly minted GHO supply after rate changes;
- liquidity depth and slippage in the main GHO swap venues;
- whether rate changes are fast enough to respond to a persistent underpeg.

### Governance response speed

Aave's peg response happened through governance proposals rather than automatic monetary policy. After AIP-323, [AIP-381](https://governance-v2.aave.com/governance/proposal/381/) raised the borrow rate again and compared GHO's current borrow rate with other stablecoin borrow costs. The December 2023 [ARFC](https://governance.aave.com/t/arfc-increase-gho-borrow-rate-100-bps-to-6-35-on-aave-v3/15744) proposed another increase, from 5.35% APY to 6.35% APY, to support peg restoration and align borrowing costs with the market.

This creates a governance-latency metric: if a stablecoin depends on governance-set rates, the market can remain underpegged while proposals are drafted, discussed, voted, queued, and executed. The governance process can be transparent and legitimate while still being slower than the market's repricing of a discounted asset.

### Peg-band rule

The December ARFC referenced a target range of 0.995 to 1.005 for the monthly average GHO price and described continuing 100 bps weekly increases if the monthly average remained outside that range. That kind of peg-band rule is a useful market-health control because it turns an ambiguous peg problem into an observable trigger.

The same fields are summarized in [aave-gho-signals.csv](aave-gho-signals.csv) for dataset-based review.

| Signal               | Observation                                             | Market-health interpretation                               |
| -------------------- | ------------------------------------------------------- | ---------------------------------------------------------- |
| GHO price            | AIP-323 cited GHO around $0.975                         | Persistent underpeg damaged trust even without bad debt    |
| Borrow-rate mismatch | GHO borrow was below comparable stablecoin borrow costs | Cheap minting can create sell pressure until rates align   |
| Rate intervention    | AIP-323, AIP-381, and later ARFCs increased rates       | Peg defense depended on governance action                  |
| Target band          | Monthly average target range was 0.995 to 1.005         | Clear peg-band triggers make rate policy easier to monitor |
| Governance latency   | Rate changes required proposals and execution           | Transparent governance can still lag fast market repricing |

## Timeline

- **July 2023:** GHO launched on Ethereum mainnet as Aave's overcollateralized native stablecoin.
- **September 20, 2023:** AIP-323 increased the GHO borrow rate and noted that GHO was around $0.975, below its target peg.
- **November 2023:** AIP-381 proposed another GHO borrow-rate increase, comparing GHO rates against other stablecoin borrow markets.
- **December 4, 2023:** Aave Chan Initiative posted an ARFC proposing to increase the GHO borrow rate from 5.35% APY to 6.35% APY and continue weekly 100 bps increases if the monthly average price remained outside the 0.995 to 1.005 range.

## Market Health Lessons

GHO's underpeg shows that an overcollateralized stablecoin can still trade below $1 when minting incentives, borrow costs, liquidity demand, and governance response speed are not aligned. Collateral backing reduces insolvency risk, but it does not guarantee secondary-market peg stability.

For stablecoin monitoring, the key signals are borrow-rate competitiveness, peg-band persistence, liquidity depth, market-cap growth, and the speed of governance parameter updates. When the peg defense mechanism is governance-controlled, the health of the market depends not only on collateral but also on whether governance can react quickly enough to changing stablecoin yields.
