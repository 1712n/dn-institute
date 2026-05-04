---
title: "Sushi MISO Jay Pegs auction exploit: when one front-end commit redirected 864.8 ETH"
date: "2026-05-05"
description: "The September 2021 MISO/Jay Pegs Auto Mart incident showed how token-launch auctions can lose custody without a Solidity bug: a malicious front-end supply-chain change replaced the auction wallet and redirected 864.8 ETH before the funds were returned."
entities:
  - SushiSwap
  - MISO
  - Jay Pegs Auto Mart
  - DONA
  - SUSHI
  - ETH
---

## Summary

On September 17, 2021, SushiSwap's MISO token launchpad disclosed that the Jay Pegs Auto Mart auction had been compromised by a front-end supply-chain attack. The immediate loss was not caused by a public on-chain exploit against a reusable auction invariant. Instead, the attacker changed the wallet destination used when the auction was created, so 864.8 ETH from the completed sale was sent to an address controlled by the attacker rather than the intended recipient.

The incident was narrow in contract scope but broad in market-health implications. MISO was a launchpad that sold new assets through mechanisms such as Dutch auctions, batch auctions, and crowdsales. Participants in those sales were not merely trusting auction math. They were also trusting the deployment pipeline, front-end configuration, repository access controls, and review process that produced the transaction path users saw in the browser. The Jay Pegs auction showed that a launchpad can appear to work exactly as expected at the user-interface level while silently binding a sale to a hostile payout address.

The stolen ETH was returned within hours. Coverage from CryptoBriefing, CryptoSlate, CoinDesk, Ars Technica, Coinspeaker, and Sonatype all converges on the same core facts: one Jay Pegs Auto Mart auction was affected, 864.8 ETH was redirected, no other auctions were reported as drained, and the funds were ultimately returned as approximately 865 ETH. That recovery materially reduced final user harm, but it should not make the event look benign. A security outcome that depends on public attribution pressure, exchange cooperation, and the attacker's decision to return funds is not a reliable control.

This article frames the exploit as a market-health failure rather than simply a one-off hack. Launchpads concentrate primary issuance, market discovery, and custody into short windows. If the address-selection process can be changed by a rogue contributor, a token sale can clear, buyers can believe they participated normally, and the issuer can lose the entire raise. For thinly capitalized projects, that can convert a launch event into an immediate solvency and credibility crisis.

## What MISO and Jay Pegs were selling

MISO, short for Minimal Initial SushiSwap Offering, was SushiSwap's launch platform for new token offerings. It was designed to let projects raise capital and distribute tokens using configurable sale formats rather than building their own launch infrastructure. In practice, that made MISO more than a website. It was a trust surface connecting sale contracts, auction parameters, project treasuries, and retail participation.

Jay Pegs Auto Mart was a deliberately playful NFT-linked project. Public reports described the sale as involving DONA, an ERC-20 token tied to rare 2007 Kia Sedona-themed NFTs. Coinspeaker summarized the project as a token sale where DONA holders would later be able to exchange tokens for randomly generated Kia Sedona NFTs. CoinDesk reported that Jay Pegs publicly reassured participants that the NFT exchange was still scheduled and that everyone would still receive their NFTs.

That detail matters because the exploit did not only affect a protocol treasury in the abstract. It hit a primary-sale market where participants had already committed ETH under a launchpad's execution path. When launch infrastructure is compromised, the damage can propagate through multiple layers:

1. buyers lose confidence that the sale terms they saw were the terms actually executed,
2. issuers lose the proceeds they expected to fund delivery,
3. launchpads lose credibility as neutral sale infrastructure,
4. secondary markets price in operational risk rather than just project fundamentals.

The Jay Pegs sale became a case study in how even a quirky NFT auction can expose serious systemic assumptions. The amount at risk, 864.8 ETH, was large enough to affect project financing and launchpad reputation. The fact that only one auction was affected limited the blast radius, but the mechanism would have been dangerous in any sale format where a front end or deployment studio selected treasury addresses.

## The exploit mechanism: custody redirection, not price manipulation

Many DeFi market-health incidents involve oracle manipulation, flash loans, reentrancy, or incorrect accounting between token balances and internal reserves. The MISO incident was different. The malicious step reportedly happened before users interacted with the final auction path: the attacker altered the front-end or studio code so the auction wallet was replaced with an attacker-controlled Ethereum address at auction creation.

CryptoBriefing reported that the attacker "switched a contract address on the launchpad with one they control" and drained 864.8 ETH from the Jay Pegs Auto Mart auction. CryptoSlate described the same mechanism as replacing the original contract for the Jay Pegs auction with a personal Ethereum address. Coinspeaker quoted SushiSwap CTO Joseph Delong's description that the attacker inserted their own wallet address to replace the auction wallets at auction creation. Ars Technica similarly reported that the attacker inserted their own wallet address to replace the `auctionWallet`.

The key distinction is that auction participants did not need to trigger an exotic on-chain sequence. The compromised configuration made the wrong destination part of the sale flow. Once the auction finalized, the proceeds moved to the hostile destination. From a user perspective, the sale could look ordinary until the recipient address was inspected. From a project perspective, the entire sale could clear while treasury custody was already lost.

This is why the incident belongs in a market-health dataset. The failure mode sits between application security and market structure:

- the market event was a token/NFT launch,
- the economic object was the sale's ETH proceeds,
- the technical weakness was supply-chain and configuration control,
- the visible outcome was a sudden disappearance of auction funds,
- the recovery depended on off-chain pressure rather than deterministic protocol remediation.

The exploit also challenges a common but incomplete DeFi security heuristic: "the contracts were audited, therefore the launch is safe." A launchpad contract can be mathematically correct and still be unsafe if the final address, ABI, build artifact, deployment script, or front-end path can be changed by one unreviewed actor.

## Why one commit was enough

Sonatype's analysis is useful because it connects the public theft to an ordinary software-delivery control failure. According to Sonatype, the attack involved one malicious code commit to Sushi's private `miso-studio` GitHub repository. The attacker could alter the auction site's front end and replace the authentic wallet address with their own. Sonatype quoted Sushi's postmortem as saying the studio repository had a process for opening pull requests against a development branch and then reviewing them before merging into the master branch, but that this process was not enforced through Git branch-protection settings.

In other words, there was a review norm, but not a hard guardrail. For a crypto launchpad, that is an economically meaningful distinction. A policy that relies on contributors remembering to follow a process is weaker than a repository setting that blocks direct or insufficiently reviewed changes. A policy that exempts administrators or trusted contractors is weaker than one that applies to every actor capable of changing production-affecting code.

The apparent root cause was therefore not only "a malicious contributor." It was that a malicious or compromised contributor could get a production-relevant change into the path that defined where auction proceeds would go. Good incident analysis should separate those concepts:

- **Actor risk:** a contractor, contributor, or account may behave maliciously or become compromised.
- **Permission risk:** that actor may have repository or deployment access beyond what is necessary.
- **Review risk:** the change may bypass mandatory independent review.
- **Configuration risk:** the changed code may control a high-value destination address.
- **Detection risk:** users and operators may not notice the altered address before funds settle.

The MISO incident required all of these layers to fail enough for the sale to complete with the wrong recipient. The lesson is not that launchpads should never use external contributors. The lesson is that economically sensitive code paths should assume contributor compromise and enforce controls that still hold under that assumption.

## Timeline

Public reporting supports the following timeline.

**Before September 17, 2021:** MISO was operating as SushiSwap's launchpad. Jay Pegs Auto Mart used the platform for its DONA/NFT-related sale. MISO's studio/front-end pipeline reportedly included a pull-request review procedure, but branch protection did not hard-enforce the process.

**September 17, 2021:** SushiSwap CTO Joseph Delong disclosed that an auction on MISO had been exploited. CoinDesk reported that 864.8 ETH had been transferred from the Jay Pegs Auto Mart sale and that Etherscan labeled the address as part of an exploit. Public reporting cited an attacker address beginning from the Etherscan link `0x3ddd8b6d092df917473680d6c41f80f708c45395`.

**Immediate response:** Sushi publicly stated that only one auction appeared to be exploited and that affected auctions had been patched. Delong publicly connected the event to an anonymous contractor using the GitHub handle AristoK3 and also stated Sushi had reason to believe a pseudonymous developer known as `eratos1122` was involved. CoinDesk noted that it could not independently verify the alleged attacker's identity. CryptoSlate later reported that some accusatory tweets were deleted and that the accused developer denied or contested the public accusations.

**Exchange and legal escalation:** Sushi asked Binance and FTX for assistance with KYC information connected to the suspected attacker. Public statements threatened an FBI complaint if funds were not returned. This response likely increased pressure on the holder of the funds, but it also produced reputational debate over doxxing and accusation handling in an ecosystem that often relies on pseudonymous contributors.

**Recovery:** Within hours, the attacker's wallet balance began falling. Ars Technica reported transactions returning stolen currency to Sushi's Operation Multisig. Sonatype, citing Sushi's write-up, reported that the full funds were returned to the operational multisig in quantities of 100 ETH, 700 ETH, and 65 ETH. CryptoBriefing and CryptoSlate reported that 865 ETH was returned, slightly more than the 864.8 ETH taken.

**Post-incident controls:** Sonatype reported that Sushi added Git branch protections, including for administrator accounts and master/main branches, mandated pull-request approval and signature policies, and began integrating supply-chain security tooling and automated diff-checker implementations.

## Market impact and confidence damage

The direct loss was reversed, so the final balance-sheet impact was much lower than the initial drain. But market impact is not only final unrecovered loss. It is also the information shock created when a launchpad demonstrates that sale proceeds can be redirected by a supply-chain change.

CryptoBriefing noted that SUSHI had gained roughly 20% on the day before the news, then dropped roughly 8% after the disclosure, from about $16 to $14. That movement should not be read as a clean causal model for the whole market, but it does show that security events around launch infrastructure can immediately affect token sentiment. Investors were forced to reprice not only the Jay Pegs sale but the operational maturity of a major DeFi brand.

For projects considering MISO or any launchpad, the event introduced a new diligence question: who can alter the path that chooses custody addresses? For buyers, it introduced a harder user problem: even if a transaction is signed voluntarily, the user's wallet may not make clear whether the destination address is the expected issuer treasury, a launchpad-controlled auction contract, or a malicious substitution. For protocol tokens, it introduced a governance and operating question: are contributors and contractors controlled like financial-infrastructure insiders?

The narrow scope helped prevent a wider collapse. Public reports repeatedly state that only the Jay Pegs Auto Mart auction was affected and that no other auctions were drained. But a narrow incident can still reveal a broad category of latent risk. If the same permissions and deployment pipeline had controlled multiple concurrent sales, or if the attacker had waited for a larger auction, the loss could have been much larger.

## Why recovery did not eliminate the risk

The return of 865 ETH was an unusually favorable outcome. It meant the issuer and sale participants did not experience the full final harm implied by the initial drain. However, treating recovery as a security control would be a dangerous conclusion.

Recovery depended on several contingent facts:

1. the incident was discovered quickly,
2. the attacker's address was public,
3. Sushi had enough reputation and relationships to escalate rapidly,
4. centralized exchanges could be asked for assistance,
5. the attacker or holder of the funds decided returning ETH was preferable,
6. the funds had not already been mixed, bridged, or converted through harder-to-trace routes.

None of these are deterministic properties of the MISO contract system. In a less visible launch, a cross-chain bridge route, or a sale with weaker issuer communications, the same redirection pattern could have produced a permanent loss. Even in this case, public attribution was disputed and criticized. An incident response that relies on naming suspected individuals and requesting exchange KYC can create its own legal and reputational risk if attribution is wrong or premature.

The correct conclusion is therefore not "the system worked because funds came back." The correct conclusion is "the system failed, and the ecosystem got lucky enough to unwind the loss."

## Technical root cause category

The MISO incident can be classified as a front-end/deployment supply-chain compromise with economic address substitution.

This category has several defining traits:

- **The malicious payload is simple.** Replacing a wallet or contract address is easier than writing a complex exploit.
- **The effect is high leverage.** A single destination field can control an entire sale's proceeds.
- **On-chain monitoring may be late.** The incorrect address may only be obvious once funds move or once someone compares deployment parameters.
- **Audits can miss it.** A Solidity audit does not necessarily cover private front-end repositories, deployment scripts, or production configuration.
- **User wallets give weak context.** A signer may see that they are interacting with a launchpad flow but not understand the economic destination chosen during creation.

This category is particularly dangerous for primary issuance. In lending markets, an exploit often has to overcome collateral accounting. In AMMs, it may need to move reserves or manipulate price. In a launch auction, the exploit can be as simple as "send the raise here instead of there." The system's economic value is concentrated in a payout address rather than a complex invariant.

## Controls that would have reduced risk

The post-incident controls reported by Sonatype point in the right direction: branch protection, mandatory pull-request approvals, signature policy, supply-chain security tooling, and automated diff checks. For launchpads, those controls should be treated as a baseline, not an optional DevOps improvement.

### Enforced branch protection

Repository settings should prevent direct pushes to production-affecting branches. The protection should apply to administrators, contractors, and automation accounts. If a branch controls the code that creates auctions or selects treasury addresses, every change should require independent review.

### Mandatory review for economic fields

Not every front-end change has the same economic risk. Changes that touch recipient addresses, factory addresses, deployment scripts, contract ABIs, chain IDs, signer flows, or auction creation parameters should trigger stricter review. A one-line address change can be more dangerous than a large visual refactor.

### Signed commits and release provenance

Signed commits do not prove a change is benign, but they improve traceability and make account compromise easier to reason about. Release artifacts should be tied to reviewed commits, and production deployments should be reproducible enough that reviewers can verify what code was shipped.

### Address allowlists and issuer confirmation

For primary sales, launchpads can require issuers to confirm treasury and payout addresses through a separate channel before launch. The confirmed address should be displayed publicly and compared automatically against the address embedded in the live auction configuration. If the live destination differs, the sale should pause.

### On-chain configuration verification

Before accepting bids, a launchpad can publish a canonical sale manifest containing the token, auction contract, payout address, start/end times, chain, and hash of the front-end release. Users and monitoring bots can compare the live auction against that manifest. This makes address substitution visible before funds accumulate.

### Real-time anomaly alerts

For auctions, alerts should fire when the recipient address is new, recently funded by unrelated accounts, absent from issuer-controlled allowlists, or different from the address announced in sale materials. In the MISO case, the attacker address had limited prior activity according to public coverage; a new or suspicious recipient address for a multimillion-dollar sale should have required manual hold.

### Separation of duties

Contractors who write launch UI code should not be able to unilaterally change production deployment parameters. A separate release or treasury role should approve economically sensitive changes. The goal is not bureaucracy; it is to ensure that one compromised or malicious account cannot redirect an entire sale.

## User-side detection limits

It is tempting to say users should verify everything on-chain. In practice, the MISO event shows why that is not sufficient for retail participants. A buyer joining a timed auction may not know the legitimate payout address. The address may not be human-readable. The auction may be created by a launchpad factory, and the relevant economic parameter may not appear in a wallet prompt in a way the buyer understands.

Better user-side protection requires infrastructure support:

- wallets can highlight when a transaction participates in a sale whose payout address differs from a published manifest,
- explorers can label official launchpad auctions and issuer treasuries,
- launchpads can expose machine-readable sale metadata,
- independent monitors can alert on changes between announced and live sale parameters,
- issuers can publish signed messages confirming exact addresses.

Without these supports, user verification becomes performative. Telling buyers to manually inspect every launch parameter does not scale, especially when the weakness is a front-end supply-chain substitution that exploits trust in the launchpad brand.

## Comparison with smart-contract exploits

The Jay Pegs/MISO exploit differs from many DeFi drains in ways that affect prevention and postmortem analysis.

In an oracle manipulation exploit, prevention focuses on price-source design, liquidity depth, delay, and manipulation-resistant valuation. In a reentrancy exploit, prevention focuses on state-update order, locks, pull payments, and token callback assumptions. In a bridge verification exploit, prevention focuses on proof validation and validator trust. In the MISO case, the central issue was whether the code path that configured the sale could be trusted.

This makes the incident closer to a traditional software supply-chain compromise than to a pure protocol invariant failure. But because the compromised software controlled crypto custody, the financial consequence was immediate and irreversible unless the attacker voluntarily returned funds. That hybrid nature is why launchpads need both smart-contract review and software-delivery governance.

One useful mental model is to treat every production-affecting launchpad release as a hot-wallet operation. If a change can redirect 864.8 ETH, it deserves controls comparable to a treasury transfer. The fact that the change is "just front-end" should not reduce the control standard.

## Attribution risk and incident communications

Several reports mention public accusations against a pseudonymous developer. CoinDesk explicitly noted that it could not independently verify the alleged attacker's identity. CryptoSlate reported that Delong's original accusation tweets were later deleted, that the accused person threatened to release MISO code absent an apology, and that community members criticized Sushi's handling of the situation.

That part of the story should be handled carefully. The attack mechanics and recovered amount are well supported across sources. The identity of the actor is less suitable for definitive claims. For a market-health record, the important lesson is not the name of the alleged contractor; it is that a contributor with sufficient access could reportedly alter the production path.

Incident response teams should preserve evidence, coordinate with counsel and exchanges, and communicate the technical facts users need. Public pressure can help recover funds, as it may have here, but premature attribution can damage innocent parties and reduce trust in the responder. In pseudonymous ecosystems, accusation discipline is part of security maturity.

## What this means for launchpad due diligence

A project choosing a launchpad should ask operational questions that go beyond auction format and fee schedule:

1. Who can merge front-end and studio changes that affect sale creation?
2. Are branch protections mandatory and applied to administrators?
3. Are production releases tied to reviewed, signed commits?
4. How are issuer treasury addresses confirmed?
5. Does the launchpad publish signed sale manifests?
6. Can a sale be paused if the live payout address differs from the manifest?
7. Are contractors least-privileged and time-limited?
8. Are audit scopes explicit about front-end, deployment, and CI/CD pipelines?
9. Are monitoring bots watching new auctions before bids accumulate?
10. What is the incident plan if sale proceeds move to the wrong address?

Those questions are not theoretical. They map directly to the MISO failure mode. A launchpad can have a polished brand and active community while still lacking enforced controls at the exact point where custody is assigned.

## Why the incident remains relevant

The crypto market has continued to professionalize since 2021, but the MISO lesson remains current. Many projects still rely on hosted front ends, private deployment repositories, third-party contributors, and hurried launch schedules. Token launches still concentrate large amounts of ETH or stablecoins into short windows. Attackers still prefer simple substitutions when simple substitutions are enough.

The broader ecosystem often separates "protocol risk" from "front-end risk." Users are told that contracts are immutable and transparent, while websites are treated as convenience layers. Launchpads blur that boundary. If the website or studio code determines which auction is created, which address receives proceeds, or which contract a user is directed to, then front-end integrity becomes protocol integrity for the duration of the sale.

The MISO exploit was small compared with later nine-figure bridge and lending incidents, but it is unusually instructive because the payload was so simple. A single malicious change allegedly redirected the whole raise. No complex exploit path was required. That makes it a clean warning for any market that treats GitHub permissions as separate from financial controls.

## Conclusion

The September 2021 MISO/Jay Pegs Auto Mart exploit converted a token-launch auction into a supply-chain custody failure. The attacker redirected 864.8 ETH by changing the wallet destination used for the auction, and the funds were later returned as roughly 865 ETH after rapid public escalation. Only one auction was reported affected, but the incident exposed a launchpad-wide lesson: primary issuance systems are only as safe as the code-review, deployment, and address-verification controls that bind sales to legitimate treasuries.

For market participants, the main takeaway is that recovered funds do not erase weak controls. For launchpads, the main takeaway is that front-end and studio repositories must be governed like treasury infrastructure. For issuers, the main takeaway is that sale manifests, payout-address verification, and emergency pause procedures should be required before any raise goes live.

The MISO incident did not become a permanent multimillion-dollar loss because the ETH came back. It still deserves to be remembered because the ecosystem should not need an attacker's cooperation to keep an auction solvent.

## References

- Sonatype, "3 Million Cryptocurrency Heist Stemmed from a Malicious GitHub Commit" — https://www.sonatype.com/blog/3-million-cryptocurrency-heist-malicious-github-commit
- Ars Technica, "Cryptocurrency launchpad hit by $3 million supply-chain attack" — https://arstechnica.com/information-technology/2021/09/cryptocurrency-launchpad-hit-by-3-million-supply-chain-attack/
- CoinDesk, "$3M in Ether Stolen From SushiSwap's MISO Launchpad" — https://www.coindesk.com/business/2021/09/17/3m-in-ether-stolen-from-sushiswaps-miso-launchpad
- CryptoBriefing, "Sushi's Initial Offering Launchpad Suffers $3M Exploit" — https://cryptobriefing.com/sushiswaps-miso-token-launchpad-suffers-3m-exploit/
- CryptoSlate, "Hacker returns 865 ETH stolen from Sushi's token launch platform MISO" — https://cryptoslate.com/hacker-returns-865-eth-stolen-from-sushis-token-launch-platform-miso/
- Coinspeaker, "SushiSwap Launchpad Miso Suffers Attack with 864.8 ETH Carted Away from Novel NFT Project" — https://www.coinspeaker.com/sushiswap-miso-attack-nft/
- Attacker address referenced in public reporting — https://etherscan.io/address/0x3ddd8b6d092df917473680d6c41f80f708c45395
