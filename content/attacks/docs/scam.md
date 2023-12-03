# Cryptocurrency Scam Types and Prevention Measures

With the rising interest in cryptocurrencies, the number of associated scams also escalates. Understanding the different types of scams and how to spot them is essential for investor protection.

## 1. Rug Pull

### Overview

In the context of cryptocurrency, rug pulls happen when creators of a project abscond with investor funds. This can occur in decentralized finance (DeFi) projects, new coin launches, or other crypto ventures.

There are three primary rug pull variants:

- **1.1. Project Abandonment**: This scenario is applied when project owners drain the project's funds and cut off all forms of communication, abandoning the project and investors.
	- *Real World Example*
		- **Ethereum Yield: February 11, 2021 - $1.1m**
			- The project's liquidity was added for two of their tokens - ETHY and ETHYS. However, ETHYS's liquidity was not locked, which led to a draining of investor's funds. After some period of time, their community managers [had published a post in Telegram](https://archive.is/fSGYW) telling that there has been not a word from project owner for a long time. The projects defined as abandoned, but the part of liquidity, amounted to around $392,000 worth of WETH [is still locked](https://etherscan.io/address/0xBe78353416003aa6e2c38E85249FDEe3Ce8c9B1B) and couldn't be 'rugged', 
    
- **1.2. Liquidity Withdrawal**: In the decentralized finance (DeFi) space, liquidity withdrawal constitutes a form of rug pull. Those who initially supplied the liquidity, usually the token deployers, withdraw a significant or all the liquidity from pools, causing the token value to plummet.
	- *Real World Example*
		- **AnubisDAO: October 29, 2021 - $60m**
			- The project claimed to be a fork of OlympusDAO was rugpulled hours before sale round of the Anubis token ends. The liquidity was withdrawn from the Balancer Pool via `exitPool()` function in a [single transaction](https://etherscan.io/tx/0x551890a877c57cf19ddcb312c0a9962029225373daf2815f3720b723bd79b7b0) by [the pool deployer](https://etherscan.io/address/0x872254d530ae8983628cb1eaafc51f78d78c86d9). As a result 13,556.36 ETH was stolen from investors, which was worth roughly $60 million.
    
- **1.3. Massive Token Sale**: A drastic drop in liquidity can also come from massive token sales by the initial creators or large holders. The smart contract might even allow privileged addresses to mint new tokens at will, exacerbating the situation.
	- *Real World Exapmle*
		- **Fintoch: May 22, 2023 - $31m**
			- Fintoch was a "P2P blockchain financial platform that focuses on innovating blockchain financial market" according to their [deleted website](https://archive.ph/9kewL). Also, they claimed to be backed by investment banking firm Morgan Stanley. In fact, it was simple ERC20 token. The token's smart contract also contained liquidity pool functionality, and all user funds were stored in it during fundraising. 100,000 FTH tokens [were minted initially](https://bscscan.com/tx/0x3ef479ba75e07ad04f02b5a5f4df476bbbc83bb5d15fdcd2acd1955a4e87fce6), and the scammer [receive 34,341 FTH](https://bscscan.com/tx/0xee053bf3c429603319d352979e09b207103a08ebf5f42aa0ddd22a9d67f004d6) a minutes before [selling 20,001 FTH and completely draining the pool](https://bscscan.com/tx/0xa5e64161928ee40f6af02a32fc5c1fb9efa05cca6b91d88326279329b71c7ea2) for 31,666,317 USDT.

### Recognition Tips

- **Unrealistic Return Promises**: Offers of high gains over short periods are red flags.
- **Anonymity of Developers**: A lack of verifiable identity for project creators is concerning.
- **Lack of Contract Transparency**: Smart contracts that are not publicly viewable or audited may be risky.
- **Tokenomics Scrutiny**: Evaluating a project's token distribution, minting rights, and liquidity provisions can reveal potential risks.

## 2. Honeypot

### Overview

Honeypots craft the illusion of a legitimate project while in reality being set up to defraud investors. The funds seem accessible at first but are actually locked and cannot be withdrawn by investors.

The Honeypot scam comes in multiple forms, including Exorbitant Commissions and Whitelisting/Blacklisting Tactics.

- **Transfer Prevention Honeypots:** The token's smart contract or liquidity pool may contain prevention functionality. The token transfers may be disabled for regular users, so only the scammer or other privileged addresses may sell tokens.
	- *Real World Example*
		- **Squid Game: November 1, 2021 - $5.7m**
			- The Squid Game cryptocurrency, an unaffiliated project leveraging the name of the popular Netflix series, [presented a whitepaper](https://drive.google.com/file/d/1--4MDZ-2lNmh9KpZ0TfosVHkAPCuxD6Y) with Ponzi-scheme characteristics and required holders to collect marbles through a pay-to-play game to sell tokens, signaling potential fraudulent mechanisms. Despite the project's alarming features, it gained extensive media coverage and saw its token price surge, reaching $2,861, an almost 30-fold increase within just eight days. However, the creators abruptly withdrew $5,723,268 from the project, leading to the liquidity pool's vanishing and the token value plummeting to a fraction of a cent. [Over 4,000 holders were left unable to sell their $SQUID due to a "TRANSFER_FROM_FAILED" error](https://www.reddit.com/r/CryptoCurrency/comments/qj9efi/the_biggest_honeypot_ever/), a consequence of an [unverified liquidity pool's source code](https://bscscan.com/address/0x5b871670d4f1d81591ecf641588a28f5032c9dcd) designed to entrap users' funds. This scam commenced with initial funding [traced back to the AscendEX exchange](https://bscscan.com/tx/0x617ab9cc0c4487c08e4888f5ed5270b2d7dce045f80d50724062d35678d4e912).

- **Exorbitant Commission Honeypots**: The token contract is manipulated to allow setting trade fees at exorbitant rates, sometimes up to 100%, ensuring that selling the tokens is virtually impossible.
	- *Real World Example*
		- **SnowFlake Floki: December 28, 2021 - $70k**
			- SnowFlake Floki's token smart contract contained setSellTax function:
			```solidity
			    function setSellTax(uint256 dev, uint256 marketing, uint256 liquidity, uint256 charity) public onlyOwner {
			        sellTaxes["dev"] = dev;
			        sellTaxes["marketing"] = marketing;
			        sellTaxes["liquidity"] = liquidity;
			        sellTaxes["charity"] = charity;
			    }
			```
			The token owner [called the function to set sell tax of 95% for dev address](https://bscscan.com/tx/0xe8e6680e9ed778c6bc9f01e86986b54fdb8462df43bc628b193cdca46ef678e5) so, the mast majority of the tokens user is trying to sell is sent to dev address. Such way, if the user bought 100 SFF tokens initially, he could sell only 5 of them, and 95 tokens is goes to the dev address as a tax in the code part shown below:
			```solidity:
			function handleTax(address from, address to, uint256 amount) private returns (uint256) {
				...
			    _transfer(address(this), taxWallets["dev"], remainingTokens);
			    ...
			    }
		  ```
			The token owner then drained liquidity and deposited the stolen funds to TornadoCash. 
    
- **Whitelisting/Blacklisting Honeypots**: The deployer of the token contract, or a person with special permissions, can blacklist certain wallets. This prevents the sale of tokens for those accounts, effectively trapping their investment.
	- *Real World Example*
		- **ValentineFloki: February 14, 2022 - $50k**
			- ValentineFloki's token smart contract contained blacklisting function:
			```solidity
			function modifyBlacklist(address[] calldata wallet, bool trueFalse)
			        external
			        onlyWhitelist
			    {
			        for (uint256 i = 0; i < wallet.length; i++) {
			            _isBlacklisted[wallet[i]] = trueFalse;
			        }
			    }
			```
			The token creator [repeatedly called this function to blacklist](https://bscscan.com/tx/0x7cb7095dd5e6ee4917a85f7f2358eefbcbd6d39069e9a54fb2cf132ad9637f36) most of the token holders. Since the transfer function contained requirement to sender or receiver not be blacklisted as shown below, they were unable to sell their tokens.
			```solidity:
		    function _transfer(
		        address sender,
		        address recipient,
		        uint256 amount
		    ) private {
		    ...
		        require(!_isBlacklisted[sender], "!Bot");
		        require(!_isBlacklisted[_msgSender()], "!Bot");
		    ...
		    }
		  ```
			The scammer then [drained the liquidity from the pool](https://bscscan.com/tx/0xf87d78d8498aca6140e5c2a2a15e238ecc3f863305d1aafd1d40d12faf93d88f), and [deposited the funds to TornadoCash](https://bscscan.com/tx/0x7e05397a357d37f290b720b9f03d940ae12698b63e71ee11560208cd00cf6e29).
### Recognition Tips

- **Inability to Withdraw**: Immediate concern should arise if there's no option to withdraw your investment.
- **Contractual Anomalies**: Seek expert advice when encountering complex or questionable clauses in a smart contract.
- **Groundless High Return Promises**: Exceptional profit promises with no credible foundation should be viewed with skepticism.