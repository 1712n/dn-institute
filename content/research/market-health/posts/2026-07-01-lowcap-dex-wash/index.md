---
title: "Fabricated Volume on Low-Cap DEX Pools: A Direct On-Chain Census of Lockstep-Bot Wash Trading"
description: "Three low-cap DEX pools on Base and BNB Chain show lockstep-bot wash trading: small fleets of externally-owned wallets holding near-zero inventory that, measured directly on-chain over 24 hours, account for about 2.85 million dollars a day of fabricated volume."
date: 2026-07-01
entities:
  - Uniswap
  - PancakeSwap
  - SOSO
  - ULTIMA
  - IN
---

## Summary

1. Across three low-cap DEX pools on Base and BNB Chain, small fleets of wallets trade against themselves; **measured directly on-chain over 24 hours, they account for 2,845,587 dollars a day of fabricated volume**.
2. **SOSO/USDC (Base) is a near-pure wash pool.** Eleven externally-owned wallets are **98.9 percent** of its 24-hour volume (about 2.0 million dollars) and hold near-zero inventory.
3. **ULTIMA/USDT (BNB Chain) is a single automated operator.** Eleven wallets (42 percent, about 0.5 million dollars) are fed by one relay bot and hold near-zero inventory.
4. **The loudest reported numbers are fictional.** One pool showed **395,507,943 dollars** of daily volume on GeckoTerminal and zero on an independent source; such phantom pools are excluded.
5. **Turnover is not the tell; concentration is.** Liquid control pools run high turnover too, but their ten largest traders hold only 26 to 28 percent of volume; SOSO (99 percent) and ULTIMA (42 percent) sit well above that, while the weakest case, IN (9 percent), sits below and rests on other signals.
6. **A trade-tape snapshot over-states bursty fleets.** Measuring full-day on-chain volume cut one pool's figure roughly six-fold and rejected a fourth pool outright, so every headline number is a direct 24-hour on-chain measurement, not an extrapolation.
7. **Read this as a flag, not a verdict.** The evidence shows deliberate self-trading and single-operator funding, not intent or off-chain identity. Every number below is re-derived from the committed data by a `verify.py` script.

## Data and scope

Public sources, none requiring a paid tier:

- **GeckoTerminal** for the pool universe and the per-trade tape (trader address, side, USD size, transaction hash, timestamp).
- **DexScreener** as an independent second measurement of each pool's daily volume and liquidity.
- **Bitquery** DEX trades for the direct full-day on-chain volume measurement (EVM), plus **public JSON-RPC** for `eth_getCode` and token balances.
- **Helius** for the equivalent on-chain check on Solana.

Starting from the established (non-launch) pool feeds on six chains, the screen keeps pools at least two days old with 10,000 to 3,000,000 dollars of liquidity, at least 300 daily trades, and daily volume of at least five times liquidity: **73 pools screened**. This is a targeted census of high-turnover, low-cap pools, not an estimate over all DEX activity.

## Detection method

A wash-trading fleet is a set of wallets that buy and sell the same token in near-equal amounts, so gross volume is large while net position is near zero. The screen flags a pool when a group of wallets each records at least three buys and three sells with balanced counts, those wallets are at least half of the sampled trades, and the pool-wide net-to-gross ratio is within 0.15 of zero. A pool must also be sustained: at least seven active days of volume history.

Three filters then decide what counts:

1. **Independent-volume corroboration.** Aggregator volume on a manipulated pool is often itself fabricated, so a flag is dropped unless DexScreener independently shows meaningful volume (daily volume above 50,000 dollars).
2. **Contract-fleet check.** The trader recorded for a swap can be a smart contract (a router, an aggregator, or a Uniswap v4 pool manager) rather than a person's wallet. For every EVM pool the detector runs `eth_getCode` on each fleet wallet and keeps only externally-owned accounts; a pool needs at least two.
3. **Direct on-chain full-day measurement.** The screen's fleet share comes from a roughly 300-trade window, which over-represents a fleet that trades in bursts. The fleet's real 24-hour USD volume is read directly from the chain (Bitquery for the EVM pools, Helius for the Solana candidate). That on-chain figure, not the window extrapolation, is the reported fabricated volume, and the pool total measured this way agrees with DexScreener independently.

Mapped to the DN [market-health metric family](https://dn.institute/market-health/docs/market-health-metrics/): the balanced-flow test is `buysellratio` (count-based, buy trades over total) with `buysellratioabs` (volume-weighted), both near 0.5 for a wash fleet; the fleet's dominance of the pool is a concentration measure, its share of 24-hour volume, reported as its own signal and deliberately not folded into `volumedist` (the metric family's trade-size histogram, which this analysis does not compute); the pool volume itself is `vwap`/`tradecount`, cross-checked between Bitquery and DexScreener. A first-digit test (`firstdigitdist`/`benfordlawtest`) is deliberately not used: low-cap trade sizes span too few orders of magnitude to track Benford, so at this sample size the test rejects even the organic control and cannot discriminate. The load-bearing signals here are concentration, near-zero inventory, and the funding graph. This carries the same non-organic-volume analysis the wiki has applied to centralized venues, in the [Huobi (2023)](https://github.com/1712n/dn-institute/tree/main/content/research/market-health/posts/2023-08-14-huobi) and [Senso (2021)](https://github.com/1712n/dn-institute/tree/main/content/research/market-health/posts/2021-01-05-Senso) posts, onto on-chain DEX pools measured per wallet.

## Findings

### The census

Of 73 screened pools, 10 flagged on mechanics and 9 were sustained. Three cleared all three filters. Measured directly on-chain over 24 hours, their fabricated volume totals **2,845,587 dollars per day**.

{{< figure src="fig1_fabricated_by_pool.png" alt="confirmed fabricated volume by pool, measured on-chain" caption="Fabricated volume measured directly on-chain over 24 hours: SOSO $2.01M (98.9% of the pool), ULTIMA $0.51M (42%), IN $0.32M (9%), $2.85M in total across three pools." >}}

| Pool | Chain | EOA fleet | On-chain fabricated / day | Fleet share of pool (24h) | Pool volume (24h) |
|------|-------|:---:|--:|:---:|--:|
| SOSO / USDC | Base | 11 | $2,014,730 | 98.9% | $2,037,268 |
| ULTIMA / USDT | BNB Chain | 11 | $506,707 | 42.0% | $1,206,839 |
| IN / WBNB | BNB Chain | 3 | $324,150 | 9.3% | $3,477,696 |

### Why a snapshot is not enough

The screen flags on a short window of the trade tape. For fleets that trade in bursts, that window catches them mid-burst and overstates their share. The full 24-hour on-chain measurement corrects this. SOSO barely moves: its fleet is 98.9 percent of the pool over the whole day, just as the snapshot suggested. ULTIMA drops modestly. IN collapses: the snapshot implied about 2 million dollars a day, but over 24 hours the three identified wallets are only 9.3 percent of the pool, about 324,000 dollars. A fourth pool, PYTH on Solana, was rejected entirely: its snapshot implied 216,000 dollars, but the on-chain check (via Helius) found the wallets trade PYTH essentially not at all over a full day (206 dollars, 0.1 percent); they are generic multi-token bots that happened to be balanced in the sampled window.

{{< figure src="fig6_window_vs_onchain.png" alt="sampled-window estimate versus direct on-chain measurement" caption="Sampled-window estimate versus the direct 24-hour on-chain measurement. SOSO is unchanged; IN falls from a snapshot-implied ~$2.0M to $324k; PYTH collapses to near zero and is rejected." loading="lazy" >}}

### Exclusion gate 1: phantom volume

Three pools flagged on mechanics were dropped because the independent source shows no volume at all. The clearest is a BNB Chain pool for the token quq: GeckoTerminal reported **395,507,943 dollars** of daily volume; DexScreener does not index the pool and shows zero. A second quq pool (20 million reported) and an ARX pool (14 million reported) show the same pattern. These three alone would have added roughly 430 million dollars per day of fictional volume had the study trusted aggregator numbers.

{{< figure src="fig2_phantom_vs_real.png" alt="phantom volume: reported versus independent" caption="Excluded phantom volume: GeckoTerminal reports up to $396M/day on these pools while DexScreener shows zero." loading="lazy" >}}

### Exclusion gate 2: contracts, not traders

Two pools cleared the volume check but failed the contract check. DUAL/ETH on Base is a Uniswap v4 pool whose flagged fleet is nine smart contracts and a single externally-owned wallet; BASED/USDT on BNB Chain has one externally-owned wallet and one contract. Balanced flow routed through shared contracts cannot be separated from organic trading aggregated by a router, so both are dropped. This also corrects a tempting but wrong inference: the wallet that appears in both the BASED and ARX fleets is itself a contract, which is why it shows up across pools. It is shared infrastructure, not a shared operator.

### A liquid control: concentration is the tell, not turnover

Turnover (a pool's daily volume divided by its liquidity) screens candidates but does not prove manipulation: liquid, legitimately-traded pools run high turnover too. Measured the same way over 24 hours, WETH/USDC on Base and USDT/WBNB on BNB Chain each turn over about seven times, both organic. What separates the flagged pools is concentration in a handful of wallets. In the two controls even the ten largest traders hold only 28 and 26 percent of volume (the single largest, 7 and 3 percent), whereas in SOSO a fleet of eleven wallets holds 98.9 percent of the pool and in ULTIMA eleven wallets hold 42 percent, both outside the range the two controls occupy. IN is the honest exception: its three wallets are 9 percent of the pool, below the controls, so IN does not rest on concentration but on the pool's own impossibility. On DexScreener's snapshot the pool turns over 481 times in a single day, 3.5 million dollars of volume through just 7,346 dollars of liquidity across 78,233 transactions, and its three named wallets trade in balanced, zero-inventory lockstep. The manipulation in the IN pool is clearly broader than the fleet we can name.

{{< figure src="fig3_concentration.png" alt="volume concentration: flagged fleets versus liquid controls" caption="Share of 24-hour pool volume held by the flagging wallet set. SOSO 98.9% and ULTIMA 42% sit above the liquid controls, whose ten largest traders hold only 26-28%; IN at 9% falls below them." loading="lazy" >}}

### Wash trading, not market-making

A legitimate market maker holds inventory to quote both sides; a wash fleet cycles the same small stack of funds and ends near flat. The fleets hold almost nothing relative to what they trade: the IN wallets hold 0 dollars of the token against 3.5 million dollars a day of volume, SOSO's fleet holds 2,531 dollars (0.12 percent of daily volume), ULTIMA's holds 377 dollars (0.03 percent). They are recycling funds, not making markets.

{{< figure src="fig4_fleet_balance.png" alt="fleet flow is balanced buy versus sell" caption="Fleet buys versus sells in the sampled tape are near-equal for each pool (net accumulation near zero): the wash signature." loading="lazy" >}}

### Three pools up close

**SOSO / USDC (Base, Uniswap).** Eleven externally-owned wallets (a twelfth sampled trader is a contract, dropped) that are **98.9 percent of the pool's on-chain volume over 24 hours** and hold near-zero inventory. This is the cleanest case. Example fleet transaction: `0x64b49d3eae370472a16b94ef3569d15c7a078b95a83425cf3f4675836edcc65c` (wallet `0x3d42f45c91279337d6a0fe76a16889288fc767b6`).

**ULTIMA / USDT (BNB Chain, Uniswap).** Eleven externally-owned wallets that are 42 percent of the pool over 24 hours and hold near-zero inventory. What makes ULTIMA the clearest attribution case is its funding: the eleven are fed by a single automated relay chain (below).

**IN / WBNB (BNB Chain, PancakeSwap).** An anomalous pool (481x turnover) where three wallets (`0xc86dc628...`, `0xc3f5edd0...`, `0x7afab429...`) account for 9.3 percent of full-day volume, about 324,000 dollars, and hold zero inventory. Example transaction: `0x6467f6c800200ed7b39b604db273186fd48cdd5bc7ae4ea7d966a70f6b70a812`.

### Operator attribution

The mechanics prove self-trading; the funding graph identifies coordination. Tracing native-token transfers upward from the BNB-Chain fleets gives two clear pictures:

**ULTIMA is a single automated operator.** The eleven wallets are linked by one automated funding chain: each receives roughly 0.052 BNB and forwards it to a single next wallet, on a fixed cadence of about eight minutes, with a small fixed per-hop decrement consistent with the forwarding-transaction fee. A chain in which every node has exactly one downstream recipient, on a regular timer, is not organic behaviour.

{{< figure src="fig5_ultima_funding_chain.png" alt="ULTIMA automated funding relay chain" caption="ULTIMA's eleven wallets are fed by one automated relay chain: each hop forwards roughly 0.052 BNB to the next wallet on a fixed ~8-minute cadence, with a small fixed decrement." loading="lazy" >}}

**IN traces to throwaway wallets.** Its fleet is funded through a short chain of throwaway externally-owned accounts (`0x50560acf...` funding `0x40068df75...` funding the fleet), each with only a couple of transactions.

The two BNB-Chain operators do not share a funding ancestor, and neither connects to the Base pool: this is a decentralised pattern, many independent operators rather than one actor.

## Limitations

The on-chain figure counts only the identified fleet; the IN pool in particular is manipulated well beyond the three wallets named, so 324,000 dollars is a floor for that pool, not a ceiling. The result does not hinge on that weakest case: SOSO and ULTIMA alone account for 2.5 million dollars of the headline. The contract and Bitquery on-chain checks are EVM-native; the one Solana candidate was checked with Helius and rejected. Prevalence (3 confirmed of 73 screened) is conditional on the screen, not an estimate over all DEX pools. The evidence establishes self-trading and single-operator funding structures, not intent or off-chain identity; manufactured volume of this kind can serve deliberate manipulation or a volume-incentive program. Each funding chain terminates where funds arrive off-native (a bridge or a centralized exchange), which on-chain data alone cannot pierce.

## Reproducibility

Everything regenerates from the companion repository, [mkzung/dex-volume-integrity](https://github.com/mkzung/dex-volume-integrity), pinned at commit `ec7b155` for this submission. Clone it and check out that commit, run `pip install -r requirements.txt`, then `python3 verify.py` to re-derive and assert every number in this post offline, and `python3 make_figures.py` to rebuild the figures. The collection scripts regenerate the data from the live sources: `runner.py` screens, `aggregate.py` applies the volume and `eth_getCode` filters, `onchain_fullday.py` (Bitquery) and `helius_pyth.py` (Helius) measure the direct full-day on-chain fabricated volume, `control_measure.py` measures the liquid controls, `net_inventory.py` checks holdings, and `attribution.py` traces funding. Dated DexScreener and trade-tape snapshots are included in the repository.

## References

- GeckoTerminal API: https://api.geckoterminal.com
- DexScreener API: https://docs.dexscreener.com
- Bitquery DEX Trades API: https://docs.bitquery.io
- Helius API: https://docs.helius.dev
- Lin William Cong, Xi Li, Ke Tang, and Yang Yang, "Crypto Wash Trading," Management Science 69(11):6427-6454, 2023 (NBER Working Paper 30783). Establishes that a large share of reported crypto trading volume is fabricated and introduces statistical detection of wash trading; this study applies a complementary on-chain, per-wallet balanced-flow test on DEX pools.
