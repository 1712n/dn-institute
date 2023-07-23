---
date: 2021-06-22
target-entities:
	- Fireblocks
	- StakeHound
entity-types:
	- Custodian
	- Yield Aggregator
attack-types:
	- Private Key Loss
title: "Negligence Leads to $75 Million Loss at Fireblocks"
---

## Summary

Israeli security firm Fireblocks is being sued by StakeHound, a staking service, for the loss of 38,178 Ether (ETH) tokens, valued at around $74.4 million. StakeHound claims the loss occurred due to Fireblocks losing two necessary keys for accessing the tokens.
The lost tokens made up over 5% of the total amount of ETH locked in liquid stake pools. Prior to the incident, StakeHound was the second-largest provider of liquid derivatives tied to staked ETH.
The case is currently being processed in the Israeli High Court. The incident has raised concerns about the risks of using custodial services for staking cryptocurrency.

## Attackers

The loss is not attributed to external attackers but rather to internal negligence at Fireblocks.

## Losses

StakeHound alleges the loss of 38,178 ETH valued at approximately $75 million at the time of an incident.

## Timeline

- **April 29, 2021:** The Fireblocks team [discovered that they couldn't decrypt some BLS key shards from the backup](https://www.fireblocks.com/blog/stakehound-eth-2-0-event/) during a routine disaster recovery drill.
- **May 2, 2021:** StakeHound was [informed by Fireblocks](https://stakehound.com/blog-post/fireblocks-eth-2-key-management-incident/), that staked ETH may have been rendered inaccessible.
- **June 22, 2021:** StakeHound [files a lawsuit against Fireblocks](https://www.calcalistech.com/ctech/articles/0,7340,L-3910671,00.html) for allegedly losing $75 million worth of ETH due to negligence.

## Security Failure Causes

- **Failure to Back Up:** Fireblocks reportedly did not transfer the relevant private keys to Coincover, a company trusted with backing up the keys. According to Fireblocks' guidelines, the keys should have been backed up with a third-party service provider, which was not done in this case. [Source](https://www.coindesk.com/markets/2021/06/22/fireblocks-being-sued-for-allegedly-losing-over-70m-of-ether-report/)
