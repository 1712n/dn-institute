---
title: "Sturdy Finance Balancer oracle market-health case"
date: "2023-06-12"
description: "Sturdy Finance lost about $800,000 after a flash-loan-funded read-only reentrancy sequence manipulated Balancer LP pricing used by its lending oracle."
entities:
  - Sturdy Finance
  - Balancer
  - B-stETH-STABLE
  - Ethereum
---

Sturdy Finance was exploited on June 12, 2023 after an attacker used a
flash-loan-funded transaction to manipulate the price path feeding Sturdy's
Balancer LP collateral oracle. Public post-mortems and security writeups
describe the core failure as a read-only reentrancy window around Balancer pool
accounting: while the pool state was temporarily inconsistent, Sturdy's oracle
read an inflated value for the collateral token and allowed excess borrowing.

The attack drained about 442 ETH, reported at roughly 800,000 dollars at the
time. Sturdy paused its markets after the exploit was reported and later
published a post-mortem explaining that the wstETH/WETH Balancer collateral
integration was vulnerable to a known read-only reentrancy manipulation vector.
The incident is a useful market-health case because the visible market signal
was not a long-lived spot-price move. The risk appeared in a short transaction
window where a lending venue trusted an LP token rate while the underlying pool
state could be temporarily distorted.

## Incident metrics

| Signal                | Observation                                                                   | Market-health interpretation                                                       |
| --------------------- | ----------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Malicious transaction | The exploit transaction was mined at 01:06:35 UTC on June 12, 2023            | The manipulation was atomic and required transaction-level monitoring              |
| Reported loss         | Public reports and DN Institute record the loss at about 442 ETH, or $800k    | A small oracle window was enough to create material lending-market bad debt risk   |
| Collateral source     | Sturdy priced collateral through Balancer's B-stETH-STABLE / wstETH-WETH path | LP-token oracles can transmit pool-accounting anomalies into borrow limits         |
| Attack primitive      | Security firms described Balancer read-only reentrancy plus oracle misuse     | Read-only calls are still market-risk surfaces when they influence solvency checks |
| Protocol response     | Sturdy paused all markets after acknowledging the exploit                     | Emergency pauses are a market-health signal, not only an operational status update |
| Negotiation signal    | Sturdy offered a $100,000 return agreement through an on-chain message        | Recovery odds and user confidence can be inferred from public negotiation behavior |
| Mixer route           | Stolen funds began moving to Tornado Cash shortly after the exploit           | Rapid laundering reduces recovery probability and raises response urgency          |

The companion `sturdy-balancer-market-signals.csv` file captures the transaction,
loss, oracle, pause, negotiation, and laundering signals in a reusable form.

## Manipulation path

The high-risk sequence linked a pool accounting window to lending-market
solvency:

1. The attacker sourced temporary liquidity and interacted with Sturdy's
   collateral path in a single transaction.
2. Balancer pool accounting entered a temporary state where read-only rate
   queries did not represent the final settled pool value.
3. Sturdy's collateral oracle consumed that distorted rate while calculating
   borrow capacity.
4. The attacker borrowed against the inflated collateral value, then unwound the
   manipulation and extracted ETH.
5. Sturdy paused markets after public alerts, limiting further exposure but
   confirming that users could no longer treat the venue as normally liquid.

The lesson is that a lending protocol can be exposed even when the underlying
market does not show a persistent price dislocation. If a valuation source can
be read mid-transition, then a one-block accounting artifact becomes a
market-health event.

## Detection controls

Sturdy points to monitoring rules that should sit beside ordinary price-feed
checks:

- **Read-only reentrancy guards:** treat view calls that influence collateral
  valuation as risk-bearing dependencies and block oracle reads during pool
  join, exit, or callback windows.
- **LP-rate sanity checks:** compare Balancer-derived LP rates with independent
  reserves, TWAPs, and previous-block rates before accepting large borrow
  capacity changes.
- **Flash-loan notional alerts:** flag transactions where temporary liquidity
  size is large relative to the venue's borrowable liquidity or collateral pool
  depth.
- **Pause-state reporting:** feed market pauses into dashboards because a
  paused lending venue changes redemption, liquidation, and confidence
  assumptions immediately.
- **Post-exploit flow tracking:** monitor rapid movement to mixers or instant
  exchangers to estimate recovery probability and user-remediation urgency.
- **Collateral-integration reviews:** require fresh risk review when a new LP
  token or yield-bearing pool is accepted as collateral, especially if the
  upstream protocol has known accounting-window disclosures.

These controls are designed to catch solvency distortion before it becomes a
borrow event. They also help distinguish ordinary collateral volatility from a
protocol-specific pricing artifact.

## Lessons for market health

The Sturdy exploit shows how market-health monitoring needs to cover both
external prices and internal accounting surfaces. A dashboard that only watches
spot ETH, stETH, or pool TVL would miss the key moment: Sturdy trusted a
temporarily manipulable Balancer rate in the same transaction that converted the
distortion into borrowable value.

For lending venues, the practical signal is abrupt borrow-capacity expansion
after flash-loan-sized pool interaction, especially when the collateral is an LP
token whose rate is computed from another protocol's transient state. For market
participants, a pause announcement is the external symptom that collateral
valuation assumptions have failed and that normal liquidity conditions no longer
apply.

## References

- [DN Institute cyberattack incident: Sturdy Finance](https://dn.institute/research/cyberattacks/incidents/2023-06-12-sturdy-finance/)
- [Olympix: Sturdy Finance Hit by Reentrancy Exploit](https://olympix.security/blog/sturdy-finance-hit-by-reentrancy-exploit)
- [CertiK: Oracle Dependency: Decrypting the Sturdy Finance Attack](https://www.certik.com/resources/blog/oracle-dependency-decrypting-the-sturdy-finance-attack)
- [CryptoSlate: Sturdy Finance halts market after $800,000 exploit linked to faulty price oracle](https://cryptoslate.com/sturdy-finance-halts-market-after-800000-exploit-linked-to-faulty-price-oracle/)
- [Exploit transaction on Etherscan](https://etherscan.io/tx/0xeb87ebc0a18aca7d2a9ffcabf61aa69c9e8d3c6efade9e2303f8857717fb9eb7)
- [Sturdy on-chain message to exploiter](https://etherscan.io/tx/0xda7fda2146ec0cc6f22920451978b41f9a9ae7f01ce6e4878b454eb2efdc9fec)
