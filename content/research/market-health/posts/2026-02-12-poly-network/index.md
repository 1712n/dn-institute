---
title: "Poly Network: $611M Cross-Chain Bridge Exploit, 'Mr. White Hat' Return, and the Limits of Post-Hack Negotiation"
date: 2026-02-12
entities:
  - Poly Network
---

## Summary

1. **$611 million stolen — largest DeFi hack at the time**: On August 10, 2021, a single attacker exploited a privilege escalation vulnerability in Poly Network's cross-chain relay contracts to drain approximately $611 million in assets across Ethereum ($273M), Binance Smart Chain ($253M), and Polygon ($85M) — the largest decentralized finance exploit in history at that time.
2. **Critical smart contract flaw — not a cryptographic break**: The attacker exploited the `EthCrossChainManager` contract's ability to call any contract function by crafting a cross-chain message that modified the `keeper` role in the `EthCrossChainData` contract, granting themselves authority to approve withdrawal transactions.
3. **Full return within 15 days**: The attacker returned all stolen funds between August 11 and August 25, 2021 — after Poly Network publicly addressed them as "Mr. White Hat," offered a $500,000 bug bounty (declined), and invited them to serve as Chief Security Advisor (also declined).
4. **Tether froze $33.4 million instantly**: Within hours of the hack, Tether blacklisted the attacker's Ethereum address containing $33.4 million in USDT, demonstrating that centralized stablecoin issuers can unilaterally freeze stolen assets — a factor that may have influenced the attacker's decision to return funds.
5. **Second hack in July 2023**: Poly Network was exploited again on July 1, 2023 — this time through compromised private keys of the 3-of-4 multisig controlling bridge operations — with the attacker minting $34 billion in tokens across 57 chains, though only approximately $5.5 million was extractable due to low liquidity.

## Background

### Poly Network and Cross-Chain Infrastructure

**Poly Network** was a cross-chain interoperability protocol launched in **August 2020**, developed as a collaboration between three blockchain projects: **Neo**, **Ontology**, and **Switcheo**. The protocol enabled users to transfer assets between blockchains including Ethereum, Binance Smart Chain, Polygon, Avalanche, Fantom, Arbitrum, and others [1].

The protocol operated through a set of smart contracts deployed on each supported chain, with a relay chain coordinating cross-chain messages. The critical components were:

- **EthCrossChainManager**: The contract responsible for executing cross-chain transactions on Ethereum
- **EthCrossChainData**: The contract storing the list of authorized "keepers" (validators) who could approve cross-chain transactions
- **LockProxy**: The contract holding locked user assets on each chain

### The Keeper System

Cross-chain transfers on Poly Network required authorization from a set of **keepers** — designated accounts whose public keys were stored in the `EthCrossChainData` contract. A threshold of keeper signatures was required to approve any cross-chain asset transfer. The ability to modify the keeper list was the critical privilege that the attacker targeted.

## The Exploit (August 10, 2021)

### Attack Vector: Cross-Contract Privilege Escalation

At approximately **17:55 UTC on August 10, 2021**, the attacker executed a sophisticated exploit that targeted a fundamental design flaw in how the `EthCrossChainManager` processed cross-chain messages [2]:

**Step 1 — Crafting a malicious cross-chain message**: The attacker constructed a cross-chain transaction on a source chain (Ontology or BSC) containing a specially crafted payload. This payload was designed to be interpreted by the `EthCrossChainManager` as a legitimate cross-chain instruction.

**Step 2 — Exploiting `executeCrossChainTx`**: The `EthCrossChainManager` contract's `executeCrossChainTx` function was designed to execute arbitrary function calls based on cross-chain messages. Critically, the function used the first four bytes of the `_method` parameter to construct a function selector, then called the target contract using a low-level `.call()`. **There was no restriction on which contracts or functions could be called.**

**Step 3 — Calling `putCurEpochConPkBytes` on EthCrossChainData**: The attacker's payload directed the `EthCrossChainManager` to call `putCurEpochConPkBytes` on the `EthCrossChainData` contract — the function that updates the list of authorized keepers. Because the `EthCrossChainData` contract only checked that the caller was the `EthCrossChainManager` (which it was), the call succeeded.

**Step 4 — Replacing keepers with attacker's key**: The attacker replaced all existing keeper public keys with their own public key, granting themselves sole authority to approve any cross-chain withdrawal.

**Step 5 — Draining all bridges**: With keeper authority, the attacker signed and executed withdrawal transactions draining the `LockProxy` contracts across three chains.

### Stolen Amounts

| Chain | Amount |
|-------|--------|
| Ethereum | ~$273 million (USDC, WBTC, WETH, DAI, UNI, SHIB, FEI, USDT) |
| Binance Smart Chain | ~$253 million (BUSD, BTCB, ETH, BNB) |
| Polygon | ~$85 million (USDC) |
| **Total** | **~$611 million** |

### Root Cause

The vulnerability was a combination of two design flaws:

1. **Unrestricted cross-contract calls**: The `EthCrossChainManager` could call any function on any contract, including the privileged `putCurEpochConPkBytes` function on `EthCrossChainData`
2. **Insufficient access control**: The `EthCrossChainData` contract's `putCurEpochConPkBytes` only verified that the caller was the `EthCrossChainManager` — it did not verify that the original cross-chain message was legitimately authorized

Security firm **SlowMist** summarized: the attacker was able to pass carefully constructed data through the `EthCrossChainManager` contract to modify the keeper to their own address, and then construct a transaction to extract all funds [3].

## The "Mr. White Hat" Return

### Poly Network's Public Response

Within hours of the hack, Poly Network took the unprecedented step of **publicly addressing the attacker** via an open letter on Twitter [4]:

- **August 10**: Poly Network published: *"Dear Hacker... We want to establish communication with you and urge you to return the hacked assets"*
- Argued that law enforcement would pursue the attacker
- Noted that Tether had already frozen $33.4 million in USDT
- Called the hack *"the biggest in defi history"* and warned the attacker would be pursued *"by law enforcement in any country"*

### Tether's Freeze

**Within hours of the exploit**, Tether blacklisted the attacker's Ethereum address containing **$33.4 million in USDT**, making those tokens permanently untransferable. This was significant because it demonstrated that:

1. Centralized stablecoin issuers can unilaterally freeze stolen assets
2. The attacker could not realize the full $611 million
3. Any attempt to swap frozen USDT would fail

### The Attacker's Embedded Messages

The attacker communicated through **Ethereum transaction input data** (embedded messages), claiming [5]:

- *"IT WOULD HAVE BEEN A BILLION HACK IF I HAD WANTED TO MOVE REMAINING SHITCOINS!"*
- *"I AM NOT SO INTERESTED IN MONEY"*
- *"I KNOW THE RISK OF EXPOSING MYSELF EVEN IF I DON'T DO EVIL"*
- When asked why they attacked Poly Network specifically: *"CROSS CHAIN HACKING IS HOT"*
- On the Tether freeze: *"WHAT IF I HAD CREATED A NEW TOKEN AND MASS-MOVED THE LIQUIDITY FROM DEXs? HAHA"*
- Stated the reason for returning was: *"THAT'S ALWAYS THE PLAN! I AM NOT VERY INTERESTED IN MONEY! ... WHEN SPOTTING THE BUG, I HAD A MIXED FEELING... I CAN'T TRUST ANYONE, SO THE ONLY SOLUTION IS SAVE IT IN A TRUSTLESS ACCOUNT WHILE KEEPING ME ANONYMOUS AND SAFE"*

### Return Timeline

| Date | Event |
|------|-------|
| August 10, 2021 | Hack executed; Poly Network publishes open letter; Tether freezes $33.4M USDT |
| August 11, 2021 | Attacker begins returning funds; $260M returned on first day |
| August 12, 2021 | Poly Network offers $500,000 bug bounty — attacker declines |
| August 13, 2021 | Total returned reaches approximately $340M |
| August 14, 2021 | Poly Network offers attacker position as "Chief Security Advisor" — attacker declines |
| August 23, 2021 | Remaining BSC and Polygon assets returned |
| August 25, 2021 | Final Ethereum assets returned (except frozen $33.4M USDT, which Tether later unfroze and returned to Poly Network) |
| **Total returned** | **$611 million (100%)** |

### Debate: Voluntary or Coerced Return?

The security community remains divided on whether the return was truly voluntary [6]:

**Voluntary theory**: The attacker was a security researcher who intended to expose the vulnerability, as evidenced by their embedded messages claiming disinterest in money.

**Coerced theory**: Multiple factors may have forced the attacker's hand:
- Tether's $33.4M freeze demonstrated centralized control over stolen assets
- **SlowMist** claimed to have identified the attacker's email, IP address, and device fingerprint
- Blockchain analytics firms were tracking all fund movements in real time
- The attacker's attempt to use Curve Finance to swap some assets was partially blocked by the community
- The sheer visibility of the exploit made laundering $611M nearly impossible

## The Second Hack (July 1, 2023)

### Compromised Keeper Keys

On **July 1, 2023**, Poly Network was exploited again — this time through a completely different attack vector [7]:

- The attackers compromised the **private keys** of the multisig keepers controlling Poly Network's bridge operations
- The bridge operated with a **3-of-4 multisig** at the time — the compromise of 3 keys was sufficient
- Using keeper authority, the attacker minted tokens across **57 blockchain networks**

### Minted Token Values

The attacker minted a nominal **$34 billion** in tokens across multiple chains, including:
- 24 billion BUSD and 999 trillion SHIB on Metis
- Large quantities of BNB, BUSD, and other tokens on Heco, Polygon, Avalanche, and BSC

However, **actual extractable value was approximately $5.5 million** due to:
- Low liquidity on most targeted chains
- Metis team locked the METIS-BUSD and METIS-BNB liquidity pools
- Most minted tokens could not be swapped due to insufficient DEX liquidity

### Response

- Poly Network suspended services and stated it was working with law enforcement
- The Poly Network bridge was **never fully restored** — the project effectively ceased operations after this second exploit

## Market Manipulation Implications

The Poly Network exploits reveal critical vulnerabilities in cross-chain bridge infrastructure:

1. **Cross-contract privilege escalation as design-level risk**: The ability to call arbitrary contracts through the `EthCrossChainManager` represented a fundamental design flaw — not a bug in a single function, but an architectural decision that treated untrusted cross-chain messages as authorized instructions for privileged operations
2. **Centralized freeze power as deterrent and risk**: Tether's ability to freeze $33.4 million within hours demonstrated that stablecoin centralization creates both a security backstop (deterring theft) and a censorship risk (unilateral asset freezing without judicial process)
3. **Post-hack negotiation as precedent**: Poly Network's public "Mr. White Hat" framing — offering bounties and job titles to a thief — established a controversial precedent where protocols negotiate with attackers rather than pursuing pure law enforcement, potentially incentivizing "white hat" exploit-and-return schemes
4. **Repeated exploitation indicates systemic failure**: The second hack in July 2023 via compromised multisig keys — after the 2021 exploit via smart contract vulnerability — demonstrates that bridge security requires continuous maintenance and that surviving one exploit does not guarantee resilience against different attack vectors

## Relevance to Market Health Metrics

Poly Network's case demonstrates several indicators in the DN Institute [Market Health Metrics](https://dn.institute/research/market-health/docs/market-health-metrics/) framework:

- **Smart contract audit coverage as security metric**: The `EthCrossChainManager` vulnerability — allowing unrestricted cross-contract calls to modify keeper lists — represents an architectural flaw that should be detectable through comprehensive security audits focused on privilege escalation paths
- **Bridge reserve monitoring**: Real-time monitoring of bridge reserve balances across chains could have detected the simultaneous drainage of $611 million across three chains within minutes, providing an automated health signal for cross-chain infrastructure
- **Multisig decentralization as resilience indicator**: The second hack's exploitation of a 3-of-4 multisig demonstrates that the number and independence of signing keys is a measurable security parameter — bridges with low key thresholds or keys controlled by related parties represent elevated risk
- **Stablecoin freeze capability as systemic factor**: Tether's instant freeze of $33.4 million demonstrates that centralized stablecoin issuers represent both a safety mechanism and a concentration of power, relevant to any assessment of DeFi ecosystem health

## References

1. Poly Network, "Poly Network Official Documentation." [poly.network](https://www.poly.network/)
2. Rekt News, "Poly Network — REKT," August 2021. [rekt.news](https://rekt.news/polynetwork-rekt/)
3. SlowMist, "SlowMist Tracking: The Poly Network Hacker's Entire Fund Flow," August 2021. [slowmist.medium.com](https://slowmist.medium.com/slowmist-tracking-possible-identification-clues-related-to-the-poly-network-attackers-b9f8caf11f17)
4. CNBC, "$600 million in crypto was stolen. This hacker gave most of it back," August 2021. [cnbc.com](https://www.cnbc.com/2021/08/13/poly-network-hacker-has-now-returned-virtually-all-of-the-stolen-crypto.html)
5. Elliptic, "Poly Network Hack: $611m Stolen in Biggest Ever DeFi Hack," August 2021. [elliptic.co](https://www.elliptic.co/blog/600-million-stolen-from-poly-network-in-biggest-ever-cryptocurrency-theft)
6. CoinDesk, "Poly Network Offers Chief Security Advisor Position to Hacker Behind $611M Exploit," August 2021. [coindesk.com](https://www.coindesk.com/markets/2021/08/17/poly-network-offers-chief-security-advisor-position-to-hacker-behind-611m-exploit/)
7. Rekt News, "Poly Network — REKT II," July 2023. [rekt.news](https://rekt.news/poly-rekt2/)
