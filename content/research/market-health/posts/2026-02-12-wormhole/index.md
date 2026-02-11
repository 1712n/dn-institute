---
title: "Wormhole: $320M Bridge Exploit via Signature Verification Bypass, Jump Crypto Bailout, and Court-Ordered Counter-Exploit Recovery"
date: 2026-02-12
entities:
  - Wormhole
  - Jump Crypto
---

## Summary

1. **$320 million stolen through signature verification bypass**: On February 2, 2022, an attacker exploited a vulnerability in Wormhole's Solana-side `verify_signatures` function, using a fake system program account to bypass guardian signature verification and mint 120,000 wETH (~$320 million) without depositing any collateral on Ethereum.
2. **Architectural flaw in Solana account validation**: The exploit targeted the `verify_signatures` instruction, which used `load_instruction_at` to read the Secp256k1 signature verification results but did not validate that the instruction data actually came from the legitimate Secp256k1 system program — allowing the attacker to supply a forged account with pre-approved verification results.
3. **Jump Crypto replaced all 120,000 ETH**: Jump Trading's crypto division, **Jump Crypto** (which operated Wormhole's guardian network), replaced the full 120,000 ETH (~$320 million) from its own reserves within 24 hours, making all wETH holders whole without any user losses.
4. **$225 million recovered via court-ordered counter-exploit**: In February 2023, approximately $225 million of the stolen funds was recovered through an unprecedented court-ordered operation: a UK High Court order authorized Oasis.app to execute a counter-exploit on its own smart contracts, upgrading a proxy to extract the attacker's funds from a MakerDAO vault.
5. **$10 million bug bounty offered — ignored**: Wormhole publicly offered the attacker a $10 million white-hat bounty for returning the funds, the largest publicly known bug bounty offer in DeFi history at the time, but the attacker never responded.

## Background

### Wormhole Bridge Protocol

**Wormhole** is a cross-chain messaging and token bridge protocol originally developed by **Certus One** and launched in **September 2021**. The protocol enables asset transfers between blockchains including Ethereum, Solana, Binance Smart Chain, Polygon, Avalanche, and others [1].

The bridge works through a **guardian network** — a set of 19 trusted validators (at the time of the exploit) who observe transactions on one chain and attest to their validity on the destination chain. These guardians were operated by major crypto entities, with **Jump Crypto** being the primary operator and development partner.

### Wrapped Token System

Wormhole's bridge creates **wrapped tokens** on destination chains:

- A user deposits native ETH on Ethereum into the Wormhole contract
- Guardians observe the deposit and sign an attestation (Verifiable Action Approval, or "VAA")
- The user submits the signed VAA on Solana
- Wormhole's Solana contract verifies the guardian signatures and mints an equivalent amount of **wETH** (wrapped ETH)
- wETH is redeemable 1:1 for ETH locked in the Ethereum-side contract

The security of the entire system depends on the integrity of the **signature verification process** on each destination chain.

### The Vulnerability: `verify_signatures` on Solana

Wormhole's Solana program used a two-step process for verifying guardian signatures [2]:

1. **Step 1** (`verify_signatures`): Verify the cryptographic signatures of the guardians using Solana's native **Secp256k1** signature verification program
2. **Step 2** (`post_vaa`): Check that sufficient guardian signatures were verified, then execute the bridge operation (minting wrapped tokens)

The critical flaw was in **Step 1**: the `verify_signatures` instruction used Solana's `load_instruction_at` function to read the results of the Secp256k1 verification. However, the code **did not validate that the account providing the instruction data was actually the legitimate Secp256k1 system program** (`Secp256k1Program`). This meant an attacker could substitute a **fake account** containing pre-crafted "verified" results.

## The Exploit (February 2, 2022)

### Attack Execution

At approximately **18:24 UTC on February 2, 2022**, the attacker exploited the signature verification bypass [3]:

**Step 1 — Create a fake Secp256k1 account**: The attacker created a Solana account that mimicked the output format of the Secp256k1 signature verification program but contained fabricated results showing that a quorum of guardians had signed a deposit message.

**Step 2 — Call `verify_signatures` with fake sysvar**: The attacker called Wormhole's `verify_signatures` instruction, passing their fake account instead of the real `Sysvar::Instructions` account. Because the code only called `load_instruction_at` without verifying the account's address, the function accepted the forged verification results.

**Step 3 — Call `post_vaa` to register forged message**: With the fabricated signature verification in place, the attacker called `post_vaa` to register a VAA claiming that 120,000 ETH had been deposited on Ethereum. The contract accepted this as a legitimate, guardian-approved message.

**Step 4 — Mint 120,000 wETH**: The attacker submitted the forged VAA to mint **120,000 wETH** on Solana — worth approximately **$320 million** at the time.

**Step 5 — Bridge and convert**: The attacker:
- Bridged **93,750 ETH** back to Ethereum through the Wormhole bridge (draining the Ethereum-side reserves)
- Converted the remaining wETH to SOL and USDC on Solana DEXs
- Deposited a portion into Solana lending protocols

### Stolen Amounts

| Chain | Amount | Value |
|-------|--------|-------|
| Ethereum (bridged back) | 93,750 ETH | ~$254 million |
| Solana (swapped to SOL/USDC) | 26,250 wETH equivalent | ~$66 million |
| **Total** | **120,000 wETH** | **~$320 million** |

### Root Cause: Missing Account Validation

The specific vulnerability was in a code path affected by a **deprecated Solana function**:

- The Wormhole codebase had been migrated to use `solana_program` v1.9, but the `verify_signatures` function still relied on behavior from the older `solana_program` version
- A fix had been developed (using `get_instruction_relative` with proper sysvar account verification) and was present in the GitHub repository **18 days before the exploit** (committed January 13, 2022)
- However, the fix had **not been deployed to mainnet** — the attacker exploited the window between the fix being committed and deployed [4]

## Wormhole and Jump Crypto Response

### Immediate Actions

| Time | Action |
|------|--------|
| 18:24 UTC, Feb 2 | Exploit executed |
| ~18:30 UTC, Feb 2 | Wormhole network taken offline for maintenance |
| ~19:00 UTC, Feb 2 | Wormhole team confirms exploit on Twitter |
| Feb 2 | $10 million bug bounty publicly offered to attacker via bridge message |
| Feb 3 | Jump Crypto deposits 120,000 ETH into Wormhole Ethereum contract |
| Feb 3 | Wormhole bridge restored to full operation |

### Jump Crypto Bailout

**Jump Crypto** — the cryptocurrency arm of Jump Trading, a major Chicago-based quantitative trading firm — replaced the full **120,000 ETH (~$320 million)** from its own reserves [5]:

- Jump Crypto operated the majority of Wormhole's guardian nodes
- The replacement was completed within approximately **24 hours** of the exploit
- All wETH holders on Solana were made whole — no user suffered losses
- Jump Crypto did not publicly disclose whether it received any consideration for the bailout
- At the time, Jump Trading was reported to have assets of approximately **$7 billion**, making the $320 million replacement approximately 4.5% of total assets

### $10 Million Bounty Offer

Wormhole sent a message to the attacker's Ethereum address offering a **$10 million "white hat" bounty** in exchange for returning all funds and sharing exploit details. The attacker **never responded** to the offer [6].

## Fund Recovery: Court-Ordered Counter-Exploit (February 2023)

### The Oasis.app Operation

In **February 2023**, approximately **$225 million** of the stolen funds was recovered through an unprecedented legal and technical operation [7]:

**Background**: The attacker had deposited a significant portion of the stolen ETH into **MakerDAO** vaults through **Oasis.app** (now Summer.fi), a DeFi front-end for MakerDAO. The attacker had borrowed DAI stablecoins against the ETH collateral.

**Court order**: Attorneys representing Jump Crypto obtained an order from the **UK High Court of Justice** directing Oasis.app's development team to implement a mechanism to recover the funds.

**Technical execution**:
1. Oasis.app's smart contracts used an **upgradeable proxy pattern** (AdminUpgradeabilityProxy)
2. Under the court order, the Oasis team deployed a new implementation contract with a function that could transfer assets from any vault
3. On **February 21, 2023**, the proxy was upgraded and the function was called, extracting approximately **120,695 wstETH and 3,213 rETH** (worth ~$225 million) from the attacker's vault
4. The funds were transferred to a wallet controlled by Jump Crypto's legal representatives

**Controversy**: The counter-exploit raised significant concerns:
- It demonstrated that "upgradeable" DeFi contracts provide a backdoor that can be used by authorized parties (including under court order)
- The DeFi community debated whether court-ordered smart contract modifications undermine the trustless nature of decentralized finance
- Some argued this proved that DeFi protocols with admin keys are not truly decentralized

## Market Impact

The Wormhole exploit had immediate effects on the Solana ecosystem:

- **SOL price**: Dropped approximately **12–13.5%** in the days following the exploit
- **Solana DeFi TVL**: Declined as users reassessed bridge security risks
- **wETH on Solana**: Briefly traded at a discount to native ETH before Jump Crypto's bailout restored confidence
- The exploit reinforced concerns about **cross-chain bridge security**, occurring just months before the Ronin ($625M) and Nomad ($190M) bridge hacks

## Wormhole's Post-Exploit Evolution

### Security Improvements

After the exploit, Wormhole implemented significant security upgrades:
- **Guardian set expanded** from 19 to additional validators
- **Global Accountant** system: An on-chain accounting module that tracks minted wrapped tokens and ensures they never exceed deposited collateral
- **Governor** system: Rate-limiting mechanism that caps the volume of transfers within time windows
- **Multiple audits**: Extensive re-auditing of all bridge contracts

### W Token Launch (April 2024)

In **April 2024**, Wormhole launched the **W token** through one of the largest airdrops in crypto history:
- **1.8 billion W tokens** distributed across Solana and Ethereum
- Market capitalization reached approximately **$3 billion** on launch day
- The airdrop rewarded bridge users and helped re-establish Wormhole as a leading cross-chain protocol

## Market Manipulation Implications

The Wormhole exploit reveals critical security considerations for cross-chain bridge infrastructure:

1. **Signature verification as single point of failure**: The entire $320 million exploit resulted from a single missing validation check in the `verify_signatures` function — a flaw that allowed the attacker to bypass the guardian signature system entirely, demonstrating that bridge security depends on the correctness of every step in the verification chain
2. **Deployment lag as attack window**: The fix for the vulnerability was committed to GitHub 18 days before the exploit but not deployed to mainnet — this gap between code availability and deployment represents a systemic risk in DeFi, where public repositories may expose vulnerabilities before patches are live
3. **Centralized bailout of "decentralized" infrastructure**: Jump Crypto's $320 million replacement demonstrated that Wormhole's practical operation depended on a single well-capitalized entity, raising questions about the decentralization claims of bridge protocols backed by dominant guardians
4. **Court-ordered smart contract modification**: The Oasis.app counter-exploit established legal precedent that upgradeable smart contracts can be modified under court order, revealing that the "immutability" of DeFi is conditional on contract architecture

## Relevance to Market Health Metrics

Wormhole's case demonstrates several indicators in the DN Institute [Market Health Metrics](https://dn.institute/research/market-health/docs/market-health-metrics/) framework:

- **Bridge reserve verification**: Real-time comparison of minted wrapped tokens against actual locked collateral provides the most direct measure of bridge solvency — the Wormhole exploit created 120,000 unbacked wETH, a discrepancy that on-chain monitoring could have detected immediately
- **Code audit recency and deployment status**: The gap between a vulnerability fix being committed (January 13) and the exploit occurring (February 2) demonstrates that audit status alone is insufficient — deployment status of known fixes represents a time-critical security metric
- **Guardian/validator concentration**: Jump Crypto's role as both the primary guardian operator and the sole entity capable of a $320 million bailout represents measurable centralization risk in bridge infrastructure
- **Upgradeability as risk factor**: The Oasis.app counter-exploit demonstrated that proxy-upgradeable contracts contain inherent centralization — the presence of admin upgrade keys in DeFi protocols should be weighted as a risk factor in protocol health assessments

## References

1. Wormhole, "Wormhole Documentation." [wormhole.com](https://wormhole.com/)
2. Samczsun, "Wormhole Unilateral Vulnerability Disclosure," February 2022. [samczsun.com](https://samczsun.com/wormhole-unilateral-vulnerability-disclosure/)
3. Rekt News, "Wormhole — REKT," February 2022. [rekt.news](https://rekt.news/wormhole-rekt/)
4. Kudelski Security, "Wormhole Hack Analysis," February 2022. [research.kudelskisecurity.com](https://research.kudelskisecurity.com/2022/02/03/wormhole-hack-analysis/)
5. CoinDesk, "Jump Crypto Quietly Replaced $320M in Ether After Wormhole Hack," February 2022. [coindesk.com](https://www.coindesk.com/business/2022/02/03/jump-crypto-quietly-replaced-320m-in-ether-after-wormhole-hack/)
6. The Block, "Wormhole Offers $10M Bug Bounty to Bridge Exploiter," February 2022. [theblock.co](https://www.theblock.co/post/133186/wormhole-offers-10-million-bug-bounty-to-its-exploiter)
7. Blockworks, "Wormhole Hacker's Funds Retrieved Via Oasis.app Counter-Exploit," February 2023. [blockworks.co](https://blockworks.co/news/wormhole-hacker-counter-exploited-oasis)
