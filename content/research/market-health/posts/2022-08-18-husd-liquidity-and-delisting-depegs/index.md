---
title: "HUSD Liquidity Shock and Huobi Delisting Depegs"
date: 2022-08-18
entities:
  - HUSD
  - Stable Universal
  - Huobi
  - USDT
---

## Summary

On August 18, 2022, HUSD lost its $1 peg despite being described as a cash-backed stablecoin. [CoinDesk reported](https://www.coindesk.com/markets/2022/08/18/cash-backed-husd-stablecoin-loses-peg-drops-to-092) that HUSD fell to $0.92, about an 8% discount from par. The next day, [CoinDesk reported](https://www.coindesk.com/business/2022/08/19/husd-stablecoin-returns-to-1-peg-after-liquidity-problems) that HUSD had returned to $1 after the HUSD team attributed the depeg to account closures, including market-maker accounts, that created a short-term liquidity problem.

The risk did not disappear after the August repeg. [CoinDesk reported](https://www.coindesk.com/business/2022/10/27/crypto-exchange-huobi-delists-its-husd-stablecoin) in October 2022 that Huobi would delist HUSD and convert user balances into USDT. Days later, [CoinDesk reported](https://www.coindesk.com/business/2022/10/31/after-huobi-delisting-stablecoin-husd-falls-72-from-dollar-peg) that HUSD had fallen as low as $0.28 after the delisting announcement, while its market cap had fallen sharply from its 2021 peak.

The HUSD case is useful for Market Health because it shows how a cash-backed stablecoin can still break its peg when liquidity rails, market makers, and venue support weaken. Backing may support ultimate redemption, but secondary-market holders price what they can actually sell or convert at the time of stress.

## Metrics Used

### Market-maker availability

HUSD's August depeg was publicly attributed to market-maker account closures and time-zone delays in banking or liquidity operations. That makes market-maker coverage a direct stablecoin health signal. A stablecoin can appear fully backed yet trade below par if the agents that normally arbitrage the discount cannot provide liquidity.

Useful market-maker metrics include:

- active market-maker account count by venue;
- market-maker inventory available for peg defense;
- time since last successful large redemption or conversion;
- time-zone and banking-hour gaps in liquidity coverage;
- quote depth within 10, 50, and 100 basis points of par.

### Venue dependence

HUSD was closely linked to Huobi, which marketed and supported it even though Stable Universal issued it. When Huobi announced delisting and conversion into USDT, HUSD lost a major source of venue utility. A stablecoin whose demand is concentrated on one exchange is exposed to that exchange's listing, conversion, and marketing decisions.

Venue-dependence metrics include:

- share of volume on the largest venue;
- number of active trading pairs by venue;
- pending delistings or conversion programs;
- deposit and withdrawal availability;
- price spread between the dominant venue and external markets.

### Peg severity and repeat depegs

The August move to $0.92 and October move toward $0.28 are different classes of stress. The first was a temporary liquidity shortfall with a fast recovery. The second reflected a deeper utility and market-access shock after delisting. Tracking both events together shows whether a stablecoin's liquidity system is becoming less resilient.

Useful peg metrics include:

- lowest trade price during each depeg window;
- time to recover to $0.99 or $1;
- depth required to restore the peg;
- whether recovery comes from normal arbitrage or forced conversion;
- market cap before and after each event.

### Backing versus tradability

HUSD's case separates backing confidence from tradability. Even if tokens are fully backed, holders who cannot directly redeem, cannot access a market maker, or lose the main exchange venue may sell at a discount. Market-health monitoring should therefore track operational redemption access and venue liquidity alongside reserve claims.

The same fields are summarized in [husd-signals.csv](husd-signals.csv) for dataset-based review.

| Signal                     | Observation                                                | Market-health interpretation                                       |
| -------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------ |
| August peg low             | HUSD fell to about $0.92                                   | Cash-backed tokens can still depeg during liquidity gaps           |
| Market-maker account shock | Issuer cited account closures including market makers      | Peg defense depends on active liquidity providers                  |
| Fast August repeg          | Huobi said the peg was restored within roughly 12 hours    | Liquidity repair can close a mild depeg if venue support remains   |
| Huobi delisting            | Huobi announced HUSD delisting and conversion into USDT    | Venue utility loss can weaken stablecoin demand                    |
| October collapse           | HUSD later fell as low as about $0.28 after delisting news | Delisting stress can be far more severe than temporary illiquidity |

## Timeline

- **August 18, 2022:** HUSD fell to about $0.92 as liquidity problems disrupted peg support.
- **August 19, 2022:** HUSD returned to $1 after the issuer cited account closures and a short-term liquidity problem.
- **October 27, 2022:** Huobi announced that it would delist HUSD and convert user balances into USDT.
- **October 31, 2022:** HUSD fell as low as about $0.28 after the delisting announcement.
- **After October 2022:** HUSD remained a case study in venue dependence, market-maker continuity, and the gap between reserve backing and market liquidity.

## Market Health Lessons

HUSD shows that stablecoin monitoring should not stop at reserve backing. The market also needs liquidity providers, redemption access, venue support, and clear conversion paths. When those operational layers weaken, even a cash-backed stablecoin can trade far below par.

For stablecoin health dashboards, market-maker coverage, dominant-venue concentration, delisting risk, deposit and withdrawal availability, and time-to-repeg are essential signals. Reserve attestations answer whether backing may exist; liquidity and venue metrics answer whether holders can actually exit near $1 under stress.
