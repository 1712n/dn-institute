---
date: 2021-02-13
categories: Cryptocurrency, DeFi Hack
title: Alpha Finance DeFi Hack: $37.5 Million Exploited

---

## Summary

On February 13, 2021, Alpha Finance, a decentralized finance (DeFi) project, experienced a sophisticated hack that resulted in the exploitation of a vulnerability in the Alpha Homora v2 contract. The attacker successfully extracted $37.5 million from the project, highlighting the risks associated with smart contract vulnerabilities and emphasizing the need for robust security measures within the DeFi ecosystem.

## Attackers

The identity of the attackers involved in the Alpha Finance DeFi hack remains unknown. However, it is evident that the attacker had a deep understanding of the Alpha Homora v2 contract and exploited its vulnerabilities to orchestrate the attack.

## Losses

The Alpha Finance DeFi hack resulted in significant financial losses, with $37.5 million extracted from the project. The stolen funds were distributed among various destinations, including Iron Bank, Alpha Homora, Tornado.cash, and the attacker's wallet.

## Timeline

- **February 13, 2021:** 
In the initial stage, the attacker borrowed 1,000e18 sUSD from HomoraBankv2, utilizing UNI-WETH LP as collateral. During repayment, the attacker exploited a rounding error in the protocol, paying slightly less than the owed amount. This manipulation resulted in a debt of 19709787742197 and a total borrow share of 1. Utilizing the accumulated debt, the attacker engaged in multiple transactions involving borrowing and lending sUSD between Alpha Homora and Iron Bank (Cream). This process enabled the attacker to amass a substantial hoard of cySUSD, which is a collateralized version of sUSD. Using the hoarded cySUSD, the attacker obtained loans of various assets, including 13.2k WETH, 3.6M USDC, 5.6M USDT, and 4.2M DAI. The USDC, USDT, and DAI were subsequently deposited into Aave to acquire aTokens, which were then added to Curve's a3Crv pool. The extracted Ether was distributed among different destinations, including Iron Bank, Alpha Homora, Tornado.cash, and the attacker's wallet.

- **Post-Hack:** 
In response to the hack, the Alpha Finance team promptly took action to address the security issues exploited by the attacker. They rectified the rounding error in the borrow code and restricted the usage of custom spells. Furthermore, they limited the buying and repayment options to four tokens, namely ETH, DAI, USDC, and USDT. These measures were implemented to prevent similar attacks in the future and enhance the project's overall security.
The team also collaborated with authorities and cybersecurity experts to trace the stolen funds and prevent the attacker from profiting. Efforts were made to freeze the remaining assets on cryptocurrency exchanges, aiming to safeguard the funds and mitigate the impact of the attack.
- **March 1, 2023:** 
Iron Bank (IB) made a unilateral decision to modify the smart contract configuration, leading to the prevention of lenders on Alpha Homora (AH) from withdrawing their liquidity. This action was taken due to an unresolved debt between AH and IB, which originated from a code exploit attack in 2021. Despite AH's commitment to a repayment plan, IB failed to liquidate collateral as required, resulting in a vulnerability in their protocol. Without AH's knowledge, IB upgraded their code and froze depositors' funds, demanding a resolution.
Over a period of 2.5 months, AH, on behalf of the depositors, engaged in negotiations with IB and proposed multiple solutions to unfreeze the funds. Despite their efforts, IB rejected all proposed solutions and maintained the freeze on the funds. Consequently, depositors unanimously voted to cease negotiations with IB, receive goodwill funds from AH, and initiate legal action against IB to unfreeze their funds.


## Security Failure Causes

The Alpha Finance DeFi hack revealed several security failure causes that allowed the attacker to exploit the vulnerabilities in the Alpha Homora v2 contract:

- **Loophole in Custom Spells:** The Alpha Homora v2 contract allowed the usage of custom spells without strict checks, providing an avenue for the attacker to execute the attack.
- **Rounding Error Exploitation:** The attacker took advantage of a rounding error in the protocol during repayment, resulting in a manipulated debt and borrow share.
- **Insufficient Validation and Access Controls:** The lack of strict validation checks and access controls for custom spells and critical functions allowed unauthorized manipulation of the protocol.


