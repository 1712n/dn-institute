---
title: "Pump and Dump Schemes in Cryptocurrency Markets: Identification Patterns and Real-World Examples"
date: 2025-02-10
entities:
  - Binance
  - Bittrex
  - Telegram
  - BTC
  - GVT
---

## Summary

1. **Pump and dump schemes** are coordinated efforts to artificially inflate the price of a low-liquidity cryptocurrency through misleading promotion, followed by rapid selling at the inflated price, resulting in losses for late participants.
2. **Telegram and Discord groups** have emerged as the primary coordination channels for organized pump and dump operations, with some groups exceeding 200,000 members and advertising scheduled pump events in advance.
3. **Quantitative analysis** of over 4,000 suspected pump and dump events across major exchanges reveals that the average pump achieves a 65% price increase within 5-10 minutes, followed by a 70-80% retracement within the first hour.
4. **Detection algorithms** based on volume anomalies, price spike characteristics, and social media signal analysis can identify pump and dump events with high accuracy, often in near-real time.
5. **Low market capitalization tokens** on exchanges with many altcoin listings are disproportionately targeted, with tokens below $10 million market capitalization accounting for the majority of identified pump and dump events.

## Introduction

Pump and dump schemes have a long history in traditional securities markets, where they are prohibited under securities fraud laws. The scheme involves three phases: accumulation (quietly buying a position), promotion (generating artificial excitement to drive up the price), and distribution (selling the position into the artificially elevated demand). In cryptocurrency markets, these schemes have taken on new dimensions due to the proliferation of low-liquidity tokens, the pseudonymous nature of trading, and the availability of instant global communication channels such as Telegram and Discord.

Research by [Xu and Livshits (2019)](https://doi.org/10.1145/3442381.3449757) at Imperial College London identified over 4,000 pump and dump events on cryptocurrency exchanges between January and July 2018 alone, involving hundreds of different tokens and coordinated through messaging platforms. Their findings demonstrate that pump and dump schemes are both systematic and prevalent in cryptocurrency markets.

## Anatomy of a Cryptocurrency Pump and Dump

### Phase 1: Target Selection and Accumulation

Pump organizers select target tokens based on specific characteristics that maximize the potential for price manipulation:

- **Low market capitalization**: Tokens with market caps below $10 million are strongly preferred, as less capital is required to move the price significantly.
- **Low daily trading volume**: Tokens with thin order books are more susceptible to sharp price movements from relatively modest buy pressure.
- **Availability on popular exchanges**: The target must be listed on exchanges where group members have accounts. Binance and Bittrex have historically been the most frequently targeted venues.
- **Sufficient liquidity to exit**: While low volume is preferred for the pump phase, the token must have enough liquidity for the organizers to sell their accumulated position during the dump phase.

During the accumulation phase, which may last days or weeks before the pump, organizers gradually build positions in the target token, taking care to avoid price increases that would alert other market participants. This pre-accumulation gives organizers a significant advantage over regular group members.

### Phase 2: The Pump - Coordinated Buying

The pump phase is typically initiated through a message in a Telegram or Discord group at a pre-announced time. The message reveals the target token and the exchange on which to buy. The buying activity proceeds in a predictable hierarchy:

1. **Inner circle** (organizers and premium members): Buy before or at the exact moment of announcement, capturing the lowest prices.
2. **Regular group members**: Buy within seconds to minutes of the announcement, paying increasingly higher prices.
3. **External participants**: Traders outside the group who observe the unusual price and volume activity and buy in, further inflating the price.

The price trajectory during the pump phase typically follows a convex curve, with the steepest gains in the first 1-3 minutes, followed by decelerating appreciation as selling pressure from early participants begins to mount.

### Phase 3: The Dump - Distribution and Collapse

The dump phase begins almost immediately after the peak, as organizers and early participants sell their accumulated holdings into the remaining buy orders. The price collapse is typically rapid and severe:

| Metric | Typical Range |
|--------|--------------|
| Time from pump start to peak | 3-10 minutes |
| Average peak price increase | 30-100% |
| Time from peak to 50% retracement | 5-30 minutes |
| Ultimate price recovery (after 24 hours) | 0-15% above pre-pump level |
| Average participant loss (excluding organizers) | 20-60% |

Research by [Kamps and Kleinberg (2018)](https://doi.org/10.1145/3301551.3301563) found that the average pump and dump event on Binance between 2017 and 2018 resulted in a 65% price increase and a return to near-baseline levels within one hour. The net wealth transfer from late participants to early participants and organizers was estimated at $3,500-$7,000 per event.

## Quantitative Detection Methods

### Volume Anomaly Detection

The most reliable early indicator of a pump and dump event is an abnormal spike in trading volume. A detection algorithm can flag potential pump events by monitoring:

- **Volume z-score**: Calculating the z-score of current volume relative to the trailing 24-hour or 7-day mean. A z-score exceeding 10-15 standard deviations is strongly indicative of a pump event for low-cap tokens.
- **Volume acceleration**: Measuring the rate of change in volume over short intervals (e.g., 1-minute candles). Pump events typically show volume increasing by 500-5,000% within the first 1-2 minutes.
- **Volume concentration**: Analyzing whether the volume spike is driven by a large number of small orders (consistent with coordinated group buying) or a small number of large orders (more typical of institutional activity or whale movements).

### Price Spike Characteristics

Pump and dump events produce distinctive price signatures that differentiate them from organic price movements:

- **Rise rate**: Prices increase at rates exceeding 0.5-1% per second during the initial pump phase, far faster than typical price discovery.
- **Candle pattern**: The pump produces a single elongated green candle followed by a series of declining red candles. The first candle often has an abnormally long upper wick, indicating intense selling at the peak.
- **Lack of consolidation**: Organic price increases typically include periods of consolidation and retracement. Pump events show continuous upward movement without consolidation, followed by an immediate reversal.
- **Bid-ask spread behavior**: The spread widens dramatically during the pump as ask-side liquidity is consumed, then collapses as the dump floods the ask side with sell orders.

### Order Book Dynamics

Monitoring order book changes during suspected pump events reveals characteristic patterns:

- **Ask-side depletion**: During the pump phase, ask orders are consumed rapidly at successively higher prices, with little replenishment between levels.
- **Bid-side buildup**: Buy orders accumulate at prices above the pre-pump level, placed by participants unaware that the pump is artificially driven.
- **Post-peak ask-side flooding**: When the dump begins, large sell orders appear at and below the current price, creating a wall of selling pressure that drives the price down.

### Social Media Signal Analysis

Monitoring Telegram groups, Discord servers, Twitter, and Reddit for pump signals provides early warning capability:

- **Scheduled pump announcements**: Many groups announce pump times hours or days in advance without specifying the token. The announcement itself signals that a pump event will occur.
- **Keyword detection**: Monitoring for terms such as "pump," "target," "buy signal," "moon," and exchange-specific terminology in known pump group channels.
- **Cross-platform correlation**: Simultaneous mentions of a previously obscure token across multiple platforms within a short time window is a strong indicator of coordinated promotion.

## Case Studies

### Case Study 1: GVT (Genesis Vision) Pump on Binance (2019)

On September 10, 2019, the Telegram group "Big Pump Signal" (over 70,000 members at the time) orchestrated a pump of Genesis Vision Token (GVT) on Binance. The event proceeded as follows:

1. **Pre-announcement**: The group announced a pump event scheduled for 19:00 UTC, without specifying the token.
2. **Announcement**: At exactly 19:00 UTC, the message "Coin: GVT" was posted to the group.
3. **Volume spike**: GVT/BTC trading volume on Binance increased from an average of approximately 5 BTC per hour to over 200 BTC within the first 5 minutes.
4. **Price impact**: The GVT/BTC price increased by approximately 40% within 3 minutes of the announcement.
5. **Collapse**: The price retraced to within 5% of the pre-pump level within 25 minutes.

Analysis of the order flow revealed that approximately 15% of the buy volume in the first 30 seconds was placed by a small number of accounts that had also placed buy orders in the 24 hours preceding the announcement, consistent with pre-accumulation by organizers.

### Case Study 2: Systematic Pump and Dump Activity on Bittrex (2018)

Research by [Li et al. (2021)](https://doi.org/10.1016/j.frl.2020.101604) identified a series of coordinated pump and dump events on Bittrex during 2018, targeting low-liquidity altcoins. The study found:

- **171 pump events** over a 6-month period, targeting 105 distinct tokens.
- **Average price increase**: 52% from the pre-pump price to the peak.
- **Average time to peak**: 7.2 minutes.
- **Token selection pattern**: 89% of targeted tokens had a daily volume below $100,000, and 78% had a market capitalization below $5 million.
- **Repeat targeting**: Some tokens were targeted multiple times, with intervals of 2-4 weeks between pump events, suggesting organizers return to tokens where the strategy has previously succeeded.

### Case Study 3: The "Squid Game" Token Rug Pull (2021)

While not a classic pump and dump in the coordinated group sense, the SQUID token incident illustrates how social media hype and market manipulation converge. In late October 2021, the SQUID token launched on PancakeSwap, capitalizing on the popularity of the Netflix series "Squid Game":

1. **Promotional phase**: The token's price surged from approximately $0.01 to over $2,800 within one week, driven by social media hype and news coverage.
2. **Liquidity trap**: The token's smart contract contained a mechanism preventing holders from selling, effectively creating a one-way market.
3. **Rug pull**: On November 1, 2021, the developers drained the liquidity pool, extracting an estimated $3.38 million.
4. **Price collapse**: The token price fell to near zero within minutes.

This case highlighted the intersection of smart contract manipulation and pump-and-dump dynamics in decentralized finance markets, and the need for automated analysis of token smart contract code as part of comprehensive market surveillance.

## Detection Using DNI Market Health API Metrics

The [DNI Market Health API](https://rapidapi.com/DNInstitute/api/crypto-market-health/) metrics provide several indicators relevant to pump and dump detection:

- **Volume Distribution**: During a pump event, the volume distribution deviates sharply from the expected power law pattern. An abnormal concentration of trades in mid-range size bins (consistent with coordinated group buying at similar order sizes) is a characteristic signature.
- **Buy/Sell Ratio**: The buy/sell ratio spikes to extreme values (>0.9) during the pump phase and then inverts (<0.1) during the dump phase. The speed and magnitude of this reversal distinguishes pump and dump events from organic demand-driven price increases.
- **Benford's Law Test**: During pump events, the first digit distribution of trade sizes may deviate significantly from Benford's Law, as many participants enter similar-sized orders (e.g., round numbers like 100 USDT, 500 USDT). A sudden drop in the benfordlawtest p-value concurrent with a volume spike is an indicator.
- **VWAP**: During a pump and dump, VWAP will lag significantly behind the spot price during the pump phase (as volume-weighted prices are pulled down by the lower-priced trades at the start), and then exceed the spot price during the dump phase. This VWAP-price divergence pattern is distinctive.
- **Trade Count**: A sharp increase in trade count, particularly when composed of many small trades rather than a few large ones, is consistent with coordinated group buying activity.

## Risk Factors and Vulnerability Assessment

Certain tokens and market conditions are more vulnerable to pump and dump manipulation:

### Token-Level Risk Factors

| Risk Factor | Low Risk | High Risk |
|------------|----------|-----------|
| Market capitalization | > $500M | < $10M |
| Daily trading volume | > $10M | < $100K |
| Number of exchange listings | > 10 | 1-3 |
| Token holder concentration | Top 10 hold < 30% | Top 10 hold > 60% |
| Project transparency | Audited, doxxed team | Anonymous team, no audit |

### Market Condition Risk Factors

- **Bull markets**: Pump and dump activity increases during bull markets when new retail participants enter the market and are more susceptible to FOMO-driven buying.
- **Weekend and holiday periods**: Lower overall market liquidity during weekends and holidays makes pump events more effective, as there are fewer sophisticated participants to absorb the artificial volume.
- **Post-listing periods**: Newly listed tokens are frequently targeted in the days following their exchange listing, when price discovery is still in progress and there is no established price history.

## Prevention and Mitigation

### For Exchanges

1. **Real-time volume and price monitoring**: Implementing automated alerts for abnormal volume spikes in low-liquidity pairs, with the ability to temporarily halt trading pending review.
2. **Account clustering analysis**: Identifying groups of accounts that consistently trade the same low-liquidity tokens within short time windows, potentially representing members of the same pump group.
3. **Position limit monitoring**: Flagging accounts that accumulate significant positions in low-liquidity tokens in the days before a pump event.
4. **Post-event analysis**: Conducting forensic analysis after identified pump events to trace the flow of funds and identify organizer accounts for potential account suspension and regulatory referral.

### For Traders

1. **Volume verification**: Before entering a position in a rapidly appreciating low-cap token, check whether the volume increase is accompanied by genuine news or developments, or whether it appears to be purely speculative.
2. **Social media awareness**: Be aware that unsolicited recommendations for obscure tokens on social media platforms are a common component of pump and dump promotion.
3. **Order book inspection**: Examine the order book for thin liquidity and wide spreads, which indicate vulnerability to manipulation and difficulty in exiting a position at a favorable price.

## Conclusion

Pump and dump schemes remain one of the most prevalent forms of market manipulation in cryptocurrency markets. The combination of low-liquidity tokens, pseudonymous trading, and instant global communication creates an environment that is structurally conducive to these schemes. Quantitative detection methods based on volume anomalies, price characteristics, and order book dynamics can identify pump and dump events with high accuracy, and integration with social media monitoring further enhances detection capability. As regulatory frameworks mature and exchanges implement more sophisticated surveillance tools, the risk-reward calculus for pump and dump organizers is shifting, but continued vigilance from market participants, exchanges, and regulators is essential.

## References and Further Reading

- [Xu, J. & Livshits, B. (2019). The Anatomy of a Cryptocurrency Pump-and-Dump Scheme](https://doi.org/10.1145/3442381.3449757)
- [Kamps, J. & Kleinberg, B. (2018). To the Moon: Defining and Detecting Cryptocurrency Pump-and-Dumps](https://doi.org/10.1145/3301551.3301563)
- [Li, T. et al. (2021). Cryptocurrency Pump-and-Dump Schemes](https://doi.org/10.1016/j.frl.2020.101604)
- [Victor, F. & Hagemann, T. (2019). Cryptocurrency Pump and Dump Schemes: Quantification and Detection](https://doi.org/10.1109/BRAINS49436.2019.9325232)
- [Hamrick, J. T. et al. (2021). An examination of the cryptocurrency pump-and-dump ecosystem](https://doi.org/10.1016/j.infoeam.2020.100338)
- [CFTC Customer Advisory: Beware Virtual Currency Pump-and-Dump Schemes](https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/CustomerAdvisory_PumpAndDump0218.html)
- [Bitwise Report. Market Manipulation Chapter](https://www.sec.gov/comments/sr-nysearca-2019-01/srnysearca201901-5164833-183434.pdf)
