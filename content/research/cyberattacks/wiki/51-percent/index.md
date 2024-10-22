---
title: "51% Attacks"
bookToc: true
---

In plain language, the 51% attack is centered around overpowering network validators for multiple blocks to convince someone to accept a fraudulent transaction. In proof-of-work blockchains, the success of a 51% attack is determined by mining consecutive blocks with high enough probability to justify the risks of using computing power. Although it used to be possible to trick crypto custodians into double-spending their funds by accumulating 51% of the hashing power, the current state of things made it a much more difficult task. Proactive network monitoring tools made it easier to spot blockchain reorgs and temporarily suspend withdrawals in case of attacks. This raised the mining power bar of a successful "51%" attack well above the original 51%.

## Frogger Formula

The retro arcade game Frogger is a good analogy to describe the chances of successfully attacking a network these days. There are 6 lanes of traffic and the frog needs to cross each lane of traffic to make it across the road. In this example, the frog needs at least a 51% chance of making it across the whole road, otherwise it's not worth trying. For a 51% chance of crossing the whole road, it’s not as simple as a one-in two-chance per lane. In fact, the frog needs a 90% chance of making it past each lane in order to have a 51% chance of crossing the whole road. Here's the Frogger Formula:
**90%<sup>6</sup> ~= 51%**

{{< image src="frogger.png" alt="Frogger" >}}

With this example, lanes represent blocks and the whole road represents convincing someone to accept a fraudulent transaction. Just as the frog can’t successfully cross the road if it doesn’t make it past one of the lanes, an attacker can’t leave orphaned blocks without arousing suspicion at a crypto custodian.

In the digital assets space there is variation among 51% attack cost definitions with some popular definitions listed here.

## Definition 1: Crypto51

Crypto51 data is built around the assumption that successfully executing an attack takes 51% of existing hashing power for 1 hour. Although this definition gets close, in reality it falls short in terms of fooling exchanges into accepting the falsified blocks, as described with the Frogger example.

Using Crypto51’s definition for Bitcoin, employing 51% of the hashing power for one hour might get you 3 non-sequential blocks and arise suspicion about orphaned blocks. For most reputable exchanges, this would be insufficient for acceptance.

## Definition 2: Investopedia

Investopedia broadly defines 51% attack as “miners controlling more than 50% of the network's mining hashrate, or computing power”. From a technical perspective, this definition is sufficient, but defining blockchain security fundamentals going forward requires an improved definition. For a 51% attack cost definition, the number of blocks necessary and the time of computing power must be defined.

## Improving Definitions

For Bitcoin, transactions are confirmed when they are followed by at least 6 successful blocks. Reputable exchanges oversee and accept transactions at intervals, and will hesitate if they see orphaned blocks or signs of tampering. All said, it takes about 10 minutes to mine each block, bringing 6 sequential blocks to 1 hour of computing power.

With this, 6 sequential blocks are needed to convince most exchanges to accept a double-spent transaction. Winning 6 sequential blocks increases the necessary probability closer to 90% per block to ensure the overall probability of 51% success for all blocks.
