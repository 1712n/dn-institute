---
date: 2022-07-28
target-entities: Nirvana Finance
entity-types:
  - DeFi
  - Yield Aggregator
attack-types:
  - Smart Contract Exploit
  - Flash Loan Attack
title: "Nirvana Finance Suffers $3.5 Million Flash Loan Attack"
loss: 3500000
---

## Summary

On July 28, 2022, Nirvana Finance suffered a $3.5 million loss due to a flash loan attack perpetrated by Shakeeb Ahmed, a senior security engineer at an international technology company. Leveraging a $10 million flash loan from Solend, Ahmed exploited a smart contract vulnerability to manipulate the $ANA token's price from approximately $8 to $24. He exploited this vulnerability to purchase tokens at an undervalued price, subsequently exchanging the inflated tokens for $USDT from Nirvana's treasury. The stolen funds were then moved to an Ethereum address through the Wormhole bridge. Following the event, Ahmed was apprehended and pled guilty to computer fraud, agreeing to forfeit over $12.3 million in assets, including the proceeds from this attack.

## Attackers

The hacker was identified as Shakeeb Ahmed, a former security engineer for an international tech company.

Hacker Ethereum Wallet:
- [0xB9AE2624Ab08661F010185d72Dd506E199E67C09](https://etherscan.io/address/0xB9AE2624Ab08661F010185d72Dd506E199E67C09)

## Losses

Nirvana Finance lost approximately $3,500,000 in total.

## Timeline

- **July 28, 2022, 05:11 AM UTC:** The [first malicious](https://solscan.io/tx/LyUnvdY9KBQiVRFqmSzGUfCuPGqYX1xNHCWLWxWZ4MvgLcNis2Kui6T25Ayai5UzpTAFkSRSgriKb3pM8tAoeR5) transaction occurred.
- **July 28, 2022, 05:19 AM UTC:** [Bridged](https://etherscan.io/tx/0xb5a89c01da58ec7ec8a4b0d0361d8f1719966d4deceaa01efc1362601a76339c) of stolen funds through Wormhole.
- **July 28, 2022, 01:17 PM UTC:** Nirvana finance [reported](https://twitter.com/nirvana_fi/status/1552629332023152641) about the hack.
- **July 28, 2022, 10:03 PM UTC:** Nirvana finance [offered](https://twitter.com/nirvana_fi/status/1552761630127177730) the hacker to return the funds.
- **August 4, 2022:** Nirvana finance published exploit [Post mortem](https://medium.com/nirvanafinance/technical-post-mortem-d738935aeec).
- **December 14, 2023** The hacker was [identified](https://www.justice.gov/usao-sdny/pr/former-security-engineer-international-technology-company-pleads-guilty-hacking-two) and pleaded guilty.

## Security Failure Causes

- **Smart Contract Vulnerability:** The exploit was implemented through the use of term loans to manipulate prices, exploiting a smart contract vulnerability that allowed the hacker to purchase tokens at an undervalued price
