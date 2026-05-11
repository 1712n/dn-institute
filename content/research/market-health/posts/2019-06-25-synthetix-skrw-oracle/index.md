---
title: "Synthetix sKRW Oracle Error and Automated Arbitrage"
date: "2019-06-25"
description: "A faulty Korean won price feed created an artificial sKRW market on Synthetix, allowing an automated trading bot to convert the mispriced asset into sETH before trades were reversed."
entities:
  - Synthetix
  - sKRW
  - sETH
  - KRW
---

On June 25, 2019, Synthetix disclosed an oracle incident in which its Korean won price feed reported KRW at roughly 1000 times the correct rate. The error did not require an attacker to compromise Synthetix contracts or manipulate the external data provider directly. Instead, an automated trading bot detected the mispriced synthetic asset and traded through it while Synthetix.exchange was still accepting the rate.

The result was a short-lived but extreme market-health failure: Synthetix reported several trades with 1000x profits and more than $1 billion in apparent profit in less than one hour. The Block separately reported that the bot accumulated more than 37 million sETH, while noting that the true dollar impact was hard to value because sETH liquidity was limited. Synthetix later said the bot owner agreed to reverse the trades in exchange for a bug bounty.

## Manipulation signal

The abnormal signal was not wash trading in the usual sense of one party trading with itself to inflate volume. It was a price-integrity failure that created an executable false market. The sKRW venue briefly priced a synthetic fiat asset as though KRW had moved by orders of magnitude, while other markets and real-world FX rates had not.

This makes the incident useful for market-health monitoring because it shows how a venue can display apparently valid executed trades even when the tradeable price is detached from the underlying reference asset. In a synthetic-asset exchange, the oracle price is the order book's economic anchor. When that anchor fails, automated arbitrage can convert an oracle-data anomaly into distorted volume, artificial profit, and debt-pool losses for other participants.

| Indicator                       | Observed value                                  | Market-health interpretation                                                               |
| ------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Reference price deviation       | KRW feed reported about 1000x the correct rate  | Synthetic asset price was detached from its underlying fiat market                         |
| Exploit window                  | Less than one hour, according to Synthetix      | Automated strategies can monetize bad oracle states faster than manual operators can react |
| Apparent profit                 | More than $1 billion reported by Synthetix      | Reported venue PnL and volume became economically meaningless during the bad-price window  |
| Exposed synthetic asset balance | More than 37 million sETH reported by The Block | A single price-feed failure could spill into another synthetic asset market                |
| Resolution                      | Trades reversed after contact with bot owner    | Final loss was mitigated socially, not by a purely market-native control                   |

## Failure chain

Synthetix said it used multiple commercial APIs for FX, commodities, and crypto price feeds. One API began intermittently reporting KRW at roughly 1000 times the current rate. Synthetix also said the outlier filter should have absorbed the error, but the KRW feed was only being served by two APIs because of an unrelated earlier outage. With fewer inputs available, the oracle averaged the two remaining prices and sent the bad KRW rate to the exchange-rates contract.

That failure chain left the trading system with two important weaknesses:

1. The venue accepted a large isolated price move in one synthetic fiat market.
2. Trades using the bad sKRW price were still composable with other synth markets, including sETH.

The bot did not need to create false public demand for sKRW. It only needed to recognize that Synthetix.exchange had published an economically impossible conversion rate. By moving into and out of sKRW while the bad feed was live, the bot transformed an oracle input error into a market event visible as outsized executed trades and synthetic profit.

## Why this matters for market health

Market-health analysis usually focuses on executed order feeds, trade-size distributions, wash-trading clusters, and venue-level volume. The Synthetix incident shows that those metrics also depend on reference-data integrity. If a venue's price source is corrupted, the downstream trade feed can look active and profitable while measuring a broken market state.

For synthetic assets and derivatives venues, useful monitoring should include:

- deviation checks between the venue's executable price and independent reference prices;
- stale-feed checks before a synthetic asset can be used in cross-asset exchange paths;
- circuit breakers that halt a market when an underlying reference asset moves beyond plausible bounds;
- cross-market impact analysis when one mispriced asset can be converted into another synthetic asset;
- post-incident labeling so suspicious volume from bad oracle windows is not treated as organic demand.

The incident also shows why social reversibility is not a complete control. Synthetix was able to contact the bot owner and negotiate a reversal, but a market-health framework should treat that as mitigation after failure, not as proof that the market remained healthy.

## Source dataset

The supporting event timeline is included in `timeline.csv`. It records the incident date, reported metrics, and public source links used for the analysis.

## References

- [Synthetix response to oracle incident](https://blog.synthetix.io/response-to-oracle-incident/)
- [The Block report on the sKRW oracle incident](https://www.theblock.co/post/28748/synthetix-suffers-oracle-attack-potentially-looting-37-million-synthetic-ether)
- [CoinDesk report on the trade reversal](https://www.coindesk.com/markets/2019/06/25/synthetix-trader-rolls-back-broken-trades-that-netted-1-billion-profit)
