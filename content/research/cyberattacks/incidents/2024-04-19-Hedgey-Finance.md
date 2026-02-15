---
date: 2024-04-19
target-entities: Hedgey Finance
entity-types:
  - DeFi
  - Token Vesting Platform
attack-types:
  - Smart Contract Exploit
  - Flash Loan Attack
title: "Hedgey Finance Exploited for $44.7 Million via Flash Loan Attack"
loss: 44700000
---

## Summary

On April 19, 2024, Hedgey Finance, a token vesting and lockup infrastructure platform, [was exploited across both Ethereum and Arbitrum networks](https://x.com/CyversAlerts/status/1781221966369714227), resulting in a total loss of approximately $44.7 million. The root cause was a [lack of input validation](https://www.halborn.com/blog/post/explained-the-hedgey-finance-hack-april-2024) in the `createLockedCampaign` function of the Token Claim Contract, specifically on the `claimLockup` parameter. The attacker utilized a flash loan of $1.3 million USDC from Balancer to manipulate this parameter and trick the contract into granting unauthorized token approvals. Approximately $2.1 million was drained from Ethereum (in USDC, NOBL, and MASA tokens), while $42.6 million worth of BONUS tokens were stolen from Arbitrum. [Hedgey confirmed the attack](https://twitter.com/hedgeyfinance/status/1781257581488418862) roughly two hours after the initial alert and urged users to cancel active claims to prevent further losses. The platform [sent an on-chain message](https://etherscan.io/idm?addresses=0x5a4bc2bda1f6b9929b6efdcef4728246bec4c635,0xd84f48b7d1aafa7bd5905c95c5d1ffb2625ada46&type=1) to the attacker requesting the return of funds and treating the incident as a potential white hat hack.

## Attackers

The identity of the attacker is unknown. The following addresses were used in the exploit:

**On Ethereum:**

- Exploiter's Address: [0xded2b1a426e1b7d415a40bcad44e98f47181dda2](https://etherscan.io/address/0xded2b1a426e1b7d415a40bcad44e98f47181dda2)
- Attack Contract: [0xc793113f1548b97e37c409f39244ee44241bf2b3](https://etherscan.io/address/0xc793113f1548b97e37c409f39244ee44241bf2b3)
- Exploited Contract: [0xbc452fdc8f851d7c5b72e1fe74dfb63bb793d511](https://etherscan.io/address/0xbc452fdc8f851d7c5b72e1fe74dfb63bb793d511)

**On Arbitrum:**

- Exploiter's Address: [0xc7241e27ee4b8d32b59a10e848b48530047a8c5b](https://arbiscan.io/txs?a=0xc7241e27ee4b8d32b59a10e848b48530047a8c5b)
- Attack Contract: [0xbb52f1723ddf2c84ba2668f4e04712f572cbf780](https://arbiscan.io/txs?a=0xbb52f1723ddf2c84ba2668f4e04712f572cbf780)
- Exploited Contract: [0xbc452fdc8f851d7c5b72e1fe74dfb63bb793d511](https://arbiscan.io/address/0xbc452fdc8f851d7c5b72e1fe74dfb63bb793d511)

Stolen funds were [consolidated and held](https://debank.com/profile/0xC7241E27Ee4B8D32b59a10E848B48530047a8c5b) in the Arbitrum exploiter address.

## Losses

Hedgey Finance suffered a total loss of approximately $44.7 million in assets:

- **Ethereum (~$2.1M):** USDC, [NOBL](https://www.geckoterminal.com/eth/pools/0xc98936de9640d6bfc24f82de1cf0f8cd9f5b388d) (NobleBlocks), and [MASA](https://www.coingecko.com/en/coins/masa) tokens
- **Arbitrum (~$42.6M):** [BONUS](https://www.coingecko.com/en/coins/bonusblock) (BonusBlock) tokens

## Timeline

- **April 19, 2024:** [Cyvers first reported](https://x.com/CyversAlerts/status/1781221966369714227) the detection of suspicious transactions targeting Hedgey Finance contracts.
- **April 19, 2024:** The attacker executed the exploit in two separate transactions on each chain — first creating the fake lockup campaign to obtain malicious approvals, then using those approvals to transfer tokens. The two-step approach was likely designed to prevent being front-run by MEV bots.
- **April 19, 2024:** [Hedgey Finance acknowledged the attack](https://twitter.com/hedgeyfinance/status/1781257581488418862) approximately two hours after the initial alert, informing the community they were investigating the exploit and urging users with active claims to cancel them using the "End Token Claim" button.
- **April 19, 2024:** [NobleBlocks (NOBL) published a detailed security report](https://twitter.com/nobleblocks/status/1781358386690617404) to their community regarding the impact of the exploit on their token.
- **April 19, 2024:** Hedgey Finance [sent an on-chain message](https://etherscan.io/idm?addresses=0x5a4bc2bda1f6b9929b6efdcef4728246bec4c635,0xd84f48b7d1aafa7bd5905c95c5d1ffb2625ada46&type=1) to the attacker requesting a return of funds and treating the incident as a white hat hack.

## Security Failure Causes

**Insufficient Input Validation:** The root cause of the exploit was the [lack of input validation](https://www.halborn.com/blog/post/explained-the-hedgey-finance-hack-april-2024) on the `claimLockup` parameter within the `createLockedCampaign` function. While the function validated most of its parameters, this critical parameter — which specified information such as the locker of a token and was used to index the newly created locking campaign — went unvalidated. This allowed the attacker to craft a malicious call that created a fake lockup campaign, which when canceled, made assets available for withdrawal through unauthorized approvals.

**Flash Loan Exploitation:** The attacker leveraged a $1.3 million USDC flash loan from Balancer to manipulate the `claimLockup` parameter and create unauthorized token approvals. The flash loan provided the initial capital needed to interact with the vulnerable contract function without requiring the attacker to hold significant funds.

**Audit Gap:** Hedgey's Token Lockup and Vesting Plans had been audited by Consensys Diligence in June-July 2023. However, the audit failed to identify the critical input validation vulnerability in the `createLockedCampaign` function, highlighting the limitations of security audits and the importance of ongoing security reviews, especially when new features or markets are added.
