---
date: 2024-05-31
target-entities: DMM Bitcoin
entity-types:
  - Exchange
  - Custodian
attack-types:
  - Wallet Hack
  - Social Engineering
title: "DMM Bitcoin Loses $308 Million in TraderTraitor Wallet Attack"
loss: 308000000
---

## Summary

On May 31, 2024, Japanese cryptocurrency exchange DMM Bitcoin detected an unauthorized Bitcoin outflow from its wallet. The incident moved [4,502.9 BTC, valued at about $308 million](https://www.elliptic.co/blog/dmm-bitcoin-loses-308-million-in-unauthorized-leak), to attacker-controlled wallets. DMM Bitcoin restricted some services after the incident and said it would procure the equivalent amount of BTC to guarantee customer balances, according to [CoinDesk's report on the exchange announcement](https://www.coindesk.com/business/2024/05/31/japanese-crypto-exchange-dmm-bitcoin-suffers-305m-hack).

In December 2024, the FBI, Department of Defense Cyber Crime Center, and Japan's National Police Agency [attributed the theft to North Korean TraderTraitor activity](https://www.npa.go.jp/bureau/cyber/pdf/20241224_jp.pdf). The agencies described a social-engineering chain that first compromised an employee of Ginco, a Japan-based enterprise cryptocurrency wallet software company, and then used that access to manipulate a legitimate DMM Bitcoin transaction request. CoinDesk also [reported the joint attribution](https://www.coindesk.com/policy/2024/12/24/north-korea-blamed-for-may-s-usd305m-hack-on-japanese-crypto-exchange-dmm).

The breach had long operational consequences. DMM Bitcoin later arranged to transfer customer accounts and deposited assets to SBI VC Trade. SBI VC Trade [announced a basic agreement](https://www.sbivc.co.jp/newsview/1zkj8mf5x3y) to accept DMM Bitcoin customer accounts and custody assets in December 2024, and DMM Bitcoin's service [ended on March 8, 2025](https://bitcoin.dmm.com/news/20240531_01), with customer accounts and assets transferred to SBI VC Trade.

## Attackers

The attackers were identified by U.S. and Japanese authorities as North Korean cyber actors tracked as TraderTraitor, also known as Jade Sleet, UNC4899, and Slow Pisces. The joint FBI/DC3/NPA attribution notice stated that TraderTraitor activity often uses targeted social engineering against multiple employees at the same company.

The attack path described by the joint attribution notice involved:

- a North Korean actor posing as a recruiter on LinkedIn;
- a Ginco employee receiving a malicious Python script under the cover of a pre-employment test;
- compromise of the employee, who had access to Ginco's wallet management system;
- exploitation of session cookie information after mid-May 2024;
- access to Ginco's unencrypted communications system;
- likely manipulation of a legitimate DMM Bitcoin transaction request in late May 2024.

Elliptic reported that the stolen bitcoin was split and sent to multiple new wallets shortly after the outflow.

## Losses

DMM Bitcoin lost 4,502.9 BTC, valued at about $308 million at the time of the attack.

The loss was a single-asset Bitcoin theft. Public reports did not identify other cryptocurrency assets as part of the unauthorized outflow.

## Timeline

- **March 31, 2024, 11:59 PM UTC:** A North Korean actor masquerading as a recruiter on LinkedIn had contacted a Ginco employee who had access to Ginco's wallet management system; the FBI report gives the timing as late March 2024, not an exact timestamp.
- **May 16, 2024, 12:00 AM UTC:** TraderTraitor actors began the source-reported post-mid-May phase of exploiting session cookie information to impersonate the compromised Ginco employee and access Ginco's unencrypted communications system; the FBI report does not publish a more exact timestamp.
- **May 31, 2024, 04:26 AM UTC:** DMM Bitcoin detected an unauthorized Bitcoin outflow from its wallet involving 4,502.9 BTC, corresponding to the company's reported 1:26 PM JST detection time.
- **May 31, 2024, 01:40 PM UTC:** CoinDesk reported DMM Bitcoin's service restrictions, including restricted spot buys and longer Japanese yen withdrawal times, and DMM Bitcoin's statement that it would procure equivalent BTC to cover the outflow.
- **May 31, 2024, 03:00 PM UTC:** Elliptic reported that the stolen bitcoin had already been split and sent to multiple new wallets as of 15:00 UTC.
- **December 2, 2024, 12:00 AM UTC:** SBI VC Trade announced that it had reached a basic agreement to accept DMM Bitcoin customer accounts and deposited assets; the announcement source provides a date but not a UTC timestamp.
- **December 23, 2024, 12:00 AM UTC:** The FBI, DC3, and Japan's National Police Agency publicly attributed the theft to North Korean TraderTraitor actors; the public attribution source provides a date but not an intraday UTC timestamp.
- **March 8, 2025, 12:00 AM UTC:** DMM Bitcoin ended service and transferred customer accounts and custody assets to SBI VC Trade; the DMM service notice provides a date but not an intraday UTC timestamp.

## Security Failure Causes

**Third-party wallet operations compromise:** The joint attribution did not describe a direct breach of DMM Bitcoin's internal systems. Instead, it described compromise of a Ginco employee with wallet-management access and later use of that access to manipulate a legitimate DMM transaction request. This made the wallet operations workflow, including third-party communications and authorization checks, part of the effective attack surface.

**Social engineering and malicious code execution:** The initial compromise came from a targeted LinkedIn recruiter lure and a malicious Python script presented as a pre-employment test. That path converted a human hiring interaction into access to systems relevant to cryptocurrency wallet operations.

**Session cookie and communication-system abuse:** After the Ginco compromise, TraderTraitor actors used session cookie information to impersonate the employee and access unencrypted communications. The incident shows how session security and communication confidentiality can directly affect custody transaction integrity.

**Insufficient transaction-request verification:** The reported manipulation of a legitimate transaction request suggests that the transaction approval process did not independently detect that the destination or request context had been altered before 4,502.9 BTC moved out of DMM Bitcoin's wallet.
