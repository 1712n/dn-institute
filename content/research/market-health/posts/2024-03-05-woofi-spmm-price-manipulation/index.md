---
title: "WOOFi sPMM price-manipulation market-health case"
date: "2024-03-05"
description: "WOOFi Swap lost about $8.75 million after flash-loan trades exploited low WOO liquidity and pushed its sPMM price adjustment close to zero."
entities:
  - WOOFi
  - WOO
  - WOOFi Swap
  - Arbitrum
---

WOOFi Swap was exploited on Arbitrum on March 5, 2024 after an attacker used
flash-loan-funded trades to manipulate the WOO price inside WOOFi's synthetic
proactive market making model, or sPMM. The official post-mortem reports that
the attacker borrowed about 7.7 million WOO plus other assets, sold the WOO into
WOOFi, pushed the sPMM price adjustment to an extreme value near zero, and then
swapped out 10 million WOO at almost no cost. The sequence was repeated three
times in a short window and produced about 8.75 million dollars in profit after
flash loans were repaid.

This is a market-health case because the exploit depended on the surrounding
market environment. WOOFi described the sPMM as a model that uses on-chain
oracles to simulate centralized-exchange-style price, spread, and depth. The
same algorithm had operated since 2021, but the March 2024 conditions made the
attack practical: WOO had relatively low liquidity on Arbitrum, a WOO lending
market had recently made large temporary WOO borrowing feasible, and WOO was not
covered by the Chainlink fallback check that protected other token prices.

## Incident metrics

| Signal             | Observation                                                                                                        | Market-health interpretation                                                                         |
| ------------------ | ------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| Funding source     | The attacker used flash loans and borrowed about 7.7 million WOO plus other assets                                 | Temporary capital can overwhelm thin venue liquidity without representing durable demand             |
| Liquidity surface  | WOOFi attributed feasibility to low WOO liquidity and WOO being relatively rare on Arbitrum                        | Venue-level liquidity should cap model-driven price movement and swap size                           |
| Price adjustment   | The sPMM moved WOO toward an extreme price close to zero, reported as about 0.00000009 dollars                     | Model prices need sanity bounds against external references and recent trade history                 |
| Swap output        | The attacker swapped out about 10 million WOO with minimal cost                                                    | A single mispriced state let the attacker reverse the manipulated flow for profit                    |
| Repeat pattern     | WOOFi reported three repetitions in a very short period                                                            | Repeated same-direction market impact should trigger automatic throttles or pauses                   |
| Detection response | WOOFi reported internal monitoring and external teams detected the large swaps; contracts were paused by 16:02 UTC | Monitoring worked, but the attack completed quickly enough to need pre-trade or intra-block controls |
| Loss estimate      | WOOFi reported about 8.75 million dollars in profit after flash loans were repaid                                  | Low-liquidity price manipulation became a multi-million-dollar protocol loss                         |

The companion `woofi-spmm-market-signals.csv` file captures the flash-loan,
liquidity, price-adjustment, repeat-trade, detection, and bounty-response
signals for reuse.

## Manipulation path

The attack turned sPMM price adjustment into a market-health failure:

1. The attacker sourced temporary WOO liquidity with flash loans and related
   borrowing.
2. The borrowed WOO was sold into WOOFi Swap on Arbitrum.
3. WOOFi's sPMM adjusted the WOO price far outside the intended range.
4. The fallback price check did not cover WOO, so the abnormal price was not
   rejected.
5. The attacker used the mispriced state to acquire about 10 million WOO at
   almost no cost.
6. The loop was repeated three times before contracts were paused.

The risky state was visible as market structure, not just code behavior. A low
liquidity asset, a venue-specific lending market, a model price override, missing
fallback coverage, and repeated large same-asset swaps created a high-risk
combination. Any one of those facts is useful context. Together they should have
triggered a stricter execution mode.

## Detection controls

WOOFi shows why model-based DEX pricing needs market-aware controls:

- **Model price rails:** bound sPMM price movement against external references,
  recent oracle updates, and time-weighted venue prices.
- **Fallback coverage checks:** block or limit trading when a token lacks the
  fallback reference used for other listed assets.
- **Liquidity-adjusted trade caps:** reduce maximum notional size when local
  liquidity is thin or token availability is concentrated on one network.
- **Flash-loan pressure alerts:** flag same-transaction borrow, sell, reprice,
  and buyback paths.
- **Repeated-impact throttles:** pause or widen controls when the same pattern
  repeats across several transactions within minutes.
- **Lending-market coupling checks:** review swap limits when a newly available
  lending market makes temporary inventory large enough to move the venue model.

These controls are most useful before the final drain, because the exploit's
economic setup was visible before the end state. If a model price moves close to
zero while the external market has not done the same, the venue should treat the
move as an abnormal market-health condition.

## Lessons for market health

The WOOFi incident is a compact example of environment-dependent manipulation.
The sPMM was designed to imitate order-book depth, but that also meant its output
needed defenses that looked beyond a single swap. The relevant dashboard should
have connected WOO's Arbitrum liquidity, available borrow depth, sPMM price
movement, fallback-reference coverage, and repeated flash-loan trade flow.

For surveillance teams, the high-signal pattern is: temporary inventory, thin
local liquidity, model-price override, missing fallback protection, and repeated
large swaps that drive the modeled price away from external reality. That
pattern should trigger pre-trade rejection or an automatic pause even if the
protocol's internal math still returns a tradeable quote.

## References

- [WOO X: WOOFi sPMM exploit post-mortem](https://woox.io/blog/woofi-spmm-exploit-post-mortem)
- [Halborn: Explained: The WOOFi Hack (March 2024)](https://www.halborn.com/blog/post/explained-the-woofi-hack-march-2024)
- [CryptoNews: WOOFi Swap Exploited With $8.75m Flash Loan Attack](https://cryptonews.net/news/security/28664946/)
- [DN Institute cyberattack incident: WOOFi](https://dn.institute/research/cyberattacks/incidents/2024-03-05-woofi/)
- [First malicious transaction on Arbiscan](https://arbiscan.io/tx/0x57e555328b7def90e1fc2a0f7aa6df8d601a8f15803800a5aaf0a20382f21fbd)
- [On-chain bounty message](https://etherscan.io/tx/0x45fb400b3cd1a4b04d8e26fa8e5b5fc92003aadf28a000b9c0766c9a408a4af8)
