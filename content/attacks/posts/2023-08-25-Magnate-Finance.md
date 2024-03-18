---
date: 2023-08-25
target-entities: Magnate Finance
entity-types:
  - DeFi
  - Lending Platform 
attack-types:
  - Scam
  - Rug Pull 
title: "Magnate Finance Executes $5.26 Million Rug Pull on Base"
loss: 5268000
---

## Summary

On August 25, Magnate Finance, a lending project on the Ethereum Layer 2 network Base, executed an exit scam, leading to losses of $5,268,000. This scam involved modifying the price oracle address to manipulate prices directly and then utilizing cDAI to borrow other tokens. This incident is linked to the deployer's previous scams, including Solfire and Kokomo Finance. Following the scam, the project deleted its website and social media accounts.
## Attackers

The anonymous Magnate Finance team, which is also associated with the [Kokomo Finance and Solfire scam](https://twitter.com/zachxbt/status/1694914871165345997?t=Cb9W5zUPYIvAsQcpk0rfog&s=19).

The following [addresses](https://twitter.com/PeckShieldAlert/status/1694986782386073922/photo/1) are associated with this attack:

- Base:
  - [0x4bdac0b6eeda6211f43178899cb73670b1952c40](https://basescan.org/address/0x4bdac0b6eeda6211f43178899cb73670b1952c40) - Deployer address
  - [0x6a8fbf751c92a8c922428c0ffc5a89e709f7e505](https://basescan.org/address/0x6a8fbf751c92a8c922428c0ffc5a89e709f7e505) - Contract address
  - [0xa146dffe1c304a8a3de74c460ffe8dc73e5ce6e1](https://basescan.org/address/0xa146dffe1c304a8a3de74c460ffe8dc73e5ce6e1)
  - [0x0664faf5afecde5958d8b32258e012c3788006a3](https://basescan.org/address/0x0664faf5afecde5958d8b32258e012c3788006a3)

- Binance Smart Chain:
  - [0x2f3801ac648413c93009b2e7bd9e7ebf5844d0cb](https://bscscan.com/address/0x2f3801ac648413c93009b2e7bd9e7ebf5844d0cb)
  
- Arbitrum:
  - [0x7b53ec7e129acf224d58d107c96ef6fd9f91fa33](https://arbiscan.io/address/0x7b53ec7e129acf224d58d107c96ef6fd9f91fa33)
  - [0x06d3930f1b34d728bccbd4dffc1c90673b41dbe8](https://arbiscan.io/address/0x06d3930f1b34d728bccbd4dffc1c90673b41dbe8)
  
- Ethereum:
  - [0x4f2b229082eda4790e2331b80038ea8c5cc0e2b3](https://etherscan.io/address/0x4f2b229082eda4790e2331b80038ea8c5cc0e2b3)

- Optimism:
  - [0xd85ac6af8cc313a30fdedf41501d00a213457820](https://optimistic.etherscan.io/address/0xd85ac6af8cc313a30fdedf41501d00a213457820) 

## Losses

Loss amounted to $5,268,000:
- 2,000,000 USDBC
- 946 ETH ($1,560,000)
- 1,300,00 DAI
- 247 WETH ($408,000)

## Timeline

- **August 25, 2023, 04:03 AM UTC:** The [first malicious](https://basescan.org/tx/0x39555e75d76b294248a434fdfe9640e0cfe3f22bd7fceb675fd4ef4b5e02f719) transaction occurred.

## Early Indicators

- **Lack of transparency:** A rug pull often involves a lack of transparency or information on the project, such as unclear tokenomics or a lack of information on the team or project roadmap.
- **Unaudited code:** A smart contract that has not been audited increases the risk of vulnerabilities and potential exploits.
