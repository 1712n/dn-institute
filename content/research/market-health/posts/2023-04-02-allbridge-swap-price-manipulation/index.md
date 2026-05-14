---
title: "Allbridge swap-price manipulation market-health case"
date: "2023-04-02"
description: "Allbridge lost about $573,000 from its BNB Chain liquidity pools after an attacker manipulated the swap price while acting as both liquidity provider and swapper."
entities:
  - Allbridge
  - BNB Chain
  - BUSD
  - USDT
  - PeckShield
---

Allbridge was exploited in early April 2023 after an attacker manipulated swap
pricing in the bridge's BNB Chain liquidity pools. Public reports describe the
attacker as acting as both a liquidity provider and a swapper, using temporary
liquidity and pool-state changes to create a favorable swap price before
draining BUSD and USDT from the affected pools.

The reported loss was about 573,000 dollars, split between 282,889 dollars of
BUSD and 290,868 dollars of USDT. Allbridge paused its bridge to prevent other
pools from being exploited, offered the attacker a white-hat bounty path, and
later reported that 1,500 BNB had been returned while the remaining funds would
be treated as the bounty. For market-health monitoring, the case shows why
bridge pools need the same route-depth and price-impact controls as lending or
DEX protocols.

## Incident metrics

| Signal            | Observation                                                                       | Market-health interpretation                                                      |
| ----------------- | --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| Exploit date      | The incident was reported on April 2, 2023 after the BNB Chain pool attack        | Same-day bridge-pool monitoring should cover swap and LP state changes            |
| Reported loss     | Public reporting cites about 282,889 dollars of BUSD and 290,868 dollars of USDT  | Stablecoin pool drains should be measured by asset and pool, not only total loss  |
| Manipulation role | The attacker acted as liquidity provider and swapper                              | Dual-role activity can indicate self-shaped pool pricing                          |
| Flash-loan signal | CertiK-linked reporting described a 7.5 million dollar BUSD flash loan            | Temporary capital should be compared with pool depth before large swaps           |
| Distorted swap    | Public reporting describes a 40,000 BUSD swap for 789,632 USDT at manipulated fit | Extreme output-to-input ratios reveal pool-state distortion                       |
| Protocol response | Allbridge temporarily suspended the bridge to prevent attacks on other pools      | Bridge suspension is a liquidity and confidence signal for cross-chain users      |
| Recovery signal   | Allbridge reported 1,500 BNB returned and treated the remainder as a bounty       | Recovery and bounty settlement should be separated from the initial loss timeline |

The companion `allbridge-swap-market-signals.csv` file records exploit-date,
loss, dual-role, flash-loan, distorted-swap, suspension, and recovery signals
for reuse.

## Manipulation path

The exploit converted pool-state control into a bridge-pool drain:

1. The attacker sourced temporary capital, with CertiK-linked reporting
   describing a 7.5 million dollar BUSD flash loan.
2. The attacker interacted with the Allbridge BNB Chain pools both as a
   liquidity provider and as a swapper.
3. Those actions distorted the pool's swap price.
4. The attacker executed swaps at the manipulated price, including a reported
   40,000 BUSD swap for 789,632 USDT.
5. The attacker withdrew value from the affected BUSD and USDT pools.
6. Allbridge paused the bridge and began recovery and bounty negotiations.

For market-health analysis, the important point is that the pool did not merely
experience ordinary arbitrage. The same actor shaped the pool state and then
traded against the shaped state. That makes dual-role LP/swapper activity,
same-transaction price impact, and pool-specific stablecoin imbalance high
signal features.

## Detection controls

Allbridge points to controls that should be applied to liquidity-pool bridges:

- **Dual-role LP/swapper alerts:** flag accounts that provide or remove
  liquidity and execute large swaps against the same pool in a short window.
- **Flash-loan notional gates:** compare temporary borrowing size with stable
  pool depth before permitting large price-moving swaps.
- **Output-to-input ratio checks:** block swaps whose output deviates sharply
  from independent stablecoin references or recent pool prices.
- **Pool-specific drain monitors:** track BUSD, USDT, and other stable pools
  separately instead of hiding the signal in aggregate bridge TVL.
- **Cross-pool pause rules:** when one pool's swap formula is manipulated,
  pause related pools until the same invariant is checked.
- **Recovery accounting:** record returned funds and bounty treatment separately
  from the exploit loss to preserve a clean incident timeline.

These controls focus on what a bridge operator can observe in real time:
temporary capital, LP position changes, abnormal swap ratios, and rapid pool
imbalance. They also reduce dependence on post-incident forensics by surfacing
the manipulation while the pool state is still changing.

## Lessons for market health

Allbridge demonstrates that stablecoin bridge pools can be market-manipulation
targets even when the affected assets are nominally low-volatility tokens. The
risk sits in the pool formula and the ability to reshape liquidity around a
swap, not only in the external price of BUSD or USDT.

For market-health teams, the strongest pattern is a flash-loan-sized capital
source, dual LP/swapper behavior, an extreme stablecoin output ratio, immediate
pool drain, and protocol-wide suspension. When those signals appear together,
bridge liquidity should be treated as stressed even if the underlying
stablecoins still trade near their pegs elsewhere.

## References

- [DN Institute cyberattack incident: Allbridge](https://dn.institute/research/cyberattacks/incidents/2023-04-02-allbridge/)
- [The Crypto Times: Allbridge offers bounty and receives most stolen funds](https://www.cryptotimes.io/2023/04/04/allbridge-offers-white-hat-bounty-receives-most-of-stolen-573-funds/)
- [ForkLog: Hacker Attacked Allbridge Liquidity Pools](https://forklog.com/en/hacker-attacked-allbridges-liquidity-pools-developers-halt-cross-chain-bridge/)
- [CSIDB: Allbridge incident record](https://www.csidb.net/csidb/incidents/d2705a97-d02e-4a3d-8c02-9f5a88bfb227/)
