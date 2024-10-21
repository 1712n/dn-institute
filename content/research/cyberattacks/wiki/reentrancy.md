---
title: Reentrancy Attacks
bookToc: true
---

## What is Reentrancy?

Reentrancy is a malicious attack that can be used to exploit smart contracts. It occurs when an attacker is able to call back into a function before its previous invocations have completed. This attack exploits the malicious sequence of function calls in smart contracts, enabling an attacker to manipulate the contract's data in unforeseen ways. It's particularly problematic for functions that send Ether or any native token of [EVM-compatible chains](https://blog.thirdweb.com/evm-compatible-blockchains-and-ethereum-virtual-machine/), as it can lead to the theft of funds.

## How do Reentrancy Attacks Work?

Reentrancy attacks exploit the way that certain calls can be made within a contract. A contract's function may call another contract's function, and if the latter has a callback, which would switch an execution flow to the calling contract, it can lead to unexpected behavior. This can cause state variables to be unpredictably modified by the malicious contract, leading to a wide variety of potential problems, including theft of funds or corrupted data.

## Types of Reentrancy Attacks

### **Single-Function Reentrancy**

This type of reentrancy attack occurs when a contract’s function is exploited to call itself recursively before its execution is complete. This is the most common type of reentrancy attack.

### Attack Example

#### The DAO: $60m (June 2016)

- **Vulnerability**: The DAO (Decentralized Autonomous Organization) had a function that allowed users to split from the DAO and create a "Child DAO." This function contained a flaw where the external call to send Ether was made before the balance was updated.
- **Attack**: An attacker exploited this by creating a malicious contract that repeatedly called the vulnerable function, draining Ether each time before the balance was updated. As a result, the attacker was able to steal about 3.6 million ETH, which was worth approximately $60 million at the time, leading to a hard fork in the Ethereum network.

### **Cross-Function Reentrancy**

This attack involves the exploitation of two or more functions within the same contract. An attacker may manipulate the control flow of one function to reenter another function, leading to unexpected changes in the contract's state, like user's balances, token prices, the share of the depositors, etc.

### Attack Example

#### Lendf.me: $25m (April 2020)

- **Vulnerability**: A pair of functions, such as borrow and withdraw, within `MoneyMarket` contract could be called in a specific order, which would allow the attackers to perform malicious actions.
- **Attack**: The attacker exploited the vulnerability by using one function to alter the state of a liquidity pool and then calling another function to falsely borrow and withdraw funds using the changed state. This sequence of actions was performed repeatedly, thus draining MoneyMarket’s liquidity for $25 million.

### **Cross-Contract Reentrancy**

This type of reentrancy occurs between different contracts. A function from one contract triggers a function from another contract, which then calls back a function from the original contract. If not handled properly, this can lead to malicious manipulation of the contract's state.

### Attack Example

#### [Fei Protocol: $80m (April 2022)](https://dn.institute/attacks/posts/2022-04-30-Fei-Protocol/)

- **Vulnerability**: The code of Rari's Fuse Pools did not follow the check-effect-interaction pattern, leading to an exposure that allowed a cross-contract reentrancy attack.
- **Attack**: An attacker exploited this vulnerability by taking a flash loan and then depositing USDC into a vulnerable contract for loans. The attacker was able to borrow ETH and use the vulnerability to make a re-entrant call to exit the market and withdraw his collateral. The attack was repeated until the flash loan was repaid, and the attacker kept the remaining profit.

### **Read-Only Reentrancy**

The classical examples of reentrancy typically reenter in a state-modifying function so that an inconsistent state is used to perform malicious writes on the contract’s storage. Typically, contracts guard themselves with reentrancy locks, protecting their state from such malicious actions. In contrast, read-only reentrancy is a reentrancy scenario where a `view` function is reentered, which in most cases is unguarded as it does not modify the contract’s state. However, if the state is inconsistent, wrong values could be reported. Other protocols, relying on a return value, can be tricked into reading the wrong state as an extremely low or high price of tokens to perform unwanted actions.

### Attack Example

#### EraLend: $3.4m (July 2023)

- **Vulnerability**: LP token burning mechanism contained a read-only reentrancy vulnerability. The reserves were not updated at the correct point, which may have allowed the oracle to use an incorrect reserve value to calculate the price.
- **Attack**: The attacker targeted the USDC pools. By burning and then using a callback before the `update_reserves` function was called, they manipulated the oracle price. Of the $3.4 million lost from EraLend, the attacker profited around $2.66 million.

## Countermeasures

- **Reentrancy Guard**: By using a Reentrancy Guard, developers can ensure that a function cannot be re-entered while it is still executing. This can be implemented by using a [mutex](<https://en.wikipedia.org/wiki/Lock_(computer_science)>) or similar locking mechanism that prevents calling certain functions in an unintended order by utilizing a variable that shows if the function has already been called or not.
- **Update State First**: Updating all state variables before making an external call can prevent reentrancy. If all internal work is done first, a callback won't be able to interfere with the state of the contract.
- **Avoid Low-Level Calls**: By avoiding low-level calls such as `call.value()()`, which expose the contract to reentrancy risks, and instead using higher-level constructs like `transfer`, the risk of reentrancy can be minimized.
- **Check-Effects-Interaction Pattern**: Following this pattern ensures that the contract's state is checked, then effects are applied, and finally, interactions are done with other contracts. This sequence helps prevent reentrancy by enforcing a proper order of operations within a function.
- **Static Analysis Tools**: There are tools available for analyzing smart contracts that can identify potential reentrancy vulnerabilities. Utilizing these tools in the development process can assist in identifying and fixing issues before deployment.
