---
title: "Euler Finance: $197M Flash Loan Exploit via donateToReserves Missing Health Check, Full Fund Recovery After Attacker Apology, and $4.5M Audit Insurer Payout"
date: 2026-02-12
entities:
  - Euler Finance
  - Angle Protocol
  - Balancer
  - Sherlock
---

## Summary

1. **$197 million drained via flash loan exploit — largest DeFi hack of 2023**: On March 13, 2023, an attacker exploited a missing liquidity check in Euler Finance's `donateToReserves` function to drain approximately $197 million in stETH ($134.6M), USDC ($34.1M), wBTC ($18.6M), and DAI ($8.8M) from the permissionless lending protocol on Ethereum.
2. **Vulnerability introduced by a bug fix**: The exploited `donateToReserves` function was added via eIP-14 in July 2022 as a fix for a "first depositor" bug discovered by whitehat Kankodu — the fix itself introduced the critical missing `checkLiquidity()` call that enabled the $197 million exploit eight months later.
3. **Full recovery of $240 million after attacker's apology**: The attacker, identifying themselves only as "Jacob," returned all stolen funds over 23 days (March 18 – April 3, 2023) after sending an on-chain message reading "I f**ked up. I didn't mean for any of this to happen" — with the recovered amount exceeding the stolen amount due to ETH price appreciation during negotiations.
4. **$37.6 million cascading losses across 11 DeFi protocols**: Euler's composability meant the exploit cascaded to downstream protocols including Angle Protocol ($17.6M), Balancer ($11.9M), Temple DAO ($5M), and SwissBorg ($4.3M), demonstrating systemic risk in DeFi lending integrations.
5. **10 audits in 2 years failed to catch the bug — Sherlock paid $4.5M insurance claim**: Despite audits by Halborn, Solidified, ZK Labs, Certora, Omniscia, and Sherlock, the missing health check survived in production for eight months — Sherlock, which had audited the eIP-14 code containing the vulnerability, accepted responsibility and paid a $4.5 million insurance claim, the largest audit-insurer payout in DeFi history at the time.

## Background

### Euler Finance Overview

**Euler Finance** was a permissionless, non-custodial lending and borrowing protocol on Ethereum. Unlike Aave or Compound, Euler allowed any ERC-20 token to be listed as a lending market without governance approval. The protocol used a tiered asset classification system (isolation tier, cross tier, collateral tier) to manage risk [1].

Before the exploit, Euler had accumulated significant TVL across its lending markets, with integrations in multiple downstream DeFi protocols.

### The donateToReserves Vulnerability

In **July 2022**, whitehat hacker **Kankodu** discovered a "first depositor" vulnerability in Euler through the protocol's bug bounty program on **Immunefi**, earning a **$50,000 bounty**. The fix, implemented via **eIP-14**, required adding a `donateToReserves` function to the `EToken` contract to allow governance to increase minimum reserves for existing eToken markets [2].

**The critical flaw**: The new `donateToReserves` function burned eTokens (collateral) from the caller's position but **did not include a `checkLiquidity()` call** afterward. This meant a user could destroy their own collateral — making their position insolvent — without the protocol detecting or preventing it.

**Second vulnerability**: A flaw in the liquidation health score calculation allowed insolvent accounts to receive collateral through self-liquidation without fully repaying outstanding debt, enabling profit extraction from the artificially underwater position.

## The Exploit (March 13, 2023)

### Attack Mechanism

The attacker deployed exploit contracts funded via **Tornado Cash** and executed the following pattern across multiple token markets (DAI, USDC, wBTC, stETH) [3]:

**Step 1 — Flash Loan**: Borrowed **30 million DAI** from Aave.

**Step 2 — Deposit**: Deposited 20 million DAI into Euler, receiving approximately 19.6 million eDAI.

**Step 3 — Leveraged Self-Borrowing**: Used eDAI as collateral to mint approximately 195.6 million eDAI and 200 million dDAI (debt tokens) through repeated self-borrowing.

**Step 4 — Donate to Destroy Collateral**: Called `donateToReserves` to donate 100 million eDAI to Euler's reserves. Because this function had **no health check**, the attacker destroyed their own collateral without being stopped, making their position deeply underwater.

**Step 5 — Self-Liquidation**: Liquidated their own underwater position using a second contract. Due to the inflated liquidation discount on the unhealthy position, the liquidator received collateral worth more than the debt repaid.

**Step 6 — Extract Profit**: Repaid the 30M DAI flash loan (~27,000 DAI interest) and kept approximately **8.88 million DAI** profit per attack cycle.

**Step 7 — Repeat**: Replicated this pattern across DAI, USDC, wBTC, and stETH markets.

### Stolen Amounts

| Asset | Amount | USD Value |
|-------|--------|-----------|
| Staked ETH (stETH) | ~86,000 stETH | ~$134.6M |
| USDC | 34,000,000 USDC | $34.1M |
| Wrapped Bitcoin (wBTC) | ~849 wBTC | ~$18.6M |
| DAI | ~8,877,507 DAI | ~$8.8M |
| **Total** | | **~$197M** |

### On-Chain Addresses

| Label | Address |
|-------|---------|
| Exploiter Primary Wallet | `0xb66cd966670d962c227b3eaba30a872dbfb995db` |
| Exploiter Address 1 | `0xb2698c2d99ad2c302a95a8db26b08d17a77cedd4` |
| Exploit Contract | `0xebc29199c817dc47ba12e3f86102564d640cbf99` |

Example exploit transaction (DAI market): `0xc310a0affe2169d1f6feec1c63dbc7f7c62a887fa48795d327d4d2da2d6b111d` [4].

## Cascading Losses Across DeFi

The exploit caused approximately **$37.6 million** in additional losses across downstream protocols that had deposited funds into Euler [5]:

| Protocol | Exposure/Loss | Details |
|----------|---------------|---------|
| Angle Protocol | ~$17.6M | Nearly half of Angle's total TVL; USDC deposits locked |
| Balancer | ~$11.9M | Euler Boosted USD (bb-e-USD) pool drained; >65% of pool TVL lost |
| Temple DAO | ~$5M | Funds locked in Euler |
| Idle DAO | ~$5M | Tranches exposed to Euler |
| SwissBorg | ~$4.3M | $2.6M in ETH + $1.7M USDT |
| Yield Protocol | ~$1.5M | Funds deposited in Euler |
| Yearn Finance | ~$1.38M | Indirect exposure; losses covered by Yearn Treasury |
| Inverse Finance | ~$800K | Funds locked in Euler |

Additional affected protocols included Swivel Finance and Sense Finance.

## Recovery: The "Jacob" Negotiations

### Initial Response (March 13–14)

Euler disabled the vulnerable EToken module immediately. On **March 14, 2023**, Euler sent an on-chain message offering the attacker a **10% bounty (~$20M)** to return 90% of funds within 24 hours, and simultaneously announced a **$1 million reward** for information leading to the attacker's arrest [6].

### Lazarus Group False Flag (March 17)

On March 17, the attacker sent **100 ETH** to `0x098b716b8aaf21512996dc57eb0615e2383e2f96` — the Ronin Bridge Exploiter address attributed by OFAC to North Korea's **Lazarus Group**. Blockchain security experts assessed this as likely a **false flag** to muddy attribution. The Lazarus Group subsequently attempted to **phish the Euler attacker** by sending a malicious decryption tool — which Euler's team warned the attacker about [7].

### Fund Returns (March 18 – April 3)

| Date | Amount Returned |
|------|----------------|
| March 18 | 3,000 ETH (~$5.3M) |
| March 25 | 51,000 ETH (~$90M) |
| March 25–28 | Cumulative 84,951 ETH ($147.8M) + $29.9M DAI |
| April 3 | Final batch: 10,580 ETH (~$19M) + $12M DAI |
| **Total Recovered** | **~$240M** (exceeded stolen amount due to ETH appreciation) |

### The Apology

On **March 28, 2023**, the attacker sent an on-chain message:

> *"Jacob here. I f\*\*ked up. I didn't mean for any of this to happen... I only look after my safety, and that is the reason for the delay. I'm sorry for any misunderstanding."*

The attacker communicated via email addresses including `inta_chez@xyzmailhub.com` and `x@proton.me`, signing as "Jacob" (not their real name). Euler CEO **Michael Bentley** engaged in direct personal communication with the attacker [8].

### Why Funds Were Returned

Multiple converging pressures led to full recovery:
- **$1 million bounty** for arrest information
- **Law enforcement engagement** in the United States and United Kingdom
- **Chainalysis** and **TRM Labs** retained for blockchain forensics
- Strategic communication blackouts to increase attacker's uncertainty
- Euler's assessment that the attacker **lacked experience of a professional hacking group**

After all recoverable funds were returned on **April 4, 2023**, Euler cancelled the $1M bounty.

## Audit History

The vulnerability survived **10 audits in 2 years** by six independent firms [9]:

| Audit Firm | Period | Notes |
|------------|--------|-------|
| Halborn | May 2021 onward | Multiple audits |
| Solidified | 2021–2022 | Multiple audits |
| ZK Labs | 2021–2022 | Multiple audits |
| Certora | 2022 | Formal verification |
| **Sherlock** | **July 2022** | **Audited eIP-14 code including donateToReserves — missed the vulnerability** |
| Omniscia | Multiple | eIP-14 was not in scope of any Omniscia audit |

### Sherlock's $4.5M Insurance Payout

**Sherlock** accepted responsibility for missing the vulnerability and paid a **$4.5 million insurance claim** to Euler ($3.3M paid on March 14, 2023). This left Sherlock with only **$2.9 million** in reserves — the first time an audit insurer paid this magnitude for a missed vulnerability [10].

**Nexus Mutual** separately paid approximately **$2.4 million** in insurance claims to covered Euler depositors. After funds were recovered, Nexus Mutual demanded refunds; 8 of 9 claimants agreed to return payments.

## Market Impact

- **EUL token**: Dropped **45–70%**, falling to approximately $2.07 at its lowest (from ~$5–6 pre-hack)
- The exploit occurred during the **Silicon Valley Bank collapse** (March 9–10), compounding market stress
- The hack was the **largest DeFi exploit of 2023**
- Demonstrated systemic risk in DeFi composability — a single protocol failure cascaded to at least 11 other protocols

## Timeline

| Date | Event |
|------|-------|
| July 2022 | Kankodu reports "first depositor" bug via Immunefi ($50K bounty); fix introduces `donateToReserves` via eIP-14; Sherlock audits the new code |
| March 13, 2023 ~08:50 UTC | Exploit executed: ~$197M drained across stETH, USDC, wBTC, DAI markets |
| March 14, 2023 | Euler offers 10% bounty; announces $1M arrest reward; Sherlock pays $3.3M insurance claim |
| March 17, 2023 | 100 ETH sent to Lazarus-linked address (assessed as false flag) |
| March 18, 2023 | First return: 3,000 ETH (~$5.3M) |
| March 25, 2023 | Major return: 51,000 ETH (~$90M) |
| March 28, 2023 | Attacker sends on-chain apology: "I f**ked up" |
| April 3, 2023 | Final batch returned; total recovered ~$240M |
| April 4, 2023 | Euler announces all recoverable funds returned |

## Market Manipulation Implications

The Euler Finance exploit reveals critical vulnerabilities in DeFi lending protocol security:

1. **Bug-fix-as-vulnerability vector**: The exploited function was introduced as a security fix for a different bug — demonstrating that remediation code itself can introduce new critical vulnerabilities, particularly when it bypasses existing safety checks like health factor validation
2. **Flash loan amplification of protocol bugs**: The exploit required zero upfront capital — the attacker borrowed $30M from Aave, exploited Euler, and returned the loan in a single transaction, demonstrating that any protocol vulnerability accessible via flash loans faces effectively unlimited attack capital
3. **DeFi composability as systemic risk amplifier**: The cascading $37.6M in losses across 11 downstream protocols demonstrates that DeFi lending integrations create correlated failure modes — a single protocol exploit can simultaneously impact all protocols with deposits or integrations
4. **Audit saturation without security guarantee**: Ten audits by six firms over two years — including an audit of the exact vulnerable code — failed to catch a missing function call, demonstrating that audit quantity does not guarantee security and that audit-based risk assessments may provide false assurance

## Relevance to Market Health Metrics

Euler Finance's case demonstrates several indicators in the DN Institute [Market Health Metrics](https://dn.institute/research/market-health/docs/market-health-metrics/) framework:

- **Downstream exposure mapping**: The cascading losses across Angle Protocol, Balancer, Temple DAO, and others demonstrate that protocol-level health metrics must account for downstream integration exposure — a protocol's risk is not isolated but propagates through every protocol holding its deposit tokens
- **Audit coverage gap analysis**: The discrepancy between "10 audits completed" and "critical vulnerability in production for 8 months" demonstrates that raw audit count is insufficient as a health metric — the specific scope coverage, including which code changes were audited and which were excluded, provides a more meaningful indicator
- **Recovery speed as protocol quality metric**: Euler's successful full recovery — achieved through professional incident response, law enforcement engagement, and strategic negotiation — demonstrates that post-exploit recovery capability is a measurable differentiator in protocol health assessment
- **Insurance fund adequacy**: Sherlock's $4.5M payout that left it with only $2.9M in reserves reveals that DeFi insurance protocols face concentration risk — their ability to cover claims after a major exploit provides a real-time indicator of ecosystem insurance adequacy

## References

1. Euler Finance, "War & Peace: Behind the Scenes of Euler's $240M Exploit & Recovery." [euler.finance](https://www.euler.finance/blog/war-peace-behind-the-scenes-of-eulers-240m-exploit-recovery)
2. The Block, "Whitehat Claims Bug Fix Led to the $200M Attack." [theblock.co](https://www.theblock.co/post/249413/euler-finance-whitehat-unknowingly-caused-200-million-hack)
3. Cyfrin, "Deep Dive: How Did the Euler Finance Hack Happen?" [cyfrin.io](https://www.cyfrin.io/blog/how-did-the-euler-finance-hack-happen-hack-analysis)
4. Chainalysis, "Euler Finance Flash Loan Attack Explained." [chainalysis.com](https://www.chainalysis.com/blog/euler-finance-flash-loan-attack/)
5. Cointelegraph, "Euler attack causes locked tokens, losses in 11 DeFi protocols including Balancer." [cointelegraph.com](https://cointelegraph.com/news/euler-attack-causes-locked-tokens-losses-in-11-defi-protocols-including-balancer)
6. CoinDesk, "Euler Says All Recoverable Funds Stolen in $200M Hack Have Been Returned," April 2023. [coindesk.com](https://www.coindesk.com/business/2023/04/03/euler-says-all-recoverable-funds-stolen-in-200m-hack-have-been-returned)
7. CoinDesk, "Hacker vs. Hacker: North Koreans Attempt to Phish Euler Exploiter," March 2023. [coindesk.com](https://www.coindesk.com/business/2023/03/21/hacker-vs-hacker-north-koreans-attempt-to-phish-euler-exploiter-of-200m-in-crypto-experts-say/)
8. CoinDesk, "Hacker Behind $200M Euler Attack Apologizes, Returns Millions in Ether, DAI," March 2023. [coindesk.com](https://www.coindesk.com/tech/2023/03/28/hacker-behind-200m-euler-attack-apologizes-returns-millions-in-ether-dai-to-protocol/)
9. Cointelegraph, "Euler Finance hacked despite 10 audits in 2 years, says CEO." [cointelegraph.com](https://cointelegraph.com/news/euler-finance-hacked-despite-10-audits-in-2-years-says-ceo)
10. DL News, "Sherlock DeFi insurer on edge after Euler hack payout." [dlnews.com](https://www.dlnews.com/articles/defi/sherlock-defi-insurer-on-edge-euler-hack/)
