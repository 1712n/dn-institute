---
title: "Cetus Protocol: $223M Sui DEX Exploit via Arithmetic Overflow, Validator-Coordinated Fund Freeze, and Decentralization Debate"
date: 2026-02-12
entities:
  - Cetus Protocol
  - Sui Network
---

## Summary

1. **$223 million drained in under 15 minutes**: On May 22, 2025, an attacker exploited an arithmetic overflow vulnerability in Cetus Protocol's `checked_shlw` function to mint massive liquidity positions for 1 token each, draining approximately $223 million from the largest DEX on the Sui blockchain — the largest DeFi exploit of 2025.
2. **Flawed overflow mask in third-party library**: The vulnerability resided in the `integer-mate` math library's `checked_shlw` function, which used an incorrect overflow threshold (`0xFFFFFFFFFFFFFFFF << 192` instead of `0x1 << 192`), allowing values that would overflow when left-shifted by 64 bits to pass the safety check — exploiting the fact that Move's bit shift operations silently truncate rather than abort on overflow.
3. **$162 million frozen by validator intervention**: Sui validators coordinated to reject all transactions from the attacker's addresses, freezing approximately $162 million before it could be bridged off-chain — while $60 million in USDC was successfully bridged to Ethereum via Wormhole and Circle's CCTP at a rate of $1 million every 30 seconds.
4. **90.9% validator vote approved fund recovery**: On May 29, 2025, a governance vote concluded with 90.9% of Sui validators voting to implement a protocol-level recovery of the frozen $162 million — effectively a hard fork to return stolen funds, sparking fierce debate about blockchain decentralization.
5. **Four audits missed the bug**: The `checked_shlw` vulnerability survived four separate security audits (OtterSec on Aptos, OtterSec on Sui, MoveBit, and Zellic in April 2025) — with the Zellic audit completing just 41 days before the exploit, though the `integer-mate` library was not in its audit scope.

## Background

### Cetus Protocol and the Sui Ecosystem

**Cetus Protocol** was the largest decentralized exchange (DEX) and concentrated liquidity market maker (CLMM) on the **Sui blockchain**. The protocol offered aggregated trading, concentrated liquidity market making, token issuance, and other DeFi tools. Before the hack, Cetus had approximately **$285–300 million in total value locked (TVL)**, making it the dominant DeFi protocol in the Sui ecosystem [1].

### The Vulnerability: `checked_shlw` in integer-mate

Cetus used the **`integer-mate`** library, a third-party math library for u256 fixed-point arithmetic operations. The critical function `checked_shlw` was designed to safely determine whether a 256-bit value could be left-shifted by 64 bits (one "word") without overflowing [2].

**The flawed mask:**
- **Incorrect threshold used**: `0xFFFFFFFFFFFFFFFF << 192` (equivalent to `2^256 - 2^192`)
- **Correct threshold should have been**: `0x1 << 192` (i.e., `2^192`)

The value `2^192` is the smallest value that cannot be safely shifted left by 64 bits without overflowing a u256. The mask actually used was vastly larger, meaning values between `2^192` and `2^256 - 2^192` would **incorrectly pass the overflow check** even though shifting them would cause silent truncation.

**Why Move's safety didn't help**: The Move programming language provides built-in overflow protection for addition, subtraction, and multiplication — these operations abort on overflow. However, **bit shift operations (`<<`) intentionally do not abort on overflow in Move** — they silently truncate the high bits. This is precisely why `checked_shlw` was needed as a manual safeguard, and why its flawed implementation was catastrophic.

### The Affected Function: `get_delta_a`

The overflow bug corrupted the `get_delta_a` function, which calculates how many tokens a user must deposit to receive a given amount of liquidity. When the attacker passed a carefully crafted liquidity parameter (~2^113), the multiplication produced a result of approximately `2^192 + epsilon`. Left-shifting by 64 bits caused it to **wrap around to epsilon** (a tiny value), and the function returned that only **1 token** was needed to mint an enormous liquidity position [3].

## The Exploit (May 22, 2025)

### Preparation

The attacker had prepared two days prior (~May 20, 2025), funding a wallet with gas fees and attempting an earlier version of the exploit that failed [4].

### Attack Execution (~10:30 UTC)

The attacker used a repeatable pattern across multiple Cetus liquidity pools:

**Step 1 — Flash Loan**: Initiated a flash swap to borrow **10+ million haSUI** without upfront capital.

**Step 2 — Price Manipulation**: Swapped borrowed tokens to crash the pool price by ~99.9%.

**Step 3 — Narrow Tick Range Position**: Created liquidity positions in extremely narrow tick ranges at the upper bounds of the price curve.

**Step 4 — Overflow Exploitation**: Called `add_liquidity` with the crafted liquidity parameter (~2^113) designed to trigger the `checked_shlw` overflow. The flawed check allowed the value to pass, the shift silently truncated, and the protocol calculated that only **1 token** was needed.

**Step 5 — Deposit 1 Token, Receive Massive Liquidity**: Deposited 1 token and was credited with trillions of units of liquidity.

**Step 6 — Withdraw Real Reserves**: Called `remove_liquidity` to extract real tokens (SUI, USDC, LBTC, haSUI, and others) against the inflated position.

**Step 7 — Repeat Across Pools**: Replicated this pattern across multiple pools to compound total theft to ~$223 million.

The entire attack was executed in **under 15 minutes**.

### Stolen Amounts and Fund Movement

| Destination | Amount | Status |
|-------------|--------|--------|
| Bridged to Ethereum (USDC via Wormhole/Circle CCTP) | ~$60–62 million | Successfully extracted |
| Frozen on Sui (validator intervention) | ~$162 million | Recovered |
| **Total** | **~$223 million** | |

The attacker bridged funds at approximately **$1 million USDC every 30 seconds** using Wormhole, Circle's Cross-Chain Transfer Protocol, Sui Bridge, and Mayan before validators intervened.

**Ethereum receiving address**: `0x89012a55cd6b88e407c9d4ae9b3425f55924919b` — received 40.88 million USDC, 8,130 ETH, 3,000 USDT, and 1,771 SOL [5].

## Sui Validator Intervention

### Emergency Freeze

In coordination with the Sui Foundation, Sui's **114 validators** updated a configuration file in their node software to **reject all transactions from the attacker's wallet addresses**. The Sui Foundation described this as a "consensus-based emergency measure" [6].

### Governance Vote (May 29, 2025)

A formal on-chain governance vote concluded on **May 29, 2025**:

| Vote | Percentage |
|------|-----------|
| **Yes** (approve fund recovery) | **90.9%** |
| Abstained | 1.5% |
| Did not participate | 7.2% |

The vote authorized a protocol-level recovery of the frozen $162 million — effectively a hard fork to return stolen funds to affected users.

### Decentralization Debate

The validator freeze ignited one of the fiercest decentralization debates in crypto during 2025 [7]:

**Critics:**
- **Justin Bons** (Cyber Capital): Accused Sui founders of controlling 84% of staked tokens, undermining decentralization claims
- **Marc Zeller** (Aave Governance Lead): Stated that centralized powers would deter DeFi protocols, writing: *"You can be sure Aave will never deploy on Sui"*
- General criticism framed the intervention as a "slippery slope" — if validators can freeze funds after a third-party application exploit, they can freeze funds for any reason

**Supporters:**
- Drew parallels to **Ethereum's 2016 DAO hack response**
- Pointed to the 90.9% validator approval as democratic legitimacy
- Argued that protecting users in emergencies is a legitimate function of validator coordination

## Recovery and Relaunch

### Compensation Sources

| Source | Amount |
|--------|--------|
| Frozen assets (validator recovery) | ~$162 million |
| Sui Foundation loan | $30 million USDC |
| Cetus treasury (cash reserves) | ~$7 million |
| CETUS token allocation (15% of supply) | 5% immediate + 10% over 12 months |

Liquidity recovery rates per pool ranged between **85% and 99%** [8].

### Platform Relaunch (June 8, 2025)

Cetus Protocol officially relaunched on **June 8, 2025, at 3:00 UTC** — 17 days after the exploit. TVL recovered to approximately **$120 million** (~50% of pre-hack peak).

## Audit History

The vulnerability survived four separate security audits, raising serious questions about audit effectiveness [9]:

| Auditor | Chain | Date | Findings | `integer-mate` in scope? |
|---------|-------|------|----------|--------------------------|
| OtterSec | Aptos | Early 2023 | Flagged similar overflow; recommended `checked_shlw` | Fix implemented, but fix had the mask bug |
| MoveBit | Sui | 2023 | 18 issues (1 critical, 2 major) | Did not catch `checked_shlw` flaw |
| OtterSec | Sui | 2023 | 1 high-risk issue | Missed library-level mask error |
| **Zellic** | Sui | **April 11, 2025** | Informational only | **Not in scope** |

The Zellic audit completed just **41 days before the hack** — but the `integer-mate` library containing the vulnerability was explicitly excluded from the audit scope.

## Market Impact

- **CETUS token**: Dropped over **40%**
- **SUI token**: Dropped approximately **15%** to $3.81
- Some Sui-based tokens fell by up to **99%**
- Sui DeFi TVL decreased by **$210 million** across the ecosystem

## Timeline

| Date | Event |
|------|-------|
| Early 2023 | OtterSec audits Cetus on Aptos; flags overflow risk; `checked_shlw` implemented with flawed mask |
| April 11, 2025 | Zellic audit completes; `integer-mate` library not in scope |
| ~May 20, 2025 | Attacker funds wallet; attempts first (failed) exploit |
| May 22, 2025 ~10:30 UTC | Exploit begins; ~$223M drained in under 15 minutes |
| May 22, 2025 (minutes later) | Attacker bridges ~$60M to Ethereum; Sui validators freeze remaining ~$162M |
| May 29, 2025 | Validator governance vote: 90.9% approve fund recovery |
| June 8, 2025 | Cetus Protocol relaunches with 85–99% liquidity recovery |

## Market Manipulation Implications

The Cetus Protocol exploit reveals critical vulnerabilities in DeFi infrastructure on newer blockchains:

1. **Third-party library risk as systemic vulnerability**: The `checked_shlw` bug resided in the `integer-mate` library, not Cetus's own code — demonstrating that DeFi protocols inherit the security risks of every dependency in their stack, and that library-level bugs can bypass protocol-level audits
2. **Audit scope limitations as false assurance**: Four audits — including one completing 41 days before the exploit — failed to catch the vulnerability, with the final audit explicitly excluding the library containing the bug from its scope, creating a false sense of security for users and investors
3. **Validator centralization as double-edged sword**: The ability of 114 validators to freeze $162 million within minutes demonstrates both a security backstop (protecting users from theft) and a centralization risk (validators can unilaterally censor transactions) — raising fundamental questions about the meaning of "decentralization" in proof-of-stake networks
4. **Bridge saturation speed**: The attacker's ability to extract $60 million at $1M per 30 seconds demonstrates that cross-chain bridges represent a critical extraction window — the speed of fund extraction relative to the speed of community response determines the severity of any exploit

## Relevance to Market Health Metrics

Cetus Protocol's case demonstrates several indicators in the DN Institute [Market Health Metrics](https://dn.institute/research/market-health/docs/market-health-metrics/) framework:

- **Dependency audit coverage as security metric**: The gap between protocol audit coverage and third-party library audit coverage represents a measurable risk factor — protocols should be assessed not only on their own audit status but on the audit status of every critical dependency
- **Validator governance structure**: The distribution of stake among validators, the existence of emergency freeze mechanisms, and the threshold required for coordinated action provide measurable indicators of both security responsiveness and centralization risk
- **Bridge extraction rate monitoring**: Real-time monitoring of outbound bridge volume — particularly sudden spikes in cross-chain transfers — provides an early detection signal for active exploits, as attackers typically saturate bridge capacity immediately after stealing funds
- **Flash loan exposure**: Protocols that allow flash-loan-funded position manipulation in low-liquidity pools face elevated oracle/price manipulation risk — the ratio of available flash loan capital to pool depth provides a quantifiable vulnerability metric

## References

1. CoinDesk, "Sui Network's Cetus Protocol Hit in Apparent Hack, Sending Token Prices Down 90%," May 2025. [coindesk.com](https://www.coindesk.com/markets/2025/05/22/sui-networks-cetus-protocol-hit-in-apparent-hack-sending-token-prices-down-90)
2. Cyfrin, "Inside The $223M Cetus Exploit: Root Cause And Impact Analysis." [cyfrin.io](https://www.cyfrin.io/blog/inside-the-223m-cetus-exploit-root-cause-and-impact-analysis)
3. Dedaub, "The Cetus AMM $200M Hack: How a Flawed 'Overflow' Check Led to Catastrophic Loss." [dedaub.com](https://dedaub.com/blog/the-cetus-amm-200m-hack-how-a-flawed-overflow-check-led-to-catastrophic-loss/)
4. SlowMist, "Analysis of the $230 Million Cetus Hack," May 2025. [slowmist.medium.com](https://slowmist.medium.com/slowmist-analysis-of-the-230-million-cetus-hack-ee569af040f2)
5. Elliptic, "Cetus Protocol hacked for more than $200 million." [elliptic.co](https://www.elliptic.co/blog/cetus-protocol-hacked-for-more-than-200-million)
6. The Defiant, "Sui Validators Vote to Restore $162 Million to Hacked Cetus Users," May 2025. [thedefiant.io](https://thedefiant.io/news/blockchains/sui-validators-vote-to-restore-usd162-million-to-hacked-cetus-users)
7. Blockworks, "$160M in stolen funds puts Sui's decentralization to the test," May 2025. [blockworks.co](https://blockworks.co/news/suis-decentralization-dex-put-to-the-test)
8. CoinDesk, "Sui Network Steps in to Compensate Cetus Losses in Full After $223M Exploit," May 2025. [coindesk.com](https://www.coindesk.com/markets/2025/05/28/sui-network-steps-in-to-compensate-cetus-losses-in-full-after-223m-exploit/)
9. QuillAudits, "Cetus Protocol Hack Analysis." [quillaudits.com](https://www.quillaudits.com/blog/hack-analysis/cetus-protocol-hack-analysis)
