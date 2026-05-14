---
title: "MakerDAO Black Thursday Zero-Bid Auction Stress"
date: 2020-03-12
entities:
  - MakerDAO
  - DAI
  - ETH
  - MKR
  - Blocknative
---

## Summary

On March 12, 2020, the crypto-market crash known as Black Thursday pushed MakerDAO's liquidation system into a severe auction failure mode. [MakerDAO's post-event writeup](https://web.archive.org/web/20200401163841/https://blog.makerdao.com/the-market-collapse-of-march-12-2020-how-it-impacted-makerdao/) described how ETH price volatility, Ethereum congestion, and DAI liquidity stress affected vault liquidations and protocol debt.

The most important market-abuse signal was the zero-bid auction outcome. [CoinDesk reported](https://www.coindesk.com/tech/2020/07/22/mempool-manipulation-enabled-theft-of-8m-in-makerdao-collateral-on-black-thursday-report) on Blocknative research finding that mempool congestion and transaction-spam dynamics helped one keeper win MakerDAO collateral auctions with zero DAI bids, taking about $8 million in collateral. [CoinDesk later reported](https://www.coindesk.com/tech/2020/09/23/makerdao-users-hosed-by-march-flash-crash-wont-get-mkr-payouts-say-mkr-whales) that affected vault users would not receive MKR-funded compensation after governance rejected a payout.

This case is useful for Market Health because it connects external market volatility, network congestion, liquidation-market design, keeper competition, and governance recovery decisions. The exploit path did not require stealing private keys or changing oracle prices. It exploited auction market structure at the exact moment when normal bidders could not reliably compete.

## Manipulation Analysis

Black Thursday shows how mempool and auction-market manipulation can convert a market crash into a collateral-transfer event. A fair liquidation auction assumes that multiple keepers can observe, bid, and settle. When gas congestion blocks most competitors, a single keeper can submit zero or near-zero bids and still win.

The first vector is transaction-priority control. A keeper that can get auction bids included while competitors are delayed by gas prices or spam can win collateral without paying economic value. The relevant surveillance metric is not simply auction price; it is auction price conditional on mempool congestion, competing keeper activity, and bid inclusion latency.

The second vector is auction-duration mismatch. CoinDesk reported that the relevant auctions lasted about 10 minutes, or only a few dozen Ethereum blocks. During an extreme gas event, that window can be too short for competitive bidding. Attackers do not need to manipulate the collateral price if they can manipulate or exploit bidder access during a short auction.

The third vector is DAI liquidity stress. If keepers cannot source DAI quickly, even rational bidders may be unable to compete. Liquidation-market health therefore depends on both collateral liquidity and settlement-asset liquidity.

## Metrics Used

### Zero-bid auction share

The clearest signal is the number and value of auctions that settle at zero or near-zero DAI. A healthy liquidation market should almost never transfer valuable ETH collateral for zero settlement value.

Useful metrics include:

- count of zero-bid and near-zero-bid auctions;
- collateral value won at zero or near-zero bids;
- number of unique winning keepers;
- number of competing bids per auction;
- bid spread between winner and next-best bidder.

### Mempool congestion and inclusion latency

Auction fairness depends on who can get transactions included. Market Health monitoring should compare auction outcomes with network congestion and bid-inclusion delays.

Useful metrics include:

- median and p95 gas price during liquidation windows;
- pending transaction count during active auctions;
- bid transaction latency by keeper;
- failed or replaced bid transactions;
- share of auctions ending before competing bids landed.

### Keeper concentration

Maker's collateral auctions depend on external keepers. If only one or two keepers are active during stress, liquidation quality becomes fragile.

Useful keeper metrics include:

- active keeper count by auction type;
- winning keeper concentration;
- keeper balances in DAI and ETH;
- keeper uptime during high-gas blocks;
- keeper bid frequency before and during market crashes.

### Protocol bad debt and user loss

Zero-bid auctions created both protocol debt and vault-user losses. These need separate accounting because the protocol can recapitalize while individual users remain uncompensated.

Useful loss metrics include:

- DAI bad debt created by failed auctions;
- user collateral lost in zero-bid auctions;
- MKR minted or auctioned to recapitalize the protocol;
- compensation proposal status;
- time between event, governance vote, and final recovery decision.

The same fields are summarized in [makerdao-black-thursday-signals.csv](makerdao-black-thursday-signals.csv) for dataset-based review.

| Signal                | Observation                                                                 | Market-health interpretation                                       |
| --------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| Zero-bid collateral   | Reporting cites roughly $8 million in collateral won at zero bids           | Liquidation auctions failed to produce competitive clearing prices |
| Mempool manipulation  | Blocknative research linked transaction spam/congestion to auction outcomes | Network-layer access can become a market-abuse vector              |
| Short auction window  | Auctions lasted about 10 minutes during extreme congestion                  | Auction duration must be stress-tested against gas conditions      |
| Protocol debt         | MakerDAO needed recapitalization after failed liquidations                  | Liquidation-market failure can become protocol solvency risk       |
| Compensation rejected | Governance rejected MKR-funded compensation for vault users                 | Recovery policy affects long-tail market confidence                |

## Timeline

- **March 12, 2020:** ETH fell sharply, Ethereum gas prices spiked, and Maker vault liquidations accelerated.
- **March 12-13, 2020:** Some collateral auctions cleared with zero DAI bids while other keepers could not compete effectively.
- **March 2020:** MakerDAO prepared MKR auctions to recapitalize protocol debt created by failed liquidations.
- **July 2020:** CoinDesk reported on Blocknative research tying mempool manipulation and congestion to the zero-bid auction outcomes.
- **September 2020:** MakerDAO governance rejected a compensation payout for affected Black Thursday vault users.

## Market Health Lessons

MakerDAO Black Thursday shows that liquidation markets need the same surveillance as spot and derivatives markets. The abuse vector can be transaction ordering, keeper access, settlement-asset liquidity, or auction-duration design rather than a direct price-feed attack.

For market-health dashboards, liquidation systems should monitor zero-bid auction share, keeper concentration, gas-adjusted bid latency, settlement-asset liquidity, and bad-debt creation in real time. If competitive bidding disappears during congestion, the system should extend auctions, raise minimum bids, pause liquidations, or route collateral through mechanisms that do not depend on a thin keeper set.
