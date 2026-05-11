---
title: "Mining Capital Coin Trading Bots and Bitchain Redemption"
date: 2022-05-06
entities:
  - Mining Capital Coin
  - MCC International Corp.
  - Luiz Carlos Capuci Jr.
  - Emerson Souza Pires
  - Capital Coin
  - Bitchain Exchanges
---

## Summary

This case study analyzes Mining Capital Coin (MCC) as a market-health warning about crypto investment programs that combine daily return promises, trading-bot claims, issuer tokens, and fake redemption venues. On May 6, 2022, the SEC announced fraud charges against MCC International Corp., which did business as Mining Capital Coin Corp.; founders Luiz Carlos Capuci Jr. and Emerson Souza Pires; CPTLCoin Corp.; and Bitchain Exchanges in connection with unregistered offerings and fraudulent sales of investment plans called mining packages.

The SEC said MCC, Capuci, and Pires sold mining packages to 65,535 investors worldwide and promised daily returns of 1 percent, paid weekly, for up to 52 weeks. MCC allegedly represented that weekly profits came from cryptocurrency mining, stock and forex trading, and cryptocurrency trading on digital asset platforms through arbitrage and semi-automatic robotic trading.

The market-health problem was that the promised trading and redemption signals allegedly did not map to real market activity. The SEC alleged that investors were initially promised bitcoin returns but were later required to withdraw in MCC's own Capital Coin token, and then redeem Capital Coin on Bitchain, a fake crypto asset trading platform created and managed by Capuci. DOJ separately announced an indictment alleging that Capuci fraudulently marketed MCC trading bots and was not using those bots to generate investor income.

The supporting dataset is available in [mcc-summary.csv](mcc-summary.csv).

## Trading Narrative

MCC marketed mining packages as income-generating crypto investment plans. According to the SEC, the defendants promised 1 percent daily returns paid weekly and represented that the weekly profits came from several sources: mining, stock and forex trading, cryptocurrency arbitrage, and semi-automatic robotic trading on digital asset platforms.

The SEC also alleged a redemption shift. In the early days, investors were promised returns in bitcoin. Later, defendants allegedly required investors to withdraw in Capital Coin, MCC's own token. Investors then had to redeem Capital Coin on Bitchain, which the SEC described as a fake crypto asset trading platform created and managed by Capuci.

That sequence created multiple false market signals. A daily return promised in bitcoin implied liquid mining or trading income. A proprietary token introduced issuer-controlled settlement risk. A fake trading platform gave investors an apparent venue for redemption while keeping exit mechanics under the promoter's control.

DOJ's indictment release described a parallel trading-bot narrative. It said Capuci touted MCC trading bots as an additional investment mechanism, claimed the bots used new technology from top software developers, and represented that they could perform thousands of trades per second and generate daily returns. DOJ alleged Capuci did not use MCC trading bots to generate income for investors and instead diverted funds to himself and co-conspirators.

## False Market Signals

### One-percent daily returns

Daily return promises imply repeatable market edge and stable liquidity. In a real mining or trading operation, profits should reconcile to mining rewards, trading venue records, fees, custody balances, realized gains, and losses. A fixed daily return claim should be treated as a hypothesis to verify, not as evidence.

### Multiple profit engines

MCC allegedly cited mining, stocks, forex, cryptocurrency arbitrage, and robotic trading as sources of weekly profits. Multiple profit engines can make a scheme look diversified, but they also increase the need for separate evidence. Each source should have its own records, counterparties, venues, and risk history.

### Trading-bot throughput claims

DOJ said Capuci marketed bots that could perform thousands of trades per second and generate daily returns. Throughput is not profitability. A legitimate high-frequency or automated strategy should produce order logs, execution timestamps, venue confirmations, realized P&L, and failure cases.

### Forced Capital Coin withdrawals

The alleged switch from bitcoin returns to Capital Coin withdrawals changed the exit asset. That is a market-health warning because the promised return asset and the redemption asset no longer matched. Forced conversion to an issuer token can hide whether liquid assets are available.

### Fake redemption platform

The SEC described Bitchain as a fake crypto asset trading platform created and managed by Capuci. A redemption platform controlled by the promoter is not independent market infrastructure. Analysts should verify platform ownership, market depth, wallet flows, order books, and actual withdrawal ability.

## Event Timeline

| Date or period      | Event                                                                                  | Market-health signal                                                           |
| ------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| January 2018 onward | MCC, Capuci, and Pires sold mining packages to investors.                              | Daily return promises were tied to mining and trading narratives.              |
| Relevant SEC period | The SEC said 65,535 investors worldwide bought mining packages.                        | Large distribution required proof of real profit sources.                      |
| Relevant SEC period | MCC allegedly promised 1 percent daily returns, paid weekly, for up to 52 weeks.       | Stable return claims required mining, trading, and custody reconciliation.     |
| Relevant SEC period | MCC allegedly cited mining, stock and forex trading, crypto arbitrage, and bots.       | Multiple profit-engine claims needed separate evidence.                        |
| Later scheme phase  | Investors were allegedly required to withdraw in Capital Coin instead of bitcoin.      | Redemption asset substitution signaled liquidity and issuer-control risk.      |
| Later scheme phase  | Investors allegedly had to redeem Capital Coin on Bitchain.                            | A fake platform claim created synthetic exit liquidity.                        |
| April 21, 2022      | Federal court issued a temporary restraining order and asset freeze, according to SEC. | Court intervention preserved assets and halted the alleged enterprise.         |
| May 6, 2022         | The SEC announced civil fraud charges.                                                 | SEC challenged the mining, trading, token, and platform representations.       |
| May 6, 2022         | DOJ announced Capuci's indictment.                                                     | DOJ alleged a $62 million scheme and fraudulent marketing of MCC trading bots. |

## Detection Checklist

1. Reconcile daily return claims to source-specific records for mining, trading, arbitrage, and bot activity.
2. Require independent exchange or broker statements before accepting trading-bot claims.
3. Compare promised bitcoin returns with the actual asset used for withdrawals.
4. Verify whether a redemption platform is independently operated and whether withdrawals settle to external wallets.
5. Treat issuer-token substitutions as a liquidity warning, especially when the original promised asset was bitcoin.
6. Separate referral, membership, and initiation fees from market-generated profits.
7. Test whether claimed high-frequency bot activity appears in venue order logs and execution records.
8. Preserve legal posture: this article relies on SEC allegations and DOJ indictment allegations.

## Market-Health Lessons

Mining Capital Coin shows how a crypto investment program can layer market stories until the underlying evidence becomes hard for investors to test. Mining, arbitrage, forex, robotic trading, Capital Coin, and Bitchain each sounded like a separate source of liquidity or returns. The SEC and DOJ allegations point to the opposite risk: the signals were under promoter control.

The practical market-health control is to reduce each claim to an independently verifiable record. Mining returns should reconcile to hashpower and rewards. Trading returns should reconcile to venue statements. Bot activity should reconcile to orders and fills. Token redemptions should reconcile to external liquidity. If withdrawals require an issuer token on a promoter-controlled platform, the displayed exit path should be treated as unverified.

## References

- [SEC press release 2022-81, May 6, 2022](https://www.sec.gov/newsroom/press-releases/2022-81)
- [DOJ press release 22-479, May 6, 2022](https://www.justice.gov/archives/opa/pr/ceo-mining-capital-coin-indicted-62-million-cryptocurrency-fraud-scheme)
