---

date: 2023-11-08
target-entities: CoinSpot
entity-types: Exchange
attack-types: Private Key Leak
title: “Crypto exchange CoinSpot reportedly suffers $2M hot wallet hack”
loss: 2622019.54

---

## Summary

According to [Etherscan](https://etherscan.io/tx/0x210ca8b12d1763307636982a0972437009ec7f65626db23c8b2b2a0a308bcf61) Australian crypto exchange CoinSpot reportedly suffered a $2.4 [million](https://cryptotvplus.com/2023/11/coinspot-exchange-allegedly-suffers-2m-hot-wallet-hack/) loss in a hot wallet hack, according to [CertiK,]((https://twitter.com/CertiK/status/17226592787863720660 ) a blockchain security firm. The hack involved a compromised private key associated with a CoinSpot hot wallet. Blockchain investigator ZachXBT noted on November 8th that two transactions were detected entering the suspected hacker's wallet, who later transferred the funds through THORChain and Wan Bridge onto the Bitcoin network. CertiK found that the compromise likely occurred due to a compromised private key. The hacker received 1,262 ETH from a known CoinSpot wallet, then made transactions, swapping ETH for Wrapped Bitcoin on Uniswap, and later exchanging ETH for Bitcoin via THORChain. The stolen Bitcoin was sent to multiple wallets, subdivided into smaller amounts to hinder tracing. CoinSpot is regulated by the Australian Transaction Reports and Analysis Centre. The incident adds to concerns about crypto platform security, leading regulators to explore protective measures. Other recent crypto hacks, such as Platypus, have contributed to increased regulatory scrutiny. The Australian financial authority AUSTRAC, is actively addressing the security breach because the amount stolen is more than [$10,000.](chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://www.austrac.gov.au/sites/default/files/2021-11/AUSTRAC%20draft%20guidance%20-%20reporting%20multiple%20cash%20transactions_0.pdf)  

## Attackers

The attacker has yet to be identified. 

## Losses

CoinSpot lost 1,262 ETH during the hack, worth 2,400,000 USD at the time of the attack. 

## Timeline

   - “November 8, 2023/20:01 UTC:” ZackLBT announces hack on [Telegram.](https://t.me/investigations/70) 
   - “November 9, 2023/5:25 UTC:” [Cointelegraph](https://twitter.com/Cointelegraph/status/1722485447723745448) posts exploit on X (formally known as Twitter) and suggests the hack is due to a private key leak. 
   - ”November 10, 2023/15:29 UTC:” The Financial [Review](https://www.afr.com/technology/crypto-hack-suggests-australia-s-coinspot-exchange-has-been-compromised-20231110-p5eizc) confirms the funds have been reported stollen to Chainalysis, and states no customers have been affected by the attack. 

## Security Failure Causes

CertiK stated in email correspondence the alleged attack was the result of a “probable private key compromise” on at least one CoinSpot hot wallet. The compromise in security may have arisen due to the presence of the following vulnerabilities or shortcomings.
   - Vulnerability in Web Application Security:
      - The successful attack on Coinspot Exchange may be attributed to a vulnerability in its web application security. This could involve inadequate input validation, improper session management, or flaws in the implementation of security mechanisms, providing attackers with the opportunity to exploit weaknesses in the website's code.
   - Failure in Multi-Factor Authentication (MFA):
      - The compromise of the hot wallet could have been facilitated by a failure in the implementation or enforcement of multi-factor authentication. MFA adds an additional layer of security, and its absence or improper configuration may have allowed unauthorized access to the wallet, leading to the reported security breach.
   - Inadequate Security Patch Management:
      - The attack may have exploited known vulnerabilities in the web server or underlying software components due to the absence of a rigorous security patch management process. Regularly updating and patching software is crucial to addressing known vulnerabilities and preventing attackers from exploiting outdated system elements.
   - Insufficient Network Intrusion Detection Systems (NIDS):
      - The absence or inefficiency of Network Intrusion Detection Systems might have contributed to the success of the attack. NIDS are essential for real-time monitoring and detection of malicious activities within the network infrastructure. Inadequate deployment or configuration of NIDS could have allowed the attackers to operate undetected.
   - Compromised API Security:
      - A breach in the security of application programming interfaces (APIs) can be a fundamental cause of an attack. If the exchange relies on APIs for transactions or interactions with the hot wallet, a lack of proper authentication, authorization, or encryption in the API layer may expose vulnerabilities that attackers can exploit to compromise the wallet.
   - Ineffective Security Information and Event Management (SIEM):
      - A deficient SIEM system may have played a role in the attack's success by failing to correlate and analyze security events in real-time. An effective SIEM solution is crucial for identifying anomalous patterns, detecting security incidents, and facilitating a timely response to potential threats.
   - Misconfiguration of Cloud Security Controls:
      - If the exchange leverages cloud services, misconfigurations in cloud security controls could be a contributing factor. Inadequate configuration of access controls, encryption settings, or other cloud security parameters may have exposed critical infrastructure to unauthorized access, enabling the reported hot wallet hack.
   - Social Engineering Exploitation:
      - Human factors, such as social engineering attacks, can be a fundamental security failure cause. If employees or stakeholders were manipulated into divulging sensitive information or performing actions that facilitated the attack, the organization may need to reinforce its security awareness training and implement measures to mitigate social engineering risks.

It is currently unknown if any additional wallets have been affected. 
