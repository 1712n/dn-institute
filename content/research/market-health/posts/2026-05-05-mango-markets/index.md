---
title: "🥭 Mango Markets — Oracle Manipulation and Governance Settlement"
date: 2026-05-05
entities:
  - Mango Markets
  - MNGO
  - Solana
  - Avraham Eisenberg
  - AscendEX
  - FTX
---

## Summary

1. **On October 11, 2022, Mango Markets was drained of more than $110 million in crypto assets after a coordinated price-and-collateral manipulation of the MNGO market.** The attacker used large MNGO perpetual futures positions and spot purchases in thin external markets to move the oracle price that Mango used to value collateral.
2. **The manipulation exploited a cross-market feedback loop**: MNGO spot trades on external venues affected the oracle, the oracle repriced MNGO-PERP positions on Mango, and the inflated account equity allowed the attacker to borrow and withdraw most of the protocol's available assets.
3. **The target asset was structurally vulnerable.** MNGO was thinly traded relative to the size of the borrowable liquidity pool behind Mango. A few million dollars of concentrated buying was enough to move the oracle-relevant market price by more than an order of magnitude for a short period.
4. **The post-exploit governance settlement became part of the attack surface.** Mango DAO accepted a proposal under which roughly $67 million was returned while the attacker kept roughly $47 million, after the proposal asked the DAO not to pursue criminal investigations or freeze funds.
5. **The incident is a canonical DeFi market-manipulation case** because it combined order-book manipulation, oracle design weakness, margin-system design, lending liquidity, and emergency DAO governance under duress.

## Background

### Mango Markets

Mango Markets was a Solana-based decentralized exchange and lending protocol offering spot trading, perpetual futures, margin trading, and borrowing. Users could deposit assets, trade with leverage, and borrow against the value of their account equity. The protocol's risk engine depended on oracle prices to mark collateral and liabilities.

### MNGO

MNGO was Mango's governance token. It had a much smaller and thinner market than the stablecoins and major crypto assets available inside Mango's lending pools. That mismatch mattered: when a protocol lets a thinly traded token affect borrowing capacity against a deep pool of liquid assets, the cost of manipulating the collateral price can be far lower than the value that can be extracted.

### Why the Case Fits Market Manipulation

The Mango incident was not a conventional private-key theft. It was a market-structure exploit:

| Layer | Weakness |
|------|----------|
| Spot market | MNGO liquidity was thin enough to move rapidly |
| Perpetual market | A very large MNGO-PERP position could create large mark-to-market account equity |
| Oracle | External and internal market prices fed the value used by Mango's risk engine |
| Lending pool | Inflated equity could be converted into withdrawals of stablecoins and other assets |
| Governance | A settlement vote occurred while the protocol and depositors were under pressure |

The result looked like a lending drain, but the mechanism was price formation and collateral valuation.

## Timeline

| Date / Time | Event |
|------------|-------|
| October 11, 2022 | Two Mango accounts were funded with about $5 million USDC each |
| October 11, 2022 | One account sold a very large MNGO-PERP position while another bought it |
| Minutes later | Concentrated MNGO spot purchases occurred on Mango and external exchanges |
| Same window | MNGO's oracle-reported price rose sharply, increasing the marked value of the long MNGO-PERP account |
| October 11, 2022 | The account used inflated equity to borrow and withdraw over $110 million in assets |
| After the drain | Mango DAO considered and accepted a settlement proposal returning part of the funds |
| December 2022-January 2023 | U.S. criminal and civil actions were filed against Avraham Eisenberg |

Solidus Labs' order-book analysis describes the market sequence as unfolding in roughly 40 minutes. The CFTC complaint describes the oracle price jumping more than 13-fold in a 30-minute span. The SEC complaint describes approximately $116 million withdrawn from the platform.

## Manipulation Mechanics

### Step 1: Create a Large Perpetual Futures Position

The attacker used two Mango accounts to create offsetting MNGO-PERP exposure. One account sold a large quantity of MNGO perpetual futures; another bought the same exposure. The key account was the long side, because a rising MNGO oracle price would create large unrealized profit on that position.

This design matters because the account did not need to sell the long position to realize the mark-to-market benefit. Mango's risk engine treated the increased value as account equity that could support borrowing.

### Step 2: Move the MNGO Spot Price

The attacker then bought MNGO in size on markets that influenced the oracle price. Public analyses cite purchases on Mango and on centralized venues including AscendEX and FTX. Solidus Labs reported that roughly $4 million of MNGO purchases across multiple venues helped move the oracle-reported price dramatically within minutes.

The important feature was not the absolute dollar amount. It was the ratio between:

- the cost required to move MNGO's market price;
- the size of the MNGO-PERP position being marked by the oracle;
- the amount of liquid collateral available to borrow from Mango.

When those three values are misaligned, a manipulator can spend a comparatively small amount moving a thin market and use the resulting mark-to-market equity to extract a much larger amount elsewhere.

### Step 3: Convert Inflated Equity into Withdrawals

After the oracle price rose, the long MNGO-PERP account appeared highly profitable. Mango's risk engine allowed that account to borrow against the inflated value. The account then withdrew available assets from the protocol, including stablecoins and major crypto assets.

The withdrawal step transformed a temporary price distortion into a protocol solvency event. When MNGO's price returned toward normal levels, the mark-to-market equity disappeared, but the borrowed assets had already left the platform.

### Step 4: Use Governance to Negotiate the Aftermath

After the drain, Mango DAO received a governance proposal that offered to return a portion of the assets while allowing the attacker to retain a large amount as a claimed bounty. The CFTC later described the proposal as conditioning return of funds on Mango agreeing not to pursue criminal investigations or freeze funds. The CFTC also stated that approximately $67 million was returned and approximately $47 million retained.

This was a second-order market-structure problem: governance voting became an emergency claims process while the protocol was impaired and depositors wanted fast recovery.

## Data Points and Indicators

### Price Movement

Regulatory and independent analyses describe an extreme short-window price move:

- The CFTC alleged that the oracle-reported MNGO price rose more than 13-fold in about 30 minutes.
- Solidus Labs reported that Mango prices fluctuated between roughly 10x and 30x their previous-day level during the manipulation window.
- The SEC alleged that large MNGO purchases artificially raised the MNGO price relative to USDC, increasing the value of MNGO perpetual futures held by the attacker.

For surveillance purposes, the exact peak price is less important than the shape: a thin governance token experienced a sudden multi-venue price spike at the same time as a large derivatives position benefited from that spike.

### Position and Liquidity Mismatch

The most important risk metric was the mismatch between open interest and spot liquidity:

| Metric | Risk Signal |
|-------|-------------|
| MNGO spot depth | Too shallow to support the size of marked derivatives exposure |
| MNGO-PERP open interest | Large enough that oracle movement produced huge unrealized profit |
| Borrowable protocol assets | Deep enough to make the manipulated equity economically useful |
| Oracle reaction speed | Fast enough to credit the temporary spike before markets normalized |
| Withdrawal controls | Not restrictive enough to pause extraction during abnormal price movement |

A healthy risk engine should treat thin-token collateral and derivatives profits as lower quality collateral when the underlying spot market cannot absorb liquidation at comparable size.

### Cross-Venue Coordination

The case also shows why single-venue surveillance is insufficient. A venue can look internally consistent while its oracle inputs are being manipulated elsewhere. Mango's risk engine consumed a price affected by activity on multiple markets; therefore, surveillance needed to correlate:

- external spot buys;
- internal perp position changes;
- oracle updates;
- account equity changes;
- borrow and withdrawal requests.

The manipulation became obvious only when these layers were viewed together.

## Oracle Design Lessons

### Liquidity-Weighted Pricing

Oracles that use market prices for thin assets need liquidity-aware safeguards. A price sourced from an exchange is not automatically a reliable collateral value. It should be discounted or capped when the trade size required to move the price is small relative to the protocol exposure that price controls.

Useful controls include:

1. **Depth-adjusted collateral haircuts** for thinly traded assets.
2. **Open-interest caps** that scale with reliable spot-market depth.
3. **Price impact limits** that cap how quickly a token's collateral value can rise.
4. **Separate mark and borrow prices**, where a token can be marked for PnL but not immediately used at full value for borrowing.
5. **Withdrawal throttles** triggered by extreme oracle moves.

### Time-Weighted Prices Are Not Enough

Time weighting reduces single-block manipulation, but it does not fully solve a multi-minute cross-market pump. If a manipulator can sustain the distorted price for the oracle window, the protocol may still accept an artificial value. Time-weighted prices are strongest when paired with depth checks, position limits, and circuit breakers.

### Perp PnL Should Not Equal Cash Collateral

The Mango attack depended on unrealized derivatives profit becoming usable collateral before it could be safely liquidated. Risk engines should distinguish:

- realized stablecoin deposits;
- high-liquidity collateral such as major assets;
- governance-token collateral;
- unrealized PnL on thin-token derivatives;
- PnL generated during abnormal market conditions.

Treating all account equity as equally borrowable makes manipulation easier.

## Governance Lessons

### Emergency Votes Are Vulnerable

Mango's settlement vote took place after the protocol had already been drained. Depositors had strong incentives to recover whatever assets could be recovered quickly. That environment is not normal governance. It is closer to a distressed settlement negotiation.

When governance can be used to ratify post-exploit terms, protocols should require:

- emergency quorum rules that exclude attacker-controlled voting power where possible;
- predefined incident response playbooks;
- independent legal and security review before settlement votes;
- clear separation between bounty programs and coerced recovery proposals;
- public accounting of recovered, retained, and unrecovered funds.

### "Bug Bounty" Framing Can Be Abused

Bug bounties are designed to reward disclosure without harming users. A drain followed by a demand to keep tens of millions of dollars is different. Protocols should define maximum bounty amounts, eligibility rules, safe-harbor conditions, and disqualifying conduct before an incident occurs.

Without clear rules, attackers can frame extraction as negotiation and force governance voters into choosing between partial recovery and prolonged uncertainty.

## Surveillance Framework

Mango-style manipulation can be monitored with a combined market and protocol-risk dashboard.

### Pre-Trade / Design-Time Metrics

| Metric | Warning Threshold |
|-------|-------------------|
| Borrowable value controlled by thin-token collateral | High relative to reliable spot depth |
| Perp open-interest cap | Exceeds plausible liquidation capacity |
| Oracle venue concentration | Few venues or shallow books dominate price |
| Collateral haircut | Too low for governance tokens or illiquid assets |
| Account equity from unrealized PnL | Treated the same as stable collateral |

### Real-Time Incident Metrics

| Metric | Mango-Style Signal |
|-------|-------------------|
| Spot price velocity | Multi-sigma move in minutes |
| Cross-venue buy concentration | Same asset bought aggressively across oracle venues |
| Perp account PnL | One account's equity rises primarily from the manipulated asset |
| Borrow request size | Large withdrawal immediately after oracle spike |
| Oracle/withdrawal coupling | Borrowing follows the oracle move before price normalizes |

### Post-Incident Metrics

| Metric | Why It Matters |
|-------|----------------|
| Returned amount | Measures depositor recovery, not exploit severity |
| Retained amount | Measures economic incentive for copycats |
| Governance vote concentration | Indicates whether settlement was broadly supported or captured |
| Protocol restart liquidity | Shows whether user confidence returned |
| Legal/regulatory actions | Shows enforcement risk for similar conduct |

## Comparison With Other Manipulation Cases

| Case | Manipulation Vector | Shared Pattern |
|-----|---------------------|----------------|
| Mango Markets | Thin-token oracle and perp PnL inflated borrowing power | Oracle-reported value exceeded realizable market value |
| bZx | Flash-loan price manipulation | Temporary price distortion converted into protocol loss |
| Harvest Finance | Curve pool imbalance manipulated vault accounting | Accounting accepted distorted pool state |
| Cream Finance | yUSDVault share accounting manipulated collateral value | Inflated collateral supported under-collateralized borrowing |
| Beanstalk | Flash-loan governance takeover | Governance process converted temporary voting power into control |

The common theme is not simply "bad oracle." It is a protocol accepting a temporary, manipulable state as if it were durable economic value.

## Defensive Checklist

Protocols listing thin assets as collateral or derivatives underlyings should ask:

1. Can a trader move the oracle price with less capital than they can borrow?
2. Is open interest capped by external market depth?
3. Does unrealized PnL become immediately borrowable?
4. Are borrow limits reduced during abnormal price velocity?
5. Are oracle venues monitored for coordinated activity?
6. Can withdrawals be delayed when account equity changes too quickly?
7. Are governance-token markets treated as lower-quality collateral?
8. Is there a predefined recovery process that avoids ad hoc settlement votes?

If any answer is weak, the protocol is exposed to Mango-style manipulation.

## Key Takeaways

1. **Thin collateral can endanger deep liquidity.** A small market should not control borrowing against a large pool.
2. **Oracle correctness is not only about data freshness.** It is also about whether the reported price is economically realizable at relevant size.
3. **Unrealized derivatives PnL is risky collateral.** It can disappear when manipulated prices normalize.
4. **Cross-venue monitoring is mandatory.** Manipulation may happen outside the protocol while losses occur inside it.
5. **Governance cannot replace incident planning.** Emergency votes under duress can become part of the exploit path.
6. **Partial recovery does not erase manipulation.** Returned funds reduce depositor losses, but retained profit can still incentivize copycats.

## References

- CFTC, "CFTC Charges Avraham Eisenberg with Manipulative and Deceptive Scheme to Misappropriate Over $110 Million from Mango Markets" (January 2023).
- SEC, "SEC Charges Avraham Eisenberg with Manipulating Mango Markets' MNGO Token" (January 2023).
- Solidus Labs, "The Mango Markets Exploit: An Order Book Analysis" (October 2022).
- Mango Markets governance records and public post-incident settlement discussions.
