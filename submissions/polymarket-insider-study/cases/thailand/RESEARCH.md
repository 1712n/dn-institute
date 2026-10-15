# Case selection and coverage search

Search date: 15 October 2026 UTC. Sources: Polymarket's public APIs and web search results.

## Choosing the case

I reviewed closed-market metadata and downloaded trades for 13 candidates, choosing them manually with the outcomes already known. The [screening table](artifacts/screened_markets.csv) records their IDs, cutoffs and rejection reasons. This package includes source responses for Thailand only.

The bank-failure market had no eligible buyer at the morning cutoff, and its large purchases on 30 January came after the bank closed at 23:00 UTC. Ciena, Vertiv, two Steam Awards markets, Wildflower, Hamnet and Wagner Moura had no eligible wallets at their initial cutoffs. DraftKings already had press discussion of possible insider betting. Culinary Class Wars had public winner leaks. Bad Bunny and Bucharest produced eligible wallets, but I chose to inspect Thailand because buying at low prices was followed by a large, focused position in the wallet history.

I kept the $500 minimum and score weights unchanged. The 72-hour spending total describes wallet 2's activity after selection; it does not enter the score. Since I selected the cases manually after their outcomes, this exercise cannot measure the method's success rate.

References used to reject candidates include the [Illinois bank closure notice](https://idfpr.illinois.gov/content/dam/soi/en/web/idfpr/news/2026/2026-1-30-idfpr-dob-release-metropolitan-capital-bank.pdf), [earlier DraftKings discussion](https://www.casino.org/news/employers-need-to-be-vigilant-on-prediction-markets-insider-trading-says-law-firm//), and the [Culinary Class Wars producer's account of leaks](https://news.sbs.co.kr/english/article.do?news_id=N1008407443).

## Prior coverage

I inspected returned results for these queries:

- `Polymarket "Thailand" "insider" election 2026`
- `Polymarket "Bhumjaithai" wallet`
- `"0x61f2853af4d13ff71d7a3c9dc5f1a5f6e7788519"`
- `"0x1cfc6f041b5b8dad3c14b867be8482a69d45b8e0"`
- `"Polymarket" "Bhumjaithai" insider trading`
- `"โพลีมาร์เก็ต" "ภูมิใจไทย" "วงใน"`
- `"Polymarket" "Thailand election" trader`
- `"Polymarket" "Bhumjaithai" bet trader 2026`
- `"1cfc6f04" polymarket`
- `"Alumer" "Thailand" Polymarket`
- `"0x1cfc6f041b5b8dad3c14b867be8482a69d45b8e0" -site:polygonscan.com`
- `"Polymarket" "Thailand" "124,000"`
- `"Polymarket" "Bhumjaithai" "whale"`
- `"Polymarket" "ภูมิใจไทย"`
- `"86shin" Polymarket Thailand`
- `"86shin" insider`
- `"0x1cfc6f" election`
- `"Polymarket" "ภูมิใจไทย" "วงใน"`

The address search returned [PolygonScan](https://polygonscan.com/address/0x1cfc6f041b5b8dad3c14b867be8482a69d45b8e0) and an [automated Polycopy profile](https://polycopy.app/trader/0x1cfc6f041b5b8dad3c14b867be8482a69d45b8e0). The profile uses `86shin` and lists a successful Bhumjaithai position. I excluded its changing profit figures from the calculations. I have not linked the profile name to a real person.

I found general market coverage in [Siam Blockchain](https://siamblockchain.com/2026/01/04/thai-election-polymarket/), [Naewna](https://www.naewna.com/politic/columnist/65411) and [Prachachat](https://www.prachachat.net/world/news-1961061), plus market data sites. None of the returned results was a press investigation of this wallet's pre-election purchases. This leaves gaps for unindexed articles, private groups, deleted posts and other languages.

## Collection notes

- The score covers only Bhumjaithai taker trades and uses the same function as the Maduro case.
- Ranks 2, 3 and 4 have trade-history downloads covering the full requested period. Requests were checked for wallet and time bounds, with capped windows split.
- Rank 1 has two requests capped at 100 records: the earliest trades since 1 November and the latest trades in the final 24 hours. The earlier sample hit the cap; the recent request returned one record. I stopped the much larger full-history download and excluded its partial results from the totals.
- Activity records include maker and taker trades, so they overlap with the market file. They provide context and do not enter the score.
- One Polygon receipt and its matching block are saved. The check compares net bridged-USDC and ERC-1155 transfers with the market API record, including its token ID.
- Funding, wider transfer history, redemptions, ownership and off-platform positions remain unchecked. The purchase totals do not establish final holdings or profit.
