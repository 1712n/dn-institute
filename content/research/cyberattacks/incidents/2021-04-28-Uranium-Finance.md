---
date: 2021-04-28
target-entities:
  - Uranium Finance
entity-types:
  - DeFi
  - Exchange
attack-types:
  - Smart Contract Exploit
title: "Uranium Finance Exploit Resulting in a $57.2 Million Loss"
loss: 57200000
---

## Summary

On April 28, 2021, Uranium Finance, a BSC-based decentralized exchange, was exploited due to a calculation error bug in its v2 pair contracts, which had been forked from the Uniswap v2 code. The bug allowed an attacker to swap minimum amount of the input token for 98% of the total balance of the output token, leading to massive losses. Uranium Finance had discovered the potential vulnerability but failed to prevent the attack:

> While doing a review of the various low level risks identified by BSC Gemz audit, the dev team became concerned that a potential critical exploit existed even though it hadn’t been caught before and the code had been running unattacked for the last ~10 days without incident, having accumulated over 80m in TVL.
>
> ~ Uranium Finance's Post Mortem

[Source](https://bscscan.com/tx/0x5a504fe72ef7fc76dfeb4d979e533af4e23fe37e90b5516186d5787893c37991)

## Attackers

The attacker's identity remains unknown. The following addresses were involved in malicious actions:

Attacker Address on BSC and Ethereum:

- [0xc47bdd0a852a88a019385ea3ff57cf8de79f019d](https://bscscan.com/address/0xc47bdd0a852a88a019385ea3ff57cf8de79f019d)
- [0xc47bdd0a852a88a019385ea3ff57cf8de79f019d](https://etherscan.io/address/0xc47bdd0a852a88a019385ea3ff57cf8de79f019d)

Malicious Contract:

- [0x2b528a28451e9853f51616f3b0f6d82af8bea6ae](https://bscscan.com/address/0x2b528a28451e9853f51616f3b0f6d82af8bea6ae).

## Losses

Uranium Finance suffered a loss totaling $57.2 million, broken down as follows:

- 34k WBNB ($18M)
- 17.9M BUSD ($17.9M)
- 1.8k ETH ($4.7M)
- 80 BTC ($4.3M)
- 26.5k DOT ($0.8M)
- 638k ADA ($0.8M)
- 5.7M USDT ($5.7M)
- 112k U92

[Source](https://rekt.news/uranium-rekt/)

## Timeline

- **April 16, 2021, 6:34 AM UTC:** The Uranium team [migrated the contract to v2](https://bscscan.com/tx/0x86bd367b42afebef3eb2f5581b326c1c83f8dcf8acafa11e87087f0ec33c59f0), which introduced the bug that facilitated the exploit.
- **April 28, 2021 3:02 AM UTC:** The attacker interacted with the pair contracts and [drained the reserves](https://bscscan.com/tx/0x5a504fe72ef7fc76dfeb4d979e533af4e23fe37e90b5516186d5787893c37991).
- **April 28, 2021, 3:22 AM UTC:** Uranium Finance [announced the news of the hack](https://twitter.com/UraniumFinance/status/1387245696454041600).
- **April 29, 2021:** Uranium Finance published a [post mortem](https://uraniumfinance.medium.com/exploit-d3a88921531c) of the incident, explaining that the bug had not been recognized as a critical issue during multiple audits, but the team has discovered a possible high severity issue right before an attack.
- **March 6, 2023, 11:02 PM UTC:** The exploiter [mixed 2,253 ETH through TornadoCash](https://etherscan.io/txs?a=0xc47bdd0a852a88a019385ea3ff57cf8de79f019d).

## Security Failure Causes

**Contract Bug:** A simple mathematical error in the pair contracts, introduced during the v2 update, allowed the attacker to drain almost all tokens. The error permitted a disproportionately large output from token swaps.

**Unsuccessful Bug Mitigation:** Although the Uranium team became aware of the potential exploit, their attempted solutions, such as liaising with BSC for assistance or considering a whitehat attack, were not effective.

**Potential Insider Involvement:** Suspicion arises from the sudden removal of the Uranium Contracts repository from Github, as well as the coincidence of the exploit occurring on the day they intended to fix the bug through the v2.1 update.
