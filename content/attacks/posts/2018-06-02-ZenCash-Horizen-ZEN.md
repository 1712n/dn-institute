---
date: 2018-06-02
target-entities: Horizen
entity-types: Blockchain
attack-types: 51%
title: "ZenCash (now Horizen) Suffers a 51% Attack Resulting in Significant Losses"
loss: 550000
---

## Summary

[On June 2, 2018, ZenCash, now known as Horizen (ZEN), fell victim to a 51% attack](https://blog.horizen.io/zencash-statement-on-double-spend-attack/). During this attack, the perpetrator managed to double-spend ZEN coins by gaining control of a majority of the network's hashrate. The attack lasted several hours and resulted in an estimated loss of approximately 23,000 ZEN, which was equivalent to about $550,000 at that time.

## Attackers

The identity of the attacker or attackers who conducted the 51% attack on the ZenCash network remains unknown.
The suspect pool address is [znkMXdwwxvPp9jNoSjukAbBHjCShQ8ZaLib](https://explorer.horizen.io/address/znkMXdwwxvPp9jNoSjukAbBHjCShQ8ZaLib).
The suspect exchange deposit adress is [zneDDN3aNebJUnAJ9DoQFys7ZuCKBNRQ115](https://explorer.horizen.io/address/zneDDN3aNebJUnAJ9DoQFys7ZuCKBNRQ115)

## Losses

The attackers managed to double-spend approximately 23,000 ZEN coins during the attack. At the time of the attack, this amount was worth around [$550,000](https://www.investing.com/analysis/could-the-zencash-51-attack-have-been-avoided-200323085). The ZenCash community and the exchanges that were targeted suffered the losses, as the value of ZEN also experienced a dip after the attack.

## Timeline

- **June 2, 2018:** The 51% attack on the ZenCash network began. The attackers gained control of a majority of the network's hashrate, which allowed them to mine blocks at an accelerated rate.
- **June 2, 2018:** The ZenCash team became aware of the attack and issued a warning to exchanges and mining pools, advising them to increase the number of confirmations required for ZEN transactions.
- **June 6, 2018:** The ZenCash team released a post-mortem report, detailing the attack and the steps taken to mitigate such incidents in the future.

## Security Failure Causes

- **Availability of Hashing Power for Rent:** The attacker likely used a hashpower marketplace to rent the mining power necessary for the attack. This practice lowers the cost and complexity of performing a 51% attack as attackers don’t need to purchase and set up mining hardware.
- **Slow Response:** Though the ZenCash team responded to the attack, there was still a window of time during which the attacker could exploit the network.
- **Exchange Vulnerabilities:** Exchanges did not require a sufficient number of confirmations for deposits, making them vulnerable to double-spend attacks. Following the attack, many exchanges increased the number of confirmations required for ZEN deposits.
