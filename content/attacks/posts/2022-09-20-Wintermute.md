---
date: 2022-09-20
target-entities: Wintermute
entity-types:
  - Exchange
  - Custodian
attack-types:
  - Wallet Hack
  - Brute Force
title: "Wintermute Incurs $160 Million Loss from Brute Force Private Key Compromise Linked to Profanity's Vulnerability"
loss: 160000000
---

## Summary

On September 20, 2022, Wintermute, a London-based algorithmic market maker offering liquidity across Centralized Finance (CeFi) and Decentralized Finance (DeFi) exchanges and over-the-counter (OTC) deals, was the victim of a security breach. The exploit resulted in a loss of approximately $160 million, impacting 90 different assets including stable coins, Bitcoin, Ether, and various altcoins. The attack was executed through a brute force private key compromise [Source](https://www.halborn.com/blog/post/explained-the-profanity-address-generator-hack-september-2022). The suspected vulnerability originated from Profanity, a service Wintermute used for generating vanity addresses, despite efforts to blacklist their Profanity-associated accounts after the vulnerability became known.

## Attackers

The identity of the attackers remains unknown. As of June 22, 2023, the Ethereum address linked to the attacker and currently holding all stolen funds is:

- [0xe74b28c2eAe8679e3cCc3a94d5d0dE83CCB84705](https://etherscan.io/address/0xe74b28c2eAe8679e3cCc3a94d5d0dE83CCB84705).

A smart contract implicated in the attack:

- [0x0248f752802b2cfb4373cc0c3bc3964429385c26](https://etherscan.io/address/0x0248f752802b2cfb4373cc0c3bc3964429385c26)

## Losses

The total losses amounted to roughly $160 million. This consisted of around $120 million in stable coins (USDC and USDT), $20 million in Bitcoin and Ether, and another $20 million spread across various altcoins.

## Timeline

- **January 17, 2022:** Profanity's vulnerability is discovered by 1inch Network Team, and proper [issue was created](https://github.com/johguse/profanity/issues/61) in GitHub.
- **September 15, 2022 6:00 AM UTC:** 1inch Network [drew attention to the issue](https://twitter.com/1inch/status/1570291260002373633) in their blog.
- **September 15, 2022 8:42 PM UTC:** [First malicious transaction](https://etherscan.io/tx/0xdf5d8d087813b2c0efed72cf3cee5b2d9beb16fca87ecfa7a78740260950fee8) of [$3.3 Million Profanity hack](https://insidebitcoins.com/news/hackers-drain-3-3m-from-profanity-wallets-despite-1inch-warning) was performed
- **September 20, 2022 5:11 AM UTC:** [Malicious transaction](https://etherscan.io/tx/0xedd31e2a949b7957a786d44b071dbe1bc5abd5c57e269edb9ec2bf1af30e9ec4) affecting Wintermute's wallets was performed.
- **September 20, 2022 8:03 AM UTC:** Wintermute's CEO, Evgeny Gaevoy, promptly [announces the theft](https://twitter.com/EvgenyGaevoy/status/1572134271011225601).

## Security Failure Causes

**Profanity's Vulnerability:** An inherent weakness in Profanity's code allowed the attacker to generate all potential keys for a vanity address by bruteforcing the private keys, scan associated accounts, and then steal the funds.

> More details on the hackers process, since the tool’s security bug enabled cracking private keys of addresses, specifically someone could brute-force private keys of every 7-character vanity address using roughly a thousand GPUs for 50 days.
>
> -- MetaSchool
> [Source](https://metaschool.so/articles/wintermute-hack-profanity/#:~:text=In%20June%202022%2C%20Wintermute%20also%20disclosed%20that%20it,and%20steal%20%24160%20million%20from%20Wintermute%E2%80%99s%20DeFi%20wallets.)

**Human Error:** Despite Wintermute's efforts to blacklist their Profanity accounts upon learning of the vulnerability, a human error resulted in one account not being blacklisted, thus remaining exposed and likely leading to the significant theft. [Source](https://www.benzinga.com/markets/cryptocurrency/22/09/28943343/human-error-caused-160m-hack-wintermute-ceo)
