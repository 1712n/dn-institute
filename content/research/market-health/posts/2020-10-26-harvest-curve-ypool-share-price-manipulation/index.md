---
title: "Harvest Finance Curve yPool Share-Price Manipulation"
date: 2020-10-26
entities:
  - Harvest Finance
  - Curve yPool
  - fUSDC
  - fUSDT
  - USDC
  - USDT
  - Uniswap
---

## Summary

This case study analyzes the October 26, 2020 Harvest Finance fUSDC and fUSDT economic attack as a market-health example of flash-loan-funded price-state manipulation. Harvest's incident page says attackers launched the attack at 02:53 UTC and drained $24 million from the USDC and USDT vaults. Harvest's post-mortem gives a more granular accounting: the attacker used large temporary USDC and USDT balances, moved the Curve yPool stablecoin mix, deposited into Harvest vaults while the vault share price referenced the manipulated pool state, reversed the Curve trade, and withdrew at a more favorable share price.

The key market-health lesson is not only that a vault lost funds. The important signal is that a venue-derived price state was made briefly false but still usable by another protocol as an accounting input. The same transaction group created the price impact, consumed the distorted price through Harvest's deposit and withdrawal logic, and removed the proceeds before normal liquidity providers could react.

The supporting event table is available in [harvest-curve-attack-summary.csv](harvest-curve-attack-summary.csv).

## Manipulation Path

Harvest's post-mortem says the attacker deployed a fresh attack contract through wallet `0xf224ab004461540778a914ea397c589b677e27bb` at 02:53:31 UTC. In the initiating transaction, the contract sourced 50,000,000 USDC and 18,308,555.417594 USDT from Uniswap. That inventory was temporary flash-loan liquidity, so the attacker could create a large Curve yPool price impact without holding the capital across blocks.

The attacker then swapped 17,222,012.640506 USDT into USDC inside Curve yPool. Harvest said this changed the relative value of USDC inside the pool because the other assets absorbed impermanent-loss effects. Immediately after that price-state change, the attacker deposited 49,977,468.555526 USDC into Harvest's USDC vault and received 51,456,280.788906 fUSDC at 0.97126080216 USDC per share. Harvest said the pre-attack share price was 0.980007 USDC, so the manipulated price lowered the deposit share price by about 1 percent and stayed inside the then-configured 3 percent arbitrage check.

The contract then swapped USDC back into USDT in Curve yPool, moving the pool state back, and withdrew from the Harvest USDC vault at 0.98329837664 USDC per share. Harvest calculated the USDC-cycle profit at 619,408.812299 USDC before flash-loan fees and said the attacker repeated the process several times in the same transaction. Harvest also reported 17 USDC-vault attack transactions within 4 minutes and 13 analogous USDT-vault transactions within another 3 minutes.

At 03:01:48 UTC, Harvest said the attacker transferred 13,000,000 USDC and 11,000,000 USDT from the attack contract to `0x3811765a53c3188c24d412daec3f60faad5f119b`. A later transaction returned 1,761,898.396474 USDC and 718,914.048541 USDT to the Harvest deployer. Etherscan labels the sender as Harvest.Finance: Hacker 1 and shows the same returned-token amounts.

## Economic Model

The representative USDC cycle in Harvest's post-mortem exposes the unit economics of the attack. The attacker deposited 49,977,468.555526 USDC and received 51,456,280.788906 fUSDC at 0.97126080216 USDC per share. The same fUSDC was later redeemed at 0.98329837664 USDC per share. The spread was 0.01203757448 USDC per fUSDC, which is about 1.24 percent of the manipulated deposit price and maps to Harvest's reported 619,408.812299 USDC profit before flash-loan fees.

That margin was large enough to survive plausible flash-loan fee assumptions. If the temporary inventory is treated as the full 68,308,555.417594 stablecoin balance sourced at the start of the transaction, a 0.09 percent flash-loan fee would cost about 61,478 stablecoins and leave roughly 557,931 USDC of profit on the sample USDC cycle. Even a 0.30 percent fee sensitivity would cost about 204,926 stablecoins and leave roughly 414,483 USDC before gas and swap fees. This was not a thin rounding exploit: the manipulated share-price spread was the dominant economic term.

The break-even fee on the representative cycle was about 0.91 percent of the temporary inventory, or 1.24 percent of the USDC deposit amount. A monitor could therefore flag any repeated vault deposit and redemption sequence where the expected share-price spread exceeds the all-in flash-liquidity and pool-reversal costs inside the same block.

## Market-Health Signals

### Depth-adjusted trade size

The initiating Curve yPool swap was large relative to the price state Harvest consumed. A surveillance rule should compare the trade size that moves an AMM pool against the depth and slippage tolerance of any dependent protocol. A large swap is not suspicious by itself, but it becomes a manipulation signal when the same actor immediately uses the resulting pool state to mint or redeem a derivative position elsewhere.

### Same-transaction price creation and consumption

The Harvest attack compressed price creation, vault deposit, price reversal, and vault withdrawal into a short transaction burst. That sequencing matters because it leaves little opportunity for external arbitrage to normalize the pool before the manipulated value is consumed. A market-health monitor should flag dependent-protocol accounting actions that occur in the same block or transaction group as the trades that moved the reference pool.

### Share-price discontinuity

Harvest reported that the USDC vault share price moved from 0.980007 to 0.834953 and that the USDT vault share price moved from 0.978874 to 0.844812. Those discontinuities are larger than the per-cycle arbitrage check that the attacker stayed under during individual deposits. For vaults, monitoring only a local deposit threshold can miss cumulative damage when the same manipulation pattern is repeated quickly.

### Why the 3 percent check failed

Harvest's protection compared the apparent arbitrage opportunity around an individual conversion against a 3 percent limit. The sample USDC deposit price of 0.97126080216 was only about 0.89 percent below the reported pre-attack price of 0.980007, so the deposit could pass the local check. The attacker then reversed the Curve trade and withdrew at 0.98329837664, creating a 1.24 percent deposit-to-withdrawal spread without ever requiring a single deposit to exceed the 3 percent threshold.

The failure mode was cumulative and atomic. The protocol treated each conversion as if the observed Curve state were a market condition, while the attacker treated the full transaction group as one trade: create the false state, mint shares, erase the false state, redeem shares, repeat. A market-health control should therefore aggregate same-actor, same-block share-price movement rather than evaluating each deposit in isolation.

### Outbound transfer reconciliation

The attack created several different loss numbers. Harvest's incident page describes a $24 million drain from the affected vaults. The post-mortem says 13 million USDC and 11 million USDT were transferred to the attacker's wallet, while the share-price drawdown produced about $33.8 million of value lost, or about 3.2 percent of total value locked before the attack. The returned funds then reduced the recoverable amount. A clean incident analysis should separate gross vault drawdown, attacker outbound transfers, returned funds, and user remediation accounting.

The stablecoins transferred out of the attack contract totaled 24,000,000. The returned amounts totaled 2,480,812.445015, leaving about 21,519,187.554985 stablecoins unrecovered from that outbound transfer path. That is distinct from the $33.8 million share-price drawdown number, which measures the accounting impact on vault depositors after the fUSDC and fUSDT share prices fell. The gap between those figures is important for datasets: one series describes attacker cash movement, while the other describes depositor balance impairment.

### Containment response

Harvest's incident page says the team moved remaining funds from shared pools back into vaults, disabled vulnerable conversions, and left reverts available. That response is useful as a market-health signal: if a strategy must exit a shared liquidity venue immediately after a price-state attack, the dependent accounting path was not robust to the venue's short-term manipulability.

## Comparative Analysis

Harvest fits the same broad family as bZx and Warp Finance flash-loan oracle manipulations, but the manipulated object was different. In bZx-style attacks, analysis by Meter and SlowMist describes attackers moving DEX or Kyber-derived prices so collateral or margin positions were valued too favorably. In Warp Finance's post-incident summary, the team described a flash-loan exploit caused by a gameable oracle that let the attacker withdraw a $7.76 million loan against collateral that was worth less than the borrowed assets.

Harvest did not simply ask, "What is this token worth on one DEX?" The vault used a Curve yPool balance state to decide how many fUSDC or fUSDT shares to mint and how much buffer asset to return. Curve's multi-asset stable pool made the manipulation look like an impermanent-loss and balance-allocation event rather than a visible spot-price spike. That made depth-adjusted pool composition, virtual-price movement, and vault share issuance part of the same surveillance problem.

The common pattern is cross-protocol atomicity. bZx consumed a manipulated market price, Warp consumed manipulated LP collateral value, and Harvest consumed a manipulated pool accounting state. The specific metric differs, but each case shows that a dependent protocol can convert a temporary venue imbalance into a permanent transfer when it accepts same-transaction observations as final accounting inputs.

## Detection Checklist

1. Track the largest trade size against pool depth for every AMM pool used as a vault pricing input.
2. Alert when the same address, contract, or funded transaction bundle both moves a reference pool and consumes that reference in a deposit, mint, withdrawal, or redemption.
3. Compare local arbitrage thresholds against cumulative same-block or same-window share-price movement.
4. Require a time-weighted or delayed price input for vault share issuance when the underlying strategy depends on a manipulable pool balance.
5. Separate gross accounting loss, realized attacker transfer, returned funds, and remediation claims in incident datasets.
6. Monitor buffer-only withdrawals that avoid interacting with the pool whose price state was just manipulated.
7. Treat flash-loan-funded inventory as temporary market depth, not as evidence of durable demand or liquidity.
8. Document emergency strategy exits as a signal that downstream protocols were relying on a venue state that could be moved by short-lived capital.
9. For Curve-style pools, alert on balance-vector changes that materially shift one asset's marginal withdrawal value even when the headline stablecoin price remains near par.
10. Compare vault share issuance against a delayed Curve virtual-price or pool-balance baseline, and flag deposits that mint materially more shares than the time-weighted baseline would allow.
11. Detect same-transaction signatures that contain the full loop: large pool imbalance, vault deposit, pool rebalance, vault withdrawal, and outbound transfer.
12. Track repeated sub-threshold arbitrage checks by actor and block, because a 1 percent local share-price edge repeated 30 times can be more damaging than one blocked 3 percent attempt.

## Controls and Mitigations

Harvest's post-mortem listed several mitigations that map directly to market-health controls. A commit-and-reveal deposit flow would split deposit and claim actions across transactions, reducing same-transaction extraction. A stricter arbitrage check could make each cycle less profitable, though Harvest noted that natural impermanent-loss effects can make overly tight thresholds impractical. Underlying-asset withdrawals would make the user receive the pool asset under current market conditions instead of receiving a buffer payout at a distorted accounting value. External oracle use was considered but not treated as a simple fix because a loose oracle-to-pool connection can create new arbitrage.

The broader control is to treat AMM pool state as a live market observation, not a neutral accounting fact. If a vault mints or redeems claims using an AMM balance that can be moved by a flash loan, the vault should either delay the observation, smooth it, cap its effect, or require the user to bear the manipulated pool state directly. Otherwise the protocol can turn a temporary pool imbalance into a permanent transfer from passive depositors to the manipulator.

For Harvest specifically, commit-and-reveal would have attacked the transaction ordering assumption. If deposits minted pending shares and only finalized after a later block, the attacker could not guarantee that the Curve yPool imbalance used at deposit time would still be present or reversible at withdrawal time. Even a short delay of 5 to 10 blocks would force the strategy to carry price risk across public mempool time instead of extracting the spread atomically.

Underlying-asset withdrawals would have changed the sample USDC cycle more directly. The attacker earned the spread between 0.97126080216 and 0.98329837664 USDC per fUSDC because withdrawal paid from a buffer after the pool state was reversed. If the redemption instead forced the attacker to receive the proportional yPool exposure at the manipulated state, the attacker would internalize the Curve imbalance rather than externalizing it to passive vault depositors. In the representative cycle, that design would target the 0.01203757448 USDC-per-share spread that produced the 619,408.812299 USDC gross profit.

The arbitrage check also needed a global circuit breaker. A per-deposit cap could remain at 3 percent to avoid blocking normal impermanent-loss noise, but it should be paired with a rolling cap such as a 0.5 percent to 1 percent same-block share-price movement limit per vault, plus a pause when a single actor repeatedly enters and exits through the same reference pool. A 10 to 30 minute TWAP or delayed pool-balance baseline would not remove all oracle risk, but it would reduce the value of a one-transaction Curve imbalance because the attacker would need to hold capital and inventory risk long enough for external arbitrage to respond.

## References

- [Harvest incident page: fUSDC/fUSDT Economic Attack Oct 26 2020](https://docs.harvest.finance/other/security/incidents/fusdc-fusdt-economic-attack-oct-26-2020)
- [Harvest Flashloan Economic Attack Post-Mortem](https://medium.com/harvest-finance/harvest-flashloan-economic-attack-post-mortem-3cf900d65217)
- [Harvest GRAIN token remediation page](https://docs.harvest.finance/archive/archived/grain-token)
- [Etherscan transaction returning USDC and USDT to Harvest deployer](https://etherscan.io/tx/0x25119cd54a4562aa427d9770af383512f9cb5e8e4d17232ad96b69dc293a3510)
- [The Chain Bulletin summary of the Harvest Finance exploit](https://chainbulletin.com/harvest-finance-exploit-explained-team-announces-plan-of-action)
- [Meter analysis of the bZx oracle attacks](https://medium.com/meter-io/the-bzx-attacks-what-went-wrong-and-the-role-oracles-played-in-the-exploits-264619b9597d)
- [SlowMist analysis of the bZx attacks](https://slowmist.medium.com/introduction-ca09c9b32b1b)
- [Warp Finance exploit summary and recovery of funds](https://warpfinance.medium.com/warp-finance-exploit-summary-recovery-of-funds-5b8fe4a11898)
