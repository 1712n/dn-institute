---
date: 2024-05-31
target-entities: DMM Bitcoin
entity-types:
  - Custodian
  - Exchange
attack-types:
  - Wallet Hack
  - Social Engineering
tags:
  - North Korea
  - TraderTraitor
  - Lazarus Group
title: "DMM Bitcoin Suffers $308 Million Hack, Later Attributed to North Korean TraderTraitor Group"
loss: 308000000
---

## Summary

On May 31, 2024, [DMM Bitcoin](https://bitcoin.dmm.com/), a Japanese cryptocurrency exchange operated by DMM Group, suffered a breach resulting in the theft of [4,502.9 BTC worth approximately $308 million](https://www.halborn.com/blog/post/explained-the-dmm-bitcoin-hack-may-2024). The stolen Bitcoin was initially [detected as a large-scale transfer by Whale Alert](https://x.com/whale_alert/status/1796394738402070590) between unknown wallets before DMM Bitcoin confirmed the security incident. On December 24, 2024, the FBI, the Department of Defense Cyber Crime Center (DC3), and Japan's National Police Agency (NPA) jointly [attributed the theft to the North Korean cyber threat group TraderTraitor](https://www.npa.go.jp/bureau/cyber/koho/caution/caution20241224.html), a cluster linked to the Lazarus Group. The attack was executed through a targeted social engineering campaign against an employee of Ginco, a Japanese enterprise wallet software company that managed DMM Bitcoin's wallet system. DMM Bitcoin was unable to recover from the losses and [ceased operations on March 8, 2025](https://bitcoin.dmm.com/news/202405_incident), transferring all customer accounts and assets to SBI VC Trade.

## Attackers

The FBI, DC3, and Japan's NPA [identified the attackers](https://www.npa.go.jp/bureau/cyber/koho/caution/caution20241224.html) as **TraderTraitor**, a North Korean state-sponsored cyber threat group also tracked as a sub-cluster of the Lazarus Group. TraderTraitor is known for targeting cryptocurrency businesses through social engineering. The attackers followed a multi-stage approach:

- **Stage 1 — LinkedIn Recruitment Lure (March 2024):** A TraderTraitor operative posing as a recruiter contacted an employee of Ginco, the Japanese enterprise wallet company that managed DMM Bitcoin's wallet infrastructure. The operative sent a malicious Python script disguised as a pre-employment test, hosted on a GitHub page.
- **Stage 2 — Session Hijacking (May 2024):** The compromised Ginco employee's access was exploited to hijack a legitimate transaction request from DMM Bitcoin, redirecting funds to attacker-controlled wallets.

The following Bitcoin address received the initial stolen funds:

- [1B6rJRfjTWwmkk3sZmb2Ehm6LDCFqFYpge](https://mempool.space/address/1B6rJRfjTWwmkk3sZmb2Ehm6LDCFqFYpge)

The stolen BTC was subsequently distributed across multiple wallets and laundered through Bitcoin CoinJoin mixing services.

## Losses

The total loss amounted to **4,502.9 BTC**, worth approximately **$308 million** at the time of the theft.

- 4,502.9 BTC (~$308,000,000)

DMM Bitcoin secured an equivalent amount of BTC through a ¥55 billion ($367 million) loan facility from DMM Group companies to guarantee customer deposits. Despite this, the exchange [determined that maintaining operations was not sustainable](https://bitcoin.dmm.com/news/202405_incident) and ultimately shut down.

## Timeline

- **March 2024:** A TraderTraitor operative [contacted a Ginco employee via LinkedIn](https://www.npa.go.jp/bureau/cyber/koho/caution/caution20241224.html) with a fake recruitment offer, delivering a malicious Python script hosted on GitHub.
- **May 31, 2024:** [4,502.9 BTC was transferred](https://www.halborn.com/blog/post/explained-the-dmm-bitcoin-hack-may-2024) from DMM Bitcoin's hot wallet to an unknown Bitcoin address. The transfer was initially flagged by blockchain monitoring services as an unusually large movement.
- **May 31, 2024:** DMM Bitcoin [acknowledged the security breach](https://bitcoin.dmm.com/) and suspended withdrawals, spot trading, and new account registrations.
- **June 2024:** DMM Bitcoin secured a ¥55 billion loan from affiliated companies to cover the stolen assets and guarantee full customer reimbursement.
- **July–November 2024:** Stolen BTC was traced being laundered through Bitcoin CoinJoin mixing services and cross-chain bridges.
- **December 2, 2024:** DMM Bitcoin [announced the decision to close](https://bitcoin.dmm.com/) and transfer all customer assets to SBI VC Trade.
- **December 24, 2024:** The FBI, DC3, and Japan's NPA [published a joint attribution](https://www.npa.go.jp/bureau/cyber/koho/caution/caution20241224.html) identifying TraderTraitor as the perpetrators.
- **March 8, 2025:** DMM Bitcoin [officially ceased operations](https://bitcoin.dmm.com/news/202405_incident). All customer accounts and remaining assets were transferred to SBI VC Trade.

## Security Failure Causes

- **Social Engineering via Supply Chain:** The attackers did not directly breach DMM Bitcoin's systems. Instead, they targeted an employee of Ginco, a third-party wallet infrastructure provider, through a LinkedIn-based social engineering attack. This supply chain compromise gave the attackers indirect access to DMM Bitcoin's transaction signing process.
- **Insufficient Third-Party Access Controls:** The compromised Ginco employee's session credentials provided sufficient access to manipulate a legitimate transaction request from DMM Bitcoin, suggesting inadequate segmentation between the wallet provider's operational access and the exchange's transaction authorization workflow.
- **Hot Wallet Concentration Risk:** The theft of 4,502.9 BTC ($308 million) in a single transaction indicates that the full amount was accessible through one hot wallet or signing pathway, without multi-layered withdrawal limits or anomaly detection that could have flagged or blocked a transfer of this size.
