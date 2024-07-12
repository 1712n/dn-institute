---
date: 2023-03-26
target-entities: Kokomo Finance
entity-types:
  - DeFi
  - Lending Platform
attack-types:
  - Scam
  - Rug Pull
title: "Kokomo Finance Executes $4.5 Million Rug Pull on Optimism"
loss: 4500000
---

## Summary

On 26 March 2023, Kokomo Finance, an open-source and non-custodial lending protocol, conducted an exit scam from their KOKO token deployed on Optimism. Sometime during the incident, Kokomo Finance removed all of its social media accounts including its website. The exit scam led to the loss of approximately $4.5 million in user funds and more than a 95% drop in the token's price.

## Attackers

The exit scam was carried out by the anonymous Kokomo Finance team. The following addresses are associated with this scam:

- Optimism:
  - [0x41be327a34d5d2f0855ff7e4fb3f6f1748b3310f](https://optimistic.etherscan.io/address/0x41be327a34d5d2f0855ff7e4fb3f6f1748b3310f) - Deployer address
  - [0x1e02E6A5b549eeAd726ebCce64a54215196760E2](https://optimistic.etherscan.io/address/0x1e02E6A5b549eeAd726ebCce64a54215196760E2) - cBTC malicious contract

- Atbitrum
  - [0x88340ff2292506d0d93934cbbfea5ed1804cda0d](https://arbiscan.io/address/0x88340ff2292506d0d93934cbbfea5ed1804cda0d)

- Binance Smart Chain
  - [0x8c0ecd7bacced114729f8269b459e0a4d5e95c3b](https://bscscan.com/address/0x8c0ecd7bacced114729f8269b459e0a4d5e95c3b)
  - [0xb74c5e41e748babc32ce33813549e2503cdab762](https://bscscan.com/address/0xb74c5e41e748babc32ce33813549e2503cdab762)

## Losses

Losses amounted to 7010 soWBTC worth $4,500,000.

## Timeline

- **March 26, 2023, 02:02 PM UTC:** Implementation contract was [upgraded](https://optimistic.etherscan.io/tx/0xd751d8b98a1720b72e516fc8f8d47a076a60b08013be101f280cf1b728b6f20b) to the malicious cBTC contract.
- **March 26, 2023, 04:07 PM UTC:** The team began [exchanging](https://optimistic.etherscan.io/tx/0x34d0c08244df664f4520e4b8656c24dd4dd134c095599028c1f07097a7a6beaf) soWBTC for BTC and subsequent distribution of stolen funds to various wallets.
- **August 1, 2023:** Certik published a [detailed analysis](https://www.certik.com/resources/blog/kokomo-finance) of incident.

## Early Indicators

- **Lack of transparency:** A rug pull often involves a lack of transparency or information on the project, such as unclear tokenomics or a lack of information on the team or project roadmap.
- **Unaudited code:** A smart contract that has not been audited increases the risk of vulnerabilities and potential exploits.
- **Unrealistic promises:** Projects that make unrealistic promises of high returns or quick profits without a clear explanation of how these returns will be generated should be approached with caution.
- **Centralized control:** A smart contract that gives excessive control to the owner or a small group of individuals can lead to potential misuse of funds or a rug pull.
