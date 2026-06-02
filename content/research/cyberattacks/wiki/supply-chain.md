---
title: Supply-Chain Attacks Against Crypto Developer Tooling
bookToc: true
---

Software supply-chain attacks have become a practical way to target crypto wallets, CI/CD pipelines, and developer credentials without touching a protocol's on-chain logic. The two cases below show different parts of the same problem: one campaign abused public troubleshooting around a Python wallet library, while another used malicious npm packages to steal credentials and spread further through compromised maintainer accounts.

## 1. Python typosquatting against `bitcoinlib` users

In late March 2025, researchers and `bitcoinlib` contributors documented malicious PyPI packages named [`bitcoinlibdbfix`](https://secure.software/pypi/packages/bitcoinlibdbfix) and [`bitcoinlib-dev`](https://secure.software/pypi/packages/bitcoinlib-dev). The package names referenced a real support thread in the upstream project: [bitcoinlib issue #455](https://github.com/1200wd/bitcoinlib/issues/455), where users were discussing database-related errors in the `clw` wallet CLI.

### How the attack worked

- The attacker published packages whose names looked like legitimate fixes for the issue discussed in public.
- In the same GitHub issue, a contributor warned that `bitcoinlibdbfix` would [overwrite the `clw` command and exfiltrate the database file](https://github.com/1200wd/bitcoinlib/issues/455#issuecomment-2765791597).
- Another participant in the thread confirmed they had [checked the source code and saw the same behavior](https://github.com/1200wd/bitcoinlib/issues/455#issuecomment-2765816420).
- ReversingLabs reported that both packages attempted a similar attack by replacing the legitimate `clw` CLI with malicious code and stealing sensitive database material from affected systems.

### Why this case matters

- The attack did **not** require compromising the legitimate `bitcoinlib` package.
- It exploited a real maintenance discussion and plausible package names instead of a direct exploit in wallet code.
- Publicly available evidence supports claims about `clw` replacement and database exfiltration; stronger claims about second-stage payloads or broader filesystem theft are harder to verify now that the packages have been removed from PyPI.

## 2. The `Shai-Hulud` npm worm

A separate 2025 campaign showed how a supply-chain attack can become self-propagating once developer credentials are captured. In September 2025, [CISA warned](https://www.cisa.gov/news-events/alerts/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem) that a worm publicly known as `Shai-Hulud` had compromised more than 500 npm packages.

### Documented behavior

According to CISA, the malware:

- scanned infected environments for sensitive credentials,
- targeted GitHub personal access tokens and cloud API keys,
- exfiltrated harvested credentials,
- uploaded stolen credentials to a public GitHub repository via the [`/user/repos` API](https://docs.github.com/en/rest/repos/repos#create-a-repository-for-the-authenticated-user), and
- authenticated to npm as the compromised developer, injected malicious code into other packages, and published new infected versions.

### Why this case matters

- The attack moved from credential theft to automated propagation.
- Maintainer account compromise turned trusted package publishers into distribution points.
- The blast radius extended beyond one package: every downstream project that resolved an infected version became a potential new entry point.

## 3. Common lessons from both cases

- **Developer workflows are part of the attack surface.** Public issue threads, package managers, and local CLI tools can be abused even when smart contracts are untouched.
- **Name trust is fragile.** Attackers only needed package names that looked plausible in context.
- **Credential hygiene matters as much as code review.** Once tokens are stolen, package publishing and repository write access can become propagation mechanisms.
- **Concrete mitigations reduce risk:**
  - **Lockfiles and version pinning** prevent automatic installation of malicious package updates.
  - **Scoped publishing controls** limit which maintainers can publish to specific package namespaces.
  - **Phishing-resistant MFA** protects maintainer accounts from credential theft.
  - **Stricter CI/CD secret handling** limits credential exposure in build environments.

## References

- [ReversingLabs: Malicious Python packages target popular Bitcoin library](https://www.reversinglabs.com/blog/malicious-python-packages-target-popular-bitcoin-library)
- [bitcoinlib issue #455](https://github.com/1200wd/bitcoinlib/issues/455)
- [Secure Software / ReversingLabs package analysis: bitcoinlibdbfix](https://secure.software/pypi/packages/bitcoinlibdbfix)
- [Secure Software / ReversingLabs package analysis: bitcoinlib-dev](https://secure.software/pypi/packages/bitcoinlib-dev)
- [CISA: Widespread Supply Chain Compromise Impacting npm Ecosystem](https://www.cisa.gov/news-events/alerts/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem)
