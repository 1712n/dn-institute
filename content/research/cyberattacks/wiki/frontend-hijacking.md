---
title: "Frontend Hijacking & DNS Spoofing"
description: "A detailed look at how attackers compromise the user-facing interfaces of dApps through DNS, malicious scripts, and supply chain attacks to steal funds."
---

While smart contracts are immutable, the web applications that provide a user interface to them are not. Frontend attacks represent a critical and often overlooked vulnerability vector where the entry point to a DeFi protocol is compromised, tricking users into signing malicious transactions.

## The Mechanism of Frontend Attacks

The vulnerability lies in the centralized components that most "decentralized" applications still rely on: web servers, domain name system (DNS) records, and third-party code dependencies.

*   **Compromised Scripts & Supply Chain Attacks:** Attackers inject malicious JavaScript into a dApp's frontend. This can happen by compromising a project's web server, or more insidiously, by publishing a malicious version of a widely used code library (e.g., an npm package for wallet connectivity).
*   **DNS Hijacking:** An attacker gains control of a project's DNS records (e.g., at a registrar like GoDaddy) and redirects the legitimate domain (e.g., `app.protocol.com`) to a perfect clone of the site hosted on an attacker-controlled server.
*   **Phishing Approvals:** The goal of these attacks is often to trick a user into signing an `approve` transaction. The malicious script or cloned site will prompt the user for a standard approval, but will have swapped the legitimate contract address with the attacker's address, giving them unlimited access to the user's tokens.

## Case Studies

### 1. Badger DAO ($120M) - Cloudflare API Key Exploit

*   **Vector:** An attacker gained access to a Cloudflare API key for the Badger DAO frontend. They used this to inject a script that only activated for high-value wallet addresses.
*   **Impact:** When targeted users interacted with the site, the script intercepted their approval transactions, changing the spender address to the attacker's. Over several weeks, the attacker drained funds from users who had unknowingly signed these malicious approvals.
*   **Lesson:** Web2 infrastructure security (API keys, admin panels) is as critical as smart contract security. A compromised frontend can bypass all on-chain safeguards.

### 2. Curve Finance ($570k) - DNS Cache Poisoning

*   **Vector:** The DNS records for `curve.fi` were hijacked, redirecting users to a malicious clone of the site.
*   **Impact:** The cloned site prompted users to approve a malicious contract. Although the amount stolen was relatively small for Curve, it demonstrated the fragility of relying on centralized DNS infrastructure.
*   **Lesson:** Protocols that are critical infrastructure should adopt decentralized alternatives for hosting and domain resolution, such as IPFS for hosting and ENS (Ethereum Name Service) for domains.

### 3. Ledger Connect Kit ($600k+) - NPM Supply Chain Attack

*   **Vector:** A former Ledger employee fell victim to a phishing attack, which allowed the attacker to publish a malicious version of the `@ledgerhq/connect-kit` library to the public NPM registry.
*   **Impact:** Hundreds of dApps that depended on `@ledgerhq/connect-kit` automatically loaded the compromised code. The malicious script could inject a fake wallet-connection or approval flow that replaced a legitimate spender address with an attacker-controlled contract, tricking users into signing malicious approvals and giving the attacker access to drain their tokens.
*   **Lesson:** Supply chain attacks on frontend dependencies are a systemic risk. Projects must use lockfiles (e.g., `package-lock.json`) and consider security measures like Subresource Integrity (SRI) to ensure dependencies have not been tampered with.
