---
title: "NFT Wash Trading on Incentive-Driven Marketplaces"
date: 2026-05-12
description: "Reward-driven NFT marketplaces created a sharp divergence between reported trading volume and organic collector demand, especially on LooksRare and X2Y2."
entities:
  - LooksRare
  - X2Y2
  - Element
  - Sudoswap
  - OpenSea
  - Ethereum NFTs
  - LOOKS
  - X2Y2 Token
---

## Summary

1. Token reward programs on NFT marketplaces created direct incentives to maximize volume rather than discover fair prices.
2. Public Ethereum data shows that a small share of trades can dominate reported volume when the largest suspicious transactions are repeated between linked wallets.
3. Dune's marketplace-agnostic filtering estimated that Ethereum NFT wash trades represented almost 45% of all NFT volume and over $30 billion in traded value, while accounting for only about 1.5% of trades.
4. The distortion was concentrated in reward-driven venues: LooksRare and X2Y2 were reported as the largest sources, with Element and Sudoswap also showing elevated wash-trade ratios.
5. Market health dashboards should therefore separate raw volume from filtered volume, participant diversity, funding-link clusters, and repeated NFT round trips.

## Why reward marketplaces were vulnerable

NFT marketplaces often compete on reported volume because volume is easy to quote, easy to rank, and frequently treated as a proxy for liquidity. The problem with reward-driven marketplaces is that the same metric used to advertise traction can become the metric users are paid to manufacture.

LooksRare made trading rewards central to its launch through the LOOKS token, and X2Y2 later used a similar token incentive model. These programs did not require a trader to prove that a sale reflected organic demand from an unrelated buyer. If rewards are based primarily on volume, a trader can be economically motivated to trade an NFT between controlled wallets, pay fees and gas, and still try to come out ahead through marketplace rewards.

This makes NFT wash trading different from ordinary low-quality liquidity. The asset is non-fungible, so repeated transfers of the exact same token between a small address cluster are especially informative. A single ERC-721 can cycle between wallets without changing the underlying economic owner. The visible sale history then looks active to ranking pages and outside buyers even when the risk has not really moved to an independent participant.

## Evidence from public datasets

Dune's open wash-trade methodology for Ethereum NFTs uses four classes of flags: buyer equals seller, back-and-forth trades of the same NFT, repeated purchases of the same NFT by one address, and buyer/seller pairs that were first funded by the same wallet. Applying these filters, Dune estimated that wash trades were about 1.5% of Ethereum NFT trades but almost 45% of volume. The same analysis estimated more than $30 billion of wash-trading volume, with 2022 reaching 58% wash volume and January 2022 peaking above 80%.

The platform concentration is the critical market-health signal. Dune reported that LooksRare and X2Y2 produced the vast majority of wash-trading volume, estimating 98% of LooksRare volume and 87% of X2Y2 volume as wash-driven. Element and Sudoswap were also affected, while OpenSea's reported wash-trade share was much lower. This pattern matches the incentive structure: the highest distortion appeared where token rewards or airdrop expectations made raw volume valuable by itself.

{{< figure src="marketplace-wash-volume-share.svg" alt="Dune reported estimated wash-trade volume share by NFT marketplace" caption="Estimated marketplace volume share classified as wash trading in Dune's Ethereum NFT analysis. Element and Sudoswap are approximate values from Dune's published marketplace breakdown." >}}

Chainalysis reached a similar conclusion through wallet funding analysis: its sample found hundreds of repeat NFT sellers whose buyers were wallets they had funded, including one cluster with more than eight hundred such sales ([Chainalysis](https://www.chainalysis.com/blog/2022-crypto-crime-report-preview-nft-wash-trading-money-laundering/)). Most identified wash traders were unprofitable after gas, but the profitable subset collectively made nearly $8.9 million. That matters because the profit would likely come from later sales to buyers who interpreted the prior wash-traded history as real demand.

Academic research also supports the use of graph features instead of simple volume thresholds. In a 2022 arXiv paper covering 52 large NFT collections from January 2018 to mid-November 2021, von Wachter, Jensen, Regner, and Ross reported that only a small minority of wallets and sales tripped their abuse heuristics, yet those flows could still add as much as $149.5 million of artificial volume to the sample ([arXiv](https://arxiv.org/abs/2202.03866)). Their finding that many patterns alternate between a small number of addresses is consistent with round-trip and cluster-based detection.

## Market health indicators

Raw marketplace volume should not be used alone when an NFT venue has volume rewards, token incentives, or airdrop expectations. The following indicators are better suited for market-health monitoring:

1. Filtered volume ratio: compare raw volume with volume after removing buyer-equals-seller trades, repeated same-NFT cycles, and common-funder clusters.
2. Trade count versus volume divergence: a low number of suspicious trades creating a high share of volume is a strong sign that headline volume is inflated.
3. Same-token round trips: flag repeated transfers of the same ERC-721 between the same counterparties or a small address set.
4. Counterparty diversity: organic markets should show many unrelated buyers and sellers, not a narrow cluster repeatedly trading the same items.
5. Funding graph overlap: buyers funded by sellers, or both sides first funded by the same wallet, should be treated as high-risk counterparties.
6. Reward sensitivity: spikes in volume around reward changes, token emissions, or airdrop snapshots should be compared with unique-buyer growth and external marketplace prices.
7. Collection-level ranking impact: suspicious trades can lift a collection into trending pages, so filtered rankings are safer than raw rankings.

These indicators should be reported per marketplace and per collection. A venue can have a low share of suspicious trades but still a high share of suspicious volume if the wash trades are large. That is why trade count, dollar volume, participant graph, and NFT-level repetition must be monitored together.

### Proposed market-health score

To make the indicators falsifiable, each marketplace or collection can be assigned a wash-trading risk score from 0 to 100. A higher score means reported volume is less reliable.

`Risk score = 0.25F + 0.15D + 0.15R + 0.15C + 0.15G + 0.10S + 0.05K`

Where:

1. `F` is the filtered-volume gap: `100 * (raw volume - filtered volume) / raw volume`.
2. `D` is volume-count divergence: `100 * max(0, suspicious volume share - suspicious trade-count share)`.
3. `R` is same-token round-trip intensity: `100 * same-NFT round-trip trades / total trades`.
4. `C` is counterparty concentration: `100 * top linked-cluster volume / total volume`.
5. `G` is funding-graph overlap: `100 * common-funder or seller-funded volume / total volume`.
6. `S` is reward sensitivity: the percent change in volume around reward, emission, or airdrop windows minus the percent change in unique buyers, clipped to 0-100.
7. `K` is ranking impact: `100 * suspicious volume that affected trending or collection-rank windows / total suspicious volume`.

The score should be computed twice: once per marketplace and once per collection. Marketplace scoring identifies venues whose total volume is reward-distorted. Collection scoring catches cases where a mostly clean venue still has a manipulated collection ranking. A marketplace or collection with a score below 25 is green, 25 to 50 is yellow, and above 50 is red. If raw volume is zero or source data is incomplete, the score should be marked "insufficient data" rather than forced into a color band.

Audit rules should be explicit. Exclude known centralized-exchange deposit wallets from common-funder tests, separate ERC-721 and ERC-1155 behavior, publish the query window, and keep every excluded suspicious category count visible. A score can fail in several ways: market makers may create false positives through fast inventory turnover, privacy tools can obscure funding links, cross-chain bridges can hide first-funder relationships, and airdrop speculation can create organic but short-lived volume. For that reason, the score should not be used as a fraud verdict. It is a reproducible risk filter for deciding which raw volume figures need manual review.

### Worked example from Dune marketplace shares

Dune's published marketplace breakdown is not enough to compute every term of the full score, but it is enough to show why raw volume alone is dangerous. Treat the reported wash-volume share as a proxy for `F`, and compute `D` as `wash-volume share - wash-trade-count share`, clipped at zero. This gives a lower-bound score from only two components: `0.25F + 0.15D`.

| Marketplace | Wash volume share | Wash trade-count share | `D` proxy | Two-factor lower-bound score |
| --- | ---: | ---: | ---: | ---: |
| LooksRare | 98% | 25% | 73 | 35.5 |
| X2Y2 | 87% | 22% | 65 | 31.5 |
| Element | about 66% | 18.5% | about 47.5 | about 23.6 |
| Sudoswap | about 11% | 14.5% | 0 | about 2.8 |
| OpenSea | 2.4% | below 1% | above 1.4 | above 0.8 |

The table is intentionally conservative because it ignores same-token round trips, funding overlap, counterparty concentration, reward sensitivity, and ranking impact. LooksRare and X2Y2 already reach yellow-zone lower bounds with only two variables. If the omitted graph variables are added, their final score would likely move closer to the red threshold.

## Practical implications

For analysts, the key lesson is that volume is not liquidity unless the counterparties are economically independent. LooksRare and X2Y2 showed how quickly a reward design can turn volume into a target to optimize rather than a measurement of demand. Public dashboards should therefore publish both raw and filtered statistics, explain the filtering rules, and make suspicious categories auditable.

For marketplaces, reward programs should avoid paying users for raw volume without controls. Better designs would cap rewards per collection, discount repeated same-token transfers, exclude common-funder address clusters, and emphasize unique counterparties or longer-term retention. Enforcement does not need to prove every suspicious trade was malicious; it only needs to prevent repeat clusters from dominating ranking systems and reward pools.

For buyers, wash-traded sale history can create a false signal of demand and price support. A collection with high volume but low unique ownership growth, repeated high-value transfers, or a narrow set of counterparties should be treated cautiously. The same warning applies to marketplace comparisons: raw volume can make a venue appear healthier than its organic user base.

The supporting source tables for this article are available in [source-metrics.csv](source-metrics.csv) and [marketplace-wash-share.csv](marketplace-wash-share.csv).

## References

- [Dune: NFT Wash Trading on Ethereum](https://dune.com/blog/nft-wash-trading-on-ethereum)
- [Chainalysis: NFT Money Laundering and Wash Trading](https://www.chainalysis.com/blog/2022-crypto-crime-report-preview-nft-wash-trading-money-laundering/)
- [von Wachter, Jensen, Regner, Ross: NFT Wash Trading: Quantifying suspicious behaviour in NFT markets](https://arxiv.org/abs/2202.03866)
