---
date: 2021-02-13
categories:
    - 51%
    - Protocol Exploit
title: "Alpha Finance DeFi Hack: $37.5 Million Exploited"
---


## Summary

On February 13, 2021, Alpha Finance, a DeFi project, experienced a hack resulting in a loss of $37.5 million. Later, Iron Bank (IB) unilaterally modified the smart contract configuration, preventing lenders on Alpha Homora (AH) from withdrawing their liquidity due to an unresolved debt. Despite negotiations and proposed solutions, IB maintained the freeze on funds, leading depositors to cease negotiations, receive goodwill funds from AH, and pursue legal action against IB.

## Attackers

The identity of the attackers remains unknown. The attack was performed using the [address](https://twitter.com/josebaredes/status/1360476183373242370) [0x905315602Ed9a854e325F692FF82F58799BEaB57](https://etherscan.io/address/0x905315602ed9a854e325f692ff82f58799beab57).

 ## Losses

The Alpha Finance DeFi hack resulted in [financial losses](https://cryptobriefing.com/alpha-finance-suffers-37-5-million-loss-major-attack/), with $37.5 million extracted from the project. The stolen funds were distributed among various destinations as follows:

  + Iron Bank: 1,000 ETH
  + Alpha Homora: 1,000 ETH
  + Tornado.cash:  320 ETH 
  + Attacker's wallet: 10,925 ETH (worth roughly $20 million)

## Timeline

- **February 13, 2021:** 
In the initial stage, the attacker borrowed [1,000e^(18)](https://www.quadrigainitiative.com/casestudy/alphahomorahack.php) sUSD from HomoraBankv2, utilizing [UNI-WETH LP](https://www.halborn.com/blog/post/explained-the-alpha-homora-defi-hack-feb-2021) as collateral. During repayment, the attacker exploited a [rounding error](https://www.halborn.com/blog/post/explained-the-alpha-homora-defi-hack-feb-2021) in the protocol, paying slightly less than the owed amount. This manipulation resulted in a debt of 19709787742197 and a total borrow share of 1. Utilizing the accumulated debt, the attacker engaged in multiple transactions involving borrowing and lending sUSD between Alpha Homora and Iron Bank (Cream). This process enabled the attacker to amass a substantial hoard of cySUSD, which is a collateralized version of sUSD. Using the hoarded cySUSD, the attacker obtained loans of various assets, including 13.2k WETH, 3.6M USDC, 5.6M USDT, and 4.2M DAI. The USDC, USDT, and DAI were subsequently deposited into Aave to acquire aTokens, which were then added to Curve's a3Crv pool. The extracted Ether was distributed among different destinations, including Iron Bank, Alpha Homora, Tornado.cash, and the attacker's wallet.

- **Post-Hack:** 
In response to the hack, the Alpha Finance team promptly responded to address the security issues exploited by the attacker. They fixed the rounding error in the borrow code and implemented restrictions on certain functions. Additionally, they limited the available options for buying and repayment to four tokens: ETH, DAI, USDC, and USDT. These actions were taken to prevent similar attacks in the future and strengthen the project's overall security.
The team also [collaborated](https://twitter.com/stellaxyz_/status/1360535699368251394?s=20) with authorities and cybersecurity experts to [trace the stolen funds](https://www.quadrigainitiative.com/casestudy/alphahomorahack.php) and prevent the attacker from profiting. They made efforts to freeze the remaining assets held on cryptocurrency exchanges, aiming to safeguard the funds and minimize the impact of the attack.

- **February 20, 2021:**
An agreement is reached between Alpha Homora V2 (Alpha Finance Lab) and CREAM V2 (CREAM) regarding the amount of funds and repayment mechanics. The funds in discussion include 13,245 ETH, 4,263,139 DAI, 4,032,014 USDC, and 5,647,242 USDT, along with the accrued interest. The borrowing interest rate on the funds is halted through an upgrade to the CREAM V2 contract. Alpha Finance Lab will cover the cost of auditing the proposed change. Additionally, $50 million worth of ALPHA tokens will be put in an escrow contract with a 7-day timelock, and they will be released back to Alpha Finance Lab periodically and proportionally as the funds are repaid.

- **March 1, 2023:** 
Iron Bank (IB) unilaterally modified the smart contract configuration, freezing Alpha Homora (AH) lenders' funds. AH proposed solutions, but IB rejected them, leading depositors to seek legal action for fund release.


## Security Failure Causes

- **Loophole in Custom Functionality:** The Alpha Homora v2 contract had a vulnerability that allowed the use of custom functionality without adequate checks, creating an opportunity for the attacker to exploit the system.
- **Rounding Error Exploitation:** The attacker took advantage of a rounding error in the protocol during repayment, resulting in a manipulated debt and borrow share.
- **Insufficient Validation and Access Controls:** The lack of strict validation checks and access controls for custom functionality and critical functions allowed unauthorized manipulation of the protocol.
