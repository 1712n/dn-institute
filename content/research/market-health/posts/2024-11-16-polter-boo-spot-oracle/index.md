---
title: "Polter Finance BOO Spot-Oracle Borrowing Cascade"
description: "A Market Health case study on how flash-loan depletion of SpookySwap BOO pools made one BOO token look large enough to empty Polter Finance lending reserves."
date: 2024-11-16
tags:
  - Polter Finance
  - SpookySwap
  - BOO
  - Fantom
  - Oracle manipulation
---

## Key points

1. Polter Finance's November 2024 exploit shows why lending protocols should treat thin spot DEX pools as market-health sensors, not as final collateral truth.
2. CertiK reported that Polter's BOO price path used two SpookySwap pairs through an AaveOracle-style feed. The attacker flash-borrowed nearly all BOO from both pairs, leaving only 1e6 wei BOO on each route.
3. After the pool state was distorted, the attacker deposited 1 BOO into Polter and borrowed against an oracle value that CertiK reported as $1,373,782,984,830,617,596 for that one token.
4. Coinspect reconstructed the exploit as a Fantom price-manipulation case with $8.7 million-plus in losses, where borrowing power was calculated from manipulated SpookySwap V2/V3 BOO prices.
5. The useful surveillance lesson is not only "use better oracles." The pre-trade control should ask whether a borrow limit can be dominated by one transaction's temporary pool inventory.

The companion file [`polter-boo-oracle-ledger.csv`](polter-boo-oracle-ledger.csv) records the source-linked evidence points used below. The chart is a compact signal path from those public reports, not a replay of Fantom execution traces.

{{< figure src="polter-boo-spot-oracle.svg" alt="Polter Finance BOO spot oracle manipulation path" caption="Selected public evidence points from the November 2024 Polter Finance BOO spot-oracle borrowing cascade." loading="lazy" >}}

## The fragile market structure

Polter Finance was a lending protocol on Fantom. Its critical market-health dependency was the BOO price feed. Halborn and CertiK both described the feed as relying on SpookySwap V2 and V3 spot pool prices rather than a robust external or time-weighted source.

That design made BOO collateral sensitive to temporary pool inventory. If the token side of a BOO/WFTM pool was depleted inside one transaction, a price read during that state could mark BOO far above its executable value. The lending protocol would then see a token whose market was actually thin and manipulated as if it were deep collateral.

Coinspect framed the vulnerable path at the borrow layer: Polter's `ILendingPool.borrow()` calculated borrowing power using those manipulated BOO prices. That is the core market-health failure. The dangerous variable was not the attacker's starting balance; it was the protocol's willingness to convert a transient spot imbalance into borrowing capacity.

## How the one-token collateral became enormous

CertiK's attack flow gives the clearest public numeric sequence:

1. The attacker borrowed 269,042 BOO from a Spooky V3 pair and 1,154,788 BOO from a Spooky V2 pair, which CertiK described as the balance of each pool.
2. That left only 1e6 wei BOO tokens on both pairs.
3. The attacker deposited 1 BOO into Polter as collateral.
4. Polter's oracle consulted the manipulated pair balances while validating a borrow.
5. CertiK reported that Polter read 1,828,570 WFTM and 1e6 wei BOO on one pair, plus 396,315 WFTM and 1e6 wei BOO on the other pair.
6. The result was an absurd collateral mark: 1 BOO was valued at $1,373,782,984,830,617,596.

The absolute valuation is so large that it is tempting to treat the incident as only a coding bug. For surveillance, the more transferable lesson is that the protocol accepted an impossible market state as a valid price. A market-health check could have failed the borrow before any token-specific vulnerability label was assigned.

## Borrowing against a pool inventory vacuum

Once the borrow check accepted the distorted BOO value, the attacker could drain lending reserves. CertiK reported an initial 9,134,844 WFTM borrow during validation. Coinspect's reconstruction shows the attack then targeting multiple reserves in sequence, including WFTM, MIM, sFTMX, axlUSDC, WBTC, WETH, USDC, and WSOL.

That path is different from ordinary liquidation stress. No broad market needed to believe BOO was worth the oracle value. The attacker only needed the protocol to sample the wrong moment in a thin venue and then apply that value across unrelated lending pools.

The exploit therefore had two liquidity domains:

1. Price domain: SpookySwap BOO/WFTM pool balances, which were small enough to be moved by flash liquidity.
2. Credit domain: Polter reserves, which treated the manipulated price as collateral support for borrowing much more valuable and liquid assets.

The bridge between those domains was the oracle.

## Surveillance indicators

### Pool-inventory dominance

- Track whether one transaction can remove nearly all inventory on any DEX pair used by a lending oracle.
- Alert when a collateral token's oracle path reads a pool with token-side balance near dust while the quote side remains substantial.
- Compare executable depth to maximum borrowable value. If one BOO can imply more borrowing power than the whole pool could support in an unwind, the price should be quarantined.

### Same-block collateral creation

- Flag deposits of freshly manipulated collateral that are immediately followed by maximum borrows.
- Require a cooling period for new or thin collateral after abnormal pool-balance changes.
- Separate "collateral accepted" from "collateral can unlock cross-reserve borrowing" for assets with shallow oracle routes.

### Oracle disagreement and sanity bands

- Compare spot DEX quotes with time-weighted prices, external feeds, and last-good-price state.
- Treat a drastic spot movement as an oracle outage unless independent sources confirm it.
- Reject price changes that imply impossible market capitalization or collateral value relative to pool depth.

### Reserve-drain sequence

- Alert when one account borrows across many unrelated reserves after posting a single volatile collateral asset.
- Limit aggregate cross-reserve borrowing capacity from thin collateral, even if per-reserve borrow checks pass.
- Track whether a protocol can lose several reserve assets from one collateral-price read.

## Controls that would have changed the outcome

1. Multi-source BOO pricing instead of a direct spot read from manipulable SpookySwap pools.
2. TWAP or delayed confirmation for collateral tokens with shallow on-chain liquidity.
3. A minimum liquidity-depth requirement before an oracle route can support borrowing.
4. A per-transaction price movement cap that fails closed when current spot and last-good price diverge too much.
5. A collateral-value ceiling based on executable depth, not only arithmetic price.
6. A new-asset or thin-asset borrow cap that limits cross-reserve exposure until the market proves stable.
7. Same-block sequencing rules that prevent flash-borrowed pool states from creating immediate borrowing power.
8. Emergency monitors for token-side pool depletion, quote-side imbalance, and one-account reserve fan-out.

## Why this belongs in a market manipulation wiki

The Polter Finance exploit is useful because it turns price manipulation into a measurable market-health control problem. The manipulated object was not a centralized order book or a long-running public market narrative. It was a short-lived on-chain pool state that a lending protocol treated as the value of collateral.

That makes the case broadly applicable. Any protocol that turns a DEX pool read into credit capacity should monitor the pool as a venue with depth, inventory, and manipulation cost, not only as a price source. The warning signals were concrete: near-total BOO depletion, dust token-side balances, a one-token deposit, an impossible collateral mark, and borrowing across multiple reserves before the market could normalize.

## References

- CertiK, "Polter Finance Incident Analysis", November 18, 2024: https://www.certik.com/skynet-report/polter-finance-incident-analysis
- Coinspect Security, "Polter Finance", Learn EVM Attacks: https://www.coinspect.com/learn-evm-attacks/cases/polter-finance/
- Halborn, "Explained: The Polter Finance Hack (November 2024)", November 25, 2024: https://www.halborn.com/blog/post/explained-the-polter-finance-hack-november-2024
