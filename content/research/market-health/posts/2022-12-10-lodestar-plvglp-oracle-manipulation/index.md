---
title: "Lodestar plvGLP Oracle Manipulation"
description: "A Market Health case study on how a manipulable vault exchange rate made Lodestar value plvGLP collateral above its economic backing and drain lending liquidity."
date: 2022-12-10
tags:
  - Lodestar Finance
  - plvGLP
  - Oracle manipulation
  - Arbitrum
  - Lending
---

## Key points

1. Lodestar's December 2022 exploit shows a market-health failure mode where a lending market priced collateral from a vault exchange rate that could be moved by direct asset donation.
2. CertiK traced the root cause to Lodestar's GLPOracle calculation, which multiplied the GLP price by the Plutus vault exchange rate. That exchange rate rose as `totalAssets` increased while `totalSupply` stayed fixed.
3. Public analyses report a plvGLP/GLP ratio move from about 1.07 before the manipulation to about 1.82 or 1.83 after the donation.
4. The inflated collateral mark let the attacker borrow nearly all available Lodestar assets, leaving more than $6 million in bad debt and producing about $5.8 million in reported attacker profit.
5. The useful monitor is not just "large borrow." It is the compound signal: vault-share exchange-rate jump, collateral factor still enabled, borrow utilization across many assets, and same-block or same-transaction flash-loan funding.

The companion file [`lodestar-plvglp-risk-signals.csv`](lodestar-plvglp-risk-signals.csv) records the source-linked evidence points used below. The chart reconstructs the observable control path from public reports rather than replaying every Arbitrum trace.

{{< figure src="lodestar-plvglp-oracle-path.svg" alt="Lodestar plvGLP oracle manipulation control path" caption="Selected public evidence points from the December 2022 Lodestar plvGLP oracle manipulation." loading="lazy" >}}

## The fragile market structure

Lodestar was a Compound-style Arbitrum lending market. That matters because a Compound fork turns collateral value into borrowing capacity: if the oracle overstates collateral, the lending pool will allow loans that are undercollateralized in the real market.

The vulnerable surface was the plvGLP collateral path. Public reports describe a price function that looked through to a Plutus vault exchange rate. In simplified form, the collateral value combined:

1. the market value of GLP, and
2. the number of GLP-equivalent assets backing each plvGLP share.

That is a reasonable design only if the share exchange rate cannot be manipulated faster than risk controls react. In this case, the backing ratio could be pushed up by donating GLP-like assets into the vault path without issuing matching new shares. The oracle then treated the higher ratio as collateral value.

The market-health problem is subtle but severe. A donation does add assets to the vault, so the accounting ratio is not arbitrary. But it is still manipulable as a price input when the same actor can move the ratio, post the marked-up share token as collateral, and borrow liquid assets before the system discounts or pauses the collateral.

## The exchange-rate jump

CertiK reports that the exchange-rate ratio moved from about 1.07 at the beginning of the incident to about 1.82 after manipulation. Cointelegraph, citing Lodestar's own explanation, reports a 1.83 GLP per plvGLP mark.

That is a roughly 70% one-incident uplift in collateral value:

```text
ratio change = 1.82 / 1.07 - 1 = 70.1%
```

For a lending market, a 70% collateral revaluation is not a normal market tick. It should be treated as a circuit-breaker event, especially when the asset is a wrapper or vault share rather than a deep external spot market.

The important distinction is between real vault backing and borrowable market value. The attacker made the share ratio richer, but the lending market's risk engine also let that ratio unlock borrow capacity across unrelated liquid assets. That converted an accounting donation into a pool-wide liquidity drain.

## Attack flow as market-health signals

The public sources give a compact signal chain:

1. Flash liquidity funded a large starting balance. CertiK reports roughly $70.5 million across eight flash loans and says 14,960 WETH was pooled into GMX-related flow.
2. The attacker built a dominant plvGLP/plsGLP position and supplied the derivative token into Lodestar.
3. The attacker manipulated the vault exchange rate by increasing the backing asset side without proportionally increasing shares.
4. Lodestar's oracle read the inflated exchange rate and marked the collateral higher.
5. The attacker borrowed nearly all remaining available assets from Lodestar.
6. The protocol was left with more than $6 million in bad debt, while public reports place attacker profit near $5.8 million.

Those steps create several monitorable conditions. The ratio jump is observable before the final bad debt is realized. The collateral factor and borrow utilization are observable while the position is being opened. The sudden cross-asset borrowout is observable as the drain happens. None of those require knowing the attacker's identity.

## What the evidence shows

NomosLabs identifies the exploit transaction as `0xc523c6307b025ebd9aef155ba792d1ba18d5d83f97c7a846f267d3d9a3004e8c` at Arbitrum block `45121904`, with a $6.5 million loss classification. CertiK reports that the funds moved through a wallet that received roughly 4,527 ETH, worth about $5.74 million at the time, and that the funds were bridged to Ethereum and distributed across externally owned accounts.

The loss estimates differ slightly across sources because they separate protocol loss, attacker profit, bad debt, recoverable GLP, and post-exploit redemption value. That spread is itself useful for market-health reporting. A venue should not wait for a final "loss" number before acting; the live risk signals are the price-ratio movement and borrow-capacity mismatch.

Cointelegraph reports that Lodestar expected about 2.8 million GLP, worth about $2.4 million, to be recoverable for depositors. Recovery did not remove the market-integrity failure: the protocol had already let a transiently manipulated collateral ratio drain liquid lending markets.

## Surveillance indicators

### Vault-share exchange-rate shocks

- Alert when a vault-share collateral exchange rate moves more than a configured band within one block, one transaction, or one oracle update interval.
- Separate organic share appreciation from direct donation effects by tracking `totalAssets`, `totalSupply`, deposit events, and transfer-only inflows.
- Disable new borrowing against the collateral when the backing ratio changes without corresponding share issuance.

### Collateral value versus external depth

- Compare the new marked collateral value with external GLP depth, vault withdrawal capacity, and historical exchange-rate movement.
- Haircut or pause wrapper assets whose price depends on internal accounting rather than an independently traded market.
- Recalculate borrow limits after a shock using the pre-shock exchange rate until the new ratio survives a time delay.

### Pool-wide borrowout pressure

- Escalate when one account's new collateral valuation is followed by borrowing across many unrelated markets.
- Treat near-total utilization drawdowns as a linked incident when they follow the same collateral-ratio jump.
- Track bad-debt risk in asset units, not only in aggregate dollars, so liquid reserves can be paused before every market is drained.

### Flash-funded collateral loops

- Detect same-transaction funding, collateral acquisition, collateral supply, oracle-ratio jump, and borrowout as one pattern.
- Increase confirmation time for high-risk wrapped collateral when position opening depends on flash liquidity.
- Require manual or delayed activation for new collateral types whose price function uses share accounting.

## Controls that would have changed the outcome

1. A cap on per-block or per-update plvGLP exchange-rate changes used by the lending oracle.
2. A donation-aware vault adapter that prices shares from internally accounted deposits rather than raw asset balance.
3. A collateral pause when `totalAssets` increases without matching share issuance.
4. A conservative collateral factor for wrapper assets whose exchange rate is not externally traded.
5. A borrowout guard that freezes new loans when one collateral asset's ratio shock is immediately followed by cross-market reserve depletion.
6. A delayed oracle acceptance window so exchange-rate changes become borrowable only after surviving multiple blocks and external validation.

## Why this belongs in a market manipulation wiki

The Lodestar incident is a useful Market Health case because the manipulated variable was not a public spot price alone. It was a protocol-specific exchange rate that a lending market treated like price. That makes the case transferable to vault shares, receipt tokens, liquid staking wrappers, LP positions, and any collateral whose value depends on internal accounting ratios.

The lesson is that market health includes the path from accounting state to borrowable value. A venue can use an honest-looking formula and still create a manipulable market if a trader can move the formula input, post collateral, and borrow before the mark is challenged. Monitoring should therefore watch accounting-ratio velocity, external price corroboration, and pool-wide borrow utilization together.

## References

- NomosLabs, "Lodestar Finance - plvGLP Oracle Manipulation on Arbitrum": https://nomoslabs.io/archive/lodestar-finance-2022
- CertiK, "Lodestar Finance Incident Analysis", December 11, 2022: https://www.certik.com/skynet-report/lodestar-finance-incident-analysis
- Cointelegraph, "Lodestar Finance exploited in flash loan attack", December 11, 2022: https://cointelegraph.com/news/lodestar-finance-exploited-in-flash-loan-attack
- Halborn, "Explained: The Lodestar Finance Hack (November 2022)", December 13, 2022: https://www.halborn.com/blog/post/explained-the-lodestar-finance-hack-november-2022
- Arbiscan attack transaction `0xc523c6307b025ebd9aef155ba792d1ba18d5d83f97c7a846f267d3d9a3004e8c`: https://arbiscan.io/tx/0xc523c6307b025ebd9aef155ba792d1ba18d5d83f97c7a846f267d3d9a3004e8c
