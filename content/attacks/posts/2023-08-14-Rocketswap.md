---
date: 2023-08-14
target-entities: Rocketswap
entity-types: DeFi
attack-types: Private Key Leak
title: "Rocketswap Suffers $868,000 Loss in Exploit"
loss: 868000
---

## Summary

Rocketswap, a protocol for trading on Base and providing liquidity, suffered a severe security breach on August 14, 2023, leading to a significant loss of $868,000. The exploit was made possible due to the compromise of private keys, which were stored on a server, enabling unauthorized asset transfers.

## Attackers

The identity of the attacker is unknown. The following addresses are associated with this attack:

- [Base](https://basescan.org/address/0x96c0876F573e27636612CF306C9db072d2B13DE8)
- [Ethereum](https://etherscan.io/address/0x96c0876f573e27636612cf306c9db072d2b13de8)

## Losses

Rocketswap lost approximately $868,000 in total. The stolen assets were swapped into 471 ETH.

## Timeline

- **August 14, 2023, 10:53 PM UTC:** The [first malicious](https://basescan.org/tx/0x25c11d664f89ef9237ecf2e8ff1f067821cb829694b184c7ee74e6d0a3f9bfba) transaction occurred.
- **August 15, 2023, 12:25 AM UTC:** Rocketswap [reported](https://twitter.com/RocketSwap_Labs/status/1691229656593371136) about the exploit.
- **August 15, 2023, 02:19 AM UTC:** Rocketswap [announced](https://twitter.com/RocketSwap_Labs/status/1691258298409029632) a new open-sourced farm contract.
- **August 16, 2023:** Rocketswap [announced](https://mirror.xyz/0x4198bADb0c3ea2efF397F3015a81A1c577ECA247/aYhXdB8FadnWPg40V7_VQEUPWaeUK4t32JYenq7IHM8) the Airdrop Сompensation Programme.
- **August 17, 2023:** Neptune Mutual [published](https://neptunemutual.com/blog/taking-a-closer-look-at-rocketswap-exploit) an analysis of the incident.

## Security Failure Causes

- **Insecure Management of Private Keys:** The exploit occurred primarily due to the insecure storage of private keys used for offline signatures on the server.
