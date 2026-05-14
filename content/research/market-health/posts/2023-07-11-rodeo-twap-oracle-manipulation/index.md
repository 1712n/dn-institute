---
title: "Rodeo Finance TWAP oracle manipulation market-health case"
date: "2023-07-11"
description: "Rodeo Finance lost about 472 ETH on Arbitrum after a sandwich-style sequence manipulated a TWAP oracle path used by its leveraged yield strategy."
entities:
  - Rodeo Finance
  - Arbitrum
  - unshETH
  - USDC
  - Camelot
---

Rodeo Finance was exploited on Arbitrum on July 11, 2023 after an attacker
manipulated the oracle path used by a leveraged yield strategy. Public incident
writeups describe the attack as a sandwich-style manipulation of a TWAP oracle:
the attacker moved the relevant market price, caused Rodeo's strategy logic to
act on the distorted reading, and then arbitraged the pool back toward its
normal state after the protocol had already taken the harmful action.

The loss was reported at roughly 472 ETH, or about 880,000 to 888,000 dollars
after recalculation. Some summaries cite a larger gross impact near 1.7 million
dollars before partial recovery. For market-health analysis, the important
signal is that a TWAP control meant to reduce spot-price manipulation still
became usable inside a tightly ordered transaction sequence when the relevant
pool depth and update path were not strong enough for the strategy's exposure.

## Incident metrics

| Signal            | Observation                                                                  | Market-health interpretation                                                       |
| ----------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Exploit date      | The malicious transaction sequence occurred on July 11, 2023                 | Same-day strategy and oracle monitoring should cover active Arbitrum yield markets |
| Reported loss     | DN Institute and PeckShield-linked reporting put the loss near 472 ETH       | A single oracle path created material lending and strategy exposure                |
| Oracle weakness   | The strategy depended on a TWAP oracle path that could be sandwiched         | TWAP windows still need manipulation-cost and liquidity-depth checks               |
| Market route      | Public reports tie the manipulation to unshETH and related swap routes       | Strategy assets need route-specific liquidity and slippage monitors                |
| Recovery signal   | Smart Contract Hacking reports about 810,000 dollars recovered from the farm | Recovery and net-loss data should be tracked separately from gross exploit impact  |
| TVL impact        | Crypto Briefing reported TVL fell from about 20 million dollars to below 500 | Post-exploit liquidity flight is a market-health event, not only a security metric |
| Attacker movement | Public reporting described bridged funds and Tornado Cash routing            | Cross-chain and mixer flows help classify adversarial extraction                   |

The companion `rodeo-twap-market-signals.csv` file records exploit-date, loss,
oracle, route, recovery, TVL-impact, and fund-flow signals for reuse.

## Manipulation path

The exploit turned a manipulated oracle window into a harmful strategy action:

1. The attacker prepared the Arbitrum transaction sequence and targeted the
   strategy path that relied on the vulnerable TWAP reading.
2. The attacker manipulated the market route used by the oracle, affecting the
   price context Rodeo used for the strategy operation.
3. Rodeo's logic acted on the distorted price and moved assets through the
   leveraged strategy path.
4. The attacker traded the pool back toward its prior state, capturing the
   difference created by the protocol's action at the manipulated price.
5. Proceeds were bridged and swapped across Ethereum and Arbitrum routes, with
   public reporting noting Tornado Cash activity.

The market-health lesson is that TWAP does not automatically remove oracle
risk. A TWAP is safer only when its update cadence, observation window,
underlying pool liquidity, and strategy exposure are sized together. If a
strategy can force or rely on a vulnerable update during a sandwichable route,
then the TWAP becomes a delayed spot-price dependency rather than a robust
market signal.

## Detection controls

Rodeo points to controls that should sit around leveraged-yield strategy
oracles:

- **TWAP manipulation-cost checks:** compare the cost of moving the reference
  pool with the strategy's maximum borrow or investment exposure.
- **Route-depth gates:** pause strategy actions when the reference route has
  shallow liquidity relative to the transaction size.
- **Same-block route reversal alerts:** flag transactions that move an oracle
  route, trigger protocol strategy logic, and then restore the route.
- **Gross versus net loss tracking:** separate stolen amount, recovered amount,
  and remaining net loss in incident dashboards.
- **TVL-flight monitors:** track post-incident TVL collapse as a liquidity and
  user-confidence metric.
- **Cross-chain flow alerts:** connect Arbitrum exploit transactions with
  bridge, Ethereum swap, and mixer activity.

These controls focus on observable market state rather than private attacker
intent. They would surface when a strategy's reference route becomes cheaper to
manipulate than the value protected by that route.

## Lessons for market health

Rodeo Finance is a reminder that oracle design and market liquidity cannot be
reviewed separately. A price feed can have the right label, such as TWAP, while
still being unsafe for a specific strategy if the reference market is thin or
the action being authorized is too large.

For market-health teams, the actionable pattern is a sequence that combines
large route movement, strategy execution, route reversal, rapid TVL exit, and
cross-chain fund movement. When those signals appear together, the protocol is
not only experiencing a contract exploit. It is showing that market depth,
oracle design, and strategy exposure have become misaligned.

## References

- [DN Institute cyberattack incident: Rodeo Finance](https://dn.institute/research/cyberattacks/incidents/2023-07-11-rodeo-finance/)
- [Smart Contract Hacking: Rodeo Finance Hack](https://smartcontractshacking.com/hacks/rodeo-finance-hack-2023)
- [Crypto Briefing: DeFi Protocol Rodeo Finance Hacked](https://cryptobriefing.com/defi-protocol-rodeo-finance-hacked-1-53m-of-eth-stolen/)
- [CertiK: Lending Contract Exploits - A Retrospective](https://www.certik.com/blog/lending-contract-exploits-a-retrospective)
