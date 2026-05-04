---
title: "🌰 Badger DAO — Frontend Injection Attack and $120M Token Approval Hijack"
date: 2026-05-04
entities:
  - Badger DAO
  - BADGER
  - Cloudflare
  - Ethereum
  - Curve Finance
  - Bitcoin
  - WBTC
---

## Summary

1. **On December 2, 2021, the Badger DAO DeFi protocol lost approximately $120 million** when an attacker exploited a compromised Cloudflare Workers script to inject malicious token approval requests into the protocol's web frontend. Unlike most DeFi exploits, the Badger attack targeted the user interface layer rather than the smart contracts themselves.
2. **The attacker gained access to a Cloudflare API key** associated with Badger's web infrastructure and used it to periodically inject a malicious script into the app.badger.com frontend. This script prompted users to sign ERC-20 `approve` transactions granting the attacker's contract unlimited spending rights over the users' deposited tokens.
3. **The malicious approvals were collected over approximately two to three weeks** before the attacker began draining wallets on December 2. Because ERC-20 approvals are standard interactions that users regularly encounter in DeFi, many users signed the requests without recognizing them as abnormal.
4. **The largest single loss was approximately $50 million from a single address**, highlighting the concentration of whale-sized positions in DeFi yield vaults. The stolen assets included various wrapped Bitcoin derivatives (WBTC, byvWBTC, bcrvRenBTC, bcrvSBTC) and other Badger vault tokens.
5. **The exploit represented a new class of DeFi attack** that bypassed smart contract security entirely. The Badger contracts functioned correctly throughout — the vulnerability was in the web infrastructure serving the frontend, demonstrating that DeFi security extends far beyond on-chain code.

## Background

Badger DAO is a DeFi protocol focused on building products that bring Bitcoin into the Ethereum DeFi ecosystem. The protocol's primary offerings were yield-bearing vaults (called Setts) that accepted various wrapped Bitcoin tokens and deployed them into yield strategies across DeFi protocols like Curve Finance and Convex.

### Protocol Architecture

The components relevant to the attack:

- **Sett Vaults**: Smart contracts where users deposited wrapped Bitcoin tokens (WBTC, renBTC, ibBTC, etc.) to earn yield. Users received bTokens (e.g., byvWBTC) representing their vault shares
- **app.badger.com**: The web frontend through which users interacted with the Sett vaults — connecting wallets, approving tokens, depositing, and withdrawing
- **Cloudflare Workers**: Serverless functions running on Cloudflare's edge network that handled various frontend functionality for the Badger application
- **ERC-20 Approvals**: The standard Ethereum token mechanism where a user grants a specific contract address the right to transfer tokens on their behalf, up to a specified amount

### Key Context at Attack Time

| Parameter | Value |
|-----------|-------|
| Protocol TVL | ~$600M across all Setts |
| Primary assets | WBTC, renBTC, ibBTC, various Curve LP tokens |
| Frontend hosting | Cloudflare Workers / CDN |
| Smart contract audits | Multiple audits completed on vault contracts |
| Frontend security | Cloudflare API key management; no on-chain approval monitoring |
| User approval patterns | Users routinely approved max (unlimited) token spending for vault interactions |

The critical vulnerability was not in any smart contract but in the web infrastructure. DeFi protocols in 2021 overwhelmingly focused security resources on smart contract audits while treating frontends as a less critical component — despite the frontend being the primary interface through which users authorize token movements.

## Technical Exploit Mechanics

### Phase 1 — Cloudflare API Key Compromise

The attacker obtained a Cloudflare API key that had permission to modify Cloudflare Workers scripts associated with Badger's web application. The exact method of key compromise has not been publicly confirmed by Badger. Possible vectors include:

- Phishing or social engineering targeting Badger team members with Cloudflare access
- Credential exposure through a third-party service or supply chain compromise
- Exploitation of another vulnerability in Badger's infrastructure

With this API key, the attacker could inject arbitrary JavaScript into the Cloudflare Workers scripts that served the Badger frontend, effectively controlling what code ran in users' browsers when they visited app.badger.com.

### Phase 2 — Malicious Script Injection

The attacker injected a script into the Badger frontend that performed the following:

1. **Detected wallet connections**: When a user connected their Ethereum wallet (MetaMask, WalletConnect, etc.) to the Badger app, the injected script activated
2. **Created malicious approval transactions**: The script generated ERC-20 `approve` transaction requests that would grant the attacker's address (or the attacker's intermediary contract) unlimited spending approval over the user's tokens
3. **Presented approvals to users**: These approval requests appeared in the user's wallet interface (e.g., MetaMask popup) alongside legitimate Badger interaction prompts
4. **Intermittent injection**: According to post-mortem reports, the script was not continuously active — it was injected at intervals, likely to avoid detection by monitoring systems or team members testing the site

The approval requests targeted the most valuable tokens in users' wallets:
- WBTC and wrapped Bitcoin variants
- Curve LP tokens containing BTC-denominated assets
- Badger vault receipt tokens (bTokens)
- Other ERC-20 tokens held by Badger users

### Phase 3 — Approval Harvesting Period

The malicious script reportedly operated for approximately two to three weeks before the drain began. During this period:

- Users who interacted with the Badger frontend and signed the malicious approval requests unknowingly granted the attacker permission to transfer their tokens
- Each signed approval was stored on-chain as a standard ERC-20 allowance — the attacker's address was granted spending rights over the user's balance
- Because the approvals were on-chain, they persisted regardless of whether the malicious script was later removed from the frontend

This harvesting period was strategically valuable because:
- It allowed the attacker to accumulate approvals from many high-value addresses
- Individual approvals did not trigger any funds movement, so there was no on-chain signal of the attack during this phase
- The attacker could choose the optimal moment to drain all compromised addresses simultaneously

### Phase 4 — Wallet Drain Execution

On December 2, 2021, the attacker began executing `transferFrom` calls against addresses that had signed the malicious approvals:

1. For each compromised address, the attacker's contract called `transferFrom` on the approved tokens, transferring the full approved amount to attacker-controlled addresses
2. The drain was executed rapidly across many addresses
3. Badger's monitoring systems detected the mass unauthorized transfers and the team paused the vault contracts within minutes — but by that point, the attacker had already drained the approved tokens from most compromised addresses

### Why Standard DeFi Security Did Not Prevent This

1. **Smart contracts were not vulnerable**: The Sett vault contracts, token contracts, and governance contracts all functioned exactly as designed. No on-chain exploit was used.
2. **Approvals are user-authorized**: From the blockchain's perspective, the victims voluntarily signed the approval transactions. The `approve` function does not know or care why the user is granting approval — it simply records the allowance.
3. **No on-chain approval monitoring**: There was no automated system checking whether approval requests initiated by the frontend matched expected patterns (e.g., approvals to unknown contracts, approvals with unlimited amounts).
4. **User habituation**: DeFi users routinely approve unlimited spending for protocol contracts when depositing into vaults. A malicious approval request looks identical to a legitimate one in a wallet popup — both display a contract address and an amount.

## Stolen Assets Breakdown

### By Token Type

| Token | Approximate Loss |
|-------|-----------------|
| Various WBTC vault tokens (byvWBTC, bcrvRenBTC, bcrvSBTC, etc.) | ~$100M |
| WBTC (direct) | ~$10M |
| Other ERC-20 tokens | ~$10M |
| **Total** | **~$120M** |

### Concentration of Losses

The losses were heavily concentrated among a small number of large depositors:
- The single largest individual loss was approximately $50 million from one address
- The top 5 affected addresses accounted for a significant majority of total losses
- Many smaller addresses had approved the malicious contract but held relatively small balances

This concentration reflects the broader distribution of DeFi capital, where a small number of "whale" addresses hold a disproportionate share of deposited assets.

## Post-Exploit Response

### Badger DAO Response

- **December 2 (day of attack)**: Badger paused all vault contracts, preventing further deposits and withdrawals. Published initial alert on Twitter.
- **December 2-4**: Badger worked with Chainalysis and other security firms to trace stolen funds and identify affected addresses.
- **December 9**: Badger published an initial post-mortem confirming the Cloudflare API key compromise as the attack vector.
- **December 2021 - January 2022**: Badger governance proposed and approved a recovery plan to partially compensate affected users using the DAO treasury.
- **Recovery plan**: The DAO allocated a portion of its treasury (BADGER tokens and other assets) to a restitution fund. The plan prioritized smaller depositors and aimed to make affected users partially whole over time through a combination of immediate distribution and vesting schedules.

### Law Enforcement

- Badger worked with law enforcement agencies and blockchain analytics firms
- Some stolen funds were reportedly traced to centralized exchanges
- No public arrests or charges have been announced in connection with the exploit as of the article date

### Fund Recovery

Unlike the Poly Network exploit (where the attacker returned funds), the Badger attacker did not return the stolen assets. The funds were moved through various DeFi protocols and some were reportedly bridged to other chains or mixed through privacy-enhancing services.

## Vulnerability Pattern: Frontend as Attack Surface

### Why Frontend Attacks Are Underappreciated in DeFi

The Badger exploit exposed a blind spot in DeFi security thinking:

1. **Audit culture focuses on contracts**: The DeFi security industry (auditors, bug bounties, formal verification) is overwhelmingly focused on smart contract code. Frontend code, infrastructure configuration, and operational security receive comparatively little attention.

2. **Frontends are centralized**: Even protocols with fully decentralized on-chain contracts typically serve their frontends through centralized web infrastructure (Cloudflare, AWS, Vercel, etc.). This creates a single point of compromise that can affect all users.

3. **The approval mechanism is dangerous by design**: ERC-20 `approve` grants the approved address permanent spending rights up to the approved amount. Most DeFi frontends request unlimited approvals for convenience, training users to sign large approval transactions routinely.

4. **Users cannot distinguish malicious from legitimate approvals**: A MetaMask popup showing "Approve [contract address] to spend your WBTC" looks the same whether the contract is a legitimate vault or an attacker-controlled drainer. The user would need to independently verify the contract address against the protocol's deployed contracts — something few users do.

### Similar Frontend/Infrastructure Attacks

| Protocol | Date | Method | Loss |
|----------|------|--------|------|
| Badger DAO | Dec 2021 | Cloudflare Workers script injection | ~$120M |
| Curve Finance | Aug 2022 | DNS hijacking (frontend redirected to phishing site) | ~$570K |
| Celer Bridge | Aug 2022 | DNS hijacking (frontend served malicious contract) | ~$240K |
| Convex Finance | Jun 2022 | Reported frontend vulnerability (patched before exploit) | $0 (prevented) |
| KyberSwap | Sep 2022 | Google Tag Manager compromise (malicious script injected) | ~$265K |

The pattern is consistent: attackers compromise web infrastructure (DNS, CDN, analytics scripts) to modify the frontend that DeFi users interact with, then harvest approvals or redirect transactions.

## Market Impact

### BADGER Token

The BADGER governance token declined sharply following the exploit disclosure:
- Pre-exploit price: approximately $22-24
- Post-exploit (48h): approximately $16-18 (roughly 25-30% decline)
- The price continued to decline over the following weeks as the full scope of the exploit became clear and confidence in the protocol eroded

### Protocol TVL

- Pre-exploit TVL: approximately $600M
- Post-exploit TVL: dropped to approximately $200-250M within days as users withdrew from non-compromised vaults
- The TVL never recovered to pre-exploit levels

### Broader Industry Impact

- **Frontend security awareness**: The exploit was a catalyst for the DeFi industry to take frontend and infrastructure security more seriously
- **Approval management tools**: Tools like Revoke.cash and similar services saw increased adoption as users became more aware of outstanding token approvals
- **Infrastructure diversification**: Some protocols began exploring IPFS-hosted frontends, on-chain frontend verification, and other approaches to reduce single-point-of-failure risk in web serving infrastructure
- **Monitoring for abnormal approvals**: Security firms developed monitoring tools to detect when a protocol's frontend begins requesting approvals to unfamiliar contract addresses

## Lessons for Market Surveillance

1. **Monitor approval patterns, not just transfers**: Traditional blockchain surveillance focuses on token transfers. The Badger attack was invisible on-chain until the drain phase because the harvesting phase only involved approval transactions. Surveillance systems should flag unusual patterns in ERC-20 approvals — such as many users of a single protocol approving the same unfamiliar contract address within a short time window.

2. **Frontend infrastructure as a risk vector**: When assessing protocol risk, the security of the web infrastructure (hosting provider, CDN, DNS, third-party scripts) should be evaluated alongside smart contract security. A protocol with audited contracts but centralized, poorly-secured frontend infrastructure has a different risk profile than one with decentralized frontend serving.

3. **Whale concentration amplifies exploit impact**: The $50M single-address loss illustrates that whale concentration in DeFi vaults creates outsized tail risk. Surveillance systems should track concentration metrics for major protocols — a vault where 5 addresses hold 80% of TVL is more vulnerable to targeted approval attacks than one with dispersed depositors.

4. **Approval revocation as a mitigation signal**: After a suspected frontend compromise, the rate of approval revocations can signal the community's awareness and response speed. Monitoring for spikes in `approve(address, 0)` calls can indicate that users are responding to a suspected attack.

5. **DNS and CDN change monitoring**: Real-time monitoring of DNS records and CDN configurations for major DeFi frontends can provide early warning of infrastructure compromise. Changes to Cloudflare Workers, DNS providers, or CDN origins outside of normal deployment patterns should trigger alerts.

6. **Cross-protocol approval correlation**: If multiple protocols sharing the same infrastructure provider begin requesting approvals to the same unfamiliar address, this suggests a supply-chain attack rather than a single-protocol incident. Cross-protocol correlation of approval targets adds detection power.

## References

1. Badger DAO. "Badger Exploit Technical Post Mortem." Badger Finance Blog, December 9, 2021.
2. Rekt News. "Badger — REKT." rekt.news, December 2, 2021.
3. PeckShield. "@paborPeck: Badger DAO Hack Analysis." Twitter, December 2, 2021.
4. Chainalysis. "The 2022 Crypto Crime Report." Chapter: DeFi Exploits. Chainalysis Inc., February 2022.
5. Immunefi. "Hack Analysis: Badger DAO, $120M Lost." Immunefi Blog, 2022.
6. Trail of Bits. "Are You Really Decentralized? Frontend Risks in DeFi." Trail of Bits Blog, 2022.
