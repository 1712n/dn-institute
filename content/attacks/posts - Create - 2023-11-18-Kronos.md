---
date: 2023-11-20
target-entities: Kronos Research 
entity-types: 
   - Trading Firm
attack-types:
   - Private Key Leak
title: “Kronos Research halts trading amid $25M API key hack investigation”
loss: 26000000
---

## Summary

Kronos Research, a Taiwan-based quantitative trading firm, has indefinitely halted trading services after a hacker stole $25 [million](https://cointelegraph.com/news/kronos-research-halts-trading-25-m-hack-investigation) in crypto assets using compromised API keys. The unauthorized entity made six transactions totaling 12,800 ETH to various wallet addresses. Despite the substantial loss, Kronos Research is in good standing and plans to cover all losses internally. The firm is actively conducting internal investigations to identify the perpetrator. Additionally, Kronos Research is engaging with the hacker directly through an Ethereum translation [message](https://etherscan.io/tx/0xfa5f39e439f057f36faa5874934146d07815b32fa231200ff0096dee7f4bc83f) offering a 10% [white hat bounty.](https://cryptopotato.com/kronos-research-offers-10-bounty-following-26-million-hack/) 

## Attackers

The attacker has yet to be identified and has not communicated with Kronos Research since the hack.

## Losses

Kronos Research lost around 13,007 ETH, valued at $25 million at the time.

## Timeline

   - “November 18, 2023, 23:05 UTC:” Kronos Research published a post on X (formally known as Twitter) that around 19:00 UTC they had been hacked and had [halted](https://twitter.com/ResearchKronos/status/1726013733888041376) all trading while they conduct their investigation. They also stated losses do not appear to be a significant portion of their equity. 
   - “November 18, 2023, 23:11 UTC:” Blockchain researcher ZachXBT identified the Ether outflow connected to [wallet 0x2b0502FDab4e221dcD492c058255D2073d50A3ae ](https://etherscan.io/address/0x2b0502FDab4e221dcD492c058255D2073d50A3ae) via an X (formally known as Twitter) post including the transfer [timeline](https://twitter.com/zachxbt/status/1726015231023796233?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1726016901770367372%7Ctwgr%5E596be3057cdaed30babe6b82a0373ad61de75da5%7Ctwcon%5Es2_&ref_url=https%3A%2F%2Fcrypto.news%2Fkronos-trading-firm-suffers-security-breach-losses-25m%2F) as follows;
      - “November 18, 2023, 1:59 UTC:” Attacker transfers 2,780 ETH [Transaction Details.](https://etherscan.io/tx/0xccbd9a91b3bb69bb990e57bcde5ed7ecebaeea948f85119836482c54785aa152) 
      - “November 18, 2023, 1:59 UTC:” Attacker transfers 2,540  ETH [Transaction Details.](https://etherscan.io/tx/0x500b9882da53e6d8ddff46b378fcd70838feef389b6aad4583b3f7d020de165c)
      - “November 18, 2023, 2:00 UTC:” Attacker transfers 2,540 [Transaction Details.](https://etherscan.io/tx/0x2fe7648952289e3c8d6477f2c6434e573ec424231bbd23ec1351fa6a11030d8e)
      - “November 18, 2023, 2:00 UTC:” Attacker transfers 2,636 [Transaction Details.](https://etherscan.io/tx/0x4f62df8581fb07dc1deef220d73a5a29fdc84f1e3a99c42ada8d4dd6c1ba843c)
      - "November 18, 2023, 2:01 UTC:” Attacker transfers 2,507.51635662 [Transaction Details.](https://etherscan.io/tx/0x3a24b938eb3c446b3dfcb42fb1430ac65020df95a9c9595986ed6cfb37739cb3)
      - “November, 19, 2023, 11:27 UTC:” Kronos Research releases a series of four posts on X letting clients know the hack involved unauthorized [access](https://twitter.com/ResearchKronos/status/1726203102842466650) to its API Keys, resulting in (an updated) loss of approximately $26 million in crypto assets and stating the firm will internally cover all losses, ensuring no impact on partners, and they are focusing on resuming trading operations and providing liquidity to exchanges and token projects.
      - “November 28, 2023, 21:30 UTC:” Kronos Research offers a whitehat [bounty](https://dailycoin.com/kronos-research-issues-ultimatum-to-reclaim-stolen-26m/0) of 10% and promise of no legal ramifications if funds are returned by 8:00 UTC on November 30, 2023.

## Security Failure Causes

The attackers were able to gain access to the stolen funds by unauthorized access of Kronos Research private keys due to the following security failure causes:

   - **Unauthorized Access through API Key Compromise:**
The sucessful attack resulted from the compromise of Kronos Research API keys, allowing unauthorized access to critical systems and resources.
   - **Weak API Key Security Practices:**
Weaknesses in the security practices surrounding Kronos Research's API keys, such as inadequate encryption or lack of proper access controls, provided an entry point for attackers.
   - **Insufficient Access Controls on API Endpoints:**
Inadequate access controls on API endpoints allowed the attackers to gain unauthorized access to the stolen funds.
   - **Lack of API Security Monitoring:**
The absence of effective monitoring on API activities and access attempts contributed to the success of the unauthorized access.
   - **Insufficient User Authentication for API Access:**
Weaknesses in user authentication mechanisms for API access may have allowed unauthorized entities to gain control of the stolen funds.
