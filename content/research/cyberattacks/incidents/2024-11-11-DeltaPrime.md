---
date: 2024-11-11
target-entities: DeltaPrime
entity-types:
  - DeFi
  - Lending Platform
attack-types:
  - Smart Contract Exploit
title: "DeltaPrime Exploit Drains About $4.75 Million Across Avalanche and Arbitrum"
loss: 4750000
---

## Summary

On November 11, 2024, DeltaPrime reported that its Avalanche and Arbitrum deployments had been exploited for an initial estimated loss of about $4.75 million. DeltaPrime's own post-mortem centered the exploit on abuse of reward-claim logic in Prime Accounts, where malicious contracts impersonated LFJ reward infrastructure and made attacker-controlled flows appear to be legitimate rewards.

Public analysis diverged on whether that description fully captured the exploit chain. DeltaPrime publicly attributed the incident primarily to reward-claim impersonation. CertiK publicly analyzed it as a chained two-vulnerability exploit that included, but was not limited to, reward-claim abuse: one flaw in debt-swap handling that allowed borrowed assets to be routed to an attacker-controlled contract without normal repayment effects, and another in reward-claim handling that accepted attacker-controlled external input and let collateral be withdrawn as apparent rewards. DeltaPrime's post-mortem reported a total loss of about $4.75 million, while third-party estimates ranged from about $4.8 million to about $4.85 million.

## Attackers

The attacker's public identity remains unknown.

Addresses publicly associated with the exploit include:

### Avalanche
- Attacker wallet holding most Avalanche proceeds: [0xd3d535141831F6Bd8B7DF92E2AE0463D60Af2413](https://snowtrace.io/address/0xd3d535141831F6Bd8B7DF92E2AE0463D60Af2413)
- Additional Avalanche address named by CertiK: [0xd5381c683191EB0999a51567274abAB73a9Df0AD](https://snowtrace.io/address/0xd5381c683191EB0999a51567274abAB73a9Df0AD)
- Malicious contract impersonating LFJ components in DeltaPrime's post-mortem: [0x055Be51BD3541C2c8F5219F5b78212b01A49BdaE](https://snowtrace.io/address/0x055Be51BD3541C2c8F5219F5b78212b01A49BdaE)
- Avalanche attack orchestrator contract in DeltaPrime's post-mortem: [0x2D81eCA9C72eA059F126a37eC205601487217A16](https://snowtrace.io/address/0x2D81eCA9C72eA059F126a37eC205601487217A16)

### Arbitrum
- Arbitrum exploiter: [0xb87881637b5c8e6885C51aB7D895e53FA7d7c567](https://arbiscan.io/address/0xb87881637b5c8e6885c51ab7d895e53fa7d7c567)
- Arbitrum attack contract: [0x52ee5c0eA2E7b38D4B24c09D4d18cba6C293200E](https://arbiscan.io/address/0x52ee5c0ea2e7b38d4b24c09d4d18cba6c293200e)
- Arbitrum recipient addresses: [0x56e7f67211683857EE31a1220827cac5cdaa634C](https://arbiscan.io/address/0x56e7f67211683857ee31a1220827cac5cdaa634c) and [0x101723dEf8695f5bb8D5d4AA70869c10b5Ff6340](https://arbiscan.io/address/0x101723def8695f5bb8d5d4aa70869c10b5ff6340)

## Losses

Loss estimates varied slightly by source.

- DeltaPrime's post-mortem reported *$4.75 million*
- CertiK estimated about *$4.1 million on Avalanche* and about *$753,000 on Arbitrum*
- Three Sigma referred to a total loss of about *$4.85 million*

CertiK reported that part of the Avalanche proceeds was deployed into Trader Joe and Stargate positions, while part of the Arbitrum proceeds was bridged to Ethereum as WBTC.

## Timeline

- **November 11, 2024, 07:35:19 UTC:** DeltaPrime's post-mortem says the attacker [deployed malicious contracts](https://snowtrace.io/tx/0xca2b006558ec99f491c7a2a030f8190aa1462bca70299263dd93f5344f152e0d?chainid=43114) on Avalanche and [on Arbitrum](https://arbiscan.io/tx/0x2ec5b7e439a446676234b4540e05519ad113ac1dde0aa9ccfa800fd50ae08033).
- **November 11, 2024, 07:35:43 UTC:** A series of [attack transactions on Avalanche](https://snowtrace.io/tx/0xece4efbe11e59d457cb1359ebdc4efdffdd310f0a82440be03591f2e27d2b59e?chainid=43114) began, according to DeltaPrime.
- **November 11, 2024, 07:36:05 UTC:** DeltaPrime's post-mortem said a similar attack began on Arbitrum.
- **November 11, 2024:** CertiK identified [0x9efe855cd3783462207ff8a3d94dc17a74e2b2f00bf1b4c8a7e0135dae83ab5c](https://arbiscan.io/tx/0x9efe855cd3783462207ff8a3d94dc17a74e2b2f00bf1b4c8a7e0135dae83ab5c) as the first Arbitrum attack transaction used in CertiK's published step-by-step analysis; the draft treats this as CertiK's analyzed transaction rather than as a replacement for DeltaPrime's 07:36:05 UTC attack-start marker.
- **November 11, 2024, 07:49 UTC:** DeltaPrime said the attacker [moved part of the Avalanche proceeds to Trader Joe pools](https://snowtrace.io/tx/0xac2d68d225c00dbaced446281e034a52d6edef330b87352bf7679c3f463501a0?chainid=43114).
- **November 11, 2024, 08:13 UTC:** DeltaPrime said the attacker [moved part of the Avalanche proceeds to Stargate pools](https://snowtrace.io/tx/0x69c200046ef7848435eadc1eb072832c94f8f785f1907b2fe72ec031ce2eb530?chainid=43114).
- **November 11, 2024, 09:04 UTC:** DeltaPrime publicly announced on [X](https://x.com/DeltaPrimeDefi/status/1855899502944903195) that Avalanche and Arbitrum had been exploited for an initial estimated $4.75 million and that the protocol had been paused.
- **November 11, 2024, 10:15 UTC:** DeltaPrime's post-mortem said the attacker [moved part of the funds to Ethereum](https://etherscan.io/tx/0x42740f84891a9a32581a66919292118fb5ce923fd0c91adf5c38aadaaa4e0efa).
- **November 12, 2024, 13:13 UTC:** DeltaPrime sent an [on-chain message to the attacker](https://snowtrace.io/tx/0x991559bd8e1725714724267071c9ec8cbf31117497cdf259cfd662b0151c2da1?chainid=43114) seeking contact.
- **December 7, 2024:** DeltaPrime published its [post-mortem and reimbursement plan](https://medium.com/@DeltaPrimeDefi/deltaprime-post-mortem-reimbursement-plan-07-12-2024-2d654912715b).

## Security Failure Causes

**Reward-Claim Impersonation Path in DeltaPrime's Post-Mortem:** DeltaPrime's own post-mortem described the exploit primarily as abuse of reward-claim logic that accepted attacker-controlled contracts masquerading as LFJ reward infrastructure.

**Additional Debt-Swap/Input-Validation Flaw in CertiK's Analysis:** CertiK reported that a separate vulnerable path in swap/debt handling allowed borrowed assets to be routed to an attacker-controlled contract without the repayment state behaving as intended.

**Public Analyses Differ on the Full Exploit Chain:** Both DeltaPrime and CertiK described abusive reward-claim behavior, but they framed its role differently. DeltaPrime's post-mortem foregrounded reward-claim impersonation as the main path, while CertiK presented reward-claim abuse as one component of a broader chained two-flaw exploit.

## References

- [DeltaPrime exploit announcement on X](https://x.com/DeltaPrimeDefi/status/1855899502944903195)
- [DeltaPrime Post Mortem & Reimbursement plan 07/12/2024](https://medium.com/@DeltaPrimeDefi/deltaprime-post-mortem-reimbursement-plan-07-12-2024-2d654912715b)
- [CertiK: DeltaPrime Incident Analysis](https://www.certik.com/blog/deltaprime-incident-analysis)
- [Three Sigma: DeltaPrime Hack: $4.85M Loss](https://threesigma.xyz/blog/exploit/deltaprime-defi-exploit-avalanche-arbitrum-hack)
