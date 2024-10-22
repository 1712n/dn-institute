---
title: Lockout Scams
bookToc: true
---

# What is Lockout?

Lockouts are scams pretending to be genuine investment opportunities. They trick investors into thinking they can easily withdraw their money, but in reality, the funds are locked and can't be taken out.

These scams can take various forms, such as Transfer Prevention, High Fees, and Whitelisting/Blacklisting.

# Types of Lockout

- **Transfer Prevention Lockouts:** The token's smart contract or liquidity pool may contain prevention functionality. The token transfers may be disabled for regular users, so only the scammer or other privileged addresses may sell tokens.
	- *Real World Example*
		- **Squid Game: November 1, 2021 - $5.7m**
			- The Squid Game cryptocurrency, an unaffiliated project leveraging the name of the popular Netflix series, [presented a whitepaper](https://drive.google.com/file/d/1--4MDZ-2lNmh9KpZ0TfosVHkAPCuxD6Y) with Ponzi-scheme characteristics and required holders to collect marbles through a pay-to-play game to sell tokens, signaling potential fraudulent mechanisms. Despite the project's alarming features, it gained extensive media coverage and saw its token price surge, reaching $2,861, an almost 30-fold increase within just eight days. However, the creators abruptly withdrew $5,723,268 from the project, leading to the liquidity pool's vanishing and the token value plummeting to a fraction of a cent. [Over 4,000 holders were left unable to sell their $SQUID due to a "TRANSFER_FROM_FAILED" error](https://www.reddit.com/r/CryptoCurrency/comments/qj9efi/the_biggest_honeypot_ever/), a consequence of an [unverified liquidity pool's source code](https://bscscan.com/address/0x5b871670d4f1d81591ecf641588a28f5032c9dcd) designed to entrap users' funds. This scam commenced with initial funding [traced back to the AscendEX exchange](https://bscscan.com/tx/0x617ab9cc0c4487c08e4888f5ed5270b2d7dce045f80d50724062d35678d4e912).
- **Exorbitant Commission Lockouts**: The token contract is manipulated to allow setting trade fees at exorbitant rates, sometimes up to 100%, ensuring that selling the tokens is virtually impossible.
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
- **Whitelisting/Blacklisting Lockouts**: The deployer of the token contract, or a person with special permissions, can blacklist certain wallets. This prevents the sale of tokens for those accounts, effectively trapping their investment.
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
			The token creator [repeatedly called this function to blacklist](https://bscscan.com/tx/0x7cb7095dd5e6ee4917a85f7f2358eefbcbd6d39069e9a54fb2cf132ad9637f36) most of the token holders. Since the transfer function contained the requirement to sender or receiver not be blacklisted as shown below, they were unable to sell their tokens.
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

# Indicators

- **Inability to Withdraw**: Be wary if you find you're unable to take your money out.
- **Contract Issues**: Get advice if the smart contract seems too complicated or suspicious.
- **Unrealistic Profits**: Be skeptical of promises for high returns with no real basis.
