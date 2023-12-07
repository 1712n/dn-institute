---
date: 2023-11-23
target-entities: Heco Cross Chain Bridge and HTX
entity-types:  
   - Exchange
   - Bridge
attack-types:
   - Private Key Leak
title: “HECO Chain bridge compromised over $86.6M sent to suspicious addresses”
loss: 87000000
---

## Summary

Blockchain [security firm’s](https://blockworks.co/news/htx-hack-ethereum-crypto-assets) CertiK, Peckshield and Cyvers have reported over $86.6 million in digital assets, including stablecoins, ETH, SHIB, LINK, and more, were transferred from the HECO Chain bridge to suspicious addresses. Various other ERC-20 tokens were drained, swapped for ether, and distributed to at least 8 wallets. Withdrawals and deposits have been temporarily [suspended](https://cointelegraph.com/news/heco-chain-bridge-hack-86-million-lost) as the company investigates the incident, with services expected to resume after the investigation is completed. Security analysts speculate that compromised private keys may be the cause of this incident.

## Attackers

The attacker has yet to be identified. 

## Losses

Between Heco Cross Chain Bridge and HTX the losses total approximately $87,000,000 USD.

## Timeline

   - **”November 22, 2023, 09:59 UTC:** 1,262 ETH is transferred into [wallet.](https://etherscan.io/tx/0xbb6fe88427c2f3bc179075109d47a805dcfedab0e475eaca0d979311873e131b)  
   - **”November 22, 2023, 11:23 UTC:”** PeckShield announces a suspicious withdrawal of 10,145 ETH. 
   - **”November 22, 2023”** Hacken posts holding wallet addresses on their [website.](https://hacken.io/insights/heco-bridge-hack-explained/)
   - **”November 22, 2023, 12:34 UTC:”** Justin Sun announces via X (formally known as Twitter) deposits and withdrawals are [temporarily suspended.](https://twitter.com/justinsuntron/status/1727304656622326180) 
   - **”November 22, 2023, 1:13 UTC:”** Coindesk releases an article stating HTX will fully compensate for any losses originating from the [exchange.](https://www.coindesk.com/tech/2023/11/22/justin-sun-confirms-htx-heco-chain-exploited-after-100m-in-suspicious-transfers/)
   - **”November 22, 2023, 2:39 UTC:”** Arkham posts via X they have created and funded a [white hat bounty}(https://twitter.com/ArkhamIntel/status/1727335953583190229?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1727335953583190229%7Ctwgr%5E762b9e6c852b5ee31866b716515fa3f6e5bd7f37%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fwww.fxstreet.com%2Fcryptocurrencies%2Fnews%2Fjustin-suns-htx-exchange-and-heco-suffer-85m-exploit-202311230005) to recover the stollen funds.  

## Security Failure Causes

   - **Vulnerability in Bridge Protocol:** The successful attack on the HECO bridge can be attributed to a fundamental security failure in the bridge protocol itself. 
   - **Lack of Real-time Monitoring and Alerts:** The absence of an effective real-time monitoring system and alert mechanism would have assisted with detection of the ongoing exploit.
