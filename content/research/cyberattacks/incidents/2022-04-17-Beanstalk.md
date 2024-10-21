---
date: 2022-04-17
target-entities: Beanstalk Farms
entity-types:
  - DeFi
  - Yield Aggregator
attack-types: Flash Loan Attack
title: "Beanstalk Farms Lost $182 Million Due To The Governance Mechanism"
loss: 182000000
---

## Summary

On April 17, 2022, Beanstalk Farms, an Ethereum-based DeFi protocol that enables users to earn yield on their cryptocurrency deposits, fell victim to a flash loan attack. This attack resulted in a staggering loss of $182 million, including around $77 million in assets taken from liquidity pools unrelated to Beanstalk. The attacker managed to profit from the exploit, [absconding with 24,840 ETH](https://medium.com/@nvy_0x/the-beanstalk-bean-exploit-b038f4d324ea), equivalent to roughly $80 million. The remaining [$106 million was returned via a flash loan to Aave](https://medium.com/coinmonks/beanstalk-exploit-a-simplified-post-mortem-analysis-92e6cdb17ace), the lending platform. The attacker leveraged the governance mechanism of the protocol, utilizing a flash loan to acquire voting rights and subsequently transferring the project's funds into their own wallet. To obfuscate their illicit activities, the stolen assets were converted to Ethereum and laundered through Tornado Cash, a privacy-focused tool. In a brazen move, the attacker even [made a donation of $250,000 to the Ukrainian relief fund Ukraine Crypto Donation](https://www.certik.com/resources/blog/6HaLMGIL5sI2fpfEZc0nzS-revisiting-beanstalk-farms-exploit), showcasing their audacious handling of the stolen funds. As a consequence of this attack, the value of the BEAN stablecoin plummeted by approximately 88%, reaching a meager $0.12 per token.

## Attackers

The identities of the attackers involved in the Beanstalk Farms attack remain unknown. However, their address on the Ethereum blockchain is [0x1c5dCdd006EA78a7E4783f9e6021C32935a10fb4](https://etherscan.io/address/0x1c5dcdd006ea78a7e4783f9e6021c32935a10fb4). This specific address has been labeled as the "Beanstalk Flashloan Exploiter," indicating their involvement in the exploit.

## Losses

Breakdown of the lost $182 million:

- [36 million BEAN](https://twitter.com/peckshield/status/1515680335769456640) ($36 million).
- $33 million in ETH and $32m in BEAN from ETH-BEAN UNI v2 LP tokens ($65 million).
- [79.2 million BEAN3CRV-f Curve LP tokens](https://medium.com/coinmonks/beanstalk-exploit-a-simplified-post-mortem-analysis-92e6cdb17ace) ($79.2 million).
- [1.6 million BEAN-LUSD Curve LP tokens](https://medium.com/coinmonks/beanstalk-exploit-a-simplified-post-mortem-analysis-92e6cdb17ace) ($1.6 million).

## Timeline:

- **April 16, 2022, 08:38 AM:** The attacker deposited BEAN tokens into Beanstalk to create a malicious proposal called "InitBip18." This proposal was utilized to transfer assets to the attacker and took 24 hours to process.
- **April 17, 2022, 12:24 PM:** The exploiter initiated the attack to execute BIP18.
- **April 17, 2022, 3:24 PM:** A total of 24,849.1 ETH (equivalent to $76,424,649.505) [was transferred to Tornado cash](https://www.certik.com/resources/blog/6HaLMGIL5sI2fpfEZc0nzS-revisiting-beanstalk-farms-exploit), with a possibility that 9 ETH belonged to the attacker.
- **April 17, 2022, 6:41 PM:** The attack was detected by PeckShield, a blockchain analytics company. They promptly shared a tweet exposing the malicious transaction.
- **April 17, 2022, 8:36 PM:** Beanstalk Farms confirmed the attack on Twitter. The Beanstalk team took immediate action by temporarily disabling protocol governance and pausing Beanstalk's operations.
- **April 19, 2022, 2:45 AM:** Beanstalk offered a "whitehat bounty" of 10% of the stolen amount to the hacker if they returned 90% of the funds to Beanstalk Farms' wallet.
- **August 6, 2022:** On its one-year anniversary, Beanstalk [resumed its protocol operations](https://bean.money/blog/beanstalk-one-year-anniversary) and relaunched on the Ethereum mainnet.

## Security Failure Causes

The hack occurred due to a security flaw in the governance design of the protocol. [The attacker leveraged a flash loan acquired through Aave to borrow nearly $1 billion](https://etherscan.io/tx/0xcd314668aaa9bbfebaf1a0bd2b6553d01dd58899c508d4729fa7311dc5d33ad7) in cryptocurrency assets, granting them a 67% voting stake in Beanstalk. Exploiting this majority control, they authorized the execution of code that facilitated the transfer of assets to their personal wallet. This attack exploited the emergencyCommit() function, which enabled the immediate implementation of a proposal with a 2/3 majority vote, bypassing the protocol's protective measures.
