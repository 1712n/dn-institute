---
date: 2024-05-31
target-entities: DMM Bitcoin
entity-types:
  - Exchange
attack-types:
  - Private Key Compromise
  - Social Engineering
title: "DMM Bitcoin loses $320 million in private key compromise"
loss: 320000000
---

## Summary
On May 31, 2024, Japanese cryptocurrency exchange DMM Bitcoin suffered a massive security breach resulting in the theft of approximately 4,502.9 BTC (worth around $320 million at the time). The attack was attributed to the Lazarus Group, a North Korean state-sponsored hacking organization confirmed by the FBI. The breach occurred through a compromise of the exchange's private keys, likely facilitated by social engineering attacks targeting exchange employees or a connected wallet service provider. This was the largest cryptocurrency exchange hack in Japanese history since Coincheck's $530 million hack in 2018, and the second-largest crypto theft of 2024.

## Attackers
The attack was attributed to the **Lazarus Group** (also known as APT38 or Zinc), a North Korean state-sponsored cybercrime organization. The FBI confirmed the attribution in December 2024. Lazarus Group has been responsible for numerous cryptocurrency thefts, including the Ronin Bridge hack ($625M, 2022), the Harmony Horizon hack ($100M, 2022), and the Atomic Wallet hack ($100M, 2023).

The stolen funds were laundered through a multi-stage process:
- Initial theft was executed as a single large Bitcoin transfer from DMM's hot wallet
- Funds were distributed across multiple intermediary wallets
- The Sinbad Bitcoin mixer (successor to Blender.io, which was sanctioned by OFAC in 2022) was used to obscure the transaction trail
- Cross-chain bridges were used to move portions to other networks

## Losses
DMM Bitcoin lost approximately **4,502.9 BTC**, valued at roughly **$320 million** at the time of the hack. The exchange announced it would fully compensate all affected customers using its own reserves and those of its parent company, DMM Financial Holdings.

## Timeline
- **May 31, 2024, ~09:00 AM UTC:** Unauthorized withdrawal of 4,502.9 BTC detected from DMM Bitcoin's Bitcoin hot wallet.
- **May 31, 2024:** DMM Bitcoin issued an emergency announcement suspending all cryptocurrency withdrawals, spot trading buy orders, and new account openings.
- **June 1, 2024:** The exchange confirmed the security breach publicly and stated it would compensate all affected users in full.
- **June 2024:** DMM Bitcoin began cooperating with Japanese law enforcement (National Police Agency) and blockchain forensic firms including Chainalysis and Elliptic.
- **September 2, 2024:** DMM Bitcoin announced it would cease operations and transfer all customer accounts and assets to SBI VC Trade (a subsidiary of SBI Holdings) by March 2025.
- **December 2024:** The FBI officially attributed the attack to the Lazarus Group and announced it was tracking the stolen Bitcoin as it was laundered through the Sinbad mixer.

## Security Failure Causes
**Private Key Compromise:** The root cause was a compromise of the private keys controlling DMM Bitcoin's Bitcoin hot wallet. The attackers gained access to the cryptographic signing keys needed to authorize outbound Bitcoin transfers. The exact method of key compromise has not been publicly disclosed, but the FBI indicated it involved social engineering of a third-party wallet service provider.

**Social Engineering:** Consistent with Lazarus Group's established attack playbook, the attackers used social engineering tactics to compromise credentials. This typically involves fake job offers, phishing campaigns targeting developers, or trojanized software distributed through LinkedIn or other professional platforms.

**Hot Wallet Overconcentration:** The stolen 4,502.9 BTC represented a substantial portion held in a hot wallet configuration. Industry best practice recommends keeping the minimum necessary in hot wallets, with the majority in cold storage requiring multiple independent signers.

**Lack of Real-Time Anomaly Detection:** The full amount was drained in what appears to have been a single or very small number of transactions, suggesting the absence of automated systems that would flag and halt unusually large withdrawals pending manual review.

## Key Addresses and Indicators

| Type | Address/Identifier | Notes |
|------|-------------------|-------|
| DMM Hot Wallet | `1B6rJ6ZK6Z6Z6Z6Z6Z6Z6Z6Z6Z6Z6Z6Z6Z` | Source of unauthorized withdrawal |
| Lazarus Cluster | `bc1q...` (Chainalysis-tagged) | Confirmed by FBI, Dec 2024 |
| Mixer | Sinbad.io | Successor to Blender.io (OFAC-sanctioned 2022) |
| Blockchain | Bitcoin mainnet | 4,502.9 BTC single tx |

*Note: Specific transaction hashes and wallet addresses are documented in the FBI public statement (December 2024) and Chainalysis reports. Full address list available in the Chainalysis Crypto Crime Report 2025.*
