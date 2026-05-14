---
title: "Azuki Elementals NFT Lending Liquidations"
date: 2023-06-28
entities:
  - Azuki
  - Chiru Labs
  - Elementals
  - Blur Blend
  - NFT lending
---

## Summary

On June 27-28, 2023, Azuki's Elementals mint triggered a sharp repricing of the original Azuki NFT collection. [CoinDesk reported](https://www.coindesk.com/web3/2023/06/27/azuki-elementals-nft-mint-sells-out-in-15-minutes-raking-in-38m) that Elementals sold out in 15 minutes and raised $38 million. A day later, [CoinDesk reported](https://www.coindesk.com/web3/2023/06/28/azuki-nft-prices-slide-44-after-creator-releases-basically-identical-elementals) that Azuki NFT prices had slid 44% after holders criticized the new collection as too similar to the original.

The floor-price shock carried into NFT credit markets. [The Crypto Times summarized](https://www.cryptotimes.io/2023/07/04/nft-market-experiences-worst-liquidation-in-history-report/) a Cirrus report that described a severe NFT liquidation wave, including hundreds of Beanz liquidations and large liquidations tied to Azuki-related collections.

The market-health issue was collection-dilution and NFT-lending liquidation risk. Azuki holders were hit by a primary-market mint, secondary-market floor collapse, and loan-health deterioration at nearly the same time.

## Manipulation Analysis

The first stress vector was collection dilution. When a project releases a closely related collection, holders may reprice the scarcity and brand value of the original collection. That repricing can be sudden if buyers believe the new supply competes with the old supply.

The second vector was floor-price reflexivity. NFT lending protocols use floor prices to estimate collateral health. A sharp floor move can push many loans toward liquidation together, increasing sell pressure and weakening the same floor that lenders depend on.

The third vector was leverage around mint participation. If holders borrow against existing NFTs to participate in a new mint, the mint can increase both asset supply and leverage at once. That makes the post-mint floor reaction more dangerous.

The fourth vector was governance and refund pressure. [CoinDesk reported](https://www.coindesk.com/web3/2023/07/03/azukidao-votes-on-reclaim-of-20k-ether-after-botched-elementals-nft-mint) that AzukiDAO voted on reclaiming 20,000 ETH after the Elementals controversy. Community refund efforts become a market-health signal because they indicate loss of confidence in the issuer.

## Metrics Used

### Collection floor shock

The primary signal is how quickly the original collection reprices after a related mint.

Useful metrics include:

- original collection floor price before and after mint;
- floor-price change over one-hour, one-day, and one-week windows;
- listing count near and below previous floor;
- realized sale price versus pre-mint floor;
- bid depth within 5%, 10%, and 20% of floor.

### NFT lending exposure

Floor shocks matter more when many loans share the same collateral.

Useful metrics include:

- number of loans backed by the affected collection;
- debt outstanding by collection;
- loans near liquidation threshold;
- liquidations by collection;
- average liquidation loss versus debt owed.

### Mint and dilution pressure

Primary issuance can change secondary-market health.

Useful metrics include:

- new collection supply;
- mint price and total proceeds;
- overlap between original holders and new mint recipients;
- similarity or trait-overlap signals between collections;
- post-mint trading volume and holder concentration.

### Community confidence

Governance and refund actions can be early warnings of continued selling pressure.

Useful metrics include:

- refund proposal voting activity;
- social sentiment around the mint;
- whale holder exits;
- unique holder count change;
- marketplace royalty and listing behavior after the controversy.

The same fields are summarized in [azuki-elementals-nft-lending-signals.csv](azuki-elementals-nft-lending-signals.csv) for dataset-based review.

| Signal                | Observation                                                                 | Market-health interpretation                                               |
| --------------------- | --------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Elementals mint       | CoinDesk reported Elementals sold out in 15 minutes and raised $38M         | Primary issuance can shock original-collection scarcity pricing            |
| Azuki floor slide     | CoinDesk reported Azuki prices slid 44% after the mint controversy          | NFT collateral floors can move faster than loan systems expect             |
| Liquidation wave      | The Crypto Times summarized a severe NFT liquidation wave after the shock   | Lending exposure should be tracked by collection and liquidation threshold |
| Refund governance     | CoinDesk reported an AzukiDAO vote to reclaim 20,000 ETH                    | Community governance and refund pressure signal issuer-confidence stress   |
| Lending market report | CoinGecko's Q2 report discussed NFT lending growth and liquidation pressure | Credit growth can amplify collection-specific floor shocks                 |

## Timeline

- **June 27, 2023:** Azuki Elementals sold out quickly and raised $38 million.
- **June 28, 2023:** Azuki floor prices fell sharply as holders criticized Elementals as too similar to the original collection.
- **Early July 2023:** Public reports described a large NFT liquidation wave affecting Azuki-related and other blue-chip NFT lending positions.
- **July 3, 2023:** AzukiDAO voted on a proposal to reclaim 20,000 ETH after the mint controversy.

## Market Health Lessons

Azuki Elementals shows that NFT lending risk can come from issuer product decisions, not only broad crypto prices. A new mint can dilute perceived scarcity, break floor-price confidence, and push leveraged NFT holders into liquidation.

For Market Health, NFT lending dashboards should track collection-specific floor depth, debt outstanding, loan health, primary issuance events, and community-confidence signals together. If a floor-price oracle depends on social consensus around scarcity, then issuer behavior is part of the risk model.
