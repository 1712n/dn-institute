---
date: 2024-05-14
target-entities: Sonne Finance
entity-types:
  - DeFi
  - Lending Protocol
attack-types:
  - Smart Contract Exploit
  - Flash Loan Attack
title: "Sonne Finance Suffers $20 Million Hack"
loss: 20000000
---

## Summary

On May 14, 2024, Sonne Finance [was exploited on the Optimism chain](https://cointelegraph.com/news/sonne-finance-pause-20m-crypto-hack), which led to a loss of nearly $20 million worth of assets including USDC, WETH and VELO. Sonne Finance is a decentralized liquidity protocol that offers Lending, Borrowing and Earning opportunities on Optimism and Base chains. The root cause of the exploit is a precision loss smart contract vulnerability. Sonne Finance's smart contracts are a fork of CompoundV2, and precision loss vulnerability is a [well-known issue](https://www.comp.xyz/t/hundred-finance-exploit-and-compound-v2/4266) with them. The attacker took advantage of the newly deployed VELO market, manipulated its collateral factor, and executed multiple malicious transactions to drain the protocol's pools. 

## Attackers

The identity of the attacker remains unknown. The attacker utilized the following Optimism addresses:

- [0x5d0d99e9886581ff8fcb01f35804317f5ed80bbb](https://optimistic.etherscan.io/address/0x5d0d99e9886581ff8fcb01f35804317f5ed80bbb)
- [0xae4A7cDe7C99fb98B0D5fA414aa40F0300531F43](https://optimistic.etherscan.io/address/0xae4a7cde7c99fb98b0d5fa414aa40f0300531f43)
- [0xB23856525e55dD3AF3Afe13740c2801Efd0ea844](https://optimistic.etherscan.io/address/0xb23856525e55dd3af3afe13740c2801efd0ea844)

## Losses

Sonne Finance suffered a loss of approximately $20 million in various assets. Lost assets breakdown:
- *2,033,723 USDC*
- *162.92 WBTC* worth *10,182,500 USD*
- *2,462.83 WETH* worth *7,265,053 USD*
- *2,352 VELO* worth *312 USD*

## Timeline

- **May 5, 2024, 03:29 AM UTC:** Sonne Finance team [initiated a proposal](https://snapshot.org/#/sonnefi.eth/proposal/0x6f3f62efc77e8c501bf71812d2fdc064710a45618d65736ed886cca38ed16fa3) to add VELO token to their market.
- **May 14, 2024, 09:56 PM UTC:** The attacker [made preparations for the hack](https://optimistic.etherscan.io/tx/0x45c0ccfd3ca1b4a937feebcb0f5a166c409c9e403070808835d41da40732db96) by changing collateral factor in soVELO pool.
- **May 14, 2024, 10:18 PM UTC:** The [first malicious transaction was executed](https://optimistic.etherscan.io/tx/0x9312ae377d7ebdf3c7c3a86f80514878deb5df51aad38b6191d55db53e42b7f0) with over $3 million worth of USDC.e, WETH and VELO being siphoned.
- **May 15, 2024, 00:11 AM UTC:** Sonne Finance team [announced the pause of all markets on Optimism](https://x.com/SonneFinance/status/1790535383005966554), and Base markets are not affected.
- **May 15, 2024, 03:02 AM UTC:** A detailed [post-mortem report was published](https://medium.com/@SonneFinance/post-mortem-sonne-finance-exploit-12f3daa82b06) by the protocol's team.
- **May 15, 2024:** CertiK, a blockchain security firm, [published an in-depth incident analysis report](https://www.certik.com/resources/blog/sonne-finance-incident-analysis).
- **May 16, 2024, 05:45 PM UTC:** Sonne Finance team [sent an on-chain message](https://optimistic.etherscan.io/tx/0x06a7561e4faa5150589f8a25153b97e73339b9e5fa5ad26dc04673283c55894c) to the attacker asking to return stolen funds for 10% bounty.

## Security Failure Causes

**Smart Contract Vulnerability:** The root cause of the exploit was a precision loss issue, a widely known vulnerability in CompoundV2 forks. The attacker manipulated the collateral factors of a lending pool, by depositing underlying tokens into an empty market to inflate the value of deposited collateral.
