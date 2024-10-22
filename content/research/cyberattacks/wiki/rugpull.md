---
title: Rug Pull Scam
bookToc: true
---

# What is Rug Pull?

A rug pull refers to a fraudulent scheme in which a cryptocurrency developer promotes a project with the intention of luring investors and then abruptly ceases operations or vanishes, thereby absconding with the investors' assets. The term "rug pull" is derived from the expression "to pull the rug out from under someone," leaving the victim disoriented and in disarray.

To allow users to buy a desired asset, the initial token owners should add liquidity into a Decentralized Exchange (DEX), creating the liquidity pool. The token owners receive newly minted liquidity pool tokens (LP tokens), which grants them access to withdraw their liquidity back at anytime. In trusted projects, LP tokens is locked in dedicated smart contract for a long period of time, which guarantees safety of user funds.

The occurrence of rug pulls has risen alongside the growing popularity of decentralized finance (DeFi). According to a [scam database](https://www.comparitech.com/crypto/cryptocurrency-scams/), there have been at least 765 documented cases of rug pulls and exit scams, resulting in a total stolen amount exceeding $26 billion.

# Types of Rug Pull

Rug pulls can be categorized based on the methods used to misappropriate user funds:

- **Liquidity Withdrawal**: Liquidity Withdrawal constitutes a form of rug pull, where the owner of the project directly removes whole liquidity from the liquidity pool via LP tokens. This leads to the asset value to plummet.
	- *Real World Example*
		- **AnubisDAO: October 29, 2021 - $60m**
			- The project claimed to be a fork of OlympusDAO was rug pulled hours before sale round of the Anubis token ends. The liquidity was withdrawn from the Balancer Pool via `exitPool()` function in a [single transaction](https://etherscan.io/tx/0x551890a877c57cf19ddcb312c0a9962029225373daf2815f3720b723bd79b7b0) by [the pool deployer](https://etherscan.io/address/0x872254d530ae8983628cb1eaafc51f78d78c86d9). As a result 13,556.36 ETH was stolen from investors, which was worth roughly $60 million.
- **Massive Token Sale**: A drastic drop in value can also come from massive token sales by the initial creators or large holders. The smart contract might even allow privileged addresses to mint new tokens at will, exacerbating the situation. In this case, LP tokens either locked or not accessible by the owners. However, privileged functions may allow to mint new tokens or initially 'hiding' some huge amount of tokens, and not adding them as initial liquidity. By selling a massive token amount, the scammer drains valuable asset from the pool, usually stablecoins, and leaves the pool with a valueless token, which loses its initial price by almost 100%.
	- *Real World Example*
		- **Fintoch: May 22, 2023 - $31m**
			- Fintoch was a Peer-to-Peer financial platform that focuses on innovating blockchain financial market, according to Fintoch's [deleted website](https://archive.ph/9kewL). Also, they claimed to be backed by investment banking firm Morgan Stanley. In fact, it was a simple ERC20 token. The token's smart contract also contained liquidity pool functionality, and all user funds were stored in it during fundraising. 100,000 FTH tokens [were minted initially](https://bscscan.com/tx/0x3ef479ba75e07ad04f02b5a5f4df476bbbc83bb5d15fdcd2acd1955a4e87fce6), and the scammer [had received 34,341 FTH](https://bscscan.com/tx/0xee053bf3c429603319d352979e09b207103a08ebf5f42aa0ddd22a9d67f004d6) a minute before [selling 20,001 FTH and completely draining the pool](https://bscscan.com/tx/0xa5e64161928ee40f6af02a32fc5c1fb9efa05cca6b91d88326279329b71c7ea2) for 31,666,317 USDT.

# Indicators

- **Unrealistic Return Promises**: Offers of high gains over short periods are red flags.
- **Anonymity of Developers**: A lack of verifiable identity for project creators is concerning.
- **Lack of Contract Transparency**: Unverified smart contracts that are neither publicly viewable nor audited by trusted companies may be risky.
- **Questionable Tokenomics**: Evaluating a project's token distribution, minting rights, and liquidity provisions can reveal potential risks.
