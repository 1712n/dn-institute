---
title: "Yearn yDAI: Curve 3pool Imbalance as Market Manipulation"
date: 2021-02-04
description: "A case study of the Yearn v1 yDAI vault exploit, where repeated Curve 3pool imbalances caused vault deposits and withdrawals to execute at unfavorable rates."
entities:
  - Yearn Finance
  - yDAI
  - Curve 3pool
  - 3CRV
---

## Summary

On February 4, 2021, an attacker used temporary Curve 3pool inventory shocks to make Yearn Finance's v1 yDAI vault execute deposits and withdrawals at poor rates. Yearn later reported about 11 million DAI of vault losses from the incident. The manipulation did not depend on a durable move in stablecoin fundamentals; it depended on creating a short imbalance, making the vault trade against that state, and then reversing enough of the imbalance to run the pattern again.[^yearn-disclosure]

This is a useful market-health case because the manipulated market was not a thin memecoin book. It was a major stablecoin AMM pool where prices are expected to remain close to parity. The attacker used very large temporary flows, not a durable change in fundamentals, to alter the price surface visible to the vault. The vault then acted as a forced taker of that distorted price.

The incident also shows why market manipulation and oracle/AMM exploitation overlap in DeFi. The direct loss came from vault strategy execution, but the enabling signal was a transient market state: an intentionally imbalanced Curve pool. That market state would look abnormal under liquidity imbalance, volume concentration, and repeated-round-trip flow metrics.

## Manipulation pattern

Yearn's disclosure links to the attacker contract and an example transaction. In that representative transaction, the attacker minted 3CRV with 134 million USDC and 36 million DAI, withdrew 165 million USDT to skew the pool composition, pushed yDAI vault activity through the distorted pool state, and eventually redeemed the original 3CRV position for 134 million USDC plus 39.4 million DAI.[^yearn-disclosure][^example-tx]

{{< figure src="yearn-ydai-curve-imbalance-flow.svg" caption="Simplified flow of the yDAI manipulation loop: distort Curve 3pool, force yDAI vault execution, restore, repeat, and redeem." >}}

The loss was not caused by a normal directional bet on DAI, USDC, or USDT. The attacker temporarily changed the relative stablecoin inventory inside Curve, made another protocol execute while that inventory was distorted, and then unwound the distortion. Yearn reported 11 million DAI of vault deposits lost, 24 million DAI saved by emergency mitigation, and an estimated attacker profit of 2.7 million DAI; Halborn and CoinDesk later summarized the incident as the February 2021 Yearn v1 yDAI exploit.[^yearn-disclosure][^halborn][^coindesk]

## Market-health signals

The accompanying dataset, [`yearn-ydai-market-health-signals.csv`](yearn-ydai-market-health-signals.csv), summarizes observable signals from the public disclosure. It is not a replacement for raw Curve swaps or Ethereum trace data; it is a compact checklist for identifying similar events in AMM and vault integrations. DN Institute's market-health API is oriented around exchange-market abuse metrics such as wash-trading indicators, so this vault-specific AMM case would need to pair those venue-level metrics with on-chain pool-composition and protocol-call data.[^dn-api]

### Pool composition imbalance

Stablecoin pools are designed to absorb routine trading while keeping coins close to parity. A sudden withdrawal of 165 million USDT after deposits of 134 million USDC and 36 million DAI is a pool-composition shock, not a normal user rebalance. The market-health question is whether one actor has enough size to dominate the pool's inventory and whether dependent protocols consume that distorted price.

A monitoring rule should flag large single-actor withdrawals that materially reduce one stablecoin's share of the pool and are followed by protocol strategy calls. The absolute dollar size matters, but the sequence matters more: imbalance first, forced protocol execution second, imbalance reversal third.

### Forced execution by an integrated protocol

The yDAI vault was vulnerable because an external caller could invoke `earn()` and push deposits into the strategy. With loose slippage protection and a temporary 0% withdrawal fee during migration to v2 vaults, the vault became a predictable counterparty. The attacker did not need to persuade users to trade at bad prices; the strategy machinery supplied the victim flow.

For market-health review, this means AMM price checks should include integration behavior. A pool can look healthy most of the time and still be unsafe if an integrated vault will transact during short-lived imbalance windows.

### Repetition and round-trip behavior

Yearn reports the pattern repeated across 11 transactions over 38 minutes before mitigation.[^yearn-disclosure] Repetition is important because it separates the event from a one-off arbitrage. The attacker repeatedly created a distorted state, used the vault against that state, and then restored enough of the pool to continue.

That produces a recognizable footprint: high-volume round trips, repeated calls to the same strategy path, and abnormal inventory swings that end closer to the starting composition than a genuine market move would.

## Timeline

- **February 4, 2021, about 21:45 UTC:** Yearn's security team noticed an unusual transaction pattern involving Yearn vaults.[^yearn-disclosure]
- **21:48 UTC:** Review identified an issue with the DAI v1 vault and additional exploit transactions underway.[^yearn-disclosure]
- **21:56 UTC:** Yearn set `setMin(0)` on the DAI vault, effectively disabling further deposits into the strategy.[^yearn-disclosure]
- **22:07 UTC:** Yearn applied the same mitigation to USDC, USDT, and TUSD v1 vaults as a precaution.[^yearn-disclosure]
- **February 5, 2021:** Yearn published the vulnerability disclosure with exploit details and references.[^yearn-disclosure]

## Lessons for market manipulation detection

First, stablecoin parity is not sufficient evidence of healthy execution. A market can return to parity after each loop while still transferring value during the short imbalance window. Monitoring should track path-dependent inventory movement, not just end-of-period prices.

Second, AMM integrations need manipulation-aware circuit breakers. Slippage limits, withdrawal fees, and permissionless keeper calls are market-health controls when a vault delegates execution to an external pool. In this case, Yearn listed loose 1% slippage protection, a temporary 0% withdrawal fee, and externally callable `earn()` as contributing factors.[^yearn-disclosure]

Third, raw volume alone can be misleading. The attacker generated huge flow, but the important signal was concentrated, reversible flow that repeatedly placed the pool in a bad state for one dependent protocol. A healthy market has diverse participants absorbing imbalances; this event had one actor creating and harvesting the imbalance.

## References

[^yearn-disclosure]: Yearn Security, ["Vulnerability disclosure 2021-02-04"](https://github.com/yearn/yearn-security/blob/master/disclosures/2021-02-04.md).

[^example-tx]: Example transaction from Yearn's disclosure: [`0xf6022012b73770e7e2177129e648980a82aab555f9ac88b8a9cda3ec44b30779`](https://etherscan.io/tx/0xf6022012b73770e7e2177129e648980a82aab555f9ac88b8a9cda3ec44b30779).

[^dn-api]: DN Institute, [Crypto Market Health API](https://rapidapi.com/DNInstitute/api/crypto-market-health/) and [Market Health Metrics documentation](https://dn.institute/market-health/docs/market-health-metrics/).

[^halborn]: Halborn, ["Explained: Inside the Yearn v1 yDAI Hack (Feb 2021)"](https://www.halborn.com/blog/post/explained-the-yearn-v1-ydai-hack-feb-2021).

[^coindesk]: CoinDesk, ["Yearn Finance DAI Vault Has Suffered an Exploit; $11M Drained"](https://www.coindesk.com/tech/2021/02/04/yearn-finance-dai-vault-has-suffered-an-exploit-11m-drained/).
