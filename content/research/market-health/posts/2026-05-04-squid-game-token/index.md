---
title: "🌰 Squid Game Token — Anti-Sell Mechanism Rug Pull and the Anatomy of a Social-Engineering Pump-and-Dump"
date: 2026-05-04
entities:
  - SQUID
  - PancakeSwap
  - BNB Chain
  - CoinMarketCap
---

## Summary

1. **SQUID was a BNB Chain token** launched on October 20, 2021, themed around Netflix's "Squid Game" series (with no official affiliation). It rose from $0.01 to an all-time high of approximately $2,861 within 13 days before crashing to near $0 in under 5 minutes on November 1, 2021.
2. **An anti-sell mechanism** was coded into the token's smart contract and project rules: holders could not sell SQUID tokens on PancakeSwap unless they satisfied a separate "Marbles" condition that ordinary market buyers could not practically meet. This meant that while anyone could buy SQUID, virtually no public holders could sell it.
3. **The rug pull extracted approximately $3.38 million** in BNB from the PancakeSwap liquidity pool. The token's developers removed all liquidity and disappeared. The token price collapsed from $2,861 to $0.0007 in approximately 5 minutes, a 99.99% decline.
4. **CoinMarketCap tracked SQUID** during its pump, reporting real-time price data that amplified media coverage before warnings were widely understood. Multiple major news outlets (BBC, CNBC, Bloomberg, and crypto trade press) reported on SQUID's meteoric rise, further driving FOMO-based buying.
5. **No arrests or regulatory actions have been publicly reported** as of 2026. The anonymous developers used no KYC exchange and communicated only through a now-defunct website (squidgame.cash) and a Telegram channel where messaging was restricted to administrators only.

## Background

SQUID launched during a period of intense "meme token" speculation on BNB Chain, when tokens themed around cultural phenomena regularly attracted speculative capital. The Squid Game Netflix series had debuted on September 17, 2021, and was the platform's most-watched series at that time, creating an ideal cultural hook for a social-engineering pump.

The token was presented through a website (squidgame.cash, now offline) that described a play-to-earn game requiring SQUID tokens as entry fees. The purported game involved rounds mirroring the show's challenges, with winners receiving token prizes from a collective pool. No functional game was ever delivered.

Key red flags present from launch:

- **No affiliation with Netflix or Squid Game IP holders**: The project had no license or partnership
- **Anonymous development team**: No verifiable identities were ever published
- **One-way communication**: The Telegram group restricted messaging to admins; community members could only read
- **Whitepaper quality**: The project's whitepaper contained multiple grammatical errors and lacked technical substance
- **Anti-sell contract code**: The selling restriction was visible on-chain in the verified BscScan contract, though few buyers checked

## 🌰 Token Price Manipulation Mechanics

### Anti-Sell Smart Contract Design

The core manipulation was a smart contract function that prevented token holders from selling unless they met specific conditions. The contract's `transfer` function included a check:

```
require(msg.sender == _owner || _hasMarbles[msg.sender], "Need Marbles to transfer");
```

This pseudocode represents the effective logic: ordinary buyers could acquire SQUID, but sell transactions were gated by privileged conditions tied to the project's "Marbles" mechanism. The Marbles requirement:

1. Was not freely obtainable by ordinary buyers during the pump
2. Depended on a promised play-to-earn game that never became a functioning public venue
3. Served as a practical gate on SQUID selling

This created a **one-way market**: anyone could buy SQUID on PancakeSwap (increasing the price), but public holders were effectively blocked from selling (decreasing the price). Every buy increased the liquidity pool's BNB reserves, which the developers could later extract.

### Price Trajectory

The price trajectory reveals the classic shape of a one-way pump enabled by selling restrictions:

| Date | SQUID Price | Daily Volume (est.) | Key Event |
|------|------------|-------------------|-----------|
| Oct 20, 2021 | $0.01 | <$100K | Token launch, initial PancakeSwap listing |
| Oct 26, 2021 | $0.35 | $500K–$1M | Social media buzz begins, first news articles |
| Oct 28, 2021 | $5.60 | $2–5M | CNBC article drives mainstream attention |
| Oct 29, 2021 | $38 | $5–10M | BBC/Bloomberg coverage; CoinMarketCap trending |
| Oct 30, 2021 | $90 | $10–15M | Users report inability to sell; warnings surface |
| Oct 31, 2021 | $630 | $15–20M | BscScan community reports confirm anti-sell |
| Nov 1, 2021 (pre-rug) | $2,861 | $20M+ (buy-only) | All-time high; peak FOMO |
| Nov 1, 2021 (rug) | $0.0007 | N/A (halted) | Liquidity removed; 99.99% crash in ~5 minutes |

The steadily accelerating price with no pullbacks is a direct consequence of the anti-sell mechanism. In a normal market, profit-taking would create periodic corrections. The absence of any sell pressure was the clearest on-chain signal that the market was artificially constructed.

### 🌰 Liquidity Pool Extraction

The rug pull itself was executed in a straightforward manner:

1. **Developers held the LP tokens** for the SQUID/BNB pair on PancakeSwap
2. At peak price ($2,861), they called `removeLiquidity` on PancakeSwap's router contract
3. This withdrew all BNB and SQUID tokens from the pool
4. The extracted BNB (~$3.38 million worth) was rapidly moved through multiple wallets
5. With no liquidity remaining, SQUID became untradeable; remaining holders were left with worthless tokens

On-chain records show the extraction occurred in a small number of transactions within a window of approximately 5 minutes. The extracted BNB was then moved through multiple wallets, making recovery and attribution harder for victims.

## Wash Trading and Volume Manipulation Evidence

### Buy-Only Volume Inflation

Because the anti-sell mechanism prevented genuine two-sided trading, all volume on SQUID was effectively **one-directional buy pressure**. This creates an extreme anomaly in standard market metrics:

- **Buy-sell ratio**: Approaching 100:0 during the pump phase (normal range: 45:55 to 55:45)
- **Volume distribution**: All trades were purchases; no sell orders were filled from genuine holders
- **Order book asymmetry**: The PancakeSwap AMM pool showed an increasingly imbalanced reserve ratio as BNB accumulated and SQUID tokens were absorbed from the pool

### Suspected Developer Self-Trading

Analysis of early SQUID transactions shows patterns consistent with the development team conducting wash trades to establish initial price momentum:

- **Pre-media-coverage volume**: Before any news coverage, SQUID showed significant daily volume ($100K+) within hours of launch, which is unusual for a token with no marketing budget and anonymous creators
- **Round-number BNB purchases**: Early buy transactions clustered around 0.1, 0.5, and 1.0 BNB amounts, indicating automated or scripted purchases rather than organic retail trading
- **Rapid succession**: Multiple purchases from different wallets within the same block or consecutive blocks during the first 48 hours suggest coordinated buying from a single actor using multiple addresses

### CoinMarketCap Amplification

CoinMarketCap listed SQUID and displayed its price in real time during the pump. The platform:

- Added a warning banner that SQUID holders could not sell their tokens (posted October 29, after the price had already risen 560x)
- Continued displaying the inflated price data, which was cited by every major news article
- Did not delist the token until after the rug pull

The delayed warning illustrates a structural vulnerability in crypto data aggregators: by listing and price-tracking tokens without verifying basic contract functionality (like the ability to sell), aggregators can inadvertently amplify manipulation schemes through the credibility and distribution their platforms provide.

## Social Engineering Mechanics

### Media Exploitation

SQUID's creators leveraged the Squid Game cultural phenomenon to generate free media coverage:

1. **Parasitic branding**: By naming the token after the most-watched Netflix series, the project guaranteed search engine visibility and journalist interest without spending on marketing
2. **Price-as-story**: A token going from $0.01 to $2,861 is inherently newsworthy. Every price milestone generated new articles, each of which drove new buyers
3. **Narrative mismatch**: News coverage focused on the price appreciation while burying or omitting the technical red flags (anti-sell mechanism, anonymous team, restricted communication)

### Information Asymmetry Timeline

| Date | Public Information | What Developers Knew |
|------|-------------------|---------------------|
| Oct 20 | "New play-to-earn game token" | Anti-sell mechanism active; no game exists |
| Oct 26 | "SQUID up 3,500%" | LP tokens unlocked; rug pull possible at any time |
| Oct 29 | CoinMarketCap warning; some Reddit/Twitter warnings | Building FOMO still drives net buying |
| Oct 31 | "Users report they cannot sell" | Preparing extraction transactions |
| Nov 1 | Price at $2,861; "is this the next Dogecoin?" | Execute rug pull |

The information asymmetry was maintained through: a Telegram group where only admins could post (preventing warnings from reaching new buyers), a website that provided no technical documentation beyond the whitepaper, and the absence of any public developer identity.

## Lessons for Market Surveillance

The SQUID token case reveals manipulation patterns that automated surveillance should detect:

1. **Anti-sell contract mechanisms**: Smart contract analysis should flag tokens where the `transfer` or `approve` function contains conditional logic restricting selling to specific addresses. Any token where `transferFrom` reverts for most holders is structurally a one-way pump.

2. **Buy-sell ratio extremes**: A sustained buy-sell ratio above 90:10 on a DEX is an unambiguous manipulation signal. Normal markets oscillate around 50:50. PancakeSwap and other AMMs could implement real-time ratio monitoring and surface warnings when a token shows persistent one-directional flow.

3. **Price trajectory without corrections**: A token that rises continuously without any pullback of 5% or more over a period exceeding 72 hours is abnormal. Legitimate price discovery involves corrections as early buyers take profits. The absence of corrections indicates either selling restrictions or extreme manipulation of the order book.

4. **Cultural event parasitism**: Tokens named after trending cultural phenomena (TV shows, memes, celebrities) that launch within weeks of the cultural event's peak attention should receive enhanced scrutiny. The combination of familiar branding and speculative interest creates ideal conditions for social-engineering-driven pumps.

5. **Aggregator listing risk**: Data platforms listing tokens without verifying basic DEX functionality (sell capability, reasonable slippage, LP lock status) provide credibility that manipulators exploit. Automated pre-listing contract analysis — checking for anti-sell logic, ownership concentration, and LP token custody — would have flagged SQUID before it appeared on CoinMarketCap's trending page.

6. **Communication red flags**: Projects that restrict community communication to one-way channels (admin-only Telegram, disabled Discord, no GitHub repository) are preventing the natural spread of warnings from informed community members to potential victims. This is a deliberate information control mechanism.

## References

1. CoinMarketCap. "SQUID Historical Market Data and Anti-Sell Warning." October-November 2021. Retrieved May 2026.
2. BscScan. "Squid Game Token Contract (0x87230146E138d3F296a9a77e497A2A83012e9Bc5) and transaction history." Binance Smart Chain Explorer. Retrieved May 2026.
3. BBC News. "Squid Game cryptocurrency crashes to almost zero." November 1, 2021.
4. CNBC. "A cryptocurrency inspired by 'Squid Game' soars over 75,000% in days, raising red flags." October 28, 2021.
5. Chainalysis. "The 2022 Crypto Crime Report." Chapter 6: Rug Pulls Overtake Scam Revenue. Chainalysis Inc., February 2022.
6. Gizmodo. "The Squid Game Coin Scam Was a Rug Pull from the Start." Burneko, Tom. November 1, 2021.
7. PeckShield. "Analysis of SQUID Token Anti-Dump Mechanism." Twitter/X, November 1, 2021.
