---
date: 2026-02-02
target-entities: CrossCurve
entity-types:
  - DeFi
  - Bridge
attack-types: Smart Contract Exploit
title: CrossCurve bridge exploited for approximately $3 million via spoofed cross-chain messages
loss: 3000000
---

## Summary

On February 2, 2026, [CrossCurve](https://crosscurve.fi/), a cross-chain bridge and DEX built with [Curve Finance](https://curve.fi/) infrastructure, was [exploited for approximately $3 million](https://www.theblock.co/post/387939/crosscurve-bridge-exploited-for-approximately-3-million-across-multiple-chains-via-spoofed-messages) across multiple blockchains. The attack exploited a [missing access control validation](https://x.com/MixBytes/status/2018304206763892766) in CrossCurve's ReceiverAxelar contracts, which were designed to receive and validate cross-chain messages from the [Axelar](https://axelar.network/) messaging protocol. Attackers crafted spoofed cross-chain messages that bypassed the contract's validation checks, instructing the PortalV2 bridge contracts to unlock and release tokens without a corresponding deposit on another chain. The exploit affected multiple chains including Ethereum, Arbitrum, Optimism, Base, Mantle, Kava, Frax, Celo, and Blast. CrossCurve [identified 10 wallets](https://invezz.com/news/2026/02/02/crosscurve-identifies-10-wallets-involved-in-the-3m-bridge-exploit/) involved in the exploit and shut down the platform to investigate and remediate the vulnerability.

## Attackers

The attacker(s) behind the CrossCurve hack have not been publicly identified. [Multiple attacker wallets](https://invezz.com/news/2026/02/02/crosscurve-identifies-10-wallets-involved-in-the-3m-bridge-exploit/) (at least 10) were involved in the exploit, suggesting either a coordinated group or multiple independent actors who discovered the vulnerability. After draining funds, the attackers [swapped and bridged stolen tokens](https://www.halborn.com/blog/post/explained-the-crosscurve-hack-february-2026) to more liquid assets and performed laundering operations to cover their tracks.

### Attack Method

The exploit targeted a [fundamental access control flaw](https://www.halborn.com/blog/post/explained-the-crosscurve-hack-february-2026) in CrossCurve's bridge architecture:

1. **Vulnerability Identification:** The attacker identified that CrossCurve's `expressExecute`-like functions in the ReceiverAxelar contracts [lacked proper validation](https://x.com/MixBytes/status/2018304206763892766) to verify that incoming messages actually originated from the Axelar network.

2. **Message Spoofing:** The attacker crafted malicious messages that mimicked legitimate Axelar cross-chain messages, specifying a target address and token amount to release.

3. **Validation Bypass:** Because the ReceiverAxelar contract's [validation checks were insufficient](https://www.halborn.com/blog/post/explained-the-crosscurve-hack-february-2026), the spoofed messages were accepted as legitimate, causing the contract to instruct the PortalV2 bridge contract to unlock assets.

4. **Multi-Chain Drain:** The attacker repeated this exploit across [multiple chains supported by CrossCurve](https://coinedition.com/crosscurve-bridge-exploited-for-3m-after-spoofed-cross-chain-messages/) — Ethereum, Arbitrum, Optimism, Base, Mantle, Kava, Frax, Celo, and Blast — draining tokens from each chain's PortalV2 contract.

5. **Fund Laundering:** Stolen tokens were swapped to more liquid assets and bridged across chains to obfuscate the trail.

## Losses

[BlockSec estimated](https://coinedition.com/crosscurve-bridge-exploited-for-3m-after-spoofed-cross-chain-messages/) total losses at approximately **$2.76–$3 million**, distributed across multiple chains:

- **Ethereum:** ~$1.3 million
- **Arbitrum:** ~$1.28 million
- **Optimism, Base, Mantle, Kava, Frax, Celo, Blast:** Smaller amounts drained across these chains

CrossCurve [identified 10 wallets](https://invezz.com/news/2026/02/02/crosscurve-identifies-10-wallets-involved-in-the-3m-bridge-exploit/) associated with the exploit.

## Timeline

- **February 2, 2026:** Attackers exploit [missing access control validation](https://x.com/MixBytes/status/2018304206763892766) in CrossCurve's ReceiverAxelar contracts, spoofing cross-chain messages to drain PortalV2 contracts across multiple chains.
- **February 2, 2026:** Security firm [Defimon Alerts identifies](https://www.cryptotimes.io/2026/02/02/crosscurve-suffers-3m-loss-in-cross-chain-smart-contract-breach/) the exploit and flags the ReceiverAxelar contract vulnerability.
- **February 2, 2026:** CrossCurve [publicly confirms the attack](https://x.com/crosscurvefi/status/2018063302199488687) on X and warns users to halt all activity on the platform.
- **February 2, 2026:** CrossCurve [shuts down the platform](https://www.halborn.com/blog/post/explained-the-crosscurve-hack-february-2026) to investigate and remediate the vulnerability.
- **February 2, 2026:** CrossCurve [identifies 10 attacker wallets](https://invezz.com/news/2026/02/02/crosscurve-identifies-10-wallets-involved-in-the-3m-bridge-exploit/) involved in the exploit.
- **February 2, 2026:** [BlockSec estimates total losses](https://coinedition.com/crosscurve-bridge-exploited-for-3m-after-spoofed-cross-chain-messages/) at approximately $2.76 million, with ~$1.3M on Ethereum and ~$1.28M on Arbitrum.

## Security Failure Causes

- **Missing Access Control Validation:** The core vulnerability was a [lack of proper sender validation](https://www.halborn.com/blog/post/explained-the-crosscurve-hack-february-2026) in the ReceiverAxelar contracts. The `expressExecute`-like functions did not adequately verify that incoming messages originated from the legitimate Axelar gateway, allowing anyone to craft and submit spoofed messages.
- **Insufficient Message Origin Verification:** The bridge architecture [relied on the ReceiverAxelar contract](https://x.com/MixBytes/status/2018304206763892766) to validate message authenticity, but the validation logic was flawed. Proper cross-chain bridge design requires cryptographic proof or gateway-level access controls to ensure only authorized relayers can trigger fund releases.
- **Multi-Chain Attack Surface:** The same vulnerability existed across [all chains where CrossCurve operated](https://coinedition.com/crosscurve-bridge-exploited-for-3m-after-spoofed-cross-chain-messages/), multiplying the impact. A single vulnerability in the shared contract design affected Ethereum, Arbitrum, Optimism, Base, Mantle, Kava, Frax, Celo, and Blast simultaneously.
- **Lack of Comprehensive Security Audit:** Cross-chain bridge contracts are [among the highest-risk DeFi components](https://www.halborn.com/blog/post/explained-the-crosscurve-hack-february-2026) due to their role in authorizing fund releases based on external messages. The fundamental nature of the access control flaw suggests insufficient security review of the bridge's core validation logic.
