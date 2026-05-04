---
date: 2026-05-05
entities:
  - id: tornado-cash
    name: Tornado Cash
    type: defi
  - id: tornado-cash-governance
    name: Tornado Cash Governance
    type: defi
title: "Tornado Cash governance takeover via CREATE2/selfdestruct proposal substitution and 1.2 M fraudulent TORN votes"
---

## 1. Introduction and incident overview

On 20 May 2023, an attacker seized complete control of Tornado Cash's decentralized governance system by exploiting a sophisticated smart-contract technique that allowed them to substitute a previously approved proposal's code after the governance vote had already passed. The attacker used a combination of the CREATE2 opcode, the selfdestruct function, and nonce manipulation to deploy a malicious contract at the same address as the originally approved (benign-appearing) proposal. Once executed, the malicious code granted the attacker 1.2 million fake TORN governance votes, giving them unilateral control over all governance decisions — including the ability to drain locked governance tokens, modify protocol parameters, and redirect Tornado Cash's router.

The Tornado Cash governance attack represented one of the most technically sophisticated governance exploits in DeFi history. Unlike the Compound governance attack (which used straightforward token accumulation to achieve a voting majority), the Tornado Cash attack exploited a fundamental property of the Ethereum Virtual Machine: the ability to deploy different bytecode at the same address by destroying and recreating contracts using CREATE2 with the same salt and creator address. The attack demonstrated that even verified proposal code cannot be fully trusted if the underlying deployment mechanism allows post-verification code substitution.

## 2. Technical background

### 2.1 Tornado Cash governance system

Tornado Cash is a privacy-focused decentralized protocol on Ethereum that enables anonymous token transfers by mixing deposits with withdrawals to break the on-chain link between sender and recipient addresses. The protocol is governed by holders of the TORN governance token through an on-chain DAO governance system.

The Tornado Cash governance process works as follows:

1. **Proposal creation**: A user deploys a smart contract containing the proposed changes and submits it to the governance contract via the `propose()` function, passing the proposal contract's address.
2. **Voting period**: TORN token holders who have locked their tokens in the governance contract vote for or against the proposal.
3. **Execution**: If the proposal passes, anyone can trigger its execution. The governance contract uses `delegatecall` to execute the proposal contract's code in the context of the governance contract itself.

The critical security implication of this design is that proposal execution via `delegatecall` gives the proposal contract full access to modify the governance contract's storage. This is by design — proposals need this access to change protocol parameters — but it means that a malicious proposal can modify any governance state, including locked token balances and voting power.

### 2.2 CREATE and CREATE2 opcodes

Ethereum provides two opcodes for contract deployment:

**CREATE**: Deploys a contract at an address determined by the deployer's address and their transaction nonce. Each deployment increments the nonce, so the same creator deploying the same bytecode will get a different address on each deployment.

**CREATE2**: Deploys a contract at an address determined by the deployer's address, a salt value, and the contract's creation bytecode. Because the address depends on deterministic inputs (not the nonce), the same creator using the same salt and bytecode will always produce the same address.

A key property of CREATE2 is that if a contract is deployed at address X, then destroyed (via `selfdestruct`), the same address X can be reused by deploying again with the same creator, salt, and creation bytecode. However, if the creation bytecode itself deploys another contract using CREATE, the deployed sub-contract's bytecode can differ between deployments because CREATE depends on the nonce — and `selfdestruct` resets the nonce to zero.

### 2.3 selfdestruct and contract redeployment

The `selfdestruct` opcode destroys a contract, removing its code and storage from the blockchain state and sending any remaining ETH balance to a designated recipient. Critically, `selfdestruct` also resets the destroyed address's nonce to zero. This nonce reset is the key enabler of the Tornado Cash governance attack: it allows a contract at a known address to be destroyed and recreated with a fresh nonce, enabling its CREATE-deployed children to have different bytecode while maintaining the same addresses.

Note: As of the Dencun upgrade in 2024, `selfdestruct` behavior has been modified (EIP-6780 limits it to only work within the same transaction as creation). However, at the time of the Tornado Cash attack in May 2023, the original `selfdestruct` behavior was still in effect.

### 2.4 The delegatecall trust assumption

Tornado Cash governance relies on `delegatecall` to execute proposals. When the governance contract `delegatecall`s a proposal, the proposal's code executes with the governance contract's storage and context. This means any `SSTORE` instruction in the proposal code directly modifies governance contract storage.

The security assumption underlying this design is that the community reviews and verifies the proposal code before voting. If the verified code is benign, execution via `delegatecall` is safe. The attack exploited this assumption by ensuring that the code visible at the proposal address during the voting period was different from the code present at execution time.

## 3. The attack mechanism

### 3.1 Setup: the deployer chain

The attacker constructed a multi-layer deployment architecture:

1. **Factory contract (0xAAA)**: Deployed normally. Contains a function that uses CREATE2 to deploy child contracts at predictable addresses.

2. **Intermediate contract (0xBBB)**: Deployed by the factory using CREATE2. Because CREATE2 is deterministic, this contract always deploys at the same address (given the same salt and bytecode). Contains a function to deploy sub-contracts using CREATE, and a `selfdestruct` function disguised as an "emergency stop."

3. **Proposal contract (0xCCC)**: Deployed by 0xBBB using CREATE. Because 0xBBB's nonce starts at 0 on first deployment, and CREATE addresses depend on the creator's nonce, the proposal deploys at a deterministic address (hash of 0xBBB's address + nonce 0).

### 3.2 Phase 1: Deploy benign proposal

The attacker first deployed the full chain:
- Factory → (CREATE2) → Intermediate 0xBBB
- Intermediate 0xBBB → (CREATE, nonce=0) → Proposal 0xCCC (benign code)

The benign proposal at 0xCCC contained code that appeared to implement routine governance functionality. The code was verified on Etherscan, and community members reviewed it during the voting period. The proposal passed the governance vote.

### 3.3 Phase 2: Destroy and redeploy

After the vote passed but before execution, the attacker triggered the attack:

1. Called `selfdestruct` on 0xCCC (the benign proposal), destroying it.
2. Called `selfdestruct` on 0xBBB (the intermediate contract), destroying it and resetting its nonce to 0.
3. Called the factory to redeploy 0xBBB using CREATE2 with the same salt and bytecode — deploying at the same address as before.
4. Called 0xBBB to deploy a new contract using CREATE with nonce 0 — this deployed at the same address 0xCCC, but now with **malicious** code.

The key insight is that the intermediate contract 0xBBB is recreated at the same address (because CREATE2 is deterministic given the same inputs), and its nonce is reset to 0 (because `selfdestruct` clears state). When 0xBBB then uses CREATE to deploy a child, the child deploys at hash(0xBBB, nonce=0) — the same address as the original benign proposal — but with completely different code.

### 3.4 Phase 3: Execute malicious proposal

When the governance contract executed the "approved" proposal via `delegatecall`, it called the code at address 0xCCC. But the code at 0xCCC was no longer the benign proposal that was reviewed — it was the attacker's malicious replacement.

The malicious code used `SSTORE` operations to directly modify the governance contract's storage, specifically:

- Setting `lockedBalance[attacker_address_1]` to 10,000 TORN
- Setting `lockedBalance[attacker_address_2]` to 10,000 TORN
- ... (repeated for approximately 120 addresses)

By setting the locked balance to 10,000 TORN for each of approximately 120 attacker-controlled addresses, the attacker created 1.2 million fake TORN votes (120 addresses × 10,000 TORN each). These addresses had never actually deposited any TORN tokens — the storage was modified directly via the `delegatecall` execution.

### 3.5 Exploitation of governance control

With 1.2 million fraudulent votes, the attacker achieved absolute control over Tornado Cash governance. This voting power exceeded any realistic opposition, allowing the attacker to:

- Pass any future proposal unilaterally.
- Drain the approximately 473,000 TORN tokens locked in the governance contract by other users.
- Modify the Tornado Cash router to redirect funds.
- Change any protocol parameter.

The attacker drained approximately 473,000 TORN tokens from the governance contract, representing the locked governance stakes of legitimate TORN holders. At the time of the attack, TORN was trading at approximately $4-5, placing the immediate loss at approximately $2 million. However, the TORN price dropped approximately 40% following news of the attack, reflecting the market's assessment that governance control was compromised.

## 4. Aftermath and resolution

### 4.1 Initial community response

The attack was identified within hours of execution. The DeFi security community, including SlowMist, PeckShield, and independent researchers, published analyses documenting the CREATE2/selfdestruct technique. The Tornado Cash community recognized that the attacker now controlled governance and that any proposals the attacker submitted would pass automatically.

### 4.2 Attacker's proposal to return control

On 26 May 2023 — six days after the attack — the attacker submitted a new proposal offering to return governance control to the community. The proposal would:

- Reset the attacker's fraudulent locked balances to zero.
- Restore governance parameters to their pre-attack state.
- Return remaining TORN tokens to the governance contract.

This reversal proposal was met with skepticism from portions of the community, as the attacker retained the ability to pass any proposal and could theoretically submit additional malicious proposals at any time. However, because the attacker controlled governance, the community had no means to restore control without the attacker's cooperation (or a full contract migration).

The reversal proposal ultimately passed (the attacker voted for their own proposal), and governance control was partially restored. However, the approximately 473,000 TORN tokens that had already been drained and sold or moved were not recovered.

### 4.3 TORN token price impact

TORN's price dropped approximately 40% immediately following news of the governance takeover, falling from approximately $5.50 to approximately $3.50. The price partially recovered following the attacker's proposal to return control but did not fully return to pre-attack levels. The incident compounded existing negative pressure on TORN from the August 2022 OFAC sanctions against the protocol, which had already significantly reduced confidence in the token's long-term value.

## 5. Market-health implications

### 5.1 CREATE2/selfdestruct as a governance attack vector

The Tornado Cash attack introduced a novel attack vector that applies to any governance system that:

1. Executes proposals via `delegatecall` (or similar mechanisms that give proposals direct storage access).
2. Identifies proposals by their contract address (rather than by their code hash).
3. Does not verify that the code at the proposal address is unchanged between voting and execution.

The CREATE2/selfdestruct technique allows an attacker to present benign code for review, obtain community approval, and then substitute malicious code at the same address before execution. This breaks the fundamental trust assumption of governance code review: that the code reviewed is the code that will be executed.

This attack vector is distinct from simpler governance attacks (like Compound's) because it does not require accumulating a voting majority. The attacker can pass the proposal with legitimate community support (because the visible code is benign), and the actual attack occurs in the gap between approval and execution.

### 5.2 Governance timing windows

The Tornado Cash attack exploited the temporal gap between proposal approval (when code is reviewed and voted on) and proposal execution (when the code is actually run). In most governance systems, there is a delay between these events — often intentional (e.g., a timelock) to allow the community to react to passed proposals.

Paradoxically, the timelock mechanism — designed to protect against malicious proposals by giving the community time to respond — created the window that the attacker exploited. The attacker needed the proposal to be approved and then waited for the timelock period to substitute the code before execution.

This creates a security trade-off: shorter timelocks reduce the window for code substitution but also reduce the window for community review of passed proposals. Longer timelocks increase both windows proportionally.

### 5.3 Implications for verified contract trust

The DeFi ecosystem has traditionally treated source-code verification (on Etherscan and other block explorers) as a trust signal. Users and governance participants review verified source code to understand what a contract does before interacting with it. The Tornado Cash attack demonstrated that source verification is not sufficient for security when the underlying deployment mechanism allows code substitution.

For market surveillance and risk assessment, this implies that:

- Governance proposals deployed using CREATE2 (or with `selfdestruct` in their dependency chain) should be treated as higher-risk than proposals deployed with standard CREATE.
- The presence of `selfdestruct` in any contract associated with a governance proposal is a red flag.
- Code hash verification at execution time (not just at voting time) is necessary for secure governance.

### 5.4 Protocol-specific vs. systemic risk

Unlike the Ledger Connect Kit or Celer cBridge attacks (which affected multiple protocols through shared dependencies), the Tornado Cash governance attack was protocol-specific — it affected only Tornado Cash's governance system. However, the attack technique is transferable to any governance system with similar architecture (delegatecall execution of proposal contracts identified by address rather than code hash).

At the time of the attack, numerous DeFi protocols used governance architectures with similar properties:

| Protocol | delegatecall Execution | Address-based Proposal ID | CREATE2 Risk |
|---|---|---|---|
| Tornado Cash | Yes | Yes | **Exploited** |
| Compound (Governor Bravo) | No (calldata-based) | N/A | Lower risk |
| OpenZeppelin Governor | No (calldata-based) | N/A | Lower risk |
| MakerDAO (DSPause) | Yes (slate-based) | Yes | Elevated risk |

Protocols using calldata-based proposal systems (where the proposal specifies target addresses and function calls rather than delegating to a proposal contract) are not vulnerable to this specific attack vector.

### 5.5 Compounding with regulatory sanctions

The governance attack occurred against the backdrop of existing OFAC sanctions against Tornado Cash (imposed in August 2022). The sanctions had already reduced developer activity on the protocol, limited governance participation, and created legal uncertainty around interacting with the protocol's governance. This pre-existing weakening of the governance community likely made the attack easier to execute, as fewer participants were actively monitoring proposals and fewer developers were maintaining governance security.

For market health, this illustrates how external pressures (regulatory actions, developer departures, community fragmentation) can compound protocol-level security risks. A protocol under sanctions with reduced governance participation becomes a softer target for governance attacks.

### 5.6 The "benevolent attacker" pattern

The attacker's decision to return governance control after draining 473,000 TORN tokens follows a pattern seen in other DeFi exploits (including Transit Swap and Euler Finance) where attackers retain a portion of stolen funds while returning the remainder. In this case, the attacker retained the already-drained TORN while returning the governance privileges that would allow continued extraction.

This pattern creates perverse incentives: if attackers routinely extract value and then return partial control (positioning the extraction as a "bug bounty" or "demonstration"), the expected payoff from governance attacks remains positive. The attacker in this case profited approximately $2 million while facing minimal personal risk, as the pseudonymous nature of the attack made identification difficult.

## 6. Lessons learned and recommendations

### 6.1 For governance protocol designers

1. **Verify code hash at execution time**: Governance contracts should record the code hash of proposal contracts at the time of vote, and verify that the code hash is unchanged at execution time. If the code at the proposal address has changed (indicating a selfdestruct/redeploy), execution should revert.

2. **Use calldata-based proposals where possible**: Instead of `delegatecall`-ing to proposal contracts, governance systems can encode proposals as structured calldata (target address, function signature, parameters). This eliminates the code-substitution risk because the proposal's behavior is defined by its calldata, not by code at an external address.

3. **Reject proposals with CREATE2/selfdestruct dependencies**: Governance frameworks should scan proposal contracts and their deployment ancestry for `selfdestruct` opcodes and CREATE2-based deployment patterns. Proposals deployed through chains that include `selfdestruct` capability should require additional review or be automatically rejected.

4. **Implement code-freeze mechanisms**: Governance contracts can require that proposal contract code be "frozen" (no `selfdestruct` possible) for a minimum period before the proposal can be executed. This can be enforced by checking that the contract's code is present both at vote time and at execution time with matching code hashes.

### 6.2 For governance participants

1. **Audit deployment patterns**: When reviewing governance proposals, examine not only the proposal's source code but also how it was deployed. Proposals deployed via CREATE2 from contracts that contain `selfdestruct` should be treated with extreme caution.

2. **Verify code presence at execution time**: Before voting to execute a passed proposal, verify that the code at the proposal address matches what was reviewed during the voting period. If the code has changed or the address contains no code, do not execute.

3. **Monitor for selfdestruct events**: Implement monitoring for `selfdestruct` events on any contracts associated with pending governance proposals. A `selfdestruct` event between the proposal's approval and its execution is a strong indicator of a code-substitution attack in progress.

### 6.3 For market surveillance

1. **Track CREATE2 factory patterns**: Monitor Ethereum for contracts that deploy governance proposals using CREATE2 with `selfdestruct` capabilities. This deployment pattern is a prerequisite for the code-substitution attack.

2. **Monitor governance token drain events**: Rapid drainage of locked governance tokens from governance contracts is a signal that a governance takeover has occurred. This is detectable on-chain regardless of the attack mechanism.

3. **Cross-reference sanctions and governance activity**: Protocols under regulatory sanctions with declining governance participation face elevated governance attack risk. Market surveillance should account for this compounding factor when assessing protocol governance security.

## 7. Conclusion

The Tornado Cash governance takeover of May 2023 demonstrated a technically sophisticated attack vector that exploits fundamental EVM properties to substitute malicious code for approved governance proposals. By combining CREATE2 deterministic addressing, selfdestruct nonce resetting, and the temporal gap between proposal approval and execution, the attacker achieved complete governance control without needing a token majority — instead tricking the community into approving a proposal whose code was later replaced.

The $2+ million in direct losses (473,000 drained TORN tokens) and 40% token price decline represented significant market-health impact for a protocol already weakened by OFAC sanctions. More broadly, the attack established that governance code review is insufficient without execution-time code verification, creating a new security requirement for any governance system that executes proposals via delegatecall to external contracts. Until governance frameworks implement code-hash verification at execution time or transition to calldata-based proposal systems, the CREATE2/selfdestruct governance attack vector remains available against any protocol with a compatible architecture.
