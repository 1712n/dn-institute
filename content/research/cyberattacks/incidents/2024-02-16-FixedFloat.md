---
date: 2024-02-16
target-entities:
  - FixedFloat
entity-types:
  - Exchange
attack-types:
  - Infrastructure Attack
  - Private Key Leak
title: "FixedFloat Exchange Hacked for $26 Million in Bitcoin and Ethereum"
loss: 26000000
---

## Summary

On February 16, 2024, [FixedFloat](https://fixedfloat.com/), a non-KYC decentralized cryptocurrency exchange, was exploited for approximately [$26 million](https://medium.com/coinmonks/fixed-float-exploit-tracing-the-26-million-lost-to-the-hack-25fda467b577) in Bitcoin and Ethereum. The attacker drained approximately 409 BTC (~$21 million) and 1,728 ETH (~$4.85 million) across 9 transactions on the Bitcoin and Ethereum networks. The attack is suspected to have resulted from a compromised private key. The exchange initially attributed the outflows to "minor technical problems" before [confirming the hack](https://x.com/FixedFloat/status/1759216185185288653) two days later.

## Attackers

The identity of the attackers remains unknown. The following addresses were used in the exploit:

- **Ethereum attacker address**: [0x85c4fF99bF0eCb24e02921b0D4b5d336523Fa085](https://etherscan.io/address/0x85c4fF99bF0eCb24e02921b0D4b5d336523Fa085)
- **Bitcoin attacker address**: [bc1q2skp47p9f5mr4n4m27k66v0l68gh3xdd7ad4e5](https://www.blockchain.com/explorer/addresses/BTC/bc1q2skp47p9f5mr4n4m27k66v0l68gh3xdd7ad4e5)
- **FixedFloat victim address (Ethereum)**: [0x4E5B2e1dc63F6b91cb6Cd759936495434C7e972F](https://etherscan.io/address/0x4E5B2e1dc63F6b91cb6Cd759936495434C7e972F)
- **FixedFloat victim address (Bitcoin)**: [bc1qns9f7yfx3ry9lj6yz7c9er0vwa0ye2eklpzqfw](https://www.blockchain.com/explorer/addresses/BTC/bc1qns9f7yfx3ry9lj6yz7c9er0vwa0ye2eklpzqfw)

## Losses

- **Total**: approximately $26.1 million
  - [409.3 BTC](https://www.blockchain.com/explorer/addresses/BTC/bc1q2skp47p9f5mr4n4m27k66v0l68gh3xdd7ad4e5) (~$21.15 million) stolen across 5 Bitcoin transactions
  - [1,728.48 ETH](https://etherscan.io/address/0x85c4fF99bF0eCb24e02921b0D4b5d336523Fa085) (~$4.85 million) stolen across 4 Ethereum transactions
- Stolen ETH was transferred to [eXch](https://exch.cx/), a centralized mixing service, to obfuscate the fund trail
- Stolen BTC was distributed through a [complex multi-hop laundering scheme](https://medium.com/coinmonks/fixed-float-exploit-tracing-the-26-million-lost-to-the-hack-25fda467b577) involving fragmentation across hundreds of wallets

## Timeline

- **February 16, 2024, ~21:05 UTC**: First Ethereum attack transaction: a [test drain of 0.007 ETH](https://etherscan.io/tx/0x35abe36b7382376e67d98d8ac8f78ef29e32e0c420e23d6c9b2d7f91a7cb704e) from the FixedFloat contract
- **February 16, 2024, ~21:05–21:39 UTC**: Three additional Ethereum transactions drain [1,076.78 ETH](https://etherscan.io/tx/0x1faa4861a2c32ceaa7c483e8dc91c18e3a9247bac7f2588903691a7a1db4ece8), [650 ETH](https://etherscan.io/tx/0x8f0bd0a0b25788a59d979a58ce4edfba8956679d7a10e1e6ce12ce945e6ce740), and [1.7 ETH](https://etherscan.io/tx/0x78d3a02a03a52f3d096a4fe98da7563388c91cfeedfd5ae4d52d284f12b59879) from the FixedFloat contract within 34 minutes
- **February 16, 2024, ~22:25–22:45 UTC**: Five Bitcoin transactions drain 409.3 BTC in under 20 minutes, including two transactions of [200 BTC each](https://www.blockchain.com/explorer/transactions/btc/15f7ac31837c8dba597f46359857205df1c41573c4bb489b5a81fd058be5da6d)
- **February 16, 2024**: FixedFloat [attributes the outflows](https://x.com/FixedFloat) to "minor technical problems" and puts systems on maintenance
- **February 17, 2024**: On-chain analyst [PeckShield alerts](https://x.com/PeckShieldAlert/status/1759296372325544117) the community to the suspicious fund movements
- **February 18, 2024**: FixedFloat [officially confirms the hack](https://x.com/FixedFloat/status/1759216185185288653): "We confirm that there was indeed a hack and theft of funds. We are not yet ready to make public comments on this matter, as we are working to eliminate all possible vulnerabilities, improve security, and investigate."
- **February 20, 2024**: [Nefture Security publishes](https://medium.com/coinmonks/fixed-float-exploit-tracing-the-26-million-lost-to-the-hack-25fda467b577) a detailed fund tracing report revealing the attacker's laundering strategy: BTC split across multiple hops with 10 BTC increments to holding wallets, and 97.64 BTC dispersed to 72 addresses which further fragmented to 576 addresses holding 0.5 BTC each
- **February 20, 2024**: FixedFloat website remains offline, showing error messages on all pages

## Security Failure Causes

- **Suspected private key compromise**: The attack is believed to have resulted from the compromise of a private key controlling FixedFloat's hot wallet infrastructure. The attacker was able to directly drain funds from the exchange's Ethereum contract and Bitcoin wallet without exploiting a smart contract vulnerability, indicating they had direct access to signing authority.
- **Insufficient hot wallet security**: The exchange stored a significant amount of funds (~$26 million) in hot wallets accessible via a single compromised key, without adequate multi-signature or threshold signature protections that would have required multiple parties to authorize large transfers.
- **Delayed incident response**: FixedFloat took two days to publicly acknowledge the hack, initially misleading users by attributing the massive outflows to "minor technical problems." This delayed response hindered community efforts to track and freeze stolen funds.
- **Lack of transaction monitoring**: The attacker conducted a small test transaction (0.007 ETH) before the main drain, a common attacker pattern that adequate real-time transaction monitoring systems could have detected and used to trigger an automated pause on further withdrawals.
