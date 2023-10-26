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

From March 14 to April 9, 2016, there were 3 hacks of the Swiss ShiftShape cryptocurrency exchange.
The first theft of funds was committed by an employee of the exchange, who was responsible for security and infrastructure. Then he sold the hacker the source code of ShapeShift core, the IP address of the main server, an SSH key and installed a remote access program on another employee's computer. The hacker entered the main server with the provided SSH key and took the coins, since the main server had SSH access to the coins server. After creating a new infrastructure, the exchange was hacked again, the hacker used remote access to the computer and received new SSH keys.

## Attackers

Behind the attack were an exchange employee, his name has not been disclosed, and a hacker under the pseudonym Rovion

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

- **Insider fraud:** An exchange employee stole a cryptocurrency and left a backdoor in the system.
- **Weak security practices:** The backdoor was not detected in time, which allowed 2 more hacks.
