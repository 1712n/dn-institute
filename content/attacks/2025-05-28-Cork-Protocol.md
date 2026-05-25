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

- Cork's May 28, 2025 beta incident drained 3,761 wstETH from the wstETH:weETH Liquidity Vault, with Cork and third-party security coverage valuing the impact at roughly $12 million.
- The transaction sequence joined two separate weaknesses: expiry rollover economics that made new cover-token exposure underpriced, and a Cork Hook / FlashSwapRouter path that let the attacker pair that exposure with depeg-swap tokens.
- The Peg Stability Module itself was not the failing component in Cork's post-mortem; the exploitable surface sat in vault rollover automation, market construction, and the Uniswap V4 hook integration around it.
- Detection came shortly after the drain, followed by protocol pauses at the vault and broader-function levels within the next hour; Cork said roughly $20 million in other vault assets stayed locked rather than being removed.

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

- **Rollover-pricing edge case:** The next issuance inherited pricing from a narrow pre-expiry trading sample. When activity was thin, an attacker-controlled trade could pull the historical implied yield average toward an artificial level and leave fresh cover-token exposure priced far below the risk it carried.
- **Cork Hook authorization gap:** The affected Uniswap V4 integration trusted hook data in a path where Cork needed a tighter caller or market authorization boundary. Cork later pointed to an upstream periphery authorization feature that was absent from the deployed integration, leaving the route open to crafted hook inputs.
- **Fake-market input validation failure:** CertiK and Halborn described a constructed market that reused the genuine market's depeg-swap token as another market's redemption asset. That cross-market substitution let the attacker bridge fake-market accounting into real derivative-token redemption instead of being rejected at market creation or swap validation.
- **Composable business-logic interaction:** The drain depended on the rollover and hook issues reinforcing each other. Cheap cover-token exposure created one side of the position, while the router/hook path supplied the matching depeg-swap side needed to redeem the underlying wstETH.
- **Residual control limits after audits:** Cork had audits, formal verification, simulations, a bug bounty, and monitoring, but the missed case lived in the interaction between expiry automation and integration glue. The gap points to scenario tests that join vault rollover, fake-market construction, hook calldata, and redemption flows rather than checking each invariant in isolation.

## Sources

- [Cork Protocol May 28 2025 exploit post-mortem](https://www.cork.tech/blog/post-mortem)
- [CertiK Cork Protocol incident analysis](https://www.certik.com/blog/cork-protocol-incident-analysis)
- [Cointelegraph coverage of the Cork Protocol exploit](https://cointelegraph.com/news/cork-protocol-hacked-contracts-paused)
- [Halborn explanation of the Cork Protocol hack](https://www.halborn.com/blog/post/explained-the-cork-protocol-hack-may-2025)
- [CertiK preparation transaction](https://etherscan.io/tx/0x14cdf1a643fc94a03140b7581239d1b7603122fbb74a80dd4704dfb336c1dec0)
- [CertiK exploit transaction](https://etherscan.io/tx/0xfd89cdd0be468a564dd525b222b728386d7c6780cf7b2f90d2b54493be09f64d)
