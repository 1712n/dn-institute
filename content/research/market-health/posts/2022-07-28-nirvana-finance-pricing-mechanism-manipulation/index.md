---
title: "Nirvana Finance ANA Pricing Mechanism Manipulation"
date: 2022-07-28
entities:
  - Nirvana Finance
  - ANA
  - NIRV
  - Solend
  - USDC
  - USDT
  - Wormhole
  - Ethereum
---

## Summary

Nirvana Finance was drained on July 28, 2022 after an attacker used flash-loan liquidity to exploit the protocol's own ANA pricing mechanism. Instead of manipulating an external exchange quote and waiting for a separate oracle to read it, the attacker exploited a smart-contract path that let a large ANA purchase be priced too cheaply. The same purchase then moved Nirvana's internal price curve upward, allowing the attacker to sell the ANA back to the protocol at the higher price.

CertiK estimated attacker profit at about 3,574,635 USD and reported that the ANA token price collapsed about 85%. Nirvana's own recovery update later described approximately 3.5 million USD in stablecoins drained from reserves, nearly all funds possessed by the protocol, and said the loss forced Nirvana to shut down shortly after the attack. The U.S. Department of Justice later identified the attacker as Shakeeb Ahmed and described the case as part of the first conviction for a smart-contract hack.

The main warning signs were:

1. a protocol-owned market whose quote could be moved and settled inside one transaction,
2. a pricing function that undercharged a very large ANA purchase,
3. flash-loan notional far larger than ordinary user demand,
4. immediate resale into protocol reserves after the price curve moved,
5. post-attack stablecoin bridging from Solana to Ethereum.

## Incident Metrics

The supporting dataset is stored in [`nirvana-attack-metrics.csv`](nirvana-attack-metrics.csv). It separates funding, price movement, reserve-drain, and legal-resolution signals so this case can be compared with other market-manipulation incidents.

| Metric                   |              Value | Market-health interpretation                                                     |
| ------------------------ | -----------------: | -------------------------------------------------------------------------------- |
| Flash-loan funding       |    10,250,000 USDC | Same-transaction capital was used to force the protocol market into a new state. |
| Initial ANA price signal |        about 8 USD | The attacker obtained ANA at the low side of the manipulated pricing path.       |
| Manipulated ANA price    | about 24-24.27 USD | The purchase moved the internal market price upward before resale.               |
| Attacker profit estimate |      3,574,635 USD | CertiK's estimate of value retained after the flash-loan cycle.                  |
| Treasury swap amount     |     3,490,563 USDT | CertiK's reported USDT received from Nirvana's treasury during the attack.       |
| ANA price impact         |         about -85% | The reserve drain broke confidence in the protocol token.                        |
| NIRV post-attack price   |     about 0.14 USD | The stablecoin lost its peg after reserves were drained.                         |

## Attack Flow

CertiK's incident analysis describes the core transaction as beginning with a 10,250,000 USDC flash loan from Solend. The attacker used that capital to buy ANA through Nirvana, then manipulated the buy path so the token was acquired as if the purchase were priced around 8 USD rather than the much higher price implied by the size of the trade.

The key market-health problem was that the same interaction that bought ANA also moved the protocol's internal price upward. CertiK reports the manipulated price moved to roughly 24 USD. Tient Technologies, in a short on-chain writeup published immediately after the exploit, reported a similar move from 8 USD to 24.27 USD.

After the price moved, the attacker sold the ANA back to Nirvana. CertiK reports that the attacker received about 3,490,563 USDT from the Nirvana treasury plus remaining value back in USDC, repaid the Solend loan, and retained the surplus. The funds were then converted and bridged through Wormhole to an Ethereum address.

## Why The Market Signal Failed

Nirvana's protocol design was meant to create a reserve-backed token with a rising floor price. That design made the protocol-owned market itself a critical source of truth. The attack showed that if a pricing function can be made to undercharge for a large buy while still letting that buy move the curve upward, the protocol's own market becomes both the manipulated venue and the settlement counterparty.

This is a stronger failure than a thin external AMM quote. The attacker did not need to hold an inflated market state across blocks. The full cycle happened as a single liquidity-funded loop:

1. borrow USDC,
2. buy ANA at an artificially favorable price,
3. let the purchase update the protocol's internal price,
4. sell ANA back into protocol reserves at the updated price,
5. repay the flash loan and bridge the extracted stablecoins away.

For market-health analysis, the important distinction is that Nirvana's reserve market was supposed to provide reliable exit liquidity. Once the market itself was used as the manipulation surface, the apparent price of ANA stopped representing sustainable demand or reserve safety.

## Market-Health Indicators

### 1. Price-curve sensitivity to one address

A reserve-backed protocol market should be watched for outsized single-address trades that move internal pricing by multiples in one transaction. A move from around 8 USD to the 24 USD range is not ordinary market discovery when it is funded and unwound before the transaction ends.

### 2. Flash-loan notional versus treasury depth

The flash-loan notional exceeded 10 million USDC, while the extracted reserve value was in the 3.5 million USD range. Monitoring should compare same-transaction borrowed capital with treasury liquid reserves and with the slippage generated by protocol-owned markets.

### 3. Self-contained buy-resell loop

The exploit was profitable because the attacker could buy from and sell back to the same protocol after moving the price. Healthy markets should not let a participant manufacture price impact through one leg and settle against the protocol on the opposite leg without delay, caps, or independent validation.

### 4. Stablecoin reserve depletion

Nirvana's later recovery update said the stolen 3.5 million USD represented nearly all funds possessed by the protocol. A market-health monitor should treat reserve depletion, not just token price movement, as the critical severity signal for reserve-backed or algorithmic markets.

### 5. Cross-chain exit path

CertiK traced the profit from Solana to an Ethereum wallet through Wormhole. Rapid bridging after a reserve-drain event is a useful indicator for incident response because it separates ordinary arbitrage from laundering-oriented extraction.

## Controls That Would Have Reduced The Risk

Nirvana's case points to controls for protocols that run their own bonding curves, reserve markets, or algorithmic pricing contracts:

- Price large buys against the actual post-trade curve rather than a stale or undercounted intermediate value.
- Add per-transaction and per-block limits when a trade would move an internal price curve by more than a configured threshold.
- Separate pricing updates from immediate same-transaction resale into protocol reserves.
- Require independent reserve and slippage checks before allowing a sell back to the protocol.
- Compare flash-loan-funded trade size with treasury liquidity before executing reserve-backed redemptions.
- Trigger emergency pauses when a single transaction combines large borrowed liquidity, a protocol-market buy, a protocol-market sell, and cross-chain transfer preparation.

## Legal And Recovery Outcome

The case later became notable beyond the technical exploit. The U.S. Attorney's Office for the Southern District of New York said Ahmed was sentenced on April 12, 2024 to three years in prison for hacking two decentralized exchanges. The DOJ described the Nirvana attack as an exploit that let him buy cryptocurrency from Nirvana at a lower price than intended, immediately resell it at a higher price, and keep the stolen funds after rejecting a bug-bounty negotiation.

Nirvana's own recovery update said law-enforcement cooperation led to identification of the perpetrator and a restitution order. The update says Ahmed was ordered to pay 3.4 million USD in restitution to Nirvana, and that the protocol planned a claims process for affected users.

## References

- [CertiK: Nirvana Finance Incident Analysis](https://www.certik.com/blog/nirvana-finance-incident-analysis)
- [Nirvana Finance: Rising from the Ashes](https://medium.com/nirvanafinance/nirvana-finance-rising-from-the-ashes-f2780607f685)
- [U.S. Department of Justice: Former Security Engineer Sentenced To Three Years In Prison For Hacking Two Decentralized Cryptocurrency Exchanges](https://www.justice.gov/usao-sdny/pr/former-security-engineer-sentenced-three-years-prison-hacking-two-decentralized)
- [Tient Technologies: A flash-loan attack on Nirvana Finance](https://medium.com/@tient.tech/a-flash-loan-attack-on-nirvana-finance-46d7cb6a5771)
- [Etherscan attacker destination address](https://etherscan.io/address/0xb9ae2624ab08661f010185d72dd506e199e67c09)
