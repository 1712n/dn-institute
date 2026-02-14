---
date: 2024-10-16
target-entities: Radiant Capital
entity-types:
  - DeFi
  - Lending Platform
attack-types:
  - Wallet Hack
  - Smart Contract Exploit
tags:
  - North Korea
  - Multisig
title: "Radiant Capital Suffers Second Major Exploit in 2024, Losing ~$50 Million Across BSC and Arbitrum"
loss: 50000000
---

## Summary

On October 16, 2024, multi-chain lending protocol [Radiant Capital was exploited for approximately $50 million](https://medium.com/@RadiantCapital/radiant-post-mortem-fecd6cd38081) across Binance Smart Chain (BSC) and Arbitrum. The attacker compromised at least three core developers' devices through [sophisticated malware injection](https://medium.com/@RadiantCapital/radiant-post-mortem-fecd6cd38081). The malware manipulated the [Safe{Wallet}](https://app.safe.global/welcome) (formerly Gnosis Safe) front-end to display legitimate transaction data while silently sending malicious transactions to their hardware wallets for signing. Transaction simulations on [Tenderly](https://tenderly.co/transaction-simulator) also showed no anomalies, making the compromise [completely undetectable during manual review](https://medium.com/@RadiantCapital/radiant-post-mortem-fecd6cd38081) — a finding confirmed by external security teams [SEAL911](https://securityalliance.org/) and [Hypernative](https://www.hypernative.io/). The attacker collected three valid but malicious signatures by exploiting the normal behavior of Safe transaction resubmissions after failures, then used the 3-of-11 multisig threshold to execute a `transferOwnership` action, upgrade lending pool implementations, and drain funds. This was Radiant Capital's [second major security incident in 2024](https://rekt.news/radiant-capital-rekt/), following a $4.5 million flash loan exploit in January. Blockchain security firm [Ancilia first detected the suspicious activity](https://x.com/AnciliaInc/status/1846606649009885515) on BSC. Radiant later disclosed through its [Mandiant investigation](https://medium.com/@RadiantCapital/radiant-post-mortem-fecd6cd38081) that the attack was attributed to a North Korean threat actor.

## Attackers

The identity of the attacker has not been publicly named. Radiant Capital engaged [Mandiant](https://www.mandiant.com/) for forensic investigation, which [attributed the attack to a North Korean-linked threat actor](https://medium.com/@RadiantCapital/radiant-post-mortem-fecd6cd38081). The attacker demonstrated an advanced understanding of Safe{Wallet} transaction flows and exploited normal multi-signature resubmission behavior to harvest malicious signatures. The malicious implementation contracts were [deployed 14 days before the attack](https://rekt.news/radiant-capital-rekt2/) on both BSC and Arbitrum, indicating weeks of preparation. The following addresses are associated with this attack:

- Attacker Address 1 (BSC): [0x0629b1048298AE9deff0F4100A31967Fb3f98962](https://bscscan.com/address/0x0629b1048298ae9deff0f4100a31967fb3f98962)
- Attacker Address 2 (Arbitrum): [0x97a05becc2e7891d07f382457cd5d57fd242e4e8](https://arbiscan.io/address/0x97a05becc2e7891d07f382457cd5d57fd242e4e8)
- Malicious Contract (BSC): [0x57ba8957ed2ff2e7AE38F4935451E81Ce1eEFbf5](https://bscscan.com/address/0x57ba8957ed2ff2e7ae38f4935451e81ce1eefbf5)
- Malicious Contract (Arbitrum): [0x57ba8957ed2ff2e7AE38F4935451E81Ce1eEFbf5](https://arbiscan.io/address/0x57ba8957ed2ff2e7ae38f4935451e81ce1eefbf5)
- Funds moved to (Arbitrum): [0x8B75E47976C3C500D0148463931717001F620887](https://arbiscan.io/address/0x8b75e47976c3c500d0148463931717001f620887)
- Funds moved to (BSC): [0xcF47c058CC4818CE90f9315B478EB2f2d588Cc78](https://bscscan.com/address/0xcf47c058cc4818ce90f9315b478eb2f2d588cc78)

## Losses

- Total: [approximately $50 million](https://medium.com/@RadiantCapital/radiant-post-mortem-fecd6cd38081) across BSC and Arbitrum
- Additional user funds drained through [exploiting open approvals](https://medium.com/@RadiantCapital/radiant-post-mortem-fecd6cd38081)
- Stolen assets were swapped through DEXs (1inch, ParaSwap, PancakeSwap, Odos) for ETH and BNB

## Timeline

- **October 2, 2024:** Attacker [deployed malicious implementation contracts](https://rekt.news/radiant-capital-rekt2/) on BSC and Arbitrum — 14 days before the attack.
- **October 16, 2024:** During a routine multi-signature emissions adjustment, [compromised developer devices](https://medium.com/@RadiantCapital/radiant-post-mortem-fecd6cd38081) displayed legitimate transaction data on the Safe{Wallet} front-end while routing malicious transactions to hardware wallets. Repeated Safe transaction "failures" prompted resubmissions, allowing the attacker to collect three valid malicious signatures.
- **October 16, 2024:** Attacker used the three compromised signatures to execute `transferOwnership` on Radiant's Pool Provider contract, upgraded lending pool implementations, and drained funds on both [BSC](https://bscscan.com/tx/0xd97b93f633aee356d992b49193e60a571b8c466bf46aaf072368f975dc11841c) and [Arbitrum](https://arbiscan.io/tx/0x7856552db409fe51e17339ab1e0e1ce9c85d68bf0f4de4c110fc4e372ea02fb1).
- **October 16, 2024:** [Ancilia detected suspicious activity](https://x.com/AnciliaInc/status/1846606649009885515) on BSC and warned users to revoke approvals.
- **October 16, 2024:** Two hours after the exploit, [Radiant Capital acknowledged the attack](https://x.com/RDNTCapital/status/1846634050100039881) on BSC and Arbitrum, announced collaboration with security firms including [SEAL911](https://securityalliance.org/) and [Hypernative](https://www.hypernative.io/), and paused markets on Base and Ethereum mainnet.
- **October 18, 2024:** Radiant Capital [published a detailed post-mortem](https://medium.com/@RadiantCapital/radiant-post-mortem-fecd6cd38081) describing the malware-based device compromise and confirming the attack was under investigation with U.S. law enforcement and [ZeroShadow](http://zeroshadow.io).

## Security Failure Causes

- **Device-Level Malware Compromise:** The attackers [compromised at least three core developers' devices](https://medium.com/@RadiantCapital/radiant-post-mortem-fecd6cd38081) through malware injection. The malware intercepted Safe{Wallet} transaction flows, displaying legitimate transaction data on screen while sending malicious payloads to hardware wallets for signing. This made the compromise undetectable through standard front-end verification, Tenderly simulation, or hardware wallet blind-signing review.
- **Low Multisig Threshold:** Radiant's 11-signer multisig wallet required [only 3 signatures to execute transactions](https://rekt.news/radiant-capital-rekt2/). By compromising three developers' devices, the attacker met the threshold needed for full control of protocol funds without alerting the remaining eight signers.
- **Lack of Independent Transaction Verification:** The signing process relied on the Safe{Wallet} interface and Tenderly simulations for transaction review, both of which were compromised at the device level. There was no [independent, uncompromised device used to verify raw transaction data](https://medium.com/@RadiantCapital/radiant-post-mortem-fecd6cd38081) against the hardware wallet payload — a mitigation Radiant themselves recommended in their post-mortem.
- **Repeat Vulnerability Pattern:** This was Radiant Capital's [second major exploit in 2024](https://rekt.news/radiant-capital-rekt/). The January $4.5 million flash loan exploit should have prompted a comprehensive security overhaul, including raising the multisig threshold, but the low 3-of-11 requirement remained in place.
