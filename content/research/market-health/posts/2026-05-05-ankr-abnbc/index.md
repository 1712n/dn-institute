---
date: 2026-05-05
entities:
  - id: ankr
    name: Ankr
    type: defi
  - id: helio-protocol
    name: Helio Protocol
    type: defi
  - id: binance
    name: Binance
    type: exchange
  - id: bnb-chain
    name: BNB Chain
    type: blockchain
title: "Ankr aBNBc deployer-key compromise, unbacked token mint, and DeFi contagion on BNB Chain"
---

## 1. Introduction and incident overview

On 1 December 2022, the Ankr protocol's BNB liquid-staking derivative token aBNBc was exploited through a compromised deployer key, enabling the attacker to mint approximately 60 trillion aBNBc tokens — far exceeding the legitimately staked BNB collateral. The attacker then sold the minted tokens through decentralized exchanges on BNB Chain, draining liquidity pools and collapsing the price of aBNBc from its approximate $300 peg to near zero. The direct extraction from on-chain liquidity pools was approximately $5 million, but the collateral damage extended further: the stablecoin protocol Helio (later rebranded HAY) suffered roughly $15 million in bad debt when its vaults accepted now-worthless aBNBc as collateral.

The incident illustrated how a single compromised administrative key in a liquid-staking protocol can cascade through the DeFi composability stack, imposing losses on downstream protocols that trusted the derivative token's peg as sound collateral.

## 2. Technical background

### 2.1 Ankr's BNB liquid-staking architecture

Ankr offered a BNB liquid-staking service on BNB Chain. Users deposited BNB into Ankr's staking contract and received aBNBc (Ankr BNB Reward Bearing Certificate), a rebasing token representing their staked BNB plus accumulated staking rewards. aBNBc was designed to maintain a 1:1 (or slightly appreciating) peg to BNB, with the collateral held in BNB Chain's native staking mechanism.

The aBNBc token contract was an upgradeable proxy contract. This architecture is standard in Ethereum-compatible DeFi: the proxy delegates all calls to a logic (implementation) contract, and the proxy's administrator can point it to a new implementation — enabling bug fixes and feature additions without requiring users to migrate to a new token address. However, this upgradeability concentrates critical power in the administrative key that controls the proxy.

### 2.2 Deployer key and access-control design

The aBNBc proxy contract's administrative functions — including the ability to upgrade the implementation and, critically, the ability to mint new tokens — were controlled by a deployer key. In Ankr's configuration at the time of the exploit, this was a single externally owned account (EOA) rather than a multisig wallet or a timelock-guarded governance mechanism.

This design choice meant that anyone who obtained the deployer key's private key could unilaterally:

1. Upgrade the aBNBc implementation to a new contract with arbitrary logic.
2. Call mint functions to create unbounded quantities of aBNBc.
3. Modify protocol parameters without delay or community approval.

### 2.3 aBNBc in the DeFi composability stack

aBNBc was integrated into several DeFi protocols on BNB Chain as collateral:

- **Helio Protocol (HAY stablecoin)**: Users could deposit aBNBc into Helio vaults as collateral to borrow the HAY stablecoin. Helio's oracle priced aBNBc based on its expected BNB peg, not its real-time DEX trading price.

- **PancakeSwap liquidity pools**: aBNBc/BNB and aBNBc/BUSD pools on PancakeSwap provided DEX liquidity that the attacker would target.

- **Other lending and yield protocols**: Various smaller protocols on BNB Chain accepted aBNBc as collateral or offered yield strategies involving it.

This composability meant that a collapse in aBNBc's value would propagate beyond Ankr's own protocol boundary.

## 3. Attack execution

### 3.1 Key compromise

Ankr's post-incident disclosure confirmed that the attacker obtained the deployer key's private key. The company stated that a former team member — described as an ex-employee — had exfiltrated the key prior to leaving the organization. Ankr did not provide detailed forensic evidence for this attribution, but the simplicity of the attack (direct use of the deployer key, no smart-contract vulnerability exploitation) is consistent with insider key theft rather than an external software exploit.

The compromised key had not been rotated after the employee's departure, and no multisig or timelock protection had been added to the deployer role.

### 3.2 Unbacked minting

At approximately 00:35 UTC on 1 December 2022, the attacker used the compromised deployer key to interact with the aBNBc proxy contract. The attacker called the mint function to create approximately 60 trillion aBNBc tokens in a series of transactions. The legitimate circulating supply of aBNBc at the time was approximately 8.5 million tokens, meaning the attacker minted roughly 7 million times the legitimate supply.

### 3.3 Liquidity extraction

The attacker immediately began selling the minted aBNBc through PancakeSwap's automated market maker (AMM) pools:

1. **aBNBc/BNB pool**: The attacker swapped large quantities of aBNBc for BNB, draining the BNB side of the pool. The constant-product AMM formula meant that each successive swap received less BNB per aBNBc as the pool's ratio skewed, but the attacker's enormous supply allowed exhaustive extraction.

2. **aBNBc/BUSD pool**: Similarly, aBNBc was swapped for BUSD.

3. **Cross-chain bridging**: The attacker bridged extracted BNB and BUSD to Ethereum via cross-chain bridges, then used Tornado Cash to obscure the trail. Approximately $5 million in value was extracted from DEX liquidity pools before arbitrage bots and manual traders stopped providing counterparty liquidity.

### 3.4 aBNBc price collapse

The massive sell pressure from 60 trillion newly minted tokens against finite pool liquidity caused aBNBc's price to crash from approximately $304 (its BNB-peg value) to effectively zero within minutes. Legitimate aBNBc holders who had staked BNB through Ankr saw their token balances become worthless on the open market, even though the underlying BNB remained staked on BNB Chain.

## 4. Contagion to Helio Protocol

### 4.1 Oracle pricing gap

The most significant downstream impact was on Helio Protocol, which accepted aBNBc as collateral for borrowing the HAY stablecoin. Helio's oracle continued to price aBNBc at its expected BNB peg value rather than its collapsed DEX price. This oracle lag created an arbitrage opportunity that compounded the damage.

### 4.2 Exploitation of Helio vaults

After the aBNBc price collapsed on DEXes, opportunistic actors (possibly including the original attacker) purchased now-worthless aBNBc on PancakeSwap for fractions of a cent, deposited it into Helio vaults where the oracle still valued it at $304, and borrowed HAY stablecoins against this inflated collateral valuation. They then sold the borrowed HAY for real assets.

This extraction from Helio was estimated at approximately $15 million in bad debt — representing HAY loans backed by collateral that was functionally worthless. The HAY stablecoin temporarily depegged as the protocol's collateral base became insolvent.

### 4.3 Helio's response

Helio Protocol paused deposits and borrowing once the oracle discrepancy was identified, but the damage had already been done during the gap between the aBNBc price collapse and the oracle update. The protocol subsequently underwent restructuring and rebranding.

## 5. Ankr's response and remediation

### 5.1 Immediate response

Ankr acknowledged the exploit within hours of its occurrence. The company stated that the underlying staked BNB was not affected — it remained locked in BNB Chain's staking contracts — and committed to reissuing a new token (ankrBNB) to replace aBNBc with improved security controls.

### 5.2 User compensation

Ankr announced a compensation plan to make affected users whole:

- Legitimate aBNBc holders before the exploit would receive the new ankrBNB token on a 1:1 basis relative to their pre-exploit balance, backed by the underlying staked BNB.
- Ankr committed $5 million to purchase BNB to recollateralize any shortfall.
- Helio Protocol separately addressed its bad-debt situation, though the mechanism and coverage were handled by Helio's own governance.

### 5.3 Security upgrades

Ankr implemented several security improvements following the incident:

1. **Multisig administration**: The deployer key was replaced with a multisig wallet requiring multiple signers for administrative actions.
2. **Timelock**: A timelock delay was added to contract upgrades, allowing users to review and react to proposed changes before they take effect.
3. **Key rotation procedures**: The company stated it had implemented key-management policies including rotation schedules and access-revocation procedures upon employee departure.
4. **Token reissuance**: The compromised aBNBc contract was deprecated and replaced with the new ankrBNB token under the improved security controls.

### 5.4 Law enforcement

Ankr stated that it reported the incident to law enforcement and that the former employee suspected of key exfiltration was identified. The company did not publicly disclose the outcome of any criminal proceedings as of early 2026.

## 6. Binance's involvement

Binance, as the operator of BNB Chain's ecosystem, took several actions in response to the incident:

1. **Exchange suspension**: Binance temporarily halted deposits and withdrawals of aBNBc on its centralized exchange.
2. **Address freezing**: Binance worked with BNB Chain validators to freeze approximately $3 million in funds linked to the attacker's addresses on BNB Chain. This ability to freeze funds on a proof-of-stake chain through validator coordination raised decentralization questions but was effective in limiting attacker extraction.
3. **Ecosystem support**: Binance assisted with coordination between Ankr, Helio, and other affected protocols.

## 7. Market-health implications

### 7.1 Administrative key risk in liquid-staking protocols

The Ankr exploit is a case study in the risk posed by centralized administrative keys in DeFi protocols. Liquid-staking protocols hold significant value in their staking contracts and issue derivative tokens that are widely integrated into the DeFi composability stack. When the administrative key for such a protocol is a single EOA, the protocol's entire security reduces to the security of one private key — a single point of failure that negates the distributed-trust benefits of the underlying blockchain.

The industry trend following incidents like Ankr's has been toward:

- **Multisig administration**: Requiring multiple independent signers for administrative actions, reducing the risk of a single compromised or malicious key.
- **Timelock governance**: Imposing delays on administrative actions, giving users time to withdraw if they disagree with proposed changes.
- **On-chain governance**: Transferring administrative control to token-holder voting, distributing power but introducing its own governance-attack surface.

### 7.2 DeFi composability as a contagion vector

The Ankr-Helio cascade demonstrates how DeFi composability — often celebrated as a feature that enables capital efficiency and innovation — can function as a contagion vector when one component fails. Helio Protocol did not have a vulnerability in its own smart contracts; its exposure was a design choice to accept aBNBc as collateral and a failure to use real-time DEX price feeds (or circuit breakers) in its oracle.

This composability risk is structural in DeFi:

- **Collateral-chain dependencies**: When Protocol B accepts Protocol A's derivative token as collateral, Protocol B inherits Protocol A's security properties — including its administrative key management, smart-contract risk, and oracle assumptions.

- **Oracle lag exploitation**: The window between an on-chain price collapse and an oracle update creates a predictable arbitrage opportunity. Protocols that rely on slow-updating oracles (Chainlink heartbeat intervals, TWAP windows, or manual price feeds) are vulnerable to exactly this type of collateral-value manipulation.

- **Cascading liquidations**: In more complex DeFi ecosystems, a collateral token collapse can trigger liquidation cascades across multiple protocols, each dumping the collateral token and reinforcing the downward price spiral.

### 7.3 Insider threat and key management

The attribution to a former employee highlights the insider-threat dimension of cryptocurrency protocol security. Traditional corporate security practices — employee offboarding procedures, access revocation, key rotation, background checks — are as relevant to DeFi teams as they are to banks and technology companies. The crypto industry's rapid growth and sometimes informal employment practices can leave gaps in these controls.

For market surveillance, the insider-threat vector is difficult to detect externally. Unlike a smart-contract vulnerability that leaves on-chain traces during exploitation, a compromised key looks identical to a legitimate administrative action until the unauthorized mint or upgrade is executed. Detection relies on:

- Monitoring for abnormal minting events (especially those that dramatically increase total supply).
- Watching for large, sudden transfers from deployer or admin addresses.
- Tracking administrative key changes and upgrades in protocol proxy contracts.

### 7.4 Centralized intervention on decentralized chains

Binance's ability to coordinate with BNB Chain validators to freeze attacker funds illustrates the tension between decentralization ideology and practical incident response. While the fund freeze limited attacker extraction, it also demonstrated that BNB Chain's validator set was sufficiently concentrated to enable targeted censorship. This capability is a double-edged sword: useful for incident response but potentially concerning for censorship resistance.

## 8. Comparative context

The Ankr exploit shares characteristics with several other DeFi incidents:

| Incident | Year | Vector | Loss | Downstream contagion |
|---|---|---|---|---|
| Ankr aBNBc | 2022 | Deployer key compromise | ~$5M direct, ~$15M Helio | HAY stablecoin depeg |
| Multichain | 2023 | MPC key compromise (CEO) | $126M+ | Multiple bridge pools |
| Harmony Horizon | 2022 | Validator key compromise | $100M | None (bridge-only) |
| Ronin Bridge | 2022 | Validator key compromise | $625M | None (bridge-only) |

The common thread is that centralized key management — whether a single EOA, a small multisig, or an MPC scheme with concentrated key shares — remains the primary attack vector for high-value DeFi exploits. Smart-contract logic bugs, while well-publicized, are less consistently responsible for the largest losses than administrative key compromises.

## 9. Lessons learned and recommendations

### 9.1 For liquid-staking protocols

1. **Eliminate single-EOA admin keys**: Use multisig wallets with geographically and organizationally distributed signers. No individual should be able to unilaterally execute administrative functions.

2. **Implement timelocks on minting and upgrades**: Even with multisig, a timelock gives the community time to detect and respond to unauthorized actions before they take effect.

3. **Enforce supply-cap checks**: Smart contracts should include hard-coded maximum supply limits that even the admin key cannot override without a governance process.

4. **Rotate keys upon personnel changes**: Implement and enforce key-rotation procedures whenever employees with access depart the organization.

### 9.2 For protocols accepting derivative collateral

1. **Use real-time price feeds with circuit breakers**: Oracles should incorporate real-time DEX price data alongside TWAP and external feeds. Circuit breakers should pause borrowing if the collateral token's price deviates from its peg by more than a defined threshold.

2. **Assess upstream administrative risk**: Before accepting a derivative token as collateral, evaluate the issuing protocol's key-management practices, not just its smart-contract logic.

3. **Implement collateral-concentration limits**: Cap the proportion of any single derivative token in the collateral base to limit contagion exposure.

### 9.3 For market surveillance

1. **Monitor abnormal supply changes**: Automated alerts for minting events that increase a token's circulating supply by more than a defined percentage (e.g., 1%) within a single block or short time window.

2. **Track deployer and admin wallet activity**: Flag transactions originating from known deployer or admin addresses, especially upgrade calls and mint functions.

3. **Cross-protocol dependency mapping**: Maintain awareness of which protocols accept which derivative tokens as collateral, enabling rapid impact assessment when a component protocol is compromised.

## 10. Conclusion

The Ankr aBNBc exploit of December 2022 demonstrated the fragility introduced when centralized key management intersects with DeFi composability. A single compromised deployer key enabled the minting of trillions of unbacked tokens, which were sold into DEX liquidity pools for approximately $5 million in direct extraction. The downstream contagion to Helio Protocol — which accepted aBNBc as collateral and suffered approximately $15 million in bad debt due to oracle lag — illustrated how DeFi's interconnected architecture can amplify a single-protocol failure into a multi-protocol crisis.

Ankr's subsequent remediation — multisig administration, timelocks, token reissuance, and user compensation — addressed the immediate vulnerability but could not undo the losses inflicted on Helio users and aBNBc liquidity providers. The incident reinforced that the security of DeFi derivative tokens depends on the operational security practices of their issuing teams, not merely on the correctness of their smart-contract code. For the broader market, the Ankr case underscores the need for downstream protocols to evaluate the administrative-key architecture of upstream collateral tokens and to implement real-time oracle circuit breakers that can halt lending when collateral pegs break.
