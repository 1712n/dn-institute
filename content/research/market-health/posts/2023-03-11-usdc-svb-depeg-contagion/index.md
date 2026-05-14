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

The market-health issue was reserve venue concentration and stablecoin dependency. USDC was not just a payment asset; it was also collateral, liquidity, and accounting inventory across DeFi. As USDC traded below $1, assets and protocols that depended on USDC as near-cash collateral inherited the same confidence shock.

## Manipulation Analysis

The first stress vector was off-chain reserve concentration. A fiat-backed stablecoin can be fully intended to redeem at $1 while still facing short-term uncertainty if a meaningful reserve slice is trapped at a failed banking partner.

The second vector was redemption timing. USDC trades around the clock, but banking rails do not. During the weekend gap, secondary-market sellers repriced USDC before ordinary banking resolution and redemption could fully reopen.

The third vector was DeFi collateral contagion. DAI and other DeFi assets with USDC exposure can transmit USDC-specific reserve stress into separate markets. [MakerDAO wrote](https://blog.makerdao.com/daidollar-is-back-on-peg/) that DAI returned to peg after the USDC disruption, highlighting the dependency between DAI stability and USDC market confidence.

The fourth vector was pool imbalance. Stablecoin AMMs and lending venues need to know when one dollar-like asset is no longer priced as equivalent to the others. A pool can remain operational while the asset mix becomes a live stress signal.

## Metrics Used

### Reserve venue concentration

The primary signal is how much backing depends on each off-chain financial institution.

Useful metrics include:

- reserve amount by banking partner;
- reserve share by banking partner;
- unsettled transfer amount;
- access status by reserve venue;
- reserve asset maturity and liquidity profile.

### Peg and redemption stress

Market price should be measured together with redemption availability.

Useful metrics include:

- USDC price deviation from $1;
- discount duration below 99 cents and 95 cents;
- redemption queue size;
- mint and burn volume;
- time between bank-market resolution and stablecoin repeg.

### DeFi contagion

Protocols that treat USDC as cash-equivalent need dependency dashboards.

Useful metrics include:

- DAI and other derivative stablecoin price deviation;
- share of protocol collateral backed directly or indirectly by USDC;
- liquidations caused by stablecoin price deviation;
- lending-market utilization for USDC, DAI, USDT, and ETH;
- stablecoin swap volume and slippage.

### Pool imbalance and flight-to-quality

Stablecoin pools show whether users are trying to exit one asset into another.

Useful metrics include:

- stablecoin pool asset composition;
- USDC share of pool balances;
- swap volume from USDC into USDT, DAI, ETH, and fiat ramps;
- one-sided liquidity withdrawal velocity;
- price impact for large USDC exits.

The same fields are summarized in [usdc-svb-depeg-signals.csv](usdc-svb-depeg-signals.csv) for dataset-based review.

| Signal                 | Observation                                                       | Market-health interpretation                                       |
| ---------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------ |
| SVB reserve exposure   | Circle disclosed $3.3 billion of USDC reserves at SVB             | Reserve venue concentration can become stablecoin market risk      |
| Weekend redemption gap | USDC traded continuously while bank access was unresolved         | Off-chain settlement hours can amplify on-chain price stress       |
| Peg recovery           | USDC regained peg after depositor protection and Circle updates   | Resolution timing links policy actions to stablecoin market depth  |
| DAI contagion          | MakerDAO discussed DAI returning to peg after the USDC disruption | USDC-backed derivative stablecoins inherit reserve confidence risk |
| Public stress signal   | Public incident tracking flagged the USDC depeg after SVB failure | External confidence signals can precede protocol parameter action  |

## Timeline

- **March 10, 2023:** Silicon Valley Bank entered receivership, and Circle later disclosed that $3.3 billion of USDC reserves remained at SVB.
- **March 11, 2023:** USDC depegged in secondary markets as holders repriced reserve-access uncertainty.
- **March 12-13, 2023:** Regulators announced depositor protection for SVB, and [Circle said](https://www.circle.com/pressroom/3-3-billion-of-usdc-reserve-risk-removed-dollar-de-peg-closes) the $3.3 billion reserve-risk issue was removed.
- **After the repeg:** DeFi protocols reviewed stablecoin exposure, reserve concentration, and emergency parameters for assets that had treated USDC as equivalent to dollars.

## Market Health Lessons

USDC's SVB depeg shows that stablecoin health is a joint on-chain and off-chain system. Reserve attestations, banking counterparties, redemption windows, pool balances, and dependent collateral systems all need to be monitored together.

For Market Health, the lesson is to model stablecoin contagion before the reserve venue fails. If a protocol depends on USDC for collateral, liquidity, or price stability, then it should track USDC reserve distribution, redemption status, AMM imbalances, and derivative stablecoin exposure as first-class risk signals.
