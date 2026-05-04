---
title: "🌰 Wormhole Bridge Exploit — Signature Verification Bypass and $320M Cross-Chain Token Theft"
date: 2026-05-04
entities:
  - Wormhole
  - Solana
  - Ethereum
  - Jump Crypto
  - wETH
---

## Summary

1. **On February 2, 2022, the Wormhole cross-chain bridge was exploited for approximately 120,000 wrapped Ether (wETH)**, worth approximately $320 million at the time. This was the second-largest DeFi exploit in history at the time of occurrence and remains one of the most significant cross-chain bridge attacks ever documented.
2. **The exploit targeted a signature verification vulnerability** in Wormhole's Solana-side smart contract. The attacker bypassed the guardian signature verification process by abusing unchecked instruction loading in the `verify_signatures` path, allowing them to forge validation of fraudulent messages.
3. **The attacker minted 120,000 wETH on Solana without depositing any ETH on Ethereum**, then bridged 93,750 of those wETH tokens back to Ethereum, extracting real ETH from the bridge's reserves. The remaining wETH was used on Solana DeFi protocols.
4. **Jump Crypto, a major backer of the Wormhole ecosystem, replaced the stolen funds** within hours by depositing 120,000 ETH (~$320M) into the bridge contract to restore the 1:1 backing of wETH. This emergency intervention prevented a broader collapse of Solana DeFi protocols that relied on wETH as collateral.
5. **In February 2023, a UK High Court order enabled a counter-exploit recovery of roughly $140 million** from positions associated with the attacker. In April 2024, the UK's National Crime Agency reported an arrest connected to the exploit.

## Background

Wormhole is a cross-chain messaging protocol that enables token transfers between blockchains including Ethereum, Solana, BNB Chain, Polygon, Avalanche, and others. At its core, Wormhole operates through a set of 19 "guardian" nodes that observe events on one chain and attest to them on another through multi-signature verification.

The bridge's basic token transfer process:

1. User locks tokens (e.g., ETH) in Wormhole's contract on the source chain (Ethereum)
2. Guardian nodes observe the lock event and produce a signed attestation (VAA — Verified Action Approval)
3. User submits the signed VAA to Wormhole's contract on the destination chain (Solana)
4. The destination contract verifies guardian signatures and mints wrapped tokens (wETH)

The security of this system depends entirely on the integrity of the signature verification step. If an attacker can forge or bypass guardian signatures, they can mint arbitrary amounts of wrapped tokens without locking any real assets.

## 🌰 Technical Exploit Mechanics

### The Vulnerability: `verify_signatures` Bypass

The Wormhole Solana program used a two-step process for validating guardian attestations:

**Step 1 — `verify_signatures`**: Verify the cryptographic signatures of the guardian set against the message hash, storing the verification result in a `SignatureSet` account.

**Step 2 — `post_vaa`**: Read the `SignatureSet` account to confirm that enough valid signatures exist, then process the message (e.g., mint wETH).

The vulnerability was in Step 1. The `verify_signatures` instruction was supposed to call Solana's native `secp256k1_recover` system program to validate ECDSA signatures. However, the Wormhole code used `load_instruction_at` to read the instruction data rather than directly invoking the system program. Critically, it failed to verify that the instruction it was reading actually came from the legitimate `secp256k1` system program.

The attacker exploited this by:

1. Creating a fake instruction that mimicked the output format of `secp256k1_recover` but was actually executed by a program the attacker controlled
2. This fake instruction returned "valid" signature results for guardian signatures that had never actually been checked
3. The `verify_signatures` instruction accepted this forged verification and created a `SignatureSet` account showing valid guardian consensus
4. The `post_vaa` instruction read this fraudulent `SignatureSet` and processed the attacker's message as if it had legitimate guardian approval

### The Root Cause: Deprecated `load_instruction_at`

The specific function exploited was `load_instruction_at`, which was already deprecated in favor of `load_instruction_at_checked` at the time of the attack. The checked version verifies that the instruction being loaded actually belongs to the expected program (in this case, the `secp256k1` system program). The unchecked version does not perform this validation.

A patch had been developed to replace the deprecated function call but had not yet been deployed to mainnet at the time of the attack. The commit fixing this vulnerability was visible in Wormhole's public GitHub repository before the exploit occurred, though it is unclear whether the attacker discovered the vulnerability independently or by reviewing the pending fix.

### Attack Execution Timeline

| Time (UTC) | Event |
|------------|-------|
| Feb 2, ~17:00 | Attacker begins testing on Solana devnet |
| Feb 2, ~18:15 | First exploit transaction on Solana mainnet |
| Feb 2, ~18:15-18:30 | Attacker mints 120,000 wETH on Solana via forged VAA |
| Feb 2, ~18:30 | Attacker bridges 93,750 wETH to Ethereum, receiving real ETH |
| Feb 2, ~18:30-19:00 | Attacker uses remaining ~26,250 wETH on Solana (swaps, DeFi deposits) |
| Feb 2, ~21:00 | Wormhole team confirms exploit, pauses bridge |
| Feb 3, ~02:00 | Jump Crypto deposits 120,000 ETH to restore wETH backing |

## Market Impact

### Immediate Price Effects

The Wormhole exploit created a temporary crisis in the Solana DeFi ecosystem because wETH was widely used as collateral:

- **SOL price**: Dropped approximately 10% in the hours following the exploit disclosure, from ~$107 to ~$96
- **wETH on Solana**: Briefly traded at a discount to ETH on Solana DEXs as traders feared the wrapped token had lost its backing
- **Solana DeFi TVL**: Public TVL trackers showed a sharp decline around the disclosure window as traders reassessed bridge-backed collateral risk

Jump Crypto's rapid fund replacement prevented a cascading liquidation event. If wETH had remained unbacked:

1. Lending protocols (Solend, Mango Markets, etc.) holding wETH as collateral would have faced a solvency gap
2. Borrowers using wETH as collateral would have been liquidated
3. The resulting sell pressure could have triggered a broader DeFi delevering cascade

### Volume and Trading Anomalies

In the hours surrounding the exploit:

- **Wormhole bridge volume**: Spiked as the attacker moved funds, then dropped to zero when the bridge was paused
- **Solana DEX volume**: Increased approximately 3x as traders rushed to sell wETH positions and adjust DeFi exposure
- **Cross-chain arbitrage**: Temporary wETH/ETH price discrepancies created arbitrage opportunities that sophisticated traders captured before the bridge was paused

## 🌰 On-Chain Fund Flow Analysis

### Attacker's Wallet Activity

The primary exploit wallet on Ethereum (`0x629e7Da20197a5429d30da36E77d06CdF796b71A`) showed clear patterns:

1. **Initial funding**: The wallet was funded with small amounts of ETH for gas fees approximately 24 hours before the exploit
2. **Bulk receipt**: 93,750 ETH received from Wormhole bridge in rapid succession
3. **Diversification**: The attacker distributed funds across multiple DeFi protocols and addresses on Ethereum
4. **Partial bridging**: Some funds were moved to other chains using alternative bridges

On Solana, the remaining ~26,250 wETH was deployed into:

- Liquidity positions on Solana DEXs
- Lending protocol deposits
- Further swaps to SOL and stablecoins

### Recovery Efforts

- **February 2023**: Oasis.app was ordered by the UK High Court to enable a counter-exploit that recovered roughly $140 million from positions associated with the attacker
- **April 2024**: The UK's National Crime Agency reported an arrest connected to the Wormhole exploit
- The total recovered amount remains below the original $320 million stolen

## Broader Bridge Security Implications

### Cross-Chain Bridge Attack Pattern

The Wormhole exploit fits a pattern of bridge attacks that together account for billions in losses:

| Bridge | Date | Amount Stolen | Attack Vector |
|--------|------|---------------|---------------|
| Ronin Bridge | Mar 2022 | $625M | Compromised validator keys |
| Wormhole | Feb 2022 | $320M | Signature verification bypass |
| Nomad Bridge | Aug 2022 | $190M | Message replay (initialization bug) |
| Harmony Horizon | Jun 2022 | $100M | Compromised multisig keys |
| Multichain | Jul 2023 | $126M | Compromised MPC keys |

Cross-chain bridges represent concentrated risk because they hold large pools of locked assets and depend on external validation mechanisms (guardians, relayers, multisigs) rather than the consensus security of the underlying chains.

### Why Bridges Are High-Value Targets

1. **Asset concentration**: Bridges hold the backing assets for all wrapped tokens on destination chains. A single bridge contract may hold hundreds of millions in ETH, USDC, or other tokens.
2. **Validation complexity**: Bridge security depends on off-chain components (guardian networks, relayers) that introduce attack surface beyond the smart contract itself.
3. **Cross-chain opacity**: Monitoring systems on one chain cannot easily detect anomalies originating from another chain. The Wormhole attacker executed the exploit on Solana but extracted value on Ethereum.
4. **Upgrade lag**: Bridge contracts must be deployed across multiple chains. A vulnerability fix on one chain may not be deployed simultaneously on all chains, creating windows of exposure.

## Lessons for Market Surveillance

The Wormhole exploit highlights detection patterns relevant to bridge security and market surveillance:

1. **Sudden large mint events**: Any wrapped token mint that exceeds normal daily bridge volume by >10x should trigger immediate investigation. The 120,000 wETH mint was orders of magnitude larger than typical Wormhole transfers.

2. **Cross-chain asset ratio monitoring**: For any bridge, the ratio of wrapped tokens on destination chains to locked assets on source chains should always be approximately 1:1. A deviation indicates either a legitimate operational issue or an exploit. Continuous monitoring of this ratio is the most direct detection mechanism.

3. **Signature verification audits**: Bridge contracts should be regularly audited for the specific pattern exploited here: accepting instruction results without verifying the instruction's source program. This extends to any system where one contract trusts the output of another without verifying its identity.

4. **Deprecated function usage**: Smart contracts using deprecated system calls should be flagged for priority remediation. The `load_instruction_at` function was deprecated specifically because it lacked the safety check that would have prevented this exploit.

5. **Public repository exposure**: Security-critical patches visible in public repositories before deployment create a race condition between the patch deployment and attacker exploitation. Bridge teams should consider private patch development and coordinated deployment across all chains simultaneously.

6. **Post-exploit market monitoring**: After any bridge exploit, surveillance should monitor for: wETH/ETH price deviations on destination chain DEXs, unusual lending protocol liquidation activity, and cross-chain fund flows from the attacker's known addresses.

## References

1. Wormhole. "Wormhole Incident Report — 02/02/22." Wormhole Foundation Post-Mortem, February 2022.
2. Samczsun (paradigm). "Wormhole Exploit Analysis." Twitter/X thread, February 2, 2022.
3. CertiK. "Wormhole Bridge Exploit — Full Analysis." CertiK Research, February 2022.
4. Chainalysis. "The 2023 Crypto Crime Report." Chapter 4: Bridge Exploits. Chainalysis Inc., January 2023.
5. UK High Court of Justice. "Oasis.app Order for Counter-Exploit Recovery." February 2023.
6. Jump Crypto. Statement on Wormhole fund replacement. February 3, 2022.
7. National Crime Agency (UK). "Arrest in Connection with Wormhole Cryptocurrency Theft." April 2024.
8. Rekt News. "Wormhole — REKT." rekt.news, February 2, 2022.
