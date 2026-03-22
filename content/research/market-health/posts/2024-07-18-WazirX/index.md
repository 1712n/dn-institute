---
date: 2024-07-18
entities:
  - WazirX
  - Liminal Custody
  - North Korea
  - Lazarus Group
  - Binance
title: "WazirX: $230M Multi-Sig Wallet Exploit and Custodial Security Failure"
---

## Summary 🌰

On July 18, 2024, WazirX, India's largest cryptocurrency exchange by trading volume, suffered a $230 million theft from its Ethereum multi-signature wallet managed through Liminal Custody's infrastructure. The attacker manipulated the transaction signing process to upgrade the multi-sig wallet's implementation contract to a malicious version, enabling unrestricted fund drainage. Blockchain security firms attributed the attack to North Korea's Lazarus Group based on on-chain behavior patterns and laundering techniques. WazirX halted all withdrawals, initiated a moratorium under Singapore's restructuring framework, and proposed a socialized loss model where all users would bear a 55% haircut on their balances. The incident exposed fundamental flaws in multi-signature custody architecture and the gap between custodial marketing claims and actual security practices. 🌰

## Background 🌰

### Exchange Overview

WazirX was founded in 2018 by Nischal Shetty and operated as India's leading cryptocurrency exchange, reporting over 15 million registered users and $38 billion in total trading volume. The exchange operated in a complex jurisdictional structure — incorporated in India but owned by Zanmai Labs Pvt. Ltd., with a disputed acquisition relationship with Binance that became contentious after the hack.

### Custody Arrangement 🌰

WazirX used a multi-signature wallet architecture for its Ethereum holdings:
- **Wallet type**: Gnosis Safe (now Safe) multi-sig contract
- **Signing threshold**: 4 of 6 signers required to authorize transactions
- **Signer distribution**: 3 WazirX signers + 3 Liminal Custody signers (with 1 required from each side)
- **Custody provider**: Liminal Custody Solutions, a Mumbai-based digital asset custody platform
- **Hardware security**: Signing keys stored in Ledger hardware wallets

The multi-sig wallet held the majority of WazirX's Ethereum and ERC-20 token reserves, valued at approximately $230 million at the time of the attack. 🌰

## The Attack 🌰

### Phase 1: Reconnaissance and Test Transactions

On-chain analysis revealed that the attacker conducted at least 8 days of preparation before the exploit:

- **July 10–17**: Small test transactions were executed through the multi-sig wallet to understand the signing flow, transaction format, and the interaction between WazirX's signing interface and Liminal's co-signing infrastructure
- The attacker deployed the malicious implementation contract on July 16, 2024 — two days before the attack

### Phase 2: Transaction Manipulation (July 18, ~06:18 UTC) 🌰

The attack exploited a discrepancy between what the signers saw on their Ledger hardware wallet screens and what was actually being signed:

1. **Legitimate-appearing transaction**: The attacker submitted a transaction through Liminal's infrastructure that appeared to WazirX signers as a routine USDT transfer
2. **Payload substitution**: The actual transaction payload was a call to the Safe's `execTransaction` method, but with a `delegatecall` to a malicious contract that executed `changeProxyAdmin` and `upgradeTo` functions
3. **Blind signing exploitation**: The Ledger hardware wallets displayed the transaction as a contract interaction with the expected Safe address, but the inner call data — which performed the implementation upgrade — was not human-readable on the device screen
4. **Three legitimate signatures collected**: Three WazirX signers approved what they believed was a standard transfer. Liminal's fourth signature was automatically applied as the co-signing node validated the transaction format

The result: the multi-sig wallet's implementation contract was upgraded from the legitimate Safe implementation to the attacker's malicious contract, which had a single function — `transfer(address,address,uint256)` — callable by the attacker alone. 🌰

### Phase 3: Fund Drainage (06:18–07:45 UTC)

With control of the wallet's implementation, the attacker systematically drained all assets:

| Asset | Amount | Value (USD) |
|-------|--------|-------------|
| SHIB | 5.43T | $102.0M |
| ETH | 15,298 | $52.5M |
| MATIC | 20.5M | $11.2M |
| PEPE | 7.6T | $7.5M |
| USDT | 5.79M | $5.8M |
| GALA | 74.7M | $3.5M |
| Other ERC-20 | Various | $47.5M |
| **Total** | | **~$230M** |

The drainage took approximately 90 minutes. WazirX detected the unauthorized transactions roughly 30 minutes after drainage began but could not halt the process — the attacker already had full control of the wallet. 🌰

## Laundering and Attribution 🌰

### On-Chain Behavior

The stolen funds were laundered through a pattern consistent with North Korean state-sponsored hacking groups:

1. **Immediate token consolidation**: All ERC-20 tokens were swapped to ETH through Uniswap V3 and 1inch within hours of the theft
2. **Tornado Cash mixing**: Batches of 100 ETH were sent through Tornado Cash starting July 19, 2024
3. **Chain-hopping**: Portions of funds were bridged to Bitcoin via THORChain and cross-chain bridges
4. **Dormancy periods**: Consistent with Lazarus Group operational patterns, some fund batches remained dormant for weeks before being moved

### Lazarus Group Attribution 🌰

Multiple blockchain analytics firms (Elliptic, ZachXBT, Arkham Intelligence) attributed the attack to North Korea's Lazarus Group based on:
- Reuse of wallet addresses linked to prior Lazarus operations
- Identical laundering methodology to the $625M Ronin Bridge hack (2022) and $100M Harmony Bridge hack (2022)
- Timing patterns consistent with Pyongyang working hours
- Use of the same Tornado Cash and THORChain routing infrastructure

## Aftermath and User Impact 🌰

### Withdrawal Halt and Moratorium

WazirX halted all withdrawals on July 18, 2024. On August 14, 2024, the company filed for a moratorium under the Singapore Companies Act's restructuring provisions — despite being primarily an Indian exchange serving Indian customers.

### Socialized Loss Proposal

WazirX proposed a restructuring scheme where:
- All users would absorb a **55% haircut** on their total balances
- The remaining 45% would be available for withdrawal over an extended timeline
- Users who held assets NOT on the compromised Ethereum wallet (e.g., INR balances, tokens on other chains) would still absorb losses proportional to their total account value
- WazirX would issue "recovery tokens" representing claims on potentially recovered stolen funds

This socialized loss model was widely criticized because it forced users whose assets were never stolen to subsidize the losses of the compromised wallet. 🌰

### Binance Ownership Dispute

The hack surfaced a disputed ownership relationship between WazirX and Binance. In November 2019, Binance had announced the "acquisition" of WazirX. However, after the hack:
- Binance CEO Richard Teng stated that Binance "does not own, operate, or control WazirX"
- Nischal Shetty maintained that the acquisition was completed and that Binance held the crypto assets
- No formal share transfer agreement was ever publicly produced
- This dispute left users without a clear liable party for the lost funds 🌰

## Technical Analysis: Multi-Sig Security Failure 🌰

### What the Architecture Was Supposed to Prevent

The 4-of-6 multi-sig with hardware wallet signing was designed to prevent:
1. Single point of compromise (no individual key can authorize transactions)
2. Remote key extraction (hardware wallets prevent key export)
3. Unauthorized transactions (multiple parties must independently verify and sign)

### Why It Failed

The architecture failed because it protected against the wrong threat model:

1. **Payload opacity**: Hardware wallets display the target contract address and ETH value, but cannot meaningfully display complex contract interaction data. Signers approved a transaction whose actual effect (implementation upgrade) was invisible to them.

2. **Trust in the intermediary**: Liminal's co-signing infrastructure was trusted to validate transaction content, but either its validation was insufficient or the attacker had compromised it to bypass content checks.

3. **No independent simulation**: Neither WazirX nor Liminal ran a simulation of the transaction's effects before signing. A Tenderly or similar simulation would have immediately shown that the transaction upgraded the Safe's implementation — which should never occur in a routine transfer.

4. **No transaction type whitelist**: The multi-sig had no restriction on what types of transactions could be executed. A security-conscious configuration would have whitelisted only `transfer` and `approve` calls, blocking `delegatecall` and `upgradeTo` operations entirely. 🌰

## Systemic Lessons 🌰

1. **Multi-sig is not security**: Multi-signature wallets protect against key compromise but not against transaction content manipulation. If all signers approve the same malicious payload, the multi-sig provides zero protection.

2. **Hardware wallet blind signing**: When hardware wallets cannot display human-readable transaction details, they become approval stamps rather than verification tools. EIP-712 typed data signing partially addresses this, but complex contract interactions remain opaque.

3. **Custodial marketing vs reality**: Liminal marketed its custody solution as institutional-grade with multiple security layers. The attack demonstrated that the actual security was dependent on signers correctly interpreting opaque transaction data — which humans cannot do.

4. **Jurisdictional arbitrage in crisis**: WazirX, an Indian exchange serving Indian customers, filed for protection under Singapore law — choosing the jurisdiction most favorable to the company rather than its users.

5. **Socialized losses as moral hazard**: Spreading losses across all users — including those whose assets were never at risk — creates perverse incentives. It effectively means the exchange's choice of custodial architecture becomes every user's risk, regardless of which assets they hold. 🌰

## References 🌰

1. WazirX Official Post-Mortem Statement, July 2024
2. Liminal Custody Incident Response Report, July 2024
3. Elliptic Research: WazirX Hack Attribution Analysis, July 2024
4. ZachXBT On-Chain Investigation Thread, July 2024
5. Singapore High Court, WazirX Moratorium Application, August 2024
6. CertiK Security Incident Analysis: Multi-Sig Vulnerability, July 2024
7. Gnosis Safe (Safe) Implementation Architecture Documentation
