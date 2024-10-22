---
title: "Phishing Attacks"
bookToc: true
---

Phishing is a cyberattack where the attacker pretends to be a trustworthy source to trick victims into revealing sensitive information. This information can include usernames, passwords, credit card numbers, and other personal details that can be misused. Cybercriminals leverage cryptocurrency transactions because they are anonymous and irreversible. They trick victims into revealing their private keys or other sensitive information, which they use to steal their cryptocurrency. These attacks can come in various forms such as fake wallet apps, fraudulent websites, or scam emails pretending to be from reputable crypto exchanges.

### Impact

- **Financial Impact:** Reports from crypto security firms reveal that over `$87 million` has been stolen through phishing attacks in decentralized finances. It's known that the overall impact is way bigger, since only confirmed losses from crypto custodians exceed `$152 million`.

### Common Phishing Techniques

#### Fake Exchange Websites and Wallets

One common phishing technique involves creating fake exchange websites and wallets that look like legitimate cryptocurrency exchange platforms or digital wallet sites. Users may enter their login credentials on these sites, which are then captured by fraudsters who can steal cryptocurrencies.

- **How to prevent it:** Always double-check the URLs of the sites you visit and ensure they use HTTPS for security. Use bookmarks for frequently visited sites and avoid clicking on suspicious links sent via email or found on social media sites.

- **Attack Example:**

##### [UniSwap: $8m (June 2022)](https://blog.checkpoint.com/2022/07/12/8-million-dollars-stolen-in-a-uniswap-phishing-attack/)

- Attackers created a simple ERC20 token and airdropped (sent it for free) it to users that hold UNI tokens. The goal of this airdrop was to lure the victims to the attacker’s scam website - UniswapLP.com, and gain access to their wallets via malicious transaction. The phishing campaign is successfully as that the transaction of the airdrop seems legitimate at etherscan.io. The scammers were able to drain $8 million of user funds.

#### Email Phishing

Email phishing involves sending emails pretending to be reputable crypto exchanges or services with urgent messages to trick users into clicking on a malicious link or attachment.

- **How to prevent it:** Be wary of unsolicited emails and double-check the sender's email address for any misspellings or extra characters. Avoid clicking on embedded links in these emails.

#### Clipboard Hijacking

Clipboard hijacking involves using malware to change the clipboard content of a user's device. When a user copies a cryptocurrency address to send funds, the malware changes the copied address to one that belongs to the attacker.
- **How to prevent it:** Always double-check the pasted address before confirming any transactions, and keep the endpoint security software up to date.
- **Attack Example:**

##### [Hack Boss Malware: $560k (November 2018)](https://decoded.avast.io/romanalinkeova/hackboss-a-cryptocurrency-stealing-malware-distributed-through-telegram/)

- This malware monitors device clipboard, where copied content is stored, and replaces any copied cryptocurrency addresses with the attacker's address. The aim is for the malware to change cryptocurrency addresses when infected users make transactions, causing the user to unknowingly send funds to the malware's creator.

#### Mobile Phishing

Mobile phishing involves sending malicious SMS messages or creating fake mobile applications to trick users into revealing sensitive information.
- **How to prevent it:** Only download apps from official app stores, verify developer information before downloading an app, and be skeptical of unsolicited SMS links.
- **Attack Example:**

##### [BitKeep: $8m (December 2022)](https://cointelegraph.com/news/hackers-drain-8m-in-assets-from-bitkeep-wallets-in-latest-defi-exploit)

- Some users of the multichain wallet BitKeep had downloaded a hacked APK version. The APK has been hacked due to a vulnerability in the API server used by the wallet app. This allowed the attacker to access the app’s database, which held critical user information such as private keys of their wallets.

### Advanced Phishing Techniques

#### Domain Spoofing

Domain spoofing involves creating domains that look very similar to original sites by using slight misspellings or different domain extensions.
- **How to prevent it:** Double-check domain names before interacting with any website and ensure that the site has a secure HTTPS connection.

- **Attack Example:**

##### [X2Y2: $165k (May 2022)](https://twitter.com/Serpent/status/1523833573815373824)

- Scammers used Google Ads to advertise their fake link that lead to a phishing website, like in the screenshot below. The website tried to get the user's seed phrase and execute the function to empty account balances. Roughly 100 ETH were stolen.

{{< image src="x2y2.png" alt="Google Ads Phishing" >}}

#### ERC20Permit Phishing

ERC20Permit phishing targets users of the Ethereum blockchain, tricking them into signing a permit function, which allows the attacker to access to the user's signature and drain funds from their address.

- **How to prevent it:** Always double-check the transactions you are going to sign and approve only to the well known addresses.

- **Attack Example:**

##### [Venom Drainer: $2.9m (March 2023)](https://twitter.com/realScamSniffer/status/1639260170021740545)

- The victim lost $2.9 million DAI after signing permit transaction. The attacker used Venom Drainer tool, that generated malicious smart contracts for phishing attacks. [The total stolen amount involving Venom Drainer reached $27 million](https://dune.com/scamsniffer/venom-drainer-stats) as of September 12, 2023.

### Spear Phishing and Whaling

Spear phishing targets specific individuals with deceptive emails or messages to trick them into revealing sensitive information. Whaling is a more advanced form of spear phishing that targets high-profile individuals or executives.

- **How to prevent them:** Regular training and awareness programs can help educate employees about these threats. Use multifactor authentication for added security, and keep personal information off social media as much as possible.

- **Attack Example:**

##### [Hayden Adams: $3.6m (July 2023)](https://cointelegraph.com/news/hackers-compromise-uniswap-founder-twitter-account-promote-scam)

- The Twitter account of Hayden Adams, creator of UniSwap exchange, was exploited by scammers. Over the course of several months, these cyber criminals created more than 23 phishing websites. They managed to steal approximately $3,600,000 from around 358 victims, by posting malicious links to fake websites from the victim's account.
