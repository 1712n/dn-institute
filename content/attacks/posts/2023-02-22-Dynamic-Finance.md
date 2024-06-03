---
date: 2023-02-22
target-entities: Dynamic Finance
entity-types: DeFi
attack-types:
  - Smart Contract Exploit
  - Reentrancy Attack
  - Flash Loan Attack
title: "Dynamic Finance Suffers $22,400 Loss Due to Reentrancy Attack"
loss: 22400
---

## Summary

Dynamic Finance, a DeFi aggregator, was exploited for 73 BNB ($22,400) on February 22, 2023, via a reentrancy attack on its StakingDYNA contract. The attacker exploited insufficient reentrancy protections, tricking the platform's deposit tracking system. Initially, the attacker deposited a small amount of $DYNA, then significantly inflated their deposit amount through a flash loan. This allowed them to claim exaggerated rewards and withdraw them, exploiting the platform’s reward calculation and withdrawal mechanisms. The attack resulted in financial loss and caused the $DYNA token price to crash by over 93%.

## Attackers

The identity of the attacker is unknown. The following addresses are associated with this attack:

- [0x0c925a25fdaac4460cab0cc7abc90ff71f410094](https://bscscan.com/address/0x0c925a25fdaac4460cab0cc7abc90ff71f410094)
- [0x35596bc57c0cab856b87854ecc142020a47f6fdf](https://bscscan.com/address/0x35596bc57c0cab856b87854ecc142020a47f6fdf)

## Losses

Losses amounted to 73 BNB worth $22,400.

## Timeline

- **February 22, 2023, 05:36 AM UTC:** The [first malicious](https://bscscan.com/tx/0xc09678fec49c643a30fc8e4dec36d0507dae7e9123c270e1f073d335deab6cf0) transaction occurred.
- **February 22, 2023, 06:02 AM UTC:** [Dyna token has dropped 93%.](https://twitter.com/CertiKAlert/status/1628274049154531329)

## Security Failure Causes

- **Smart Contract Vulnerability:** The root cause of the attack is a reentrancy bug that tricked the deposit tracking system of the contract.
