---
title: "🌰 Parity Wallet — Library Self-Destruct and $150M Frozen Ether"
date: 2026-05-05
entities:
  - Parity Technologies
  - Ethereum
  - Polkadot
  - Web3 Foundation
---

## Summary

1. **On November 6, 2017, a user accidentally triggered a vulnerability in Parity's multi-signature wallet library contract**, causing it to self-destruct and permanently freezing approximately 513,774 ETH (valued at roughly $150 million at the time) across 587 wallets that depended on the library. The frozen ETH has never been recovered.
2. **The root cause was a combination of two design flaws**: the library contract was left uninitialized after deployment (meaning anyone could call its initialization function and claim ownership), and the library contract included a `kill` function that the owner could use to execute `selfdestruct`. When a user initialized the unowned library and then called `kill`, the shared library code was destroyed, rendering all dependent wallets permanently unable to execute any transactions.
3. **This was the second major Parity wallet vulnerability in 2017**. In July 2017, a different vulnerability in an earlier version of the Parity multi-sig wallet allowed an attacker to steal approximately 150,000 ETH (~$30 million). The November incident affected the patched version that was deployed in response to the July hack.
4. **The largest affected party was the Web3 Foundation**, which had approximately 306,276 ETH (roughly $98 million at the time) frozen in a Parity multi-sig wallet. These were proceeds from the Polkadot token sale that had concluded just weeks earlier in October 2017.
5. **Multiple Ethereum Improvement Proposals (EIPs) were submitted** to recover the frozen funds through protocol-level intervention, but none gained sufficient community consensus. The proposals were controversial because they would have set a precedent for modifying Ethereum's state to reverse the consequences of smart contract bugs — similar to the debate surrounding the 2016 DAO hack and subsequent hard fork.

## Background

### Parity Technologies and Multi-Sig Wallets

Parity Technologies, founded by Ethereum co-founder Gavin Wood, developed the Parity Ethereum client and a suite of smart contract tools. Among these was the Parity multi-signature wallet — a smart contract that required multiple private key signatures to authorize transactions, providing enhanced security for organizations and individuals holding large amounts of ETH.

Multi-signature wallets were (and remain) a standard security practice for cryptocurrency treasury management. By requiring, for example, 3-of-5 key holders to approve a transaction, multi-sig wallets protect against single-key compromise.

### Delegatecall Library Pattern

To save gas costs on deployment, the Parity multi-sig wallet used a common Solidity design pattern:

- **Library contract**: A single deployed contract containing the wallet's business logic (initialization, transaction execution, ownership management, etc.)
- **Wallet contracts**: Lightweight proxy contracts that stored each wallet's state (owner addresses, required signatures, ETH balance) but delegated all function calls to the shared library using Solidity's `delegatecall` mechanism
- **`delegatecall`**: A low-level EVM instruction that executes the code of another contract in the context of the calling contract. The library's code runs, but it reads and writes the calling wallet's storage.

This pattern meant that hundreds of wallets shared a single copy of the business logic. If the library worked correctly, all wallets worked. If the library was destroyed, all wallets became non-functional.

### Key Design Parameters

| Parameter | Value |
|-----------|-------|
| Affected library contract | `0x863DF6BFa4469f3ead0bE8f9F2AAE51c91A907b4` |
| Wallets depending on library | 587 multi-sig wallets |
| Total ETH frozen | ~513,774 ETH |
| Value at time of freeze | ~$150M (ETH ~$292) |
| Peak value of frozen ETH | >$1.5B (ETH >$3,000 in 2021) |
| Library deployed | July 20, 2017 (after first Parity hack fix) |
| Library destroyed | November 6, 2017 |

## Technical Exploit Mechanics

### The Two Vulnerabilities

The incident resulted from the combination of two independent flaws:

**Flaw 1 — Uninitialized Library Contract**:

When the library contract was deployed, its `initWallet` function (which set the wallet owner and other parameters) was never called on the library contract itself. This function was designed to be called on each individual wallet proxy — the proxy would `delegatecall` the library's `initWallet`, which would write the owner addresses into the proxy's storage.

However, the library contract was also a regular Ethereum contract with its own storage. Because `initWallet` was never called directly on the library, the library's own storage had no owner set. This meant anyone could call `initWallet` directly on the library contract (not via delegatecall from a proxy) and become the owner of the library contract itself.

**Flaw 2 — Library Included `kill` Function**:

The library contract contained a `kill` function that called Solidity's `selfdestruct` opcode, sending any ETH balance to the caller and destroying the contract's bytecode. This function was restricted to the contract owner via a modifier.

In the context of individual wallets using `delegatecall`, this function would allow a wallet's owners to destroy their own wallet (using `delegatecall`, the `selfdestruct` would apply to the calling proxy, not the library). But because the library was also a regular contract that could have its own owner, calling `kill` directly on the library would destroy the library itself.

### The Accidental Trigger

On November 6, 2017, a GitHub user known as "devops199" performed the following actions:

1. **Called `initWallet` directly on the library contract**: Because the library was uninitialized, this succeeded, and devops199 became the owner of the library contract
2. **Called `kill` on the library contract**: As the newly set owner, devops199 could call the owner-restricted `kill` function
3. **The library contract self-destructed**: The `selfdestruct` opcode destroyed the library contract's bytecode and sent its (near-zero) ETH balance to devops199

### Why All Dependent Wallets Froze

When the library contract was destroyed:

1. All 587 proxy wallets still had their state (owner lists, ETH balances) intact in their own storage
2. However, every function call on these wallets used `delegatecall` to the library address
3. After `selfdestruct`, the library address contained no bytecode
4. `delegatecall` to an address with no code returns success but does nothing
5. Therefore, no wallet function (including `transfer`, `execute`, or any ownership operation) could execute any logic
6. The ETH locked in these wallets became permanently inaccessible — it could not be sent, and no logic could be executed to authorize a transfer

The wallets were not empty — the ETH was still there, visible on the blockchain. But without executable code at the library address, there was no mechanism to move it.

### devops199's Statement

The user posted on the Parity GitHub repository: "I accidentally killed it." The incident appeared to be unintentional — devops199 was reportedly exploring the uninitialized library contract and triggered the self-destruct without understanding the consequences. The user's account showed no pattern of malicious activity, and there was no financial benefit to destroying the library (the library held negligible ETH).

## The July 2017 Parity Hack (Context)

The November library freeze occurred in the context of an earlier, separate Parity wallet vulnerability:

### July 19, 2017 — Multi-Sig Wallet Hack

| Parameter | Value |
|-----------|-------|
| ETH stolen | ~153,037 ETH |
| Value at time | ~$30M |
| Vulnerability | `initWallet` could be called by anyone on deployed wallets |
| Attacker action | Called `initWallet` to claim ownership, then withdrew funds |
| White hat response | White Hat Group used the same vulnerability to rescue ~377,105 ETH from other vulnerable wallets |

The July hack exploited the same `initWallet` visibility issue, but applied to the wallet proxies rather than the library. After the July hack, Parity deployed a new version of the library contract (the one that would later be accidentally destroyed in November). The fix addressed the wallet-level initialization issue but introduced the library-level vulnerability: the new library itself was deployed without being initialized.

### Irony of the Fix

The November freeze was a direct consequence of the July fix:
- The July vulnerability: individual wallets could be taken over because their `initWallet` was externally callable
- The fix: deployed a new library with an improved initialization pattern
- The November vulnerability: the new library contract itself was left uninitialized, inheriting a version of the same class of bug it was designed to fix

## Recovery Attempts

### EIP-999: Restore Contract Code

In April 2018, Parity submitted EIP-999, proposing to restore the destroyed library contract by deploying new bytecode at the same address through an Ethereum protocol upgrade. This would have re-enabled all 587 frozen wallets to function again.

**Arguments in favor**:
- The frozen funds belonged to legitimate users who had done nothing wrong
- The total amount was significant (~$150M at the time, much more as ETH appreciated)
- The library destruction was accidental, not a deliberate exploit
- The fix was technically simple — restore the contract code

**Arguments against**:
- Setting a precedent for state modifications to fix smart contract bugs undermined Ethereum's immutability
- Similar to the DAO hard fork debate, but without the urgency of an ongoing theft
- Where would the line be drawn? Every future smart contract bug would generate pressure for protocol-level recovery
- Affected parties (especially Parity/Web3 Foundation) were closely associated with Ethereum's core development, raising conflict-of-interest concerns

EIP-999 did not achieve consensus and was not implemented. Subsequent proposals for more general "stuck funds" recovery mechanisms also failed to gain traction.

### Current Status

As of 2026, the approximately 513,774 ETH remains frozen at the same addresses. At ETH prices significantly above $292 (the price at the time of the freeze), the unrealized value of the frozen funds has fluctuated into the billions of dollars. No protocol-level recovery has been implemented, and under Ethereum's current governance norms, none is expected.

## Market Impact

### Immediate Price Effects

| Metric | Pre-Incident | Post-Incident (48h) |
|--------|-------------|-------------------|
| ETH price | ~$305 | ~$292 |
| ETH decline | — | ~4% |

The market impact was relatively muted because:
- No funds were stolen — the ETH was frozen, not taken by an attacker
- The incident affected a specific set of users, not the Ethereum protocol itself
- The broader crypto market was in a strong bull trend in November 2017

### Long-Term Impact on Ethereum Development

1. **Smart contract security practices**: The Parity incidents (both July and November) became canonical examples in smart contract security education, illustrating the dangers of uninitialized contracts, library patterns, and `selfdestruct`
2. **`selfdestruct` deprecation**: The incidents contributed to a broader re-evaluation of the `selfdestruct` opcode. EIP-6780, implemented in the Dencun upgrade (March 2024), restricted `selfdestruct` to only work within the same transaction as contract creation, effectively deprecating its original behavior
3. **Proxy pattern evolution**: The delegatecall proxy pattern was refined with initialization guards (e.g., OpenZeppelin's `Initializable` contract) that prevent the re-initialization vulnerability
4. **Immutability debate**: The frozen funds became a long-running reference point in debates about Ethereum's immutability and the limits of "code is law"

### Impact on Polkadot

The Web3 Foundation's ~306,276 frozen ETH represented a significant portion of Polkadot's initial fundraise. Despite this loss, the Polkadot project continued development and launched its mainnet in 2020, suggesting either sufficient remaining funding or alternative funding mechanisms.

## Vulnerability Pattern: Shared Library Destruction

### The Delegatecall Library Anti-Pattern

The Parity incident revealed that the delegatecall library pattern, while gas-efficient, creates a single point of failure:

1. **Shared dependency**: Hundreds of independent contracts depend on a single library contract's bytecode
2. **Library as a contract**: The library is itself a contract with its own storage, which can be independently manipulated if not properly secured
3. **`selfdestruct` as nuclear option**: Including `selfdestruct` in a shared library means the library's owner can destroy all dependent contracts' functionality with a single transaction

### Comparison to Other Smart Contract Architecture Failures

| Incident | Date | Impact | Architecture Flaw |
|----------|------|--------|------------------|
| The DAO | Jun 2016 | ~$60M stolen | Reentrancy in split function |
| Parity July hack | Jul 2017 | ~$30M stolen | Uninitialized wallet `initWallet` |
| Parity November freeze | Nov 2017 | ~$150M frozen | Uninitialized library + `selfdestruct` |
| Ronin Bridge | Mar 2022 | ~$625M stolen | Centralized validator key management |
| Nomad Bridge | Aug 2022 | ~$190M stolen | Initialization bug in upgrade |

The Parity November incident is unique in this taxonomy because it resulted in permanent fund freezing rather than theft. The funds were not taken by an attacker — they became permanently inaccessible due to a destroyed dependency.

### Post-Parity Security Standards

The Parity incidents drove adoption of several security practices:

1. **Initialization guards**: Contracts that use proxy/library patterns now include checks to prevent re-initialization (e.g., a boolean flag set during initialization that reverts on subsequent calls)
2. **Immutable proxies**: Some proxy patterns avoid using `selfdestruct` entirely, eliminating the library destruction vector
3. **UUPS and Transparent Proxy patterns**: More structured proxy patterns (e.g., OpenZeppelin's UUPS and TransparentUpgradeableProxy) that separate upgrade authority from regular functionality and include initialization protections
4. **Audit focus on initialization**: Smart contract audits now routinely check whether proxy and library contracts are properly initialized at deployment and whether initialization functions are protected against re-calling

## Lessons for Market Surveillance

1. **Shared library dependency mapping**: DeFi protocols that use delegatecall proxy patterns share a dependency on the library contract. Surveillance systems should map which protocols depend on which library contracts and monitor those libraries for ownership changes, self-destruct calls, or other state-modifying transactions.

2. **Uninitialized contract detection**: Contracts deployed without calling their initialization function represent a class of vulnerability. Automated scanning for deployed contracts that have initialization functions which have never been called (and which are externally callable) can identify potential Parity-style risks.

3. **`selfdestruct` monitoring**: Any `selfdestruct` call to a contract that is used as a library or implementation for proxies is a critical event. Real-time monitoring for `selfdestruct` events on addresses identified as library/implementation contracts should trigger immediate alerts.

4. **Frozen fund tracking**: Permanently frozen funds (like the Parity wallets) remain visible on-chain and are sometimes counted in circulating supply metrics. Accurate supply analysis should exclude known frozen addresses to avoid overstating available supply.

5. **Post-fix vulnerability emergence**: The November freeze was a direct consequence of the July fix. Surveillance and audit processes should pay special attention to hastily deployed fixes for prior vulnerabilities, as the fix itself may introduce new issues — particularly in complex patterns like proxy/library architectures.

6. **Protocol upgrade impact on frozen funds**: Ethereum protocol changes (like EIP-6780 restricting `selfdestruct`) can affect the status of frozen contracts. Monitoring for protocol upgrades that change EVM semantics (opcodes, gas costs, state access rules) should include an assessment of impact on known frozen or vulnerable contracts.

## References

1. Parity Technologies. "A Postmortem on the Parity Multi-Sig Library Self-Destruct." Parity Blog, November 2017.
2. Parity Technologies. "Security Alert — Parity Wallet." Parity Blog, July 19, 2017.
3. devops199. "anyone can kill your contract #6995." GitHub Issue, Parity Wallet, November 6, 2017.
4. Ethereum Foundation. "EIP-999: Restore Contract Code at a Specific Address." Ethereum Improvement Proposals, April 2018.
5. OpenZeppelin. "Proxy Patterns and Initializable Contracts." OpenZeppelin Documentation, 2020.
6. Ethereum Foundation. "EIP-6780: SELFDESTRUCT Only in Same Transaction." Ethereum Improvement Proposals, 2023.
