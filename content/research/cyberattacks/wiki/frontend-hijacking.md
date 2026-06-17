---
title: Frontend Hijacking & DNS Spoofing
bookToc: true
---

Even when smart contracts are immutable, the web interfaces that users rely on are not. Frontend compromises let attackers weaponize web servers, registrar accounts, injected JavaScript, and package dependencies to trick users into signing approvals that grant token access to attacker-controlled spenders.

## The Mechanism of Frontend Attacks

Most dApps still depend on centralized web infrastructure at the point where users click "connect wallet" or sign a transaction.

- **Compromised scripts and dependencies:** A malicious third-party package or injected script can rewrite wallet prompts, replace spender addresses, or present fake approval flows.
- **Registrar or DNS hijacking:** If an attacker controls a domain or DNS entry, they can redirect users to a pixel-perfect clone that asks for malicious approvals.
- **Approval abuse:** The most common end state is not "send funds directly" but tricking the user into signing an `approve` transaction that grants token access to an attacker-controlled contract.

## Case Studies

### 1. Badger DAO ($120M) - Cloudflare API Key Exploit

- **Vector:** Public incident reporting describes the Badger DAO compromise as a frontend-injection attack in which an attacker abused a compromised Cloudflare API key and Cloudflare-connected web infrastructure to inject malicious JavaScript into the production interface, reportedly toggling the payload on and off during November 2021 before the December 2 drain ([rekt.news](https://rekt.news/badger-rekt/), [Chainalysis](https://www.chainalysis.com/blog/chainalysis-podcast-episode-6-badgerdao-hack/)).
- **Impact:** The injected code targeted approvals by replacing the intended spender flow with attacker-controlled approvals, and reported losses were about [$120 million](https://rekt.news/badger-rekt/).
- **Lesson:** Web2 admin credentials can become DeFi key material if they control production frontend assets.

### 2. Curve Finance ($570k) - DNS Hijacking via Registrar Compromise

- **Vector:** In August 2022, attackers reportedly compromised Curve's account at registrar `iwantmyname` and rewrote the DNS records for `curve.fi`, redirecting users to a malicious site. Contemporary reporting therefore describes the incident as DNS hijacking caused by registrar-account compromise rather than DNS cache poisoning ([BleepingComputer](https://www.bleepingcomputer.com/news/security/curve-finance-loses-570-000-in-dns-hijacking-attack/), [CoinDesk](https://www.coindesk.com/business/2022/08/10/curve-finance-front-end-compromised/)).
- **Impact:** The fake site presented malicious approval flows, and users who signed them exposed funds to the attacker; reported realized losses were around [$570,000](https://www.bleepingcomputer.com/news/security/curve-finance-loses-570-000-in-dns-hijacking-attack/).
- **Lesson:** If the registrar account is compromised, the security of the smart contracts no longer matters to end users interacting through the browser.

### 3. Ledger Connect Kit ($600k+) - NPM Supply Chain Attack

- **Vector:** A former Ledger employee was phished, and the attacker used that access to publish a malicious version of [`@ledgerhq/connect-kit`](https://www.ledger.com/blog/security-incident-report) to npm.
- **Impact:** dApps that auto-loaded the compromised package could present wallet prompts that swapped a legitimate spender for an attacker-controlled contract, pushing users toward malicious approvals; Ledger's incident report and later security reporting place the initial theft at [more than $600,000](https://www.ledger.com/blog/security-incident-report) before white hats and responders intervened ([Ledger](https://www.ledger.com/blog/security-incident-report), [The Hacker News](https://thehackernews.com/2023/12/crypto-hardware-wallet-ledgers-supply.html)).
- **Lesson:** Frontend dependency trust is part of protocol security, especially when wallet libraries can shape the exact transaction a user sees and signs.

## Mitigations

- **Use deterministic dependency controls:** Pin package versions with lockfiles and review any wallet or frontend package upgrade before deployment.
- **Harden registrar and CDN access:** Registrar accounts, DNS providers, and CDN/API dashboards should use phishing-resistant MFA and tightly scoped admin rights.
- **Add transaction sanity checks in the UI:** Frontends should surface spender addresses and approval scopes clearly so malicious substitutions are easier to spot.
- **Prepare fallback delivery paths:** ENS/IPFS mirrors, emergency banners, and social incident channels help users verify when the main frontend is compromised.
