---
title: "Acala aUSD Depeg After iBTC Pool Misconfiguration"
date: 2022-08-14
entities:
  - Acala
  - aUSD
  - iBTC
  - Polkadot
  - Honzon
---

## Summary

On August 14, 2022, Acala's aUSD stablecoin lost its dollar peg after a misconfiguration in a newly deployed iBTC/aUSD liquidity pool allowed erroneous aUSD mints. [CoinDesk reported](https://www.coindesk.com/tech/2022/08/15/acalas-stablecoin-falls-99-percent-after-hackers-issue-13-billion-tokens) that aUSD fell 99% after attackers exploited the pool bug to mint 1.28 billion tokens. Acala developers attributed the issue to a misconfiguration of the iBTC/aUSD pool shortly after it went live.

[CoinDesk's follow-up analysis](https://www.coindesk.com/tech/2022/08/22/inside-the-3b-defi-exploit-of-acalas-crypto-platform) described the broader scale as technically about $3 billion of aUSD minted through the affected platform, noted that the issue involved a liquidity-pool configuration from the Honzon protocol, and said the peg had partially recovered to around $0.80 after Acala traced and froze much of the erroneous supply. The incident showed that even overcollateralized stablecoin systems can suffer sharp peg breaks when protocol configuration allows unbacked supply to enter circulation.

The Acala case is useful for Market Health because it joins stablecoin monitoring with operational controls. The immediate market signal was a peg collapse, but the root market-health failure was a supply-integrity failure: the market could no longer trust that every aUSD unit had been minted through the normal collateral path.

## Metrics Used

### Unauthorized supply expansion

The clearest market-health signal was not just price. It was the sudden creation of a massive amount of aUSD outside normal collateralized minting. Stablecoin dashboards should alert when total supply jumps without a matching change in collateral, debt positions, or governance-approved issuance.

Useful supply-integrity metrics include:

- total stablecoin supply change by block;
- supply minted by pool or module;
- collateral posted against new supply;
- mismatch between minted supply and recognized debt positions;
- addresses receiving unusually large newly minted balances.

### Peg deviation and liquidity depth

aUSD's market price collapsed because holders and traders no longer knew which supply was legitimate, which supply would be frozen or burned, and how much unbacked aUSD might reach liquid markets. A 99% depeg is a market's way of saying that normal redemption and collateral assumptions no longer apply.

Useful peg and liquidity metrics include:

- lowest aUSD price after the minting event;
- depth in aUSD pools before and after the incident;
- swap slippage for fixed aUSD sale sizes;
- cross-venue price gaps if bridge or exchange deposits are disabled;
- recovery speed after erroneous supply is frozen, traced, or burned.

### Pool-launch risk

The affected iBTC/aUSD pool was newly deployed. New pools are high-risk because configuration errors can create paths that were not exercised in prior production liquidity. A stablecoin system should treat new pool activation as a market-health event, especially when the pool can mint rewards or interact with the stablecoin's core accounting.

Launch controls should monitor:

- first-hour minting and reward claims from a new pool;
- abnormal balance changes from liquidity-provider reward logic;
- whether pool modules can mint stablecoin supply directly or indirectly;
- timelocks and caps on newly launched pools;
- audit scope that specifically covers configuration and deployment parameters.

### Freeze, trace, and burn response

Acala's recovery depended on tracing erroneous mints, freezing affected balances, and restoring confidence that bad supply would not remain freely tradable. This response path is important market-health data: a stablecoin may recover if illegitimate supply is contained quickly, but may fail if bad supply escapes into deep external venues.

The same fields are summarized in [acala-ausd-signals.csv](acala-ausd-signals.csv) for dataset-based review.

| Signal                    | Observation                                                        | Market-health interpretation                                       |
| ------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------ |
| Erroneous mint size       | Reports cited 1.28 billion aUSD and broader $3 billion scale       | Supply integrity failed outside normal collateralized issuance     |
| Peg collapse              | aUSD fell roughly 99% after the minting event                      | Market discounted all aUSD until legitimate supply was clarified   |
| New pool misconfiguration | The iBTC/aUSD pool had recently gone live                          | Fresh liquidity-pool launches need caps, alarms, and staged risk   |
| Partial recovery          | Follow-up coverage described a partial recovery toward about $0.80 | Freezing and tracing can restore some confidence before full repeg |
| Audit/config gap          | The issue was described as a configuration problem despite audits  | Deployment configuration must be monitored like code risk          |

## Timeline

- **August 4, 2022:** Acala announced the iBTC/aUSD liquidity pool.
- **August 14, 2022:** A configuration issue in the pool allowed erroneous aUSD minting shortly after deployment.
- **August 14-15, 2022:** aUSD depegged sharply, with public reports describing a 99% collapse after 1.28 billion aUSD was issued.
- **August 15-22, 2022:** Acala traced affected balances and attempted to restore the peg by containing erroneous supply.
- **August 22, 2022:** CoinDesk follow-up coverage said the peg had partially recovered to about $0.80, showing progress but not immediate full confidence.

## Market Health Lessons

Acala shows that stablecoin peg health depends on supply integrity as much as collateral ratios. If a module or pool can create unbacked stablecoin supply, a stablecoin can depeg even if its normal design is overcollateralized.

Market-health monitoring should combine price feeds with protocol-accounting controls. Sudden supply growth, abnormal reward claims, new-pool mint activity, collateral mismatch, frozen-balance counts, and cross-venue price gaps should all be treated as stablecoin health signals. For newly deployed liquidity pools, hard caps and first-hour anomaly alerts can matter as much as ordinary audits.
