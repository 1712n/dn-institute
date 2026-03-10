---
title: "Hyperliquid JELLY Incident: DEX Liquidation Manipulation and Vault Exploitation"
date: 2025-03-26
entities:
  - Hyperliquid
  - JELLY
  - HLP
  - Binance
  - OKX
---

## Summary

1. On March 26, 2025, an attacker exploited Hyperliquid's liquidation engine by opening a **~$4.1 million short position** in JELLY across one wallet and offsetting longs across two others, then **intentionally triggering self-liquidation** to force the HLP (HyperLiquidity Provider) vault to inherit a **$15.3 million short position**.
2. The attacker subsequently pumped JELLY's spot price on Raydium by over **400%**, creating an unrealized loss of approximately **$12-13.5 million** on the HLP vault's inherited short.
3. Hyperliquid's 16 validators voted unanimously within **2 minutes** to delist JELLY perpetual futures and force-settled all positions at **$0.0095** (the attacker's original entry price), rather than the prevailing market price of ~$0.043-0.050.
4. The incident exposed critical vulnerabilities in DEX liquidation mechanisms, including the absence of open interest caps relative to token market capitalization, and raised questions about decentralization when a small validator set can override market outcomes unilaterally.
5. **Binance and OKX listed JELLY perpetual futures within hours** of Hyperliquid's delisting, fueling speculation about competitive dynamics between centralized and decentralized exchanges.

## Background

### JELLYJELLY Token

JELLYJELLY (JELLY) is a Solana-based memecoin launched on January 29-30, 2025, via Pump.fun. It was created by Venmo co-founder Iqram Magdon-Ismail and former Facebook VP Sam Lessin as a token granting early access to the JellyJelly social app. At launch, JELLY reached a market cap of roughly $230-250 million and an all-time high price of $0.21. By March 26, the market cap had collapsed to approximately $25 million.

### Hyperliquid and the HLP Vault

Hyperliquid is a Layer 1 blockchain and on-chain perpetuals DEX using a Central Limit Order Book (CLOB) model. Its liquidity infrastructure depends on the HLP (HyperLiquidity Provider) vault, a passive market-making pool that automatically inherits positions that cannot be liquidated through normal means. Before the incident, HLP held approximately $240 million in total value locked (TVL).

The platform operates with 16 validators, with the Hyper Foundation controlling approximately 81% of staked HYPE tokens.

### Prior Context: The March 12 ETH Incident

Two weeks earlier, on March 12, a separate whale manipulated Hyperliquid's ETH market by building a $306 million ETH long position using 50x leverage, then withdrawing $17 million USDC by exploiting the ability to withdraw against unrealized PnL. This caused approximately $4 million in losses to the HLP vault and triggered $80 million in user outflows. This earlier exploit demonstrated the same category of HLP vault vulnerability that the JELLY attacker would later exploit more aggressively.

## Attack Timeline

| Time (UTC) | Event |
|---|---|
| ~10:00 | Attacker conducts preliminary price manipulation: a small pump (~13%) followed by a major dump (~30%) to establish favorable spot liquidity conditions |
| ~12:50 | Attack window opens with JELLY spot price at approximately $0.0095-$0.0128 |
| 12:53 | Primary wallet (`0xde95...c91`) opens a massive short position of approximately 215 million JELLY tokens (~$4.1M notional) |
| 12:53-13:00 | Two coordinating wallets (`0x67fe...CA2` and `0x20e8...808`) open long positions of $2.15M and $1.9M respectively, creating delta-neutral exposure |
| 13:03-13:04 | Attacker withdraws collateral from the short position, intentionally triggering liquidation. HLP vault inherits a **398 million JELLY short position** ($15.3M notional) at entry price ~$0.011282 |
| 13:00-14:00 | Attacker aggressively buys JELLY on Raydium (Solana DEX), pumping the price over 400% |
| ~14:00 | JELLY peaks at approximately $0.043-0.050. HLP unrealized loss reaches $12-13.5 million |
| ~15:00 | Validators convene emergency session |
| ~15:00 | All 16 validators vote unanimously to delist JELLY perpetual futures |
| 15:15 | All JELLY positions force-settled at $0.0095 (original short entry price). JELLY long holders receive refund at $0.037555 |
| Same day | Binance and OKX list JELLY perpetual futures, causing another 426-560% price spike |

## Attack Mechanism

This attack is structurally distinct from wash trading. Rather than inflating volume metrics, the attacker weaponized Hyperliquid's automated risk management system against the protocol itself through a five-step process:

### Step 1: Delta-Neutral Positioning

Three wallets opened opposing positions to maintain zero net market exposure. The $4.1M short on wallet `0xde95` was offset by longs of $2.15M and $1.9M on wallets `0x20e8` and `0x67fe`.

### Step 2: Intentional Liquidation Trigger

The attacker removed margin from the short position, making it undercollateralized. Because Hyperliquid's liquidation engine could not find external takers for a ~$15M short on an asset with only a ~$25M market cap, the position was automatically transferred to the HLP vault.

### Step 3: Spot Market Price Manipulation

With HLP now holding the massive short, every dollar increase in JELLY's price created proportional unrealized losses on the vault's inherited position. The attacker pumped JELLY on Raydium and other Solana DEXs.

### Step 4: Oracle Price Feed Exploitation

Hyperliquid's price oracle, partly fed by on-chain DEX prices, began reflecting the manipulated spot price. This directly amplified HLP's mark-to-market losses.

### Step 5: Vault Solvency Threat

At the peak manipulation price, had JELLY reached $0.15374, the HLP vault's **entire $230 million** would have been wiped. The attacker managed to push the price to approximately $0.043-0.050 before validators intervened.

## Key Vulnerability: Open Interest vs. Market Cap

A critical design flaw enabled this attack: Hyperliquid's open interest (OI) caps did not account for the relationship between OI and total token market capitalization. During the attack, JELLY's open interest on Hyperliquid **exceeded the token's total market cap**. The HLP vault held approximately 50% of all JELLY open interest, with the attacker holding the other ~50%. In a properly designed system, automatic circuit breakers would have prevented OI from surpassing the underlying asset's market cap.

## On-Chain Data

| Metric | Value |
|---|---|
| Attacker short wallet | `0xde95...c91` |
| Long wallet 1 | `0x20e8...808` |
| Long wallet 2 | `0x67fe...CA2` |
| Short position size | ~215M JELLY tokens (~$4.1M) |
| Long position sizes | $2.15M + $1.9M |
| Total deposited (3 wallets) | $7.17M |
| HLP inherited short (notional) | $15.3M (398M JELLY) |
| HLP peak unrealized loss | $12-13.5M |
| JELLY price at attack start | ~$0.0095 |
| JELLY price at peak manipulation | ~$0.043-0.050 |
| Force-settlement price | $0.0095 |
| JELLY long refund price | $0.037555 |
| HLP vault-wipe threshold | $0.15374 |
| HLP net gain from settlement | +$703,000 |
| Attacker funds withdrawn | ~$6.26M (incl. 2.76M USDC to Arbitrum) |
| Attacker funds frozen | ~$900,000 |
| HYPE token price drop | 16-22% |
| USDC outflow in 3 hours | $140M |
| Post-incident HLP TVL | ~$195-197M (down from ~$240M) |

## Hyperliquid's Response

Hyperliquid's validators voted to delist JELLY and force-settle positions at $0.0095, the attacker's original entry price. Long holders received compensation at $0.037555. The flagged attacker addresses were excluded from any refund.

Following the incident, Hyperliquid announced several risk management improvements:

- **Stricter Liquidator vault caps**: The Liquidator vault (within HLP) will hold a smaller portion of total HLP value
- **Dynamic OI caps**: Open interest limits adjusted based on market size and market capitalization
- **ADL triggers**: Auto-Deleveraging to activate when Liquidator vault losses exceed defined thresholds
- **Increased margin requirements**: Maintenance margin raised to 20% for certain leveraged positions
- **On-chain governance**: Fully on-chain validator voting for asset delisting deployed on March 29 (previously off-chain coordination)

## Industry Reaction and Competitive Dynamics

### Binance and OKX

Within hours of Hyperliquid delisting JELLY, both Binance and OKX listed JELLY perpetual futures. On-chain investigator ZachXBT found that the two long wallets had received funding from Binance, OKX, Bybit, and MEXC prior to the attack, though no definitive proof of CEX-level coordination was established.

### Centralization Criticism

The incident sparked significant debate about DEX decentralization claims. Bitget CEO Gracy Chen characterized the response as "immature, unethical, and unprofessional" and warned Hyperliquid "may be on track to become FTX 2.0." The core criticism centered on two points:

1. The validator vote completed within 2 minutes, demonstrating that 16 validators could override market mechanics unilaterally
2. The settlement at $0.0095 versus the market price of $0.043-0.050 was characterized as arbitrary price setting by the protocol itself

### Long-Term Impact

According to subsequent reporting, HLP TVL dropped from approximately $540M to $150M in the month following the incident, reflecting erosion of user confidence in the vault's risk management.

## DEX Liquidation Manipulation vs. Traditional Wash Trading

| Dimension | Traditional Wash Trading | DEX Liquidation Manipulation (JELLY) |
|---|---|---|
| **Objective** | Inflate volume metrics, create false price signals | Force the protocol's vault to absorb a losing position |
| **Target** | Market participants, exchange rankings | The exchange's own liquidity infrastructure |
| **Mechanism** | Circular buy-sell between controlled accounts | Self-liquidation to transfer toxic positions to the vault |
| **Price role** | Volume is artificial but price may be natural | Price is directly manipulated to worsen the inherited position |
| **Counterparty** | No genuine counterparty transfer | Protocol vault becomes forced counterparty |
| **Oracle dependency** | Not relevant | Critical: DEX oracle feeds amplify manipulation |
| **Regulatory framework** | Established (SEC, CFTC wash trading prohibitions) | No established framework; exploits DeFi regulatory vacuum |
| **Detection** | Moderate (matching volumes, same address pairs) | High difficulty (delta-neutral on paper, legitimate perp/spot trading) |

## Conclusion

The Hyperliquid JELLY incident represents a new category of market manipulation unique to decentralized perpetuals exchanges. Unlike traditional wash trading that targets volume metrics, this attack weaponized the protocol's automated liquidation engine to create a forced counterparty relationship between the attacker and the platform's own liquidity vault.

The incident exposed three structural risks in DEX design: (1) liquidation engines that can be gamed through self-liquidation of illiquid positions, (2) oracle systems that amplify spot market manipulation into derivatives losses, and (3) governance structures where a small validator set can unilaterally override market outcomes. Hyperliquid's subsequent risk management updates address some of these vulnerabilities, but the fundamental tension between automated DeFi mechanisms and the need for human intervention in crisis scenarios remains unresolved.

## References

1. CoinDesk, "HyperLiquid Delists JELLY After Vault Squeezed in $13M Tussle," March 26, 2025. [Link](https://www.coindesk.com/markets/2025/03/26/hyperliquid-delists-jellyjelly-after-vault-squeezed-in-usd13m-tussle)
2. The Block, "Hyperliquid Delists JELLYJELLY Memecoin Amid Whale Manipulation Fiasco," March 26, 2025. [Link](https://www.theblock.co/post/348314/hyperliquid-delists-jellyjelly-memecoin-amid-whale-manipulation-fiasco)
3. CoinTelegraph, "Timeline: Jelly Token Goes Sour After $6M Exploit on Hyperliquid," March 2025. [Link](https://cointelegraph.com/news/timeline-jelly-token-exploit-hyperliquid)
4. Arkham Intelligence, "JELLYJELLY Exploit on Hyperliquid," March 2025. [Link](https://info.arkm.com/research/jellyjelly-exploit-on-hyperliquid)
5. Halborn Security, "Explained: The Hyperliquid Hack (March 2025)," March 2025. [Link](https://www.halborn.com/blog/post/explained-the-hyperliquid-hack-march-2025)
6. Hyperliquid Wiki, "Incident Report 2025-26-03." [Link](https://hyperliquid-co.gitbook.io/wiki/introduction/roadmap/incident/2025-26-03)
7. Arrington Capital, "Hyperliquid Under Attack: Three Things They Must Do Now," March 2025. [Link](https://www.arringtoncapital.com/blog/hyperliquids-tipping-point-three-things-they-must-do-now/)
8. Crypto.news, "Binance and OKX List JELLY Futures Amid Hyperliquid's Delisting," March 26, 2025. [Link](https://crypto.news/binance-and-okx-list-jelly-futures-amid-hyperliquids-delisting-and-market-manipulation-fallout/)
9. CoinDesk, "How the Hype for Hyperliquid's Vault Evaporated on Concerns Over Centralization," April 10, 2025. [Link](https://www.coindesk.com/business/2025/04/10/how-the-hype-for-hyperliquid-s-vault-evaporated-on-concerns-over-centralization)
10. WuBlockchain, "Exploring the Jelly Short-Squeeze Incident: Are Centralized Exchanges Really Superior to Hyperliquid?" March 2025. [Link](https://wublock.substack.com/p/exploring-the-jelly-short-squeeze)
