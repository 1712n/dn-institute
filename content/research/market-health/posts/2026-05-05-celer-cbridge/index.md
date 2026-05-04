---
date: 2026-05-05
entities:
  - id: celer-network
    name: Celer Network
    type: defi
  - id: cbridge
    name: cBridge
    type: defi
  - id: quickhostuk
    name: QuickHostUk
    type: infrastructure
title: "Celer cBridge BGP hijacking attack, front-end smart-contract substitution, and $235 K user losses"
---

## 1. Introduction and incident overview

On 17 August 2022, users of Celer Network's cBridge cross-chain bridge were targeted in a front-end hijacking attack that resulted in approximately $235,000 in stolen funds across 32 victims. The attack exploited Border Gateway Protocol (BGP) hijacking — a technique that manipulates the Internet's core routing infrastructure to redirect traffic — to intercept requests to a critical cBridge configuration endpoint and replace legitimate bridge smart-contract addresses with attacker-controlled phishing contracts. Users who interacted with the cBridge front end during the approximately three-hour attack window were presented with malicious contracts that drained their token approvals and direct transfers.

The Celer cBridge incident was notable not because of its monetary scale (which was relatively modest compared to other bridge exploits) but because of its attack vector. Unlike the vast majority of DeFi exploits, which target smart-contract logic or private-key compromise, the cBridge attack targeted the Internet's routing layer — a domain that most DeFi security audits and monitoring tools do not cover. The incident demonstrated that even a protocol with secure smart contracts and properly managed private keys can be compromised through infrastructure-level attacks on the network paths between users and the protocol's front end.

## 2. Technical background

### 2.1 Celer Network and cBridge

Celer Network is a blockchain interoperability protocol that provides cross-chain asset transfers and cross-chain messaging through its cBridge product. cBridge allows users to transfer tokens between Ethereum, BNB Chain, Polygon, Arbitrum, Optimism, Fantom, Avalanche, Metis, Astar, Aurora, and other EVM-compatible chains. Users interact with cBridge through a web-based decentralized application (dApp) front end that communicates with on-chain bridge contracts on each supported network.

The cBridge front end relies on a configuration endpoint — hosted at `cbridge-prod2.celer.network` — to provide users with the current bridge contract addresses for each supported chain. When a user initiates a cross-chain transfer, the front end fetches the latest contract configuration from this endpoint and constructs the appropriate transaction for the user to sign. This architecture means that the integrity of the configuration endpoint is a critical trust assumption: if the endpoint serves incorrect contract addresses, users will unknowingly interact with the wrong contracts.

### 2.2 Border Gateway Protocol (BGP)

The Border Gateway Protocol is the routing protocol that governs how data packets are routed between Autonomous Systems (ASes) on the Internet. Each AS — typically an Internet service provider (ISP), hosting provider, or large enterprise — announces the IP address ranges it can reach, and BGP routers across the Internet use these announcements to build routing tables that determine how to forward traffic.

BGP was designed in an era when the Internet was operated by a small number of trusted organizations, and the protocol lacks built-in authentication of route announcements. Any AS can announce routes for any IP address range, and neighboring ASes will generally accept and propagate these announcements based on standard routing policies. This trust model creates a fundamental vulnerability: a malicious or compromised AS can announce routes for IP address ranges it does not legitimately serve, causing some portion of Internet traffic destined for those addresses to be redirected through the attacker's network.

### 2.3 BGP hijacking mechanics

A BGP hijacking attack works by exploiting the fact that BGP routers prefer more specific routes. If the legitimate route for a target IP address is a /11 prefix (e.g., 44.224.0.0/11), an attacker can announce a more specific /24 prefix (e.g., 44.235.216.0/24) that covers the target IP. Because /24 is more specific than /11, BGP routers that receive both announcements will prefer the attacker's /24 route for traffic destined for addresses within that /24 range. This causes traffic that would normally flow to the legitimate server to be redirected to the attacker's infrastructure instead.

The attacker must also obtain a valid TLS certificate for the target domain to complete the interception. Without a valid certificate, users' browsers would display certificate warnings when connecting to the hijacked endpoint. However, because the attacker controls the DNS resolution path for the hijacked IP range, they can obtain a domain-validation (DV) certificate from any certificate authority that uses HTTP-based validation, since the CA's validation request will also be routed through the attacker's infrastructure.

### 2.4 Prior BGP hijacking incidents in cryptocurrency

The Celer cBridge attack was not the first use of BGP hijacking against cryptocurrency targets. In February 2022, the KLAYswap protocol on the Klaytn blockchain was similarly attacked through BGP hijacking, resulting in approximately $1.9 million in losses. The KLAYswap incident used the same general technique: BGP route manipulation redirected traffic to a malicious server that injected modified JavaScript into the protocol's front end. The recurrence of BGP hijacking attacks against DeFi protocols within a six-month period indicated that this attack vector was being actively developed and refined by threat actors targeting the cryptocurrency ecosystem.

## 3. Attack preparation

### 3.1 Malicious smart-contract deployment

The attacker began preparations on 12 August 2022, five days before the BGP hijack, by deploying a series of malicious phishing smart contracts across ten blockchain networks: Ethereum, BNB Chain (BSC), Polygon, Optimism, Fantom, Arbitrum, Avalanche, Metis, Astar, and Aurora. The deployment of contracts across all chains that cBridge supported indicated thorough reconnaissance and preparation.

Each phishing contract was designed to closely mimic the legitimate cBridge contract on its respective chain. The contracts used a proxy architecture: for any function not explicitly overridden by the attacker, the contract forwarded calls to the legitimate cBridge contract using a delegate-call-like proxy pattern. This meant that basic interactions with the phishing contract would appear to behave normally, reducing the likelihood that users or monitoring tools would detect the substitution from on-chain behavior alone.

The phishing contracts overrode four specific functions that handle fund transfers:

1. **`send()`**: Used for transferring ERC-20 tokens (e.g., USDC, USDT) across chains. The overridden function redirected the tokens to the attacker's wallet instead of the bridge pool.
2. **`sendNative()`**: Used for transferring native chain assets (e.g., ETH, BNB). The overridden function sent the native assets to the attacker.
3. **`addLiquidity()`**: Used by liquidity providers to deposit tokens into bridge pools. The overridden function stole the deposited tokens.
4. **`addNativeLiquidity()`**: Used by liquidity providers to deposit native assets. The overridden function stole the deposited assets.

Additionally, the phishing contracts included a custom function (4-byte selector `0x9c307de6`) that allowed the attacker to drain any ERC-20 tokens that victims had previously approved for the phishing contract address. This function served as a cleanup mechanism to extract value from token approvals that were granted during the attack window but not immediately exploited through the overridden bridge functions.

### 3.2 BGP route preparation

On 16 August 2022, one day before the attack, the attacker created routing registry entries in the Internet Routing Registry (IRR) under the MAINT-QUICKHOSTUK maintainer object, adding a route for the 44.235.216.0/24 prefix. This prefix covered the IP address 44.235.216.69, which hosted the critical `cbridge-prod2.celer.network` configuration endpoint on Amazon Web Services (AWS) infrastructure.

QuickHostUk (AS-209243) is a UK-based hosting provider whose AS number was used in the malicious route announcement. Whether QuickHostUk was complicit in the attack or was itself compromised (through credential theft or social engineering) was not conclusively determined in public reporting. The registration of the /24 route in the IRR the day before the attack suggests that the attacker needed time for the route object to propagate through the registry before announcing it via BGP.

### 3.3 TLS certificate acquisition

As part of the attack preparation, the attacker obtained a valid TLS certificate for `cbridge-prod2.celer.network` from GoGetSSL, an SSL certificate provider based in Latvia. The certificate was first observed at approximately 19:42 UTC on 17 August 2022, shortly after the BGP route announcement began propagating. The timing indicates that the attacker used the BGP hijack itself to complete the domain-validation challenge: once the attacker controlled traffic to the target IP address, they could respond to the CA's HTTP validation request and obtain a certificate for the domain without needing to compromise Celer's DNS registrar or hosting account.

Prior to the attack, Celer Network used TLS certificates issued by Let's Encrypt and Amazon Certificate Manager. The appearance of a GoGetSSL-issued certificate for a Celer subdomain was an anomaly that, in principle, could have been detected through Certificate Transparency (CT) log monitoring. However, CT monitoring was not in place for this domain at the time of the attack.

## 4. Attack execution

### 4.1 BGP route announcement

On 17 August 2022 at approximately 19:39 UTC, a malicious BGP route announcement began propagating across the Internet. The announcement advertised the 44.235.216.0/24 prefix with origin AS-14618 (Amazon) and upstream AS-209243 (QuickHostUk). Because 44.235.216.0/24 is more specific than the legitimate 44.224.0.0/11 route announced by Amazon, BGP routers that received the malicious announcement began routing traffic for the target IP address through QuickHostUk's network to the attacker's infrastructure.

The BGP hijack did not affect all Internet users uniformly. BGP route propagation depends on peering relationships, routing policies, and geographic proximity, so only users whose ISPs or upstream providers accepted and preferred the malicious /24 route were redirected. Users whose network paths did not incorporate the hijacked route continued to reach the legitimate cBridge configuration endpoint and were not affected.

### 4.2 Configuration endpoint substitution

Once the BGP hijack redirected traffic for `cbridge-prod2.celer.network` to the attacker's server, the attacker served a modified version of the cBridge configuration endpoint. The endpoint's response — specifically the `/v1/getTransferConfigsForAll` API — contained bridge contract addresses for each supported chain. The attacker replaced the legitimate contract addresses with the addresses of the phishing contracts deployed in the preparation phase.

When cBridge front-end users loaded the dApp during the attack window, their browsers fetched the configuration data from the attacker's server (which appeared legitimate due to the valid TLS certificate). The front end then constructed transactions targeting the phishing contracts instead of the real bridge contracts. Users who signed and submitted these transactions had their funds stolen.

### 4.3 User impact

The first funds were stolen at approximately 19:51 UTC on 17 August 2022, when a victim on the Fantom network interacted with a phishing contract. The last theft occurred at approximately 21:49 UTC on the BNB Chain network. During the roughly three-hour attack window, 32 users were affected.

Ethereum users suffered the largest monetary losses, with a single victim losing approximately $156,000. BNB Chain had the highest number of individual victims. Users on some chains, including Avalanche and Metis, suffered no losses despite the phishing contracts being deployed on those networks — likely because no users happened to interact with the cBridge front end on those chains during the attack window.

The total losses across all chains and victims were approximately $235,000. This amount was relatively modest for a cross-chain bridge attack (compared to the hundreds of millions lost in the Nomad, Ronin, and Wormhole bridge exploits), but this reflected the attack's dependence on individual user interactions rather than direct pool drainage.

### 4.4 Fund laundering

During and immediately following the attack, the attacker executed a multi-step fund movement process:

1. **Token swaps**: On each chain where funds were stolen, the attacker swapped stolen tokens (USDC, USDT, and others) into native chain assets or wrapped ETH using decentralized exchanges including Curve, Uniswap, TraderJoe, and AuroraSwap.
2. **Cross-chain bridging**: The attacker bridged all converted assets from non-Ethereum chains to Ethereum, consolidating the stolen funds onto a single chain.
3. **Final swap**: On Ethereum, the attacker swapped remaining tokens to ETH using Uniswap.
4. **Tornado Cash deposits**: Starting at 22:33 UTC on 17 August 2022 (less than an hour after the last theft), the attacker deposited approximately 127 ETH into Tornado Cash. A second deposit of 1.4 ETH followed at 01:01 UTC on 18 August.

The rapid movement to Tornado Cash — within hours of the exploit — indicated an attacker who had pre-planned the laundering process and was aware of blockchain analytics capabilities. After the primary Tornado Cash deposits, the attacker sent a small remaining balance (0.012 ETH) to an address that had previous connections to a Binance deposit address, though this connection did not lead to publicly reported identification.

## 5. Response and aftermath

### 5.1 Detection and shutdown

The Celer Network team detected the suspicious activity and announced the incident via social media. The team shut down the cBridge front end and urged users to revoke token approvals for the phishing contract addresses. Because the attack targeted the front-end configuration rather than the bridge contracts themselves, the bridge's smart contracts and liquidity pools were not directly compromised. Users who had not interacted with the front end during the attack window, or who interacted with the bridge contracts directly (bypassing the front end), were not affected.

### 5.2 BGP route withdrawal and recovery

The malicious BGP route was withdrawn at approximately 20:22 UTC on 17 August 2022, roughly 43 minutes after the route began propagating. The withdrawal may have been initiated by the attacker (upon detecting that the attack had been discovered), by QuickHostUk (if the hosting provider identified the unauthorized route announcement), or by upstream transit providers that received abuse reports.

At 23:08 UTC, Amazon announced the 44.235.216.0/24 prefix from its own AS to reclaim the hijacked IP range and prevent any residual route leakage. This defensive announcement ensured that even if the malicious route reappeared, the legitimate Amazon announcement would compete on equal specificity.

### 5.3 User advisories

Celer Network published advisories urging all cBridge users to revoke ERC-20 token approvals for the phishing contract addresses on all affected chains. This was particularly important because the phishing contracts' custom drain function (`0x9c307de6`) could be used to steal tokens from any address that had granted an approval to the phishing contract, even after the BGP hijack ended and the front end was restored. Users who had approved tokens during the attack window but had not yet had their funds drained remained at risk until they revoked the approvals.

### 5.4 Celer's post-incident measures

Following the attack, Celer Network implemented several security improvements:

- **Certificate Transparency monitoring**: Celer set up monitoring for any new TLS certificates issued for its domains, which would enable early detection of unauthorized certificate issuance (a potential indicator of BGP hijacking or DNS compromise).
- **RPKI adoption**: Celer worked with its hosting providers to implement Resource Public Key Infrastructure (RPKI) route origin validation, which cryptographically attests the authorized origin AS for an IP prefix and allows RPKI-validating routers to reject unauthorized BGP announcements.
- **Multi-source configuration verification**: Celer explored approaches to validate the integrity of the bridge configuration data served to the front end, reducing reliance on a single endpoint.

## 6. Market-health implications

### 6.1 Infrastructure-layer attacks as an emerging DeFi threat

The Celer cBridge incident highlighted a category of risk that falls outside the scope of most DeFi security analysis: attacks on the Internet infrastructure layer. The vast majority of DeFi security audits, bug bounties, and monitoring tools focus on smart-contract vulnerabilities, private-key management, and oracle manipulation. BGP hijacking targets a completely different layer of the stack — the network routing that determines how traffic flows between users and servers — and cannot be detected or prevented by smart-contract-level security measures.

This infrastructure-layer risk is particularly concerning because it does not require any vulnerability in the target protocol's code. Celer's smart contracts were not compromised; the bridge's liquidity pools were not drained; and the protocol's private keys were not stolen. The attack succeeded entirely by redirecting users to malicious front-end infrastructure, exploiting the trust that users place in the URL they navigate to and the TLS certificate their browser validates.

### 6.2 Front-end as a single point of trust

The cBridge attack exposed a common architectural pattern in DeFi protocols: the front-end dApp serves as a trusted intermediary that provides users with the correct contract addresses and transaction parameters. While the blockchain itself is decentralized and trustless, the web-based front ends through which most users interact with DeFi protocols are centralized web applications hosted on conventional infrastructure. This creates a trust bottleneck: users rely on the front end to provide correct information, and the front end relies on DNS, BGP, TLS, CDN, and hosting infrastructure that is subject to the same attack vectors as any other web application.

This front-end trust dependency has been exploited in multiple incidents:

| Incident | Date | Vector | Loss |
|---|---|---|---|
| BadgerDAO | Dec 2021 | Cloudflare API key compromise, malicious frontend injection | ~$120M |
| KLAYswap | Feb 2022 | BGP hijacking, JavaScript injection | ~$1.9M |
| Celer cBridge | Aug 2022 | BGP hijacking, contract address substitution | ~$235K |
| Curve Finance | Aug 2022 | DNS hijacking via registrar compromise | ~$570K |

### 6.3 BGP security and RPKI adoption

The Internet's vulnerability to BGP hijacking is a well-known problem in network security, and the primary mitigation is Resource Public Key Infrastructure (RPKI) — a cryptographic framework that allows IP address holders to authorize specific ASes to originate routes for their prefixes. When RPKI is deployed and enforced by transit providers, unauthorized route announcements are rejected before they propagate.

However, RPKI adoption remains incomplete across the Internet. As of the time of the Celer incident, many transit providers did not enforce RPKI route origin validation, meaning that hijacked routes could still propagate through portions of the Internet's routing infrastructure. For DeFi protocols, this means that BGP hijacking remains a viable attack vector until RPKI deployment reaches critical mass — a process that has been ongoing for years and depends on coordinated action across thousands of independent network operators.

### 6.4 Scale advantage of infrastructure attacks

While the Celer cBridge attack resulted in modest losses ($235K), the attack vector has a significantly higher potential scale. A more extended BGP hijack — lasting days instead of hours — targeting a higher-traffic protocol could potentially affect thousands of users and result in losses comparable to smart-contract-level exploits. The relatively low losses in the Celer case reflected the short attack window (approximately three hours), the limited number of users who happened to interact with cBridge during that window, and the rapid detection by the Celer team. A more sophisticated attacker might extend the attack window by targeting less actively monitored endpoints or by timing the attack to coincide with periods of low security-team availability.

### 6.5 Cross-chain bridge risk concentration

The Celer incident added to the growing list of cross-chain bridge attacks in 2022, which also included the Ronin Bridge ($625M, March 2022), Wormhole ($325M, February 2022), Nomad Bridge ($190M, August 2022), and Harmony Horizon Bridge ($100M, June 2022). While the cBridge attack used a fundamentally different vector (infrastructure hijacking rather than smart-contract exploit or key compromise), it reinforced the broader market-health concern that cross-chain bridges represent concentrated points of risk in the multi-chain DeFi ecosystem. Bridges concentrate value (in liquidity pools), trust (in validators or contract logic), and user traffic (through front-end interfaces), making them high-value targets for a variety of attack strategies.

## 7. Lessons learned and recommendations

### 7.1 For DeFi protocol operators

1. **Monitor Certificate Transparency logs**: Set up automated monitoring for any TLS certificates issued for the protocol's domains. An unauthorized certificate issuance is a strong indicator of an ongoing or imminent BGP hijack or DNS compromise. Multiple open-source and commercial CT monitoring tools exist for this purpose.

2. **Implement RPKI**: Work with hosting providers and CDN services to ensure that RPKI Route Origin Authorizations (ROAs) are created for all IP prefixes hosting critical protocol infrastructure. This does not guarantee protection (since not all transit providers enforce RPKI), but it significantly reduces the set of networks through which a BGP hijack can propagate.

3. **Diversify configuration trust**: Avoid relying on a single centralized endpoint for critical configuration data (such as contract addresses). Consider approaches such as serving configuration from multiple independent endpoints and requiring consensus, embedding known-good contract addresses in the front-end code, or using on-chain registries that the front end can verify independently.

4. **Implement Subresource Integrity (SRI) and Content Security Policy (CSP)**: These web security mechanisms can help detect modifications to front-end code and restrict the resources that the front end can load, providing additional layers of defense against front-end hijacking.

### 7.2 For DeFi users

1. **Verify contract addresses independently**: Before signing transactions, especially high-value ones, verify that the contract address matches the address published in the protocol's documentation or on-chain registry, rather than relying solely on what the front-end interface presents.

2. **Limit token approvals**: Use limited (rather than unlimited) ERC-20 token approvals when interacting with DeFi protocols. This bounds the potential loss if a front-end substitution attack presents a malicious contract that the user unknowingly approves.

3. **Revoke approvals promptly after incidents**: When a protocol announces a front-end compromise, immediately revoke any token approvals that may have been granted to the compromised addresses.

### 7.3 For market surveillance

1. **Monitor CT logs for DeFi domains**: Certificate Transparency log monitoring can provide early warning of BGP hijacking or DNS compromise targeting DeFi protocol front ends. An anomalous certificate issued by an unexpected CA for a DeFi protocol's domain warrants immediate investigation.

2. **Track BGP anomalies for critical DeFi infrastructure**: Network-level monitoring services (such as RIPE RIS, BGPStream, and commercial BGP monitoring platforms) can detect anomalous route announcements for IP prefixes hosting major DeFi protocol infrastructure. Integrating BGP monitoring into DeFi market surveillance provides a layer of detection that purely on-chain monitoring cannot achieve.

3. **Assess bridge front-end centralization risk**: When evaluating cross-chain bridge risk, consider not only the bridge's smart-contract security and validator set but also the centralization of its front-end infrastructure. A bridge with secure contracts but a single-endpoint front end hosted on infrastructure without RPKI protection has a different risk profile than one with decentralized or multi-source front-end architecture.

## 8. Conclusion

The Celer cBridge BGP hijacking attack of August 2022 demonstrated that DeFi protocol security extends beyond smart contracts and private keys to encompass the Internet infrastructure on which protocol front ends depend. By exploiting BGP — the Internet's core routing protocol — the attacker redirected users to a malicious front end that substituted phishing contracts for legitimate cBridge addresses, resulting in $235,000 in losses across 32 victims on multiple blockchain networks.

The incident's significance for market health lies less in its monetary impact than in the attack vector it validated. BGP hijacking requires no smart-contract vulnerability, no private-key compromise, and no insider access to the target protocol. It exploits a structural weakness in the Internet's routing infrastructure that is not addressed by standard DeFi security measures. The recurrence of BGP hijacking attacks against cryptocurrency targets in 2022 (including KLAYswap and Celer) indicated an emerging threat pattern that warrants dedicated monitoring and mitigation by DeFi protocols, infrastructure providers, and market-surveillance entities. Until RPKI adoption reaches comprehensive coverage across Internet transit providers, BGP hijacking will remain a viable and difficult-to-prevent attack vector against any Internet-hosted service, including DeFi protocol front ends.
