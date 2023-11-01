---
date: 2016-03-14
target-entities: ShapeShift
entity-types:
  - Custodian
  - Exchange
attack-types:
  - Insider Attack
  - Infrastructure Attack
  - Wallet Hack
title: "ShapeShift Exchange Hacked for $230000"
loss: 230000
---

## Summary

Between March 14 and April 9, 2016, the Swiss-based cryptocurrency exchange, ShapeShift, experienced three security breaches. The initial compromise was an insider threat, where an employee responsible for the platform's security and infrastructure misappropriated funds. Subsequently, this individual provided an external threat actor with critical assets: the source code of ShapeShift's core system, the IP address of the primary server, an SSH private key, and deployed a Remote Access Trojan (RAT) on a colleague's workstation. Utilizing the acquired SSH credentials, the external attacker gained access to the primary server which, due to its permissions, had subsequent access to the server storing the cryptocurrency. Despite efforts to re-establish a secure environment, the exchange faced another intrusion. This time, the threat actor leveraged the previously installed RAT, obtaining new SSH credentials, leading to further unauthorized access.

## Attackers

The security incident at ShapeShift was attributed to an internal exchange employee, whose identity remains undisclosed, in collaboration with an external threat actor operating under the pseudonym "Rovion."

Exchange employee wallet:
- **BTC:** [1LchKFYxkugq3EPMoJJp5cvUyTyPMu1qBR](https://www.blockchain.com/en/explorer/addresses/btc/1LchKFYxkugq3EPMoJJp5cvUyTyPMu1qBR)

Hacker wallets:
- **BTC:** [14Kt9i5MdQCKvjX6HS2hEevVgbPhK13SKD](https://www.blockchain.com/explorer/addresses/btc/14Kt9i5MdQCKvjX6HS2hEevVgbPhK13SKD)
- **ETH:** [0xC26B321d50910f2f990EF92A8Effd8EC38aDE8f5](https://etherscan.io/address/0xC26B321d50910f2f990EF92A8Effd8EC38aDE8f5)
- **LTC:** [LL9jqgXVqxUbWbWVaJocBcF9Vm8uS3NaTd](https://blockchair.com/litecoin/address/LL9jqgXVqxUbWbWVaJocBcF9Vm8uS3NaTd)

## Losses

ShapeShift lost approximately $230000:

- 469 BTC
- 5800 ETH
- 1900 LTC

## Timeline

- **March 14, 2016, 02:13:17 AM +UTC:** [Exchange employee stole 315 bitcoins](https://www.blockchain.com/en/explorer/transactions/btc/0d5f8538d43a5e0ccdd2e26536251b7fd253b62ae743faea1db7fdfd44635423)
- **April 07, 2016, 07:11:25 PM +UTC:** [Hacker makes the first malicious transaction](https://etherscan.io/tx/0x47d9a3ba0734ef38d06c8a32cf5bcd94dc4cee2c30f614f55b04630581f68c82)
- **April 09, 2016, 12:17:57 PM +UTC:** [Hacker commits a second malicious transaction](https://etherscan.io/tx/0x775785159bfc0b1ebc193e9171295f534034310ab1a6df8fe4cdc80232f291e7)
- **April 16, 2016:** [The CEO of the exchange wrote an article about hacking](https://news.bitcoin.com/looting-fox-sabotage-shapeshift)
- **May 10, 2016:** [An interview with the CEO of the exchange about hacking was released](https://www.youtube.com/watch?v=G8QNpyqHr04)

## Security Failure Causes

- **Insider threat:** An exchange employee stole a cryptocurrency and left a backdoor in the system.
- **Weak operational security practices:** The backdoor was not detected in time, which allowed 2 more hacks.
