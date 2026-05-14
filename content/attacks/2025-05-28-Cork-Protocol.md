---
date: 2025-05-28
target-entities: Cork Protocol
entity-types:
  - DeFi
  - Liquidity Vault
attack-types:
  - Smart Contract Exploit
  - Access Control Issue
  - Input Validation Issue
title: "Cork Protocol Hack Drains $12 Million Through Rollover and Hook Exploits"
loss: 12000000
---

## Summary

- On May 28, 2025, Cork Protocol's public beta was exploited for 3,761 wstETH from the wstETH:weETH Liquidity Vault, a loss reported at about $12 million by Cork and independent security coverage.
- The attack combined two failure paths: a rollover-pricing edge case that made cover tokens extremely cheap after expiry and a Cork Hook / FlashSwapRouter authorization gap that let the attacker extract matching depeg-swap tokens.
- Cork said its core Peg Stability Module behaved as designed, but downstream automation around liquidity-vault rollovers and the Uniswap V4 hook integration created exploitable business-logic and access-control conditions.
- Hypernative alerted Cork minutes after the exploit, Cork paused the Liquidity Vault by 12:33 UTC and all other protocol functions by 12:35 UTC, and about $20 million in other Cork vault assets remained locked but not drained.

## Attackers

- The attacker has not been publicly identified by name. The incident was executed through smart contracts and an externally owned wallet rather than through a known centralized-exchange account.
- CertiK identified the attack wallet as [0xEA6f30e360192bae715599E15e2F765B49E4da98](https://etherscan.io/address/0xEA6f30e360192bae715599E15e2F765B49E4da98) and the main attack contract as [0x9Af3dCE0813FD7428c47F57A39da2F6Dd7C9bb09](https://etherscan.io/address/0x9Af3dCE0813FD7428c47F57A39da2F6Dd7C9bb09).
- Cork's post-mortem lists two exploiter contracts: [0x6e54115de254805365c2d9c8a2eeb9b52e54668f](https://etherscan.io/address/0x6e54115de254805365c2d9c8a2eeb9b52e54668f), used to skew risk-premium and HIYA values, and [0x9Af3dCE0813FD7428c47F57A39da2F6Dd7C9bb09](https://etherscan.io/address/0x9Af3dCE0813FD7428c47F57A39da2F6Dd7C9bb09), used to gain cover-token and depeg-swap exposure.
- The stolen wstETH was swapped to ETH through 1inch and was held at the address linked in Cork's post-mortem at publication time.

## Losses

- Cork reported that the attacker extracted 3,761 wstETH from the wstETH:weETH Liquidity Vault on May 28, 2025.
- Cointelegraph, citing Cyvers, reported the same approximate stolen amount and noted that the wstETH was converted to ETH shortly after the exploit.
- Cork stated that approximately $20 million in assets remained locked in Cork Liquidity Vaults and were not impacted by the drain, but protocol functions remained paused pending contract upgrades and a safe withdrawal plan.

## Timeline

- **March 4, 2025:** Cork Protocol launched its public beta with liquidity-vault caps and previously completed audits, according to Cork's post-mortem.
- **May 28, 2025, 11:23 UTC:** Cyvers reported that the attack transaction occurred around 11:23:19 UTC and was funded by an address ending in 762B.
- **May 28, 2025, 11:39 UTC:** Cork recorded the exploit time in its post-mortem, saying 3,761 wstETH was extracted from the wstETH:weETH Liquidity Vault.
- **May 28, 2025, 11:43 UTC:** Hypernative notified Cork of the exploit.
- **May 28, 2025, 12:17 UTC:** Cork began multisig pause transactions and opened an incident war room with Hypernative, Spearbit Labs, Quantstamp, Certora, and other advisors.
- **May 28, 2025, 12:33 UTC:** Cork executed the transaction pausing the Liquidity Vault.
- **May 28, 2025, 12:35 UTC:** Cork executed the transaction pausing other protocol functions.
- **May 28, 2025, 13:21 UTC:** Cork published a public incident statement.
- **May 29, 2025:** Cork completed an initial proof of concept reproducing the attack.
- **June 4, 2025:** Cork published its detailed post-mortem after consolidating technical feedback.

## Security Failure Causes

- **Rollover-pricing edge case:** Cork's rollover automation used historical risk-premium inputs to price the next issuance. In a low-volume market close to expiry, a small trade shortly before rollover could dominate the historical implied yield average and make new cover tokens abnormally cheap.
- **Cork Hook authorization gap:** Cork's Uniswap V4 hook integration did not enforce a sufficient authorization check on hook data in the affected path. Cork noted that a later upstream Uniswap periphery change added an explicit authorization feature, but Cork's deployed version did not include it.
- **Fake-market input validation failure:** CertiK and Halborn both described a fake-market setup in which the real market's depeg-swap token was treated as the redemption asset of a second market. That setup should not have been permitted because it let the attacker move between fake and real derivative-token accounting paths.
- **Composable business-logic interaction:** The exploit was not a single isolated bug. It required pairing manipulated rollover economics with hook / router authorization behavior so that the attacker could obtain both cover tokens and depeg swaps and redeem them for the underlying wstETH.
- **Residual control limits after audits:** Cork had multiple audits, formal-verification work, simulations, a bug bounty, and monitoring, but the exploit landed in downstream automation and integration logic. This indicates that vault automation, expiry handling, and hook data paths need scenario testing beyond standard invariant checks.

## Sources

- [Cork Protocol May 28 2025 exploit post-mortem](https://www.cork.tech/blog/post-mortem)
- [CertiK Cork Protocol incident analysis](https://www.certik.com/blog/cork-protocol-incident-analysis)
- [Cointelegraph coverage of the Cork Protocol exploit](https://cointelegraph.com/news/cork-protocol-hacked-contracts-paused)
- [Halborn explanation of the Cork Protocol hack](https://www.halborn.com/blog/post/explained-the-cork-protocol-hack-may-2025)
- [CertiK preparation transaction](https://etherscan.io/tx/0x14cdf1a643fc94a03140b7581239d1b7603122fbb74a80dd4704dfb336c1dec0)
- [CertiK exploit transaction](https://etherscan.io/tx/0xfd89cdd0be468a564dd525b222b728386d7c6780cf7b2f90d2b54493be09f64d)
