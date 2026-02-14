---
date: 2024-03-26
target-entities: Munchables
entity-types:
  - DeFi
  - GameFi
attack-types:
  - Smart Contract Exploit
  - Insider Threat
title: "Munchables Exploited for $62.5 Million by Rogue Developer on Blast L2"
loss: 62500000
tags:
  - North Korea
  - Insider Threat
  - Blast
  - Upgradeable Proxy
---

## Summary

On March 26, 2024, Munchables, a GameFi project on the Blast L2 network and a [Blast Big Bang award winner](https://rekt.news/munchables-rekt/), was exploited for approximately $62.5 million in ETH by a rogue developer who had been embedded within the team. The attacker exploited a dangerously upgradeable proxy contract by [manipulating storage slots](https://rekt.news/munchables-rekt/) to assign themselves a deposited balance of 1,000,000 ETH before upgrading the contract to a version that appeared legitimate. Once TVL was sufficiently high, the attacker simply withdrew the fabricated balance. [ZachXBT's investigation revealed](https://twitter.com/zachxbt/status/1772843238539325947) that four different developers hired by Munchables were likely the same person — they recommended each other for the job, regularly transferred payments to the same exchange deposit addresses, and funded each other's wallets. The rogue developer was [linked to North Korea](https://www.coindesk.com/tech/2024/03/27/munchables-exploited-for-62m-ether-linked-to-rogue-north-korean-team-member/) by ZachXBT based on GitHub commit activity. In a dramatic turn of events, the developer [agreed to return all private keys](https://twitter.com/_munchables_/status/1772846122236862789) without conditions within hours of the exploit, after being publicly identified by ZachXBT. The funds (~$60.5 million) were [secured in a multisig controlled by Blast core contributors](https://twitter.com/PacmanBlur/status/1772871466935013701).

## Attackers

The attacker was a rogue developer embedded within the Munchables team, suspected to be a North Korean operative operating under multiple identities. [ZachXBT's investigation](https://twitter.com/zachxbt/status/1772843238539325947) linked the developer to North Korea based on GitHub commit patterns and payment flows, though [no official confirmation was made](https://www.coindesk.com/tech/2024/03/27/munchables-exploited-for-62m-ether-linked-to-rogue-north-korean-team-member/). The investigation revealed four GitHub accounts linked to the same individual:

- NelsonMurua913 (account deleted)
- Werewolves0493 (account deleted)
- BrightDragon0719 (account deleted)
- Super1114 (account deleted)

These accounts recommended each other for the job, regularly transferred payments to the same two exchange deposit addresses, and funded each other's wallets.

Attacker's address:

- [0x6e8836f050a315611208a5cd7e228701563d09c5](https://blastscan.io/address/0x6e8836f050a315611208a5cd7e228701563d09c5)

Payment addresses used by the rogue developer:

- [0x4890e32a6A631Ba451b7823dAd39E88614f59C97](https://etherscan.io/address/0x4890e32a6a631ba451b7823dad39e88614f59c97)
- [0x6BE96b68A46879305c905CcAFFF02B2519E78055](https://etherscan.io/address/0x6be96b68a46879305c905ccafff02b2519e78055)
- [0x9976Fe30DAc6063666eEA87133dFad1d5ec27c5E](https://etherscan.io/address/0x9976fe30dac6063666eea87133dfad1d5ec27c5e)

Exchange deposit addresses:

- [0x84e86b461a3063ad255575b30756bdc4d051a04b](https://etherscan.io/address/0x84e86b461a3063ad255575b30756bdc4d051a04b)
- [0xe362130d4718dc9f86c802ca17fe94041f1cfc77](https://etherscan.io/address/0xe362130d4718dc9f86c802ca17fe94041f1cfc77)

## Losses

Munchables lost approximately **$62.5 million** in ETH. Approximately **$60.5 million** was [returned by the attacker](https://twitter.com/PacmanBlur/status/1772871466935013701) after being identified and pressured by ZachXBT.

Funds returned via three transactions:

- [Transaction 1](https://blastscan.io/tx/0x69f271f90204ae993200f54676c922fe5ee3e5020a16ae34f589f52d923857f1)
- [Transaction 2](https://blastscan.io/tx/0x381d57aa2d959ff9580ad61cc6549ae3c026eed9ee5b2ea10f9601a186c49a13)
- [Transaction 3](https://blastscan.io/tx/0x62a148877957cbf1ae89cafa144496d99239ee900a3b90194249e6baaa3ddc2f)

## Timeline

- **March 21, 2024:** The rogue developer [upgraded the Munchables contract](https://blastscan.io/tx/0xea1d9c0d8de4280b538b6fe6dbc3636602075184651dfeb837cb03f8a19ffc4f) to a new implementation, manipulating storage slots to assign themselves a balance of 1,000,000 ETH. The contract was then upgraded again to a version that appeared legitimate, hiding the manipulated storage.
- **March 26, 2024:** The attacker [withdrew the fabricated balance](https://rekt.news/munchables-rekt/), draining approximately $62.5 million in ETH from the protocol.
- **March 26, 2024:** Munchables [reported the compromise on Twitter](https://twitter.com/_munchables_/status/1772739713687752761), stating they were tracking movements and attempting to stop transactions.
- **March 26, 2024:** [Pop Punk raised suspicions](https://twitter.com/PopPunkOnChain/status/1772746208047518025) in the Web3 security community that Munchables may have accidentally hired a North Korean developer who never transferred ownership of the smart contracts.
- **March 26, 2024:** [quit.q00t.eth revealed](https://twitter.com/0xQuit/status/1772764460647846273) that the Munchables contract was a dangerously upgradeable proxy, upgraded from an [unverified implementation address](https://blastscan.io/address/0x910ffc04a3006007a453e5dd325babe1e1fc4511).
- **March 26, 2024:** [ZachXBT publicly identified](https://twitter.com/zachxbt/status/1772843238539325947) the rogue developer, linking four GitHub identities to the same person.
- **March 26, 2024:** 11 minutes after ZachXBT's identification, [Munchables announced](https://twitter.com/_munchables_/status/1772846122236862789) the developer had agreed to share the private keys unconditionally.
- **March 26, 2024:** [Pacman (Blast co-founder) confirmed](https://twitter.com/PacmanBlur/status/1772871466935013701) that the funds had been secured in a multisig by Blast core contributors.
- **March 27, 2024:** [CoinDesk reported](https://www.coindesk.com/tech/2024/03/27/munchables-exploited-for-62m-ether-linked-to-rogue-north-korean-team-member/) that ZachXBT linked the attacker to North Korea's Lazarus Group, though no official confirmation was made.

## Security Failure Causes

- **Insider Threat — Rogue Developer with Contract Ownership:** The primary failure was allowing a developer to retain ownership and upgrade control over the protocol's core smart contracts. The rogue developer used this privileged access to [manipulate storage slots](https://rekt.news/munchables-rekt/) and assign themselves an enormous ETH balance before changing the contract implementation to one that appeared legitimate.

- **Inadequate Hiring Due Diligence:** The Munchables team hired a developer without sufficient background verification. [ZachXBT's investigation revealed](https://twitter.com/zachxbt/status/1772843238539325947) the same individual operated under at least four identities and was employed multiple times by the same team. The CEO of Pixecraft Studios [confirmed having given the same developer](https://rekt.news/munchables-rekt/) a trial hire in 2022, which didn't last a month "due to the dev being sketchy af."

- **Dangerously Upgradeable Proxy Without Safeguards:** The Munchables contract used an upgradeable proxy pattern without timelocks, multisig governance, or other safeguards that would prevent a single developer from unilaterally upgrading the contract. The implementation was [upgraded from an unverified address](https://blastscan.io/address/0x910ffc04a3006007a453e5dd325babe1e1fc4511), which should have been a red flag.

- **Insufficient Audit Coverage for Insider Threats:** While [an audit was completed in March 2024](https://rekt.news/munchables-rekt/) by Entersof, the audit could not have detected a deliberately planted backdoor through storage manipulation by the contract owner. The attack vector — a trusted insider abusing privileged access — falls outside the scope of standard smart contract audits.
