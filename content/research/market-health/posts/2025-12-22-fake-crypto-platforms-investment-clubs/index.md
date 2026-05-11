---
title: "Fake Crypto Trading Platforms and Investment Clubs as Synthetic Market Infrastructure"
date: 2025-12-22
entities:
  - Morocoin
  - Berge
  - Cirkor
  - AI Wealth
  - Lane Wealth
  - AI Investment Education Foundation
  - Zenith Asset Tech Foundation
  - NNET
---

## Summary

This case study analyzes the SEC's December 22, 2025 complaint against three purported crypto asset trading platforms, Morocoin Tech Corp., Berge Blockchain Technology Co. Ltd., and Cirkor Inc., and four investment-club entities, AI Wealth Inc., Lane Wealth Inc., AI Investment Education Foundation Ltd., and Zenith Asset Tech Foundation. The SEC alleged that the defendants ran a coordinated investment confidence scam that misappropriated at least $14 million from U.S.-based retail investors between January 2024 and January 2025.

The case is useful for market-health research because the alleged misconduct did not depend on manipulating a real order book. Instead, the platform layer itself allegedly created synthetic market evidence: trading screens, account balances, real-time-looking crypto prices, claimed regulatory licenses, fictitious security token offerings, and withdrawal workflows. Investors saw market-like activity, but the SEC complaint says no trading actually occurred on the platforms.

The supporting dataset is available in [fake-platforms-summary.csv](fake-platforms-summary.csv).

## Scheme Structure

The complaint describes a two-layer funnel. First, the club defendants allegedly used social media ads to recruit U.S.-based investors into WhatsApp investment clubs. The clubs were presented as groups led by experienced financial professionals. The SEC says some ads used deepfake videos of prominent financial professionals, and the WhatsApp groups relied on a "professor" and "assistant" pattern to build trust with participants.

Second, the clubs allegedly routed investors to the platform defendants. AI Wealth and Lane Wealth directed investors to Morocoin, AIIEF directed investors to Berge, and Zenith directed investors to Cirkor. The platforms then displayed trading-account interfaces that mimicked legitimate crypto venues, including balances, real-time price information, purported transactions, and reported profits and losses.

The SEC's core market-health allegation is direct: Morocoin, Berge, and Cirkor were not genuine trading platforms, and trading never actually took place on them. That distinction matters for surveillance. A fake venue can imitate the user-facing features of a market without producing public execution data, independent custody records, or an external settlement trail. Traditional wash-trading metrics are not enough when the exchange screen itself is synthetic.

## Fake Market Signals

### Claimed regulatory legitimacy

The complaint says the platforms relied on regulatory and compliance claims to make the venue appear safe. Morocoin, Berge, and Cirkor allegedly referenced money-services-business registrations, National Futures Association licenses, SEC licenses, corporate registrations, and security controls. The SEC alleged that the platforms did not hold SEC or NFA licenses and that MSB or corporate registrations did not establish that the platforms were compliant or legitimate.

For market-health monitoring, this is a venue-verification signal. A platform that advertises regulatory licensing should be checked against the named regulator's public records. A mismatch between the claimed license and the regulator's registry is not a trading anomaly, but it is a market-integrity warning because the venue is using compliance language to lower investor scrutiny.

### Account balances without external settlement

The platforms allegedly credited investor accounts after victims sent fiat currency or crypto assets. Investors could then see account balances and trade results on the platform interface. The complaint alleges that the funds were never invested as represented and were misappropriated from the start.

The monitoring issue is that balances shown inside a closed platform can be economically meaningless when they are not backed by third-party custody, public settlement records, or verifiable withdrawal history. A market-health review should separate interface activity from externally verifiable trading activity. If the only evidence of a trade is the platform's own screen, the evidence is weak.

### Fictitious STOs

The SEC complaint alleges that the defendants promoted security token offerings that were purportedly issued by legitimate businesses and compared them to initial public offerings. One example was NNET, a token allegedly promoted through AI Wealth and Lane Wealth groups as an offering by a company called NeuralNet. The SEC says the STOs and the purported issuing companies were fictitious.

This converts a fake venue into a fake primary market. The trading platform supplies the account interface, the investment club supplies social proof, and the STO narrative supplies urgency. A monitoring system should treat new-offering solicitations on thinly verifiable venues as higher risk when the issuer, token contract, cap table, and trading venue are all controlled or introduced by the same promoter network.

### Withdrawal-fee pressure

The complaint alleges that when investors tried to withdraw funds, defendants demanded advance fees and told some victims their accounts would be frozen. In a legitimate venue, withdrawal limits and compliance checks should be governed by published policies and auditable account records. In a synthetic venue, withdrawal fees can become the final monetization step after a victim already believes that platform balances are real.

For market-health analysis, withdrawal friction is a post-trade integrity signal. A platform that accepts deposits easily, reports profits internally, and then demands new money before permitting withdrawals is not just operationally weak; it can indicate that the displayed balances are part of the scheme.

## Detection Checklist

1. Verify claimed SEC, NFA, MSB, and corporate registrations against regulator databases and corporate records.
2. Separate platform-displayed balances from externally verifiable settlement evidence.
3. Check whether a venue's domains, customer-service scripts, and marketing language are reused across supposedly independent platforms.
4. Flag investment-club funnels that route participants from social media or messaging apps into a single recommended trading venue.
5. Treat STO or primary-offering solicitations as high risk when issuer identity, token existence, venue custody, and pricing are not independently verifiable.
6. Track withdrawal outcomes, not just deposit acceptance and reported account gains.
7. Preserve the legal status of the evidence: this article discusses SEC allegations, not adjudicated findings.

## Market-Health Lessons

This case broadens the market-health model beyond exchange-level trade surveillance. In ordinary wash trading, investigators often look for self-matches, repeated account-pair reversals, order-book mirroring, and volume-depth divergence. Here, the more important question is whether the displayed market exists at all.

The same analytical frame still applies: reported activity must be tied to independent evidence. Real venues can show order books, executions, wallet flows, custody arrangements, and withdrawal histories. Synthetic venues can show only what their interface chooses to show. When social-media recruitment, claimed AI signals, fake licensing, fictitious offerings, and advance-fee withdrawal demands appear together, the market-health risk is not merely suspicious volume. It is the creation of an entire fake trading environment.

## References

- [SEC press release 2025-144, December 22, 2025](https://www.sec.gov/newsroom/press-releases/2025-144-sec-charges-three-purported-crypto-asset-trading-platforms-four-investment-clubs-scheme-targeted)
- [SEC complaint, SEC v. Morocoin Tech Corp. et al., filed December 22, 2025](https://www.sec.gov/file/comp-pr2025-144)
- [SEC investor alert: Group Chats as a Gateway to Investment Scams](https://www.investor.gov/index.php/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-alerts/gateway-to-investment-scams)
