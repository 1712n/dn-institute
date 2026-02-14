---
date: 2026-01-31
target-entities: Step Finance
entity-types:
  - DeFi
  - Yield Aggregator
attack-types:
  - Private Key Leak
  - Social Engineering
title: "Step Finance Loses $27.3 Million in SOL After Executive Device Compromise"
loss: 27300000
---

## Summary

On January 31, 2026, [Step Finance, a Solana-based DeFi dashboard and yield aggregator, lost $27.3 million](https://cointelegraph.com/news/step-finance-treasury-breach-solana-step-token-crash) (261,854 SOL) after attackers compromised executive team devices through social engineering. The attacker gained stake authorization on Step Finance's treasury wallets, unstaked the SOL, and transferred it to attacker-controlled wallets. [CertiK first detected the large-scale unstaking](https://x.com/certikalert/status/2017610781660217643), while Step Finance scrambled to engage cybersecurity firms. The team later [confirmed the breach resulted from executive device compromise](https://x.com/StepFinance_/status/2018379876642804213), most likely through a phishing attack. The STEP token [crashed 93%](https://www.coingecko.com/en/coins/step-finance) following the incident. Step Finance [recovered approximately $4.7 million through Solana Token22 protections](https://x.com/StepFinance_/status/2018379876642804213).

## Attackers

The identity of the attacker is unknown. [Step Finance described the perpetrator as a "sophisticated actor" operating during APAC hours](https://x.com/StepFinance_/status/2017667403803410554) who used "a well known attack vector" — widely interpreted as a phishing or social engineering attack targeting executive devices.

## Losses

- 261,854 SOL (~$27.3 million)
- ~$4.7 million recovered through Token22 protections
- Net loss: ~$22.6 million
- STEP token price collapsed 93%

## Timeline

- **January 31, 2026, early morning:** Attacker compromised executive team devices and gained stake authorization on Step Finance treasury wallets.
- **January 31, 2026:** [261,854 SOL unstaked and transferred](https://x.com/certikalert/status/2017610781660217643) to attacker-controlled wallets.
- **January 31, 2026:** [Step Finance acknowledged a breach](https://x.com/StepFinance_/status/2017579514943938646) of "some of our treasury wallets."
- **January 31, 2026:** Step Finance [called for cybersecurity firm assistance via X](https://x.com/StepFinance_/status/2017581368226574472).
- **January 31, 2026:** Step Finance [described the attack as conducted by a "sophisticated actor"](https://x.com/StepFinance_/status/2017667403803410554) during APAC hours using "a well known attack vector."
- **February 2, 2026:** Step Finance [confirmed that executive team devices were compromised](https://x.com/StepFinance_/status/2018379876642804213) and announced the recovery of $4.7 million through Token22 protections.

## Security Failure Causes

- **Executive Device Compromise:** The attack did not exploit any smart contract vulnerability. Instead, the attacker [compromised executive team devices](https://x.com/StepFinance_/status/2018379876642804213), most likely through phishing or social engineering, gaining direct access to wallet credentials and stake authorization.
- **Centralized Key Management:** Despite operating in DeFi, Step Finance's treasury SOL was secured through keys accessible from executive devices rather than through hardware wallets, multi-party computation, or institutional custody solutions that would have limited the impact of a single device compromise.
- **Insufficient Operational Security:** The protocol had audited smart contracts, bug bounties, and public security reviews, but these measures [did not extend to operational security of personnel devices](https://x.com/rzonsol/status/2018395166118150320) — the actual attack vector.
