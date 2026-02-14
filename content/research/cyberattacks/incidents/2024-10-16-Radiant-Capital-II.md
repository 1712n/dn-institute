---
date: 2024-10-16
target-entities: Radiant Capital
entity-types:
  - DeFi
  - Lending Platform
attack-types:
  - Private Key Leak
  - Wallet Hack
tags:
  - North Korea
  - Multisig
title: "Radiant Capital Suffers Second Major Exploit in 2024, Losing $53 Million Across BSC and Arbitrum"
loss: 53000000
---

## Summary

On October 16, 2024, multi-chain lending protocol [Radiant Capital was exploited for over $53 million](https://rekt.news/radiant-capital-rekt2/) across Binance Smart Chain (BSC) and Arbitrum. The attacker compromised at least 3 of 11 private keys in Radiant's multi-signature wallet, which required only a 3-of-11 threshold to execute transactions. With these keys, the attacker transferred ownership of the lending pool contracts to a malicious contract, upgraded the pool implementations, and drained user funds. This was Radiant Capital's [second major security incident in 2024](https://rekt.news/radiant-capital-rekt/), following a $4.5 million flash loan exploit in January. The malicious contracts had been [deployed 14 days before the attack](https://rekt.news/radiant-capital-rekt2/), suggesting weeks of preparation. Blockchain security firm [Ancilia first detected the suspicious activity](https://x.com/AnciliaInc/status/1846606649009885515) as $16 million had already been drained from BSC.

## Attackers

The identity of the attacker has not been officially confirmed. On-chain analysis revealed a sophisticated actor who prepared the attack infrastructure two weeks in advance. The following addresses are associated with this attack:

- Attacker Address 1 (BSC): [0x0629b1048298AE9deff0F4100A31967Fb3f98962](https://bscscan.com/address/0x0629b1048298ae9deff0f4100a31967fb3f98962)
- Attacker Address 2 (Arbitrum): [0x97a05becc2e7891d07f382457cd5d57fd242e4e8](https://arbiscan.io/address/0x97a05becc2e7891d07f382457cd5d57fd242e4e8)
- Malicious Contract (BSC): [0x57ba8957ed2ff2e7AE38F4935451E81Ce1eEFbf5](https://bscscan.com/address/0x57ba8957ed2ff2e7ae38f4935451e81ce1eefbf5)
- Malicious Contract (Arbitrum): [0x57ba8957ed2ff2e7AE38F4935451E81Ce1eEFbf5](https://arbiscan.io/address/0x57ba8957ed2ff2e7ae38f4935451e81ce1eefbf5)
- Funds moved to (Arbitrum): [0x8B75E47976C3C500D0148463931717001F620887](https://arbiscan.io/address/0x8b75e47976c3c500d0148463931717001f620887)
- Funds moved to (BSC): [0xcF47c058CC4818CE90f9315B478EB2f2d588Cc78](https://bscscan.com/address/0xcf47c058cc4818ce90f9315b478eb2f2d588cc78)

## Losses

The total loss exceeded **$53 million** across two chains:

- BSC: ~$16 million drained initially, with additional funds following
- Arbitrum: remaining funds drained in parallel
- Stolen assets were swapped through DEXs (1inch, ParaSwap, PancakeSwap, Odos) for ETH and BNB

## Timeline

- **October 2, 2024:** Attacker [deployed malicious implementation contracts](https://rekt.news/radiant-capital-rekt2/) on BSC and Arbitrum — 14 days before the attack.
- **October 16, 2024:** Attacker used compromised multisig keys to transfer ownership of Radiant's Pool Provider contract to the malicious contract, then upgraded lending pool implementations and drained funds on both [BSC](https://bscscan.com/tx/0xd97b93f633aee356d992b49193e60a571b8c466bf46aaf072368f975dc11841c) and [Arbitrum](https://arbiscan.io/tx/0x7856552db409fe51e17339ab1e0e1ce9c85d68bf0f4de4c110fc4e372ea02fb1).
- **October 16, 2024:** [Ancilia detected suspicious activity](https://x.com/AnciliaInc/status/1846606649009885515) on BSC and warned users to revoke approvals.
- **October 16, 2024:** Two hours after the exploit, [Radiant Capital acknowledged the attack](https://x.com/RDNTCapital/status/1846634050100039881) on BSC and Arbitrum, announced collaboration with security firms, and paused markets on Base and Ethereum mainnet.
- **October 16, 2024:** Stolen funds were swapped via DEXs and moved to fresh wallets.

## Security Failure Causes

- **Low Multisig Threshold:** Radiant's security relied on an 11-signer multisig wallet, but only 3 signatures were required to execute transactions. This 3-of-11 threshold meant an attacker only needed to compromise a small fraction of signers to gain full control of protocol funds.
- **Private Key Compromise:** The attacker obtained at least 3 multisig signer private keys, likely through social engineering, malware, or phishing. The exact compromise method has not been publicly disclosed.
- **Repeat Vulnerability Pattern:** This was Radiant Capital's second major exploit in 2024. The January flash loan exploit should have prompted a comprehensive security overhaul, including raising the multisig threshold, but the low 3-of-11 requirement remained in place.
