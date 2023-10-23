---
date: 2021-10-27
target-entities: Cream Finance
entity-types:
  - DeFi
  - Lending Platform
attack-types:
  - Smart Contract Exploit
  - Flash Loan Attack
  - Price Oracle Manipulation
title: "Cream Finance Hack: $130 Million Stolen in Exploit"
loss: 130000000
---

## Summary

On October 27, 2021, a hacker stole $130 million worth of cryptocurrency from Cream Finance, a decentralized finance (DeFi) platform.

The hack was carried out using a combination of a flash loan attack and price oracle manipulation. In a flash loan attack, the hacker borrows a large amount of cryptocurrency and then uses it to exploit a vulnerability in a DeFi protocol. In price oracle manipulation, the hacker manipulates the price of an asset to make a profit.

The hacker used a flash loan to borrow a large amount of cryptocurrency and then used it to manipulate the price of an asset on Cream Finance's price oracle. This allowed the hacker to borrow more cryptocurrency than they had originally borrowed.

## Attackers

The attackers remain unidentified. The attacker(s) utilized the following Ethereum address:

- [0x24354d31bc9d90f62fe5f2454709c32049cf866b](https://etherscan.io/address/0x24354d31bc9d90f62fe5f2454709c32049cf866b)

## Losses

$130 million in USD

## Timeline

- **October 27, 2021, 01:54:10 PM +UTC** Attacker's [transaction](https://etherscan.io/tx/0x0fe2542079644e107cbf13690eb9c2c65963ccb79089ff96bfaf8dced2331c92)
- **October 28, 2021, 03:17 AM +UTC:** Cream Finance [announced](https://twitter.com/CreamdotFinance/status/1453455806075006976) that the protocol was hacked.
- **October 28, 2021:** Blockchain security firm Slow Mist [published hack analysis](https://medium.com/@slowmist/cream-hacked-analysis-us-130-million-hacked-95c9410320ca)
- **November 1, 2021:** Cream Finance [published exploit Post-Mortem.](https://medium.com/cream-finance/c-r-e-a-m-finance-post-mortem-amp-exploit-6ceb20a630c5)
- **November 13, 2021:** Cream Finance [announced](https://creamdotfinance.medium.com/moving-forward-post-exploit-next-steps-for-c-r-e-a-m-finance-1ad05e2066d5) that affected users will receive 1,453,415 CREAM tokens
- **November 9, 2022:** Immunefi [published hack analysis](https://medium.com/immunefi/hack-analysis-cream-finance-oct-2021-fc222d913fc5)

## Security Failure Causes

- **Flash Loans Exploitation:** The exploit leveraged flash loans, which allow borrowing large sums without collateral, for price manipulation and creating strain on the system.
- **Price Oracle Manipulation:** The attackers manipulated price oracles, leading the protocol to make decisions based on incorrect asset prices.
