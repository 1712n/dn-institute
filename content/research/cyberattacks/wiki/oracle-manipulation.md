---
title: Oracle Manipulation Attacks
bookToc: true
---

Oracle manipulation attacks corrupt the price feed that a DeFi protocol treats as truth. If the protocol trusts a manipulable market, an attacker can inflate collateral, trigger bad liquidations, or borrow against fake value, as shown in [Mango Markets](https://dn.institute/attacks/posts/2022-10-11-Mango-Markets/), [BonqDAO](https://dn.institute/attacks/posts/2023-02-01-BonqDAO/), and [Cream Finance](https://dn.institute/attacks/posts/2021-10-27-Cream-Finance/).

## What is a Price Oracle?

A blockchain cannot query off-chain price data by itself. Protocols therefore rely on oracles or oracle-like pricing mechanisms to decide:
- how much collateral a user can borrow against,
- when a position should be liquidated,
- or how synthetic / vault assets should be priced.

If that price feed can be skewed, the protocol's accounting logic breaks.

## The Mechanism of Attack

Most oracle-manipulation attacks follow the same broad pattern:

1. **Acquire enough capital** — often through a flash loan — to move a thin market.
2. **Push the referenced market price** on a DEX or reporting source far away from fair value.
3. **Let the victim protocol ingest the manipulated price** through its oracle or pricing logic.
4. **Exploit the bad price** by borrowing too much, minting under-collateralized assets, or triggering liquidations.
5. **Exit before the market normalizes** and repay the borrowed capital.

## Famous Case Studies

### 1. Mango Markets (October 2022)
- **Loss:** Approximately [$116 million](https://dn.institute/attacks/posts/2022-10-11-Mango-Markets/).
- **Mechanism:** Oracle manipulation of the low-liquidity MNGO market.
- **Details:** The attacker used two funded accounts to take large opposing positions, then bought MNGO aggressively enough to move the price from roughly [$0.03 to $0.91](https://dn.institute/attacks/posts/2022-10-11-Mango-Markets/). Mango then treated the inflated MNGO valuation as real collateral.
- **Result:** The attacker borrowed out protocol liquidity worth about [$116 million](https://dn.institute/attacks/posts/2022-10-11-Mango-Markets/) against unrealized gains created by the manipulated oracle state.

### 2. BonqDAO (February 2023)
- **Loss:** The repo's [BonqDAO incident page](https://dn.institute/attacks/posts/2023-02-01-BonqDAO/) records an estimated loss of roughly [$120 million](https://dn.institute/attacks/posts/2023-02-01-BonqDAO/), including about $108 million in BEUR and $12 million in WALBT, even though the exploit path centered on minting capacity.
- **Mechanism:** Manipulation of the Tellor-fed WALBT price.
- **Details:** The attacker staked Tellor assets, submitted a manipulated WALBT value, minted roughly [100 million BEUR](https://dn.institute/attacks/posts/2023-02-01-BonqDAO/), and then liquidated collateral using the distorted price.
- **Result:** BonqDAO's dependence on an instantaneous single-source price made the protocol vulnerable to minting and liquidation abuse.

### 3. Cream Finance (October 2021)
- **Loss:** Approximately [$130 million](https://dn.institute/attacks/posts/2021-10-27-Cream-Finance/).
- **Mechanism:** Flash-loan-assisted oracle manipulation involving Yearn / Curve pricing assumptions.
- **Details:** The attacker exploited Cream's hybrid oracle design and uncapped collateral mechanics to double-count value in yUSD-related positions, as summarized in the repo's [Cream Finance incident page](https://dn.institute/attacks/posts/2021-10-27-Cream-Finance/).
- **Result:** The protocol overvalued manipulated collateral and allowed the attacker to drain lending liquidity worth roughly [$130 million](https://dn.institute/attacks/posts/2021-10-27-Cream-Finance/).

## Prevention and Mitigation

### 1. Use harder-to-manipulate pricing inputs
- **Decentralized oracle networks:** Aggregated sources such as Chainlink are generally harder to move than a single DEX market.
- **Oracle diversity:** Combining multiple venues or sanity checks reduces single-source failure modes.

### 2. Smooth short-lived price spikes
- **TWAPs:** Time-weighted average prices make one-block distortions less effective.
- **Liquidity thresholds:** Illiquid markets should not drive high-value collateral decisions without guardrails.

### 3. Add protocol-side brakes
- **Circuit breakers:** Pause borrowing or liquidations when prices move too far too fast.
- **Conservative collateral factors:** Thin or volatile assets should have lower LTVs and tighter borrow caps.
