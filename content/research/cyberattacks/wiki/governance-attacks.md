---
title: Governance Attacks
bookToc: true
---

Governance attacks exploit the fact that many DAOs treat token ownership as control. If an attacker can cheaply accumulate voting power, borrow it through a flash loan, or exploit low voter participation, they can pass proposals that transfer treasury assets, mint tokens, or rewrite protocol rules.

## The Mechanism

In a standard DAO, governance power is proportional to token ownership or delegated voting weight. That model becomes fragile when:

1. **Flash loans** let an attacker borrow enough capital to dominate a vote in one transaction, as seen in [Beanstalk](https://dn.institute/attacks/posts/2022-04-17-Beanstalk/).
2. **Low participation** allows hostile proposals to pass when honest voters are absent or disengaged.
3. **Thin governance-token liquidity** lets an attacker buy effective control cheaply and then extract more value than the acquisition cost.

## Famous Case Studies

### 1. Beanstalk Farms (April 2022)
- **Loss:** Approximately [$182 million](https://dn.institute/attacks/posts/2022-04-17-Beanstalk/).
- **Mechanism:** Flash-loan governance attack.
- **Details:** The attacker used a flash loan of nearly [$1 billion](https://dn.institute/attacks/posts/2022-04-17-Beanstalk/) in assets to gain a 67% governance supermajority, then executed proposal BIP-18 to transfer protocol funds.
- **Speed:** The exploit completed in a single transaction because Beanstalk's emergency execution path allowed immediate enactment after the malicious vote.

### 2. Build Finance (February 2022)
- **Loss:** Contemporary reporting put the immediate loss at about [$470,000](https://www.theblock.co/post/134180/build-finance-dao-suffers-hostile-governance-takeover-loses-470000), with the more important consequence being full protocol control.
- **Mechanism:** Hostile governance takeover through low participation.
- **Details:** A malicious proposal granted the attacker control over the BUILD token contract. Because community turnout was weak, the proposal passed and the attacker minted new tokens, drained liquidity, and effectively captured the protocol ([The Block](https://www.theblock.co/post/134180/build-finance-dao-suffers-hostile-governance-takeover-loses-470000), [rekt.news](https://rekt.news/build-finance-rekt/)).
- **Speed:** Slower than flash-loan exploits because it depended on the governance timetable, but still effective because almost nobody showed up to stop it.

### 3. True Seigniorage Dollar (TSD) (March 2021)
- **Loss:** Reporting on the incident focused less on a stable realized dollar total than on the fact that the attacker minted [11.8 billion TSD](https://tokenpost.com/news/investing/7404) and collapsed the token's market value.
- **Mechanism:** Governance arbitrage via cheaply accumulated voting power.
- **Details:** In the TSD takeover, the attacker accumulated enough governance influence to pass a self-serving proposal, minted [11.8 billion TSD](https://tokenpost.com/news/investing/7404), and dumped the newly created supply on PancakeSwap. This was a TSD incident, not Empty Set Dollar (ESD), and it illustrates how thin-liquidity governance systems can be looted without flash loans.
- **Speed:** The accumulation phase took longer than Beanstalk, but the destructive payout and market collapse followed quickly once governance control was obtained.

## Prevention and Mitigation

### 1. Snapshot voting power before execution
- **Snapshotting:** Count voting power at a prior block so attackers cannot borrow governance weight only for the execution window.
- **Time-locks:** Add a delay between proposal passage and execution so the community can react.

### 2. Raise the cost of hostile passage
- **Minimum quorum:** Require meaningful turnout so a tiny cabal cannot seize control in a quiet vote.
- **Veto or guardian controls:** Some protocols use a security council or guardian multisig that can stop obviously malicious proposals during the delay period.

### 3. Keep honest governance active
- **Vote delegation:** Encourage token holders to delegate voting power to trusted, active participants.
- **Liquidity-aware risk design:** Thinly traded governance tokens should not control treasury functions without additional safeguards.
