---
title: "USDC SVB Depeg Contagion"
date: 2023-03-11
entities:
  - Circle
  - USDC
  - Silicon Valley Bank
  - DAI
  - MakerDAO
---

## Summary

On March 10-13, 2023, USDC temporarily lost its dollar peg after Circle disclosed reserve exposure to Silicon Valley Bank. [Circle said](https://www.circle.com/blog/an-update-on-usdc-and-silicon-valley-bank) that $3.3 billion of roughly $40 billion of USDC reserves remained at SVB after transfers initiated before the bank entered receivership were not settled.

[CoinDesk reported](https://www.coindesk.com/markets/2023/03/11/usdc-stablecoin-depegs-from-1-circle-says-operations-are-normal) that USDC depegged as contagion from SVB spread. [A later CoinDesk report](https://www.coindesk.com/business/2023/03/13/usdc-stablecoin-regains-dollar-peg-after-silicon-valley-bank-induced-chaos) said USDC regained its peg after federal banking regulators said all SVB depositors would be made whole and Circle said the trapped reserve deposit would be available.

The market-health issue was reserve venue concentration and stablecoin dependency. USDC was not just a payment asset; it was also collateral, liquidity, and accounting inventory across DeFi. As USDC traded below $1, assets and protocols that depended on USDC as near-cash collateral inherited the same confidence shock. This article treats the episode as an in-scope Market Health stress event: not manipulation by a single trader, but a case where market-participant incentives, liquidity routing, and collateral dependencies transmitted an off-chain reserve shock into on-chain prices.

## Risk Transmission Analysis

The first stress vector was reserve concentration crossing a confidence threshold. Circle disclosed $3.3 billion at SVB, about 8.25% of the roughly $40 billion reserve base cited in its update. That share was small enough that full recovery would likely restore confidence, but large enough that weekend markets could not ignore it. Secondary markets therefore priced USDC as a claim with uncertain recovery timing rather than as immediately fungible cash.

The second vector was redemption timing and market-maker inventory. USDC trades continuously, but bank settlement, issuer wires, and large-scale redemptions depended on weekday banking rails. During the weekend gap, market makers faced uncertainty about how much inventory they could redeem, when they could settle, and whether they would be compensated for absorbing sell pressure. That pulled liquidity away from the peg exactly when sellers most needed it.

The third vector was DeFi collateral contagion. DAI and other DeFi assets with USDC exposure transmitted USDC-specific reserve stress into separate markets. [CoinDesk reported](https://www.coindesk.com/markets/2023/03/11/dai-depegs-as-stablecoin-rout-plagues-crypto) that DAI hit an all-time low of 88 cents as the stablecoin rout spread. [MakerDAO wrote](https://blog.makerdao.com/daidollar-is-back-on-peg/) that DAI returned to peg after the USDC disruption, highlighting the dependency between DAI stability and USDC market confidence.

The fourth vector was pool imbalance and flight-to-quality routing. Stablecoin AMMs and lending venues need to know when one dollar-like asset is no longer priced as equivalent to the others. A pool can remain operational while the asset mix becomes a live stress signal. [Later CoinDesk reporting on stablecoin pool imbalances](https://www.coindesk.com/markets/2023/08/03/traders-ditch-usdt-on-curve-uniswap-pushing-key-exchange-pools-into-imbalance) noted that, during the March USDC shock, USDC and DAI each rose above 45% of Curve 3pool balances, meaning traders were routing away from those assets and into alternatives rather than treating the pool as three equivalent dollars.

## Metrics Used

### Reserve venue concentration

The primary signal is how much backing depends on each off-chain financial institution. In this case, the specific concentration metric was $3.3 billion divided by roughly $40 billion of reserves, or about 8.25% of the reserve base temporarily tied to SVB settlement risk.

Useful metrics include:

- reserve amount by banking partner;
- reserve share by banking partner;
- unsettled transfer amount;
- access status by reserve venue;
- reserve asset maturity and liquidity profile.

### Peg and redemption stress

Market price should be measured together with redemption availability. CoinDesk's spot-market coverage said USDC/USDT fell as low as 94 cents on Kraken, while [CryptoCompare's March 2023 stablecoin report](https://www.cryptocompare.com/media/44081939/stablecoin-report-march-2023.pdf) put the broader USDC low near $0.877 on March 11. Those two numbers measure different venues and aggregation methods, but together they show that the event was not merely a tiny spread around par.

Useful metrics include:

- USDC price deviation from $1;
- discount duration below 99 cents and 95 cents;
- redemption queue size;
- mint and burn volume;
- time between bank-market resolution and stablecoin repeg.

### DeFi contagion

Protocols that treat USDC as cash-equivalent need dependency dashboards. DAI was the key transmission example: CoinDesk reported an 88-cent DAI low, and MakerDAO later wrote that DAI returned to peg after USDC stabilized. That means the same reserve shock affected both the primary stablecoin and a derivative stablecoin that used USDC as part of its peg and collateral design.

Useful metrics include:

- DAI and other derivative stablecoin price deviation;
- share of protocol collateral backed directly or indirectly by USDC;
- liquidations caused by stablecoin price deviation;
- lending-market utilization for USDC, DAI, USDT, and ETH;
- stablecoin swap volume and slippage.

### Pool imbalance and flight-to-quality

Stablecoin pools show whether users are trying to exit one asset into another. A useful threshold rule is to flag any three-stablecoin pool when one leg rises above 45% or when two correlated legs rise above 45% each. The March 2023 USDC event crossed that second form because USDC and DAI both became overweight in Curve 3pool, showing a shared confidence problem rather than a neutral pool rebalance.

Useful metrics include:

- stablecoin pool asset composition;
- USDC share of pool balances;
- swap volume from USDC into USDT, DAI, ETH, and fiat ramps;
- one-sided liquidity withdrawal velocity;
- price impact for large USDC exits.

The same fields are summarized in [usdc-svb-depeg-signals.csv](usdc-svb-depeg-signals.csv) for dataset-based review.

| Signal                 | Observation                                                                                                                                       | Market-health interpretation                                                |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| svb_reserve_exposure   | Circle said that $3.3 billion of roughly $40 billion of USDC reserves remained at Silicon Valley Bank                                             | Track reserve venue concentration and unresolved banking exposure           |
| secondary_market_depeg | CoinDesk reported that USDC depegged as contagion from Silicon Valley Bank spread                                                                 | Monitor stablecoin market-price deviation and discount duration             |
| peg_recovery           | CoinDesk reported that USDC regained its peg after regulators said SVB depositors would be made whole and Circle said deposits would be available | Measure time from reserve-resolution signal to secondary-market repeg       |
| dai_contagion          | MakerDAO wrote that DAI returned to peg after the USDC disruption                                                                                 | Track derivative stablecoin exposure to USDC reserve confidence             |
| reserve_risk_removed   | Circle said the $3.3 billion USDC reserve deposit held at Silicon Valley Bank would be fully available                                            | Compare issuer reserve updates against market repeg and redemption behavior |

## Timeline

- **March 10, 2023:** Silicon Valley Bank entered receivership, and Circle later disclosed that $3.3 billion of USDC reserves remained at SVB.
- **March 11, 2023:** USDC depegged in secondary markets as holders repriced reserve-access uncertainty. CoinDesk reported USDC/USDT as low as 94 cents on Kraken, while DAI fell to 88 cents as contagion reached USDC-dependent collateral systems.
- **March 12-13, 2023:** Regulators announced depositor protection for SVB, and [Circle said](https://www.circle.com/pressroom/3-3-billion-of-usdc-reserve-risk-removed-dollar-de-peg-closes) the $3.3 billion reserve-risk issue was removed. USDC's recovery showed that the market was pricing access timing and legal certainty, not only reserve arithmetic.
- **After the repeg:** DeFi protocols reviewed stablecoin exposure, reserve concentration, and emergency parameters for assets that had treated USDC as equivalent to dollars.

## Market Health Lessons

USDC's SVB depeg shows that stablecoin health is a joint on-chain and off-chain system. Reserve attestations, banking counterparties, redemption windows, pool balances, and dependent collateral systems all need to be monitored together.

For Market Health, the useful model is a two-threshold contagion rule. First, flag reserve-access stress when any single banking partner holds more than a protocol-defined reserve share and access becomes uncertain. Second, escalate the alert when secondary-market price, derivative stablecoins, or AMM pool weights confirm that users are treating the asset as impaired. In March 2023, both thresholds fired: Circle's $3.3 billion SVB exposure created the access shock, and USDC price discounts, DAI's 88-cent low, and Curve 3pool imbalance confirmed the on-chain transmission path.

If a protocol depends on USDC for collateral, liquidity, or price stability, then it should track USDC reserve distribution, redemption status, AMM imbalances, and derivative stablecoin exposure as first-class risk signals.
