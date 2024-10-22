---
title: Flash Loan Attacks
bookToc: true
---

## What are Flash Loans?

Flash loans are an innovative financial instrument in the decentralized finance (DeFi) sector. Flash loans exist on protocols like Aave, dYdX, and others. They enable users to borrow funds without collateral for a very brief period (within one transaction). The primary condition is that the borrowed funds, along with any applicable fees, must be repaid by the end of the transaction. If the repayment fails, the whole transaction reverts, meaning nothing changes from before the transaction began.

## How do Flash Loan Attacks Work?

A flash loan attack typically involves exploiting some weakness or loophole in a smart contract or protocol. Here's a general overview of how a flash loan attack might be carried out:

1. **Initiate a Flash Loan**: The attacker takes out a flash loan, borrowing a large amount of cryptocurrency.
2. **Manipulate Market Prices**: The attacker uses these borrowed funds to manipulate the price of an asset on a decentralized exchange (DEX). This could involve buying up large quantities of an asset to artificially raise its price.
3. **Exploit Vulnerable Protocols**: With the manipulated prices, the attacker interacts with other DeFi protocols that rely on the altered price feed. They could exploit arbitrage opportunities, abuse token exchange functionalities, or manipulate collateralized loans.
4. **Repay the Flash Loan**: Finally, the attacker repays the flash loan, along with any fees, and keeps the profits made from exploiting the vulnerable protocols.

## Attack Examples

### [Euler Finance: $197m (March 2023)](https://dn.institute/attacks/posts/2023-03-13-Euler-Finance/)

- **Vulnerability**: A flaw in the conversion of borrowed assets to collateralized assets.
- **Attack**: The attacker borrowed $30 million and exploited the vulnerability to borrow 10 times the original amount, causing a loss of around $197 million.

### [Beanstalk Farms: $182m (April 2022)](https://dn.institute/attacks/posts/2022-04-17-Beanstalk/)

- **Vulnerability**: A security flaw in the governance design of the protocol, specifically in the emergencyCommit() function.
- **Attack**: The attacker utilized a flash loan to borrow nearly $1 billion in cryptocurrency assets, which allowed them to gain a 67% voting stake in Beanstalk. By exploiting this majority control, they authorized the execution of malicious code that transferred assets to their wallet.

## Countermeasures

- **Reentrancy Guards and Access Control Mechanisms**: Prevent unexpected contract calls by implementing reentrancy guards. Utilize proper access control mechanisms, such as OpenZeppelin's Ownable, to restrict critical functions. Employ well-tested libraries and frameworks for contract development to ensure a robust design.
- **External Smart Contracts Validation**: Since flash loan attacks often originate from external smart contracts, it's prudent to validate the addresses allowed to utilize flash loan functionalities. Ensure that external contract calls are authentic and secure, limiting interactions exclusively to trusted contracts.
- **Contract Auditing and Testing**: Regular, in-depth security audits of smart contracts can help identify vulnerabilities before they are exploited. Employing thorough third-party smart contract auditing and validation is always a valuable security measure. Conduct comprehensive testing to identify potential vulnerabilities and collaborate with reputable auditing firms to review your contracts.
- **Oracle Redundancy and TWAP Mechanisms**: To obtain the most precise and secure price information, consider connecting multiple oracles, accounting for potential attacks on oracles. Implement time-weighted average price (TWAP) mechanisms to minimize risks tied to price manipulation.
