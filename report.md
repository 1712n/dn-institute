[report.md](https://github.com/user-attachments/files/33229228/report.md)
# Investigation of Potential Informed Trading on Polymarket

## 1. Objective

The goal of this research is to identify Polymarket wallets whose trading behavior may be consistent with having better or earlier information than other market participants.

This analysis does **not** prove that any wallet belongs to an insider. Instead, I use the term **potentially informed trading** and treat the identified wallets as candidates for further investigation.

---

## 2. Data

I used publicly available Polymarket market and trade data.

**Research period:** November 1, 2025 – May 1, 2026

First, I collected all markets that closed during this period. There were **1,161 markets**.

To keep the analysis manageable, I selected the **30 markets with the highest trading volume**.

For these markets, I collected approximately **1.33 million historical trades**.

After limiting the trades to the research period, the dataset contained:

- **383,615 trades**
- **96,039 unique wallets**

### Scope limitation

The top-30 markets are not fully independent observations. For example, the dataset contains multiple markets related to the same real-world event, such as different candidates in the NYC mayoral election and different NFL teams.

Therefore, repeat activity across related markets should not be interpreted as completely independent evidence.

---

## 3. Screening Methodology

I used several simple and explainable signals to identify potentially interesting wallets.

| Signal | Rule | Why it matters |
|---|---|---|
| Winning outcome | Bought the outcome that eventually won | Initial screening signal |
| Timing | Purchase made 6–72h before resolution | Focuses on potentially informative late positioning |
| Trade size | Position of at least $1,000 | Removes very small trades |
| 6h price movement | Favorable price movement after entry | Measures whether the entry was well timed |
| Repeatability | Similar activity across multiple markets | Reduces the importance of one-off successful trades |
| Bot-like activity | Extremely high trading frequency | Downweighted because it may indicate automated trading rather than information advantage |

### 3.1. Buying the Winning Outcome

First, I looked at purchases of the outcome that eventually won.

This signal alone is weak because successful traders are common. It was therefore used as an initial filter rather than as evidence of insider trading.

### 3.2. Timing

I focused on purchases made **6–72 hours before market resolution**.

The intuition is that a large position shortly before an event resolves may be more interesting than a position taken weeks or months earlier.

### 3.3. Trade Size

I considered purchases of at least **$1,000**.

This removes a large number of small trades and focuses the investigation on positions that are more economically meaningful.

### 3.4. Price Movement After Entry

For each qualifying purchase, I measured the maximum price of the same outcome during the following six hours.

For example:

- trader buys at 0.80;
- the outcome reaches 0.90 during the following six hours;
- the measured price movement is **+10 percentage points**.

This is **not realized profit or P&L**. It is only a measure of how favorable the entry was shortly after the trade.

### 3.5. Repeatability

I checked whether similar behavior appeared across multiple markets.

One successful trade can easily be explained by luck.

Repeated large positions on eventual winners across several markets are more interesting and therefore receive higher investigation priority.

### 3.6. Bot-like Activity

Some wallets trade extremely frequently and may behave like automated market makers or trading bots.

For example, one wallet in the dataset made more than 3,000 trades on a single market.

I did not treat this behavior as strong evidence of insider trading and reduced its priority in the ranking.

---

## 4. Ranking Methodology

The ranking is an **investigation-priority score**, not a probability of insider trading.

The main components considered were:

- number of different markets;
- total notional of qualifying positions;
- average entry price;
- timing relative to resolution;
- favorable price movement after entry;
- repeatability across markets;
- signs of bot-like activity.

The purpose of the ranking is to answer:

> Which wallets would be most useful to investigate manually first?

It is not intended to answer:

> What is the probability that this wallet is an insider?

---

## 5. Main Candidates

The screening produced a shortlist of wallets with particularly interesting combinations of size, timing, repeatability and favorable subsequent price movement.

### Ranking overview

| Rank | Wallet      | Markets | Qualifying Notional | Avg. Entry | Avg. 6h Move | Priority |
|---:  |---          |---:     |---:                 |---:        |---:          |---       |
| 1    | `0x24c8...` | 4       | ~$125K              | 0.940      | +2.95 pp     | High     |
| 2    | `0x7c3d...` | 3       | ~$72K               | 0.939      | +4.15 pp     | High     |
| 3    | `0xd218...` | 4       | ~$397K              | 0.949      | +1.89 pp     | High     |
| 4    | `0x0c4b...` | 3       | ~$216K              | 0.925      | +3.31 pp     | High     |
| 5    | `0xbacd...` | 3       | ~$30K               | 0.869      | +5.28 pp     | High     |

These five wallets were selected for manual review because they combined multiple signals rather than because of any single trade.

### 5.1. `0x24c8...`

This is one of the cleanest patterns in the dataset.

The wallet made several relatively large purchases close to market resolution, particularly in the Mamdani market.

Several entries were followed by favorable price movements of approximately 2–5 percentage points.

Examples include purchases around:

- 0.932–0.934 in the Mamdani market;
- approximately $17K–$42K positions around 12 hours before resolution;
- a ~$21K position on Andrew Cuomo around 8 hours before resolution.

The repeated nature of these entries makes this wallet particularly interesting.

### 5.2. `0x7c3d...`

This wallet showed several relatively early entries at lower prices followed by larger favorable movements.

The strongest examples were in the Trump UFO market, where some entries were followed by price movements of approximately **+8–13 percentage points**.

This combination of relatively early positioning, meaningful trade size and repeated favorable movement makes the wallet a high-priority candidate.

### 5.3. `0xd218...`

This wallet stands out primarily because of its size and repeatability.

It had approximately **$397K** in qualifying trades across four markets.

There is, however, an important caveat: a significant portion of its activity was at prices close to **0.999**.

Such trades are less informative because the market outcome was already priced as almost certain.

Therefore, this wallet is interesting because of its scale and repeatability, but its raw volume should not be interpreted as direct evidence of informed trading.

### 5.4. `0x0c4b...`

This wallet made relatively large purchases across several markets.

The more interesting positions were earlier purchases at lower prices, followed by additional upward price movement.

For example, several trades in the Trump UFO market were made between approximately 0.86 and 0.94 and were followed by favorable movements of several percentage points.

The pattern is interesting, although there is not enough evidence to distinguish informed trading from a strong trading strategy or good market analysis.

### 5.5. `0xbacd...`

This wallet had a smaller overall volume but some of the strongest individual examples.

In the Trump UFO market, several positions were followed by large favorable price movements.

Examples include:

- entry at **0.600 → approximately +23 pp**
- entry at **0.661 → approximately +17 pp**
- entry at **0.837 → approximately +2 pp**

These trades make the wallet particularly interesting for manual investigation, despite its smaller total notional.

---

## 6. Examples of Trades Driving Investigation Priority

The following trades illustrate why the wallets above received higher investigation priority.

| Wallet      | Market               | Entry Price | Position | Hours Before Resolution | Max 6h Move |
|---          |---                   |---:         |---:      |---:                     |---:         |
| `0x24c8...` | Mamdani              | 0.934       | ~$41.6K  | 11.8h                   | +2.5 pp     |
| `0x24c8...` | Andrew Cuomo         | 0.940       | ~$21.1K  | 8.3h                    | +5.9 pp     |
| `0x7c3d...` | Trump UFO            | 0.858       | ~$2.2K   | 21.8h                   | +13.3 pp    |
| `0x7c3d...` | Trump UFO            | 0.910       | ~$2.9K   | 21.1h                   | +8.1 pp     |
| `0xbacd...` | Trump UFO            | 0.600       | ~$1.3K   | 50.2h                   | +23.0 pp    |
| `0xbacd...` | Trump UFO            | 0.661       | ~$1.5K   | 49.4h                   | +16.9 pp    |
| `0xd218...` | New England Patriots | 0.678       | ~$2.0K   | 7.9h                    | +32.1 pp    |

These examples should be interpreted as **screening evidence**, not as proof of insider knowledge.

In particular, the six-hour price movement is a market-price metric rather than realized trader profit.

---

## 7. What Did We Find?

The research **does not allow us to say that we found actual insiders**.

Instead, we found several wallets that:

- frequently selected the correct outcome;
- made relatively large trades;
- sometimes entered shortly before resolution;
- showed favorable price movement after entry;
- repeated similar behavior across multiple markets.

The main candidates are:

1. `0x24c8...`
2. `0x7c3d...`
3. `0xd218...`
4. `0x0c4b...`
5. `0xbacd...`

There may be completely normal explanations for this behavior, including:

- strong market analysis;
- faster interpretation of public information;
- arbitrage;
- market-making or systematic trading;
- correlated positions across related markets;
- or simply luck.

The analysis therefore identifies **investigation candidates rather than confirmed insiders**.

---

## 8. Limitations

There are several important limitations to this analysis.

### Retrospective selection

The analysis uses the final market outcome to identify successful trades. This creates an unavoidable retrospective bias.

### No proof of information advantage

Correctly predicting an outcome does not prove access to non-public information.

### Price movement is not P&L

The six-hour price movement measures how the market moved after entry. It does not account for whether the trader actually sold, held the position, or realized a profit.

### Related markets

The selected top-30 markets are not fully independent. Several markets may correspond to the same underlying real-world event.

### Automated trading

Some wallets may be bots, market makers or arbitrageurs. Their high success rate may have little to do with insider information.

### Public data only

This investigation uses public blockchain and Polymarket data. It does not attempt to identify the real-world owner of any wallet or access private communications.

### Limited market scope

The analysis focuses on the 30 highest-volume markets rather than every market on Polymarket. This makes the investigation more manageable but means that potentially interesting behavior in lower-volume markets may have been missed.

---

## 9. Conclusion

The main result of this research is not proof of insider trading, but a **shortlist of wallets with unusually interesting trading behavior**.

The approach is intentionally simple and explainable:

**position size + timing + repeatability + favorable price movement**

This makes it possible to explain why a particular wallet received a higher investigation priority without relying on an opaque machine-learning model.

The five highest-priority candidates identified in this analysis are:

| Priority | Wallet      | Main Reason for Investigation                                            |
|---:      |---          |---                                                                       |
| 1        | `0x24c8...` | Repeated large entries close to resolution with favorable movement       |
| 2        | `0x7c3d...` | Several lower-price entries followed by strong upward movement           |
| 3        | `0xd218...` | Large and repeated activity across markets, with some very strong trades |
| 4        | `0x0c4b...` | Large repeated positions across several markets                          |
| 5        | `0xbacd...` | Smaller volume but unusually strong individual entries                   |

A useful next step would be to compare these wallets against a larger sample of ordinary traders and measure whether their timing and post-entry performance are statistically unusual. Another useful extension would be to investigate activity immediately before specific real-world events and compare trading behavior with the timing of public information releases.
