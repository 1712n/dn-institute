---
date: 2018-06-18
custodians: Bancor
categories: Smart Contract Exploit
title: The Bancor hack results in $23.5M tokens loss
---

## Summary

The hack was conducted by taking advantage of a weakness in the smart contract that controlled the Bancor network. Due to a vulnerability, an attacker was able to take over the Bancor contract and steal money from it. In order to stop more losses, the Bancor team was able to react to the attack promptly and halt trading on the site.

## Attackers 

The attackers behind the Bancor hack remain unidentified. In order to execute the Bancor hack, attackers called functions of several smart contracts in the network. The attackers simply initiated a Bancor exchange procedure and authorized transfers of tokens from the compromised contracts to their own accounts. In particular, attackers called a BancorConverter contract function, **withdrawTo**, from the hacked account. 

## Losses

Attackers took control of a wallet that was later used to transfer approximately $23 million in cryptocurrencies, including ether, to a personal account. However, the Bancor team was able to mitigate some damage and recovered around $10 million worth of their own BNT tokens

The losses approximately are:
- 5,000 ether (~ $12.5 million)
- 3,200,000 BNT (~ $10 million)
- 230,000,000 NPXS (~ $1 million)


## Timeline

Apparently, the Bancor Team or some white hackers discovered this issue before anyone could begin draining user wallets and made attempts to rescue user funds by withdrawing them from user wallets.

Subsequently, two automatic front-runners joined in, helping the Bancor Team to withdraw funds from user wallets.

 **2018-06-18**: 
 - Somewhere during the morning the hack occurs.
 - at 03:06 am UTC, the Bancor team began the rescue attempts, withdrawing $409,656 using an exploit a breach by producing batched transactions with temporary smart contracts. An automatic front-runner registered with the email address arden43y@gmail.com joined in almost immediately and successfully front-runned the Bancor team transactions. A total of 16 withdrawal transactions were conducted for a total of $131,889.34. At 03:09am UTC, another front-runner, joined the party and conducted four successful transactions, grabbing a total of $3,340:;
 - The Bancor Team continued to withdraw user funds with both front-runners almost every minute until 06:56 am UTC; 
 

## Security Failure Causes

### The function flaw

The security bug was originated in the contract’s function **safeTransferFrom**:

The function’s flaw is the unauthenticated call to **transferFrom**. This is ERC20’s interface function to enable a certain spender (Bancor’s contract in this context) to transfer funds on behalf of the actual owner of the token (i.e. the user interacting with Bancor’s exchange). Because this function is public, anyone can call this function with a destination address to his choice.

### The architectural flaw

This vulnerability in **safeTransferFrom** could have gone irrelevant, as the success of such a function call is dependent on a preceding transaction where the owner of the tokens approves that the smart contract can transfer a certain amount of tokens on his behalf.
Unfortunately, Bancor Wallet and other external wallets that interact with this contract adopted a common anti-pattern where the requested amount to approve is infinite.

Bancor has acknowledged this issue in their blog post:

"In addition, infinite approval was removed from bancor.network in favor of the exact amount required for conversions."

