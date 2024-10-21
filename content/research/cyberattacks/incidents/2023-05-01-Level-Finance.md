---
date: 2023-05-01
target-entities:
  - Level Finance
entity-types:
  - DeFi
  - Exchange
attack-types:
  - Smart Contract Exploit
title: "Level Finance Hacked for $1.1 Million in LVL Tokens"
loss: 1100000
---

## Summary

On May 1, 2023, Level Finance, a decentralized finance (DeFi) protocol, was hacked for $1.1 million in LVL tokens. The attacker [exploited a vulnerability in the protocol's Referral Controller Contract](https://www.halborn.com/blog/post/explained-the-level-finance-hack-may-2023).

## Attackers

The identity of the attacker is unknown.

BSC:

- [0x70319d1c09e1373fc7b10403c852909e5b20a9d5](https://bscscan.com/address/0x70319d1c09e1373fc7b10403c852909e5b20a9d5)

## Losses

The attacker stole 214,000 LVL tokens and swapped LVL to 3,345 BNB, which were worth approximately $1.1 million at the time of the hack.

## Timeline

- **April 24, 2023, 01:52:59 PM +UTC:** [First failed hack attempt](https://bscscan.com/tx/0x95c5b17707294680c06641f253bf79e831ab47b41f41415cc8b93a9ac590363f)
- **May 1, 2023, 05:50:41 PM +UTC:** [First successful hack attempt](https://bscscan.com/tx/0xe1f257041872c075cbe6a1212827bc346df3def6d01a07914e4006ec43027165)
- **May 1, 2023, 08:54 PM +UTC:** [The Level Finance team announced the hack on Twitter](https://twitter.com/Level__Finance/status/1653140756540825638)
- **May 2, 2023:** The DAO has released a [proposal](https://app.level.finance/dao/proposals/0xb057d0796ec3cd09daf01453076a1ced3b9e49173c50abc5d9bf0bd9d8e0e164) asking for votes on how the community should handle the 214K LVL tokens added to circulation by the attack.

## Security Failure Causes

- **Failed Precondition Checks:** The Level Finance hack was made possible by failed precondition checks. In theory, the protocol is designed to allow a user to claim a referral reward once per epoch. However, the protocol lacked checks to ensure that an epoch is not being reused by a claim.
