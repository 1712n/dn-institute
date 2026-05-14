---
title: "BendDAO NFT Lending Liquidity Crisis"
date: 2022-08-22
entities:
  - BendDAO
  - Bored Ape Yacht Club
  - BAYC
  - NFT lending
  - ETH
---

## Summary

In August 2022, BendDAO showed how NFT-collateralized lending can turn a floor-price decline into a liquidity run. [CoinDesk reported](https://www.coindesk.com/business/2022/08/19/many-bored-ape-nfts-are-in-danger-of-getting-liquidated-as-borrowed-money-comes-back-to-bite) that BendDAO had collateralized almost 3% of the Bored Ape Yacht Club collection and that many NFTs were entering the liquidation danger zone as floor prices fell.

[Decrypt described](https://decrypt.co/108019/benddao-nft-lending-protocol-bank-run-bored-apes) the event as a bank-run-style crisis in which lenders withdrew liquidity while NFT collateral became harder to auction. [ForkLog reported](https://forklog.com/en/users-drain-benddao-lending-protocol-to-12-5-weth/) that the protocol had only 12.5 WETH left to pay creditors while owing roughly 15,000 ETH.

The market-health issue was a collateral-liquidity mismatch. BendDAO loans were backed by NFTs priced from collection floor values, but those NFTs could not necessarily be liquidated quickly enough, or at high enough bids, to protect lenders during a broad floor-price decline.

## Manipulation Analysis

The first stress vector was floor-price dependency. If a lending protocol marks NFT collateral against a collection floor, the oracle-like input is thin and sentiment-driven. A small number of listings, bids, or sales can move the risk profile of many loans at once.

The second vector was auction friction. NFT liquidations need bidders who are willing to absorb unique assets quickly. If auction rules require an opening bid that is too high, collateral can sit unsold while lenders race to withdraw available ETH.

The third vector was collection concentration. Bored Ape Yacht Club was the headline collection, but the same mechanism applies to any NFT collection where many loans depend on the same floor-price signal. Correlated collateral makes liquidations cluster.

The fourth vector was lender exit sequencing. When available ETH falls, lenders who withdraw early reduce the remaining liquidity buffer. Later lenders are left exposed to collateral auctions whose execution time and clearing price are uncertain.

## Metrics Used

### NFT collateral concentration

The primary signal is whether a protocol has too much exposure to one collection or floor-price index.

Useful metrics include:

- share of a collection pledged as collateral;
- share of total protocol loans backed by the largest collection;
- top borrower exposure by collection;
- average and tail loan-to-value ratio by collection;
- number of loans near health factor 1.0.

### Floor-price and bid depth

NFT floor price needs depth, not just a single headline number.

Useful metrics include:

- floor-price change over one-hour, one-day, and one-week windows;
- active bids within 5%, 10%, and 20% of floor;
- listing depth below liquidation break-even prices;
- realized sale price versus floor at auction close;
- floor-price divergence across marketplaces.

### Auction execution

Liquidation design should be measured as an execution system.

Useful metrics include:

- auction duration;
- minimum opening bid versus floor price;
- failed auction count;
- average time from health factor breach to sale;
- bad-debt estimate after each unsold auction.

### Lender liquidity run

The liquidity pool is the lender-side stress signal.

Useful metrics include:

- available ETH in the lending pool;
- pending withdrawal demand;
- utilization rate;
- lender withdrawal velocity;
- ratio of available ETH to loans in liquidation danger zones.

The same fields are summarized in [benddao-nft-lending-signals.csv](benddao-nft-lending-signals.csv) for dataset-based review.

| Signal                | Observation                                                              | Market-health interpretation                                        |
| --------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------- |
| BAYC concentration    | CoinDesk reported almost 3% of BAYC was collateralized on BendDAO        | Collection concentration can create correlated liquidation risk     |
| ETH reserve drain     | ForkLog reported only 12.5 WETH remained while about 15,000 ETH was owed | Available lender liquidity can collapse before auctions clear       |
| Bank-run behavior     | Decrypt described lenders withdrawing during liquidation stress          | First-exit incentives can worsen NFT lending solvency risk          |
| Auction rule pressure | BendDAO proposed shorter auctions and lower liquidation thresholds       | Liquidation parameters need to adapt to illiquid collateral         |
| Emergency governance  | BendDAO used an emergency proposal to change market parameters           | Governance changes are part of market health during collateral runs |

## Timeline

- **August 19, 2022:** CoinDesk reported that many Bored Ape NFTs backing BendDAO loans had entered liquidation danger zones.
- **August 21-22, 2022:** Lender withdrawals drained available ETH as NFT collateral auctions struggled to clear.
- **August 22-23, 2022:** [The Crypto Times reported](https://www.cryptotimes.io/2022/08/23/benddao-initiates-proposal-to-reduce-liquidity-threshold/) that BendDAO proposed changing liquidation thresholds, auction duration, interest rates, and first-bid limitations.
- **After the crisis:** The episode became a reference case for NFT lending protocols that depend on thin collateral floors and lender liquidity pools.

## Market Health Lessons

BendDAO shows that NFT lending needs risk metrics that connect collateral floors, bid depth, auction mechanics, and lender withdrawals. A floor price is not enough; the protocol needs to know whether enough buyers can absorb liquidated collateral quickly.

For Market Health, the warning signal is a combined loop: falling floor prices push loans toward liquidation, lenders withdraw ETH, auctions fail or clear slowly, and remaining lenders face greater liquidity risk. NFT-backed lending protocols should track that loop continuously and set liquidation parameters before a collection-wide floor decline becomes a run.
